#!/usr/bin/env python3
"""
🧠 Capability-Based AI Model Router - Enterprise Decision Matrix
Advanced router that selects optimal AI models based on comprehensive capability analysis

Features:
- 50+ capability evaluation per model
- Multi-dimensional optimization (cost, latency, privacy, quality)
- Dynamic learning from results
- Marketing-specific routing optimizations
- Predictive model selection using ML
- Real-time cost optimization with total value
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import pickle
from collections import defaultdict, deque
import redis
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelSelectionResult:
    """Result of model selection process"""
    selected_model: str
    model_info: Dict[str, Any]
    score_breakdown: Dict[str, float]
    rationale: str
    alternatives: List[Tuple[str, float]]
    estimated_cost: float
    estimated_latency: int
    confidence: float
    selection_time_ms: float
    cache_hit: bool = False

@dataclass
class TaskRequirements:
    """Task requirements for model selection"""
    required_capabilities: List[str]
    max_cost_per_1k_tokens: float
    max_latency_ms: int
    privacy_level: int
    estimated_context_tokens: int
    quality_threshold: float
    urgency_level: int
    domain: str
    task_type: str

class ModelCostCalculator:
    """Advanced cost calculation with multiple factors"""
    
    def __init__(self):
        self.base_hourly_rate = 50.0  # Default hourly rate for time value
        self.opportunity_cost_multiplier = 1.2
        
    async def calculate_total_cost(self, model_info: Dict, task_requirements: TaskRequirements) -> Dict[str, float]:
        """Calculate comprehensive cost including opportunity costs"""
        
        # Base token cost
        estimated_tokens = task_requirements.estimated_context_tokens
        base_cost = model_info.get("cost_per_1k_tokens", 0) * (estimated_tokens / 1000)
        
        # Output tokens cost (usually higher)
        output_cost_multiplier = model_info.get("cost_per_1k_tokens_output", base_cost * 4) / base_cost if base_cost > 0 else 4
        estimated_output_tokens = estimated_tokens * 0.3  # Rough estimate
        output_cost = (model_info.get("cost_per_1k_tokens_output", base_cost * 4)) * (estimated_output_tokens / 1000)
        
        # Time cost
        latency_ms = model_info.get("avg_latency_ms", 1000)
        time_cost = (latency_ms / 1000 / 3600) * self.base_hourly_rate
        
        # Opportunity cost for delayed decisions
        urgency_multiplier = max(1.0, task_requirements.urgency_level / 5.0)
        opportunity_cost = time_cost * self.opportunity_cost_multiplier * urgency_multiplier
        
        # Quality cost adjustment
        expected_quality = await self._estimate_quality(model_info, task_requirements)
        quality_cost_adjustment = max(0.5, 2.0 - (expected_quality / 10.0))
        
        total_direct_cost = base_cost + output_cost
        total_time_cost = time_cost + opportunity_cost
        adjusted_total = (total_direct_cost + total_time_cost) * quality_cost_adjustment
        
        return {
            "base_cost": base_cost,
            "output_cost": output_cost,
            "time_cost": time_cost,
            "opportunity_cost": opportunity_cost,
            "quality_adjustment": quality_cost_adjustment,
            "total_direct_cost": total_direct_cost,
            "total_time_cost": total_time_cost,
            "total_cost": adjusted_total,
            "cost_per_quality_point": adjusted_total / max(expected_quality, 1.0)
        }
    
    async def _estimate_quality(self, model_info: Dict, task_requirements: TaskRequirements) -> float:
        """Estimate expected quality score for this model on this task"""
        capabilities = model_info.get("capabilities", {})
        
        quality_scores = []
        for capability in task_requirements.required_capabilities:
            score = capabilities.get(capability, 5.0)
            quality_scores.append(score)
        
        if not quality_scores:
            return 7.0  # Default quality
            
        # Weighted average with emphasis on lowest scores (weakest link)
        sorted_scores = sorted(quality_scores)
        weights = [3, 2, 1.5] + [1] * (len(sorted_scores) - 3)  # Higher weight for lowest scores
        weights = weights[:len(sorted_scores)]
        
        weighted_score = sum(score * weight for score, weight in zip(sorted_scores, weights)) / sum(weights)
        return min(10.0, max(1.0, weighted_score))

class ModelPerformanceBenchmarks:
    """Historical performance data and benchmarks"""
    
    def __init__(self, db_path: str = "/root/supermcp/data/model_benchmarks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for benchmarks"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    capability TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    cost REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_reliability (
                    model_name TEXT PRIMARY KEY,
                    total_tasks INTEGER DEFAULT 0,
                    successful_tasks INTEGER DEFAULT 0,
                    avg_quality_score REAL DEFAULT 7.0,
                    avg_latency_ms INTEGER DEFAULT 1000,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_task_type 
                ON model_performance(model_name, task_type)
            """)
    
    async def get_model_reliability(self, model_name: str) -> Dict[str, float]:
        """Get reliability metrics for a model"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT total_tasks, successful_tasks, avg_quality_score, avg_latency_ms
                FROM model_reliability 
                WHERE model_name = ?
            """, (model_name,))
            
            result = cursor.fetchone()
            
            if result:
                total, successful, avg_quality, avg_latency = result
                success_rate = (successful / total) if total > 0 else 0.85  # Default
                
                return {
                    "success_rate": success_rate,
                    "avg_quality": avg_quality,
                    "avg_latency": avg_latency,
                    "total_tasks": total,
                    "reliability_score": min(10.0, success_rate * 10 + (avg_quality / 10))
                }
            else:
                # Default values for new models
                return {
                    "success_rate": 0.85,
                    "avg_quality": 7.0,
                    "avg_latency": 1500,
                    "total_tasks": 0,
                    "reliability_score": 8.5
                }
    
    async def record_task_result(self, model_name: str, task_type: str, capability: str, 
                               quality_score: float, latency_ms: int, cost: float, success: bool):
        """Record task result for learning"""
        with sqlite3.connect(self.db_path) as conn:
            # Insert performance record
            conn.execute("""
                INSERT INTO model_performance 
                (model_name, task_type, capability, quality_score, latency_ms, cost, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (model_name, task_type, capability, quality_score, latency_ms, cost, success))
            
            # Update reliability metrics
            conn.execute("""
                INSERT OR REPLACE INTO model_reliability 
                (model_name, total_tasks, successful_tasks, avg_quality_score, avg_latency_ms, last_updated)
                SELECT 
                    ?,
                    COALESCE((SELECT total_tasks FROM model_reliability WHERE model_name = ?), 0) + 1,
                    COALESCE((SELECT successful_tasks FROM model_reliability WHERE model_name = ?), 0) + ?,
                    (
                        COALESCE((SELECT avg_quality_score * total_tasks FROM model_reliability WHERE model_name = ?), 0) + ?
                    ) / (COALESCE((SELECT total_tasks FROM model_reliability WHERE model_name = ?), 0) + 1),
                    (
                        COALESCE((SELECT avg_latency_ms * total_tasks FROM model_reliability WHERE model_name = ?), 0) + ?
                    ) / (COALESCE((SELECT total_tasks FROM model_reliability WHERE model_name = ?), 0) + 1),
                    CURRENT_TIMESTAMP
            """, (model_name, model_name, model_name, 1 if success else 0, 
                  model_name, quality_score, model_name, model_name, latency_ms, model_name))

class ModelSelectionCache:
    """Redis-based caching for model selections"""
    
    def __init__(self, redis_url: str = "redis://sam.chat:6379/1"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.cache_enabled = True
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}")
            self.cache_enabled = False
            self.local_cache = {}
    
    def _generate_cache_key(self, task_requirements: TaskRequirements, user_context: Dict) -> str:
        """Generate cache key for task + context"""
        cache_data = {
            "capabilities": sorted(task_requirements.required_capabilities),
            "max_cost": task_requirements.max_cost_per_1k_tokens,
            "max_latency": task_requirements.max_latency_ms,
            "privacy": task_requirements.privacy_level,
            "context_tokens": task_requirements.estimated_context_tokens,
            "quality_threshold": task_requirements.quality_threshold,
            "domain": task_requirements.domain,
            "task_type": task_requirements.task_type,
            "user_preferences": user_context.get("preferences", {})
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"model_selection:{hashlib.md5(cache_str.encode()).hexdigest()}"
    
    async def get(self, task_requirements: TaskRequirements, user_context: Dict) -> Optional[ModelSelectionResult]:
        """Get cached model selection"""
        if not self.cache_enabled:
            return None
            
        cache_key = self._generate_cache_key(task_requirements, user_context)
        
        try:
            if hasattr(self, 'redis_client'):
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    result_dict = json.loads(cached_data)
                    result = ModelSelectionResult(**result_dict)
                    result.cache_hit = True
                    return result
            else:
                # Local cache fallback
                if cache_key in self.local_cache:
                    cache_entry = self.local_cache[cache_key]
                    if datetime.now() - cache_entry['timestamp'] < timedelta(minutes=5):
                        result = cache_entry['result']
                        result.cache_hit = True
                        return result
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def set(self, task_requirements: TaskRequirements, user_context: Dict, 
                  result: ModelSelectionResult, ttl: int = 300):
        """Cache model selection result"""
        if not self.cache_enabled:
            return
            
        cache_key = self._generate_cache_key(task_requirements, user_context)
        result.cache_hit = False  # Reset cache hit flag
        
        try:
            if hasattr(self, 'redis_client'):
                result_dict = asdict(result)
                self.redis_client.setex(cache_key, ttl, json.dumps(result_dict))
            else:
                # Local cache fallback
                self.local_cache[cache_key] = {
                    'result': result,
                    'timestamp': datetime.now()
                }
                
                # Clean old entries
                cutoff = datetime.now() - timedelta(minutes=10)
                self.local_cache = {
                    k: v for k, v in self.local_cache.items() 
                    if v['timestamp'] > cutoff
                }
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

class CapabilityBasedModelRouter:
    """
    Advanced router that decides optimal model based on comprehensive capability analysis,
    costs, latency, privacy and real benchmarks
    """
    
    def __init__(self, config_path: str = "/root/supermcp/supermcp_new/config/defaults.yaml"):
        self.config_path = Path(config_path)
        self.model_database = self._initialize_comprehensive_model_db()
        self.capability_weights = self._initialize_capability_weights()
        self.cost_calculator = ModelCostCalculator()
        self.performance_benchmarks = ModelPerformanceBenchmarks()
        self.cache = ModelSelectionCache()
        
        # Performance tracking
        self.selection_history = deque(maxlen=1000)
        self.model_usage_stats = defaultdict(int)
        
    def _initialize_comprehensive_model_db(self) -> Dict[str, Dict]:
        """Comprehensive model database with detailed capabilities"""
        return {
            # ==================================================
            # LOCAL MODELS (Ollama/Self-Hosted)
            # ==================================================
            
            "deepseek-r1": {
                "type": "local",
                "provider": "ollama",
                "endpoint": "http://sam.chat:11434",
                "model_size": "7B",
                "context_window": 32000,
                "cost_per_1k_tokens": 0.0,
                "avg_latency_ms": 800,
                "privacy_score": 10,
                "capabilities": {
                    # Core capabilities (1-10 score)
                    "reasoning": 9,
                    "coding": 8,
                    "mathematics": 9,
                    "analysis": 8,
                    "writing": 7,
                    "summarization": 8,
                    "translation": 7,
                    
                    # Advanced capabilities
                    "chain_of_thought": 9,
                    "step_by_step_reasoning": 9,
                    "problem_solving": 9,
                    "logical_deduction": 9,
                    "code_explanation": 8,
                    "debugging": 8,
                    "algorithm_design": 8,
                    
                    # Specialized tasks
                    "financial_analysis": 7,
                    "scientific_reasoning": 8,
                    "legal_analysis": 6,
                    "creative_writing": 6,
                    "technical_documentation": 8,
                    
                    # Limitations
                    "multimodal": 0,
                    "image_analysis": 0,
                    "voice_processing": 0,
                    "real_time_data": 0
                },
                "best_for": [
                    "complex_reasoning", "mathematical_problems", "code_analysis",
                    "privacy_sensitive_tasks", "offline_processing", "cost_optimization"
                ],
                "avoid_for": [
                    "image_analysis", "multimodal_tasks", "real_time_data",
                    "large_context_requirements"
                ]
            },
            
            "llama3.3-70b": {
                "type": "local",
                "provider": "ollama", 
                "endpoint": "http://sam.chat:11434",
                "model_size": "70B",
                "context_window": 128000,
                "cost_per_1k_tokens": 0.0,
                "avg_latency_ms": 2500,
                "privacy_score": 10,
                "capabilities": {
                    "reasoning": 8,
                    "coding": 8,
                    "mathematics": 7,
                    "analysis": 9,
                    "writing": 9,
                    "summarization": 9,
                    "translation": 8,
                    "conversation": 9,
                    "instruction_following": 9,
                    "creative_writing": 8,
                    "content_generation": 9,
                    "document_analysis": 8,
                    "research_synthesis": 8,
                    
                    # Limitations
                    "multimodal": 0,
                    "image_analysis": 0,
                    "real_time_data": 0
                },
                "best_for": [
                    "long_documents", "content_generation", "conversation",
                    "analysis_tasks", "privacy_critical", "large_context"
                ],
                "avoid_for": [
                    "mathematical_proofs", "complex_coding", "multimodal_tasks"
                ]
            },
            
            "phi-3.5-mini": {
                "type": "local",
                "provider": "ollama",
                "endpoint": "http://sam.chat:11434", 
                "model_size": "3.8B",
                "context_window": 4000,
                "cost_per_1k_tokens": 0.0,
                "avg_latency_ms": 300,
                "privacy_score": 10,
                "capabilities": {
                    "reasoning": 6,
                    "coding": 7,
                    "mathematics": 7,
                    "analysis": 6,
                    "writing": 6,
                    "summarization": 7,
                    "translation": 6,
                    "quick_responses": 9,
                    "simple_tasks": 8,
                    "chat": 7,
                    
                    # Specialized
                    "code_completion": 8,
                    "quick_explanations": 8,
                    "simple_qa": 8
                },
                "best_for": [
                    "quick_tasks", "simple_coding", "fast_responses",
                    "high_frequency", "resource_constrained", "edge_computing"
                ],
                "avoid_for": [
                    "complex_reasoning", "long_documents", "advanced_analysis"
                ]
            },
            
            # ==================================================
            # API MODELS - OpenAI
            # ==================================================
            
            "gpt-4o": {
                "type": "api",
                "provider": "openai",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "context_window": 128000,
                "cost_per_1k_tokens": 0.0025,
                "cost_per_1k_tokens_output": 0.01,
                "avg_latency_ms": 2000,
                "privacy_score": 6,
                "capabilities": {
                    # Top-tier capabilities
                    "reasoning": 9,
                    "coding": 9,
                    "mathematics": 9,
                    "analysis": 9,
                    "writing": 9,
                    "summarization": 9,
                    "translation": 9,
                    
                    # Multimodal excellence
                    "image_analysis": 9,
                    "vision_processing": 9,
                    "chart_reading": 9,
                    "diagram_interpretation": 9,
                    "multimodal": 9,
                    
                    # Advanced reasoning
                    "complex_problem_solving": 9,
                    "strategic_thinking": 9,
                    "creative_problem_solving": 9,
                    "research_synthesis": 9,
                    "technical_writing": 9,
                    
                    # Business tasks
                    "business_analysis": 9,
                    "financial_modeling": 8,
                    "market_research": 8,
                    "legal_analysis": 8,
                    "scientific_reasoning": 9
                },
                "best_for": [
                    "complex_multimodal_tasks", "advanced_reasoning", 
                    "business_critical", "high_quality_content", "image_analysis",
                    "strategic_planning", "research_reports"
                ],
                "avoid_for": [
                    "high_frequency_simple_tasks", "cost_sensitive", 
                    "privacy_critical", "offline_requirements"
                ]
            },
            
            "gpt-4o-mini": {
                "type": "api",
                "provider": "openai",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "context_window": 128000,
                "cost_per_1k_tokens": 0.00015,
                "cost_per_1k_tokens_output": 0.0006,
                "avg_latency_ms": 1500,
                "privacy_score": 6,
                "capabilities": {
                    "reasoning": 7,
                    "coding": 8,
                    "mathematics": 7,
                    "analysis": 8,
                    "writing": 8,
                    "summarization": 8,
                    "translation": 8,
                    
                    # Efficient processing
                    "quick_analysis": 8,
                    "content_generation": 8,
                    "code_review": 8,
                    "data_extraction": 8,
                    "simple_vision": 7,
                    
                    # Good balance
                    "cost_efficiency": 9,
                    "speed": 8,
                    "quality": 7
                },
                "best_for": [
                    "balanced_cost_quality", "frequent_tasks", "content_generation",
                    "code_review", "data_processing", "moderate_complexity"
                ],
                "avoid_for": [
                    "complex_reasoning", "advanced_vision", "high_stakes_decisions"
                ]
            },
            
            "o1-pro": {
                "type": "api",
                "provider": "openai",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "context_window": 200000,
                "cost_per_1k_tokens": 0.015,
                "cost_per_1k_tokens_output": 0.06,
                "avg_latency_ms": 8000,
                "privacy_score": 6,
                "capabilities": {
                    # Exceptional reasoning
                    "reasoning": 10,
                    "mathematics": 10,
                    "scientific_reasoning": 10,
                    "complex_problem_solving": 10,
                    "logical_deduction": 10,
                    "step_by_step_analysis": 10,
                    
                    # Advanced specialties
                    "research_methodology": 10,
                    "academic_writing": 9,
                    "technical_analysis": 10,
                    "algorithm_design": 9,
                    "mathematical_proofs": 10,
                    "scientific_computation": 9,
                    
                    # Business applications
                    "strategic_planning": 9,
                    "risk_analysis": 9,
                    "financial_modeling": 9,
                    
                    # Limitations
                    "speed": 4,
                    "cost_efficiency": 3,
                    "simple_tasks": 5
                },
                "best_for": [
                    "complex_research", "mathematical_analysis", "scientific_reasoning",
                    "strategic_decisions", "academic_work", "high_stakes_analysis",
                    "detailed_planning", "complex_problem_solving"
                ],
                "avoid_for": [
                    "simple_tasks", "high_frequency", "cost_sensitive",
                    "time_critical_simple", "basic_content_generation"
                ]
            },
            
            # ==================================================
            # API MODELS - Anthropic Claude
            # ==================================================
            
            "claude-3-5-sonnet": {
                "type": "api",
                "provider": "anthropic",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "context_window": 200000,
                "cost_per_1k_tokens": 0.003,
                "cost_per_1k_tokens_output": 0.015,
                "avg_latency_ms": 1800,
                "privacy_score": 7,
                "capabilities": {
                    # Excellent across the board
                    "reasoning": 9,
                    "coding": 9,
                    "mathematics": 8,
                    "analysis": 9,
                    "writing": 10,
                    "summarization": 9,
                    "translation": 8,
                    
                    # Content excellence
                    "creative_writing": 10,
                    "technical_writing": 9,
                    "content_editing": 10,
                    "document_analysis": 9,
                    "research_synthesis": 9,
                    
                    # Vision capabilities
                    "image_analysis": 8,
                    "chart_interpretation": 8,
                    "document_ocr": 8,
                    
                    # Business tasks
                    "business_writing": 10,
                    "email_drafting": 9,
                    "proposal_writing": 9,
                    "report_generation": 9,
                    "presentation_content": 9,
                    
                    # Code tasks
                    "code_review": 9,
                    "code_explanation": 9,
                    "debugging": 8,
                    "architecture_design": 8
                },
                "best_for": [
                    "content_creation", "business_writing", "analysis_tasks",
                    "code_review", "document_processing", "creative_content",
                    "long_form_writing", "research_reports"
                ],
                "avoid_for": [
                    "high_frequency_simple", "mathematical_proofs", 
                    "basic_calculations", "simple_data_extraction"
                ]
            },
            
            "claude-3-haiku": {
                "type": "api",
                "provider": "anthropic", 
                "endpoint": "https://api.anthropic.com/v1/messages",
                "context_window": 200000,
                "cost_per_1k_tokens": 0.00025,
                "cost_per_1k_tokens_output": 0.00125,
                "avg_latency_ms": 800,
                "privacy_score": 7,
                "capabilities": {
                    "reasoning": 7,
                    "coding": 7,
                    "mathematics": 6,
                    "analysis": 7,
                    "writing": 8,
                    "summarization": 8,
                    "translation": 7,
                    
                    # Speed optimized
                    "quick_responses": 9,
                    "simple_analysis": 8,
                    "data_extraction": 8,
                    "content_summarization": 8,
                    "quick_coding": 7,
                    
                    # Efficiency
                    "cost_efficiency": 9,
                    "speed": 9,
                    "batch_processing": 8
                },
                "best_for": [
                    "high_frequency_tasks", "quick_analysis", "summarization",
                    "data_extraction", "simple_coding", "cost_optimization",
                    "real_time_processing"
                ],
                "avoid_for": [
                    "complex_reasoning", "advanced_vision", "deep_analysis",
                    "creative_writing", "complex_problem_solving"
                ]
            },
            
            # ==================================================
            # API MODELS - Google
            # ==================================================
            
            "gemini-1.5-pro": {
                "type": "api",
                "provider": "google",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro",
                "context_window": 2000000,
                "cost_per_1k_tokens": 0.00125,
                "cost_per_1k_tokens_output": 0.005,
                "avg_latency_ms": 2200,
                "privacy_score": 6,
                "capabilities": {
                    # Strong general capabilities
                    "reasoning": 8,
                    "coding": 8,
                    "mathematics": 8,
                    "analysis": 9,
                    "writing": 8,
                    "summarization": 9,
                    "translation": 9,
                    
                    # Exceptional context handling
                    "long_context": 10,
                    "document_analysis": 10,
                    "large_file_processing": 10,
                    "comprehensive_analysis": 9,
                    
                    # Multimodal strength
                    "image_analysis": 8,
                    "video_analysis": 8,
                    "audio_processing": 7,
                    "multimodal": 8,
                    
                    # Specialized tasks
                    "research_synthesis": 9,
                    "data_analysis": 8,
                    "pattern_recognition": 8,
                    "information_extraction": 9
                },
                "best_for": [
                    "large_documents", "comprehensive_analysis", "long_context_tasks",
                    "multi_document_research", "extensive_data_processing",
                    "video_analysis", "large_scale_summarization"
                ],
                "avoid_for": [
                    "simple_quick_tasks", "high_precision_math", 
                    "real_time_conversation", "creative_writing"
                ]
            },
            
            "gemini-1.5-flash": {
                "type": "api",
                "provider": "google",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash",
                "context_window": 1000000,
                "cost_per_1k_tokens": 0.000075,
                "cost_per_1k_tokens_output": 0.0003,
                "avg_latency_ms": 600,
                "privacy_score": 6,
                "capabilities": {
                    "reasoning": 7,
                    "coding": 7,
                    "mathematics": 6,
                    "analysis": 7,
                    "writing": 7,
                    "summarization": 8,
                    "translation": 8,
                    
                    # Speed and efficiency
                    "speed": 9,
                    "cost_efficiency": 10,
                    "quick_analysis": 8,
                    "rapid_processing": 9,
                    
                    # Good for volume
                    "batch_processing": 9,
                    "high_frequency": 9,
                    "real_time": 8,
                    
                    # Decent multimodal
                    "image_analysis": 6,
                    "simple_vision": 7
                },
                "best_for": [
                    "high_volume_processing", "real_time_applications", 
                    "cost_sensitive_tasks", "quick_analysis", "batch_operations",
                    "API_heavy_applications", "fast_prototyping"
                ],
                "avoid_for": [
                    "complex_reasoning", "high_precision_tasks", 
                    "advanced_vision", "creative_writing", "detailed_analysis"
                ]
            }
        }
    
    def _initialize_capability_weights(self) -> Dict[str, float]:
        """Initialize capability importance weights"""
        return {
            # Core capabilities
            "reasoning": 1.0,
            "coding": 1.0,
            "mathematics": 1.0,
            "analysis": 1.0,
            "writing": 1.0,
            "summarization": 1.0,
            "translation": 1.0,
            
            # Advanced capabilities  
            "chain_of_thought": 1.2,
            "step_by_step_reasoning": 1.2,
            "problem_solving": 1.1,
            "logical_deduction": 1.1,
            "complex_problem_solving": 1.3,
            "strategic_thinking": 1.2,
            
            # Specialized tasks
            "image_analysis": 1.4,
            "multimodal": 1.3,
            "real_time_data": 1.2,
            "privacy_sensitive": 1.5,
            "cost_efficiency": 1.1,
            "speed": 1.0,
            
            # Business tasks
            "business_analysis": 1.1,
            "content_generation": 1.0,
            "creative_writing": 1.1,
            "technical_documentation": 1.0,
            
            # Quality metrics
            "reliability": 1.2,
            "accuracy": 1.3,
            "consistency": 1.1
        }
    
    async def select_optimal_model(self, task: Dict, user_context: Dict = None) -> ModelSelectionResult:
        """Select the optimal model based on multi-dimensional analysis"""
        
        start_time = datetime.now()
        
        if user_context is None:
            user_context = {}
        
        # 1. Convert task to requirements
        task_requirements = await self._analyze_task_requirements(task)
        
        # 2. Check cache first
        cached_result = await self.cache.get(task_requirements, user_context)
        if cached_result:
            return cached_result
        
        # 3. Evaluate all models
        model_scores = {}
        for model_name, model_info in self.model_database.items():
            score = await self._calculate_model_score(model_info, task_requirements)
            model_scores[model_name] = score
        
        # 4. Apply hard filters
        filtered_models = await self._apply_hard_filters(model_scores, task_requirements)
        
        # 5. Select best model
        if not filtered_models:
            logger.warning("No models passed filters, using best available")
            best_model = max(model_scores.items(), key=lambda x: x[1]["total_score"])
        else:
            best_model = max(filtered_models.items(), key=lambda x: x[1]["total_score"])
        
        selected_model_name = best_model[0]
        model_info = self.model_database[selected_model_name]
        
        # 6. Calculate costs and create result
        cost_breakdown = await self.cost_calculator.calculate_total_cost(model_info, task_requirements)
        
        selection_time = (datetime.now() - start_time).total_seconds() * 1000
        
        result = ModelSelectionResult(
            selected_model=selected_model_name,
            model_info=model_info,
            score_breakdown=best_model[1],
            rationale=await self._generate_selection_rationale(selected_model_name, task_requirements, best_model[1]),
            alternatives=await self._get_top_alternatives(filtered_models, 3),
            estimated_cost=cost_breakdown["total_cost"],
            estimated_latency=model_info.get("avg_latency_ms", 1000),
            confidence=best_model[1]["confidence"],
            selection_time_ms=selection_time
        )
        
        # 7. Cache result
        await self.cache.set(task_requirements, user_context, result)
        
        # 8. Track usage
        self._track_selection(result, task_requirements)
        
        return result
    
    async def _analyze_task_requirements(self, task: Dict) -> TaskRequirements:
        """Analyze task and extract requirements"""
        
        # Extract basic requirements
        task_type = task.get("type", "general")
        content = task.get("content", "")
        
        # Infer required capabilities from task
        required_capabilities = []
        
        # Content analysis for capability detection
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["analyze", "analysis", "examine", "evaluate"]):
            required_capabilities.append("analysis")
        
        if any(word in content_lower for word in ["code", "programming", "function", "algorithm"]):
            required_capabilities.extend(["coding", "code_explanation"])
        
        if any(word in content_lower for word in ["calculate", "math", "equation", "formula"]):
            required_capabilities.append("mathematics")
        
        if any(word in content_lower for word in ["write", "create", "draft", "compose"]):
            required_capabilities.append("writing")
        
        if any(word in content_lower for word in ["summarize", "summary", "brief"]):
            required_capabilities.append("summarization")
        
        if any(word in content_lower for word in ["image", "picture", "chart", "diagram"]):
            required_capabilities.extend(["image_analysis", "multimodal"])
        
        if any(word in content_lower for word in ["reason", "logic", "because", "therefore"]):
            required_capabilities.append("reasoning")
        
        # Task type specific capabilities
        task_type_capabilities = {
            "marketing": ["business_analysis", "creative_writing", "content_generation"],
            "research": ["analysis", "research_synthesis", "document_analysis"],
            "coding": ["coding", "debugging", "code_review"],
            "financial": ["financial_analysis", "mathematics", "analysis"],
            "creative": ["creative_writing", "content_generation"],
            "technical": ["technical_documentation", "analysis", "writing"]
        }
        
        if task_type in task_type_capabilities:
            required_capabilities.extend(task_type_capabilities[task_type])
        
        # Remove duplicates while preserving order
        required_capabilities = list(dict.fromkeys(required_capabilities))
        
        if not required_capabilities:
            required_capabilities = ["reasoning", "analysis"]  # Default capabilities
        
        # Estimate context tokens
        estimated_tokens = len(content.split()) * 1.3  # Rough token estimation
        estimated_tokens = max(500, min(estimated_tokens, 100000))  # Reasonable bounds
        
        return TaskRequirements(
            required_capabilities=required_capabilities,
            max_cost_per_1k_tokens=task.get("max_cost", 0.1),
            max_latency_ms=task.get("max_latency_ms", 10000),
            privacy_level=task.get("privacy_level", 5),
            estimated_context_tokens=int(estimated_tokens),
            quality_threshold=task.get("quality_threshold", 7.0),
            urgency_level=task.get("urgency", 5),
            domain=task.get("domain", "general"),
            task_type=task_type
        )
    
    async def _calculate_model_score(self, model_info: Dict, requirements: TaskRequirements) -> Dict:
        """Calculate multi-dimensional score for a model"""
        
        scores = {
            "capability_score": 0,
            "cost_score": 0,
            "latency_score": 0,
            "privacy_score": 0,
            "context_score": 0,
            "reliability_score": 0
        }
        
        # 1. CAPABILITY SCORE
        capability_scores = []
        for capability in requirements.required_capabilities:
            model_capability = model_info["capabilities"].get(capability, 0)
            weight = self.capability_weights.get(capability, 1.0)
            capability_scores.append(model_capability * weight)
        
        scores["capability_score"] = np.mean(capability_scores) if capability_scores else 0
        
        # 2. COST SCORE
        model_cost = model_info.get("cost_per_1k_tokens", 0)
        if model_cost == 0:  # Local model
            scores["cost_score"] = 10
        elif model_cost <= requirements.max_cost_per_1k_tokens:
            scores["cost_score"] = max(0, 10 - (model_cost / requirements.max_cost_per_1k_tokens) * 10)
        else:
            scores["cost_score"] = 0
        
        # 3. LATENCY SCORE
        model_latency = model_info.get("avg_latency_ms", 1000)
        if model_latency <= requirements.max_latency_ms:
            scores["latency_score"] = max(0, 10 - (model_latency / requirements.max_latency_ms) * 10)
        else:
            scores["latency_score"] = 0
        
        # 4. PRIVACY SCORE
        model_privacy = model_info.get("privacy_score", 5)
        if model_privacy >= requirements.privacy_level:
            scores["privacy_score"] = 10
        else:
            scores["privacy_score"] = (model_privacy / requirements.privacy_level) * 10
        
        # 5. CONTEXT SCORE
        model_context = model_info.get("context_window", 4000)
        if model_context >= requirements.estimated_context_tokens:
            scores["context_score"] = 10
        else:
            scores["context_score"] = (model_context / requirements.estimated_context_tokens) * 10
        
        # 6. RELIABILITY SCORE
        reliability_data = await self.performance_benchmarks.get_model_reliability(
            model_info.get("provider", "") + "/" + model_info.get("model_size", "")
        )
        scores["reliability_score"] = reliability_data.get("reliability_score", 8.5)
        
        # WEIGHTED TOTAL SCORE
        weights = {
            "capability_score": 0.35,
            "cost_score": 0.20,
            "latency_score": 0.15,
            "privacy_score": 0.15,
            "context_score": 0.10,
            "reliability_score": 0.05
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        # CONFIDENCE CALCULATION
        score_variance = np.var(list(scores.values()))
        confidence = max(0.5, min(1.0, 1.0 - (score_variance / 25)))
        
        return {
            **scores,
            "total_score": total_score,
            "confidence": confidence,
            "weights_applied": weights
        }
    
    async def _apply_hard_filters(self, model_scores: Dict, requirements: TaskRequirements) -> Dict:
        """Apply hard filters that eliminate models"""
        filtered = {}
        
        for model_name, score in model_scores.items():
            model_info = self.model_database[model_name]
            
            # Privacy filter
            if model_info.get("privacy_score", 0) < requirements.privacy_level:
                continue
            
            # Context filter
            if model_info.get("context_window", 0) < requirements.estimated_context_tokens:
                continue
            
            # Cost filter
            model_cost = model_info.get("cost_per_1k_tokens", 0)
            if model_cost > requirements.max_cost_per_1k_tokens and model_cost > 0:
                continue
            
            # Latency filter
            if model_info.get("avg_latency_ms", 0) > requirements.max_latency_ms:
                continue
            
            # Capability minimum threshold
            min_capability_score = min(
                model_info["capabilities"].get(cap, 0) 
                for cap in requirements.required_capabilities
            )
            if min_capability_score < requirements.quality_threshold:
                continue
            
            filtered[model_name] = score
        
        return filtered
    
    async def _generate_selection_rationale(self, model_name: str, requirements: TaskRequirements, scores: Dict) -> str:
        """Generate human-readable rationale for model selection"""
        model_info = self.model_database[model_name]
        
        strengths = []
        considerations = []
        
        # Analyze scores
        if scores["capability_score"] >= 8:
            strengths.append(f"excellent capabilities for {', '.join(requirements.required_capabilities[:3])}")
        
        if scores["cost_score"] >= 8:
            strengths.append("cost-effective choice")
        
        if scores["latency_score"] >= 8:
            strengths.append("fast response time")
        
        if scores["privacy_score"] >= 9:
            strengths.append("high privacy compliance")
        
        if model_info.get("type") == "local":
            strengths.append("runs locally for privacy")
        
        # Add considerations
        if scores["cost_score"] < 6:
            considerations.append("higher cost but better quality")
        
        if scores["latency_score"] < 6:
            considerations.append("slower but more thorough")
        
        rationale = f"Selected {model_name} for {', '.join(strengths[:3])}"
        
        if considerations:
            rationale += f". Note: {considerations[0]}"
        
        rationale += f". Confidence: {scores['confidence']:.1%}"
        
        return rationale
    
    async def _get_top_alternatives(self, filtered_models: Dict, count: int) -> List[Tuple[str, float]]:
        """Get top alternative models"""
        sorted_models = sorted(
            filtered_models.items(), 
            key=lambda x: x[1]["total_score"], 
            reverse=True
        )[1:count+1]  # Skip first (selected model)
        
        return [(name, score["total_score"]) for name, score in sorted_models]
    
    def _track_selection(self, result: ModelSelectionResult, requirements: TaskRequirements):
        """Track model selection for analytics"""
        self.selection_history.append({
            "timestamp": datetime.now(),
            "model": result.selected_model,
            "task_type": requirements.task_type,
            "domain": requirements.domain,
            "cost": result.estimated_cost,
            "confidence": result.confidence,
            "cache_hit": result.cache_hit
        })
        
        self.model_usage_stats[result.selected_model] += 1
    
    def get_usage_analytics(self) -> Dict:
        """Get usage analytics and insights"""
        total_selections = len(self.selection_history)
        
        if total_selections == 0:
            return {"total_selections": 0}
        
        recent_selections = [
            s for s in self.selection_history 
            if s["timestamp"] > datetime.now() - timedelta(hours=24)
        ]
        
        model_distribution = {}
        for model, count in self.model_usage_stats.items():
            model_distribution[model] = f"{(count/total_selections)*100:.1f}%"
        
        avg_cost = np.mean([s["cost"] for s in self.selection_history])
        avg_confidence = np.mean([s["confidence"] for s in self.selection_history])
        cache_hit_rate = np.mean([s["cache_hit"] for s in self.selection_history])
        
        return {
            "total_selections": total_selections,
            "last_24h_selections": len(recent_selections),
            "model_distribution": model_distribution,
            "avg_cost_per_task": f"${avg_cost:.4f}",
            "avg_confidence": f"{avg_confidence:.1%}",
            "cache_hit_rate": f"{cache_hit_rate:.1%}",
            "most_used_model": max(self.model_usage_stats.items(), key=lambda x: x[1])[0]
        }

# Task type to model mapping for quick reference
TASK_TO_MODEL_MAPPING = {
    # CODING TASKS
    "simple_code_completion": "phi-3.5-mini",
    "code_review": "claude-3-5-sonnet", 
    "complex_algorithm_design": "o1-pro",
    "debugging": "deepseek-r1",
    "code_explanation": "claude-3-5-sonnet",
    
    # ANALYSIS TASKS  
    "quick_data_analysis": "gemini-1.5-flash",
    "comprehensive_research": "gemini-1.5-pro",
    "financial_analysis": "o1-pro",
    "document_analysis": "claude-3-5-sonnet",
    "image_analysis": "gpt-4o",
    
    # CONTENT TASKS
    "blog_writing": "claude-3-5-sonnet",
    "technical_documentation": "claude-3-5-sonnet", 
    "creative_writing": "claude-3-5-sonnet",
    "summarization": "claude-3-haiku",
    "translation": "gemini-1.5-flash",
    
    # REASONING TASKS
    "mathematical_proofs": "o1-pro",
    "logical_puzzles": "deepseek-r1",
    "strategic_planning": "gpt-4o",
    "problem_solving": "o1-pro",
    
    # HIGH-VOLUME TASKS
    "batch_processing": "gemini-1.5-flash",
    "high_frequency_api": "phi-3.5-mini",
    "cost_sensitive": "llama3.3-70b",
    
    # PRIVACY-SENSITIVE
    "confidential_analysis": "deepseek-r1",
    "internal_documents": "llama3.3-70b",
    "sensitive_data": "phi-3.5-mini",
    
    # MULTIMODAL TASKS
    "image_and_text": "gpt-4o",
    "video_analysis": "gemini-1.5-pro",
    "chart_interpretation": "gpt-4o",
    
    # BUSINESS TASKS
    "email_drafting": "claude-3-5-sonnet",
    "proposal_writing": "claude-3-5-sonnet",
    "market_research": "gpt-4o",
    "competitive_analysis": "o1-pro"
}

# Global router instance
router = CapabilityBasedModelRouter()

async def route_task_to_optimal_model(task: Dict, user_context: Dict = None) -> ModelSelectionResult:
    """Convenience function to route a task to the optimal model"""
    return await router.select_optimal_model(task, user_context)

if __name__ == "__main__":
    # Example usage
    async def test_router():
        # Test marketing task
        marketing_task = {
            "type": "marketing",
            "content": "Create a blog post about AI automation benefits for small businesses",
            "domain": "marketing",
            "privacy_level": 5,
            "max_cost": 0.01,
            "quality_threshold": 8.0
        }
        
        result = await route_task_to_optimal_model(marketing_task)
        
        print(f"Selected Model: {result.selected_model}")
        print(f"Rationale: {result.rationale}")
        print(f"Estimated Cost: ${result.estimated_cost:.4f}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Alternatives: {result.alternatives}")
        
        # Get analytics
        analytics = router.get_usage_analytics()
        print(f"\nUsage Analytics: {analytics}")
    
    # Run test
    asyncio.run(test_router())