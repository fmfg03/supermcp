#!/usr/bin/env python3
"""
🔥 Integrated AI Model Router - Production System
Combines all router components into a unified production-ready system

Features:
- Unified interface for all router components
- Production configuration management
- Health monitoring and diagnostics
- Error handling and fallbacks
- Performance metrics and monitoring
- API compatibility with existing SuperMCP system
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback

from .capability_based_router import (
    CapabilityBasedModelRouter, 
    ModelSelectionResult, 
    TaskRequirements,
    router as base_router
)
from .marketing_router import (
    MarketingModelRouter, 
    MarketingTaskContext,
    route_marketing_task
)
from .smart_cost_optimizer import (
    SmartCostOptimizer,
    CostAnalysis,
    cost_optimizer
)
from .model_performance_learner import (
    ModelPerformanceLearner,
    TaskOutcome,
    performance_learner
)

logger = logging.getLogger(__name__)

@dataclass
class RouterConfig:
    """Configuration for integrated router"""
    enable_learning: bool = True
    enable_cost_optimization: bool = True
    enable_marketing_specialization: bool = True
    enable_caching: bool = True
    fallback_model: str = "phi-3.5-mini"
    max_selection_time_ms: float = 1000.0
    default_privacy_level: int = 5
    default_quality_threshold: float = 7.0

class IntegratedAIModelRouter:
    """
    Production-ready integrated router combining all specialized components
    """
    
    def __init__(self, config: RouterConfig = None):
        self.config = config or RouterConfig()
        
        # Initialize all router components
        self.base_router = base_router
        self.marketing_router = MarketingModelRouter()
        self.cost_optimizer = cost_optimizer
        self.performance_learner = performance_learner
        
        # System state
        self.is_healthy = True
        self.startup_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Performance tracking
        self.response_times = []
        self.model_usage_stats = {}
        
        logger.info("🔥 IntegratedAIModelRouter initialized successfully")
    
    async def route_task(self, 
                        task: Dict, 
                        user_context: Dict = None,
                        route_type: str = "auto") -> ModelSelectionResult:
        """
        Main routing method that intelligently selects the optimal model
        
        Args:
            task: Task specification
            user_context: User preferences and context
            route_type: "auto", "marketing", "cost_first", "quality_first"
        """
        
        start_time = datetime.now()
        self.total_requests += 1
        
        try:
            # Validate inputs
            task = await self._validate_and_enhance_task(task)
            user_context = user_context or {}
            
            # Determine routing strategy
            if route_type == "auto":
                route_type = await self._determine_routing_strategy(task, user_context)
            
            # Route based on strategy
            if route_type == "marketing" and self.config.enable_marketing_specialization:
                result = await self._route_marketing_task(task, user_context)
            elif route_type == "cost_first" and self.config.enable_cost_optimization:
                result = await self._route_cost_optimized(task, user_context)
            else:
                result = await self._route_standard(task, user_context)
            
            # Apply cost optimization if enabled
            if self.config.enable_cost_optimization and route_type != "cost_first":
                result = await self._apply_cost_optimization(result, task, user_context)
            
            # Track performance
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.response_times.append(response_time)
            self.model_usage_stats[result.selected_model] = self.model_usage_stats.get(result.selected_model, 0) + 1
            
            self.successful_requests += 1
            
            logger.info(f"✅ Routed task to {result.selected_model} in {response_time:.1f}ms")
            
            return result
            
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"❌ Router error: {e}")
            
            # Return fallback model
            return await self._get_fallback_result(task, str(e))
    
    async def _validate_and_enhance_task(self, task: Dict) -> Dict:
        """Validate and enhance task specification"""
        
        # Ensure required fields
        if "content" not in task:
            task["content"] = ""
        
        if "type" not in task:
            task["type"] = "general"
        
        # Set defaults
        task.setdefault("privacy_level", self.config.default_privacy_level)
        task.setdefault("quality_threshold", self.config.default_quality_threshold)
        task.setdefault("max_cost", 0.1)
        task.setdefault("max_latency_ms", 10000)
        task.setdefault("urgency", 5)
        
        return task
    
    async def _determine_routing_strategy(self, task: Dict, user_context: Dict) -> str:
        """Automatically determine the best routing strategy"""
        
        # Check for marketing indicators
        marketing_indicators = [
            "marketing", "content", "social", "email", "ad", "campaign", 
            "seo", "brand", "copy", "creative"
        ]
        
        task_text = f"{task.get('type', '')} {task.get('content', '')}".lower()
        
        if any(indicator in task_text for indicator in marketing_indicators):
            return "marketing"
        
        # Check for cost sensitivity
        if user_context.get("cost_sensitive", False) or task.get("max_cost", 1.0) < 0.01:
            return "cost_first"
        
        # Check for quality requirements
        if task.get("quality_threshold", 7.0) >= 9.0:
            return "quality_first"
        
        return "standard"
    
    async def _route_marketing_task(self, task: Dict, user_context: Dict) -> ModelSelectionResult:
        """Route marketing tasks using specialized router"""
        
        try:
            # Create marketing context if needed
            marketing_context = user_context.get("marketing_context")
            
            if not marketing_context:
                marketing_context = MarketingTaskContext(
                    campaign_type=task.get("marketing_type", "content_creation"),
                    brand_guidelines=user_context.get("brand_guidelines", {}),
                    target_audience=user_context.get("target_audience", "general"),
                    content_format=task.get("content_format", "general"),
                    seo_requirements=task.get("seo_focus", False),
                    volume_expected=task.get("volume", 1),
                    brand_voice=user_context.get("brand_voice", "professional"),
                    competitive_context=task.get("competitive_analysis", False),
                    urgency_level=task.get("urgency", 5),
                    quality_vs_cost_preference=user_context.get("quality_preference", 0.7)
                )
            
            return await self.marketing_router.route_marketing_task(task, marketing_context)
            
        except Exception as e:
            logger.warning(f"Marketing routing failed: {e}, falling back to standard")
            return await self._route_standard(task, user_context)
    
    async def _route_cost_optimized(self, task: Dict, user_context: Dict) -> ModelSelectionResult:
        """Route with cost optimization priority"""
        
        # Get candidate models
        candidates = []
        for model_name, model_info in self.base_router.model_database.items():
            candidates.append((model_name, model_info))
        
        # Optimize for cost
        user_context["optimization_strategy"] = "cost_first"
        
        try:
            best_model, cost_analysis = await self.cost_optimizer.optimize_model_selection(
                candidates, task, user_context
            )
            
            # Get full result from base router
            result = await self.base_router.select_optimal_model(task, user_context)
            
            # Override with cost-optimized selection if different
            if result.selected_model != best_model:
                result.selected_model = best_model
                result.estimated_cost = cost_analysis.total_adjusted_cost
                result.rationale = f"Cost-optimized: {cost_analysis.cost_efficiency_rating} efficiency"
            
            return result
            
        except Exception as e:
            logger.warning(f"Cost optimization failed: {e}, falling back to standard")
            return await self._route_standard(task, user_context)
    
    async def _route_standard(self, task: Dict, user_context: Dict) -> ModelSelectionResult:
        """Route using standard capability-based router"""
        return await self.base_router.select_optimal_model(task, user_context)
    
    async def _apply_cost_optimization(self, result: ModelSelectionResult, 
                                     task: Dict, user_context: Dict) -> ModelSelectionResult:
        """Apply cost optimization to existing result"""
        
        try:
            # Get cost analysis for selected model
            model_info = self.base_router.model_database.get(result.selected_model)
            if not model_info:
                return result
            
            cost_analysis = await self.cost_optimizer.calculate_total_value_score(
                model_info, task, user_context
            )
            
            # Update result with cost information
            result.estimated_cost = cost_analysis.total_adjusted_cost
            
            return result
            
        except Exception as e:
            logger.warning(f"Cost optimization application failed: {e}")
            return result
    
    async def _get_fallback_result(self, task: Dict, error_message: str) -> ModelSelectionResult:
        """Get fallback result when routing fails"""
        
        fallback_model = self.config.fallback_model
        model_info = self.base_router.model_database.get(fallback_model, {})
        
        return ModelSelectionResult(
            selected_model=fallback_model,
            model_info=model_info,
            score_breakdown={"error_fallback": 1.0},
            rationale=f"Fallback due to error: {error_message}",
            alternatives=[],
            estimated_cost=0.0,
            estimated_latency=model_info.get("avg_latency_ms", 1000),
            confidence=0.5,
            selection_time_ms=0.0,
            cache_hit=False
        )
    
    async def record_task_outcome(self, 
                                task_id: str,
                                result: ModelSelectionResult,
                                actual_cost: float = None,
                                actual_quality: float = None,
                                user_satisfaction: float = None,
                                task_success: bool = True,
                                user_feedback: str = "") -> None:
        """Record task outcome for learning"""
        
        if not self.config.enable_learning:
            return
        
        try:
            outcome = TaskOutcome(
                task_id=task_id,
                selected_model=result.selected_model,
                task_type="general",  # Could be enhanced to extract from original task
                required_capabilities=["general"],  # Could be enhanced
                estimated_cost=result.estimated_cost,
                actual_cost=actual_cost or result.estimated_cost,
                estimated_quality=8.0,  # Could be enhanced
                actual_quality=actual_quality or 8.0,
                estimated_latency=result.estimated_latency,
                actual_latency=result.estimated_latency,
                user_satisfaction=user_satisfaction or 8.0,
                task_success=task_success,
                completion_time=datetime.now(),
                user_feedback=user_feedback,
                context_metadata={}
            )
            
            await self.performance_learner.record_task_outcome(outcome)
            
        except Exception as e:
            logger.warning(f"Failed to record task outcome: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        
        uptime = datetime.now() - self.startup_time
        success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
        avg_response_time = sum(self.response_times[-100:]) / max(len(self.response_times[-100:]), 1)
        
        return {
            "status": "healthy" if self.is_healthy else "unhealthy",
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": success_rate,
            "avg_response_time_ms": avg_response_time,
            "model_usage_stats": self.model_usage_stats,
            "config": asdict(self.config),
            "components": {
                "base_router": True,
                "marketing_router": self.config.enable_marketing_specialization,
                "cost_optimizer": self.config.enable_cost_optimization,
                "performance_learner": self.config.enable_learning
            }
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get detailed analytics"""
        
        base_analytics = self.base_router.get_usage_analytics()
        
        if self.config.enable_marketing_specialization:
            marketing_analytics = self.marketing_router.get_marketing_analytics()
        else:
            marketing_analytics = {}
        
        return {
            "base_router": base_analytics,
            "marketing_router": marketing_analytics,
            "system_metrics": {
                "total_requests": self.total_requests,
                "success_rate": (self.successful_requests / max(self.total_requests, 1)) * 100,
                "avg_response_time": sum(self.response_times[-100:]) / max(len(self.response_times[-100:]), 1),
                "most_used_model": max(self.model_usage_stats.items(), key=lambda x: x[1])[0] if self.model_usage_stats else "none"
            }
        }

