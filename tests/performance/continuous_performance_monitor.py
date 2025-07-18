#!/usr/bin/env python3
"""
ACGS-2 Continuous Performance Monitor
Constitutional Hash: cdd01ef066bc6cf2

Continuous monitoring of ACGS-2 performance to ensure constitutional 
compliance is maintained in production environments.
"""

import asyncio
import aiohttp
import time
import statistics
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os
from pathlib import Path

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class PerformanceSnapshot:
    """Single performance measurement snapshot"""
    timestamp: datetime
    service_name: str
    endpoint: str
    response_time_ms: float
    status_code: int
    constitutional_valid: bool
    success: bool

@dataclass
class ServiceHealthMetrics:
    """Health metrics for a service over time"""
    service_name: str
    measurement_window_minutes: int
    total_requests: int
    successful_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_response_time_ms: float
    success_rate: float
    constitutional_compliance_rate: float
    availability_percentage: float
    meets_constitutional_targets: bool

@dataclass
class SystemHealthReport:
    """Overall system health report"""
    timestamp: datetime
    measurement_window_minutes: int
    system_p99_response_time_ms: float
    system_availability: float
    system_constitutional_compliance: float
    services_meeting_targets: int
    total_services: int
    critical_alerts: List[str]
    performance_degradation_detected: bool
    constitutional_violations: List[str]

