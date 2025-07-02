#!/usr/bin/env python3
"""
Reorganization Validation Script
Validates the new directory structure and import paths
"""

import ast
import os
import subprocess
import sys
from pathlib import Path


class ReorganizationValidator:
    """Validates the reorganized codebase structure"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_directory_structure(self) -> bool:
        """Validate expected directory structure exists"""
        expected_dirs = [
            "blockchain/programs",
            "blockchain/client",
            "blockchain/tests",
            "blockchain/scripts",
            "services/core/constitutional-ai",
            "services/core/governance-synthesis",
            "services/core/policy-governance",
            "services/core/formal-verification",
            "services/platform/authentication",
            "services/platform/integrity",
            "services/platform/workflow",
            "services/research/federated-evaluation",
            "services/research/research-platform",
            "services/shared/models",
            "services/shared/database",
            "services/shared/auth",
            "services/shared/config",
            "applications/governance-dashboard",
            "applications/constitutional-council",
            "integrations/quantumagi-bridge",
            "integrations/alphaevolve-engine",
            "infrastructure/docker",
            "infrastructure/kubernetes",
            "tools/cli",
            "docs/architecture",
            "docs/api",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "config/environments",
        ]

        missing_dirs = []
        for dir_path in expected_dirs:
            full_path = self.root_path / dir_path
            if not full_path.exists():
                missing_dirs.append(str(dir_path))
                self.errors.append(f"Missing directory: {dir_path}")
            else:
                print(f"✅ {dir_path}")

        if missing_dirs:
            print(f"❌ Missing {len(missing_dirs)} directories")
            return False

        print("✅ All expected directories exist")
        return True

    def validate_import_paths(self) -> bool:
        """Validate that all import paths are correct after reorganization"""
        print("🔍 Validating import paths...")

        python_files = list(self.root_path.rglob("*.py"))
        problematic_imports = []

        for py_file in python_files:
            if self._is_excluded_path(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find imports
                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                # Check for problematic patterns
                for import_stmt in imports:
                    if self._is_problematic_import(import_stmt):
                        problematic_imports.append(
                            {
                                "file": str(py_file.relative_to(self.root_path)),
                                "import": import_stmt,
                            }
                        )

            except Exception as e:
                self.warnings.append(f"Could not parse {py_file}: {e}")

        if problematic_imports:
            print(f"❌ Found {len(problematic_imports)} problematic imports")
            for item in problematic_imports[:10]:  # Show first 10
                print(f"  {item['file']}: {item['import']}")
            return False

        print("✅ All import paths are valid")
        return True

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def _is_problematic_import(self, import_stmt: str) -> bool:
        """Check if import statement indicates reorganization issues"""
        problematic_patterns = [
            "src.backend",  # Old backend path
            "quantumagi_core.gs_engine",  # Old GS engine path
            # "sys.path.append",  # Path manipulation  # Removed during reorganization
            "../",  # Relative imports
        ]

        return any(pattern in import_stmt for pattern in problematic_patterns)

    def _is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded from validation"""
        excluded_patterns = [
            "venv/",
            "node_modules/",
            "__pycache__/",
            ".git/",
            "target/",
            ".pytest_cache/",
        ]

        path_str = str(path)
        return any(pattern in path_str for pattern in excluded_patterns)

    def validate_build_processes(self) -> bool:
        """Validate that build processes work with new structure"""
        print("🔨 Validating build processes...")

        build_validations = [
            self._validate_anchor_build,
            self._validate_python_services,
            self._validate_frontend_build,
            self._validate_docker_builds,
        ]

        all_passed = True
        for validation in build_validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"Build validation failed: {e}")
                all_passed = False

        return all_passed

    def _validate_anchor_build(self) -> bool:
        """Validate Anchor build process"""
        blockchain_dir = self.root_path / "blockchain"
        if not blockchain_dir.exists():
            self.errors.append("Blockchain directory not found")
            return False

        try:
            result = subprocess.run(
                ["anchor", "build"],
                check=False,
                cwd=blockchain_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ Anchor build successful")
                return True
            self.errors.append(f"Anchor build failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.errors.append("Anchor build timed out")
            return False
        except FileNotFoundError:
            self.warnings.append("Anchor CLI not found, skipping build validation")
            return True

    def _validate_python_services(self) -> bool:
        """Validate Python service imports and syntax"""
        services_dir = self.root_path / "services"
        if not services_dir.exists():
            self.errors.append("Services directory not found")
            return False

        python_files = list(services_dir.rglob("*.py"))
        syntax_errors = []

        for py_file in python_files:
            if self._is_excluded_path(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")

        if syntax_errors:
            print(f"❌ Found {len(syntax_errors)} Python syntax errors")
            for error in syntax_errors[:5]:
                print(f"  {error}")
            return False

        print("✅ All Python services have valid syntax")
        return True

    def _validate_frontend_build(self) -> bool:
        """Validate frontend build process"""
        frontend_dir = self.root_path / "applications" / "governance-dashboard"
        if not frontend_dir.exists():
            self.warnings.append("Frontend directory not found")
            return True

        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            self.errors.append("Frontend package.json not found")
            return False

        print("✅ Frontend structure validated")
        return True

    def _validate_docker_builds(self) -> bool:
        """Validate Docker build configurations"""
        docker_dir = self.root_path / "infrastructure" / "docker"
        if not docker_dir.exists():
            self.warnings.append("Docker directory not found")
            return True

        dockerfiles = list(docker_dir.rglob("Dockerfile*"))
        if not dockerfiles:
            self.warnings.append("No Dockerfiles found")
            return True

        print(f"✅ Found {len(dockerfiles)} Docker configurations")
        return True

    def run_full_validation(self) -> bool:
        """Run complete validation suite"""
        print("🚀 Starting ACGS-1 Reorganization Validation")
        print("=" * 50)

        validations = [
            ("Directory Structure", self.validate_directory_structure),
            ("Import Paths", self.validate_import_paths),
            ("Build Processes", self.validate_build_processes),
        ]

        all_passed = True
        for name, validation_func in validations:
            print(f"\n📋 {name}")
            print("-" * 30)
            if not validation_func():
                all_passed = False

        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 All validations passed!")
        else:
            print("❌ Some validations failed")
            print(f"Errors: {len(self.errors)}")
            print(f"Warnings: {len(self.warnings)}")

        return all_passed


def main():
    """Main validation entry point"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()

    validator = ReorganizationValidator(root_path)
    success = validator.run_full_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
