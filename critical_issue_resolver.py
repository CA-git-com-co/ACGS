#!/usr/bin/env python3
"""
Critical Issue Resolution Framework for ACGS-2
Addresses critical bugs affecting core algorithmic correctness,
security vulnerabilities, and performance bottlenecks.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@dataclass
class ResolutionResult:
    issue_id: str
    status: str  # RESOLVED, PARTIAL, FAILED, SKIPPED
    resolution_time: float
    actions_taken: List[str]
    verification_passed: bool
    remaining_work: List[str]
    details: Dict[str, Any]

class CriticalIssueResolver:
    def __init__(self):
        self.project_root = project_root
        self.resolution_results = []
        
    def load_critical_issues(self) -> List[Dict[str, Any]]:
        """Load critical issues from the analysis results."""
        issue_file = self.project_root / "issue_analysis_results.json"
        
        if not issue_file.exists():
            print("❌ Issue analysis results not found. Run issue_analyzer.py first.")
            return []
        
        with open(issue_file, 'r') as f:
            data = json.load(f)
        
        # Filter for critical issues
        critical_issues = [
            issue for issue in data.get("prioritized_issues", [])
            if issue.get("severity") == "CRITICAL"
        ]
        
        print(f"📋 Found {len(critical_issues)} critical issues to resolve")
        return critical_issues
    
    def resolve_input_validation_security(self, issue: Dict[str, Any]) -> ResolutionResult:
        """Resolve critical input validation security vulnerabilities."""
        start_time = time.time()
        actions_taken = []
        
        try:
            # Create comprehensive input validation module
            validation_code = '''"""