class ContinuousPerformanceMonitor:
    """Continuous performance monitoring system"""
    
    def __init__(self, 
                 measurement_interval_seconds: int = 30,
                 report_interval_minutes: int = 5,
                 alert_threshold_ms: float = 5.0,
                 constitutional_compliance_threshold: float = 100.0):
        
        self.measurement_interval = measurement_interval_seconds
        self.report_interval = report_interval_minutes
        self.alert_threshold_ms = alert_threshold_ms
        self.constitutional_threshold = constitutional_compliance_threshold
        
        self.snapshots: List[PerformanceSnapshot] = []
        self.alerts: List[str] = []
        self.running = False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('performance_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Service endpoints to monitor
        self.services = [
            {
                "name": "auth-service",
                "base_url": "http://localhost:8013",
                "endpoints": ["/health", "/api/v1/auth/health"],
                "critical": True
            },
            {
                "name": "monitoring-service", 
                "base_url": "http://localhost:8014",
                "endpoints": ["/health", "/api/v1/services/health"],
                "critical": True
            },
            {
                "name": "audit-service",
                "base_url": "http://localhost:8015", 
                "endpoints": ["/health"],
                "critical": True
            },
            {
                "name": "gdpr-compliance",
                "base_url": "http://localhost:8016",
                "endpoints": ["/health"],
                "critical": False
            },
            {
                "name": "alerting-service",
                "base_url": "http://localhost:8017",
                "endpoints": ["/health"],
                "critical": True
            },
            {
                "name": "api-gateway",
                "base_url": "http://localhost:8080",
                "endpoints": ["/health", "/gateway/metrics"],
                "critical": True
            }
        ]
    
    async def measure_endpoint_performance(self, 
                                         session: aiohttp.ClientSession,
                                         service: Dict[str, Any],
                                         endpoint: str) -> PerformanceSnapshot:
        """Measure performance of a single endpoint"""
        
        start_time = time.time()
        url = f"{service['base_url']}{endpoint}"
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                # Check constitutional compliance
                constitutional_valid = True
                try:
                    if response.status == 200:
                        data = await response.json()
                        constitutional_hash = data.get("constitutional_hash")
                        constitutional_valid = (constitutional_hash == CONSTITUTIONAL_HASH)
                except:
                    constitutional_valid = False
                
                return PerformanceSnapshot(
                    timestamp=datetime.utcnow(),
                    service_name=service["name"],
                    endpoint=endpoint,
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    constitutional_valid=constitutional_valid,
                    success=(response.status == 200)
                )
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"Error measuring {service['name']}{endpoint}: {e}")
            
            return PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                service_name=service["name"],
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=0,
                constitutional_valid=False,
                success=False
            )
    
    async def collect_performance_measurements(self):
        """Collect performance measurements from all services"""
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for service in self.services:
                for endpoint in service["endpoints"]:
                    task = self.measure_endpoint_performance(session, service, endpoint)
                    tasks.append(task)
            
            # Execute all measurements in parallel
            snapshots = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store valid snapshots
            for snapshot in snapshots:
                if isinstance(snapshot, PerformanceSnapshot):
                    self.snapshots.append(snapshot)
    
    def analyze_service_health(self, service_name: str, window_minutes: int = 5) -> ServiceHealthMetrics:
        """Analyze health metrics for a specific service"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Get recent snapshots for this service
        service_snapshots = [
            s for s in self.snapshots 
            if s.service_name == service_name and s.timestamp > cutoff_time
        ]
        
        if not service_snapshots:
            return ServiceHealthMetrics(
                service_name=service_name,
                measurement_window_minutes=window_minutes,
                total_requests=0,
                successful_requests=0,
                avg_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                max_response_time_ms=0,
                success_rate=0,
                constitutional_compliance_rate=0,
                availability_percentage=0,
                meets_constitutional_targets=False
            )
        
        # Calculate metrics
        total_requests = len(service_snapshots)
        successful_requests = len([s for s in service_snapshots if s.success])
        constitutional_valid = len([s for s in service_snapshots if s.constitutional_valid])
        
        response_times = [s.response_time_ms for s in service_snapshots if s.success]
        
        if response_times:
            avg_response_time_ms = statistics.mean(response_times)
            max_response_time_ms = max(response_times)
            
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            
            p95_response_time_ms = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time_ms
            p99_response_time_ms = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time_ms
        else:
            avg_response_time_ms = 0
            p95_response_time_ms = 0
            p99_response_time_ms = 0
            max_response_time_ms = 0
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        constitutional_compliance_rate = (constitutional_valid / total_requests * 100) if total_requests > 0 else 0
        availability_percentage = success_rate  # Simplified availability calculation
        
        # Check constitutional targets
        meets_targets = (
            p99_response_time_ms <= self.alert_threshold_ms and
            constitutional_compliance_rate >= self.constitutional_threshold and
            success_rate >= 95.0
        )
        
        return ServiceHealthMetrics(
            service_name=service_name,
            measurement_window_minutes=window_minutes,
            total_requests=total_requests,
            successful_requests=successful_requests,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
            max_response_time_ms=max_response_time_ms,
            success_rate=success_rate,
            constitutional_compliance_rate=constitutional_compliance_rate,
            availability_percentage=availability_percentage,
            meets_constitutional_targets=meets_targets
        )
    
    def generate_system_health_report(self, window_minutes: int = 5) -> SystemHealthReport:
        """Generate comprehensive system health report"""
        
        # Analyze each service
        service_metrics = []
        for service in self.services:
            metrics = self.analyze_service_health(service["name"], window_minutes)
            service_metrics.append(metrics)
        
        # System-wide calculations
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
        
        if recent_snapshots:
            successful_snapshots = [s for s in recent_snapshots if s.success]
            constitutional_valid_snapshots = [s for s in recent_snapshots if s.constitutional_valid]
            
            if successful_snapshots:
                response_times = [s.response_time_ms for s in successful_snapshots]
                sorted_times = sorted(response_times)
                p99_index = int(0.99 * len(sorted_times))
                system_p99_response_time_ms = sorted_times[p99_index] if p99_index < len(sorted_times) else max(response_times)
            else:
                system_p99_response_time_ms = 0
            
            system_availability = (len(successful_snapshots) / len(recent_snapshots) * 100) if recent_snapshots else 0
            system_constitutional_compliance = (len(constitutional_valid_snapshots) / len(recent_snapshots) * 100) if recent_snapshots else 0
        else:
            system_p99_response_time_ms = 0
            system_availability = 0
            system_constitutional_compliance = 0
        
        # Check for critical issues
        critical_alerts = []
        constitutional_violations = []
        services_meeting_targets = 0
        
        for metrics in service_metrics:
            if metrics.meets_constitutional_targets:
                services_meeting_targets += 1
            
            # Check for performance degradation
            if metrics.p99_response_time_ms > self.alert_threshold_ms:
                critical_alerts.append(f"{metrics.service_name}: P99 latency {metrics.p99_response_time_ms:.2f}ms exceeds {self.alert_threshold_ms}ms threshold")
            
            # Check constitutional compliance
            if metrics.constitutional_compliance_rate < self.constitutional_threshold:
                constitutional_violations.append(f"{metrics.service_name}: Constitutional compliance {metrics.constitutional_compliance_rate:.1f}% below {self.constitutional_threshold}% threshold")
            
            # Check availability
            if metrics.availability_percentage < 95.0:
                critical_alerts.append(f"{metrics.service_name}: Availability {metrics.availability_percentage:.1f}% below 95% threshold")
        
        performance_degradation_detected = (
            system_p99_response_time_ms > self.alert_threshold_ms or
            system_availability < 95.0 or
            len(critical_alerts) > 0
        )
        
        return SystemHealthReport(
            timestamp=datetime.utcnow(),
            measurement_window_minutes=window_minutes,
            system_p99_response_time_ms=system_p99_response_time_ms,
            system_availability=system_availability,
            system_constitutional_compliance=system_constitutional_compliance,
            services_meeting_targets=services_meeting_targets,
            total_services=len(service_metrics),
            critical_alerts=critical_alerts,
            performance_degradation_detected=performance_degradation_detected,
            constitutional_violations=constitutional_violations
        )
    
    def log_health_report(self, report: SystemHealthReport):
        """Log health report with appropriate severity"""
        
        if report.performance_degradation_detected or report.constitutional_violations:
            self.logger.error(f"🚨 CONSTITUTIONAL PERFORMANCE ALERT - Hash: {CONSTITUTIONAL_HASH}")
            self.logger.error(f"System P99: {report.system_p99_response_time_ms:.2f}ms, Availability: {report.system_availability:.1f}%")
            self.logger.error(f"Constitutional Compliance: {report.system_constitutional_compliance:.1f}%")
            self.logger.error(f"Services Meeting Targets: {report.services_meeting_targets}/{report.total_services}")
            
            for alert in report.critical_alerts:
                self.logger.error(f"   ⚠️ {alert}")
            
            for violation in report.constitutional_violations:
                self.logger.error(f"   ⚖️ {violation}")
        
        elif report.services_meeting_targets < report.total_services:
            self.logger.warning(f"⚠️ Performance degradation detected - Hash: {CONSTITUTIONAL_HASH}")
            self.logger.warning(f"Services meeting targets: {report.services_meeting_targets}/{report.total_services}")
        
        else:
            self.logger.info(f"✅ System performance healthy - Hash: {CONSTITUTIONAL_HASH}")
            self.logger.info(f"P99: {report.system_p99_response_time_ms:.2f}ms, Availability: {report.system_availability:.1f}%")
    
    def save_performance_data(self):
        """Save performance data to files"""
        
        # Save recent snapshots
        recent_snapshots = [
            s for s in self.snapshots 
            if s.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        snapshots_data = [
            {
                "timestamp": s.timestamp.isoformat(),
                "service_name": s.service_name,
                "endpoint": s.endpoint,
                "response_time_ms": s.response_time_ms,
                "status_code": s.status_code,
                "constitutional_valid": s.constitutional_valid,
                "success": s.success
            }
            for s in recent_snapshots
        ]
        
        # Save to JSON file
        data_file = Path("performance_data.json")
        with open(data_file, 'w') as f:
            json.dump({
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "last_updated": datetime.utcnow().isoformat(),
                "snapshots": snapshots_data
            }, f, indent=2)
        
        # Save latest health report
        report = self.generate_system_health_report()
        report_file = Path("latest_health_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "report": asdict(report)
            }, f, indent=2, default=str)
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        
        self.logger.info(f"🏛️ Starting Constitutional Performance Monitor - Hash: {CONSTITUTIONAL_HASH}")
        self.logger.info(f"📊 Measurement interval: {self.measurement_interval}s")
        self.logger.info(f"📋 Report interval: {self.report_interval}m") 
        self.logger.info(f"⚡ Alert threshold: {self.alert_threshold_ms}ms")
        
        last_report_time = time.time()
        
        while self.running:
            try:
                # Collect performance measurements
                await self.collect_performance_measurements()
                
                # Generate and log health report periodically
                if time.time() - last_report_time >= (self.report_interval * 60):
                    report = self.generate_system_health_report()
                    self.log_health_report(report)
                    self.save_performance_data()
                    last_report_time = time.time()
                
                # Clean up old snapshots (keep last 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
                
                # Wait for next measurement
                await asyncio.sleep(self.measurement_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.measurement_interval)
    
    async def start(self):
        """Start continuous monitoring"""
        self.running = True
        await self.monitoring_loop()
    
    def stop(self):
        """Stop continuous monitoring"""
        self.running = False
        self.logger.info("🛑 Constitutional Performance Monitor stopped")

async def main():
    """Main entry point for continuous monitoring"""
    
    import argparse
    parser = argparse.ArgumentParser(description="ACGS-2 Continuous Performance Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Measurement interval in seconds")
    parser.add_argument("--report-interval", type=int, default=5, help="Report interval in minutes") 
    parser.add_argument("--threshold", type=float, default=5.0, help="Alert threshold in milliseconds")
    
    args = parser.parse_args()
    
    monitor = ContinuousPerformanceMonitor(
        measurement_interval_seconds=args.interval,
        report_interval_minutes=args.report_interval,
        alert_threshold_ms=args.threshold
    )
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
        print("\n🛑 Performance monitoring stopped by user")

if __name__ == "__main__":
    asyncio.run(main())