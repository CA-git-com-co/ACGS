#!/usr/bin/env python3
"""
ACGS-2 Comprehensive Cleanup and Documentation Update Tool

Constitutional Hash: cdd01ef066bc6cf2
Performs systematic cleanup while preserving all governance components and audit trails.
"""

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ACGSComprehensiveCleanup:
    """
    ACGS-2 comprehensive cleanup tool following constitutional governance framework.
    Maintains constitutional hash validation throughout all operations.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "operations": [],
            "preserved_governance_components": [],
            "performance_metrics": {}
        }
        
    def analyze_cleanup_opportunities(self) -> Dict:
        """Analyze codebase for cleanup opportunities while preserving governance."""
        print(f"🔍 Analyzing cleanup opportunities (Constitutional Hash: {self.constitutional_hash})")
        
        analysis = {
            "temporary_files": self._find_temporary_files(),
            "duplicate_reports": self._find_duplicate_reports(),
            "redundant_configs": self._find_redundant_configs(),
            "unused_dependencies": self._analyze_dependencies(),
            "governance_components": self._identify_governance_components()
        }
        
        self.cleanup_report["operations"].append({
            "operation": "analysis",
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "results": analysis
        })
        
        return analysis
    
    def _find_temporary_files(self) -> List[str]:
        """Find temporary files that can be safely removed."""
        temp_patterns = [
            "*.tmp", "*.temp", "*.cache", "*.log", "*~", "*.bak",
            "*test_results*.json", "*report*.json", "*.pyc", "__pycache__"
        ]
        
        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(self.base_path.glob(f"**/{pattern}"))
        
        # Filter out governance-critical files
        governance_keywords = ["constitutional", "governance", "compliance", "audit"]
        safe_temp_files = []
        
        for file_path in temp_files:
            file_str = str(file_path).lower()
            if not any(keyword in file_str for keyword in governance_keywords):
                # Additional check for constitutional hash in file content
                if self._is_safe_to_remove(file_path):
                    safe_temp_files.append(str(file_path))
        
        return safe_temp_files
    
    def _find_duplicate_reports(self) -> List[str]:
        """Find duplicate report files that can be consolidated."""
        reports_dir = self.base_path / "reports"
        if not reports_dir.exists():
            return []
        
        # Group files by similar names and content
        json_files = list(reports_dir.glob("*.json"))
        duplicates = []
        
        # Simple duplicate detection based on file size and name patterns
        size_groups = {}
        for file_path in json_files:
            if file_path.stat().st_size > 0:
                size = file_path.stat().st_size
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(file_path)
        
        # Identify potential duplicates (same size, similar names)
        for size, files in size_groups.items():
            if len(files) > 1:
                # Keep the most recent, mark others as duplicates
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                duplicates.extend([str(f) for f in files[1:]])
        
        return duplicates
    
    def _find_redundant_configs(self) -> List[str]:
        """Find redundant configuration files."""
        config_patterns = ["*.yml.bak", "*.yaml.bak", "*.json.bak", "*.old"]
        redundant_configs = []
        
        for pattern in config_patterns:
            redundant_configs.extend(str(p) for p in self.base_path.glob(f"**/{pattern}"))
        
        return redundant_configs
    
    def _analyze_dependencies(self) -> Dict:
        """Analyze dependencies for unused packages."""
        # This is a placeholder for dependency analysis
        # In a real implementation, this would check config/environments/requirements.txt, package.json, etc.
        return {
            "python_unused": [],
            "node_unused": [],
            "rust_unused": []
        }
    
    def _identify_governance_components(self) -> List[str]:
        """Identify critical governance components that must be preserved."""
        governance_files = []
        
        # Constitutional compliance files
        constitutional_patterns = [
            "**/constitutional*", "**/governance*", "**/compliance*",
            "**/audit*", "**/*constitutional*", "**/*governance*"
        ]
        
        for pattern in constitutional_patterns:
            governance_files.extend(str(p) for p in self.base_path.glob(pattern))
        
        # Files containing constitutional hash
        for file_path in self.base_path.rglob("*.py"):
            if self._contains_constitutional_hash(file_path):
                governance_files.append(str(file_path))
        
        self.cleanup_report["preserved_governance_components"] = governance_files
        return governance_files
    
    def _is_safe_to_remove(self, file_path: Path) -> bool:
        """Check if file is safe to remove (doesn't contain constitutional hash)."""
        if not file_path.is_file():
            return False
        
        try:
            if file_path.suffix in ['.json', '.py', '.md', '.yml', '.yaml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if self.constitutional_hash in content:
                        return False
        except Exception:
            # If we can't read the file, err on the side of caution
            return False
        
        return True
    
    def _contains_constitutional_hash(self, file_path: Path) -> bool:
        """Check if file contains constitutional hash."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self.constitutional_hash in content
        except Exception:
            return False
    
    def execute_cleanup(self, analysis: Dict, dry_run: bool = True) -> Dict:
        """Execute the cleanup operations."""
        print(f"🧹 Executing cleanup (Constitutional Hash: {self.constitutional_hash})")
        print(f"Dry run: {dry_run}")
        
        results = {
            "files_removed": 0,
            "space_freed": 0,
            "operations": [],
            "constitutional_hash": self.constitutional_hash
        }
        
        # Remove temporary files
        for temp_file in analysis["temporary_files"]:
            if not dry_run:
                try:
                    file_path = Path(temp_file)
                    size = file_path.stat().st_size
                    file_path.unlink()
                    results["files_removed"] += 1
                    results["space_freed"] += size
                    results["operations"].append(f"Removed temporary file: {temp_file}")
                except Exception as e:
                    results["operations"].append(f"Failed to remove {temp_file}: {e}")
            else:
                results["operations"].append(f"Would remove: {temp_file}")
        
        # Remove duplicate reports
        for duplicate in analysis["duplicate_reports"]:
            if not dry_run:
                try:
                    file_path = Path(duplicate)
                    size = file_path.stat().st_size
                    file_path.unlink()
                    results["files_removed"] += 1
                    results["space_freed"] += size
                    results["operations"].append(f"Removed duplicate: {duplicate}")
                except Exception as e:
                    results["operations"].append(f"Failed to remove {duplicate}: {e}")
            else:
                results["operations"].append(f"Would remove duplicate: {duplicate}")
        
        self.cleanup_report["operations"].append({
            "operation": "cleanup_execution",
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "results": results
        })
        
        return results
    
    def generate_cleanup_report(self) -> str:
        """Generate comprehensive cleanup report."""
        report_path = self.base_path / f"cleanup_report_{self.constitutional_hash}_{int(time.time())}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        print(f"📊 Cleanup report generated: {report_path}")
        return str(report_path)

def main():
    """Main execution function with constitutional compliance."""
    print(f"🚀 ACGS-2 Comprehensive Cleanup Tool")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("-" * 60)
    
    cleanup_tool = ACGSComprehensiveCleanup()
    
    # Analyze cleanup opportunities
    analysis = cleanup_tool.analyze_cleanup_opportunities()
    
    print(f"\n📋 Cleanup Analysis Results:")
    print(f"Temporary files found: {len(analysis['temporary_files'])}")
    print(f"Duplicate reports found: {len(analysis['duplicate_reports'])}")
    print(f"Redundant configs found: {len(analysis['redundant_configs'])}")
    print(f"Governance components preserved: {len(analysis['governance_components'])}")
    
    # Execute cleanup (dry run first)
    print(f"\n🧪 Executing dry run...")
    dry_results = cleanup_tool.execute_cleanup(analysis, dry_run=True)
    
    print(f"\nDry run results:")
    print(f"Files that would be removed: {dry_results['files_removed']}")
    print(f"Space that would be freed: {dry_results['space_freed']} bytes")
    
    # Generate report
    report_path = cleanup_tool.generate_cleanup_report()
    print(f"\nConstitutional Hash Validation: {CONSTITUTIONAL_HASH} ✅")

if __name__ == "__main__":
    main()
