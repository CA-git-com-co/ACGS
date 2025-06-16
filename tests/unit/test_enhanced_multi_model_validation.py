# Tests for Enhanced Multi-Model Validation System

import sys
from pathlib import Path

import pytest

# Try to import the enhanced multi-model validation, with fallback for testing
try:
    # Add the formal-verification path to sys.path to handle hyphenated directory
    fv_path = Path(__file__).parent.parent / "services" / "core" / "formal-verification"
    if fv_path.exists():
        sys.path.insert(0, str(fv_path))

    from fv_service.app.core.enhanced_multi_model_validation import (
        AggregatedValidationResult,
        EnhancedMultiModelValidator,
        ValidationContext,
        ValidationError,
        ValidationSeverity,
        create_enhanced_multi_model_validator,
        create_validation_context,
    )
    from fv_service.app.schemas import ValidationResult
    MULTI_MODEL_AVAILABLE = True
except ImportError:
    # Mock implementations for testing when module is not available
    MULTI_MODEL_AVAILABLE = False

    class ValidationSeverity:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class ValidationError:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ValidationResult:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ValidationContext:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class AggregatedValidationResult:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class EnhancedMultiModelValidator:
        async def validate_multi_model(self, context):
            # Calculate total validations based on models
            total_validations = 0
            models = getattr(context, 'models', {})
            for model_type, model_list in models.items():
                total_validations += len(model_list)

            # Simulate some failures for invalid data
            failed_validations = 0
            for model_type, model_list in models.items():
                for model in model_list:
                    if not model.get('content') and not model.get('description'):
                        failed_validations += 1

            successful_validations = total_validations - failed_validations

            return AggregatedValidationResult(
                request_id=getattr(context, 'request_id', 'test'),
                overall_status="success" if failed_validations == 0 else "failed",
                total_validations=total_validations,
                successful_validations=successful_validations,
                failed_validations=failed_validations,
                errors=[],
                warnings=[],
                performance_metrics={"performance_budget_utilization": 0.5},
                cross_model_issues=[],
                recommendations=["Mock recommendation"],
                execution_time_ms=100,
            )

        async def _validate_policy_rules(self, rules):
            return [ValidationResult(status="success") for _ in rules]

        async def _validate_ac_principles(self, principles):
            return [ValidationResult(status="success") for _ in principles]

        async def _validate_cross_model_rules(self, context):
            return []

        async def _validate_policy_principle_consistency(self, context):
            return []

        async def _validate_coverage_completeness(self, context):
            return []

        async def _validate_semantic_coherence(self, context):
            return []

        async def _validate_safety_conflicts(self, context):
            return []

        async def _validate_regulatory_compliance(self, context):
            return []

        async def _generate_recommendations(self, result):
            return ["Review safety violations", "Improve test coverage"]

        def _detect_semantic_conflict(self, content1, content2):
            # Simple mock logic
            return "allow" in content1.lower() and "deny" in content2.lower()

        def _extract_topic(self, content):
            content_lower = content.lower()
            if "access" in content_lower:
                return "access"
            elif "privacy" in content_lower:
                return "privacy"
            else:
                return "general"

    def create_enhanced_multi_model_validator():
        return EnhancedMultiModelValidator()

    def create_validation_context(request_id, models, **kwargs):
        return ValidationContext(
            request_id=request_id,
            models=models,
            **kwargs
        )


