#!/usr/bin/env python3
"""
ACGS-PGP Applications Directory Restructuring Script
Organizes frontend applications following ACGS-PGP framework best practices
"""

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ApplicationsRestructurer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.applications_dir = self.project_root / "applications"
        self.dry_run = False
        
        # Track operations for summary
        self.operations = {
            "files_moved": [],
            "directories_created": [],
            "files_updated": [],
            "errors": [],
            "validations": []
        }
        
        # Expected structure after reorganization
        self.target_structure = {
            "governance-dashboard": {
                "description": "Primary governance interface",
                "type": "react-frontend",
                "services": ["AC", "GS", "PGC"]
            },
            "legacy-frontend": {
                "description": "Legacy frontend interface",
                "type": "react-frontend", 
                "services": ["AC", "GS", "PGC", "FV"]
            },
            "shared": {
                "description": "Shared components and utilities",
                "type": "shared-library",
                "services": ["common"]
            }
        }

    def set_dry_run(self, dry_run: bool = True):
        """Enable/disable dry run mode"""
        self.dry_run = dry_run
        if dry_run:
            logger.info("🔍 DRY RUN MODE: No actual changes will be made")

    def _safe_move(self, src: Path, dst: Path) -> bool:
        """Safely move files/directories with error handling"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would move: {src} -> {dst}")
                return True
                
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                shutil.move(str(src), str(dst))
                self.operations["files_moved"].append(f"{src} -> {dst}")
                return True
            return False
        except Exception as e:
            error_msg = f"Failed to move {src} to {dst}: {e}"
            logger.error(error_msg)
            self.operations["errors"].append(error_msg)
            return False

    def _safe_copy(self, src: Path, dst: Path) -> bool:
        """Safely copy files with error handling"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would copy: {src} -> {dst}")
                return True
                
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst, dirs_exist_ok=True)
            return True
        except Exception as e:
            error_msg = f"Failed to copy {src} to {dst}: {e}"
            logger.error(error_msg)
            self.operations["errors"].append(error_msg)
            return False

    def analyze_current_structure(self) -> Dict:
        """Analyze the current applications directory structure"""
        logger.info("📊 Analyzing current applications structure...")
        
        if not self.applications_dir.exists():
            logger.warning(f"Applications directory not found: {self.applications_dir}")
            return {}
            
        structure = {}
        for item in self.applications_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure[item.name] = {
                    "path": str(item),
                    "type": self._detect_app_type(item),
                    "files": list(item.glob("**/*")),
                    "size": sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                }
        
        logger.info(f"Found {len(structure)} application directories")
        return structure

    def _detect_app_type(self, app_dir: Path) -> str:
        """Detect the type of application based on files present"""
        if (app_dir / "package.json").exists():
            return "react-frontend"
        elif (app_dir / "Cargo.toml").exists():
            return "rust-service"
        elif (app_dir / "requirements.txt").exists():
            return "python-service"
        else:
            return "unknown"

    def consolidate_shared_components(self):
        """Consolidate shared components into applications/shared/"""
        logger.info("🔧 Consolidating shared components...")
        
        shared_dir = self.applications_dir / "shared"
        if not self.dry_run:
            shared_dir.mkdir(exist_ok=True)
            self.operations["directories_created"].append(str(shared_dir))
        
        # Move shared components from root applications directory
        shared_items = [
            "components", "hooks", "types", "utils", 
            "styles", "assets", "lib", "constants"
        ]
        
        for item_name in shared_items:
            src_path = self.applications_dir / item_name
            if src_path.exists():
                dst_path = shared_dir / item_name
                if self._safe_move(src_path, dst_path):
                    logger.info(f"✅ Moved shared {item_name} to shared directory")

    def organize_frontend_applications(self):
        """Organize frontend applications according to ACGS-PGP standards"""
        logger.info("🎯 Organizing frontend applications...")
        
        # Ensure governance-dashboard structure
        self._organize_governance_dashboard()
        
        # Ensure legacy-frontend structure  
        self._organize_legacy_frontend()
        
        # Clean up root-level files
        self._cleanup_root_level_files()

    def _organize_governance_dashboard(self):
        """Organize governance-dashboard application"""
        logger.info("📱 Organizing governance-dashboard...")
        
        dashboard_dir = self.applications_dir / "governance-dashboard"
        if not dashboard_dir.exists():
            logger.warning("governance-dashboard directory not found")
            return
            
        # Ensure proper structure
        required_dirs = ["src", "public", "src/components", "src/services", "src/pages"]
        for dir_name in required_dirs:
            dir_path = dashboard_dir / dir_name
            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.operations["directories_created"].append(str(dir_path))

    def _organize_legacy_frontend(self):
        """Organize legacy-frontend application"""
        logger.info("📱 Organizing legacy-frontend...")
        
        legacy_dir = self.applications_dir / "legacy-frontend"
        if not legacy_dir.exists():
            logger.warning("legacy-frontend directory not found")
            return
            
        # Ensure proper structure
        required_dirs = ["src", "public", "src/components", "src/services", "src/pages"]
        for dir_name in required_dirs:
            dir_path = legacy_dir / dir_name
            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.operations["directories_created"].append(str(dir_path))

    def _cleanup_root_level_files(self):
        """Clean up root-level configuration files"""
        logger.info("🧹 Cleaning up root-level files...")
        
        # Files that should remain at root level
        root_files = [
            "package.json", "package-lock.json", "tsconfig.json", 
            "next.config.js", "tailwind.config.ts", "postcss.config.js",
            "next-env.d.ts", "README.md"
        ]
        
        for file_name in root_files:
            file_path = self.applications_dir / file_name
            if file_path.exists():
                logger.info(f"✅ Root file preserved: {file_name}")

    def update_import_paths(self):
        """Update import paths to reflect new structure"""
        logger.info("🔄 Updating import paths...")
        
        # Update imports in TypeScript/JavaScript files
        for app_dir in ["governance-dashboard", "legacy-frontend"]:
            app_path = self.applications_dir / app_dir
            if app_path.exists():
                self._update_imports_in_directory(app_path)

    def _update_imports_in_directory(self, directory: Path):
        """Update imports in all TypeScript/JavaScript files in directory"""
        for file_path in directory.rglob("*.{ts,tsx,js,jsx}"):
            if file_path.is_file():
                try:
                    if not self.dry_run:
                        content = file_path.read_text(encoding='utf-8')
                        updated_content = self._update_import_statements(content)
                        if content != updated_content:
                            file_path.write_text(updated_content, encoding='utf-8')
                            self.operations["files_updated"].append(str(file_path))
                except Exception as e:
                    error_msg = f"Failed to update imports in {file_path}: {e}"
                    self.operations["errors"].append(error_msg)

    def _update_import_statements(self, content: str) -> str:
        """Update import statements to use new paths"""
        # Update relative imports to shared components
        import_mappings = {
            "from '../components/": "from '../shared/components/",
            "from '../../components/": "from '../shared/components/",
            "from '../hooks/": "from '../shared/hooks/",
            "from '../../hooks/": "from '../shared/hooks/",
            "from '../types/": "from '../shared/types/",
            "from '../../types/": "from '../shared/types/",
        }
        
        for old_import, new_import in import_mappings.items():
            content = content.replace(old_import, new_import)
            
        return content

    def validate_structure(self) -> bool:
        """Validate the restructured applications directory"""
        logger.info("✅ Validating restructured applications...")
        
        validation_results = []
        
        # Check required directories exist
        required_dirs = [
            "governance-dashboard",
            "legacy-frontend", 
            "shared"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.applications_dir / dir_name
            if dir_path.exists():
                validation_results.append(f"✅ {dir_name} directory exists")
                self.operations["validations"].append(f"PASS: {dir_name} directory exists")
            else:
                validation_results.append(f"❌ {dir_name} directory missing")
                self.operations["validations"].append(f"FAIL: {dir_name} directory missing")
        
        # Check package.json files
        for app in ["governance-dashboard", "legacy-frontend"]:
            package_json = self.applications_dir / app / "package.json"
            if package_json.exists():
                validation_results.append(f"✅ {app}/package.json exists")
                self.operations["validations"].append(f"PASS: {app}/package.json exists")
            else:
                validation_results.append(f"❌ {app}/package.json missing")
                self.operations["validations"].append(f"FAIL: {app}/package.json missing")
        
        # Log validation results
        for result in validation_results:
            logger.info(result)
            
        # Return overall success
        failed_validations = [v for v in validation_results if v.startswith("❌")]
        return len(failed_validations) == 0

    def print_summary(self):
        """Print comprehensive summary of restructuring operations"""
        logger.info("\n" + "="*80)
        logger.info("📋 ACGS-PGP APPLICATIONS RESTRUCTURING SUMMARY")
        logger.info("="*80)
        
        # Operation counts
        logger.info(f"📁 Directories Created: {len(self.operations['directories_created'])}")
        logger.info(f"📦 Files Moved: {len(self.operations['files_moved'])}")
        logger.info(f"📝 Files Updated: {len(self.operations['files_updated'])}")
        logger.info(f"❌ Errors Encountered: {len(self.operations['errors'])}")
        logger.info(f"✅ Validations: {len([v for v in self.operations['validations'] if 'PASS' in v])}")
        logger.info(f"❌ Failed Validations: {len([v for v in self.operations['validations'] if 'FAIL' in v])}")
        
        # Detailed breakdown
        if self.operations['directories_created']:
            logger.info("\n📁 DIRECTORIES CREATED:")
            for directory in self.operations['directories_created']:
                logger.info(f"  • {directory}")
        
        if self.operations['files_moved']:
            logger.info("\n📦 FILES MOVED:")
            for move_op in self.operations['files_moved'][:10]:  # Show first 10
                logger.info(f"  • {move_op}")
            if len(self.operations['files_moved']) > 10:
                logger.info(f"  ... and {len(self.operations['files_moved']) - 10} more")
        
        if self.operations['files_updated']:
            logger.info("\n📝 FILES UPDATED:")
            for file_path in self.operations['files_updated'][:10]:  # Show first 10
                logger.info(f"  • {file_path}")
            if len(self.operations['files_updated']) > 10:
                logger.info(f"  ... and {len(self.operations['files_updated']) - 10} more")
        
        if self.operations['errors']:
            logger.info("\n❌ ERRORS ENCOUNTERED:")
            for error in self.operations['errors']:
                logger.error(f"  • {error}")
        
        # Validation results
        logger.info("\n✅ VALIDATION RESULTS:")
        for validation in self.operations['validations']:
            status = "✅" if "PASS" in validation else "❌"
            logger.info(f"  {status} {validation}")
        
        # Final status
        total_errors = len(self.operations['errors'])
        failed_validations = len([v for v in self.operations['validations'] if 'FAIL' in v])
        
        if total_errors == 0 and failed_validations == 0:
            logger.info("\n🎉 RESTRUCTURING COMPLETED SUCCESSFULLY!")
            logger.info("✅ All operations completed without errors")
            logger.info("✅ All validations passed")
        elif total_errors == 0 and failed_validations > 0:
            logger.info("\n⚠️  RESTRUCTURING COMPLETED WITH VALIDATION ISSUES")
            logger.info(f"✅ No errors during operations")
            logger.info(f"❌ {failed_validations} validation(s) failed")
        else:
            logger.info("\n❌ RESTRUCTURING COMPLETED WITH ERRORS")
            logger.info(f"❌ {total_errors} error(s) encountered")
            logger.info(f"❌ {failed_validations} validation(s) failed")
        
        logger.info("="*80)

    def run_restructuring(self, dry_run: bool = False) -> bool:
        """Execute the complete restructuring process"""
        self.set_dry_run(dry_run)
        
        logger.info("🚀 Starting ACGS-PGP Applications Restructuring...")
        start_time = time.time()
        
        try:
            # Phase 1: Analysis
            current_structure = self.analyze_current_structure()
            
            # Phase 2: Restructuring
            self.consolidate_shared_components()
            self.organize_frontend_applications()
            
            # Phase 3: Updates
            self.update_import_paths()
            
            # Phase 4: Validation
            validation_success = self.validate_structure()
            
            # Phase 5: Summary
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"\n⏱️  Total execution time: {duration:.2f} seconds")
            self.print_summary()
            
            return validation_success and len(self.operations['errors']) == 0
            
        except Exception as e:
            logger.error(f"💥 Restructuring failed with exception: {e}")
            self.operations['errors'].append(f"Critical failure: {e}")
            self.print_summary()
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-PGP Applications Restructuring")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    restructurer = ApplicationsRestructurer(args.project_root)
    success = restructurer.run_restructuring(dry_run=args.dry_run)
    
    exit(0 if success else 1)
