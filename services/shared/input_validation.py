# Input Validation Utilities
import re

from fastapi import HTTPException


class InputValidator:
    """Secure input validation utilities."""

    @staticmethod
    def validate_string(value: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="Invalid input type")

        if len(value) > max_length:
            raise HTTPException(status_code=400, detail=f"Input too long (max {max_length})")

        if not allow_html:
            # Remove potential HTML/script tags
            value = re.sub(r"<[^>]*>", "", value)

        return value.strip()

    @staticmethod
    def validate_policy_id(policy_id: str) -> str:
        """Validate policy ID format."""
        if not re.match(r"^[A-Z]{2,3}-\d{3}$", policy_id):
            raise HTTPException(status_code=400, detail="Invalid policy ID format")
        return policy_id

    @staticmethod
    def validate_hash(hash_value: str) -> str:
        """Validate hash format (SHA-256)."""
        if not re.match(r"^[a-fA-F0-9]{64}$", hash_value):
            raise HTTPException(status_code=400, detail="Invalid hash format")
        return hash_value.lower()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\|?*]', "", filename)
        filename = filename.replace("..", "")
        return filename[:255]  # Limit length
