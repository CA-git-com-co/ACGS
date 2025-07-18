#!/usr/bin/env python3

"""
ACGS-2 Architectural Analysis
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import datetime
from collections import defaultdict

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def analyze_service_architecture() -> Dict[str, Any]:
    """Analyze service architecture and boundaries."""
    architecture_analysis = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "service_categories": {},
        "service_boundaries": {},
        "communication_patterns": {},
        "dependency_analysis": {}
    }
    
    services_path = Path("services")
    if not services_path.exists():
        return architecture_analysis
    
    # Analyze service categories
    for category_dir in services_path.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            services = []
            
            for service_dir in category_dir.iterdir():
                if service_dir.is_dir():
                    service_info = analyze_service_structure(service_dir)
                    services.append(service_info)
            
            architecture_analysis["service_categories"][category_name] = {
                "service_count": len(services),
                "services": services,
                "category_complexity": calculate_category_complexity(services)
            }
    
    return architecture_analysis

def analyze_service_structure(service_path: Path) -> Dict[str, Any]:
    """Analyze individual service structure."""
    service_info = {
        "name": service_path.name,
        "path": str(service_path),
        "files": {"total": 0, "by_type": defaultdict(int)},
        "lines_of_code": 0,
        "has_constitutional_hash": False,
        "api_endpoints": [],
        "dependencies": [],
        "communication_patterns": [],
        "architectural_patterns": []
    }
    
    # Analyze files in service
    for file_path in service_path.rglob('*'):
        if file_path.is_file():
            service_info["files"]["total"] += 1
            ext = file_path.suffix.lower()
            service_info["files"]["by_type"][ext] += 1
            
            # Analyze Python files
            if ext == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        service_info["lines_of_code"] += lines
                        
                        # Check constitutional compliance
                        if CONSTITUTIONAL_HASH in content:
                            service_info["has_constitutional_hash"] = True
                        
                        # Extract API endpoints
                        endpoints = extract_api_endpoints(content)
                        service_info["api_endpoints"].extend(endpoints)
                        
                        # Extract dependencies
                        dependencies = extract_dependencies(content)
                        service_info["dependencies"].extend(dependencies)
                        
                        # Extract communication patterns
                        comm_patterns = extract_communication_patterns(content)
                        service_info["communication_patterns"].extend(comm_patterns)
                        
                        # Extract architectural patterns
                        arch_patterns = extract_architectural_patterns(content)
                        service_info["architectural_patterns"].extend(arch_patterns)
                        
                except Exception:
                    pass
    
    # Remove duplicates
    service_info["api_endpoints"] = list(set(service_info["api_endpoints"]))
    service_info["dependencies"] = list(set(service_info["dependencies"]))
    service_info["communication_patterns"] = list(set(service_info["communication_patterns"]))
    service_info["architectural_patterns"] = list(set(service_info["architectural_patterns"]))
    
    return service_info

def extract_api_endpoints(content: str) -> List[str]:
    """Extract API endpoints from service code."""
    endpoints = []
    
    # FastAPI patterns
    endpoint_patterns = [
        r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'@api\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    ]
    
    for pattern in endpoint_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match) >= 2:
                endpoints.append(f"{match[0].upper()} {match[1]}")
    
    return endpoints

def extract_dependencies(content: str) -> List[str]:
    """Extract service dependencies."""
    dependencies = []
    
    # Import patterns
    import_patterns = [
        r'from\s+(\w+)\s+import',
        r'import\s+(\w+)',
        r'requests\.(get|post|put|delete)\(["\']http://([^/]+)',
        r'http://([^:/]+):(\d+)'
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) >= 2 and match[1].isdigit():
                    dependencies.append(f"{match[0]}:{match[1]}")
                else:
                    dependencies.append(match[0])
            else:
                dependencies.append(match)
    
    return dependencies

def extract_communication_patterns(content: str) -> List[str]:
    """Extract communication patterns."""
    patterns = []
    
    # Communication patterns
    comm_patterns = {
        "async_communication": r'\basync\s+def\b',
        "event_driven": r'event|message|queue|pubsub',
        "rest_api": r'@app\.(get|post|put|delete)',
        "graphql": r'graphql|gql',
        "grpc": r'grpc|protobuf',
        "websocket": r'websocket|ws',
        "message_queue": r'rabbitmq|kafka|redis.*queue',
        "database": r'database|db|sql|mongo'
    }
    
    for pattern_name, pattern in comm_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            patterns.append(pattern_name)
    
    return patterns

def extract_architectural_patterns(content: str) -> List[str]:
    """Extract architectural patterns."""
    patterns = []
    
    # Architectural patterns
    arch_patterns = {
        "mvc": r'model|view|controller',
        "repository": r'repository|repo',
        "service_layer": r'service.*layer|business.*logic',
        "dependency_injection": r'inject|di|dependency',
        "factory": r'factory|builder',
        "observer": r'observer|listener|subscriber',
        "middleware": r'middleware|interceptor',
        "decorator": r'@.*decorator|@wraps',
        "singleton": r'singleton|single.*instance',
        "facade": r'facade|wrapper'
    }
    
    for pattern_name, pattern in arch_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            patterns.append(pattern_name)
    
    return patterns

def calculate_category_complexity(services: List[Dict]) -> Dict[str, Any]:
    """Calculate complexity metrics for service category."""
    total_services = len(services)
    total_lines = sum(s["lines_of_code"] for s in services)
    total_files = sum(s["files"]["total"] for s in services)
    
    complexity_metrics = {
        "total_services": total_services,
        "total_lines": total_lines,
        "total_files": total_files,
        "average_lines_per_service": total_lines / max(total_services, 1),
        "average_files_per_service": total_files / max(total_services, 1),
        "constitutional_compliance_rate": sum(1 for s in services if s["has_constitutional_hash"]) / max(total_services, 1)
    }
    
    return complexity_metrics

def analyze_docker_architecture() -> Dict[str, Any]:
    """Analyze Docker and containerization architecture."""
    docker_analysis = {
        "compose_files": [],
        "dockerfiles": [],
        "containerization_patterns": {},
        "service_definitions": {}
    }
    
    # Find Docker Compose files
    for compose_file in Path('.').rglob('docker-compose*.yml'):
        try:
            with open(compose_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            docker_analysis["compose_files"].append({
                "file": str(compose_file),
                "has_constitutional_hash": CONSTITUTIONAL_HASH in content,
                "service_count": content.count("services:"),
                "has_networking": "networks:" in content,
                "has_volumes": "volumes:" in content
            })
            
        except Exception:
            pass
    
    # Find Dockerfiles
    for dockerfile in Path('.').rglob('Dockerfile*'):
        try:
            with open(dockerfile, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            docker_analysis["dockerfiles"].append({
                "file": str(dockerfile),
                "has_constitutional_hash": CONSTITUTIONAL_HASH in content,
                "base_image": extract_base_image(content),
                "multi_stage": "FROM" in content and content.count("FROM") > 1
            })
            
        except Exception:
            pass
    
    return docker_analysis

def extract_base_image(dockerfile_content: str) -> str:
    """Extract base image from Dockerfile."""
    match = re.search(r'FROM\s+([^\s]+)', dockerfile_content)
    return match.group(1) if match else "unknown"

def analyze_infrastructure_patterns() -> Dict[str, Any]:
    """Analyze infrastructure and deployment patterns."""
    infrastructure_analysis = {
        "kubernetes_configs": [],
        "monitoring_configs": [],
        "security_configs": [],
        "deployment_patterns": []
    }
    
    # Kubernetes configurations
    for k8s_file in Path('.').rglob('*.yaml'):
        if any(k8s_term in str(k8s_file) for k8s_term in ['k8s', 'kubernetes', 'deployment']):
            try:
                with open(k8s_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                infrastructure_analysis["kubernetes_configs"].append({
                    "file": str(k8s_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content,
                    "resource_type": extract_k8s_resource_type(content)
                })
                
            except Exception:
                pass
    
    # Monitoring configurations
    for monitoring_file in Path('.').rglob('*'):
        if any(monitor_term in str(monitoring_file) for monitor_term in ['prometheus', 'grafana', 'alert']):
            try:
                with open(monitoring_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                infrastructure_analysis["monitoring_configs"].append({
                    "file": str(monitoring_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content,
                    "type": determine_monitoring_type(str(monitoring_file))
                })
                
            except Exception:
                pass
    
    return infrastructure_analysis

def extract_k8s_resource_type(content: str) -> str:
    """Extract Kubernetes resource type."""
    match = re.search(r'kind:\s*(\w+)', content)
    return match.group(1) if match else "unknown"

def determine_monitoring_type(file_path: str) -> str:
    """Determine monitoring configuration type."""
    if 'prometheus' in file_path.lower():
        return 'prometheus'
    elif 'grafana' in file_path.lower():
        return 'grafana'
    elif 'alert' in file_path.lower():
        return 'alerting'
    else:
        return 'monitoring'

def generate_architectural_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
    """Generate architectural recommendations."""
    recommendations = []
    
    # Service architecture recommendations
    service_categories = analysis_results.get("service_analysis", {}).get("service_categories", {})
    
    total_services = sum(cat.get("service_count", 0) for cat in service_categories.values())
    if total_services > 200:
        recommendations.append("CRITICAL: Consider service consolidation - 200+ services may indicate over-decomposition")
    elif total_services > 100:
        recommendations.append("HIGH: Review service boundaries - 100+ services require careful management")
    
    # Constitutional compliance recommendations
    for category_name, category_data in service_categories.items():
        complexity = category_data.get("category_complexity", {})
        compliance_rate = complexity.get("constitutional_compliance_rate", 0)
        if compliance_rate < 1.0:
            recommendations.append(f"MEDIUM: Improve constitutional compliance in {category_name} category ({compliance_rate*100:.1f}%)")
    
    # Docker architecture recommendations
    docker_analysis = analysis_results.get("docker_analysis", {})
    compose_files = docker_analysis.get("compose_files", [])
    if len(compose_files) > 50:
        recommendations.append("HIGH: Consolidate Docker Compose files - 50+ files create operational complexity")
    
    # Infrastructure recommendations
    infrastructure = analysis_results.get("infrastructure_analysis", {})
    k8s_configs = infrastructure.get("kubernetes_configs", [])
    if len(k8s_configs) > 100:
        recommendations.append("MEDIUM: Review Kubernetes configurations for consolidation opportunities")
    
    return recommendations

def main():
    """Main architectural analysis function."""
    print("Analyzing ACGS-2 Architecture...")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Run architectural analysis
    service_analysis = analyze_service_architecture()
    docker_analysis = analyze_docker_architecture()
    infrastructure_analysis = analyze_infrastructure_patterns()
    
    # Combine results
    analysis_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "service_analysis": service_analysis,
        "docker_analysis": docker_analysis,
        "infrastructure_analysis": infrastructure_analysis
    }
    
    # Generate recommendations
    recommendations = generate_architectural_recommendations(analysis_results)
    analysis_results["recommendations"] = recommendations
    
    # Save results
    output_file = "architectural_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"Architectural analysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("ARCHITECTURAL ANALYSIS SUMMARY")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Service architecture
    service_categories = service_analysis.get("service_categories", {})
    total_services = sum(cat.get("service_count", 0) for cat in service_categories.values())
    total_lines = sum(cat.get("category_complexity", {}).get("total_lines", 0) for cat in service_categories.values())
    
    print("SERVICE ARCHITECTURE")
    print("-" * 30)
    print(f"Total Services: {total_services}")
    print(f"Total Lines of Code: {total_lines}")
    print(f"Service Categories: {len(service_categories)}")
    print()
    
    for category_name, category_data in service_categories.items():
        complexity = category_data.get("category_complexity", {})
        print(f"{category_name}: {category_data.get('service_count', 0)} services")
        print(f"  Lines: {complexity.get('total_lines', 0)}")
        print(f"  Constitutional Compliance: {complexity.get('constitutional_compliance_rate', 0)*100:.1f}%")
    
    print()
    
    # Docker architecture
    compose_files = docker_analysis.get("compose_files", [])
    dockerfiles = docker_analysis.get("dockerfiles", [])
    
    print("CONTAINERIZATION ARCHITECTURE")
    print("-" * 35)
    print(f"Docker Compose Files: {len(compose_files)}")
    print(f"Dockerfiles: {len(dockerfiles)}")
    
    # Constitutional compliance in Docker files
    compose_compliance = sum(1 for f in compose_files if f.get("has_constitutional_hash", False))
    dockerfile_compliance = sum(1 for f in dockerfiles if f.get("has_constitutional_hash", False))
    
    print(f"Compose Files with Constitutional Hash: {compose_compliance}/{len(compose_files)}")
    print(f"Dockerfiles with Constitutional Hash: {dockerfile_compliance}/{len(dockerfiles)}")
    print()
    
    # Infrastructure architecture
    k8s_configs = infrastructure_analysis.get("kubernetes_configs", [])
    monitoring_configs = infrastructure_analysis.get("monitoring_configs", [])
    
    print("INFRASTRUCTURE ARCHITECTURE")
    print("-" * 35)
    print(f"Kubernetes Configs: {len(k8s_configs)}")
    print(f"Monitoring Configs: {len(monitoring_configs)}")
    print()
    
    # Recommendations
    if recommendations:
        print("ARCHITECTURAL RECOMMENDATIONS")
        print("-" * 40)
        for rec in recommendations:
            print(f"• {rec}")
    else:
        print("✅ Architecture is well-structured!")
    
    print()
    
    return analysis_results

if __name__ == "__main__":
    main()