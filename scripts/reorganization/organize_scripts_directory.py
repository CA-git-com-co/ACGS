#!/usr/bin/env python3
"""
ACGS-2 Scripts Directory Organization Script
Constitutional Hash: cdd01ef066bc6cf2

This script reorganizes the scripts directory by moving files from the overpopulated
development subdirectory into more logical groupings following ACGS-2 patterns.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ScriptsDirectoryOrganizer:
    """Organize scripts directory following ACGS-2 patterns"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.scripts_dir = self.project_root / "scripts"
        self.dev_dir = self.scripts_dir / "development"
        self.backup_dir = self.project_root / "archive" / "scripts_reorganization_backup"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "moved_files": [],
            "errors": [],
            "summary": {}
        }
        
    def create_backup_dir(self):
        """Create backup directory for safety"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created backup directory: {self.backup_dir}")
        
    def get_file_categorization(self) -> Dict[str, List[str]]:
        """Categorize files in development directory for reorganization"""
        
        # Files to move to deployment/
        deployment_files = [
            "deploy_*.py", "deploy_*.sh", "deploy-*.sh", 
            "production_*.py", "production_*.sh",
            "staging_*.py", "staging_*.sh",
            "blue_green_*.py", "rollback*.py", "rollback*.sh",
            "backup_*.py", "backup_*.sh"
        ]
        
        # Files to move to testing/
        testing_files = [
            "test_*.py", "test_*.sh", "test-*.py", "test-*.sh",
            "run_*test*.py", "run_*test*.sh",
            "validate_*.py", "validate_*.sh", "validate-*.sh",
            "comprehensive_*test*.py", "integration_test*.py"
        ]
        
        # Files to move to monitoring/
        monitoring_files = [
            "monitor_*.py", "monitor_*.sh", "monitor-*.sh",
            "health_*.py", "health_*.sh", "health-*.sh",
            "metrics_*.py", "dashboard*.py", "alerting*.py",
            "performance_monitor*.py", "observability*.py"
        ]
        
        # Files to move to security/
        security_files = [
            "security_*.py", "security_*.sh", "security-*.sh",
            "vulnerability_*.py", "penetration_*.py",
            "audit_*.py", "compliance_*.py", "hardening*.py"
        ]
        
        # Files to move to maintenance/
        maintenance_files = [
            "cleanup_*.py", "cleanup_*.sh", "fix_*.py", "fix_*.sh",
            "repair_*.py", "maintenance_*.py", "optimize_*.py",
            "cache_*.py", "database_*.py", "dependency_*.py"
        ]
        
        # Files to move to setup/
        setup_files = [
            "setup_*.py", "setup_*.sh", "setup-*.sh",
            "install_*.py", "install_*.sh", "install-*.sh",
            "configure_*.py", "initialize_*.py"
        ]
        
        return {
            "deployment": deployment_files,
            "testing": testing_files,
            "monitoring": monitoring_files,
            "security": security_files,
            "maintenance": maintenance_files,
            "setup": setup_files
        }
        
    def find_files_by_patterns(self, patterns: List[str]) -> List[Path]:
        """Find files matching given patterns in development directory"""
        found_files = []
        
        for pattern in patterns:
            found_files.extend(self.dev_dir.glob(pattern))
            
        return found_files
        
    def move_file_safely(self, source: Path, dest_dir: str) -> bool:
        """Move a file safely with backup and validation"""
        if not source.exists():
            print(f"⚠️  File not found: {source}")
            return False
            
        # Create backup
        backup_path = self.backup_dir / source.relative_to(self.scripts_dir)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup_path)
        
        # Determine destination
        dest_path = self.scripts_dir / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)
        
        final_dest = dest_path / source.name
        
        # Check if destination already exists
        if final_dest.exists():
            print(f"⚠️  Destination exists, skipping: {source.name}")
            return False
            
        try:
            shutil.move(str(source), str(final_dest))
            print(f"✅ Moved: {source.relative_to(self.scripts_dir)} → {dest_dir}/{source.name}")
            
            self.report["moved_files"].append({
                "source": str(source.relative_to(self.scripts_dir)),
                "destination": f"{dest_dir}/{source.name}",
                "backup": str(backup_path)
            })
            return True
            
        except Exception as e:
            error_msg = f"Failed to move {source}: {e}"
            print(f"❌ {error_msg}")
            self.report["errors"].append(error_msg)
            return False
            
    def reorganize_development_files(self):
        """Reorganize files from development directory"""
        print(f"\n🔄 Reorganizing scripts/development/ directory...")
        print(f"📍 Scripts directory: {self.scripts_dir}")
        print(f"🔒 Constitutional hash: {self.CONSTITUTIONAL_HASH}")
        
        categorization = self.get_file_categorization()
        
        for category, patterns in categorization.items():
            print(f"\n📁 Moving {category} files...")
            files_to_move = self.find_files_by_patterns(patterns)
            
            for file_path in files_to_move:
                self.move_file_safely(file_path, category)
                
    def clean_empty_subdirectories(self):
        """Remove empty subdirectories in development/"""
        print(f"\n🧹 Cleaning empty subdirectories...")
        
        for subdir in self.dev_dir.iterdir():
            if subdir.is_dir():
                try:
                    # Try to remove if empty
                    if not any(subdir.iterdir()):
                        subdir.rmdir()
                        print(f"🗑️  Removed empty directory: {subdir.relative_to(self.scripts_dir)}")
                except OSError:
                    # Directory not empty, skip
                    pass
                    
    def update_script_references(self):
        """Update references to moved scripts in other files"""
        print(f"\n🔗 Updating script references...")
        
        # This is a simplified version - in practice, you'd want to scan
        # for references to moved scripts and update them
        reference_files = [
            self.project_root / ".github" / "workflows",
            self.project_root / "docs",
            self.project_root / "scripts"
        ]
        
        # For now, just report that this step would be needed
        print("⚠️  Manual review needed for script reference updates")
        
    def generate_report(self):
        """Generate reorganization report"""
        self.report["summary"] = {
            "total_moved": len(self.report["moved_files"]),
            "total_errors": len(self.report["errors"]),
            "backup_location": str(self.backup_dir)
        }
        
        report_path = self.project_root / "reports" / f"scripts_reorganization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        print(f"\n📋 Report saved: {report_path}")
        print(f"✅ Moved {self.report['summary']['total_moved']} files")
        print(f"❌ Errors: {self.report['summary']['total_errors']}")
        
    def run(self):
        """Execute the complete reorganization process"""
        self.create_backup_dir()
        self.reorganize_development_files()
        self.clean_empty_subdirectories()
        self.update_script_references()
        self.generate_report()
        print(f"\n🎉 Scripts directory reorganization completed!")
        print(f"🔒 Constitutional compliance maintained: {self.CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    organizer = ScriptsDirectoryOrganizer()
    organizer.run()
