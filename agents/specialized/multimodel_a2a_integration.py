#!/usr/bin/env python3
"""
🔗 SuperMCP A2A Multi-Model Integration
Integrates the Multi-Model Router into the existing A2A Agent system

This module creates a new A2A agent "multimodel" that provides unified AI access
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from multi_model_system import MultiModelRouter, GenerationRequest, TaskType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiModelA2AAgent:
    """A2A Agent wrapper for Multi-Model Router"""
    
    def __init__(self):
        self.agent_id = "multimodel"
        self.agent_name = "Universal AI Router"
        self.agent_description = "Unified access to all AI models with intelligent routing"
        self.router = MultiModelRouter()
        
        # A2A Agent capabilities
        self.capabilities = {
            "text_generation": True,
            "code_generation": True,
            "research": True,
            "analysis": True,
            "chat": True,
            "translation": True,
            "cost_optimization": True,
            "model_selection": True
        }
        
        # Status
        self.status = "active"
        self.last_heartbeat = datetime.now()
        
    async def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A agent request"""
        try:
            # Extract request data
            request_type = message.get("type", "generate")
            payload = message.get("payload", {})
            
            if request_type == "generate":
                return await self._handle_generate(payload)
            elif request_type == "status":
                return await self._handle_status()
            elif request_type == "models":
                return await self._handle_models()
            elif request_type == "stats":
                return await self._handle_stats()
            else:
                return {
                    "success": False,
                    "error": f"Unknown request type: {request_type}",
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text generation request"""
        
        # Create generation request
        req = GenerationRequest(
            prompt=payload.get("prompt", ""),
            task_type=TaskType(payload.get("task_type", "general")),
            max_tokens=payload.get("max_tokens", 1000),
            temperature=payload.get("temperature", 0.7),
            force_model=payload.get("force_model"),
            budget_limit=payload.get("budget_limit", 0.0)
        )
        
        # Generate response
        response = await self.router.generate(req)
        
        # Return A2A format
        return {
            "success": response.error is None,
            "agent_id": self.agent_id,
            "response": {
                "content": response.content,
                "model_used": response.model_used,
                "tokens_used": response.tokens_used,
                "cost_estimate": response.cost_estimate,
                "response_time": response.response_time,
                "error": response.error
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_status(self) -> Dict[str, Any]:
        """Handle status request"""
        
        # Count available models
        available_models = 0
        for name, config in self.router.models.items():
            if config.requires_api_key:
                provider_key = config.provider.value
                if self.router.api_keys.get(provider_key):
                    available_models += 1
            else:
                available_models += 1
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "status": self.status,
            "response": {
                "agent_name": self.agent_name,
                "description": self.agent_description,
                "capabilities": self.capabilities,
                "models_available": available_models,
                "total_models": len(self.router.models),
                "last_heartbeat": self.last_heartbeat.isoformat(),
                "uptime": (datetime.now() - self.last_heartbeat).total_seconds()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_models(self) -> Dict[str, Any]:
        """Handle models list request"""
        
        models_info = []
        for name, config in self.router.models.items():
            # Check if model is available
            available = True
            if config.requires_api_key:
                provider_key = config.provider.value
                available = bool(self.router.api_keys.get(provider_key))
            
            models_info.append({
                "name": name,
                "provider": config.provider.value,
                "cost_per_1k_tokens": config.cost_per_1k_tokens,
                "specializations": [t.value for t in config.specializations],
                "priority": config.priority,
                "available": available,
                "local": not config.requires_api_key
            })
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "response": {
                "models": models_info,
                "total_models": len(models_info),
                "available_models": len([m for m in models_info if m["available"]]),
                "local_models": len([m for m in models_info if m["local"]])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_stats(self) -> Dict[str, Any]:
        """Handle stats request"""
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "response": {
                "usage_stats": self.router.usage_stats,
                "total_requests": sum(stats["requests"] for stats in self.router.usage_stats.values()),
                "total_tokens": sum(stats["tokens"] for stats in self.router.usage_stats.values()),
                "total_cost": sum(stats["cost"] for stats in self.router.usage_stats.values())
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def heartbeat(self):
        """Update heartbeat"""
        self.last_heartbeat = datetime.now()
    
    async def start_agent(self):
        """Start the A2A agent"""
        logger.info(f"🤖 Starting A2A agent: {self.agent_name}")
        logger.info(f"🔌 Agent ID: {self.agent_id}")
        logger.info(f"⚡ Models available: {len(self.router.models)}")
        
        # Register with A2A system (implementation depends on your A2A framework)
        await self._register_with_a2a()
        
        # Start heartbeat loop
        await self._heartbeat_loop()
    
    async def _register_with_a2a(self):
        """Register with A2A system"""
        # This would integrate with your existing A2A registration system
        # For now, just log the registration
        
        registration_data = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.agent_description,
            "capabilities": self.capabilities,
            "endpoints": {
                "generate": "/multimodel/generate",
                "status": "/multimodel/status", 
                "models": "/multimodel/models",
                "stats": "/multimodel/stats"
            },
            "cost_optimization": True,
            "local_models_available": True
        }
        
        logger.info(f"📝 Registering with A2A system: {json.dumps(registration_data, indent=2)}")
    
    async def _heartbeat_loop(self):
        """Heartbeat loop"""
        while True:
            try:
                self.heartbeat()
                logger.debug(f"💓 Heartbeat: {self.agent_id}")
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)

# Integration functions for existing A2A system
class A2AMultiModelIntegration:
    """Integration layer for existing A2A system"""
    
    def __init__(self):
        self.agent = MultiModelA2AAgent()
    
    async def register_multimodel_agent(self, a2a_system):
        """Register multimodel agent with existing A2A system"""
        
        # Add to agent registry
        agent_config = {
            "id": "multimodel",
            "name": "Universal AI Router",
            "type": "ai_router",
            "priority": 1,  # High priority for AI tasks
            "capabilities": self.agent.capabilities,
            "cost_optimization": True,
            "local_first": True  # Prefer local models
        }
        
        # Register endpoints
        endpoints = {
            "multimodel_generate": self._handle_generate_wrapper,
            "multimodel_status": self._handle_status_wrapper,
            "multimodel_models": self._handle_models_wrapper,
            "multimodel_stats": self._handle_stats_wrapper
        }
        
        return agent_config, endpoints
    
    async def _handle_generate_wrapper(self, request_data):
        """Wrapper for A2A system compatibility"""
        message = {
            "type": "generate",
            "payload": request_data
        }
        return await self.agent.handle_request(message)
    
    async def _handle_status_wrapper(self, request_data):
        """Wrapper for A2A system compatibility"""
        message = {
            "type": "status",
            "payload": request_data
        }
        return await self.agent.handle_request(message)
    
    async def _handle_models_wrapper(self, request_data):
        """Wrapper for A2A system compatibility"""
        message = {
            "type": "models", 
            "payload": request_data
        }
        return await self.agent.handle_request(message)
    
    async def _handle_stats_wrapper(self, request_data):
        """Wrapper for A2A system compatibility"""
        message = {
            "type": "stats",
            "payload": request_data
        }
        return await self.agent.handle_request(message)

# Example usage for integration
async def integrate_with_supermcp():
    """Example integration with SuperMCP system"""
    
    # Create integration
    integration = A2AMultiModelIntegration()
    
    # Start the agent
    await integration.agent.start_agent()
    
    # Example: How this would work with your existing A2A system
    logger.info("🔗 MultiModel agent ready for A2A integration")
    logger.info("📋 Available for tasks:")
    logger.info("   - Text generation with cost optimization")
    logger.info("   - Code generation (DeepSeek priority)")
    logger.info("   - Research tasks (Perplexity priority)")
    logger.info("   - Analysis tasks (Claude priority)")
    logger.info("   - Chat (Local models priority)")
    logger.info("   - Translation (Google AI priority)")

# Test function
async def test_multimodel_agent():
    """Test the multimodel agent"""
    
    agent = MultiModelA2AAgent()
    
    # Test generation
    test_request = {
        "type": "generate",
        "payload": {
            "prompt": "Write a simple Python function to calculate fibonacci numbers",
            "task_type": "code",
            "max_tokens": 500
        }
    }
    
    logger.info("🧪 Testing multimodel agent...")
    response = await agent.handle_request(test_request)
    
    if response["success"]:
        logger.info("✅ Test successful!")
        logger.info(f"Model used: {response['response']['model_used']}")
        logger.info(f"Tokens: {response['response']['tokens_used']}")
        logger.info(f"Cost: ${response['response']['cost_estimate']:.4f}")
        logger.info(f"Response time: {response['response']['response_time']:.2f}s")
    else:
        logger.error(f"❌ Test failed: {response['error']}")
    
    return response

if __name__ == "__main__":
    print("🔗 SuperMCP Multi-Model A2A Integration")
    print("=" * 50)
    print("🤖 Creates 'multimodel' A2A agent")
    print("🧠 Intelligent routing across all AI models")
    print("💰 Cost optimization with local-first priority")
    print("🔌 Integrates with existing A2A infrastructure")
    print("=" * 50)
    
    # Run test
    asyncio.run(test_multimodel_agent())