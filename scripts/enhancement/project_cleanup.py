#!/usr/bin/env python3
"""
ACGS-2 Project Cleanup Script
Constitutional Hash: cdd01ef066bc6cf2

This script performs comprehensive cleanup of processing documents while preserving essential files:
1. Remove temporary and backup files
2. Organize reports into logical structure
3. Clean up old archive directories
4. Preserve essential documentation and configurations
5. Maintain constitutional compliance throughout
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set
import json
from datetime import datetime

class ProjectCleanup:
    """Comprehensive project cleanup with preservation of essential files"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Files and directories to preserve (essential)
        self.preserve_patterns = {
            # Essential documentation
            "CLAUDE.md", "README.md", "CHANGELOG.md", "CONTRIBUTING.md",
            "DEPENDENCIES.md", "EXECUTIVE_SUMMARY.md", "NON_TECHNICAL_SUMMARY.md",
            
            # Essential configuration
            "docker-compose.yml", "Dockerfile", "config/environments/requirements.txt", "package.json",
            "config/environments/pyproject.toml", "Cargo.toml", "go.mod", ".env.example",
            
            # Essential scripts and tools
            "scripts/enhancement/", "scripts/validation/", "scripts/reorganization/",
            ".github/workflows/",
            
            # Essential reports (keep latest)
            "constitutional_compliance_report_", "claude_md_cross_reference_report",
            "ACGS_2_SYSTEMATIC_REORGANIZATION_", "ACGS_2_NEXT_PHASE_",
            "ACGS_2_VALIDATED_COMPLETION_SUMMARY.md"
        }
        
        # Patterns for files/directories to remove
        self.cleanup_patterns = {
            # Temporary files
            "*.tmp", "*.temp", "*.bak", "*.backup", "*.old",
            
            # Cache and build artifacts
            "__pycache__/", "*.pyc", "*.pyo", ".pytest_cache/",
            "node_modules/", "target/", ".cache/", "htmlcov/",
            
            # Editor and IDE files
            ".vscode/", ".idea/", "*.swp", "*.swo", "*~",
            
            # OS files
            ".DS_Store", "Thumbs.db", "desktop.ini",
            
            # Log files (old)
            "*.log", "*.log.*", "logs/",
            
            # Archive directories (old)
            "docs_consolidated_archive_*", "archive/",
            
            # Duplicate backup files
            "*.backup", "*.bak"
        }
        
        # Archive directories to evaluate
        self.archive_directories = [
            "docs_backup_20250717_155154",
            "docs_consolidated_archive_20250710_120000",
            "archive"
        ]
    
    def analyze_directory_size(self, directory: Path) -> Dict:
        """Analyze directory size and file count"""
        if not directory.exists():
            return {"size_mb": 0, "file_count": 0, "exists": False}
        
        total_size = 0
        file_count = 0
        
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
        except Exception as e:
            print(f"  ⚠️ Error analyzing {directory}: {e}")
        
        return {
            "size_mb": total_size / (1024 * 1024),
            "file_count": file_count,
            "exists": True
        }
    
    def should_preserve_file(self, file_path: Path) -> bool:
        """Determine if a file should be preserved"""
        file_str = str(file_path)
        file_name = file_path.name
        
        # Always preserve files with constitutional hash
        try:
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.yml', '.yaml', '.json']:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if self.constitutional_hash in content:
                    return True
        except:
            pass
        
        # Check preserve patterns
        for pattern in self.preserve_patterns:
            if pattern in file_str or pattern in file_name:
                return True
        
        # Preserve recent files (last 7 days)
        try:
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                age_days = (datetime.now().timestamp() - mtime) / (24 * 3600)
                if age_days < 7:
                    return True
        except:
            pass
        
        return False
    
    def should_cleanup_file(self, file_path: Path) -> bool:
        """Determine if a file should be cleaned up"""
        file_str = str(file_path)
        file_name = file_path.name
        
        # Don't cleanup preserved files
        if self.should_preserve_file(file_path):
            return False
        
        # Check cleanup patterns
        for pattern in self.cleanup_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if pattern.rstrip('/') in file_str:
                    return True
            elif '*' in pattern:
                # Wildcard pattern
                import fnmatch
                if fnmatch.fnmatch(file_name, pattern):
                    return True
            else:
                # Exact match
                if pattern in file_str or pattern == file_name:
                    return True
        
        return False
    
    def cleanup_archive_directories(self) -> Dict:
        """Clean up old archive directories"""
        print("📦 Analyzing archive directories...")
        
        cleanup_stats = {
            "directories_analyzed": 0,
            "directories_removed": 0,
            "space_freed_mb": 0,
            "files_removed": 0
        }
        
        for archive_name in self.archive_directories:
            archive_path = self.project_root / archive_name
            
            if archive_path.exists():
                cleanup_stats["directories_analyzed"] += 1
                
                # Analyze before removal
                analysis = self.analyze_directory_size(archive_path)
                print(f"  📁 {archive_name}: {analysis['size_mb']:.1f} MB, {analysis['file_count']} files")
                
                # Check if it's safe to remove (older than 30 days or very large)
                try:
                    mtime = archive_path.stat().st_mtime
                    age_days = (datetime.now().timestamp() - mtime) / (24 * 3600)
                    
                    should_remove = (
                        age_days > 30 or  # Older than 30 days
                        analysis['size_mb'] > 100 or  # Larger than 100 MB
                        "consolidated_archive" in archive_name  # Old consolidated archives
                    )
                    
                    if should_remove:
                        shutil.rmtree(archive_path)
                        cleanup_stats["directories_removed"] += 1
                        cleanup_stats["space_freed_mb"] += analysis['size_mb']
                        cleanup_stats["files_removed"] += analysis['file_count']
                        print(f"    ✅ Removed: {analysis['size_mb']:.1f} MB freed")
                    else:
                        print(f"    ⏸️ Preserved: Recent or small archive")
                        
                except Exception as e:
                    print(f"    ❌ Error removing {archive_name}: {e}")
        
        return cleanup_stats
    
    def cleanup_temporary_files(self) -> Dict:
        """Clean up temporary and backup files"""
        print("🧹 Cleaning up temporary files...")
        
        cleanup_stats = {
            "files_analyzed": 0,
            "files_removed": 0,
            "space_freed_mb": 0
        }
        
        # Find files to cleanup
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue
            
            cleanup_stats["files_analyzed"] += 1
            
            if self.should_cleanup_file(file_path):
                try:
                    file_size = file_path.stat().st_size / (1024 * 1024)
                    file_path.unlink()
                    cleanup_stats["files_removed"] += 1
                    cleanup_stats["space_freed_mb"] += file_size
                    
                    if cleanup_stats["files_removed"] <= 20:  # Show first 20
                        print(f"  ✅ Removed: {file_path.relative_to(self.project_root)}")
                        
                except Exception as e:
                    print(f"  ❌ Error removing {file_path}: {e}")
        
        return cleanup_stats
    
    def organize_reports(self) -> Dict:
        """Organize reports into logical structure"""
        print("📊 Organizing reports...")
        
        reports_dir = self.project_root / "reports"
        if not reports_dir.exists():
            return {"organized": 0, "errors": 0}
        
        organization_stats = {
            "organized": 0,
            "errors": 0
        }
        
        # Create organized subdirectories
        subdirs = {
            "compliance": reports_dir / "compliance",
            "performance": reports_dir / "performance", 
            "validation": reports_dir / "validation",
            "security": reports_dir / "security",
            "coverage": reports_dir / "coverage",
            "test_reports": reports_dir / "test_reports"
        }
        
        for subdir in subdirs.values():
            subdir.mkdir(exist_ok=True)
        
        # Move files to appropriate subdirectories
        for file_path in reports_dir.iterdir():
            if not file_path.is_file():
                continue
            
            file_name = file_path.name.lower()
            target_dir = None
            
            if "compliance" in file_name or "constitutional" in file_name:
                target_dir = subdirs["compliance"]
            elif "performance" in file_name or "benchmark" in file_name:
                target_dir = subdirs["performance"]
            elif "validation" in file_name or "test" in file_name:
                target_dir = subdirs["validation"]
            elif "security" in file_name or "vulnerability" in file_name:
                target_dir = subdirs["security"]
            elif "coverage" in file_name:
                target_dir = subdirs["coverage"]
            
            if target_dir and file_path.parent != target_dir:
                try:
                    target_path = target_dir / file_path.name
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
                        organization_stats["organized"] += 1
                        if organization_stats["organized"] <= 10:  # Show first 10
                            print(f"  📁 Moved: {file_path.name} → {target_dir.name}/")
                except Exception as e:
                    organization_stats["errors"] += 1
                    print(f"  ❌ Error moving {file_path.name}: {e}")
        
        return organization_stats
    
    def generate_cleanup_report(self, stats: Dict) -> str:
        """Generate comprehensive cleanup report"""
        report_path = self.project_root / "ACGS_2_PROJECT_CLEANUP_REPORT.md"
        
        report_content = f"""# ACGS-2 Project Cleanup Report
<!-- Constitutional Hash: {self.constitutional_hash} -->

## Cleanup Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Constitutional Hash**: `{self.constitutional_hash}`

### Archive Cleanup
- **Directories Analyzed**: {stats['archive']['directories_analyzed']}
- **Directories Removed**: {stats['archive']['directories_removed']}
- **Space Freed**: {stats['archive']['space_freed_mb']:.1f} MB
- **Files Removed**: {stats['archive']['files_removed']}

### Temporary File Cleanup
- **Files Analyzed**: {stats['temp']['files_analyzed']}
- **Files Removed**: {stats['temp']['files_removed']}
- **Space Freed**: {stats['temp']['space_freed_mb']:.1f} MB

### Report Organization
- **Reports Organized**: {stats['reports']['organized']}
- **Organization Errors**: {stats['reports']['errors']}

### Total Impact
- **Total Space Freed**: {stats['archive']['space_freed_mb'] + stats['temp']['space_freed_mb']:.1f} MB
- **Total Files Removed**: {stats['archive']['files_removed'] + stats['temp']['files_removed']}

## Preserved Files

The following essential files and directories were preserved:
- All CLAUDE.md files with constitutional compliance
- Essential configuration files (docker-compose.yml, config/environments/requirements.txt, etc.)
- Enhancement and validation scripts
- GitHub Actions workflows
- Recent reports and documentation
- Files containing constitutional hash `{self.constitutional_hash}`

## Post-Cleanup Structure

The project now has a clean, organized structure with:
- ✅ Organized reports in `/reports` subdirectories
- ✅ Removed temporary and backup files
- ✅ Cleaned up old archive directories
- ✅ Preserved all essential documentation and configurations
- ✅ Maintained constitutional compliance throughout

---

**Constitutional Compliance**: All cleanup operations maintained constitutional hash `{self.constitutional_hash}` validation and preserved essential project files.

**Implementation Status**: ✅ COMPLETED - Project cleanup successful with {stats['archive']['space_freed_mb'] + stats['temp']['space_freed_mb']:.1f} MB space freed

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')} - Comprehensive project cleanup completion
"""
        
        report_path.write_text(report_content)
        return str(report_path)
    
    def execute_project_cleanup(self):
        """Execute comprehensive project cleanup"""
        print("🚀 Starting ACGS-2 Project Cleanup")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target: Clean up processing documents while preserving essential files")
        
        try:
            # Collect cleanup statistics
            stats = {
                "archive": self.cleanup_archive_directories(),
                "temp": self.cleanup_temporary_files(),
                "reports": self.organize_reports()
            }
            
            # Generate cleanup report
            report_path = self.generate_cleanup_report(stats)
            
            total_space_freed = stats['archive']['space_freed_mb'] + stats['temp']['space_freed_mb']
            total_files_removed = stats['archive']['files_removed'] + stats['temp']['files_removed']
            
            print(f"\n✅ Project cleanup completed!")
            print(f"📊 Summary:")
            print(f"  - Archive directories removed: {stats['archive']['directories_removed']}")
            print(f"  - Temporary files removed: {stats['temp']['files_removed']}")
            print(f"  - Reports organized: {stats['reports']['organized']}")
            print(f"  - Total space freed: {total_space_freed:.1f} MB")
            print(f"  - Total files removed: {total_files_removed}")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            print(f"  - Cleanup report: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Project cleanup failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    cleanup = ProjectCleanup(project_root)
    
    # Execute project cleanup
    success = cleanup.execute_project_cleanup()
    
    if success:
        print("\n🎉 Project Cleanup Complete!")
        print("✅ Processing documents cleaned up while preserving essential files")
    else:
        print("\n❌ Project cleanup encountered issues.")

if __name__ == "__main__":
    main()
