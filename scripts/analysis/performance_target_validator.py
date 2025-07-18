#!/usr/bin/env python3

"""
ACGS-2 Performance Target Validator
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Constitutional Performance Targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,  # P99 latency must be <5ms
    "throughput_rps": 100.0,  # Throughput must be >100 RPS
    "cache_hit_rate": 0.85,  # Cache hit rate must be >85%
    "constitutional_compliance": 1.0  # Must be 100%
}

def analyze_performance_implementations() -> Dict[str, Any]:
    """Analyze performance-related implementations in the codebase."""
    analysis = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "performance_implementations": {
            "async_operations": 0,
            "caching_layers": 0,
            "connection_pooling": 0,
            "performance_monitoring": 0,
            "latency_tracking": 0,
            "throughput_monitoring": 0
        },
        "constitutional_validations": {
            "performance_target_files": [],
            "constitutional_hash_usage": 0,
            "performance_middleware": 0
        },
        "optimization_patterns": {
            "database_optimizations": 0,
            "memory_optimizations": 0,
            "network_optimizations": 0
        },
        "potential_improvements": []
    }
    
    # Search for performance-related patterns
    performance_patterns = {
        "async_operations": [r'\basync\s+def\b', r'\bawait\b', r'\basyncio\b'],
        "caching_layers": [r'@cache', r'@lru_cache', r'redis', r'memcache', r'cache\.'],
        "connection_pooling": [r'ConnectionPool', r'create_engine', r'pool_size', r'max_connections'],
        "performance_monitoring": [r'track_performance', r'measure_time', r'timer', r'latency'],
        "latency_tracking": [r'latency', r'response_time', r'duration', r'p99', r'p95'],
        "throughput_monitoring": [r'throughput', r'rps', r'requests_per_second', r'rate_limit']
    }
    
    # Search for constitutional compliance patterns
    constitutional_patterns = {
        "constitutional_hash_usage": [CONSTITUTIONAL_HASH],
        "performance_middleware": [r'performance.*middleware', r'latency.*middleware'],
        "performance_targets": [r'P99.*<.*5ms', r'100.*RPS', r'85%.*cache', r'5ms.*latency']
    }
    
    # Scan Python files for performance patterns
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Count performance patterns
            for pattern_type, patterns in performance_patterns.items():
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    analysis["performance_implementations"][pattern_type] += matches
            
            # Count constitutional compliance patterns
            for pattern_type, patterns in constitutional_patterns.items():
                for pattern in patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    if pattern_type == "performance_targets" and matches > 0:
                        analysis["constitutional_validations"]["performance_target_files"].append(str(py_file))
                    else:
                        analysis["constitutional_validations"][pattern_type] += matches
                        
        except Exception:
            continue
    
    return analysis

def analyze_monitoring_configurations() -> Dict[str, Any]:
    """Analyze monitoring and metrics configurations."""
    monitoring_analysis = {
        "prometheus_configs": [],
        "grafana_configs": [],
        "performance_dashboards": [],
        "alert_rules": []
    }
    
    # Find monitoring configuration files
    monitoring_files = [
        "prometheus*.yml",
        "grafana*.yml", 
        "alert*.yml",
        "dashboard*.yml"
    ]
    
    for pattern in monitoring_files:
        for config_file in Path('.').rglob(pattern):
            if any(exclude in str(config_file) for exclude in ['.git', '__pycache__']):
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check for performance-related metrics
                if 'prometheus' in pattern:
                    monitoring_analysis["prometheus_configs"].append({
                        "file": str(config_file),
                        "has_latency_metrics": "latency" in content.lower(),
                        "has_throughput_metrics": "throughput" in content.lower() or "rps" in content.lower(),
                        "has_cache_metrics": "cache" in content.lower(),
                        "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                    })
                elif 'grafana' in pattern or 'dashboard' in pattern:
                    monitoring_analysis["grafana_configs"].append({
                        "file": str(config_file),
                        "has_performance_panels": any(term in content.lower() for term in ["latency", "throughput", "cache"]),
                        "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                    })
                elif 'alert' in pattern:
                    monitoring_analysis["alert_rules"].append({
                        "file": str(config_file),
                        "has_performance_alerts": any(term in content.lower() for term in ["latency", "throughput", "cache"]),
                        "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                    })
                    
            except Exception:
                continue
    
    return monitoring_analysis

def validate_constitutional_performance() -> Dict[str, Any]:
    """Validate constitutional performance target implementations."""
    validation_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "targets_validation": {},
        "implementation_status": {},
        "recommendations": []
    }
    
    # Check for performance target validations in code
    target_implementations = {
        "p99_latency_validation": 0,
        "throughput_validation": 0,
        "cache_hit_validation": 0,
        "constitutional_compliance_validation": 0
    }
    
    # Search for target validation implementations
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for performance target validations
            if re.search(r'p99.*[<].*5|latency.*[<].*5', content, re.IGNORECASE):
                target_implementations["p99_latency_validation"] += 1
            if re.search(r'throughput.*[>].*100|rps.*[>].*100', content, re.IGNORECASE):
                target_implementations["throughput_validation"] += 1
            if re.search(r'cache.*hit.*[>].*85|cache.*[>].*0\.85', content, re.IGNORECASE):
                target_implementations["cache_hit_validation"] += 1
            if CONSTITUTIONAL_HASH in content:
                target_implementations["constitutional_compliance_validation"] += 1
                
        except Exception:
            continue
    
    validation_results["targets_validation"] = target_implementations
    
    # Generate recommendations
    recommendations = []
    
    if target_implementations["p99_latency_validation"] < 5:
        recommendations.append("CRITICAL: Implement P99 latency validation (<5ms) in more services")
    if target_implementations["throughput_validation"] < 5:
        recommendations.append("HIGH: Implement throughput validation (>100 RPS) in more services")
    if target_implementations["cache_hit_validation"] < 5:
        recommendations.append("MEDIUM: Implement cache hit rate validation (>85%) in more services")
    if target_implementations["constitutional_compliance_validation"] < 100:
        recommendations.append("LOW: Ensure constitutional hash is present in all performance-critical files")
    
    validation_results["recommendations"] = recommendations
    
    return validation_results

def main():
    """Main analysis function."""
    print("Analyzing ACGS-2 Performance Target Compliance...")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Performance Targets: P99 <5ms, >100 RPS, >85% cache hit")
    print()
    
    # Run analysis
    performance_analysis = analyze_performance_implementations()
    monitoring_analysis = analyze_monitoring_configurations()
    constitutional_validation = validate_constitutional_performance()
    
    # Combine results
    analysis_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "performance_targets": PERFORMANCE_TARGETS,
        "performance_analysis": performance_analysis,
        "monitoring_analysis": monitoring_analysis,
        "constitutional_validation": constitutional_validation
    }
    
    # Save results
    output_file = "performance_target_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"Analysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("PERFORMANCE TARGET VALIDATION SUMMARY")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Performance implementations
    perf_impl = performance_analysis["performance_implementations"]
    print("PERFORMANCE IMPLEMENTATIONS")
    print("-" * 40)
    print(f"Async Operations: {perf_impl['async_operations']}")
    print(f"Caching Layers: {perf_impl['caching_layers']}")
    print(f"Connection Pooling: {perf_impl['connection_pooling']}")
    print(f"Performance Monitoring: {perf_impl['performance_monitoring']}")
    print(f"Latency Tracking: {perf_impl['latency_tracking']}")
    print(f"Throughput Monitoring: {perf_impl['throughput_monitoring']}")
    print()
    
    # Constitutional validation
    const_val = constitutional_validation["targets_validation"]
    print("CONSTITUTIONAL TARGET VALIDATION")
    print("-" * 40)
    print(f"P99 Latency Validation: {const_val['p99_latency_validation']} implementations")
    print(f"Throughput Validation: {const_val['throughput_validation']} implementations")
    print(f"Cache Hit Validation: {const_val['cache_hit_validation']} implementations")
    print(f"Constitutional Hash Usage: {const_val['constitutional_compliance_validation']} files")
    print()
    
    # Monitoring
    mon_configs = monitoring_analysis
    print("MONITORING CONFIGURATIONS")
    print("-" * 40)
    print(f"Prometheus Configs: {len(mon_configs['prometheus_configs'])}")
    print(f"Grafana Configs: {len(mon_configs['grafana_configs'])}")
    print(f"Alert Rules: {len(mon_configs['alert_rules'])}")
    print()
    
    # Recommendations
    recommendations = constitutional_validation["recommendations"]
    if recommendations:
        print("RECOMMENDATIONS")
        print("-" * 40)
        for rec in recommendations:
            print(f"• {rec}")
    else:
        print("✅ All performance targets are well-implemented!")
    
    print()
    
    return analysis_results

if __name__ == "__main__":
    main()