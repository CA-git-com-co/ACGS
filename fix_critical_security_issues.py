#!/usr/bin/env python3
"""
ACGS-1 Phase A2: Critical Security Issues Remediation
Automatically fixes critical security vulnerabilities identified by Bandit
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class SecurityRemediator:
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
        self.files_modified = set()

    def fix_md5_usage(self, file_path, line_number):
        """Replace MD5 hash usage with SHA-256."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_number <= len(lines):
                original_line = lines[line_number - 1]

                # Replace MD5 with SHA-256
                if "hashlib.md5()" in original_line:
                    new_line = original_line.replace(
                        "hashlib.md5()", "hashlib.sha256()"
                    )
                    lines[line_number - 1] = new_line

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    self.fixes_applied.append(
                        {
                            "type": "MD5_to_SHA256",
                            "file": file_path,
                            "line": line_number,
                            "original": original_line.strip(),
                            "fixed": new_line.strip(),
                        }
                    )
                    self.files_modified.add(file_path)
                    return True

        except Exception as e:
            self.errors.append(
                {"file": file_path, "line": line_number, "error": str(e)}
            )
            return False

        return False

    def add_security_headers_middleware(self):
        """Add security headers middleware to FastAPI services."""

        security_middleware_code = '''
# Security Headers Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets

def add_security_middleware(app):
    """Add comprehensive security middleware to FastAPI app."""

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://localhost:3000", "https://127.0.0.1:3000"],  # Restrict origins
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"]
    )

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.acgs.local"]
    )

    # Session Middleware with secure settings
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.environ.get("SESSION_SECRET_KEY", secrets.token_urlsafe(32)),
        max_age=3600,  # 1 hour
        same_site="strict",
        https_only=True
    )

    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

    return app
'''

        # Create security middleware file
        security_file = Path("services/shared/security_middleware.py")
        security_file.parent.mkdir(parents=True, exist_ok=True)

        with open(security_file, "w") as f:
            f.write(security_middleware_code)

        self.fixes_applied.append(
            {
                "type": "Security_Middleware",
                "file": str(security_file),
                "description": "Added comprehensive security headers middleware",
            }
        )

        return str(security_file)

    def fix_input_validation(self):
        """Add input validation utilities."""

        validation_code = '''
# Input Validation Utilities
import re
from typing import Any, Optional
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
            value = re.sub(r'<[^>]*>', '', value)

        return value.strip()

    @staticmethod
    def validate_policy_id(policy_id: str) -> str:
        """Validate policy ID format."""
        if not re.match(r'^[A-Z]{2,3}-\\d{3}$', policy_id):
            raise HTTPException(status_code=400, detail="Invalid policy ID format")
        return policy_id

    @staticmethod
    def validate_hash(hash_value: str) -> str:
        """Validate hash format (SHA-256)."""
        if not re.match(r'^[a-fA-F0-9]{64}$', hash_value):
            raise HTTPException(status_code=400, detail="Invalid hash format")
        return hash_value.lower()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.replace('..', '')
        return filename[:255]  # Limit length
'''

        validation_file = Path("services/shared/input_validation.py")
        validation_file.parent.mkdir(parents=True, exist_ok=True)

        with open(validation_file, "w") as f:
            f.write(validation_code)

        self.fixes_applied.append(
            {
                "type": "Input_Validation",
                "file": str(validation_file),
                "description": "Added secure input validation utilities",
            }
        )

        return str(validation_file)

    def process_remediation_plan(self, plan_file):
        """Process the remediation plan and apply fixes."""

        try:
            with open(plan_file) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Remediation plan file {plan_file} not found")
            return False

        critical_actions = data.get("remediation_plan", {}).get("critical_actions", [])

        print(f"🔧 Processing {len(critical_actions)} critical security issues...")

        for i, action in enumerate(critical_actions, 1):
            if action["type"] == "Weak Cryptography":
                file_path = action["file"]
                line_number = action["line"]

                # Skip virtual environment files (not our code)
                if "/venv/" in file_path or "/site-packages/" in file_path:
                    print(f"  ⏭️  Skipping venv file: {file_path}")
                    continue

                print(f"  {i}. Fixing MD5 usage in {file_path}:{line_number}")

                if self.fix_md5_usage(file_path, line_number):
                    print("     ✅ Fixed MD5 → SHA-256")
                else:
                    print("     ❌ Failed to fix")

        return True

    def generate_report(self):
        """Generate remediation report."""

        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": len(self.fixes_applied),
            "files_modified": len(self.files_modified),
            "errors": len(self.errors),
            "details": {
                "fixes": self.fixes_applied,
                "errors": self.errors,
                "modified_files": list(self.files_modified),
            },
        }

        return report


def main():
    """Main execution function."""

    print("🔒 ACGS-1 Phase A2: Critical Security Issues Remediation")
    print("=" * 60)

    remediator = SecurityRemediator()

    # Process critical issues from remediation plan
    plan_file = "security_remediation_plan.json"
    if os.path.exists(plan_file):
        print("📋 Processing critical security issues...")
        remediator.process_remediation_plan(plan_file)
    else:
        print("⚠️  No remediation plan found, skipping automated fixes")

    # Add security infrastructure
    print("\n🛡️  Adding security infrastructure...")

    print("  • Adding security headers middleware...")
    remediator.add_security_headers_middleware()

    print("  • Adding input validation utilities...")
    remediator.fix_input_validation()

    # Generate report
    report = remediator.generate_report()

    # Save report
    report_file = "security_fixes_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 Remediation Summary:")
    print(f"  ✅ Fixes Applied: {report['fixes_applied']}")
    print(f"  📁 Files Modified: {report['files_modified']}")
    print(f"  ❌ Errors: {report['errors']}")

    if report["errors"] > 0:
        print("\n⚠️  Errors encountered:")
        for error in remediator.errors:
            print(f"    • {error['file']}:{error['line']} - {error['error']}")

    print(f"\n💾 Detailed report saved to: {report_file}")

    if report["fixes_applied"] > 0:
        print("\n✅ Critical security issues remediation completed!")
        print("🔄 Re-run security scan to validate improvements")
    else:
        print("\n⚠️  No fixes were applied")

    return 0 if report["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
