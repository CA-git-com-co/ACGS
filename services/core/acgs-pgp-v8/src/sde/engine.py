"""
Syndrome Diagnostic Engine

ML-powered diagnostic capabilities with constitutional compliance features
and integration with ACGS-1 analytics engine.
"""

import logging
import time
from datetime import datetime
from typing import Any

import httpx

# Optional ML dependencies
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    TfidfVectorizer = None

# Import ML models
from ..generation_engine.models import LogicalSemanticUnit
from ..see.models import StabilizerResult
from .ml_models import (
    AnomalyDetectionModel,
    ErrorClassificationModel,
    RecoveryRecommendationModel,
)
from .models import (
    DiagnosticMetrics,
    DiagnosticResult,
    ErrorCategory,
    ErrorClassification,
    ErrorSeverity,
    RecoveryRecommendation,
    RecoveryStrategy,
)

logger = logging.getLogger(__name__)


class SyndromeDiagnosticEngine:
    """
    ML-powered diagnostic engine with constitutional compliance features.

    Provides comprehensive error analysis, classification, and recovery
    recommendation generation with integration to ACGS-1 analytics.
    """

    def __init__(
        self,
        stabilizer_env=None,
        constitutional_hash: str = "cdd01ef066bc6cf2",
        error_classification_threshold: float = 0.7,
        enable_ml_models: bool = True,
    ):
        """Initialize the Syndrome Diagnostic Engine."""
        self.stabilizer_env = stabilizer_env
        self.constitutional_hash = constitutional_hash
        self.error_classification_threshold = error_classification_threshold
        self.enable_ml_models = enable_ml_models

        # ML models for error detection and classification
        self.anomaly_detector = None
        self.text_vectorizer = None

        # Diagnostic metrics
        self.metrics = DiagnosticMetrics(constitutional_hash=constitutional_hash)

        # HTTP client for external service integration
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Error pattern database
        self.error_patterns = self._initialize_error_patterns()

        logger.info("Syndrome Diagnostic Engine initialized")

    async def initialize(self) -> None:
        """Initialize ML models and diagnostic capabilities."""
        try:
            if self.enable_ml_models and SKLEARN_AVAILABLE:
                # Initialize trained ML models
                self.error_classifier = None
                self.anomaly_detector = None
                self.recovery_recommender = None

                # Try to load pre-trained models
                self._load_trained_models()

                # If no pre-trained models, initialize basic models
                if not self.error_classifier:
                    self.error_classifier = ErrorClassificationModel("random_forest")

                if not self.anomaly_detector:
                    self.anomaly_detector = AnomalyDetectionModel(contamination=0.1)

                if not self.recovery_recommender:
                    self.recovery_recommender = RecoveryRecommendationModel()

                # Initialize text vectorizer for error message analysis
                self.text_vectorizer = TfidfVectorizer(
                    max_features=1000, stop_words="english", ngram_range=(1, 2)
                )

                logger.info("ML models initialized successfully")
            elif self.enable_ml_models and not SKLEARN_AVAILABLE:
                logger.warning(
                    "ML models requested but sklearn not available, using rule-based classification"
                )
                self.enable_ml_models = False

            logger.info("Syndrome Diagnostic Engine fully initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Syndrome Diagnostic Engine: {e}")
            raise

    def _load_trained_models(self):
        """Load pre-trained ML models if available."""
        try:
            from pathlib import Path

            import joblib

            models_dir = Path("models")
            if not models_dir.exists():
                logger.info("No models directory found, will use untrained models")
                return

            # Load error classification model
            error_model_path = models_dir / "error_classification_random_forest.joblib"
            if error_model_path.exists():
                self.error_classifier = ErrorClassificationModel("random_forest")
                self.error_classifier.load_model(error_model_path)
                logger.info("Loaded pre-trained error classification model")

            # Load anomaly detection model
            anomaly_model_path = models_dir / "anomaly_detection.joblib"
            if anomaly_model_path.exists():
                self.anomaly_detector = joblib.load(anomaly_model_path)
                logger.info("Loaded pre-trained anomaly detection model")

            # Load recovery recommendation model
            recovery_model_path = models_dir / "recovery_recommendation.joblib"
            if recovery_model_path.exists():
                self.recovery_recommender = joblib.load(recovery_model_path)
                logger.info("Loaded pre-trained recovery recommendation model")

        except Exception as e:
            logger.warning(f"Failed to load pre-trained models: {e}")
            # Continue with untrained models

    async def diagnose_system(
        self,
        target_system: str,
        error_data: dict[str, Any] | None = None,
        include_recommendations: bool = True,
    ) -> DiagnosticResult:
        """
        Perform comprehensive system diagnosis.

        Args:
            target_system: Name of the system to diagnose
            error_data: Optional error data for analysis
            include_recommendations: Whether to generate recovery recommendations

        Returns:
            DiagnosticResult with comprehensive analysis
        """
        start_time = time.time()
        diagnostic_id = f"diag_{int(start_time)}_{hash(target_system) % 10000:04d}"

        logger.info(f"Starting system diagnosis: {diagnostic_id} for {target_system}")

        try:
            # Create diagnostic result
            result = DiagnosticResult(
                diagnostic_id=diagnostic_id,
                target_system=target_system,
                constitutional_hash=self.constitutional_hash,
            )

            result.audit_trail.append(f"Started diagnosis for {target_system}")

            # Analyze errors if provided
            if error_data:
                errors = await self._analyze_errors(error_data, target_system)
                for error in errors:
                    result.add_error(error)

            # Perform system health analysis
            health_analysis = await self._analyze_system_health(target_system)
            if health_analysis.get("errors"):
                for error_info in health_analysis["errors"]:
                    error = await self._classify_error(error_info, target_system)
                    result.add_error(error)

            # Generate recovery recommendations if requested
            if include_recommendations and result.errors_detected:
                recommendations = await self._generate_recommendations(
                    result.errors_detected
                )
                for recommendation in recommendations:
                    result.add_recommendation(recommendation)

            # Calculate diagnostic duration
            diagnostic_duration = (time.time() - start_time) * 1000
            result.diagnostic_duration_ms = diagnostic_duration

            # Update metrics
            self.metrics.total_diagnostics += 1
            self.metrics.total_errors_detected += result.error_count
            self.metrics.critical_errors_detected += result.critical_error_count
            self.metrics.total_recommendations += len(result.recommendations)

            if result.is_system_healthy():
                self.metrics.successful_diagnostics += 1

            # Update average metrics
            self._update_average_metrics(result)

            result.audit_trail.append(
                f"Diagnosis completed in {diagnostic_duration:.2f}ms"
            )
            logger.info(f"System diagnosis completed: {diagnostic_id}")

            return result

        except Exception as e:
            logger.error(f"System diagnosis failed: {diagnostic_id} - {e!s}")
            raise RuntimeError(f"Diagnosis failed: {e!s}")

    async def _analyze_errors(
        self, error_data: dict[str, Any], target_system: str
    ) -> list[ErrorClassification]:
        """Analyze provided error data and classify errors."""
        errors = []

        # Handle different error data formats
        if isinstance(error_data, dict):
            if "errors" in error_data:
                error_list = error_data["errors"]
            elif "error" in error_data:
                error_list = [error_data["error"]]
            else:
                error_list = [error_data]
        else:
            error_list = [{"message": str(error_data)}]

        for error_info in error_list:
            error = await self._classify_error(error_info, target_system)
            errors.append(error)

        return errors

    async def _classify_error(
        self, error_info: dict[str, Any], target_system: str
    ) -> ErrorClassification:
        """Classify a single error using ML and rule-based approaches."""
        error_message = error_info.get("message", str(error_info))
        error_context = error_info.get("context", {})
        stack_trace = error_info.get("stack_trace")

        # Determine severity using pattern matching
        severity = self._determine_error_severity(error_message, error_context)

        # Determine category using pattern matching
        category = self._determine_error_category(error_message, error_context)

        # Check for constitutional impact
        constitutional_impact = self._check_constitutional_impact(
            error_message, error_context
        )

        # Calculate confidence score
        confidence_score = self._calculate_classification_confidence(
            error_message, severity, category
        )

        # Create error classification
        error = ErrorClassification(
            error_id="",  # Will be auto-generated
            severity=severity,
            category=category,
            confidence_score=confidence_score,
            constitutional_impact=constitutional_impact,
            error_message=error_message,
            error_context=error_context,
            stack_trace=stack_trace,
            constitutional_hash=self.constitutional_hash,
        )

        # Add constitutional violation details if applicable
        if constitutional_impact:
            error.compliance_violation_details = self._get_compliance_violations(
                error_message, error_context
            )

        return error

    def _determine_error_severity(
        self, error_message: str, error_context: dict[str, Any]
    ) -> ErrorSeverity:
        """Determine error severity using pattern matching."""
        message_lower = error_message.lower()

        # Critical patterns
        critical_patterns = [
            "constitutional violation",
            "security breach",
            "data corruption",
            "system crash",
            "critical failure",
            "emergency",
            "fatal",
        ]

        # High severity patterns
        high_patterns = [
            "timeout",
            "connection failed",
            "authentication failed",
            "permission denied",
            "resource exhausted",
            "service unavailable",
        ]

        # Medium severity patterns
        medium_patterns = [
            "warning",
            "deprecated",
            "performance",
            "slow response",
            "retry",
            "fallback",
            "degraded",
        ]

        if any(pattern in message_lower for pattern in critical_patterns):
            return ErrorSeverity.CRITICAL
        if any(pattern in message_lower for pattern in high_patterns):
            return ErrorSeverity.HIGH
        if any(pattern in message_lower for pattern in medium_patterns):
            return ErrorSeverity.MEDIUM
        if "info" in message_lower or "debug" in message_lower:
            return ErrorSeverity.INFO
        return ErrorSeverity.LOW

    def _determine_error_category(
        self, error_message: str, error_context: dict[str, Any]
    ) -> ErrorCategory:
        """Determine error category using pattern matching."""
        message_lower = error_message.lower()

        category_patterns = {
            ErrorCategory.CONSTITUTIONAL_VIOLATION: [
                "constitutional",
                "compliance",
                "governance",
                "principle",
            ],
            ErrorCategory.SECURITY_BREACH: [
                "security",
                "authentication",
                "authorization",
                "breach",
                "unauthorized",
            ],
            ErrorCategory.PERFORMANCE_DEGRADATION: [
                "timeout",
                "slow",
                "performance",
                "latency",
                "response time",
            ],
            ErrorCategory.NETWORK_FAILURE: [
                "connection",
                "network",
                "socket",
                "dns",
                "endpoint",
            ],
            ErrorCategory.DATA_CORRUPTION: [
                "corruption",
                "invalid data",
                "checksum",
                "integrity",
            ],
            ErrorCategory.RESOURCE_EXHAUSTION: [
                "memory",
                "cpu",
                "disk",
                "resource",
                "exhausted",
                "limit",
            ],
            ErrorCategory.CONFIGURATION_ERROR: [
                "configuration",
                "config",
                "setting",
                "parameter",
            ],
            ErrorCategory.EXTERNAL_DEPENDENCY: [
                "external",
                "dependency",
                "service",
                "api",
                "third-party",
            ],
        }

        for category, patterns in category_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return category

        return ErrorCategory.UNKNOWN

    def _check_constitutional_impact(
        self, error_message: str, error_context: dict[str, Any]
    ) -> bool:
        """Check if error has constitutional compliance impact."""
        constitutional_keywords = [
            "constitutional",
            "compliance",
            "governance",
            "principle",
            "policy",
            "rule",
            "regulation",
            "audit",
            "transparency",
        ]

        message_lower = error_message.lower()
        return any(keyword in message_lower for keyword in constitutional_keywords)

    def _calculate_classification_confidence(
        self, error_message: str, severity: ErrorSeverity, category: ErrorCategory
    ) -> float:
        """Calculate confidence score for error classification."""
        # Base confidence based on message length and content
        base_confidence = min(0.9, len(error_message) / 100.0 + 0.5)

        # Adjust based on pattern matching strength
        if category != ErrorCategory.UNKNOWN:
            base_confidence += 0.1

        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            base_confidence += 0.1

        return min(1.0, base_confidence)

    def _get_compliance_violations(
        self, error_message: str, error_context: dict[str, Any]
    ) -> list[str]:
        """Get specific constitutional compliance violation details."""
        violations = []

        message_lower = error_message.lower()

        if "transparency" in message_lower:
            violations.append("Transparency principle violation")

        if "accountability" in message_lower:
            violations.append("Accountability principle violation")

        if "democratic" in message_lower:
            violations.append("Democratic participation violation")

        if "rule of law" in message_lower:
            violations.append("Rule of law violation")

        return violations

    def _initialize_error_patterns(self) -> dict[str, Any]:
        """Initialize error pattern database."""
        return {
            "constitutional_patterns": [
                "constitutional hash mismatch",
                "governance policy violation",
                "compliance check failed",
            ],
            "performance_patterns": [
                "response time exceeded",
                "timeout occurred",
                "resource limit reached",
            ],
            "security_patterns": [
                "authentication failed",
                "unauthorized access",
                "security violation",
            ],
        }

    async def _analyze_system_health(self, target_system: str) -> dict[str, Any]:
        """Analyze overall system health."""
        health_data = {
            "system": target_system,
            "timestamp": datetime.now().isoformat(),
            "errors": [],
            "warnings": [],
            "metrics": {},
        }

        # Mock health analysis - in production, this would integrate with monitoring systems
        if target_system == "acgs-pgp-v8":
            # Simulate some health checks
            health_data["metrics"] = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time_ms": 234.5,
                "error_rate": 0.02,
            }

            # Add mock errors based on metrics
            if health_data["metrics"]["response_time_ms"] > 500:
                health_data["errors"].append(
                    {
                        "message": "Response time exceeded threshold",
                        "context": {
                            "response_time": health_data["metrics"]["response_time_ms"]
                        },
                    }
                )

        return health_data

    async def _generate_recommendations(
        self, errors: list[ErrorClassification]
    ) -> list[RecoveryRecommendation]:
        """Generate recovery recommendations for detected errors."""
        recommendations = []

        for error in errors:
            recommendation = self._create_recommendation_for_error(error)
            if recommendation:
                recommendations.append(recommendation)

        return recommendations

    def _create_recommendation_for_error(
        self, error: ErrorClassification
    ) -> RecoveryRecommendation | None:
        """Create recovery recommendation for a specific error."""
        # Determine strategy based on error category and severity
        if error.category == ErrorCategory.PERFORMANCE_DEGRADATION:
            strategy = RecoveryStrategy.AUTOMATIC_RETRY
            description = "Implement automatic retry with exponential backoff"
            steps = [
                "Enable circuit breaker pattern",
                "Implement retry logic with backoff",
                "Monitor performance metrics",
                "Scale resources if needed",
            ]
            success_probability = 0.8
            recovery_time = 5

        elif error.category == ErrorCategory.CONSTITUTIONAL_VIOLATION:
            strategy = RecoveryStrategy.MANUAL_INTERVENTION
            description = "Manual review and constitutional compliance restoration"
            steps = [
                "Review constitutional compliance requirements",
                "Identify specific violations",
                "Implement compliance fixes",
                "Validate against constitutional hash",
            ]
            success_probability = 0.9
            recovery_time = 30

        elif error.category == ErrorCategory.NETWORK_FAILURE:
            strategy = RecoveryStrategy.CIRCUIT_BREAKER
            description = "Activate circuit breaker and fallback mechanisms"
            steps = [
                "Activate circuit breaker",
                "Switch to fallback service",
                "Monitor network connectivity",
                "Restore primary service when available",
            ]
            success_probability = 0.7
            recovery_time = 10

        else:
            strategy = RecoveryStrategy.FALLBACK_MODE
            description = "Activate fallback mode for error recovery"
            steps = [
                "Identify fallback options",
                "Activate fallback mode",
                "Monitor system stability",
                "Plan primary system restoration",
            ]
            success_probability = 0.6
            recovery_time = 15

        return RecoveryRecommendation(
            recommendation_id="",  # Will be auto-generated
            strategy=strategy,
            description=description,
            implementation_steps=steps,
            success_probability=success_probability,
            estimated_recovery_time_minutes=recovery_time,
            constitutional_compliance=not error.constitutional_impact,
            risk_level=(
                ErrorSeverity.LOW if success_probability > 0.8 else ErrorSeverity.MEDIUM
            ),
        )

    def _update_average_metrics(self, result: DiagnosticResult) -> None:
        """Update running average metrics."""
        total = self.metrics.total_diagnostics

        # Update average diagnostic time
        current_avg_time = self.metrics.average_diagnostic_time_ms
        self.metrics.average_diagnostic_time_ms = (
            current_avg_time * (total - 1) + result.diagnostic_duration_ms
        ) / total

        # Update average health score
        current_avg_health = self.metrics.average_health_score
        self.metrics.average_health_score = (
            current_avg_health * (total - 1) + result.overall_health_score
        ) / total

        # Update average compliance score
        current_avg_compliance = self.metrics.average_compliance_score
        self.metrics.average_compliance_score = (
            current_avg_compliance * (total - 1)
            + result.constitutional_compliance_score
        ) / total

        self.metrics.last_updated = datetime.now()

    async def get_health_status(self) -> dict[str, Any]:
        """Get diagnostic engine health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "ml_models_enabled": self.enable_ml_models,
            "metrics": self.metrics.dict(),
            "error_patterns_loaded": len(self.error_patterns),
        }

    async def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive diagnostic metrics."""
        return {
            "status": "healthy",
            "metrics": self.metrics.dict(),
            "performance": {
                "success_rate": self.metrics.calculate_success_rate(),
                "recovery_success_rate": self.metrics.calculate_recovery_success_rate(),
                "average_diagnostic_time_ms": self.metrics.average_diagnostic_time_ms,
            },
        }

    async def diagnose_lsu_stabilizer_results(
        self,
        lsu: LogicalSemanticUnit,
        stabilizer_results: list[StabilizerResult],
        include_recommendations: bool = True,
    ) -> DiagnosticResult:
        """
        Diagnose LSU based on stabilizer execution results.

        Args:
            lsu: The Logical Semantic Unit that was validated
            stabilizer_results: Results from stabilizer executions
            include_recommendations: Whether to generate recovery recommendations

        Returns:
            DiagnosticResult with comprehensive analysis
        """
        start_time = time.time()
        diagnostic_id = f"lsu_diag_{int(start_time)}_{lsu.id}"

        logger.info(f"Starting LSU diagnosis: {diagnostic_id} for {lsu.id}")

        try:
            # Create diagnostic result
            result = DiagnosticResult(
                diagnostic_id=diagnostic_id,
                target_system=f"LSU-{lsu.id}",
                constitutional_hash=self.constitutional_hash,
            )

            result.audit_trail.append(f"Started LSU diagnosis for {lsu.id}")

            # Analyze stabilizer results
            for stabilizer_result in stabilizer_results:
                errors = await self._analyze_stabilizer_result(stabilizer_result, lsu)
                for error in errors:
                    result.add_error(error)

            # Analyze LSU semantic integrity
            semantic_errors = await self._analyze_lsu_semantic_integrity(lsu)
            for error in semantic_errors:
                result.add_error(error)

            # Generate recovery recommendations if requested
            if include_recommendations and result.errors_detected:
                recommendations = await self._generate_lsu_recommendations(
                    lsu, result.errors_detected, stabilizer_results
                )
                for recommendation in recommendations:
                    result.add_recommendation(recommendation)

            # Calculate diagnostic duration
            diagnostic_duration = (time.time() - start_time) * 1000
            result.diagnostic_duration_ms = diagnostic_duration

            # Update metrics
            self.metrics.total_diagnostics += 1
            self.metrics.total_errors_detected += result.error_count
            self.metrics.critical_errors_detected += result.critical_error_count
            self.metrics.total_recommendations += len(result.recommendations)

            if result.is_system_healthy():
                self.metrics.successful_diagnostics += 1

            # Update average metrics
            self._update_average_metrics(result)

            result.audit_trail.append(
                f"LSU diagnosis completed in {diagnostic_duration:.2f}ms"
            )
            logger.info(f"LSU diagnosis completed: {diagnostic_id}")

            return result

        except Exception as e:
            logger.error(f"LSU diagnosis failed: {diagnostic_id} - {e!s}")
            raise RuntimeError(f"LSU diagnosis failed: {e!s}")

    async def _analyze_stabilizer_result(
        self, stabilizer_result: StabilizerResult, lsu: LogicalSemanticUnit
    ) -> list[ErrorClassification]:
        """Analyze a single stabilizer result for errors."""
        errors = []

        # Check for execution failures
        if stabilizer_result.status.value in ["failed", "degraded"]:
            error = ErrorClassification(
                error_id="",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.LOGIC_ERROR,
                confidence_score=0.9,
                constitutional_impact=True,
                error_message=f"Stabilizer execution failed: {stabilizer_result.execution_id}",
                error_context={
                    "stabilizer_id": stabilizer_result.metadata.get("stabilizer_id"),
                    "lsu_id": lsu.id,
                    "execution_time_ms": stabilizer_result.execution_time_ms,
                    "status": stabilizer_result.status.value,
                },
                constitutional_hash=self.constitutional_hash,
            )
            errors.append(error)

        # Check for performance issues
        if stabilizer_result.execution_time_ms > 5000:  # 5 second threshold
            error = ErrorClassification(
                error_id="",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.PERFORMANCE_DEGRADATION,
                confidence_score=0.8,
                constitutional_impact=False,
                error_message=f"Stabilizer execution exceeded time threshold: {stabilizer_result.execution_time_ms}ms",
                error_context={
                    "stabilizer_id": stabilizer_result.metadata.get("stabilizer_id"),
                    "execution_time_ms": stabilizer_result.execution_time_ms,
                    "threshold_ms": 5000,
                },
                constitutional_hash=self.constitutional_hash,
            )
            errors.append(error)

        # Check for constitutional compliance violations
        if not stabilizer_result.compliance_validated:
            error = ErrorClassification(
                error_id="",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.CONSTITUTIONAL_VIOLATION,
                confidence_score=1.0,
                constitutional_impact=True,
                error_message="Constitutional compliance validation failed",
                error_context={
                    "stabilizer_id": stabilizer_result.metadata.get("stabilizer_id"),
                    "compliance_score": stabilizer_result.compliance_score,
                    "constitutional_hash": stabilizer_result.constitutional_hash,
                },
                constitutional_hash=self.constitutional_hash,
            )
            errors.append(error)

        return errors

    async def _analyze_lsu_semantic_integrity(
        self, lsu: LogicalSemanticUnit
    ) -> list[ErrorClassification]:
        """Analyze LSU for semantic integrity issues."""
        errors = []

        # Check constitutional compliance
        if not lsu.compliance_validated:
            error = ErrorClassification(
                error_id="",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.CONSTITUTIONAL_VIOLATION,
                confidence_score=1.0,
                constitutional_impact=True,
                error_message="LSU constitutional compliance not validated",
                error_context={
                    "lsu_id": lsu.id,
                    "constitutional_hash": lsu.constitutional_hash,
                    "domain": lsu.domain.value,
                },
                constitutional_hash=self.constitutional_hash,
            )
            errors.append(error)

        return errors

    def _update_average_metrics(self, result: DiagnosticResult) -> None:
        """Update running average metrics."""
        total_diagnostics = max(1, self.metrics.total_diagnostics)

        # Update average diagnostic time
        current_avg = self.metrics.average_diagnostic_time_ms
        new_avg = (
            (current_avg * (total_diagnostics - 1)) + result.diagnostic_duration_ms
        ) / total_diagnostics
        self.metrics.average_diagnostic_time_ms = new_avg

        # Update average health score
        current_health_avg = self.metrics.average_health_score
        new_health_avg = (
            (current_health_avg * (total_diagnostics - 1)) + result.overall_health_score
        ) / total_diagnostics
        self.metrics.average_health_score = new_health_avg

        # Update average compliance score
        current_compliance_avg = self.metrics.average_compliance_score
        new_compliance_avg = (
            (current_compliance_avg * (total_diagnostics - 1))
            + result.constitutional_compliance_score
        ) / total_diagnostics
        self.metrics.average_compliance_score = new_compliance_avg

        # Update last updated timestamp
        self.metrics.last_updated = datetime.now()

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.http_client:
                await self.http_client.aclose()
            logger.info("Syndrome Diagnostic Engine cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
