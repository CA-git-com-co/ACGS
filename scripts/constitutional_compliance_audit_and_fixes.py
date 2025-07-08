#!/usr/bin/env python3
"""
Constitutional Compliance Audit and Code Quality Enhancement

This script implements the required constitutional compliance audit and
code quality improvements for the ACGS system.

Constitutional Hash: cdd01ef066bc6cf2
"""

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
AUTH_SERVICE_PORT = 8016
POSTGRESQL_PORT = 5439
REDIS_PORT = 6389


@dataclass
class AuditResult:
    """Results of the constitutional compliance audit."""

    hash_verification: Dict[str, bool]
    port_validation: Dict[str, List[str]]
    mypy_issues: Dict[str, List[str]]
    formatting_issues: Dict[str, List[str]]
    missing_error_handlers: Dict[str, List[str]]
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ConstitutionalComplianceAuditor:
    """Constitutional compliance auditor and code quality enforcer."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.issues_found = {}

    def run_audit(self) -> AuditResult:
        """Run comprehensive constitutional compliance audit."""
        print(
            f"🏛️ Starting Constitutional Compliance Audit (Hash: {self.constitutional_hash})"
        )

        # 1. Hash Verification
        print("📋 1. Verifying constitutional hash in all files...")
        hash_verification = self._verify_constitutional_hash()

        # 2. Service Port Validation
        print("🔌 2. Validating service port configurations...")
        port_validation = self._validate_service_ports()

        # 3. MyPy Type Checking for Async Functions
        print("🔍 3. Running MyPy type checking on async functions...")
        mypy_issues = self._check_async_function_types()

        # 4. Black Formatting Check
        print("🎨 4. Checking Black formatting compliance...")
        formatting_issues = self._check_formatting()

        # 5. Missing Error Handlers
        print("🛡️ 5. Checking for missing FastAPI error handlers...")
        missing_error_handlers = self._check_error_handlers()

        return AuditResult(
            hash_verification=hash_verification,
            port_validation=port_validation,
            mypy_issues=mypy_issues,
            formatting_issues=formatting_issues,
            missing_error_handlers=missing_error_handlers,
        )

    def _verify_constitutional_hash(self) -> Dict[str, bool]:
        """Verify constitutional hash exists in all relevant files."""
        results = {}

        # Define file patterns to check
        patterns = ["**/*.py", "**/*.yml", "**/*.yaml", "**/*.md", "**/*.json"]

        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if self._should_skip_file(file_path) or file_path.is_dir():
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        results[str(file_path.relative_to(self.project_root))] = (
                            self.constitutional_hash in content
                        )
                except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                    # Skip binary files, directories, or files we can't read
                    continue

        return results

    def _validate_service_ports(self) -> Dict[str, List[str]]:
        """Validate service port configurations."""
        issues = {
            "auth_service_port_violations": [],
            "postgresql_port_violations": [],
            "redis_port_violations": [],
        }

        # Search for port configurations
        port_patterns = {
            "auth_service": {
                "correct": str(AUTH_SERVICE_PORT),
                "incorrect": [r"(?<!80)16(?!39)", "8001", "8000", "3000"],
            },
            "postgresql": {
                "correct": str(POSTGRESQL_PORT),
                "incorrect": ["5432", "5433", "5434"],
            },
            "redis": {
                "correct": str(REDIS_PORT),
                "incorrect": ["6379", "6380", "6381"],
            },
        }

        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path) or file_path.is_dir():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Check for auth service port violations
                    if "auth" in str(file_path).lower():
                        for incorrect_port in port_patterns["auth_service"][
                            "incorrect"
                        ]:
                            if re.search(rf"\b{incorrect_port}\b", content):
                                issues["auth_service_port_violations"].append(
                                    f"{file_path}: Found port {incorrect_port} instead of {AUTH_SERVICE_PORT}"
                                )

                    # Check for PostgreSQL port violations
                    if any(
                        db_term in content.lower()
                        for db_term in ["postgres", "postgresql", "psql"]
                    ):
                        for incorrect_port in port_patterns["postgresql"]["incorrect"]:
                            if re.search(rf"\b{incorrect_port}\b", content):
                                issues["postgresql_port_violations"].append(
                                    f"{file_path}: Found port {incorrect_port} instead of {POSTGRESQL_PORT}"
                                )

                    # Check for Redis port violations
                    if "redis" in content.lower():
                        for incorrect_port in port_patterns["redis"]["incorrect"]:
                            if re.search(rf"\b{incorrect_port}\b", content):
                                issues["redis_port_violations"].append(
                                    f"{file_path}: Found port {incorrect_port} instead of {REDIS_PORT}"
                                )

            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                continue

        return issues

    def _check_async_function_types(self) -> Dict[str, List[str]]:
        """Check MyPy type annotations for async functions."""
        issues = {}

        # Find Python files with async functions
        async_files = self._find_files_with_async_functions()

        for file_path in async_files:
            try:
                # Run MyPy on the file
                result = subprocess.run(
                    [
                        "/home/dislove/ACGS-2/.venv/bin/python3",
                        "-m",
                        "mypy",
                        "--strict",
                        "--ignore-missing-imports",
                        str(file_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode != 0:
                    issues[str(file_path.relative_to(self.project_root))] = (
                        result.stdout.split("\n")
                        if result.stdout
                        else result.stderr.split("\n")
                    )

            except Exception as e:
                issues[str(file_path.relative_to(self.project_root))] = [
                    f"MyPy check failed: {e}"
                ]

        return issues

    def _check_formatting(self) -> Dict[str, List[str]]:
        """Check Black formatting and isort import sorting."""
        issues = {"black_issues": [], "isort_issues": []}

        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path) or file_path.is_dir():
                continue

            # Check Black formatting
            try:
                result = subprocess.run(
                    [
                        "/home/dislove/ACGS-2/.venv/bin/python3",
                        "-m",
                        "black",
                        "--check",
                        str(file_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode != 0:
                    issues["black_issues"].append(
                        str(file_path.relative_to(self.project_root))
                    )

            except Exception as e:
                issues["black_issues"].append(f"{file_path}: Black check failed - {e}")

            # Check isort import sorting
            try:
                result = subprocess.run(
                    [
                        "/home/dislove/ACGS-2/.venv/bin/python3",
                        "-m",
                        "isort",
                        "--check-only",
                        str(file_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode != 0:
                    issues["isort_issues"].append(
                        str(file_path.relative_to(self.project_root))
                    )

            except Exception as e:
                issues["isort_issues"].append(f"{file_path}: isort check failed - {e}")

        return issues

    def _check_error_handlers(self) -> Dict[str, List[str]]:
        """Check for missing FastAPI error handlers."""
        issues = {"missing_error_handlers": []}

        # Look for FastAPI apps without proper error handlers
        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path) or file_path.is_dir():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if this is a FastAPI app file
                if "FastAPI" in content and "app = FastAPI" in content:
                    # Check for exception handlers
                    has_http_exception_handler = (
                        "@app.exception_handler(HTTPException)" in content
                    )
                    has_general_exception_handler = (
                        "@app.exception_handler(Exception)" in content
                    )
                    has_add_exception_handler = "add_exception_handler" in content

                    if not (
                        has_http_exception_handler
                        or has_general_exception_handler
                        or has_add_exception_handler
                    ):
                        issues["missing_error_handlers"].append(
                            str(file_path.relative_to(self.project_root))
                        )

            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                continue

        return issues

    def _find_files_with_async_functions(self) -> List[Path]:
        """Find Python files containing async functions."""
        async_files = []

        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path) or file_path.is_dir():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if re.search(r"async\s+def\s+", content):
                        async_files.append(file_path)
            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                continue

        return async_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped in audit."""
        skip_patterns = [
            ".git/",
            "__pycache__/",
            ".pytest_cache/",
            ".mypy_cache/",
            "node_modules/",
            ".venv/",
            "venv/",
            ".env",
            "*.pyc",
            "*.pyo",
            "*.egg-info/",
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)


class ConstitutionalComplianceFixer:
    """Fix constitutional compliance and code quality issues."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def apply_fixes(self, audit_result: AuditResult) -> Dict[str, int]:
        """Apply fixes for identified issues."""
        fixes_applied = {
            "hash_fixes": 0,
            "port_fixes": 0,
            "mypy_fixes": 0,
            "formatting_fixes": 0,
            "error_handler_fixes": 0,
        }

        print("🔧 Applying constitutional compliance fixes...")

        # 1. Add missing constitutional hashes
        fixes_applied["hash_fixes"] = self._fix_missing_hashes(
            audit_result.hash_verification
        )

        # 2. Fix port configurations
        fixes_applied["port_fixes"] = self._fix_port_configurations(
            audit_result.port_validation
        )

        # 3. Fix MyPy type annotations
        fixes_applied["mypy_fixes"] = self._fix_mypy_issues(audit_result.mypy_issues)

        # 4. Apply Black formatting and isort
        fixes_applied["formatting_fixes"] = self._fix_formatting_issues(
            audit_result.formatting_issues
        )

        # 5. Add missing error handlers
        fixes_applied["error_handler_fixes"] = self._fix_missing_error_handlers(
            audit_result.missing_error_handlers
        )

        return fixes_applied

    def _fix_missing_hashes(self, hash_verification: Dict[str, bool]) -> int:
        """Add missing constitutional hashes to files."""
        fixes = 0

        for file_path, has_hash in hash_verification.items():
            if not has_hash and file_path.endswith(".py"):
                full_path = self.project_root / file_path
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Add constitutional hash comment at the top
                    if not content.startswith('"""') and not content.startswith("#"):
                        new_content = f"# Constitutional Hash: {self.constitutional_hash}\n{content}"
                    elif '"""' in content:
                        # Add to docstring
                        docstring_end = content.find('"""', 3) + 3
                        if docstring_end > 2:
                            new_content = (
                                content[: docstring_end - 3]
                                + f"\nConstitutional Hash: {self.constitutional_hash}\n"
                                + content[docstring_end - 3 :]
                            )
                        else:
                            new_content = f"# Constitutional Hash: {self.constitutional_hash}\n{content}"
                    else:
                        new_content = f"# Constitutional Hash: {self.constitutional_hash}\n{content}"

                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    fixes += 1
                    print(f"  ✅ Added constitutional hash to {file_path}")

                except Exception as e:
                    print(f"  ❌ Failed to fix hash in {file_path}: {e}")

        return fixes

    def _fix_port_configurations(self, port_validation: Dict[str, List[str]]) -> int:
        """Fix incorrect port configurations."""
        fixes = 0

        port_replacements = {
            # Auth service ports
            "8001": str(AUTH_SERVICE_PORT),
            "8000": str(AUTH_SERVICE_PORT),
            "3000": str(AUTH_SERVICE_PORT),
            # PostgreSQL ports
            "5432": str(POSTGRESQL_PORT),
            "5433": str(POSTGRESQL_PORT),
            "5434": str(POSTGRESQL_PORT),
            # Redis ports
            "6379": str(REDIS_PORT),
            "6380": str(REDIS_PORT),
            "6381": str(REDIS_PORT),
        }

        all_violations = []
        for violation_list in port_validation.values():
            all_violations.extend(violation_list)

        for violation in all_violations:
            try:
                file_path_str = violation.split(":")[0]
                file_path = Path(file_path_str)

                if not file_path.exists():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                for incorrect_port, correct_port in port_replacements.items():
                    # Use word boundaries to avoid partial replacements
                    content = re.sub(rf"\b{incorrect_port}\b", correct_port, content)

                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    fixes += 1
                    print(f"  ✅ Fixed port configuration in {file_path}")

            except Exception as e:
                print(f"  ❌ Failed to fix port in {violation}: {e}")

        return fixes

    def _fix_mypy_issues(self, mypy_issues: Dict[str, List[str]]) -> int:
        """Fix common MyPy type annotation issues."""
        fixes = 0

        for file_path_str, issues in mypy_issues.items():
            file_path = self.project_root / file_path_str

            if not file_path.exists():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Fix common async function return type issues
                content = self._fix_async_return_types(content, issues)

                # Fix missing type imports
                content = self._fix_missing_type_imports(content, issues)

                # Fix generic type arguments
                content = self._fix_generic_type_args(content, issues)

                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    fixes += 1
                    print(f"  ✅ Fixed MyPy issues in {file_path_str}")

            except Exception as e:
                print(f"  ❌ Failed to fix MyPy issues in {file_path_str}: {e}")

        return fixes

    def _fix_async_return_types(self, content: str, issues: List[str]) -> str:
        """Fix missing return type annotations for async functions."""
        # Add -> None for async functions that don't return values
        no_return_pattern = r"(async def \w+\([^)]*\)):"

        for issue in issues:
            if "missing a return type annotation" in issue and "-> None" in issue:
                # Extract function name from issue
                func_match = re.search(r"async def (\w+)", issue)
                if func_match:
                    func_name = func_match.group(1)
                    pattern = rf"(async def {func_name}\([^)]*\)):"
                    replacement = r"\1 -> None:"
                    content = re.sub(pattern, replacement, content)

        # Fix dict type annotations
        content = re.sub(r"(\w+: )dict([,\)\]\s])", r"\1Dict[str, Any]\2", content)

        # Add Any import if needed and not present
        if "Dict[str, Any]" in content and "from typing import" in content:
            if "Any" not in content:
                content = re.sub(
                    r"(from typing import [^)]+)([)\n])", r"\1, Any\2", content
                )

        return content

    def _fix_missing_type_imports(self, content: str, issues: List[str]) -> str:
        """Add missing type imports."""
        imports_needed = set()

        for issue in issues:
            if "Dict" in issue and "from typing import" in content:
                imports_needed.add("Dict")
            if "List" in issue and "from typing import" in content:
                imports_needed.add("List")
            if "Optional" in issue and "from typing import" in content:
                imports_needed.add("Optional")
            if "Union" in issue and "from typing import" in content:
                imports_needed.add("Union")
            if "Callable" in issue and "from typing import" in content:
                imports_needed.add("Callable")
            if "Any" in issue and "from typing import" in content:
                imports_needed.add("Any")

        # Add missing imports to existing typing import
        if imports_needed and "from typing import" in content:
            for import_name in imports_needed:
                if import_name not in content:
                    content = re.sub(
                        r"(from typing import [^)]+)([)\n])",
                        f"\\1, {import_name}\\2",
                        content,
                    )

        return content

    def _fix_generic_type_args(self, content: str, issues: List[str]) -> str:
        """Fix missing generic type arguments."""
        # Fix dict -> Dict[str, Any]
        content = re.sub(r"\bdict\b(?!\[)", "Dict[str, Any]", content)

        # Fix list -> List[Any]
        content = re.sub(r"\blist\b(?!\[)", "List[Any]", content)

        return content

    def _fix_formatting_issues(self, formatting_issues: Dict[str, List[str]]) -> int:
        """Apply Black formatting and isort import sorting."""
        fixes = 0

        # Apply Black formatting
        for file_path_str in formatting_issues.get("black_issues", []):
            if isinstance(file_path_str, str) and not file_path_str.startswith("/"):
                file_path = self.project_root / file_path_str
                try:
                    subprocess.run(
                        [
                            "/home/dislove/ACGS-2/.venv/bin/python3",
                            "-m",
                            "black",
                            str(file_path),
                        ],
                        check=True,
                        cwd=self.project_root,
                    )
                    fixes += 1
                    print(f"  ✅ Applied Black formatting to {file_path_str}")
                except Exception as e:
                    print(
                        f"  ❌ Failed to apply Black formatting to {file_path_str}: {e}"
                    )

        # Apply isort import sorting
        for file_path_str in formatting_issues.get("isort_issues", []):
            if isinstance(file_path_str, str) and not file_path_str.startswith("/"):
                file_path = self.project_root / file_path_str
                try:
                    subprocess.run(
                        [
                            "/home/dislove/ACGS-2/.venv/bin/python3",
                            "-m",
                            "isort",
                            str(file_path),
                        ],
                        check=True,
                        cwd=self.project_root,
                    )
                    fixes += 1
                    print(f"  ✅ Applied isort import sorting to {file_path_str}")
                except Exception as e:
                    print(f"  ❌ Failed to apply isort to {file_path_str}: {e}")

        return fixes

    def _fix_missing_error_handlers(
        self, missing_error_handlers: Dict[str, List[str]]
    ) -> int:
        """Add missing FastAPI error handlers."""
        fixes = 0

        error_handler_template = '''

# Constitutional compliance error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with constitutional compliance."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "constitutional_hash": "{constitutional_hash}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with constitutional compliance."""
    logger.error(f"Unhandled exception: {{exc}}")
    return JSONResponse(
        status_code=500,
        content={{
            "detail": "Internal server error",
            "constitutional_hash": "{constitutional_hash}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": 500
        }}
    )
'''.format(
            constitutional_hash=self.constitutional_hash
        )

        for file_path_str in missing_error_handlers.get("missing_error_handlers", []):
            file_path = self.project_root / file_path_str

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if we need to add imports
                imports_to_add = []
                if "from datetime import datetime, timezone" not in content:
                    imports_to_add.append("from datetime import datetime, timezone")
                if "from fastapi.responses import JSONResponse" not in content:
                    imports_to_add.append("from fastapi.responses import JSONResponse")
                if "import logging" not in content and "logger" not in content:
                    imports_to_add.append("import logging")
                    imports_to_add.append("logger = logging.getLogger(__name__)")

                # Add imports after existing imports
                if imports_to_add:
                    import_section = "\n".join(imports_to_add) + "\n"
                    # Find the last import statement
                    lines = content.split("\n")
                    last_import_idx = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith(
                            ("import ", "from ")
                        ) and not line.strip().startswith("#"):
                            last_import_idx = i

                    if last_import_idx >= 0:
                        lines.insert(last_import_idx + 1, import_section)
                        content = "\n".join(lines)

                # Add error handlers at the end of the file
                content += error_handler_template

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                fixes += 1
                print(f"  ✅ Added error handlers to {file_path_str}")

            except Exception as e:
                print(f"  ❌ Failed to add error handlers to {file_path_str}: {e}")

        return fixes


