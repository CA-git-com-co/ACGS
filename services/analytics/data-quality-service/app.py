#!/usr/bin/env python3
"""
ACGS Data Quality Microservice

Focused microservice for data quality assessment and monitoring:
- RESTful API for quality assessments
- Real-time quality monitoring
- Event-driven quality alerts
- Constitutional compliance validation
- Integration with NATS message broker

Constitutional Hash: cdd01ef066bc6cf2
Port: 8010
"""

import asyncio
import logging
import json
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add core modules to path
sys.path.append("../../core/acgs-pgp-v8")
from event_driven_data_quality import EventDrivenDataQualityFramework, QualityEvent
from nats_event_broker import NATSEventBroker, ACGSEvent

logger = logging.getLogger(__name__)


# Pydantic models for API
class QualityAssessmentRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data records to assess")
    service_id: str = Field(default="unknown", description="Source service ID")
    target_column: Optional[str] = Field(
        None, description="Target column for classification analysis"
    )
    timestamp_column: Optional[str] = Field(None, description="Timestamp column name")
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for validation"
    )


class QualityAssessmentResponse(BaseModel):
    assessment_id: str
    overall_score: float
    missing_value_rate: float
    outlier_rate: float
    freshness_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    constitutional_hash: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    constitutional_hash: str
    timestamp: str


