#!/usr/bin/env python3
"""
🧠 Model Performance Learning System
Adaptive learning system that improves model selection through real-world feedback

Features:
- Real-time performance tracking
- Adaptive capability weight adjustment
- Predictive model selection using ML
- Performance pattern recognition
- Automatic model benchmark updates
- Quality degradation detection
- Cost-performance optimization learning
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import json
import pickle
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib

logger = logging.getLogger(__name__)

@dataclass
class TaskOutcome:
    """Result of a completed task for learning"""
    task_id: str
    selected_model: str
    task_type: str
    required_capabilities: List[str]
    estimated_cost: float
    actual_cost: float
    estimated_quality: float
    actual_quality: float
    estimated_latency: int
    actual_latency: int
    user_satisfaction: float  # 1-10 scale
    task_success: bool
    completion_time: datetime
    user_feedback: str
    context_metadata: Dict[str, Any]

@dataclass
class ModelLearningInsights:
    """Learning insights about model performance"""
    model_name: str
    capability_accuracy: Dict[str, float]
    cost_prediction_accuracy: float
    quality_prediction_accuracy: float
    user_satisfaction_trend: float
    recommended_adjustments: List[str]
    confidence_level: float

class ModelPerformanceLearner:
    """Learning system that continuously improves model selection through feedback"""
    
    def __init__(self, data_path: str = "/root/supermcp/data/model_learning"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Database for storing learning data
        self.learning_db = self.data_path / "learning_data.db"
        self._init_learning_database()
        
        # ML models for prediction
        self.model_quality_predictor = None
        self.model_cost_predictor = None
        self.model_selection_classifier = None
        self.feature_scaler = StandardScaler()
        
        # Learning configuration
        self.learning_config = {
            "min_samples_for_learning": 50,
            "weight_adjustment_rate": 0.05,
            "prediction_confidence_threshold": 0.7,
            "model_retraining_interval": 24,  # hours
            "feedback_weight_decay": 0.95,
            "quality_threshold_adjustment": 0.1
        }
        
        # Capability weight adjustments based on learning
        self.capability_weight_adjustments = defaultdict(float)
        self.model_performance_history = defaultdict(list)
        
        # Learning metrics
        self.learning_metrics = {
            "total_tasks_learned": 0,
            "prediction_accuracy": 0.0,
            "weight_adjustments_made": 0,
            "models_retrained": 0,
            "last_learning_update": None
        }
        
        # Load existing ML models if available
        self._load_ml_models()
    
    def _init_learning_database(self):
        """Initialize learning database"""
        with sqlite3.connect(self.learning_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    selected_model TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    required_capabilities TEXT NOT NULL,
                    estimated_cost REAL NOT NULL,
                    actual_cost REAL,
                    estimated_quality REAL NOT NULL,
                    actual_quality REAL,
                    estimated_latency INTEGER NOT NULL,
                    actual_latency INTEGER,
                    user_satisfaction REAL,
                    task_success BOOLEAN,
                    completion_time TIMESTAMP,
                    user_feedback TEXT,
                    context_metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS capability_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    capability TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    predicted_score REAL NOT NULL,
                    actual_performance REAL NOT NULL,
                    weight_adjustment REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_benchmarks_learned (
                    model_name TEXT PRIMARY KEY,
                    avg_quality_error REAL DEFAULT 0.0,
                    avg_cost_error REAL DEFAULT 0.0,
                    avg_latency_error REAL DEFAULT 0.0,
                    prediction_confidence REAL DEFAULT 0.5,
                    total_samples INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_model ON task_outcomes(selected_model, task_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capability_model ON capability_learning(capability, model_name)
            """)
    
    async def record_task_outcome(self, outcome: TaskOutcome):
        """Record the outcome of a completed task for learning"""
        
        with sqlite3.connect(self.learning_db) as conn:
            # Insert task outcome
            conn.execute("""
                INSERT OR REPLACE INTO task_outcomes 
                (task_id, selected_model, task_type, required_capabilities, 
                 estimated_cost, actual_cost, estimated_quality, actual_quality,
                 estimated_latency, actual_latency, user_satisfaction, task_success,
                 completion_time, user_feedback, context_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                outcome.task_id, outcome.selected_model, outcome.task_type,
                json.dumps(outcome.required_capabilities),
                outcome.estimated_cost, outcome.actual_cost,
                outcome.estimated_quality, outcome.actual_quality,
                outcome.estimated_latency, outcome.actual_latency,
                outcome.user_satisfaction, outcome.task_success,
                outcome.completion_time, outcome.user_feedback,
                json.dumps(outcome.context_metadata)
            ))
        
        # Update learning metrics
        self.learning_metrics["total_tasks_learned"] += 1
        self.learning_metrics["last_learning_update"] = datetime.now()
        
        # Store outcome for immediate learning
        self.model_performance_history[outcome.selected_model].append(outcome)
        
        # Trigger learning updates
        await self._update_capability_weights(outcome)
        await self._update_model_benchmarks(outcome)
        
        # Check if we should retrain ML models
        if self.learning_metrics["total_tasks_learned"] % 50 == 0:
            await self._retrain_ml_models()
    
    async def _update_capability_weights(self, outcome: TaskOutcome):
        """Update capability weights based on task outcome"""
        
        if outcome.actual_quality is None or outcome.estimated_quality <= 0:
            return
        
        # Calculate quality prediction error
        quality_error = abs(outcome.actual_quality - outcome.estimated_quality) / 10.0
        
        # Adjust weights for each capability based on performance
        adjustment_rate = self.learning_config["weight_adjustment_rate"]
        
        for capability in outcome.required_capabilities:
            # If quality was worse than expected, reduce capability weight
            if outcome.actual_quality < outcome.estimated_quality:
                adjustment = -quality_error * adjustment_rate
            else:
                # If quality was better than expected, increase capability weight
                adjustment = quality_error * adjustment_rate * 0.5  # More conservative increase
            
            self.capability_weight_adjustments[capability] += adjustment
            
            # Record the learning
            with sqlite3.connect(self.learning_db) as conn:
                conn.execute("""
                    INSERT INTO capability_learning 
                    (capability, model_name, predicted_score, actual_performance, weight_adjustment)
                    VALUES (?, ?, ?, ?, ?)
                """, (capability, outcome.selected_model, outcome.estimated_quality, 
                      outcome.actual_quality, adjustment))
        
        self.learning_metrics["weight_adjustments_made"] += len(outcome.required_capabilities)
    
    async def _update_model_benchmarks(self, outcome: TaskOutcome):
        """Update model benchmark data based on actual performance"""
        
        model_name = outcome.selected_model
        
        # Calculate prediction errors
        quality_error = abs(outcome.actual_quality - outcome.estimated_quality) if outcome.actual_quality else 0
        cost_error = abs(outcome.actual_cost - outcome.estimated_cost) if outcome.actual_cost else 0
        latency_error = abs(outcome.actual_latency - outcome.estimated_latency) if outcome.actual_latency else 0
        
        with sqlite3.connect(self.learning_db) as conn:
            # Get current benchmarks
            cursor = conn.execute("""
                SELECT avg_quality_error, avg_cost_error, avg_latency_error, 
                       prediction_confidence, total_samples
                FROM model_benchmarks_learned 
                WHERE model_name = ?
            """, (model_name,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing benchmarks with exponential moving average
                old_quality_error, old_cost_error, old_latency_error, old_confidence, total_samples = result
                alpha = 0.1  # Learning rate for exponential moving average
                
                new_quality_error = old_quality_error * (1 - alpha) + quality_error * alpha
                new_cost_error = old_cost_error * (1 - alpha) + cost_error * alpha
                new_latency_error = old_latency_error * (1 - alpha) + latency_error * alpha
                
                # Update confidence based on recent prediction accuracy
                prediction_accuracy = 1.0 - (new_quality_error / 10.0)
                new_confidence = old_confidence * 0.9 + prediction_accuracy * 0.1
                
                new_total_samples = total_samples + 1
            else:
                # Create new benchmark entry
                new_quality_error = quality_error
                new_cost_error = cost_error
                new_latency_error = latency_error
                new_confidence = max(0.1, 1.0 - (quality_error / 10.0))
                new_total_samples = 1
            
            # Update or insert benchmark
            conn.execute("""
                INSERT OR REPLACE INTO model_benchmarks_learned 
                (model_name, avg_quality_error, avg_cost_error, avg_latency_error, 
                 prediction_confidence, total_samples, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (model_name, new_quality_error, new_cost_error, new_latency_error,
                  new_confidence, new_total_samples, datetime.now()))
    
    async def get_learned_capability_weights(self) -> Dict[str, float]:
        """Get capability weights adjusted by learning"""
        return dict(self.capability_weight_adjustments)
    
    async def get_model_learning_insights(self, model_name: str) -> ModelLearningInsights:
        """Get learning insights for a specific model"""
        
        with sqlite3.connect(self.learning_db) as conn:
            # Get capability accuracy for this model
            cursor = conn.execute("""
                SELECT capability, AVG(ABS(predicted_score - actual_performance)) as avg_error
                FROM capability_learning 
                WHERE model_name = ?
                GROUP BY capability
            """, (model_name,))
            
            capability_accuracy = {}
            for capability, avg_error in cursor.fetchall():
                accuracy = max(0.0, 1.0 - (avg_error / 10.0))
                capability_accuracy[capability] = accuracy
            
            # Get overall prediction accuracy
            cursor = conn.execute("""
                SELECT avg_quality_error, avg_cost_error, prediction_confidence, total_samples
                FROM model_benchmarks_learned 
                WHERE model_name = ?
            """, (model_name,))
            
            result = cursor.fetchone()
            if result:
                quality_error, cost_error, confidence, total_samples = result
                quality_accuracy = max(0.0, 1.0 - (quality_error / 10.0))
                cost_accuracy = max(0.0, 1.0 - (cost_error / 1.0))  # Assuming $1 max error
            else:
                quality_accuracy = 0.5
                cost_accuracy = 0.5
                confidence = 0.5
                total_samples = 0
            
            # Get recent user satisfaction trend
            cursor = conn.execute("""
                SELECT AVG(user_satisfaction) as avg_satisfaction
                FROM task_outcomes 
                WHERE selected_model = ? AND user_satisfaction IS NOT NULL
                AND timestamp > datetime('now', '-30 days')
            """, (model_name,))
            
            result = cursor.fetchone()
            satisfaction_trend = result[0] if result and result[0] else 7.0
        
        # Generate recommendations
        recommendations = []
        
        if quality_accuracy < 0.7:
            recommendations.append(f"Quality predictions for {model_name} are unreliable ({quality_accuracy:.1%})")
        
        if cost_accuracy < 0.8:
            recommendations.append(f"Cost estimates need improvement ({cost_accuracy:.1%})")
        
        if satisfaction_trend < 6.0:
            recommendations.append(f"User satisfaction is below target ({satisfaction_trend:.1f}/10)")
        
        if total_samples < 20:
            recommendations.append("Insufficient data for reliable insights")
        
        return ModelLearningInsights(
            model_name=model_name,
            capability_accuracy=capability_accuracy,
            cost_prediction_accuracy=cost_accuracy,
            quality_prediction_accuracy=quality_accuracy,
            user_satisfaction_trend=satisfaction_trend,
            recommended_adjustments=recommendations,
            confidence_level=confidence
        )
    
    async def predict_model_performance(self, model_name: str, task_features: Dict) -> Dict[str, float]:
        """Predict model performance for a task using learned patterns"""
        
        if not self.model_quality_predictor:
            return {"quality": 7.0, "confidence": 0.5}
        
        try:
            # Prepare features for prediction
            features = self._extract_prediction_features(task_features)
            features_scaled = self.feature_scaler.transform([features])
            
            # Predict quality
            predicted_quality = self.model_quality_predictor.predict(features_scaled)[0]
            
            # Get prediction confidence from model benchmark
            with sqlite3.connect(self.learning_db) as conn:
                cursor = conn.execute("""
                    SELECT prediction_confidence 
                    FROM model_benchmarks_learned 
                    WHERE model_name = ?
                """, (model_name,))
                
                result = cursor.fetchone()
                confidence = result[0] if result else 0.5
            
            return {
                "quality": max(1.0, min(10.0, predicted_quality)),
                "confidence": confidence
            }
            
        except Exception as e:
            logger.warning(f"Error in prediction: {e}")
            return {"quality": 7.0, "confidence": 0.5}
    
    async def _retrain_ml_models(self):
        """Retrain ML models with accumulated data"""
        
        with sqlite3.connect(self.learning_db) as conn:
            # Get training data
            df = pd.read_sql_query("""
                SELECT selected_model, task_type, required_capabilities,
                       estimated_quality, actual_quality, estimated_cost, actual_cost,
                       estimated_latency, actual_latency, user_satisfaction, task_success
                FROM task_outcomes 
                WHERE actual_quality IS NOT NULL 
                AND actual_cost IS NOT NULL
                ORDER BY timestamp DESC
            """, conn)
        
        if len(df) < self.learning_config["min_samples_for_learning"]:
            logger.info(f"Insufficient data for retraining ({len(df)} samples)")
            return
        
        try:
            # Prepare features and targets
            features = []
            quality_targets = []
            cost_targets = []
            
            for _, row in df.iterrows():
                feature_vector = self._extract_prediction_features({
                    "model_name": row["selected_model"],
                    "task_type": row["task_type"],
                    "required_capabilities": json.loads(row["required_capabilities"]),
                    "estimated_latency": row["estimated_latency"]
                })
                
                features.append(feature_vector)
                quality_targets.append(row["actual_quality"])
                cost_targets.append(row["actual_cost"])
            
            features = np.array(features)
            quality_targets = np.array(quality_targets)
            cost_targets = np.array(cost_targets)
            
            # Scale features
            features_scaled = self.feature_scaler.fit_transform(features)
            
            # Split data
            X_train, X_test, y_quality_train, y_quality_test = train_test_split(
                features_scaled, quality_targets, test_size=0.2, random_state=42
            )
            
            _, _, y_cost_train, y_cost_test = train_test_split(
                features_scaled, cost_targets, test_size=0.2, random_state=42
            )
            
            # Train quality predictor
            self.model_quality_predictor = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10
            )
            self.model_quality_predictor.fit(X_train, y_quality_train)
            
            # Train cost predictor
            self.model_cost_predictor = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10
            )
            self.model_cost_predictor.fit(X_train, y_cost_train)
            
            # Evaluate models
            quality_predictions = self.model_quality_predictor.predict(X_test)
            cost_predictions = self.model_cost_predictor.predict(X_test)
            
            quality_mse = mean_squared_error(y_quality_test, quality_predictions)
            cost_mse = mean_squared_error(y_cost_test, cost_predictions)
            
            # Update learning metrics
            self.learning_metrics["prediction_accuracy"] = max(0.0, 1.0 - (quality_mse / 25.0))
            self.learning_metrics["models_retrained"] += 1
            
            # Save models
            self._save_ml_models()
            
            logger.info(f"ML models retrained. Quality MSE: {quality_mse:.3f}, Cost MSE: {cost_mse:.6f}")
            
        except Exception as e:
            logger.error(f"Error retraining ML models: {e}")
    
    def _extract_prediction_features(self, task_data: Dict) -> List[float]:
        """Extract numerical features for ML prediction"""
        
        features = []
        
        # Model encoding (simple hash-based)
        model_name = task_data.get("model_name", "unknown")
        model_hash = hash(model_name) % 1000
        features.append(model_hash)
        
        # Task type encoding
        task_type = task_data.get("task_type", "general")
        task_hash = hash(task_type) % 100
        features.append(task_hash)
        
        # Capability count
        capabilities = task_data.get("required_capabilities", [])
        features.append(len(capabilities))
        
        # Capability complexity (sum of capability hashes)
        capability_complexity = sum(hash(cap) % 10 for cap in capabilities)
        features.append(capability_complexity)
        
        # Estimated latency
        features.append(task_data.get("estimated_latency", 1000))
        
        # Time features
        now = datetime.now()
        features.append(now.hour)  # Hour of day
        features.append(now.weekday())  # Day of week
        
        return features
    
    def _save_ml_models(self):
        """Save trained ML models to disk"""
        models_path = self.data_path / "ml_models"
        models_path.mkdir(exist_ok=True)
        
        try:
            if self.model_quality_predictor:
                joblib.dump(self.model_quality_predictor, models_path / "quality_predictor.pkl")
            
            if self.model_cost_predictor:
                joblib.dump(self.model_cost_predictor, models_path / "cost_predictor.pkl")
            
            joblib.dump(self.feature_scaler, models_path / "feature_scaler.pkl")
            
            # Save learning metrics
            with open(models_path / "learning_metrics.json", "w") as f:
                metrics = self.learning_metrics.copy()
                if metrics["last_learning_update"]:
                    metrics["last_learning_update"] = metrics["last_learning_update"].isoformat()
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving ML models: {e}")
    
    def _load_ml_models(self):
        """Load trained ML models from disk"""
        models_path = self.data_path / "ml_models"
        
        if not models_path.exists():
            return
        
        try:
            quality_model_path = models_path / "quality_predictor.pkl"
            if quality_model_path.exists():
                self.model_quality_predictor = joblib.load(quality_model_path)
            
            cost_model_path = models_path / "cost_predictor.pkl"
            if cost_model_path.exists():
                self.model_cost_predictor = joblib.load(cost_model_path)
            
            scaler_path = models_path / "feature_scaler.pkl"
            if scaler_path.exists():
                self.feature_scaler = joblib.load(scaler_path)
            
            metrics_path = models_path / "learning_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, "r") as f:
                    loaded_metrics = json.load(f)
                    self.learning_metrics.update(loaded_metrics)
                    if self.learning_metrics["last_learning_update"]:
                        self.learning_metrics["last_learning_update"] = datetime.fromisoformat(
                            self.learning_metrics["last_learning_update"]
                        )
            
            logger.info("Loaded existing ML models and learning metrics")
            
        except Exception as e:
            logger.warning(f"Could not load existing ML models: {e}")
    
    async def get_learning_dashboard_data(self) -> Dict:
        """Get data for learning performance dashboard"""
        
        with sqlite3.connect(self.learning_db) as conn:
            # Model performance overview
            cursor = conn.execute("""
                SELECT selected_model, 
                       COUNT(*) as task_count,
                       AVG(actual_quality) as avg_quality,
                       AVG(user_satisfaction) as avg_satisfaction,
                       AVG(ABS(estimated_quality - actual_quality)) as avg_quality_error
                FROM task_outcomes 
                WHERE actual_quality IS NOT NULL
                GROUP BY selected_model
                ORDER BY avg_satisfaction DESC
            """)
            
            model_performance = [
                {
                    "model": row[0],
                    "task_count": row[1],
                    "avg_quality": row[2] or 0,
                    "avg_satisfaction": row[3] or 0,
                    "quality_prediction_error": row[4] or 0
                } for row in cursor.fetchall()
            ]
            
            # Learning progress over time
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as tasks_learned,
                       AVG(ABS(estimated_quality - actual_quality)) as daily_error
                FROM task_outcomes 
                WHERE actual_quality IS NOT NULL
                AND timestamp > date('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """)
            
            learning_progress = [
                {
                    "date": row[0],
                    "tasks_learned": row[1],
                    "prediction_error": row[2] or 0
                } for row in cursor.fetchall()
            ]
            
            # Capability learning insights
            cursor = conn.execute("""
                SELECT capability,
                       COUNT(*) as adjustments_made,
                       AVG(weight_adjustment) as avg_adjustment,
                       AVG(ABS(predicted_score - actual_performance)) as avg_error
                FROM capability_learning
                WHERE timestamp > date('now', '-30 days')
                GROUP BY capability
                ORDER BY avg_error DESC
            """)
            
            capability_insights = [
                {
                    "capability": row[0],
                    "adjustments_made": row[1],
                    "avg_weight_adjustment": row[2] or 0,
                    "prediction_error": row[3] or 0
                } for row in cursor.fetchall()
            ]
        
        return {
            "learning_summary": {
                **self.learning_metrics,
                "active_models": len(model_performance),
                "avg_prediction_accuracy": np.mean([mp["quality_prediction_error"] for mp in model_performance]) if model_performance else 0
            },
            "model_performance": model_performance,
            "learning_progress": learning_progress,
            "capability_insights": capability_insights,
            "capability_weight_adjustments": dict(self.capability_weight_adjustments)
        }
    
    async def suggest_model_improvements(self) -> List[Dict]:
        """Suggest improvements based on learning data"""
        suggestions = []
        
        # Analyze model performance gaps
        dashboard_data = await self.get_learning_dashboard_data()
        
        for model_data in dashboard_data["model_performance"]:
            model_name = model_data["model"]
            
            if model_data["quality_prediction_error"] > 2.0:
                suggestions.append({
                    "type": "quality_prediction",
                    "model": model_name,
                    "issue": "High quality prediction error",
                    "recommendation": f"Review capability scores for {model_name}",
                    "priority": "high"
                })
            
            if model_data["avg_satisfaction"] < 6.0:
                suggestions.append({
                    "type": "user_satisfaction",
                    "model": model_name,
                    "issue": "Low user satisfaction",
                    "recommendation": f"Consider adjusting {model_name} selection criteria",
                    "priority": "medium"
                })
        
        # Analyze capability adjustment patterns
        for capability_data in dashboard_data["capability_insights"]:
            if capability_data["prediction_error"] > 1.5:
                suggestions.append({
                    "type": "capability_accuracy",
                    "capability": capability_data["capability"],
                    "issue": "Poor capability prediction accuracy",
                    "recommendation": f"Review {capability_data['capability']} scoring methodology",
                    "priority": "medium"
                })
        
        return suggestions

# Global learner instance
performance_learner = ModelPerformanceLearner()

async def record_task_result(task_id: str, selected_model: str, task_type: str,
                           required_capabilities: List[str], estimated_cost: float,
                           actual_cost: float, estimated_quality: float,
                           actual_quality: float, user_satisfaction: float,
                           task_success: bool, user_feedback: str = "") -> None:
    """Convenience function to record task outcome for learning"""
    
    outcome = TaskOutcome(
        task_id=task_id,
        selected_model=selected_model,
        task_type=task_type,
        required_capabilities=required_capabilities,
        estimated_cost=estimated_cost,
        actual_cost=actual_cost,
        estimated_quality=estimated_quality,
        actual_quality=actual_quality,
        estimated_latency=1000,  # Default if not provided
        actual_latency=1000,     # Default if not provided
        user_satisfaction=user_satisfaction,
        task_success=task_success,
        completion_time=datetime.now(),
        user_feedback=user_feedback,
        context_metadata={}
    )
    
    await performance_learner.record_task_outcome(outcome)

async def get_learned_model_insights(model_name: str) -> ModelLearningInsights:
    """Get learning insights for a specific model"""
    return await performance_learner.get_model_learning_insights(model_name)

if __name__ == "__main__":
    # Example usage
    async def test_learning_system():
        # Simulate some task outcomes
        outcomes = [
            TaskOutcome(
                task_id="task_1",
                selected_model="claude-3-5-sonnet",
                task_type="content_creation",
                required_capabilities=["writing", "creativity"],
                estimated_cost=0.05,
                actual_cost=0.048,
                estimated_quality=8.5,
                actual_quality=9.0,
                estimated_latency=1800,
                actual_latency=1650,
                user_satisfaction=9.0,
                task_success=True,
                completion_time=datetime.now(),
                user_feedback="Excellent quality content",
                context_metadata={"domain": "marketing"}
            ),
            TaskOutcome(
                task_id="task_2",
                selected_model="gpt-4o-mini",
                task_type="data_analysis",
                required_capabilities=["analysis", "reasoning"],
                estimated_cost=0.02,
                actual_cost=0.025,
                estimated_quality=7.5,
                actual_quality=7.0,
                estimated_latency=1500,
                actual_latency=1800,
                user_satisfaction=6.5,
                task_success=True,
                completion_time=datetime.now(),
                user_feedback="Good but could be more detailed",
                context_metadata={"domain": "research"}
            )
        ]
        
        # Record outcomes
        for outcome in outcomes:
            await performance_learner.record_task_outcome(outcome)
        
        # Get insights
        insights = await performance_learner.get_model_learning_insights("claude-3-5-sonnet")
        print(f"Claude 3.5 Sonnet Insights:")
        print(f"  Quality Prediction Accuracy: {insights.quality_prediction_accuracy:.1%}")
        print(f"  User Satisfaction Trend: {insights.user_satisfaction_trend:.1f}/10")
        print(f"  Recommendations: {insights.recommended_adjustments}")
        
        # Get dashboard data
        dashboard = await performance_learner.get_learning_dashboard_data()
        print(f"\nLearning Dashboard Summary:")
        print(f"  Total Tasks Learned: {dashboard['learning_summary']['total_tasks_learned']}")
        print(f"  Prediction Accuracy: {dashboard['learning_summary']['prediction_accuracy']:.1%}")
        
        # Get improvement suggestions
        suggestions = await performance_learner.suggest_model_improvements()
        print(f"\nImprovement Suggestions: {len(suggestions)} suggestions generated")
    
    asyncio.run(test_learning_system())