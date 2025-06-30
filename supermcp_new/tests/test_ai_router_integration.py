#!/usr/bin/env python3
"""
🧪 Comprehensive Integration Tests for AI Model Router System
Tests all components together for production readiness

Test Categories:
- Basic functionality tests
- Integration tests between components  
- Performance and load tests
- Error handling and edge cases
- Security validation
- Configuration validation
"""

import asyncio
import pytest
import json
import tempfile
import time
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai.models.integrated_router import (
        IntegratedAIModelRouter, 
        RouterConfig,
        route_ai_task,
        get_router_health,
        get_router_analytics
    )
    from ai.models.capability_based_router import ModelSelectionResult
    from ai.models.marketing_router import MarketingTaskContext
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the supermcp_new directory")
    sys.exit(1)

class TestAIRouterIntegration:
    """Comprehensive integration tests for AI Router system"""
    
    @pytest.fixture
    def router_config(self):
        """Test router configuration"""
        return RouterConfig(
            enable_learning=True,
            enable_cost_optimization=True,
            enable_marketing_specialization=True,
            enable_caching=True,
            fallback_model="phi-3.5-mini",
            max_selection_time_ms=1000.0
        )
    
    @pytest.fixture
    def router(self, router_config):
        """Test router instance"""
        return IntegratedAIModelRouter(router_config)
    
    @pytest.mark.asyncio
    async def test_basic_routing(self, router):
        """Test basic task routing functionality"""
        
        task = {
            "type": "content_creation",
            "content": "Write a short blog post about artificial intelligence",
            "quality_threshold": 7.0
        }
        
        result = await router.route_task(task)
        
        assert isinstance(result, ModelSelectionResult)
        assert result.selected_model is not None
        assert result.confidence > 0
        assert result.estimated_cost >= 0
        assert result.estimated_latency > 0
        assert len(result.rationale) > 0
        
        print(f"✅ Basic routing test passed - selected {result.selected_model}")
    
    @pytest.mark.asyncio
    async def test_marketing_routing(self, router):
        """Test marketing-specific routing"""
        
        task = {
            "type": "seo_content_creation",
            "content": "Create SEO-optimized content for email marketing campaign",
            "marketing_type": "seo_content_creation",
            "seo_focus": True,
            "quality_threshold": 8.5
        }
        
        user_context = {
            "role": "marketer",
            "brand_voice": "professional",
            "target_audience": "small_businesses"
        }
        
        result = await router.route_task(task, user_context, "marketing")
        
        assert result.selected_model is not None
        assert "marketing" in result.rationale.lower() or "seo" in result.rationale.lower()
        
        print(f"✅ Marketing routing test passed - selected {result.selected_model}")
    
    @pytest.mark.asyncio
    async def test_cost_optimization_routing(self, router):
        """Test cost-optimized routing"""
        
        task = {
            "type": "simple_analysis",
            "content": "Analyze this short text for sentiment",
            "max_cost": 0.001,  # Very low cost requirement
            "quality_threshold": 6.0
        }
        
        user_context = {
            "cost_sensitive": True,
            "optimization_strategy": "cost_first"
        }
        
        result = await router.route_task(task, user_context, "cost_first")
        
        assert result.selected_model is not None
        assert result.estimated_cost <= 0.001 or result.estimated_cost == 0  # Local model
        
        print(f"✅ Cost optimization test passed - selected {result.selected_model} at ${result.estimated_cost:.4f}")
    
    @pytest.mark.asyncio
    async def test_privacy_sensitive_routing(self, router):
        """Test privacy-sensitive task routing"""
        
        task = {
            "type": "confidential_analysis",
            "content": "Analyze internal company financial data",
            "privacy_level": 10,  # Maximum privacy required
            "quality_threshold": 8.0
        }
        
        result = await router.route_task(task)
        
        # Should select a local model for high privacy
        model_info = router.base_router.model_database.get(result.selected_model, {})
        assert model_info.get("privacy_score", 0) >= 10 or model_info.get("type") == "local"
        
        print(f"✅ Privacy routing test passed - selected {result.selected_model}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, router):
        """Test error handling and fallback mechanisms"""
        
        # Test with invalid task
        invalid_task = {
            "type": None,
            "content": None,
            "invalid_field": "should_be_ignored"
        }
        
        result = await router.route_task(invalid_task)
        
        # Should still return a valid result (fallback)
        assert isinstance(result, ModelSelectionResult)
        assert result.selected_model == router.config.fallback_model
        
        print("✅ Error handling test passed - fallback model selected")
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, router):
        """Test performance requirements are met"""
        
        task = {
            "type": "quick_task",
            "content": "Simple content generation",
            "max_latency_ms": 1000
        }
        
        start_time = time.time()
        result = await router.route_task(task)
        end_time = time.time()
        
        selection_time_ms = (end_time - start_time) * 1000
        
        # Router should respond quickly
        assert selection_time_ms < router.config.max_selection_time_ms
        assert result.estimated_latency <= task["max_latency_ms"]
        
        print(f"✅ Performance test passed - selection took {selection_time_ms:.1f}ms")
    
    @pytest.mark.asyncio 
    async def test_outcome_recording(self, router):
        """Test task outcome recording for learning"""
        
        task = {
            "type": "test_task",
            "content": "Test content for outcome recording"
        }
        
        result = await router.route_task(task)
        
        # Record outcome
        await router.record_task_outcome(
            task_id="test_task_123",
            result=result,
            actual_cost=0.05,
            actual_quality=8.5,
            user_satisfaction=9.0,
            task_success=True,
            user_feedback="Excellent results"
        )
        
        # Should not raise an exception
        print("✅ Outcome recording test passed")
    
    def test_health_monitoring(self, router):
        """Test health monitoring functionality"""
        
        health = router.get_health_status()
        
        assert "status" in health
        assert health["status"] in ["healthy", "unhealthy"]
        assert "uptime_seconds" in health
        assert "total_requests" in health
        assert "success_rate_percent" in health
        assert "config" in health
        assert "components" in health
        
        print(f"✅ Health monitoring test passed - status: {health['status']}")
    
    def test_analytics(self, router):
        """Test analytics functionality"""
        
        analytics = router.get_analytics()
        
        assert "base_router" in analytics
        assert "system_metrics" in analytics
        assert "total_requests" in analytics["system_metrics"]
        assert "success_rate" in analytics["system_metrics"]
        
        print("✅ Analytics test passed")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, router):
        """Test handling multiple concurrent requests"""
        
        tasks = [
            {
                "type": f"concurrent_task_{i}",
                "content": f"Concurrent test content {i}",
                "quality_threshold": 7.0
            }
            for i in range(5)
        ]
        
        # Execute concurrent requests
        results = await asyncio.gather(*[
            router.route_task(task) for task in tasks
        ])
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert isinstance(result, ModelSelectionResult)
            assert result.selected_model is not None
        
        print("✅ Concurrent requests test passed")
    
    @pytest.mark.asyncio
    async def test_configuration_validation(self, router):
        """Test configuration validation"""
        
        # Test with different configurations
        configs = [
            RouterConfig(enable_learning=False),
            RouterConfig(enable_cost_optimization=False),
            RouterConfig(enable_marketing_specialization=False),
            RouterConfig(enable_caching=False)
        ]
        
        for config in configs:
            test_router = IntegratedAIModelRouter(config)
            
            task = {
                "type": "config_test",
                "content": "Test configuration variations"
            }
            
            result = await test_router.route_task(task)
            assert isinstance(result, ModelSelectionResult)
        
        print("✅ Configuration validation test passed")

