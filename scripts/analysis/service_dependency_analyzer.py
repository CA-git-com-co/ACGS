#!/usr/bin/env python3

"""
ACGS-2 Service Dependency Graph Analyzer
Analyzes service dependencies to detect cycles and optimize architecture
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import json
import argparse
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches


@dataclass
class ServiceDependency:
    """Represents a dependency between services"""
    source: str
    target: str
    dependency_type: str  # 'api', 'database', 'queue', 'config'
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    file_path: str = ""
    line_number: int = 0


@dataclass
class ServiceInfo:
    """Information about a service"""
    name: str
    service_type: str  # 'core', 'platform', 'infrastructure'
    language: str
    port: Optional[int] = None
    endpoints: List[str] = field(default_factory=list)
    dependencies: List[ServiceDependency] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    docker_compose_services: List[str] = field(default_factory=list)


class ServiceDependencyAnalyzer:
    """Analyzes service dependencies in ACGS-2 architecture"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services: Dict[str, ServiceInfo] = {}
        self.dependencies: List[ServiceDependency] = []
        self.graph = nx.DiGraph()
        
        # Known service patterns
        self.service_patterns = {
            'auth_service': {
                'names': ['auth_service', 'authentication', 'auth-service'],
                'ports': [8000],
                'type': 'platform'
            },
            'ac_service': {
                'names': ['ac_service', 'constitutional-ai', 'constitutional_ai'],
                'ports': [8001],
                'type': 'core'
            },
            'integrity_service': {
                'names': ['integrity_service', 'integrity-service'],
                'ports': [8002],
                'type': 'platform'
            },
            'fv_service': {
                'names': ['fv_service', 'formal-verification', 'formal_verification'],
                'ports': [8003],
                'type': 'core'
            },
            'gs_service': {
                'names': ['gs_service', 'governance-synthesis', 'governance_synthesis'],
                'ports': [8004],
                'type': 'core'
            },
            'pgc_service': {
                'names': ['pgc_service', 'policy-governance', 'policy_governance'],
                'ports': [8005],
                'type': 'core'
            },
            'ec_service': {
                'names': ['ec_service', 'evolutionary-computation', 'evolutionary_computation'],
                'ports': [8006],
                'type': 'core'
            },
            'postgres': {
                'names': ['postgres', 'postgresql', 'database'],
                'ports': [5432, 5433, 5434, 5439],
                'type': 'infrastructure'
            },
            'redis': {
                'names': ['redis', 'cache'],
                'ports': [6379, 6380, 6381, 6389],
                'type': 'infrastructure'
            },
            'prometheus': {
                'names': ['prometheus', 'metrics'],
                'ports': [9090, 9091],
                'type': 'infrastructure'
            },
            'grafana': {
                'names': ['grafana', 'dashboard'],
                'ports': [3000, 3001],
                'type': 'infrastructure'
            }
        }
        
        # Dependency detection patterns
        self.dependency_patterns = [
            # HTTP API calls
            (r'http://(\w+):(\d+)', 'api', 0.9),
            (r'https://(\w+):(\d+)', 'api', 0.9),
            (r'requests\.get\(["\']http://(\w+):(\d+)', 'api', 0.8),
            (r'requests\.post\(["\']http://(\w+):(\d+)', 'api', 0.8),
            (r'fetch\(["\']http://(\w+):(\d+)', 'api', 0.8),
            (r'axios\.get\(["\']http://(\w+):(\d+)', 'api', 0.8),
            (r'curl.*http://(\w+):(\d+)', 'api', 0.7),
            
            # Database connections
            (r'postgresql://.*@(\w+):(\d+)', 'database', 0.9),
            (r'redis://.*@(\w+):(\d+)', 'database', 0.9),
            (r'DATABASE_URL.*(\w+):(\d+)', 'database', 0.8),
            (r'REDIS_URL.*(\w+):(\d+)', 'database', 0.8),
            
            # Service environment variables
            (r'(\w+)_SERVICE_URL', 'config', 0.7),
            (r'(\w+)_HOST', 'config', 0.6),
            (r'(\w+)_PORT', 'config', 0.6),
            
            # Docker Compose dependencies
            (r'depends_on:.*(\w+)', 'dependency', 0.8),
            (r'links:.*(\w+)', 'dependency', 0.7),
            
            # Import statements (for internal dependencies)
            (r'from\s+(\w+)\.', 'import', 0.5),
            (r'import\s+(\w+)', 'import', 0.4),
        ]
        
    def discover_services(self) -> None:
        """Discover all services in the project"""
        print("Discovering services...")
        
        # Scan Docker Compose files
        self._scan_docker_compose_files()
        
        # Scan service directories
        self._scan_service_directories()
        
        # Scan configuration files
        self._scan_configuration_files()
        
        print(f"Discovered {len(self.services)} services")
        
    def _scan_docker_compose_files(self) -> None:
        """Scan Docker Compose files for service definitions"""
        compose_files = list(self.project_root.glob("**/docker-compose*.yml"))
        compose_files.extend(list(self.project_root.glob("**/docker-compose*.yaml")))
        
        for compose_file in compose_files:
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_data = yaml.safe_load(f)
                    
                if not compose_data or 'services' not in compose_data:
                    continue
                    
                for service_name, service_config in compose_data['services'].items():
                    if service_name not in self.services:
                        self.services[service_name] = ServiceInfo(
                            name=service_name,
                            service_type=self._classify_service_type(service_name),
                            language=self._detect_language(service_config),
                            port=self._extract_port(service_config),
                            file_paths=[str(compose_file)]
                        )
                    
                    self.services[service_name].docker_compose_services.append(str(compose_file))
                    
                    # Extract dependencies from depends_on
                    if 'depends_on' in service_config:
                        depends_on = service_config['depends_on']
                        if isinstance(depends_on, list):
                            for dep in depends_on:
                                self._add_dependency(service_name, dep, 'dependency', 0.9, 
                                                   [f"depends_on in {compose_file}"])
                        elif isinstance(depends_on, dict):
                            for dep in depends_on.keys():
                                self._add_dependency(service_name, dep, 'dependency', 0.9,
                                                   [f"depends_on in {compose_file}"])
                                
            except Exception as e:
                print(f"Error scanning {compose_file}: {e}")
                
    def _scan_service_directories(self) -> None:
        """Scan service directories for dependencies"""
        service_dirs = []
        
        # Find service directories
        for pattern in ["services/*/", "services/*/*/"]:
            service_dirs.extend(self.project_root.glob(pattern))
            
        for service_dir in service_dirs:
            if service_dir.is_dir():
                service_name = service_dir.name
                
                # Initialize service if not already discovered
                if service_name not in self.services:
                    self.services[service_name] = ServiceInfo(
                        name=service_name,
                        service_type=self._classify_service_type(service_name),
                        language=self._detect_language_from_files(service_dir),
                        file_paths=[str(service_dir)]
                    )
                
                # Scan source files for dependencies
                self._scan_source_files(service_dir, service_name)
                
    def _scan_source_files(self, directory: Path, service_name: str) -> None:
        """Scan source files for dependency patterns"""
        source_extensions = ['.py', '.js', '.ts', '.rs', '.go', '.java', '.yml', '.yaml', '.json']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in source_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Apply dependency patterns
                    for pattern, dep_type, confidence in self.dependency_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            if match.groups():
                                target_service = match.group(1)
                                evidence = [f"Pattern '{pattern}' in {file_path}"]
                                
                                # Map known service names
                                target_service = self._normalize_service_name(target_service)
                                
                                if target_service and target_service != service_name:
                                    self._add_dependency(service_name, target_service, dep_type, 
                                                       confidence, evidence, str(file_path))
                                    
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
                    
    def _scan_configuration_files(self) -> None:
        """Scan configuration files for service dependencies"""
        config_files = []
        
        # Find configuration files
        for pattern in ["config/**/*.yml", "config/**/*.yaml", "config/**/*.json", "**/.env*"]:
            config_files.extend(self.project_root.glob(pattern))
            
        for config_file in config_files:
            try:
                if config_file.suffix in ['.yml', '.yaml']:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        
                    self._extract_dependencies_from_config(config_data, str(config_file))
                    
                elif config_file.suffix == '.json':
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        
                    self._extract_dependencies_from_config(config_data, str(config_file))
                    
                else:  # .env files
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    self._extract_dependencies_from_env(content, str(config_file))
                    
            except Exception as e:
                print(f"Error scanning {config_file}: {e}")
                
    def _extract_dependencies_from_config(self, config_data: dict, file_path: str) -> None:
        """Extract dependencies from configuration data"""
        if not isinstance(config_data, dict):
            return
            
        # Look for service URLs and references
        def extract_recursive(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, str):
                        # Check for service URLs
                        for pattern, dep_type, confidence in self.dependency_patterns:
                            match = re.search(pattern, value, re.IGNORECASE)
                            if match and match.groups():
                                target_service = self._normalize_service_name(match.group(1))
                                if target_service:
                                    evidence = [f"Config key '{current_path}' in {file_path}"]
                                    self._add_dependency("config", target_service, dep_type, 
                                                       confidence, evidence, file_path)
                    
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, current_path)
                        
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    extract_recursive(item, f"{path}[{i}]")
                    
        extract_recursive(config_data)
        
    def _extract_dependencies_from_env(self, content: str, file_path: str) -> None:
        """Extract dependencies from environment file"""
        for line in content.split('\n'):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                
                # Check for service URLs
                for pattern, dep_type, confidence in self.dependency_patterns:
                    match = re.search(pattern, value, re.IGNORECASE)
                    if match and match.groups():
                        target_service = self._normalize_service_name(match.group(1))
                        if target_service:
                            evidence = [f"Environment variable '{key}' in {file_path}"]
                            self._add_dependency("config", target_service, dep_type, 
                                               confidence, evidence, file_path)
                            
    def _classify_service_type(self, service_name: str) -> str:
        """Classify service type based on name"""
        for service_id, info in self.service_patterns.items():
            if service_name.lower() in [name.lower() for name in info['names']]:
                return info['type']
                
        # Default classification
        if any(keyword in service_name.lower() for keyword in ['auth', 'security', 'gateway']):
            return 'platform'
        elif any(keyword in service_name.lower() for keyword in ['postgres', 'redis', 'prometheus', 'grafana']):
            return 'infrastructure'
        else:
            return 'core'
            
    def _detect_language(self, service_config: dict) -> str:
        """Detect programming language from service configuration"""
        if 'image' in service_config:
            image = service_config['image']
            if 'python' in image or 'fastapi' in image:
                return 'python'
            elif 'node' in image or 'npm' in image:
                return 'javascript'
            elif 'rust' in image:
                return 'rust'
            elif 'golang' in image or 'go:' in image:
                return 'go'
                
        if 'build' in service_config:
            build_config = service_config['build']
            if isinstance(build_config, dict):
                dockerfile = build_config.get('dockerfile', 'Dockerfile')
                if 'python' in dockerfile:
                    return 'python'
                elif 'node' in dockerfile:
                    return 'javascript'
                elif 'rust' in dockerfile:
                    return 'rust'
                elif 'go' in dockerfile:
                    return 'go'
                    
        return 'unknown'
        
    def _detect_language_from_files(self, directory: Path) -> str:
        """Detect programming language from files in directory"""
        languages = {'python': 0, 'javascript': 0, 'rust': 0, 'go': 0}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix == '.py':
                    languages['python'] += 1
                elif suffix in ['.js', '.ts']:
                    languages['javascript'] += 1
                elif suffix == '.rs':
                    languages['rust'] += 1
                elif suffix == '.go':
                    languages['go'] += 1
                    
        return max(languages.keys(), key=lambda k: languages[k]) if any(languages.values()) else 'unknown'
        
    def _extract_port(self, service_config: dict) -> Optional[int]:
        """Extract service port from configuration"""
        if 'ports' in service_config:
            ports = service_config['ports']
            if isinstance(ports, list) and ports:
                port_mapping = ports[0]
                if isinstance(port_mapping, str):
                    # Format: "8000:8000" or "8000"
                    external_port = port_mapping.split(':')[0]
                    try:
                        return int(external_port)
                    except ValueError:
                        pass
                        
        return None
        
    def _normalize_service_name(self, service_name: str) -> Optional[str]:
        """Normalize service name to known service"""
        service_name = service_name.lower().replace('-', '_')
        
        for service_id, info in self.service_patterns.items():
            if service_name in [name.lower().replace('-', '_') for name in info['names']]:
                return service_id
                
        # Return as-is if not found in patterns
        return service_name if service_name else None
        
    def _add_dependency(self, source: str, target: str, dep_type: str, confidence: float, 
                       evidence: List[str], file_path: str = "") -> None:
        """Add a dependency to the list"""
        dependency = ServiceDependency(
            source=source,
            target=target,
            dependency_type=dep_type,
            confidence=confidence,
            evidence=evidence,
            file_path=file_path
        )
        
        self.dependencies.append(dependency)
        
        # Add to service info
        if source in self.services:
            self.services[source].dependencies.append(dependency)
            
    def build_dependency_graph(self) -> None:
        """Build NetworkX dependency graph"""
        print("Building dependency graph...")
        
        # Add nodes
        for service_name, service_info in self.services.items():
            self.graph.add_node(service_name, 
                               service_type=service_info.service_type,
                               language=service_info.language,
                               port=service_info.port)
            
        # Add edges
        for dependency in self.dependencies:
            if dependency.source in self.services and dependency.target in self.services:
                self.graph.add_edge(dependency.source, dependency.target,
                                   dependency_type=dependency.dependency_type,
                                   confidence=dependency.confidence,
                                   evidence=dependency.evidence)
                
    def detect_dependency_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in the service graph"""
        print("Detecting dependency cycles...")
        
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXError:
            return []
            
    def analyze_service_complexity(self) -> Dict[str, dict]:
        """Analyze complexity metrics for each service"""
        print("Analyzing service complexity...")
        
        metrics = {}
        
        for service_name in self.services:
            if service_name not in self.graph:
                continue
                
            # Calculate metrics
            in_degree = self.graph.in_degree(service_name)
            out_degree = self.graph.out_degree(service_name)
            
            # PageRank for importance
            pagerank = nx.pagerank(self.graph).get(service_name, 0)
            
            # Betweenness centrality
            betweenness = nx.betweenness_centrality(self.graph).get(service_name, 0)
            
            # Clustering coefficient
            clustering = nx.clustering(self.graph.to_undirected()).get(service_name, 0)
            
            metrics[service_name] = {
                'in_degree': in_degree,
                'out_degree': out_degree,
                'total_degree': in_degree + out_degree,
                'pagerank': pagerank,
                'betweenness': betweenness,
                'clustering': clustering,
                'service_type': self.services[service_name].service_type,
                'language': self.services[service_name].language
            }
            
        return metrics
        
    def generate_recommendations(self, cycles: List[List[str]], metrics: Dict[str, dict]) -> List[str]:
        """Generate architectural recommendations"""
        recommendations = []
        
        # Cycle recommendations
        if cycles:
            recommendations.append(f"🔄 CRITICAL: {len(cycles)} circular dependencies detected")
            for i, cycle in enumerate(cycles[:3]):  # Show first 3
                cycle_str = " → ".join(cycle + [cycle[0]])
                recommendations.append(f"   Cycle {i+1}: {cycle_str}")
                
            recommendations.append("   → Use event-driven architecture to break cycles")
            recommendations.append("   → Consider service consolidation for tightly coupled services")
            
        # High complexity services
        high_complexity = [(name, m) for name, m in metrics.items() 
                          if m['total_degree'] > 5 or m['betweenness'] > 0.1]
        
        if high_complexity:
            recommendations.append(f"📊 HIGH COMPLEXITY: {len(high_complexity)} services with high complexity")
            for name, metric in sorted(high_complexity, key=lambda x: x[1]['total_degree'], reverse=True)[:3]:
                recommendations.append(f"   {name}: {metric['total_degree']} connections, {metric['betweenness']:.3f} centrality")
                
            recommendations.append("   → Consider breaking down complex services")
            recommendations.append("   → Use service mesh for cross-cutting concerns")
            
        # Language diversity
        languages = set(m['language'] for m in metrics.values())
        if len(languages) > 3:
            recommendations.append(f"🔧 LANGUAGE DIVERSITY: {len(languages)} different languages")
            lang_counts = {lang: sum(1 for m in metrics.values() if m['language'] == lang) 
                          for lang in languages}
            for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
                recommendations.append(f"   {lang}: {count} services")
                
            recommendations.append("   → Consider standardizing on 1-2 primary languages")
            recommendations.append("   → Extract common libraries for shared functionality")
            
        # Service type imbalance
        type_counts = {stype: sum(1 for m in metrics.values() if m['service_type'] == stype) 
                      for stype in ['core', 'platform', 'infrastructure']}
        
        if type_counts['core'] > 6:
            recommendations.append(f"🏗️ SERVICE SPRAWL: {type_counts['core']} core services")
            recommendations.append("   → Consider consolidating related core services")
            
        return recommendations
        
    def visualize_dependency_graph(self, output_file: str = "dependency_graph.png") -> None:
        """Visualize the dependency graph"""
        print(f"Generating dependency graph visualization: {output_file}")
        
        if not self.graph.nodes():
            print("No services to visualize")
            return
            
        plt.figure(figsize=(16, 12))
        
        # Create layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Color nodes by service type
        service_colors = {
            'core': '#FF6B6B',
            'platform': '#4ECDC4', 
            'infrastructure': '#45B7D1',
            'unknown': '#96CEB4'
        }
        
        node_colors = [service_colors.get(self.services[node].service_type, '#96CEB4') 
                      for node in self.graph.nodes()]
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                              node_size=1500, alpha=0.9)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray', 
                              arrows=True, arrowsize=20, alpha=0.6)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold')
        
        # Add legend
        legend_elements = [patches.Patch(color=color, label=service_type.title()) 
                          for service_type, color in service_colors.items()]
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.title("ACGS-2 Service Dependency Graph\nConstitutional Hash: cdd01ef066bc6cf2", 
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_report(self, output_file: str = "dependency_analysis.json") -> None:
        """Generate comprehensive dependency analysis report"""
        print(f"Generating dependency analysis report: {output_file}")
        
        cycles = self.detect_dependency_cycles()
        metrics = self.analyze_service_complexity()
        recommendations = self.generate_recommendations(cycles, metrics)
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'constitutional_hash': 'cdd01ef066bc6cf2',
            'project_root': str(self.project_root),
            'summary': {
                'total_services': len(self.services),
                'total_dependencies': len(self.dependencies),
                'circular_dependencies': len(cycles),
                'service_types': {
                    stype: sum(1 for s in self.services.values() if s.service_type == stype)
                    for stype in ['core', 'platform', 'infrastructure']
                },
                'languages': {
                    lang: sum(1 for s in self.services.values() if s.language == lang)
                    for lang in set(s.language for s in self.services.values())
                }
            },
            'services': {
                name: {
                    'service_type': info.service_type,
                    'language': info.language,
                    'port': info.port,
                    'dependencies': [
                        {
                            'target': dep.target,
                            'type': dep.dependency_type,
                            'confidence': dep.confidence
                        }
                        for dep in info.dependencies
                    ]
                }
                for name, info in self.services.items()
            },
            'circular_dependencies': cycles,
            'complexity_metrics': metrics,
            'recommendations': recommendations,
            'high_risk_services': [
                name for name, metric in metrics.items()
                if metric['total_degree'] > 5 or metric['betweenness'] > 0.1
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return report
        
    def print_summary(self) -> None:
        """Print a summary of the dependency analysis"""
        cycles = self.detect_dependency_cycles()
        metrics = self.analyze_service_complexity()
        recommendations = self.generate_recommendations(cycles, metrics)
        
        print("\n" + "="*80)
        print("ACGS-2 SERVICE DEPENDENCY ANALYSIS")
        print("="*80)
        print(f"Constitutional Hash: cdd01ef066bc6cf2")
        print(f"Analysis Timestamp: {datetime.now().isoformat()}")
        print(f"Project Root: {self.project_root}")
        print()
        
        # Summary
        print("SUMMARY")
        print("-" * 40)
        print(f"Total Services: {len(self.services)}")
        print(f"Total Dependencies: {len(self.dependencies)}")
        print(f"Circular Dependencies: {len(cycles)}")
        print()
        
        # Service breakdown
        type_counts = {stype: sum(1 for s in self.services.values() if s.service_type == stype)
                      for stype in ['core', 'platform', 'infrastructure']}
        
        print("SERVICE BREAKDOWN")
        print("-" * 40)
        for stype, count in type_counts.items():
            print(f"{stype.title()}: {count} services")
        print()
        
        # Language breakdown
        lang_counts = {lang: sum(1 for s in self.services.values() if s.language == lang)
                      for lang in set(s.language for s in self.services.values())}
        
        print("LANGUAGE BREAKDOWN")
        print("-" * 40)
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{lang.title()}: {count} services")
        print()
        
        # Circular dependencies
        if cycles:
            print("CIRCULAR DEPENDENCIES")
            print("-" * 40)
            for i, cycle in enumerate(cycles):
                cycle_str = " → ".join(cycle + [cycle[0]])
                print(f"Cycle {i+1}: {cycle_str}")
            print()
            
        # High complexity services
        high_complexity = [(name, m) for name, m in metrics.items() 
                          if m['total_degree'] > 5 or m['betweenness'] > 0.1]
        
        if high_complexity:
            print("HIGH COMPLEXITY SERVICES")
            print("-" * 40)
            for name, metric in sorted(high_complexity, key=lambda x: x[1]['total_degree'], reverse=True):
                print(f"{name}: {metric['total_degree']} connections, "
                      f"{metric['betweenness']:.3f} centrality")
            print()
            
        # Recommendations
        if recommendations:
            print("RECOMMENDATIONS")
            print("-" * 40)
            for rec in recommendations:
                print(rec)
            print()
            
        # Status
        print("ANALYSIS STATUS")
        print("-" * 40)
        if cycles:
            print("❌ CRITICAL ISSUES DETECTED")
            print("   → Circular dependencies must be resolved")
        elif high_complexity:
            print("⚠️  COMPLEXITY ISSUES DETECTED")
            print("   → Consider service consolidation")
        else:
            print("✅ ARCHITECTURE LOOKS GOOD")
            print("   → No critical issues detected")
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS-2 Service Dependency Analyzer"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Root directory of the ACGS-2 project"
    )
    parser.add_argument(
        "--output", "-o",
        default="dependency_analysis.json",
        help="Output file for JSON report"
    )
    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Generate dependency graph visualization"
    )
    parser.add_argument(
        "--graph-output", "-g",
        default="dependency_graph.png",
        help="Output file for dependency graph visualization"
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = ServiceDependencyAnalyzer(args.project_root)
    
    # Discover services
    analyzer.discover_services()
    
    # Build dependency graph
    analyzer.build_dependency_graph()
    
    # Generate report
    analyzer.generate_report(args.output)
    
    # Print summary
    analyzer.print_summary()
    
    # Generate visualization if requested
    if args.visualize:
        try:
            analyzer.visualize_dependency_graph(args.graph_output)
        except ImportError:
            print("Warning: matplotlib not available, skipping visualization")
        except Exception as e:
            print(f"Error generating visualization: {e}")
            
    print(f"Analysis complete. Report saved to: {args.output}")


if __name__ == "__main__":
    main()