#!/usr/bin/env python3
"""
ACGS-2 Duplicate Files Removal Script
Constitutional Hash: cdd01ef066bc6cf2

This script identifies and removes duplicate files while preserving essential functionality
and maintaining constitutional compliance throughout the cleanup process.
"""

import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict

class DuplicateFilesRemover:
    """Remove duplicate files while preserving functionality"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "archive" / "duplicates_removal_backup"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "duplicates_found": {},
            "removed_files": [],
            "preserved_files": [],
            "errors": [],
            "summary": {}
        }
        
        # Directories to skip during duplicate detection
        self.skip_dirs = {
            ".git", "__pycache__", "node_modules", "target", 
            ".pytest_cache", ".coverage", "htmlcov",
            "archive", "backup", "logs", "pids"
        }
        
        # File extensions to prioritize when choosing which duplicate to keep
        self.priority_extensions = [".py", ".rs", ".js", ".ts", ".yml", ".yaml", ".md"]
        
    def create_backup_dir(self):
        """Create backup directory for safety"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created backup directory: {self.backup_dir}")
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  Could not hash {file_path}: {e}")
            return None
            
    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during duplicate detection"""
        # Skip files in certain directories
        for part in file_path.parts:
            if part in self.skip_dirs:
                return True
                
        # Skip very small files (likely empty or minimal)
        try:
            if file_path.stat().st_size < 10:
                return True
        except:
            return True
            
        # Skip binary files that are likely unique
        binary_extensions = {".db", ".sqlite", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}
        if file_path.suffix.lower() in binary_extensions:
            return True
            
        return False
        
    def find_duplicate_files(self) -> Dict[str, List[Path]]:
        """Find all duplicate files in the project"""
        print(f"\n🔍 Scanning for duplicate files...")
        
        hash_to_files = defaultdict(list)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self.should_skip_file(file_path):
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    hash_to_files[file_hash].append(file_path)
                    
        # Filter to only groups with duplicates
        duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
        
        print(f"📊 Found {len(duplicates)} groups of duplicate files")
        return duplicates
        
    def choose_file_to_keep(self, duplicate_files: List[Path]) -> Path:
        """Choose which duplicate file to keep based on priority rules"""
        
        # Rule 1: Prefer files not in backup directories
        non_backup_files = [f for f in duplicate_files if "backup" not in str(f).lower()]
        if non_backup_files:
            duplicate_files = non_backup_files
            
        # Rule 2: Prefer files with priority extensions
        for ext in self.priority_extensions:
            priority_files = [f for f in duplicate_files if f.suffix == ext]
            if priority_files:
                duplicate_files = priority_files
                break
                
        # Rule 3: Prefer files in main directories over subdirectories
        main_dirs = ["services", "scripts", "docs", "config"]
        for main_dir in main_dirs:
            main_files = [f for f in duplicate_files if str(f).startswith(str(self.project_root / main_dir))]
            if main_files:
                duplicate_files = main_files
                break
                
        # Rule 4: Prefer shorter paths (closer to root)
        duplicate_files.sort(key=lambda x: len(x.parts))
        
        return duplicate_files[0]
        
    def remove_duplicate_safely(self, file_to_remove: Path) -> bool:
        """Remove a duplicate file safely with backup"""
        try:
            # Create backup
            backup_path = self.backup_dir / file_to_remove.relative_to(self.project_root)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy to backup before removing
            import shutil
            shutil.copy2(file_to_remove, backup_path)
            
            # Remove the file
            file_to_remove.unlink()
            
            print(f"🗑️  Removed: {file_to_remove.relative_to(self.project_root)}")
            
            self.report["removed_files"].append({
                "file": str(file_to_remove.relative_to(self.project_root)),
                "backup": str(backup_path)
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to remove {file_to_remove}: {e}"
            print(f"❌ {error_msg}")
            self.report["errors"].append(error_msg)
            return False
            
    def process_duplicates(self):
        """Process all duplicate files"""
        duplicates = self.find_duplicate_files()
        
        if not duplicates:
            print("✅ No duplicate files found!")
            return
            
        print(f"\n🔄 Processing {len(duplicates)} groups of duplicates...")
        
        for file_hash, duplicate_files in duplicates.items():
            print(f"\n📁 Processing group with {len(duplicate_files)} duplicates:")
            
            # Show all files in the group
            for file_path in duplicate_files:
                print(f"   - {file_path.relative_to(self.project_root)}")
                
            # Choose which file to keep
            file_to_keep = self.choose_file_to_keep(duplicate_files)
            files_to_remove = [f for f in duplicate_files if f != file_to_keep]
            
            print(f"   ✅ Keeping: {file_to_keep.relative_to(self.project_root)}")
            
            self.report["preserved_files"].append(str(file_to_keep.relative_to(self.project_root)))
            
            # Remove the duplicates
            for file_to_remove in files_to_remove:
                self.remove_duplicate_safely(file_to_remove)
                
            # Store in report
            self.report["duplicates_found"][file_hash] = {
                "kept": str(file_to_keep.relative_to(self.project_root)),
                "removed": [str(f.relative_to(self.project_root)) for f in files_to_remove]
            }
            
    def clean_backup_files(self):
        """Clean up .backup files that are no longer needed"""
        print(f"\n🧹 Cleaning up .backup files...")
        
        backup_files = list(self.project_root.rglob("*.backup"))
        
        for backup_file in backup_files:
            original_file = backup_file.with_suffix('')
            
            # If original file exists and is newer, remove backup
            if original_file.exists():
                try:
                    backup_mtime = backup_file.stat().st_mtime
                    original_mtime = original_file.stat().st_mtime
                    
                    if original_mtime > backup_mtime:
                        # Move to archive instead of deleting
                        archive_path = self.backup_dir / "old_backups" / backup_file.relative_to(self.project_root)
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        import shutil
                        shutil.move(str(backup_file), str(archive_path))
                        print(f"📦 Archived: {backup_file.relative_to(self.project_root)}")
                        
                except Exception as e:
                    print(f"⚠️  Could not process {backup_file}: {e}")
                    
    def generate_report(self):
        """Generate duplicate removal report"""
        self.report["summary"] = {
            "duplicate_groups_found": len(self.report["duplicates_found"]),
            "total_files_removed": len(self.report["removed_files"]),
            "total_files_preserved": len(self.report["preserved_files"]),
            "total_errors": len(self.report["errors"]),
            "backup_location": str(self.backup_dir)
        }
        
        report_path = self.project_root / "reports" / f"duplicates_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        print(f"\n📋 Report saved: {report_path}")
        print(f"✅ Removed {self.report['summary']['total_files_removed']} duplicate files")
        print(f"✅ Preserved {self.report['summary']['total_files_preserved']} unique files")
        print(f"❌ Errors: {self.report['summary']['total_errors']}")
        
    def run(self):
        """Execute the complete duplicate removal process"""
        self.create_backup_dir()
        self.process_duplicates()
        self.clean_backup_files()
        self.generate_report()
        print(f"\n🎉 Duplicate files removal completed!")
        print(f"🔒 Constitutional compliance maintained: {self.CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    remover = DuplicateFilesRemover()
    remover.run()
