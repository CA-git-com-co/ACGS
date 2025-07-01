#!/usr/bin/env python3
"""
ACGS Drift Detection Microservice

Focused microservice for model drift detection and monitoring:
- RESTful API for drift analysis
- Real-time drift monitoring
- Automated retraining triggers
- Constitutional compliance validation
- Integration with NATS message broker

Constitutional Hash: cdd01ef066bc6cf2
Port: 8011
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add core modules to path
sys.path.append("../../core/acgs-pgp-v8")
from event_driven_drift_detection import EventDrivenDriftDetector
from nats_event_broker import ACGSEvent, NATSEventBroker

logger = logging.getLogger(__name__)


# Pydantic models for API
class DriftDetectionRequest(BaseModel):
    reference_data: list[dict[str, Any]] = Field(..., description="Reference dataset")
    current_data: list[dict[str, Any]] = Field(
        ..., description="Current dataset to compare"
    )
    model_id: str = Field(..., description="Model identifier")
    service_id: str = Field(default="unknown", description="Source service ID")
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for validation"
    )


class DriftDetectionResponse(BaseModel):
    detection_id: str
    model_id: str
    drift_detected: bool
    retraining_required: bool
    features_with_ks_drift: list[str]
    features_with_psi_drift: list[str]
    drift_severity: str
    recommendations: list[str]
    constitutional_hash: str
    timestamp: str


class ModelRegistrationRequest(BaseModel):
    model_id: str = Field(..., description="Model identifier")
    reference_data: list[dict[str, Any]] = Field(..., description="Reference dataset")
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for validation"
    )


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    constitutional_hash: str
    timestamp: str


class DriftDetectionMicroservice:
    """Drift Detection Microservice implementation."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.service_name = "drift-detection-service"
        self.version = "v8.0.0"
        self.port = 8011

        # Initialize FastAPI app
        self.app = FastAPI(
            title="ACGS Drift Detection Service",
            description="Microservice for model drift detection and monitoring",
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
        self.drift_detector = EventDrivenDriftDetector()
        self.event_broker = NATSEventBroker()

        # Service metrics
        self.metrics = {
            "detections_completed": 0,
            "drift_alerts_generated": 0,
            "retraining_triggers": 0,
            "models_monitored": 0,
            "average_processing_time_ms": 0,
            "uptime_start": datetime.now().isoformat(),
        }

        # Setup routes
        self._setup_routes()

        logger.info(f"Drift Detection Microservice initialized on port {self.port}")

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

        @self.app.post("/models/register")
        async def register_model(request: ModelRegistrationRequest):
            """Register a model with reference dataset for drift monitoring."""

            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional hash mismatch"
                )

            try:
                # Convert reference data to DataFrame
                reference_df = pd.DataFrame(request.reference_data)

                if reference_df.empty:
                    raise HTTPException(
                        status_code=400, detail="Empty reference dataset provided"
                    )

                # Register reference dataset
                self.drift_detector.register_reference_dataset(
                    request.model_id, reference_df
                )

                self.metrics["models_monitored"] += 1

                logger.info(
                    f"✅ Registered model: {request.model_id} "
                    f"({len(reference_df)} reference records)"
                )

                return {
                    "message": f"Model {request.model_id} registered successfully",
                    "reference_records": len(reference_df),
                    "constitutional_hash": self.constitutional_hash,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"❌ Model registration failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Model registration failed: {e!s}"
                )

        @self.app.post("/detect", response_model=DriftDetectionResponse)
        async def detect_drift(
            request: DriftDetectionRequest, background_tasks: BackgroundTasks
        ):
            """Detect drift between reference and current datasets."""

            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional hash mismatch"
                )

            start_time = datetime.now()

            try:
                # Convert data to DataFrames
                reference_df = pd.DataFrame(request.reference_data)
                current_df = pd.DataFrame(request.current_data)

                if reference_df.empty or current_df.empty:
                    raise HTTPException(
                        status_code=400, detail="Empty datasets provided"
                    )

                # Register reference data if model not already registered
                if request.model_id not in self.drift_detector.reference_datasets:
                    self.drift_detector.register_reference_dataset(
                        request.model_id, reference_df
                    )

                # Perform drift detection
                drift_result = await self.drift_detector.detect_drift_async(
                    current_data=current_df,
                    model_id=request.model_id,
                    service_id=request.service_id,
                )

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                # Update metrics
                self.metrics["detections_completed"] += 1
                self.metrics["average_processing_time_ms"] = (
                    self.metrics["average_processing_time_ms"]
                    * (self.metrics["detections_completed"] - 1)
                    + processing_time
                ) / self.metrics["detections_completed"]

                if drift_result.drift_detected:
                    self.metrics["drift_alerts_generated"] += 1

                if drift_result.retraining_required:
                    self.metrics["retraining_triggers"] += 1

                # Determine drift severity
                drift_severity = self._determine_drift_severity(drift_result)

                # Generate recommendations
                recommendations = self._generate_drift_recommendations(drift_result)

                # Create response
                detection_id = f"drift-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                response = DriftDetectionResponse(
                    detection_id=detection_id,
                    model_id=request.model_id,
                    drift_detected=drift_result.drift_detected,
                    retraining_required=drift_result.retraining_required,
                    features_with_ks_drift=drift_result.features_with_ks_drift,
                    features_with_psi_drift=drift_result.features_with_psi_drift,
                    drift_severity=drift_severity,
                    recommendations=recommendations,
                    constitutional_hash=self.constitutional_hash,
                    timestamp=datetime.now().isoformat(),
                )

                # Publish drift event in background
                background_tasks.add_task(
                    self._publish_drift_event,
                    detection_id,
                    request.model_id,
                    request.service_id,
                    drift_result,
                    drift_severity,
                )

                logger.info(
                    f"✅ Drift detection completed: {detection_id} "
                    f"(drift: {drift_result.drift_detected}, "
                    f"retraining: {drift_result.retraining_required}, "
                    f"processing: {processing_time:.1f}ms)"
                )

                return response

            except Exception as e:
                logger.error(f"❌ Drift detection failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Drift detection failed: {e!s}"
                )

        @self.app.post("/monitor/start")
        async def start_monitoring(
            model_id: str, service_id: str, monitoring_interval: int = 300
        ):
            """Start continuous drift monitoring for a model."""

            # Start monitoring task
            asyncio.create_task(
                self._continuous_monitoring(model_id, service_id, monitoring_interval)
            )

            return {
                "message": f"Started drift monitoring for {model_id}",
                "interval_seconds": monitoring_interval,
                "constitutional_hash": self.constitutional_hash,
            }

        @self.app.get("/models")
        async def list_models():
            """List registered models."""

            models = list(self.drift_detector.reference_datasets.keys())

            return {
                "models": models,
                "count": len(models),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/detections/recent")
        async def get_recent_detections(limit: int = 10):
            """Get recent drift detections."""

            # In production, would query database
            return {
                "detections": [],  # Placeholder
                "count": 0,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

    def _determine_drift_severity(self, drift_result) -> str:
        """Determine drift severity based on detection results."""

        total_drift_features = len(drift_result.features_with_ks_drift) + len(
            drift_result.features_with_psi_drift
        )

        if drift_result.retraining_required:
            return "CRITICAL"
        if total_drift_features >= 3:
            return "HIGH"
        if total_drift_features >= 1:
            return "MEDIUM"
        return "LOW"

    def _generate_drift_recommendations(self, drift_result) -> list[str]:
        """Generate drift handling recommendations."""

        recommendations = []

        if drift_result.retraining_required:
            recommendations.append(
                "Immediate model retraining required due to significant drift."
            )

        if drift_result.features_with_ks_drift:
            recommendations.append(
                f"KS drift detected in features: {', '.join(drift_result.features_with_ks_drift)}. "
                "Consider feature engineering or data preprocessing adjustments."
            )

        if drift_result.features_with_psi_drift:
            recommendations.append(
                f"PSI drift detected in features: {', '.join(drift_result.features_with_psi_drift)}. "
                "Monitor data distribution changes and update reference dataset."
            )

        if not drift_result.drift_detected:
            recommendations.append(
                "No significant drift detected. Continue monitoring."
            )

        return recommendations

    async def _publish_drift_event(
        self,
        detection_id: str,
        model_id: str,
        service_id: str,
        drift_result,
        drift_severity: str,
    ):
        """Publish drift detection event."""

        try:
            # Create drift event
            event = ACGSEvent(
                event_type="drift_detection_completed",
                timestamp=datetime.now().isoformat(),
                constitutional_hash=self.constitutional_hash,
                source_service=self.service_name,
                target_service=service_id,
                event_id=detection_id,
                payload={
                    "model_id": model_id,
                    "drift_detected": drift_result.drift_detected,
                    "retraining_required": drift_result.retraining_required,
                    "features_with_ks_drift": drift_result.features_with_ks_drift,
                    "features_with_psi_drift": drift_result.features_with_psi_drift,
                    "drift_severity": drift_severity,
                },
                priority=(
                    "CRITICAL"
                    if drift_result.retraining_required
                    else "HIGH" if drift_result.drift_detected else "NORMAL"
                ),
            )

            # Publish event
            await self.event_broker.publish_event("acgs.drift.detection", event)

            # If retraining required, publish retraining event
            if drift_result.retraining_required:
                retraining_event = ACGSEvent(
                    event_type="retraining_required",
                    timestamp=datetime.now().isoformat(),
                    constitutional_hash=self.constitutional_hash,
                    source_service=self.service_name,
                    target_service="automated_retraining",
                    event_id=f"retrain-{detection_id}",
                    payload={
                        "model_id": model_id,
                        "trigger": "drift_detection",
                        "drift_features": drift_result.features_with_ks_drift
                        + drift_result.features_with_psi_drift,
                        "severity": drift_severity,
                    },
                    priority="CRITICAL",
                )

                await self.event_broker.publish_event(
                    "acgs.model.retraining.required", retraining_event
                )

        except Exception as e:
            logger.error(f"❌ Failed to publish drift event: {e}")

    async def _continuous_monitoring(
        self, model_id: str, service_id: str, interval_seconds: int
    ):
        """Continuous drift monitoring for a model."""

        logger.info(f"🔍 Starting continuous drift monitoring for {model_id}")

        while True:
            try:
                # In production, would fetch current data from service
                # For demo, generate sample data with potential drift
                current_data = self._generate_sample_data_with_drift()

                # Perform drift detection
                current_df = pd.DataFrame(current_data)
                drift_result = await self.drift_detector.detect_drift_async(
                    current_data=current_df, model_id=model_id, service_id=service_id
                )

                # Check for alerts
                if drift_result.drift_detected:
                    logger.warning(
                        f"🚨 Drift alert for {model_id}: "
                        f"KS features: {len(drift_result.features_with_ks_drift)}, "
                        f"PSI features: {len(drift_result.features_with_psi_drift)}"
                    )

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"❌ Error in continuous drift monitoring: {e}")
                await asyncio.sleep(5)

    def _generate_sample_data_with_drift(self) -> list[dict[str, Any]]:
        """Generate sample data with potential drift for monitoring demo."""

        data = []
        drift_factor = np.random.random() * 2  # Random drift intensity

        for i in range(100):
            record = {
                "timestamp": datetime.now().isoformat(),
                "feature1": np.random.normal(drift_factor, 1),  # Potential mean shift
                "feature2": np.random.normal(
                    0, 1 + drift_factor * 0.5
                ),  # Potential variance change
                "feature3": np.random.exponential(
                    1 + drift_factor * 0.3
                ),  # Potential distribution change
                "response_time_ms": np.random.lognormal(6, 0.5),
                "quality_score": np.random.beta(8, 2),
            }
            data.append(record)

        return data

    async def startup(self):
        """Startup tasks for the microservice."""

        # Connect to event broker
        await self.event_broker.connect()
        await self.drift_detector.connect_to_nats()

        logger.info(f"✅ Drift Detection Microservice started on port {self.port}")

    async def shutdown(self):
        """Shutdown tasks for the microservice."""

        # Disconnect from event broker
        await self.event_broker.disconnect()
        await self.drift_detector.disconnect_from_nats()

        logger.info("✅ Drift Detection Microservice shutdown completed")


# Global service instance
service = DriftDetectionMicroservice()


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
