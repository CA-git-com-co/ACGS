"""
Enhanced Business Rule Validation for ACGS-2
Improves edge case handling and validation robustness.
"""

from typing import Any, Dict, List, Optional, Union
import re
import json
from datetime import datetime, timezone

class EnhancedBusinessRuleValidator:
    """Enhanced validator with comprehensive edge case handling."""

    def __init__(self):
        self.validation_errors = []
        self.warnings = []

    def validate_governance_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate governance proposal with enhanced edge case handling."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_proposal": proposal.copy()
        }

        # Enhanced title validation
        title = proposal.get("title", "")
        if not title or not isinstance(title, str):
            self.validation_errors.append("Title is required and must be a string")
        elif len(title.strip()) == 0:
            self.validation_errors.append("Title cannot be empty or whitespace only")
        elif len(title) > 200:
            self.validation_errors.append("Title cannot exceed 200 characters")
        elif len(title) < 5:
            self.warnings.append("Title is very short, consider adding more detail")

        # Enhanced description validation
        description = proposal.get("description", "")
        if not description or not isinstance(description, str):
            self.validation_errors.append("Description is required and must be a string")
        elif len(description.strip()) < 10:
            self.validation_errors.append("Description must be at least 10 characters")
        elif len(description) > 5000:
            self.validation_errors.append("Description cannot exceed 5000 characters")

        # Status validation with edge cases
        status = proposal.get("status", "")
        valid_statuses = ["draft", "submitted", "under_review", "approved", "rejected", "withdrawn"]
        if status not in valid_statuses:
            self.validation_errors.append(f"Status must be one of: {', '.join(valid_statuses)}")

        # Priority validation
        priority = proposal.get("priority", "")
        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            self.validation_errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Date validation
        submitted_at = proposal.get("submitted_at")
        if submitted_at:
            try:
                if isinstance(submitted_at, str):
                    datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                elif not isinstance(submitted_at, datetime):
                    self.validation_errors.append("submitted_at must be a valid datetime or ISO string")
            except ValueError:
                self.validation_errors.append("submitted_at must be a valid ISO datetime string")

        # Approval validation edge cases
        if status == "approved":
            if not proposal.get("approved_by"):
                self.validation_errors.append("Approved proposals must have approved_by field")
            if not proposal.get("approved_at"):
                self.validation_errors.append("Approved proposals must have approved_at timestamp")

        # Sanitize proposal
        if "title" in result["sanitized_proposal"]:
            result["sanitized_proposal"]["title"] = title.strip()
        if "description" in result["sanitized_proposal"]:
            result["sanitized_proposal"]["description"] = description.strip()

        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

    def validate_policy_document(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate policy document with comprehensive checks."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_policy": policy.copy()
        }

        # Policy ID validation
        policy_id = policy.get("id")
        if not policy_id:
            self.validation_errors.append("Policy ID is required")
        elif not isinstance(policy_id, str):
            self.validation_errors.append("Policy ID must be a string")
        elif not re.match(r'^[A-Z]{3}-\d{4}$', policy_id):
            self.warnings.append("Policy ID should follow format: ABC-1234")

        # Version validation
        version = policy.get("version", "")
        if not version:
            self.validation_errors.append("Policy version is required")
        elif not re.match(r'^\d+\.\d+\.\d+$', str(version)):
            self.validation_errors.append("Version must follow semantic versioning (x.y.z)")

        # Content validation
        content = policy.get("content")
        if not content:
            self.validation_errors.append("Policy content is required")
        elif isinstance(content, str) and len(content.strip()) == 0:
            self.validation_errors.append("Policy content cannot be empty")
        elif isinstance(content, dict) and not content:
            self.validation_errors.append("Policy content cannot be empty object")

        # Effective date validation
        effective_date = policy.get("effective_date")
        if effective_date:
            try:
                if isinstance(effective_date, str):
                    parsed_date = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
                    if parsed_date < datetime.now(timezone.utc):
                        self.warnings.append("Effective date is in the past")
            except ValueError:
                self.validation_errors.append("effective_date must be a valid ISO datetime string")

        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

    def validate_constitutional_compliance(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constitutional compliance with edge case handling."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "compliance_score": 0.0
        }

        # Constitutional hash validation
        const_hash = document.get("constitutional_hash", "")
        if not const_hash:
            self.validation_errors.append("Constitutional hash is required")
        elif not isinstance(const_hash, str):
            self.validation_errors.append("Constitutional hash must be a string")
        elif not re.match(r'^[a-f0-9]{16}$', const_hash):
            self.validation_errors.append("Constitutional hash must be 16 hexadecimal characters")

        # Compliance level validation
        compliance_level = document.get("compliance_level", "")
        valid_levels = ["full", "partial", "non_compliant", "pending", "under_review"]
        if compliance_level not in valid_levels:
            self.validation_errors.append(f"Compliance level must be one of: {', '.join(valid_levels)}")

        # Required fields validation
        required_fields = ["constitutional_hash", "compliance_level", "validation_timestamp"]
        missing_fields = [field for field in required_fields if not document.get(field)]
        if missing_fields:
            self.validation_errors.append(f"Missing required fields: {', '.join(missing_fields)}")

        # High compliance validation
        if compliance_level == "full":
            if not document.get("approved_by"):
                self.validation_errors.append("Full compliance documents must have approved_by field")
            if not document.get("approval_timestamp"):
                self.validation_errors.append("Full compliance documents must have approval_timestamp")

        # Calculate compliance score
        score = 0.0
        if compliance_level == "full":
            score = 100.0
        elif compliance_level == "partial":
            score = 75.0
        elif compliance_level == "under_review":
            score = 50.0
        elif compliance_level == "pending":
            score = 25.0
        else:
            score = 0.0

        result["compliance_score"] = score
        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

# Global validator instance
enhanced_validator = EnhancedBusinessRuleValidator()

def validate_governance_proposal(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating governance proposals."""
    return enhanced_validator.validate_governance_proposal(proposal)

def validate_policy_document(policy: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating policy documents."""
    return enhanced_validator.validate_policy_document(policy)

def validate_constitutional_compliance(document: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating constitutional compliance."""
    return enhanced_validator.validate_constitutional_compliance(document)