class DataQualityMicroservice:
    """Data Quality Microservice implementation."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.service_name = "data-quality-service"
        self.version = "v8.0.0"
        self.port = 8010

        # Initialize FastAPI app
        self.app = FastAPI(
            title="ACGS Data Quality Service",
            description="Microservice for data quality assessment and monitoring",
            version=self.version,
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize components
        self.quality_framework = EventDrivenDataQualityFramework()
        self.event_broker = NATSEventBroker()

        # Service metrics
        self.metrics = {
            "assessments_completed": 0,
            "alerts_generated": 0,
            "average_processing_time_ms": 0,
            "uptime_start": datetime.now().isoformat(),
        }

        # Setup routes
        self._setup_routes()

        logger.info(f"Data Quality Microservice initialized on port {self.port}")

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                service=self.service_name,
                version=self.version,
                constitutional_hash=self.constitutional_hash,
                timestamp=datetime.now().isoformat(),
            )

        @self.app.get("/metrics")
        async def get_metrics():
            """Get service metrics."""
            return {
                **self.metrics,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/assess", response_model=QualityAssessmentResponse)
        async def assess_quality(
            request: QualityAssessmentRequest, background_tasks: BackgroundTasks
        ):
            """Assess data quality for provided dataset."""

            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional hash mismatch"
                )

            start_time = datetime.now()

            try:
                # Convert request data to DataFrame
                df = pd.DataFrame(request.data)

                if df.empty:
                    raise HTTPException(
                        status_code=400, detail="Empty dataset provided"
                    )

                # Perform quality assessment
                metrics = await self.quality_framework.assess_quality_async(
                    df=df,
                    service_id=request.service_id,
                    target_column=request.target_column,
                    timestamp_column=request.timestamp_column,
                )

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                # Update metrics
                self.metrics["assessments_completed"] += 1
                self.metrics["average_processing_time_ms"] = (
                    self.metrics["average_processing_time_ms"]
                    * (self.metrics["assessments_completed"] - 1)
                    + processing_time
                ) / self.metrics["assessments_completed"]

                # Generate recommendations
                recommendations = self._generate_recommendations(metrics)

                # Create response
                assessment_id = f"qa-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                response = QualityAssessmentResponse(
                    assessment_id=assessment_id,
                    overall_score=metrics.overall_score,
                    missing_value_rate=metrics.missing_value_rate,
                    outlier_rate=metrics.outlier_rate,
                    freshness_score=metrics.freshness_score,
                    violations=self._extract_violations(metrics),
                    recommendations=recommendations,
                    constitutional_hash=self.constitutional_hash,
                    timestamp=datetime.now().isoformat(),
                )

                # Publish quality event in background
                background_tasks.add_task(
                    self._publish_quality_event,
                    assessment_id,
                    request.service_id,
                    metrics,
                )

                logger.info(
                    f"✅ Quality assessment completed: {assessment_id} "
                    f"(score: {metrics.overall_score:.3f}, "
                    f"processing: {processing_time:.1f}ms)"
                )

                return response

            except Exception as e:
                logger.error(f"❌ Quality assessment failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Quality assessment failed: {str(e)}"
                )

        @self.app.post("/monitor/start")
        async def start_monitoring(service_id: str, monitoring_interval: int = 60):
            """Start continuous quality monitoring for a service."""

            # Start monitoring task
            asyncio.create_task(
                self._continuous_monitoring(service_id, monitoring_interval)
            )

            return {
                "message": f"Started monitoring for {service_id}",
                "interval_seconds": monitoring_interval,
                "constitutional_hash": self.constitutional_hash,
            }

        @self.app.get("/assessments/recent")
        async def get_recent_assessments(limit: int = 10):
            """Get recent quality assessments."""

            # In production, would query database
            return {
                "assessments": [],  # Placeholder
                "count": 0,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_recommendations(self, metrics) -> List[str]:
        """Generate quality improvement recommendations."""

        recommendations = []

        if metrics.missing_value_rate > 0.1:
            recommendations.append(
                f"High missing value rate ({metrics.missing_value_rate:.1%}). "
                "Consider data imputation or collection improvements."
            )

        if metrics.outlier_rate > 0.05:
            recommendations.append(
                f"High outlier rate ({metrics.outlier_rate:.1%}). "
                "Review data collection process and consider outlier handling."
            )

        if metrics.freshness_score < 0.8:
            recommendations.append(
                f"Low data freshness score ({metrics.freshness_score:.3f}). "
                "Consider more frequent data updates."
            )

        if metrics.overall_score < 0.8:
            recommendations.append(
                "Overall quality below target. Implement comprehensive data quality program."
            )

        return recommendations

    def _extract_violations(self, metrics) -> List[Dict[str, Any]]:
        """Extract quality violations from metrics."""

        violations = []

        if metrics.missing_value_rate > 0.1:
            violations.append(
                {
                    "type": "missing_values",
                    "severity": (
                        "HIGH" if metrics.missing_value_rate > 0.2 else "MEDIUM"
                    ),
                    "value": metrics.missing_value_rate,
                    "threshold": 0.1,
                    "description": "Missing value rate exceeds threshold",
                }
            )

        if metrics.outlier_rate > 0.05:
            violations.append(
                {
                    "type": "outliers",
                    "severity": "HIGH" if metrics.outlier_rate > 0.1 else "MEDIUM",
                    "value": metrics.outlier_rate,
                    "threshold": 0.05,
                    "description": "Outlier rate exceeds threshold",
                }
            )

        return violations

    async def _publish_quality_event(
        self, assessment_id: str, service_id: str, metrics
    ):
        """Publish quality assessment event."""

        try:
            # Create quality event
            event = ACGSEvent(
                event_type="quality_assessment_completed",
                timestamp=datetime.now().isoformat(),
                constitutional_hash=self.constitutional_hash,
                source_service=self.service_name,
                target_service=service_id,
                event_id=assessment_id,
                payload={
                    "overall_score": metrics.overall_score,
                    "missing_value_rate": metrics.missing_value_rate,
                    "outlier_rate": metrics.outlier_rate,
                    "freshness_score": metrics.freshness_score,
                },
                priority="HIGH" if metrics.overall_score < 0.8 else "NORMAL",
            )

            # Publish event
            await self.event_broker.publish_event("acgs.quality.assessment", event)

        except Exception as e:
            logger.error(f"❌ Failed to publish quality event: {e}")

    async def _continuous_monitoring(self, service_id: str, interval_seconds: int):
        """Continuous quality monitoring for a service."""

        logger.info(f"🔍 Starting continuous monitoring for {service_id}")

        while True:
            try:
                # In production, would fetch data from service
                # For demo, generate sample data
                sample_data = self._generate_sample_data()

                # Assess quality
                df = pd.DataFrame(sample_data)
                metrics = await self.quality_framework.assess_quality_async(
                    df=df, service_id=service_id
                )

                # Check for alerts
                if metrics.overall_score < 0.8:
                    self.metrics["alerts_generated"] += 1
                    logger.warning(
                        f"🚨 Quality alert for {service_id}: {metrics.overall_score:.3f}"
                    )

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"❌ Error in continuous monitoring: {e}")
                await asyncio.sleep(5)

    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample data for monitoring demo."""

        data = []
        for i in range(100):
            record = {
                "timestamp": datetime.now().isoformat(),
                "feature1": np.random.normal(0, 1),
                "feature2": np.random.normal(0, 1),
                "response_time_ms": np.random.lognormal(6, 0.5),
                "quality_score": np.random.beta(8, 2),
            }

            # Introduce some missing values
            if np.random.random() < 0.05:
                record["feature1"] = None

            data.append(record)

        return data

    async def startup(self):
        """Startup tasks for the microservice."""

        # Connect to event broker
        await self.event_broker.connect()
        await self.quality_framework.connect_to_nats()

        logger.info(f"✅ Data Quality Microservice started on port {self.port}")

    async def shutdown(self):
        """Shutdown tasks for the microservice."""

        # Disconnect from event broker
        await self.event_broker.disconnect()
        await self.quality_framework.disconnect_from_nats()

        logger.info("✅ Data Quality Microservice shutdown completed")


# Global service instance
service = DataQualityMicroservice()


# FastAPI event handlers
@service.app.on_event("startup")
async def startup_event():
    await service.startup()


@service.app.on_event("shutdown")
async def shutdown_event():
    await service.shutdown()


# Main entry point
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the service
    uvicorn.run(
        "app:service.app",
        host="0.0.0.0",
        port=service.port,
        reload=False,
        log_level="info",
    )
