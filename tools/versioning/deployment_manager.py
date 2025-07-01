"""
ACGS-1 Deployment Manager

Manages version-specific deployment strategies including blue-green deployments
for major versions and rolling updates for minor/patch versions.
"""

import logging
import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ...services.shared.versioning.version_manager import APIVersion, VersionPolicy

logger = logging.getLogger(__name__)


class DeploymentStrategy(str, Enum):
    """Deployment strategies for different version types."""

    BLUE_GREEN = "blue_green"  # For major versions
    ROLLING = "rolling"  # For minor/patch versions
    CANARY = "canary"  # For testing new features
    IMMEDIATE = "immediate"  # For hotfixes


class DeploymentStatus(str, Enum):
    """Deployment status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Configuration for a deployment."""

    strategy: DeploymentStrategy
    source_version: APIVersion
    target_version: APIVersion
    rollback_threshold_error_rate: float = 0.05  # 5% error rate triggers rollback
    health_check_timeout_seconds: int = 300  # 5 minutes
    traffic_shift_percentage: int = 10  # For canary deployments
    max_unavailable_instances: int = 1  # For rolling deployments

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "strategy": self.strategy.value,
            "source_version": str(self.source_version),
            "target_version": str(self.target_version),
            "rollback_threshold_error_rate": self.rollback_threshold_error_rate,
            "health_check_timeout_seconds": self.health_check_timeout_seconds,
            "traffic_shift_percentage": self.traffic_shift_percentage,
            "max_unavailable_instances": self.max_unavailable_instances,
        }


@dataclass
class DeploymentStep:
    """Individual step in a deployment process."""

    name: str
    description: str
    commands: List[str] = field(default_factory=list)
    health_checks: List[str] = field(default_factory=list)
    rollback_commands: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "commands": self.commands,
            "health_checks": self.health_checks,
            "rollback_commands": self.rollback_commands,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
        }


@dataclass
class DeploymentPlan:
    """Complete deployment plan with all steps."""

    config: DeploymentConfig
    steps: List[DeploymentStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_duration_minutes: int = 0

    def add_step(self, step: DeploymentStep):
        """Add a deployment step."""
        self.steps.append(step)
        self.estimated_duration_minutes += step.timeout_seconds // 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "config": self.config.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "estimated_duration_minutes": self.estimated_duration_minutes,
        }


