#!/usr/bin/env python3
"""
ACGS-2 Root Directory Cleanup Script
Constitutional Hash: cdd01ef066bc6cf2

This script systematically reorganizes the ACGS-2 root directory by moving
misplaced files to their proper locations according to ACGS-2 architectural patterns.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ACGS2RootCleanup:
    """Systematic root directory cleanup following ACGS-2 patterns"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "archive" / "root_cleanup_backup"
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
        
    def get_misplaced_files(self) -> Dict[str, List[str]]:
        """Identify files that need to be moved"""
        
        # Documentation files that should be in docs/reports/
        docs_files = [
            "ACGS_2_COMPREHENSIVE_DUPLICATE_CODE_ANALYSIS.md",
            "ACGS_2_COMPREHENSIVE_TECHNICAL_ANALYSIS_REPORT.md", 
            "ACGS_2_DUPLICATE_IMPLEMENTATION_SUMMARY.md",
            "ACGS_2_DUPLICATE_REMOVAL_COMPLETION_REPORT.md",
            "ACGS_2_FINAL_COMPLETION_REPORT.md",
            "ACGS_2_NEXT_PHASE_COMPLETION_REPORT.md",
            "ACGS_2_PROJECT_CLEANUP_REPORT.md",
            "ACGS_2_SYSTEMATIC_REORGANIZATION_COMPLETION_REPORT.md",
            "ACGS_2_SYSTEMATIC_REORGANIZATION_PLAN.md",
            "ACGS_2_VALIDATED_COMPLETION_SUMMARY.md",
            "REMAINING_SERVICES_DESIGN_COMPLETE.md",
            "comprehensive_consolidation_completion_report.md",
            "comprehensive_deployment_report_20250718_093439.md",
            "production-deployment-plan.md"
        ]
        
        # Configuration files that should be in config/
        config_files = [
            "config/docker/docker-compose.local.yml",
            "config/docker/docker-compose.test.yml", 
            "config/nginx.production.conf",
            "config/environments/pnpm-lock.yaml",
            "config/environments/pnpm-workspace.yaml",
            "config/environments/pyproject.toml",
            "config/environments/pytest.benchmark.ini",
            "config/environments/pytest.ini",
            "config/environments/requirements-security.txt",
            "config/environments/requirements.txt",
            "config/environments/uv.lock",
            "config/environments/uv.toml"
        ]
        
        # JSON reports that should be in reports/
        report_files = [
            "claude_md_cross_reference_report.json",
            "compliance_report.json",
            "compliance_report_fixed.json", 
            "comprehensive_codebase_analysis.json",
            "detailed_compliance_analysis.json",
            "duplicate_removal_report.json",
            "final_compliance_report.json"
        ]
        
        # Backup files to archive
        backup_files = [
            "CHANGELOG.md.backup",
            "README.md.backup"
        ]
        
        # Artifacts to clean up
        cleanup_files = [
            "=4.5.0",  # Stray file
            "acgs_security.db"  # Should be in database/
        ]
        
        return {
            "docs": docs_files,
            "config": config_files, 
            "reports": report_files,
            "backup": backup_files,
            "cleanup": cleanup_files
        }
        
    def move_file_safely(self, source: str, dest_dir: str, filename: str = None) -> bool:
        """Move a file safely with backup and validation"""
        source_path = self.project_root / source
        
        if not source_path.exists():
            print(f"⚠️  File not found: {source}")
            return False
            
        # Create backup
        backup_path = self.backup_dir / source
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, backup_path)
        
        # Determine destination
        dest_path = self.project_root / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)
        
        final_name = filename or source_path.name
        final_dest = dest_path / final_name
        
        try:
            shutil.move(str(source_path), str(final_dest))
            print(f"✅ Moved: {source} → {dest_dir}/{final_name}")
            
            self.report["moved_files"].append({
                "source": source,
                "destination": f"{dest_dir}/{final_name}",
                "backup": str(backup_path)
            })
            return True
            
        except Exception as e:
            error_msg = f"Failed to move {source}: {e}"
            print(f"❌ {error_msg}")
            self.report["errors"].append(error_msg)
            return False
            
    def reorganize_files(self):
        """Execute the reorganization plan"""
        print(f"\n🚀 Starting ACGS-2 root directory cleanup...")
        print(f"📍 Project root: {self.project_root}")
        print(f"🔒 Constitutional hash: {self.CONSTITUTIONAL_HASH}")
        
        misplaced = self.get_misplaced_files()
        
        # Move documentation files
        print(f"\n📄 Moving documentation files to docs/reports/...")
        for file in misplaced["docs"]:
            self.move_file_safely(file, "docs/reports")
            
        # Move configuration files  
        print(f"\n⚙️  Moving configuration files to config/...")
        for file in misplaced["config"]:
            if file.startswith("docker-compose"):
                self.move_file_safely(file, "config/docker")
            elif file in ["config/environments/pyproject.toml", "config/environments/uv.lock", "config/environments/uv.toml"]:
                self.move_file_safely(file, "config/environments")
            elif file.startswith("requirements"):
                self.move_file_safely(file, "config/environments") 
            elif file.startswith("pytest"):
                self.move_file_safely(file, "config/environments")
            elif file.startswith("pnpm"):
                self.move_file_safely(file, "config/environments")
            else:
                self.move_file_safely(file, "config")
                
        # Move report files
        print(f"\n📊 Moving report files to reports/...")
        for file in misplaced["reports"]:
            self.move_file_safely(file, "reports")
            
        # Archive backup files
        print(f"\n🗄️  Archiving backup files...")
        for file in misplaced["backup"]:
            self.move_file_safely(file, "archive/backups")
            
        # Handle cleanup files
        print(f"\n🧹 Cleaning up artifacts...")
        for file in misplaced["cleanup"]:
            if file == "acgs_security.db":
                self.move_file_safely(file, "database/data")
            else:
                # Remove stray files
                file_path = self.project_root / file
                if file_path.exists():
                    backup_path = self.backup_dir / file
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    file_path.unlink()
                    print(f"🗑️  Removed: {file}")
                    
    def generate_report(self):
        """Generate cleanup report"""
        self.report["summary"] = {
            "total_moved": len(self.report["moved_files"]),
            "total_errors": len(self.report["errors"]),
            "backup_location": str(self.backup_dir)
        }
        
        report_path = self.project_root / "reports" / f"root_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        print(f"\n📋 Report saved: {report_path}")
        print(f"✅ Moved {self.report['summary']['total_moved']} files")
        print(f"❌ Errors: {self.report['summary']['total_errors']}")
        
    def run(self):
        """Execute the complete cleanup process"""
        self.create_backup_dir()
        self.reorganize_files()
        self.generate_report()
        print(f"\n🎉 ACGS-2 root directory cleanup completed!")
        print(f"🔒 Constitutional compliance maintained: {self.CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    cleanup = ACGS2RootCleanup()
    cleanup.run()
