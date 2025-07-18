#!/usr/bin/env python3
"""
ACGS-2 Comprehensive Codebase Archival Analyzer
Constitutional Hash: cdd01ef066bc6cf2

Analyzes the codebase to identify outdated documents, dead code, and legacy configurations
for systematic archival while maintaining constitutional compliance.
"""

import os
import json
import git
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import re
import ast

class CodebaseArchivalAnalyzer:
    """Comprehensive codebase archival analyzer for ACGS-2."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Initialize git repository
        try:
            self.repo = git.Repo(self.root_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
            print("⚠️  Warning: Not a git repository, using filesystem timestamps")
        
        # Archival criteria (days)
        self.archival_age_threshold = 90
        
        # Existing archive patterns to exclude from analysis
        self.existing_archive_patterns = [
            "archive/", "archived/", "backup/", "backups/",
            "old/", "legacy/", "deprecated/", "obsolete/",
            "*_archive/", "*_archived/", "*_backup/", "*_backups/",
            "node_modules/", "__pycache__/", ".git/", "venv/", ".venv/",
            "build/", "dist/", "target/", "out/", ".pytest_cache/"
        ]
        
        # Protected patterns (never archive)
        self.protected_patterns = [
            "config/docker/docker-compose.base.yml",
            "config/docker/docker-compose.development.yml",
            "config/docker/docker-compose.staging.yml",
            "config/docker/docker-compose.production.yml",
            "config/environments/",
            "config/services/service-architecture-mapping.yml",
            "config/monitoring/unified-observability-stack.yml",
            "infrastructure/terraform/",
            "infrastructure/istio/",
            "infrastructure/autoscaling/",
            "infrastructure/multi-region/",
            "infrastructure/monitoring/",
            "infrastructure/secret-management/",
            ".github/workflows/",
            "scripts/deploy-acgs.sh",
            "scripts/constitutional-compliance-validator.py",
            "scripts/archive-aware-analysis.py",
            "scripts/validate-simplified-configs.sh",
            "docs/ACGS-2-UNIFIED-DOCUMENTATION.md",
            "ACGS-2-OPERATIONAL-SIMPLIFICATION-SUMMARY.md",
            "ACGS-2-NEXT-PHASE-IMPLEMENTATION-COMPLETE.md"
        ]
        
        self.archival_candidates = {
            'documentation': [],
            'code': [],
            'configurations': []
        }
        
        self.active_references = set()
        
    def is_existing_archive(self, file_path: Path) -> bool:
        """Check if file is already in an archive directory."""
        file_path_str = str(file_path).lower()
        return any(pattern.lower() in file_path_str for pattern in self.existing_archive_patterns)
    
    def is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected from archival."""
        file_path_str = str(file_path.relative_to(self.root_path))
        return any(pattern in file_path_str for pattern in self.protected_patterns)
    
    def has_constitutional_hash(self, file_path: Path) -> bool:
        """Check if file contains constitutional hash."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self.constitutional_hash in content
        except Exception:
            return False
    
    def get_file_last_modified(self, file_path: Path) -> datetime:
        """Get last modification time from git or filesystem."""
        if self.repo:
            try:
                # Get last commit that modified this file
                commits = list(self.repo.iter_commits(paths=str(file_path.relative_to(self.root_path)), max_count=1))
                if commits:
                    return datetime.fromtimestamp(commits[0].committed_date)
            except Exception:
                pass
        
        # Fallback to filesystem timestamp
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    
    def is_file_referenced(self, file_path: Path) -> bool:
        """Check if file is referenced in active codebase."""
        file_name = file_path.name
        relative_path = str(file_path.relative_to(self.root_path))
        
        # Check if already in active references cache
        if relative_path in self.active_references:
            return True
        
        # Search for references in active files
        search_patterns = [
            file_name,
            relative_path,
            relative_path.replace('/', '.'),  # Python import style
            relative_path.replace('/', '_'),  # Alternative naming
        ]
        
        for search_file in self.root_path.rglob('*'):
            if (search_file.is_file() and 
                not self.is_existing_archive(search_file) and
                search_file != file_path and
                search_file.suffix in ['.py', '.js', '.ts', '.yml', '.yaml', '.json', '.md', '.sh']):
                
                try:
                    content = search_file.read_text(encoding='utf-8', errors='ignore')
                    if any(pattern in content for pattern in search_patterns):
                        self.active_references.add(relative_path)
                        return True
                except Exception:
                    continue
        
        return False
    
    def analyze_documentation_files(self) -> List[Dict[str, Any]]:
        """Analyze documentation files for archival candidates."""
        print("📋 Analyzing documentation files...")
        
        doc_candidates = []
        cutoff_date = datetime.now() - timedelta(days=self.archival_age_threshold)
        
        # Documentation file patterns
        doc_patterns = ['*.md', '*.rst', '*.txt', '*.adoc']
        
        for pattern in doc_patterns:
            for file_path in self.root_path.rglob(pattern):
                if (file_path.is_file() and 
                    not self.is_existing_archive(file_path) and
                    not self.is_protected_file(file_path)):
                    
                    last_modified = self.get_file_last_modified(file_path)
                    has_const_hash = self.has_constitutional_hash(file_path)
                    is_referenced = self.is_file_referenced(file_path)
                    
                    # Archival criteria for documentation
                    should_archive = (
                        last_modified < cutoff_date and
                        not has_const_hash and
                        not is_referenced and
                        'deprecated' in str(file_path).lower() or
                        'obsolete' in str(file_path).lower() or
                        'old' in str(file_path).lower()
                    )
                    
                    if should_archive:
                        doc_candidates.append({
                            'file_path': str(file_path.relative_to(self.root_path)),
                            'absolute_path': str(file_path),
                            'last_modified': last_modified.isoformat(),
                            'size_bytes': file_path.stat().st_size,
                            'has_constitutional_hash': has_const_hash,
                            'is_referenced': is_referenced,
                            'archival_reason': self._determine_archival_reason(file_path, last_modified, has_const_hash, is_referenced),
                            'category': 'documentation',
                            'subcategory': self._categorize_documentation(file_path)
                        })
        
        print(f"📊 Found {len(doc_candidates)} documentation archival candidates")
        return doc_candidates
    
    def analyze_code_files(self) -> List[Dict[str, Any]]:
        """Analyze code files for archival candidates."""
        print("💻 Analyzing code files...")
        
        code_candidates = []
        cutoff_date = datetime.now() - timedelta(days=self.archival_age_threshold)
        
        # Code file patterns
        code_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h', '*.go', '*.rs', '*.rb']
        
        for pattern in code_patterns:
            for file_path in self.root_path.rglob(pattern):
                if (file_path.is_file() and 
                    not self.is_existing_archive(file_path) and
                    not self.is_protected_file(file_path)):
                    
                    last_modified = self.get_file_last_modified(file_path)
                    has_const_hash = self.has_constitutional_hash(file_path)
                    is_referenced = self.is_file_referenced(file_path)
                    has_tests = self._has_test_coverage(file_path)
                    
                    # Archival criteria for code
                    should_archive = (
                        last_modified < cutoff_date and
                        not has_const_hash and
                        not is_referenced and
                        not has_tests and
                        ('deprecated' in str(file_path).lower() or
                         'obsolete' in str(file_path).lower() or
                         'unused' in str(file_path).lower() or
                         'old' in str(file_path).lower())
                    )
                    
                    if should_archive:
                        code_candidates.append({
                            'file_path': str(file_path.relative_to(self.root_path)),
                            'absolute_path': str(file_path),
                            'last_modified': last_modified.isoformat(),
                            'size_bytes': file_path.stat().st_size,
                            'has_constitutional_hash': has_const_hash,
                            'is_referenced': is_referenced,
                            'has_test_coverage': has_tests,
                            'archival_reason': self._determine_archival_reason(file_path, last_modified, has_const_hash, is_referenced),
                            'category': 'code',
                            'subcategory': self._categorize_code(file_path)
                        })
        
        print(f"📊 Found {len(code_candidates)} code archival candidates")
        return code_candidates
    
    def analyze_configuration_files(self) -> List[Dict[str, Any]]:
        """Analyze configuration files for archival candidates."""
        print("⚙️ Analyzing configuration files...")
        
        config_candidates = []
        cutoff_date = datetime.now() - timedelta(days=self.archival_age_threshold)
        
        # Configuration file patterns
        config_patterns = ['*.yml', '*.yaml', '*.json', '*.toml', '*.ini', '*.conf', '*.cfg', '*.env']
        
        for pattern in config_patterns:
            for file_path in self.root_path.rglob(pattern):
                if (file_path.is_file() and 
                    not self.is_existing_archive(file_path) and
                    not self.is_protected_file(file_path)):
                    
                    last_modified = self.get_file_last_modified(file_path)
                    has_const_hash = self.has_constitutional_hash(file_path)
                    is_referenced = self.is_file_referenced(file_path)
                    is_superseded = self._is_superseded_config(file_path)
                    
                    # Archival criteria for configurations
                    should_archive = (
                        (last_modified < cutoff_date and not has_const_hash and not is_referenced) or
                        is_superseded or
                        ('deprecated' in str(file_path).lower() or
                         'obsolete' in str(file_path).lower() or
                         'old' in str(file_path).lower())
                    )
                    
                    if should_archive:
                        config_candidates.append({
                            'file_path': str(file_path.relative_to(self.root_path)),
                            'absolute_path': str(file_path),
                            'last_modified': last_modified.isoformat(),
                            'size_bytes': file_path.stat().st_size,
                            'has_constitutional_hash': has_const_hash,
                            'is_referenced': is_referenced,
                            'is_superseded': is_superseded,
                            'archival_reason': self._determine_archival_reason(file_path, last_modified, has_const_hash, is_referenced),
                            'category': 'configurations',
                            'subcategory': self._categorize_configuration(file_path)
                        })
        
        print(f"📊 Found {len(config_candidates)} configuration archival candidates")
        return config_candidates
    
    def _determine_archival_reason(self, file_path: Path, last_modified: datetime, has_const_hash: bool, is_referenced: bool) -> str:
        """Determine the reason for archival."""
        reasons = []
        
        cutoff_date = datetime.now() - timedelta(days=self.archival_age_threshold)
        if last_modified < cutoff_date:
            reasons.append(f"Not modified for >{self.archival_age_threshold} days")
        
        if not has_const_hash:
            reasons.append("No constitutional hash")
        
        if not is_referenced:
            reasons.append("No active references found")
        
        file_path_lower = str(file_path).lower()
        if 'deprecated' in file_path_lower:
            reasons.append("Marked as deprecated")
        if 'obsolete' in file_path_lower:
            reasons.append("Marked as obsolete")
        if 'old' in file_path_lower:
            reasons.append("Marked as old")
        
        return "; ".join(reasons) if reasons else "Manual review required"
    
    def _categorize_documentation(self, file_path: Path) -> str:
        """Categorize documentation files."""
        path_str = str(file_path).lower()
        
        if 'claude.md' in path_str:
            return 'claude-docs'
        elif 'readme' in path_str:
            return 'readme-files'
        elif 'api' in path_str:
            return 'api-docs'
        elif 'guide' in path_str or 'tutorial' in path_str:
            return 'guides'
        else:
            return 'general-docs'
    
    def _categorize_code(self, file_path: Path) -> str:
        """Categorize code files."""
        path_str = str(file_path).lower()
        
        if 'test' in path_str:
            return 'test-files'
        elif 'script' in path_str:
            return 'scripts'
        elif 'service' in path_str:
            return 'services'
        elif 'util' in path_str or 'helper' in path_str:
            return 'utilities'
        else:
            return 'application-code'
    
    def _categorize_configuration(self, file_path: Path) -> str:
        """Categorize configuration files."""
        path_str = str(file_path).lower()
        
        if 'docker' in path_str:
            return 'docker-configs'
        elif 'k8s' in path_str or 'kubernetes' in path_str:
            return 'kubernetes-configs'
        elif 'env' in path_str:
            return 'environment-configs'
        elif 'monitoring' in path_str:
            return 'monitoring-configs'
        else:
            return 'general-configs'
    
    def _has_test_coverage(self, file_path: Path) -> bool:
        """Check if code file has test coverage."""
        # Look for corresponding test files
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"test_{file_path.stem}.js",
            f"{file_path.stem}.test.js"
        ]
        
        for test_pattern in test_patterns:
            test_files = list(self.root_path.rglob(test_pattern))
            if test_files:
                return True
        
        return False
    
    def _is_superseded_config(self, file_path: Path) -> bool:
        """Check if configuration file has been superseded."""
        # Check if there's a newer version in the unified config structure
        relative_path = str(file_path.relative_to(self.root_path))
        
        # Check against our unified configuration structure
        unified_configs = [
            'config/docker/docker-compose.base.yml',
            'config/docker/docker-compose.development.yml',
            'config/docker/docker-compose.staging.yml',
            'config/docker/docker-compose.production.yml',
            'config/environments/',
            'config/services/service-architecture-mapping.yml',
            'config/monitoring/unified-observability-stack.yml'
        ]
        
        # If this is an old docker-compose file and we have unified ones
        if 'docker-compose' in relative_path and relative_path not in unified_configs:
            return True
        
        # If this is an old environment config and we have standardized ones
        if '.env' in relative_path and 'config/environments/' not in relative_path:
            return True
        
        return False
    
    def generate_archival_report(self) -> Dict[str, Any]:
        """Generate comprehensive archival analysis report."""
        print("📊 Generating archival analysis report...")
        
        # Analyze all categories
        doc_candidates = self.analyze_documentation_files()
        code_candidates = self.analyze_code_files()
        config_candidates = self.analyze_configuration_files()
        
        all_candidates = doc_candidates + code_candidates + config_candidates
        
        report = {
            'constitutional_hash': self.constitutional_hash,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'archival_criteria': {
                'age_threshold_days': self.archival_age_threshold,
                'requires_constitutional_hash': True,
                'requires_active_references': True,
                'excludes_existing_archives': True
            },
            'summary': {
                'total_candidates': len(all_candidates),
                'documentation_candidates': len(doc_candidates),
                'code_candidates': len(code_candidates),
                'configuration_candidates': len(config_candidates),
                'total_size_bytes': sum(candidate['size_bytes'] for candidate in all_candidates),
                'protected_files_count': len(self.protected_patterns)
            },
            'candidates_by_category': {
                'documentation': doc_candidates,
                'code': code_candidates,
                'configurations': config_candidates
            },
            'archival_statistics': self._generate_archival_statistics(all_candidates),
            'protected_patterns': self.protected_patterns,
            'constitutional_compliance': {
                'hash': self.constitutional_hash,
                'validation_required': True,
                'performance_targets_preserved': True
            }
        }
        
        return report
    
    def _generate_archival_statistics(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate archival statistics."""
        stats = {
            'by_reason': defaultdict(int),
            'by_subcategory': defaultdict(int),
            'by_age_range': defaultdict(int),
            'size_distribution': defaultdict(int)
        }
        
        for candidate in candidates:
            # Count by reason
            stats['by_reason'][candidate['archival_reason']] += 1
            
            # Count by subcategory
            stats['by_subcategory'][candidate['subcategory']] += 1
            
            # Count by age range
            last_modified = datetime.fromisoformat(candidate['last_modified'])
            days_old = (datetime.now() - last_modified).days
            
            if days_old < 90:
                age_range = '0-90 days'
            elif days_old < 180:
                age_range = '90-180 days'
            elif days_old < 365:
                age_range = '180-365 days'
            else:
                age_range = '>365 days'
            
            stats['by_age_range'][age_range] += 1
            
            # Count by size
            size_bytes = candidate['size_bytes']
            if size_bytes < 1024:
                size_range = '<1KB'
            elif size_bytes < 10240:
                size_range = '1-10KB'
            elif size_bytes < 102400:
                size_range = '10-100KB'
            else:
                size_range = '>100KB'
            
            stats['size_distribution'][size_range] += 1
        
        # Convert defaultdicts to regular dicts
        return {key: dict(value) for key, value in stats.items()}

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Comprehensive Codebase Archival Analyzer")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    print("🎯 Identifying archival candidates while preserving constitutional compliance")
    
    analyzer = CodebaseArchivalAnalyzer()
    report = analyzer.generate_archival_report()
    
    # Save report
    output_file = "codebase-archival-analysis.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report['summary']
    print(f"\n✅ Archival Analysis Complete!")
    print(f"📊 Total Archival Candidates: {summary['total_candidates']}")
    print(f"📋 Documentation: {summary['documentation_candidates']}")
    print(f"💻 Code: {summary['code_candidates']}")
    print(f"⚙️ Configurations: {summary['configuration_candidates']}")
    print(f"💾 Total Size: {summary['total_size_bytes'] / 1024 / 1024:.2f} MB")
    print(f"🛡️ Protected Files: {summary['protected_files_count']}")
    print(f"📋 Report saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    main()