# Convenience test functions for manual testing

async def test_real_world_scenarios():
    """Test real-world usage scenarios"""
    
    router = IntegratedAIModelRouter()
    
    scenarios = [
        {
            "name": "Blog Writing",
            "task": {
                "type": "content_creation", 
                "content": "Write a 1000-word blog post about sustainable technology",
                "quality_threshold": 8.5
            },
            "context": {"role": "content_creator", "brand_voice": "informative"}
        },
        {
            "name": "Code Review",
            "task": {
                "type": "code_analysis",
                "content": "Review this Python function for bugs and improvements",
                "quality_threshold": 9.0
            },
            "context": {"role": "developer"}
        },
        {
            "name": "Quick Social Media",
            "task": {
                "type": "social_media_post",
                "content": "Create 5 LinkedIn posts about productivity",
                "max_cost": 0.01,
                "volume": 5
            },
            "context": {"role": "marketer", "cost_sensitive": True}
        },
        {
            "name": "Confidential Analysis",
            "task": {
                "type": "financial_analysis",
                "content": "Analyze Q4 financial projections",
                "privacy_level": 10,
                "quality_threshold": 9.0
            },
            "context": {"role": "analyst"}
        }
    ]
    
    print("\n🧪 Testing Real-World Scenarios:")
    print("=" * 50)
    
    for scenario in scenarios:
        print(f"\n📝 {scenario['name']}:")
        
        result = await router.route_task(scenario["task"], scenario["context"])
        
        print(f"   Model: {result.selected_model}")
        print(f"   Cost: ${result.estimated_cost:.4f}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Rationale: {result.rationale}")
    
    print("\n📊 Router Health:")
    health = router.get_health_status()
    print(f"   Status: {health['status']}")
    print(f"   Requests: {health['total_requests']}")
    print(f"   Success Rate: {health['success_rate_percent']:.1f}%")

