"""
Buyer-Agent Simulator - The Dirty Negotiator
==========================================

Simulates real-world buyer behavior including dirty tactics, budget games,
and psychological pressure. This agent stress-tests proposals like a real buyer would.
"""

import asyncio
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger
from .specialized_judges import FearCode, SpecializedJudge

logger = setup_logger(__name__)

class NegotiationTactic(Enum):
    """Dirty negotiation tactics buyers use"""
    BUDGET_FINTA = "budget_finta"  # "We only have $X" (pero tienen más)
    COMPETITOR_LEVERAGE = "competitor_leverage"  # "Competitor offers this for less"
    URGENCY_PRESSURE = "urgency_pressure"  # "Need decision by Friday"
    FEATURE_CREEP = "feature_creep"  # "Can you also add..."
    AUTHORITY_ESCALATION = "authority_escalation"  # "I need to ask my boss"
    RELATIONSHIP_GUILT = "relationship_guilt"  # "I thought we were partners"
    TECHNICAL_DOUBT = "technical_doubt"  # "Are you sure this will work?"
    PAYMENT_DELAY = "payment_delay"  # "Net 90 terms only"
    PILOT_TRAP = "pilot_trap"  # "Start small to prove it"
    EQUITY_DEMAND = "equity_demand"  # "We want skin in the game"

@dataclass
class BuyerPersona:
    """Different buyer personalities"""
    name: str
    aggression_level: float  # 0.0 to 1.0
    budget_sensitivity: float
    risk_tolerance: float
    decision_speed: str  # "slow", "medium", "fast"
    dirty_tactics: List[NegotiationTactic]
    pressure_points: List[str]
    typical_objections: List[str]

@dataclass
class NegotiationRound:
    """Single round of negotiation"""
    round_number: int
    buyer_move: str
    tactic_used: Optional[NegotiationTactic]
    pressure_applied: float
    proposal_response: str
    buyer_satisfaction: float
    deal_probability: float
    escalation_triggered: bool

