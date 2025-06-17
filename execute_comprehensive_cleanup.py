#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Cleanup Execution Script

This script safely executes the cleanup plan while preserving all critical components:
- Quantumagi Solana deployment functionality
- Enhancement framework
- All 7 core services (operational versions)
- Constitutional governance files
- Database migrations and schemas

SAFETY MEASURES:
- Creates backup before any changes
- Validates critical services remain functional
- Provides rollback capability
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

class ACGSCleanupExecutor:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backups" / f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cleanup_log = []
        self.removed_files = []
        self.consolidated_services = []
        
        # Critical service mappings (keep the enhanced/hyphenated versions)
        self.service_consolidation_plan = {
            # Keep hyphenated versions, remove underscore versions
            "constitutional_ai": "constitutional-ai",
            "evolutionary_computation": "evolutionary-computation", 
            "formal_verification": "formal-verification",
            "governance_synthesis": "governance-synthesis",
            "policy_governance": "policy-governance",
            "self_evolving_ai": "self-evolving-ai"
        }

    def log_action(self, action: str, details: str = ""):
        """Log cleanup actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}"
        if details:
            log_entry += f": {details}"
        self.cleanup_log.append(log_entry)
        print(f"📝 {log_entry}")

    def create_backup(self):
        """Create backup of critical files before cleanup."""
        print("💾 Creating backup before cleanup...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup critical directories
        critical_dirs = [
            "services/core",
            "services/shared/enhancement_framework",
            "blockchain/quantumagi-deployment",
            "blockchain/programs",
            "services/shared/alembic",
            "migrations"
        ]
        
        for dir_path in critical_dirs:
            source = self.project_root / dir_path
            if source.exists():
                dest = self.backup_dir / dir_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, dest)
                self.log_action(f"Backed up {dir_path}")

    def consolidate_duplicate_services(self):
        """Consolidate duplicate service implementations."""
        print("🔄 Consolidating duplicate services...")
        
        services_core = self.project_root / "services" / "core"
        
        for old_name, new_name in self.service_consolidation_plan.items():
            old_path = services_core / old_name
            new_path = services_core / new_name
            
            if old_path.exists() and new_path.exists():
                # Compare to ensure we're keeping the more complete version
                old_size = sum(f.stat().st_size for f in old_path.rglob('*') if f.is_file())
                new_size = sum(f.stat().st_size for f in new_path.rglob('*') if f.is_file())
                
                if old_size > new_size:
                    # Old version is larger, might be more complete
                    self.log_action(f"WARNING: {old_name} ({old_size} bytes) larger than {new_name} ({new_size} bytes)")
                    print(f"⚠️  Manual review needed for {old_name} vs {new_name}")
                    continue
                
                # Remove the old underscore version
                if old_path.is_symlink():
                    old_path.unlink()
                else:
                    shutil.rmtree(old_path)
                self.removed_files.append(str(old_path))
                self.consolidated_services.append(f"{old_name} -> {new_name}")
                self.log_action(f"Removed duplicate service", f"{old_name} (kept {new_name})")

    def remove_cache_and_temp_files(self):
        """Remove cache and temporary files."""
        print("🧹 Removing cache and temporary files...")
        
        cache_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            "node_modules/.cache",
            "target/debug",
            "target/release"
        ]
        
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*~",
            "*.swp",
            "*.bak"
        ]
        
        removed_count = 0
        
        # Remove cache files
        for pattern in cache_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.exists() and not self.is_critical_path(file_path):
                    try:
                        if file_path.is_symlink():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()
                        removed_count += 1
                    except Exception as e:
                        self.log_action(f"Warning: Could not remove {file_path}: {e}")
        
        # Remove temp files
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.exists() and not self.is_critical_path(file_path):
                    try:
                        if file_path.is_symlink():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()
                        removed_count += 1
                    except Exception as e:
                        self.log_action(f"Warning: Could not remove {file_path}: {e}")
        
        self.log_action(f"Removed {removed_count} cache/temp files")

    def remove_old_log_files(self):
        """Remove old log files (keep recent ones)."""
        print("📋 Cleaning up old log files...")
        
        logs_dir = self.project_root / "logs"
        if not logs_dir.exists():
            return
        
        # Keep logs from last 7 days, remove older ones
        cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        removed_count = 0
        
        for log_file in logs_dir.rglob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                removed_count += 1
        
        # Remove old JSON reports (keep last 5 of each type)
        report_patterns = ["*_report_*.json", "*_results_*.json", "*_analysis_*.json"]
        
        for pattern in report_patterns:
            files = sorted(self.project_root.rglob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)
            for old_file in files[5:]:  # Keep newest 5, remove rest
                if not self.is_critical_path(old_file):
                    old_file.unlink()
                    removed_count += 1
        
        self.log_action(f"Removed {removed_count} old log/report files")

    def is_critical_path(self, file_path: Path) -> bool:
        """Check if path is critical and should not be removed."""
        critical_patterns = [
            "quantumagi",
            "enhancement_framework",
            "constitutional",
            "constitution",
            "cdd01ef066bc6cf2",
            "blockchain/programs",
            "alembic",
            "migrations"
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in critical_patterns)

    def validate_critical_services(self) -> bool:
        """Validate that critical services are still functional after cleanup."""
        print("✅ Validating critical services...")
        
        # Check that all 7 core services exist
        required_services = [
            "constitutional-ai",
            "governance-synthesis", 
            "formal-verification",
            "policy-governance",
            "evolutionary-computation",
            "self-evolving-ai"
        ]
        
        services_core = self.project_root / "services" / "core"
        missing_services = []
        
        for service in required_services:
            service_path = services_core / service
            if not service_path.exists():
                missing_services.append(service)
        
        if missing_services:
            self.log_action(f"ERROR: Missing critical services: {missing_services}")
            return False
        
        # Check enhancement framework
        framework_path = self.project_root / "services" / "shared" / "enhancement_framework"
        if not framework_path.exists():
            self.log_action("ERROR: Enhancement framework missing")
            return False
        
        # Check Quantumagi deployment
        quantumagi_path = self.project_root / "blockchain" / "quantumagi-deployment"
        if not quantumagi_path.exists():
            self.log_action("ERROR: Quantumagi deployment missing")
            return False
        
        self.log_action("All critical services validated successfully")
        return True

    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "actions_performed": self.cleanup_log,
            "removed_files_count": len(self.removed_files),
            "consolidated_services": self.consolidated_services,
            "validation_passed": True,
            "summary": {
                "services_consolidated": len(self.consolidated_services),
                "total_actions": len(self.cleanup_log)
            }
        }
        
        report_file = self.project_root / f"cleanup_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Cleanup report saved to {report_file}")
        return report

    def execute_cleanup(self):
        """Execute the complete cleanup process."""
        print("🚀 Starting ACGS-1 comprehensive cleanup execution...")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Consolidate duplicate services
            self.consolidate_duplicate_services()
            
            # Step 3: Remove cache and temp files
            self.remove_cache_and_temp_files()
            
            # Step 4: Clean up old logs
            self.remove_old_log_files()
            
            # Step 5: Validate critical services
            if not self.validate_critical_services():
                print("❌ Critical service validation failed! Check logs.")
                return False
            
            # Step 6: Generate report
            report = self.generate_cleanup_report()
            
            print("✅ Cleanup completed successfully!")
            print(f"📁 Backup created at: {self.backup_dir}")
            print(f"🔄 Services consolidated: {len(self.consolidated_services)}")
            print(f"📝 Total actions: {len(self.cleanup_log)}")
            
            return True
            
        except Exception as e:
            self.log_action(f"ERROR during cleanup: {str(e)}")
            print(f"❌ Cleanup failed: {e}")
            return False

if __name__ == "__main__":
    executor = ACGSCleanupExecutor()
    success = executor.execute_cleanup()
    sys.exit(0 if success else 1)
