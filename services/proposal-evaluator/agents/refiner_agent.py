"""
RefinerAgent - Iterates and improves proposals based on judge feedback
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from .judge_agent import JudgeEvaluation
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class RefinementResult:
    """Result of proposal refinement"""
    refined_proposal: str
    notes: str
    changes_made: List[str]
    addressed_objections: List[str]
    improvement_score: float

class RefinerAgent:
    """
    Agent responsible for iteratively improving proposals based on judge feedback
    Analyzes objections and suggestions to make targeted improvements
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = LLMClient(config.get("llm", {}))
        self.version = "1.0.0"
        
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt for refinement"""
        return """You are a senior proposal consultant specializing in iterative improvement and stakeholder alignment.

Your expertise includes:
- Analyzing feedback from multiple perspectives
- Identifying root causes of objections
- Making targeted improvements without losing proposal strength
- Balancing competing stakeholder concerns
- Maintaining proposal coherence and flow
- Strengthening weak areas while preserving strong elements

When refining proposals, you:
1. Carefully analyze all feedback and objections
2. Prioritize the most critical issues
3. Make surgical improvements that address concerns
4. Ensure changes don't create new problems
5. Maintain the proposal's overall persuasive power
6. Document what changes were made and why

Your approach is:
- Analytical: Understand the root cause of each objection
- Strategic: Address concerns that matter most to decision makers
- Surgical: Make precise changes without unnecessary rewrites
- Balanced: Consider all stakeholder perspectives
- Documented: Clearly explain what changed and why

