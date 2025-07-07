#!/usr/bin/env python3
"""
ACGS Unified Monitoring Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Consolidates and modernizes all ACGS monitoring and observability tools.

Features:
- Real-time service health monitoring
- Performance metrics collection and analysis
- Constitutional compliance monitoring
- Distributed tracing and observability
- Automated alerting and notifications
- Comprehensive dashboards and visualization
- Log aggregation and analysis
- System resource monitoring
- SLA/SLO tracking and reporting
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

import aiohttp
import aioredis
import asyncpg
import psutil
from pydantic import BaseModel

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS service configuration
ACGS_SERVICES = {
    "auth": {"port": 8016, "name": "Auth Service", "critical": True},
    "constitutional_ai": {"port": 8001, "name": "Constitutional AI", "critical": True},
    "integrity": {"port": 8002, "name": "Integrity Service", "critical": True},
    "formal_verification": {"port": 8003, "name": "Formal Verification", "critical": False},
    "governance_synthesis": {"port": 8004, "name": "Governance Synthesis", "critical": False},
    "policy_governance": {"port": 8005, "name": "Policy Governance", "critical": False},
    "evolutionary_computation": {"port": 8006, "name": "Evolutionary Computation", "critical": False},
}

# Infrastructure services
INFRASTRUCTURE_SERVICES = {
    "postgresql": {"port": 5439, "name": "PostgreSQL Database", "critical": True},
    "redis": {"port": 6389, "name": "Redis Cache", "critical": True},
    "prometheus": {"port": 9090, "name": "Prometheus", "critical": False},
    "grafana": {"port": 3000, "name": "Grafana", "critical": False},
}

# Monitoring configuration
MONITORING_CONFIG = {
    "health_check_interval": 30,  # seconds
    "metrics_collection_interval": 60,  # seconds
    "performance_test_interval": 300,  # seconds
    "alert_check_interval": 60,  # seconds
    "retention_days": 30,
    "thresholds": {
        "response_time_ms": 5.0,  # P99 <5ms target
        "throughput_rps": 100.0,  # >100 RPS target
        "cache_hit_rate": 0.85,  # >85% cache hit rate
        "cpu_percent": 80.0,
        "memory_percent": 85.0,
        "disk_percent": 90.0,
        "error_rate_percent": 1.0,
        "uptime_percent": 99.9,
    },
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceHealthMetrics:
    """Service health metrics data structure."""
    service_name: str
    port: int
    status: str  # "healthy", "unhealthy", "unknown", "error"
    response_time_ms: float
    uptime_seconds: Optional[float]
    last_check: datetime
    error_count: int = 0
    success_count: int = 0
    constitutional_compliance: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: List[float]
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    service_name: str
    avg_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    error_rate_percent: float
    cache_hit_rate: Optional[float] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class AlertRule(BaseModel):
    """Alert rule configuration."""
    name: str
    condition: str
    threshold: float
    severity: str  # "critical", "warning", "info"
    enabled: bool = True
    cooldown_minutes: int = 5


class ACGSMonitoringOrchestrator:
    """Unified monitoring orchestrator for ACGS."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.redis_client: Optional[aioredis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Metrics storage
        self.health_metrics: Dict[str, ServiceHealthMetrics] = {}
        self.system_metrics_history: deque = deque(maxlen=1000)
        self.performance_metrics_history: deque = deque(maxlen=1000)
        self.alerts_history: deque = deque(maxlen=100)
        
        # Response time tracking
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Monitoring state
        self.monitoring_active = False
        self.start_time = datetime.now(timezone.utc)
        
        # Alert rules
        self.alert_rules = self._initialize_alert_rules()
        self.alert_cooldowns: Dict[str, datetime] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize monitoring orchestrator."""
        logger.info("📊 Initializing ACGS Monitoring Orchestrator...")
        
        # Validate constitutional hash
        if not self._validate_constitutional_hash():
            raise ValueError(f"Invalid constitutional hash: {CONSTITUTIONAL_HASH}")
        
        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Initialize Redis client
        try:
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6389/0",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
        
        # Initialize database connection
        try:
            db_config = {
                "host": "localhost",
                "port": 5439,
                "database": "acgs_db",
                "user": "acgs_user",
                "password": "acgs_secure_password",
                "min_size": 2,
                "max_size": 10,
                "command_timeout": 5,
            }
            self.db_pool = await asyncpg.create_pool(**db_config)
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
        
        # Create monitoring directories
        self._create_monitoring_directories()
        
        # Initialize monitoring tables
        await self._initialize_monitoring_tables()
        
        logger.info("✅ Monitoring orchestrator initialized")
        
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up monitoring orchestrator...")
        
        self.monitoring_active = False
        
        if self.session:
            await self.session.close()
            
        if self.redis_client:
            await self.redis_client.close()
            
        if self.db_pool:
            await self.db_pool.close()
            
        logger.info("✅ Cleanup completed")

    def _validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash."""
        return CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    def _create_monitoring_directories(self):
        """Create necessary monitoring directories."""
        monitoring_dirs = [
            "reports/monitoring",
            "reports/health_checks",
            "reports/performance",
            "reports/alerts",
            "logs/monitoring",
            "dashboards/grafana",
            "configs/prometheus",
        ]
        
        for monitoring_dir in monitoring_dirs:
            Path(monitoring_dir).mkdir(parents=True, exist_ok=True)

    async def _initialize_monitoring_tables(self):
        """Initialize monitoring database tables."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Health metrics table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS health_metrics (
                        id SERIAL PRIMARY KEY,
                        service_name VARCHAR(100) NOT NULL,
                        port INTEGER NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        response_time_ms FLOAT NOT NULL,
                        uptime_seconds FLOAT,
                        error_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        constitutional_compliance BOOLEAN DEFAULT TRUE,
                        constitutional_hash VARCHAR(32) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Performance metrics table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id SERIAL PRIMARY KEY,
                        service_name VARCHAR(100) NOT NULL,
                        avg_response_time_ms FLOAT NOT NULL,
                        p99_response_time_ms FLOAT NOT NULL,
                        throughput_rps FLOAT NOT NULL,
                        error_rate_percent FLOAT NOT NULL,
                        cache_hit_rate FLOAT,
                        constitutional_hash VARCHAR(32) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # System metrics table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id SERIAL PRIMARY KEY,
                        cpu_percent FLOAT NOT NULL,
                        memory_percent FLOAT NOT NULL,
                        disk_percent FLOAT NOT NULL,
                        network_bytes_sent BIGINT NOT NULL,
                        network_bytes_recv BIGINT NOT NULL,
                        load_average FLOAT[] NOT NULL,
                        constitutional_hash VARCHAR(32) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Alerts table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id SERIAL PRIMARY KEY,
                        alert_name VARCHAR(200) NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        message TEXT NOT NULL,
                        service_name VARCHAR(100),
                        metric_value FLOAT,
                        threshold_value FLOAT,
                        resolved BOOLEAN DEFAULT FALSE,
                        constitutional_hash VARCHAR(32) NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_health_metrics_timestamp 
                    ON health_metrics(timestamp)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp 
                    ON performance_metrics(timestamp)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp 
                    ON system_metrics(timestamp)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                    ON alerts(timestamp)
                """)
                
            logger.info("✅ Monitoring tables initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring tables: {e}")

    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Initialize default alert rules."""
        return [
            AlertRule(
                name="High Response Time",
                condition="response_time_ms",
                threshold=MONITORING_CONFIG["thresholds"]["response_time_ms"],
                severity="warning",
            ),
            AlertRule(
                name="Low Throughput",
                condition="throughput_rps",
                threshold=MONITORING_CONFIG["thresholds"]["throughput_rps"],
                severity="warning",
            ),
            AlertRule(
                name="High CPU Usage",
                condition="cpu_percent",
                threshold=MONITORING_CONFIG["thresholds"]["cpu_percent"],
                severity="warning",
            ),
            AlertRule(
                name="High Memory Usage",
                condition="memory_percent",
                threshold=MONITORING_CONFIG["thresholds"]["memory_percent"],
                severity="warning",
            ),
            AlertRule(
                name="Service Down",
                condition="service_status",
                threshold=0,
                severity="critical",
            ),
            AlertRule(
                name="Constitutional Compliance Violation",
                condition="constitutional_compliance",
                threshold=1,
                severity="critical",
            ),
        ]

    async def start_comprehensive_monitoring(self) -> Dict[str, Any]:
        """Start comprehensive monitoring of all ACGS components."""
        logger.info("🚀 Starting comprehensive ACGS monitoring...")

        self.monitoring_active = True
        monitoring_summary = {
            "monitoring_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "monitoring_duration_minutes": 0,
            "health_checks_performed": 0,
            "performance_tests_performed": 0,
            "alerts_generated": 0,
            "overall_system_health": "unknown",
        }

        try:
            # Start monitoring tasks
            monitoring_tasks = [
                self._health_monitoring_loop(),
                self._performance_monitoring_loop(),
                self._system_monitoring_loop(),
                self._alert_monitoring_loop(),
            ]

            # Run monitoring tasks concurrently
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            monitoring_summary["error"] = str(e)
        finally:
            self.monitoring_active = False

            # Calculate final summary
            monitoring_duration = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 60
            monitoring_summary["monitoring_duration_minutes"] = round(monitoring_duration, 2)
            monitoring_summary["health_checks_performed"] = len(self.health_metrics)
            monitoring_summary["alerts_generated"] = len(self.alerts_history)

            # Save monitoring summary
            await self._save_monitoring_summary(monitoring_summary)

        return monitoring_summary

    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        logger.info("🏥 Starting health monitoring loop...")

        while self.monitoring_active:
            try:
                # Check all services
                await self._check_all_services_health()

                # Check infrastructure
                await self._check_infrastructure_health()

                # Save health metrics
                await self._save_health_metrics()

                await asyncio.sleep(MONITORING_CONFIG["health_check_interval"])

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(MONITORING_CONFIG["health_check_interval"])

    async def _check_all_services_health(self):
        """Check health of all ACGS services."""
        # Check ACGS services
        for service_name, config in ACGS_SERVICES.items():
            health_metrics = await self._check_service_health(
                service_name,
                config["port"],
                config["name"],
                config["critical"]
            )
            self.health_metrics[service_name] = health_metrics

    async def _check_service_health(
        self,
        service_name: str,
        port: int,
        display_name: str,
        critical: bool
    ) -> ServiceHealthMetrics:
        """Check health of a specific service."""
        start_time = time.time()

        try:
            health_url = f"http://localhost:{port}/health"

            async with self.session.get(health_url) as response:
                response_time_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    # Try to parse response for additional metrics
                    try:
                        health_data = await response.json()
                        uptime_seconds = health_data.get("uptime_seconds")
                        constitutional_compliance = health_data.get(
                            "constitutional_hash"
                        ) == CONSTITUTIONAL_HASH
                    except Exception:
                        uptime_seconds = None
                        constitutional_compliance = True

                    # Track response times
                    self.response_times[service_name].append(response_time_ms)

                    # Get previous metrics for counters
                    prev_metrics = self.health_metrics.get(service_name)
                    success_count = (prev_metrics.success_count + 1) if prev_metrics else 1
                    error_count = prev_metrics.error_count if prev_metrics else 0

                    return ServiceHealthMetrics(
                        service_name=service_name,
                        port=port,
                        status="healthy",
                        response_time_ms=round(response_time_ms, 2),
                        uptime_seconds=uptime_seconds,
                        last_check=datetime.now(timezone.utc),
                        success_count=success_count,
                        error_count=error_count,
                        constitutional_compliance=constitutional_compliance,
                    )
                else:
                    # Service returned non-200 status
                    prev_metrics = self.health_metrics.get(service_name)
                    error_count = (prev_metrics.error_count + 1) if prev_metrics else 1
                    success_count = prev_metrics.success_count if prev_metrics else 0

                    return ServiceHealthMetrics(
                        service_name=service_name,
                        port=port,
                        status=f"unhealthy_http_{response.status}",
                        response_time_ms=round((time.time() - start_time) * 1000, 2),
                        uptime_seconds=None,
                        last_check=datetime.now(timezone.utc),
                        success_count=success_count,
                        error_count=error_count,
                        constitutional_compliance=False,
                    )

        except Exception as e:
            # Service is not reachable
            prev_metrics = self.health_metrics.get(service_name)
            error_count = (prev_metrics.error_count + 1) if prev_metrics else 1
            success_count = prev_metrics.success_count if prev_metrics else 0

            return ServiceHealthMetrics(
                service_name=service_name,
                port=port,
                status=f"error_{str(e)[:20]}",
                response_time_ms=round((time.time() - start_time) * 1000, 2),
                uptime_seconds=None,
                last_check=datetime.now(timezone.utc),
                success_count=success_count,
                error_count=error_count,
                constitutional_compliance=False,
            )

    async def _check_infrastructure_health(self):
        """Check health of infrastructure services."""
        for service_name, config in INFRASTRUCTURE_SERVICES.items():
            if service_name == "postgresql":
                health_metrics = await self._check_postgresql_health()
            elif service_name == "redis":
                health_metrics = await self._check_redis_health()
            else:
                # HTTP-based infrastructure services
                health_metrics = await self._check_service_health(
                    service_name,
                    config["port"],
                    config["name"],
                    config["critical"]
                )

            self.health_metrics[service_name] = health_metrics

    async def _check_postgresql_health(self) -> ServiceHealthMetrics:
        """Check PostgreSQL database health."""
        start_time = time.time()

        try:
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    # Simple query to test connectivity
                    result = await conn.fetchval("SELECT 1")

                    response_time_ms = (time.time() - start_time) * 1000

                    if result == 1:
                        return ServiceHealthMetrics(
                            service_name="postgresql",
                            port=5439,
                            status="healthy",
                            response_time_ms=round(response_time_ms, 2),
                            uptime_seconds=None,
                            last_check=datetime.now(timezone.utc),
                            success_count=1,
                            error_count=0,
                            constitutional_compliance=True,
                        )

            # Database not available
            return ServiceHealthMetrics(
                service_name="postgresql",
                port=5439,
                status="unhealthy_no_connection",
                response_time_ms=round((time.time() - start_time) * 1000, 2),
                uptime_seconds=None,
                last_check=datetime.now(timezone.utc),
                success_count=0,
                error_count=1,
                constitutional_compliance=False,
            )

        except Exception as e:
            return ServiceHealthMetrics(
                service_name="postgresql",
                port=5439,
                status=f"error_{str(e)[:20]}",
                response_time_ms=round((time.time() - start_time) * 1000, 2),
                uptime_seconds=None,
                last_check=datetime.now(timezone.utc),
                success_count=0,
                error_count=1,
                constitutional_compliance=False,
            )

    async def _check_redis_health(self) -> ServiceHealthMetrics:
        """Check Redis cache health."""
        start_time = time.time()

        try:
            if self.redis_client:
                # Test Redis connectivity
                pong = await self.redis_client.ping()

                response_time_ms = (time.time() - start_time) * 1000

                if pong:
                    return ServiceHealthMetrics(
                        service_name="redis",
                        port=6389,
                        status="healthy",
                        response_time_ms=round(response_time_ms, 2),
                        uptime_seconds=None,
                        last_check=datetime.now(timezone.utc),
                        success_count=1,
                        error_count=0,
                        constitutional_compliance=True,
                    )

            # Redis not available
            return ServiceHealthMetrics(
                service_name="redis",
                port=6389,
                status="unhealthy_no_connection",
                response_time_ms=round((time.time() - start_time) * 1000, 2),
                uptime_seconds=None,
                last_check=datetime.now(timezone.utc),
                success_count=0,
                error_count=1,
                constitutional_compliance=False,
            )

        except Exception as e:
            return ServiceHealthMetrics(
                service_name="redis",
                port=6389,
                status=f"error_{str(e)[:20]}",
                response_time_ms=round((time.time() - start_time) * 1000, 2),
                uptime_seconds=None,
                last_check=datetime.now(timezone.utc),
                success_count=0,
                error_count=1,
                constitutional_compliance=False,
            )

    async def _performance_monitoring_loop(self):
        """Continuous performance monitoring loop."""
        logger.info("⚡ Starting performance monitoring loop...")

        while self.monitoring_active:
            try:
                # Collect performance metrics
                await self._collect_performance_metrics()

                # Save performance metrics
                await self._save_performance_metrics()

                await asyncio.sleep(MONITORING_CONFIG["performance_test_interval"])

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(MONITORING_CONFIG["performance_test_interval"])

    async def _collect_performance_metrics(self):
        """Collect performance metrics for all services."""
        for service_name, config in ACGS_SERVICES.items():
            if service_name in self.health_metrics:
                health_metrics = self.health_metrics[service_name]

                if health_metrics.status == "healthy":
                    # Calculate performance metrics
                    response_times = list(self.response_times[service_name])

                    if response_times:
                        avg_response_time = sum(response_times) / len(response_times)
                        sorted_times = sorted(response_times)
                        p99_index = int(len(sorted_times) * 0.99)
                        p99_response_time = sorted_times[p99_index] if sorted_times else 0

                        # Calculate throughput (simplified)
                        throughput_rps = len(response_times) / (MONITORING_CONFIG["performance_test_interval"] / 60)

                        # Calculate error rate
                        total_requests = health_metrics.success_count + health_metrics.error_count
                        error_rate = (health_metrics.error_count / total_requests * 100) if total_requests > 0 else 0

                        # Create performance metrics
                        perf_metrics = PerformanceMetrics(
                            timestamp=datetime.now(timezone.utc),
                            service_name=service_name,
                            avg_response_time_ms=round(avg_response_time, 2),
                            p99_response_time_ms=round(p99_response_time, 2),
                            throughput_rps=round(throughput_rps, 2),
                            error_rate_percent=round(error_rate, 2),
                        )

                        self.performance_metrics_history.append(perf_metrics)

    async def _system_monitoring_loop(self):
        """Continuous system monitoring loop."""
        logger.info("🖥️ Starting system monitoring loop...")

        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)

                # Save system metrics
                await self._save_system_metrics(system_metrics)

                await asyncio.sleep(MONITORING_CONFIG["metrics_collection_interval"])

            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(MONITORING_CONFIG["metrics_collection_interval"])

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv

            # Load average
            load_average = list(psutil.getloadavg())

            return SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=round(cpu_percent, 2),
                memory_percent=round(memory_percent, 2),
                disk_percent=round(disk_percent, 2),
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                load_average=load_average,
            )

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                load_average=[0.0, 0.0, 0.0],
            )

    async def _alert_monitoring_loop(self):
        """Continuous alert monitoring loop."""
        logger.info("🚨 Starting alert monitoring loop...")

        while self.monitoring_active:
            try:
                # Check alert conditions
                await self._check_alert_conditions()

                await asyncio.sleep(MONITORING_CONFIG["alert_check_interval"])

            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(MONITORING_CONFIG["alert_check_interval"])

    async def _check_alert_conditions(self):
        """Check all alert conditions and generate alerts."""
        current_time = datetime.now(timezone.utc)

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.name in self.alert_cooldowns:
                cooldown_end = self.alert_cooldowns[rule.name] + timedelta(minutes=rule.cooldown_minutes)
                if current_time < cooldown_end:
                    continue

            # Check condition
            alert_triggered = await self._evaluate_alert_condition(rule)

            if alert_triggered:
                # Generate alert
                alert = {
                    "alert_name": rule.name,
                    "severity": rule.severity,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "timestamp": current_time.isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

                # Add specific alert details
                if rule.condition == "service_status":
                    unhealthy_services = [
                        name for name, metrics in self.health_metrics.items()
                        if metrics.status != "healthy"
                    ]
                    alert["message"] = f"Services unhealthy: {', '.join(unhealthy_services)}"
                    alert["services"] = unhealthy_services
                elif rule.condition == "response_time_ms":
                    slow_services = []
                    for name, metrics in self.health_metrics.items():
                        if metrics.response_time_ms > rule.threshold:
                            slow_services.append(f"{name}({metrics.response_time_ms:.1f}ms)")
                    alert["message"] = f"High response times: {', '.join(slow_services)}"
                elif rule.condition == "constitutional_compliance":
                    non_compliant = [
                        name for name, metrics in self.health_metrics.items()
                        if not metrics.constitutional_compliance
                    ]
                    alert["message"] = f"Constitutional compliance violations: {', '.join(non_compliant)}"
                    alert["services"] = non_compliant
                else:
                    # System resource alerts
                    if self.system_metrics_history:
                        latest_metrics = self.system_metrics_history[-1]
                        if rule.condition == "cpu_percent":
                            alert["message"] = f"High CPU usage: {latest_metrics.cpu_percent:.1f}%"
                            alert["metric_value"] = latest_metrics.cpu_percent
                        elif rule.condition == "memory_percent":
                            alert["message"] = f"High memory usage: {latest_metrics.memory_percent:.1f}%"
                            alert["metric_value"] = latest_metrics.memory_percent

                # Store alert
                self.alerts_history.append(alert)

                # Set cooldown
                self.alert_cooldowns[rule.name] = current_time

                # Log alert
                logger.warning(f"🚨 ALERT [{rule.severity.upper()}]: {alert['message']}")

                # Save alert to database
                await self._save_alert(alert)

    async def _evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """Evaluate if an alert condition is met."""
        try:
            if rule.condition == "service_status":
                # Check if any critical services are down
                for name, metrics in self.health_metrics.items():
                    service_config = ACGS_SERVICES.get(name) or INFRASTRUCTURE_SERVICES.get(name)
                    if service_config and service_config.get("critical", False):
                        if metrics.status != "healthy":
                            return True
                return False

            elif rule.condition == "response_time_ms":
                # Check if any service exceeds response time threshold
                for metrics in self.health_metrics.values():
                    if metrics.response_time_ms > rule.threshold:
                        return True
                return False

            elif rule.condition == "constitutional_compliance":
                # Check for constitutional compliance violations
                for metrics in self.health_metrics.values():
                    if not metrics.constitutional_compliance:
                        return True
                return False

            elif rule.condition in ["cpu_percent", "memory_percent"]:
                # Check system resource thresholds
                if self.system_metrics_history:
                    latest_metrics = self.system_metrics_history[-1]
                    if rule.condition == "cpu_percent":
                        return latest_metrics.cpu_percent > rule.threshold
                    elif rule.condition == "memory_percent":
                        return latest_metrics.memory_percent > rule.threshold
                return False

            elif rule.condition == "throughput_rps":
                # Check if throughput is below threshold
                if self.performance_metrics_history:
                    recent_metrics = [m for m in self.performance_metrics_history if
                                    (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 300]
                    if recent_metrics:
                        avg_throughput = sum(m.throughput_rps for m in recent_metrics) / len(recent_metrics)
                        return avg_throughput < rule.threshold
                return False

            return False

        except Exception as e:
            logger.error(f"Error evaluating alert condition {rule.name}: {e}")
            return False

    async def _save_health_metrics(self):
        """Save health metrics to database."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                for metrics in self.health_metrics.values():
                    await conn.execute("""
                        INSERT INTO health_metrics (
                            service_name, port, status, response_time_ms,
                            uptime_seconds, error_count, success_count,
                            constitutional_compliance, constitutional_hash
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    metrics.service_name,
                    metrics.port,
                    metrics.status,
                    metrics.response_time_ms,
                    metrics.uptime_seconds,
                    metrics.error_count,
                    metrics.success_count,
                    metrics.constitutional_compliance,
                    metrics.constitutional_hash
                    )
        except Exception as e:
            logger.error(f"Failed to save health metrics: {e}")

    async def _save_performance_metrics(self):
        """Save performance metrics to database."""
        if not self.db_pool or not self.performance_metrics_history:
            return

        try:
            async with self.db_pool.acquire() as conn:
                # Save recent performance metrics
                recent_metrics = [
                    m for m in self.performance_metrics_history
                    if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 300
                ]

                for metrics in recent_metrics:
                    await conn.execute("""
                        INSERT INTO performance_metrics (
                            service_name, avg_response_time_ms, p99_response_time_ms,
                            throughput_rps, error_rate_percent, cache_hit_rate,
                            constitutional_hash
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    metrics.service_name,
                    metrics.avg_response_time_ms,
                    metrics.p99_response_time_ms,
                    metrics.throughput_rps,
                    metrics.error_rate_percent,
                    metrics.cache_hit_rate,
                    metrics.constitutional_hash
                    )
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")

    async def _save_system_metrics(self, metrics: SystemMetrics):
        """Save system metrics to database."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO system_metrics (
                        cpu_percent, memory_percent, disk_percent,
                        network_bytes_sent, network_bytes_recv, load_average,
                        constitutional_hash
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.disk_percent,
                metrics.network_bytes_sent,
                metrics.network_bytes_recv,
                metrics.load_average,
                metrics.constitutional_hash
                )
        except Exception as e:
            logger.error(f"Failed to save system metrics: {e}")

    async def _save_alert(self, alert: Dict[str, Any]):
        """Save alert to database."""
        if not self.db_pool:
            return

        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO alerts (
                        alert_name, severity, message, service_name,
                        metric_value, threshold_value, constitutional_hash
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                alert["alert_name"],
                alert["severity"],
                alert["message"],
                alert.get("services", [None])[0] if alert.get("services") else None,
                alert.get("metric_value"),
                alert.get("threshold"),
                alert["constitutional_hash"]
                )
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")

    async def _save_monitoring_summary(self, summary: Dict[str, Any]):
        """Save monitoring summary to file."""
        try:
            # Create reports directory
            reports_dir = Path("reports/monitoring")
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_summary_{timestamp}.json"
            filepath = reports_dir / filename

            # Save summary
            with open(filepath, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"✅ Monitoring summary saved to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save monitoring summary: {e}")

    async def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        logger.info("📋 Generating comprehensive monitoring report...")

        try:
            # Calculate overall system health
            healthy_services = sum(
                1 for metrics in self.health_metrics.values()
                if metrics.status == "healthy"
            )
            total_services = len(self.health_metrics)
            health_percentage = (healthy_services / total_services) * 100 if total_services > 0 else 0

            # Calculate average response time
            all_response_times = []
            for response_times in self.response_times.values():
                all_response_times.extend(response_times)

            avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0

            # Get latest system metrics
            latest_system_metrics = self.system_metrics_history[-1] if self.system_metrics_history else None

            # Count alerts by severity
            alert_counts = {"critical": 0, "warning": 0, "info": 0}
            for alert in self.alerts_history:
                severity = alert.get("severity", "info")
                if severity in alert_counts:
                    alert_counts[severity] += 1

            # Check constitutional compliance
            compliant_services = sum(
                1 for metrics in self.health_metrics.values()
                if metrics.constitutional_compliance
            )
            compliance_percentage = (compliant_services / total_services) * 100 if total_services > 0 else 0

            report = {
                "report_timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "monitoring_duration_minutes": (
                    datetime.now(timezone.utc) - self.start_time
                ).total_seconds() / 60,
                "system_health": {
                    "overall_health_percentage": round(health_percentage, 2),
                    "healthy_services": healthy_services,
                    "total_services": total_services,
                    "average_response_time_ms": round(avg_response_time, 2),
                    "constitutional_compliance_percentage": round(compliance_percentage, 2),
                },
                "service_details": {
                    name: {
                        "status": metrics.status,
                        "response_time_ms": metrics.response_time_ms,
                        "success_count": metrics.success_count,
                        "error_count": metrics.error_count,
                        "constitutional_compliance": metrics.constitutional_compliance,
                    }
                    for name, metrics in self.health_metrics.items()
                },
                "system_resources": {
                    "cpu_percent": latest_system_metrics.cpu_percent if latest_system_metrics else 0,
                    "memory_percent": latest_system_metrics.memory_percent if latest_system_metrics else 0,
                    "disk_percent": latest_system_metrics.disk_percent if latest_system_metrics else 0,
                } if latest_system_metrics else {},
                "alerts_summary": {
                    "total_alerts": len(self.alerts_history),
                    "critical_alerts": alert_counts["critical"],
                    "warning_alerts": alert_counts["warning"],
                    "info_alerts": alert_counts["info"],
                    "recent_alerts": list(self.alerts_history)[-5:],  # Last 5 alerts
                },
                "performance_targets": {
                    "response_time_target_met": avg_response_time <= MONITORING_CONFIG["thresholds"]["response_time_ms"],
                    "health_target_met": health_percentage >= 95.0,
                    "compliance_target_met": compliance_percentage >= 95.0,
                },
            }

            # Save report
            await self._save_monitoring_report(report)

            return report

        except Exception as e:
            logger.error(f"Failed to generate monitoring report: {e}")
            return {"error": str(e)}

    async def _save_monitoring_report(self, report: Dict[str, Any]):
        """Save monitoring report to file."""
        try:
            # Create reports directory
            reports_dir = Path("reports/monitoring")
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_report_{timestamp}.json"
            filepath = reports_dir / filename

            # Save report
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Monitoring report saved to {filepath}")

            # Also save latest report
            latest_filepath = reports_dir / "latest_monitoring_report.json"
            with open(latest_filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save monitoring report: {e}")


async def main():
    """Main function for monitoring orchestration."""
    logger.info("🚀 ACGS Monitoring Orchestrator Starting...")

    async with ACGSMonitoringOrchestrator() as orchestrator:
        try:
            # Start monitoring for 5 minutes
            monitoring_task = asyncio.create_task(
                orchestrator.start_comprehensive_monitoring()
            )

            # Wait for monitoring to complete or timeout
            await asyncio.wait_for(monitoring_task, timeout=300)  # 5 minutes

            # Generate final report
            report = await orchestrator.generate_monitoring_report()

            # Print summary
            system_health = report.get("system_health", {})
            alerts_summary = report.get("alerts_summary", {})

            print("\n" + "="*60)
            print("📊 ACGS MONITORING SUMMARY")
            print("="*60)
            print(f"Overall Health: {system_health.get('overall_health_percentage', 0):.1f}%")
            print(f"Healthy Services: {system_health.get('healthy_services', 0)}/{system_health.get('total_services', 0)}")
            print(f"Avg Response Time: {system_health.get('average_response_time_ms', 0):.2f}ms")
            print(f"Constitutional Compliance: {system_health.get('constitutional_compliance_percentage', 0):.1f}%")
            print(f"Total Alerts: {alerts_summary.get('total_alerts', 0)}")
            print(f"Critical Alerts: {alerts_summary.get('critical_alerts', 0)}")

            # Print performance targets status
            targets = report.get("performance_targets", {})
            print(f"\n🎯 PERFORMANCE TARGETS:")
            print(f"Response Time: {'✅' if targets.get('response_time_target_met', False) else '❌'}")
            print(f"Health Target: {'✅' if targets.get('health_target_met', False) else '❌'}")
            print(f"Compliance Target: {'✅' if targets.get('compliance_target_met', False) else '❌'}")

            print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            print("="*60)

        except asyncio.TimeoutError:
            logger.info("⏰ Monitoring completed after timeout")
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
