#!/usr/bin/env python3
"""
💰 Smart Cost Optimizer for AI Model Selection
Advanced cost optimization that considers total value, not just price

Features:
- Total Value Score calculation (quality/cost ratio)
- Opportunity cost analysis
- Time value of money considerations
- Quality-adjusted cost metrics
- ROI optimization for different use cases
- Dynamic pricing models
- Cost prediction and budgeting
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sqlite3

from .capability_based_router import ModelSelectionResult, TaskRequirements

logger = logging.getLogger(__name__)

@dataclass
class CostAnalysis:
    """Comprehensive cost analysis result"""
    base_token_cost: float
    output_token_cost: float
    time_cost: float
    opportunity_cost: float
    quality_adjustment_factor: float
    total_direct_cost: float
    total_adjusted_cost: float
    value_score: float
    roi_estimate: float
    cost_efficiency_rating: str
    break_even_threshold: float

@dataclass
class ValueMetrics:
    """Value metrics for cost optimization"""
    quality_score: float
    speed_score: float
    reliability_score: float
    total_value: float
    cost_per_quality_point: float
    time_to_value: float
    productivity_multiplier: float

class SmartCostOptimizer:
    """Advanced cost optimizer that considers total value beyond just token pricing"""
    
    def __init__(self, config_path: str = "/root/supermcp/supermcp_new/config/cost_config.json"):
        self.config_path = Path(config_path)
        self.cost_history_db = "/root/supermcp/data/cost_history.db"
        
        # Initialize cost configuration
        self.cost_config = self._load_cost_config()
        self._init_cost_database()
        
        # Business value parameters
        self.hourly_rates = {
            "developer": 75.0,
            "content_creator": 45.0, 
            "analyst": 60.0,
            "marketer": 50.0,
            "executive": 150.0,
            "default": 50.0
        }
        
        # Quality thresholds for different use cases
        self.quality_thresholds = {
            "production": 8.5,
            "development": 7.0,
            "experimentation": 6.0,
            "high_stakes": 9.0,
            "cost_sensitive": 5.5
        }
        
        # ROI expectations by task type
        self.roi_targets = {
            "content_creation": 3.0,  # 300% ROI expected
            "data_analysis": 4.0,
            "code_generation": 5.0,
            "marketing": 2.5,
            "research": 2.0,
            "automation": 10.0
        }
    
    def _load_cost_config(self) -> Dict:
        """Load cost optimization configuration"""
        default_config = {
            "opportunity_cost_multiplier": 1.2,
            "quality_weight": 0.4,
            "speed_weight": 0.3,
            "cost_weight": 0.3,
            "time_value_discount_rate": 0.05,
            "quality_cost_curve": "exponential",
            "max_acceptable_cost": 1.0,
            "cost_efficiency_thresholds": {
                "excellent": 0.001,
                "good": 0.005, 
                "fair": 0.02,
                "poor": 0.1
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load cost config: {e}")
        else:
            # Create default config file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _init_cost_database(self):
        """Initialize cost tracking database"""
        Path(self.cost_history_db).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.cost_history_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    estimated_cost REAL NOT NULL,
                    actual_cost REAL,
                    estimated_quality REAL NOT NULL,
                    actual_quality REAL,
                    estimated_time INTEGER NOT NULL,
                    actual_time INTEGER,
                    value_score REAL NOT NULL,
                    roi_actual REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_benchmarks (
                    model_name TEXT PRIMARY KEY,
                    avg_cost_per_1k REAL NOT NULL,
                    avg_quality REAL NOT NULL,
                    avg_latency_ms INTEGER NOT NULL,
                    avg_value_score REAL NOT NULL,
                    total_tasks INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def calculate_total_value_score(self, model_info: Dict, task: Dict, 
                                        user_context: Dict = None) -> CostAnalysis:
        """Calculate comprehensive total value score considering all cost factors"""
        
        if user_context is None:
            user_context = {}
        
        # Extract task parameters
        estimated_tokens = task.get("estimated_tokens", self._estimate_tokens(task))
        task_type = task.get("type", "general")
        urgency_level = task.get("urgency", 5)
        quality_requirement = task.get("quality_threshold", 7.0)
        
        # Base cost calculation
        base_cost = await self._calculate_base_cost(model_info, estimated_tokens)
        output_cost = await self._calculate_output_cost(model_info, estimated_tokens)
        
        # Time and opportunity costs
        time_cost = await self._calculate_time_cost(model_info, task, user_context)
        opportunity_cost = await self._calculate_opportunity_cost(model_info, task, urgency_level)
        
        # Quality adjustments
        estimated_quality = await self._estimate_quality_score(model_info, task)
        quality_adjustment = await self._calculate_quality_adjustment(estimated_quality, quality_requirement)
        
        # Total costs
        total_direct_cost = base_cost + output_cost
        total_adjusted_cost = (total_direct_cost + time_cost + opportunity_cost) * quality_adjustment
        
        # Value calculations
        value_score = await self._calculate_value_score(estimated_quality, total_adjusted_cost, model_info)
        roi_estimate = await self._estimate_roi(value_score, total_adjusted_cost, task_type)
        
        # Cost efficiency rating
        cost_efficiency = await self._get_cost_efficiency_rating(total_adjusted_cost, estimated_quality)
        
        # Break-even analysis
        break_even = await self._calculate_break_even_threshold(model_info, task)
        
        return CostAnalysis(
            base_token_cost=base_cost,
            output_token_cost=output_cost,
            time_cost=time_cost,
            opportunity_cost=opportunity_cost,
            quality_adjustment_factor=quality_adjustment,
            total_direct_cost=total_direct_cost,
            total_adjusted_cost=total_adjusted_cost,
            value_score=value_score,
            roi_estimate=roi_estimate,
            cost_efficiency_rating=cost_efficiency,
            break_even_threshold=break_even
        )
    
    async def optimize_model_selection(self, candidate_models: List[Tuple[str, Dict]], 
                                     task: Dict, user_context: Dict = None) -> Tuple[str, CostAnalysis]:
        """Optimize model selection based on total value, not just cost"""
        
        best_model = None
        best_analysis = None
        best_value_score = -1
        
        optimization_strategy = user_context.get("optimization_strategy", "balanced") if user_context else "balanced"
        
        for model_name, model_info in candidate_models:
            analysis = await self.calculate_total_value_score(model_info, task, user_context)
            
            # Apply optimization strategy
            weighted_score = await self._apply_optimization_strategy(analysis, optimization_strategy)
            
            if weighted_score > best_value_score:
                best_value_score = weighted_score
                best_model = model_name
                best_analysis = analysis
        
        return best_model, best_analysis
    
    async def _calculate_base_cost(self, model_info: Dict, estimated_tokens: int) -> float:
        """Calculate base token cost"""
        cost_per_1k = model_info.get("cost_per_1k_tokens", 0.0)
        return cost_per_1k * (estimated_tokens / 1000)
    
    async def _calculate_output_cost(self, model_info: Dict, estimated_tokens: int) -> float:
        """Calculate output token cost (usually higher than input)"""
        output_cost_per_1k = model_info.get("cost_per_1k_tokens_output", 
                                          model_info.get("cost_per_1k_tokens", 0.0) * 4)
        
        # Estimate output tokens as 30% of input tokens
        estimated_output_tokens = estimated_tokens * 0.3
        
        return output_cost_per_1k * (estimated_output_tokens / 1000)
    
    async def _calculate_time_cost(self, model_info: Dict, task: Dict, user_context: Dict) -> float:
        """Calculate the cost of time spent waiting for model response"""
        
        latency_ms = model_info.get("avg_latency_ms", 1000)
        user_role = user_context.get("role", "default") if user_context else "default"
        hourly_rate = self.hourly_rates.get(user_role, self.hourly_rates["default"])
        
        # Convert latency to hours and calculate cost
        latency_hours = latency_ms / (1000 * 3600)
        base_time_cost = latency_hours * hourly_rate
        
        # Adjust for task urgency
        urgency_multiplier = max(1.0, task.get("urgency", 5) / 5.0)
        
        # Adjust for context switching cost (higher for longer delays)
        if latency_ms > 5000:  # More than 5 seconds
            context_switch_penalty = (latency_ms - 5000) / 1000 * 0.02  # 2 cents per second over 5s
            base_time_cost += context_switch_penalty
        
        return base_time_cost * urgency_multiplier
    
    async def _calculate_opportunity_cost(self, model_info: Dict, task: Dict, urgency_level: int) -> float:
        """Calculate opportunity cost of delays"""
        
        latency_ms = model_info.get("avg_latency_ms", 1000)
        multiplier = self.cost_config["opportunity_cost_multiplier"]
        
        # Base opportunity cost increases with urgency and delay
        base_opportunity = (latency_ms / 1000) * (urgency_level / 10) * multiplier
        
        # Task type adjustments
        task_type = task.get("type", "general")
        type_multipliers = {
            "real_time": 3.0,
            "interactive": 2.0,
            "batch": 0.5,
            "research": 0.8,
            "production": 1.5
        }
        
        type_multiplier = type_multipliers.get(task_type, 1.0)
        
        return base_opportunity * type_multiplier
    
    async def _estimate_quality_score(self, model_info: Dict, task: Dict) -> float:
        """Estimate expected quality score for this model on this task"""
        
        required_capabilities = task.get("required_capabilities", ["reasoning"])
        capabilities = model_info.get("capabilities", {})
        
        # Calculate capability-weighted quality score
        quality_scores = []
        for capability in required_capabilities:
            score = capabilities.get(capability, 5.0)
            quality_scores.append(score)
        
        if not quality_scores:
            return 7.0
        
        # Use harmonic mean to penalize weak capabilities more heavily
        harmonic_mean = len(quality_scores) / sum(1/max(score, 0.1) for score in quality_scores)
        
        # Adjust for model reliability
        reliability_bonus = model_info.get("reliability_score", 8.5) / 10.0
        
        final_quality = min(10.0, harmonic_mean * reliability_bonus)
        return final_quality
    
    async def _calculate_quality_adjustment(self, estimated_quality: float, required_quality: float) -> float:
        """Calculate quality adjustment factor for cost"""
        
        if estimated_quality >= required_quality:
            # Good quality, minimal adjustment
            return 1.0
        else:
            # Poor quality, increase effective cost
            quality_gap = required_quality - estimated_quality
            
            # Exponential penalty for quality gaps
            penalty = 1.0 + (quality_gap / 10.0) ** 2
            
            return min(penalty, 3.0)  # Cap at 3x cost penalty
    
    async def _calculate_value_score(self, quality: float, total_cost: float, model_info: Dict) -> float:
        """Calculate total value score (quality/cost ratio with adjustments)"""
        
        if total_cost <= 0:
            return quality * 10  # Local models get bonus
        
        # Base value score
        base_value = quality / max(total_cost, 0.0001)
        
        # Adjust for model characteristics
        privacy_bonus = model_info.get("privacy_score", 5) / 10.0
        speed_bonus = max(0.5, 1.0 - (model_info.get("avg_latency_ms", 1000) / 10000))
        
        adjusted_value = base_value * (1 + privacy_bonus * 0.2) * (1 + speed_bonus * 0.1)
        
        return adjusted_value
    
    async def _estimate_roi(self, value_score: float, total_cost: float, task_type: str) -> float:
        """Estimate ROI for this model selection"""
        
        target_roi = self.roi_targets.get(task_type, 3.0)
        
        # Estimate value created
        estimated_value_created = value_score * 0.1  # Rough conversion
        
        if total_cost <= 0:
            return 999.0  # Infinite ROI for free models
        
        roi = (estimated_value_created - total_cost) / total_cost
        
        return max(0.0, roi)
    
    async def _get_cost_efficiency_rating(self, total_cost: float, quality: float) -> str:
        """Get cost efficiency rating"""
        
        cost_per_quality = total_cost / max(quality, 1.0)
        thresholds = self.cost_config["cost_efficiency_thresholds"]
        
        if cost_per_quality <= thresholds["excellent"]:
            return "excellent"
        elif cost_per_quality <= thresholds["good"]:
            return "good"
        elif cost_per_quality <= thresholds["fair"]:
            return "fair"
        else:
            return "poor"
    
    async def _calculate_break_even_threshold(self, model_info: Dict, task: Dict) -> float:
        """Calculate break-even threshold for cost justification"""
        
        base_cost = model_info.get("cost_per_1k_tokens", 0.0)
        
        if base_cost <= 0:
            return 0.0  # Local models always break even
        
        # Estimate minimum value that must be created to justify cost
        minimum_roi = 1.0  # 100% ROI minimum
        break_even_value = base_cost * (1 + minimum_roi)
        
        return break_even_value
    
    async def _apply_optimization_strategy(self, analysis: CostAnalysis, strategy: str) -> float:
        """Apply optimization strategy to get weighted score"""
        
        if strategy == "cost_first":
            # Prioritize low cost
            cost_score = 1.0 / max(analysis.total_adjusted_cost, 0.0001)
            quality_score = analysis.value_score * 0.1
            return cost_score * 0.8 + quality_score * 0.2
            
        elif strategy == "quality_first":
            # Prioritize high quality/value
            return analysis.value_score * 0.9 + (1.0 / max(analysis.total_adjusted_cost, 0.0001)) * 0.1
            
        elif strategy == "roi_focused":
            # Prioritize ROI
            return analysis.roi_estimate * 0.7 + analysis.value_score * 0.3
            
        elif strategy == "speed_first":
            # Factor in speed more heavily
            speed_bonus = 1.0 / max(analysis.time_cost, 0.001)
            return analysis.value_score * 0.6 + speed_bonus * 0.4
            
        else:  # "balanced"
            # Balanced optimization
            weights = self.cost_config
            cost_score = 1.0 / max(analysis.total_adjusted_cost, 0.0001)
            
            weighted_score = (
                analysis.value_score * weights["quality_weight"] +
                cost_score * weights["cost_weight"] +
                (1.0 / max(analysis.time_cost, 0.001)) * weights["speed_weight"]
            )
            
            return weighted_score
    
    def _estimate_tokens(self, task: Dict) -> int:
        """Estimate token count for a task"""
        content = task.get("content", "")
        
        if not content:
            return 1000  # Default
        
        # Rough estimation: 1 word = 1.3 tokens
        word_count = len(content.split())
        estimated_tokens = int(word_count * 1.3)
        
        # Add context tokens for system prompts, etc.
        estimated_tokens += 500
        
        # Reasonable bounds
        return max(500, min(estimated_tokens, 100000))
    
    async def record_actual_costs(self, task_id: str, model_name: str, 
                                actual_cost: float, actual_quality: float, 
                                actual_time_ms: int):
        """Record actual costs for learning and improvement"""
        
        with sqlite3.connect(self.cost_history_db) as conn:
            # Update the existing record with actual values
            conn.execute("""
                UPDATE cost_history 
                SET actual_cost = ?, actual_quality = ?, actual_time = ?
                WHERE task_id = ? AND model_name = ?
            """, (actual_cost, actual_quality, actual_time_ms, task_id, model_name))
            
            # Calculate actual ROI
            cursor = conn.execute("""
                SELECT estimated_cost, value_score FROM cost_history 
                WHERE task_id = ? AND model_name = ?
            """, (task_id, model_name))
            
            result = cursor.fetchone()
            if result:
                estimated_cost, value_score = result
                actual_roi = (value_score - actual_cost) / max(actual_cost, 0.001)
                
                conn.execute("""
                    UPDATE cost_history 
                    SET roi_actual = ?
                    WHERE task_id = ? AND model_name = ?
                """, (actual_roi, task_id, model_name))
    
    async def get_cost_insights(self) -> Dict:
        """Get cost optimization insights and recommendations"""
        
        with sqlite3.connect(self.cost_history_db) as conn:
            # Get average costs by model
            cursor = conn.execute("""
                SELECT model_name, 
                       AVG(actual_cost) as avg_cost,
                       AVG(actual_quality) as avg_quality,
                       AVG(roi_actual) as avg_roi,
                       COUNT(*) as task_count
                FROM cost_history 
                WHERE actual_cost IS NOT NULL
                GROUP BY model_name
                ORDER BY avg_roi DESC
            """)
            
            model_performance = cursor.fetchall()
            
            # Get recent cost trends
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date,
                       AVG(actual_cost) as avg_cost,
                       COUNT(*) as tasks
                FROM cost_history 
                WHERE actual_cost IS NOT NULL 
                AND timestamp > date('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """)
            
            cost_trends = cursor.fetchall()
        
        # Calculate cost savings opportunities
        total_cost = sum(row[1] * row[4] for row in model_performance if row[1])
        potential_savings = total_cost * 0.15  # Estimate 15% savings potential
        
        insights = {
            "model_performance": [
                {
                    "model": row[0],
                    "avg_cost": row[1] or 0,
                    "avg_quality": row[2] or 0,
                    "avg_roi": row[3] or 0,
                    "task_count": row[4]
                } for row in model_performance
            ],
            
            "cost_trends": [
                {
                    "date": row[0],
                    "avg_cost": row[1],
                    "task_count": row[2]
                } for row in cost_trends
            ],
            
            "optimization_opportunities": {
                "potential_monthly_savings": f"${potential_savings:.2f}",
                "cost_efficiency_recommendation": "Consider using more local models for non-sensitive tasks",
                "roi_leaders": [perf["model"] for perf in 
                              sorted([{"model": row[0], "roi": row[3] or 0} for row in model_performance], 
                                   key=lambda x: x["roi"], reverse=True)[:3]]
            },
            
            "cost_summary": {
                "total_estimated_monthly_cost": f"${total_cost:.2f}",
                "best_roi_model": model_performance[0][0] if model_performance else "No data",
                "avg_cost_per_task": f"${np.mean([row[1] for row in model_performance if row[1]]):.4f}" if model_performance else "$0.0000"
            }
        }
        
        return insights
    
    async def predict_monthly_costs(self, projected_tasks: Dict[str, int]) -> Dict:
        """Predict monthly costs based on projected task volumes"""
        
        predictions = {}
        total_predicted_cost = 0
        
        for task_type, volume in projected_tasks.items():
            # Get historical average cost for this task type
            with sqlite3.connect(self.cost_history_db) as conn:
                cursor = conn.execute("""
                    SELECT AVG(actual_cost) 
                    FROM cost_history 
                    WHERE task_id LIKE ? AND actual_cost IS NOT NULL
                """, (f"%{task_type}%",))
                
                result = cursor.fetchone()
                avg_cost = result[0] if result and result[0] else 0.01  # Default cost
            
            predicted_cost = avg_cost * volume
            total_predicted_cost += predicted_cost
            
            predictions[task_type] = {
                "volume": volume,
                "avg_cost_per_task": avg_cost,
                "total_cost": predicted_cost
            }
        
        return {
            "task_predictions": predictions,
            "total_monthly_cost": total_predicted_cost,
            "recommendations": await self._generate_cost_recommendations(predictions)
        }
    
    async def _generate_cost_recommendations(self, predictions: Dict) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # Check for high-volume, high-cost tasks
        for task_type, data in predictions.items():
            if data["volume"] > 100 and data["avg_cost_per_task"] > 0.01:
                recommendations.append(
                    f"Consider optimizing {task_type} tasks - high volume ({data['volume']}) "
                    f"with high per-task cost (${data['avg_cost_per_task']:.4f})"
                )
        
        # General recommendations
        if any(data["avg_cost_per_task"] > 0.05 for data in predictions.values()):
            recommendations.append("Consider using more local models for cost-sensitive tasks")
        
        if len(predictions) > 5:
            recommendations.append("Implement batch processing for similar tasks to reduce overhead")
        
        return recommendations

