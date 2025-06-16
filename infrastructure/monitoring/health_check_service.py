#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Health Check & Alerting Service
Enterprise-grade health monitoring for constitutional governance system
Target: >99.5% uptime, <500ms response times, >1000 concurrent actions
"""

import asyncio
import aiohttp
import json
import time
import logging
import redis
import psycopg2
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class HealthCheckResult:
    service_name: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class Alert:
    severity: AlertSeverity
    service: str
    message: str
    timestamp: datetime
    details: Dict[str, Any]


class ACGSHealthMonitor:
    """Comprehensive health monitoring for ACGS-1 constitutional governance system."""
    
    def __init__(self, config_path: str = "config/health_monitor_config.json"):
        self.config = self._load_config(config_path)
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.alerts: List[Alert] = []
        self.is_monitoring = False
        
        # Service configuration
        self.services = {
            "auth_service": {"port": 8000, "endpoint": "/health"},
            "ac_service": {"port": 8001, "endpoint": "/health"},
            "integrity_service": {"port": 8002, "endpoint": "/health"},
            "fv_service": {"port": 8003, "endpoint": "/health"},
            "gs_service": {"port": 8004, "endpoint": "/health"},
            "pgc_service": {"port": 8005, "endpoint": "/health"},
            "ec_service": {"port": 8006, "endpoint": "/health"},
        }
        
        # Infrastructure components
        self.infrastructure = {
            "postgresql": {"host": "localhost", "port": 5432, "database": "acgs_pgp_db"},
            "redis": {"host": "localhost", "port": 6379},
            "prometheus": {"host": "localhost", "port": 9090},
            "grafana": {"host": "localhost", "port": 3001},
        }
        
        # Solana/Quantumagi configuration
        self.blockchain = {
            "solana_rpc": "https://api.devnet.solana.com",
            "constitution_hash": "cdd01ef066bc6cf2",
            "program_ids": {
                "quantumagi_core": "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4",
                "appeals": "CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ",
                "logging": "CjZi5hi9qggBzbXDht9YSJhN5cw7Bhz3rHhn63QQcPQo",
            }
        }
        
        # Performance targets
        self.targets = {
            "max_response_time_ms": 500,
            "min_uptime_percentage": 99.5,
            "max_error_rate": 0.01,
            "max_concurrent_actions": 1000,
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load health monitor configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "check_interval": 30,
                "alert_cooldown": 300,
                "max_retries": 3,
                "timeout": 10,
            }

    async def start_monitoring(self):
        """Start continuous health monitoring."""
        self.is_monitoring = True
        logger.info("🚀 Starting ACGS-1 Health Monitor")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_services()),
            asyncio.create_task(self._monitor_infrastructure()),
            asyncio.create_task(self._monitor_blockchain()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._generate_reports()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
        finally:
            self.is_monitoring = False

    async def _monitor_services(self):
        """Monitor ACGS service health."""
        while self.is_monitoring:
            try:
                logger.info("🔍 Checking ACGS services health...")
                
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 10))
                ) as session:
                    
                    for service_name, config in self.services.items():
                        result = await self._check_service_health(
                            session, service_name, config
                        )
                        self.health_results[service_name] = result
                        
                        # Generate alerts if needed
                        await self._evaluate_service_health(result)
                
                await asyncio.sleep(self.config.get("check_interval", 30))
                
            except Exception as e:
                logger.error(f"Service monitoring error: {e}")
                await asyncio.sleep(10)

    async def _check_service_health(
        self, session: aiohttp.ClientSession, service_name: str, config: Dict[str, Any]
    ) -> HealthCheckResult:
        """Check individual service health."""
        start_time = time.time()
        
        try:
            url = f"http://localhost:{config['port']}{config['endpoint']}"
            
            async with session.get(url) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Determine health status based on response
                    status = HealthStatus.HEALTHY
                    if response_time_ms > self.targets["max_response_time_ms"]:
                        status = HealthStatus.DEGRADED
                    
                    return HealthCheckResult(
                        service_name=service_name,
                        status=status,
                        response_time_ms=response_time_ms,
                        timestamp=datetime.now(timezone.utc),
                        details={
                            "http_status": response.status,
                            "response_data": data,
                            "url": url,
                        }
                    )
                else:
                    return HealthCheckResult(
                        service_name=service_name,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=response_time_ms,
                        timestamp=datetime.now(timezone.utc),
                        details={"http_status": response.status, "url": url},
                        error_message=f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(timezone.utc),
                details={"url": f"http://localhost:{config['port']}{config['endpoint']}"},
                error_message=str(e)
            )

    async def _evaluate_service_health(self, result: HealthCheckResult):
        """Evaluate service health and generate alerts."""
        if result.status == HealthStatus.UNHEALTHY:
            await self._create_alert(
                AlertSeverity.CRITICAL,
                result.service_name,
                f"Service {result.service_name} is unhealthy: {result.error_message}",
                result.details
            )
        elif result.status == HealthStatus.DEGRADED:
            await self._create_alert(
                AlertSeverity.HIGH,
                result.service_name,
                f"Service {result.service_name} is degraded (response time: {result.response_time_ms:.2f}ms)",
                result.details
            )

    async def _create_alert(self, severity: AlertSeverity, service: str, message: str, details: Dict[str, Any]):
        """Create and process an alert."""
        alert = Alert(
            severity=severity,
            service=service,
            message=message,
            timestamp=datetime.now(timezone.utc),
            details=details
        )
        
        self.alerts.append(alert)
        logger.warning(f"🚨 ALERT [{severity.value.upper()}] {service}: {message}")
        
        # Send to alerting systems (Prometheus Alertmanager, etc.)
        await self._send_alert_to_systems(alert)

    async def _monitor_infrastructure(self):
        """Monitor infrastructure components (PostgreSQL, Redis, Prometheus, Grafana)."""
        while self.is_monitoring:
            try:
                logger.info("🔍 Checking infrastructure health...")

                # Check PostgreSQL
                await self._check_postgresql_health()

                # Check Redis
                await self._check_redis_health()

                # Check Prometheus
                await self._check_prometheus_health()

                # Check Grafana
                await self._check_grafana_health()

                await asyncio.sleep(self.config.get("check_interval", 30))

            except Exception as e:
                logger.error(f"Infrastructure monitoring error: {e}")
                await asyncio.sleep(10)

    async def _check_postgresql_health(self):
        """Check PostgreSQL database health."""
        try:
            config = self.infrastructure["postgresql"]
            start_time = time.time()

            # Test connection
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                database=config["database"],
                user="acgs_user",
                password="acgs_password",
                connect_timeout=5
            )

            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()

            response_time_ms = (time.time() - start_time) * 1000

            result = HealthCheckResult(
                service_name="postgresql",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(timezone.utc),
                details={"database": config["database"], "host": config["host"]}
            )

            self.health_results["postgresql"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="postgresql",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"database": config["database"], "host": config["host"]},
                error_message=str(e)
            )

            self.health_results["postgresql"] = result
            await self._create_alert(
                AlertSeverity.CRITICAL,
                "postgresql",
                f"PostgreSQL database is unhealthy: {str(e)}",
                {"database": config["database"]}
            )

    async def _check_redis_health(self):
        """Check Redis cache health."""
        try:
            config = self.infrastructure["redis"]
            start_time = time.time()

            # Test Redis connection
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                decode_responses=True,
                socket_timeout=5
            )

            # Test ping
            r.ping()

            # Test set/get
            test_key = "health_check_test"
            r.set(test_key, "test_value", ex=10)
            value = r.get(test_key)
            r.delete(test_key)

            response_time_ms = (time.time() - start_time) * 1000

            result = HealthCheckResult(
                service_name="redis",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(timezone.utc),
                details={"host": config["host"], "port": config["port"]}
            )

            self.health_results["redis"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="redis",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"host": config["host"], "port": config["port"]},
                error_message=str(e)
            )

            self.health_results["redis"] = result
            await self._create_alert(
                AlertSeverity.CRITICAL,
                "redis",
                f"Redis cache is unhealthy: {str(e)}",
                {"host": config["host"]}
            )

    async def _check_prometheus_health(self):
        """Check Prometheus monitoring health."""
        try:
            config = self.infrastructure["prometheus"]
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                url = f"http://{config['host']}:{config['port']}/-/healthy"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time_ms = (time.time() - start_time) * 1000

                    if response.status == 200:
                        result = HealthCheckResult(
                            service_name="prometheus",
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time_ms,
                            timestamp=datetime.now(timezone.utc),
                            details={"url": url}
                        )
                    else:
                        result = HealthCheckResult(
                            service_name="prometheus",
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            timestamp=datetime.now(timezone.utc),
                            details={"url": url, "http_status": response.status},
                            error_message=f"HTTP {response.status}"
                        )

                    self.health_results["prometheus"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="prometheus",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"host": config["host"], "port": config["port"]},
                error_message=str(e)
            )

            self.health_results["prometheus"] = result

    async def _check_grafana_health(self):
        """Check Grafana dashboard health."""
        try:
            config = self.infrastructure["grafana"]
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                url = f"http://{config['host']}:{config['port']}/api/health"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time_ms = (time.time() - start_time) * 1000

                    if response.status == 200:
                        result = HealthCheckResult(
                            service_name="grafana",
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time_ms,
                            timestamp=datetime.now(timezone.utc),
                            details={"url": url}
                        )
                    else:
                        result = HealthCheckResult(
                            service_name="grafana",
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            timestamp=datetime.now(timezone.utc),
                            details={"url": url, "http_status": response.status},
                            error_message=f"HTTP {response.status}"
                        )

                    self.health_results["grafana"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="grafana",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"host": config["host"], "port": config["port"]},
                error_message=str(e)
            )

            self.health_results["grafana"] = result

    async def _monitor_blockchain(self):
        """Monitor Solana blockchain and Quantumagi deployment health."""
        while self.is_monitoring:
            try:
                logger.info("🔍 Checking blockchain health...")

                # Check Solana network connectivity
                await self._check_solana_health()

                # Check Quantumagi program deployment
                await self._check_quantumagi_health()

                # Check Constitution Hash integrity
                await self._check_constitution_hash()

                await asyncio.sleep(self.config.get("check_interval", 30) * 2)  # Less frequent checks

            except Exception as e:
                logger.error(f"Blockchain monitoring error: {e}")
                await asyncio.sleep(30)

    async def _check_solana_health(self):
        """Check Solana network health."""
        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                # Check Solana RPC health
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth"
                }

                async with session.post(
                    self.blockchain["solana_rpc"],
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()

                        if data.get("result") == "ok":
                            result = HealthCheckResult(
                                service_name="solana_network",
                                status=HealthStatus.HEALTHY,
                                response_time_ms=response_time_ms,
                                timestamp=datetime.now(timezone.utc),
                                details={"rpc_url": self.blockchain["solana_rpc"], "result": data.get("result")}
                            )
                        else:
                            result = HealthCheckResult(
                                service_name="solana_network",
                                status=HealthStatus.DEGRADED,
                                response_time_ms=response_time_ms,
                                timestamp=datetime.now(timezone.utc),
                                details={"rpc_url": self.blockchain["solana_rpc"], "result": data.get("result")},
                                error_message="Solana network not fully healthy"
                            )
                    else:
                        result = HealthCheckResult(
                            service_name="solana_network",
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            timestamp=datetime.now(timezone.utc),
                            details={"rpc_url": self.blockchain["solana_rpc"], "http_status": response.status},
                            error_message=f"HTTP {response.status}"
                        )

                    self.health_results["solana_network"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="solana_network",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"rpc_url": self.blockchain["solana_rpc"]},
                error_message=str(e)
            )

            self.health_results["solana_network"] = result
            await self._create_alert(
                AlertSeverity.HIGH,
                "solana_network",
                f"Solana network connectivity issues: {str(e)}",
                {"rpc_url": self.blockchain["solana_rpc"]}
            )

    async def _check_quantumagi_health(self):
        """Check Quantumagi program deployment health."""
        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                # Check if programs are deployed and executable
                healthy_programs = 0
                total_programs = len(self.blockchain["program_ids"])

                for program_name, program_id in self.blockchain["program_ids"].items():
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getAccountInfo",
                        "params": [program_id, {"encoding": "base64"}]
                    }

                    async with session.post(
                        self.blockchain["solana_rpc"],
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            account_info = data.get("result", {}).get("value")

                            if account_info and account_info.get("executable"):
                                healthy_programs += 1

                response_time_ms = (time.time() - start_time) * 1000

                if healthy_programs == total_programs:
                    status = HealthStatus.HEALTHY
                    message = f"All {total_programs} Quantumagi programs deployed"
                elif healthy_programs > 0:
                    status = HealthStatus.DEGRADED
                    message = f"{healthy_programs}/{total_programs} Quantumagi programs deployed"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = "No Quantumagi programs found"

                result = HealthCheckResult(
                    service_name="quantumagi_programs",
                    status=status,
                    response_time_ms=response_time_ms,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "healthy_programs": healthy_programs,
                        "total_programs": total_programs,
                        "program_ids": self.blockchain["program_ids"]
                    },
                    error_message=message if status != HealthStatus.HEALTHY else None
                )

                self.health_results["quantumagi_programs"] = result

                if status == HealthStatus.UNHEALTHY:
                    await self._create_alert(
                        AlertSeverity.CRITICAL,
                        "quantumagi_programs",
                        message,
                        {"program_ids": self.blockchain["program_ids"]}
                    )

        except Exception as e:
            result = HealthCheckResult(
                service_name="quantumagi_programs",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"program_ids": self.blockchain["program_ids"]},
                error_message=str(e)
            )

            self.health_results["quantumagi_programs"] = result

    async def _check_constitution_hash(self):
        """Check Constitution Hash integrity."""
        try:
            # Check if PGC service can validate the constitution hash
            async with aiohttp.ClientSession() as session:
                url = "http://localhost:8005/api/v1/constitutional/validate"
                params = {"hash_value": self.blockchain["constitution_hash"]}

                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("valid", False):
                            result = HealthCheckResult(
                                service_name="constitution_hash",
                                status=HealthStatus.HEALTHY,
                                response_time_ms=(time.time() - time.time()) * 1000,
                                timestamp=datetime.now(timezone.utc),
                                details={"hash": self.blockchain["constitution_hash"], "validation": data}
                            )
                        else:
                            result = HealthCheckResult(
                                service_name="constitution_hash",
                                status=HealthStatus.UNHEALTHY,
                                response_time_ms=0,
                                timestamp=datetime.now(timezone.utc),
                                details={"hash": self.blockchain["constitution_hash"], "validation": data},
                                error_message="Constitution hash validation failed"
                            )
                    else:
                        result = HealthCheckResult(
                            service_name="constitution_hash",
                            status=HealthStatus.UNKNOWN,
                            response_time_ms=0,
                            timestamp=datetime.now(timezone.utc),
                            details={"hash": self.blockchain["constitution_hash"]},
                            error_message=f"PGC service unavailable (HTTP {response.status})"
                        )

                    self.health_results["constitution_hash"] = result

        except Exception as e:
            result = HealthCheckResult(
                service_name="constitution_hash",
                status=HealthStatus.UNKNOWN,
                response_time_ms=0,
                timestamp=datetime.now(timezone.utc),
                details={"hash": self.blockchain["constitution_hash"]},
                error_message=str(e)
            )

            self.health_results["constitution_hash"] = result

    async def _process_alerts(self):
        """Process and manage alerts."""
        while self.is_monitoring:
            try:
                # Clean up old alerts
                cutoff_time = datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour-24)
                self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]

                await asyncio.sleep(60)  # Process alerts every minute

            except Exception as e:
                logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(60)

    async def _generate_reports(self):
        """Generate periodic health reports."""
        while self.is_monitoring:
            try:
                # Generate health report every 5 minutes
                await asyncio.sleep(300)

                summary = self.get_health_summary()

                # Save report to file
                report_path = Path("logs/health_reports")
                report_path.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                report_file = report_path / f"health_report_{timestamp}.json"

                with open(report_file, 'w') as f:
                    json.dump(summary, f, indent=2, default=str)

                logger.info(f"📊 Health report generated: {report_file}")

            except Exception as e:
                logger.error(f"Report generation error: {e}")
                await asyncio.sleep(300)

    async def _send_alert_to_systems(self, alert: Alert):
        """Send alert to external alerting systems."""
        # Implementation for sending to Prometheus Alertmanager, Slack, etc.
        pass

    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.is_monitoring = False
        logger.info("🛑 Stopping ACGS-1 Health Monitor")

    def get_health_summary(self) -> Dict[str, Any]:
        """Get current health summary."""
        healthy_services = sum(1 for result in self.health_results.values()
                             if result.status == HealthStatus.HEALTHY)
        total_services = len(self.health_results)

        avg_response_time = sum(result.response_time_ms for result in self.health_results.values()) / max(total_services, 1)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy" if healthy_services == total_services else "degraded",
            "healthy_services": healthy_services,
            "total_services": total_services,
            "average_response_time_ms": round(avg_response_time, 2),
            "active_alerts": len([a for a in self.alerts if a.timestamp > datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour-1)]),
            "services": {name: asdict(result) for name, result in self.health_results.items()}
        }


if __name__ == "__main__":
    async def main():
        monitor = ACGSHealthMonitor()
        try:
            await monitor.start_monitoring()
        except KeyboardInterrupt:
            await monitor.stop_monitoring()
    
    asyncio.run(main())
