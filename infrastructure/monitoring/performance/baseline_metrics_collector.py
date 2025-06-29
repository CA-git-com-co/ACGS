#!/usr/bin/env python3
"""
ACGS Performance Baseline Metrics Collector
Establishes and maintains performance baselines for all 11 services with constitutional compliance tracking.
"""

import asyncio
import json
import logging
import statistics
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import aiohttp
import numpy as np
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class ServiceMetrics:
    """Performance metrics for a service."""
    service_name: str
    port: int
    
    # Response time metrics (milliseconds)
    avg_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    max_response_time: float = 0.0
    
    # Throughput metrics (requests per second)
    avg_throughput: float = 0.0
    peak_throughput: float = 0.0
    
    # Error metrics
    error_rate_percent: float = 0.0
    total_requests: int = 0
    total_errors: int = 0
    
    # Constitutional compliance metrics
    constitutional_compliance_rate: float = 1.0
    constitutional_validation_time_ms: float = 0.0
    
    # Resource utilization
    avg_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    
    # Availability metrics
    uptime_percent: float = 100.0
    health_check_success_rate: float = 100.0
    
    # Timestamps
    baseline_established: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PerformanceBaseline:
    """Complete performance baseline for ACGS system."""
    baseline_id: str
    version: str = "1.0.0"
    
    # Service metrics
    services: Dict[str, ServiceMetrics] = field(default_factory=dict)
    
    # System-wide metrics
    overall_avg_response_time: float = 0.0
    overall_error_rate: float = 0.0
    overall_throughput: float = 0.0
    overall_constitutional_compliance: float = 1.0
    
    # Infrastructure metrics
    database_performance: Dict[str, float] = field(default_factory=dict)
    message_broker_performance: Dict[str, float] = field(default_factory=dict)
    
    # Baseline metadata
    measurement_duration_hours: int = 24
    sample_count: int = 0
    constitutional_hash: str = CONSTITUTIONAL_HASH
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class PerformanceBaselineCollector:
    """Collects and establishes performance baselines for all ACGS services."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
        # Service configuration
        self.services = {
            "auth-service": 8000,
            "ac-service": 8001,
            "integrity-service": 8002,
            "fv-service": 8003,
            "gs-service": 8004,
            "pgc-service": 8005,
            "ec-service": 8006
        }
        
        # Infrastructure services
        self.infrastructure = {
            "prometheus": 9090,
            "grafana": 3001,
            "postgres": 5432,
            "redis": 6379,
            "nats": 4222
        }
        
        # Baseline data
        self.current_baseline: Optional[PerformanceBaseline] = None
        self.measurement_data: Dict[str, List[Dict]] = {}
        
        logger.info("Performance Baseline Collector initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for baseline collection."""
        self.baseline_response_time = Histogram(
            'acgs_baseline_response_time_seconds',
            'Response time measurements for baseline',
            ['service'],
            registry=self.registry
        )
        
        self.baseline_throughput = Gauge(
            'acgs_baseline_throughput_rps',
            'Throughput measurements for baseline',
            ['service'],
            registry=self.registry
        )
        
        self.baseline_error_rate = Gauge(
            'acgs_baseline_error_rate',
            'Error rate measurements for baseline',
            ['service'],
            registry=self.registry
        )
        
        self.constitutional_compliance_baseline = Gauge(
            'acgs_baseline_constitutional_compliance',
            'Constitutional compliance baseline',
            ['service'],
            registry=self.registry
        )

    async def establish_performance_baseline(self, duration_hours: int = 24) -> PerformanceBaseline:
        """Establish comprehensive performance baseline."""
        logger.info(f"Starting {duration_hours}-hour performance baseline establishment...")
        
        baseline_id = str(uuid.uuid4())
        self.current_baseline = PerformanceBaseline(
            baseline_id=baseline_id,
            measurement_duration_hours=duration_hours
        )
        
        # Start metrics server
        start_http_server(8093, registry=self.registry)
        logger.info("Baseline metrics server started on port 8093")
        
        # Initialize measurement data
        for service_name in self.services.keys():
            self.measurement_data[service_name] = []
        
        # Collect baseline data
        end_time = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        sample_interval = 30  # seconds
        
        while datetime.now(timezone.utc) < end_time:
            await self.collect_measurement_sample()
            await asyncio.sleep(sample_interval)
        
        # Calculate baseline metrics
        await self.calculate_baseline_metrics()
        
        # Save baseline
        await self.save_baseline()
        
        logger.info(f"Performance baseline established: {baseline_id}")
        return self.current_baseline

    async def collect_measurement_sample(self):
        """Collect a single measurement sample from all services."""
        sample_timestamp = datetime.now(timezone.utc)
        
        # Collect from ACGS services
        for service_name, port in self.services.items():
            try:
                metrics = await self.measure_service_performance(service_name, port)
                metrics['timestamp'] = sample_timestamp.isoformat()
                self.measurement_data[service_name].append(metrics)
                
                # Update Prometheus metrics
                if 'response_time_ms' in metrics:
                    self.baseline_response_time.labels(service=service_name).observe(
                        metrics['response_time_ms'] / 1000
                    )
                
                if 'error_rate' in metrics:
                    self.baseline_error_rate.labels(service=service_name).set(
                        metrics['error_rate']
                    )
                
                if 'constitutional_compliance' in metrics:
                    self.constitutional_compliance_baseline.labels(service=service_name).set(
                        metrics['constitutional_compliance']
                    )
                
            except Exception as e:
                logger.warning(f"Failed to collect metrics for {service_name}: {e}")
        
        self.current_baseline.sample_count += 1
        
        if self.current_baseline.sample_count % 120 == 0:  # Log every hour
            logger.info(f"Collected {self.current_baseline.sample_count} baseline samples")

    async def measure_service_performance(self, service_name: str, port: int) -> Dict:
        """Measure performance metrics for a specific service."""
        metrics = {}
        
        async with aiohttp.ClientSession() as session:
            # Measure response time and availability
            start_time = time.time()
            
            try:
                health_url = f"http://localhost:{port}/health"
                async with session.get(health_url, timeout=10) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    metrics['response_time_ms'] = response_time_ms
                    metrics['status_code'] = response.status
                    metrics['available'] = response.status == 200
                    
                    if response.status == 200:
                        health_data = await response.json()
                        metrics['health_status'] = health_data.get('status', 'unknown')
                    
            except Exception as e:
                metrics['response_time_ms'] = (time.time() - start_time) * 1000
                metrics['status_code'] = 0
                metrics['available'] = False
                metrics['error'] = str(e)
            
            # Measure API endpoint performance
            try:
                api_url = f"http://localhost:{port}/api/v1/status"
                start_time = time.time()
                
                async with session.get(api_url, timeout=10) as response:
                    api_response_time = (time.time() - start_time) * 1000
                    
                    metrics['api_response_time_ms'] = api_response_time
                    metrics['api_status_code'] = response.status
                    
                    if response.status == 200:
                        api_data = await response.json()
                        metrics['service_info'] = api_data
                    
            except Exception as e:
                metrics['api_response_time_ms'] = (time.time() - start_time) * 1000
                metrics['api_error'] = str(e)
            
            # Measure constitutional compliance (for applicable services)
            if service_name in ['ac-service', 'pgc-service', 'ec-service']:
                try:
                    constitutional_url = f"http://localhost:{port}/api/v1/constitutional/validate"
                    start_time = time.time()
                    
                    test_request = {
                        'constitutional_hash': CONSTITUTIONAL_HASH,
                        'validation_level': 'basic'
                    }
                    
                    async with session.post(constitutional_url, json=test_request, timeout=15) as response:
                        constitutional_time = (time.time() - start_time) * 1000
                        
                        metrics['constitutional_validation_time_ms'] = constitutional_time
                        
                        if response.status == 200:
                            constitutional_data = await response.json()
                            metrics['constitutional_compliance'] = constitutional_data.get('compliance_score', 1.0)
                        else:
                            metrics['constitutional_compliance'] = 0.0
                            
                except Exception as e:
                    metrics['constitutional_compliance'] = 0.0
                    metrics['constitutional_error'] = str(e)
            else:
                metrics['constitutional_compliance'] = 1.0  # Default for non-constitutional services
            
            # Get Prometheus metrics if available
            try:
                metrics_url = f"http://localhost:{port}/metrics"
                async with session.get(metrics_url, timeout=5) as response:
                    if response.status == 200:
                        prometheus_metrics = await response.text()
                        metrics['prometheus_available'] = True
                        
                        # Parse key metrics
                        if 'http_requests_total' in prometheus_metrics:
                            metrics['has_request_metrics'] = True
                        
                        if 'process_resident_memory_bytes' in prometheus_metrics:
                            metrics['has_memory_metrics'] = True
                            
                    else:
                        metrics['prometheus_available'] = False
                        
            except Exception:
                metrics['prometheus_available'] = False
        
        return metrics

    async def calculate_baseline_metrics(self):
        """Calculate baseline metrics from collected data."""
        logger.info("Calculating baseline metrics...")
        
        for service_name, measurements in self.measurement_data.items():
            if not measurements:
                continue
            
            service_metrics = ServiceMetrics(
                service_name=service_name,
                port=self.services[service_name]
            )
            
            # Extract response times
            response_times = [m.get('response_time_ms', 0) for m in measurements if m.get('response_time_ms')]
            api_response_times = [m.get('api_response_time_ms', 0) for m in measurements if m.get('api_response_time_ms')]
            
            if response_times:
                service_metrics.avg_response_time = statistics.mean(response_times)
                service_metrics.p50_response_time = np.percentile(response_times, 50)
                service_metrics.p95_response_time = np.percentile(response_times, 95)
                service_metrics.p99_response_time = np.percentile(response_times, 99)
                service_metrics.max_response_time = max(response_times)
            
            # Calculate availability
            total_checks = len(measurements)
            successful_checks = sum(1 for m in measurements if m.get('available', False))
            service_metrics.uptime_percent = (successful_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Calculate error rate
            total_requests = len([m for m in measurements if 'status_code' in m])
            error_requests = len([m for m in measurements if m.get('status_code', 200) >= 400])
            service_metrics.error_rate_percent = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Constitutional compliance
            compliance_scores = [m.get('constitutional_compliance', 1.0) for m in measurements]
            service_metrics.constitutional_compliance_rate = statistics.mean(compliance_scores) if compliance_scores else 1.0
            
            constitutional_times = [m.get('constitutional_validation_time_ms', 0) for m in measurements if m.get('constitutional_validation_time_ms')]
            service_metrics.constitutional_validation_time_ms = statistics.mean(constitutional_times) if constitutional_times else 0
            
            # Estimate throughput (simplified calculation)
            measurement_duration_minutes = self.current_baseline.measurement_duration_hours * 60
            service_metrics.avg_throughput = total_requests / measurement_duration_minutes if measurement_duration_minutes > 0 else 0
            
            # Update baseline
            self.current_baseline.services[service_name] = service_metrics
            
            logger.info(f"Baseline calculated for {service_name}: "
                       f"avg_response={service_metrics.avg_response_time:.2f}ms, "
                       f"error_rate={service_metrics.error_rate_percent:.2f}%, "
                       f"uptime={service_metrics.uptime_percent:.2f}%")
        
        # Calculate system-wide metrics
        await self.calculate_system_wide_metrics()

    async def calculate_system_wide_metrics(self):
        """Calculate system-wide performance metrics."""
        if not self.current_baseline.services:
            return
        
        # Overall response time
        response_times = [s.avg_response_time for s in self.current_baseline.services.values() if s.avg_response_time > 0]
        self.current_baseline.overall_avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Overall error rate
        error_rates = [s.error_rate_percent for s in self.current_baseline.services.values()]
        self.current_baseline.overall_error_rate = statistics.mean(error_rates) if error_rates else 0
        
        # Overall throughput
        throughputs = [s.avg_throughput for s in self.current_baseline.services.values() if s.avg_throughput > 0]
        self.current_baseline.overall_throughput = sum(throughputs) if throughputs else 0
        
        # Overall constitutional compliance
        compliance_rates = [s.constitutional_compliance_rate for s in self.current_baseline.services.values()]
        self.current_baseline.overall_constitutional_compliance = statistics.mean(compliance_rates) if compliance_rates else 1.0
        
        logger.info(f"System-wide baseline: "
                   f"avg_response={self.current_baseline.overall_avg_response_time:.2f}ms, "
                   f"error_rate={self.current_baseline.overall_error_rate:.2f}%, "
                   f"constitutional_compliance={self.current_baseline.overall_constitutional_compliance:.2%}")

    async def save_baseline(self):
        """Save baseline to file and database."""
        if not self.current_baseline:
            return
        
        # Save to JSON file
        baseline_data = {
            'baseline_id': self.current_baseline.baseline_id,
            'version': self.current_baseline.version,
            'services': {
                name: {
                    'service_name': metrics.service_name,
                    'port': metrics.port,
                    'avg_response_time': metrics.avg_response_time,
                    'p95_response_time': metrics.p95_response_time,
                    'p99_response_time': metrics.p99_response_time,
                    'error_rate_percent': metrics.error_rate_percent,
                    'uptime_percent': metrics.uptime_percent,
                    'constitutional_compliance_rate': metrics.constitutional_compliance_rate,
                    'constitutional_validation_time_ms': metrics.constitutional_validation_time_ms,
                    'avg_throughput': metrics.avg_throughput
                }
                for name, metrics in self.current_baseline.services.items()
            },
            'system_wide': {
                'overall_avg_response_time': self.current_baseline.overall_avg_response_time,
                'overall_error_rate': self.current_baseline.overall_error_rate,
                'overall_throughput': self.current_baseline.overall_throughput,
                'overall_constitutional_compliance': self.current_baseline.overall_constitutional_compliance
            },
            'metadata': {
                'measurement_duration_hours': self.current_baseline.measurement_duration_hours,
                'sample_count': self.current_baseline.sample_count,
                'constitutional_hash': self.current_baseline.constitutional_hash,
                'created_at': self.current_baseline.created_at.isoformat()
            }
        }
        
        # Save baseline file
        import os
        baseline_dir = "infrastructure/monitoring/performance/baselines"
        os.makedirs(baseline_dir, exist_ok=True)
        
        baseline_file = f"{baseline_dir}/baseline_{self.current_baseline.baseline_id}.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        # Save current baseline as latest
        latest_file = f"{baseline_dir}/latest_baseline.json"
        with open(latest_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        logger.info(f"Baseline saved: {baseline_file}")

    async def load_baseline(self, baseline_id: Optional[str] = None) -> Optional[PerformanceBaseline]:
        """Load baseline from file."""
        baseline_file = "infrastructure/monitoring/performance/baselines/latest_baseline.json"
        
        if baseline_id:
            baseline_file = f"infrastructure/monitoring/performance/baselines/baseline_{baseline_id}.json"
        
        try:
            with open(baseline_file) as f:
                baseline_data = json.load(f)
            
            baseline = PerformanceBaseline(
                baseline_id=baseline_data['baseline_id'],
                version=baseline_data['version'],
                overall_avg_response_time=baseline_data['system_wide']['overall_avg_response_time'],
                overall_error_rate=baseline_data['system_wide']['overall_error_rate'],
                overall_throughput=baseline_data['system_wide']['overall_throughput'],
                overall_constitutional_compliance=baseline_data['system_wide']['overall_constitutional_compliance'],
                measurement_duration_hours=baseline_data['metadata']['measurement_duration_hours'],
                sample_count=baseline_data['metadata']['sample_count'],
                constitutional_hash=baseline_data['metadata']['constitutional_hash']
            )
            
            # Load service metrics
            for service_name, service_data in baseline_data['services'].items():
                metrics = ServiceMetrics(
                    service_name=service_data['service_name'],
                    port=service_data['port'],
                    avg_response_time=service_data['avg_response_time'],
                    p95_response_time=service_data['p95_response_time'],
                    p99_response_time=service_data['p99_response_time'],
                    error_rate_percent=service_data['error_rate_percent'],
                    uptime_percent=service_data['uptime_percent'],
                    constitutional_compliance_rate=service_data['constitutional_compliance_rate'],
                    constitutional_validation_time_ms=service_data['constitutional_validation_time_ms'],
                    avg_throughput=service_data['avg_throughput']
                )
                baseline.services[service_name] = metrics
            
            logger.info(f"Baseline loaded: {baseline.baseline_id}")
            return baseline
            
        except FileNotFoundError:
            logger.warning(f"Baseline file not found: {baseline_file}")
            return None
        except Exception as e:
            logger.error(f"Failed to load baseline: {e}")
            return None

    def get_baseline_summary(self) -> Dict:
        """Get baseline summary for reporting."""
        if not self.current_baseline:
            return {}
        
        return {
            'baseline_id': self.current_baseline.baseline_id,
            'version': self.current_baseline.version,
            'services_count': len(self.current_baseline.services),
            'measurement_duration_hours': self.current_baseline.measurement_duration_hours,
            'sample_count': self.current_baseline.sample_count,
            'system_metrics': {
                'avg_response_time_ms': self.current_baseline.overall_avg_response_time,
                'error_rate_percent': self.current_baseline.overall_error_rate,
                'throughput_rps': self.current_baseline.overall_throughput,
                'constitutional_compliance_percent': self.current_baseline.overall_constitutional_compliance * 100
            },
            'service_summary': {
                service_name: {
                    'avg_response_time_ms': metrics.avg_response_time,
                    'p95_response_time_ms': metrics.p95_response_time,
                    'error_rate_percent': metrics.error_rate_percent,
                    'uptime_percent': metrics.uptime_percent,
                    'constitutional_compliance_percent': metrics.constitutional_compliance_rate * 100
                }
                for service_name, metrics in self.current_baseline.services.items()
            },
            'constitutional_hash': self.current_baseline.constitutional_hash,
            'created_at': self.current_baseline.created_at.isoformat()
        }

# Global baseline collector instance
baseline_collector = PerformanceBaselineCollector()

if __name__ == "__main__":
    async def main():
        # Establish 1-hour baseline for testing
        baseline = await baseline_collector.establish_performance_baseline(duration_hours=1)
        
        # Print summary
        summary = baseline_collector.get_baseline_summary()
        print(json.dumps(summary, indent=2))
    
    asyncio.run(main())
