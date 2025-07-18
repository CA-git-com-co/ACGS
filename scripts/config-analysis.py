#!/usr/bin/env python3
"""
ACGS-2 Configuration Analysis Script
Constitutional Hash: cdd01ef066bc6cf2

Analyzes and categorizes configuration files for operational simplification.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
import configparser

class ConfigurationAnalyzer:
    """Analyzes ACGS-2 configuration files for consolidation opportunities."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_files = defaultdict(list)
        self.categories = {
            'docker': ['docker-compose*.yml', 'docker-compose*.yaml', 'Dockerfile*'],
            'monitoring': ['prometheus*.yml', 'grafana*.yml', '*monitoring*.yml', 'alerts*.yml'],
            'database': ['*postgres*.yml', '*redis*.yml', '*db*.yml', '*database*.yml'],
            'services': ['*service*.yml', '*config*.yml', '*settings*.yml'],
            'environment': ['*.env', '*environment*.yml', '*env*.yml'],
            'security': ['*auth*.yml', '*security*.yml', '*ssl*.yml', '*cert*.yml'],
            'networking': ['*network*.yml', '*proxy*.yml', '*nginx*.yml'],
            'testing': ['*test*.yml', '*pytest*.ini', '*coverage*.yml'],
            'ci_cd': ['.github/workflows/*.yml', '*pipeline*.yml', '*deploy*.yml'],
            'application': ['*app*.yml', '*main*.yml', '*core*.yml']
        }
        
    def scan_configurations(self) -> Dict[str, List[str]]:
        """Scan and categorize all configuration files."""
        print(f"🔍 Scanning configuration files from {self.root_path}")
        
        # File extensions to analyze
        extensions = ['.yml', '.yaml', '.json', '.toml', '.ini', '.conf', '.cfg', '.env']
        
        # Exclude patterns - comprehensive archive and backup exclusions
        exclude_patterns = [
            'archive/', 'archived/', 'backup/', 'backups/',
            '*_archive/', '*_archived/', '*_backup/', '*_backups/',
            'archive_*/', 'archived_*/', 'backup_*/', 'backups_*/',
            'old/', 'legacy/', 'deprecated/', 'obsolete/',
            'node_modules/', '__pycache__/', '.git/',
            'venv/', '.venv/', 'build/', 'dist/', '.pytest_cache/',
            'temp/', 'tmp/', '.tmp/', 'cache/', '.cache/'
        ]
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip excluded directories - enhanced pattern matching
                file_path_str = str(file_path).lower()
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern.endswith('/'):
                        # Directory pattern
                        if f"/{pattern}" in f"/{file_path_str}/" or file_path_str.startswith(pattern):
                            should_exclude = True
                            break
                    elif '*' in pattern:
                        # Wildcard pattern
                        import fnmatch
                        if fnmatch.fnmatch(file_path_str, pattern.lower()):
                            should_exclude = True
                            break
                    else:
                        # Simple substring pattern
                        if pattern.lower() in file_path_str:
                            should_exclude = True
                            break

                if should_exclude:
                    continue
                    
                relative_path = str(file_path.relative_to(self.root_path))
                category = self._categorize_file(relative_path)
                self.config_files[category].append(relative_path)
        
        return dict(self.config_files)
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize a configuration file based on its path and name."""
        file_path_lower = file_path.lower()
        
        # Check each category pattern
        for category, patterns in self.categories.items():
            for pattern in patterns:
                pattern_lower = pattern.lower().replace('*', '')
                if pattern_lower in file_path_lower:
                    return category
        
        # Default categorization based on location
        if 'docker' in file_path_lower:
            return 'docker'
        elif 'config' in file_path_lower:
            return 'services'
        elif 'test' in file_path_lower:
            return 'testing'
        elif '.github' in file_path_lower:
            return 'ci_cd'
        else:
            return 'miscellaneous'
    
    def analyze_consolidation_opportunities(self) -> Dict[str, Dict]:
        """Analyze consolidation opportunities for each category."""
        analysis = {}
        
        for category, files in self.config_files.items():
            if not files:
                continue
                
            analysis[category] = {
                'file_count': len(files),
                'consolidation_potential': self._assess_consolidation_potential(category, files),
                'recommended_structure': self._recommend_structure(category),
                'files': files[:10] if len(files) > 10 else files,  # Show first 10 files
                'total_files': len(files)
            }
        
        return analysis
    
    def _assess_consolidation_potential(self, category: str, files: List[str]) -> str:
        """Assess consolidation potential for a category."""
        file_count = len(files)
        
        if category == 'docker' and file_count > 10:
            return "HIGH - Multiple Docker Compose files can be unified"
        elif category == 'environment' and file_count > 5:
            return "HIGH - Environment configs can be standardized"
        elif category == 'monitoring' and file_count > 3:
            return "MEDIUM - Monitoring configs can be consolidated"
        elif category == 'services' and file_count > 20:
            return "HIGH - Service configs need standardization"
        elif file_count > 15:
            return "MEDIUM - Multiple files suggest consolidation opportunity"
        elif file_count > 5:
            return "LOW - Some consolidation possible"
        else:
            return "MINIMAL - Few files, limited consolidation needed"
    
    def _recommend_structure(self, category: str) -> Dict[str, str]:
        """Recommend consolidated structure for each category."""
        recommendations = {
            'docker': {
                'structure': 'config/docker/{environment}/docker-compose.yml',
                'environments': ['development', 'staging', 'production'],
                'pattern': 'Environment-specific with override files'
            },
            'environment': {
                'structure': 'config/environments/{environment}.env',
                'environments': ['development', 'staging', 'production'],
                'pattern': 'Single environment file per deployment stage'
            },
            'monitoring': {
                'structure': 'config/monitoring/{component}.yml',
                'components': ['prometheus', 'grafana', 'alertmanager'],
                'pattern': 'Unified monitoring stack configuration'
            },
            'services': {
                'structure': 'config/services/{domain}/{service}.yml',
                'domains': ['constitutional-ai', 'governance-synthesis', 'formal-verification'],
                'pattern': 'Domain-grouped service configurations'
            }
        }
        
        return recommendations.get(category, {
            'structure': f'config/{category}/consolidated.yml',
            'pattern': 'Single consolidated configuration file'
        })
    
    def generate_consolidation_plan(self) -> Dict[str, any]:
        """Generate a comprehensive consolidation plan."""
        analysis = self.analyze_consolidation_opportunities()
        
        plan = {
            'constitutional_hash': self.constitutional_hash,
            'analysis_summary': {
                'total_categories': len(analysis),
                'total_files': sum(cat['file_count'] for cat in analysis.values()),
                'high_priority_categories': [
                    cat for cat, data in analysis.items() 
                    if 'HIGH' in data['consolidation_potential']
                ],
                'consolidation_savings': self._calculate_savings(analysis)
            },
            'categories': analysis,
            'implementation_phases': self._create_implementation_phases(analysis),
            'constitutional_compliance': {
                'hash_validation': self.constitutional_hash,
                'performance_targets': {
                    'p99_latency_ms': 5,
                    'throughput_rps': 100,
                    'cache_hit_rate': 0.85
                },
                'validation_requirements': [
                    'All consolidated configs must include constitutional hash',
                    'Maintain backward compatibility during transition',
                    'Implement validation checks in automation scripts'
                ]
            }
        }
        
        return plan
    
    def _calculate_savings(self, analysis: Dict) -> Dict[str, int]:
        """Calculate potential savings from consolidation."""
        total_files = sum(cat['file_count'] for cat in analysis.values())
        
        # Estimate consolidated file count
        consolidated_files = 0
        for category, data in analysis.items():
            if 'HIGH' in data['consolidation_potential']:
                consolidated_files += max(3, data['file_count'] // 10)  # 90% reduction
            elif 'MEDIUM' in data['consolidation_potential']:
                consolidated_files += max(2, data['file_count'] // 5)   # 80% reduction
            else:
                consolidated_files += max(1, data['file_count'] // 2)   # 50% reduction
        
        return {
            'current_files': total_files,
            'projected_files': consolidated_files,
            'reduction_count': total_files - consolidated_files,
            'reduction_percentage': round((total_files - consolidated_files) / total_files * 100, 1)
        }
    
    def _create_implementation_phases(self, analysis: Dict) -> List[Dict]:
        """Create phased implementation plan."""
        phases = [
            {
                'phase': 1,
                'name': 'Critical Priority (Week 1-2)',
                'categories': ['docker', 'environment'],
                'description': 'Consolidate Docker Compose and environment configurations',
                'success_criteria': ['Unified Docker Compose files', 'Standardized environment configs']
            },
            {
                'phase': 2,
                'name': 'High Priority (Week 3-4)',
                'categories': ['services', 'monitoring'],
                'description': 'Group services and unify monitoring stack',
                'success_criteria': ['Service domain grouping', 'Single monitoring stack']
            },
            {
                'phase': 3,
                'name': 'Medium Priority (Week 5-8)',
                'categories': ['security', 'networking', 'ci_cd'],
                'description': 'Consolidate security, networking, and CI/CD configurations',
                'success_criteria': ['Unified security configs', 'Standardized CI/CD pipelines']
            }
        ]
        
        return phases

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Configuration Analysis Starting...")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    
    analyzer = ConfigurationAnalyzer()
    
    # Scan configurations
    config_files = analyzer.scan_configurations()
    
    # Generate consolidation plan
    plan = analyzer.generate_consolidation_plan()
    
    # Save analysis results
    output_file = "config-consolidation-analysis.json"
    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"✅ Analysis complete! Results saved to {output_file}")
    print(f"📊 Found {plan['analysis_summary']['total_files']} configuration files")
    print(f"🎯 Potential reduction: {plan['analysis_summary']['consolidation_savings']['reduction_percentage']}%")
    
    return plan

if __name__ == "__main__":
    main()