You never compromise the proposal's core strength while addressing legitimate concerns."""

    async def refine_proposal(
        self, 
        current_proposal: str, 
        evaluations: List[JudgeEvaluation], 
        context
    ) -> RefinementResult:
        """
        Refine a proposal based on judge evaluations
        
        Args:
            current_proposal: Current proposal text
            evaluations: List of evaluations from different perspectives
            context: Original proposal context
            
        Returns:
            RefinementResult with improved proposal and notes
        """
        logger.info(f"Refining proposal based on {len(evaluations)} evaluations")
        
        try:
            # Analyze feedback
            feedback_analysis = self._analyze_feedback(evaluations)
            
            # Build refinement prompt
            prompt = self._build_refinement_prompt(
                current_proposal, 
                evaluations, 
                context, 
                feedback_analysis
            )
            
            # Generate refined proposal
            response = await self.llm_client.generate(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                temperature=0.4,  # Balanced creativity for improvements
                max_tokens=5000
            )
            
            # Parse refinement result
            result = self._parse_refinement_response(response, evaluations)
            
            logger.info(f"Refinement complete: {len(result.changes_made)} changes made")
            return result
            
        except Exception as e:
            logger.error(f"Failed to refine proposal: {e}")
            raise
    
    def _analyze_feedback(self, evaluations: List[JudgeEvaluation]) -> Dict[str, Any]:
        """Analyze feedback to identify patterns and priorities"""
        
        all_objections = []
        all_suggestions = []
        all_concerns = []
        
        perspective_scores = {}
        
        for eval in evaluations:
            all_objections.extend(eval.objections)
            all_suggestions.extend(eval.suggestions)
            all_concerns.extend(eval.concerns)
            perspective_scores[eval.perspective] = eval.score
        
        # Identify common themes
        common_themes = self._identify_common_themes(all_objections + all_concerns)
        
        # Prioritize by frequency and severity
        priority_issues = self._prioritize_issues(evaluations)
        
        return {
            "total_objections": len(all_objections),
            "total_suggestions": len(all_suggestions),
            "total_concerns": len(all_concerns),
            "perspective_scores": perspective_scores,
            "lowest_score": min(perspective_scores.values()),
            "common_themes": common_themes,
            "priority_issues": priority_issues,
            "avg_score": sum(perspective_scores.values()) / len(perspective_scores)
        }
    
    def _identify_common_themes(self, items: List[str]) -> List[str]:
        """Identify common themes in feedback"""
        # Simple keyword-based theme identification
        keywords = {
            "financial": ["budget", "cost", "roi", "revenue", "financial", "money", "price"],
            "timeline": ["timeline", "schedule", "time", "deadline", "duration"],
            "risk": ["risk", "uncertainty", "concern", "problem", "issue"],
            "implementation": ["implementation", "execution", "deploy", "rollout"],
            "market": ["market", "customer", "competition", "competitive"],
            "strategy": ["strategy", "strategic", "vision", "goal", "objective"]
        }
        
        themes = []
        for theme, words in keywords.items():
            if any(word in " ".join(items).lower() for word in words):
                themes.append(theme)
        
        return themes
    
    def _prioritize_issues(self, evaluations: List[JudgeEvaluation]) -> List[Dict[str, Any]]:
        """Prioritize issues based on perspective and severity"""
        issues = []
        
        for eval in evaluations:
            for objection in eval.objections:
                issues.append({
                    "text": objection,
                    "perspective": eval.perspective,
                    "severity": "high" if eval.score < 6 else "medium" if eval.score < 8 else "low",
                    "score": eval.score
                })
        
        # Sort by score (lowest first) and then by perspective importance
        perspective_weights = {"CEO": 3, "CFO": 2, "CMO": 1}
        
        issues.sort(key=lambda x: (x["score"], -perspective_weights.get(x["perspective"], 0)))
        
        return issues[:10]  # Top 10 priority issues
    
    def _build_refinement_prompt(
        self, 
        current_proposal: str, 
        evaluations: List[JudgeEvaluation], 
        context, 
        analysis: Dict[str, Any]
    ) -> str:
        """Build refinement prompt with detailed feedback"""
        
        # Compile feedback by perspective
        feedback_sections = []
        
        for eval in evaluations:
            section = f"""
{eval.perspective} EVALUATION (Score: {eval.score}/10):

Strengths:
{chr(10).join([f"+ {s}" for s in eval.strengths])}

Concerns:
{chr(10).join([f"- {c}" for c in eval.concerns])}

Objections (MUST ADDRESS):
{chr(10).join([f"! {o}" for o in eval.objections])}

Suggestions:
{chr(10).join([f"→ {s}" for s in eval.suggestions])}
"""
            feedback_sections.append(section)
        
        feedback_text = "\n".join(feedback_sections)
        
        priority_issues_text = "\n".join([
            f"- {issue['text']} ({issue['perspective']}, {issue['severity']} priority)"
            for issue in analysis["priority_issues"]
        ])
        
        prompt = f"""Refine the following business proposal based on detailed stakeholder feedback.

CLIENT: {context.client}
CURRENT AVERAGE SCORE: {analysis['avg_score']:.1f}/10
TARGET: 8.0+/10

CURRENT PROPOSAL:
{current_proposal}

DETAILED FEEDBACK BY PERSPECTIVE:
{feedback_text}

PRIORITY ISSUES TO ADDRESS:
{priority_issues_text}

REFINEMENT INSTRUCTIONS:
1. Address ALL objections marked with "!" - these are blocking concerns
2. Focus on the lowest-scoring perspective ({min(analysis['perspective_scores'], key=analysis['perspective_scores'].get)}: {analysis['lowest_score']:.1f}/10)
3. Incorporate relevant suggestions to strengthen the proposal
4. Maintain the proposal's core value proposition
5. Ensure changes don't create new concerns for other perspectives

Please provide your response in this format:

REFINED_PROPOSAL:
[Complete refined proposal here]

REFINEMENT_NOTES:
[Explanation of what was changed and why]

CHANGES_MADE:
- [Specific change 1]
- [Specific change 2]
...

OBJECTIONS_ADDRESSED:
- [Which objections were addressed and how]
...

Focus on making surgical improvements that directly address the feedback while maintaining proposal strength."""

        return prompt
    
    def _parse_refinement_response(
        self, 
        response: str, 
        evaluations: List[JudgeEvaluation]
    ) -> RefinementResult:
        """Parse the refinement response"""
        
        # Initialize defaults
        refined_proposal = response  # fallback to full response
        notes = "Refinement completed"
        changes_made = []
        addressed_objections = []
        
        try:
            sections = response.split('\n\n')
            current_section = None
            
            for section in sections:
                lines = section.split('\n')
                
                if lines[0].strip() == "REFINED_PROPOSAL:":
                    refined_proposal = '\n'.join(lines[1:]).strip()
                elif lines[0].strip() == "REFINEMENT_NOTES:":
                    notes = '\n'.join(lines[1:]).strip()
                elif lines[0].strip() == "CHANGES_MADE:":
                    changes_made = [
                        line.strip()[2:] for line in lines[1:] 
                        if line.strip().startswith('- ')
                    ]
                elif lines[0].strip() == "OBJECTIONS_ADDRESSED:":
                    addressed_objections = [
                        line.strip()[2:] for line in lines[1:] 
                        if line.strip().startswith('- ')
                    ]
                    
        except Exception as e:
            logger.warning(f"Failed to parse refinement response: {e}")
            # Use the full response as refined proposal
        
        # Calculate improvement score estimate
        total_objections = sum(len(eval.objections) for eval in evaluations)
        improvement_score = min(1.0, len(addressed_objections) / max(1, total_objections))
        
        return RefinementResult(
            refined_proposal=refined_proposal,
            notes=notes,
            changes_made=changes_made,
            addressed_objections=addressed_objections,
            improvement_score=improvement_score
        )
    
    async def validate_refinement(
        self, 
        original: str, 
        refined: str, 
        evaluations: List[JudgeEvaluation]
    ) -> Dict[str, Any]:
        """Validate that refinement actually improves the proposal"""
        
        prompt = f"""Compare these two proposal versions and assess if the refinement is an improvement:

ORIGINAL PROPOSAL:
{original}

REFINED PROPOSAL:
{refined}

FEEDBACK THAT WAS ADDRESSED:
{self._format_feedback_for_validation(evaluations)}

Please evaluate:
1. Does the refined version address the key objections?
2. Is the proposal stronger overall?
3. Were any strengths lost in the refinement?
4. What is the estimated score improvement?

Format response as:
IMPROVEMENT_QUALITY: [excellent/good/fair/poor]
ESTIMATED_SCORE_CHANGE: [+/-X.X points]
OBJECTIONS_ADDRESSED: [number]
STRENGTHS_PRESERVED: [yes/no]
SUMMARY: [brief assessment]"""

        response = await self.llm_client.generate(
            system_prompt="You are an expert proposal evaluator assessing refinement quality.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        return self._parse_validation_response(response)
    
    def _format_feedback_for_validation(self, evaluations: List[JudgeEvaluation]) -> str:
        """Format feedback for validation prompt"""
        feedback_text = ""
        
        for eval in evaluations:
            if eval.objections:
                feedback_text += f"\n{eval.perspective} Objections:\n"
                feedback_text += "\n".join([f"- {obj}" for obj in eval.objections])
        
        return feedback_text
    
    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse validation response"""
        result = {
            "improvement_quality": "unknown",
            "estimated_score_change": 0.0,
            "objections_addressed": 0,
            "strengths_preserved": True,
            "summary": "Validation incomplete"
        }
        
        try:
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('IMPROVEMENT_QUALITY:'):
                    result["improvement_quality"] = line.split(':')[1].strip()
                elif line.startswith('ESTIMATED_SCORE_CHANGE:'):
                    score_text = line.split(':')[1].strip()
                    result["estimated_score_change"] = float(score_text.replace('+', '').replace('points', '').strip())
                elif line.startswith('OBJECTIONS_ADDRESSED:'):
                    result["objections_addressed"] = int(line.split(':')[1].strip())
                elif line.startswith('STRENGTHS_PRESERVED:'):
                    result["strengths_preserved"] = line.split(':')[1].strip().lower() == 'yes'
                elif line.startswith('SUMMARY:'):
                    result["summary"] = line.split(':', 1)[1].strip()
        except Exception as e:
            logger.warning(f"Failed to parse validation response: {e}")
        
        return result