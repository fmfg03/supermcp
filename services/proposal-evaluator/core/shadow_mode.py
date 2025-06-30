"""
Shadow Mode - Silent Learning System
==================================

Agentius observes human proposals without intervention, evaluating in parallel
to generate training data and improve without risk.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from .decision_tracer import global_tracer, DecisionType
from .training_engine import TrainingExample, training_orchestrator
from ..agents.specialized_judges import JudgeFactory
from ..utils.logger import setup_logger
from ..utils.config import load_config

logger = setup_logger(__name__)

@dataclass
class ShadowObservation:
    """Single observation in shadow mode"""
    id: str
    timestamp: datetime
    proposal_text: str
    human_outcome: Optional[str]  # "approved", "rejected", "modified"
    human_feedback: Optional[str]
    agentius_prediction: Dict[str, Any]
    accuracy_score: Optional[float]  # How close Agentius was to human decision
    context: Dict[str, Any]
    source: str  # "email", "slack", "document", "meeting"

@dataclass
class ShadowLearningMetrics:
    """Metrics for shadow mode learning"""
    total_observations: int
    prediction_accuracy: float
    judge_accuracy_by_archetype: Dict[str, float]
    common_failure_patterns: List[str]
    improvement_rate: float
    confidence_calibration: float
    false_positive_rate: float
    false_negative_rate: float

class ShadowModeProcessor:
    """
    Processes human proposals in shadow mode without intervention
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.shadow_data_path = Path(config.get("shadow_data_path", "/tmp/agentius_shadow"))
        self.shadow_data_path.mkdir(exist_ok=True)
        
        self.observations: List[ShadowObservation] = []
        self.judge_factory = JudgeFactory()
        
        # Learning thresholds
        self.min_confidence_threshold = 0.6
        self.learning_batch_size = 20
        self.accuracy_improvement_threshold = 0.05
    
    async def observe_proposal(
        self, 
        proposal_text: str,
        context: Dict[str, Any],
        source: str = "unknown"
    ) -> str:
        """Silently observe and evaluate a human proposal"""
        
        observation_id = f"shadow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(proposal_text.encode()).hexdigest()[:8]}"
        
        logger.info(f"Shadow observation started: {observation_id}")
        
        try:
            # Run Agentius evaluation silently
            agentius_prediction = await self._run_silent_evaluation(
                proposal_text, context, observation_id
            )
            
            # Create observation record
            observation = ShadowObservation(
                id=observation_id,
                timestamp=datetime.utcnow(),
                proposal_text=proposal_text,
                human_outcome=None,  # Will be filled later
                human_feedback=None,
                agentius_prediction=agentius_prediction,
                accuracy_score=None,
                context=context,
                source=source
            )
            
            # Store observation
            await self._store_observation(observation)
            self.observations.append(observation)
            
            logger.info(f"Shadow observation completed: {observation_id}")
            return observation_id
            
        except Exception as e:
            logger.error(f"Shadow observation failed: {e}")
            return ""
    
    async def record_human_outcome(
        self, 
        observation_id: str,
        human_outcome: str,
        human_feedback: Optional[str] = None
    ):
        """Record the actual human decision for comparison"""
        
        # Find observation
        observation = next(
            (obs for obs in self.observations if obs.id == observation_id), 
            None
        )
        
        if not observation:
            logger.warning(f"Observation {observation_id} not found")
            return
        
        # Update observation with human outcome
        observation.human_outcome = human_outcome
        observation.human_feedback = human_feedback
        
        # Calculate accuracy
        accuracy = await self._calculate_prediction_accuracy(observation)
        observation.accuracy_score = accuracy
        
        # Update stored observation
        await self._update_stored_observation(observation)
        
        # Generate training data if accuracy is useful
        if accuracy is not None:
            await self._generate_shadow_training_data(observation)
        
        # Check if we should trigger learning update
        if len(self.observations) % self.learning_batch_size == 0:
            await self._trigger_learning_update()
        
        logger.info(f"Human outcome recorded for {observation_id}: {human_outcome} (accuracy: {accuracy})")
    
    async def _run_silent_evaluation(
        self, 
        proposal_text: str,
        context: Dict[str, Any],
        observation_id: str
    ) -> Dict[str, Any]:
        """Run full Agentius evaluation silently"""
        
        # Start shadow trace
        global_tracer.start_trace(observation_id, {
            "mode": "shadow",
            "client": context.get("client", "Unknown"),
            "source": context.get("source", "unknown")
        })
        
        try:
            # Run judge evaluations
            judge_results = await self._run_shadow_judges(proposal_text, context, observation_id)
            
            # Calculate aggregate scores
            avg_score = sum(j["score"] for j in judge_results) / len(judge_results)
            
            # Make prediction
            prediction = {
                "overall_score": avg_score,
                "recommendation": "approve" if avg_score >= 7.0 else "reject" if avg_score < 5.0 else "modify",
                "confidence": self._calculate_prediction_confidence(judge_results),
                "judge_evaluations": judge_results,
                "key_concerns": self._extract_key_concerns(judge_results),
                "improvement_suggestions": self._extract_suggestions(judge_results)
            }
            
            # Complete trace
            global_tracer.complete_trace(observation_id, "shadow_complete")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Silent evaluation failed: {e}")
            global_tracer.complete_trace(observation_id, "shadow_failed")
            return {"error": str(e)}
    
    async def _run_shadow_judges(
        self, 
        proposal_text: str,
        context: Dict[str, Any],
        observation_id: str
    ) -> List[Dict[str, Any]]:
        """Run judge evaluations in shadow mode"""
        
        # Use standard archetypes
        archetypes = ["technical_founder", "conservative_cfo", "growth_cmo"]
        judge_results = []
        
        for archetype in archetypes:
            try:
                # Create judge
                judge = self.judge_factory.create_judge(archetype, self.config)
                
                # Run evaluation
                evaluation = await judge.evaluate(proposal_text, context, iteration=1)
                
                # Convert to dict
                result = {
                    "archetype": archetype,
                    "score": evaluation.score,
                    "confidence": getattr(evaluation, 'confidence', 0.7),
                    "objections": evaluation.objections,
                    "suggestions": evaluation.suggestions,
                    "strengths": evaluation.strengths,
                    "concerns": evaluation.concerns
                }
                
                judge_results.append(result)
                
                # Add to trace
                global_tracer.add_decision_point(
                    observation_id,
                    DecisionType.JUDGE_EVALUATION,
                    f"shadow_{archetype}_judge",
                    [],  # No detailed reasoning chain in shadow mode
                    result,
                    result["confidence"]
                )
                
            except Exception as e:
                logger.warning(f"Shadow judge {archetype} failed: {e}")
        
        return judge_results
    
    def _calculate_prediction_confidence(self, judge_results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in prediction"""
        
        if not judge_results:
            return 0.0
        
        # Average judge confidence
        avg_confidence = sum(j["confidence"] for j in judge_results) / len(judge_results)
        
        # Score consistency (lower variance = higher confidence)
        scores = [j["score"] for j in judge_results]
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            consistency_factor = max(0.0, 1.0 - variance / 10.0)
        else:
            consistency_factor = 1.0
        
        return avg_confidence * consistency_factor
    
    def _extract_key_concerns(self, judge_results: List[Dict[str, Any]]) -> List[str]:
        """Extract most common concerns across judges"""
        
        all_concerns = []
        for result in judge_results:
            all_concerns.extend(result.get("concerns", []))
            all_concerns.extend(result.get("objections", []))
        
        # Return unique concerns
        return list(set(all_concerns))
    
    def _extract_suggestions(self, judge_results: List[Dict[str, Any]]) -> List[str]:
        """Extract improvement suggestions"""
        
        all_suggestions = []
        for result in judge_results:
            all_suggestions.extend(result.get("suggestions", []))
        
        return list(set(all_suggestions))
    
    async def _calculate_prediction_accuracy(self, observation: ShadowObservation) -> Optional[float]:
        """Calculate how accurate Agentius prediction was vs human decision"""
        
        if not observation.human_outcome or not observation.agentius_prediction:
            return None
        
        human_outcome = observation.human_outcome.lower()
        agentius_recommendation = observation.agentius_prediction.get("recommendation", "").lower()
        
        # Direct match
        if human_outcome == agentius_recommendation:
            return 1.0
        
        # Partial matches
        if human_outcome == "approved" and agentius_recommendation in ["approve", "modify"]:
            return 0.7
        elif human_outcome == "rejected" and agentius_recommendation in ["reject", "modify"]:
            return 0.7
        elif human_outcome == "modified" and agentius_recommendation in ["modify", "approve"]:
            return 0.8
        else:
            return 0.0
    
    async def _generate_shadow_training_data(self, observation: ShadowObservation):
        """Generate training data from shadow observation"""
        
        if observation.accuracy_score is None or observation.accuracy_score < 0.5:
            return  # Don't learn from inaccurate predictions
        
        training_examples = []
        
        # Generate examples for each judge
        for judge_result in observation.agentius_prediction.get("judge_evaluations", []):
            
            archetype = judge_result["archetype"]
            
            # Create training example
            example = TrainingExample(
                input_prompt=f"Evaluate this proposal as a {archetype}: {observation.proposal_text}",
                expected_output=json.dumps({
                    "score": judge_result["score"],
                    "objections": judge_result["objections"],
                    "suggestions": judge_result["suggestions"]
                }),
                context={
                    "archetype": archetype,
                    "human_outcome": observation.human_outcome,
                    "source": observation.source
                },
                performance_score=observation.accuracy_score,
                archetype=archetype,
                fear_triggers=[],
                outcome_quality="excellent" if observation.accuracy_score > 0.8 else "good",
                feedback_source="shadow_learning"
            )
            
            training_examples.append(example)
        
        # Store training examples
        if training_examples and training_orchestrator:
            await training_orchestrator._store_training_examples(training_examples)
            logger.info(f"Generated {len(training_examples)} shadow training examples")
    
    async def _store_observation(self, observation: ShadowObservation):
        """Store observation to disk"""
        
        file_path = self.shadow_data_path / f"{observation.id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(asdict(observation), f, default=str, indent=2)
    
    async def _update_stored_observation(self, observation: ShadowObservation):
        """Update stored observation with human outcome"""
        
        file_path = self.shadow_data_path / f"{observation.id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(asdict(observation), f, default=str, indent=2)
    
    async def _trigger_learning_update(self):
        """Trigger learning update based on accumulated observations"""
        
        # Calculate current metrics
        metrics = await self.calculate_shadow_metrics()
        
        logger.info(f"Shadow learning update: accuracy={metrics.prediction_accuracy:.2f}")
        
        # Check if improvement is needed
        if metrics.prediction_accuracy < 0.7:
            logger.info("Prediction accuracy below threshold - triggering retraining")
            
            if training_orchestrator:
                await training_orchestrator._trigger_retraining()
    
    async def calculate_shadow_metrics(self) -> ShadowLearningMetrics:
        """Calculate comprehensive shadow learning metrics"""
        
        observations_with_outcomes = [
            obs for obs in self.observations 
            if obs.human_outcome and obs.accuracy_score is not None
        ]
        
        if not observations_with_outcomes:
            return ShadowLearningMetrics(
                total_observations=0,
                prediction_accuracy=0.0,
                judge_accuracy_by_archetype={},
                common_failure_patterns=[],
                improvement_rate=0.0,
                confidence_calibration=0.0,
                false_positive_rate=0.0,
                false_negative_rate=0.0
            )
        
        # Overall accuracy
        total_accuracy = sum(obs.accuracy_score for obs in observations_with_outcomes) / len(observations_with_outcomes)
        
        # Accuracy by archetype
        archetype_accuracy = {}
        for archetype in ["technical_founder", "conservative_cfo", "growth_cmo"]:
            archetype_scores = []
            
            for obs in observations_with_outcomes:
                judge_evals = obs.agentius_prediction.get("judge_evaluations", [])
                archetype_eval = next((j for j in judge_evals if j["archetype"] == archetype), None)
                
                if archetype_eval:
                    # Calculate archetype-specific accuracy
                    archetype_scores.append(obs.accuracy_score)
            
            if archetype_scores:
                archetype_accuracy[archetype] = sum(archetype_scores) / len(archetype_scores)
        
        # Failure patterns
        failure_patterns = self._analyze_failure_patterns(observations_with_outcomes)
        
        # Improvement rate (last 10 vs previous 10)
        improvement_rate = self._calculate_improvement_rate(observations_with_outcomes)
        
        # False positive/negative rates
        fp_rate, fn_rate = self._calculate_error_rates(observations_with_outcomes)
        
        return ShadowLearningMetrics(
            total_observations=len(observations_with_outcomes),
            prediction_accuracy=total_accuracy,
            judge_accuracy_by_archetype=archetype_accuracy,
            common_failure_patterns=failure_patterns,
            improvement_rate=improvement_rate,
            confidence_calibration=self._calculate_confidence_calibration(observations_with_outcomes),
            false_positive_rate=fp_rate,
            false_negative_rate=fn_rate
        )
    
    def _analyze_failure_patterns(self, observations: List[ShadowObservation]) -> List[str]:
        """Analyze common patterns in failed predictions"""
        
        failures = [obs for obs in observations if obs.accuracy_score < 0.5]
        
        patterns = []
        
        # Analyze by source
        source_failures = {}
        for obs in failures:
            source = obs.source
            if source not in source_failures:
                source_failures[source] = 0
            source_failures[source] += 1
        
        if source_failures:
            worst_source = max(source_failures, key=source_failures.get)
            if source_failures[worst_source] > len(failures) * 0.3:
                patterns.append(f"High failure rate with {worst_source} source")
        
        # Analyze by human feedback themes
        feedback_themes = []
        for obs in failures:
            if obs.human_feedback:
                feedback_themes.append(obs.human_feedback.lower())
        
        common_feedback = set()
        for feedback in feedback_themes:
            if "budget" in feedback:
                common_feedback.add("budget_concerns")
            if "timeline" in feedback or "time" in feedback:
                common_feedback.add("timeline_concerns")
            if "risk" in feedback:
                common_feedback.add("risk_concerns")
        
        patterns.extend(list(common_feedback))
        
        return patterns[:5]  # Top 5 patterns
    
    def _calculate_improvement_rate(self, observations: List[ShadowObservation]) -> float:
        """Calculate improvement rate over time"""
        
        if len(observations) < 20:
            return 0.0
        
        # Sort by timestamp
        sorted_obs = sorted(observations, key=lambda x: x.timestamp)
        
        # Compare first half vs second half
        midpoint = len(sorted_obs) // 2
        first_half = sorted_obs[:midpoint]
        second_half = sorted_obs[midpoint:]
        
        first_avg = sum(obs.accuracy_score for obs in first_half) / len(first_half)
        second_avg = sum(obs.accuracy_score for obs in second_half) / len(second_half)
        
        return second_avg - first_avg
    
    def _calculate_error_rates(self, observations: List[ShadowObservation]) -> Tuple[float, float]:
        """Calculate false positive and false negative rates"""
        
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        for obs in observations:
            human_approved = obs.human_outcome.lower() in ["approved", "modified"]
            agentius_approved = obs.agentius_prediction.get("recommendation", "").lower() in ["approve", "modify"]
            
            if human_approved and agentius_approved:
                true_positives += 1
            elif not human_approved and not agentius_approved:
                true_negatives += 1
            elif not human_approved and agentius_approved:
                false_positives += 1
            elif human_approved and not agentius_approved:
                false_negatives += 1
        
        total_negative = true_negatives + false_positives
        total_positive = true_positives + false_negatives
        
        fp_rate = false_positives / total_negative if total_negative > 0 else 0.0
        fn_rate = false_negatives / total_positive if total_positive > 0 else 0.0
        
        return fp_rate, fn_rate
    
    def _calculate_confidence_calibration(self, observations: List[ShadowObservation]) -> float:
        """Calculate how well confidence correlates with accuracy"""
        
        if len(observations) < 5:
            return 0.5
        
        # Group by confidence levels
        high_conf = [obs for obs in observations if obs.agentius_prediction.get("confidence", 0) > 0.8]
        low_conf = [obs for obs in observations if obs.agentius_prediction.get("confidence", 0) < 0.5]
        
        if not high_conf or not low_conf:
            return 0.5
        
        high_conf_accuracy = sum(obs.accuracy_score for obs in high_conf) / len(high_conf)
        low_conf_accuracy = sum(obs.accuracy_score for obs in low_conf) / len(low_conf)
        
        # Good calibration means high confidence predictions are more accurate
        calibration = high_conf_accuracy - low_conf_accuracy
        
        return max(0.0, min(1.0, calibration + 0.5))
    
    async def get_shadow_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive shadow mode report"""
        
        # Filter recent observations
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_observations = [
            obs for obs in self.observations 
            if obs.timestamp >= cutoff_date
        ]
        
        if not recent_observations:
            return {"error": "No shadow observations in the specified period"}
        
        # Calculate metrics
        metrics = await self.calculate_shadow_metrics()
        
        # Performance trends
        weekly_accuracy = self._calculate_weekly_accuracy_trend(recent_observations)
        
        # Top insights
        insights = []
        
        if metrics.prediction_accuracy > 0.8:
            insights.append("Shadow predictions are highly accurate - ready for increased autonomy")
        elif metrics.prediction_accuracy < 0.6:
            insights.append("Prediction accuracy needs improvement - more training data required")
        
        if metrics.improvement_rate > 0.1:
            insights.append("Learning system is improving over time")
        elif metrics.improvement_rate < -0.05:
            insights.append("Performance degradation detected - investigation needed")
        
        if metrics.false_positive_rate > 0.3:
            insights.append("High false positive rate - Agentius too optimistic")
        
        if metrics.false_negative_rate > 0.3:
            insights.append("High false negative rate - Agentius too pessimistic")
        
        return {
            "period_summary": {
                "days_analyzed": days,
                "total_observations": len(recent_observations),
                "observations_with_outcomes": len([obs for obs in recent_observations if obs.human_outcome]),
                "accuracy_score": metrics.prediction_accuracy,
                "improvement_rate": metrics.improvement_rate
            },
            "performance_metrics": asdict(metrics),
            "accuracy_trends": weekly_accuracy,
            "key_insights": insights,
            "archetype_performance": {
                archetype: {
                    "accuracy": accuracy,
                    "status": "excellent" if accuracy > 0.8 else "good" if accuracy > 0.6 else "needs_improvement"
                }
                for archetype, accuracy in metrics.judge_accuracy_by_archetype.items()
            },
            "learning_recommendations": self._generate_learning_recommendations(metrics),
            "data_quality": {
                "outcome_completion_rate": len([obs for obs in recent_observations if obs.human_outcome]) / len(recent_observations),
                "feedback_completion_rate": len([obs for obs in recent_observations if obs.human_feedback]) / len(recent_observations),
                "source_distribution": self._calculate_source_distribution(recent_observations)
            }
        }
    
    def _calculate_weekly_accuracy_trend(self, observations: List[ShadowObservation]) -> List[Dict[str, Any]]:
        """Calculate weekly accuracy trends"""
        
        # Group by week
        weekly_data = {}
        
        for obs in observations:
            if obs.accuracy_score is None:
                continue
                
            week_start = obs.timestamp - timedelta(days=obs.timestamp.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            
            weekly_data[week_key].append(obs.accuracy_score)
        
        # Calculate weekly averages
        weekly_trends = []
        for week, scores in sorted(weekly_data.items()):
            avg_accuracy = sum(scores) / len(scores)
            weekly_trends.append({
                "week": week,
                "accuracy": avg_accuracy,
                "observations": len(scores)
            })
        
        return weekly_trends
    
    def _calculate_source_distribution(self, observations: List[ShadowObservation]) -> Dict[str, int]:
        """Calculate distribution of observation sources"""
        
        source_counts = {}
        for obs in observations:
            source = obs.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return source_counts
    
    def _generate_learning_recommendations(self, metrics: ShadowLearningMetrics) -> List[str]:
        """Generate recommendations for improving shadow learning"""
        
        recommendations = []
        
        if metrics.prediction_accuracy < 0.7:
            recommendations.append("Increase training data collection from shadow observations")
        
        if metrics.confidence_calibration < 0.6:
            recommendations.append("Improve confidence calibration training")
        
        if metrics.false_positive_rate > 0.3:
            recommendations.append("Add more conservative evaluation criteria")
        
        if metrics.false_negative_rate > 0.3:
            recommendations.append("Reduce evaluation strictness for approval decisions")
        
        # Archetype-specific recommendations
        for archetype, accuracy in metrics.judge_accuracy_by_archetype.items():
            if accuracy < 0.6:
                recommendations.append(f"Focus training on {archetype} archetype - accuracy below threshold")
        
        if "budget_concerns" in metrics.common_failure_patterns:
            recommendations.append("Improve budget and financial analysis capabilities")
        
        if "timeline_concerns" in metrics.common_failure_patterns:
            recommendations.append("Add timeline feasibility evaluation")
        
        return recommendations

# Global shadow processor
shadow_processor = None

def initialize_shadow_mode(config: Dict[str, Any]):
    """Initialize shadow mode processor"""
    global shadow_processor
    shadow_processor = ShadowModeProcessor(config)
    logger.info("Shadow mode initialized")

async def observe_proposal_silently(
    proposal_text: str,
    context: Dict[str, Any],
    source: str = "unknown"
) -> str:
    """Silently observe a proposal (main entry point)"""
    if shadow_processor:
        return await shadow_processor.observe_proposal(proposal_text, context, source)
    return ""

async def record_human_decision(
    observation_id: str,
    human_outcome: str,
    human_feedback: Optional[str] = None
):
    """Record human decision for shadow learning"""
    if shadow_processor:
        await shadow_processor.record_human_outcome(observation_id, human_outcome, human_feedback)