class BuyerSimulator:
    """
    Simulates a real buyer with dirty tactics and psychological games
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = LLMClient(config.get("llm", {}))
        self.buyer_personas = self._define_buyer_personas()
        self.negotiation_history: List[NegotiationRound] = []
        
    def _define_buyer_personas(self) -> Dict[str, BuyerPersona]:
        """Define different buyer archetypes"""
        
        return {
            "ruthless_procurement": BuyerPersona(
                name="Ruthless Procurement Manager",
                aggression_level=0.9,
                budget_sensitivity=0.8,
                risk_tolerance=0.3,
                decision_speed="slow",
                dirty_tactics=[
                    NegotiationTactic.BUDGET_FINTA,
                    NegotiationTactic.COMPETITOR_LEVERAGE,
                    NegotiationTactic.PAYMENT_DELAY,
                    NegotiationTactic.PILOT_TRAP
                ],
                pressure_points=["cost_reduction", "vendor_risk", "compliance"],
                typical_objections=[
                    "This is 40% over our budget ceiling",
                    "Your competitor quoted half this price",
                    "We need 90-day payment terms minimum",
                    "Start with a $10K pilot to prove value"
                ]
            ),
            
            "paranoid_cto": BuyerPersona(
                name="Paranoid CTO",
                aggression_level=0.6,
                budget_sensitivity=0.5,
                risk_tolerance=0.2,
                decision_speed="slow",
                dirty_tactics=[
                    NegotiationTactic.TECHNICAL_DOUBT,
                    NegotiationTactic.FEATURE_CREEP,
                    NegotiationTactic.AUTHORITY_ESCALATION
                ],
                pressure_points=["security", "scalability", "vendor_lock"],
                typical_objections=[
                    "How do we know this won't break our existing systems?",
                    "We also need real-time monitoring and alerts",
                    "I need to run this by our security team first"
                ]
            ),
            
            "impatient_startup_ceo": BuyerPersona(
                name="Impatient Startup CEO",
                aggression_level=0.8,
                budget_sensitivity=0.9,
                risk_tolerance=0.7,
                decision_speed="fast",
                dirty_tactics=[
                    NegotiationTactic.URGENCY_PRESSURE,
                    NegotiationTactic.EQUITY_DEMAND,
                    NegotiationTactic.RELATIONSHIP_GUILT
                ],
                pressure_points=["speed", "equity", "partnership"],
                typical_objections=[
                    "We need this live by next week",
                    "Can you take equity instead of cash?",
                    "I thought we were building a partnership here"
                ]
            ),
            
            "corporate_bureaucrat": BuyerPersona(
                name="Corporate Bureaucrat",
                aggression_level=0.4,
                budget_sensitivity=0.6,
                risk_tolerance=0.1,
                decision_speed="slow",
                dirty_tactics=[
                    NegotiationTactic.AUTHORITY_ESCALATION,
                    NegotiationTactic.FEATURE_CREEP,
                    NegotiationTactic.PILOT_TRAP
                ],
                pressure_points=["process", "approvals", "documentation"],
                typical_objections=[
                    "This needs approval from 3 different committees",
                    "We also need integration with our ERP system",
                    "Let's start with a 6-month pilot program"
                ]
            ),
            
            "price_shark": BuyerPersona(
                name="Price Shark Negotiator",
                aggression_level=1.0,
                budget_sensitivity=1.0,
                risk_tolerance=0.8,
                decision_speed="medium",
                dirty_tactics=[
                    NegotiationTactic.BUDGET_FINTA,
                    NegotiationTactic.COMPETITOR_LEVERAGE,
                    NegotiationTactic.RELATIONSHIP_GUILT,
                    NegotiationTactic.PAYMENT_DELAY
                ],
                pressure_points=["cost", "terms", "competition"],
                typical_objections=[
                    "We have exactly $50K in the budget, not a penny more",
                    "CompetitorX will do this for $30K",
                    "If you were a real partner, you'd work with our budget",
                    "Net 120 terms or we walk"
                ]
            )
        }
    
    async def simulate_negotiation(
        self, 
        proposal: str, 
        context: Dict[str, Any],
        persona_type: str = "ruthless_procurement",
        max_rounds: int = 5
    ) -> Dict[str, Any]:
        """Run a full negotiation simulation"""
        
        persona = self.buyer_personas[persona_type]
        self.negotiation_history = []
        
        logger.info(f"Starting negotiation simulation with {persona.name}")
        
        # Initial buyer reaction
        current_proposal = proposal
        deal_probability = 0.3  # Start pessimistic
        
        for round_num in range(1, max_rounds + 1):
            
            # Buyer makes their move
            buyer_move, tactic_used, pressure = await self._generate_buyer_move(
                current_proposal, persona, round_num, context
            )
            
            # Simulate proposal response (this would come from your system)
            proposal_response = await self._simulate_proposal_response(
                buyer_move, tactic_used, current_proposal, context
            )
            
            # Calculate buyer satisfaction and deal probability
            satisfaction = await self._calculate_buyer_satisfaction(
                proposal_response, persona, tactic_used
            )
            
            deal_probability = self._update_deal_probability(
                deal_probability, satisfaction, persona, round_num
            )
            
            # Check for escalation
            escalation = self._check_escalation(persona, satisfaction, round_num)
            
            # Record round
            round_data = NegotiationRound(
                round_number=round_num,
                buyer_move=buyer_move,
                tactic_used=tactic_used,
                pressure_applied=pressure,
                proposal_response=proposal_response,
                buyer_satisfaction=satisfaction,
                deal_probability=deal_probability,
                escalation_triggered=escalation
            )
            
            self.negotiation_history.append(round_data)
            
            # Update proposal for next round
            current_proposal = proposal_response
            
            # Check termination conditions
            if deal_probability > 0.8:
                logger.info(f"Deal likely - probability: {deal_probability:.2f}")
                break
            elif deal_probability < 0.1:
                logger.info(f"Deal dead - probability: {deal_probability:.2f}")
                break
            elif escalation:
                logger.info("Buyer escalated - negotiation stalled")
                break
        
        return await self._generate_negotiation_report(persona, context)
    
    async def _generate_buyer_move(
        self, 
        proposal: str, 
        persona: BuyerPersona, 
        round_num: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[NegotiationTactic], float]:
        """Generate buyer's next move with potential dirty tactics"""
        
        # Select tactic based on persona and round
        tactic = self._select_tactic(persona, round_num)
        pressure_level = persona.aggression_level * (1 + round_num * 0.1)
        
        # Build buyer prompt
        prompt = await self._build_buyer_prompt(proposal, persona, tactic, round_num, context)
        
        # Generate buyer response
        system_prompt = self._get_buyer_system_prompt(persona, tactic)
        
        response = await self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=0.7,  # Some randomness for realistic behavior
            max_tokens=1000
        )
        
        return response.strip(), tactic, pressure_level
    
    def _select_tactic(self, persona: BuyerPersona, round_num: int) -> Optional[NegotiationTactic]:
        """Select which dirty tactic to use"""
        
        # Escalate tactics as rounds progress
        if round_num == 1:
            # Start gentle
            return random.choice([None, NegotiationTactic.BUDGET_FINTA])
        elif round_num <= 3:
            # Mid-game tactics
            return random.choice(persona.dirty_tactics[:2] + [None])
        else:
            # Late game - bring out the big guns
            return random.choice(persona.dirty_tactics)
    
    async def _build_buyer_prompt(
        self, 
        proposal: str, 
        persona: BuyerPersona, 
        tactic: Optional[NegotiationTactic],
        round_num: int,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for buyer response"""
        
        tactic_instruction = ""
        if tactic:
            tactic_instruction = self._get_tactic_instruction(tactic, persona)
        
        history_context = ""
        if self.negotiation_history:
            history_context = f"\\nPREVIOUS ROUNDS:\\n"
            for round_data in self.negotiation_history[-2:]:  # Last 2 rounds
                history_context += f"Round {round_data.round_number}: You said '{round_data.buyer_move[:100]}...'\n"
        
        return f"""You are negotiating for: {context.get('client', 'Unknown Company')}

CURRENT PROPOSAL:
{proposal}

ROUND: {round_num}
YOUR PERSONA: {persona.name}
YOUR PRESSURE POINTS: {', '.join(persona.pressure_points)}
{history_context}

SPECIFIC TACTIC TO USE: {tactic_instruction}

Respond as the buyer. Be realistic about what buyers actually say and do. Include specific objections, requests, and pressure tactics that real buyers use.

Your response:"""
    
    def _get_tactic_instruction(self, tactic: NegotiationTactic, persona: BuyerPersona) -> str:
        """Get specific instruction for the tactic"""
        
        instructions = {
            NegotiationTactic.BUDGET_FINTA: f"Claim your budget is much lower than the proposal price. Be specific about the 'ceiling' amount.",
            NegotiationTactic.COMPETITOR_LEVERAGE: f"Mention that a competitor offered similar services for significantly less. Name a real competitor if possible.",
            NegotiationTactic.URGENCY_PRESSURE: f"Create artificial urgency - claim you need a decision/implementation by an unrealistic deadline.",
            NegotiationTactic.FEATURE_CREEP: f"Ask for additional features or services to be included at no extra cost.",
            NegotiationTactic.AUTHORITY_ESCALATION: f"Claim you need to 'check with your boss' or get additional approvals.",
            NegotiationTactic.RELATIONSHIP_GUILT: f"Appeal to the relationship and partnership, suggesting they should give you a better deal.",
            NegotiationTactic.TECHNICAL_DOUBT: f"Express skepticism about whether the solution will actually work as promised.",
            NegotiationTactic.PAYMENT_DELAY: f"Demand extended payment terms (60-120 days) as a condition of the deal.",
            NegotiationTactic.PILOT_TRAP: f"Insist on starting with a much smaller pilot project to 'prove value'.",
            NegotiationTactic.EQUITY_DEMAND: f"Suggest taking equity or revenue share instead of cash payment."
        }
        
        return instructions.get(tactic, "Use your standard negotiation approach.")
    
    def _get_buyer_system_prompt(self, persona: BuyerPersona, tactic: Optional[NegotiationTactic]) -> str:
        """Get system prompt for buyer persona"""
        
        return f"""You are a {persona.name} in a business negotiation.

PERSONALITY TRAITS:
- Aggression Level: {persona.aggression_level}/1.0
- Budget Sensitivity: {persona.budget_sensitivity}/1.0  
- Risk Tolerance: {persona.risk_tolerance}/1.0
- Decision Speed: {persona.decision_speed}

BEHAVIOR PATTERNS:
- You are experienced in negotiations and know all the tricks
- You will use pressure tactics to get better deals
- You care about {', '.join(persona.pressure_points)}
- You typically object about: {', '.join(persona.typical_objections[:2])}

NEGOTIATION STYLE:
{"You play hardball and use psychological pressure." if persona.aggression_level > 0.7 else "You are firm but professional in negotiations."}
{"You're very budget conscious and fight every dollar." if persona.budget_sensitivity > 0.7 else "You focus on value over pure cost."}
{"You make quick decisions when pressured." if persona.decision_speed == "fast" else "You take time to evaluate decisions carefully."}

Remember: You represent a real buyer with real constraints and pressures. Be authentic to how these conversations actually happen in business."""
    
    async def _simulate_proposal_response(
        self, 
        buyer_move: str, 
        tactic: Optional[NegotiationTactic],
        current_proposal: str,
        context: Dict[str, Any]
    ) -> str:
        """Simulate how the proposal would respond to buyer tactics"""
        
        # This would integrate with your actual proposal refinement system
        # For simulation, we'll create a basic response
        
        response_prompt = f"""A buyer just said this in a negotiation:
"{buyer_move}"

They used this tactic: {tactic.value if tactic else "None"}

Your current proposal is:
{current_proposal[:500]}...

Generate a professional response that addresses their concerns while maintaining your position. Be realistic about what a vendor would actually say."""
        
        response = await self.llm_client.generate(
            system_prompt="You are a professional vendor responding to buyer objections and tactics in a negotiation.",
            user_prompt=response_prompt,
            temperature=0.3,
            max_tokens=800
        )
        
        return response.strip()
    
    async def _calculate_buyer_satisfaction(
        self, 
        proposal_response: str, 
        persona: BuyerPersona,
        tactic_used: Optional[NegotiationTactic]
    ) -> float:
        """Calculate how satisfied the buyer is with the response"""
        
        # Analyze response for satisfaction indicators
        analysis_prompt = f"""Rate buyer satisfaction with this vendor response:

BUYER PERSONA: {persona.name}
BUYER TACTIC USED: {tactic_used.value if tactic_used else "None"}
VENDOR RESPONSE: {proposal_response}

Consider:
- Did vendor address the buyer's main concerns?
- Did vendor make meaningful concessions?
- Was the response respectful of buyer's position?
- Does the response move the deal forward?

Rate satisfaction from 0.0 to 1.0:"""
        
        satisfaction_response = await self.llm_client.generate(
            system_prompt="You are an expert negotiation analyst. Rate buyer satisfaction objectively.",
            user_prompt=analysis_prompt,
            temperature=0.1,
            max_tokens=100
        )
        
        # Extract satisfaction score
        try:
            # Look for decimal number in response
            import re
            scores = re.findall(r'0\.\d+|1\.0', satisfaction_response)
            if scores:
                return float(scores[0])
        except:
            pass
        
        # Fallback: simple keyword analysis
        positive_words = ["yes", "agreed", "accept", "concession", "discount", "flexible"]
        negative_words = ["no", "cannot", "impossible", "standard", "policy"]
        
        response_lower = proposal_response.lower()
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        base_satisfaction = 0.5
        satisfaction = base_satisfaction + (positive_count * 0.1) - (negative_count * 0.1)
        
        return max(0.0, min(1.0, satisfaction))
    
    def _update_deal_probability(
        self, 
        current_probability: float, 
        satisfaction: float, 
        persona: BuyerPersona,
        round_num: int
    ) -> float:
        """Update deal probability based on buyer satisfaction"""
        
        # Satisfaction impact
        satisfaction_impact = (satisfaction - 0.5) * 0.3
        
        # Persona-specific modifiers
        aggression_penalty = persona.aggression_level * -0.1 if satisfaction < 0.6 else 0
        
        # Round penalty (buyer gets impatient)
        round_penalty = round_num * -0.05
        
        new_probability = current_probability + satisfaction_impact + aggression_penalty + round_penalty
        
        return max(0.0, min(1.0, new_probability))
    
    def _check_escalation(self, persona: BuyerPersona, satisfaction: float, round_num: int) -> bool:
        """Check if buyer escalates (brings in boss, threatens to walk, etc.)"""
        
        escalation_threshold = 0.3
        
        # High aggression buyers escalate faster
        if persona.aggression_level > 0.8 and satisfaction < escalation_threshold:
            return True
        
        # Late rounds with low satisfaction
        if round_num > 3 and satisfaction < 0.4:
            return True
        
        # Authority escalation tactic specifically
        if hasattr(self, 'negotiation_history') and self.negotiation_history:
            last_round = self.negotiation_history[-1]
            if last_round.tactic_used == NegotiationTactic.AUTHORITY_ESCALATION:
                return True
        
        return False
    
    async def _generate_negotiation_report(self, persona: BuyerPersona, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive negotiation simulation report"""
        
        if not self.negotiation_history:
            return {"error": "No negotiation history available"}
        
        final_round = self.negotiation_history[-1]
        
        # Calculate key metrics
        avg_satisfaction = sum(r.buyer_satisfaction for r in self.negotiation_history) / len(self.negotiation_history)
        max_pressure = max(r.pressure_applied for r in self.negotiation_history)
        tactics_used = [r.tactic_used.value for r in self.negotiation_history if r.tactic_used]
        
        # Determine outcome
        if final_round.deal_probability > 0.8:
            outcome = "Deal Likely"
        elif final_round.deal_probability > 0.5:
            outcome = "Deal Possible"
        elif final_round.deal_probability > 0.2:
            outcome = "Deal Unlikely"
        else:
            outcome = "Deal Dead"
        
        # Generate insights
        insights = []
        
        if avg_satisfaction < 0.4:
            insights.append("Buyer consistently unsatisfied - proposal needs major revisions")
        
        if max_pressure > 0.8:
            insights.append("High pressure tactics used - buyer is aggressive negotiator")
        
        if NegotiationTactic.BUDGET_FINTA.value in tactics_used:
            insights.append("Budget objections raised - price may be key sticking point")
        
        if len(set(tactics_used)) > 3:
            insights.append("Multiple tactics deployed - buyer is experienced negotiator")
        
        if final_round.escalation_triggered:
            insights.append("Escalation triggered - senior stakeholders may enter negotiation")
        
        return {
            "simulation_summary": {
                "buyer_persona": persona.name,
                "total_rounds": len(self.negotiation_history),
                "final_deal_probability": final_round.deal_probability,
                "outcome": outcome,
                "avg_buyer_satisfaction": avg_satisfaction,
                "max_pressure_applied": max_pressure
            },
            "tactics_analysis": {
                "tactics_used": tactics_used,
                "most_effective_tactic": self._find_most_effective_tactic(),
                "escalation_triggered": final_round.escalation_triggered
            },
            "negotiation_rounds": [
                {
                    "round": r.round_number,
                    "buyer_move": r.buyer_move[:200] + "..." if len(r.buyer_move) > 200 else r.buyer_move,
                    "tactic": r.tactic_used.value if r.tactic_used else None,
                    "satisfaction": r.buyer_satisfaction,
                    "deal_probability": r.deal_probability
                }
                for r in self.negotiation_history
            ],
            "key_insights": insights,
            "recommendations": self._generate_recommendations(persona, final_round),
            "stress_test_score": self._calculate_stress_test_score()
        }
    
    def _find_most_effective_tactic(self) -> Optional[str]:
        """Find which tactic generated highest satisfaction"""
        
        tactic_satisfaction = {}
        
        for round_data in self.negotiation_history:
            if round_data.tactic_used:
                tactic = round_data.tactic_used.value
                if tactic not in tactic_satisfaction:
                    tactic_satisfaction[tactic] = []
                tactic_satisfaction[tactic].append(round_data.buyer_satisfaction)
        
        if not tactic_satisfaction:
            return None
        
        # Find tactic with highest average satisfaction
        avg_satisfaction = {
            tactic: sum(scores) / len(scores) 
            for tactic, scores in tactic_satisfaction.items()
        }
        
        return max(avg_satisfaction, key=avg_satisfaction.get)
    
    def _generate_recommendations(self, persona: BuyerPersona, final_round: NegotiationRound) -> List[str]:
        """Generate recommendations based on simulation"""
        
        recommendations = []
        
        if final_round.deal_probability < 0.5:
            recommendations.append("Consider significant price concessions or value-add services")
        
        if persona.budget_sensitivity > 0.8:
            recommendations.append("Focus on ROI justification and payment flexibility")
        
        if persona.risk_tolerance < 0.3:
            recommendations.append("Emphasize security, compliance, and proven track record")
        
        if final_round.escalation_triggered:
            recommendations.append("Prepare executive-level materials for senior stakeholder meeting")
        
        # Tactic-specific recommendations
        tactics_used = [r.tactic_used for r in self.negotiation_history if r.tactic_used]
        
        if NegotiationTactic.COMPETITOR_LEVERAGE in tactics_used:
            recommendations.append("Prepare competitive differentiation and value proposition defense")
        
        if NegotiationTactic.FEATURE_CREEP in tactics_used:
            recommendations.append("Set clear scope boundaries and change request process")
        
        if NegotiationTactic.PILOT_TRAP in tactics_used:
            recommendations.append("Design pilot with clear success metrics and expansion path")
        
        return recommendations
    
    def _calculate_stress_test_score(self) -> float:
        """Calculate how well the proposal survived the stress test"""
        
        if not self.negotiation_history:
            return 0.0
        
        final_probability = self.negotiation_history[-1].deal_probability
        avg_satisfaction = sum(r.buyer_satisfaction for r in self.negotiation_history) / len(self.negotiation_history)
        rounds_survived = len(self.negotiation_history)
        
        # Weighted score
        score = (
            final_probability * 0.5 +  # 50% weight on final deal probability
            avg_satisfaction * 0.3 +   # 30% weight on buyer satisfaction
            min(rounds_survived / 5, 1.0) * 0.2  # 20% weight on endurance
        )
        
        return round(score, 2)

# Factory function for easy usage
def create_buyer_simulator(config: Dict[str, Any]) -> BuyerSimulator:
    """Create a buyer simulator instance"""
    return BuyerSimulator(config)

# Integration with main evaluation system
async def stress_test_proposal(
    proposal: str, 
    context: Dict[str, Any],
    config: Dict[str, Any],
    buyer_types: List[str] = None
) -> Dict[str, Any]:
    """Run proposal through multiple buyer simulations"""
    
    if buyer_types is None:
        buyer_types = ["ruthless_procurement", "paranoid_cto", "price_shark"]
    
    simulator = create_buyer_simulator(config)
    results = {}
    
    for buyer_type in buyer_types:
        logger.info(f"Running stress test with {buyer_type}")
        
        simulation_result = await simulator.simulate_negotiation(
            proposal=proposal,
            context=context,
            persona_type=buyer_type,
            max_rounds=4
        )
        
        results[buyer_type] = simulation_result
    
    # Generate overall stress test report
    overall_score = sum(
        result["stress_test_score"] for result in results.values()
    ) / len(results)
    
    return {
        "overall_stress_test_score": overall_score,
        "individual_simulations": results,
        "summary": {
            "most_challenging_buyer": min(results.items(), key=lambda x: x[1]["stress_test_score"])[0],
            "best_performing_buyer": max(results.items(), key=lambda x: x[1]["stress_test_score"])[0],
            "avg_deal_probability": sum(r["simulation_summary"]["final_deal_probability"] for r in results.values()) / len(results),
            "common_failure_points": _extract_common_failure_points(results)
        },
        "recommendations": _generate_overall_recommendations(results)
    }

def _extract_common_failure_points(results: Dict[str, Any]) -> List[str]:
    """Extract common points where negotiations failed"""
    
    failure_points = []
    
    for buyer_type, result in results.items():
        if result["simulation_summary"]["final_deal_probability"] < 0.3:
            insights = result.get("key_insights", [])
            failure_points.extend(insights)
    
    # Find most common failure points
    from collections import Counter
    common_failures = Counter(failure_points)
    
    return [failure for failure, count in common_failures.most_common(3)]

def _generate_overall_recommendations(results: Dict[str, Any]) -> List[str]:
    """Generate overall recommendations from all simulations"""
    
    all_recommendations = []
    
    for result in results.values():
        all_recommendations.extend(result.get("recommendations", []))
    
    # Deduplicate and prioritize
    from collections import Counter
    rec_counts = Counter(all_recommendations)
    
    # Return top recommendations that appeared in multiple simulations
    priority_recs = [rec for rec, count in rec_counts.most_common() if count > 1]
    
    if not priority_recs:
        # If no common recommendations, return top 3 unique ones
        priority_recs = [rec for rec, _ in rec_counts.most_common(3)]
    
    return priority_recs