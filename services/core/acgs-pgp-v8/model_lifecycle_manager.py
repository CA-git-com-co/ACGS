#!/usr/bin/env python3
"""
Model Lifecycle Manager for ACGS-PGP v8

Manages the complete lifecycle of ML models in the ACGS platform:
- Model registration and versioning
- Performance monitoring and alerting
- Automated deployment and rollback
- Constitutional compliance tracking
- Integration with automated retraining system

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# Import retraining system components
from automated_model_retraining import (
    ModelMetadata,
    ModelStatus,
    RetrainingTrigger,
    AutomatedRetrainingOrchestrator,
    ConstitutionalComplianceValidator,
)
from nats_event_broker import NATSEventBroker, ACGSEvent

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Model deployment strategies."""

    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMEDIATE = "immediate"


@dataclass
class ModelDeployment:
    """Model deployment configuration."""

    deployment_id: str
    model_id: str
    version: str
    strategy: DeploymentStrategy
    target_services: List[str]
    traffic_percentage: float
    health_check_url: str
    rollback_threshold: float
    constitutional_hash: str
    deployed_at: str


@dataclass
class ModelPerformanceSnapshot:
    """Snapshot of model performance metrics."""

    model_id: str
    version: str
    timestamp: str
    metrics: Dict[str, float]
    service_id: str
    constitutional_compliance_score: float
    constitutional_hash: str


@dataclass
class ModelAlert:
    """Model performance or compliance alert."""

    alert_id: str
    model_id: str
    alert_type: str  # 'performance', 'compliance', 'availability'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    message: str
    metrics: Dict[str, Any]
    triggered_at: str
    resolved_at: Optional[str]
    constitutional_hash: str


