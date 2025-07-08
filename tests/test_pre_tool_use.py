#!/usr/bin/env python3
"""
Unit tests for the pre_tool_use.py security blocking script.

Tests both benign and malicious command samples to ensure proper
constitutional AI governance and security pattern blocking.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import subprocess
import unittest
from pathlib import Path


class TestPreToolUseSecurity(unittest.TestCase):
    """Test suite for pre_tool_use.py security blocking functionality."""

    script_path = "/home/dislove/ACGS-2/.claude/hooks/pre_tool_use.py"
    constitutional_hash = "cdd01ef066bc6cf2"

    def run_security_check(self, command: str) -> tuple[int, dict]:
        """Helper method to run security check and parse output."""
        input_data = {"command": command}
        process = subprocess.Popen(
            ["python3", self.script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input=json.dumps(input_data))

        try:
            response = json.loads(stdout.strip())
        except json.JSONDecodeError:
            response = {
                "error": "Failed to parse JSON",
                "stdout": stdout,
                "stderr": stderr,
            }

        return process.returncode, response

    def test_allowed_benign_commands(self):
        """Test that benign commands are allowed."""
        benign_commands = [
            "echo Hello World",
            "ls -la",
            "pwd",
            "whoami",
            "date",
            "python3 --version",
            "git status",
            "pip list",
            "cat README.md",
            "grep 'pattern' file.txt",
        ]

        for command in benign_commands:
            with self.subTest(command=command):
                exit_code, response = self.run_security_check(command)

                self.assertEqual(
                    exit_code, 0, f"Benign command should exit with 0: {command}"
                )
                self.assertTrue(
                    response.get("allowed"),
                    f"Benign command should be allowed: {command}",
                )
                self.assertEqual(
                    response.get("constitutional_hash"), self.constitutional_hash
                )

    def test_blocked_dangerous_commands(self):
        """Test that dangerous commands are blocked."""
        dangerous_commands = [
            ("rm -rf /important_folder", r"rm\s+-rf\s+"),
            ("sudo apt-get install malware", r"sudo\s+"),
            ("cat .env", r"\.env"),
            ("vim .env", r"\.env"),
            ("rm .env", r"\.env"),
            ("chmod 644 .env", r"\s*chmod\s+[0-7]{3,4}\s+.*\.env"),
            ("dd if=/dev/zero of=/dev/sda", r"dd\s+if=/dev/zero"),
            ("mkfs.ext4 /dev/sda1", r"mkfs\."),
            ("fdisk /dev/sda", r"fdisk\s+"),
            ("shutdown now", r"shutdown\s+"),
            ("reboot", r"reboot\s*$"),
            ("halt", r"halt\s*$"),
            ("killall python", r"killall\s+"),
        ]

        for command, expected_pattern in dangerous_commands:
            with self.subTest(command=command):
                exit_code, response = self.run_security_check(command)

                self.assertEqual(
                    exit_code, 2, f"Dangerous command should exit with 2: {command}"
                )
                self.assertFalse(
                    response.get("allowed"),
                    f"Dangerous command should be blocked: {command}",
                )
                self.assertEqual(
                    response.get("constitutional_hash"), self.constitutional_hash
                )
                self.assertIn(
                    "Command blocked by security pattern", response.get("reason", "")
                )

    def test_input_validation(self):
        """Test input validation for malformed requests."""
        # Test empty input
        process = subprocess.Popen(
            ["python3", self.script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input="")
        exit_code = process.returncode

        self.assertEqual(exit_code, 2)
        response = json.loads(stdout.strip())
        self.assertFalse(response.get("allowed"))
        self.assertEqual(response.get("constitutional_hash"), self.constitutional_hash)

        # Test invalid JSON
        process = subprocess.Popen(
            ["python3", self.script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input="{invalid json}")
        exit_code = process.returncode

        self.assertEqual(exit_code, 2)
        response = json.loads(stdout.strip())
        self.assertFalse(response.get("allowed"))
        self.assertIn("Invalid JSON input", response.get("reason", ""))

        # Test missing command field
        process = subprocess.Popen(
            ["python3", self.script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input='{"other_field": "value"}')
        exit_code = process.returncode

        self.assertEqual(exit_code, 2)
        response = json.loads(stdout.strip())
        self.assertFalse(response.get("allowed"))
        self.assertIn("Missing required field: command", response.get("reason", ""))

    def test_logging_functionality(self):
        """Test that events are properly logged."""
        log_file = Path("/home/dislove/ACGS-2/logs/pre_tool_use.json")

        # Ensure logs directory exists
        log_file.parent.mkdir(exist_ok=True)

        # Clear log file for clean test
        if log_file.exists():
            log_file.unlink()

        # Run a test command
        self.run_security_check("echo test logging")

        # Check that log file was created and contains entry
        self.assertTrue(log_file.exists(), "Log file should be created")

        with log_file.open() as f:
            log_entries = [json.loads(line) for line in f if line.strip()]

        self.assertGreater(len(log_entries), 0, "Should have at least one log entry")

        last_entry = log_entries[-1]
        self.assertEqual(last_entry["constitutional_hash"], self.constitutional_hash)
        self.assertIn("timestamp", last_entry)
        self.assertIn("compliance_version", last_entry)
        self.assertEqual(last_entry["command"], "echo test logging")

    def test_constitutional_compliance(self):
        """Test constitutional compliance metadata."""
        exit_code, response = self.run_security_check("echo constitutional test")

        # Verify constitutional hash is always present
        self.assertEqual(response.get("constitutional_hash"), self.constitutional_hash)

        # Test blocked command also has constitutional compliance
        exit_code, response = self.run_security_check("rm -rf /test")
        self.assertEqual(response.get("constitutional_hash"), self.constitutional_hash)

        # Verify response structure
        required_fields = ["allowed", "constitutional_hash"]
        for field in required_fields:
            self.assertIn(field, response, f"Response should contain {field}")

    def test_case_insensitive_blocking(self):
        """Test that security patterns work case-insensitively."""
        case_variants = ["RM -RF /test", "Sudo whoami", "CAT .ENV", "SHUTDOWN now"]

        for command in case_variants:
            with self.subTest(command=command):
                exit_code, response = self.run_security_check(command)
                self.assertEqual(
                    exit_code, 2, f"Case variant should be blocked: {command}"
                )
                self.assertFalse(response.get("allowed"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
