#!/usr/bin/env python3
"""
ACGS-1 Advanced Analytics & Reporting Engine
Constitutional governance analytics with predictive insights
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import asyncpg
import numpy as np
import plotly.graph_objects as go
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Query
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GovernanceMetrics:
    """Governance performance metrics"""

    tenant_id: str
    period_start: datetime
    period_end: datetime
    total_policies: int
    active_policies: int
    policy_approval_rate: float
    avg_policy_creation_time_hours: float
    constitutional_compliance_score: float
    governance_participation_rate: float
    policy_effectiveness_score: float
    democratic_index: float
    transparency_score: float


@dataclass
class PolicyAnalytics:
    """Policy-specific analytics"""

    policy_id: str
    title: str
    category: str
    creation_date: datetime
    approval_date: datetime | None
    effectiveness_score: float
    compliance_score: float
    stakeholder_satisfaction: float
    implementation_success_rate: float
    amendment_count: int
    usage_frequency: int


@dataclass
class ConstitutionalTrend:
    """Constitutional compliance trends"""

    date: datetime
    compliance_score: float
    violation_count: int
    amendment_proposals: int
    council_activity_level: float
    democratic_participation: float


class GovernanceAnalyticsEngine:
    """Advanced analytics engine for constitutional governance"""

    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.models: dict[str, Any] = {}
        self.scalers: dict[str, StandardScaler] = {}

    async def initialize(self):
        """Initialize analytics engine"""
        self.db_pool = await asyncpg.create_pool(self.database_url)
        self.redis_client = redis.from_url(self.redis_url)
        await self._initialize_ml_models()

    async def _initialize_ml_models(self):
        """Initialize machine learning models"""
        # Policy effectiveness prediction model
        self.models["policy_effectiveness"] = RandomForestRegressor(
            n_estimators=100, random_state=42
        )

        # Constitutional compliance prediction model
        self.models["compliance_prediction"] = RandomForestRegressor(
            n_estimators=100, random_state=42
        )

        # Anomaly detection model
        self.models["anomaly_detection"] = IsolationForest(contamination=0.1, random_state=42)

        # Initialize scalers
        self.scalers["policy_features"] = StandardScaler()
        self.scalers["compliance_features"] = StandardScaler()

        logger.info("ML models initialized")

    async def collect_governance_metrics(self, tenant_id: str, days: int = 30) -> GovernanceMetrics:
        """Collect comprehensive governance metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        async with self.db_pool.acquire() as conn:
            # Total and active policies
            policy_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_policies,
                    COUNT(*) FILTER (WHERE status = 'active') as active_policies,
                    AVG(CASE WHEN status = 'approved' THEN 1.0 ELSE 0.0 END) as approval_rate,
                    AVG(EXTRACT(EPOCH FROM (approved_at - created_at))/3600) as avg_creation_time
                FROM policies
                WHERE tenant_id = $1 AND created_at >= $2
            """,
                tenant_id,
                start_date,
            )

            # Constitutional compliance
            compliance_stats = await conn.fetchrow(
                """
                SELECT
                    AVG(compliance_score) as avg_compliance,
                    COUNT(*) FILTER (WHERE compliance_score < 0.8) as violations
                FROM governance_actions
                WHERE tenant_id = $1 AND created_at >= $2
            """,
                tenant_id,
                start_date,
            )

            # Participation metrics
            participation_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(*) as total_actions
                FROM governance_actions
                WHERE tenant_id = $1 AND created_at >= $2
            """,
                tenant_id,
                start_date,
            )

            # Calculate derived metrics
            total_users = await conn.fetchval(
                """
                SELECT COUNT(*) FROM tenant_users WHERE tenant_id = $1
            """,
                tenant_id,
            )

            participation_rate = (participation_stats["active_users"] / max(total_users, 1)) * 100

            # Policy effectiveness (mock calculation - would use real implementation data)
            effectiveness_score = min(
                (policy_stats["approval_rate"] or 0) * 0.4
                + (compliance_stats["avg_compliance"] or 0) * 0.6,
                1.0,
            )

            # Democratic index (composite score)
            democratic_index = min(
                participation_rate * 0.01 * 0.3
                + (policy_stats["approval_rate"] or 0) * 0.4
                + (compliance_stats["avg_compliance"] or 0) * 0.3,
                1.0,
            )

            return GovernanceMetrics(
                tenant_id=tenant_id,
                period_start=start_date,
                period_end=end_date,
                total_policies=policy_stats["total_policies"] or 0,
                active_policies=policy_stats["active_policies"] or 0,
                policy_approval_rate=policy_stats["approval_rate"] or 0.0,
                avg_policy_creation_time_hours=policy_stats["avg_creation_time"] or 0.0,
                constitutional_compliance_score=compliance_stats["avg_compliance"] or 0.0,
                governance_participation_rate=participation_rate,
                policy_effectiveness_score=effectiveness_score,
                democratic_index=democratic_index,
                transparency_score=0.85,  # Would calculate from audit logs
            )

    async def analyze_policy_effectiveness(self, tenant_id: str, policy_id: str) -> PolicyAnalytics:
        """Analyze individual policy effectiveness"""
        async with self.db_pool.acquire() as conn:
            policy_data = await conn.fetchrow(
                """
                SELECT
                    p.*,
                    AVG(ga.compliance_score) as avg_compliance,
                    COUNT(ga.action_id) as usage_count,
                    COUNT(pa.amendment_id) as amendment_count
                FROM policies p
                LEFT JOIN governance_actions ga ON p.policy_id = ga.policy_id
                LEFT JOIN policy_amendments pa ON p.policy_id = pa.policy_id
                WHERE p.tenant_id = $1 AND p.policy_id = $2
                GROUP BY p.policy_id
            """,
                tenant_id,
                policy_id,
            )

            if not policy_data:
                raise HTTPException(status_code=404, detail="Policy not found")

            # Calculate effectiveness metrics
            effectiveness_score = min(
                (policy_data["avg_compliance"] or 0) * 0.6
                + min(policy_data["usage_count"] / 100, 1.0) * 0.4,
                1.0,
            )

            # Mock stakeholder satisfaction (would come from surveys/feedback)
            stakeholder_satisfaction = 0.75 + (effectiveness_score * 0.25)

            return PolicyAnalytics(
                policy_id=policy_data["policy_id"],
                title=policy_data["title"],
                category=policy_data["category"] or "general",
                creation_date=policy_data["created_at"],
                approval_date=policy_data["approved_at"],
                effectiveness_score=effectiveness_score,
                compliance_score=policy_data["avg_compliance"] or 0.0,
                stakeholder_satisfaction=stakeholder_satisfaction,
                implementation_success_rate=0.85,  # Would calculate from implementation data
                amendment_count=policy_data["amendment_count"] or 0,
                usage_frequency=policy_data["usage_count"] or 0,
            )

    async def predict_policy_success(self, policy_features: dict[str, Any]) -> dict[str, float]:
        """Predict policy success probability using ML"""
        # Extract features for prediction
        features = np.array(
            [
                [
                    policy_features.get("complexity_score", 0.5),
                    policy_features.get("stakeholder_count", 10),
                    policy_features.get("constitutional_alignment", 0.8),
                    policy_features.get("resource_requirements", 0.3),
                    policy_features.get("implementation_difficulty", 0.4),
                ]
            ]
        )

        # Scale features
        if hasattr(self.scalers["policy_features"], "mean_"):
            features_scaled = self.scalers["policy_features"].transform(features)
        else:
            features_scaled = features  # Use unscaled if not trained

        # Predict (mock prediction if model not trained)
        try:
            success_probability = self.models["policy_effectiveness"].predict(features_scaled)[0]
        except:
            # Mock prediction based on features
            success_probability = (
                policy_features.get("constitutional_alignment", 0.8) * 0.4
                + (1 - policy_features.get("complexity_score", 0.5)) * 0.3
                + (1 - policy_features.get("implementation_difficulty", 0.4)) * 0.3
            )

        return {
            "success_probability": min(max(success_probability, 0.0), 1.0),
            "confidence_interval": [
                max(success_probability - 0.1, 0.0),
                min(success_probability + 0.1, 1.0),
            ],
            "key_factors": [
                "constitutional_alignment",
                "implementation_difficulty",
                "stakeholder_support",
            ],
        }

    async def detect_governance_anomalies(
        self, tenant_id: str, days: int = 7
    ) -> list[dict[str, Any]]:
        """Detect anomalies in governance patterns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        async with self.db_pool.acquire() as conn:
            # Get daily governance metrics
            daily_metrics = await conn.fetch(
                """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as action_count,
                    AVG(compliance_score) as avg_compliance,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT policy_id) as policies_affected
                FROM governance_actions
                WHERE tenant_id = $1 AND created_at >= $2
                GROUP BY DATE(created_at)
                ORDER BY date
            """,
                tenant_id,
                start_date,
            )

            if len(daily_metrics) < 3:
                return []  # Need at least 3 days for anomaly detection

            # Prepare features for anomaly detection
            features = np.array(
                [
                    [
                        row["action_count"],
                        row["avg_compliance"] or 0,
                        row["unique_users"],
                        row["policies_affected"],
                    ]
                    for row in daily_metrics
                ]
            )

            # Detect anomalies
            try:
                anomaly_scores = self.models["anomaly_detection"].decision_function(features)
                anomalies = self.models["anomaly_detection"].predict(features)

                anomaly_results = []
                for _i, (row, score, is_anomaly) in enumerate(
                    zip(daily_metrics, anomaly_scores, anomalies, strict=False)
                ):
                    if is_anomaly == -1:  # Anomaly detected
                        anomaly_results.append(
                            {
                                "date": row["date"].isoformat(),
                                "anomaly_score": float(score),
                                "metrics": {
                                    "action_count": row["action_count"],
                                    "avg_compliance": row["avg_compliance"],
                                    "unique_users": row["unique_users"],
                                    "policies_affected": row["policies_affected"],
                                },
                                "severity": "high" if score < -0.5 else "medium",
                                "description": self._generate_anomaly_description(
                                    row, daily_metrics
                                ),
                            }
                        )

                return anomaly_results

            except Exception as e:
                logger.warning(f"Anomaly detection failed: {e}")
                return []

    def _generate_anomaly_description(self, anomaly_row: dict, all_metrics: list[dict]) -> str:
        """Generate human-readable anomaly description"""
        avg_actions = np.mean([row["action_count"] for row in all_metrics])
        avg_compliance = np.mean([row["avg_compliance"] or 0 for row in all_metrics])

        descriptions = []

        if anomaly_row["action_count"] > avg_actions * 2:
            descriptions.append("Unusually high governance activity")
        elif anomaly_row["action_count"] < avg_actions * 0.5:
            descriptions.append("Unusually low governance activity")

        if (anomaly_row["avg_compliance"] or 0) < avg_compliance * 0.8:
            descriptions.append("Lower than normal constitutional compliance")

        return "; ".join(descriptions) if descriptions else "Unusual governance pattern detected"

    async def generate_constitutional_trend_analysis(
        self, tenant_id: str, days: int = 90
    ) -> list[ConstitutionalTrend]:
        """Generate constitutional compliance trend analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        async with self.db_pool.acquire() as conn:
            trends = await conn.fetch(
                """
                SELECT
                    DATE(created_at) as date,
                    AVG(compliance_score) as avg_compliance,
                    COUNT(*) FILTER (WHERE compliance_score < 0.8) as violations,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(*) as total_actions
                FROM governance_actions
                WHERE tenant_id = $1 AND created_at >= $2
                GROUP BY DATE(created_at)
                ORDER BY date
            """,
                tenant_id,
                start_date,
            )

            # Get total users for participation calculation
            total_users = await conn.fetchval(
                """
                SELECT COUNT(*) FROM tenant_users WHERE tenant_id = $1
            """,
                tenant_id,
            )

            trend_data = []
            for row in trends:
                participation = (row["active_users"] / max(total_users, 1)) * 100

                trend_data.append(
                    ConstitutionalTrend(
                        date=row["date"],
                        compliance_score=row["avg_compliance"] or 0.0,
                        violation_count=row["violations"] or 0,
                        amendment_proposals=0,  # Would get from amendments table
                        council_activity_level=min(row["total_actions"] / 100, 1.0),
                        democratic_participation=participation,
                    )
                )

            return trend_data

    async def create_governance_dashboard_data(self, tenant_id: str) -> dict[str, Any]:
        """Create comprehensive dashboard data"""
        # Collect metrics
        metrics = await self.collect_governance_metrics(tenant_id)
        trends = await self.generate_constitutional_trend_analysis(tenant_id, days=30)
        anomalies = await self.detect_governance_anomalies(tenant_id)

        # Create visualizations
        trend_chart = self._create_trend_chart(trends)
        compliance_chart = self._create_compliance_chart(trends)

        return {
            "summary_metrics": asdict(metrics),
            "trends": [asdict(trend) for trend in trends],
            "anomalies": anomalies,
            "charts": {
                "constitutional_trends": trend_chart,
                "compliance_overview": compliance_chart,
            },
            "recommendations": await self._generate_recommendations(metrics, trends, anomalies),
            "generated_at": datetime.now().isoformat(),
        }

    def _create_trend_chart(self, trends: list[ConstitutionalTrend]) -> dict:
        """Create constitutional trend chart"""
        dates = [trend.date for trend in trends]
        compliance_scores = [trend.compliance_score for trend in trends]
        participation = [trend.democratic_participation for trend in trends]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=compliance_scores,
                mode="lines+markers",
                name="Constitutional Compliance",
                line={"color": "blue"},
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=participation,
                mode="lines+markers",
                name="Democratic Participation",
                yaxis="y2",
                line={"color": "green"},
            )
        )

        fig.update_layout(
            title="Constitutional Governance Trends",
            xaxis_title="Date",
            yaxis_title="Compliance Score",
            yaxis2={"title": "Participation %", "overlaying": "y", "side": "right"},
        )

        return json.loads(fig.to_json())

    def _create_compliance_chart(self, trends: list[ConstitutionalTrend]) -> dict:
        """Create compliance overview chart"""
        compliance_scores = [trend.compliance_score for trend in trends]

        # Create compliance distribution
        excellent = sum(1 for score in compliance_scores if score >= 0.9)
        good = sum(1 for score in compliance_scores if 0.8 <= score < 0.9)
        fair = sum(1 for score in compliance_scores if 0.7 <= score < 0.8)
        poor = sum(1 for score in compliance_scores if score < 0.7)

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Excellent (≥90%)",
                        "Good (80-89%)",
                        "Fair (70-79%)",
                        "Poor (<70%)",
                    ],
                    values=[excellent, good, fair, poor],
                    hole=0.3,
                )
            ]
        )

        fig.update_layout(title="Constitutional Compliance Distribution")

        return json.loads(fig.to_json())

    async def _generate_recommendations(
        self,
        metrics: GovernanceMetrics,
        trends: list[ConstitutionalTrend],
        anomalies: list[dict],
    ) -> list[dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Compliance recommendations
        if metrics.constitutional_compliance_score < 0.8:
            recommendations.append(
                {
                    "type": "compliance",
                    "priority": "high",
                    "title": "Improve Constitutional Compliance",
                    "description": f"Current compliance score ({metrics.constitutional_compliance_score:.1%}) is below target. Review policy creation processes and provide additional constitutional training.",
                    "action": "Review and update policy creation guidelines",
                }
            )

        # Participation recommendations
        if metrics.governance_participation_rate < 30:
            recommendations.append(
                {
                    "type": "participation",
                    "priority": "medium",
                    "title": "Increase Democratic Participation",
                    "description": f"Only {metrics.governance_participation_rate:.1f}% of users are actively participating in governance. Consider engagement initiatives.",
                    "action": "Launch governance engagement campaign",
                }
            )

        # Anomaly recommendations
        if anomalies:
            recommendations.append(
                {
                    "type": "anomaly",
                    "priority": "high",
                    "title": "Address Governance Anomalies",
                    "description": f"{len(anomalies)} governance anomalies detected in recent activity. Investigate unusual patterns.",
                    "action": "Review anomalous governance activities",
                }
            )

        return recommendations


class AnalyticsAPI:
    """FastAPI application for analytics endpoints"""

    def __init__(self, analytics_engine: GovernanceAnalyticsEngine):
        self.app = FastAPI(
            title="ACGS-1 Analytics API",
            version="3.0.0",
            description="Advanced analytics and reporting for constitutional governance",
        )
        self.analytics = analytics_engine
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "analytics_api",
                "version": "3.0.0",
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/analytics/governance-metrics/{tenant_id}")
        async def get_governance_metrics(tenant_id: str, days: int = Query(30, ge=1, le=365)):
            """Get comprehensive governance metrics"""
            metrics = await self.analytics.collect_governance_metrics(tenant_id, days)
            return asdict(metrics)

        @self.app.get("/analytics/policy/{tenant_id}/{policy_id}")
        async def get_policy_analytics(tenant_id: str, policy_id: str):
            """Get detailed policy analytics"""
            analytics = await self.analytics.analyze_policy_effectiveness(tenant_id, policy_id)
            return asdict(analytics)

        @self.app.post("/analytics/predict-policy-success")
        async def predict_policy_success(policy_features: dict[str, Any]):
            """Predict policy success probability"""
            prediction = await self.analytics.predict_policy_success(policy_features)
            return prediction

        @self.app.get("/analytics/anomalies/{tenant_id}")
        async def get_governance_anomalies(tenant_id: str, days: int = Query(7, ge=1, le=30)):
            """Get governance anomalies"""
            anomalies = await self.analytics.detect_governance_anomalies(tenant_id, days)
            return {"anomalies": anomalies}

        @self.app.get("/analytics/trends/{tenant_id}")
        async def get_constitutional_trends(tenant_id: str, days: int = Query(90, ge=7, le=365)):
            """Get constitutional compliance trends"""
            trends = await self.analytics.generate_constitutional_trend_analysis(tenant_id, days)
            return {"trends": [asdict(trend) for trend in trends]}

        @self.app.get("/analytics/dashboard/{tenant_id}")
        async def get_dashboard_data(tenant_id: str):
            """Get comprehensive dashboard data"""
            dashboard = await self.analytics.create_governance_dashboard_data(tenant_id)
            return dashboard


# Global analytics engine and API
analytics_engine = GovernanceAnalyticsEngine(
    database_url=os.getenv(
        "DATABASE_URL", "postgresql://acgs_user:password@localhost:5432/acgs_pgp_db"
    ),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

analytics_api = AnalyticsAPI(analytics_engine)
app = analytics_api.app


@app.on_event("startup")
async def startup_event():
    await analytics_engine.initialize()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8007)
