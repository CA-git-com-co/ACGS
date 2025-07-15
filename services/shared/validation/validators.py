"""
Comprehensive Validation System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Advanced validation with business rules, constitutional compliance, and security.
"""

import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from services.shared.resilience.exceptions import (
    ValidationError,
)

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    field: str
    message: str
    severity: ValidationSeverity
    error_code: str
    value: Any = None
    rule_name: str = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value,
            "error_code": self.error_code,
            "value": str(self.value) if self.value is not None else None,
            "rule_name": self.rule_name,
            "context": self.context,
        }


@dataclass
class ValidationResult:
    """Result of validation operation."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    validated_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_issue(
        self,
        field: str,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        error_code: str | None = None,
        value: Any = None,
        rule_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a validation issue."""
        issue = ValidationIssue(
            field=field,
            message=message,
            severity=severity,
            error_code=error_code or "VALIDATION_ERROR",
            value=value,
            rule_name=rule_name,
            context=context or {},
        )
        self.issues.append(issue)

        # Mark as invalid if any error or critical issue
        if severity in {ValidationSeverity.ERROR, ValidationSeverity.CRITICAL}:
            self.is_valid = False

    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(
            issue.severity in {ValidationSeverity.ERROR, ValidationSeverity.CRITICAL}
            for issue in self.issues
        )

    def has_warnings(self) -> bool:
        """Check if there are any warning-level issues."""
        return any(
            issue.severity == ValidationSeverity.WARNING
            for issue in self.issues
        )

    @property
    def errors(self) -> list[str]:
        """Get error messages for test compatibility."""
        return [issue.message for issue in self.get_errors()]

    @property
    def warnings(self) -> list[str]:
        """Get warning messages for test compatibility."""
        return [issue.message for issue in self.get_warnings()]

    def get_errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity in {ValidationSeverity.ERROR, ValidationSeverity.CRITICAL}
        ]

    def get_warnings(self) -> list[ValidationIssue]:
        """Get warning-level issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "has_errors": self.has_errors(),
            "error_count": len(self.get_errors()),
            "warning_count": len(self.get_warnings()),
            "issues": [issue.to_dict() for issue in self.issues],
            "validated_data": self.validated_data,
            "metadata": self.metadata,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    def raise_if_invalid(self) -> None:
        """Raise exception if validation failed."""
        if not self.is_valid:
            field_errors = {issue.field: issue.message for issue in self.get_errors()}
            raise ValidationError(
                "Validation failed", field_errors=field_errors, details=self.to_dict()
            )


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, name: str, error_message: str | None = None):
        self.name = name
        self.error_message = error_message or f"Validation rule '{name}' failed"

    @abstractmethod
    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        """Validate a value."""

    def get_error_message(
        self, value: Any, context: dict[str, Any] | None = None
    ) -> str:
        """Get error message for failed validation."""
        return self.error_message


class RequiredRule(ValidationRule):
    """Rule to check if a value is required."""

    def __init__(self):
        super().__init__("required", "Field is required")

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        return not (isinstance(value, (list, dict)) and len(value) == 0)


class LengthRule(ValidationRule):
    """Rule to check string/list length."""

    def __init__(self, min_length: int | None = None, max_length: int | None = None):
        self.min_length = min_length
        self.max_length = max_length

        message_parts = []
        if min_length is not None:
            message_parts.append(f"minimum length {min_length}")
        if max_length is not None:
            message_parts.append(f"maximum length {max_length}")

        super().__init__("length", f"Length must be {' and '.join(message_parts)}")

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        if value is None:
            return True  # Let RequiredRule handle None values

        try:
            length = len(value)

            if self.min_length is not None and length < self.min_length:
                return False

            return not (self.max_length is not None and length > self.max_length)
        except TypeError:
            return False


class RegexRule(ValidationRule):
    """Rule to validate against regular expressions."""

    def __init__(self, pattern: str, message: str | None = None):
        self.pattern = re.compile(pattern)
        super().__init__("regex", message or f"Value must match pattern: {pattern}")

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        if value is None:
            return True

        if not isinstance(value, str):
            return False

        return bool(self.pattern.match(value))


class EmailRule(RegexRule):
    """Rule to validate email addresses."""

    def __init__(self):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        super().__init__(email_pattern, "Invalid email address format")


class UUIDRule(RegexRule):
    """Rule to validate UUID format."""

    def __init__(self):
        uuid_pattern = (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        super().__init__(uuid_pattern, "Invalid UUID format")


class RangeRule(ValidationRule):
    """Rule to validate numeric ranges."""

    def __init__(
        self, min_value: int | float | None = None, max_value: int | float | None = None
    ):
        self.min_value = min_value
        self.max_value = max_value

        message_parts = []
        if min_value is not None:
            message_parts.append(f"minimum {min_value}")
        if max_value is not None:
            message_parts.append(f"maximum {max_value}")

        super().__init__("range", f"Value must be {' and '.join(message_parts)}")

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        if value is None:
            return True

        try:
            numeric_value = float(value)

            if self.min_value is not None and numeric_value < self.min_value:
                return False

            return not (self.max_value is not None and numeric_value > self.max_value)
        except (ValueError, TypeError):
            return False


class ChoicesRule(ValidationRule):
    """Rule to validate against allowed choices."""

    def __init__(self, choices: list[Any]):
        self.choices = choices
        super().__init__(
            "choices", f"Value must be one of: {', '.join(str(c) for c in choices)}"
        )

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        return value in self.choices


class CustomRule(ValidationRule):
    """Rule for custom validation logic."""

    def __init__(
        self, name: str, validator: Callable[[Any, dict[str, Any]], bool], message: str
    ):
        self.validator = validator
        super().__init__(name, message)

    async def validate(self, value: Any, context: dict[str, Any] | None = None) -> bool:
        try:
            return self.validator(value, context or {})
        except Exception as e:
            logger.exception(f"Custom validation rule '{self.name}' failed: {e}")
            return False


class Validator(ABC):
    """Abstract base class for validators."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def validate(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate data and return result."""


