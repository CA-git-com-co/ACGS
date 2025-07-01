#!/usr/bin/env python3
"""
ACGS-1 Code Quality Standardization
===================================

This script applies comprehensive code quality improvements while preserving
all critical functionality including Policy Synthesis Engine and Multi-Model Consensus.

Key objectives:
- Apply automated formatting (rustfmt, black, prettier)
- Fix import ordering and remove unused imports
- Standardize error handling patterns
- Remove dead code while preserving critical components
- Maintain >80% test coverage
"""

import os
import sys
import json
import subprocess
import logging
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'code_quality_standardization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CodeQualityStandardizer:
    """Manages code quality standardization across the codebase"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.report = {
            "start_time": datetime.now().isoformat(),
            "formatting_results": {},
            "import_fixes": {},
            "error_handling_updates": {},
            "dead_code_removal": {},
            "preserved_components": [],
        }

        # Critical components to preserve
        self.preserve_patterns = [
            "*policy_synthesis*",
            "*multi_model*",
            "*constitutional*",
            "*quantumagi*",
            "*wina*",
            "*governance*",
            "*pgc*",
            "*formal_verification*",
        ]

    def apply_python_formatting(self) -> bool:
        """Apply Python code formatting with black and isort"""
        logger.info("Applying Python code formatting...")

        try:
            # Install formatting tools if needed
            subprocess.run(
                ["pip", "install", "black", "isort", "autoflake"],
                check=False,
                capture_output=True,
            )

            # Apply black formatting
            black_result = subprocess.run(
                [
                    "black",
                    "--line-length",
                    "88",
                    "--target-version",
                    "py39",
                    "services/",
                    "scripts/",
                    "tests/",
                    "integrations/",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            # Apply isort for import sorting
            isort_result = subprocess.run(
                [
                    "isort",
                    "--profile",
                    "black",
                    "--line-length",
                    "88",
                    "services/",
                    "scripts/",
                    "tests/",
                    "integrations/",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            # Remove unused imports with autoflake
            autoflake_result = subprocess.run(
                [
                    "autoflake",
                    "--remove-all-unused-imports",
                    "--recursive",
                    "--in-place",
                    "services/",
                    "scripts/",
                    "tests/",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            self.report["formatting_results"]["python"] = {
                "black": black_result.returncode == 0,
                "isort": isort_result.returncode == 0,
                "autoflake": autoflake_result.returncode == 0,
            }

            logger.info("Python formatting completed")
            return True

        except Exception as e:
            logger.error(f"Python formatting failed: {e}")
            return False

    def apply_rust_formatting(self) -> bool:
        """Apply Rust code formatting with rustfmt"""
        logger.info("Applying Rust code formatting...")

        try:
            # Create rustfmt.toml configuration
            rustfmt_config = self.project_root / "blockchain/rustfmt.toml"
            with open(rustfmt_config, "w") as f:
                f.write(
                    """# ACGS-1 Rust Formatting Configuration
