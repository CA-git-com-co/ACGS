#!/usr/bin/env python3
"""
Port Number Validation Script for ACGS Infrastructure
Constitutional Hash: cdd01ef066bc6cf2

Validates that port numbers used in ACGS services are within assigned ranges
and do not conflict with reserved or system ports.

ACGS Port Allocation:
- Authentication Service: 8000
- Constitutional AI Service: 8001
- Integrity Service: 8002
- Formal Verification Service: 8003
- Governance Synthesis Service: 8004
- Policy Governance Service: 8005
- Evolutionary Computation Service: 8006
- Multi-Agent Coordinator: 8008
- Worker Agents: 8009
- Blackboard Service: 8010
- MCP Aggregator: 3000
- Redis: 6379
- PostgreSQL: 5432
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

# ACGS Reserved Port Ranges
ACGS_RESERVED_PORTS = {
    8000: "Authentication Service",
    8001: "Constitutional AI Service",
    8002: "Integrity Service",
    8003: "Formal Verification Service",
    8004: "Governance Synthesis Service",
    8005: "Policy Governance Service",
    8006: "Evolutionary Computation Service",
    8008: "Multi-Agent Coordinator",
    8009: "Worker Agents",
    8010: "Blackboard Service",
    3000: "MCP Aggregator",
    6379: "Redis",
    5432: "PostgreSQL",
}

# System reserved ports (0-1023)
SYSTEM_RESERVED_RANGE = (0, 1023)

# ACGS service port range (8000-8099)
ACGS_SERVICE_RANGE = (8000, 8099)

# Well-known ports to avoid
WELL_KNOWN_PORTS = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    993: "IMAPS",
    995: "POP3S",
}


class PortValidator:
    """Validator for ACGS port number assignments"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.found_ports: Dict[int, List[str]] = {}

    def validate_project(self, project_root: Path) -> bool:
        """Validate all port assignments in the project"""
        print(f"🔍 Validating port numbers in ACGS project")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")

        # Files to check for port configurations
        config_patterns = [
            "**/*.yml",
            "**/*.yaml",
            "**/*.json",
            "**/*.py",
            "**/*.sh",
            "**/*.md",
            "**/docker-compose*.yml",
            "**/Dockerfile*",
            "**/.env*",
        ]

        files_checked = 0

        for pattern in config_patterns:
            for file_path in project_root.glob(pattern):
                if self._should_skip_file(file_path):
                    continue

                files_checked += 1
                self._check_file_ports(file_path)

        print(f"📁 Checked {files_checked} files")

        # Validate port assignments
        self._validate_port_assignments()
        self._check_port_conflicts()
        self._validate_acgs_compliance()

        # Report results
        return self._report_results()

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".mypy_cache",
            ".coverage",
            "venv",
            ".venv",
            "env",
            "dist",
            "build",
            "target",
        }

        skip_files = {".gitignore", ".dockerignore", "LICENSE", "README.md"}

        # Skip if in excluded directory
        for part in file_path.parts:
            if part in skip_dirs:
                return True

        # Skip if excluded file
        if file_path.name in skip_files:
            return True

        # Skip binary files
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(512)
                if b"\0" in chunk:
                    return True
        except (OSError, IOError):
            return True

        return False

    def _check_file_ports(self, file_path: Path) -> None:
        """Check a single file for port numbers"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Find port patterns
            port_patterns = [
                r":(\d{1,5})(?:[/\s]|$)",  # :8000
                r"port[:\s=]+(\d{1,5})",  # port: 8000, port=8000
                r"PORT[:\s=]+(\d{1,5})",  # PORT=8000
                r"listen[:\s]+(\d{1,5})",  # listen 8000
                r"expose[:\s]+(\d{1,5})",  # expose 8000
                r"bind[:\s]+.*:(\d{1,5})",  # bind 0.0.0.0:8000
                r"localhost:(\d{1,5})",  # localhost:8000
                r"127\.0\.0\.1:(\d{1,5})",  # 127.0.0.1:8000
                r"0\.0\.0\.0:(\d{1,5})",  # 0.0.0.0:8000
            ]

            for pattern in port_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    try:
                        port = int(match)
                        if 1 <= port <= 65535:  # Valid port range
                            rel_path = str(file_path.relative_to(Path.cwd()))
                            if port not in self.found_ports:
                                self.found_ports[port] = []
                            self.found_ports[port].append(rel_path)
                    except ValueError:
                        continue

        except (OSError, IOError, UnicodeDecodeError) as e:
            self.warnings.append(f"Could not read {file_path}: {e}")

    def _validate_port_assignments(self) -> None:
        """Validate individual port assignments"""
        for port, files in self.found_ports.items():
            # Check system reserved ports
            if SYSTEM_RESERVED_RANGE[0] <= port <= SYSTEM_RESERVED_RANGE[1]:
                if port not in WELL_KNOWN_PORTS:
                    self.errors.append(
                        f"Port {port} is in system reserved range (0-1023). "
                        f"Found in: {', '.join(files[:3])}"
                    )

            # Check well-known ports
            if port in WELL_KNOWN_PORTS:
                self.warnings.append(
                    f"Port {port} conflicts with {WELL_KNOWN_PORTS[port]}. "
                    f"Found in: {', '.join(files[:3])}"
                )

            # Check if port is outside recommended range for services
            if port > 65535:
                self.errors.append(
                    f"Port {port} exceeds maximum valid port number (65535). "
                    f"Found in: {', '.join(files[:3])}"
                )

    def _check_port_conflicts(self) -> None:
        """Check for port conflicts within the project"""
        port_usage = {}

        for port, files in self.found_ports.items():
            if len(files) > 1:
                # Group by file type to reduce noise
                file_types = {}
                for file_path in files:
                    ext = Path(file_path).suffix or "no_ext"
                    if ext not in file_types:
                        file_types[ext] = []
                    file_types[ext].append(file_path)

                # Only warn if used in different service contexts
                if len(file_types) > 1 or len(files) > 3:
                    self.warnings.append(
                        f"Port {port} used in multiple files: {', '.join(files[:5])}"
                        + ("..." if len(files) > 5 else "")
                    )

    def _validate_acgs_compliance(self) -> None:
        """Validate compliance with ACGS port allocation scheme"""
        print(f"\n🏗️  ACGS Port Allocation Validation:")

        # Check reserved ACGS ports
        missing_services = []
        conflicting_services = []

        for port, service_name in ACGS_RESERVED_PORTS.items():
            if port in self.found_ports:
                files = self.found_ports[port]
                print(f"✅ Port {port} ({service_name}): Found in {len(files)} files")

                # Validate service files contain correct service references
                service_keywords = service_name.lower().replace(" ", "_")
                matching_files = []

                for file_path in files:
                    if any(
                        keyword in file_path.lower()
                        for keyword in service_keywords.split("_")
                    ):
                        matching_files.append(file_path)

                if not matching_files and port in ACGS_SERVICE_RANGE:
                    self.warnings.append(
                        f"Port {port} assigned to {service_name} but found in "
                        f"non-service files: {', '.join(files[:3])}"
                    )
            else:
                if port in range(ACGS_SERVICE_RANGE[0], ACGS_SERVICE_RANGE[1] + 1):
                    missing_services.append(f"Port {port} ({service_name})")

        if missing_services:
            print(f"⚠️  Missing ACGS service ports: {', '.join(missing_services)}")

        # Check for ports in ACGS range that aren't reserved
        for port in self.found_ports:
            if ACGS_SERVICE_RANGE[0] <= port <= ACGS_SERVICE_RANGE[1]:
                if port not in ACGS_RESERVED_PORTS:
                    self.warnings.append(
                        f"Port {port} is in ACGS service range (8000-8099) but not in "
                        f"reserved allocation. Consider using a different port."
                    )

    def _report_results(self) -> bool:
        """Report validation results"""
        print(f"\n📊 Port Validation Results:")
        print(f"   Total ports found: {len(self.found_ports)}")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")

        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        # Show port summary
        print(f"\n📋 Port Usage Summary:")
        sorted_ports = sorted(self.found_ports.keys())

        for port in sorted_ports:
            files = self.found_ports[port]
            service_name = ACGS_RESERVED_PORTS.get(port, "Unknown")
            status = "🔧 ACGS" if port in ACGS_RESERVED_PORTS else "🔍 Other"

            print(f"   {status} Port {port}: {service_name} " f"({len(files)} files)")

        # Constitutional compliance check
        constitutional_files = []
        for files in self.found_ports.values():
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        if self.constitutional_hash in f.read():
                            constitutional_files.append(file_path)
                            break
                except (OSError, IOError):
                    continue

        print(f"\n🏛️  Constitutional Compliance:")
        print(f"   Files with constitutional hash: {len(set(constitutional_files))}")

        # Return success status
        success = len(self.errors) == 0

        if success:
            print(f"\n✅ Port validation passed!")
        else:
            print(f"\n❌ Port validation failed with {len(self.errors)} errors")

        return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate ACGS port number assignments"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the ACGS project",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )

    args = parser.parse_args()

    validator = PortValidator()
    success = validator.validate_project(args.project_root)

    # In strict mode, warnings also cause failure
    if args.strict and validator.warnings:
        print(f"\n⚠️  Strict mode: {len(validator.warnings)} warnings treated as errors")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
