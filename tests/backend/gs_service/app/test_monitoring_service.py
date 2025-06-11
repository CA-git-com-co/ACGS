import os

import pytest
from prometheus_client import Counter

try:
    import os
    import sys

    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__),
            "../../../../services/core/governance-synthesis/gs_service",
        ),
    )
    from app.services import monitoring_service
    from app.services.advanced_cache import CacheStats
    from app.services.monitoring_service import MonitoringService
except ImportError:
    # Fallback to mock implementations for testing
    from dataclasses import dataclass
    from unittest.mock import MagicMock

    @dataclass
    class CacheStats:
        total_requests: int = 0
        cache_hits: int = 0
        cache_misses: int = 0
        hit_rate: float = 0.0
        memory_usage_bytes: int = 0
        entry_count: int = 0
        evictions: int = 0
        errors: int = 0

    class MonitoringService:
        async def _collect_performance_metrics(self):
            return MagicMock()

        async def _handle_alerts(self, alerts):
            pass

    monitoring_service = MagicMock()


@pytest.mark.asyncio
async def test_collect_performance_metrics_integration(monkeypatch):
    class FakeCacheManager:
        async def get_cache_stats(self):
            return {
                "policy_decisions": {
                    "multi_tier": CacheStats(
                        total_requests=100,
                        cache_hits=80,
                        cache_misses=20,
                        hit_rate=0.8,
                        memory_usage_bytes=0,
                        entry_count=0,
                        evictions=0,
                        errors=0,
                    )
                }
            }

    class FakeProfiler:
        def get_latency_profile(self, name):
            assert name == "opa_policy_evaluation:policy_decision"
            return type("P", (), {"avg_latency_ms": 30.0})()

    class FakePerformanceMonitor:
        active_requests = 5
        profiler = FakeProfiler()

    async def fake_get_cache_manager():
        return FakeCacheManager()

    def fake_get_performance_monitor():
        return FakePerformanceMonitor()

    monkeypatch.setattr(monitoring_service, "get_cache_manager", fake_get_cache_manager)
    monkeypatch.setattr(
        monitoring_service, "get_performance_monitor", fake_get_performance_monitor
    )

    # Use isolated counters for testing
    monkeypatch.setattr(
        monitoring_service,
        "ERROR_RATE",
        Counter("test_error_rate_total", "test", ["t", "e"]),
    )
    monkeypatch.setattr(
        monitoring_service,
        "THROUGHPUT",
        Counter("test_throughput_total", "test", ["e", "s"]),
    )
    monitoring_service.ERROR_RATE.labels("t", "e").inc()
    monitoring_service.THROUGHPUT.labels("e", "success").inc(4)
    monitoring_service.THROUGHPUT.labels("e", "error").inc()

    service = MonitoringService()
    metrics = await service._collect_performance_metrics()

    assert metrics.cache_hit_rate == 0.8
    assert metrics.policy_decision_latency_ms == 30.0
    assert metrics.concurrent_requests == 5
    assert pytest.approx(metrics.error_rate) == 1 / 5


@pytest.mark.asyncio
async def test_handle_alerts_sends_slack(monkeypatch):
    service = MonitoringService()
    sent = {}

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json=None):
            sent["url"] = url
            sent["json"] = json
            return type("Resp", (), {"status_code": 200})()

    monkeypatch.setattr(monitoring_service.httpx, "AsyncClient", DummyClient)
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://example.com")

    alert = {
        "metric_name": "cpu_usage_percent",
        "current_value": 90,
        "threshold_value": 80,
        "severity": "warning",
        "description": "CPU usage high",
    }

    await service._handle_alerts([alert])

    assert sent["url"] == "http://example.com"
    assert "CPU usage high" in sent["json"]["text"]
