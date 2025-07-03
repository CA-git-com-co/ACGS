#!/usr/bin/env python3
"""
ACGS Performance Monitoring System

Continuous performance validation with automated monitoring of P99 latency,
cache hit rates, and other critical performance metrics.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime, timedelta


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: str
    service_name: str
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_latency_ms: float
    cache_hit_rate: Optional[float] = None
    throughput_rps: Optional[float] = None
    error_rate: Optional[float] = None
    constitutional_compliance: Optional[float] = None


@dataclass
class PerformanceTargets:
    """Performance targets for validation."""
    p99_latency_ms: float = 5.0
    cache_hit_rate: float = 0.85
    throughput_rps: float = 100.0
    error_rate: float = 0.01
    constitutional_compliance: float = 0.95


class ACGSPerformanceMonitor:
    """ACGS Performance Monitoring System."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.logger = self._setup_logging()
        self.targets = PerformanceTargets()
        
        # ACGS Services to monitor
        self.services = {
            "auth_service": "http://localhost:8016",
            "ac_service": "http://localhost:8001",
            "fv_service": "http://localhost:8003",
            "gs_service": "http://localhost:8004",
            "pgc_service": "http://localhost:8005",
        }
        
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.metrics_history: List[PerformanceMetrics] = []
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger(__name__)
    
    async def measure_service_latency(self, service_name: str, base_url: str, samples: int = 20) -> PerformanceMetrics:
        """Measure latency metrics for a service."""
        latencies = []
        errors = 0
        
        async with aiohttp.ClientSession() as session:
            for _ in range(samples):
                start_time = time.perf_counter()
                
                try:
                    async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                        end_time = time.perf_counter()
                        latency_ms = (end_time - start_time) * 1000
                        
                        if response.status == 200:
                            latencies.append(latency_ms)
                        else:
                            errors += 1
                            
                except Exception as e:
                    errors += 1
                    self.logger.warning(f"Error measuring {service_name}: {e}")
                
                # Small delay between requests
                await asyncio.sleep(0.01)
        
        if not latencies:
            # Return default metrics if all requests failed
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                service_name=service_name,
                p50_latency_ms=float('inf'),
                p95_latency_ms=float('inf'),
                p99_latency_ms=float('inf'),
                avg_latency_ms=float('inf'),
                error_rate=1.0
            )
        
        # Calculate percentiles
        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(0.95 * len(latencies))] if len(latencies) > 1 else latencies[0]
        p99 = latencies[int(0.99 * len(latencies))] if len(latencies) > 1 else latencies[0]
        avg = statistics.mean(latencies)
        error_rate = errors / samples
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            service_name=service_name,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            avg_latency_ms=avg,
            error_rate=error_rate
        )
    
    async def measure_cache_performance(self, service_name: str, base_url: str) -> Optional[float]:
        """Measure cache hit rate for a service."""
        try:
            async with aiohttp.ClientSession() as session:
                # Try to get cache metrics endpoint
                async with session.get(f"{base_url}/metrics", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Look for cache metrics in various formats
                        cache_hits = data.get('cache_hits', 0)
                        cache_misses = data.get('cache_misses', 0)
                        total_requests = cache_hits + cache_misses
                        
                        if total_requests > 0:
                            return cache_hits / total_requests
                        
        except Exception as e:
            self.logger.debug(f"Could not get cache metrics for {service_name}: {e}")
        
        return None
    
    async def measure_constitutional_compliance(self, service_name: str, base_url: str) -> Optional[float]:
        """Measure constitutional compliance rate."""
        try:
            async with aiohttp.ClientSession() as session:
                # Check constitutional compliance endpoint
                async with session.get(f"{base_url}/constitutional/status", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Look for compliance metrics
                        compliance_rate = data.get('compliance_rate')
                        if compliance_rate is not None:
                            return float(compliance_rate)
                        
                        # Check if constitutional hash matches
                        current_hash = data.get('constitutional_hash')
                        if current_hash == self.constitutional_hash:
                            return 1.0
                        
        except Exception as e:
            self.logger.debug(f"Could not get constitutional compliance for {service_name}: {e}")
        
        return None
    
    async def collect_all_metrics(self) -> List[PerformanceMetrics]:
        """Collect performance metrics from all services."""
        self.logger.info("📊 Collecting performance metrics from all services...")
        
        tasks = []
        for service_name, base_url in self.services.items():
            task = self.collect_service_metrics(service_name, base_url)
            tasks.append(task)
        
        metrics = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_metrics = []
        for metric in metrics:
            if isinstance(metric, PerformanceMetrics):
                valid_metrics.append(metric)
                self.metrics_history.append(metric)
            else:
                self.logger.error(f"Error collecting metrics: {metric}")
        
        return valid_metrics
    
    async def collect_service_metrics(self, service_name: str, base_url: str) -> PerformanceMetrics:
        """Collect comprehensive metrics for a single service."""
        # Measure latency
        metrics = await self.measure_service_latency(service_name, base_url)
        
        # Enhance with cache and compliance metrics
        cache_hit_rate = await self.measure_cache_performance(service_name, base_url)
        constitutional_compliance = await self.measure_constitutional_compliance(service_name, base_url)
        
        metrics.cache_hit_rate = cache_hit_rate
        metrics.constitutional_compliance = constitutional_compliance
        
        return metrics
    
    def validate_performance_targets(self, metrics: List[PerformanceMetrics]) -> Dict[str, bool]:
        """Validate metrics against performance targets."""
        validation_results = {}
        
        for metric in metrics:
            service_results = {
                "p99_latency": metric.p99_latency_ms <= self.targets.p99_latency_ms,
                "cache_hit_rate": (
                    metric.cache_hit_rate is None or 
                    metric.cache_hit_rate >= self.targets.cache_hit_rate
                ),
                "error_rate": (
                    metric.error_rate is None or 
                    metric.error_rate <= self.targets.error_rate
                ),
                "constitutional_compliance": (
                    metric.constitutional_compliance is None or 
                    metric.constitutional_compliance >= self.targets.constitutional_compliance
                )
            }
            
            validation_results[metric.service_name] = service_results
        
        return validation_results
    
    def generate_performance_report(self, metrics: List[PerformanceMetrics], validation: Dict[str, bool]) -> str:
        """Generate human-readable performance report."""
        lines = [
            "📊 ACGS Performance Monitoring Report",
            "=" * 50,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Constitutional Hash: {self.constitutional_hash}",
            "",
            "🎯 Performance Targets:",
            f"  P99 Latency: ≤{self.targets.p99_latency_ms}ms",
            f"  Cache Hit Rate: ≥{self.targets.cache_hit_rate*100:.1f}%",
            f"  Error Rate: ≤{self.targets.error_rate*100:.1f}%",
            f"  Constitutional Compliance: ≥{self.targets.constitutional_compliance*100:.1f}%",
            "",
            "📈 Service Performance:"
        ]
        
        for metric in metrics:
            service_validation = validation.get(metric.service_name, {})
            
            # Status indicators
            p99_status = "✅" if service_validation.get("p99_latency", False) else "❌"
            cache_status = "✅" if service_validation.get("cache_hit_rate", True) else "❌"
            error_status = "✅" if service_validation.get("error_rate", True) else "❌"
            compliance_status = "✅" if service_validation.get("constitutional_compliance", True) else "❌"
            
            lines.extend([
                f"",
                f"  🔧 {metric.service_name}:",
                f"    {p99_status} P99 Latency: {metric.p99_latency_ms:.2f}ms",
                f"    {cache_status} Cache Hit Rate: {metric.cache_hit_rate*100:.1f}%" if metric.cache_hit_rate else "    ⚪ Cache Hit Rate: N/A",
                f"    {error_status} Error Rate: {metric.error_rate*100:.1f}%" if metric.error_rate else "    ⚪ Error Rate: N/A",
                f"    {compliance_status} Constitutional Compliance: {metric.constitutional_compliance*100:.1f}%" if metric.constitutional_compliance else "    ⚪ Constitutional Compliance: N/A"
            ])
        
        # Overall status
        all_services_healthy = all(
            all(service_results.values()) 
            for service_results in validation.values()
        )
        
        overall_status = "✅ ALL TARGETS MET" if all_services_healthy else "⚠️ SOME TARGETS MISSED"
        lines.extend([
            "",
            f"🏆 Overall Status: {overall_status}"
        ])
        
        return "\n".join(lines)
    
    async def run_monitoring_cycle(self) -> bool:
        """Run a complete monitoring cycle."""
        self.logger.info("🚀 Starting ACGS performance monitoring cycle...")
        
        # Collect metrics
        metrics = await self.collect_all_metrics()
        
        if not metrics:
            self.logger.error("No metrics collected")
            return False
        
        # Validate against targets
        validation = self.validate_performance_targets(metrics)
        
        # Generate report
        report = self.generate_performance_report(metrics, validation)
        print(report)
        
        # Save detailed data
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Save JSON data
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "targets": asdict(self.targets),
            "metrics": [asdict(m) for m in metrics],
            "validation": validation
        }
        
        with open(reports_dir / "performance_metrics.json", "w") as f:
            json.dump(metrics_data, f, indent=2)
        
        # Save text report
        with open(reports_dir / "performance_report.txt", "w") as f:
            f.write(report)
        
        # Return overall health status
        all_healthy = all(
            all(service_results.values()) 
            for service_results in validation.values()
        )
        
        return all_healthy


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS Performance Monitor")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    monitor = ACGSPerformanceMonitor(args.project_root)
    
    if args.continuous:
        print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
        while True:
            success = await monitor.run_monitoring_cycle()
            if not success:
                print("⚠️ Monitoring cycle failed")
            
            await asyncio.sleep(args.interval)
    else:
        success = await monitor.run_monitoring_cycle()
        return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
