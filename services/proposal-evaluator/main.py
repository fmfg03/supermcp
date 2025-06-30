#!/usr/bin/env python3
"""
SuperMCP Proposal Evaluator Service
===================================

A multi-agent system for generating and refining business proposals through
iterative evaluation and feedback loops.

Pipeline:
1. BuilderAgent: Generates initial proposal
2. JudgeAgent: Evaluates from CFO/CMO/CEO perspectives
3. RefinerAgent: Iterates against objections
4. Loop until score >8/10 or no substantial objections

Features:
- CLI interface
- Telegram bot integration
- Supabase persistence
- Parallel variant evaluation
- Structured logging
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import typer
from supabase import create_client, Client
from pydantic import BaseModel, Field

# Import our agents
from agents.builder_agent import BuilderAgent
from agents.judge_agent import JudgeAgent
from agents.refiner_agent import RefinerAgent
from utils.logger import setup_logger
from utils.config import load_config

app = typer.Typer(help="SuperMCP Proposal Evaluator - Multi-agent proposal generation and refinement")
logger = setup_logger(__name__)

@dataclass
class ProposalContext:
    """Input context for proposal generation"""
    client: str
    context: str
    objectives: List[str]
    constraints: Optional[List[str]] = None
    tone: str = "professional"
    
@dataclass
class JudgeEvaluation:
    """Evaluation from a judge perspective"""
    perspective: str  # CFO, CMO, CEO
    score: float  # 0-10
    objections: List[str]
    suggestions: List[str]
    timestamp: datetime

@dataclass
class ProposalIteration:
    """Single iteration of proposal refinement"""
    iteration: int
    proposal: str
    evaluations: List[JudgeEvaluation]
    overall_score: float
    refinement_notes: str
    timestamp: datetime

@dataclass
class ProposalResult:
    """Final result of proposal evaluation process"""
    id: str
    client: str
    input_context: ProposalContext
    initial_proposal: str
    final_proposal: str
    iterations: List[ProposalIteration]
    final_score: float
    justification: str
    metadata: Dict
    created_at: datetime

class ProposalEvaluator:
    """Main service for proposal evaluation"""
    
    def __init__(self, config_path: str = "config/proposal_evaluator.yaml"):
        self.config = load_config(config_path)
        self.supabase = self._init_supabase()
        
        # Initialize agents
        self.builder_agent = BuilderAgent(self.config.get("builder_agent", {}))
        self.judge_agent = JudgeAgent(self.config.get("judge_agent", {}))
        self.refiner_agent = RefinerAgent(self.config.get("refiner_agent", {}))
        
        # Evaluation thresholds
        self.min_score = self.config.get("min_score", 8.0)
        self.max_iterations = self.config.get("max_iterations", 5)
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        url = self.config["supabase"]["url"]
        key = self.config["supabase"]["service_key"]
        return create_client(url, key)
    
    async def evaluate_proposal(
        self, 
        context: ProposalContext,
        enable_parallel_variants: bool = False
    ) -> ProposalResult:
        """
        Main evaluation pipeline
        """
        proposal_id = str(uuid.uuid4())
        logger.info(f"Starting proposal evaluation for {context.client} (ID: {proposal_id})")
        
        if enable_parallel_variants:
            return await self._evaluate_parallel_variants(proposal_id, context)
        else:
            return await self._evaluate_single_proposal(proposal_id, context)
    
    async def _evaluate_single_proposal(
        self, 
        proposal_id: str, 
        context: ProposalContext
    ) -> ProposalResult:
        """Evaluate a single proposal variant"""
        
        # Step 1: Generate initial proposal
        logger.info("BuilderAgent: Generating initial proposal...")
        initial_proposal = await self.builder_agent.generate_proposal(context)
        
        iterations = []
        current_proposal = initial_proposal
        
        # Step 2: Iterative refinement loop
        for iteration in range(self.max_iterations):
            logger.info(f"Iteration {iteration + 1}/{self.max_iterations}")
            
            # Judge evaluation
            evaluations = await self._judge_proposal(current_proposal, context)
            overall_score = sum(eval.score for eval in evaluations) / len(evaluations)
            
            # Check if we've reached our target
            if overall_score >= self.min_score:
                logger.info(f"Target score reached: {overall_score:.1f}/10")
                break
            
            # Check for substantial objections
            total_objections = sum(len(eval.objections) for eval in evaluations)
            if total_objections == 0:
                logger.info("No substantial objections found")
                break
            
            # Refine proposal
            refinement_notes = await self.refiner_agent.refine_proposal(
                current_proposal, 
                evaluations, 
                context
            )
            
            current_proposal = refinement_notes.refined_proposal
            
            # Store iteration
            iteration_data = ProposalIteration(
                iteration=iteration + 1,
                proposal=current_proposal,
                evaluations=evaluations,
                overall_score=overall_score,
                refinement_notes=refinement_notes.notes,
                timestamp=datetime.utcnow()
            )
            iterations.append(iteration_data)
            
            logger.info(f"Iteration {iteration + 1} score: {overall_score:.1f}/10")
        
        # Generate final justification
        justification = await self._generate_justification(
            initial_proposal, 
            current_proposal, 
            iterations
        )
        
        # Create result
        result = ProposalResult(
            id=proposal_id,
            client=context.client,
            input_context=context,
            initial_proposal=initial_proposal,
            final_proposal=current_proposal,
            iterations=iterations,
            final_score=iterations[-1].overall_score if iterations else 0,
            justification=justification,
            metadata={
                "total_iterations": len(iterations),
                "improvement": iterations[-1].overall_score - iterations[0].overall_score if iterations else 0,
                "agent_versions": {
                    "builder": self.builder_agent.version,
                    "judge": self.judge_agent.version,
                    "refiner": self.refiner_agent.version
                }
            },
            created_at=datetime.utcnow()
        )
        
        # Persist to database
        await self._save_proposal(result)
        
        return result
    
    async def _evaluate_parallel_variants(
        self, 
        proposal_id: str, 
        context: ProposalContext
    ) -> ProposalResult:
        """Evaluate multiple proposal variants in parallel"""
        logger.info("Evaluating parallel variants: aggressive vs diplomatic")
        
        # Create variant contexts
        aggressive_context = ProposalContext(
            client=context.client,
            context=context.context,
            objectives=context.objectives,
            constraints=context.constraints,
            tone="aggressive"
        )
        
        diplomatic_context = ProposalContext(
            client=context.client,
            context=context.context,
            objectives=context.objectives,
            constraints=context.constraints,
            tone="diplomatic"
        )
        
        # Generate variants in parallel
        aggressive_task = self._evaluate_single_proposal(f"{proposal_id}_aggressive", aggressive_context)
        diplomatic_task = self._evaluate_single_proposal(f"{proposal_id}_diplomatic", diplomatic_context)
        
        aggressive_result, diplomatic_result = await asyncio.gather(
            aggressive_task, 
            diplomatic_task
        )
        
        # Judge comparison
        winner = await self._compare_variants(aggressive_result, diplomatic_result)
        
        # Update winner with original ID
        winner.id = proposal_id
        winner.metadata["variant_comparison"] = {
            "aggressive_score": aggressive_result.final_score,
            "diplomatic_score": diplomatic_result.final_score,
            "winner": "aggressive" if winner == aggressive_result else "diplomatic"
        }
        
        # Save final result
        await self._save_proposal(winner)
        
        return winner
    
    async def _judge_proposal(
        self, 
        proposal: str, 
        context: ProposalContext
    ) -> List[JudgeEvaluation]:
        """Get evaluations from all judge perspectives"""
        perspectives = ["CFO", "CMO", "CEO"]
        evaluations = []
        
        for perspective in perspectives:
            evaluation = await self.judge_agent.evaluate(
                proposal, 
                context, 
                perspective
            )
            evaluations.append(evaluation)
        
        return evaluations
    
    async def _generate_justification(
        self, 
        initial: str, 
        final: str, 
        iterations: List[ProposalIteration]
    ) -> str:
        """Generate justification document"""
        justification = f"""# Proposal Evaluation Justification

