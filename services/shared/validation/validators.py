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

from shared.resilience.exceptions import (
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
