#!/usr/bin/env python3
"""
ACGS-1 Lite Prometheus Metrics Integration
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import time
from datetime import datetime

import httpx
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)


class PolicyEngineMetricsCollector:
    """Collect and export policy engine metrics to Prometheus"""

    def __init__(
        self,
        policy_engine_url: str = "http://localhost:8004",
        prometheus_url: str = "http://localhost:9090",
    ):
        self.policy_engine_url = policy_engine_url
        self.prometheus_url = prometheus_url
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Create custom registry
        self.registry = CollectorRegistry()

        # Define metrics
        self.setup_metrics()

        # Historical data for trend analysis
        self.historical_data = []
        self.max_history_points = 1440  # 24 hours at 1-minute intervals

    def setup_metrics(self):
        """Initialize Prometheus metrics"""
        # Policy evaluation metrics
        self.policy_evaluations_total = Counter(
            "acgs_policy_evaluations_total",
            "Total number of policy evaluations",
            ["type", "action", "result"],
            registry=self.registry,
        )

        self.policy_evaluation_duration = Histogram(
            "acgs_policy_evaluation_duration_seconds",
            "Time spent on policy evaluation",
            ["type", "cache_hit"],
            registry=self.registry,
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ),
        )

        # Performance metrics
        self.latency_percentiles = Gauge(
            "acgs_latency_percentile_seconds",
            "Latency percentiles",
            ["percentile"],
            registry=self.registry,
        )

        self.requests_per_second = Gauge(
            "acgs_requests_per_second",
            "Current requests per second",
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hit_rate = Gauge(
            "acgs_cache_hit_rate",
            "Cache hit rate (0-1)",
            ["tier"],
            registry=self.registry,
        )

        self.cache_size = Gauge(
            "acgs_cache_size", "Current cache size", ["tier"], registry=self.registry
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_rate = Gauge(
            "acgs_constitutional_compliance_rate",
            "Rate of constitutional compliance (0-1)",
            registry=self.registry,
        )

        self.safety_violations_total = Counter(
            "acgs_safety_violations_total",
            "Total number of safety violations detected",
            ["violation_type"],
            registry=self.registry,
        )

        # Service health metrics
        self.service_health = Gauge(
            "acgs_service_health",
            "Service health status (1=healthy, 0=unhealthy)",
            registry=self.registry,
        )

        self.constitutional_hash_info = Info(
            "acgs_constitutional_hash",
            "Current constitutional hash",
            registry=self.registry,
        )

        # SLO target metrics
        self.slo_target_met = Gauge(
            "acgs_slo_target_met",
            "Whether SLO targets are being met (1=met, 0=not met)",
            ["target"],
            registry=self.registry,
        )

        # Batch processing metrics
        self.batch_size = Histogram(
            "acgs_batch_size",
            "Size of request batches",
            registry=self.registry,
            buckets=(1, 2, 5, 10, 20, 50, 100),
        )

        self.partial_evaluation_rate = Gauge(
            "acgs_partial_evaluation_rate",
            "Rate of partial evaluations (0-1)",
            registry=self.registry,
        )

    async def collect_policy_engine_metrics(self) -> dict | None:
        """Collect metrics from policy engine service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.policy_engine_url}/v1/metrics")
                if response.status_code == 200:
                    return response.json()
                print(f"Failed to collect metrics: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return None

    async def collect_health_metrics(self) -> dict | None:
        """Collect health information from policy engine"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.policy_engine_url}/v1/data/acgs/main/health"
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Error collecting health metrics: {e}")
            return None

    def update_prometheus_metrics(self, metrics: dict, health: dict | None = None):
        """Update Prometheus metrics with collected data"""
        timestamp = time.time()

        # Update latency percentiles
        percentiles = metrics.get("percentiles", {})
        for percentile, value in percentiles.items():
            self.latency_percentiles.labels(percentile=percentile).set(
                value / 1000
            )  # Convert to seconds

        # Update performance metrics
        if "avg_latency_ms" in metrics:
            avg_latency_seconds = metrics["avg_latency_ms"] / 1000
            self.policy_evaluation_duration.labels(
                type="average", cache_hit="mixed"
            ).observe(avg_latency_seconds)

        # Calculate RPS from request count and time (simple estimation)
        request_count = metrics.get("request_count", 0)
        if hasattr(self, "_last_request_count") and hasattr(self, "_last_timestamp"):
            time_diff = timestamp - self._last_timestamp
            if time_diff > 0:
                rps = (request_count - self._last_request_count) / time_diff
                self.requests_per_second.set(max(0, rps))

        self._last_request_count = request_count
        self._last_timestamp = timestamp

        # Update cache metrics
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        l1_hit_rate = metrics.get("l1_hit_rate", 0)
        l2_hit_rate = metrics.get("l2_hit_rate", 0)

        self.cache_hit_rate.labels(tier="overall").set(cache_hit_rate)
        self.cache_hit_rate.labels(tier="l1").set(l1_hit_rate)
        self.cache_hit_rate.labels(tier="l2").set(l2_hit_rate)

        # Update partial evaluation rate
        partial_eval_rate = metrics.get("partial_eval_rate", 0)
        self.partial_evaluation_rate.set(partial_eval_rate)

        # Update batch metrics
        batch_stats = metrics.get("batch_stats", {})
        avg_batch_size = batch_stats.get("avg_batch_size", 0)
        if avg_batch_size > 0:
            self.batch_size.observe(avg_batch_size)

        # Update SLO target metrics
        targets_met = metrics.get("targets_met", {})
        for target, met in targets_met.items():
            self.slo_target_met.labels(target=target).set(1 if met else 0)

        # Update health metrics
        if health:
            health_status = 1 if health.get("status") == "healthy" else 0
            self.service_health.set(health_status)

            constitutional_hash = health.get("constitutional_hash", "")
            if constitutional_hash:
                self.constitutional_hash_info.info(
                    {
                        "hash": constitutional_hash,
                        "version": health.get("version", "unknown"),
                    }
                )

        # Store historical data
        self.historical_data.append(
            {
                "timestamp": timestamp,
                "metrics": metrics.copy(),
                "health": health.copy() if health else None,
            }
        )

        # Trim historical data
        if len(self.historical_data) > self.max_history_points:
            self.historical_data = self.historical_data[-self.max_history_points :]

    def analyze_performance_trends(self, window_minutes: int = 30) -> dict:
        """Analyze performance trends over time window"""
        if not self.historical_data:
            return {"error": "No historical data available"}

        cutoff_time = time.time() - (window_minutes * 60)
        recent_data = [d for d in self.historical_data if d["timestamp"] >= cutoff_time]

        if len(recent_data) < 2:
            return {"error": "Insufficient data for trend analysis"}

        # Extract metrics over time
        latencies = []
        cache_hit_rates = []
        request_counts = []

        for data_point in recent_data:
            metrics = data_point["metrics"]
            percentiles = metrics.get("percentiles", {})
            if "p99" in percentiles:
                latencies.append(percentiles["p99"])

            cache_hit_rates.append(metrics.get("cache_hit_rate", 0))
            request_counts.append(metrics.get("request_count", 0))

        # Calculate trends
        trends = {}

        if latencies:
            first_latency = latencies[0]
            last_latency = latencies[-1]
            trends["latency_trend"] = {
                "direction": (
                    "improving"
                    if last_latency < first_latency
                    else "degrading" if last_latency > first_latency else "stable"
                ),
                "change_percent": (
                    ((last_latency - first_latency) / first_latency * 100)
                    if first_latency > 0
                    else 0
                ),
                "current_p99_ms": last_latency,
                "window_min_ms": min(latencies),
                "window_max_ms": max(latencies),
            }

        if cache_hit_rates:
            current_cache_rate = cache_hit_rates[-1]
            avg_cache_rate = sum(cache_hit_rates) / len(cache_hit_rates)
            trends["cache_trend"] = {
                "current_rate": current_cache_rate,
                "average_rate": avg_cache_rate,
                "is_stable": abs(current_cache_rate - avg_cache_rate) < 0.05,
            }

        if len(request_counts) >= 2:
            first_count = request_counts[0]
            last_count = request_counts[-1]
            time_span = recent_data[-1]["timestamp"] - recent_data[0]["timestamp"]

            if time_span > 0:
                avg_rps = (last_count - first_count) / time_span
                trends["throughput_trend"] = {
                    "avg_rps": avg_rps,
                    "total_requests": last_count - first_count,
                    "time_span_minutes": time_span / 60,
                }

        return trends

    def validate_slo_compliance(self, metrics: dict) -> dict:
        """Validate current metrics against SLO targets"""
        slo_results = {"compliant": True, "violations": [], "warnings": []}

        # P99 latency target: < 5ms
        percentiles = metrics.get("percentiles", {})
        p99_latency = percentiles.get("p99", 0)
        if p99_latency > 5.0:
            slo_results["compliant"] = False
            slo_results["violations"].append(
                f"P99 latency {p99_latency:.1f}ms exceeds 5ms target"
            )
        elif p99_latency > 3.0:
            slo_results["warnings"].append(
                f"P99 latency {p99_latency:.1f}ms approaching 5ms target"
            )

        # Average latency target: < 2ms
        avg_latency = metrics.get("avg_latency_ms", 0)
        if avg_latency > 2.0:
            slo_results["compliant"] = False
            slo_results["violations"].append(
                f"Average latency {avg_latency:.1f}ms exceeds 2ms target"
            )

        # Cache hit rate target: > 90%
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        if cache_hit_rate < 0.9:
            slo_results["compliant"] = False
            slo_results["violations"].append(
                f"Cache hit rate {cache_hit_rate:.1%} below 90% target"
            )
        elif cache_hit_rate < 0.95:
            slo_results["warnings"].append(
                f"Cache hit rate {cache_hit_rate:.1%} below optimal 95%"
            )

        # Request success rate (derived from error metrics if available)
        request_count = metrics.get("request_count", 0)
        if request_count > 100:  # Only check if we have sufficient data
            # This would need to be implemented based on actual error tracking
            pass

        return slo_results

    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus metrics output"""
        return generate_latest(self.registry).decode("utf-8")

    async def continuous_collection(self, interval_seconds: int = 60):
        """Continuously collect and update metrics"""
        print(f"Starting continuous metrics collection (interval: {interval_seconds}s)")
        print(f"Policy Engine: {self.policy_engine_url}")
        print(f"Constitutional Hash: {self.constitutional_hash}")

        while True:
            try:
                # Collect metrics
                metrics = await self.collect_policy_engine_metrics()
                health = await self.collect_health_metrics()

                if metrics:
                    # Update Prometheus metrics
                    self.update_prometheus_metrics(metrics, health)

                    # Validate SLOs
                    slo_results = self.validate_slo_compliance(metrics)

                    # Print status
                    p99 = metrics.get("percentiles", {}).get("p99", 0)
                    cache_rate = metrics.get("cache_hit_rate", 0)
                    request_count = metrics.get("request_count", 0)

                    status = "✅" if slo_results["compliant"] else "❌"
                    print(
                        f"{status} {datetime.now().strftime('%H:%M:%S')} - "
                        f"P99: {p99:.1f}ms, Cache: {cache_rate:.1%}, Requests: {request_count}"
                    )

                    # Print any violations or warnings
                    for violation in slo_results.get("violations", []):
                        print(f"   ❌ SLO Violation: {violation}")
                    for warning in slo_results.get("warnings", []):
                        print(f"   ⚠️  Warning: {warning}")

                else:
                    print(
                        f"❌ {datetime.now().strftime('%H:%M:%S')} - Failed to collect metrics"
                    )
                    self.service_health.set(0)

            except Exception as e:
                print(
                    f"❌ {datetime.now().strftime('%H:%M:%S')} - Collection error: {e}"
                )
                self.service_health.set(0)

            await asyncio.sleep(interval_seconds)


class MetricsValidationSuite:
    """Validation suite for metrics and SLO compliance"""

    def __init__(
        self,
        policy_engine_url: str = "http://localhost:8004",
        prometheus_url: str = "http://localhost:9090",
    ):
        self.policy_engine_url = policy_engine_url
        self.prometheus_url = prometheus_url
        self.collector = PolicyEngineMetricsCollector(policy_engine_url, prometheus_url)

    async def validate_metrics_availability(self) -> dict:
        """Validate that all expected metrics are available"""
        print("🔍 Validating metrics availability...")

        results = {
            "policy_engine_metrics": False,
            "health_endpoint": False,
            "prometheus_scraping": False,
            "details": {},
        }

        # Test policy engine metrics endpoint
        try:
            metrics = await self.collector.collect_policy_engine_metrics()
            if metrics:
                results["policy_engine_metrics"] = True
                results["details"]["policy_engine"] = {
                    "request_count": metrics.get("request_count", 0),
                    "avg_latency_ms": metrics.get("avg_latency_ms", 0),
                    "cache_hit_rate": metrics.get("cache_hit_rate", 0),
                }
                print(f"   ✅ Policy engine metrics: {len(metrics)} fields")
            else:
                results["details"]["policy_engine"] = "Failed to retrieve"
                print("   ❌ Policy engine metrics: unavailable")
        except Exception as e:
            results["details"]["policy_engine"] = str(e)
            print(f"   ❌ Policy engine metrics: {e}")

        # Test health endpoint
        try:
            health = await self.collector.collect_health_metrics()
            if health and health.get("status") == "healthy":
                results["health_endpoint"] = True
                results["details"]["health"] = health
                print(f"   ✅ Health endpoint: {health.get('status')}")
            else:
                results["details"]["health"] = health or "No response"
                print("   ❌ Health endpoint: unhealthy or unavailable")
        except Exception as e:
            results["details"]["health"] = str(e)
            print(f"   ❌ Health endpoint: {e}")

        # Test Prometheus scraping (if available)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.prometheus_url}/api/v1/query", params={"query": "up"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        results["prometheus_scraping"] = True
                        print("   ✅ Prometheus: accessible")
                    else:
                        print("   ⚠️  Prometheus: query failed")
                else:
                    print(f"   ⚠️  Prometheus: HTTP {response.status_code}")
        except Exception as e:
            results["details"]["prometheus"] = str(e)
            print(f"   ⚠️  Prometheus: {e}")

        return results

    async def run_performance_regression_test(self, duration_seconds: int = 30) -> dict:
        """Run a performance test and check for regressions"""
        print(f"🚀 Running {duration_seconds}s performance regression test...")

        # Generate load
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "regression_test",
                "explanation": "Performance regression test",
            },
        }

        latencies = []
        errors = 0
        start_time = time.time()

        async with httpx.AsyncClient(timeout=30.0) as client:
            while time.time() - start_time < duration_seconds:
                req_start = time.perf_counter_ns()
                try:
                    response = await client.post(
                        f"{self.policy_engine_url}/v1/data/acgs/main/decision",
                        json=test_request,
                    )
                    req_end = time.perf_counter_ns()

                    if response.status_code == 200:
                        latency_ms = (req_end - req_start) / 1_000_000
                        latencies.append(latency_ms)
                    else:
                        errors += 1
                except Exception:
                    errors += 1

                await asyncio.sleep(0.05)  # 50ms between requests

        # Analyze results
        if latencies:
            latencies.sort()
            n = len(latencies)

            results = {
                "total_requests": len(latencies) + errors,
                "successful_requests": len(latencies),
                "error_count": errors,
                "error_rate": errors / (len(latencies) + errors),
                "mean_latency_ms": sum(latencies) / len(latencies),
                "p95_latency_ms": latencies[int(0.95 * n)],
                "p99_latency_ms": latencies[int(0.99 * n)],
                "max_latency_ms": max(latencies),
            }

            # Check against targets
            results["slo_compliance"] = {
                "p99_under_5ms": results["p99_latency_ms"] < 5.0,
                "error_rate_under_1pct": results["error_rate"] < 0.01,
                "mean_under_2ms": results["mean_latency_ms"] < 2.0,
            }

            all_targets_met = all(results["slo_compliance"].values())
            results["passed"] = all_targets_met

            print(
                f"   📊 Results: {results['successful_requests']} requests in {duration_seconds}s"
            )
            print(
                f"   📈 P99: {results['p99_latency_ms']:.1f}ms, Mean: {results['mean_latency_ms']:.1f}ms"
            )
            print(
                f"   {'✅' if all_targets_met else '❌'} SLO Compliance: {all_targets_met}"
            )

            return results
        return {"error": "No successful requests", "passed": False}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ACGS-1 Lite Prometheus Metrics")
    parser.add_argument(
        "--mode",
        choices=["collect", "validate", "test"],
        default="collect",
        help="Operation mode",
    )
    parser.add_argument(
        "--policy-url", default="http://localhost:8004", help="Policy engine URL"
    )
    parser.add_argument(
        "--prometheus-url", default="http://localhost:9090", help="Prometheus URL"
    )
    parser.add_argument(
        "--interval", type=int, default=60, help="Collection interval in seconds"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Test duration in seconds"
    )

    args = parser.parse_args()

    async def main():
        if args.mode == "collect":
            collector = PolicyEngineMetricsCollector(
                args.policy_url, args.prometheus_url
            )
            await collector.continuous_collection(args.interval)

        elif args.mode == "validate":
            validator = MetricsValidationSuite(args.policy_url, args.prometheus_url)
            results = await validator.validate_metrics_availability()

            if all([results["policy_engine_metrics"], results["health_endpoint"]]):
                print("\n✅ All critical metrics are available")
                exit(0)
            else:
                print("\n❌ Some metrics are unavailable")
                exit(1)

        elif args.mode == "test":
            validator = MetricsValidationSuite(args.policy_url, args.prometheus_url)
            results = await validator.run_performance_regression_test(args.duration)

            if results.get("passed"):
                print("\n✅ Performance regression test passed")
                exit(0)
            else:
                print("\n❌ Performance regression test failed")
                exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
