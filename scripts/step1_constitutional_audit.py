#!/usr/bin/env python3
"""
Step 1: Constitutional Compliance Audit and Code Review

Targeted implementation of the constitutional compliance requirements:
1. Hash Verification: Confirm `cdd01ef066bc6cf2` exists in all files
2. Service Port Validation
3. Code Quality Checks

Constitutional Hash: cdd01ef066bc6cf2
"""

import re
import subprocess
from pathlib import Path

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
AUTH_SERVICE_PORT = 8016
POSTGRESQL_PORT = 5439
REDIS_PORT = 6389


def verify_constitutional_hash() -> dict[str, int]:
    """Verify constitutional hash exists in key files."""
    print("📋 1. Hash Verification: Confirming constitutional hash in all files...")

    # Key directories to check
    key_dirs = [
        "services/platform_services/api_gateway",
        "services/platform_services/authentication",
        "services/core/constitutional-ai",
        "services/shared/middleware",
    ]

    files_with_hash = 0
    files_without_hash = 0

    for dir_path in key_dirs:
        dir_full_path = Path("/home/dislove/ACGS-2") / dir_path
        if not dir_full_path.exists():
            continue

        for py_file in dir_full_path.glob("**/*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                        if CONSTITUTIONAL_HASH in content:
                            files_with_hash += 1
                        else:
                            files_without_hash += 1
                            print(
                                "  ❌ Missing hash:"
                                f" {py_file.relative_to(Path('/home/dislove/ACGS-2'))}"
                            )
                except Exception:
                    continue

    print(f"  ✅ Files with constitutional hash: {files_with_hash}")
    print(f"  ❌ Files missing constitutional hash: {files_without_hash}")

    return {"with_hash": files_with_hash, "without_hash": files_without_hash}


def validate_service_ports() -> dict[str, list[str]]:
    """Validate service port configurations."""
    print("🔌 2. Service Port Validation:")
    print(f"   - Auth Service: Enforcing port {AUTH_SERVICE_PORT}")
    print(f"   - PostgreSQL: Enforcing port {POSTGRESQL_PORT}")
    print(f"   - Redis: Enforcing port {REDIS_PORT}")

    violations = {
        "auth_violations": [],
        "postgres_violations": [],
        "redis_violations": [],
    }

    # Check key files for port violations
    key_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py",
        "services/platform_services/authentication/auth_service/app/main.py",
        "infrastructure/docker/docker-compose.yml",
        "infrastructure/docker/docker-compose.acgs.yml",
    ]

    for file_path in key_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

                # Check for incorrect ports
                if "auth" in str(full_path).lower():
                    if re.search(r"\b(8001|8000|3000)\b", content):
                        violations["auth_violations"].append(str(full_path))

                if re.search(r"\b5432\b", content):
                    violations["postgres_violations"].append(str(full_path))

                if re.search(r"\b6379\b", content):
                    violations["redis_violations"].append(str(full_path))

        except Exception:
            continue

    for violation_type, files in violations.items():
        print(f"   {violation_type}: {len(files)} violations")
        for file_path in files:
            print(f"     - {file_path}")

    return violations


def check_mypy_async_functions() -> dict[str, list[str]]:
    """Check MyPy type checking for async functions."""
    print("🔍 3. Code Quality Checks - MyPy type checking for async functions:")

    # Target specific files with async functions
    target_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py",
        "services/platform_services/authentication/auth_service/app/crud/crud_user.py",
        "services/shared/middleware/prometheus_metrics_middleware.py",
    ]

    mypy_issues = {}

    for file_path in target_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        print(f"   Checking {file_path}...")

        try:
            result = subprocess.run(
                [
                    "/home/dislove/ACGS-2/.venv/bin/python3",
                    "-m",
                    "mypy",
                    "--strict",
                    "--ignore-missing-imports",
                    str(full_path),
                ],
                capture_output=True,
                text=True,
                cwd="/home/dislove/ACGS-2",
            )

            if result.returncode != 0:
                issues = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
                mypy_issues[file_path] = issues
                print(f"     ❌ {len(issues)} MyPy issues found")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"       - {issue}")
                if len(issues) > 3:
                    print(f"       ... and {len(issues) - 3} more")
            else:
                print("     ✅ No MyPy issues")

        except Exception as e:
            print(f"     ❌ MyPy check failed: {e}")

    return mypy_issues


def apply_black_formatting() -> int:
    """Apply Black formatting to key files."""
    print("🎨 4. Applying Black formatting:")

    target_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py",
        "services/platform_services/authentication/auth_service/app/crud/crud_user.py",
    ]

    formatted_files = 0

    for file_path in target_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        try:
            # Check if formatting is needed
            check_result = subprocess.run(
                [
                    "/home/dislove/ACGS-2/.venv/bin/python3",
                    "-m",
                    "black",
                    "--check",
                    str(full_path),
                ],
                capture_output=True,
                text=True,
                cwd="/home/dislove/ACGS-2",
            )

            if check_result.returncode != 0:
                # Apply formatting
                format_result = subprocess.run(
                    [
                        "/home/dislove/ACGS-2/.venv/bin/python3",
                        "-m",
                        "black",
                        str(full_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd="/home/dislove/ACGS-2",
                )

                if format_result.returncode == 0:
                    formatted_files += 1
                    print(f"   ✅ Applied Black formatting to {file_path}")
                else:
                    print(f"   ❌ Failed to format {file_path}")
            else:
                print(f"   ✅ {file_path} already properly formatted")

        except Exception as e:
            print(f"   ❌ Failed to check/format {file_path}: {e}")

    return formatted_files


def apply_isort_sorting() -> int:
    """Apply isort import sorting to key files."""
    print("📂 5. Applying isort import sorting:")

    target_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py",
        "services/platform_services/authentication/auth_service/app/crud/crud_user.py",
    ]

    sorted_files = 0

    for file_path in target_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        try:
            # Check if sorting is needed
            check_result = subprocess.run(
                [
                    "/home/dislove/ACGS-2/.venv/bin/python3",
                    "-m",
                    "isort",
                    "--check-only",
                    str(full_path),
                ],
                capture_output=True,
                text=True,
                cwd="/home/dislove/ACGS-2",
            )

            if check_result.returncode != 0:
                # Apply sorting
                sort_result = subprocess.run(
                    [
                        "/home/dislove/ACGS-2/.venv/bin/python3",
                        "-m",
                        "isort",
                        str(full_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd="/home/dislove/ACGS-2",
                )

                if sort_result.returncode == 0:
                    sorted_files += 1
                    print(f"   ✅ Applied isort sorting to {file_path}")
                else:
                    print(f"   ❌ Failed to sort imports in {file_path}")
            else:
                print(f"   ✅ {file_path} imports already properly sorted")

        except Exception as e:
            print(f"   ❌ Failed to check/sort {file_path}: {e}")

    return sorted_files


def add_missing_error_handlers() -> int:
    """Add missing error handlers using FastAPI exception middleware pattern."""
    print("🛡️ 6. Adding missing FastAPI exception middleware error handlers:")

    # Target FastAPI main files
    target_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py"
    ]

    error_handler_template = '''

# Constitutional compliance error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with constitutional compliance."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with constitutional compliance."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": 500
        }
    )
'''

    handlers_added = 0

    for file_path in target_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            # Check if error handlers already exist
            if "@app.exception_handler(HTTPException)" in content:
                print(f"   ✅ {file_path} already has error handlers")
                continue

            # Check if this is a FastAPI app file
            if "FastAPI" in content and "app = FastAPI" in content:
                # Add required imports if missing
                imports_to_add = []
                if "from datetime import datetime, timezone" not in content:
                    imports_to_add.append("from datetime import datetime, timezone")
                if "from fastapi.responses import JSONResponse" not in content:
                    imports_to_add.append("from fastapi.responses import JSONResponse")
                if "import logging" not in content:
                    imports_to_add.append("import logging")
                    imports_to_add.append("logger = logging.getLogger(__name__)")

                # Add imports
                if imports_to_add:
                    lines = content.split("\n")
                    last_import_idx = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith(
                            ("import ", "from ")
                        ) and not line.strip().startswith("#"):
                            last_import_idx = i

                    if last_import_idx >= 0:
                        for import_line in reversed(imports_to_add):
                            lines.insert(last_import_idx + 1, import_line)
                        content = "\n".join(lines)

                # Add error handlers at the end
                content += error_handler_template

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                handlers_added += 1
                print(f"   ✅ Added error handlers to {file_path}")
            else:
                print(f"   ⚠️ {file_path} is not a FastAPI app file")

        except Exception as e:
            print(f"   ❌ Failed to add error handlers to {file_path}: {e}")

    return handlers_added


def fix_mypy_type_annotations() -> int:
    """Fix common MyPy type annotation issues in async functions."""
    print("🔧 7. Fixing MyPy type annotations for async functions:")

    # Target specific files that need fixes
    target_files = [
        "services/platform_services/api_gateway/gateway_service/app/main.py"
    ]

    fixes_applied = 0

    for file_path in target_files:
        full_path = Path("/home/dislove/ACGS-2") / file_path
        if not full_path.exists():
            continue

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix async function return types
            # Add -> None for async functions without return type
            async_func_pattern = r"(async def \w+\([^)]*\)):"
            async_funcs = re.findall(async_func_pattern, content)

            for func_def in async_funcs:
                if " -> " not in func_def:
                    # Add -> None return type
                    old_pattern = func_def + ":"
                    new_pattern = func_def + " -> None:"
                    content = content.replace(old_pattern, new_pattern)

            # Fix dict type annotations
            content = re.sub(r"(\w+: )dict([,\)\]\s])", r"\1Dict[str, Any]\2", content)

            # Add missing imports
            if "Dict[str, Any]" in content and "from typing import" in content:
                if "Any" not in content:
                    content = re.sub(
                        r"(from typing import [^)]+)([)\n])", r"\1, Any\2", content
                    )
                if "Dict" not in content:
                    content = re.sub(
                        r"(from typing import [^)]+)([)\n])", r"\1, Dict\2", content
                    )

            if content != original_content:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                fixes_applied += 1
                print(f"   ✅ Fixed type annotations in {file_path}")
            else:
                print(f"   ✅ {file_path} type annotations already correct")

        except Exception as e:
            print(f"   ❌ Failed to fix type annotations in {file_path}: {e}")

    return fixes_applied


def main():
    """Run Step 1: Constitutional Compliance Audit and Code Review."""
    print("🏛️ ACGS Step 1: Constitutional Compliance Audit and Code Review")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 80)

    # 1. Hash Verification
    hash_results = verify_constitutional_hash()

    # 2. Service Port Validation
    port_violations = validate_service_ports()

    # 3. MyPy Type Checking
    mypy_issues = check_mypy_async_functions()

    # 4. Apply Black Formatting
    formatted_files = apply_black_formatting()

    # 5. Apply isort Import Sorting
    sorted_files = apply_isort_sorting()

    # 6. Add Missing Error Handlers
    handlers_added = add_missing_error_handlers()

    # 7. Fix MyPy Type Annotations
    type_fixes = fix_mypy_type_annotations()

    # Summary
    print("\n✅ STEP 1 COMPLETION SUMMARY:")
    print("=" * 50)
    print("📋 Constitutional Hash Verification:")
    print(f"   Files with hash: {hash_results['with_hash']}")
    print(f"   Files missing hash: {hash_results['without_hash']}")

    print("\n🔌 Service Port Validation:")
    total_violations = sum(len(v) for v in port_violations.values())
    print(f"   Total port violations found: {total_violations}")

    print("\n🔍 Code Quality Improvements:")
    print(f"   Files with MyPy issues: {len(mypy_issues)}")
    print(f"   Files formatted with Black: {formatted_files}")
    print(f"   Files sorted with isort: {sorted_files}")
    print(f"   Error handlers added: {handlers_added}")
    print(f"   Type annotation fixes: {type_fixes}")

    total_improvements = formatted_files + sorted_files + handlers_added + type_fixes
    print(f"\n🎉 Total code quality improvements: {total_improvements}")
    print("🏛️ Constitutional compliance audit completed!")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    main()