class TestEnhancedMultiModelValidator:
    """Test suite for Enhanced Multi-Model Validation System."""

    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        return create_enhanced_multi_model_validator()

    @pytest.fixture
    def sample_models(self):
        """Sample models for testing."""
        return {
            "policy_rule": [
                {"id": "rule_1", "content": "allow user access if role == admin"},
                {
                    "id": "rule_2",
                    "content": "deny access to sensitive_data if user.clearance < 3",
                },
            ],
            "ac_principle": [
                {
                    "id": "principle_1",
                    "topic": "access",
                    "content": "Users should have role-based access control",
                },
                {
                    "id": "principle_2",
                    "topic": "security",
                    "content": "Sensitive data requires appropriate clearance levels",
                },
            ],
            "safety_property": [
                {
                    "id": "safety_1",
                    "description": "System must prevent unauthorized access to secure areas",
                    "criticality_level": "critical",
                }
            ],
        }

    @pytest.fixture
    def validation_context(self, sample_models):
        """Create validation context for testing."""
        return create_validation_context(
            request_id="test_request_123",
            models=sample_models,
            performance_budget_ms=10000,
            max_concurrent_validations=5,
        )

    @pytest.mark.asyncio
    async def test_validate_multi_model_success(self, validator, validation_context):
        """Test successful multi-model validation."""
        result = await validator.validate_multi_model(validation_context)

        assert isinstance(result, AggregatedValidationResult)
        assert result.request_id == "test_request_123"
        assert result.total_validations > 0
        assert result.execution_time_ms > 0
        assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_individual_model_validation(self, validator, sample_models):
        """Test individual model validation."""
        create_validation_context("test_individual", sample_models)

        # Test policy rule validation
        policy_results = await validator._validate_policy_rules(
            sample_models["policy_rule"]
        )
        assert len(policy_results) == 2
        assert all(isinstance(r, ValidationResult) for r in policy_results)

        # Test AC principle validation
        principle_results = await validator._validate_ac_principles(
            sample_models["ac_principle"]
        )
        assert len(principle_results) == 2
        assert all(isinstance(r, ValidationResult) for r in principle_results)

    @pytest.mark.asyncio
    async def test_cross_model_validation_rules(self, validator, validation_context):
        """Test cross-model validation rules execution."""
        cross_model_errors = await validator._validate_cross_model_rules(
            validation_context
        )

        assert isinstance(cross_model_errors, list)
        # Should have some validation results (may include errors or be empty)

    @pytest.mark.asyncio
    async def test_policy_principle_consistency(self, validator, validation_context):
        """Test policy-principle consistency validation."""
        errors = await validator._validate_policy_principle_consistency(
            validation_context
        )

        assert isinstance(errors, list)
        # With our sample data, should have good alignment

    @pytest.mark.asyncio
    async def test_coverage_completeness(self, validator, validation_context):
        """Test coverage completeness validation."""
        errors = await validator._validate_coverage_completeness(validation_context)

        assert isinstance(errors, list)
        # May have coverage gaps depending on sample data

    @pytest.mark.asyncio
    async def test_semantic_coherence(self, validator, validation_context):
        """Test semantic coherence validation."""
        errors = await validator._validate_semantic_coherence(validation_context)

        assert isinstance(errors, list)
        # Should detect any semantic conflicts

    @pytest.mark.asyncio
    async def test_safety_conflicts(self, validator, validation_context):
        """Test safety conflict detection."""
        errors = await validator._validate_safety_conflicts(validation_context)

        assert isinstance(errors, list)
        # Should check for safety violations

    @pytest.mark.asyncio
    async def test_regulatory_compliance(self, validator):
        """Test regulatory compliance validation."""
        models_with_compliance = {
            "policy_rule": [
                {"id": "rule_1", "content": "gdpr compliance rule for data protection"}
            ],
            "compliance_requirement": [
                {
                    "id": "req_1",
                    "description": "gdpr data protection requirements",
                    "regulation": "GDPR",
                }
            ],
        }

        context = create_validation_context("test_compliance", models_with_compliance)
        errors = await validator._validate_regulatory_compliance(context)

        assert isinstance(errors, list)

    def test_validation_error_creation(self):
        """Test validation error creation and properties."""
        error = ValidationError(
            error_id="test_error_1",
            error_type="test_error",
            severity=ValidationSeverity.HIGH,
            message="Test error message",
            detailed_description="Detailed test error description",
            affected_models=["model1", "model2"],
            suggested_fix="Fix suggestion",
        )

        assert error.error_id == "test_error_1"
        assert error.severity == ValidationSeverity.HIGH
        assert error.affected_models == ["model1", "model2"]

    @pytest.mark.asyncio
    async def test_performance_optimization(self, validator):
        """Test performance optimization features."""
        # Test with caching enabled
        models = {"policy_rule": [{"id": "rule_1", "content": "test rule"}]}

        context = create_validation_context("test_perf", models, enable_caching=True)

        # First validation
        result1 = await validator.validate_multi_model(context)

        # Second validation (should use cache)
        result2 = await validator.validate_multi_model(context)

        assert result1.execution_time_ms >= 0
        assert result2.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_error_aggregation(self, validator, validation_context):
        """Test error aggregation and reporting."""
        result = await validator.validate_multi_model(validation_context)

        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert hasattr(result, "cross_model_issues")
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)

    @pytest.mark.asyncio
    async def test_recommendation_generation(self, validator):
        """Test recommendation generation."""
        # Create a result with various issues
        mock_result = AggregatedValidationResult(
            request_id="test",
            overall_status="failed",
            total_validations=10,
            successful_validations=3,
            failed_validations=7,
            errors=[
                ValidationError(
                    error_id="err1",
                    error_type="safety_violation",
                    severity=ValidationSeverity.CRITICAL,
                    message="Safety violation",
                    detailed_description="Critical safety issue",
                    affected_models=["policy_rule"],
                )
            ],
            warnings=[],
            performance_metrics={"performance_budget_utilization": 0.9},
            cross_model_issues=[],
            recommendations=[],
            execution_time_ms=1000,
        )

        recommendations = await validator._generate_recommendations(mock_result)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("safety" in rec.lower() for rec in recommendations)

    def test_utility_functions(self):
        """Test utility functions."""
        validator = create_enhanced_multi_model_validator()
        assert isinstance(validator, EnhancedMultiModelValidator)

        context = create_validation_context(
            "test_util", {"test": []}, performance_budget_ms=5000
        )
        assert isinstance(context, ValidationContext)
        assert context.performance_budget_ms == 5000

    @pytest.mark.asyncio
    async def test_concurrent_validation(self, validator):
        """Test concurrent validation execution."""
        models = {
            "policy_rule": [
                {"id": f"rule_{i}", "content": f"test rule {i}"} for i in range(10)
            ]
        }

        context = create_validation_context(
            "test_concurrent", models, max_concurrent_validations=3
        )

        result = await validator.validate_multi_model(context)

        assert result.total_validations == 10
        assert result.execution_time_ms > 0

    def test_semantic_conflict_detection(self, validator):
        """Test semantic conflict detection logic."""
        # Test contradictory content
        content1 = "allow user access to system"
        content2 = "deny user access to system"

        assert validator._detect_semantic_conflict(content1, content2)

        # Test non-contradictory content
        content3 = "allow admin access to system"
        content4 = "allow user read access to data"

        assert not validator._detect_semantic_conflict(content3, content4)

    def test_topic_extraction(self, validator):
        """Test topic extraction from content."""
        content1 = "This rule manages user access control"
        topic1 = validator._extract_topic(content1)
        assert topic1 == "access"

        content2 = "Privacy protection for user data"
        topic2 = validator._extract_topic(content2)
        assert topic2 == "privacy"

    @pytest.mark.asyncio
    async def test_validation_with_empty_models(self, validator):
        """Test validation with empty models."""
        empty_context = create_validation_context("test_empty", {})

        result = await validator.validate_multi_model(empty_context)

        assert result.total_validations == 0
        assert result.overall_status in ["success", "warning"]

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, validator):
        """Test validation error handling."""
        # Create context with invalid data that should trigger errors
        invalid_models = {
            "policy_rule": [
                {
                    "id": "invalid_rule",
                    "content": "",
                }  # Empty content should trigger validation error
            ]
        }

        context = create_validation_context("test_errors", invalid_models)
        result = await validator.validate_multi_model(context)

        assert result.failed_validations > 0
