"""
Decision Traceability System for Agentius
========================================

Tracks the complete reasoning chain, decision paths, and score evolution
for transparency, reproducibility, and training data generation.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class DecisionType(Enum):
    """Types of decisions tracked in the system"""
    PROPOSAL_GENERATION = "proposal_generation"
    JUDGE_EVALUATION = "judge_evaluation"
    FEAR_TRIGGER_ANALYSIS = "fear_trigger_analysis"
    REFINEMENT_STRATEGY = "refinement_strategy"
    ITERATION_DECISION = "iteration_decision"
    TERMINATION_DECISION = "termination_decision"
    VARIANT_COMPARISON = "variant_comparison"

@dataclass
class ReasoningStep:
    """Individual step in the reasoning chain"""
    id: str
    step_type: str
    input_data: Dict[str, Any]
    reasoning: str
    output_data: Dict[str, Any]
    confidence: float
    alternatives_considered: List[str]
    timestamp: datetime

@dataclass
class DecisionPoint:
    """Critical decision point in the evaluation process"""
    id: str
    decision_type: DecisionType
    context: Dict[str, Any]
    reasoning_chain: List[ReasoningStep]
    final_decision: Any
    confidence_score: float
    influencing_factors: List[str]
    timestamp: datetime
    agent_id: str

@dataclass
class ScoreEvolution:
    """Tracks how scores change over iterations"""
    iteration: int
    timestamp: datetime
    scores: Dict[str, float]  # perspective -> score
    changes_from_previous: Dict[str, float]
    reasons_for_change: Dict[str, str]
    triggered_improvements: List[str]

@dataclass
class FearTriggerTrace:
    """Tracks fear code triggers and their impact"""
    judge_archetype: str
    fear_code: str
    intensity: float
    triggered_by: List[str]  # Text snippets that triggered
    resulting_objections: List[str]
    mitigation_attempted: bool
    mitigation_success: Optional[bool]

class DecisionTracer:
    """
    Main traceability system for Agentius decisions
    Provides complete audit trail and reasoning transparency
    """
    
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}  # context_id -> trace data
        
    def start_trace(self, context_id: str, initial_context: Dict[str, Any]):
        """Start tracing for a new evaluation context"""
        self.traces[context_id] = {
            "context_id": context_id,
            "started_at": datetime.utcnow(),
            "initial_context": initial_context,
            "decision_points": [],
            "score_evolution": [],
            "fear_triggers": [],
            "agent_interactions": [],
            "metadata": {
                "total_decisions": 0,
                "total_reasoning_steps": 0,
                "completion_status": "active"
            }
        }
        
        logger.info(f"Started decision trace for context {context_id}")
    
    def add_decision_point(
        self, 
        context_id: str, 
        decision_type: DecisionType,
        agent_id: str,
        reasoning_chain: List[ReasoningStep],
        final_decision: Any,
        confidence: float,
        context: Dict[str, Any] = None
    ) -> str:
        """Add a decision point to the trace"""
        
        if context_id not in self.traces:
            logger.warning(f"No trace found for context {context_id}")
            return ""
        
        decision_id = str(uuid.uuid4())
        
        decision_point = DecisionPoint(
            id=decision_id,
            decision_type=decision_type,
            context=context or {},
            reasoning_chain=reasoning_chain,
            final_decision=final_decision,
            confidence_score=confidence,
            influencing_factors=self._extract_influencing_factors(reasoning_chain),
            timestamp=datetime.utcnow(),
            agent_id=agent_id
        )
        
        self.traces[context_id]["decision_points"].append(asdict(decision_point))
        self.traces[context_id]["metadata"]["total_decisions"] += 1
        self.traces[context_id]["metadata"]["total_reasoning_steps"] += len(reasoning_chain)
        
        logger.debug(f"Added decision point {decision_id} for context {context_id}")
        return decision_id
    
    def add_score_evolution(
        self, 
        context_id: str,
        iteration: int,
        scores: Dict[str, float],
        reasons_for_change: Dict[str, str] = None
    ):
        """Track score evolution over iterations"""
        
        if context_id not in self.traces:
            return
        
        previous_scores = {}
        if self.traces[context_id]["score_evolution"]:
            previous_scores = self.traces[context_id]["score_evolution"][-1]["scores"]
        
        changes = {
            perspective: scores.get(perspective, 0) - previous_scores.get(perspective, 0)
            for perspective in scores
        }
        
        evolution = ScoreEvolution(
            iteration=iteration,
            timestamp=datetime.utcnow(),
            scores=scores,
            changes_from_previous=changes,
            reasons_for_change=reasons_for_change or {},
            triggered_improvements=self._identify_improvements(changes)
        )
        
        self.traces[context_id]["score_evolution"].append(asdict(evolution))
    
    def add_fear_trigger(
        self,
        context_id: str,
        judge_archetype: str,
        fear_code: str,
        intensity: float,
        triggered_by: List[str],
        objections: List[str]
    ):
        """Track fear code triggers and their impact"""
        
        if context_id not in self.traces:
            return
        
        trigger_trace = FearTriggerTrace(
            judge_archetype=judge_archetype,
            fear_code=fear_code,
            intensity=intensity,
            triggered_by=triggered_by,
            resulting_objections=objections,
            mitigation_attempted=False,
            mitigation_success=None
        )
        
        self.traces[context_id]["fear_triggers"].append(asdict(trigger_trace))
    
    def update_fear_mitigation(
        self,
        context_id: str,
        fear_code: str,
        mitigation_attempted: bool,
        success: bool
    ):
        """Update fear mitigation results"""
        
        if context_id not in self.traces:
            return
        
        for trigger in self.traces[context_id]["fear_triggers"]:
            if trigger["fear_code"] == fear_code:
                trigger["mitigation_attempted"] = mitigation_attempted
                trigger["mitigation_success"] = success
                break
    
    def add_reasoning_step(
        self,
        step_type: str,
        input_data: Dict[str, Any],
        reasoning: str,
        output_data: Dict[str, Any],
        confidence: float,
        alternatives: List[str] = None
    ) -> ReasoningStep:
        """Create a reasoning step for inclusion in decision points"""
        
        return ReasoningStep(
            id=str(uuid.uuid4()),
            step_type=step_type,
            input_data=input_data,
            reasoning=reasoning,
            output_data=output_data,
            confidence=confidence,
            alternatives_considered=alternatives or [],
            timestamp=datetime.utcnow()
        )
    
    def complete_trace(self, context_id: str, status: str = "completed"):
        """Mark a trace as complete"""
        
        if context_id not in self.traces:
            return
        
        self.traces[context_id]["completed_at"] = datetime.utcnow()
        self.traces[context_id]["metadata"]["completion_status"] = status
        
        # Calculate final metrics
        self._calculate_final_metrics(context_id)
        
        logger.info(f"Completed trace for context {context_id} with status {status}")
    
    def get_trace(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get complete trace for a context"""
        return self.traces.get(context_id)
    
    def get_decision_path(self, context_id: str) -> List[Dict[str, Any]]:
        """Get the sequence of decisions for a context"""
        trace = self.traces.get(context_id)
        if not trace:
            return []
        
        return sorted(
            trace["decision_points"], 
            key=lambda x: x["timestamp"]
        )
    
    def get_score_history(self, context_id: str) -> List[Dict[str, Any]]:
        """Get score evolution history"""
        trace = self.traces.get(context_id)
        if not trace:
            return []
        
        return trace["score_evolution"]
    
    def get_fear_analysis(self, context_id: str) -> Dict[str, Any]:
        """Get fear trigger analysis"""
        trace = self.traces.get(context_id)
        if not trace:
            return {}
        
        fears = trace["fear_triggers"]
        
        return {
            "total_triggers": len(fears),
            "unique_fears": len(set(f["fear_code"] for f in fears)),
            "avg_intensity": sum(f["intensity"] for f in fears) / len(fears) if fears else 0,
            "mitigation_success_rate": len([f for f in fears if f.get("mitigation_success")]) / len(fears) if fears else 0,
            "most_triggered_fears": self._get_most_triggered_fears(fears),
            "archetype_fear_distribution": self._get_archetype_fear_distribution(fears)
        }
    
    def generate_transparency_report(self, context_id: str) -> str:
        """Generate human-readable transparency report"""
        trace = self.traces.get(context_id)
        if not trace:
            return "No trace found for this context."
        
        report = f"""# Agentius Decision Transparency Report
Context ID: {context_id}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Executive Summary
- Total Decisions Made: {trace['metadata']['total_decisions']}
- Total Reasoning Steps: {trace['metadata']['total_reasoning_steps']}
- Evaluation Status: {trace['metadata']['completion_status']}
- Duration: {self._calculate_duration(trace)}

## Score Evolution
"""
        
        for evolution in trace["score_evolution"]:
            report += f"\n### Iteration {evolution['iteration']}\n"
            for perspective, score in evolution["scores"].items():
                change = evolution["changes_from_previous"].get(perspective, 0)
                change_str = f" (+{change:.1f})" if change > 0 else f" ({change:.1f})" if change < 0 else ""
                report += f"- {perspective}: {score:.1f}/10{change_str}\n"
        
        report += "\n## Fear Code Analysis\n"
        fear_analysis = self.get_fear_analysis(context_id)
        report += f"- Total Fear Triggers: {fear_analysis['total_triggers']}\n"
        report += f"- Average Intensity: {fear_analysis['avg_intensity']:.2f}\n"
        report += f"- Mitigation Success Rate: {fear_analysis['mitigation_success_rate']:.1%}\n"
        
        report += "\n## Key Decisions\n"
        for decision in trace["decision_points"]:
            report += f"\n### {decision['decision_type']} by {decision['agent_id']}\n"
            report += f"Confidence: {decision['confidence_score']:.2f}\n"
            report += f"Reasoning Steps: {len(decision['reasoning_chain'])}\n"
        
        return report
    
    def export_training_data(self, context_id: str) -> Dict[str, Any]:
        """Export trace data suitable for training judge models"""
        trace = self.traces.get(context_id)
        if not trace:
            return {}
        
        return {
            "context": trace["initial_context"],
            "decision_sequence": self.get_decision_path(context_id),
            "score_progression": self.get_score_history(context_id),
            "fear_triggers": trace["fear_triggers"],
            "final_outcome": {
                "status": trace["metadata"]["completion_status"],
                "final_scores": trace["score_evolution"][-1]["scores"] if trace["score_evolution"] else {},
                "total_iterations": len(trace["score_evolution"])
            },
            "patterns": {
                "common_objections": self._extract_common_objections(trace),
                "effective_mitigations": self._extract_effective_mitigations(trace),
                "score_improvement_triggers": self._extract_improvement_triggers(trace)
            }
        }
    
    def _extract_influencing_factors(self, reasoning_chain: List[ReasoningStep]) -> List[str]:
        """Extract key influencing factors from reasoning chain"""
        factors = []
        for step in reasoning_chain:
            if step.confidence > 0.7:  # High confidence steps are likely influential
                factors.append(step.step_type)
        return factors
    
    def _identify_improvements(self, changes: Dict[str, float]) -> List[str]:
        """Identify what triggered score improvements"""
        improvements = []
        for perspective, change in changes.items():
            if change > 0.5:  # Significant improvement
                improvements.append(f"{perspective}_improvement")
        return improvements
    
    def _get_most_triggered_fears(self, fears: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get most frequently triggered fears"""
        fear_counts = {}
        for fear in fears:
            fear_code = fear["fear_code"]
            if fear_code not in fear_counts:
                fear_counts[fear_code] = {"count": 0, "total_intensity": 0}
            fear_counts[fear_code]["count"] += 1
            fear_counts[fear_code]["total_intensity"] += fear["intensity"]
        
        return sorted(
            [
                {
                    "fear_code": code, 
                    "count": data["count"],
                    "avg_intensity": data["total_intensity"] / data["count"]
                }
                for code, data in fear_counts.items()
            ],
            key=lambda x: x["count"] * x["avg_intensity"],
            reverse=True
        )[:5]
    
    def _get_archetype_fear_distribution(self, fears: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of fears by archetype"""
        distribution = {}
        for fear in fears:
            archetype = fear["judge_archetype"]
            distribution[archetype] = distribution.get(archetype, 0) + 1
        return distribution
    
    def _calculate_duration(self, trace: Dict[str, Any]) -> str:
        """Calculate trace duration"""
        start = datetime.fromisoformat(trace["started_at"].replace('Z', '+00:00')) if isinstance(trace["started_at"], str) else trace["started_at"]
        end = datetime.fromisoformat(trace.get("completed_at", datetime.utcnow().isoformat()).replace('Z', '+00:00')) if isinstance(trace.get("completed_at"), str) else trace.get("completed_at", datetime.utcnow())
        
        duration = end - start
        return f"{duration.total_seconds():.1f} seconds"
    
    def _calculate_final_metrics(self, context_id: str):
        """Calculate final metrics for the trace"""
        trace = self.traces[context_id]
        
        # Add summary metrics
        trace["metadata"]["final_metrics"] = {
            "decision_efficiency": len(trace["decision_points"]) / len(trace["score_evolution"]) if trace["score_evolution"] else 0,
            "fear_mitigation_rate": len([f for f in trace["fear_triggers"] if f.get("mitigation_success")]) / len(trace["fear_triggers"]) if trace["fear_triggers"] else 0,
            "score_improvement": self._calculate_total_score_improvement(trace),
            "reasoning_depth": sum(len(d["reasoning_chain"]) for d in trace["decision_points"]) / len(trace["decision_points"]) if trace["decision_points"] else 0
        }
    
    def _calculate_total_score_improvement(self, trace: Dict[str, Any]) -> float:
        """Calculate total score improvement across all perspectives"""
        if not trace["score_evolution"]:
            return 0
        
        initial = trace["score_evolution"][0]["scores"]
        final = trace["score_evolution"][-1]["scores"]
        
        improvements = [final.get(p, 0) - initial.get(p, 0) for p in initial.keys()]
        return sum(improvements) / len(improvements) if improvements else 0
    
    def _extract_common_objections(self, trace: Dict[str, Any]) -> List[str]:
        """Extract common objection patterns for training data"""
        objections = []
        for trigger in trace["fear_triggers"]:
            objections.extend(trigger["resulting_objections"])
        return list(set(objections))
    
    def _extract_effective_mitigations(self, trace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract effective mitigation strategies"""
        effective = []
        for trigger in trace["fear_triggers"]:
            if trigger.get("mitigation_success"):
                effective.append({
                    "fear_code": trigger["fear_code"],
                    "archetype": trigger["judge_archetype"],
                    "objections": trigger["resulting_objections"]
                })
        return effective
    
    def _extract_improvement_triggers(self, trace: Dict[str, Any]) -> List[str]:
        """Extract what triggered score improvements"""
        triggers = []
        for evolution in trace["score_evolution"]:
            triggers.extend(evolution["triggered_improvements"])
        return list(set(triggers))

# Global tracer instance
global_tracer = DecisionTracer()