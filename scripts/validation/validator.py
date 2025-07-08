"""
ACGS Unified Validator
Constitutional Hash: cdd01ef066bc6cf2

Main validator class that orchestrates all validation checks.
"""

import asyncio
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import HTTPClient, get_config, get_logger

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    check_name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    error: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "constitutional_hash": self.constitutional_hash,
        }


@dataclass
class ValidationSummary:
    """Summary of all validation results."""

    total_checks: int
    passed_checks: int
    failed_checks: int
    total_duration_ms: float
    constitutional_hash: str = CONSTITUTIONAL_HASH
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    @property
    def all_passed(self) -> bool:
        """Check if all validations passed."""
        return self.failed_checks == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "success_rate": self.success_rate,
            "all_passed": self.all_passed,
            "total_duration_ms": self.total_duration_ms,
            "constitutional_hash": self.constitutional_hash,
            "results": [r.to_dict() for r in self.results],
        }


class BaseValidationCheck:
    """Base class for validation checks."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"validator.{name}")

    async def run(self) -> ValidationResult:
        """Run the validation check."""
        self.logger.info(f"Starting validation: {self.description}")
        start_time = time.time()

        try:
            passed, message, details = await self.validate()
            duration_ms = (time.time() - start_time) * 1000

            result = ValidationResult(
                check_name=self.name,
                passed=passed,
                message=message,
                details=details,
                duration_ms=duration_ms,
            )

            self.logger.validation_result(self.name, passed, details)
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Validation check failed: {self.name}", error=e)

            return ValidationResult(
                check_name=self.name,
                passed=False,
                message=f"Validation failed with error: {e!s}",
                details={"error_type": e.__class__.__name__},
                duration_ms=duration_ms,
                error=str(e),
            )

    async def validate(self) -> tuple[bool, str, dict[str, Any]]:
        """
        Perform the actual validation.

        Returns:
            Tuple of (passed, message, details)
        """
        raise NotImplementedError("Subclasses must implement validate method")


class ACGSValidator:
    """Main ACGS validation orchestrator."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = get_config()
        self.logger = get_logger("validator")
        self.http_client = HTTPClient(
            timeout=self.config.validation_timeout, max_retries=3
        )
        self.checks: list[BaseValidationCheck] = []

    def add_check(self, check: BaseValidationCheck) -> None:
        """Add a validation check."""
        self.checks.append(check)
        self.logger.debug(f"Added validation check: {check.name}")

    def add_checks(self, checks: list[BaseValidationCheck]) -> None:
        """Add multiple validation checks."""
        for check in checks:
            self.add_check(check)

    async def run_all(
        self, parallel: bool = True, max_concurrent: int = None
    ) -> ValidationSummary:
        """
        Run all validation checks.

        Args:
            parallel: Whether to run checks in parallel
            max_concurrent: Maximum concurrent checks (uses config default if None)

        Returns:
            ValidationSummary with all results
        """
        if not self.checks:
            self.logger.warning("No validation checks to run")
            return ValidationSummary(
                total_checks=0, passed_checks=0, failed_checks=0, total_duration_ms=0.0
            )

        max_concurrent = max_concurrent or self.config.max_concurrent_validations
        self.logger.info(f"Running {len(self.checks)} validation checks")

        start_time = time.time()

        if parallel and len(self.checks) > 1:
            results = await self._run_parallel(max_concurrent)
        else:
            results = await self._run_sequential()

        total_duration_ms = (time.time() - start_time) * 1000

        # Calculate summary
        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = len(results) - passed_checks

        summary = ValidationSummary(
            total_checks=len(results),
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            total_duration_ms=total_duration_ms,
            results=results,
        )

        # Log summary
        self.logger.performance(
            "Validation suite completed",
            total_duration_ms,
            passed=passed_checks,
            failed=failed_checks,
            success_rate=summary.success_rate,
        )

        if summary.all_passed:
            self.logger.success(f"All {len(results)} validation checks passed!")
        else:
            self.logger.error(
                f"{failed_checks} of {len(results)} validation checks failed"
            )

        return summary

    async def _run_sequential(self) -> list[ValidationResult]:
        """Run validation checks sequentially."""
        results = []

        for i, check in enumerate(self.checks, 1):
            self.logger.info(f"Running check {i}/{len(self.checks)}: {check.name}")
            result = await check.run()
            results.append(result)

        return results

    async def _run_parallel(self, max_concurrent: int) -> list[ValidationResult]:
        """Run validation checks in parallel."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(check: BaseValidationCheck) -> ValidationResult:
            async with semaphore:
                return await check.run()

        self.logger.info(
            f"Running checks in parallel (max concurrent: {max_concurrent})"
        )

        # Run all checks concurrently
        tasks = [run_with_semaphore(check) for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                check_name = self.checks[i].name
                self.logger.error(f"Check {check_name} raised exception", error=result)
                processed_results.append(
                    ValidationResult(
                        check_name=check_name,
                        passed=False,
                        message=f"Check failed with exception: {result!s}",
                        error=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def run_check(self, check_name: str) -> Optional[ValidationResult]:
        """
        Run a specific validation check by name.

        Args:
            check_name: Name of the check to run

        Returns:
            ValidationResult if check found, None otherwise
        """
        for check in self.checks:
            if check.name == check_name:
                self.logger.info(f"Running specific check: {check_name}")
                return await check.run()

        self.logger.error(f"Validation check not found: {check_name}")
        return None

    def list_checks(self) -> list[dict[str, str]]:
        """List all available validation checks."""
        return [
            {
                "name": check.name,
                "description": check.description,
                "type": check.__class__.__name__,
            }
            for check in self.checks
        ]

    async def __aenter__(self):
        """Async context manager entry."""
        await self.http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