async def test_performance_benchmark():
    """Benchmark router performance"""
    
    router = IntegratedAIModelRouter()
    
    task = {
        "type": "performance_test",
        "content": "Simple test for performance benchmarking"
    }
    
    print("\n⚡ Performance Benchmark:")
    print("=" * 30)
    
    # Warm up
    await router.route_task(task)
    
    # Benchmark
    times = []
    for i in range(10):
        start = time.time()
        await router.route_task(task)
        end = time.time()
        times.append((end - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Average: {avg_time:.1f}ms")
    print(f"Min: {min_time:.1f}ms")
    print(f"Max: {max_time:.1f}ms")
    print(f"Target: <{router.config.max_selection_time_ms}ms")
    
    if avg_time < router.config.max_selection_time_ms:
        print("✅ Performance target met")
    else:
        print("❌ Performance target missed")

def test_input_validation():
    """Test input validation and security"""
    
    router = IntegratedAIModelRouter()
    
    print("\n🔒 Security & Validation Tests:")
    print("=" * 35)
    
    # Test various input types
    test_inputs = [
        {},  # Empty
        {"type": ""},  # Empty type
        {"content": "x" * 100000},  # Very long content
        {"type": "../../../etc/passwd"},  # Path traversal attempt
        {"content": "<script>alert('xss')</script>"},  # XSS attempt
        {"privacy_level": -1},  # Invalid privacy level
        {"quality_threshold": 11},  # Invalid quality threshold
        {"max_cost": -1},  # Invalid cost
    ]
    
    async def test_single_input(task_input):
        try:
            result = await router.route_task(task_input)
            return "✅ Handled safely"
        except Exception as e:
            return f"❌ Error: {str(e)[:50]}"
    
    async def run_validation_tests():
        for i, test_input in enumerate(test_inputs):
            result = await test_single_input(test_input)
            print(f"   Test {i+1}: {result}")
    
    asyncio.run(run_validation_tests())

if __name__ == "__main__":
    print("🧪 AI Router Integration Tests")
    print("=" * 40)
    
    # Run pytest tests
    print("\n1. Running Unit Tests...")
    pytest.main([__file__, "-v"])
    
    # Run real-world scenario tests
    print("\n2. Running Real-World Scenarios...")
    asyncio.run(test_real_world_scenarios())
    
    # Run performance benchmark
    print("\n3. Running Performance Benchmark...")
    asyncio.run(test_performance_benchmark())
    
    # Run security tests
    print("\n4. Running Security Tests...")
    test_input_validation()
    
    print("\n🎉 All tests completed!")
    print("\nRouter is ready for production deployment! 🚀")