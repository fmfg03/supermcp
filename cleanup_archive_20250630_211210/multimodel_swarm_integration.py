#!/usr/bin/env python3
"""
🤖 Multi-Model AI Router ←→ Swarm Intelligence Integration
Connects the multi-model router as a specialized agent in the swarm

Features:
- Swarm agent with AI routing capabilities
- Automatic model selection for swarm tasks
- Cost optimization for swarm operations
- Real-time performance reporting
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import asdict
import threading
import websockets

from swarm_intelligence_system import SwarmAgentClient, SwarmMessage, MessageType, AgentType
from multi_model_system import MultiModelRouter, GenerationRequest, TaskType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiModelSwarmAgent(SwarmAgentClient):
    """Multi-model AI router as a swarm agent"""
    
    def __init__(self, swarm_port: int = 8400):
        # Initialize as swarm agent
        agent_info = {
            "name": "Multi-Model AI Router",
            "type": "multimodel",
            "role": "specialist",
            "capabilities": [
                "ai_routing",
                "model_selection",
                "cost_optimization",
                "fallback_handling",
                "performance_monitoring",
                "ai_inference",
                "text_generation",
                "code_generation",
                "analysis",
                "research",
                "translation"
            ],
            "specialization_scores": {
                "ai_routing": 0.95,
                "optimization": 0.9,
                "monitoring": 0.85,
                "ai_inference": 0.9
            }
        }
        
        super().__init__("multimodel", agent_info, swarm_port)
        
        # Initialize multi-model router
        self.router = MultiModelRouter()
        self.active_requests = {}
        
        # Performance metrics
        self.swarm_metrics = {
            "requests_processed": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "models_used": {},
            "cost_savings": 0.0  # From using free models
        }
    
    async def process_swarm_message(self, message: Dict[str, Any]):
        """Enhanced message processing for AI tasks"""
        await super().process_swarm_message(message)
        
        msg_type = message.get("message_type")
        content = message.get("content", {})
        sender_id = message.get("sender_id")
        
        # Handle AI generation requests
        if content.get("type") == "ai_generation_request":
            await self._handle_ai_generation_request(content, sender_id)
        elif content.get("type") == "model_recommendation_request":
            await self._handle_model_recommendation(content, sender_id)
        elif content.get("type") == "task_assignment" and self.agent_id in content.get("task", {}).get("assigned_agents", []):
            await self._handle_swarm_task_assignment(content)
        elif content.get("type") == "performance_query":
            await self._handle_performance_query(content, sender_id)
    
    async def _handle_ai_generation_request(self, content: Dict[str, Any], sender_id: str):
        """Handle AI generation request from swarm"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        prompt = content.get("prompt", "")
        task_type_str = content.get("task_type", "general")
        
        try:
            # Convert to task type
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.GENERAL
        
        # Create generation request
        gen_request = GenerationRequest(
            prompt=prompt,
            task_type=task_type,
            max_tokens=content.get("max_tokens", 1000),
            temperature=content.get("temperature", 0.7),
            force_model=content.get("force_model"),
            budget_limit=content.get("budget_limit", 0.0)
        )
        
        logger.info(f"🤖 Processing AI generation request from {sender_id}: {task_type.value}")
        
        # Store active request
        self.active_requests[request_id] = {
            "sender": sender_id,
            "start_time": datetime.now(),
            "task_type": task_type.value
        }
        
        # Generate response
        try:
            response = await self.router.generate(gen_request)
            
            # Update metrics
            self._update_swarm_metrics(response)
            
            # Send response back to requester
            ai_response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.MULTIMODEL,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "ai_generation_response",
                    "request_id": request_id,
                    "content": response.content,
                    "model_used": response.model_used,
                    "tokens_used": response.tokens_used,
                    "cost_estimate": response.cost_estimate,
                    "response_time": response.response_time,
                    "error": response.error,
                    "success": response.error is None
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(ai_response)))
            
            # Clean up active request
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            
            logger.info(f"✅ AI response sent to {sender_id}: {response.model_used} ({response.tokens_used} tokens)")
            
        except Exception as e:
            logger.error(f"❌ Error generating AI response: {e}")
            
            # Send error response
            error_response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.MULTIMODEL,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "ai_generation_response",
                    "request_id": request_id,
                    "content": "",
                    "error": str(e),
                    "success": False
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(error_response)))
    
    async def _handle_model_recommendation(self, content: Dict[str, Any], sender_id: str):
        """Handle model recommendation request"""
        task_type_str = content.get("task_type", "general")
        budget_limit = content.get("budget_limit", 0.0)
        
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.GENERAL
        
        # Get model recommendation
        recommended_model = self.router.select_model(task_type, budget_limit)
        
        if recommended_model:
            model_config = self.router.models[recommended_model]
            recommendation = {
                "model": recommended_model,
                "provider": model_config.provider.value,
                "cost_per_1k_tokens": model_config.cost_per_1k_tokens,
                "specializations": [t.value for t in model_config.specializations],
                "priority": model_config.priority
            }
        else:
            recommendation = {
                "model": None,
                "error": "No suitable model found"
            }
        
        # Send recommendation
        rec_response = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id=self.agent_id,
            sender_type=AgentType.MULTIMODEL,
            message_type=MessageType.RESPONSE,
            content={
                "type": "model_recommendation_response",
                "request_id": content.get("request_id"),
                "recommendation": recommendation,
                "task_type": task_type_str,
                "budget_limit": budget_limit
            },
            recipients=[sender_id]
        )
        
        await self.websocket.send(json.dumps(asdict(rec_response)))
        logger.info(f"📋 Model recommendation sent to {sender_id}: {recommended_model}")
    
    async def _handle_swarm_task_assignment(self, content: Dict[str, Any]):
        """Handle task assignment from swarm coordinator"""
        task = content.get("task", {})
        task_id = task.get("id")
        task_description = task.get("description", "")
        requirements = task.get("requirements", [])
        
        logger.info(f"📋 Assigned swarm task: {task.get('title', 'Unknown Task')}")
        
        # Analyze task to determine AI approach
        if any(req in ["ai_inference", "text_generation", "analysis"] for req in requirements):
            # This is an AI task
            task_type = self._determine_task_type_from_description(task_description)
            
            # Process the task
            gen_request = GenerationRequest(
                prompt=f"Task: {task_description}\n\nPlease complete this task:",
                task_type=task_type,
                max_tokens=2000,
                temperature=0.6
            )
            
            try:
                response = await self.router.generate(gen_request)
                
                # Report task completion
                completion_msg = SwarmMessage(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    sender_id=self.agent_id,
                    sender_type=AgentType.MULTIMODEL,
                    message_type=MessageType.BROADCAST,
                    content={
                        "type": "task_completion",
                        "task_id": task_id,
                        "result": response.content,
                        "model_used": response.model_used,
                        "tokens_used": response.tokens_used,
                        "cost_estimate": response.cost_estimate,
                        "success": response.error is None
                    }
                )
                
                await self.websocket.send(json.dumps(asdict(completion_msg)))
                logger.info(f"✅ Completed swarm task {task_id} using {response.model_used}")
                
            except Exception as e:
                logger.error(f"❌ Failed to complete swarm task {task_id}: {e}")
    
    def _determine_task_type_from_description(self, description: str) -> TaskType:
        """Determine task type from description"""
        description = description.lower()
        
        if any(word in description for word in ["code", "programming", "function", "script"]):
            return TaskType.CODE
        elif any(word in description for word in ["research", "search", "investigate", "find"]):
            return TaskType.RESEARCH
        elif any(word in description for word in ["analyze", "analysis", "examine", "evaluate"]):
            return TaskType.ANALYSIS
        elif any(word in description for word in ["translate", "translation", "language"]):
            return TaskType.TRANSLATION
        elif any(word in description for word in ["creative", "story", "poem", "creative"]):
            return TaskType.CREATIVE
        elif any(word in description for word in ["math", "calculate", "equation", "solve"]):
            return TaskType.MATH
        else:
            return TaskType.GENERAL
    
    async def _handle_performance_query(self, content: Dict[str, Any], sender_id: str):
        """Handle performance query"""
        performance_data = {
            "swarm_metrics": self.swarm_metrics,
            "router_stats": self.router.usage_stats,
            "active_requests": len(self.active_requests),
            "available_models": len(self.router.models),
            "timestamp": datetime.now().isoformat()
        }
        
        perf_response = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id=self.agent_id,
            sender_type=AgentType.MULTIMODEL,
            message_type=MessageType.RESPONSE,
            content={
                "type": "performance_response",
                "request_id": content.get("request_id"),
                "performance_data": performance_data
            },
            recipients=[sender_id]
        )
        
        await self.websocket.send(json.dumps(asdict(perf_response)))
    
    def _update_swarm_metrics(self, response):
        """Update swarm performance metrics"""
        self.swarm_metrics["requests_processed"] += 1
        self.swarm_metrics["total_tokens"] += response.tokens_used
        self.swarm_metrics["total_cost"] += response.cost_estimate
        
        # Update average response time
        current_avg = self.swarm_metrics["average_response_time"]
        count = self.swarm_metrics["requests_processed"]
        new_avg = ((current_avg * (count - 1)) + response.response_time) / count
        self.swarm_metrics["average_response_time"] = new_avg
        
        # Track models used
        model = response.model_used
        if model not in self.swarm_metrics["models_used"]:
            self.swarm_metrics["models_used"][model] = 0
        self.swarm_metrics["models_used"][model] += 1
        
        # Calculate cost savings (from free models)
        if response.cost_estimate == 0.0 and response.tokens_used > 0:
            # Estimate savings by comparing to average paid model cost
            estimated_paid_cost = (response.tokens_used / 1000) * 0.01  # $0.01 per 1k tokens average
            self.swarm_metrics["cost_savings"] += estimated_paid_cost
    
    async def send_proactive_suggestions(self):
        """Send proactive AI suggestions to swarm"""
        while self.running:
            try:
                await asyncio.sleep(600)  # Every 10 minutes
                
                if self.swarm_metrics["requests_processed"] > 5:
                    # Analyze usage patterns and suggest optimizations
                    most_used_model = max(self.swarm_metrics["models_used"].items(), key=lambda x: x[1])[0] if self.swarm_metrics["models_used"] else "none"
                    total_cost = self.swarm_metrics["total_cost"]
                    cost_savings = self.swarm_metrics["cost_savings"]
                    
                    suggestion_msg = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id=self.agent_id,
                        sender_type=AgentType.MULTIMODEL,
                        message_type=MessageType.BROADCAST,
                        content={
                            "type": "ai_optimization_suggestion",
                            "insights": [
                                f"Most used model: {most_used_model}",
                                f"Total cost savings from free models: ${cost_savings:.2f}",
                                f"Average response time: {self.swarm_metrics['average_response_time']:.2f}s",
                                f"Processed {self.swarm_metrics['requests_processed']} AI requests"
                            ],
                            "recommendations": [
                                "Consider using local models for simple tasks to reduce costs",
                                "Batch similar requests for better efficiency",
                                "Monitor model performance for optimal routing"
                            ]
                        }
                    )
                    
                    await self.websocket.send(json.dumps(asdict(suggestion_msg)))
                    logger.info("💡 Sent proactive AI optimization suggestions to swarm")
                    
            except Exception as e:
                logger.error(f"Error sending proactive suggestions: {e}")

async def main():
    """Main function to run the multi-model swarm agent"""
    print("🤖 Multi-Model AI Router ←→ Swarm Integration")
    print("=" * 60)
    print("🎯 Features:")
    print("   • AI routing for swarm tasks")
    print("   • Automatic model selection")
    print("   • Cost optimization")
    print("   • Performance monitoring")
    print("   • Fallback handling")
    print("=" * 60)
    print("🔗 Connecting to swarm...")
    
    # Create and start the multi-model swarm agent
    agent = MultiModelSwarmAgent()
    
    # Start proactive suggestions
    asyncio.create_task(agent.send_proactive_suggestions())
    
    # Connect to swarm
    await agent.connect_to_swarm()

if __name__ == "__main__":
    asyncio.run(main())