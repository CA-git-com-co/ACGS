#!/usr/bin/env python3
"""
Applications Directory Restructuring Script

This script performs a comprehensive restructuring of the ACGS-1 applications directory:
1. Migrates content from legacy-frontend to governance-dashboard
2. Creates standard application directories
3. Fixes import statements in Python files
4. Updates references in configuration files
5. Organizes components, services, and utilities
6. Removes outdated files
7. Validates the restructured applications
"""

import os
import re
import sys
import shutil
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("applications_restructure.log")
    ]
)
logger = logging.getLogger(__name__)

class ApplicationsRestructurer:
    """Handles restructuring of the ACGS-1 applications directory"""
    
    def __init__(self, base_path: str = "/home/dislove/ACGS-1"):
        self.base_path = Path(base_path)
        self.applications_dir = self.base_path / "applications"
        self.legacy_frontend_dir = self.applications_dir / "legacy-frontend"
        self.governance_dashboard_dir = self.applications_dir / "governance-dashboard"
        
        # Standard application directories to create
        self.standard_dirs = [
            "governance-dashboard",
            "constitutional-council",
            "public-consultation",
            "admin-panel"
        ]
        
        # Component organization structure
        self.component_structure = {
            "components": ["common", "layout", "forms", "modals", "widgets"],
            "services": ["api", "auth", "blockchain", "data"],
            "utils": ["helpers", "formatters", "validators"],
            "hooks": [],
            "contexts": [],
            "pages": [],
            "assets": ["images", "styles", "fonts"],
            "tests": ["unit", "integration", "e2e"]
        }
        
        # Import mappings for fixing imports
        self.import_mappings = {
            "src.frontend": "applications.governance_dashboard",
            "src.backend.shared": "services.shared",
            "src.backend.ac_service": "services.core.constitutional_ai",
            "src.backend.gs_service": "services.core.governance_synthesis",
            "src.backend.pgc_service": "services.core.policy_governance",
            "shared.": "services.shared.",
            "quantumagi_core.frontend": "applications.governance_dashboard"
        }
        
        # Files to be cleaned up
        self.cleanup_patterns = [
            "*.bak", "*.tmp", "*_old.*", "*.log", "*.pyc",
            "__pycache__", ".DS_Store", "Thumbs.db"
        ]
        
        # Stats for reporting
        self.stats = {
            "files_migrated": 0,
            "imports_fixed": 0,
            "configs_updated": 0,
            "components_organized": 0,
            "files_cleaned": 0
        }
    
    def run(self) -> bool:
        """Execute the complete restructuring process"""
        logger.info("🚀 Starting applications directory restructuring...")
        
        try:
            # Create backup
            self.create_backup()
            
            # Create standard directories
            self.create_standard_directories()
            
            # Migrate legacy frontend
            if self.legacy_frontend_dir.exists():
                self.migrate_legacy_frontend()
            
            # Organize components within each application
            for app_dir in self.standard_dirs:
                app_path = self.applications_dir / app_dir
                if app_path.exists():
                    self.organize_application_structure(app_path)
            
            # Fix imports in Python files
            self.fix_import_statements()
            
            # Update configuration files
            self.update_configuration_files()
            
            # Clean up outdated files
            self.cleanup_outdated_files()
            
            # Validate restructuring
            validation_result = self.validate_restructuring()
            
            # Print summary
            self.print_summary()
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Restructuring failed: {e}", exc_info=True)
            return False
    
    def create_backup(self) -> None:
        """Create a backup of the applications directory"""
        backup_dir = self.base_path / "applications_backup"
        
        if backup_dir.exists():
            logger.info(f"Removing existing backup directory: {backup_dir}")
            shutil.rmtree(backup_dir)
        
        logger.info(f"Creating backup of applications directory to {backup_dir}")
        shutil.copytree(self.applications_dir, backup_dir)
    
    def create_standard_directories(self) -> None:
        """Create the standard application directories"""
        logger.info("Creating standard application directories...")
        
        for app_dir in self.standard_dirs:
            dir_path = self.applications_dir / app_dir
            if not dir_path.exists():
                logger.info(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def migrate_legacy_frontend(self) -> None:
        """Migrate content from legacy-frontend to governance-dashboard"""
        logger.info("Migrating content from legacy-frontend to governance-dashboard...")
        
        if not self.governance_dashboard_dir.exists():
            logger.info("Creating governance-dashboard directory")
            self.governance_dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files from legacy-frontend to governance-dashboard
        for item in self.legacy_frontend_dir.glob("*"):
            target_path = self.governance_dashboard_dir / item.name
            
            # Skip if the target already exists
            if target_path.exists():
                logger.info(f"Skipping existing item: {target_path}")
                continue
            
            if item.is_dir():
                logger.info(f"Copying directory: {item} -> {target_path}")
                shutil.copytree(item, target_path)
            else:
                logger.info(f"Copying file: {item} -> {target_path}")
                shutil.copy2(item, target_path)
            
            self.stats["files_migrated"] += 1
        
        # Remove legacy-frontend directory after migration
        logger.info("Removing legacy-frontend directory")
        shutil.rmtree(self.legacy_frontend_dir)
    
    def organize_application_structure(self, app_dir: Path) -> None:
        """Organize components, services, and utilities within an application"""
        logger.info(f"Organizing structure for application: {app_dir.name}")
        
        # Create component structure directories
        for category, subcategories in self.component_structure.items():
            category_dir = app_dir / category
            if not category_dir.exists():
                category_dir.mkdir(parents=True, exist_ok=True)
            
            for subcategory in subcategories:
                subcategory_dir = category_dir / subcategory
                if not subcategory_dir.exists():
                    subcategory_dir.mkdir(parents=True, exist_ok=True)
        
        # Move files to appropriate directories
        self._organize_files_by_type(app_dir)
        
        logger.info(f"Completed organizing structure for {app_dir.name}")
    
    def _organize_files_by_type(self, app_dir: Path) -> None:
        """Move files to appropriate directories based on their type and content"""
        # Map of file patterns to target directories
        file_patterns = {
            r".*Component\.(?:jsx?|tsx?)$": "components/common",
            r".*Layout\.(?:jsx?|tsx?)$": "components/layout",
            r".*Form\.(?:jsx?|tsx?)$": "components/forms",
            r".*Modal\.(?:jsx?|tsx?)$": "components/modals",
            r".*Widget\.(?:jsx?|tsx?)$": "components/widgets",
            r".*Service\.(?:jsx?|tsx?|js|ts)$": "services/api",
            r".*Auth.*\.(?:jsx?|tsx?|js|ts)$": "services/auth",
            r".*Blockchain.*\.(?:jsx?|tsx?|js|ts)$": "services/blockchain",
            r".*Helper\.(?:jsx?|tsx?|js|ts)$": "utils/helpers",
            r".*Formatter\.(?:jsx?|tsx?|js|ts)$": "utils/formatters",
            r".*Validator\.(?:jsx?|tsx?|js|ts)$": "utils/validators",
            r".*Hook\.(?:jsx?|tsx?|js|ts)$": "hooks",
            r".*Context\.(?:jsx?|tsx?|js|ts)$": "contexts",
            r".*Page\.(?:jsx?|tsx?)$": "pages",
            r".*\.(?:png|jpg|jpeg|gif|svg)$": "assets/images",
            r".*\.(?:css|scss|less)$": "assets/styles",
            r".*\.(?:woff|woff2|eot|ttf|otf)$": "assets/fonts",
            r".*\.test\.(?:jsx?|tsx?|js|ts)$": "tests/unit",
            r".*\.spec\.(?:jsx?|tsx?|js|ts)$": "tests/unit",
            r".*\.e2e\.(?:jsx?|tsx?|js|ts)$": "tests/e2e",
        }
        
        # Find files in the src directory or root of the app
        src_dir = app_dir / "src"
        search_dirs = [src_dir] if src_dir.exists() else [app_dir]
        
        for search_dir in search_dirs:
            for file_path in search_dir.glob("**/*"):
                if file_path.is_file() and not self._is_excluded_path(file_path):
                    for pattern, target_dir in file_patterns.items():
                        if re.match(pattern, file_path.name):
                            target_path = app_dir / target_dir / file_path.name
                            
                            # Create parent directory if it doesn't exist
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Skip if the file is already in the correct location
                            if file_path.parent == target_path.parent:
                                continue
                            
                            # Move the file
                            try:
                                logger.info(f"Moving {file_path} -> {target_path}")
                                shutil.move(file_path, target_path)
                                self.stats["components_organized"] += 1
                            except Exception as e:
                                logger.warning(f"Failed to move {file_path}: {e}")
                            
                            break
    
    def fix_import_statements(self) -> None:
        """Fix import statements in Python files to match the new project structure"""
        logger.info("Fixing import statements in Python files...")
        
        python_files = list(self.applications_dir.glob("**/*.py"))
        
        for py_file in python_files:
            if self._is_excluded_path(py_file):
                continue
            
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # Update import statements
                for old_import, new_import in self.import_mappings.items():
                    # Handle different import patterns
                    patterns = [
                        f"from {old_import}",
                        f"import {old_import}",
                        f"from {old_import}.",
                        f"import {old_import}.",
                    ]
                    
                    for pattern in patterns:
                        if pattern in content:
                            new_pattern = pattern.replace(old_import, new_import)
                            content = content.replace(pattern, new_pattern)
                
                # Write back if changed
                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    logger.info(f"Fixed imports in {py_file.relative_to(self.base_path)}")
                    self.stats["imports_fixed"] += 1
            
            except Exception as e:
                logger.warning(f"Failed to fix imports in {py_file}: {e}")
    
    def update_configuration_files(self) -> None:
        """Update references to old paths in configuration files"""
        logger.info("Updating configuration files...")
        
        # Update package.json files
        package_json_files = list(self.applications_dir.glob("**/package.json"))
        
        for package_file in package_json_files:
            try:
                with open(package_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                modified = False
                
                # Update dependencies paths if they reference old structure
                if "dependencies" in data:
                    for dep_name, dep_value in data["dependencies"].items():
                        if "file:src/frontend" in dep_value:
                            data["dependencies"][dep_name] = dep_value.replace(
                                "file:src/frontend", "file:applications/governance-dashboard"
                            )
                            modified = True
                
                # Update scripts if they reference old paths
                if "scripts" in data:
                    for script_name, script_value in data["scripts"].items():
                        if "src/frontend" in script_value:
                            data["scripts"][script_name] = script_value.replace(
                                "src/frontend", "applications/governance-dashboard"
                            )
                            modified = True
                
                if modified:
                    with open(package_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    
                    logger.info(f"Updated {package_file.relative_to(self.base_path)}")
                    self.stats["configs_updated"] += 1
            
            except Exception as e:
                logger.warning(f"Failed to update {package_file}: {e}")
        
        # Update other configuration files (tsconfig.json, .env, etc.)
        config_files = list(self.applications_dir.glob("**/*.json"))
        config_files.extend(list(self.applications_dir.glob("**/*.env*")))
        config_files.extend(list(self.applications_dir.glob("**/tsconfig.json")))
        config_files.extend(list(self.applications_dir.glob("**/webpack.config.js")))
        
        path_mappings = {
            "src/frontend": "applications/governance-dashboard",
            "src/backend/shared": "services/shared",
            "src/backend/ac_service": "services/core/constitutional-ai/ac_service",
            "src/backend/gs_service": "services/core/governance-synthesis/gs_service",
            "src/backend/pgc_service": "services/core/policy-governance/pgc_service",
            "../src/frontend": "../applications/governance-dashboard",
            "../../src/frontend": "../../applications/governance-dashboard",
        }
        
        for config_file in config_files:
            if self._is_excluded_path(config_file) or config_file in package_json_files:
                continue
            
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # Update path references
                for old_path, new_path in path_mappings.items():
                    content = content.replace(old_path, new_path)
                
                # Write back if changed
                if content != original_content:
                    with open(config_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    logger.info(f"Updated {config_file.relative_to(self.base_path)}")
                    self.stats["configs_updated"] += 1
            
            except Exception as e:
                logger.warning(f"Failed to update {config_file}: {e}")
    
    def cleanup_outdated_files(self) -> None:
        """Remove outdated files, backups, and temporary files"""
        logger.info("Cleaning up outdated files...")
        
        for pattern in self.cleanup_patterns:
            for file_path in self.applications_dir.glob(f"**/{pattern}"):
                try:
                    if file_path.is_dir():
                        logger.info(f"Removing directory: {file_path}")
                        shutil.rmtree(file_path)
                    else:
                        logger.info(f"Removing file: {file_path}")
                        file_path.unlink()
                    
                    self.stats["files_cleaned"] += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")
    
    def validate_restructuring(self) -> bool:
        """Validate the restructured applications to ensure they maintain functionality"""
        logger.info("Validating restructured applications...")
        
        validation_results = []
        
        # Check that all standard directories exist
        for app_dir in self.standard_dirs:
            dir_path = self.applications_dir / app_dir
            validation_results.append((dir_path.exists(), f"Directory exists: {app_dir}"))
        
        # Check that legacy-frontend has been removed
        validation_results.append(
            (not self.legacy_frontend_dir.exists(), "Legacy frontend directory removed")
        )
        
        # Validate governance-dashboard structure
        if self.governance_dashboard_dir.exists():
            # Check for essential files
            package_json = self.governance_dashboard_dir / "package.json"
            validation_results.append(
                (package_json.exists(), "Governance dashboard package.json exists")
            )
            
            # Try to run npm install to verify dependencies
            if package_json.exists():
                try:
                    logger.info("Testing npm install in governance-dashboard...")
                    result = subprocess.run(
                        ["npm", "install", "--dry-run"],
                        cwd=self.governance_dashboard_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    validation_results.append(
                        (result.returncode == 0, "npm install test successful")
                    )
                    if result.returncode != 0:
                        logger.warning(f"npm install test failed: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Failed to test npm install: {e}")
                    validation_results.append((False, "npm install test failed"))
        
        # Check for any remaining old import patterns
        old_import_patterns = [
            "from services.core.frontend", 
            "import src.frontend",
            "from services.core.backend",
            "import src.backend"
        ]
        
        has_old_imports = False
        for py_file in self.applications_dir.glob("**/*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if any(pattern in content for pattern in old_import_patterns):
                    has_old_imports = True
                    logger.warning(f"Found old import patterns in {py_file}")
            except Exception:
                pass
        
        validation_results.append((not has_old_imports, "No old import patterns found"))
        
        # Print validation results
        logger.info("Validation results:")
        for result, message in validation_results:
            status = "✅" if result else "❌"
            logger.info(f"{status} {message}")
        
        # Overall validation result
        is_valid = all(result for result, _ in validation_results)
        if is_valid:
            logger.info("✅ Validation successful! All checks passed.")
        else:
            logger.warning("⚠️ Validation failed. Some checks did not pass.")
        
        return is_valid
    
    def print_summary(self) -> None:
        """Print a summary of the restructuring operations"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 Applications Restructuring Summary")
        logger.info("=" * 50)
        logger.info(f"Files migrated from legacy-frontend: {self.stats['files_migrated']}")
        logger.info(f"Import statements fixed: {self.stats['imports_fixed']}")
        logger.info(f"Configuration files updated: