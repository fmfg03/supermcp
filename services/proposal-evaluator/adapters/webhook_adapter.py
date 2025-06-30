"""
Webhook Adapter for Agentius Proposal Evaluator
==============================================

RESTful API for integration with frontend applications, automation systems,
and external services.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from ..main import ProposalEvaluator, ProposalContext
from ..core.event_system import global_event_bus, Event, EventType
from ..core.decision_tracer import global_tracer
from ..utils.logger import setup_logger
from ..utils.config import load_config

logger = setup_logger(__name__)

# Pydantic models for API
class ProposalRequest(BaseModel):
    """Request model for proposal evaluation"""
    client: str = Field(..., description="Client name")
    context: str = Field(..., description="Business context and background")
    objectives: List[str] = Field(default=[], description="Business objectives")
    constraints: Optional[List[str]] = Field(default=None, description="Constraints and limitations")
    tone: str = Field(default="professional", description="Proposal tone")
    judge_archetypes: Optional[List[str]] = Field(default=None, description="Specific judge archetypes to use")
    enable_parallel_variants: bool = Field(default=False, description="Enable parallel variant evaluation")
    max_iterations: int = Field(default=5, description="Maximum refinement iterations")
    min_score: float = Field(default=8.0, description="Minimum acceptable score")

class EvaluationStatus(BaseModel):
    """Status model for evaluation tracking"""
    id: str
    status: str  # pending, running, completed, failed
    client: str
    progress: Dict[str, Any]
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    current_stage: str
    error_message: Optional[str] = None

class ProposalResponse(BaseModel):
    """Response model for completed evaluation"""
    id: str
    client: str
    status: str
    final_score: float
    iterations: int
    final_proposal: str
    justification: str
    metadata: Dict[str, Any]
    decision_trace_url: str
    download_urls: Dict[str, str]

# FastAPI app
app = FastAPI(
    title="Agentius Proposal Evaluator API",
    description="AI-powered proposal generation and refinement engine",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_evaluations: Dict[str, Dict[str, Any]] = {}
evaluator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    global evaluator
    evaluator = ProposalEvaluator()
    logger.info("Agentius Webhook Adapter started")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Agentius Proposal Evaluator",
        "version": "2.0.0",
        "description": "AI-powered proposal generation and refinement engine",
        "endpoints": {
            "evaluate": "/api/v1/evaluate",
            "status": "/api/v1/status/{evaluation_id}",
            "download": "/api/v1/download/{evaluation_id}/{file_type}",
            "history": "/api/v1/history",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_evaluations": len(active_evaluations),
        "service": "agentius-proposal-evaluator"
    }

@app.post("/api/v1/evaluate", response_model=Dict[str, str])
async def start_evaluation(
    request: ProposalRequest, 
    background_tasks: BackgroundTasks
):
    """Start a new proposal evaluation"""
    
    try:
        # Create proposal context
        context = ProposalContext(
            client=request.client,
            context=request.context,
            objectives=request.objectives or ["Increase revenue", "Reduce costs", "Improve efficiency"],
            constraints=request.constraints,
            tone=request.tone
        )
        
        # Generate evaluation ID
        evaluation_id = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.client[:10]}"
        
        # Track evaluation
        active_evaluations[evaluation_id] = {
            "id": evaluation_id,
            "status": "pending",
            "client": request.client,
            "context": context,
            "request": request,
            "started_at": datetime.utcnow(),
            "current_stage": "initializing",
            "progress": {"current": 0, "total": 100}
        }
        
        # Start evaluation in background
        background_tasks.add_task(
            run_evaluation,
            evaluation_id,
            context,
            request
        )
        
        logger.info(f"Started evaluation {evaluation_id} for {request.client}")
        
        return {
            "evaluation_id": evaluation_id,
            "status": "started",
            "status_url": f"/api/v1/status/{evaluation_id}",
            "estimated_duration": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/status/{evaluation_id}", response_model=EvaluationStatus)
async def get_evaluation_status(evaluation_id: str):
    """Get the status of an evaluation"""
    
    if evaluation_id not in active_evaluations:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    eval_data = active_evaluations[evaluation_id]
    
    return EvaluationStatus(
        id=evaluation_id,
        status=eval_data["status"],
        client=eval_data["client"],
        progress=eval_data["progress"],
        started_at=eval_data["started_at"],
        current_stage=eval_data["current_stage"],
        error_message=eval_data.get("error_message")
    )

@app.get("/api/v1/result/{evaluation_id}", response_model=ProposalResponse)
async def get_evaluation_result(evaluation_id: str):
    """Get the result of a completed evaluation"""
    
    if evaluation_id not in active_evaluations:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    eval_data = active_evaluations[evaluation_id]
    
    if eval_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Evaluation not completed")
    
    result = eval_data["result"]
    
    return ProposalResponse(
        id=evaluation_id,
        client=result.client,
        status="completed",
        final_score=result.final_score,
        iterations=len(result.iterations),
        final_proposal=result.final_proposal,
        justification=result.justification,
        metadata=result.metadata,
        decision_trace_url=f"/api/v1/trace/{evaluation_id}",
        download_urls={
            "proposal": f"/api/v1/download/{evaluation_id}/proposal",
            "justification": f"/api/v1/download/{evaluation_id}/justification",
            "full_report": f"/api/v1/download/{evaluation_id}/report"
        }
    )

@app.get("/api/v1/download/{evaluation_id}/{file_type}")
async def download_file(evaluation_id: str, file_type: str):
    """Download evaluation files"""
    
    if evaluation_id not in active_evaluations:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    eval_data = active_evaluations[evaluation_id]
    
    if eval_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Evaluation not completed")
    
    result = eval_data["result"]
    
    # Generate file content based on type
    if file_type == "proposal":
        content = result.final_proposal
        filename = f"{result.client}_proposal.md"
        media_type = "text/markdown"
        
    elif file_type == "justification":
        content = result.justification
        filename = f"{result.client}_justification.txt"
        media_type = "text/plain"
        
    elif file_type == "report":
        # Generate comprehensive report
        trace = global_tracer.get_trace(evaluation_id)
        report = global_tracer.generate_transparency_report(evaluation_id)
        
        content = f"""# Agentius Evaluation Report
{report}

