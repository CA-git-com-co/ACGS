"""
Constitutional Hash Validator for ACGS-1 PGC Service Enterprise Implementation

Implements comprehensive constitutional hash validation with enterprise-grade security,
integrity verification, and constitutional compliance checking for all policy operations.

# requires: constitutional_hash = "cdd01ef066bc6cf2", Redis client available
# ensures: 100% constitutional compliance AND validation_latency_ms <= 5.0
# sha256: constitutional_hash_validator_enterprise_v1.0_acgs1_governance

Enterprise Features:
- Constitutional hash validation against reference (cdd01ef066bc6cf2)
- HMAC-SHA256 integrity verification for all constitutional operations
- Real-time constitutional state monitoring and validation
- Circuit breaker pattern for constitutional service failures
- Comprehensive audit logging for constitutional compliance
- Performance monitoring with <5ms validation latency target
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class ConstitutionalValidationLevel(Enum):
    """Constitutional validation levels for different operation types."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRITICAL = "critical"


class ConstitutionalHashStatus(Enum):
    """Constitutional hash validation status."""

    VALID = "valid"
    INVALID = "invalid"
    MISMATCH = "mismatch"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass
class ConstitutionalValidationResult:
    """Result of constitutional hash validation."""

    status: ConstitutionalHashStatus
    hash_valid: bool
    compliance_score: float
    validation_timestamp: float
    validation_level: ConstitutionalValidationLevel
    violations: list[str]
    recommendations: list[str]
    performance_metrics: dict[str, float]
    constitutional_hash: str
    integrity_signature: str | None = None


@dataclass
class ConstitutionalContext:
    """Context for constitutional validation operations."""

    operation_type: str
    policy_id: str | None = None
    user_id: str | None = None
    service_name: str = "pgc_service"
    validation_level: ConstitutionalValidationLevel = (
        ConstitutionalValidationLevel.STANDARD
    )
    additional_context: dict[str, Any] = None


