"""
Event-Driven Architecture for Proposal Evaluator
===============================================

Agentius Core Event System - Orchestrates autonomous agent reactions
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class EventType(Enum):
    """Core event types in the Agentius system"""
    PROPOSAL_SUBMITTED = "proposal_submitted"
    BUILDER_COMPLETE = "builder_complete"
    JUDGE_READY = "judge_ready"
    CFO_EVALUATION_COMPLETE = "cfo_evaluation_complete"
    CMO_EVALUATION_COMPLETE = "cmo_evaluation_complete"
    CEO_EVALUATION_COMPLETE = "ceo_evaluation_complete"
    ALL_JUDGES_COMPLETE = "all_judges_complete"
    REFINER_READY = "refiner_ready"
    REFINER_COMPLETE = "refiner_complete"
    ITERATION_COMPLETE = "iteration_complete"
    EVALUATION_COMPLETE = "evaluation_complete"
    EVALUATION_FAILED = "evaluation_failed"
    THRESHOLD_REACHED = "threshold_reached"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"

@dataclass
class Event:
    """Core event structure"""
    id: str
    type: EventType
    payload: Dict[str, Any]
    context_id: str  # Proposal evaluation session ID
    agent_id: Optional[str] = None
    timestamp: datetime = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.id is None:
            self.id = str(uuid.uuid4())

@dataclass 
class TaskRegistration:
    """Persistent task registry entry"""
    id: str
    context_id: str
    task_type: str
    status: str  # pending, running, complete, failed
    agent_id: str
    depends_on: List[str]  # Event IDs this task depends on
    payload: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class EventBus:
    """
    Event-driven orchestration for Agentius
    Manages autonomous agent reactions and task scheduling
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.task_registry: Dict[str, TaskRegistration] = {}
        self.active_contexts: Dict[str, Dict[str, Any]] = {}
        
    async def emit(self, event: Event):
        """Emit an event to all subscribers"""
        logger.info(f"Emitting event: {event.type.value} for context {event.context_id}")
        
        # Store in history
        self.event_history.append(event)
        
        # Update context
        if event.context_id not in self.active_contexts:
            self.active_contexts[event.context_id] = {
                "events": [],
                "tasks": [],
                "state": "active",
                "created_at": event.timestamp
            }
        
        self.active_contexts[event.context_id]["events"].append(event)
        
        # Notify subscribers
        if event.type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event.type]:
                task = asyncio.create_task(handler(event))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for task completions
        await self._process_dependent_tasks(event)
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
        logger.debug(f"Subscribed handler to {event_type.value}")
    
    async def register_task(self, task: TaskRegistration):
        """Register a task in the persistent registry"""
        self.task_registry[task.id] = task
        
        # Add to context
        if task.context_id in self.active_contexts:
            self.active_contexts[task.context_id]["tasks"].append(task.id)
        
        logger.info(f"Registered task {task.id} for context {task.context_id}")
        
        # Check if task can run immediately
        await self._check_task_readiness(task.id)
    
    async def _check_task_readiness(self, task_id: str):
        """Check if a task's dependencies are met"""
        task = self.task_registry.get(task_id)
        if not task or task.status != "pending":
            return
        
        # Check dependencies
        context_events = [e.id for e in self.event_history if e.context_id == task.context_id]
        dependencies_met = all(dep_id in context_events for dep_id in task.depends_on)
        
        if dependencies_met:
            await self._execute_task(task_id)
    
    async def _process_dependent_tasks(self, event: Event):
        """Process tasks that depend on this event"""
        for task_id, task in self.task_registry.items():
            if (task.status == "pending" and 
                event.context_id == task.context_id and 
                event.id in task.depends_on):
                await self._check_task_readiness(task_id)
    
    async def _execute_task(self, task_id: str):
        """Execute a ready task"""
        task = self.task_registry[task_id]
        task.status = "running"
        task.started_at = datetime.utcnow()
        
        logger.info(f"Executing task {task_id}: {task.task_type}")
        
        try:
            # Task execution would be handled by specific agent handlers
            # This is a placeholder for the execution framework
            await self.emit(Event(
                id=str(uuid.uuid4()),
                type=EventType(f"{task.task_type}_started"),
                payload=task.payload,
                context_id=task.context_id,
                agent_id=task.agent_id
            ))
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            logger.error(f"Task {task_id} failed: {e}")
    
    def get_context_state(self, context_id: str) -> Dict[str, Any]:
        """Get the current state of an evaluation context"""
        return self.active_contexts.get(context_id, {})
    
    def get_event_chain(self, context_id: str) -> List[Event]:
        """Get the event chain for a context"""
        return [e for e in self.event_history if e.context_id == context_id]
    
    def get_task_status(self, context_id: str) -> Dict[str, Any]:
        """Get task status for a context"""
        context_tasks = [
            task for task in self.task_registry.values() 
            if task.context_id == context_id
        ]
        
        return {
            "total": len(context_tasks),
            "pending": len([t for t in context_tasks if t.status == "pending"]),
            "running": len([t for t in context_tasks if t.status == "running"]),
            "complete": len([t for t in context_tasks if t.status == "complete"]),
            "failed": len([t for t in context_tasks if t.status == "failed"]),
            "tasks": [asdict(t) for t in context_tasks]
        }