class ModelLifecycleManager:
    """Manages the complete lifecycle of ML models."""

    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.nats_url = nats_url

        # Initialize components
        self.event_broker = NATSEventBroker(nats_url)
        self.retraining_orchestrator = AutomatedRetrainingOrchestrator(nats_url)
        self.compliance_validator = ConstitutionalComplianceValidator()

        # Model registry and tracking
        self.model_registry: Dict[str, ModelMetadata] = {}
        self.deployment_registry: Dict[str, ModelDeployment] = {}
        self.performance_history: Dict[str, List[ModelPerformanceSnapshot]] = {}
        self.active_alerts: Dict[str, ModelAlert] = {}

        # Lifecycle configuration
        self.lifecycle_config = {
            "performance_monitoring_interval_seconds": 60,
            "compliance_check_interval_seconds": 300,
            "alert_cooldown_seconds": 600,
            "performance_history_retention_days": 30,
            "auto_rollback_enabled": True,
            "rollback_threshold": 0.1,  # 10% performance degradation
        }

        # Performance thresholds
        self.performance_thresholds = {
            "response_time_ms": {"warning": 400, "critical": 800},
            "accuracy": {"warning": 0.85, "critical": 0.80},
            "error_rate": {"warning": 0.05, "critical": 0.10},
            "throughput_rps": {"warning": 50, "critical": 25},
        }

        logger.info(f"Model Lifecycle Manager initialized")

    async def initialize(self):
        """Initialize the model lifecycle manager."""

        # Connect to event broker
        await self.event_broker.connect()
        await self.retraining_orchestrator.initialize()

        # Set up event subscriptions
        await self.event_broker.subscribe_to_subject(
            "acgs.model.metrics.*", self._handle_model_metrics
        )

        await self.event_broker.subscribe_to_subject(
            "acgs.model.deployment.*", self._handle_deployment_event
        )

        await self.event_broker.subscribe_to_subject(
            "acgs.model.retraining.completed", self._handle_retraining_completion
        )

        # Start monitoring tasks
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._compliance_monitoring_loop())
        asyncio.create_task(self._alert_management_loop())

        logger.info("✅ Model Lifecycle Manager initialized")

    async def register_model(self, model_metadata: ModelMetadata) -> bool:
        """Register a new model in the lifecycle management system."""

        # Validate constitutional hash
        if model_metadata.constitutional_hash != self.constitutional_hash:
            logger.error(
                f"❌ Constitutional hash mismatch for model {model_metadata.model_id}"
            )
            return False

        # Validate constitutional compliance
        compliance_result = await self.compliance_validator.validate_model_compliance(
            model_metadata.model_id, model_metadata.performance_metrics
        )

        if not compliance_result["compliant"]:
            logger.error(
                f"❌ Model {model_metadata.model_id} failed compliance validation"
            )
            return False

        # Register model
        self.model_registry[model_metadata.model_id] = model_metadata
        self.performance_history[model_metadata.model_id] = []

        # Register with retraining orchestrator
        await self.retraining_orchestrator.register_model(model_metadata)

        # Publish registration event
        registration_event = ACGSEvent(
            event_type="model_registered",
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            source_service="model_lifecycle_manager",
            target_service=None,
            event_id=f"reg-{model_metadata.model_id}",
            payload=asdict(model_metadata),
            priority="NORMAL",
        )

        await self.event_broker.publish_event(
            "acgs.model.lifecycle.registered", registration_event
        )

        logger.info(
            f"✅ Registered model: {model_metadata.model_id} v{model_metadata.version}"
        )
        return True

    async def deploy_model(
        self, model_id: str, deployment_config: Dict[str, Any]
    ) -> bool:
        """Deploy a model using specified deployment strategy."""

        if model_id not in self.model_registry:
            logger.error(f"❌ Model {model_id} not found in registry")
            return False

        model = self.model_registry[model_id]

        # Create deployment record
        deployment = ModelDeployment(
            deployment_id=f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            model_id=model_id,
            version=model.version,
            strategy=DeploymentStrategy(deployment_config.get("strategy", "immediate")),
            target_services=deployment_config.get("target_services", []),
            traffic_percentage=deployment_config.get("traffic_percentage", 100.0),
            health_check_url=deployment_config.get("health_check_url", ""),
            rollback_threshold=deployment_config.get("rollback_threshold", 0.1),
            constitutional_hash=self.constitutional_hash,
            deployed_at=datetime.now().isoformat(),
        )

        # Execute deployment
        success = await self._execute_deployment(deployment)

        if success:
            self.deployment_registry[deployment.deployment_id] = deployment
            model.status = ModelStatus.ACTIVE

            logger.info(f"✅ Deployed model: {model_id} v{model.version}")
        else:
            logger.error(f"❌ Failed to deploy model: {model_id}")

        return success

    async def _execute_deployment(self, deployment: ModelDeployment) -> bool:
        """Execute model deployment based on strategy."""

        logger.info(
            f"🚀 Executing {deployment.strategy.value} deployment for {deployment.model_id}"
        )

        try:
            if deployment.strategy == DeploymentStrategy.BLUE_GREEN:
                return await self._blue_green_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.CANARY:
                return await self._canary_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.ROLLING:
                return await self._rolling_deployment(deployment)
            else:  # IMMEDIATE
                return await self._immediate_deployment(deployment)

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False

    async def _blue_green_deployment(self, deployment: ModelDeployment) -> bool:
        """Execute blue-green deployment."""
        logger.info(f"🔵🟢 Blue-green deployment for {deployment.model_id}")

        # Simulate blue-green deployment
        await asyncio.sleep(2)  # Simulate deployment time

        # Health check
        health_ok = await self._perform_health_check(deployment)

        if health_ok:
            # Switch traffic
            logger.info(f"✅ Traffic switched to new version")
            return True
        else:
            logger.error(f"❌ Health check failed, rolling back")
            return False

    async def _canary_deployment(self, deployment: ModelDeployment) -> bool:
        """Execute canary deployment."""
        logger.info(f"🐤 Canary deployment for {deployment.model_id}")

        # Start with small traffic percentage
        current_traffic = 5.0
        target_traffic = deployment.traffic_percentage

        while current_traffic <= target_traffic:
            logger.info(f"📊 Canary traffic: {current_traffic}%")

            # Simulate traffic routing
            await asyncio.sleep(1)

            # Monitor performance
            performance_ok = await self._monitor_canary_performance(
                deployment, current_traffic
            )

            if not performance_ok:
                logger.error(f"❌ Canary performance degraded, rolling back")
                return False

            # Increase traffic gradually
            current_traffic = min(current_traffic * 2, target_traffic)

        logger.info(f"✅ Canary deployment completed")
        return True

    async def _rolling_deployment(self, deployment: ModelDeployment) -> bool:
        """Execute rolling deployment."""
        logger.info(f"🔄 Rolling deployment for {deployment.model_id}")

        # Simulate rolling deployment across services
        for service in deployment.target_services:
            logger.info(f"📦 Deploying to service: {service}")
            await asyncio.sleep(1)

            # Health check after each service
            if not await self._perform_health_check(deployment):
                logger.error(f"❌ Health check failed for {service}")
                return False

        logger.info(f"✅ Rolling deployment completed")
        return True

    async def _immediate_deployment(self, deployment: ModelDeployment) -> bool:
        """Execute immediate deployment."""
        logger.info(f"⚡ Immediate deployment for {deployment.model_id}")

        # Simulate immediate deployment
        await asyncio.sleep(1)

        return await self._perform_health_check(deployment)

    async def _perform_health_check(self, deployment: ModelDeployment) -> bool:
        """Perform health check on deployed model."""

        # Simulate health check
        health_score = np.random.beta(9, 1)  # High probability of success

        if health_score > 0.9:
            logger.info(f"✅ Health check passed: {health_score:.3f}")
            return True
        else:
            logger.warning(f"⚠️ Health check failed: {health_score:.3f}")
            return False

    async def _monitor_canary_performance(
        self, deployment: ModelDeployment, traffic_percentage: float
    ) -> bool:
        """Monitor canary deployment performance."""

        # Simulate performance monitoring
        performance_score = np.random.beta(8, 2)  # Generally good performance

        if performance_score > 0.8:
            logger.info(f"✅ Canary performance good: {performance_score:.3f}")
            return True
        else:
            logger.warning(f"⚠️ Canary performance degraded: {performance_score:.3f}")
            return False

    async def _handle_model_metrics(self, event_data: Dict[str, Any], msg):
        """Handle incoming model performance metrics."""

        model_id = event_data.get("model_id")
        if not model_id or model_id not in self.model_registry:
            return

        # Create performance snapshot
        snapshot = ModelPerformanceSnapshot(
            model_id=model_id,
            version=event_data.get("version", "unknown"),
            timestamp=datetime.now().isoformat(),
            metrics=event_data.get("metrics", {}),
            service_id=event_data.get("service_id", "unknown"),
            constitutional_compliance_score=event_data.get("compliance_score", 1.0),
            constitutional_hash=self.constitutional_hash,
        )

        # Add to performance history
        self.performance_history[model_id].append(snapshot)

        # Keep only recent history
        retention_cutoff = datetime.now() - timedelta(
            days=self.lifecycle_config["performance_history_retention_days"]
        )
        self.performance_history[model_id] = [
            s
            for s in self.performance_history[model_id]
            if datetime.fromisoformat(s.timestamp) > retention_cutoff
        ]

        # Check for performance issues
        await self._check_performance_alerts(snapshot)

    async def _check_performance_alerts(self, snapshot: ModelPerformanceSnapshot):
        """Check for performance threshold violations."""

        for metric_name, value in snapshot.metrics.items():
            if metric_name not in self.performance_thresholds:
                continue

            thresholds = self.performance_thresholds[metric_name]

            # Determine alert severity
            severity = None
            if metric_name in ["response_time_ms", "error_rate"]:
                # Higher is worse
                if value >= thresholds["critical"]:
                    severity = "CRITICAL"
                elif value >= thresholds["warning"]:
                    severity = "HIGH"
            else:
                # Lower is worse
                if value <= thresholds["critical"]:
                    severity = "CRITICAL"
                elif value <= thresholds["warning"]:
                    severity = "HIGH"

            if severity:
                await self._create_alert(
                    model_id=snapshot.model_id,
                    alert_type="performance",
                    severity=severity,
                    message=f"{metric_name} threshold violation: {value}",
                    metrics={
                        "metric": metric_name,
                        "value": value,
                        "threshold": thresholds,
                    },
                )

    async def _create_alert(
        self,
        model_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metrics: Dict[str, Any],
    ):
        """Create a model alert."""

        alert_id = f"{alert_type}-{model_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Check for alert cooldown
        recent_alerts = [
            alert
            for alert in self.active_alerts.values()
            if (
                alert.model_id == model_id
                and alert.alert_type == alert_type
                and alert.resolved_at is None
                and (
                    datetime.now() - datetime.fromisoformat(alert.triggered_at)
                ).total_seconds()
                < self.lifecycle_config["alert_cooldown_seconds"]
            )
        ]

        if recent_alerts:
            logger.debug(f"⏰ Alert cooldown active for {model_id}")
            return

        alert = ModelAlert(
            alert_id=alert_id,
            model_id=model_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metrics=metrics,
            triggered_at=datetime.now().isoformat(),
            resolved_at=None,
            constitutional_hash=self.constitutional_hash,
        )

        self.active_alerts[alert_id] = alert

        # Publish alert event
        alert_event = ACGSEvent(
            event_type="model_alert",
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            source_service="model_lifecycle_manager",
            target_service=None,
            event_id=alert_id,
            payload=asdict(alert),
            priority=severity,
        )

        await self.event_broker.publish_event(
            f"acgs.model.alert.{severity.lower()}", alert_event
        )

        logger.warning(f"🚨 Model alert created: {alert_id} - {message}")

    async def _handle_deployment_event(self, event_data: Dict[str, Any], msg):
        """Handle deployment-related events."""
        logger.info(f"📦 Deployment event: {event_data.get('event_type', 'unknown')}")

    async def _handle_retraining_completion(self, event_data: Dict[str, Any], msg):
        """Handle retraining completion events."""

        model_id = event_data.get("payload", {}).get("model_id")
        success = event_data.get("payload", {}).get("success", False)

        if model_id and model_id in self.model_registry:
            if success:
                logger.info(f"✅ Retraining completed successfully for {model_id}")
                # Update model status
                self.model_registry[model_id].status = ModelStatus.ACTIVE
            else:
                logger.error(f"❌ Retraining failed for {model_id}")
                self.model_registry[model_id].status = ModelStatus.FAILED

    async def _performance_monitoring_loop(self):
        """Continuous performance monitoring loop."""

        while True:
            try:
                await asyncio.sleep(
                    self.lifecycle_config["performance_monitoring_interval_seconds"]
                )

                # Monitor all active models
                for model_id, model in self.model_registry.items():
                    if model.status == ModelStatus.ACTIVE:
                        await self._monitor_model_performance(model_id)

            except Exception as e:
                logger.error(f"❌ Error in performance monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _compliance_monitoring_loop(self):
        """Continuous compliance monitoring loop."""

        while True:
            try:
                await asyncio.sleep(
                    self.lifecycle_config["compliance_check_interval_seconds"]
                )

                # Check compliance for all active models
                for model_id, model in self.model_registry.items():
                    if model.status == ModelStatus.ACTIVE:
                        await self._monitor_model_compliance(model_id)

            except Exception as e:
                logger.error(f"❌ Error in compliance monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _alert_management_loop(self):
        """Alert management and resolution loop."""

        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Auto-resolve old alerts
                current_time = datetime.now()
                for alert_id, alert in list(self.active_alerts.items()):
                    if alert.resolved_at is None:
                        alert_age = (
                            current_time - datetime.fromisoformat(alert.triggered_at)
                        ).total_seconds()

                        # Auto-resolve alerts older than 1 hour
                        if alert_age > 3600:
                            alert.resolved_at = current_time.isoformat()
                            logger.info(f"🔄 Auto-resolved alert: {alert_id}")

            except Exception as e:
                logger.error(f"❌ Error in alert management loop: {e}")
                await asyncio.sleep(5)

    async def _monitor_model_performance(self, model_id: str):
        """Monitor performance of a specific model."""

        # Get recent performance history
        if model_id not in self.performance_history:
            return

        recent_snapshots = self.performance_history[model_id][-5:]  # Last 5 snapshots

        if len(recent_snapshots) < 2:
            return

        # Check for performance degradation trends
        for metric_name in self.performance_thresholds.keys():
            values = [
                s.metrics.get(metric_name)
                for s in recent_snapshots
                if metric_name in s.metrics
            ]

            if len(values) >= 3:
                # Simple trend analysis
                trend = np.polyfit(range(len(values)), values, 1)[0]

                # Check if trend indicates degradation
                if metric_name in ["response_time_ms", "error_rate"]:
                    degrading = trend > 0  # Increasing is bad
                else:
                    degrading = trend < 0  # Decreasing is bad

                if degrading and abs(trend) > 0.1:  # Significant trend
                    logger.warning(
                        f"📉 Performance trend degradation detected for {model_id}: {metric_name}"
                    )

    async def _monitor_model_compliance(self, model_id: str):
        """Monitor constitutional compliance of a specific model."""

        model = self.model_registry[model_id]

        # Validate compliance
        compliance_result = await self.compliance_validator.validate_model_compliance(
            model_id, model.performance_metrics
        )

        if not compliance_result["compliant"]:
            await self._create_alert(
                model_id=model_id,
                alert_type="compliance",
                severity="CRITICAL",
                message=f"Constitutional compliance violation: {len(compliance_result['violations'])} violations",
                metrics=compliance_result,
            )


# Example usage and testing
async def demo_model_lifecycle():
    """Demonstrate model lifecycle management."""

    # Initialize lifecycle manager
    manager = ModelLifecycleManager()
    await manager.initialize()

    # Register a sample model
    model = ModelMetadata(
        model_id="acgs_demo_model",
        model_name="ACGS Demo Model",
        version="v1.0.0",
        service_id="ac",
        status=ModelStatus.ACTIVE,
        created_at=datetime.now().isoformat(),
        last_updated=datetime.now().isoformat(),
        performance_metrics={"accuracy": 0.89, "response_time_ms": 250},
        constitutional_compliance_score=0.95,
        constitutional_hash=manager.constitutional_hash,
    )

    await manager.register_model(model)

    # Deploy the model
    deployment_config = {
        "strategy": "canary",
        "target_services": ["ac", "integrity"],
        "traffic_percentage": 50.0,
        "health_check_url": "/health",
    }

    await manager.deploy_model("acgs_demo_model", deployment_config)

    # Simulate some performance metrics
    for i in range(5):
        metrics_event = {
            "model_id": "acgs_demo_model",
            "version": "v1.0.0",
            "service_id": "ac",
            "metrics": {
                "accuracy": 0.89 - (i * 0.02),
                "response_time_ms": 250 + (i * 50),
                "error_rate": 0.01 + (i * 0.01),
            },
            "compliance_score": 0.95,
        }

        await manager._handle_model_metrics(metrics_event, None)
        await asyncio.sleep(1)

    # Wait for monitoring
    await asyncio.sleep(3)

    # Cleanup
    await manager.event_broker.disconnect()

    print("✅ Model lifecycle management demo completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    asyncio.run(demo_model_lifecycle())