## Executive Summary
This proposal underwent {len(iterations)} iterations of multi-perspective evaluation and refinement.

## Initial Proposal Score
{iterations[0].overall_score:.1f}/10

## Final Proposal Score  
{iterations[-1].overall_score:.1f}/10

## Improvement
+{iterations[-1].overall_score - iterations[0].overall_score:.1f} points

## Key Refinements Made:
"""
        
        for i, iteration in enumerate(iterations, 1):
            justification += f"\n### Iteration {i}\n"
            justification += f"**Score:** {iteration.overall_score:.1f}/10\n"
            justification += f"**Refinements:** {iteration.refinement_notes}\n"
            
            for eval in iteration.evaluations:
                if eval.objections:
                    justification += f"**{eval.perspective} Objections:**\n"
                    for objection in eval.objections:
                        justification += f"- {objection}\n"
        
        justification += f"\n## Final Assessment\n"
        justification += f"The proposal has been refined to meet high standards across all stakeholder perspectives.\n"
        
        return justification
    
    async def _compare_variants(
        self, 
        aggressive: ProposalResult, 
        diplomatic: ProposalResult
    ) -> ProposalResult:
        """Compare two proposal variants and select winner"""
        comparison = await self.judge_agent.compare_proposals(
            aggressive.final_proposal,
            diplomatic.final_proposal,
            aggressive.input_context
        )
        
        if comparison.winner == "proposal_1":
            return aggressive
        else:
            return diplomatic
    
    async def _save_proposal(self, result: ProposalResult):
        """Save proposal to Supabase"""
        try:
            data = {
                "id": result.id,
                "client": result.client,
                "input_context": asdict(result.input_context),
                "initial_proposal": result.initial_proposal,
                "final_proposal": result.final_proposal,
                "judge_logs": [asdict(iteration) for iteration in result.iterations],
                "score": result.final_score,
                "justification": result.justification,
                "metadata": result.metadata,
                "timestamp": result.created_at.isoformat()
            }
            
            response = self.supabase.table("proposals").insert(data).execute()
            logger.info(f"Proposal saved to database: {result.id}")
            
        except Exception as e:
            logger.error(f"Failed to save proposal: {e}")
            raise

# CLI Commands
@app.command()
def evaluate(
    client: str = typer.Option(..., help="Client name"),
    context_file: str = typer.Option(..., help="Path to context file"),
    objectives: List[str] = typer.Option([], help="Proposal objectives"),
    output_dir: str = typer.Option("./output", help="Output directory"),
    parallel: bool = typer.Option(False, help="Enable parallel variant evaluation"),
    config: str = typer.Option("config/proposal_evaluator.yaml", help="Config file path")
):
    """Evaluate a proposal for a client"""
    asyncio.run(_run_evaluation(client, context_file, objectives, output_dir, parallel, config))

async def _run_evaluation(
    client: str, 
    context_file: str, 
    objectives: List[str], 
    output_dir: str, 
    parallel: bool, 
    config: str
):
    """Run the evaluation pipeline"""
    # Load context
    context_path = Path(context_file)
    if not context_path.exists():
        typer.echo(f"Error: Context file not found: {context_file}")
        raise typer.Exit(1)
    
    context_content = context_path.read_text()
    
    # Create context object
    context = ProposalContext(
        client=client,
        context=context_content,
        objectives=objectives or ["Increase revenue", "Reduce costs", "Improve efficiency"]
    )
    
    # Initialize evaluator
    evaluator = ProposalEvaluator(config)
    
    # Run evaluation
    typer.echo(f"🚀 Starting proposal evaluation for {client}...")
    result = await evaluator.evaluate_proposal(context, parallel)
    
    # Save outputs
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save final proposal
    proposal_file = output_path / f"{client}_proposal_{result.id[:8]}.md"
    proposal_file.write_text(result.final_proposal)
    
    # Save justification
    justification_file = output_path / f"{client}_justification_{result.id[:8]}.txt"
    justification_file.write_text(result.justification)
    
    # Save full result as JSON
    result_file = output_path / f"{client}_result_{result.id[:8]}.json"
    result_file.write_text(json.dumps(asdict(result), indent=2, default=str))
    
    typer.echo(f"✅ Evaluation complete!")
    typer.echo(f"📊 Final Score: {result.final_score:.1f}/10")
    typer.echo(f"🔄 Iterations: {len(result.iterations)}")
    typer.echo(f"📁 Output saved to: {output_path}")

@app.command()
def list_proposals(
    client: Optional[str] = typer.Option(None, help="Filter by client"),
    limit: int = typer.Option(10, help="Number of proposals to show")
):
    """List recent proposals"""
    asyncio.run(_list_proposals(client, limit))

async def _list_proposals(client: Optional[str], limit: int):
    """List proposals from database"""
    evaluator = ProposalEvaluator()
    
    query = evaluator.supabase.table("proposals").select("*").order("timestamp", desc=True).limit(limit)
    
    if client:
        query = query.eq("client", client)
    
    response = query.execute()
    
    if not response.data:
        typer.echo("No proposals found")
        return
    
    for proposal in response.data:
        typer.echo(f"📋 {proposal['client']} - Score: {proposal['score']:.1f}/10 - {proposal['timestamp']}")

@app.command()
def get_proposal(
    proposal_id: str = typer.Argument(..., help="Proposal ID"),
    output_dir: str = typer.Option("./output", help="Output directory")
):
    """Get a specific proposal by ID"""
    asyncio.run(_get_proposal(proposal_id, output_dir))

async def _get_proposal(proposal_id: str, output_dir: str):
    """Retrieve proposal from database"""
    evaluator = ProposalEvaluator()
    
    response = evaluator.supabase.table("proposals").select("*").eq("id", proposal_id).execute()
    
    if not response.data:
        typer.echo(f"Proposal not found: {proposal_id}")
        return
    
    proposal = response.data[0]
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save files
    proposal_file = output_path / f"proposal_{proposal_id[:8]}.md"
    proposal_file.write_text(proposal["final_proposal"])
    
    justification_file = output_path / f"justification_{proposal_id[:8]}.txt"
    justification_file.write_text(proposal["justification"])
    
    typer.echo(f"✅ Proposal retrieved and saved to: {output_path}")

if __name__ == "__main__":
    app()