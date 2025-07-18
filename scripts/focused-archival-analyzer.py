#!/usr/bin/env python3
"""
ACGS-2 Focused Archival Analyzer
Constitutional Hash: cdd01ef066bc6cf2

Focused analysis of specific outdated files and directories for archival.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class FocusedArchivalAnalyzer:
    """Focused archival analyzer for ACGS-2."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Known outdated patterns to archive
        self.outdated_patterns = [
            # Old Docker Compose files (superseded by unified configs)
            "**/docker-compose.yml",
            "**/docker-compose.yaml", 
            "**/docker-compose.*.yml",
            "**/docker-compose.*.yaml",
            
            # Old environment files (superseded by standardized configs)
            "**/.env.*",
            "**/env.*",
            
            # Deprecated documentation
            "**/README.old.*",
            "**/README.backup.*",
            "**/DEPRECATED.*",
            "**/OBSOLETE.*",
            
            # Old configuration files
            "**/config.old.*",
            "**/config.backup.*",
            "**/settings.old.*",
            
            # Test artifacts and temporary files
            "**/*.tmp",
            "**/*.temp",
            "**/*.bak",
            "**/*.backup",
            "**/*~",
            
            # Old scripts
            "**/old_*",
            "**/deprecated_*",
            "**/backup_*"
        ]
        
        # Protected files (never archive)
        self.protected_files = [
            "config/docker/docker-compose.base.yml",
            "config/docker/docker-compose.development.yml", 
            "config/docker/docker-compose.staging.yml",
            "config/docker/docker-compose.production.yml",
            "config/environments/development.env",
            "config/environments/staging.env",
            "config/environments/production-standardized.env",
            "scripts/deploy-acgs.sh",
            "scripts/constitutional-compliance-validator.py",
            "scripts/archive-aware-analysis.py",
            "scripts/validate-simplified-configs.sh",
            "docs/ACGS-2-UNIFIED-DOCUMENTATION.md"
        ]
        
        # Existing archive directories to exclude
        self.archive_exclusions = [
            "archive/", "archived/", "backup/", "backups/",
            "old/", "legacy/", "deprecated/", "obsolete/"
        ]
    
    def is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected from archival."""
        relative_path = str(file_path.relative_to(self.root_path))
        return any(protected in relative_path for protected in self.protected_files)
    
    def is_in_archive(self, file_path: Path) -> bool:
        """Check if file is already in an archive directory."""
        path_str = str(file_path).lower()
        return any(archive in path_str for archive in self.archive_exclusions)
    
    def has_constitutional_hash(self, file_path: Path) -> bool:
        """Check if file contains constitutional hash."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self.constitutional_hash in content
        except Exception:
            return False
    
    def analyze_outdated_files(self) -> List[Dict[str, Any]]:
        """Analyze files matching outdated patterns."""
        print("🔍 Analyzing outdated files for archival...")
        
        candidates = []
        
        for pattern in self.outdated_patterns:
            print(f"  Checking pattern: {pattern}")
            
            for file_path in self.root_path.glob(pattern):
                if (file_path.is_file() and 
                    not self.is_in_archive(file_path) and
                    not self.is_protected_file(file_path)):
                    
                    # Additional safety checks
                    has_const_hash = self.has_constitutional_hash(file_path)
                    
                    # Skip files with constitutional hash unless explicitly deprecated
                    if has_const_hash and 'deprecated' not in str(file_path).lower():
                        continue
                    
                    relative_path = str(file_path.relative_to(self.root_path))
                    
                    candidate = {
                        'file_path': relative_path,
                        'absolute_path': str(file_path),
                        'size_bytes': file_path.stat().st_size,
                        'has_constitutional_hash': has_const_hash,
                        'pattern_matched': pattern,
                        'archival_reason': self._determine_reason(file_path, pattern),
                        'category': self._determine_category(file_path),
                        'subcategory': self._determine_subcategory(file_path)
                    }
                    
                    candidates.append(candidate)
        
        print(f"📊 Found {len(candidates)} archival candidates")
        return candidates
    
    def _determine_reason(self, file_path: Path, pattern: str) -> str:
        """Determine archival reason based on file and pattern."""
        path_str = str(file_path).lower()
        
        if 'docker-compose' in pattern:
            return "Superseded by unified Docker Compose configurations"
        elif '.env' in pattern:
            return "Superseded by standardized environment configurations"
        elif any(word in path_str for word in ['deprecated', 'obsolete', 'old']):
            return "Explicitly marked as deprecated/obsolete"
        elif any(ext in pattern for ext in ['.tmp', '.temp', '.bak', '.backup']):
            return "Temporary or backup file"
        else:
            return "Matches outdated file pattern"
    
    def _determine_category(self, file_path: Path) -> str:
        """Determine archival category."""
        path_str = str(file_path).lower()
        suffix = file_path.suffix.lower()
        
        if suffix in ['.md', '.rst', '.txt', '.adoc']:
            return 'documentation'
        elif suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs']:
            return 'code'
        elif suffix in ['.yml', '.yaml', '.json', '.toml', '.ini', '.conf', '.cfg', '.env']:
            return 'configurations'
        else:
            return 'miscellaneous'
    
    def _determine_subcategory(self, file_path: Path) -> str:
        """Determine archival subcategory."""
        path_str = str(file_path).lower()
        
        if 'docker' in path_str:
            return 'docker-configs'
        elif 'env' in path_str or 'environment' in path_str:
            return 'environment-configs'
        elif 'readme' in path_str:
            return 'readme-files'
        elif 'test' in path_str:
            return 'test-files'
        elif 'script' in path_str:
            return 'scripts'
        elif any(word in path_str for word in ['.tmp', '.temp', '.bak', '.backup']):
            return 'temporary-files'
        else:
            return 'general'
    
    def generate_focused_report(self) -> Dict[str, Any]:
        """Generate focused archival report."""
        print("📊 Generating focused archival report...")
        
        candidates = self.analyze_outdated_files()
        
        # Group by category
        by_category = {'documentation': [], 'code': [], 'configurations': [], 'miscellaneous': []}
        for candidate in candidates:
            category = candidate['category']
            if category in by_category:
                by_category[category].append(candidate)
            else:
                by_category['miscellaneous'].append(candidate)
        
        report = {
            'constitutional_hash': self.constitutional_hash,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'focused_archival',
            'summary': {
                'total_candidates': len(candidates),
                'documentation_candidates': len(by_category['documentation']),
                'code_candidates': len(by_category['code']),
                'configuration_candidates': len(by_category['configurations']),
                'miscellaneous_candidates': len(by_category['miscellaneous']),
                'total_size_bytes': sum(c['size_bytes'] for c in candidates)
            },
            'candidates_by_category': by_category,
            'patterns_analyzed': self.outdated_patterns,
            'protected_files': self.protected_files,
            'constitutional_compliance': {
                'hash': self.constitutional_hash,
                'files_with_hash': sum(1 for c in candidates if c['has_constitutional_hash']),
                'validation_required': True
            }
        }
        
        return report

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Focused Archival Analyzer")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    
    analyzer = FocusedArchivalAnalyzer()
    report = analyzer.generate_focused_report()
    
    # Save report
    output_file = "focused-archival-analysis.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report['summary']
    print(f"\n✅ Focused Analysis Complete!")
    print(f"📊 Total Candidates: {summary['total_candidates']}")
    print(f"📋 Documentation: {summary['documentation_candidates']}")
    print(f"💻 Code: {summary['code_candidates']}")
    print(f"⚙️ Configurations: {summary['configuration_candidates']}")
    print(f"📦 Miscellaneous: {summary['miscellaneous_candidates']}")
    print(f"💾 Total Size: {summary['total_size_bytes'] / 1024:.2f} KB")
    print(f"🏛️ Files with Constitutional Hash: {report['constitutional_compliance']['files_with_hash']}")
    print(f"📋 Report saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    main()