def main():
    """Run the constitutional compliance audit and apply fixes."""
    print("🏛️ ACGS Constitutional Compliance Audit and Code Quality Enhancement")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 80)

    # Initialize auditor
    auditor = ConstitutionalComplianceAuditor()

    # Run audit
    audit_result = auditor.run_audit()

    # Print audit results
    print("\n📊 AUDIT RESULTS:")
    print("=" * 50)

    # Hash verification results
    missing_hashes = sum(
        1 for has_hash in audit_result.hash_verification.values() if not has_hash
    )
    total_files = len(audit_result.hash_verification)
    print(f"📋 Constitutional Hash Verification:")
    print(f"   ✅ Files with hash: {total_files - missing_hashes}/{total_files}")
    print(f"   ❌ Files missing hash: {missing_hashes}")

    # Port validation results
    print(f"\n🔌 Service Port Validation:")
    for violation_type, violations in audit_result.port_validation.items():
        print(f"   {violation_type}: {len(violations)} violations")

    # MyPy issues
    print(f"\n🔍 MyPy Type Checking:")
    total_mypy_issues = sum(len(issues) for issues in audit_result.mypy_issues.values())
    print(f"   Files with issues: {len(audit_result.mypy_issues)}")
    print(f"   Total issues: {total_mypy_issues}")

    # Formatting issues
    print(f"\n🎨 Code Formatting:")
    black_issues = len(audit_result.formatting_issues.get("black_issues", []))
    isort_issues = len(audit_result.formatting_issues.get("isort_issues", []))
    print(f"   Black formatting issues: {black_issues}")
    print(f"   Import sorting issues: {isort_issues}")

    # Error handler issues
    print(f"\n🛡️ Error Handlers:")
    missing_handlers = len(
        audit_result.missing_error_handlers.get("missing_error_handlers", [])
    )
    print(f"   Missing error handlers: {missing_handlers}")

    # Apply fixes
    print("\n🔧 APPLYING FIXES:")
    print("=" * 50)

    fixer = ConstitutionalComplianceFixer()
    fixes_applied = fixer.apply_fixes(audit_result)

    print("\n✅ FIXES COMPLETED:")
    print("=" * 50)
    for fix_type, count in fixes_applied.items():
        print(f"   {fix_type}: {count} fixes applied")

    total_fixes = sum(fixes_applied.values())
    print(f"\n🎉 Total fixes applied: {total_fixes}")
    print(f"🏛️ Constitutional compliance enhanced!")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    main()
