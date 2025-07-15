#!/usr/bin/env python3
"""
ACGS-2 Dynamic Service Discovery Engine
Constitutional Hash: cdd01ef066bc6cf2

Advanced service discovery for complex microservices architecture.
Supports dynamic path resolution, service health validation, and dependency mapping.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import subprocess
import argparse
from dataclasses import dataclass, asdict
import yaml

@dataclass
class ServiceInfo:
    """Comprehensive service information"""
    name: str
    logical_name: str
    path: Path
    service_type: str  # core, platform_services, shared
    main_files: List[str]
    test_paths: List[str]
    config_files: List[str]
    dependencies: List[str]
    health_endpoint: Optional[str]
    constitutional_compliance: bool
    coverage_target: float
    priority: str  # critical, high, medium, low

class ServiceDiscoveryEngine:
    """Advanced service discovery with constitutional compliance validation"""
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.root_path = Path.cwd()
        self.services_cache = {}
        self.dependency_graph = {}
        
    def discover_all_services(self) -> Dict[str, ServiceInfo]:
        """Discover all ACGS services with comprehensive analysis"""
        
        print(f"🔍 ACGS-2 Advanced Service Discovery")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Root Path: {self.root_path}")
        
        services = {}
        
        # Define service patterns with priorities
        service_patterns = {
            # Platform Services (Critical)
            "auth-service": {
                "patterns": [
                    "services/platform_services/authentication/auth_service",
                    "services/platform_services/auth_service",
                    "services/authentication",
                    "auth_service"
                ],
                "type": "platform_services",
                "priority": "critical",
                "coverage_target": 95.0
            },
            "integrity-service": {
                "patterns": [
                    "services/platform_services/integrity/integrity_service",
                    "services/platform_services/integrity_service",
                    "services/integrity",
                    "integrity_service"
                ],
                "type": "platform_services",
                "priority": "critical",
                "coverage_target": 98.0
            },
            "api-gateway": {
                "patterns": [
                    "services/platform_services/api_gateway/gateway_service",
                    "services/api_gateway",
                    "gateway_service"
                ],
                "type": "platform_services",
                "priority": "critical",
                "coverage_target": 92.0
            },
            
            # Core Services (High Priority)
            "ac-service": {
                "patterns": [
                    "services/core/constitutional-ai/ac_service",
                    "services/core/constitutional_ai",
                    "services/constitutional_ai",
                    "ac_service"
                ],
                "type": "core",
                "priority": "high",
                "coverage_target": 99.0
            },
            "gs-service": {
                "patterns": [
                    "services/core/governance-synthesis/gs_service",
                    "services/core/governance_synthesis",
                    "services/governance_synthesis",
                    "gs_service"
                ],
                "type": "core",
                "priority": "high",
                "coverage_target": 90.0
            },
            "fv-service": {
                "patterns": [
                    "services/core/formal-verification/fv_service",
                    "services/core/formal_verification",
                    "services/formal_verification",
                    "fv_service"
                ],
                "type": "core",
                "priority": "high",
                "coverage_target": 95.0
            },
            "pgc-service": {
                "patterns": [
                    "services/core/policy-governance/pgc_service",
                    "services/core/policy_governance",
                    "services/policy_governance",
                    "pgc_service"
                ],
                "type": "core",
                "priority": "high",
                "coverage_target": 93.0
            },
            "ec-service": {
                "patterns": [
                    "services/core/evolutionary-computation/ec_service",
                    "services/core/evolutionary_computation",
                    "services/evolutionary_computation",
                    "ec_service"
                ],
                "type": "core",
                "priority": "medium",
                "coverage_target": 88.0
            },
            
            # Additional Services
            "context-service": {
                "patterns": [
                    "services/core/context/context_service",
                    "services/context",
                    "context_service"
                ],
                "type": "core",
                "priority": "medium",
                "coverage_target": 85.0
            },
            "worker-agents": {
                "patterns": [
                    "services/core/worker_agents",
                    "services/worker_agents"
                ],
                "type": "core",
                "priority": "medium",
                "coverage_target": 80.0
            }
        }
        
        # Discover services
        for logical_name, config in service_patterns.items():
            service_info = self._discover_service(logical_name, config)
            if service_info:
                services[logical_name] = service_info
                print(f"✅ Found: {logical_name} -> {service_info.path}")
            else:
                print(f"⚠️ Missing: {logical_name}")
        
        # Auto-discover additional services
        auto_discovered = self._auto_discover_services()
        for name, service in auto_discovered.items():
            if name not in services:
                services[name] = service
                print(f"🔍 Auto-discovered: {name} -> {service.path}")
        
        # Build dependency graph
        self._build_dependency_graph(services)
        
        # Validate constitutional compliance
        self._validate_constitutional_compliance(services)
        
        print(f"\n📊 Discovery Summary:")
        print(f"Total Services Found: {len(services)}")
        print(f"Critical Services: {len([s for s in services.values() if s.priority == 'critical'])}")
        print(f"High Priority: {len([s for s in services.values() if s.priority == 'high'])}")
        print(f"Constitutional Compliant: {len([s for s in services.values() if s.constitutional_compliance])}")
        
        return services
    
    def _discover_service(self, logical_name: str, config: Dict) -> Optional[ServiceInfo]:
        """Discover a specific service with comprehensive analysis"""
        
        for pattern in config["patterns"]:
            service_path = self.root_path / pattern
            if service_path.exists():
                return self._analyze_service(logical_name, service_path, config)
        
        return None
    
    def _analyze_service(self, logical_name: str, service_path: Path, config: Dict) -> ServiceInfo:
        """Comprehensive service analysis"""
        
        # Find main files
        main_files = []
        for main_file in ["main.py", "app.py", "server.py", "__init__.py"]:
            if (service_path / main_file).exists():
                main_files.append(main_file)
        
        # Find nested main files
        for subdir in ["app", "src"]:
            subdir_path = service_path / subdir
            if subdir_path.exists():
                for main_file in ["main.py", "app.py", "__init__.py"]:
                    if (subdir_path / main_file).exists():
                        main_files.append(f"{subdir}/{main_file}")
        
        # Find test paths
        test_paths = []
        for test_dir in ["tests", "test", "testing"]:
            test_path = service_path / test_dir
            if test_path.exists():
                test_paths.append(str(test_path.relative_to(self.root_path)))
        
        # Find config files
        config_files = []
        for config_file in ["config.py", "settings.py", "config.yaml", "config.json"]:
            if (service_path / config_file).exists():
                config_files.append(config_file)
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies(service_path)
        
        # Check constitutional compliance
        constitutional_compliance = self._check_constitutional_hash(service_path)
        
        # Determine health endpoint
        health_endpoint = self._detect_health_endpoint(service_path)
        
        return ServiceInfo(
            name=service_path.name,
            logical_name=logical_name,
            path=service_path,
            service_type=config["type"],
            main_files=main_files,
            test_paths=test_paths,
            config_files=config_files,
            dependencies=dependencies,
            health_endpoint=health_endpoint,
            constitutional_compliance=constitutional_compliance,
            coverage_target=config["coverage_target"],
            priority=config["priority"]
        )
    
    def _auto_discover_services(self) -> Dict[str, ServiceInfo]:
        """Auto-discover services not in predefined patterns"""
        
        discovered = {}
        services_dirs = ["services/core", "services/platform_services", "services/shared"]
        
        for services_dir in services_dirs:
            services_path = self.root_path / services_dir
            if not services_path.exists():
                continue
                
            for item in services_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if it's a service directory
                    if self._is_service_directory(item):
                        logical_name = f"auto-{item.name}"
                        service_info = self._analyze_service(
                            logical_name, 
                            item, 
                            {
                                "type": services_dir.split('/')[-1],
                                "priority": "low",
                                "coverage_target": 75.0
                            }
                        )
                        discovered[logical_name] = service_info
        
        return discovered
    
    def _is_service_directory(self, path: Path) -> bool:
        """Check if directory is a service"""
        
        # Look for service indicators
        indicators = [
            "main.py", "app.py", "server.py",
            "requirements.txt", "pyproject.toml",
            "Dockerfile", "docker-compose.yml"
        ]
        
        for indicator in indicators:
            if (path / indicator).exists():
                return True
                
        # Check subdirectories
        for subdir in ["app", "src"]:
            subdir_path = path / subdir
            if subdir_path.exists():
                for indicator in ["main.py", "app.py", "__init__.py"]:
                    if (subdir_path / indicator).exists():
                        return True
        
        return False
    
    def _analyze_dependencies(self, service_path: Path) -> List[str]:
        """Analyze service dependencies"""
        
        dependencies = []
        
        # Check requirements.txt
        req_file = service_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name
                            package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                            dependencies.append(package.strip())
            except Exception:
                pass
        
        # Check pyproject.toml
        pyproject_file = service_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import toml
                with open(pyproject_file) as f:
                    data = toml.load(f)
                    deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
                    dependencies.extend(deps.keys())
            except Exception:
                pass
        
        return dependencies
    
    def _check_constitutional_hash(self, service_path: Path) -> bool:
        """Check constitutional compliance"""
        
        # Search for constitutional hash in Python files
        for py_file in service_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if self.constitutional_hash in content:
                        return True
            except Exception:
                continue
        
        # Search in config files
        for config_file in service_path.rglob("*.yml"):
            try:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if self.constitutional_hash in content:
                        return True
            except Exception:
                continue
        
        return False
    
    def _detect_health_endpoint(self, service_path: Path) -> Optional[str]:
        """Detect health check endpoint"""
        
        # Look for common health endpoint patterns
        health_patterns = ["/health", "/healthz", "/status", "/ping"]
        
        for py_file in service_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in health_patterns:
                        if pattern in content:
                            return pattern
            except Exception:
                continue
        
        return "/health"  # Default
    
    def _build_dependency_graph(self, services: Dict[str, ServiceInfo]):
        """Build service dependency graph"""
        
        self.dependency_graph = {}
        
        for name, service in services.items():
            self.dependency_graph[name] = {
                "depends_on": [],
                "dependents": []
            }
        
        # Analyze import dependencies
        for name, service in services.items():
            for py_file in service.path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Look for service imports
                        for other_name, other_service in services.items():
                            if other_name != name:
                                service_module = other_service.path.name
                                if f"from {service_module}" in content or f"import {service_module}" in content:
                                    if other_name not in self.dependency_graph[name]["depends_on"]:
                                        self.dependency_graph[name]["depends_on"].append(other_name)
                                        self.dependency_graph[other_name]["dependents"].append(name)
                except Exception:
                    continue
    
    def _validate_constitutional_compliance(self, services: Dict[str, ServiceInfo]):
        """Validate constitutional compliance across services"""
        
        compliant_services = [s for s in services.values() if s.constitutional_compliance]
        compliance_rate = len(compliant_services) / len(services) * 100 if services else 0
        
        print(f"\n🔒 Constitutional Compliance Analysis:")
        print(f"Compliance Rate: {compliance_rate:.1f}%")
        print(f"Compliant Services: {len(compliant_services)}/{len(services)}")
        
        if compliance_rate < 100:
            non_compliant = [s.logical_name for s in services.values() if not s.constitutional_compliance]
            print(f"Non-compliant Services: {', '.join(non_compliant)}")
    
    def generate_service_matrix(self, services: Dict[str, ServiceInfo]) -> List[str]:
        """Generate optimized service matrix for GitHub Actions"""
        
        # Sort by priority and dependencies
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        sorted_services = sorted(
            services.items(),
            key=lambda x: (
                priority_order.get(x[1].priority, 4),
                len(self.dependency_graph.get(x[0], {}).get("depends_on", [])),
                x[0]
            )
        )
        
        return [name for name, _ in sorted_services]
    
    def export_service_config(self, services: Dict[str, ServiceInfo], output_file: str):
        """Export service configuration for CI/CD"""
        
        config = {
            "constitutional_hash": self.constitutional_hash,
            "discovery_timestamp": "2025-07-11T00:00:00Z",
            "services": {
                name: asdict(service) for name, service in services.items()
            },
            "dependency_graph": self.dependency_graph,
            "testing_matrix": self.generate_service_matrix(services)
        }
        
        # Convert Path objects to strings for JSON serialization
        def path_converter(obj):
            if isinstance(obj, Path):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2, default=path_converter)
        
        print(f"📄 Service configuration exported to: {output_file}")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='ACGS-2 Advanced Service Discovery Engine'
    )
    parser.add_argument('--constitutional-hash', 
                       default='cdd01ef066bc6cf2',
                       help='Constitutional hash for compliance validation')
    parser.add_argument('--output-config',
                       default='config/services/discovery.json',
                       help='Output file for service configuration')
    parser.add_argument('--output-matrix',
                       help='Output file for GitHub Actions matrix')
    parser.add_argument('--format', choices=['json', 'yaml'],
                       default='json',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Initialize discovery engine
    engine = ServiceDiscoveryEngine(args.constitutional_hash)
    
    # Discover all services
    services = engine.discover_all_services()
    
    # Export configuration
    engine.export_service_config(services, args.output_config)
    
    # Export testing matrix if requested
    if args.output_matrix:
        matrix = engine.generate_service_matrix(services)
        matrix_config = {"service": matrix}
        
        with open(args.output_matrix, 'w') as f:
            if args.format == 'yaml':
                yaml.dump(matrix_config, f)
            else:
                json.dump(matrix_config, f, indent=2)
        
        print(f"🎯 Testing matrix exported to: {args.output_matrix}")
    
    # Print summary
    print(f"\n✅ Service Discovery Complete")
    print(f"Services Discovered: {len(services)}")
    print(f"Configuration: {args.output_config}")
    
    # Exit with appropriate code
    constitutional_compliant = all(s.constitutional_compliance for s in services.values())
    if constitutional_compliant and services:
        print(f"🔒 All services are constitutionally compliant")
        sys.exit(0)
    else:
        print(f"⚠️ Some services need constitutional compliance updates")
        sys.exit(1)

if __name__ == "__main__":
    main()