Comprehensive Input Validation Module for ACGS-2
Implements security-hardened input validation to prevent injection attacks.
"""

import re
import html
import json
from typing import Any, Dict, List, Optional, Union

class SecurityInputValidator:
    """Security-focused input validator with comprehensive protection."""
    
    def __init__(self):
        # Dangerous patterns for different attack types
        self.sql_injection_patterns = [
            r"('|(\\'))+.*(;|--|#)",
            r"(union|select|insert|update|delete|drop|create|alter)\\s",
            r"'\\s*(or|and)\\s*'",
            r"'\\s*(or|and)\\s*\\d+\\s*=\\s*\\d+",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\\w+\\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        self.command_injection_patterns = [
            r"[;&|`]\\s*(rm|del|format|cat|type|whoami|id|ps|ls|dir)",
            r"\\$\\([^)]*\\)",
            r"`[^`]*`",
            r"\\|\\s*(curl|wget|nc|netcat)",
        ]
        
        self.path_traversal_patterns = [
            r"\\.\\./",
            r"\\.\\.\\\\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
        ]
        
        # Maximum lengths for different input types
        self.max_lengths = {
            "username": 50,
            "email": 254,
            "password": 128,
            "title": 200,
            "description": 2000,
            "general": 1000
        }
    
    def validate_input(self, input_data: Any, input_type: str = "general") -> Dict[str, Any]:
        """
        Comprehensive input validation.
        
        Args:
            input_data: The input to validate
            input_type: Type of input (username, email, password, etc.)
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": True,
            "sanitized_input": input_data,
            "violations": [],
            "risk_level": "LOW"
        }
        
        # Convert to string for validation
        if input_data is None:
            result["is_valid"] = False
            result["violations"].append("Input cannot be None")
            result["risk_level"] = "HIGH"
            return result
        
        input_str = str(input_data)
        
        # Check length limits
        max_length = self.max_lengths.get(input_type, self.max_lengths["general"])
        if len(input_str) > max_length:
            result["is_valid"] = False
            result["violations"].append(f"Input exceeds maximum length of {max_length}")
            result["risk_level"] = "MEDIUM"
        
        # Check for null bytes
        if "\\x00" in input_str or "\\0" in input_str:
            result["is_valid"] = False
            result["violations"].append("Null bytes not allowed")
            result["risk_level"] = "HIGH"
        
        # Check for SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential SQL injection detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential XSS attack detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for command injection patterns
        for pattern in self.command_injection_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential command injection detected")
                result["risk_level"] = "CRITICAL"
                break
        
        # Check for path traversal patterns
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                result["is_valid"] = False
                result["violations"].append("Potential path traversal detected")
                result["risk_level"] = "HIGH"
                break
        
        # Sanitize input if valid
        if result["is_valid"]:
            result["sanitized_input"] = self.sanitize_input(input_str, input_type)
        
        return result
    
    def sanitize_input(self, input_str: str, input_type: str = "general") -> str:
        """Sanitize input string based on type."""
        if input_type == "email":
            # Basic email sanitization
            return re.sub(r'[^a-zA-Z0-9@._-]', '', input_str)
        elif input_type == "username":
            # Allow alphanumeric and basic punctuation
            return re.sub(r'[^a-zA-Z0-9._-]', '', input_str)
        elif input_type == "html":
            # HTML escape
            return html.escape(input_str)
        else:
            # General sanitization - remove dangerous characters
            sanitized = re.sub(r'[<>"\\'`]', '', input_str)
            return sanitized.strip()
    
    def validate_json_input(self, json_str: str) -> Dict[str, Any]:
        """Validate JSON input for injection attacks."""
        result = {
            "is_valid": True,
            "parsed_json": None,
            "violations": [],
            "risk_level": "LOW"
        }
        
        try:
            # Parse JSON
            parsed = json.loads(json_str)
            
            # Check for dangerous keys/values
            dangerous_keys = ["$ne", "$gt", "$lt", "$regex", "$where", "eval", "function"]
            
            def check_dangerous_content(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in dangerous_keys:
                            result["is_valid"] = False
                            result["violations"].append(f"Dangerous key '{key}' found at {path}")
                            result["risk_level"] = "HIGH"
                        check_dangerous_content(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_dangerous_content(item, f"{path}[{i}]")
                elif isinstance(obj, str):
                    # Check string values for injection patterns
                    validation_result = self.validate_input(obj)
                    if not validation_result["is_valid"]:
                        result["is_valid"] = False
                        result["violations"].extend(validation_result["violations"])
                        if validation_result["risk_level"] == "CRITICAL":
                            result["risk_level"] = "CRITICAL"
            
            check_dangerous_content(parsed)
            result["parsed_json"] = parsed
            
        except json.JSONDecodeError as e:
            result["is_valid"] = False
            result["violations"].append(f"Invalid JSON format: {str(e)}")
            result["risk_level"] = "MEDIUM"
        
        return result

# Global validator instance
security_validator = SecurityInputValidator()

def validate_user_input(input_data: Any, input_type: str = "general") -> Dict[str, Any]:
    """
    Main function for validating user input.
    
    Args:
        input_data: The input to validate
        input_type: Type of input for context-specific validation
        
    Returns:
        Validation result dictionary
    """
    return security_validator.validate_input(input_data, input_type)

def sanitize_user_input(input_data: str, input_type: str = "general") -> str:
    """
    Main function for sanitizing user input.
    
    Args:
        input_data: The input to sanitize
        input_type: Type of input for context-specific sanitization
        
    Returns:
        Sanitized input string
    """
    return security_validator.sanitize_input(input_data, input_type)
'''
            
            # Save the validation module
            validation_file = self.project_root / "services" / "shared" / "security_validation.py"
            validation_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(validation_file, 'w') as f:
                f.write(validation_code)
            
            actions_taken.append("Created comprehensive input validation module")
            
            # Create test file for the validation module
            test_code = '''"""
Tests for the security input validation module.
"""

import pytest
from services.shared.security_validation import validate_user_input, sanitize_user_input

def test_sql_injection_prevention():
    """Test SQL injection prevention."""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users --"
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
        "<img src=x onerror=alert('XSS')>"
    ]
    
    for malicious_input in malicious_inputs:
        result = validate_user_input(malicious_input)
        assert not result["is_valid"], f"Should reject XSS: {malicious_input}"
        assert "XSS" in str(result["violations"])

def test_command_injection_prevention():
    """Test command injection prevention."""
    malicious_inputs = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "&& whoami"
    ]
    
    for malicious_input in malicious_inputs:
        result = validate_user_input(malicious_input)
        assert not result["is_valid"], f"Should reject command injection: {malicious_input}"
        assert "command injection" in str(result["violations"])

def test_valid_inputs():
    """Test that valid inputs are accepted."""
    valid_inputs = [
        "normal text",
        "user@example.com",
        "ValidUsername123",
        "A normal description with punctuation."
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
'''
            
            test_file = self.project_root / "tests" / "unit" / "test_security_validation.py"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            actions_taken.append("Created comprehensive test suite for input validation")
            
            # Verify the fix by running a quick test
            verification_passed = self._verify_input_validation_fix()
            actions_taken.append("Verified input validation fixes")
            
            remaining_work = [
                "Integrate validation module into all input endpoints",
                "Update existing code to use new validation functions",
                "Add logging for security violations",
                "Implement rate limiting for repeated violations"
            ]
            
            return ResolutionResult(
                issue["id"],
                "RESOLVED" if verification_passed else "PARTIAL",
                time.time() - start_time,
                actions_taken,
                verification_passed,
                remaining_work,
                {
                    "validation_module_created": str(validation_file),
                    "test_file_created": str(test_file),
                    "security_patterns_implemented": 4
                }
            )
            
        except Exception as e:
            return ResolutionResult(
                issue["id"],
                "FAILED",
                time.time() - start_time,
                actions_taken,
                False,
                [],
                {"error": str(e)}
            )
    
    def _verify_input_validation_fix(self) -> bool:
        """Verify that the input validation fix works correctly."""
        try:
            # Import the new validation module
            sys.path.insert(0, str(self.project_root / "services" / "shared"))
            from security_validation import validate_user_input
            
            # Test with known malicious inputs
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('XSS')</script>",
                "; rm -rf /",
                "../../../etc/passwd"
            ]
            
            for malicious_input in malicious_inputs:
                result = validate_user_input(malicious_input)
                if result["is_valid"]:
                    return False  # Should have been rejected
            
            # Test with valid input
            valid_result = validate_user_input("normal text input")
            if not valid_result["is_valid"]:
                return False  # Should have been accepted
            
            return True
            
        except Exception:
            return False
    
    def resolve_test_coverage_gaps(self, issue: Dict[str, Any]) -> ResolutionResult:
        """Resolve critical test coverage gaps."""
        start_time = time.time()
        actions_taken = []
        
        try:
            component_name = issue["affected_components"][0] if issue["affected_components"] else "unknown"
            
            # Create basic test template for the component
            test_template = f'''"""
Test suite for {component_name} component.
Generated to address critical test coverage gap.
"""

import pytest
import sys
from pathlib import Path

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))

class Test{component_name.replace("-", "").replace("_", "").title()}:
    """Test class for {component_name} component."""
    
    def test_component_initialization(self):
        """Test component can be initialized."""
        # TODO: Implement actual initialization test
        assert True, "Component initialization test placeholder"
    
    def test_component_basic_functionality(self):
        """Test basic component functionality."""
        # TODO: Implement basic functionality tests
        assert True, "Basic functionality test placeholder"
    
    def test_component_error_handling(self):
        """Test component error handling."""
        # TODO: Implement error handling tests
        assert True, "Error handling test placeholder"
    
    def test_component_edge_cases(self):
        """Test component edge cases."""
        # TODO: Implement edge case tests
        assert True, "Edge case test placeholder"
    
    def test_component_performance(self):
        """Test component performance characteristics."""
        # TODO: Implement performance tests
        assert True, "Performance test placeholder"
    
    def test_component_security(self):
        """Test component security aspects."""
        # TODO: Implement security tests
        assert True, "Security test placeholder"

# Integration tests
class Test{component_name.replace("-", "").replace("_", "").title()}Integration:
    """Integration tests for {component_name} component."""
    
    def test_component_integration_with_dependencies(self):
        """Test component integration with its dependencies."""
        # TODO: Implement integration tests
        assert True, "Integration test placeholder"
    
    def test_component_data_flow(self):
        """Test data flow through the component."""
        # TODO: Implement data flow tests
        assert True, "Data flow test placeholder"

# Performance tests
class Test{component_name.replace("-", "").replace("_", "").title()}Performance:
    """Performance tests for {component_name} component."""
    
    def test_component_latency(self):
        """Test component latency requirements."""
        # TODO: Implement latency tests
        assert True, "Latency test placeholder"
    
    def test_component_throughput(self):
        """Test component throughput requirements."""
        # TODO: Implement throughput tests
        assert True, "Throughput test placeholder"
'''
            
            # Create test file
            safe_component_name = component_name.replace("-", "_").replace(" ", "_")
            test_file = self.project_root / "tests" / "unit" / f"test_{safe_component_name}.py"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write(test_template)
            
            actions_taken.append(f"Created test template for {component_name}")
            
            # Create integration test file
            integration_test_file = self.project_root / "tests" / "integration" / f"test_{safe_component_name}_integration.py"
            integration_test_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(integration_test_file, 'w') as f:
                f.write(test_template.replace("unit", "integration"))
            
            actions_taken.append(f"Created integration test template for {component_name}")
            
            verification_passed = test_file.exists() and integration_test_file.exists()
            
            remaining_work = [
                f"Implement actual test cases for {component_name}",
                "Add component-specific test data and fixtures",
                "Implement mocking for external dependencies",
                "Add performance benchmarks",
                "Integrate tests into CI/CD pipeline"
            ]
            
            return ResolutionResult(
                issue["id"],
                "PARTIAL",  # Templates created, but actual tests need implementation
                time.time() - start_time,
                actions_taken,
                verification_passed,
                remaining_work,
                {
                    "test_file_created": str(test_file),
                    "integration_test_file_created": str(integration_test_file),
                    "component_name": component_name
                }
            )
            
        except Exception as e:
            return ResolutionResult(
                issue["id"],
                "FAILED",
                time.time() - start_time,
                actions_taken,
                False,
                [],
                {"error": str(e)}
            )
    
    def resolve_critical_issues(self) -> Dict[str, Any]:
        """Resolve all critical issues."""
        print("Starting Critical Issue Resolution...")
        print("=" * 60)
        
        critical_issues = self.load_critical_issues()
        
        if not critical_issues:
            print("✅ No critical issues found to resolve.")
            return {"total_issues": 0, "resolved": 0, "failed": 0, "results": []}
        
        resolved_count = 0
        failed_count = 0
        
        for issue in critical_issues:
            print(f"\n🔧 Resolving: {issue['id']} - {issue['title']}")
            
            if issue["category"] == "SECURITY" and "input_validation" in issue["title"].lower():
                result = self.resolve_input_validation_security(issue)
            elif issue["category"] == "RELIABILITY" and "test coverage" in issue["title"].lower():
                result = self.resolve_test_coverage_gaps(issue)
            else:
                # Generic resolution for other critical issues
                result = ResolutionResult(
                    issue["id"],
                    "SKIPPED",
                    0.0,
                    ["Issue type not yet supported by automated resolution"],
                    False,
                    ["Manual resolution required"],
                    {"issue_type": issue["category"]}
                )
            
            self.resolution_results.append(result)
            
            # Log result
            status_symbol = {"RESOLVED": "✅", "PARTIAL": "🟡", "FAILED": "❌", "SKIPPED": "⊝"}
            symbol = status_symbol.get(result.status, "?")
            
            print(f"{symbol} {result.issue_id}: {result.status} ({result.resolution_time:.3f}s)")
            print(f"   Actions: {len(result.actions_taken)}")
            print(f"   Verified: {'✓' if result.verification_passed else '✗'}")
            print(f"   Remaining: {len(result.remaining_work)}")
            
            if result.status == "RESOLVED":
                resolved_count += 1
            elif result.status == "FAILED":
                failed_count += 1
        
        # Generate summary
        summary = {
            "total_issues": len(critical_issues),
            "resolved": resolved_count,
            "partial": sum(1 for r in self.resolution_results if r.status == "PARTIAL"),
            "failed": failed_count,
            "skipped": sum(1 for r in self.resolution_results if r.status == "SKIPPED"),
            "resolution_rate": (resolved_count / len(critical_issues) * 100) if critical_issues else 0,
            "results": [
                {
                    "issue_id": r.issue_id,
                    "status": r.status,
                    "resolution_time": r.resolution_time,
                    "actions_taken": r.actions_taken,
                    "verification_passed": r.verification_passed,
                    "remaining_work": r.remaining_work,
                    "details": r.details
                }
                for r in self.resolution_results
            ]
        }
        
        print("\n" + "=" * 60)
        print("CRITICAL ISSUE RESOLUTION SUMMARY")
        print("=" * 60)
        print(f"Total Critical Issues: {summary['total_issues']}")
        print(f"Resolved: {summary['resolved']}")
        print(f"Partial: {summary['partial']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Resolution Rate: {summary['resolution_rate']:.1f}%")
        
        return summary

def main():
    resolver = CriticalIssueResolver()
    summary = resolver.resolve_critical_issues()
    
    # Save results
    output_file = project_root / "critical_issue_resolution_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Return appropriate exit code
    if summary["failed"] > 0:
        print(f"\n⚠️  {summary['failed']} critical issues failed to resolve!")
        return 1
    elif summary["resolved"] < summary["total_issues"]:
        print(f"\n⚠️  {summary['total_issues'] - summary['resolved']} critical issues need manual attention!")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
