#!/usr/bin/env python3
"""
ACGS Service Deployment Validation Script
========================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

Constitutional hash: cdd01ef066bc6cf2

This script validates that all ACGS services are properly deployed with
constitutional compliance and performs comprehensive health checks.
"""

import argparse
import asyncio
import fnmatch
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import docker

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Default excludes for repo crawling
DEFAULT_EXCLUDE = {".venv", "venv", "config/environments/development.env", ".tox", "__pycache__", "*.egg-info"}

# Service configuration
ACGS_SERVICES = {
    "postgres": {
        "port": 5439,
        "health_endpoint": None,
        "container_name": "acgs_postgres",
        "required": True,
    },
    "redis": {
        "port": 6389,
        "health_endpoint": None,
        "container_name": "acgs_redis",
        "required": True,
    },
    "opa": {
        "port": 8181,
        "health_endpoint": "http://localhost:8181/health",
        "container_name": "acgs_opa",
        "required": True,
    },
    "api_gateway": {
        "port": 8080,
        "health_endpoint": "http://localhost:8080/gateway/health",
        "container_name": "acgs_api_gateway",
        "required": True,
    },
    "auth_service": {
        "port": 8016,
        "health_endpoint": "http://localhost:8016/health",
        "container_name": "acgs_auth_service",
        "required": False,  # Optional service
    },
    "constitutional_core": {
        "port": 8001,
        "health_endpoint": "http://localhost:8001/health",
        "container_name": "acgs_constitutional_core",
        "required": True,
    },
    "integrity_service": {
        "port": 8002,
        "health_endpoint": "http://localhost:8002/health",
        "container_name": "acgs_integrity_service",
        "required": True,
    },
    "governance_engine": {
        "port": 8004,
        "health_endpoint": "http://localhost:8004/health",
        "container_name": "acgs_governance_engine",
        "required": True,
    },
    "ec_service": {
        "port": 8006,
        "health_endpoint": "http://localhost:8006/health",
        "container_name": "acgs_ec_service",
        "required": True,
    },
    "opencode_cli": {
        "port": 8020,
        "health_endpoint": None,
        "container_name": "acgs_opencode_cli",
        "required": False,
    },
}


@dataclass
class ServiceStatus:
    name: str
    running: bool
    healthy: bool
    constitutional_compliant: bool
    port_accessible: bool
    response_time: Optional[float]
    error_message: Optional[str]


