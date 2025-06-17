#!/usr/bin/env python3
"""
ACGS-1 Real-Time Performance Monitoring Dashboard

Enterprise-grade performance monitoring system for the ACGS-1 constitutional governance system.
Monitors all 7 core services, tracks response times, uptime, and resource utilization.

Features:
- Real-time service health monitoring
- Response time tracking with percentile analysis
- Resource utilization monitoring (CPU, memory)
- Automated alerting for performance degradation
- Constitutional governance workflow performance tracking
- Enterprise dashboard with live metrics

Performance Targets:
- Response Times: <500ms for 95% of requests
- Uptime: >99.9% availability
- Concurrent Users: >1000 users supported
- Governance Costs: <0.01 SOL per transaction
"""

import asyncio
import aiohttp
import time
import json
import logging
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ACGS-1-Performance-Monitor')

@dataclass
class ServiceMetrics:
    """Service performance metrics."""
    service_name: str
    port: int
    status: str
    response_time_ms: float
    uptime_seconds: Optional[float]
    last_check: datetime
    error_count: int = 0
    success_count: int = 0

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_connections: int

@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    alert_type: str
    service: str
    metric: str
    threshold: float
    current_value: float
    severity: str
    timestamp: datetime

class PerformanceMonitor:
    """Real-time performance monitoring system for ACGS-1."""
    
    def __init__(self):
        self.services = {
            8000: "Auth Service",
            8001: "AC Service",
            8002: "Integrity Service",
            8003: "FV Service",
            8004: "GS Service",
            8005: "PGC Service",
            8006: "EC Service",
            8010: "ACGS-PGP v8 Service"
        }
        
        # Performance tracking
        self.response_times = defaultdict(lambda: deque(maxlen=1000))
        self.service_metrics = {}
        self.system_metrics = deque(maxlen=1000)
        self.alerts = deque(maxlen=100)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_ms': 500,
            'cpu_percent': 80,
            'memory_percent': 85,
            'error_rate_percent': 5,
            'uptime_target': 99.9
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.start_time = datetime.now()
        
    async def check_service_health(self, session: aiohttp.ClientSession, port: int) -> ServiceMetrics:
        """Check health of a single service."""
        service_name = self.services[port]
        start_time = time.time()
        
        try:
            async with session.get(
                f'http://localhost:{port}/health',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', 'unknown')
                    uptime = data.get('uptime_seconds')
                    
                    metrics = ServiceMetrics(
                        service_name=service_name,
                        port=port,
                        status=status,
                        response_time_ms=response_time,
                        uptime_seconds=uptime,
                        last_check=datetime.now(),
                        success_count=self.service_metrics.get(port, ServiceMetrics("", 0, "", 0, 0, datetime.now())).success_count + 1
                    )
                    
                    # Track response times
                    self.response_times[port].append(response_time)
                    
                    return metrics
                else:
                    raise aiohttp.ClientError(f"HTTP {response.status}")
                    
        except Exception as e:
            logger.warning(f"Health check failed for {service_name} (port {port}): {e}")
            
            previous_metrics = self.service_metrics.get(port, ServiceMetrics("", 0, "", 0, 0, datetime.now()))
            return ServiceMetrics(
                service_name=service_name,
                port=port,
                status="unhealthy",
                response_time_ms=5000,  # Timeout value
                uptime_seconds=None,
                last_check=datetime.now(),
                error_count=previous_metrics.error_count + 1,
                success_count=previous_metrics.success_count
            )
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-wide performance metrics."""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Active connections
            connections = len(psutil.net_connections())
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                active_connections=connections
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0,
                memory_percent=0,
                disk_usage_percent=0,
                network_io={},
                active_connections=0
            )
    
    def analyze_performance(self) -> Dict[str, any]:
        """Analyze current performance and generate insights."""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'services': {},
            'system': {},
            'alerts': [],
            'performance_summary': {}
        }
        
        # Analyze service performance
        healthy_services = 0
        total_services = len(self.services)
        
        for port, metrics in self.service_metrics.items():
            service_analysis = {
                'status': metrics.status,
                'response_time_ms': metrics.response_time_ms,
                'uptime_seconds': metrics.uptime_seconds,
                'error_rate': self._calculate_error_rate(port),
                'response_time_percentiles': self._calculate_percentiles(port)
            }
            
            if metrics.status in ['healthy', 'ok']:
                healthy_services += 1
            
            analysis['services'][metrics.service_name] = service_analysis
        
        # Calculate availability
        availability = (healthy_services / total_services) * 100 if total_services > 0 else 0
        analysis['performance_summary']['availability_percent'] = availability
        
        # System performance
        if self.system_metrics:
            latest_system = self.system_metrics[-1]
            analysis['system'] = {
                'cpu_percent': latest_system.cpu_percent,
                'memory_percent': latest_system.memory_percent,
                'disk_usage_percent': latest_system.disk_usage_percent,
                'active_connections': latest_system.active_connections
            }
        
        # Check for alerts
        self._check_performance_alerts(analysis)
        
        # Overall status determination
        if availability < 99.0:
            analysis['overall_status'] = 'degraded'
        elif any(alert['severity'] == 'critical' for alert in analysis['alerts']):
            analysis['overall_status'] = 'critical'
        
        return analysis
    
    def _calculate_error_rate(self, port: int) -> float:
        """Calculate error rate for a service."""
        metrics = self.service_metrics.get(port)
        if not metrics:
            return 0.0
        
        total_requests = metrics.success_count + metrics.error_count
        if total_requests == 0:
            return 0.0
        
        return (metrics.error_count / total_requests) * 100
    
    def _calculate_percentiles(self, port: int) -> Dict[str, float]:
        """Calculate response time percentiles."""
        response_times = list(self.response_times[port])
        if not response_times:
            return {}
        
        return {
            'p50': statistics.median(response_times),
            'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
            'p99': statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times),
            'avg': statistics.mean(response_times),
            'min': min(response_times),
            'max': max(response_times)
        }
    
    def _check_performance_alerts(self, analysis: Dict) -> None:
        """Check for performance alerts and add to analysis."""
        alerts = []
        
        # Check service response times
        for service_name, service_data in analysis['services'].items():
            if service_data['response_time_ms'] > self.thresholds['response_time_ms']:
                alerts.append({
                    'type': 'response_time',
                    'service': service_name,
                    'severity': 'warning',
                    'message': f"Response time {service_data['response_time_ms']:.1f}ms exceeds threshold {self.thresholds['response_time_ms']}ms",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check system resources
        system_data = analysis.get('system', {})
        if system_data.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_usage',
                'service': 'system',
                'severity': 'warning',
                'message': f"CPU usage {system_data['cpu_percent']:.1f}% exceeds threshold {self.thresholds['cpu_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if system_data.get('memory_percent', 0) > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_usage',
                'service': 'system',
                'severity': 'critical',
                'message': f"Memory usage {system_data['memory_percent']:.1f}% exceeds threshold {self.thresholds['memory_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Check availability
        availability = analysis['performance_summary'].get('availability_percent', 100)
        if availability < self.thresholds['uptime_target']:
            alerts.append({
                'type': 'availability',
                'service': 'system',
                'severity': 'critical',
                'message': f"System availability {availability:.1f}% below target {self.thresholds['uptime_target']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        analysis['alerts'] = alerts
    
    async def monitoring_loop(self, interval: int = 10) -> None:
        """Main monitoring loop."""
        logger.info(f"Starting ACGS-1 performance monitoring (interval: {interval}s)")
        self.monitoring_active = True
        
        async with aiohttp.ClientSession() as session:
            while self.monitoring_active:
                try:
                    # Collect service metrics
                    tasks = [
                        self.check_service_health(session, port)
                        for port in self.services.keys()
                    ]
                    
                    service_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Update service metrics
                    for result in service_results:
                        if isinstance(result, ServiceMetrics):
                            self.service_metrics[result.port] = result
                    
                    # Collect system metrics
                    system_metrics = await self.collect_system_metrics()
                    self.system_metrics.append(system_metrics)
                    
                    # Generate performance analysis
                    analysis = self.analyze_performance()
                    
                    # Log performance summary
                    logger.info(
                        f"Performance Check - "
                        f"Availability: {analysis['performance_summary'].get('availability_percent', 0):.1f}%, "
                        f"Alerts: {len(analysis['alerts'])}, "
                        f"Avg Response: {self._get_avg_response_time():.1f}ms"
                    )
                    
                    # Save metrics to file for dashboard
                    await self._save_metrics(analysis)
                    
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    await asyncio.sleep(interval)
    
    def _get_avg_response_time(self) -> float:
        """Get average response time across all services."""
        all_times = []
        for times in self.response_times.values():
            all_times.extend(times)
        return statistics.mean(all_times) if all_times else 0.0
    
    async def _save_metrics(self, analysis: Dict) -> None:
        """Save metrics to file for dashboard consumption."""
        try:
            with open('/tmp/acgs1_performance_metrics.json', 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        logger.info("Stopping ACGS-1 performance monitoring")
        self.monitoring_active = False

async def main():
    """Main function to run the performance monitor."""
    monitor = PerformanceMonitor()
    
    try:
        await monitor.monitoring_loop(interval=5)  # 5-second monitoring interval
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
