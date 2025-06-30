"""
JudgeAgent - Evaluates proposals from CFO/CMO/CEO perspectives
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class JudgeEvaluation:
    """Evaluation from a judge perspective"""
    perspective: str  # CFO, CMO, CEO
    score: float  # 0-10
    objections: List[str]
    suggestions: List[str]
    strengths: List[str]
    concerns: List[str]
    timestamp: datetime

@dataclass
class ComparisonResult:
    """Result of comparing two proposals"""
    winner: str  # "proposal_1" or "proposal_2"
    reasoning: str
    score_difference: float
    key_differentiators: List[str]

class JudgeAgent:
    """
    Agent that evaluates proposals from different C-level perspectives
    Provides detailed feedback, scores, and objections
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = LLMClient(config.get("llm", {}))
        self.version = "1.0.0"
        
        # Perspective-specific prompts
        self.perspective_prompts = self._load_perspective_prompts()
        
    def _load_perspective_prompts(self) -> Dict[str, str]:
        """Load perspective-specific system prompts"""
        return {
            "CFO": """You are a seasoned Chief Financial Officer with 20+ years of experience evaluating business proposals.

Your primary concerns are:
- Financial viability and ROI
- Budget requirements and cash flow impact
- Risk assessment and mitigation
- Cost-benefit analysis
- Compliance and regulatory considerations
- Scalability of financial model

When evaluating proposals, you focus on:
1. Clear financial projections and assumptions
2. Realistic budget estimates
3. Identified revenue streams
4. Cost structure analysis
5. Risk factors and mitigation strategies
6. Timeline for ROI achievement
7. Impact on company financials

You are naturally skeptical and ask tough questions about:
- Hidden costs
- Revenue assumptions
- Market size estimates
- Competitive threats
- Implementation risks
- Resource requirements

Rate proposals on a scale of 1-10 where:
- 8-10: Financially sound with strong ROI potential
- 6-7: Acceptable with minor financial concerns
- 4-5: Significant financial concerns requiring revision
- 1-3: Financially unviable or too risky""",

            "CMO": """You are an experienced Chief Marketing Officer with deep expertise in brand strategy, customer acquisition, and market positioning.

Your primary concerns are:
- Market opportunity and sizing
- Customer value proposition
- Brand alignment and positioning
- Go-to-market strategy
- Customer acquisition costs
- Competitive differentiation

When evaluating proposals, you focus on:
1. Clear target market definition
2. Compelling value proposition
3. Competitive advantage
4. Marketing and sales strategy
5. Customer journey and experience
6. Brand consistency and messaging
7. Market timing and trends

You are particularly interested in:
- Customer needs validation
- Market research and insights
- Differentiation from competitors
- Marketing channel strategy
- Customer acquisition metrics
- Brand reputation impact
- Long-term market positioning

Rate proposals on a scale of 1-10 where:
- 8-10: Strong market opportunity with clear differentiation
- 6-7: Good market potential with minor positioning concerns
- 4-5: Unclear market strategy requiring significant revision
- 1-3: Poor market fit or weak value proposition""",

            "CEO": """You are a visionary Chief Executive Officer with extensive experience in strategic planning, organizational leadership, and business transformation.

Your primary concerns are:
- Strategic alignment with company vision
- Competitive positioning and advantage
- Organizational capability and readiness
- Stakeholder impact and buy-in
- Long-term sustainability
- Risk vs. reward balance

When evaluating proposals, you focus on:
1. Strategic fit with company goals
2. Execution feasibility
3. Organizational impact
4. Stakeholder considerations
5. Competitive implications
6. Innovation and differentiation
7. Scalability and growth potential

You think holistically about:
- Company culture and values alignment
- Leadership and talent requirements
- Stakeholder communication needs
- Change management considerations
- Long-term strategic impact
- Innovation and market leadership
- Organizational learning opportunities

Rate proposals on a scale of 1-10 where:
- 8-10: Strategically aligned with strong execution plan
- 6-7: Good strategic fit with manageable execution challenges
- 4-5: Strategic concerns or significant execution risks
- 1-3: Poor strategic alignment or unrealistic execution"""
        }
    
    async def evaluate(self, proposal: str, context, perspective: str) -> JudgeEvaluation:
        """
        Evaluate a proposal from a specific perspective
        
        Args:
            proposal: The proposal text to evaluate
            context: ProposalContext with client info and objectives
            perspective: "CFO", "CMO", or "CEO"
            
        Returns:
            JudgeEvaluation with score, objections, and feedback
        """
        logger.info(f"Evaluating proposal from {perspective} perspective")
        
        try:
            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(proposal, context, perspective)
            
            # Get evaluation from LLM
            response = await self.llm_client.generate(
                system_prompt=self.perspective_prompts[perspective],
                user_prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent evaluations
                max_tokens=2000
            )
            
            # Parse evaluation response
            evaluation = self._parse_evaluation_response(response, perspective)
            
            logger.info(f"{perspective} evaluation complete: {evaluation.score:.1f}/10")
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to evaluate from {perspective} perspective: {e}")
            raise
    
    def _build_evaluation_prompt(self, proposal: str, context, perspective: str) -> str:
        """Build perspective-specific evaluation prompt"""
        
        objectives_text = "\n".join([f"- {obj}" for obj in context.objectives])
        
        prompt = f"""Please evaluate the following business proposal from your {perspective} perspective:

CLIENT: {context.client}
OBJECTIVES: 
{objectives_text}

PROPOSAL TO EVALUATE:
{proposal}

Please provide a detailed evaluation including:

1. OVERALL SCORE (1-10 scale)
2. STRENGTHS (what works well from your perspective)
3. CONCERNS (what worries you or needs attention)
4. SPECIFIC OBJECTIONS (concrete issues that must be addressed)
5. SUGGESTIONS (how to improve the proposal)
6. KEY QUESTIONS (important questions that need answers)

Format your response as:
SCORE: [number]/10
STRENGTHS:
- [strength 1]
- [strength 2]
...

CONCERNS:
- [concern 1]
- [concern 2]
...

OBJECTIONS:
- [objection 1]
- [objection 2]
...

SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
...

Be thorough and specific in your evaluation. Focus on the aspects most relevant to your role as {perspective}."""

        return prompt
    
    def _parse_evaluation_response(self, response: str, perspective: str) -> JudgeEvaluation:
        """Parse the LLM response into structured evaluation"""
        
        # Initialize with defaults
        score = 5.0
        strengths = []
        concerns = []
        objections = []
        suggestions = []
        
        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('SCORE:'):
                    score_text = line.split(':')[1].strip()
                    # Extract just the number
                    score = float(score_text.split('/')[0])
                    
                elif line.startswith('STRENGTHS:'):
                    current_section = 'strengths'
                elif line.startswith('CONCERNS:'):
                    current_section = 'concerns'
                elif line.startswith('OBJECTIONS:'):
                    current_section = 'objections'
                elif line.startswith('SUGGESTIONS:'):
                    current_section = 'suggestions'
                elif line.startswith('- ') and current_section:
                    item = line[2:]  # Remove "- "
                    if current_section == 'strengths':
                        strengths.append(item)
                    elif current_section == 'concerns':
                        concerns.append(item)
                    elif current_section == 'objections':
                        objections.append(item)
                    elif current_section == 'suggestions':
                        suggestions.append(item)
                        
        except Exception as e:
            logger.warning(f"Failed to parse evaluation response: {e}")
            # Use defaults
        
        return JudgeEvaluation(
            perspective=perspective,
            score=max(0, min(10, score)),  # Clamp between 0-10
            objections=objections,
            suggestions=suggestions,
            strengths=strengths,
            concerns=concerns,
            timestamp=datetime.utcnow()
        )
    
    async def compare_proposals(
        self, 
        proposal1: str, 
        proposal2: str, 
        context
    ) -> ComparisonResult:
        """
        Compare two proposals and determine which is better
        
        Args:
            proposal1: First proposal to compare
            proposal2: Second proposal to compare  
            context: ProposalContext for evaluation criteria
            
        Returns:
            ComparisonResult with winner and reasoning
        """
        logger.info("Comparing two proposal variants")
        
        try:
            prompt = self._build_comparison_prompt(proposal1, proposal2, context)
            
            response = await self.llm_client.generate(
                system_prompt="""You are a senior business consultant tasked with comparing business proposals.
                
Evaluate both proposals holistically considering:
- Strategic alignment
- Financial viability  
- Market opportunity
- Execution feasibility
- Risk assessment
- Stakeholder impact

Provide a clear winner with detailed reasoning.""",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse comparison result
            result = self._parse_comparison_response(response)
            
            logger.info(f"Comparison complete: Winner is {result.winner}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to compare proposals: {e}")
            raise
    
    def _build_comparison_prompt(self, proposal1: str, proposal2: str, context) -> str:
        """Build comparison prompt"""
        
        objectives_text = "\n".join([f"- {obj}" for obj in context.objectives])
        
        prompt = f"""Compare these two business proposals for {context.client}:

CLIENT OBJECTIVES:
{objectives_text}

PROPOSAL 1:
{proposal1}

PROPOSAL 2:  
{proposal2}

Please provide a detailed comparison and select the superior proposal.

Format your response as:
WINNER: [proposal_1 or proposal_2]
SCORE_DIFFERENCE: [numerical difference]
REASONING: [detailed explanation of why the winner is better]
KEY_DIFFERENTIATORS:
- [differentiator 1]
- [differentiator 2]
...

Consider all aspects: strategy, financials, market fit, execution, and risk."""

        return prompt
    
    def _parse_comparison_response(self, response: str) -> ComparisonResult:
        """Parse comparison response"""
        
        winner = "proposal_1"  # default
        reasoning = "No clear reasoning provided"
        score_difference = 0.0
        differentiators = []
        
        try:
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('WINNER:'):
                    winner = line.split(':')[1].strip()
                elif line.startswith('SCORE_DIFFERENCE:'):
                    score_text = line.split(':')[1].strip()
                    score_difference = float(score_text)
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.startswith('- '):
                    differentiators.append(line[2:])
                    
        except Exception as e:
            logger.warning(f"Failed to parse comparison response: {e}")
        
        return ComparisonResult(
            winner=winner,
            reasoning=reasoning,
            score_difference=score_difference,
            key_differentiators=differentiators
        )
    
    async def evaluate_all_perspectives(
        self, 
        proposal: str, 
        context
    ) -> List[JudgeEvaluation]:
        """Evaluate proposal from all three perspectives simultaneously"""
        
        tasks = [
            self.evaluate(proposal, context, "CFO"),
            self.evaluate(proposal, context, "CMO"), 
            self.evaluate(proposal, context, "CEO")
        ]
        
        evaluations = await asyncio.gather(*tasks)
        
        overall_score = sum(eval.score for eval in evaluations) / len(evaluations)
        logger.info(f"Overall evaluation score: {overall_score:.1f}/10")
        
        return evaluations