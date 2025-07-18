#!/usr/bin/env python3
"""
ACGS-2 Constitutional Compliance Validator
Constitutional Hash: cdd01ef066bc6cf2

Validates constitutional compliance across all simplified configurations.
"""

import os
import json
import yaml
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComplianceResult:
    """Represents a constitutional compliance validation result."""
    file_path: str
    is_compliant: bool
    issues: List[str]
    constitutional_hash_found: bool
    performance_targets_valid: bool
    security_requirements_met: bool

class ConstitutionalComplianceValidator:
    """Validates constitutional compliance across ACGS-2 configurations."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.performance_targets = {
            "p99_latency_ms": 5,
            "throughput_rps": 100,
            "cache_hit_rate": 0.85
        }
        self.results: List[ComplianceResult] = []
    
    def validate_all_configurations(self) -> Dict[str, Any]:
        """Validate constitutional compliance across all configuration files."""
        print(f"🔍 Starting constitutional compliance validation...")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        
        # Configuration file patterns to validate
        config_patterns = [
            "**/*.yml",
            "**/*.yaml", 
            "**/*.json",
            "**/*.env",
            "**/docker-compose*.yml",
            "**/Dockerfile*"
        ]
        
        # Exclude patterns - comprehensive archive and backup exclusions
        exclude_patterns = [
            "archive/", "archived/", "backup/", "backups/",
            "*_archive/", "*_archived/", "*_backup/", "*_backups/",
            "archive_*", "archived_*", "backup_*", "backups_*",
            "old/", "legacy/", "deprecated/", "obsolete/",
            "node_modules/", "__pycache__/", ".git/",
            "venv/", ".venv/", "build/", "dist/", ".pytest_cache/",
            "temp/", "tmp/", ".tmp/", "cache/", ".cache/"
        ]
        
        total_files = 0
        compliant_files = 0
        
        for pattern in config_patterns:
            for file_path in self.root_path.rglob(pattern):
                if file_path.is_file():
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
                    
                    total_files += 1
                    result = self._validate_file(file_path)
                    self.results.append(result)
                    
                    if result.is_compliant:
                        compliant_files += 1
        
        # Generate compliance report
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        report = {
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_files": total_files,
                "compliant_files": compliant_files,
                "non_compliant_files": total_files - compliant_files,
                "compliance_rate": round(compliance_rate, 2)
            },
            "performance_targets": self.performance_targets,
            "validation_results": [
                {
                    "file_path": result.file_path,
                    "is_compliant": result.is_compliant,
                    "issues": result.issues,
                    "constitutional_hash_found": result.constitutional_hash_found,
                    "performance_targets_valid": result.performance_targets_valid,
                    "security_requirements_met": result.security_requirements_met
                }
                for result in self.results
            ],
            "critical_issues": self._get_critical_issues(),
            "recommendations": self._get_recommendations()
        }
        
        return report
    
    def _validate_file(self, file_path: Path) -> ComplianceResult:
        """Validate a single configuration file for constitutional compliance."""
        relative_path = str(file_path.relative_to(self.root_path))
        issues = []
        constitutional_hash_found = False
        performance_targets_valid = False
        security_requirements_met = False
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for constitutional hash
            if self.constitutional_hash in content:
                constitutional_hash_found = True
            else:
                issues.append(f"Constitutional hash {self.constitutional_hash} not found")
            
            # Validate based on file type
            if file_path.suffix in ['.yml', '.yaml']:
                self._validate_yaml_file(content, issues)
                performance_targets_valid = self._check_performance_targets_yaml(content)
                security_requirements_met = self._check_security_requirements_yaml(content)
            
            elif file_path.suffix == '.json':
                self._validate_json_file(content, issues)
                performance_targets_valid = self._check_performance_targets_json(content)
                security_requirements_met = self._check_security_requirements_json(content)
            
            elif file_path.suffix == '.env':
                self._validate_env_file(content, issues)
                performance_targets_valid = self._check_performance_targets_env(content)
                security_requirements_met = self._check_security_requirements_env(content)
            
            elif 'docker-compose' in file_path.name:
                self._validate_docker_compose(content, issues)
                performance_targets_valid = self._check_docker_performance_targets(content)
                security_requirements_met = self._check_docker_security(content)
            
            elif 'Dockerfile' in file_path.name:
                self._validate_dockerfile(content, issues)
                security_requirements_met = self._check_dockerfile_security(content)
            
        except Exception as e:
            issues.append(f"Error reading file: {str(e)}")
        
        is_compliant = (
            constitutional_hash_found and 
            len(issues) == 0 and
            performance_targets_valid and
            security_requirements_met
        )
        
        return ComplianceResult(
            file_path=relative_path,
            is_compliant=is_compliant,
            issues=issues,
            constitutional_hash_found=constitutional_hash_found,
            performance_targets_valid=performance_targets_valid,
            security_requirements_met=security_requirements_met
        )
    
    def _validate_yaml_file(self, content: str, issues: List[str]) -> None:
        """Validate YAML file for constitutional compliance."""
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                # Check for required constitutional fields
                if 'constitutional_hash' not in data:
                    issues.append("Missing constitutional_hash field in YAML")
                
                # Check for performance monitoring
                if 'performance_targets' in data:
                    targets = data['performance_targets']
                    if not self._validate_performance_targets(targets):
                        issues.append("Performance targets do not meet constitutional requirements")
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML syntax: {str(e)}")
    
    def _validate_json_file(self, content: str, issues: List[str]) -> None:
        """Validate JSON file for constitutional compliance."""
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                # Check for required constitutional fields
                if 'constitutional_hash' not in data:
                    issues.append("Missing constitutional_hash field in JSON")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON syntax: {str(e)}")
    
    def _validate_env_file(self, content: str, issues: List[str]) -> None:
        """Validate environment file for constitutional compliance."""
        lines = content.split('\n')
        has_constitutional_hash = False
        has_performance_targets = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('CONSTITUTIONAL_HASH='):
                has_constitutional_hash = True
                if self.constitutional_hash not in line:
                    issues.append("Constitutional hash value mismatch in environment file")
            
            if any(target in line for target in ['P99_LATENCY', 'THROUGHPUT', 'CACHE_HIT']):
                has_performance_targets = True
        
        if not has_constitutional_hash:
            issues.append("Missing CONSTITUTIONAL_HASH environment variable")
    
    def _validate_docker_compose(self, content: str, issues: List[str]) -> None:
        """Validate Docker Compose file for constitutional compliance."""
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and 'services' in data:
                for service_name, service_config in data['services'].items():
                    if isinstance(service_config, dict):
                        # Check environment variables
                        env = service_config.get('environment', {})
                        if isinstance(env, dict):
                            if 'CONSTITUTIONAL_HASH' not in env:
                                issues.append(f"Service {service_name} missing CONSTITUTIONAL_HASH environment variable")
                        
                        # Check health checks
                        if 'healthcheck' not in service_config:
                            issues.append(f"Service {service_name} missing health check configuration")
                        
                        # Check resource limits
                        deploy = service_config.get('deploy', {})
                        if isinstance(deploy, dict):
                            resources = deploy.get('resources', {})
                            if not resources.get('limits'):
                                issues.append(f"Service {service_name} missing resource limits")
        except yaml.YAMLError as e:
            issues.append(f"Invalid Docker Compose YAML: {str(e)}")
    
    def _validate_dockerfile(self, content: str, issues: List[str]) -> None:
        """Validate Dockerfile for constitutional compliance."""
        lines = content.split('\n')
        has_constitutional_hash = False
        has_healthcheck = False
        has_user = False
        
        for line in lines:
            line = line.strip().upper()
            if 'CONSTITUTIONAL_HASH' in line:
                has_constitutional_hash = True
            if line.startswith('HEALTHCHECK'):
                has_healthcheck = True
            if line.startswith('USER ') and 'root' not in line:
                has_user = True
        
        if not has_constitutional_hash:
            issues.append("Dockerfile missing constitutional hash reference")
        if not has_healthcheck:
            issues.append("Dockerfile missing HEALTHCHECK instruction")
        if not has_user:
            issues.append("Dockerfile should specify non-root USER")
    
    def _check_performance_targets_yaml(self, content: str) -> bool:
        """Check if YAML file contains valid performance targets."""
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and 'performance_targets' in data:
                return self._validate_performance_targets(data['performance_targets'])
        except:
            pass
        return False
    
    def _check_performance_targets_json(self, content: str) -> bool:
        """Check if JSON file contains valid performance targets."""
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'performance_targets' in data:
                return self._validate_performance_targets(data['performance_targets'])
        except:
            pass
        return False
    
    def _check_performance_targets_env(self, content: str) -> bool:
        """Check if environment file contains valid performance targets."""
        return any(target in content for target in ['P99_LATENCY_TARGET', 'THROUGHPUT_TARGET', 'CACHE_HIT_RATE_TARGET'])
    
    def _check_docker_performance_targets(self, content: str) -> bool:
        """Check if Docker Compose file contains performance target configurations."""
        return 'performance' in content.lower() or 'target' in content.lower()
    
    def _check_security_requirements_yaml(self, content: str) -> bool:
        """Check if YAML file meets security requirements."""
        security_keywords = ['security', 'auth', 'ssl', 'tls', 'encryption']
        return any(keyword in content.lower() for keyword in security_keywords)
    
    def _check_security_requirements_json(self, content: str) -> bool:
        """Check if JSON file meets security requirements."""
        security_keywords = ['security', 'auth', 'ssl', 'tls', 'encryption']
        return any(keyword in content.lower() for keyword in security_keywords)
    
    def _check_security_requirements_env(self, content: str) -> bool:
        """Check if environment file meets security requirements."""
        security_keywords = ['JWT_SECRET', 'PASSWORD', 'API_KEY', 'SSL_', 'TLS_']
        return any(keyword in content for keyword in security_keywords)
    
    def _check_docker_security(self, content: str) -> bool:
        """Check if Docker Compose file meets security requirements."""
        security_keywords = ['security_opt', 'read_only', 'no-new-privileges']
        return any(keyword in content for keyword in security_keywords)
    
    def _check_dockerfile_security(self, content: str) -> bool:
        """Check if Dockerfile meets security requirements."""
        return 'USER ' in content and 'root' not in content.lower()
    
    def _validate_performance_targets(self, targets: Dict[str, Any]) -> bool:
        """Validate performance targets against constitutional requirements."""
        if not isinstance(targets, dict):
            return False
        
        # Check P99 latency
        p99_latency = targets.get('p99_latency_ms', targets.get('P99_LATENCY_TARGET_MS'))
        if p99_latency and int(p99_latency) > self.performance_targets['p99_latency_ms']:
            return False
        
        # Check throughput
        throughput = targets.get('throughput_rps', targets.get('THROUGHPUT_TARGET_RPS'))
        if throughput and int(throughput) < self.performance_targets['throughput_rps']:
            return False
        
        # Check cache hit rate
        cache_hit_rate = targets.get('cache_hit_rate', targets.get('CACHE_HIT_RATE_TARGET'))
        if cache_hit_rate and float(cache_hit_rate) < self.performance_targets['cache_hit_rate']:
            return False
        
        return True
    
    def _get_critical_issues(self) -> List[Dict[str, Any]]:
        """Get critical constitutional compliance issues."""
        critical_issues = []
        
        for result in self.results:
            if not result.constitutional_hash_found:
                critical_issues.append({
                    "file": result.file_path,
                    "issue": "Missing constitutional hash",
                    "severity": "critical"
                })
            
            if not result.performance_targets_valid and 'docker-compose' in result.file_path:
                critical_issues.append({
                    "file": result.file_path,
                    "issue": "Performance targets not meeting constitutional requirements",
                    "severity": "high"
                })
        
        return critical_issues
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations for improving constitutional compliance."""
        recommendations = [
            f"Ensure all configuration files include constitutional hash: {self.constitutional_hash}",
            "Implement performance monitoring with constitutional targets (P99 <5ms, >100 RPS, >85% cache hit)",
            "Add health checks to all Docker services",
            "Implement resource limits for all containerized services",
            "Use non-root users in Docker containers",
            "Enable security options in Docker Compose files",
            "Implement structured logging with constitutional compliance tracking",
            "Add constitutional compliance validation to CI/CD pipelines"
        ]
        
        return recommendations

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Constitutional Compliance Validator")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    
    validator = ConstitutionalComplianceValidator()
    report = validator.validate_all_configurations()
    
    # Save report
    output_file = "constitutional-compliance-report.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report['summary']
    print(f"\n✅ Validation Complete!")
    print(f"📊 Total Files: {summary['total_files']}")
    print(f"✅ Compliant Files: {summary['compliant_files']}")
    print(f"❌ Non-Compliant Files: {summary['non_compliant_files']}")
    print(f"📈 Compliance Rate: {summary['compliance_rate']}%")
    
    if summary['compliance_rate'] < 95:
        print(f"\n⚠️  Constitutional compliance below target (95%)")
        print(f"📋 Report saved to: {output_file}")
        return 1
    else:
        print(f"\n🎉 Constitutional compliance target achieved!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