class AgentiusOrchestrator:
    """
    Main orchestrator for the Agentius proposal evaluation system
    Manages the complete event-driven workflow
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._setup_workflow_handlers()
    
    def _setup_workflow_handlers(self):
        """Set up the core workflow event handlers"""
        
        # Proposal submission starts the workflow
        self.event_bus.subscribe(
            EventType.PROPOSAL_SUBMITTED, 
            self._handle_proposal_submitted
        )
        
        # Builder completion triggers judge readiness
        self.event_bus.subscribe(
            EventType.BUILDER_COMPLETE,
            self._handle_builder_complete
        )
        
        # All judges complete triggers refiner readiness
        self.event_bus.subscribe(
            EventType.ALL_JUDGES_COMPLETE,
            self._handle_all_judges_complete
        )
        
        # Refiner completion triggers iteration check
        self.event_bus.subscribe(
            EventType.REFINER_COMPLETE,
            self._handle_refiner_complete
        )
        
        # Iteration completion triggers next cycle or termination
        self.event_bus.subscribe(
            EventType.ITERATION_COMPLETE,
            self._handle_iteration_complete
        )
    
    async def _handle_proposal_submitted(self, event: Event):
        """Handle new proposal submission"""
        logger.info(f"Orchestrating new proposal evaluation: {event.context_id}")
        
        # Register builder task
        builder_task = TaskRegistration(
            id=f"builder_{event.context_id}",
            context_id=event.context_id,
            task_type="build_proposal",
            status="pending",
            agent_id="builder_agent",
            depends_on=[event.id],
            payload=event.payload,
            created_at=datetime.utcnow()
        )
        
        await self.event_bus.register_task(builder_task)
    
    async def _handle_builder_complete(self, event: Event):
        """Handle builder completion"""
        proposal_text = event.payload.get("proposal_text")
        
        # Register judge tasks (parallel execution)
        judge_perspectives = ["CFO", "CMO", "CEO"]
        
        for perspective in judge_perspectives:
            judge_task = TaskRegistration(
                id=f"judge_{perspective}_{event.context_id}",
                context_id=event.context_id,
                task_type=f"judge_{perspective.lower()}",
                status="pending",
                agent_id=f"judge_{perspective.lower()}_agent",
                depends_on=[event.id],
                payload={
                    **event.payload,
                    "perspective": perspective,
                    "proposal_text": proposal_text
                },
                created_at=datetime.utcnow()
            )
            
            await self.event_bus.register_task(judge_task)
    
    async def _handle_all_judges_complete(self, event: Event):
        """Handle completion of all judge evaluations"""
        evaluations = event.payload.get("evaluations", [])
        
        # Check if refinement is needed
        avg_score = sum(e["score"] for e in evaluations) / len(evaluations)
        
        if avg_score >= 8.0:
            # Threshold reached, complete evaluation
            await self.event_bus.emit(Event(
                id=str(uuid.uuid4()),
                type=EventType.THRESHOLD_REACHED,
                payload=event.payload,
                context_id=event.context_id
            ))
        else:
            # Register refiner task
            refiner_task = TaskRegistration(
                id=f"refiner_{event.context_id}_{datetime.utcnow().timestamp()}",
                context_id=event.context_id,
                task_type="refine_proposal",
                status="pending",
                agent_id="refiner_agent",
                depends_on=[event.id],
                payload=event.payload,
                created_at=datetime.utcnow()
            )
            
            await self.event_bus.register_task(refiner_task)
    
    async def _handle_refiner_complete(self, event: Event):
        """Handle refiner completion"""
        iteration_count = event.payload.get("iteration_count", 0)
        
        await self.event_bus.emit(Event(
            id=str(uuid.uuid4()),
            type=EventType.ITERATION_COMPLETE,
            payload={
                **event.payload,
                "iteration_count": iteration_count + 1
            },
            context_id=event.context_id
        ))
    
    async def _handle_iteration_complete(self, event: Event):
        """Handle iteration completion and decide next steps"""
        iteration_count = event.payload.get("iteration_count", 0)
        max_iterations = event.payload.get("max_iterations", 5)
        
        if iteration_count >= max_iterations:
            await self.event_bus.emit(Event(
                id=str(uuid.uuid4()),
                type=EventType.MAX_ITERATIONS_REACHED,
                payload=event.payload,
                context_id=event.context_id
            ))
        else:
            # Continue with next iteration - trigger judges again
            refined_proposal = event.payload.get("refined_proposal")
            
            await self.event_bus.emit(Event(
                id=str(uuid.uuid4()),
                type=EventType.JUDGE_READY,
                payload={
                    **event.payload,
                    "proposal_text": refined_proposal
                },
                context_id=event.context_id
            ))

# Global event bus instance
global_event_bus = EventBus()
global_orchestrator = AgentiusOrchestrator(global_event_bus)