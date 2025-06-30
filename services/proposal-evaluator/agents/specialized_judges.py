"""
Specialized Judge Agents - Archetypal client decision makers
==========================================================

Each judge agent represents a specific client archetype with their unique
"fear codes" and decision-making patterns.
"""

import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

from .judge_agent import JudgeEvaluation
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class FearCode:
    """Specific fear/concern patterns for each archetype"""
    name: str
    triggers: List[str]  # Keywords/patterns that trigger this fear
    intensity: float  # 0.0 to 1.0
    objection_templates: List[str]
    mitigation_strategies: List[str]

class SpecializedJudge(ABC):
    """Base class for specialized judge agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = LLMClient(config.get("llm", {}))
        self.version = "2.0.0"
        self.fear_codes = self._define_fear_codes()
        self.decision_patterns = self._define_decision_patterns()
        
    @abstractmethod
    def _define_fear_codes(self) -> List[FearCode]:
        """Define the specific fears/concerns for this archetype"""
        pass
    
    @abstractmethod
    def _define_decision_patterns(self) -> Dict[str, Any]:
        """Define decision-making patterns for this archetype"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the specialized system prompt for this judge"""
        pass
    
    async def evaluate(self, proposal: str, context, iteration: int = 1) -> JudgeEvaluation:
        """Evaluate proposal with archetype-specific lens"""
        
        # Analyze proposal for fear triggers
        triggered_fears = self._analyze_fear_triggers(proposal)
        
        # Build specialized evaluation prompt
        prompt = self._build_specialized_prompt(proposal, context, triggered_fears, iteration)
        
        # Generate evaluation
        response = await self.llm_client.generate(
            system_prompt=self._get_system_prompt(),
            user_prompt=prompt,
            temperature=0.2,  # Lower temperature for consistent archetype behavior
            max_tokens=2000
        )
        
        # Parse with archetype-specific logic
        evaluation = self._parse_archetype_evaluation(response, triggered_fears)
        
        return evaluation
    
    def _analyze_fear_triggers(self, proposal: str) -> List[FearCode]:
        """Analyze proposal text for fear-triggering patterns"""
        triggered = []
        proposal_lower = proposal.lower()
        
        for fear in self.fear_codes:
            trigger_count = sum(1 for trigger in fear.triggers if trigger.lower() in proposal_lower)
            if trigger_count > 0:
                # Adjust intensity based on trigger frequency
                adjusted_fear = FearCode(
                    name=fear.name,
                    triggers=fear.triggers,
                    intensity=min(1.0, fear.intensity * (1 + trigger_count * 0.2)),
                    objection_templates=fear.objection_templates,
                    mitigation_strategies=fear.mitigation_strategies
                )
                triggered.append(adjusted_fear)
        
        return sorted(triggered, key=lambda x: x.intensity, reverse=True)
    
    def _build_specialized_prompt(
        self, 
        proposal: str, 
        context, 
        triggered_fears: List[FearCode], 
        iteration: int
    ) -> str:
        """Build prompt with archetype-specific context"""
        
        fear_context = ""
        if triggered_fears:
            fear_context = f"\nTRIGGERED CONCERNS (based on your archetype):\n"
            for fear in triggered_fears[:3]:  # Top 3 fears
                fear_context += f"- {fear.name} (intensity: {fear.intensity:.1f})\n"
                fear_context += f"  Specific triggers detected in proposal\n"
        
        iteration_context = f"\nITERATION CONTEXT: This is iteration {iteration} of the proposal refinement."
        if iteration > 1:
            iteration_context += " Focus on whether previous concerns have been adequately addressed."
        
        return f"""Evaluate this business proposal through your specific archetype lens:

CLIENT: {context.client}
PROPOSAL:
{proposal}
{fear_context}
{iteration_context}

Provide evaluation in this format:
SCORE: [1-10]/10
CONFIDENCE: [1-10]/10 (how confident you are in this assessment)

STRENGTHS:
- [specific strength 1]
- [specific strength 2]

TRIGGERED_CONCERNS:
- [specific concern based on your archetype]
- [another archetype-specific concern]

OBJECTIONS:
- [must-address objection 1]
- [must-address objection 2]

SUGGESTIONS:
- [specific suggestion for improvement]
- [another improvement suggestion]

RISK_ASSESSMENT:
- [risk factor 1 from your perspective]
- [risk factor 2 from your perspective]

DECISION_LIKELIHOOD: [would you personally approve this proposal? yes/no/conditional]
CONDITIONAL_REQUIREMENTS: [if conditional, what specific requirements must be met]"""

    def _parse_archetype_evaluation(self, response: str, triggered_fears: List[FearCode]) -> JudgeEvaluation:
        """Parse evaluation with archetype-specific logic"""
        
        # Initialize defaults
        score = 5.0
        confidence = 5.0
        strengths = []
        concerns = []
        objections = []
        suggestions = []
        risk_factors = []
        decision_likelihood = "conditional"
        
        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('SCORE:'):
                    score = float(line.split(':')[1].strip().split('/')[0])
                elif line.startswith('CONFIDENCE:'):
                    confidence = float(line.split(':')[1].strip().split('/')[0])
                elif line.startswith('DECISION_LIKELIHOOD:'):
                    decision_likelihood = line.split(':')[1].strip()
                elif line.startswith('STRENGTHS:'):
                    current_section = 'strengths'
                elif line.startswith('TRIGGERED_CONCERNS:'):
                    current_section = 'concerns'
                elif line.startswith('OBJECTIONS:'):
                    current_section = 'objections'
                elif line.startswith('SUGGESTIONS:'):
                    current_section = 'suggestions'
                elif line.startswith('RISK_ASSESSMENT:'):
                    current_section = 'risks'
                elif line.startswith('- ') and current_section:
                    item = line[2:]
                    if current_section == 'strengths':
                        strengths.append(item)
                    elif current_section == 'concerns':
                        concerns.append(item)
                    elif current_section == 'objections':
                        objections.append(item)
                    elif current_section == 'suggestions':
                        suggestions.append(item)
                    elif current_section == 'risks':
                        risk_factors.append(item)
        
        except Exception as e:
            logger.warning(f"Failed to parse archetype evaluation: {e}")
        
        # Enhance evaluation with fear-based insights
        evaluation = JudgeEvaluation(
            perspective=self.__class__.__name__.replace('Judge', ''),
            score=max(0, min(10, score)),
            objections=objections,
            suggestions=suggestions,
            strengths=strengths,
            concerns=concerns,
            timestamp=datetime.utcnow()
        )
        
        # Add archetype-specific metadata
        evaluation.confidence = confidence
        evaluation.triggered_fears = [f.name for f in triggered_fears]
        evaluation.risk_factors = risk_factors
        evaluation.decision_likelihood = decision_likelihood
        
        return evaluation

