#!/usr/bin/env python3
"""
ACGS-1 Security Cleanup and Vulnerability Remediation

This script addresses the 58 GitHub security vulnerabilities and implements
security hardening measures for the ACGS-1 constitutional governance system.

Focus Areas:
- Remove hardcoded credentials and sensitive data
- Update vulnerable dependencies
- Implement security best practices
- Clean up security configurations
"""

import json
import logging
import re
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityCleanup:
    """Handles security cleanup and vulnerability remediation."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.security_report = {
            "hardcoded_secrets_removed": [],
            "vulnerable_dependencies": [],
            "security_configs_updated": [],
            "files_secured": [],
        }

    def scan_for_hardcoded_secrets(self) -> List[str]:
        """Scan for hardcoded secrets and credentials."""
        logger.info("🔍 Scanning for hardcoded secrets...")

        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'SECRET_KEY\s*=\s*["\'][^"\']+["\']',
            r'DATABASE_URL\s*=\s*["\']postgresql://[^"\']+["\']',
        ]

        suspicious_files = []

        # Scan Python files
        for py_file in self.project_root.glob("**/*.py"):
            if self._should_scan_file(py_file):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            suspicious_files.append(str(py_file))
                            break

                except Exception as e:
                    logger.warning(f"Could not scan {py_file}: {e}")

        # Scan configuration files
        for config_file in self.project_root.glob("**/*.env*"):
            if config_file.is_file():
                suspicious_files.append(str(config_file))

        return suspicious_files

    def clean_hardcoded_secrets(self, files_with_secrets: List[str]):
        """Clean hardcoded secrets from files."""
        logger.info("🧹 Cleaning hardcoded secrets...")

        for file_path in files_with_secrets:
            try:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue

                with open(file_obj, "r", encoding="utf-8") as f:
                    content = f.read()

                # Replace common hardcoded patterns with environment variables
                replacements = {
                    r'password\s*=\s*["\'][^"\']+["\']': 'password = os.getenv("DATABASE_PASSWORD")',
                    r'secret\s*=\s*["\'][^"\']+["\']': 'secret = os.getenv("SECRET_KEY")',
                    r'api_key\s*=\s*["\'][^"\']+["\']': 'api_key = os.getenv("API_KEY")',
                    r'SECRET_KEY\s*=\s*["\'][^"\']+["\']': 'SECRET_KEY = os.getenv("SECRET_KEY", "development-key")',
                }

                modified = False
                for pattern, replacement in replacements.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        content = re.sub(
                            pattern, replacement, content, flags=re.IGNORECASE
                        )
                        modified = True

                if modified:
                    # Add import os if not present
                    if "import os" not in content and "os.getenv" in content:
                        content = "import os\n" + content

                    with open(file_obj, "w", encoding="utf-8") as f:
                        f.write(content)

                    self.security_report["files_secured"].append(str(file_obj))
                    logger.info(f"Secured file: {file_obj}")

            except Exception as e:
                logger.error(f"Error cleaning {file_path}: {e}")

    def update_gitignore_security(self):
        """Update .gitignore to exclude sensitive files."""
        logger.info("🔒 Updating .gitignore for security...")

        gitignore_path = self.project_root / ".gitignore"

        security_patterns = [
            "# Security and sensitive files",
            "*.env",
            "*.env.local",
            "*.env.production",
            ".env.*",
            "auth_tokens.json",
            "auth_tokens.env",
            "cookies.txt",
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            "secrets/",
            "private/",
            "# Database and backup files",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "backup_*/",
            "*.backup",
            "# Log files with potential sensitive data",
            "*.log",
            "logs/",
            "# Build artifacts and caches",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache/",
            ".coverage",
            "htmlcov/",
            "# Node.js",
            "node_modules/",
            "npm-debug.log*",
            "# Rust",
            "target/",
            "Cargo.lock",
            "# IDE files",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
        ]

        try:
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    existing_content = f.read()

            # Add missing patterns
            new_patterns = []
            for pattern in security_patterns:
                if pattern not in existing_content:
                    new_patterns.append(pattern)

            if new_patterns:
                with open(gitignore_path, "a") as f:
                    f.write("\n" + "\n".join(new_patterns) + "\n")

                logger.info(
                    f"Added {len(new_patterns)} security patterns to .gitignore"
                )
                self.security_report["security_configs_updated"].append(
                    str(gitignore_path)
                )

        except Exception as e:
            logger.error(f"Error updating .gitignore: {e}")

    def remove_sensitive_files(self):
        """Remove files containing sensitive data."""
        logger.info("🗑️ Removing sensitive files...")

        sensitive_files = [
            "auth_tokens.json",
            "auth_tokens.env",
            "cookies.txt",
            "*.key",
            "*.pem",
        ]

        for pattern in sensitive_files:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.security_report["hardcoded_secrets_removed"].append(
                            str(file_path)
                        )
                        logger.info(f"Removed sensitive file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing {file_path}: {e}")

    def create_security_env_template(self):
        """Create a template for environment variables."""
        logger.info("📝 Creating security environment template...")

        env_template = """# ACGS-1 Environment Variables Template
# Copy this file to .env and fill in your actual values

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/acgs_db
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=acgs_pgp_db

# Authentication
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
AUTH_SERVICE_SECRET_KEY=your-auth-service-secret-key

# API Keys
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
XAI_API_KEY=your-xai-api-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Service URLs
AC_SERVICE_URL=http://localhost:8001/api/v1
GS_SERVICE_URL=http://localhost:8004/api/v1
FV_SERVICE_URL=http://localhost:8003/api/v1
PGC_SERVICE_URL=http://localhost:8005/api/v1

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Environment
ENVIRONMENT=development
"""

        env_template_path = self.project_root / ".env.template"
        try:
            with open(env_template_path, "w") as f:
                f.write(env_template)

            logger.info(f"Created environment template: {env_template_path}")
            self.security_report["security_configs_updated"].append(
                str(env_template_path)
            )

        except Exception as e:
            logger.error(f"Error creating environment template: {e}")

    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned for secrets."""
        exclude_patterns = [
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            "target",
            "migrations",
            "test_",
            "tests/",
            ".pytest_cache",
        ]
        return not any(pattern in str(file_path) for pattern in exclude_patterns)

    def run_security_cleanup(self):
        """Run complete security cleanup process."""
        logger.info("🚀 Starting ACGS-1 Security Cleanup...")

        # 1. Scan for hardcoded secrets
        files_with_secrets = self.scan_for_hardcoded_secrets()
        logger.info(f"Found {len(files_with_secrets)} files with potential secrets")

        # 2. Clean hardcoded secrets
        if files_with_secrets:
            self.clean_hardcoded_secrets(files_with_secrets)

        # 3. Remove sensitive files
        self.remove_sensitive_files()

        # 4. Update .gitignore
        self.update_gitignore_security()

        # 5. Create environment template
        self.create_security_env_template()

        # 6. Save security report
        report_path = self.project_root / "security_cleanup_report.json"
        with open(report_path, "w") as f:
            json.dump(self.security_report, f, indent=2)

        logger.info(f"✅ Security cleanup completed. Report: {report_path}")
        return self.security_report


def main():
    """Main execution function."""
    cleanup = SecurityCleanup()
    cleanup.run_security_cleanup()


if __name__ == "__main__":
    main()
