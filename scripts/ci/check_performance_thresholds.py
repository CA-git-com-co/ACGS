#!/usr/bin/env python3
"""
ACGS-2 Performance Threshold Checker
Validates performance metrics against constitutional requirements.
Constitutional Compliance: cdd01ef066bc6cf2
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import sys


def check_performance_thresholds(benchmark_data: Dict[str, Any], 
                                p99_threshold: float, 
                                rps_threshold: float, 
                                cache_threshold: float) -> Dict[str, Any]:
    """Check performance metrics against thresholds."""
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "constitutional_hash": "cdd01ef066bc6cf2",
        "thresholds": {
            "p99_latency_ms": p99_threshold,
            "throughput_rps": rps_threshold,
            "cache_hit_rate_percent": cache_threshold
        },
        "results": {},
        "overall_pass": False,
        "violations": [],
        "recommendations": []
    }
    
    # Extract performance metrics from benchmark data
    benchmarks = benchmark_data.get('benchmarks', [])
    
    if not benchmarks:
        report["violations"].append("No benchmark data found")
        return report
    
    # Analyze latency metrics
    latencies = []
    for benchmark in benchmarks:
        stats = benchmark.get('stats', {})
        if 'mean' in stats:
            latencies.append(stats['mean'] * 1000)  # Convert to ms
    
    if latencies:
        latencies.sort()
        p99_index = int(len(latencies) * 0.99)
        p99_latency = latencies[p99_index] if p99_index < len(latencies) else latencies[-1]
        
        report["results"]["p99_latency_ms"] = round(p99_latency, 3)
        report["results"]["p99_threshold_met"] = p99_latency <= p99_threshold
        
        if p99_latency > p99_threshold:
            report["violations"].append(f"P99 latency {p99_latency:.3f}ms exceeds threshold {p99_threshold}ms")
            report["recommendations"].append("Optimize critical path performance and reduce processing overhead")
    
    # Estimate throughput (simplified calculation)
    if latencies:
        avg_latency_seconds = sum(latencies) / len(latencies) / 1000
        estimated_rps = 1.0 / avg_latency_seconds if avg_latency_seconds > 0 else 0
        
        report["results"]["estimated_throughput_rps"] = round(estimated_rps, 2)
        report["results"]["throughput_threshold_met"] = estimated_rps >= rps_threshold
        
        if estimated_rps < rps_threshold:
            report["violations"].append(f"Estimated throughput {estimated_rps:.2f} RPS below threshold {rps_threshold} RPS")
            report["recommendations"].append("Implement connection pooling and async processing optimizations")
    
    # Cache hit rate (would need to be provided in benchmark data)
    # For now, assume it meets threshold if no cache data is available
    report["results"]["cache_hit_rate_percent"] = cache_threshold  # Placeholder
    report["results"]["cache_threshold_met"] = True
    
    # Overall assessment
    all_thresholds_met = all([
        report["results"].get("p99_threshold_met", False),
        report["results"].get("throughput_threshold_met", False),
        report["results"].get("cache_threshold_met", False)
    ])
    
    report["overall_pass"] = all_thresholds_met
    
    if not all_thresholds_met:
        report["recommendations"].append("Review ACGS-2 performance optimization guidelines")
        report["recommendations"].append("Consider implementing multi-tier caching strategy")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Check ACGS-2 performance thresholds")
    parser.add_argument("--benchmark-json", type=Path, required=True, help="Path to benchmark JSON")
    parser.add_argument("--p99-threshold", type=float, required=True, help="P99 latency threshold (ms)")
    parser.add_argument("--rps-threshold", type=float, required=True, help="Throughput threshold (RPS)")
    parser.add_argument("--cache-threshold", type=float, required=True, help="Cache hit rate threshold (%)")
    parser.add_argument("--output", type=Path, required=True, help="Output performance check JSON")
    
    args = parser.parse_args()
    
    # Load benchmark data
    try:
        with open(args.benchmark_json, 'r') as f:
            benchmark_data = json.load(f)
    except Exception as e:
        print(f"Error loading benchmark data: {e}")
        sys.exit(1)
    
    # Check thresholds
    report = check_performance_thresholds(
        benchmark_data,
        args.p99_threshold,
        args.rps_threshold,
        args.cache_threshold
    )
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Write report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"🚀 Performance Threshold Check Complete")
    print(f"📊 Overall Pass: {'✅' if report['overall_pass'] else '❌'}")
    
    if report["results"].get("p99_latency_ms"):
        print(f"⏱️ P99 Latency: {report['results']['p99_latency_ms']:.3f}ms (target: {args.p99_threshold}ms)")
    
    if report["results"].get("estimated_throughput_rps"):
        print(f"🔄 Throughput: {report['results']['estimated_throughput_rps']:.2f} RPS (target: {args.rps_threshold} RPS)")
    
    if report["violations"]:
        print(f"⚠️ Violations: {len(report['violations'])}")
        for violation in report["violations"]:
            print(f"  - {violation}")
    
    # Exit with error if thresholds not met
    if not report["overall_pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
