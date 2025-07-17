"""
Feedback Collector Service - Handles feedback collection and processing
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import redis.asyncio as redis
from collections import defaultdict

from ..models.schemas import (
    Feedback,
    FeedbackRequest,
    FeedbackType,
    FeedbackSource,
    ModelType,
    LearningMetric,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class FeedbackCollector:
    """Service for collecting and processing user feedback."""
    
    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url
        self.feedback_weights = {
            FeedbackType.POSITIVE: 1.0,
            FeedbackType.NEGATIVE: -1.0,
            FeedbackType.NEUTRAL: 0.0,
            FeedbackType.EXPLICIT: 2.0,
            FeedbackType.IMPLICIT: 0.5
        }
        
    async def initialize(self):
        """Initialize the feedback collector."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Feedback collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize feedback collector: {e}")
            raise
    
    async def collect_feedback(self, feedback_request: FeedbackRequest) -> Feedback:
        """Process and store feedback."""
        try:
            # Validate constitutional hash
            if feedback_request.constitutional_hash != self.constitutional_hash:
                raise ValueError("Invalid constitutional hash")
            
            # Create feedback object
            feedback = Feedback(
                user_id=feedback_request.user_id,
                session_id=feedback_request.session_id,
                model_type=feedback_request.model_type,
                feedback_type=feedback_request.feedback_type,
                feedback_source=feedback_request.feedback_source,
                content=feedback_request.content,
                context=feedback_request.context,
                rating=feedback_request.rating,
                constitutional_hash=self.constitutional_hash
            )
            
            # Store in Redis for real-time processing
            await self._store_feedback_redis(feedback)
            
            # Process feedback for immediate insights
            await self._process_feedback_immediate(feedback)
            
            logger.info(f"Feedback collected: {feedback.id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            raise
    
    async def _store_feedback_redis(self, feedback: Feedback):
        """Store feedback in Redis for real-time processing."""
        try:
            if not self.redis_client:
                return
            
            # Store individual feedback
            feedback_key = f"feedback:{feedback.id}"
            await self.redis_client.hset(
                feedback_key,
                mapping={
                    "user_id": feedback.user_id,
                    "model_type": feedback.model_type.value,
                    "feedback_type": feedback.feedback_type.value,
                    "rating": str(feedback.rating) if feedback.rating else "",
                    "timestamp": feedback.timestamp.isoformat(),
                    "constitutional_hash": feedback.constitutional_hash
                }
            )
            
            # Set expiration (7 days)
            await self.redis_client.expire(feedback_key, 604800)
            
            # Add to model-specific feedback list
            model_feedback_key = f"model_feedback:{feedback.model_type.value}"
            await self.redis_client.lpush(model_feedback_key, feedback.id)
            await self.redis_client.ltrim(model_feedback_key, 0, 999)  # Keep last 1000
            
            # Update feedback counters
            counter_key = f"feedback_stats:{feedback.model_type.value}"
            await self.redis_client.hincrby(counter_key, "total_count", 1)
            await self.redis_client.hincrby(counter_key, f"type_{feedback.feedback_type.value}", 1)
            await self.redis_client.hincrby(counter_key, f"source_{feedback.feedback_source.value}", 1)
            
            if feedback.rating:
                await self.redis_client.hincrbyfloat(counter_key, "rating_sum", feedback.rating)
                await self.redis_client.hincrby(counter_key, "rating_count", 1)
            
            logger.info(f"Feedback stored in Redis: {feedback.id}")
            
        except Exception as e:
            logger.error(f"Failed to store feedback in Redis: {e}")
    
    async def _process_feedback_immediate(self, feedback: Feedback):
        """Process feedback for immediate insights and alerts."""
        try:
            # Calculate feedback weight
            weight = self.feedback_weights.get(feedback.feedback_type, 0.0)
            
            # Check for negative feedback patterns
            if feedback.feedback_type == FeedbackType.NEGATIVE and feedback.rating and feedback.rating < 2.0:
                await self._trigger_negative_feedback_alert(feedback)
            
            # Update real-time metrics
            await self._update_realtime_metrics(feedback, weight)
            
            # Check for constitutional compliance concerns
            if "constitutional" in feedback.content.lower() or "compliance" in feedback.content.lower():
                await self._trigger_constitutional_review(feedback)
            
            logger.info(f"Immediate feedback processing completed: {feedback.id}")
            
        except Exception as e:
            logger.error(f"Failed to process immediate feedback: {e}")
    
    async def _trigger_negative_feedback_alert(self, feedback: Feedback):
        """Trigger alert for negative feedback."""
        try:
            alert_key = f"alert:negative_feedback:{feedback.model_type.value}"
            alert_data = {
                "feedback_id": feedback.id,
                "user_id": feedback.user_id,
                "rating": feedback.rating,
                "content": feedback.content,
                "timestamp": feedback.timestamp.isoformat(),
                "constitutional_hash": feedback.constitutional_hash
            }
            
            await self.redis_client.lpush(alert_key, json.dumps(alert_data))
            await self.redis_client.ltrim(alert_key, 0, 99)  # Keep last 100 alerts
            
            logger.warning(f"Negative feedback alert triggered: {feedback.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger negative feedback alert: {e}")
    
    async def _trigger_constitutional_review(self, feedback: Feedback):
        """Trigger constitutional compliance review."""
        try:
            review_key = f"review:constitutional:{feedback.model_type.value}"
            review_data = {
                "feedback_id": feedback.id,
                "content": feedback.content,
                "context": feedback.context,
                "timestamp": feedback.timestamp.isoformat(),
                "constitutional_hash": feedback.constitutional_hash
            }
            
            await self.redis_client.lpush(review_key, json.dumps(review_data))
            await self.redis_client.ltrim(review_key, 0, 49)  # Keep last 50 reviews
            
            logger.info(f"Constitutional review triggered: {feedback.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger constitutional review: {e}")
    
    async def _update_realtime_metrics(self, feedback: Feedback, weight: float):
        """Update real-time metrics."""
        try:
            metrics_key = f"metrics:{feedback.model_type.value}"
            
            # Update weighted feedback score
            await self.redis_client.hincrbyfloat(metrics_key, "weighted_score", weight)
            
            # Update time-based metrics
            hour_key = f"metrics:hourly:{feedback.model_type.value}:{datetime.utcnow().hour}"
            await self.redis_client.hincrby(hour_key, "feedback_count", 1)
            await self.redis_client.hincrbyfloat(hour_key, "weighted_score", weight)
            await self.redis_client.expire(hour_key, 86400)  # 24 hours
            
            if feedback.rating:
                await self.redis_client.hincrbyfloat(metrics_key, "avg_rating", feedback.rating)
                await self.redis_client.hincrby(metrics_key, "rating_samples", 1)
            
            logger.info(f"Real-time metrics updated for {feedback.model_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {e}")
    
    async def get_feedback_analytics(self, model_type: ModelType, days: int = 7) -> Dict[str, Any]:
        """Get feedback analytics for a model."""
        try:
            stats_key = f"feedback_stats:{model_type.value}"
            
            # Get basic stats
            stats = await self.redis_client.hgetall(stats_key)
            
            # Calculate average rating
            rating_sum = float(stats.get("rating_sum", 0))
            rating_count = int(stats.get("rating_count", 0))
            avg_rating = rating_sum / rating_count if rating_count > 0 else 0.0
            
            # Get recent feedback trends
            trends = await self._get_feedback_trends(model_type, days)
            
            analytics = {
                "total_feedback": int(stats.get("total_count", 0)),
                "average_rating": avg_rating,
                "feedback_by_type": {
                    "positive": int(stats.get("type_positive", 0)),
                    "negative": int(stats.get("type_negative", 0)),
                    "neutral": int(stats.get("type_neutral", 0)),
                    "explicit": int(stats.get("type_explicit", 0)),
                    "implicit": int(stats.get("type_implicit", 0))
                },
                "feedback_by_source": {
                    "user_explicit": int(stats.get("source_user_explicit", 0)),
                    "user_implicit": int(stats.get("source_user_implicit", 0)),
                    "system_metrics": int(stats.get("source_system_metrics", 0)),
                    "human_review": int(stats.get("source_human_review", 0)),
                    "automated_evaluation": int(stats.get("source_automated_evaluation", 0))
                },
                "trends": trends,
                "constitutional_hash": self.constitutional_hash
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get feedback analytics: {e}")
            return {}
    
    async def _get_feedback_trends(self, model_type: ModelType, days: int) -> Dict[str, List[float]]:
        """Get feedback trends over time."""
        try:
            trends = {
                "daily_counts": [],
                "daily_ratings": [],
                "hourly_counts": []
            }
            
            # Get hourly trends for last 24 hours
            for hour in range(24):
                hour_key = f"metrics:hourly:{model_type.value}:{hour}"
                count = await self.redis_client.hget(hour_key, "feedback_count")
                trends["hourly_counts"].append(int(count) if count else 0)
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get feedback trends: {e}")
            return {}
    
    async def get_model_recommendations(self, model_type: ModelType) -> Dict[str, Any]:
        """Get model improvement recommendations based on feedback."""
        try:
            analytics = await self.get_feedback_analytics(model_type)
            
            recommendations = {
                "retrain_recommended": False,
                "priority_areas": [],
                "constitutional_concerns": [],
                "performance_insights": [],
                "constitutional_hash": self.constitutional_hash
            }
            
            # Analyze feedback patterns
            total_feedback = analytics.get("total_feedback", 0)
            avg_rating = analytics.get("average_rating", 0.0)
            negative_count = analytics.get("feedback_by_type", {}).get("negative", 0)
            
            # Retrain recommendation
            if total_feedback > 100 and (avg_rating < 3.0 or negative_count > total_feedback * 0.3):
                recommendations["retrain_recommended"] = True
                recommendations["priority_areas"].append("Overall model performance")
            
            # Constitutional compliance check
            constitutional_reviews = await self.redis_client.llen(f"review:constitutional:{model_type.value}")
            if constitutional_reviews > 5:
                recommendations["constitutional_concerns"].append("Multiple constitutional compliance issues reported")
            
            # Performance insights
            if avg_rating < 2.0:
                recommendations["performance_insights"].append("Critical: User satisfaction extremely low")
            elif avg_rating < 3.0:
                recommendations["performance_insights"].append("Warning: User satisfaction below average")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get model recommendations: {e}")
            return {}
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old feedback data."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_old)
            
            # Clean up old feedback keys
            pattern = "feedback:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                # Check timestamp and remove if too old
                timestamp_str = await self.redis_client.hget(key, "timestamp")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp < cutoff_time:
                        await self.redis_client.delete(key)
            
            logger.info(f"Cleaned up feedback data older than {days_old} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def health_check(self) -> bool:
        """Check service health."""
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.ping()
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False