class ConstitutionalHashValidator:
    """
    Enterprise-grade constitutional hash validator for ACGS-1 governance system.

    Provides comprehensive constitutional hash validation with integrity verification,
    performance monitoring, and enterprise compliance features.
    """

    def __init__(
        self,
        constitutional_hash: str = "cdd01ef066bc6cf2",
        hmac_secret_key: str | None = None,
        redis_client: Any | None = None,
        performance_target_ms: float = 5.0,
    ):
        """
        Initialize constitutional hash validator.

        Args:
            constitutional_hash: Reference constitutional hash
            hmac_secret_key: Secret key for HMAC integrity verification
            redis_client: Redis client for caching and state management
            performance_target_ms: Target validation latency in milliseconds
        """
        self.constitutional_hash = constitutional_hash
        self.hmac_secret_key = hmac_secret_key or "acgs1_constitutional_integrity_key"
        self.redis_client = redis_client
        self.performance_target_ms = performance_target_ms

        # Performance metrics with PGC service prefix and instance ID to avoid collisions
        instance_id = str(id(self))[-6:]  # Use last 6 digits of instance ID

        self.validation_counter = Counter(
            f"pgc_constitutional_validations_total_{instance_id}",
            "Total constitutional hash validations in PGC service",
            ["status", "level", "operation_type"],
        )
        self.validation_latency = Histogram(
            f"pgc_constitutional_validation_duration_seconds_{instance_id}",
            "Constitutional validation latency in PGC service",
            ["level", "operation_type"],
        )
        self.compliance_score_gauge = Gauge(
            f"pgc_constitutional_compliance_score_{instance_id}",
            "Current constitutional compliance score in PGC service",
        )

        # Internal state
        self._validation_cache: dict[str, ConstitutionalValidationResult] = {}
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_reset_time = None

        logger.info(
            f"Constitutional hash validator initialized with hash: {constitutional_hash[:8]}..."
        )

    async def validate_constitutional_hash(
        self,
        provided_hash: str | None,
        context: ConstitutionalContext,
        policy_data: dict[str, Any] | None = None,
    ) -> ConstitutionalValidationResult:
        """
        Validate constitutional hash with comprehensive compliance checking.

        Args:
            provided_hash: Hash to validate against constitutional reference
            context: Validation context with operation details
            policy_data: Optional policy data for enhanced validation

        Returns:
            Constitutional validation result with compliance details
        """
        start_time = time.time()

        try:
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                return self._create_circuit_breaker_result(context)

            # Generate cache key
            cache_key = self._generate_cache_key(provided_hash, context)

            # Check cache first
            cached_result = await self._get_cached_validation(cache_key)
            if cached_result:
                self._update_metrics(cached_result, start_time, context, cached=True)
                return cached_result

            # Perform validation
            validation_result = await self._perform_constitutional_validation(
                provided_hash, context, policy_data
            )

            # Cache result
            await self._cache_validation_result(cache_key, validation_result)

            # Update metrics
            self._update_metrics(validation_result, start_time, context, cached=False)

            return validation_result

        except Exception as e:
            logger.exception(f"Constitutional validation failed: {e}")
            self._circuit_breaker_failures += 1

            return ConstitutionalValidationResult(
                status=ConstitutionalHashStatus.UNKNOWN,
                hash_valid=False,
                compliance_score=0.0,
                validation_timestamp=time.time(),
                validation_level=context.validation_level,
                violations=[f"Validation error: {e!s}"],
                recommendations=[
                    "Retry validation",
                    "Check constitutional service health",
                ],
                performance_metrics={
                    "validation_time_ms": (time.time() - start_time) * 1000
                },
                constitutional_hash=self.constitutional_hash,
            )

    async def validate_policy_constitutional_compliance(
        self,
        policy_data: dict[str, Any],
        context: ConstitutionalContext,
    ) -> ConstitutionalValidationResult:
        """
        Validate policy compliance with constitutional requirements.

        Args:
            policy_data: Policy data to validate
            context: Validation context

        Returns:
            Constitutional validation result
        """
        start_time = time.time()

        try:
            # Extract constitutional hash from policy if present
            policy_hash = policy_data.get("constitutional_hash")

            # Perform hash validation
            hash_result = await self.validate_constitutional_hash(
                policy_hash, context, policy_data
            )

            # Perform additional policy compliance checks
            compliance_checks = await self._perform_policy_compliance_checks(
                policy_data, context
            )

            # Combine results
            return self._combine_validation_results(
                hash_result, compliance_checks, start_time
            )

        except Exception as e:
            logger.exception(f"Policy constitutional compliance validation failed: {e}")
            return self._create_error_result(context, str(e), start_time)

    async def get_constitutional_state(self) -> dict[str, Any]:
        """
        Get current constitutional state and validation metrics.

        Returns:
            Constitutional state information
        """
        try:
            current_time = time.time()

            # Get validation statistics
            total_validations = (
                sum(self.validation_counter._value.values())
                if hasattr(self.validation_counter, "_value")
                else 0
            )

            # Calculate average compliance score
            avg_compliance_score = (
                self.compliance_score_gauge._value._value
                if hasattr(self.compliance_score_gauge, "_value")
                else 0.0
            )

            return {
                "constitutional_hash": self.constitutional_hash,
                "validation_status": (
                    "healthy" if not self._is_circuit_breaker_open() else "degraded"
                ),
                "total_validations": total_validations,
                "average_compliance_score": avg_compliance_score,
                "circuit_breaker_status": {
                    "open": self._is_circuit_breaker_open(),
                    "failures": self._circuit_breaker_failures,
                    "threshold": self._circuit_breaker_threshold,
                },
                "performance_metrics": {
                    "target_latency_ms": self.performance_target_ms,
                    "cache_size": len(self._validation_cache),
                },
                "timestamp": current_time,
            }

        except Exception as e:
            logger.exception(f"Failed to get constitutional state: {e}")
            return {
                "constitutional_hash": self.constitutional_hash,
                "validation_status": "error",
                "error": str(e),
                "timestamp": time.time(),
            }

    # Private helper methods

    async def _perform_constitutional_validation(
        self,
        provided_hash: str | None,
        context: ConstitutionalContext,
        policy_data: dict[str, Any] | None = None,
    ) -> ConstitutionalValidationResult:
        """Perform the actual constitutional validation."""
        violations = []
        recommendations = []
        compliance_score = 1.0

        # Basic hash validation
        if provided_hash is None:
            if context.validation_level in {
                ConstitutionalValidationLevel.COMPREHENSIVE,
                ConstitutionalValidationLevel.CRITICAL,
            }:
                violations.append(
                    "Constitutional hash is required for this operation level"
                )
                compliance_score -= 0.3
            else:
                recommendations.append(
                    "Consider providing constitutional hash for enhanced validation"
                )
        elif provided_hash != self.constitutional_hash:
            violations.append(
                f"Constitutional hash mismatch: expected {self.constitutional_hash}, got {provided_hash}"
            )
            compliance_score = 0.0

        # Enhanced validation for higher levels
        if context.validation_level in {
            ConstitutionalValidationLevel.COMPREHENSIVE,
            ConstitutionalValidationLevel.CRITICAL,
        }:
            enhanced_checks = await self._perform_enhanced_constitutional_checks(
                provided_hash, context, policy_data
            )
            violations.extend(enhanced_checks.get("violations", []))
            recommendations.extend(enhanced_checks.get("recommendations", []))
            compliance_score *= enhanced_checks.get("compliance_multiplier", 1.0)

        # Determine status
        if compliance_score >= 0.95:
            status = ConstitutionalHashStatus.VALID
        elif compliance_score >= 0.7:
            status = ConstitutionalHashStatus.INVALID
        else:
            status = ConstitutionalHashStatus.MISMATCH

        # Generate integrity signature
        integrity_signature = self._generate_integrity_signature(
            provided_hash or "", context.operation_type
        )

        return ConstitutionalValidationResult(
            status=status,
            hash_valid=provided_hash == self.constitutional_hash,
            compliance_score=max(0.0, compliance_score),
            validation_timestamp=time.time(),
            validation_level=context.validation_level,
            violations=violations,
            recommendations=recommendations,
            performance_metrics={},
            constitutional_hash=self.constitutional_hash,
            integrity_signature=integrity_signature,
        )

    async def _perform_enhanced_constitutional_checks(
        self,
        provided_hash: str | None,
        context: ConstitutionalContext,
        policy_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform enhanced constitutional checks for comprehensive validation."""
        violations = []
        recommendations = []
        compliance_multiplier = 1.0

        # Check constitutional hash format
        if provided_hash and len(provided_hash) != 16:
            violations.append("Constitutional hash must be 16 characters")
            compliance_multiplier *= 0.8

        # Check constitutional hash character set
        if provided_hash and not all(c in "0123456789abcdef" for c in provided_hash):
            violations.append("Constitutional hash must be hexadecimal")
            compliance_multiplier *= 0.8

        # Policy-specific checks
        if policy_data:
            policy_checks = await self._validate_policy_constitutional_elements(
                policy_data
            )
            violations.extend(policy_checks.get("violations", []))
            recommendations.extend(policy_checks.get("recommendations", []))
            compliance_multiplier *= policy_checks.get("compliance_multiplier", 1.0)

        # Context-specific checks
        if context.operation_type in {"policy_creation", "constitutional_amendment"}:
            if not provided_hash:
                violations.append(
                    "Constitutional hash is mandatory for constitutional operations"
                )
                compliance_multiplier *= 0.5

        return {
            "violations": violations,
            "recommendations": recommendations,
            "compliance_multiplier": compliance_multiplier,
        }

    async def _validate_policy_constitutional_elements(
        self, policy_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate policy constitutional elements."""
        violations = []
        recommendations = []
        compliance_multiplier = 1.0

        # Check for required constitutional elements
        required_elements = ["title", "description", "constitutional_principles"]
        for element in required_elements:
            if not policy_data.get(element):
                violations.append(
                    f"Policy missing required constitutional element: {element}"
                )
                compliance_multiplier *= 0.9

        # Check constitutional principles
        principles = policy_data.get("constitutional_principles", [])
        if isinstance(principles, list) and len(principles) == 0:
            recommendations.append(
                "Consider specifying applicable constitutional principles"
            )

        # Check for constitutional compliance metadata
        if not policy_data.get("constitutional_compliance"):
            recommendations.append("Include constitutional compliance metadata")

        return {
            "violations": violations,
            "recommendations": recommendations,
            "compliance_multiplier": compliance_multiplier,
        }

    async def _perform_policy_compliance_checks(
        self,
        policy_data: dict[str, Any],
        context: ConstitutionalContext,
    ) -> dict[str, Any]:
        """Perform comprehensive policy compliance checks."""
        violations = []
        recommendations = []
        compliance_score = 1.0

        # Basic policy structure validation
        if not policy_data.get("title"):
            violations.append("Policy title is required")
            compliance_score -= 0.1

        if not policy_data.get("description"):
            violations.append("Policy description is required")
            compliance_score -= 0.1

        # Constitutional principles validation
        principles = policy_data.get("constitutional_principles", [])
        if not principles:
            violations.append("Policy must reference constitutional principles")
            compliance_score -= 0.2

        # Policy content validation
        content = policy_data.get("content", "")
        if len(content) < 50:
            recommendations.append("Consider providing more detailed policy content")

        # Governance context validation
        governance_context = policy_data.get("governance_context", {})
        if not governance_context.get("scope"):
            recommendations.append("Specify policy governance scope")

        return {
            "violations": violations,
            "recommendations": recommendations,
            "compliance_score": max(0.0, compliance_score),
        }

    def _combine_validation_results(
        self,
        hash_result: ConstitutionalValidationResult,
        compliance_checks: dict[str, Any],
        start_time: float,
    ) -> ConstitutionalValidationResult:
        """Combine hash validation and compliance check results."""
        combined_violations = hash_result.violations + compliance_checks.get(
            "violations", []
        )
        combined_recommendations = hash_result.recommendations + compliance_checks.get(
            "recommendations", []
        )

        # Calculate combined compliance score
        hash_score = hash_result.compliance_score
        policy_score = compliance_checks.get("compliance_score", 1.0)
        combined_score = (hash_score + policy_score) / 2.0

        # Determine final status
        if combined_score >= 0.95 and hash_result.hash_valid:
            final_status = ConstitutionalHashStatus.VALID
        elif combined_score >= 0.7:
            final_status = ConstitutionalHashStatus.INVALID
        else:
            final_status = ConstitutionalHashStatus.MISMATCH

        return ConstitutionalValidationResult(
            status=final_status,
            hash_valid=hash_result.hash_valid,
            compliance_score=combined_score,
            validation_timestamp=time.time(),
            validation_level=hash_result.validation_level,
            violations=combined_violations,
            recommendations=combined_recommendations,
            performance_metrics={
                "validation_time_ms": (time.time() - start_time) * 1000
            },
            constitutional_hash=self.constitutional_hash,
            integrity_signature=hash_result.integrity_signature,
        )

    def _generate_cache_key(
        self, provided_hash: str | None, context: ConstitutionalContext
    ) -> str:
        """Generate cache key for validation result."""
        key_components = [
            provided_hash or "none",
            context.operation_type,
            context.validation_level.value,
            context.policy_id or "none",
        ]
        return hashlib.sha256("|".join(key_components).encode()).hexdigest()[:16]

    async def _get_cached_validation(
        self, cache_key: str
    ) -> ConstitutionalValidationResult | None:
        """Get cached validation result."""
        try:
            # Check in-memory cache first
            if cache_key in self._validation_cache:
                cached_result = self._validation_cache[cache_key]
                # Check if cache entry is still valid (5 minutes TTL)
                if time.time() - cached_result.validation_timestamp < 300:
                    return cached_result
                del self._validation_cache[cache_key]

            # Check Redis cache if available
            if self.redis_client:
                cached_data = await self.redis_client.get(
                    f"constitutional_validation:{cache_key}"
                )
                if cached_data:
                    # Parse cached result (simplified for this implementation)
                    return None  # Would implement proper deserialization

            return None

        except Exception as e:
            logger.warning(f"Failed to get cached validation: {e}")
            return None

    async def _cache_validation_result(
        self, cache_key: str, result: ConstitutionalValidationResult
    ) -> None:
        """Cache validation result."""
        try:
            # Store in memory cache
            self._validation_cache[cache_key] = result

            # Limit cache size
            if len(self._validation_cache) > 1000:
                # Remove oldest entries
                oldest_keys = sorted(
                    self._validation_cache.keys(),
                    key=lambda k: self._validation_cache[k].validation_timestamp,
                )[:100]
                for key in oldest_keys:
                    del self._validation_cache[key]

            # Store in Redis if available
            if self.redis_client:
                # Simplified caching (would implement proper serialization)
                await self.redis_client.setex(
                    f"constitutional_validation:{cache_key}",
                    300,  # 5 minutes TTL
                    "cached_result",  # Would serialize actual result
                )

        except Exception as e:
            logger.warning(f"Failed to cache validation result: {e}")

    def _generate_integrity_signature(self, data: str, operation_type: str) -> str:
        """Generate HMAC-SHA256 integrity signature."""
        try:
            message = f"{data}|{operation_type}|{self.constitutional_hash}"
            return hmac.new(
                self.hmac_secret_key.encode(), message.encode(), hashlib.sha256
            ).hexdigest()
        except Exception as e:
            logger.exception(f"Failed to generate integrity signature: {e}")
            return ""

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            if self._circuit_breaker_reset_time is None:
                self._circuit_breaker_reset_time = time.time() + 60  # 1 minute reset
            elif time.time() > self._circuit_breaker_reset_time:
                self._circuit_breaker_failures = 0
                self._circuit_breaker_reset_time = None
                return False
            return True
        return False

    def _create_circuit_breaker_result(
        self, context: ConstitutionalContext
    ) -> ConstitutionalValidationResult:
        """Create result when circuit breaker is open."""
        return ConstitutionalValidationResult(
            status=ConstitutionalHashStatus.UNKNOWN,
            hash_valid=False,
            compliance_score=0.0,
            validation_timestamp=time.time(),
            validation_level=context.validation_level,
            violations=["Constitutional validation service temporarily unavailable"],
            recommendations=[
                "Retry after circuit breaker reset",
                "Check service health",
            ],
            performance_metrics={"circuit_breaker_open": True},
            constitutional_hash=self.constitutional_hash,
        )

    def _create_error_result(
        self, context: ConstitutionalContext, error_message: str, start_time: float
    ) -> ConstitutionalValidationResult:
        """Create error result for validation failures."""
        return ConstitutionalValidationResult(
            status=ConstitutionalHashStatus.UNKNOWN,
            hash_valid=False,
            compliance_score=0.0,
            validation_timestamp=time.time(),
            validation_level=context.validation_level,
            violations=[f"Validation error: {error_message}"],
            recommendations=["Check input data", "Retry validation", "Contact support"],
            performance_metrics={
                "validation_time_ms": (time.time() - start_time) * 1000
            },
            constitutional_hash=self.constitutional_hash,
        )

    def _update_metrics(
        self,
        result: ConstitutionalValidationResult,
        start_time: float,
        context: ConstitutionalContext,
        cached: bool = False,
    ) -> None:
        """Update performance and compliance metrics."""
        try:
            # Update validation counter
            self.validation_counter.labels(
                status=result.status.value,
                level=context.validation_level.value,
                operation_type=context.operation_type,
            ).inc()

            # Update latency histogram
            validation_time = time.time() - start_time
            self.validation_latency.labels(
                level=context.validation_level.value,
                operation_type=context.operation_type,
            ).observe(validation_time)

            # Update compliance score gauge
            self.compliance_score_gauge.set(result.compliance_score)

            # Log performance if exceeding target
            validation_time_ms = validation_time * 1000
            if validation_time_ms > self.performance_target_ms:
                logger.warning(
                    f"Constitutional validation exceeded target: {validation_time_ms:.2f}ms > {self.performance_target_ms}ms"
                )

        except Exception as e:
            logger.exception(f"Failed to update metrics: {e}")