class DeploymentManager:
    """
    Manages API version deployments with different strategies based on version type.

    Features:
    - Blue-green deployments for major versions
    - Rolling updates for minor/patch versions
    - Canary deployments for feature testing
    - Automatic rollback on health check failures
    - Traffic shifting and load balancing
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.active_deployments: Dict[str, DeploymentStatus] = {}
        self.deployment_history: List[Dict[str, Any]] = []

    def create_deployment_plan(
        self,
        source_version: APIVersion,
        target_version: APIVersion,
        strategy: Optional[DeploymentStrategy] = None,
    ) -> DeploymentPlan:
        """
        Create deployment plan based on version change type.

        Args:
            source_version: Current version
            target_version: Target version
            strategy: Override automatic strategy selection

        Returns:
            Complete deployment plan
        """
        # Determine strategy if not provided
        if strategy is None:
            strategy = self._determine_strategy(source_version, target_version)

        config = DeploymentConfig(
            strategy=strategy,
            source_version=source_version,
            target_version=target_version,
        )

        plan = DeploymentPlan(config=config)

        # Generate steps based on strategy
        if strategy == DeploymentStrategy.BLUE_GREEN:
            self._create_blue_green_steps(plan)
        elif strategy == DeploymentStrategy.ROLLING:
            self._create_rolling_steps(plan)
        elif strategy == DeploymentStrategy.CANARY:
            self._create_canary_steps(plan)
        elif strategy == DeploymentStrategy.IMMEDIATE:
            self._create_immediate_steps(plan)

        logger.info(
            f"Created {strategy.value} deployment plan with {len(plan.steps)} steps"
        )
        return plan

    def _determine_strategy(
        self, source_version: APIVersion, target_version: APIVersion
    ) -> DeploymentStrategy:
        """Determine appropriate deployment strategy based on version change."""
        compatibility_level = source_version.get_compatibility_level(target_version)

        if compatibility_level == VersionPolicy.MAJOR:
            return DeploymentStrategy.BLUE_GREEN
        elif compatibility_level == VersionPolicy.MINOR:
            return DeploymentStrategy.ROLLING
        else:  # PATCH
            return DeploymentStrategy.ROLLING

    def _create_blue_green_steps(self, plan: DeploymentPlan):
        """Create blue-green deployment steps."""
        # Step 1: Prepare green environment
        plan.add_step(
            DeploymentStep(
                name="prepare_green_environment",
                description="Set up green environment with new version",
                commands=[
                    f"# Deploy {plan.config.target_version} to green environment",
                    "docker build -t acgs-service:green .",
                    "docker-compose -f docker-compose.green.yml up -d",
                    "# Wait for services to start",
                    "sleep 30",
                ],
                health_checks=[
                    "curl -f http://green-env:8000/health",
                    "curl -f http://green-env:8000/api/v1/health",
                ],
                rollback_commands=["docker-compose -f docker-compose.green.yml down"],
                timeout_seconds=300,
            )
        )

        # Step 2: Run health checks
        plan.add_step(
            DeploymentStep(
                name="health_check_green",
                description="Verify green environment health",
                commands=[
                    "# Run comprehensive health checks",
                    "python tools/health_check.py --env=green",
                    "# Run smoke tests",
                    "python -m pytest tests/smoke/ --env=green",
                ],
                health_checks=[
                    "All health endpoints return 200",
                    "Database connectivity verified",
                    "External service dependencies verified",
                ],
                timeout_seconds=180,
            )
        )

        # Step 3: Switch traffic
        plan.add_step(
            DeploymentStep(
                name="switch_traffic",
                description="Switch load balancer to green environment",
                commands=[
                    "# Update load balancer configuration",
                    'kubectl patch service acgs-service -p \'{"spec":{"selector":{"version":"green"}}}\'',
                    "# Verify traffic switch",
                    "sleep 10",
                    "curl -f http://acgs-service:8000/health",
                ],
                health_checks=[
                    "Load balancer routing to green environment",
                    "No 5xx errors in logs",
                    "Response times within acceptable range",
                ],
                rollback_commands=[
                    'kubectl patch service acgs-service -p \'{"spec":{"selector":{"version":"blue"}}}\''
                ],
                timeout_seconds=120,
            )
        )

        # Step 4: Monitor and cleanup
        plan.add_step(
            DeploymentStep(
                name="monitor_and_cleanup",
                description="Monitor new version and cleanup old environment",
                commands=[
                    "# Monitor for 10 minutes",
                    "python tools/monitor_deployment.py --duration=600",
                    "# If stable, cleanup blue environment",
                    "docker-compose -f docker-compose.blue.yml down",
                ],
                health_checks=[
                    "Error rate below threshold",
                    "Performance metrics stable",
                    "No critical alerts",
                ],
                timeout_seconds=720,
            )
        )

    def _create_rolling_steps(self, plan: DeploymentPlan):
        """Create rolling deployment steps."""
        # Step 1: Update instances gradually
        plan.add_step(
            DeploymentStep(
                name="rolling_update",
                description="Update instances one by one",
                commands=[
                    f"# Rolling update to {plan.config.target_version}",
                    "kubectl set image deployment/acgs-service acgs-service=acgs-service:latest",
                    "kubectl rollout status deployment/acgs-service --timeout=300s",
                ],
                health_checks=[
                    "All pods running and ready",
                    "Health endpoints responding",
                    "No service disruption",
                ],
                rollback_commands=["kubectl rollout undo deployment/acgs-service"],
                timeout_seconds=300,
            )
        )

        # Step 2: Verify deployment
        plan.add_step(
            DeploymentStep(
                name="verify_rolling_deployment",
                description="Verify rolling deployment success",
                commands=[
                    "# Verify all instances updated",
                    "kubectl get pods -l app=acgs-service",
                    "# Run health checks",
                    "python tools/health_check.py",
                ],
                health_checks=[
                    "All instances running new version",
                    "Health checks passing",
                    "Performance within acceptable range",
                ],
                timeout_seconds=180,
            )
        )

    def _create_canary_steps(self, plan: DeploymentPlan):
        """Create canary deployment steps."""
        # Step 1: Deploy canary
        plan.add_step(
            DeploymentStep(
                name="deploy_canary",
                description="Deploy canary version with limited traffic",
                commands=[
                    f"# Deploy canary with {plan.config.traffic_shift_percentage}% traffic",
                    "kubectl apply -f canary-deployment.yaml",
                    f"# Configure traffic split: {100-plan.config.traffic_shift_percentage}% stable, {plan.config.traffic_shift_percentage}% canary",
                    "istioctl apply -f traffic-split.yaml",
                ],
                health_checks=[
                    "Canary pods running",
                    "Traffic split configured correctly",
                    "Canary receiving expected traffic",
                ],
                rollback_commands=[
                    "kubectl delete -f canary-deployment.yaml",
                    "istioctl apply -f traffic-split-stable.yaml",
                ],
                timeout_seconds=240,
            )
        )

        # Step 2: Monitor canary
        plan.add_step(
            DeploymentStep(
                name="monitor_canary",
                description="Monitor canary performance and errors",
                commands=[
                    "# Monitor canary for 30 minutes",
                    "python tools/monitor_canary.py --duration=1800",
                    "# Compare metrics with stable version",
                ],
                health_checks=[
                    "Canary error rate below threshold",
                    "Canary performance comparable to stable",
                    "No critical issues detected",
                ],
                timeout_seconds=1800,
            )
        )

        # Step 3: Promote or rollback
        plan.add_step(
            DeploymentStep(
                name="promote_or_rollback",
                description="Promote canary to stable or rollback",
                commands=[
                    "# If metrics good, promote canary",
                    "kubectl apply -f promote-canary.yaml",
                    "# Route 100% traffic to new version",
                    "istioctl apply -f traffic-split-new.yaml",
                ],
                health_checks=[
                    "All traffic routed to new version",
                    "Old version instances terminated",
                    "System stable",
                ],
                rollback_commands=[
                    "istioctl apply -f traffic-split-stable.yaml",
                    "kubectl delete -f canary-deployment.yaml",
                ],
                timeout_seconds=300,
            )
        )

    def _create_immediate_steps(self, plan: DeploymentPlan):
        """Create immediate deployment steps for hotfixes."""
        # Step 1: Immediate deployment
        plan.add_step(
            DeploymentStep(
                name="immediate_deployment",
                description="Deploy hotfix immediately",
                commands=[
                    f"# Immediate deployment of {plan.config.target_version}",
                    "kubectl set image deployment/acgs-service acgs-service=acgs-service:hotfix",
                    "kubectl rollout status deployment/acgs-service --timeout=120s",
                ],
                health_checks=[
                    "All pods updated",
                    "Health endpoints responding",
                    "Critical issue resolved",
                ],
                rollback_commands=["kubectl rollout undo deployment/acgs-service"],
                timeout_seconds=120,
            )
        )

        # Step 2: Verify hotfix
        plan.add_step(
            DeploymentStep(
                name="verify_hotfix",
                description="Verify hotfix resolves critical issue",
                commands=[
                    "# Verify hotfix effectiveness",
                    "python tools/verify_hotfix.py",
                    "# Monitor for immediate issues",
                ],
                health_checks=[
                    "Critical issue resolved",
                    "No new issues introduced",
                    "System stable",
                ],
                timeout_seconds=300,
            )
        )

    async def execute_deployment(self, plan: DeploymentPlan) -> bool:
        """
        Execute deployment plan with monitoring and rollback capabilities.

        Args:
            plan: Deployment plan to execute

        Returns:
            True if deployment successful, False if rolled back
        """
        deployment_id = f"{self.service_name}-{plan.config.target_version}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_deployments[deployment_id] = DeploymentStatus.IN_PROGRESS

        try:
            logger.info(f"Starting deployment {deployment_id}")

            for i, step in enumerate(plan.steps):
                logger.info(f"Executing step {i+1}/{len(plan.steps)}: {step.name}")

                success = await self._execute_step(step)
                if not success:
                    logger.error(f"Step {step.name} failed, initiating rollback")
                    await self._rollback_deployment(plan, i)
                    self.active_deployments[deployment_id] = (
                        DeploymentStatus.ROLLED_BACK
                    )
                    return False

            self.active_deployments[deployment_id] = DeploymentStatus.COMPLETED
            logger.info(f"Deployment {deployment_id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed with exception: {e}")
            self.active_deployments[deployment_id] = DeploymentStatus.FAILED
            return False

    async def _execute_step(self, step: DeploymentStep) -> bool:
        """Execute a single deployment step."""
        try:
            # Execute commands
            for command in step.commands:
                logger.debug(f"Executing: {command}")
                # In real implementation, execute the command
                await asyncio.sleep(1)  # Simulate command execution

            # Run health checks
            for health_check in step.health_checks:
                logger.debug(f"Health check: {health_check}")
                # In real implementation, run the health check
                await asyncio.sleep(1)  # Simulate health check

            return True

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False

    async def _rollback_deployment(self, plan: DeploymentPlan, failed_step_index: int):
        """Rollback deployment by executing rollback commands in reverse order."""
        logger.info("Initiating deployment rollback")

        # Execute rollback commands for completed steps in reverse order
        for i in range(failed_step_index, -1, -1):
            step = plan.steps[i]
            if step.rollback_commands:
                logger.info(f"Rolling back step: {step.name}")
                for command in step.rollback_commands:
                    logger.debug(f"Rollback command: {command}")
                    # In real implementation, execute rollback command
                    await asyncio.sleep(1)

    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentStatus]:
        """Get status of a specific deployment."""
        return self.active_deployments.get(deployment_id)

    def list_active_deployments(self) -> Dict[str, DeploymentStatus]:
        """List all active deployments."""
        return self.active_deployments.copy()

    def save_deployment_plan(self, plan: DeploymentPlan, output_path: str):
        """Save deployment plan to file."""
        import json
        from pathlib import Path

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(plan.to_dict(), f, indent=2)

        logger.info(f"Deployment plan saved to {output_path}")
