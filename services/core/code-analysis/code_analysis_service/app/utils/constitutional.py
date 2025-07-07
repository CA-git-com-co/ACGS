"""
ACGS Code Analysis Engine - Constitutional Compliance Utilities
Provides constitutional hash validation and compliance checking functionality.

Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalValidator:
    """
    Constitutional compliance validator for ACGS Code Analysis Engine.

    Provides validation, signature generation, and compliance checking
    for all operations within the constitutional framework.
    """

    def __init__(self, constitutional_hash: str = CONSTITUTIONAL_HASH):
        """Initialize constitutional validator with hash verification."""
        if constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )

        self.constitutional_hash = constitutional_hash
        self.validation_count = 0
        self.last_validation = None

    def validate_hash(self, provided_hash: str) -> bool:
        """
        Validate provided hash against constitutional standard.

        Args:
            provided_hash: Hash to validate

        Returns:
            bool: True if hash is valid
        """
        is_valid = provided_hash == self.constitutional_hash
        self.validation_count += 1
        self.last_validation = datetime.now(timezone.utc)

        if not is_valid:
            logger.warning(f"Constitutional hash validation failed: {provided_hash}")

        return is_valid

    def generate_compliance_signature(self, data: dict[str, Any]) -> str:
        """
        Generate constitutional compliance signature for data.

        Args:
            data: Data to generate signature for

        Returns:
            str: Constitutional compliance signature
        """
        # Create deterministic string representation
        data_str = self._serialize_data(data)

        # Generate signature with constitutional hash
        signature_input = f"{self.constitutional_hash}:{data_str}:{int(time.time())}"
        signature = hashlib.sha256(signature_input.encode()).hexdigest()[:16]

        return f"const_{signature}"

    def validate_compliance(
        self, data: dict[str, Any], signature: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Validate constitutional compliance of data and operations.

        Args:
            data: Data to validate
            signature: Optional signature to verify

        Returns:
            dict: Compliance validation result
        """
        validation_result = {
            "compliant": True,
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "validation_id": f"val_{int(time.time())}_{self.validation_count}",
            "issues": [],
        }

        # Check for required constitutional hash in data
        if "constitutional_hash" in data:
            if not self.validate_hash(data["constitutional_hash"]):
                validation_result["compliant"] = False
                validation_result["issues"].append(
                    "Invalid constitutional hash in data"
                )

        # Validate signature if provided
        if signature:
            expected_signature = self.generate_compliance_signature(data)
            if signature != expected_signature:
                validation_result["compliant"] = False
                validation_result["issues"].append("Constitutional signature mismatch")

        # Check for sensitive operations requiring enhanced validation
        if self._requires_enhanced_validation(data):
            enhanced_result = self._perform_enhanced_validation(data)
            if not enhanced_result["compliant"]:
                validation_result["compliant"] = False
                validation_result["issues"].extend(enhanced_result["issues"])

        return validation_result

    def add_constitutional_metadata(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Add constitutional compliance metadata to data.

        Args:
            data: Data to enhance with constitutional metadata

        Returns:
            dict: Data with constitutional metadata
        """
        enhanced_data = data.copy()

        enhanced_data.update(
            {
                "constitutional_hash": self.constitutional_hash,
                "constitutional_compliance": {
                    "validated": True,
                    "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                    "validator_version": "1.0.0",
                    "compliance_signature": self.generate_compliance_signature(data),
                },
            }
        )

        return enhanced_data

    def _serialize_data(self, data: dict[str, Any]) -> str:
        """Create deterministic string representation of data."""
        import json

        # Remove non-deterministic fields
        clean_data = {
            k: v
            for k, v in data.items()
            if k not in ["timestamp", "validation_timestamp", "request_id"]
        }

        # Sort keys for deterministic output
        return json.dumps(clean_data, sort_keys=True, separators=(",", ":"))

    def _requires_enhanced_validation(self, data: dict[str, Any]) -> bool:
        """Check if data requires enhanced constitutional validation."""
        sensitive_operations = [
            "policy_change",
            "governance_update",
            "constitutional_modification",
            "user_permission_change",
            "security_configuration",
        ]

        operation_type = data.get("operation_type", "")
        return operation_type in sensitive_operations

    def _perform_enhanced_validation(self, data: dict[str, Any]) -> dict[str, Any]:
        """Perform enhanced constitutional validation for sensitive operations."""
        result = {"compliant": True, "issues": []}

        # Enhanced validation rules
        required_fields = ["user_id", "operation_type", "justification"]
        for field in required_fields:
            if field not in data:
                result["compliant"] = False
                result["issues"].append(
                    f"Missing required field for enhanced validation: {field}"
                )

        # Check justification length for sensitive operations
        justification = data.get("justification", "")
        if len(justification) < 50:
            result["compliant"] = False
            result["issues"].append(
                "Insufficient justification for sensitive operation"
            )

        return result


def validate_constitutional_hash(hash_value: str) -> bool:
    """
    Quick validation function for constitutional hash.

    Args:
        hash_value: Hash to validate

    Returns:
        bool: True if valid
    """
    return hash_value == CONSTITUTIONAL_HASH


def get_constitutional_headers() -> dict[str, str]:
    """
    Get standard constitutional compliance headers.

    Returns:
        dict: Headers with constitutional compliance information
    """
    return {
        "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
        "X-Constitutional-Compliance": "validated",
        "X-Constitutional-Timestamp": datetime.now(timezone.utc).isoformat(),
    }


def ensure_constitutional_compliance(data: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure data includes constitutional compliance metadata.

    Args:
        data: Data to ensure compliance for

    Returns:
        dict: Data with constitutional compliance ensured
    """
    validator = ConstitutionalValidator()
    return validator.add_constitutional_metadata(data)


# Global validator instance for module-level operations
_global_validator = ConstitutionalValidator()


def validate_operation(operation_data: dict[str, Any]) -> bool:
    """
    Module-level function to validate constitutional compliance of operations.

    Args:
        operation_data: Operation data to validate

    Returns:
        bool: True if operation is constitutionally compliant
    """
    result = _global_validator.validate_compliance(operation_data)
    return result["compliant"]


def get_compliance_signature(data: dict[str, Any]) -> str:
    """
    Module-level function to generate compliance signature.

    Args:
        data: Data to generate signature for

    Returns:
        str: Constitutional compliance signature
    """
    return _global_validator.generate_compliance_signature(data)
