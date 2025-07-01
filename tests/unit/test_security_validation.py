"""
Tests for the security input validation module.
"""

from services.shared.security_validation import sanitize_user_input, validate_user_input


def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users --",
    ]

    for malicious_input in malicious_inputs:
        result = validate_user_input(malicious_input)
        assert not result["is_valid"], f"Should reject SQL injection: {malicious_input}"
        assert "SQL injection" in str(result["violations"])


def test_xss_prevention():
    """Test XSS prevention."""
    malicious_inputs = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
    ]

    for malicious_input in malicious_inputs:
        result = validate_user_input(malicious_input)
        assert not result["is_valid"], f"Should reject XSS: {malicious_input}"
        assert "XSS" in str(result["violations"])


def test_command_injection_prevention():
    """Test command injection prevention."""
    malicious_inputs = ["; rm -rf /", "| cat /etc/passwd", "&& whoami"]

    for malicious_input in malicious_inputs:
        result = validate_user_input(malicious_input)
        assert not result[
            "is_valid"
        ], f"Should reject command injection: {malicious_input}"
        assert "command injection" in str(result["violations"])


def test_valid_inputs():
    """Test that valid inputs are accepted."""
    valid_inputs = [
        "normal text",
        "user@example.com",
        "ValidUsername123",
        "A normal description with punctuation.",
    ]

    for valid_input in valid_inputs:
        result = validate_user_input(valid_input)
        assert result["is_valid"], f"Should accept valid input: {valid_input}"


def test_input_sanitization():
    """Test input sanitization."""
    test_cases = [
        ("normal text", "normal text"),
        ("text with <script>", "text with "),
        ("user@example.com", "user@example.com"),
    ]

    for input_text, expected in test_cases:
        sanitized = sanitize_user_input(input_text)
        assert sanitized == expected, f"Sanitization failed for: {input_text}"
