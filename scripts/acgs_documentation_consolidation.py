#!/usr/bin/env python3
"""
ACGS Documentation and Report Consolidation
Constitutional Hash: cdd01ef066bc6cf2

Organizes and consolidates duplicate documentation files and reports
while maintaining constitutional compliance and ACGS structure.
"""

import os
import shutil
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from collections import defaultdict

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Documentation patterns to consolidate
DOC_PATTERNS = [
    "*.md",
    "*.txt", 
    "*.rst",
    "README*"
]

# Report patterns to consolidate
REPORT_PATTERNS = [
    "*_report*.md",
    "*_summary*.md",
    "*_completion*.md",
    "*_analysis*.md",
    "*REPORT*.md",
    "*SUMMARY*.md"
]

# Protected documentation (never consolidate)
PROTECTED_DOCS = {
    "README.md",
    "CLAUDE.md",
    "AGENTS.md", 
    "GEMINI.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "CHANGELOG.md"
}

class ACGSDocumentationConsolidation:
    """Handles consolidation of documentation and reports."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.consolidation_stats = {
            "duplicates_found": 0,
            "duplicates_removed": 0,
            "reports_consolidated": 0,
            "bytes_freed": 0,
            "protected_files": 0,
            "errors": []
        }
        self.file_hashes = {}
        self.duplicate_groups = defaultdict(list)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for consolidation operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file should be protected from consolidation."""
        file_name = file_path.name
        file_str = str(file_path).lower()
        
        # Check protected file names
        if file_name in PROTECTED_DOCS:
            return True
            
        # Check for constitutional compliance content
        if CONSTITUTIONAL_HASH in file_str:
            return True
            
        # Check if file contains constitutional hash
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1KB
                if CONSTITUTIONAL_HASH in content:
                    return True
        except (UnicodeDecodeError, PermissionError):
            pass
        
        # Protect critical directories
        critical_paths = ["services/core", "services/shared", "config", "infrastructure/monitoring"]
        if any(critical in str(file_path) for critical in critical_paths):
            return True
        
        return False
    
    def find_duplicate_documents(self) -> Dict[str, List[Path]]:
        """Find duplicate documentation files by content hash."""
        self.logger.info("🔍 Finding duplicate documentation files...")
        
        # Scan all documentation files
        all_docs = []
        for pattern in DOC_PATTERNS:
            all_docs.extend(REPO_ROOT.rglob(pattern))
        
        # Calculate hashes and group duplicates
        for doc_file in all_docs:
            if doc_file.is_file() and not self._is_protected_file(doc_file):
                file_hash = self._get_file_hash(doc_file)
                if file_hash:
                    self.file_hashes[str(doc_file)] = file_hash
                    self.duplicate_groups[file_hash].append(doc_file)
        
        # Filter to only groups with duplicates
        duplicates = {h: files for h, files in self.duplicate_groups.items() if len(files) > 1}
        
        self.logger.info(f"  Found {len(duplicates)} groups of duplicate files")
        return duplicates
    
    def consolidate_duplicate_reports(self) -> List[str]:
        """Consolidate duplicate report files."""
        self.logger.info("📋 Consolidating duplicate reports...")
        removed_files = []
        
        duplicates = self.find_duplicate_documents()
        
        for file_hash, duplicate_files in duplicates.items():
            # Check if any files are reports
            report_files = [f for f in duplicate_files if any(pattern.replace("*", "") in f.name.lower() for pattern in REPORT_PATTERNS)]
            
            if len(report_files) > 1:
                # Keep the most recent file, remove others
                report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                keep_file = report_files[0]
                
                for duplicate_file in report_files[1:]:
                    if not self._is_protected_file(duplicate_file):
                        try:
                            size = duplicate_file.stat().st_size
                            duplicate_file.unlink()
                            removed_files.append(str(duplicate_file.relative_to(REPO_ROOT)))
                            self.consolidation_stats["duplicates_removed"] += 1
                            self.consolidation_stats["bytes_freed"] += size
                            self.logger.info(f"  ✅ Removed duplicate: {duplicate_file.relative_to(REPO_ROOT)}")
                            self.logger.info(f"    Kept: {keep_file.relative_to(REPO_ROOT)}")
                        except Exception as e:
                            error_msg = f"Failed to remove {duplicate_file}: {e}"
                            self.consolidation_stats["errors"].append(error_msg)
                            self.logger.error(f"  ❌ {error_msg}")
                    else:
                        self.consolidation_stats["protected_files"] += 1
                        self.logger.info(f"  🛡️ Protected: {duplicate_file.relative_to(REPO_ROOT)}")
        
        return removed_files
    
    def organize_reports_by_date(self) -> List[str]:
        """Organize reports into date-based directories."""
        self.logger.info("📁 Organizing reports by date...")
        organized_files = []
        
        # Create reports archive directory
        reports_archive = REPO_ROOT / "reports" / "archive"
        reports_archive.mkdir(parents=True, exist_ok=True)
        
        # Find timestamped reports
        timestamp_patterns = [
            "*_20[0-9][0-9][0-1][0-9][0-3][0-9]_*.md",
            "*_20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]*.md"
        ]
        
        for pattern in timestamp_patterns:
            for report_file in REPO_ROOT.rglob(pattern):
                if report_file.is_file() and not self._is_protected_file(report_file):
                    # Extract date from filename
                    filename = report_file.name
                    date_parts = []
                    
                    # Try to extract date
                    import re
                    date_match = re.search(r'20(\d{2})(\d{2})(\d{2})', filename)
                    if not date_match:
                        date_match = re.search(r'20(\d{2})-(\d{2})-(\d{2})', filename)
                    
                    if date_match:
                        year = "20" + date_match.group(1)
                        month = date_match.group(2)
                        day = date_match.group(3)
                        
                        # Create date directory
                        date_dir = reports_archive / f"{year}-{month}"
                        date_dir.mkdir(exist_ok=True)
                        
                        # Move file if not already in archive
                        if "archive" not in str(report_file):
                            try:
                                new_path = date_dir / report_file.name
                                if not new_path.exists():
                                    shutil.move(str(report_file), str(new_path))
                                    organized_files.append(f"{report_file.relative_to(REPO_ROOT)} -> {new_path.relative_to(REPO_ROOT)}")
                                    self.consolidation_stats["reports_consolidated"] += 1
                                    self.logger.info(f"  ✅ Moved: {report_file.relative_to(REPO_ROOT)} -> {new_path.relative_to(REPO_ROOT)}")
                            except Exception as e:
                                error_msg = f"Failed to move {report_file}: {e}"
                                self.consolidation_stats["errors"].append(error_msg)
                                self.logger.error(f"  ❌ {error_msg}")
        
        return organized_files
    
    def create_documentation_index(self) -> str:
        """Create a consolidated documentation index."""
        self.logger.info("📚 Creating documentation index...")
        
        index_content = f"""# ACGS Documentation Index
<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Core Documentation

"""
        
        # Core docs
        core_docs = [
            ("README.md", "Main project documentation"),
            ("CLAUDE.md", "Claude agent configuration and guidelines"),
            ("AGENTS.md", "Multi-agent coordination framework"),
            ("GEMINI.md", "Gemini agent integration"),
            ("CONTRIBUTING.md", "Contribution guidelines"),
            ("CHANGELOG.md", "Project changelog")
        ]
        
        for doc_file, description in core_docs:
            if (REPO_ROOT / doc_file).exists():
                index_content += f"- [{doc_file}](./{doc_file}) - {description}\n"
        
        index_content += "\n## Service Documentation\n\n"
        
        # Service docs
        services_dir = REPO_ROOT / "services"
        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir():
                    readme_path = service_dir / "README.md"
                    if readme_path.exists():
                        rel_path = readme_path.relative_to(REPO_ROOT)
                        index_content += f"- [{service_dir.name}](./{rel_path}) - {service_dir.name} service\n"
        
        index_content += "\n## Infrastructure Documentation\n\n"
        
        # Infrastructure docs
        infra_dir = REPO_ROOT / "infrastructure"
        if infra_dir.exists():
            for infra_file in infra_dir.rglob("*.md"):
                if infra_file.name != "README.md":
                    rel_path = infra_file.relative_to(REPO_ROOT)
                    index_content += f"- [{infra_file.stem}](./{rel_path})\n"
        
        index_content += f"\n## Reports Archive\n\n"
        index_content += f"Historical reports are organized in [reports/archive](./reports/archive/)\n"
        
        # Write index file
        index_path = REPO_ROOT / "docs" / "DOCUMENTATION_INDEX.md"
        index_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(index_path, 'w') as f:
                f.write(index_content)
            self.logger.info(f"  ✅ Created documentation index: {index_path.relative_to(REPO_ROOT)}")
            return str(index_path.relative_to(REPO_ROOT))
        except Exception as e:
            error_msg = f"Failed to create documentation index: {e}"
            self.consolidation_stats["errors"].append(error_msg)
            self.logger.error(f"  ❌ {error_msg}")
            return ""
    
    def validate_constitutional_compliance(self) -> bool:
        """Ensure constitutional compliance files are preserved."""
        self.logger.info("🔍 Validating constitutional compliance preservation...")
        
        critical_files = [
            "CLAUDE.md",
            "AGENTS.md",
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
    
    def run_consolidation(self) -> Dict:
        """Run complete documentation consolidation."""
        self.logger.info("🧹 Starting ACGS Documentation Consolidation...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        # Run all consolidation operations
        self.consolidate_duplicate_reports()
        self.organize_reports_by_date()
        self.create_documentation_index()
        
        # Validate constitutional compliance
        if not self.validate_constitutional_compliance():
            self.logger.error("❌ Constitutional compliance validation failed!")
            return {"error": "Constitutional compliance validation failed"}
        
        # Format bytes freed
        bytes_freed = self.consolidation_stats["bytes_freed"]
        if bytes_freed > 1024 * 1024:
            size_str = f"{bytes_freed / (1024 * 1024):.1f} MB"
        elif bytes_freed > 1024:
            size_str = f"{bytes_freed / 1024:.1f} KB"
        else:
            size_str = f"{bytes_freed} bytes"
        
        self.logger.info("📊 Consolidation Summary:")
        self.logger.info(f"  Duplicates removed: {self.consolidation_stats['duplicates_removed']}")
        self.logger.info(f"  Reports organized: {self.consolidation_stats['reports_consolidated']}")
        self.logger.info(f"  Protected files: {self.consolidation_stats['protected_files']}")
        self.logger.info(f"  Space freed: {size_str}")
        self.logger.info(f"  Errors: {len(self.consolidation_stats['errors'])}")
        
        if self.consolidation_stats["errors"]:
            self.logger.warning("⚠️ Errors encountered:")
            for error in self.consolidation_stats["errors"]:
                self.logger.warning(f"  - {error}")
        
        return self.consolidation_stats

def main():
    """Main consolidation function."""
    print("🧹 ACGS Documentation and Report Consolidation")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()
    
    consolidator = ACGSDocumentationConsolidation()
    results = consolidator.run_consolidation()
    
    if "error" not in results:
        print("\n✅ Documentation consolidation completed!")
    else:
        print(f"\n❌ Consolidation failed: {results['error']}")
    
    return results

if __name__ == "__main__":
    main()