# Global integrated router instance
integrated_router = IntegratedAIModelRouter()

# Convenience functions for external usage
async def route_ai_task(task: Dict, user_context: Dict = None, route_type: str = "auto") -> ModelSelectionResult:
    """Main function for routing AI tasks"""
    return await integrated_router.route_task(task, user_context, route_type)

async def record_ai_task_outcome(task_id: str, result: ModelSelectionResult, **kwargs) -> None:
    """Record outcome of AI task for learning"""
    await integrated_router.record_task_outcome(task_id, result, **kwargs)

def get_router_health() -> Dict[str, Any]:
    """Get router health status"""
    return integrated_router.get_health_status()

def get_router_analytics() -> Dict[str, Any]:
    """Get router analytics"""
    return integrated_router.get_analytics()

# Example usage
async def example_usage():
    """Example of how to use the integrated router"""
    
    # Marketing task
    marketing_task = {
        "type": "content_creation",
        "content": "Create a blog post about AI automation for small businesses",
        "marketing_type": "seo_content_creation",
        "seo_focus": True,
        "quality_threshold": 8.5
    }
    
    user_context = {
        "role": "marketer",
        "brand_voice": "professional",
        "cost_sensitive": False
    }
    
    # Route the task
    result = await route_ai_task(marketing_task, user_context, "auto")
    
    print(f"Selected Model: {result.selected_model}")
    print(f"Rationale: {result.rationale}")
    print(f"Estimated Cost: ${result.estimated_cost:.4f}")
    print(f"Confidence: {result.confidence:.1%}")
    
    # Simulate task completion and record outcome
    await record_ai_task_outcome(
        task_id="example_task_1",
        result=result,
        actual_cost=result.estimated_cost * 0.95,  # Slightly lower than estimated
        actual_quality=9.0,  # High quality
        user_satisfaction=8.5,
        task_success=True,
        user_feedback="Excellent content quality"
    )
    
    # Get analytics
    health = get_router_health()
    analytics = get_router_analytics()
    
    print(f"\nRouter Health: {health['status']}")
    print(f"Success Rate: {health['success_rate_percent']:.1f}%")
    print(f"Most Used Model: {analytics['system_metrics']['most_used_model']}")

if __name__ == "__main__":
    asyncio.run(example_usage())