# Global optimizer instance
cost_optimizer = SmartCostOptimizer()

async def optimize_model_for_value(candidate_models: List[Tuple[str, Dict]], 
                                 task: Dict, user_context: Dict = None) -> Tuple[str, CostAnalysis]:
    """Convenience function to optimize model selection for total value"""
    return await cost_optimizer.optimize_model_selection(candidate_models, task, user_context)

async def calculate_task_value(model_info: Dict, task: Dict, 
                             user_context: Dict = None) -> CostAnalysis:
    """Convenience function to calculate total value for a specific model/task combination"""
    return await cost_optimizer.calculate_total_value_score(model_info, task, user_context)

if __name__ == "__main__":
    # Example usage
    async def test_cost_optimizer():
        # Example model candidates
        candidates = [
            ("gpt-4o", {
                "cost_per_1k_tokens": 0.0025,
                "cost_per_1k_tokens_output": 0.01,
                "avg_latency_ms": 2000,
                "capabilities": {"reasoning": 9, "writing": 9},
                "privacy_score": 6,
                "reliability_score": 9.2
            }),
            ("claude-3-5-sonnet", {
                "cost_per_1k_tokens": 0.003,
                "cost_per_1k_tokens_output": 0.015,
                "avg_latency_ms": 1800,
                "capabilities": {"reasoning": 9, "writing": 10},
                "privacy_score": 7,
                "reliability_score": 9.0
            }),
            ("deepseek-r1", {
                "cost_per_1k_tokens": 0.0,
                "cost_per_1k_tokens_output": 0.0,
                "avg_latency_ms": 800,
                "capabilities": {"reasoning": 9, "writing": 7},
                "privacy_score": 10,
                "reliability_score": 8.5
            })
        ]
        
        task = {
            "type": "content_creation",
            "content": "Write a comprehensive analysis of AI market trends",
            "required_capabilities": ["reasoning", "writing", "analysis"],
            "estimated_tokens": 3000,
            "quality_threshold": 8.0,
            "urgency": 6
        }
        
        user_context = {
            "role": "analyst",
            "optimization_strategy": "balanced"
        }
        
        # Optimize selection
        best_model, analysis = await optimize_model_for_value(candidates, task, user_context)
        
        print(f"Optimal Model: {best_model}")
        print(f"Total Adjusted Cost: ${analysis.total_adjusted_cost:.4f}")
        print(f"Value Score: {analysis.value_score:.2f}")
        print(f"ROI Estimate: {analysis.roi_estimate:.1%}")
        print(f"Cost Efficiency: {analysis.cost_efficiency_rating}")
        print(f"Break-even Threshold: ${analysis.break_even_threshold:.4f}")
        
        # Get cost insights
        insights = await cost_optimizer.get_cost_insights()
        print(f"\nCost Insights: {insights}")
    
    asyncio.run(test_cost_optimizer())