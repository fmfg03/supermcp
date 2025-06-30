#!/usr/bin/env python3
"""
🎯 Marketing-Specialized AI Model Router
Optimized routing for marketing tasks with domain-specific intelligence

Features:
- Marketing-specific capability weights
- Campaign-aware model selection
- Brand consistency optimization
- Content type specialization
- SEO-optimized routing decisions
- Cost efficiency for high-volume marketing tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from .capability_based_router import (
    CapabilityBasedModelRouter, 
    ModelSelectionResult, 
    TaskRequirements,
    ModelCostCalculator
)

logger = logging.getLogger(__name__)

@dataclass
class MarketingTaskContext:
    """Marketing-specific context for task routing"""
    campaign_type: str
    brand_guidelines: Dict[str, Any]
    target_audience: str
    content_format: str
    seo_requirements: bool
    volume_expected: int
    brand_voice: str
    competitive_context: bool
    urgency_level: int
    quality_vs_cost_preference: float  # 0.0 = cost priority, 1.0 = quality priority

class MarketingModelRouter(CapabilityBasedModelRouter):
    """Router especializado para tareas de marketing con optimizaciones específicas"""
    
    def __init__(self):
        super().__init__()
        
        # Marketing-specific capability weights
        self.marketing_weights = {
            # Core marketing capabilities
            "creative_writing": 1.5,
            "business_writing": 1.4,
            "content_generation": 1.3,
            "brand_consistency": 1.4,
            "persuasive_writing": 1.3,
            "copywriting": 1.4,
            
            # SEO and digital marketing
            "seo_optimization": 1.3,
            "keyword_integration": 1.2,
            "meta_description": 1.2,
            "content_optimization": 1.2,
            
            # Market analysis
            "trend_analysis": 1.2,
            "competitor_analysis": 1.2,
            "market_research": 1.1,
            "audience_analysis": 1.1,
            
            # Efficiency for volume
            "cost_efficiency": 1.3,
            "batch_processing": 1.2,
            "speed": 1.1,
            
            # Content types
            "social_media": 1.2,
            "email_marketing": 1.2,
            "blog_content": 1.1,
            "product_descriptions": 1.1,
            "ad_copy": 1.3,
            
            # Brand and voice
            "tone_adaptation": 1.2,
            "brand_voice_consistency": 1.3,
            "personality_matching": 1.1
        }
        
        # Marketing task type to model preferences
        self.marketing_task_preferences = {
            "content_research": {
                "optimal_models": ["deepseek-r1", "gemini-1.5-pro", "claude-3-5-sonnet"],
                "fallbacks": ["claude-3-haiku", "gemini-1.5-flash"],
                "rationale": "Privacy + comprehensive analysis for competitive research",
                "avoid_apis_for_competitive": True
            },
            
            "seo_content_creation": {
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o-mini", "llama3.3-70b"],
                "fallbacks": ["gemini-1.5-flash"],
                "rationale": "Content quality + SEO understanding + keyword integration",
                "prefer_quality": True
            },
            
            "social_media_batch": {
                "optimal_models": ["gemini-1.5-flash", "phi-3.5-mini", "claude-3-haiku"],
                "fallbacks": ["llama3.3-70b"],
                "rationale": "High volume + cost efficiency + quick turnaround",
                "optimize_for_volume": True
            },
            
            "competitor_analysis": {
                "optimal_models": ["gpt-4o", "o1-pro", "deepseek-r1"],
                "fallbacks": ["claude-3-5-sonnet"],
                "rationale": "Strategic analysis + business insight + competitive intelligence",
                "require_privacy": True
            },
            
            "brand_content_review": {
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o"],
                "fallbacks": ["deepseek-r1", "llama3.3-70b"],
                "rationale": "Quality assessment + brand understanding + consistency check",
                "require_quality": True
            },
            
            "ad_copy_creation": {
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o-mini"],
                "fallbacks": ["gemini-1.5-flash"],
                "rationale": "Persuasive writing + conversion optimization + A/B testing support",
                "optimize_for_conversion": True
            },
            
            "email_marketing": {
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o-mini"],
                "fallbacks": ["claude-3-haiku"],
                "rationale": "Personalization + email best practices + deliverability awareness",
                "require_personalization": True
            },
            
            "product_descriptions": {
                "optimal_models": ["claude-3-5-sonnet", "gemini-1.5-flash"],
                "fallbacks": ["gpt-4o-mini"],
                "rationale": "Feature highlighting + benefits focus + SEO optimization",
                "balance_features_benefits": True
            },
            
            "market_research": {
                "optimal_models": ["gpt-4o", "gemini-1.5-pro", "o1-pro"],
                "fallbacks": ["claude-3-5-sonnet"],
                "rationale": "Data analysis + trend identification + strategic insights",
                "require_analytical_depth": True
            },
            
            "campaign_strategy": {
                "optimal_models": ["o1-pro", "gpt-4o", "claude-3-5-sonnet"],
                "fallbacks": ["deepseek-r1"],
                "rationale": "Strategic thinking + campaign planning + ROI optimization",
                "require_strategic_thinking": True
            },
            
            "content_personalization": {
                "optimal_models": ["gpt-4o", "claude-3-5-sonnet"],
                "fallbacks": ["gpt-4o-mini"],
                "rationale": "Audience adaptation + personalization + dynamic content",
                "require_personalization": True
            },
            
            "influencer_content": {
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o"],
                "fallbacks": ["llama3.3-70b"],
                "rationale": "Authentic voice + platform optimization + engagement focus",
                "optimize_for_authenticity": True
            }
        }
        
        # Content format specific optimizations
        self.content_format_preferences = {
            "blog_post": {
                "preferred_capabilities": ["long_form_writing", "seo_optimization", "research_synthesis"],
                "min_quality_threshold": 8.0,
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o"]
            },
            
            "social_media_post": {
                "preferred_capabilities": ["concise_writing", "engagement_optimization", "hashtag_optimization"],
                "max_latency": 2000,
                "optimal_models": ["gemini-1.5-flash", "claude-3-haiku"]
            },
            
            "email_subject_line": {
                "preferred_capabilities": ["persuasive_writing", "a_b_testing", "open_rate_optimization"],
                "max_cost": 0.001,
                "optimal_models": ["phi-3.5-mini", "gemini-1.5-flash"]
            },
            
            "product_page": {
                "preferred_capabilities": ["conversion_optimization", "feature_highlighting", "seo_optimization"],
                "min_quality_threshold": 8.5,
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o-mini"]
            },
            
            "video_script": {
                "preferred_capabilities": ["storytelling", "visual_thinking", "engagement_optimization"],
                "min_quality_threshold": 8.0,
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o"]
            },
            
            "press_release": {
                "preferred_capabilities": ["formal_writing", "news_style", "brand_representation"],
                "min_quality_threshold": 9.0,
                "optimal_models": ["claude-3-5-sonnet", "gpt-4o"]
            }
        }
        
        # Industry-specific adjustments
        self.industry_adjustments = {
            "technology": {
                "capability_boosts": {"technical_accuracy": 1.3, "innovation_focus": 1.2},
                "preferred_models": ["claude-3-5-sonnet", "gpt-4o"]
            },
            
            "healthcare": {
                "capability_boosts": {"accuracy": 1.5, "compliance_awareness": 1.4},
                "privacy_requirement": 8,
                "preferred_models": ["deepseek-r1", "llama3.3-70b"]
            },
            
            "finance": {
                "capability_boosts": {"accuracy": 1.4, "regulatory_compliance": 1.3},
                "privacy_requirement": 9,
                "preferred_models": ["deepseek-r1", "o1-pro"]
            },
            
            "retail": {
                "capability_boosts": {"conversion_optimization": 1.3, "product_highlighting": 1.2},
                "cost_sensitivity": 1.2,
                "preferred_models": ["gemini-1.5-flash", "claude-3-haiku"]
            },
            
            "b2b_saas": {
                "capability_boosts": {"technical_communication": 1.3, "business_value": 1.2},
                "preferred_models": ["claude-3-5-sonnet", "gpt-4o-mini"]
            }
        }
    
    async def route_marketing_task(self, task: Dict, marketing_context: MarketingTaskContext = None) -> ModelSelectionResult:
        """Route specifically optimized for marketing tasks"""
        
        # Enhance task with marketing-specific analysis
        enhanced_task = await self._enhance_marketing_task(task, marketing_context)
        
        # Apply marketing-specific routing logic
        if marketing_context and marketing_context.campaign_type in self.marketing_task_preferences:
            return await self._route_by_campaign_type(enhanced_task, marketing_context)
        
        # Fallback to content format routing
        content_format = task.get("content_format", "general")
        if content_format in self.content_format_preferences:
            return await self._route_by_content_format(enhanced_task, content_format)
        
        # Apply industry-specific routing
        industry = task.get("industry", "general")
        if industry in self.industry_adjustments:
            return await self._route_by_industry(enhanced_task, industry)
        
        # Default to base router with marketing weights
        return await self._route_with_marketing_weights(enhanced_task)
    
    async def _enhance_marketing_task(self, task: Dict, marketing_context: MarketingTaskContext) -> Dict:
        """Enhance task with marketing-specific requirements"""
        enhanced_task = task.copy()
        
        # Add marketing-specific capabilities
        marketing_capabilities = []
        
        # Determine capabilities based on task type
        task_type = task.get("type", "content_creation")
        
        if "seo" in task_type.lower() or task.get("seo_focus", False):
            marketing_capabilities.extend(["seo_optimization", "keyword_integration"])
        
        if "social" in task_type.lower():
            marketing_capabilities.extend(["social_media", "engagement_optimization"])
        
        if "email" in task_type.lower():
            marketing_capabilities.extend(["email_marketing", "personalization"])
        
        if "ad" in task_type.lower() or "advertisement" in task_type.lower():
            marketing_capabilities.extend(["ad_copy", "persuasive_writing"])
        
        if "brand" in task_type.lower():
            marketing_capabilities.extend(["brand_consistency", "brand_voice_consistency"])
        
        if marketing_context:
            # Adjust based on marketing context
            if marketing_context.competitive_context:
                marketing_capabilities.append("competitor_analysis")
            
            if marketing_context.seo_requirements:
                marketing_capabilities.extend(["seo_optimization", "meta_description"])
            
            if marketing_context.volume_expected > 10:
                marketing_capabilities.extend(["batch_processing", "cost_efficiency"])
            
            # Quality vs cost preference
            if marketing_context.quality_vs_cost_preference > 0.7:
                enhanced_task["quality_threshold"] = max(enhanced_task.get("quality_threshold", 7), 8.5)
                enhanced_task["max_cost"] = enhanced_task.get("max_cost", 0.1) * 2  # Allow higher cost
            elif marketing_context.quality_vs_cost_preference < 0.3:
                enhanced_task["max_cost"] = min(enhanced_task.get("max_cost", 0.01), 0.005)  # Strict cost limit
        
        # Add marketing capabilities to required capabilities
        existing_capabilities = enhanced_task.get("required_capabilities", [])
        enhanced_task["required_capabilities"] = list(set(existing_capabilities + marketing_capabilities))
        
        return enhanced_task
    
    async def _route_by_campaign_type(self, task: Dict, marketing_context: MarketingTaskContext) -> ModelSelectionResult:
        """Route based on specific campaign type"""
        campaign_type = marketing_context.campaign_type
        preferences = self.marketing_task_preferences[campaign_type]
        
        # Apply campaign-specific adjustments
        adjusted_task = task.copy()
        
        if preferences.get("avoid_apis_for_competitive") and marketing_context.competitive_context:
            # Force local models for competitive analysis
            adjusted_task["privacy_level"] = 10
        
        if preferences.get("optimize_for_volume") and marketing_context.volume_expected > 5:
            adjusted_task["max_cost"] = min(adjusted_task.get("max_cost", 0.01), 0.002)
            adjusted_task["max_latency_ms"] = min(adjusted_task.get("max_latency_ms", 5000), 2000)
        
        if preferences.get("require_quality"):
            adjusted_task["quality_threshold"] = max(adjusted_task.get("quality_threshold", 7), 8.5)
        
        # Try optimal models first
        for model_name in preferences["optimal_models"]:
            if await self._is_model_suitable(model_name, adjusted_task):
                result = await self.select_optimal_model(adjusted_task)
                if result.selected_model == model_name:
                    result.rationale = f"Campaign-optimized: {preferences['rationale']}"
                    return result
        
        # Try fallbacks
        for model_name in preferences["fallbacks"]:
            if await self._is_model_suitable(model_name, adjusted_task):
                # Force selection of this model
                filtered_task = await self._force_model_selection(adjusted_task, model_name)
                result = await self.select_optimal_model(filtered_task)
                result.rationale = f"Fallback for {campaign_type}: {preferences['rationale']}"
                return result
        
        # Default routing
        return await self.select_optimal_model(adjusted_task)
    
    async def _route_by_content_format(self, task: Dict, content_format: str) -> ModelSelectionResult:
        """Route based on content format requirements"""
        format_prefs = self.content_format_preferences[content_format]
        
        adjusted_task = task.copy()
        
        # Apply format-specific requirements
        if "min_quality_threshold" in format_prefs:
            adjusted_task["quality_threshold"] = max(
                adjusted_task.get("quality_threshold", 7),
                format_prefs["min_quality_threshold"]
            )
        
        if "max_latency" in format_prefs:
            adjusted_task["max_latency_ms"] = min(
                adjusted_task.get("max_latency_ms", 10000),
                format_prefs["max_latency"]
            )
        
        if "max_cost" in format_prefs:
            adjusted_task["max_cost"] = min(
                adjusted_task.get("max_cost", 0.01),
                format_prefs["max_cost"]
            )
        
        # Add preferred capabilities
        existing_caps = adjusted_task.get("required_capabilities", [])
        preferred_caps = format_prefs.get("preferred_capabilities", [])
        adjusted_task["required_capabilities"] = list(set(existing_caps + preferred_caps))
        
        # Try optimal models for this format
        if "optimal_models" in format_prefs:
            for model_name in format_prefs["optimal_models"]:
                if await self._is_model_suitable(model_name, adjusted_task):
                    result = await self.select_optimal_model(adjusted_task)
                    if result.selected_model == model_name:
                        result.rationale = f"Format-optimized for {content_format}: {result.rationale}"
                        return result
        
        return await self.select_optimal_model(adjusted_task)
    
    async def _route_by_industry(self, task: Dict, industry: str) -> ModelSelectionResult:
        """Route based on industry-specific requirements"""
        industry_config = self.industry_adjustments[industry]
        
        adjusted_task = task.copy()
        
        # Apply industry-specific privacy requirements
        if "privacy_requirement" in industry_config:
            adjusted_task["privacy_level"] = max(
                adjusted_task.get("privacy_level", 5),
                industry_config["privacy_requirement"]
            )
        
        # Apply cost sensitivity
        if "cost_sensitivity" in industry_config:
            current_max_cost = adjusted_task.get("max_cost", 0.01)
            adjusted_task["max_cost"] = current_max_cost / industry_config["cost_sensitivity"]
        
        # Boost certain capabilities
        capability_boosts = industry_config.get("capability_boosts", {})
        for capability, boost in capability_boosts.items():
            if capability not in self.marketing_weights:
                self.marketing_weights[capability] = 1.0
            self.marketing_weights[capability] *= boost
        
        # Try industry-preferred models
        if "preferred_models" in industry_config:
            for model_name in industry_config["preferred_models"]:
                if await self._is_model_suitable(model_name, adjusted_task):
                    result = await self.select_optimal_model(adjusted_task)
                    if result.selected_model == model_name:
                        result.rationale = f"Industry-optimized for {industry}: {result.rationale}"
                        return result
        
        return await self.select_optimal_model(adjusted_task)
    
    async def _route_with_marketing_weights(self, task: Dict) -> ModelSelectionResult:
        """Route with marketing-specific capability weights applied"""
        
        # Temporarily update capability weights
        original_weights = self.capability_weights.copy()
        self.capability_weights.update(self.marketing_weights)
        
        try:
            result = await self.select_optimal_model(task)
            result.rationale = f"Marketing-weighted selection: {result.rationale}"
            return result
        finally:
            # Restore original weights
            self.capability_weights = original_weights
    
    async def _is_model_suitable(self, model_name: str, task: Dict) -> bool:
        """Check if a model is suitable for the given task"""
        if model_name not in self.model_database:
            return False
        
        model_info = self.model_database[model_name]
        
        # Check privacy requirements
        required_privacy = task.get("privacy_level", 5)
        if model_info.get("privacy_score", 0) < required_privacy:
            return False
        
        # Check cost requirements
        max_cost = task.get("max_cost", 0.1)
        model_cost = model_info.get("cost_per_1k_tokens", 0)
        if model_cost > max_cost and model_cost > 0:
            return False
        
        # Check latency requirements
        max_latency = task.get("max_latency_ms", 10000)
        if model_info.get("avg_latency_ms", 0) > max_latency:
            return False
        
        return True
    
    async def _force_model_selection(self, task: Dict, preferred_model: str) -> Dict:
        """Adjust task parameters to favor a specific model"""
        adjusted_task = task.copy()
        
        if preferred_model in self.model_database:
            model_info = self.model_database[preferred_model]
            
            # Adjust cost to accommodate model
            model_cost = model_info.get("cost_per_1k_tokens", 0)
            if model_cost > 0:
                adjusted_task["max_cost"] = max(adjusted_task.get("max_cost", 0.01), model_cost * 1.1)
            
            # Adjust latency to accommodate model
            model_latency = model_info.get("avg_latency_ms", 1000)
            adjusted_task["max_latency_ms"] = max(adjusted_task.get("max_latency_ms", 5000), model_latency * 1.2)
            
            # Adjust privacy to accommodate model
            model_privacy = model_info.get("privacy_score", 5)
            adjusted_task["privacy_level"] = min(adjusted_task.get("privacy_level", 10), model_privacy)
        
        return adjusted_task
    
    def get_marketing_analytics(self) -> Dict:
        """Get marketing-specific analytics and insights"""
        base_analytics = self.get_usage_analytics()
        
        # Add marketing-specific metrics
        marketing_analytics = {
            **base_analytics,
            "marketing_optimizations": {
                "campaign_types_served": list(self.marketing_task_preferences.keys()),
                "content_formats_supported": list(self.content_format_preferences.keys()),
                "industries_optimized": list(self.industry_adjustments.keys()),
                "marketing_weights_active": len(self.marketing_weights)
            },
            
            "cost_efficiency": {
                "local_model_usage": sum(1 for s in self.selection_history 
                                       if s.get("model", "").startswith(("deepseek", "llama", "phi"))),
                "avg_cost_per_marketing_task": np.mean([s["cost"] for s in self.selection_history 
                                                      if s.get("domain") == "marketing"]) if self.selection_history else 0
            },
            
            "quality_metrics": {
                "high_quality_model_selections": sum(1 for s in self.selection_history 
                                                   if s.get("confidence", 0) > 0.8),
                "avg_confidence_marketing": np.mean([s["confidence"] for s in self.selection_history 
                                                   if s.get("domain") == "marketing"]) if self.selection_history else 0
            }
        }
        
        return marketing_analytics

# Convenience functions for marketing tasks
async def route_marketing_task(task: Dict, marketing_context: MarketingTaskContext = None) -> ModelSelectionResult:
    """Route a marketing task to the optimal model"""
    router = MarketingModelRouter()
    return await router.route_marketing_task(task, marketing_context)

async def route_campaign_content(campaign_type: str, content: str, 
                                brand_voice: str = "professional", 
                                volume: int = 1,
                                quality_preference: float = 0.7) -> ModelSelectionResult:
    """Quick routing for campaign content creation"""
    
    task = {
        "type": "content_creation",
        "content": content,
        "domain": "marketing",
        "campaign_type": campaign_type
    }
    
    marketing_context = MarketingTaskContext(
        campaign_type=campaign_type,
        brand_guidelines={},
        target_audience="general",
        content_format="general",
        seo_requirements=False,
        volume_expected=volume,
        brand_voice=brand_voice,
        competitive_context=False,
        urgency_level=5,
        quality_vs_cost_preference=quality_preference
    )
    
    return await route_marketing_task(task, marketing_context)

# Marketing-specific task examples
MARKETING_TASK_EXAMPLES = {
    "blog_seo": {
        "type": "seo_content_creation",
        "content": "Write a 1500-word blog post about email marketing best practices",
        "content_format": "blog_post",
        "seo_focus": True,
        "quality_threshold": 8.5
    },
    
    "social_batch": {
        "type": "social_media_batch",
        "content": "Create 10 LinkedIn posts about productivity tips",
        "content_format": "social_media_post",
        "volume_expected": 10,
        "max_cost": 0.01
    },
    
    "competitor_research": {
        "type": "competitor_analysis",
        "content": "Analyze top 5 competitors' content strategy",
        "privacy_level": 10,
        "competitive_context": True
    },
    
    "email_campaign": {
        "type": "email_marketing",
        "content": "Create email sequence for product launch",
        "content_format": "email_subject_line",
        "personalization_required": True
    }
}

if __name__ == "__main__":
    # Example usage
    async def test_marketing_router():
        router = MarketingModelRouter()
        
        # Test SEO content creation
        seo_task = MARKETING_TASK_EXAMPLES["blog_seo"]
        result = await router.route_marketing_task(seo_task)
        
        print(f"SEO Content Task:")
        print(f"  Selected Model: {result.selected_model}")
        print(f"  Rationale: {result.rationale}")
        print(f"  Cost: ${result.estimated_cost:.4f}")
        print(f"  Confidence: {result.confidence:.1%}")
        print()
        
        # Test social media batch
        social_context = MarketingTaskContext(
            campaign_type="social_media_batch",
            brand_guidelines={},
            target_audience="professionals",
            content_format="social_media_post",
            seo_requirements=False,
            volume_expected=10,
            brand_voice="casual",
            competitive_context=False,
            urgency_level=3,
            quality_vs_cost_preference=0.3  # Cost priority
        )
        
        social_task = MARKETING_TASK_EXAMPLES["social_batch"]
        result = await router.route_marketing_task(social_task, social_context)
        
        print(f"Social Media Batch Task:")
        print(f"  Selected Model: {result.selected_model}")
        print(f"  Rationale: {result.rationale}")
        print(f"  Cost: ${result.estimated_cost:.4f}")
        print(f"  Confidence: {result.confidence:.1%}")
        print()
        
        # Get marketing analytics
        analytics = router.get_marketing_analytics()
        print(f"Marketing Analytics: {analytics}")
    
    asyncio.run(test_marketing_router())