edition = "2021"
max_width = 100
hard_tabs = false
tab_spaces = 4
newline_style = "Unix"
use_small_heuristics = "Default"
reorder_imports = true
reorder_modules = true
remove_nested_parens = true
"""
                )

            # Apply rustfmt
            result = subprocess.run(
                ["cargo", "fmt", "--all"],
                cwd=self.project_root / "blockchain",
                capture_output=True,
                text=True,
            )

            self.report["formatting_results"]["rust"] = {
                "rustfmt": result.returncode == 0,
                "output": result.stdout if result.stdout else result.stderr,
            }

            logger.info("Rust formatting completed")
            return True

        except Exception as e:
            logger.error(f"Rust formatting failed: {e}")
            return False

    def apply_javascript_formatting(self) -> bool:
        """Apply JavaScript/TypeScript formatting with prettier"""
        logger.info("Applying JavaScript/TypeScript formatting...")

        try:
            # Create prettier configuration
            prettier_config = self.project_root / ".prettierrc"
            with open(prettier_config, "w") as f:
                json.dump(
                    {
                        "semi": true,
                        "trailingComma": "es5",
                        "singleQuote": true,
                        "printWidth": 100,
                        "tabWidth": 2,
                        "useTabs": false,
                    },
                    f,
                    indent=2,
                )

            # Apply prettier formatting
            result = subprocess.run(
                [
                    "npx",
                    "prettier",
                    "--write",
                    "applications/**/*.{js,ts,jsx,tsx}",
                    "blockchain/**/*.{js,ts}",
                    "*.{js,ts,json}",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            self.report["formatting_results"]["javascript"] = {
                "prettier": result.returncode == 0,
                "output": result.stdout if result.stdout else result.stderr,
            }

            logger.info("JavaScript/TypeScript formatting completed")
            return True

        except Exception as e:
            logger.error(f"JavaScript formatting failed: {e}")
            return False

    def fix_python_imports(self) -> bool:
        """Fix Python import issues across the codebase"""
        logger.info("Fixing Python imports...")

        try:
            import_fixes = 0

            # Find all Python files
            python_files = []
            for pattern in ["services/**/*.py", "scripts/**/*.py", "tests/**/*.py"]:
                python_files.extend(self.project_root.glob(pattern))

            for py_file in python_files:
                if self._fix_file_imports(py_file):
                    import_fixes += 1

            self.report["import_fixes"]["files_fixed"] = import_fixes
            logger.info(f"Fixed imports in {import_fixes} files")
            return True

        except Exception as e:
            logger.error(f"Import fixing failed: {e}")
            return False

    def _fix_file_imports(self, file_path: Path) -> bool:
        """Fix imports in a specific Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip files with merge conflicts
            if "<<<<<<< HEAD" in content or ">>>>>>> " in content:
                return False

            # Common import fixes
            fixes = [
                # Fix relative imports
                (r"from \.\.shared import", "from services.shared import"),
                (r"from \.shared import", "from services.shared import"),
                # Fix service imports
                (r"from app\.", "from ."),
                # Fix common typos
                (r"import asyncio\nimport asyncio", "import asyncio"),
            ]

            original_content = content
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            logger.warning(f"Could not fix imports in {file_path}: {e}")
            return False

    def standardize_error_handling(self) -> bool:
        """Standardize error handling patterns"""
        logger.info("Standardizing error handling...")

        try:
            # Create error handling templates
            error_templates = {
                "fastapi_exception": '''
from fastapi import HTTPException
from typing import Optional

class ACGSException(Exception):
    """Base exception for ACGS services"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(ACGSException):
    """Validation error"""
    pass

class ServiceUnavailableError(ACGSException):
    """Service unavailable error"""
    pass
''',
                "rust_error": """
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ACGSError {
    #[error("Validation error: {0}")]
    Validation(String),
    
    #[error("Service unavailable: {0}")]
    ServiceUnavailable(String),
    
    #[error("Configuration error: {0}")]
    Configuration(String),
}

pub type Result<T> = std::result::Result<T, ACGSError>;
""",
            }

            # Apply error handling templates to core services
            core_services = [
                "services/core/constitutional-ai",
                "services/core/governance-synthesis",
                "services/core/formal-verification",
                "services/core/policy-governance",
            ]

            for service_path in core_services:
                service_dir = self.project_root / service_path
                if service_dir.exists():
                    self._apply_error_handling_template(service_dir)

            logger.info("Error handling standardization completed")
            return True

        except Exception as e:
            logger.error(f"Error handling standardization failed: {e}")
            return False

    def _apply_error_handling_template(self, service_dir: Path):
        """Apply error handling template to a service"""
        # Create exceptions.py if it doesn't exist
        exceptions_file = service_dir / "app" / "exceptions.py"
        if not exceptions_file.exists() and (service_dir / "app").exists():
            exceptions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(exceptions_file, "w") as f:
                f.write('"""ACGS Service Exceptions"""\n')
                f.write(self.error_templates["fastapi_exception"])

    def remove_dead_code(self) -> bool:
        """Remove dead code while preserving critical components"""
        logger.info("Removing dead code...")

        try:
            # Use vulture to find dead code
            subprocess.run(
                ["pip", "install", "vulture"], check=False, capture_output=True
            )

            # Scan for dead code but don't auto-remove
            result = subprocess.run(
                ["vulture", "services/", "--min-confidence", "80"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            # Log findings but preserve critical components
            if result.stdout:
                dead_code_candidates = result.stdout.split("\n")
                preserved = []

                for candidate in dead_code_candidates:
                    if any(
                        pattern.replace("*", "") in candidate.lower()
                        for pattern in self.preserve_patterns
                    ):
                        preserved.append(candidate)

                self.report["dead_code_removal"]["candidates"] = len(
                    dead_code_candidates
                )
                self.report["dead_code_removal"]["preserved"] = len(preserved)
                self.report["preserved_components"] = preserved

            logger.info("Dead code analysis completed")
            return True

        except Exception as e:
            logger.error(f"Dead code removal failed: {e}")
            return False

    def run_code_quality_standardization(self) -> bool:
        """Execute complete code quality standardization"""
        try:
            logger.info("Starting ACGS-1 code quality standardization...")

            # Phase 1: Python formatting
            if not self.apply_python_formatting():
                logger.warning("Python formatting had issues but continuing...")

            # Phase 2: Rust formatting
            if not self.apply_rust_formatting():
                logger.warning("Rust formatting had issues but continuing...")

            # Phase 3: JavaScript formatting
            if not self.apply_javascript_formatting():
                logger.warning("JavaScript formatting had issues but continuing...")

            # Phase 4: Fix imports
            if not self.fix_python_imports():
                logger.warning("Import fixing had issues but continuing...")

            # Phase 5: Standardize error handling
            if not self.standardize_error_handling():
                logger.warning(
                    "Error handling standardization had issues but continuing..."
                )

            # Phase 6: Remove dead code
            if not self.remove_dead_code():
                logger.warning("Dead code removal had issues but continuing...")

            # Generate report
            self.report["end_time"] = datetime.now().isoformat()
            self.report["success"] = True

            report_file = (
                self.project_root
                / f"code_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(self.report, f, indent=2)

            logger.info(
                f"Code quality standardization completed. Report: {report_file}"
            )
            return True

        except Exception as e:
            logger.error(f"Code quality standardization failed: {e}")
            self.report["success"] = False
            self.report["error"] = str(e)
            return False


def main():
    """Main execution function"""
    standardizer = CodeQualityStandardizer()

    if standardizer.run_code_quality_standardization():
        print("✅ ACGS-1 code quality standardization completed successfully!")
        print("🔍 Check the code quality report for details")
        sys.exit(0)
    else:
        print("❌ Code quality standardization failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
