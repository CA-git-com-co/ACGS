#!/usr/bin/env python3
"""
ACGS Performance Regression Detection System
Monitors for cache hit rates <85% and performance degradation

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import requests
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class PerformanceRegressor:
    """Detects performance regressions in ACGS services"""
    
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.performance_targets = {
            "p99_latency_ms": 5.0,
            "cache_hit_rate": 0.85,
            "throughput_rps": 100.0,
            "error_rate": 0.01
        }
        
    def query_prometheus(self, query: str, time_range: str = "5m") -> List[Dict]:
        """Query Prometheus for metrics"""
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {"query": query}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    return data["data"]["result"]
            return []
        except Exception as e:
            print(f"❌ Prometheus query error: {e}")
            return []
    
    def query_prometheus_range(self, query: str, duration: str = "1h") -> List[Dict]:
        """Query Prometheus for time series data"""
        try:
            url = f"{self.prometheus_url}/api/v1/query_range"
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            params = {
                "query": query,
                "start": start_time.isoformat() + "Z",
                "end": end_time.isoformat() + "Z",
                "step": "30s"
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    return data["data"]["result"]
            return []
        except Exception as e:
            print(f"❌ Prometheus range query error: {e}")
            return []
    
    def check_latency_regression(self) -> Tuple[bool, Dict]:
        """Check for P99 latency regression"""
        print("⏱️  Checking P99 Latency Regression...")
        
        # Query current P99 latency
        query = 'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))'
        results = self.query_prometheus(query)
        
        regressions = []
        healthy_services = 0
        
        for result in results:
            instance = result["metric"].get("instance", "unknown")
            latency_seconds = float(result["value"][1])
            latency_ms = latency_seconds * 1000
            
            target_ms = self.performance_targets["p99_latency_ms"]
            
            if latency_ms > target_ms:
                regressions.append({
                    "service": instance,
                    "metric": "p99_latency",
                    "current": latency_ms,
                    "target": target_ms,
                    "severity": "critical" if latency_ms > target_ms * 2 else "warning"
                })
                print(f"⚠️  {instance}: {latency_ms:.2f}ms (target: {target_ms}ms)")
            else:
                healthy_services += 1
                print(f"✅ {instance}: {latency_ms:.2f}ms")
        
        return len(regressions) == 0, {
            "regressions": regressions,
            "healthy_services": healthy_services,
            "total_services": len(results)
        }
    
    def check_cache_regression(self) -> Tuple[bool, Dict]:
        """Check for cache hit rate regression"""
        print("\n💾 Checking Cache Hit Rate Regression...")
        
        # Query cache hit rates
        queries = [
            'acgs_cache_hit_rate',
            'rate(acgs_cache_hits_total[5m]) / rate(acgs_cache_requests_total[5m])'
        ]
        
        regressions = []
        healthy_services = 0
        all_results = []
        
        for query in queries:
            results = self.query_prometheus(query)
            all_results.extend(results)
        
        for result in all_results:
            instance = result["metric"].get("instance", "unknown")
            hit_rate = float(result["value"][1])
            
            target_rate = self.performance_targets["cache_hit_rate"]
            
            if hit_rate < target_rate:
                regressions.append({
                    "service": instance,
                    "metric": "cache_hit_rate",
                    "current": hit_rate,
                    "target": target_rate,
                    "severity": "critical" if hit_rate < target_rate * 0.8 else "warning"
                })
                print(f"⚠️  {instance}: {hit_rate:.1%} (target: {target_rate:.1%})")
            else:
                healthy_services += 1
                print(f"✅ {instance}: {hit_rate:.1%}")
        
        return len(regressions) == 0, {
            "regressions": regressions,
            "healthy_services": healthy_services,
            "total_services": len(all_results)
        }
    
    def check_throughput_regression(self) -> Tuple[bool, Dict]:
        """Check for throughput regression"""
        print("\n🚀 Checking Throughput Regression...")
        
        # Query request rates
        query = 'rate(http_requests_total[5m])'
        results = self.query_prometheus(query)
        
        regressions = []
        healthy_services = 0
        
        for result in results:
            instance = result["metric"].get("instance", "unknown")
            rps = float(result["value"][1])
            
            target_rps = self.performance_targets["throughput_rps"]
            
            if rps < target_rps:
                regressions.append({
                    "service": instance,
                    "metric": "throughput_rps",
                    "current": rps,
                    "target": target_rps,
                    "severity": "critical" if rps < target_rps * 0.5 else "warning"
                })
                print(f"⚠️  {instance}: {rps:.1f} RPS (target: {target_rps} RPS)")
            else:
                healthy_services += 1
                print(f"✅ {instance}: {rps:.1f} RPS")
        
        return len(regressions) == 0, {
            "regressions": regressions,
            "healthy_services": healthy_services,
            "total_services": len(results)
        }
    
    def check_constitutional_compliance_regression(self) -> Tuple[bool, Dict]:
        """Check for constitutional compliance regression"""
        print("\n⚖️  Checking Constitutional Compliance Regression...")
        
        # Check constitutional hash validation
        services = [
            ("Constitutional AI", 8001),
            ("Integrity Service", 8002),
            ("Formal Verification", 8003),
            ("Governance Synthesis", 8004),
            ("Policy Governance", 8005),
            ("Evolutionary Computation", 8006),
            ("Code Analysis", 8007),
            ("Context Service", 8012),
            ("Authentication", 8016)
        ]
        
        regressions = []
        compliant_services = 0
        
        for service_name, port in services:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    constitutional_hash = data.get("constitutional_hash", "missing")
                    
                    if constitutional_hash != self.constitutional_hash:
                        regressions.append({
                            "service": service_name,
                            "metric": "constitutional_hash",
                            "current": constitutional_hash,
                            "target": self.constitutional_hash,
                            "severity": "critical"
                        })
                        print(f"🚨 {service_name}: Hash mismatch ({constitutional_hash})")
                    else:
                        compliant_services += 1
                        print(f"✅ {service_name}: Constitutional compliance OK")
                else:
                    regressions.append({
                        "service": service_name,
                        "metric": "service_availability",
                        "current": "down",
                        "target": "up",
                        "severity": "critical"
                    })
                    print(f"❌ {service_name}: Service unavailable")
            except Exception as e:
                regressions.append({
                    "service": service_name,
                    "metric": "service_connectivity",
                    "current": "error",
                    "target": "connected",
                    "severity": "critical"
                })
                print(f"❌ {service_name}: Connection error")
        
        return len(regressions) == 0, {
            "regressions": regressions,
            "compliant_services": compliant_services,
            "total_services": len(services)
        }
    
    def generate_regression_report(self, results: Dict) -> str:
        """Generate a comprehensive regression report"""
        report = []
        report.append("📊 ACGS PERFORMANCE REGRESSION REPORT")
        report.append("=" * 80)
        report.append(f"Constitutional Hash: {self.constitutional_hash}")
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")
        
        total_regressions = 0
        critical_regressions = 0
        
        for check_name, (healthy, data) in results.items():
            report.append(f"🔍 {check_name.upper()}")
            report.append("-" * 40)
            
            if healthy:
                report.append("✅ No regressions detected")
            else:
                regressions = data.get("regressions", [])
                total_regressions += len(regressions)
                
                for regression in regressions:
                    if regression["severity"] == "critical":
                        critical_regressions += 1
                        icon = "🚨"
                    else:
                        icon = "⚠️ "
                    
                    report.append(f"{icon} {regression['service']}: {regression['metric']}")
                    report.append(f"   Current: {regression['current']}")
                    report.append(f"   Target:  {regression['target']}")
            
            report.append("")
        
        # Summary
        report.append("📈 REGRESSION SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Regressions: {total_regressions}")
        report.append(f"Critical Regressions: {critical_regressions}")
        report.append(f"Warning Regressions: {total_regressions - critical_regressions}")
        
        if total_regressions == 0:
            report.append("✅ SYSTEM PERFORMANCE HEALTHY")
        elif critical_regressions > 0:
            report.append("🚨 CRITICAL PERFORMANCE ISSUES DETECTED")
        else:
            report.append("⚠️  PERFORMANCE WARNINGS DETECTED")
        
        return "\n".join(report)
    
    def run_regression_detection(self) -> bool:
        """Run complete regression detection"""
        print("🔍 ACGS Performance Regression Detection")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("=" * 80)
        
        checks = {
            "Latency Check": self.check_latency_regression,
            "Cache Check": self.check_cache_regression,
            "Throughput Check": self.check_throughput_regression,
            "Constitutional Compliance": self.check_constitutional_compliance_regression
        }
        
        results = {}
        for check_name, check_func in checks.items():
            results[check_name] = check_func()
        
        # Generate and save report
        report = self.generate_regression_report(results)
        print(f"\n{report}")
        
        # Save report to file
        with open("performance_regression_report.txt", "w") as f:
            f.write(report)
        
        # Return overall health status
        all_healthy = all(healthy for healthy, _ in results.values())
        return all_healthy


def main():
    """Main function"""
    detector = PerformanceRegressor()
    healthy = detector.run_regression_detection()
    
    if healthy:
        print("\n✅ NO PERFORMANCE REGRESSIONS DETECTED")
        exit(0)
    else:
        print("\n⚠️  PERFORMANCE REGRESSIONS DETECTED")
        print("📄 Report saved to: performance_regression_report.txt")
        exit(1)


if __name__ == "__main__":
    main()