class InputValidator(Validator):
    """Validator for input data with configurable rules."""

    def __init__(self, name: str = "input_validator"):
        super().__init__(name)
        self.field_rules: dict[str, list[ValidationRule]] = {}
        self.global_rules: list[ValidationRule] = []

    def add_field_rule(self, field: str, rule: ValidationRule) -> "InputValidator":
        """Add validation rule for specific field."""
        if field not in self.field_rules:
            self.field_rules[field] = []
        self.field_rules[field].append(rule)
        return self

    def add_global_rule(self, rule: ValidationRule) -> "InputValidator":
        """Add global validation rule."""
        self.global_rules.append(rule)
        return self

    def required(self, field: str) -> "InputValidator":
        """Mark field as required."""
        return self.add_field_rule(field, RequiredRule())

    def length(
        self, field: str, min_length: int | None = None, max_length: int | None = None
    ) -> "InputValidator":
        """Add length validation for field."""
        return self.add_field_rule(field, LengthRule(min_length, max_length))

    def email(self, field: str) -> "InputValidator":
        """Add email validation for field."""
        return self.add_field_rule(field, EmailRule())

    def uuid(self, field: str) -> "InputValidator":
        """Add UUID validation for field."""
        return self.add_field_rule(field, UUIDRule())

    def range(
        self,
        field: str,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
    ) -> "InputValidator":
        """Add range validation for field."""
        return self.add_field_rule(field, RangeRule(min_value, max_value))

    def choices(self, field: str, choices: list[Any]) -> "InputValidator":
        """Add choices validation for field."""
        return self.add_field_rule(field, ChoicesRule(choices))

    def custom(
        self, field: str, validator: Callable[[Any, dict[str, Any]], bool], message: str
    ) -> "InputValidator":
        """Add custom validation for field."""
        return self.add_field_rule(
            field, CustomRule(f"custom_{field}", validator, message)
        )

    async def validate(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate input data."""
        result = ValidationResult(is_valid=True)
        context = context or {}

        if not isinstance(data, dict):
            result.add_issue(
                field="root",
                message="Input must be a dictionary",
                severity=ValidationSeverity.CRITICAL,
                error_code="INVALID_INPUT_TYPE",
            )
            return result

        # Validate field-specific rules
        for field, rules in self.field_rules.items():
            value = data.get(field)

            for rule in rules:
                try:
                    is_valid = await rule.validate(value, context)
                    if not is_valid:
                        result.add_issue(
                            field=field,
                            message=rule.get_error_message(value, context),
                            severity=ValidationSeverity.ERROR,
                            error_code=f"FIELD_{rule.name.upper()}_ERROR",
                            value=value,
                            rule_name=rule.name,
                        )
                except Exception as e:
                    logger.exception(
                        f"Error in validation rule '{rule.name}' for field '{field}': {e}"
                    )
                    result.add_issue(
                        field=field,
                        message=f"Validation error: {e}",
                        severity=ValidationSeverity.CRITICAL,
                        error_code="VALIDATION_RULE_ERROR",
                        rule_name=rule.name,
                    )

        # Validate global rules
        for rule in self.global_rules:
            try:
                is_valid = await rule.validate(data, context)
                if not is_valid:
                    result.add_issue(
                        field="global",
                        message=rule.get_error_message(data, context),
                        severity=ValidationSeverity.ERROR,
                        error_code=f"GLOBAL_{rule.name.upper()}_ERROR",
                        rule_name=rule.name,
                    )
            except Exception as e:
                logger.exception(f"Error in global validation rule '{rule.name}': {e}")
                result.add_issue(
                    field="global",
                    message=f"Global validation error: {e}",
                    severity=ValidationSeverity.CRITICAL,
                    error_code="GLOBAL_VALIDATION_ERROR",
                    rule_name=rule.name,
                )

        # Store validated data if successful
        if result.is_valid:
            result.validated_data = data.copy()

        return result


class SchemaValidator(Validator):
    """JSON Schema validator with enhanced error reporting."""

    def __init__(self, schema: dict[str, Any], name: str = "schema_validator"):
        super().__init__(name)
        self.schema = schema

        # Try to import jsonschema
        try:
            import jsonschema

            self.jsonschema = jsonschema
        except ImportError:
            logger.warning("jsonschema not available, schema validation disabled")
            self.jsonschema = None

    async def validate(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate data against JSON schema."""
        result = ValidationResult(is_valid=True)

        if not self.jsonschema:
            result.add_issue(
                field="schema",
                message="JSON schema validation not available",
                severity=ValidationSeverity.WARNING,
                error_code="SCHEMA_VALIDATOR_UNAVAILABLE",
            )
            return result

        try:
            # Validate against schema
            validator = self.jsonschema.Draft7Validator(self.schema)
            errors = list(validator.iter_errors(data))

            if errors:
                result.is_valid = False
                for error in errors:
                    field_path = ".".join(str(p) for p in error.absolute_path) or "root"
                    result.add_issue(
                        field=field_path,
                        message=error.message,
                        severity=ValidationSeverity.ERROR,
                        error_code="SCHEMA_VALIDATION_ERROR",
                        value=error.instance,
                        context={
                            "schema_path": ".".join(str(p) for p in error.schema_path)
                        },
                    )
            else:
                result.validated_data = data

        except Exception as e:
            logger.exception(f"Schema validation error: {e}")
            result.add_issue(
                field="schema",
                message=f"Schema validation failed: {e}",
                severity=ValidationSeverity.CRITICAL,
                error_code="SCHEMA_VALIDATION_EXCEPTION",
            )

        return result


class BusinessRuleValidator(Validator):
    """Validator for business rules and domain constraints."""

    def __init__(self, name: str = "business_rule_validator"):
        super().__init__(name)
        self.business_rules: list[Callable[[Any, dict[str, Any]], ValidationResult]] = (
            []
        )

    # Test compatibility methods
    def validate_age_requirement(self, age: int, min_age: int = 18) -> ValidationResult:
        """Validate age requirement."""
        result = ValidationResult(is_valid=True)
        if age < min_age:
            result.add_issue(
                field="age",
                message=f"Age {age} is below minimum requirement of {min_age}",
                severity=ValidationSeverity.ERROR,
                error_code="AGE_REQUIREMENT_ERROR"
            )
        return result

    def validate_business_hours(self, timestamp) -> ValidationResult:
        """Validate business hours."""
        result = ValidationResult(is_valid=True)
        # Simple business hours check (9 AM - 5 PM, Monday-Friday)
        if timestamp.weekday() >= 5:  # Weekend
            result.add_issue(
                field="timestamp",
                message="Outside business hours (weekends)",
                severity=ValidationSeverity.ERROR,
                error_code="BUSINESS_HOURS_ERROR"
            )
        elif timestamp.hour < 9 or timestamp.hour >= 17:  # Outside 9-5
            result.add_issue(
                field="timestamp",
                message="Outside business hours (9 AM - 5 PM)",
                severity=ValidationSeverity.ERROR,
                error_code="BUSINESS_HOURS_ERROR"
            )
        return result

    def validate_credit_limit(self, transaction_amount: float, credit_limit: float) -> ValidationResult:
        """Validate credit limit."""
        result = ValidationResult(is_valid=True)
        if transaction_amount > credit_limit:
            result.add_issue(
                field="transaction_amount",
                message=f"Transaction amount {transaction_amount} exceeds credit limit {credit_limit}",
                severity=ValidationSeverity.ERROR,
                error_code="CREDIT_LIMIT_ERROR"
            )
        return result

    def validate_inventory_availability(self, requested_quantity: int, available_quantity: int) -> ValidationResult:
        """Validate inventory availability."""
        result = ValidationResult(is_valid=True)
        if requested_quantity > available_quantity:
            result.add_issue(
                field="requested_quantity",
                message=f"Requested quantity {requested_quantity} exceeds available {available_quantity}",
                severity=ValidationSeverity.ERROR,
                error_code="INVENTORY_ERROR"
            )
        return result

    def validate_duplicate_prevention(self, value: str, existing_values: list[str]) -> ValidationResult:
        """Validate duplicate prevention."""
        result = ValidationResult(is_valid=True)
        if value in existing_values:
            result.add_issue(
                field="value",
                message=f"Value '{value}' already exists",
                severity=ValidationSeverity.ERROR,
                error_code="DUPLICATE_ERROR"
            )
        return result

    def add_rule(
        self, rule: Callable[[Any, dict[str, Any]], ValidationResult]
    ) -> "BusinessRuleValidator":
        """Add a business rule."""
        self.business_rules.append(rule)
        return self

    async def validate(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate business rules."""
        combined_result = ValidationResult(is_valid=True)
        context = context or {}

        for rule in self.business_rules:
            try:
                rule_result = rule(data, context)

                # Combine results
                combined_result.issues.extend(rule_result.issues)
                if not rule_result.is_valid:
                    combined_result.is_valid = False

                # Merge validated data
                combined_result.validated_data.update(rule_result.validated_data)
                combined_result.metadata.update(rule_result.metadata)

            except Exception as e:
                logger.exception(f"Business rule validation error: {e}")
                combined_result.add_issue(
                    field="business_rule",
                    message=f"Business rule validation failed: {e}",
                    severity=ValidationSeverity.CRITICAL,
                    error_code="BUSINESS_RULE_ERROR",
                )

        return combined_result


class ConstitutionalValidator(Validator):
    """Validator for constitutional compliance requirements."""

    def __init__(self, name: str = "constitutional_validator"):
        super().__init__(name)
        self.required_hash = "cdd01ef066bc6cf2"

    # Test compatibility methods
    def validate_hash(self, hash_value: str) -> ValidationResult:
        """Validate constitutional hash."""
        result = ValidationResult(is_valid=True)
        if hash_value != self.required_hash:
            result.add_issue(
                field="constitutional_hash",
                message=f"Invalid constitutional hash. Expected: {self.required_hash}",
                severity=ValidationSeverity.ERROR,
                error_code="INVALID_HASH"
            )
        return result

    def validate_governance_compliance(self, data: dict) -> ValidationResult:
        """Validate governance compliance."""
        result = ValidationResult(is_valid=True)

        # Check for required governance fields
        required_fields = ["policy_id", "governance_level", "constitutional_hash"]
        for field in required_fields:
            if field not in data:
                result.add_issue(
                    field=field,
                    message=f"Required governance field '{field}' is missing",
                    severity=ValidationSeverity.ERROR,
                    error_code="MISSING_GOVERNANCE_FIELD"
                )

        # Validate constitutional hash if present
        if "constitutional_hash" in data:
            hash_result = self.validate_hash(data["constitutional_hash"])
            result.issues.extend(hash_result.issues)
            if not hash_result.is_valid:
                result.is_valid = False

        return result

    def validate_ethical_guidelines(self, data: dict) -> ValidationResult:
        """Validate ethical guidelines compliance."""
        result = ValidationResult(is_valid=True)

        # Check for ethical compliance indicators
        if "ethical_review" not in data:
            result.add_issue(
                field="ethical_review",
                message="Ethical review status is required",
                severity=ValidationSeverity.WARNING,
                error_code="MISSING_ETHICAL_REVIEW"
            )

        return result

    def validate_privacy_compliance(self, data: dict) -> ValidationResult:
        """Validate privacy compliance."""
        result = ValidationResult(is_valid=True)

        # Check for privacy compliance indicators
        privacy_fields = ["data_classification", "privacy_level"]
        for field in privacy_fields:
            if field not in data:
                result.add_issue(
                    field=field,
                    message=f"Privacy field '{field}' is required",
                    severity=ValidationSeverity.WARNING,
                    error_code="MISSING_PRIVACY_FIELD"
                )

        return result

    def validate_security_requirements(self, data: dict) -> ValidationResult:
        """Validate security requirements."""
        result = ValidationResult(is_valid=True)

        # Check for security compliance indicators
        if "security_level" not in data:
            result.add_issue(
                field="security_level",
                message="Security level is required",
                severity=ValidationSeverity.ERROR,
                error_code="MISSING_SECURITY_LEVEL"
            )

        return result

    async def validate(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate constitutional compliance."""
        result = ValidationResult(is_valid=True)
        context = context or {}

        # Check for constitutional hash
        constitutional_hash = None
        if isinstance(data, dict):
            constitutional_hash = data.get("constitutional_hash")

        if not constitutional_hash:
            # Check context
            constitutional_hash = context.get("constitutional_hash")

        if not constitutional_hash:
            result.add_issue(
                field="constitutional_hash",
                message="Constitutional hash is required",
                severity=ValidationSeverity.CRITICAL,
                error_code="MISSING_CONSTITUTIONAL_HASH",
            )
        elif constitutional_hash != self.required_hash:
            result.add_issue(
                field="constitutional_hash",
                message=f"Invalid constitutional hash. Expected: {self.required_hash}, Got: {constitutional_hash}",
                severity=ValidationSeverity.CRITICAL,
                error_code="INVALID_CONSTITUTIONAL_HASH",
                value=constitutional_hash,
            )

        # Additional constitutional compliance checks can be added here

        if result.is_valid:
            result.validated_data = data if isinstance(data, dict) else {}
            result.metadata["constitutional_compliance"] = True

        return result


class ConstitutionalHashValidator:
    """Validator specifically for constitutional hash validation."""

    def __init__(self):
        self.required_hash = "cdd01ef066bc6cf2"

    def validate_hash_format(self, hash_value: str) -> ValidationResult:
        """Validate hash format."""
        result = ValidationResult(is_valid=True)

        if not hash_value:
            result.add_issue(
                field="constitutional_hash",
                message="Constitutional hash cannot be empty",
                severity=ValidationSeverity.ERROR,
                error_code="EMPTY_HASH"
            )
        elif len(hash_value) != 16:
            result.add_issue(
                field="constitutional_hash",
                message=f"Constitutional hash must be 16 characters, got {len(hash_value)}",
                severity=ValidationSeverity.ERROR,
                error_code="INVALID_HASH_LENGTH"
            )
        elif not hash_value.isalnum():
            result.add_issue(
                field="constitutional_hash",
                message="Constitutional hash must be alphanumeric",
                severity=ValidationSeverity.ERROR,
                error_code="INVALID_HASH_FORMAT"
            )

        return result

    def validate_hash_integrity(self, hash_value: str) -> ValidationResult:
        """Validate hash integrity."""
        result = ValidationResult(is_valid=True)

        # First validate format
        format_result = self.validate_hash_format(hash_value)
        result.issues.extend(format_result.issues)
        if not format_result.is_valid:
            result.is_valid = False
            return result

        # Then validate against expected hash
        if hash_value != self.required_hash:
            result.add_issue(
                field="constitutional_hash",
                message=f"Hash integrity check failed. Expected: {self.required_hash}",
                severity=ValidationSeverity.ERROR,
                error_code="HASH_INTEGRITY_ERROR"
            )

        return result

    def validate_constitutional_compliance_function(self, data: dict) -> ValidationResult:
        """Validate constitutional compliance function."""
        result = ValidationResult(is_valid=True)

        # Check if constitutional hash is present
        if "constitutional_hash" not in data:
            result.add_issue(
                field="constitutional_hash",
                message="Constitutional hash is required for compliance",
                severity=ValidationSeverity.ERROR,
                error_code="MISSING_CONSTITUTIONAL_HASH"
            )
        else:
            # Validate the hash
            hash_result = self.validate_hash_integrity(data["constitutional_hash"])
            result.issues.extend(hash_result.issues)
            if not hash_result.is_valid:
                result.is_valid = False

        return result


# Convenience function for quick validation
async def validate_input(
    data: dict[str, Any],
    rules: dict[str, list[ValidationRule]] | None = None,
    context: dict[str, Any] | None = None,
) -> ValidationResult:
    """Quick input validation with specified rules."""
    validator = InputValidator()

    if rules:
        for field, field_rules in rules.items():
            for rule in field_rules:
                validator.add_field_rule(field, rule)

    return await validator.validate(data, context)
