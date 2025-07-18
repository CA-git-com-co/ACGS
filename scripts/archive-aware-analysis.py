#!/usr/bin/env python3
"""
ACGS-2 Archive-Aware Configuration Analysis
Constitutional Hash: cdd01ef066bc6cf2

Enhanced configuration analysis that properly excludes archived content
and focuses only on active, current ACGS-2 configurations.
"""

import os
import json
import fnmatch
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class ArchiveAwareAnalyzer:
    """Archive-aware configuration analyzer for ACGS-2."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Comprehensive archive and backup exclusion patterns
        self.archive_patterns = [
            # Direct archive directories
            "archive/", "archived/", "backup/", "backups/",
            "old/", "legacy/", "deprecated/", "obsolete/",
            
            # Archive suffixed directories
            "*_archive/", "*_archived/", "*_backup/", "*_backups/",
            "*_old/", "*_legacy/", "*_deprecated/", "*_obsolete/",
            
            # Archive prefixed directories
            "archive_*/", "archived_*/", "backup_*/", "backups_*/",
            "old_*/", "legacy_*/", "deprecated_*/", "obsolete_*/",
            
            # Common backup patterns
            "*.backup", "*.bak", "*.old", "*.orig", "*.save",
            "*~", "*.tmp", "*.temp",
            
            # Development and build exclusions
            "node_modules/", "__pycache__/", ".git/", ".svn/",
            "venv/", ".venv/", "env/", ".env/",
            "build/", "dist/", "target/", "out/",
            ".pytest_cache/", ".coverage/", ".tox/",
            "temp/", "tmp/", ".tmp/", "cache/", ".cache/",
            
            # IDE and editor files
            ".vscode/", ".idea/", "*.swp", "*.swo", ".DS_Store"
        ]
    
    def is_archived_path(self, file_path: Path) -> bool:
        """Check if a file path should be excluded as archived content."""
        file_path_str = str(file_path).lower()
        
        for pattern in self.archive_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if f"/{pattern}" in f"/{file_path_str}/" or file_path_str.startswith(pattern):
                    return True
            elif '*' in pattern:
                # Wildcard pattern
                if fnmatch.fnmatch(file_path_str, pattern.lower()):
                    return True
                # Also check individual path components
                for part in file_path.parts:
                    if fnmatch.fnmatch(part.lower(), pattern.lower()):
                        return True
            else:
                # Simple substring pattern
                if pattern.lower() in file_path_str:
                    return True
        
        return False
    
    def scan_active_configurations(self) -> Dict[str, List[str]]:
        """Scan only active (non-archived) configuration files."""
        print(f"🔍 Scanning active configurations from {self.root_path}")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        print(f"🚫 Excluding archived content with {len(self.archive_patterns)} patterns")
        
        config_files = defaultdict(list)
        total_scanned = 0
        excluded_count = 0
        
        # Configuration file extensions
        config_extensions = ['.yml', '.yaml', '.json', '.toml', '.ini', '.conf', '.cfg', '.env']
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in config_extensions:
                total_scanned += 1
                
                # Check if file should be excluded
                if self.is_archived_path(file_path):
                    excluded_count += 1
                    continue
                
                relative_path = str(file_path.relative_to(self.root_path))
                category = self._categorize_config_file(relative_path)
                config_files[category].append(relative_path)
        
        print(f"📊 Scanned {total_scanned} files, excluded {excluded_count} archived files")
        print(f"📁 Found {sum(len(files) for files in config_files.values())} active configuration files")
        
        return dict(config_files)
    
    def _categorize_config_file(self, file_path: str) -> str:
        """Categorize a configuration file based on its path and name."""
        file_path_lower = file_path.lower()
        
        # Configuration categories with patterns
        categories = {
            'docker': ['docker-compose', 'dockerfile', 'docker/'],
            'kubernetes': ['k8s/', 'kubernetes/', '*.k8s.', 'kustomization'],
            'monitoring': ['prometheus', 'grafana', 'monitoring/', 'metrics/', 'alerts/'],
            'database': ['postgres', 'redis', 'db/', 'database/'],
            'services': ['service', 'config/', 'settings/', 'app/'],
            'environment': ['.env', 'environment', 'env/'],
            'security': ['auth', 'security/', 'ssl/', 'cert/', 'tls/'],
            'networking': ['network', 'proxy/', 'nginx/', 'ingress/'],
            'testing': ['test', 'pytest', 'coverage'],
            'ci_cd': ['.github/', 'pipeline', 'deploy', 'ci/', 'cd/'],
            'infrastructure': ['infra', 'terraform/', 'ansible/', 'helm/']
        }
        
        # Check each category
        for category, patterns in categories.items():
            for pattern in patterns:
                if pattern in file_path_lower:
                    return category
        
        return 'miscellaneous'
    
    def analyze_constitutional_compliance(self) -> Dict[str, any]:
        """Analyze constitutional compliance of active configurations."""
        config_files = self.scan_active_configurations()
        
        compliance_analysis = {
            'constitutional_hash': self.constitutional_hash,
            'total_active_files': sum(len(files) for files in config_files.values()),
            'categories': {},
            'compliance_summary': {
                'files_with_hash': 0,
                'files_without_hash': 0,
                'compliance_rate': 0.0
            }
        }
        
        total_files = 0
        compliant_files = 0
        
        for category, files in config_files.items():
            category_analysis = {
                'file_count': len(files),
                'compliant_files': 0,
                'non_compliant_files': [],
                'sample_files': files[:5]  # Show first 5 files as samples
            }
            
            for file_path in files:
                total_files += 1
                full_path = self.root_path / file_path
                
                try:
                    if full_path.exists():
                        content = full_path.read_text(encoding='utf-8', errors='ignore')
                        if self.constitutional_hash in content:
                            compliant_files += 1
                            category_analysis['compliant_files'] += 1
                        else:
                            category_analysis['non_compliant_files'].append(file_path)
                except Exception as e:
                    category_analysis['non_compliant_files'].append(f"{file_path} (error: {str(e)})")
            
            compliance_analysis['categories'][category] = category_analysis
        
        # Calculate overall compliance rate
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        compliance_analysis['compliance_summary'] = {
            'files_with_hash': compliant_files,
            'files_without_hash': total_files - compliant_files,
            'compliance_rate': round(compliance_rate, 2)
        }
        
        return compliance_analysis
    
    def generate_simplification_recommendations(self) -> Dict[str, any]:
        """Generate recommendations for operational simplification."""
        config_files = self.scan_active_configurations()
        compliance_analysis = self.analyze_constitutional_compliance()
        
        recommendations = {
            'constitutional_hash': self.constitutional_hash,
            'analysis_timestamp': '2025-01-18T00:00:00Z',
            'current_state': {
                'total_active_configs': sum(len(files) for files in config_files.values()),
                'categories': len(config_files),
                'compliance_rate': compliance_analysis['compliance_summary']['compliance_rate']
            },
            'simplification_opportunities': [],
            'priority_actions': [],
            'archive_exclusions': {
                'patterns_used': len(self.archive_patterns),
                'files_excluded': 'See scan output for count'
            }
        }
        
        # Analyze each category for simplification opportunities
        for category, files in config_files.items():
            file_count = len(files)
            
            if file_count > 10:
                recommendations['simplification_opportunities'].append({
                    'category': category,
                    'current_files': file_count,
                    'recommendation': 'HIGH - Consolidate multiple files into standardized templates',
                    'potential_reduction': f"{max(1, file_count // 5)} files (80% reduction)"
                })
            elif file_count > 5:
                recommendations['simplification_opportunities'].append({
                    'category': category,
                    'current_files': file_count,
                    'recommendation': 'MEDIUM - Standardize and potentially consolidate',
                    'potential_reduction': f"{max(1, file_count // 3)} files (60% reduction)"
                })
        
        # Priority actions based on compliance and complexity
        if compliance_analysis['compliance_summary']['compliance_rate'] < 95:
            recommendations['priority_actions'].append({
                'action': 'Constitutional Compliance Enhancement',
                'description': 'Add constitutional hash to all active configuration files',
                'impact': 'Critical for governance compliance'
            })
        
        high_complexity_categories = [cat for cat, files in config_files.items() if len(files) > 10]
        if high_complexity_categories:
            recommendations['priority_actions'].append({
                'action': 'Configuration Consolidation',
                'description': f'Consolidate configurations in: {", ".join(high_complexity_categories)}',
                'impact': 'Significant operational simplification'
            })
        
        return recommendations

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Archive-Aware Configuration Analysis")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    print("🎯 Focus: Active configurations only (excluding archives)")
    
    analyzer = ArchiveAwareAnalyzer()
    
    # Perform analysis
    compliance_analysis = analyzer.analyze_constitutional_compliance()
    recommendations = analyzer.generate_simplification_recommendations()
    
    # Save results
    with open("active-config-analysis.json", 'w') as f:
        json.dump({
            'compliance_analysis': compliance_analysis,
            'recommendations': recommendations
        }, f, indent=2)
    
    # Print summary
    print(f"\n✅ Analysis Complete!")
    print(f"📊 Active Configuration Files: {compliance_analysis['total_active_files']}")
    print(f"📈 Constitutional Compliance: {compliance_analysis['compliance_summary']['compliance_rate']}%")
    print(f"📋 Report saved to: active-config-analysis.json")
    
    return 0

if __name__ == "__main__":
    main()
