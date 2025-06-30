"""
Auto-Feedback Retraining Engine for Agentius
==========================================

Converts live evaluation data into training datasets for continuous model improvement.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from .decision_tracer import global_tracer, DecisionType
from ..utils.logger import setup_logger
from ..utils.config import load_config

logger = setup_logger(__name__)

@dataclass
class TrainingExample:
    """Single training example for fine-tuning"""
    input_prompt: str
    expected_output: str
    context: Dict[str, Any]
    performance_score: float  # How well this performed in practice
    archetype: str
    fear_triggers: List[str]
    outcome_quality: str  # "excellent", "good", "poor", "failed"
    feedback_source: str  # "client_approval", "score_improvement", "human_feedback"

@dataclass
class ModelPerformanceMetrics:
    """Track model performance over time"""
    archetype: str
    period: str  # "daily", "weekly", "monthly"
    accuracy_score: float
    consistency_score: float
    improvement_rate: float
    confidence_calibration: float
    fear_detection_accuracy: float
    total_evaluations: int
    successful_outcomes: int

class TrainingDataGenerator:
    """Generates high-quality training data from evaluation sessions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.training_data_path = Path(config.get("training_data_path", "/tmp/agentius_training"))
        self.training_data_path.mkdir(exist_ok=True)
        
        # Quality thresholds for training data inclusion
        self.min_score_improvement = 1.5  # Minimum score improvement to include
        self.min_confidence = 0.7  # Minimum confidence for reliable examples
        self.max_iterations = 3  # Only include examples from efficient evaluations
    
    async def extract_training_data(self, context_id: str) -> List[TrainingExample]:
        """Extract training examples from a completed evaluation"""
        
        trace = global_tracer.get_trace(context_id)
        if not trace or trace["metadata"]["completion_status"] != "completed":
            return []
        
        examples = []
        
        # Extract judge training examples
        for decision in trace["decision_points"]:
            if decision["decision_type"] == DecisionType.JUDGE_EVALUATION:
                example = await self._extract_judge_example(decision, trace)
                if example and self._is_high_quality_example(example):
                    examples.append(example)
        
        # Extract refiner training examples
        for decision in trace["decision_points"]:
            if decision["decision_type"] == DecisionType.REFINEMENT_STRATEGY:
                example = await self._extract_refiner_example(decision, trace)
                if example and self._is_high_quality_example(example):
                    examples.append(example)
        
        # Extract fear detection examples
        fear_examples = await self._extract_fear_detection_examples(trace)
        examples.extend(fear_examples)
        
        logger.info(f"Extracted {len(examples)} training examples from context {context_id}")
        return examples
    
    async def _extract_judge_example(self, decision: Dict[str, Any], trace: Dict[str, Any]) -> Optional[TrainingExample]:
        """Extract judge evaluation training example"""
        
        try:
            # Find the reasoning chain
            reasoning_chain = decision["reasoning_chain"]
            if not reasoning_chain:
                return None
            
            # Get the proposal input
            proposal_step = next((step for step in reasoning_chain if step["step_type"] == "proposal_analysis"), None)
            if not proposal_step:
                return None
            
            # Calculate performance score based on outcome
            performance_score = self._calculate_performance_score(decision, trace)
            
            # Build training example
            input_prompt = self._build_judge_prompt(proposal_step["input_data"], decision["agent_id"])
            expected_output = self._build_judge_expected_output(decision)
            
            return TrainingExample(
                input_prompt=input_prompt,
                expected_output=expected_output,
                context={
                    "archetype": decision["agent_id"],
                    "iteration": proposal_step["input_data"].get("iteration", 1),
                    "context_id": trace["context_id"]
                },
                performance_score=performance_score,
                archetype=decision["agent_id"],
                fear_triggers=self._extract_fear_triggers_from_decision(decision),
                outcome_quality=self._determine_outcome_quality(performance_score),
                feedback_source="score_improvement"
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract judge example: {e}")
            return None
    
    async def _extract_refiner_example(self, decision: Dict[str, Any], trace: Dict[str, Any]) -> Optional[TrainingExample]:
        """Extract refiner training example"""
        
        try:
            reasoning_chain = decision["reasoning_chain"]
            refinement_step = next((step for step in reasoning_chain if step["step_type"] == "refinement_strategy"), None)
            
            if not refinement_step:
                return None
            
            # Get before/after scores to measure improvement
            score_improvement = self._calculate_score_improvement(decision, trace)
            
            input_prompt = self._build_refiner_prompt(refinement_step["input_data"])
            expected_output = refinement_step["output_data"].get("refined_proposal", "")
            
            return TrainingExample(
                input_prompt=input_prompt,
                expected_output=expected_output,
                context={
                    "score_improvement": score_improvement,
                    "objections_addressed": len(refinement_step["input_data"].get("objections", [])),
                    "context_id": trace["context_id"]
                },
                performance_score=score_improvement,
                archetype="refiner",
                fear_triggers=[],
                outcome_quality=self._determine_outcome_quality(score_improvement),
                feedback_source="score_improvement"
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract refiner example: {e}")
            return None
    
    async def _extract_fear_detection_examples(self, trace: Dict[str, Any]) -> List[TrainingExample]:
        """Extract fear detection training examples"""
        
        examples = []
        
        for fear_trigger in trace["fear_triggers"]:
            try:
                # Create positive example (fear correctly detected)
                input_text = " ".join(fear_trigger["triggered_by"])
                expected_output = {
                    "fear_detected": True,
                    "fear_code": fear_trigger["fear_code"],
                    "intensity": fear_trigger["intensity"],
                    "archetype": fear_trigger["judge_archetype"]
                }
                
                example = TrainingExample(
                    input_prompt=f"Analyze this text for {fear_trigger['judge_archetype']} fears: {input_text}",
                    expected_output=json.dumps(expected_output),
                    context={"fear_code": fear_trigger["fear_code"]},
                    performance_score=fear_trigger["intensity"],
                    archetype=fear_trigger["judge_archetype"],
                    fear_triggers=[fear_trigger["fear_code"]],
                    outcome_quality="good" if fear_trigger["intensity"] > 0.6 else "poor",
                    feedback_source="fear_detection"
                )
                
                examples.append(example)
                
            except Exception as e:
                logger.warning(f"Failed to extract fear detection example: {e}")
        
        return examples
    
    def _is_high_quality_example(self, example: TrainingExample) -> bool:
        """Determine if example meets quality thresholds"""
        
        return (
            example.performance_score >= self.min_score_improvement and
            len(example.input_prompt) > 50 and  # Reasonable input length
            len(example.expected_output) > 20 and  # Reasonable output length
            example.outcome_quality in ["excellent", "good"]
        )
    
    def _calculate_performance_score(self, decision: Dict[str, Any], trace: Dict[str, Any]) -> float:
        """Calculate how well this decision performed"""
        
        # Look for score improvements after this decision
        decision_time = decision["timestamp"]
        
        score_evolutions = trace["score_evolution"]
        improvements = []
        
        for i, evolution in enumerate(score_evolutions):
            if evolution["timestamp"] > decision_time and i > 0:
                prev_scores = score_evolutions[i-1]["scores"]
                curr_scores = evolution["scores"]
                
                for perspective in curr_scores:
                    if perspective in prev_scores:
                        improvement = curr_scores[perspective] - prev_scores[perspective]
                        improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def _calculate_score_improvement(self, decision: Dict[str, Any], trace: Dict[str, Any]) -> float:
        """Calculate score improvement for refinement decisions"""
        
        # Similar to performance score but more focused on refinement outcomes
        score_evolutions = trace["score_evolution"]
        
        if len(score_evolutions) < 2:
            return 0.0
        
        # Compare last two iterations
        final_scores = score_evolutions[-1]["scores"]
        prev_scores = score_evolutions[-2]["scores"]
        
        improvements = []
        for perspective in final_scores:
            if perspective in prev_scores:
                improvement = final_scores[perspective] - prev_scores[perspective]
                improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def _extract_fear_triggers_from_decision(self, decision: Dict[str, Any]) -> List[str]:
        """Extract fear codes that influenced this decision"""
        
        fear_triggers = []
        for step in decision["reasoning_chain"]:
            if "fear" in step["reasoning"].lower():
                # Extract fear-related terms (simplified)
                fear_triggers.extend([
                    "technical_debt", "vendor_lock", "budget_risk", 
                    "compliance_risk", "brand_damage"
                ])
        
        return list(set(fear_triggers))
    
    def _determine_outcome_quality(self, performance_score: float) -> str:
        """Categorize outcome quality"""
        
        if performance_score >= 3.0:
            return "excellent"
        elif performance_score >= 1.5:
            return "good"
        elif performance_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def _build_judge_prompt(self, input_data: Dict[str, Any], archetype: str) -> str:
        """Build standardized judge prompt for training"""
        
        proposal = input_data.get("proposal_text", "")
        context = input_data.get("context", {})
        
        return f"""Evaluate this business proposal as a {archetype}:

CLIENT: {context.get('client', 'Unknown')}
PROPOSAL:
{proposal}

Provide detailed evaluation focusing on your archetype-specific concerns."""
    
    def _build_judge_expected_output(self, decision: Dict[str, Any]) -> str:
        """Build expected output for judge training"""
        
        # Extract the final evaluation from reasoning chain
        final_step = decision["reasoning_chain"][-1] if decision["reasoning_chain"] else {}
        
        return json.dumps({
            "score": decision.get("final_decision", {}).get("score", 5.0),
            "confidence": decision["confidence_score"],
            "objections": final_step.get("output_data", {}).get("objections", []),
            "suggestions": final_step.get("output_data", {}).get("suggestions", []),
            "reasoning": final_step.get("reasoning", "")
        })
    
    def _build_refiner_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build standardized refiner prompt for training"""
        
        proposal = input_data.get("current_proposal", "")
        objections = input_data.get("objections", [])
        suggestions = input_data.get("suggestions", [])
        
        return f"""Refine this proposal to address the following concerns:

CURRENT PROPOSAL:
{proposal}

OBJECTIONS TO ADDRESS:
{chr(10).join(f'- {obj}' for obj in objections)}

IMPROVEMENT SUGGESTIONS:
{chr(10).join(f'- {sug}' for sug in suggestions)}

Provide improved proposal text:"""

class ModelRetrainingOrchestrator:
    """Orchestrates the continuous retraining process"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_generator = TrainingDataGenerator(config)
        self.performance_tracker = ModelPerformanceTracker()
        
        # Retraining thresholds
        self.min_examples_for_retraining = 100
        self.retraining_interval_days = 7
        self.performance_degradation_threshold = 0.1
    
    async def process_completed_evaluation(self, context_id: str):
        """Process a completed evaluation for training data"""
        
        try:
            # Extract training data
            examples = await self.data_generator.extract_training_data(context_id)
            
            if examples:
                # Store examples
                await self._store_training_examples(examples)
                
                # Update performance metrics
                await self.performance_tracker.update_metrics(context_id, examples)
                
                # Check if retraining is needed
                if await self._should_trigger_retraining():
                    await self._trigger_retraining()
                    
        except Exception as e:
            logger.error(f"Failed to process evaluation for training: {e}")
    
    async def _store_training_examples(self, examples: List[TrainingExample]):
        """Store training examples for later use"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        for archetype in set(ex.archetype for ex in examples):
            archetype_examples = [ex for ex in examples if ex.archetype == archetype]
            
            file_path = self.data_generator.training_data_path / f"{archetype}_{timestamp}.jsonl"
            
            with open(file_path, 'w') as f:
                for example in archetype_examples:
                    f.write(json.dumps(asdict(example)) + '\n')
            
            logger.info(f"Stored {len(archetype_examples)} examples for {archetype}")
    
    async def _should_trigger_retraining(self) -> bool:
        """Determine if retraining should be triggered"""
        
        # Check number of new examples
        total_examples = await self._count_stored_examples()
        
        if total_examples < self.min_examples_for_retraining:
            return False
        
        # Check performance degradation
        recent_performance = await self.performance_tracker.get_recent_performance()
        
        for archetype, metrics in recent_performance.items():
            if metrics.accuracy_score < 0.7:  # Performance threshold
                logger.info(f"Performance degradation detected for {archetype}: {metrics.accuracy_score}")
                return True
        
        # Check time since last retraining
        last_retraining = await self._get_last_retraining_time()
        days_since = (datetime.utcnow() - last_retraining).days
        
        return days_since >= self.retraining_interval_days
    
    async def _trigger_retraining(self):
        """Trigger the retraining pipeline"""
        
        logger.info("Triggering model retraining pipeline")
        
        # This would typically trigger an external MLOps pipeline
        # For now, we'll just log and prepare the data
        
        await self._prepare_retraining_dataset()
        await self._notify_retraining_required()
    
    async def _prepare_retraining_dataset(self):
        """Prepare consolidated dataset for retraining"""
        
        all_examples = []
        
        # Collect all recent training examples
        for file_path in self.data_generator.training_data_path.glob("*.jsonl"):
            with open(file_path, 'r') as f:
                for line in f:
                    example_data = json.loads(line)
                    all_examples.append(TrainingExample(**example_data))
        
        # Split by archetype and quality
        datasets = {
            "high_quality": [ex for ex in all_examples if ex.outcome_quality in ["excellent", "good"]],
            "fear_detection": [ex for ex in all_examples if ex.feedback_source == "fear_detection"],
            "refinement": [ex for ex in all_examples if ex.archetype == "refiner"]
        }
        
        # Save consolidated datasets
        for dataset_name, examples in datasets.items():
            output_path = self.data_generator.training_data_path / f"consolidated_{dataset_name}.jsonl"
            
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps(asdict(example)) + '\n')
            
            logger.info(f"Prepared {len(examples)} examples for {dataset_name} retraining")
    
    async def _notify_retraining_required(self):
        """Notify that retraining is required"""
        
        # This could send notifications, trigger CI/CD pipelines, etc.
        logger.info("Retraining notification sent - dataset ready for ML pipeline")
        
        # Store retraining trigger
        with open(self.data_generator.training_data_path / "retraining_log.json", 'a') as f:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "trigger_reason": "performance_degradation",
                "examples_count": await self._count_stored_examples()
            }
            f.write(json.dumps(log_entry) + '\n')
    
    async def _count_stored_examples(self) -> int:
        """Count total stored training examples"""
        
        total = 0
        for file_path in self.data_generator.training_data_path.glob("*.jsonl"):
            with open(file_path, 'r') as f:
                total += sum(1 for _ in f)
        
        return total
    
    async def _get_last_retraining_time(self) -> datetime:
        """Get timestamp of last retraining"""
        
        log_file = self.data_generator.training_data_path / "retraining_log.json"
        
        if not log_file.exists():
            return datetime.utcnow() - timedelta(days=30)  # Default to 30 days ago
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                return datetime.fromisoformat(last_entry["timestamp"])
        
        return datetime.utcnow() - timedelta(days=30)

class ModelPerformanceTracker:
    """Tracks model performance metrics over time"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[ModelPerformanceMetrics]] = {}
    
    async def update_metrics(self, context_id: str, examples: List[TrainingExample]):
        """Update performance metrics based on new examples"""
        
        for archetype in set(ex.archetype for ex in examples):
            archetype_examples = [ex for ex in examples if ex.archetype == archetype]
            
            # Calculate metrics
            accuracy = sum(1 for ex in archetype_examples if ex.outcome_quality in ["excellent", "good"]) / len(archetype_examples)
            avg_performance = sum(ex.performance_score for ex in archetype_examples) / len(archetype_examples)
            
            metrics = ModelPerformanceMetrics(
                archetype=archetype,
                period="daily",
                accuracy_score=accuracy,
                consistency_score=self._calculate_consistency(archetype_examples),
                improvement_rate=avg_performance,
                confidence_calibration=self._calculate_confidence_calibration(archetype_examples),
                fear_detection_accuracy=self._calculate_fear_accuracy(archetype_examples),
                total_evaluations=len(archetype_examples),
                successful_outcomes=sum(1 for ex in archetype_examples if ex.outcome_quality in ["excellent", "good"])
            )
            
            if archetype not in self.metrics_history:
                self.metrics_history[archetype] = []
            
            self.metrics_history[archetype].append(metrics)
    
    async def get_recent_performance(self) -> Dict[str, ModelPerformanceMetrics]:
        """Get recent performance metrics for all archetypes"""
        
        recent_metrics = {}
        
        for archetype, history in self.metrics_history.items():
            if history:
                recent_metrics[archetype] = history[-1]  # Most recent
        
        return recent_metrics
    
    def _calculate_consistency(self, examples: List[TrainingExample]) -> float:
        """Calculate consistency score for examples"""
        
        if len(examples) < 2:
            return 1.0
        
        scores = [ex.performance_score for ex in examples]
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Lower variance = higher consistency
        return max(0.0, 1.0 - variance / 10.0)
    
    def _calculate_confidence_calibration(self, examples: List[TrainingExample]) -> float:
        """Calculate how well confidence correlates with actual performance"""
        
        # This would require confidence scores from examples
        # For now, return a placeholder
        return 0.8
    
    def _calculate_fear_accuracy(self, examples: List[TrainingExample]) -> float:
        """Calculate fear detection accuracy"""
        
        fear_examples = [ex for ex in examples if ex.feedback_source == "fear_detection"]
        
        if not fear_examples:
            return 1.0
        
        accurate = sum(1 for ex in fear_examples if ex.outcome_quality in ["excellent", "good"])
        return accurate / len(fear_examples)

# Global instances
training_orchestrator = None

def initialize_training_system(config: Dict[str, Any]):
    """Initialize the training system"""
    global training_orchestrator
    training_orchestrator = ModelRetrainingOrchestrator(config)
    logger.info("Training system initialized")

async def process_evaluation_for_training(context_id: str):
    """Process completed evaluation for training data generation"""
    if training_orchestrator:
        await training_orchestrator.process_completed_evaluation(context_id)