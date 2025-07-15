#!/usr/bin/env python3
"""
Test Result Monitoring and Reporting System for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive test result monitoring, real-time reporting,
and performance tracking for the ACGS-2 testing framework.
"""

import asyncio
import json
import logging
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from collections import defaultdict, deque

import psutil
import requests
import websockets
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class TestResult:
    """Individual test result data"""
    test_name: str
    test_type: str  # unit, integration, e2e, security, performance
    status: str  # passed, failed, skipped, error
    duration: float  # seconds
    timestamp: datetime
    constitutional_compliant: bool
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    coverage_data: Optional[Dict[str, float]] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class TestSuiteResult:
    """Test suite execution result"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    start_time: datetime
    end_time: datetime
    coverage_percentage: float
    constitutional_compliance_rate: float
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class SystemMetrics:
    """System performance metrics during testing"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    test_process_count: int
    constitutional_hash: str = CONSTITUTIONAL_HASH

class TestMetricsCollector:
    """Collects and stores test metrics"""
    
    def __init__(self, db_path: str = "test_metrics.db"):
        self.db_path = db_path
        self.registry = CollectorRegistry()
        self._init_database()
        self._init_prometheus_metrics()
        
    def _init_database(self):
        """Initialize SQLite database for test metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_type TEXT NOT NULL,
                status TEXT NOT NULL,
                duration REAL NOT NULL,
                timestamp TEXT NOT NULL,
                constitutional_compliant BOOLEAN NOT NULL,
                error_message TEXT,
                performance_metrics TEXT,
                coverage_data TEXT,
                constitutional_hash TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_suite_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_name TEXT NOT NULL,
                total_tests INTEGER NOT NULL,
                passed_tests INTEGER NOT NULL,
                failed_tests INTEGER NOT NULL,
                skipped_tests INTEGER NOT NULL,
                error_tests INTEGER NOT NULL,
                total_duration REAL NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                coverage_percentage REAL NOT NULL,
                constitutional_compliance_rate REAL NOT NULL,
                constitutional_hash TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                disk_usage REAL NOT NULL,
                network_io TEXT NOT NULL,
                test_process_count INTEGER NOT NULL,
                constitutional_hash TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.test_counter = Counter(
            'acgs_tests_total',
            'Total number of tests executed',
            ['test_type', 'status', 'constitutional_compliant'],
            registry=self.registry
        )
        
        self.test_duration = Histogram(
            'acgs_test_duration_seconds',
            'Test execution duration in seconds',
            ['test_type', 'test_name'],
            registry=self.registry
        )
        
        self.coverage_gauge = Gauge(
            'acgs_test_coverage_percentage',
            'Test coverage percentage',
            ['test_type'],
            registry=self.registry
        )
        
        self.constitutional_compliance_gauge = Gauge(
            'acgs_constitutional_compliance_rate',
            'Constitutional compliance rate',
            registry=self.registry
        )
        
        self.system_cpu_gauge = Gauge(
            'acgs_test_system_cpu_usage',
            'CPU usage during testing',
            registry=self.registry
        )
        
        self.system_memory_gauge = Gauge(
            'acgs_test_system_memory_usage',
            'Memory usage during testing',
            registry=self.registry
        )
    
    def record_test_result(self, result: TestResult):
        """Record individual test result"""
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_results (
                test_name, test_type, status, duration, timestamp,
                constitutional_compliant, error_message, performance_metrics,
                coverage_data, constitutional_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.test_name,
            result.test_type,
            result.status,
            result.duration,
            result.timestamp.isoformat(),
            result.constitutional_compliant,
            result.error_message,
            json.dumps(result.performance_metrics) if result.performance_metrics else None,
            json.dumps(result.coverage_data) if result.coverage_data else None,
            result.constitutional_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Update Prometheus metrics
        self.test_counter.labels(
            test_type=result.test_type,
            status=result.status,
            constitutional_compliant=str(result.constitutional_compliant)
        ).inc()
        
        self.test_duration.labels(
            test_type=result.test_type,
            test_name=result.test_name
        ).observe(result.duration)
        
        logger.info(f"Recorded test result: {result.test_name} - {result.status}")
    
    def record_test_suite_result(self, result: TestSuiteResult):
        """Record test suite execution result"""
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_suite_results (
                suite_name, total_tests, passed_tests, failed_tests,
                skipped_tests, error_tests, total_duration, start_time,
                end_time, coverage_percentage, constitutional_compliance_rate,
                constitutional_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.suite_name,
            result.total_tests,
            result.passed_tests,
            result.failed_tests,
            result.skipped_tests,
            result.error_tests,
            result.total_duration,
            result.start_time.isoformat(),
            result.end_time.isoformat(),
            result.coverage_percentage,
            result.constitutional_compliance_rate,
            result.constitutional_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Update Prometheus metrics
        self.coverage_gauge.labels(test_type=result.suite_name).set(result.coverage_percentage)
        self.constitutional_compliance_gauge.set(result.constitutional_compliance_rate)
        
        logger.info(f"Recorded test suite result: {result.suite_name} - {result.passed_tests}/{result.total_tests} passed")
    
    def record_system_metrics(self, metrics: SystemMetrics):
        """Record system performance metrics"""
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_metrics (
                timestamp, cpu_usage, memory_usage, disk_usage,
                network_io, test_process_count, constitutional_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp.isoformat(),
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.disk_usage,
            json.dumps(metrics.network_io),
            metrics.test_process_count,
            metrics.constitutional_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Update Prometheus metrics
        self.system_cpu_gauge.set(metrics.cpu_usage)
        self.system_memory_gauge.set(metrics.memory_usage)
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')

class TestMonitor:
    """Real-time test monitoring and alerting"""
    
    def __init__(self, metrics_collector: TestMetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_thresholds = {
            "max_test_duration": 300.0,  # 5 minutes
            "max_failure_rate": 0.1,     # 10%
            "min_coverage": 80.0,        # 80%
            "min_constitutional_compliance": 95.0  # 95%
        }
        self.running = False
        self.alert_callbacks = []
        
    def add_alert_callback(self, callback):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.running = True
        
        # Start system metrics collection thread
        system_thread = threading.Thread(target=self._collect_system_metrics)
        system_thread.daemon = True
        system_thread.start()
        
        logger.info("Test monitoring started")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Test monitoring stopped")
        
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        while self.running:
            try:
                # Get system metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Count test processes
                test_process_count = 0
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline and any('pytest' in cmd or 'test' in cmd for cmd in cmdline):
                            test_process_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                metrics = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_usage=cpu_usage,
                    memory_usage=memory.percent,
                    disk_usage=(disk.used / disk.total) * 100,
                    network_io={
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv
                    },
                    test_process_count=test_process_count
                )
                
                self.metrics_collector.record_system_metrics(metrics)
                
                # Check for alerts
                self._check_system_alerts(metrics)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            time.sleep(10)  # Collect every 10 seconds
    
    def _check_system_alerts(self, metrics: SystemMetrics):
        """Check system metrics for alert conditions"""
        alerts = []
        
        if metrics.cpu_usage > 90:
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
            
        if metrics.memory_usage > 90:
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f}%")
            
        if metrics.disk_usage > 90:
            alerts.append(f"High disk usage: {metrics.disk_usage:.1f}%")
            
        if metrics.test_process_count > 50:
            alerts.append(f"High test process count: {metrics.test_process_count}")
        
        for alert in alerts:
            self._send_alert("System Alert", alert)
    
    def check_test_result_alerts(self, result: TestResult):
        """Check test result for alert conditions"""
        alerts = []
        
        if result.duration > self.alert_thresholds["max_test_duration"]:
            alerts.append(f"Test duration exceeded threshold: {result.duration:.1f}s > {self.alert_thresholds['max_test_duration']}s")
        
        if not result.constitutional_compliant:
            alerts.append(f"Constitutional compliance violation in test: {result.test_name}")
        
        if result.status == "failed":
            alerts.append(f"Test failed: {result.test_name} - {result.error_message}")
        
        for alert in alerts:
            self._send_alert("Test Alert", alert)
    
    def check_test_suite_alerts(self, result: TestSuiteResult):
        """Check test suite result for alert conditions"""
        alerts = []
        
        failure_rate = result.failed_tests / result.total_tests if result.total_tests > 0 else 0
        if failure_rate > self.alert_thresholds["max_failure_rate"]:
            alerts.append(f"High failure rate: {failure_rate:.1%} > {self.alert_thresholds['max_failure_rate']:.1%}")
        
        if result.coverage_percentage < self.alert_thresholds["min_coverage"]:
            alerts.append(f"Low test coverage: {result.coverage_percentage:.1f}% < {self.alert_thresholds['min_coverage']}%")
        
        if result.constitutional_compliance_rate < self.alert_thresholds["min_constitutional_compliance"]:
            alerts.append(f"Low constitutional compliance: {result.constitutional_compliance_rate:.1f}% < {self.alert_thresholds['min_constitutional_compliance']}%")
        
        for alert in alerts:
            self._send_alert("Test Suite Alert", alert)
    
    def _send_alert(self, alert_type: str, message: str):
        """Send alert to registered callbacks"""
        alert_data = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        logger.warning(f"ALERT: {alert_type} - {message}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Error sending alert to callback: {e}")

class TestReportGenerator:
    """Generates comprehensive test reports"""
    
    def __init__(self, metrics_collector: TestMetricsCollector):
        self.metrics_collector = metrics_collector
        
    def generate_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for real-time dashboard"""
        conn = sqlite3.connect(self.metrics_collector.db_path)
        cursor = conn.cursor()
        
        # Get recent test results (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        cursor.execute("""
            SELECT test_type, status, COUNT(*) as count
            FROM test_results 
            WHERE timestamp > ?
            GROUP BY test_type, status
        """, (since.isoformat(),))
        
        test_results = {}
        for row in cursor.fetchall():
            test_type, status, count = row
            if test_type not in test_results:
                test_results[test_type] = {}
            test_results[test_type][status] = count
        
        # Get recent system metrics
        cursor.execute("""
            SELECT timestamp, cpu_usage, memory_usage, disk_usage
            FROM system_metrics 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (since.isoformat(),))
        
        system_metrics = []
        for row in cursor.fetchall():
            timestamp, cpu, memory, disk = row
            system_metrics.append({
                "timestamp": timestamp,
                "cpu_usage": cpu,
                "memory_usage": memory,
                "disk_usage": disk
            })
        
        # Get constitutional compliance rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN constitutional_compliant = 1 THEN 1 ELSE 0 END) as compliant
            FROM test_results 
            WHERE timestamp > ?
        """, (since.isoformat(),))
        
        compliance_data = cursor.fetchone()
        compliance_rate = (compliance_data[1] / compliance_data[0] * 100) if compliance_data[0] > 0 else 0
        
        conn.close()
        
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.utcnow().isoformat(),
            "test_results": test_results,
            "system_metrics": system_metrics,
            "constitutional_compliance_rate": compliance_rate,
            "prometheus_metrics": self.metrics_collector.get_prometheus_metrics()
        }
    
    def generate_comprehensive_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive test report for the last N days"""
        conn = sqlite3.connect(self.metrics_collector.db_path)
        cursor = conn.cursor()
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Test execution summary
        cursor.execute("""
            SELECT 
                test_type,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(duration) as avg_duration,
                SUM(CASE WHEN constitutional_compliant = 1 THEN 1 ELSE 0 END) as compliant
            FROM test_results 
            WHERE timestamp > ?
            GROUP BY test_type
        """, (since.isoformat(),))
        
        test_summary = {}
        for row in cursor.fetchall():
            test_type, total, passed, failed, avg_duration, compliant = row
            test_summary[test_type] = {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": (passed / total * 100) if total > 0 else 0,
                "avg_duration": avg_duration,
                "constitutional_compliance_rate": (compliant / total * 100) if total > 0 else 0
            }
        
        # Performance trends
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(duration) as avg_duration,
                COUNT(*) as test_count
            FROM test_results 
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (since.isoformat(),))
        
        performance_trends = []
        for row in cursor.fetchall():
            date, avg_duration, test_count = row
            performance_trends.append({
                "date": date,
                "avg_duration": avg_duration,
                "test_count": test_count
            })
        
        # System performance summary
        cursor.execute("""
            SELECT 
                AVG(cpu_usage) as avg_cpu,
                MAX(cpu_usage) as max_cpu,
                AVG(memory_usage) as avg_memory,
                MAX(memory_usage) as max_memory,
                AVG(test_process_count) as avg_processes
            FROM system_metrics 
            WHERE timestamp > ?
        """, (since.isoformat(),))
        
        system_summary = cursor.fetchone()
        
        conn.close()
        
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "report_period": {
                "start": since.isoformat(),
                "end": datetime.utcnow().isoformat(),
                "days": days
            },
            "test_summary": test_summary,
            "performance_trends": performance_trends,
            "system_performance": {
                "avg_cpu_usage": system_summary[0] or 0,
                "max_cpu_usage": system_summary[1] or 0,
                "avg_memory_usage": system_summary[2] or 0,
                "max_memory_usage": system_summary[3] or 0,
                "avg_test_processes": system_summary[4] or 0
            } if system_summary else {}
        }

