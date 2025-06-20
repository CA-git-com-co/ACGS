"""
Evolution Engine for ACGS-1 Self-Evolving AI Architecture Foundation.

This module implements the core evolution engine with manual policy evolution,
100% human oversight, and comprehensive safety controls. The engine coordinates
policy evolution cycles while maintaining constitutional compliance and security.

Key Features:
- Manual policy evolution with mandatory human approval
- Constitutional compliance validation
- Integration with all ACGS-1 services
- Comprehensive audit logging
- Rollback capabilities
- Performance monitoring
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import timezone, datetime
from enum import Enum
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class EvolutionStatus(Enum):
    """Evolution cycle status enumeration."""

    PENDING = "pending"
    INITIATED = "initiated"
    ANALYZING = "analyzing"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class EvolutionType(Enum):
    """Types of evolution operations."""

    POLICY_REFINEMENT = "policy_refinement"
    RULE_OPTIMIZATION = "rule_optimization"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"
    GOVERNANCE_ENHANCEMENT = "governance_enhancement"
    SECURITY_UPDATE = "security_update"


@dataclass
class EvolutionRequest:
    """Evolution request data structure."""

    evolution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evolution_type: EvolutionType = EvolutionType.POLICY_REFINEMENT
    description: str = ""
    target_policies: list[str] = field(default_factory=list)
    proposed_changes: dict[str, Any] = field(default_factory=dict)
    justification: str = ""
    requester_id: str = ""
    priority: str = "medium"  # low, medium, high, critical
    estimated_duration_minutes: int = 10
    requires_constitutional_validation: bool = True
    requires_formal_verification: bool = True
    status: EvolutionStatus = EvolutionStatus.PENDING
    approver_id: str | None = None
    approval_notes: str = ""
    approved_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EvolutionResult:
    """Evolution result data structure."""

    evolution_id: str
    status: EvolutionStatus
    success: bool
    changes_applied: dict[str, Any] = field(default_factory=dict)
    validation_results: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    completed_at: datetime | None = None
    rollback_available: bool = True


class EvolutionEngine:
    """
    Core evolution engine for manual policy evolution with human oversight.

    This engine implements the foundational capabilities for self-evolving AI
    governance while maintaining strict human control and safety mechanisms.
    """

    def __init__(
        self,
        settings,
        security_manager,
        policy_orchestrator,
        background_processor,
        observability_framework,
    ):
        self.settings = settings
        self.security_manager = security_manager
        self.policy_orchestrator = policy_orchestrator
        self.background_processor = background_processor
        self.observability_framework = observability_framework

        # Evolution tracking
        self.active_evolutions: dict[str, EvolutionRequest] = {}
        self.evolution_history: list[EvolutionResult] = []
        self.evolution_metrics: dict[str, Any] = {
            "total_evolutions": 0,
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "average_duration_minutes": 0,
            "human_approval_rate": 0,
        }

        # Safety controls
        self.max_concurrent_evolutions = settings.MAX_CONCURRENT_EVOLUTIONS
        self.manual_approval_required = settings.MANUAL_APPROVAL_REQUIRED
        self.rollback_enabled = settings.ROLLBACK_ENABLED

        # Service integration
        self.service_clients = {}
        self.constitution_hash = settings.CONSTITUTION_HASH

        logger.info("Evolution engine initialized with manual oversight")

    async def initialize(self):
        """Initialize the evolution engine."""
        try:
            # Initialize service clients
            await self._initialize_service_clients()

            # Validate constitutional compliance
            await self._validate_constitutional_compliance()

            # Start monitoring tasks
            asyncio.create_task(self._monitor_evolution_performance())

            logger.info("✅ Evolution engine initialization complete")

        except Exception as e:
            logger.error(f"❌ Evolution engine initialization failed: {e}")
            raise

    async def initiate_evolution(
        self, evolution_request: EvolutionRequest
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Initiate a manual policy evolution cycle.

        Args:
            evolution_request: Evolution request details

        Returns:
            Tuple of (success, evolution_id, status_info)
        """
        try:
            # Validate evolution request
            validation_result = await self._validate_evolution_request(
                evolution_request
            )
            if not validation_result["valid"]:
                return False, "", validation_result

            # Check concurrent evolution limits
            if len(self.active_evolutions) >= self.max_concurrent_evolutions:
                return (
                    False,
                    "",
                    {
                        "error": "Maximum concurrent evolutions reached",
                        "limit": self.max_concurrent_evolutions,
                        "active": len(self.active_evolutions),
                    },
                )

            # Security assessment
            security_assessment = await self.security_manager.assess_evolution_security(
                evolution_request
            )
            if not security_assessment["approved"]:
                return (
                    False,
                    "",
                    {
                        "error": "Security assessment failed",
                        "details": security_assessment,
                    },
                )

            # Add to active evolutions
            evolution_request.status = EvolutionStatus.INITIATED
            self.active_evolutions[evolution_request.evolution_id] = evolution_request

            # Start evolution process in background
            asyncio.create_task(
                self._execute_evolution_cycle(evolution_request.evolution_id)
            )

            # Update metrics
            self.evolution_metrics["total_evolutions"] += 1

            logger.info(f"Evolution {evolution_request.evolution_id} initiated")

            return (
                True,
                evolution_request.evolution_id,
                {
                    "status": "initiated",
                    "evolution_id": evolution_request.evolution_id,
                    "estimated_duration": evolution_request.estimated_duration_minutes,
                    "requires_approval": self.manual_approval_required,
                },
            )

        except Exception as e:
            logger.error(f"Failed to initiate evolution: {e}")
            return False, "", {"error": str(e)}

    async def approve_evolution(
        self, evolution_id: str, approver_id: str, approval_notes: str = ""
    ) -> tuple[bool, dict[str, Any]]:
        """
        Approve a pending evolution (human-in-the-loop control).

        Args:
            evolution_id: Evolution identifier
            approver_id: ID of the approving user
            approval_notes: Optional approval notes

        Returns:
            Tuple of (success, status_info)
        """
        try:
            if evolution_id not in self.active_evolutions:
                return False, {"error": "Evolution not found"}

            evolution = self.active_evolutions[evolution_id]

            if evolution.status != EvolutionStatus.PENDING_APPROVAL:
                return False, {
                    "error": "Evolution not in pending approval state",
                    "current_status": evolution.status.value,
                }

            # Validate approver permissions
            approval_valid = await self._validate_approver_permissions(
                approver_id, evolution
            )
            if not approval_valid:
                return False, {"error": "Insufficient permissions for approval"}

            # Record approval
            evolution.status = EvolutionStatus.APPROVED
            evolution.approver_id = approver_id
            evolution.approval_notes = approval_notes
            evolution.approved_at = datetime.now(timezone.utc)

            # Continue evolution process
            asyncio.create_task(self._continue_evolution_after_approval(evolution_id))

            logger.info(f"Evolution {evolution_id} approved by {approver_id}")

            return True, {
                "status": "approved",
                "evolution_id": evolution_id,
                "approver_id": approver_id,
                "approved_at": evolution.approved_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to approve evolution {evolution_id}: {e}")
            return False, {"error": str(e)}

    async def get_evolution_status(
        self, evolution_id: str
    ) -> tuple[bool, dict[str, Any]]:
        """
        Get the status of an evolution cycle.

        Args:
            evolution_id: Evolution identifier

        Returns:
            Tuple of (found, status_info)
        """
        try:
            # Check active evolutions
            if evolution_id in self.active_evolutions:
                evolution = self.active_evolutions[evolution_id]
                return True, {
                    "evolution_id": evolution_id,
                    "status": evolution.status.value,
                    "type": evolution.evolution_type.value,
                    "description": evolution.description,
                    "created_at": evolution.created_at.isoformat(),
                    "estimated_duration": evolution.estimated_duration_minutes,
                    "requires_approval": self.manual_approval_required,
                    "progress": await self._get_evolution_progress(evolution_id),
                }

            # Check evolution history
            for result in self.evolution_history:
                if result.evolution_id == evolution_id:
                    return True, {
                        "evolution_id": evolution_id,
                        "status": result.status.value,
                        "success": result.success,
                        "completed_at": (
                            result.completed_at.isoformat()
                            if result.completed_at
                            else None
                        ),
                        "changes_applied": result.changes_applied,
                        "validation_results": result.validation_results,
                        "performance_metrics": result.performance_metrics,
                        "rollback_available": result.rollback_available,
                    }

            return False, {"error": "Evolution not found"}

        except Exception as e:
            logger.error(f"Failed to get evolution status {evolution_id}: {e}")
            return False, {"error": str(e)}

    async def rollback_evolution(
        self, evolution_id: str, rollback_reason: str = ""
    ) -> tuple[bool, dict[str, Any]]:
        """
        Rollback a completed evolution.

        Args:
            evolution_id: Evolution identifier
            rollback_reason: Reason for rollback

        Returns:
            Tuple of (success, rollback_info)
        """
        try:
            if not self.rollback_enabled:
                return False, {"error": "Rollback is disabled"}

            # Find evolution in history
            evolution_result = None
            for result in self.evolution_history:
                if result.evolution_id == evolution_id:
                    evolution_result = result
                    break

            if not evolution_result:
                return False, {"error": "Evolution not found in history"}

            if not evolution_result.rollback_available:
                return False, {"error": "Rollback not available for this evolution"}

            if evolution_result.status == EvolutionStatus.ROLLED_BACK:
                return False, {"error": "Evolution already rolled back"}

            # Execute rollback
            rollback_success = await self._execute_rollback(
                evolution_result, rollback_reason
            )

            if rollback_success:
                evolution_result.status = EvolutionStatus.ROLLED_BACK
                logger.info(f"Evolution {evolution_id} rolled back successfully")

                return True, {
                    "evolution_id": evolution_id,
                    "status": "rolled_back",
                    "rollback_reason": rollback_reason,
                    "rolled_back_at": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return False, {"error": "Rollback execution failed"}

        except Exception as e:
            logger.error(f"Failed to rollback evolution {evolution_id}: {e}")
            return False, {"error": str(e)}

    async def get_evolution_metrics(self) -> dict[str, Any]:
        """Get evolution engine performance metrics."""
        try:
            # Calculate current metrics
            total_evolutions = len(self.evolution_history) + len(self.active_evolutions)
            successful_evolutions = sum(
                1
                for result in self.evolution_history
                if result.success and result.status == EvolutionStatus.COMPLETED
            )

            # Calculate average duration
            completed_evolutions = [
                result
                for result in self.evolution_history
                if result.completed_at and result.status == EvolutionStatus.COMPLETED
            ]

            if completed_evolutions:
                total_duration = sum(
                    (result.completed_at - result.created_at).total_seconds() / 60
                    for result in completed_evolutions
                    if hasattr(result, "created_at")
                )
                average_duration = total_duration / len(completed_evolutions)
            else:
                average_duration = 0

            return {
                "total_evolutions": total_evolutions,
                "active_evolutions": len(self.active_evolutions),
                "successful_evolutions": successful_evolutions,
                "failed_evolutions": len(self.evolution_history)
                - successful_evolutions,
                "success_rate": successful_evolutions
                / max(len(self.evolution_history), 1),
                "average_duration_minutes": round(average_duration, 2),
                "human_approval_required": self.manual_approval_required,
                "rollback_enabled": self.rollback_enabled,
                "max_concurrent_evolutions": self.max_concurrent_evolutions,
                "constitution_hash": self.constitution_hash,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get evolution metrics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the evolution engine."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check service integrations
            for service_name, client in self.service_clients.items():
                try:
                    # Simple connectivity check - use the stored base URL
                    base_url = getattr(
                        client,
                        "_base_url",
                        f"http://localhost:800{list(self.service_clients.keys()).index(service_name)}",
                    )
                    async with client.get(f"{base_url}/health", timeout=5) as response:
                        if response.status == 200:
                            health_status["checks"][f"{service_name}_integration"] = {
                                "healthy": True,
                                "response_time_ms": response.headers.get(
                                    "X-Response-Time", "unknown"
                                ),
                            }
                        else:
                            health_status["checks"][f"{service_name}_integration"] = {
                                "healthy": False,
                                "status_code": response.status,
                            }
                            health_status["healthy"] = False
                except Exception as e:
                    health_status["checks"][f"{service_name}_integration"] = {
                        "healthy": False,
                        "error": str(e),
                    }
                    health_status["healthy"] = False

            # Check evolution engine status
            health_status["checks"]["evolution_engine"] = {
                "healthy": True,
                "active_evolutions": len(self.active_evolutions),
                "max_concurrent": self.max_concurrent_evolutions,
                "manual_approval_required": self.manual_approval_required,
            }

            return health_status

        except Exception as e:
            logger.error(f"Evolution engine health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the evolution engine gracefully."""
        try:
            logger.info("Shutting down evolution engine...")

            # Cancel active evolutions
            for evolution_id in list(self.active_evolutions.keys()):
                evolution = self.active_evolutions[evolution_id]
                evolution.status = EvolutionStatus.CANCELLED
                logger.info(f"Cancelled evolution {evolution_id}")

            # Close service clients
            for client in self.service_clients.values():
                await client.close()

            logger.info("✅ Evolution engine shutdown complete")

        except Exception as e:
            logger.error(f"Error during evolution engine shutdown: {e}")

    # Private helper methods
    async def _initialize_service_clients(self):
        """Initialize HTTP clients for ACGS-1 service integration."""
        service_urls = {
            "auth": self.settings.AUTH_SERVICE_URL,
            "ac": self.settings.AC_SERVICE_URL,
            "integrity": self.settings.INTEGRITY_SERVICE_URL,
            "fv": self.settings.FV_SERVICE_URL,
            "gs": self.settings.GS_SERVICE_URL,
            "pgc": self.settings.PGC_SERVICE_URL,
            "ec": self.settings.EC_SERVICE_URL,
        }

        for service_name, url in service_urls.items():
            timeout = aiohttp.ClientTimeout(total=self.settings.SERVICE_TIMEOUT)
            # Store the base URL separately since aiohttp ClientSession doesn't store it as an attribute
            self.service_clients[service_name] = aiohttp.ClientSession(timeout=timeout)
            # Store the base URL for later use
            self.service_clients[service_name]._base_url = url

        logger.info("Service clients initialized for ACGS-1 integration")

    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance and hash."""
        try:
            # Verify constitution hash matches Quantumagi deployment
            if self.constitution_hash != "cdd01ef066bc6cf2":
                raise ValueError(
                    f"Constitution hash mismatch: {self.constitution_hash}"
                )

            logger.info(
                f"✅ Constitutional compliance validated: {self.constitution_hash}"
            )

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            raise

    async def _validate_evolution_request(
        self, request: EvolutionRequest
    ) -> dict[str, Any]:
        """Validate evolution request for safety and compliance."""
        validation_result = {"valid": True, "errors": []}

        try:
            # Basic validation
            if not request.description:
                validation_result["errors"].append("Description is required")

            if not request.justification:
                validation_result["errors"].append("Justification is required")

            if not request.requester_id:
                validation_result["errors"].append("Requester ID is required")

            # Constitutional validation
            if request.requires_constitutional_validation:
                constitutional_check = await self._check_constitutional_compliance(
                    request
                )
                if not constitutional_check["compliant"]:
                    validation_result["errors"].extend(
                        constitutional_check["violations"]
                    )

            # Security validation
            security_check = await self.security_manager.validate_evolution_request(
                request
            )
            if not security_check["secure"]:
                validation_result["errors"].extend(security_check["security_issues"])

            validation_result["valid"] = len(validation_result["errors"]) == 0
            return validation_result

        except Exception as e:
            logger.error(f"Evolution request validation failed: {e}")
            return {"valid": False, "errors": [str(e)]}

    async def _check_constitutional_compliance(
        self, request: EvolutionRequest
    ) -> dict[str, Any]:
        """Check constitutional compliance for evolution request."""
        try:
            # Use AC service for constitutional validation
            async with self.service_clients["ac"].post(
                "/api/v1/constitutional/validate",
                json={
                    "evolution_type": request.evolution_type.value,
                    "proposed_changes": request.proposed_changes,
                    "constitution_hash": self.constitution_hash,
                },
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "compliant": result.get("compliant", False),
                        "violations": result.get("violations", []),
                        "confidence": result.get("confidence", 0),
                    }
                else:
                    return {
                        "compliant": False,
                        "violations": ["Constitutional validation service unavailable"],
                    }

        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e}")
            return {
                "compliant": False,
                "violations": [f"Constitutional validation error: {str(e)}"],
            }

    async def _validate_approver_permissions(
        self, approver_id: str, evolution: EvolutionRequest
    ) -> bool:
        """Validate approver has sufficient permissions."""
        try:
            # Use Auth service for permission validation
            async with self.service_clients["auth"].post(
                "/api/v1/auth/validate-permissions",
                json={
                    "user_id": approver_id,
                    "required_permissions": ["evolution_approval"],
                    "resource_type": "evolution",
                    "resource_id": evolution.evolution_id,
                },
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("authorized", False)
                else:
                    logger.error(f"Permission validation failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Approver permission validation failed: {e}")
            return False

    async def _execute_evolution_cycle(self, evolution_id: str):
        """Execute the complete evolution cycle."""
        try:
            evolution = self.active_evolutions[evolution_id]

            # Phase 1: Analysis
            evolution.status = EvolutionStatus.ANALYZING
            analysis_result = await self._analyze_evolution_impact(evolution)

            if not analysis_result["safe_to_proceed"]:
                await self._fail_evolution(evolution_id, "Analysis phase failed")
                return

            # Phase 2: Human approval (if required)
            if self.manual_approval_required:
                evolution.status = EvolutionStatus.PENDING_APPROVAL
                logger.info(f"Evolution {evolution_id} waiting for human approval")
                return  # Wait for manual approval

            # Phase 3: Execution
            await self._continue_evolution_after_approval(evolution_id)

        except Exception as e:
            logger.error(f"Evolution cycle execution failed for {evolution_id}: {e}")
            await self._fail_evolution(evolution_id, str(e))

    async def _continue_evolution_after_approval(self, evolution_id: str):
        """Continue evolution after human approval."""
        try:
            evolution = self.active_evolutions[evolution_id]

            # Phase 3: Execution
            evolution.status = EvolutionStatus.EXECUTING
            execution_result = await self._execute_evolution_changes(evolution)

            if not execution_result["success"]:
                await self._fail_evolution(evolution_id, "Execution phase failed")
                return

            # Phase 4: Validation
            evolution.status = EvolutionStatus.VALIDATING
            validation_result = await self._validate_evolution_results(evolution)

            if validation_result["valid"]:
                await self._complete_evolution(
                    evolution_id, execution_result, validation_result
                )
            else:
                await self._fail_evolution(evolution_id, "Validation phase failed")

        except Exception as e:
            logger.error(f"Evolution continuation failed for {evolution_id}: {e}")
            await self._fail_evolution(evolution_id, str(e))

    async def _analyze_evolution_impact(
        self, evolution: EvolutionRequest
    ) -> dict[str, Any]:
        """Analyze the potential impact of the evolution."""
        try:
            # Use FV service for formal verification
            async with self.service_clients["fv"].post(
                "/api/v1/formal-verification/analyze-impact",
                json={
                    "evolution_type": evolution.evolution_type.value,
                    "proposed_changes": evolution.proposed_changes,
                    "target_policies": evolution.target_policies,
                },
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "safe_to_proceed": result.get("safe", False),
                        "risk_level": result.get("risk_level", "unknown"),
                        "impact_assessment": result.get("impact", {}),
                    }
                else:
                    return {
                        "safe_to_proceed": False,
                        "error": "Analysis service unavailable",
                    }

        except Exception as e:
            logger.error(f"Evolution impact analysis failed: {e}")
            return {"safe_to_proceed": False, "error": str(e)}

    async def _execute_evolution_changes(
        self, evolution: EvolutionRequest
    ) -> dict[str, Any]:
        """Execute the actual evolution changes."""
        try:
            # Use GS service for policy synthesis and updates
            async with self.service_clients["gs"].post(
                "/api/v1/governance-synthesis/apply-evolution",
                json={
                    "evolution_id": evolution.evolution_id,
                    "evolution_type": evolution.evolution_type.value,
                    "proposed_changes": evolution.proposed_changes,
                    "target_policies": evolution.target_policies,
                },
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "changes_applied": result.get("changes_applied", {}),
                        "affected_policies": result.get("affected_policies", []),
                    }
                else:
                    return {
                        "success": False,
                        "error": "Evolution execution service unavailable",
                    }

        except Exception as e:
            logger.error(f"Evolution changes execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _validate_evolution_results(
        self, evolution: EvolutionRequest
    ) -> dict[str, Any]:
        """Validate the results of evolution changes."""
        try:
            validation_results = {}

            # Formal verification
            if evolution.requires_formal_verification:
                async with self.service_clients["fv"].post(
                    "/api/v1/formal-verification/validate-evolution",
                    json={
                        "evolution_id": evolution.evolution_id,
                        "target_policies": evolution.target_policies,
                    },
                ) as response:
                    if response.status == 200:
                        fv_result = await response.json()
                        validation_results["formal_verification"] = fv_result
                    else:
                        validation_results["formal_verification"] = {
                            "valid": False,
                            "error": "FV service unavailable",
                        }

            # Constitutional compliance check
            if evolution.requires_constitutional_validation:
                async with self.service_clients["ac"].post(
                    "/api/v1/constitutional/validate-evolution",
                    json={
                        "evolution_id": evolution.evolution_id,
                        "constitution_hash": self.constitution_hash,
                    },
                ) as response:
                    if response.status == 200:
                        cc_result = await response.json()
                        validation_results["constitutional_compliance"] = cc_result
                    else:
                        validation_results["constitutional_compliance"] = {
                            "valid": False,
                            "error": "CC service unavailable",
                        }

            # PGC enforcement validation
            async with self.service_clients["pgc"].post(
                "/api/v1/policy-governance/validate-evolution",
                json={
                    "evolution_id": evolution.evolution_id,
                    "target_policies": evolution.target_policies,
                },
            ) as response:
                if response.status == 200:
                    pgc_result = await response.json()
                    validation_results["policy_governance"] = pgc_result
                else:
                    validation_results["policy_governance"] = {
                        "valid": False,
                        "error": "PGC service unavailable",
                    }

            # Determine overall validity
            all_valid = all(
                result.get("valid", False) for result in validation_results.values()
            )

            return {
                "valid": all_valid,
                "validation_results": validation_results,
            }

        except Exception as e:
            logger.error(f"Evolution results validation failed: {e}")
            return {"valid": False, "error": str(e)}

    async def _complete_evolution(
        self,
        evolution_id: str,
        execution_result: dict[str, Any],
        validation_result: dict[str, Any],
    ):
        """Complete a successful evolution."""
        try:
            evolution = self.active_evolutions[evolution_id]

            # Create evolution result
            result = EvolutionResult(
                evolution_id=evolution_id,
                status=EvolutionStatus.COMPLETED,
                success=True,
                changes_applied=execution_result.get("changes_applied", {}),
                validation_results=validation_result.get("validation_results", {}),
                performance_metrics=await self._calculate_performance_metrics(
                    evolution
                ),
                completed_at=datetime.now(timezone.utc),
                rollback_available=True,
            )

            # Move to history
            self.evolution_history.append(result)
            del self.active_evolutions[evolution_id]

            # Update metrics
            self.evolution_metrics["successful_evolutions"] += 1

            # Log completion
            logger.info(f"Evolution {evolution_id} completed successfully")

            # Notify observability framework
            await self.observability_framework.record_evolution_completion(result)

        except Exception as e:
            logger.error(f"Failed to complete evolution {evolution_id}: {e}")
            await self._fail_evolution(evolution_id, str(e))

    async def _fail_evolution(self, evolution_id: str, error_message: str):
        """Handle evolution failure."""
        try:
            evolution = self.active_evolutions.get(evolution_id)
            if not evolution:
                return

            # Create failure result
            result = EvolutionResult(
                evolution_id=evolution_id,
                status=EvolutionStatus.FAILED,
                success=False,
                error_message=error_message,
                completed_at=datetime.now(timezone.utc),
                rollback_available=False,
            )

            # Move to history
            self.evolution_history.append(result)
            del self.active_evolutions[evolution_id]

            # Update metrics
            self.evolution_metrics["failed_evolutions"] += 1

            # Log failure
            logger.error(f"Evolution {evolution_id} failed: {error_message}")

            # Notify observability framework
            await self.observability_framework.record_evolution_failure(result)

        except Exception as e:
            logger.error(f"Failed to handle evolution failure for {evolution_id}: {e}")

    async def _execute_rollback(
        self, evolution_result: EvolutionResult, rollback_reason: str
    ) -> bool:
        """Execute rollback of evolution changes."""
        try:
            # Use GS service for rollback
            async with self.service_clients["gs"].post(
                "/api/v1/governance-synthesis/rollback-evolution",
                json={
                    "evolution_id": evolution_result.evolution_id,
                    "changes_to_rollback": evolution_result.changes_applied,
                    "rollback_reason": rollback_reason,
                },
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("success", False)
                else:
                    logger.error(f"Rollback service unavailable: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Rollback execution failed: {e}")
            return False

    async def _calculate_performance_metrics(
        self, evolution: EvolutionRequest
    ) -> dict[str, Any]:
        """Calculate performance metrics for completed evolution."""
        try:
            end_time = datetime.now(timezone.utc)
            duration_minutes = (end_time - evolution.created_at).total_seconds() / 60

            return {
                "duration_minutes": round(duration_minutes, 2),
                "estimated_duration_minutes": evolution.estimated_duration_minutes,
                "duration_variance": round(
                    duration_minutes - evolution.estimated_duration_minutes, 2
                ),
                "evolution_type": evolution.evolution_type.value,
                "target_policies_count": len(evolution.target_policies),
                "completed_at": end_time.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {"error": str(e)}

    async def _get_evolution_progress(self, evolution_id: str) -> dict[str, Any]:
        """Get current progress of an active evolution."""
        try:
            evolution = self.active_evolutions.get(evolution_id)
            if not evolution:
                return {"error": "Evolution not found"}

            # Calculate progress based on status
            progress_map = {
                EvolutionStatus.PENDING: 0,
                EvolutionStatus.INITIATED: 10,
                EvolutionStatus.ANALYZING: 25,
                EvolutionStatus.PENDING_APPROVAL: 40,
                EvolutionStatus.APPROVED: 50,
                EvolutionStatus.EXECUTING: 75,
                EvolutionStatus.VALIDATING: 90,
                EvolutionStatus.COMPLETED: 100,
                EvolutionStatus.FAILED: 0,
                EvolutionStatus.CANCELLED: 0,
            }

            progress_percent = progress_map.get(evolution.status, 0)

            return {
                "progress_percent": progress_percent,
                "current_phase": evolution.status.value,
                "estimated_completion": self._estimate_completion_time(evolution),
                "next_action": self._get_next_action(evolution),
            }

        except Exception as e:
            logger.error(f"Failed to get evolution progress: {e}")
            return {"error": str(e)}

    def _estimate_completion_time(self, evolution: EvolutionRequest) -> str:
        """Estimate completion time for evolution."""
        try:
            elapsed_minutes = (
                datetime.now(timezone.utc) - evolution.created_at
            ).total_seconds() / 60
            remaining_minutes = max(
                0, evolution.estimated_duration_minutes - elapsed_minutes
            )

            if remaining_minutes > 0:
                completion_time = datetime.now(timezone.utc).timestamp() + (
                    remaining_minutes * 60
                )
                return datetime.fromtimestamp(completion_time, timezone.utc).isoformat()
            else:
                return "overdue"

        except Exception as e:
            logger.error(f"Failed to estimate completion time: {e}")
            return "unknown"

    def _get_next_action(self, evolution: EvolutionRequest) -> str:
        """Get the next required action for evolution."""
        if evolution.status == EvolutionStatus.PENDING_APPROVAL:
            return "waiting_for_human_approval"
        elif evolution.status == EvolutionStatus.ANALYZING:
            return "analyzing_impact"
        elif evolution.status == EvolutionStatus.EXECUTING:
            return "applying_changes"
        elif evolution.status == EvolutionStatus.VALIDATING:
            return "validating_results"
        else:
            return "processing"

    async def _monitor_evolution_performance(self):
        """Background task to monitor evolution performance."""
        while True:
            try:
                # Check for overdue evolutions
                current_time = datetime.now(timezone.utc)

                for evolution_id, evolution in list(self.active_evolutions.items()):
                    elapsed_minutes = (
                        current_time - evolution.created_at
                    ).total_seconds() / 60

                    if (
                        elapsed_minutes > evolution.estimated_duration_minutes * 2
                    ):  # 2x overdue
                        logger.warning(
                            f"Evolution {evolution_id} is significantly overdue"
                        )

                        # Notify observability framework
                        await self.observability_framework.record_evolution_warning(
                            evolution_id, "significantly_overdue", elapsed_minutes
                        )

                # Update performance metrics
                await self._update_performance_metrics()

                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Evolution performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def _update_performance_metrics(self):
        """Update evolution performance metrics."""
        try:
            # Calculate success rate
            total_completed = len(self.evolution_history)
            if total_completed > 0:
                successful = sum(
                    1 for result in self.evolution_history if result.success
                )
                self.evolution_metrics["human_approval_rate"] = (
                    successful / total_completed
                )

            # Calculate average duration
            completed_evolutions = [
                result
                for result in self.evolution_history
                if result.completed_at and hasattr(result, "performance_metrics")
            ]

            if completed_evolutions:
                durations = [
                    result.performance_metrics.get("duration_minutes", 0)
                    for result in completed_evolutions
                    if result.performance_metrics
                ]
                if durations:
                    self.evolution_metrics["average_duration_minutes"] = sum(
                        durations
                    ) / len(durations)

        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
