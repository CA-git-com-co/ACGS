#!/usr/bin/env python3
"""
5-Tier Hybrid Inference Router Metrics Exporter

Exports Prometheus metrics for the 5-tier hybrid inference router system.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any

import aiohttp
import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
router_requests_total = Counter(
    'router_requests_total',
    'Total number of router requests',
    ['tier', 'status', 'constitutional_hash']
)

router_latency_seconds = Histogram(
    'router_latency_seconds',
    'Router request latency in seconds',
    ['tier', 'constitutional_hash'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

router_tier_usage = Gauge(
    'router_tier_usage_total',
    'Total usage count per tier',
    ['tier', 'constitutional_hash']
)

router_cost_per_request = Gauge(
    'router_cost_per_request_dollars',
    'Cost per request in dollars',
    ['tier', 'constitutional_hash']
)

router_constitutional_compliance_score = Gauge(
    'router_constitutional_compliance_score',
    'Constitutional compliance score',
    ['tier', 'constitutional_hash']
)

router_health_status = Gauge(
    'router_health_status',
    'Router health status (1=healthy, 0=unhealthy)',
    ['service', 'constitutional_hash']
)

router_performance_target_met = Gauge(
    'router_performance_target_met',
    'Whether performance target is met (1=met, 0=not met)',
    ['tier', 'target_type', 'constitutional_hash']
)


class RouterMetricsExporter:
    """Exports metrics for the 5-tier router system."""
    
    def __init__(self):
        self.router_url = os.getenv('ROUTER_URL', 'http://localhost:8020')
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Performance targets
        self.tier_targets = {
            'tier_1_nano': float(os.getenv('TIER_1_TARGET_LATENCY', 50)),
            'tier_2_fast': float(os.getenv('TIER_2_TARGET_LATENCY', 100)),
            'tier_3_balanced': float(os.getenv('TIER_3_TARGET_LATENCY', 200)),
            'tier_4_premium': float(os.getenv('TIER_4_TARGET_LATENCY', 600)),
            'tier_5_expert': float(os.getenv('TIER_5_TARGET_LATENCY', 900))
        }
        
    async def collect_metrics(self):
        """Collect metrics from the router."""
        while True:
            try:
                await self._collect_health_metrics()
                await self._collect_router_metrics()
                await self._collect_performance_metrics()
                
                logger.info(f"Metrics collected successfully (Hash: {self.constitutional_hash})")
                
            except Exception as e:
                logger.error(f"Failed to collect metrics: {e}")
                
            await asyncio.sleep(30)  # Collect every 30 seconds
    
    async def _collect_health_metrics(self):
        """Collect health status metrics."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.router_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Overall health
                        health_status = 1 if health_data.get('status') == 'healthy' else 0
                        router_health_status.labels(
                            service='router',
                            constitutional_hash=self.constitutional_hash
                        ).set(health_status)
                        
                        # Component health
                        components = health_data.get('components', {})
                        for component, status in components.items():
                            component_status = 1 if status == 'healthy' else 0
                            router_health_status.labels(
                                service=component,
                                constitutional_hash=self.constitutional_hash
                            ).set(component_status)
                    else:
                        router_health_status.labels(
                            service='router',
                            constitutional_hash=self.constitutional_hash
                        ).set(0)
                        
        except Exception as e:
            logger.warning(f"Health metrics collection failed: {e}")
            router_health_status.labels(
                service='router',
                constitutional_hash=self.constitutional_hash
            ).set(0)
    
    async def _collect_router_metrics(self):
        """Collect router-specific metrics."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.router_url}/metrics",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        metrics_data = await response.json()
                        
                        # Tier usage statistics
                        tier_usage = metrics_data.get('metrics', {}).get('tier_usage', {})
                        for tier, count in tier_usage.items():
                            router_tier_usage.labels(
                                tier=tier,
                                constitutional_hash=self.constitutional_hash
                            ).set(float(count))
                        
        except Exception as e:
            logger.warning(f"Router metrics collection failed: {e}")
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics by testing each tier."""
        test_queries = {
            'tier_1_nano': 'Hello',
            'tier_2_fast': 'Explain machine learning',
            'tier_3_balanced': 'Compare ML algorithms and their use cases',
            'tier_4_premium': 'Comprehensive analysis of constitutional AI governance',
            'tier_5_expert': 'Analyze constitutional governance scenarios with stakeholders'
        }
        
        for expected_tier, query in test_queries.items():
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.router_url}/route",
                        json={
                            "query": query,
                            "strategy": "balanced",
                            "max_tokens": 100
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        latency = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            actual_tier = result.get('tier', 'unknown')
                            
                            # Record latency
                            router_latency_seconds.labels(
                                tier=actual_tier,
                                constitutional_hash=self.constitutional_hash
                            ).observe(latency)
                            
                            # Record request
                            router_requests_total.labels(
                                tier=actual_tier,
                                status='success',
                                constitutional_hash=self.constitutional_hash
                            ).inc()
                            
                            # Record cost
                            cost = result.get('estimated_cost', 0.0)
                            router_cost_per_request.labels(
                                tier=actual_tier,
                                constitutional_hash=self.constitutional_hash
                            ).set(cost)
                            
                            # Record compliance score
                            compliance_score = result.get('constitutional_compliance_score', 0.0)
                            router_constitutional_compliance_score.labels(
                                tier=actual_tier,
                                constitutional_hash=self.constitutional_hash
                            ).set(compliance_score)
                            
                            # Check performance targets
                            target_latency_ms = self.tier_targets.get(actual_tier, 1000)
                            latency_ms = latency * 1000
                            
                            target_met = 1 if latency_ms <= target_latency_ms else 0
                            router_performance_target_met.labels(
                                tier=actual_tier,
                                target_type='latency',
                                constitutional_hash=self.constitutional_hash
                            ).set(target_met)
                            
                        else:
                            router_requests_total.labels(
                                tier=expected_tier,
                                status='error',
                                constitutional_hash=self.constitutional_hash
                            ).inc()
                            
            except Exception as e:
                logger.warning(f"Performance metrics collection failed for {expected_tier}: {e}")
                router_requests_total.labels(
                    tier=expected_tier,
                    status='error',
                    constitutional_hash=self.constitutional_hash
                ).inc()


def main():
    """Main exporter function."""
    logger.info("🚀 Starting 5-Tier Router Metrics Exporter")
    logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Start Prometheus metrics server
    start_http_server(9200)
    logger.info("📊 Prometheus metrics server started on port 9200")
    
    # Start metrics collection
    exporter = RouterMetricsExporter()
    
    try:
        asyncio.run(exporter.collect_metrics())
    except KeyboardInterrupt:
        logger.info("🔄 Metrics exporter stopped")
    except Exception as e:
        logger.error(f"❌ Metrics exporter failed: {e}")


if __name__ == "__main__":
    main()
