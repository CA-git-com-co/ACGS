#!/usr/bin/env python3
"""
ACGS Log Files and Temporary Data Cleanup
Constitutional Hash: cdd01ef066bc6cf2

Safely removes old log files, temporary JSON reports, and development artifacts
while preserving audit logs and constitutional compliance data.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Log cleanup patterns (files older than 7 days)
LOG_CLEANUP_PATTERNS = [
    "*.log",
    "*.log.*",
    "*_report_*.json",
    "*_results_*.json", 
    "*_metrics_*.json",
    "*_analysis_*.json",
    "*_summary_*.json",
    "*_validation_*.json",
    "*_performance_*.json",
    "*_test_*.json"
]

# Protected log patterns (never clean)
PROTECTED_LOG_PATTERNS = [
    "*constitutional*",
    "*compliance*", 
    "*audit*",
    "*governance*",
    "*security*",
    "*integrity*"
]

# Directories to clean temporary files from
TEMP_CLEANUP_DIRS = [
    "logs",
    "reports", 
    "metrics",
    "analysis",
    "validation_reports",
    "backups"
]

class ACGSLogCleanup:
    """Handles safe cleanup of log files and temporary data."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "bytes_freed": 0,
            "protected_files": 0,
            "errors": []
        }
        self.cutoff_date = datetime.now() - timedelta(days=7)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cleanup operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _get_file_age(self, file_path: Path) -> datetime:
        """Get file modification time."""
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file should be protected from cleanup."""
        file_str = str(file_path).lower()
        
        # Check for constitutional compliance content
        if CONSTITUTIONAL_HASH in file_str:
            return True
            
        # Check protected patterns
        for pattern in PROTECTED_LOG_PATTERNS:
            if pattern.replace("*", "") in file_str:
                return True
        
        # Check if file contains constitutional hash
        if file_path.suffix in ['.json', '.log', '.md', '.txt']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024)  # Read first 1KB
                    if CONSTITUTIONAL_HASH in content:
                        return True
            except (UnicodeDecodeError, PermissionError):
                pass
        
        return False
    
    def _is_old_file(self, file_path: Path) -> bool:
        """Check if file is older than cutoff date."""
        try:
            file_age = self._get_file_age(file_path)
            return file_age < self.cutoff_date
        except OSError:
            return False
    
    def clean_log_files(self) -> List[str]:
        """Clean old log files while preserving protected ones."""
        self.logger.info("🗑️ Cleaning old log files (>7 days)...")
        removed_files = []
        
        for pattern in LOG_CLEANUP_PATTERNS:
            for log_file in REPO_ROOT.rglob(pattern):
                if log_file.is_file():
                    if self._is_protected_file(log_file):
                        self.cleanup_stats["protected_files"] += 1
                        self.logger.info(f"  🛡️ Protected: {log_file.relative_to(REPO_ROOT)}")
                        continue
                    
                    if self._is_old_file(log_file):
                        try:
                            size = log_file.stat().st_size
                            log_file.unlink()
                            removed_files.append(str(log_file.relative_to(REPO_ROOT)))
                            self.cleanup_stats["files_removed"] += 1
                            self.cleanup_stats["bytes_freed"] += size
                            self.logger.info(f"  ✅ Removed: {log_file.relative_to(REPO_ROOT)}")
                        except Exception as e:
                            error_msg = f"Failed to remove {log_file}: {e}"
                            self.cleanup_stats["errors"].append(error_msg)
                            self.logger.error(f"  ❌ {error_msg}")
        
        return removed_files
    
    def clean_temporary_reports(self) -> List[str]:
        """Clean temporary report files."""
        self.logger.info("🗑️ Cleaning temporary report files...")
        removed_files = []
        
        # Look for timestamped files that are likely temporary
        timestamp_patterns = [
            "*_20[0-9][0-9][0-1][0-9][0-3][0-9]_*.json",
            "*_20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]*.json",
            "*_20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]*.md"
        ]
        
        for pattern in timestamp_patterns:
            for temp_file in REPO_ROOT.rglob(pattern):
                if temp_file.is_file():
                    if self._is_protected_file(temp_file):
                        self.cleanup_stats["protected_files"] += 1
                        self.logger.info(f"  🛡️ Protected: {temp_file.relative_to(REPO_ROOT)}")
                        continue
                    
                    if self._is_old_file(temp_file):
                        try:
                            size = temp_file.stat().st_size
                            temp_file.unlink()
                            removed_files.append(str(temp_file.relative_to(REPO_ROOT)))
                            self.cleanup_stats["files_removed"] += 1
                            self.cleanup_stats["bytes_freed"] += size
                            self.logger.info(f"  ✅ Removed: {temp_file.relative_to(REPO_ROOT)}")
                        except Exception as e:
                            error_msg = f"Failed to remove {temp_file}: {e}"
                            self.cleanup_stats["errors"].append(error_msg)
                            self.logger.error(f"  ❌ {error_msg}")
        
        return removed_files
    
    def clean_development_artifacts(self) -> List[str]:
        """Clean development artifacts and temporary files."""
        self.logger.info("🗑️ Cleaning development artifacts...")
        removed_files = []
        
        # Development artifact patterns
        dev_patterns = [
            "*.tmp",
            "*.temp", 
            "*~",
            "*.bak",
            "*.backup",
            ".DS_Store",
            "Thumbs.db",
            "*.swp",
            "*.swo"
        ]
        
        for pattern in dev_patterns:
            for dev_file in REPO_ROOT.rglob(pattern):
                if dev_file.is_file():
                    if self._is_protected_file(dev_file):
                        self.cleanup_stats["protected_files"] += 1
                        continue
                    
                    try:
                        size = dev_file.stat().st_size
                        dev_file.unlink()
                        removed_files.append(str(dev_file.relative_to(REPO_ROOT)))
                        self.cleanup_stats["files_removed"] += 1
                        self.cleanup_stats["bytes_freed"] += size
                        self.logger.info(f"  ✅ Removed: {dev_file.relative_to(REPO_ROOT)}")
                    except Exception as e:
                        error_msg = f"Failed to remove {dev_file}: {e}"
                        self.cleanup_stats["errors"].append(error_msg)
                        self.logger.error(f"  ❌ {error_msg}")
        
        return removed_files
    
    def clean_empty_directories(self) -> List[str]:
        """Remove empty directories (except protected ones)."""
        self.logger.info("🗑️ Cleaning empty directories...")
        removed_dirs = []
        
        # Find empty directories
        for dir_path in REPO_ROOT.rglob("*"):
            if dir_path.is_dir():
                try:
                    # Check if directory is empty
                    if not any(dir_path.iterdir()):
                        # Don't remove protected directories
                        if self._is_protected_file(dir_path):
                            continue
                        
                        # Don't remove important directories
                        important_dirs = {
                            ".git", "services", "config", "docs", 
                            "infrastructure", "tests", "tools"
                        }
                        
                        if any(part in important_dirs for part in dir_path.parts):
                            continue
                        
                        dir_path.rmdir()
                        removed_dirs.append(str(dir_path.relative_to(REPO_ROOT)))
                        self.cleanup_stats["directories_removed"] += 1
                        self.logger.info(f"  ✅ Removed empty dir: {dir_path.relative_to(REPO_ROOT)}")
                except (OSError, PermissionError) as e:
                    # Directory not empty or permission denied
                    continue
        
        return removed_dirs
    
    def validate_constitutional_compliance(self) -> bool:
        """Ensure constitutional compliance files are still intact."""
        self.logger.info("🔍 Validating constitutional compliance preservation...")
        
        critical_files = [
            "constitutional_compliance_audit_and_fixes.py",
            "fix_constitutional_hashes.py",
            "CLAUDE.md",
            "config/constitutional_compliance.json"
        ]
        
        all_exist = True
        for file_path in critical_files:
            full_path = REPO_ROOT / file_path
            if not full_path.exists():
                self.logger.error(f"❌ CRITICAL: Constitutional file missing: {file_path}")
                all_exist = False
            else:
                self.logger.info(f"✅ Constitutional file preserved: {file_path}")
        
        return all_exist
    
    def run_cleanup(self) -> Dict:
        """Run complete log and temporary data cleanup."""
        self.logger.info("🧹 Starting ACGS Log and Temporary Data Cleanup...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        self.logger.info(f"Cutoff Date: {self.cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all cleanup operations
        self.clean_log_files()
        self.clean_temporary_reports()
        self.clean_development_artifacts()
        self.clean_empty_directories()
        
        # Validate constitutional compliance
        if not self.validate_constitutional_compliance():
            self.logger.error("❌ Constitutional compliance validation failed!")
            return {"error": "Constitutional compliance validation failed"}
        
        # Format bytes freed
        bytes_freed = self.cleanup_stats["bytes_freed"]
        if bytes_freed > 1024 * 1024:
            size_str = f"{bytes_freed / (1024 * 1024):.1f} MB"
        elif bytes_freed > 1024:
            size_str = f"{bytes_freed / 1024:.1f} KB"
        else:
            size_str = f"{bytes_freed} bytes"
        
        self.logger.info("📊 Cleanup Summary:")
        self.logger.info(f"  Files removed: {self.cleanup_stats['files_removed']}")
        self.logger.info(f"  Directories removed: {self.cleanup_stats['directories_removed']}")
        self.logger.info(f"  Protected files: {self.cleanup_stats['protected_files']}")
        self.logger.info(f"  Space freed: {size_str}")
        self.logger.info(f"  Errors: {len(self.cleanup_stats['errors'])}")
        
        if self.cleanup_stats["errors"]:
            self.logger.warning("⚠️ Errors encountered:")
            for error in self.cleanup_stats["errors"]:
                self.logger.warning(f"  - {error}")
        
        return self.cleanup_stats

def main():
    """Main cleanup function."""
    print("🧹 ACGS Log Files and Temporary Data Cleanup")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()
    
    cleaner = ACGSLogCleanup()
    results = cleaner.run_cleanup()
    
    if "error" not in results:
        print("\n✅ Log and temporary data cleanup completed!")
    else:
        print(f"\n❌ Cleanup failed: {results['error']}")
    
    return results

if __name__ == "__main__":
    main()