class ACGSServiceValidator:
    def __init__(self, extra_exclude: Optional[Set[str]] = None):
        self.logger = self._setup_logging()
        self.docker_client = docker.from_env()
        self.exclude_patterns = DEFAULT_EXCLUDE.copy()
        if extra_exclude:
            self.exclude_patterns.update(extra_exclude)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with constitutional compliance context."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger("ACGSValidator")
        logger.info(
            f"Initializing ACGS Service Validator - Constitutional Hash: {CONSTITUTIONAL_HASH}"
        )
        return logger

    def _should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded based on exclude patterns."""
        path_str = str(path)
        path_parts = path.parts

        for pattern in self.exclude_patterns:
            # Check if any part of the path matches the pattern
            for part in path_parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            # Also check the full path for wildcard patterns
            if fnmatch.fnmatch(path_str, f"*{pattern}*") or fnmatch.fnmatch(
                path_str, pattern
            ):
                return True
        return False

    def scan_repo_for_compliance(self, repo_path: Path = None) -> Dict[str, any]:
        """Scan repository for constitutional compliance, excluding virtual environment artifacts."""
        if repo_path is None:
            repo_path = Path(".")

        self.logger.info(f"Scanning repository for compliance: {repo_path}")
        self.logger.info(f"Excluding patterns: {self.exclude_patterns}")

        scan_results = {
            "total_files": 0,
            "scanned_files": 0,
            "excluded_files": 0,
            "compliant_files": 0,
            "non_compliant_files": [],
            "excluded_paths": [],
        }

        # Walk through all files in the repository
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                scan_results["total_files"] += 1

                # Check if path should be excluded
                if self._should_exclude_path(file_path):
                    scan_results["excluded_files"] += 1
                    scan_results["excluded_paths"].append(str(file_path))
                    continue

                # Only scan Python files for constitutional hash
                if file_path.suffix == ".py":
                    scan_results["scanned_files"] += 1

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if CONSTITUTIONAL_HASH in content:
                                scan_results["compliant_files"] += 1
                            else:
                                scan_results["non_compliant_files"].append(
                                    str(file_path)
                                )
                    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                        self.logger.warning(f"Could not read file: {file_path}")

        return scan_results

    async def check_port_accessibility(self, port: int) -> bool:
        """Check if a port is accessible."""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except Exception:
            return False

    async def check_service_health(
        self, service_name: str, endpoint: str
    ) -> Tuple[bool, float, Optional[str]]:
        """Check service health endpoint and measure response time."""
        if not endpoint:
            return True, 0.0, None

        try:
            start_time = time.time()
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(endpoint) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        # Check for constitutional compliance in response
                        try:
                            data = await response.json()
                            constitutional_compliant = CONSTITUTIONAL_HASH in str(
                                data
                            ) or any(
                                CONSTITUTIONAL_HASH in str(v)
                                for v in data.values()
                                if isinstance(v, (str, dict))
                            )
                            return True, response_time, None
                        except:
                            # If not JSON, assume healthy but check headers
                            constitutional_compliant = CONSTITUTIONAL_HASH in str(
                                response.headers
                            )
                            return True, response_time, None
                    else:
                        return False, response_time, f"HTTP {response.status}"
        except Exception as e:
            return False, 0.0, str(e)

    def check_container_status(self, container_name: str) -> Tuple[bool, Optional[str]]:
        """Check if Docker container is running."""
        try:
            container = self.docker_client.containers.get(container_name)
            return container.status == "running", None
        except docker.errors.NotFound:
            return False, "Container not found"
        except Exception as e:
            return False, str(e)

    async def validate_constitutional_compliance(
        self, service_name: str, endpoint: str
    ) -> bool:
        """Validate constitutional compliance for a service."""
        if not endpoint:
            return True  # Skip for services without health endpoints

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                # Check main health endpoint
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if CONSTITUTIONAL_HASH in str(data):
                                return True
                        except:
                            pass

                # Check constitutional-specific endpoint if available
                constitutional_endpoint = endpoint.replace(
                    "/health", "/health/constitutional"
                )
                try:
                    async with session.get(constitutional_endpoint) as response:
                        if response.status == 200:
                            data = await response.json()
                            return CONSTITUTIONAL_HASH in str(data)
                except:
                    pass

                # Check for constitutional hash in headers
                return CONSTITUTIONAL_HASH in str(response.headers)
        except Exception as e:
            self.logger.warning(
                f"Constitutional compliance check failed for {service_name}: {e}"
            )
            return False

    async def validate_service(self, service_name: str, config: Dict) -> ServiceStatus:
        """Validate a single service comprehensively."""
        self.logger.info(f"Validating service: {service_name}")

        # Check container status
        container_running, container_error = self.check_container_status(
            config["container_name"]
        )

        # Check port accessibility
        port_accessible = await self.check_port_accessibility(config["port"])

        # Check health endpoint
        healthy = True
        response_time = 0.0
        health_error = None

        if config["health_endpoint"]:
            healthy, response_time, health_error = await self.check_service_health(
                service_name, config["health_endpoint"]
            )

        # Check constitutional compliance
        constitutional_compliant = await self.validate_constitutional_compliance(
            service_name, config["health_endpoint"]
        )

        return ServiceStatus(
            name=service_name,
            running=container_running,
            healthy=healthy,
            constitutional_compliant=constitutional_compliant,
            port_accessible=port_accessible,
            response_time=response_time,
            error_message=container_error or health_error,
        )

    async def run_validation(
        self, scan_repo: bool = True
    ) -> Tuple[Dict[str, ServiceStatus], Dict[str, any]]:
        """Run validation for all ACGS services and optionally scan repository."""
        self.logger.info("Starting ACGS service deployment validation")

        results = {}
        tasks = []

        for service_name, config in ACGS_SERVICES.items():
            task = self.validate_service(service_name, config)
            tasks.append((service_name, task))

        # Execute validations concurrently
        for service_name, task in tasks:
            try:
                result = await task
                results[service_name] = result
            except Exception as e:
                self.logger.error(f"Validation failed for {service_name}: {e}")
                results[service_name] = ServiceStatus(
                    name=service_name,
                    running=False,
                    healthy=False,
                    constitutional_compliant=False,
                    port_accessible=False,
                    response_time=None,
                    error_message=str(e),
                )

        # Run repository compliance scan if requested
        repo_scan_results = None
        if scan_repo:
            self.logger.info("Running repository compliance scan...")
            repo_scan_results = self.scan_repo_for_compliance()
            self.logger.info(
                f"Repository scan completed: {repo_scan_results['scanned_files']} files scanned, "
                f"{repo_scan_results['excluded_files']} files excluded"
            )

        return results, repo_scan_results

    def generate_report(
        self,
        results: Dict[str, ServiceStatus],
        repo_scan_results: Dict[str, any] = None,
    ) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("=" * 80)
        report.append("ACGS SERVICE DEPLOYMENT VALIDATION REPORT")
        report.append(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 80)
        report.append("")

        # Summary
        total_services = len(results)
        running_services = sum(1 for r in results.values() if r.running)
        healthy_services = sum(1 for r in results.values() if r.healthy)
        compliant_services = sum(
            1 for r in results.values() if r.constitutional_compliant
        )
        required_services = [
            name for name, config in ACGS_SERVICES.items() if config["required"]
        ]
        required_running = sum(1 for name in required_services if results[name].running)

        report.append("SUMMARY:")
        report.append(f"  Total Services: {total_services}")
        report.append(f"  Running: {running_services}/{total_services}")
        report.append(f"  Healthy: {healthy_services}/{total_services}")
        report.append(
            f"  Constitutional Compliant: {compliant_services}/{total_services}"
        )
        report.append(
            f"  Required Services Running: {required_running}/{len(required_services)}"
        )
        report.append("")

        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("")

        for service_name, status in results.items():
            config = ACGS_SERVICES[service_name]
            required_str = "REQUIRED" if config["required"] else "OPTIONAL"

            report.append(f"Service: {service_name.upper()} ({required_str})")
            report.append(f"  Container: {config['container_name']}")
            report.append(f"  Port: {config['port']}")
            report.append(f"  Running: {'✓' if status.running else '✗'}")
            report.append(
                f"  Port Accessible: {'✓' if status.port_accessible else '✗'}"
            )
            report.append(f"  Healthy: {'✓' if status.healthy else '✗'}")
            report.append(
                f"  Constitutional Compliant: {'✓' if status.constitutional_compliant else '✗'}"
            )

            if status.response_time is not None:
                report.append(f"  Response Time: {status.response_time:.3f}s")

            if status.error_message:
                report.append(f"  Error: {status.error_message}")

            report.append("")

        # Repository Scan Results
        if repo_scan_results:
            report.append("REPOSITORY COMPLIANCE SCAN:")
            report.append("")
            report.append(f"  Total Files: {repo_scan_results['total_files']}")
            report.append(f"  Scanned Files: {repo_scan_results['scanned_files']}")
            report.append(f"  Excluded Files: {repo_scan_results['excluded_files']}")
            report.append(f"  Compliant Files: {repo_scan_results['compliant_files']}")
            report.append(
                f"  Non-Compliant Files: {len(repo_scan_results['non_compliant_files'])}"
            )

            if repo_scan_results["scanned_files"] > 0:
                compliance_rate = (
                    repo_scan_results["compliant_files"]
                    / repo_scan_results["scanned_files"]
                ) * 100
                report.append(f"  Compliance Rate: {compliance_rate:.1f}%")

            report.append(
                f"  Excluded Patterns: {', '.join(sorted(self.exclude_patterns))}"
            )

            if repo_scan_results["non_compliant_files"]:
                report.append("")
                report.append("  Non-Compliant Files:")
                for file_path in repo_scan_results["non_compliant_files"][
                    :10
                ]:  # Show first 10
                    report.append(f"    - {file_path}")
                if len(repo_scan_results["non_compliant_files"]) > 10:
                    report.append(
                        f"    ... and {len(repo_scan_results['non_compliant_files']) - 10} more"
                    )

            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS:")
        failed_required = [
            name for name in required_services if not results[name].running
        ]
        if failed_required:
            report.append(
                f"  ⚠️  Critical: Start required services: {', '.join(failed_required)}"
            )

        slow_services = [
            name
            for name, status in results.items()
            if status.response_time and status.response_time > 1.0
        ]
        if slow_services:
            report.append(
                f"  ⚠️  Performance: Slow response times: {', '.join(slow_services)}"
            )

        non_compliant = [
            name
            for name, status in results.items()
            if not status.constitutional_compliant
            and ACGS_SERVICES[name]["health_endpoint"]
        ]
        if non_compliant:
            report.append(
                f"  ⚠️  Compliance: Non-compliant services: {', '.join(non_compliant)}"
            )

        if not failed_required and not slow_services and not non_compliant:
            report.append("  ✅ All services are properly deployed and compliant!")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def start_missing_services(self, results: Dict[str, ServiceStatus]) -> None:
        """Start missing required services."""
        failed_required = [
            name
            for name in ACGS_SERVICES.keys()
            if ACGS_SERVICES[name]["required"] and not results[name].running
        ]

        if not failed_required:
            self.logger.info("All required services are running")
            return

        self.logger.info(f"Starting missing required services: {failed_required}")

        try:
            # Start services with docker-compose
            cmd = [
                "docker-compose",
                "-f",
                "infrastructure/docker/docker-compose.acgs.yml",
                "up",
                "-d",
            ] + failed_required

            subprocess.run(cmd, check=True, cwd=Path.cwd())
            self.logger.info("Services started successfully")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start services: {e}")


async def main():
    """Main validation routine."""
    parser = argparse.ArgumentParser(description="Validate ACGS service deployment")
    parser.add_argument(
        "--extra-exclude", nargs="*", help="Additional paths to exclude during scanning"
    )
    parser.add_argument(
        "--scan-repo", action="store_true", help="Enable scanning of the repository"
    )
    parser.add_argument(
        "--no-prompt", action="store_true", help="Disable interactive prompts"
    )
    args = parser.parse_args()

    extra_exclude = set(args.extra_exclude) if args.extra_exclude else None
    validator = ACGSServiceValidator(extra_exclude=extra_exclude)

    # Run validation
    results, repo_scan_results = await validator.run_validation(
        scan_repo=args.scan_repo
    )

    # Generate and display report
    report = validator.generate_report(results, repo_scan_results)
    print(report)

    # Save report to file
    report_path = Path("logs/service_validation_report.txt")
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)

    # Determine exit code
    required_services = [
        name for name, config in ACGS_SERVICES.items() if config["required"]
    ]
    failed_required = [name for name in required_services if not results[name].running]

    if failed_required:
        print(
            f"\n❌ Validation FAILED: {len(failed_required)} required services not running"
        )

        # Offer to start missing services
        if not args.no_prompt:
            try:
                response = input("\nWould you like to start missing services? (y/N): ")
                if response.lower() == "y":
                    validator.start_missing_services(results)
                    print("Services started. Run validation again to verify.")
            except KeyboardInterrupt:
                print("\nValidation cancelled.")

        sys.exit(1)
    else:
        print("\n✅ Validation PASSED: All required services are running")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
