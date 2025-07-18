#!/usr/bin/env python3

"""
ACGS-2 Comprehensive Codebase Analyzer
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import ast
import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def analyze_project_structure() -> Dict[str, Any]:
    """Analyze the overall project structure."""
    structure = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "directories": {},
        "file_counts": defaultdict(int),
        "total_files": 0,
        "total_lines": 0
    }
    
    # Analyze directory structure
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and common build directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'target']]
        
        level = root.replace('.', '').count(os.sep)
        if level <= 2:  # Only go 2 levels deep for structure
            structure["directories"][root] = {
                "subdirs": len(dirs),
                "files": len(files),
                "file_types": {}
            }
            
            # Count file types
            for file in files:
                ext = Path(file).suffix.lower()
                structure["directories"][root]["file_types"][ext] = structure["directories"][root]["file_types"].get(ext, 0) + 1
                structure["file_counts"][ext] += 1
                structure["total_files"] += 1
                
                # Count lines for source files
                if ext in ['.py', '.js', '.ts', '.rs', '.go']:
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            structure["total_lines"] += lines
                    except Exception:
                        pass
    
    return structure

def analyze_services() -> Dict[str, Any]:
    """Analyze service structure and patterns."""
    services = {}
    
    services_dir = Path('services')
    if not services_dir.exists():
        return {"error": "Services directory not found"}
    
    for service_category in services_dir.iterdir():
        if service_category.is_dir():
            services[service_category.name] = {
                "services": {},
                "category_type": service_category.name
            }
            
            for service_dir in service_category.iterdir():
                if service_dir.is_dir():
                    service_analysis = analyze_single_service(service_dir)
                    services[service_category.name]["services"][service_dir.name] = service_analysis
    
    return services

def analyze_single_service(service_path: Path) -> Dict[str, Any]:
    """Analyze a single service."""
    analysis = {
        "path": str(service_path),
        "files": {"total": 0, "by_type": defaultdict(int)},
        "lines_of_code": 0,
        "has_dockerfile": False,
        "has_requirements": False,
        "has_config": False,
        "has_tests": False,
        "constitutional_compliant": False,
        "endpoints": [],
        "dependencies": []
    }
    
    # Analyze files in service
    for file_path in service_path.rglob('*'):
        if file_path.is_file():
            analysis["files"]["total"] += 1
            ext = file_path.suffix.lower()
            analysis["files"]["by_type"][ext] += 1
            
            # Check for specific files
            if file_path.name.lower() == 'dockerfile':
                analysis["has_dockerfile"] = True
            elif file_path.name in ['config/environments/requirements.txt', 'package.json', 'Cargo.toml']:
                analysis["has_requirements"] = True
            elif 'config' in file_path.name.lower():
                analysis["has_config"] = True
            elif 'test' in file_path.name.lower():
                analysis["has_tests"] = True
            
            # Count lines and check constitutional compliance
            if ext in ['.py', '.js', '.ts', '.rs', '.go']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        analysis["lines_of_code"] += lines
                        
                        # Check constitutional compliance
                        if CONSTITUTIONAL_HASH in content:
                            analysis["constitutional_compliant"] = True
                        
                        # Extract API endpoints (simple pattern matching)
                        if ext == '.py':
                            endpoints = re.findall(r'@app\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
                            analysis["endpoints"].extend([endpoint[1] for endpoint in endpoints])
                        
                        # Extract dependencies
                        if ext == '.py':
                            imports = re.findall(r'from\s+(\w+)', content)
                            analysis["dependencies"].extend(imports)
                            
                except Exception:
                    pass
    
    # Remove duplicates from endpoints and dependencies
    analysis["endpoints"] = list(set(analysis["endpoints"]))
    analysis["dependencies"] = list(set(analysis["dependencies"]))
    
    return analysis

def analyze_docker_structure() -> Dict[str, Any]:
    """Analyze Docker and containerization setup."""
    docker_analysis = {
        "compose_files": [],
        "dockerfiles": [],
        "total_services_defined": 0,
        "networks": [],
        "volumes": []
    }
    
    # Find all Docker Compose files
    for compose_file in Path('.').rglob('docker-compose*.yml'):
        docker_analysis["compose_files"].append(str(compose_file))
    
    for compose_file in Path('.').rglob('docker-compose*.yaml'):
        docker_analysis["compose_files"].append(str(compose_file))
    
    # Find all Dockerfiles
    for dockerfile in Path('.').rglob('Dockerfile*'):
        docker_analysis["dockerfiles"].append(str(dockerfile))
    
    return docker_analysis

def analyze_testing_framework() -> Dict[str, Any]:
    """Analyze testing setup and coverage."""
    testing_analysis = {
        "test_files": {"total": 0, "by_type": defaultdict(int)},
        "testing_frameworks": set(),
        "test_directories": [],
        "has_ci_config": False
    }
    
    # Find test files
    for test_file in Path('.').rglob('test*.py'):
        testing_analysis["test_files"]["total"] += 1
        testing_analysis["test_files"]["by_type"]["python"] += 1
        
        # Check for testing frameworks
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'pytest' in content:
                    testing_analysis["testing_frameworks"].add('pytest')
                if 'unittest' in content:
                    testing_analysis["testing_frameworks"].add('unittest')
                if 'asyncio' in content:
                    testing_analysis["testing_frameworks"].add('asyncio')
        except Exception:
            pass
    
    # Find test directories
    for test_dir in Path('.').rglob('test*'):
        if test_dir.is_dir():
            testing_analysis["test_directories"].append(str(test_dir))
    
    # Check for CI configuration
    ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile']
    for ci_file in ci_files:
        if Path(ci_file).exists():
            testing_analysis["has_ci_config"] = True
            break
    
    # Convert set to list for JSON serialization
    testing_analysis["testing_frameworks"] = list(testing_analysis["testing_frameworks"])
    
    return testing_analysis

def analyze_performance_patterns() -> Dict[str, Any]:
    """Analyze performance-related patterns in the codebase."""
    performance_analysis = {
        "async_patterns": 0,
        "caching_implementations": 0,
        "database_connections": 0,
        "potential_bottlenecks": []
    }
    
    # Scan Python files for performance patterns
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Count async patterns
                performance_analysis["async_patterns"] += len(re.findall(r'\basync\s+def\b', content))
                performance_analysis["async_patterns"] += len(re.findall(r'\bawait\b', content))
                
                # Count caching patterns
                performance_analysis["caching_implementations"] += len(re.findall(r'@cache|@lru_cache|redis|memcached', content))
                
                # Count database connections
                performance_analysis["database_connections"] += len(re.findall(r'connect\(|engine|session', content))
                
                # Identify potential bottlenecks
                if 'time.sleep' in content:
                    performance_analysis["potential_bottlenecks"].append(f"Blocking sleep in {py_file}")
                
                if len(re.findall(r'for.*in.*query', content)) > 0:
                    performance_analysis["potential_bottlenecks"].append(f"Potential N+1 query in {py_file}")
                    
        except Exception:
            pass
    
    return performance_analysis

def analyze_security_patterns() -> Dict[str, Any]:
    """Analyze security implementations and patterns."""
    security_analysis = {
        "jwt_usage": 0,
        "encryption_patterns": 0,
        "authentication_files": [],
        "potential_vulnerabilities": []
    }
    
    # Scan for security patterns
    for file_path in Path('.').rglob('*.py'):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # JWT usage
                if 'jwt' in content.lower():
                    security_analysis["jwt_usage"] += 1
                
                # Encryption patterns
                if any(pattern in content.lower() for pattern in ['encrypt', 'decrypt', 'hash', 'bcrypt']):
                    security_analysis["encryption_patterns"] += 1
                
                # Authentication files
                if any(pattern in content.lower() for pattern in ['authenticate', 'authorize', 'login', 'token']):
                    security_analysis["authentication_files"].append(str(file_path))
                
                # Potential vulnerabilities
                if 'password' in content and '=' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'password' in line.lower() and '=' in line and not line.strip().startswith('#'):
                            security_analysis["potential_vulnerabilities"].append(f"Potential hardcoded password in {file_path}:{i+1}")
                            
        except Exception:
            pass
    
    # Remove duplicates and limit results
    security_analysis["authentication_files"] = list(set(security_analysis["authentication_files"]))[:10]
    security_analysis["potential_vulnerabilities"] = security_analysis["potential_vulnerabilities"][:10]
    
    return security_analysis

def main():
    """Main analysis function."""
    print("Starting comprehensive ACGS-2 codebase analysis...")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    analysis_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "project_structure": analyze_project_structure(),
        "services_analysis": analyze_services(),
        "docker_structure": analyze_docker_structure(),
        "testing_framework": analyze_testing_framework(),
        "performance_patterns": analyze_performance_patterns(),
        "security_patterns": analyze_security_patterns()
    }
    
    # Save results
    output_file = "comprehensive_codebase_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\nAnalysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("ACGS-2 COMPREHENSIVE CODEBASE ANALYSIS SUMMARY")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Analysis Timestamp: {analysis_results['analysis_timestamp']}")
    print()
    
    # Project overview
    structure = analysis_results["project_structure"]
    print("PROJECT OVERVIEW")
    print("-" * 40)
    print(f"Total Files: {structure['total_files']}")
    print(f"Total Lines of Code: {structure['total_lines']}")
    print(f"Main File Types: {dict(list(structure['file_counts'].items())[:5])}")
    print()
    
    # Services overview
    services = analysis_results["services_analysis"]
    total_services = sum(len(category["services"]) for category in services.values())
    print("SERVICES OVERVIEW")
    print("-" * 40)
    print(f"Total Services: {total_services}")
    for category, data in services.items():
        print(f"{category}: {len(data['services'])} services")
    print()
    
    # Docker overview
    docker = analysis_results["docker_structure"]
    print("CONTAINERIZATION OVERVIEW")
    print("-" * 40)
    print(f"Docker Compose Files: {len(docker['compose_files'])}")
    print(f"Dockerfiles: {len(docker['dockerfiles'])}")
    print()
    
    # Testing overview
    testing = analysis_results["testing_framework"]
    print("TESTING OVERVIEW")
    print("-" * 40)
    print(f"Test Files: {testing['test_files']['total']}")
    print(f"Testing Frameworks: {testing['testing_frameworks']}")
    print(f"Has CI Config: {testing['has_ci_config']}")
    print()
    
    # Performance overview
    performance = analysis_results["performance_patterns"]
    print("PERFORMANCE OVERVIEW")
    print("-" * 40)
    print(f"Async Patterns: {performance['async_patterns']}")
    print(f"Caching Implementations: {performance['caching_implementations']}")
    print(f"Database Connections: {performance['database_connections']}")
    print(f"Potential Bottlenecks: {len(performance['potential_bottlenecks'])}")
    print()
    
    # Security overview
    security = analysis_results["security_patterns"]
    print("SECURITY OVERVIEW")
    print("-" * 40)
    print(f"JWT Usage: {security['jwt_usage']}")
    print(f"Encryption Patterns: {security['encryption_patterns']}")
    print(f"Authentication Files: {len(security['authentication_files'])}")
    print(f"Potential Vulnerabilities: {len(security['potential_vulnerabilities'])}")
    print()
    
    return analysis_results

if __name__ == "__main__":
    main()