class TestMonitoringWebServer:
    """Web server for test monitoring dashboard"""
    
    def __init__(self, report_generator: TestReportGenerator, port: int = 8080):
        self.report_generator = report_generator
        self.port = port
        self.clients = set()
        
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections for real-time updates"""
        self.clients.add(websocket)
        logger.info(f"WebSocket client connected: {websocket.remote_address}")
        
        try:
            # Send initial dashboard data
            dashboard_data = self.report_generator.generate_real_time_dashboard_data()
            await websocket.send(json.dumps(dashboard_data))
            
            # Keep connection alive and send periodic updates
            while True:
                await asyncio.sleep(5)  # Update every 5 seconds
                dashboard_data = self.report_generator.generate_real_time_dashboard_data()
                await websocket.send(json.dumps(dashboard_data))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
        finally:
            self.clients.discard(websocket)
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        if self.clients:
            disconnected_clients = set()
            for websocket in self.clients:
                try:
                    await websocket.send(json.dumps(data))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(websocket)
            
            # Remove disconnected clients
            self.clients -= disconnected_clients
    
    def start_server(self):
        """Start the WebSocket server"""
        start_server = websockets.serve(self.websocket_handler, "localhost", self.port)
        logger.info(f"Test monitoring WebSocket server started on port {self.port}")
        return start_server

# Example usage and integration functions

def create_test_monitoring_system() -> Tuple[TestMetricsCollector, TestMonitor, TestReportGenerator]:
    """Create and configure the complete test monitoring system"""
    # Initialize components
    metrics_collector = TestMetricsCollector()
    monitor = TestMonitor(metrics_collector)
    report_generator = TestReportGenerator(metrics_collector)
    
    # Configure alerts
    def log_alert(alert_data):
        logger.warning(f"TEST ALERT: {alert_data['type']} - {alert_data['message']}")
    
    def webhook_alert(alert_data):
        """Send alert to webhook (example)"""
        try:
            webhook_url = os.getenv("ALERT_WEBHOOK_URL")
            if webhook_url:
                requests.post(webhook_url, json=alert_data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    monitor.add_alert_callback(log_alert)
    monitor.add_alert_callback(webhook_alert)
    
    return metrics_collector, monitor, report_generator

def example_test_execution_with_monitoring():
    """Example of how to integrate monitoring with test execution"""
    metrics_collector, monitor, report_generator = create_test_monitoring_system()
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Simulate test execution
        suite_start = datetime.utcnow()
        
        # Example test results
        test_results = [
            TestResult(
                test_name="test_constitutional_compliance",
                test_type="unit",
                status="passed",
                duration=1.5,
                timestamp=datetime.utcnow(),
                constitutional_compliant=True,
                performance_metrics={"memory_usage": 45.2, "cpu_time": 1.2}
            ),
            TestResult(
                test_name="test_security_validation",
                test_type="security",
                status="passed",
                duration=3.2,
                timestamp=datetime.utcnow(),
                constitutional_compliant=True
            ),
            TestResult(
                test_name="test_performance_benchmark",
                test_type="performance",
                status="failed",
                duration=10.5,
                timestamp=datetime.utcnow(),
                constitutional_compliant=False,
                error_message="Performance threshold exceeded"
            )
        ]
        
        # Record test results
        for result in test_results:
            metrics_collector.record_test_result(result)
            monitor.check_test_result_alerts(result)
        
        # Record suite result
        suite_result = TestSuiteResult(
            suite_name="comprehensive_test_suite",
            total_tests=3,
            passed_tests=2,
            failed_tests=1,
            skipped_tests=0,
            error_tests=0,
            total_duration=15.2,
            start_time=suite_start,
            end_time=datetime.utcnow(),
            coverage_percentage=85.5,
            constitutional_compliance_rate=66.7
        )
        
        metrics_collector.record_test_suite_result(suite_result)
        monitor.check_test_suite_alerts(suite_result)
        
        # Generate report
        report = report_generator.generate_comprehensive_report(days=1)
        print(json.dumps(report, indent=2, default=str))
        
    finally:
        # Stop monitoring
        monitor.stop_monitoring()

if __name__ == "__main__":
    example_test_execution_with_monitoring()