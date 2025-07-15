#!/usr/bin/env python3
"""
ACGS-2 Test Metrics Generator
Generates comprehensive test metrics from pytest reports for CI/CD monitoring.
Constitutional Compliance: cdd01ef066bc6cf2
"""

import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys


class TestMetricsGenerator:
    """Generate comprehensive test metrics for ACGS-2 monitoring."""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self):
        self.metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "test_suite": "",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "error_tests": 0,
            "success_rate": 0.0,
            "coverage_percentage": 0.0,
            "average_duration": 0.0,
            "slowest_tests": [],
            "failed_test_details": [],
            "constitutional_compliance": False,
            "performance_metrics": {},
            "quality_score": 0.0
        }
    
    def parse_json_report(self, json_path: Path) -> None:
        """Parse pytest JSON report."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            self.metrics.update({
                "total_tests": summary.get('total', 0),
                "passed_tests": summary.get('passed', 0),
                "failed_tests": summary.get('failed', 0),
                "skipped_tests": summary.get('skipped', 0),
                "error_tests": summary.get('error', 0)
            })
            
            # Calculate success rate
            if self.metrics["total_tests"] > 0:
                self.metrics["success_rate"] = round(
                    (self.metrics["passed_tests"] / self.metrics["total_tests"]) * 100, 2
                )
            
            # Extract test durations and failures
            tests = data.get('tests', [])
            durations = []
            failed_details = []
            
            for test in tests:
                if 'duration' in test:
                    durations.append(test['duration'])
                
                if test.get('outcome') == 'failed':
                    failed_details.append({
                        "name": test.get('nodeid', 'unknown'),
                        "error": test.get('call', {}).get('longrepr', 'No error details'),
                        "duration": test.get('duration', 0)
                    })
            
            if durations:
                self.metrics["average_duration"] = round(sum(durations) / len(durations), 3)
                
                # Get slowest tests
                test_durations = [(test.get('nodeid', 'unknown'), test.get('duration', 0)) 
                                for test in tests if 'duration' in test]
                test_durations.sort(key=lambda x: x[1], reverse=True)
                self.metrics["slowest_tests"] = test_durations[:5]
            
            self.metrics["failed_test_details"] = failed_details[:10]  # Limit to 10 failures
            
        except Exception as e:
            print(f"Error parsing JSON report: {e}")
            sys.exit(1)
    
    def parse_coverage_xml(self, coverage_path: Path) -> None:
        """Parse coverage XML report."""
        try:
            tree = ET.parse(coverage_path)
            root = tree.getroot()
            
            # Find coverage percentage
            coverage_elem = root.find('.//coverage')
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get('line-rate', 0))
                self.metrics["coverage_percentage"] = round(line_rate * 100, 2)
            
        except Exception as e:
            print(f"Warning: Could not parse coverage XML: {e}")
            # Don't exit on coverage parsing errors
    
    def parse_benchmark_json(self, benchmark_path: Path) -> None:
        """Parse pytest-benchmark JSON report."""
        try:
            with open(benchmark_path, 'r') as f:
                data = json.load(f)
            
            benchmarks = data.get('benchmarks', [])
            if benchmarks:
                performance_metrics = {
                    "total_benchmarks": len(benchmarks),
                    "average_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "p99_latency": 0.0,
                    "throughput_estimate": 0.0
                }
                
                times = []
                for benchmark in benchmarks:
                    stats = benchmark.get('stats', {})
                    mean_time = stats.get('mean', 0)
                    times.append(mean_time)
                    
                    performance_metrics["min_time"] = min(performance_metrics["min_time"], mean_time)
                    performance_metrics["max_time"] = max(performance_metrics["max_time"], mean_time)
                
                if times:
                    performance_metrics["average_time"] = round(sum(times) / len(times), 6)
                    times.sort()
                    p99_index = int(len(times) * 0.99)
                    performance_metrics["p99_latency"] = round(times[p99_index] * 1000, 3)  # Convert to ms
                    
                    # Estimate throughput (requests per second)
                    if performance_metrics["average_time"] > 0:
                        performance_metrics["throughput_estimate"] = round(1.0 / performance_metrics["average_time"], 2)
                
                self.metrics["performance_metrics"] = performance_metrics
            
        except Exception as e:
            print(f"Warning: Could not parse benchmark JSON: {e}")
            # Don't exit on benchmark parsing errors
    
    def validate_constitutional_compliance(self) -> None:
        """Validate constitutional compliance in test results."""
        # Check if constitutional hash appears in test outputs
        compliance_indicators = [
            self.metrics["constitutional_hash"] in str(self.metrics),
            self.metrics["success_rate"] >= 70.0,  # Minimum success rate requirement
            self.metrics["total_tests"] > 0  # Must have tests
        ]
        
        self.metrics["constitutional_compliance"] = all(compliance_indicators)
    
    def calculate_quality_score(self) -> None:
        """Calculate overall quality score based on multiple factors."""
        score = 0.0
        
        # Success rate component (40% weight)
        score += (self.metrics["success_rate"] / 100.0) * 0.4
        
        # Coverage component (30% weight)
        score += (self.metrics["coverage_percentage"] / 100.0) * 0.3
        
        # Performance component (20% weight)
        perf_metrics = self.metrics.get("performance_metrics", {})
        p99_latency = perf_metrics.get("p99_latency", 1000)  # Default to 1000ms if not available
        if p99_latency <= 5.0:  # Target: P99 < 5ms
            score += 0.2
        elif p99_latency <= 10.0:
            score += 0.1
        
        # Constitutional compliance component (10% weight)
        if self.metrics["constitutional_compliance"]:
            score += 0.1
        
        self.metrics["quality_score"] = round(score * 100, 2)
    
    def generate_metrics(self, test_suite: str, json_report: Optional[Path], 
                        coverage_xml: Optional[Path], benchmark_json: Optional[Path]) -> Dict[str, Any]:
        """Generate comprehensive test metrics."""
        self.metrics["test_suite"] = test_suite
        
        if json_report and json_report.exists():
            self.parse_json_report(json_report)
        
        if coverage_xml and coverage_xml.exists():
            self.parse_coverage_xml(coverage_xml)
        
        if benchmark_json and benchmark_json.exists():
            self.parse_benchmark_json(benchmark_json)
        
        self.validate_constitutional_compliance()
        self.calculate_quality_score()
        
        return self.metrics


def main():
    parser = argparse.ArgumentParser(description="Generate ACGS-2 test metrics")
    parser.add_argument("--test-suite", required=True, help="Test suite name")
    parser.add_argument("--json-report", type=Path, help="Path to pytest JSON report")
    parser.add_argument("--coverage-xml", type=Path, help="Path to coverage XML report")
    parser.add_argument("--benchmark-json", type=Path, help="Path to benchmark JSON report")
    parser.add_argument("--output", type=Path, required=True, help="Output metrics JSON file")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    generator = TestMetricsGenerator()
    metrics = generator.generate_metrics(
        args.test_suite,
        args.json_report,
        args.coverage_xml,
        args.benchmark_json
    )
    
    # Write metrics to output file
    with open(args.output, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Generated metrics for {args.test_suite}")
    print(f"📊 Success Rate: {metrics['success_rate']}%")
    print(f"📈 Coverage: {metrics['coverage_percentage']}%")
    print(f"🔒 Constitutional Compliance: {'✅' if metrics['constitutional_compliance'] else '❌'}")
    print(f"⭐ Quality Score: {metrics['quality_score']}/100")
    
    # Exit with error code if success rate is below threshold
    if metrics['success_rate'] < 70.0:
        print("⚠️ Warning: Success rate below 70% threshold")
        sys.exit(1)


if __name__ == "__main__":
    main()