## Final Proposal
{result.final_proposal}

## Justification
{result.justification}

## Technical Details
- Evaluation ID: {evaluation_id}
- Total Iterations: {len(result.iterations)}
- Final Score: {result.final_score:.1f}/10
- Generated: {datetime.utcnow().isoformat()}
"""
        filename = f"{result.client}_complete_report.md"
        media_type = "text/markdown"
        
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Create temporary file
    temp_file = Path(f"/tmp/{filename}")
    temp_file.write_text(content)
    
    return FileResponse(
        path=str(temp_file),
        media_type=media_type,
        filename=filename
    )

@app.get("/api/v1/trace/{evaluation_id}")
async def get_decision_trace(evaluation_id: str):
    """Get the complete decision trace for an evaluation"""
    
    trace = global_tracer.get_trace(evaluation_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Decision trace not found")
    
    return {
        "evaluation_id": evaluation_id,
        "trace": trace,
        "decision_path": global_tracer.get_decision_path(evaluation_id),
        "score_history": global_tracer.get_score_history(evaluation_id),
        "fear_analysis": global_tracer.get_fear_analysis(evaluation_id),
        "transparency_report": global_tracer.generate_transparency_report(evaluation_id)
    }

@app.get("/api/v1/history")
async def get_evaluation_history(limit: int = 20):
    """Get recent evaluation history"""
    
    # Get recent evaluations from database
    try:
        response = evaluator.supabase.table("proposals").select(
            "id, client, score, timestamp, metadata"
        ).order("timestamp", desc=True).limit(limit).execute()
        
        return {
            "evaluations": response.data,
            "total": len(response.data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@app.post("/api/v1/upload-context")
async def upload_context_file(file: UploadFile = File(...)):
    """Upload context file for evaluation"""
    
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Only .txt and .md files are supported")
    
    try:
        content = await file.read()
        context_text = content.decode('utf-8')
        
        # Generate context ID for later use
        context_id = f"ctx_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Store temporarily (in production, use proper storage)
        temp_context_file = Path(f"/tmp/context_{context_id}.txt")
        temp_context_file.write_text(context_text)
        
        return {
            "context_id": context_id,
            "filename": file.filename,
            "size": len(context_text),
            "message": "Context uploaded successfully. Use context_id in evaluation request."
        }
        
    except Exception as e:
        logger.error(f"Failed to upload context: {e}")
        raise HTTPException(status_code=500, detail="Failed to process uploaded file")

@app.get("/api/v1/archetypes")
async def get_available_archetypes():
    """Get available judge archetypes"""
    
    from ..agents.specialized_judges import JudgeFactory
    
    archetypes = JudgeFactory.get_available_archetypes()
    
    return {
        "archetypes": archetypes,
        "descriptions": {
            "technical_founder": "Technical founder - fears loss of control and technical debt",
            "conservative_cfo": "Conservative CFO - fears financial risk and compliance issues",
            "growth_cmo": "Growth CMO - fears missed opportunities and brand damage",
            "bureaucratic_executive": "Corporate executive - fears process violations and career risk"
        }
    }

@app.websocket("/api/v1/stream/{evaluation_id}")
async def evaluation_stream(websocket, evaluation_id: str):
    """WebSocket endpoint for real-time evaluation updates"""
    
    await websocket.accept()
    
    try:
        while evaluation_id in active_evaluations:
            eval_data = active_evaluations[evaluation_id]
            
            # Send current status
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "status": eval_data["status"],
                    "progress": eval_data["progress"],
                    "current_stage": eval_data["current_stage"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            # Check if completed or failed
            if eval_data["status"] in ["completed", "failed"]:
                if eval_data["status"] == "completed":
                    await websocket.send_json({
                        "type": "evaluation_complete",
                        "data": {
                            "evaluation_id": evaluation_id,
                            "result_url": f"/api/v1/result/{evaluation_id}"
                        }
                    })
                break
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error for {evaluation_id}: {e}")
    finally:
        await websocket.close()

async def run_evaluation(
    evaluation_id: str, 
    context: ProposalContext, 
    request: ProposalRequest
):
    """Run evaluation in background task"""
    
    try:
        # Update status
        active_evaluations[evaluation_id]["status"] = "running"
        active_evaluations[evaluation_id]["current_stage"] = "generating_proposal"
        
        # Start decision trace
        global_tracer.start_trace(evaluation_id, {
            "client": context.client,
            "objectives": context.objectives,
            "tone": context.tone,
            "archetypes": request.judge_archetypes
        })
        
        # Run evaluation
        result = await evaluator.evaluate_proposal(
            context, 
            request.enable_parallel_variants
        )
        
        # Update status
        active_evaluations[evaluation_id]["status"] = "completed"
        active_evaluations[evaluation_id]["result"] = result
        active_evaluations[evaluation_id]["completed_at"] = datetime.utcnow()
        active_evaluations[evaluation_id]["current_stage"] = "completed"
        active_evaluations[evaluation_id]["progress"] = {"current": 100, "total": 100}
        
        # Complete trace
        global_tracer.complete_trace(evaluation_id, "completed")
        
        logger.info(f"Completed evaluation {evaluation_id} with score {result.final_score:.1f}/10")
        
    except Exception as e:
        logger.error(f"Evaluation {evaluation_id} failed: {e}")
        
        # Update status
        active_evaluations[evaluation_id]["status"] = "failed"
        active_evaluations[evaluation_id]["error_message"] = str(e)
        active_evaluations[evaluation_id]["current_stage"] = "failed"
        
        # Complete trace with error
        global_tracer.complete_trace(evaluation_id, "failed")

def start_webhook_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the webhook server"""
    logger.info(f"Starting Agentius Webhook Adapter on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    start_webhook_server()