class TechnicalFounderJudge(SpecializedJudge):
    """Technical founder archetype - fears loss of control and technical debt"""
    
    def _define_fear_codes(self) -> List[FearCode]:
        return [
            FearCode(
                name="loss_of_technical_control",
                triggers=["outsource", "vendor", "third-party", "external team", "consultant"],
                intensity=0.8,
                objection_templates=[
                    "This creates dependency on external parties",
                    "We lose control over our technical roadmap",
                    "What happens when the vendor relationship ends?"
                ],
                mitigation_strategies=[
                    "Emphasize knowledge transfer requirements",
                    "Include source code ownership clauses",
                    "Propose hybrid internal/external team structure"
                ]
            ),
            FearCode(
                name="technical_debt_accumulation",
                triggers=["quick fix", "temporary", "patch", "legacy", "workaround"],
                intensity=0.9,
                objection_templates=[
                    "This looks like it will create technical debt",
                    "How do we ensure long-term maintainability?",
                    "What's the migration path for existing systems?"
                ],
                mitigation_strategies=[
                    "Detail refactoring roadmap",
                    "Include technical debt assessment",
                    "Propose incremental modernization approach"
                ]
            ),
            FearCode(
                name="scalability_concerns",
                triggers=["current load", "existing users", "prototype", "MVP"],
                intensity=0.7,
                objection_templates=[
                    "Will this solution scale with our growth?",
                    "What happens when we 10x our user base?",
                    "Are we building for today or tomorrow?"
                ],
                mitigation_strategies=[
                    "Include performance benchmarks",
                    "Detail scalability architecture",
                    "Propose load testing methodology"
                ]
            )
        ]
    
    def _define_decision_patterns(self) -> Dict[str, Any]:
        return {
            "decision_style": "analytical_skeptical",
            "key_drivers": ["technical_excellence", "maintainability", "team_autonomy"],
            "typical_objections": ["vendor_lock_in", "technical_debt", "complexity"],
            "persuasion_points": ["technical_details", "architecture_diagrams", "code_quality"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are a technical founder and CTO with 10+ years of engineering leadership experience.

ARCHETYPE PROFILE:
- Deep technical background in software architecture
- Burned by vendor lock-in and technical debt in the past
- Highly values maintainable, scalable solutions
- Skeptical of "black box" solutions
- Needs to understand technical implementation details
- Fears losing control over technical decisions

EVALUATION CRITERIA:
- Technical feasibility and architecture quality
- Long-term maintainability and scalability
- Team autonomy and knowledge retention
- Vendor dependency and lock-in risks
- Integration complexity with existing systems
- Technical debt implications

TYPICAL CONCERNS:
- "This sounds too good to be true technically"
- "How do we maintain this when the consultants leave?"
- "Will this create more problems than it solves?"
- "What's the real technical complexity here?"

You evaluate proposals through the lens of technical sustainability and team empowerment."""

class ConservativeCFOJudge(SpecializedJudge):
    """Conservative CFO archetype - fears financial risk and compliance issues"""
    
    def _define_fear_codes(self) -> List[FearCode]:
        return [
            FearCode(
                name="budget_overrun_risk",
                triggers=["estimate", "approximately", "should cost", "initial budget"],
                intensity=0.9,
                objection_templates=[
                    "Budget estimates are rarely accurate in practice",
                    "What contingency is built into these numbers?",
                    "How do we control scope creep and cost overruns?"
                ],
                mitigation_strategies=[
                    "Provide detailed budget breakdown",
                    "Include contingency percentages",
                    "Propose fixed-price contracts where possible"
                ]
            ),
            FearCode(
                name="roi_uncertainty",
                triggers=["potential", "could increase", "estimated savings", "projected"],
                intensity=0.8,
                objection_templates=[
                    "ROI projections seem optimistic",
                    "How do we measure and track these benefits?",
                    "What if the benefits don't materialize?"
                ],
                mitigation_strategies=[
                    "Provide conservative ROI scenarios",
                    "Include measurement methodology",
                    "Propose phased implementation with checkpoints"
                ]
            ),
            FearCode(
                name="compliance_risk",
                triggers=["data", "security", "privacy", "regulation", "audit"],
                intensity=0.7,
                objection_templates=[
                    "What are the compliance implications?",
                    "How does this affect our audit readiness?",
                    "Are we creating new regulatory risks?"
                ],
                mitigation_strategies=[
                    "Include compliance assessment",
                    "Detail security measures",
                    "Propose legal review checkpoints"
                ]
            )
        ]
    
    def _define_decision_patterns(self) -> Dict[str, Any]:
        return {
            "decision_style": "risk_averse_analytical",
            "key_drivers": ["cost_control", "predictable_outcomes", "compliance"],
            "typical_objections": ["budget_risk", "roi_uncertainty", "hidden_costs"],
            "persuasion_points": ["detailed_financials", "risk_mitigation", "proven_results"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are a conservative CFO with 15+ years of financial leadership in mid-size companies.

ARCHETYPE PROFILE:
- Experienced multiple budget overruns and failed projects
- Highly risk-averse, especially with new initiatives
- Demands detailed financial justification
- Concerned about audit and compliance implications
- Values predictable, measurable outcomes
- Skeptical of optimistic projections

EVALUATION CRITERIA:
- Detailed cost breakdown and budget reliability
- Conservative ROI analysis with downside scenarios
- Risk assessment and mitigation strategies
- Compliance and audit implications
- Cash flow impact and timing
- Measurable success metrics

TYPICAL CONCERNS:
- "The budget will definitely exceed these estimates"
- "ROI projections are too optimistic"
- "What are the hidden costs we're not seeing?"
- "How does this affect our compliance posture?"

You evaluate proposals through the lens of financial prudence and risk management."""

class GrowthMarketingCMOJudge(SpecializedJudge):
    """Growth-focused CMO archetype - fears missed opportunities and brand damage"""
    
    def _define_fear_codes(self) -> List[FearCode]:
        return [
            FearCode(
                name="competitive_disadvantage",
                triggers=["competitors", "market leader", "catching up", "behind"],
                intensity=0.8,
                objection_templates=[
                    "Will this keep us competitive in the market?",
                    "Are our competitors already doing this?",
                    "How does this position us versus market leaders?"
                ],
                mitigation_strategies=[
                    "Include competitive analysis",
                    "Highlight differentiating factors",
                    "Propose unique positioning angles"
                ]
            ),
            FearCode(
                name="brand_reputation_risk",
                triggers=["public", "customer-facing", "brand", "reputation", "image"],
                intensity=0.9,
                objection_templates=[
                    "What if this reflects poorly on our brand?",
                    "How do customers perceive this change?",
                    "Are we risking our brand reputation?"
                ],
                mitigation_strategies=[
                    "Include brand impact assessment",
                    "Propose customer communication strategy",
                    "Detail reputation monitoring approach"
                ]
            ),
            FearCode(
                name="market_timing_failure",
                triggers=["launch", "timing", "market window", "opportunity"],
                intensity=0.7,
                objection_templates=[
                    "Are we moving fast enough to capture this opportunity?",
                    "What if we miss the market timing?",
                    "Is this the right time to enter this space?"
                ],
                mitigation_strategies=[
                    "Provide market timing analysis",
                    "Include accelerated timeline options",
                    "Detail first-mover advantages"
                ]
            )
        ]
    
    def _define_decision_patterns(self) -> Dict[str, Any]:
        return {
            "decision_style": "opportunity_focused_urgent",
            "key_drivers": ["market_share", "brand_positioning", "customer_satisfaction"],
            "typical_objections": ["timing_risk", "brand_impact", "competitive_response"],
            "persuasion_points": ["market_data", "customer_insights", "competitive_advantage"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are a growth-focused CMO with extensive experience in competitive markets.

ARCHETYPE PROFILE:
- Obsessed with market positioning and competitive advantage
- Highly sensitive to brand reputation and customer perception
- Driven by growth metrics and market share
- Fears missing market opportunities more than failure
- Values speed to market and customer impact
- Concerned about competitive response and timing

EVALUATION CRITERIA:
- Market opportunity size and competitive positioning
- Brand impact and customer perception implications
- Speed to market and competitive timing
- Customer acquisition and retention impact
- Marketing scalability and channel effectiveness
- Differentiation and unique value proposition

TYPICAL CONCERNS:
- "Will this strengthen our competitive position?"
- "How do customers really feel about this?"
- "Are we moving fast enough to win?"
- "What's our differentiation story?"

You evaluate proposals through the lens of market opportunity and brand strength."""

class BureaucraticExecutiveJudge(SpecializedJudge):
    """Large corp executive archetype - fears process violations and career risk"""
    
    def _define_fear_codes(self) -> List[FearCode]:
        return [
            FearCode(
                name="process_compliance_violation",
                triggers=["bypass", "shortcut", "exception", "workaround", "fast-track"],
                intensity=0.9,
                objection_templates=[
                    "This doesn't follow our established processes",
                    "What approvals and sign-offs do we need?",
                    "How does this align with corporate governance?"
                ],
                mitigation_strategies=[
                    "Map to existing approval processes",
                    "Include compliance checkpoints",
                    "Propose process integration plan"
                ]
            ),
            FearCode(
                name="career_limiting_failure",
                triggers=["innovative", "experimental", "untested", "first-time", "pilot"],
                intensity=0.8,
                objection_templates=[
                    "What if this initiative fails publicly?",
                    "How do we mitigate career and reputational risk?",
                    "Can we point to similar successful implementations?"
                ],
                mitigation_strategies=[
                    "Provide industry case studies",
                    "Propose low-risk pilot approach",
                    "Include executive air cover strategy"
                ]
            ),
            FearCode(
                name="stakeholder_misalignment",
                triggers=["departments", "teams", "groups", "stakeholders", "coordination"],
                intensity=0.7,
                objection_templates=[
                    "Have all stakeholders bought into this?",
                    "What about other department priorities?",
                    "How do we manage competing interests?"
                ],
                mitigation_strategies=[
                    "Include stakeholder alignment plan",
                    "Detail change management approach",
                    "Propose steering committee structure"
                ]
            )
        ]
    
    def _define_decision_patterns(self) -> Dict[str, Any]:
        return {
            "decision_style": "consensus_seeking_cautious",
            "key_drivers": ["process_compliance", "stakeholder_alignment", "career_safety"],
            "typical_objections": ["governance_issues", "political_risk", "process_deviation"],
            "persuasion_points": ["proven_methodologies", "stakeholder_support", "risk_mitigation"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are a senior executive in a large corporation with complex stakeholder dynamics.

ARCHETYPE PROFILE:
- 20+ years in large corporate environments
- Highly sensitive to process compliance and governance
- Risk-averse due to career considerations
- Values consensus and stakeholder alignment
- Experienced with complex change management
- Concerned about political implications and optics

EVALUATION CRITERIA:
- Alignment with corporate processes and governance
- Stakeholder buy-in and political feasibility
- Risk management and mitigation strategies
- Change management and implementation complexity
- Precedent and proven methodologies
- Executive visibility and career implications

TYPICAL CONCERNS:
- "Does this follow our standard approval processes?"
- "Have we secured buy-in from all stakeholders?"
- "What are the political and career risks?"
- "Can we point to successful precedents?"

You evaluate proposals through the lens of organizational dynamics and career safety."""

# Factory for creating specialized judges
class JudgeFactory:
    """Factory for creating specialized judge agents"""
    
    _judges = {
        "technical_founder": TechnicalFounderJudge,
        "conservative_cfo": ConservativeCFOJudge,
        "growth_cmo": GrowthMarketingCMOJudge,
        "bureaucratic_executive": BureaucraticExecutiveJudge
    }
    
    @classmethod
    def create_judge(cls, archetype: str, config: Dict[str, Any]) -> SpecializedJudge:
        """Create a specialized judge for the given archetype"""
        
        if archetype not in cls._judges:
            raise ValueError(f"Unknown judge archetype: {archetype}")
        
        return cls._judges[archetype](config)
    
    @classmethod
    def get_available_archetypes(cls) -> List[str]:
        """Get list of available judge archetypes"""
        return list(cls._judges.keys())
    
    @classmethod
    def create_panel(cls, archetypes: List[str], config: Dict[str, Any]) -> List[SpecializedJudge]:
        """Create a panel of specialized judges"""
        return [cls.create_judge(archetype, config) for archetype in archetypes]