"""
ACGS Code Analysis Engine - Service Registry Client
Integration with ACGS service registry with constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from ..utils.constitutional import CONSTITUTIONAL_HASH, ensure_constitutional_compliance
from ..utils.logging import get_logger, performance_logger

logger = get_logger("services.registry")


class ServiceRegistryClient:
    """
    Service registry client for ACGS Code Analysis Engine.

    Handles service registration, discovery, and health monitoring.
    """

    def __init__(
        self,
        registry_url: str = "http://localhost:8001",
        service_name: str = "acgs-code-analysis-engine",
        service_port: int = 8007,
        health_check_interval: int = 30,
        timeout_seconds: float = 5.0,
    ):
        """
        Initialize service registry client.

        Args:
            registry_url: URL of ACGS service registry
            service_name: Name of this service
            service_port: Port this service runs on
            health_check_interval: Health check interval in seconds
            timeout_seconds: Request timeout
        """
        self.registry_url = registry_url.rstrip("/")
        self.service_name = service_name
        self.service_port = service_port
        self.health_check_interval = health_check_interval
        self.timeout_seconds = timeout_seconds

        # HTTP client
        self.http_client = httpx.AsyncClient(timeout=timeout_seconds)

        # Registration state
        self.is_registered = False
        self.registration_id: Optional[str] = None
        self.last_health_check: Optional[datetime] = None
        self._start_time = time.time()  # Track service start time for metrics

        # Health check task
        self.health_check_task: Optional[asyncio.Task] = None

        logger.info(
            "Service registry client initialized",
            extra={
                "registry_url": registry_url,
                "service_name": service_name,
                "service_port": service_port,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

    async def register_service(self) -> bool:
        """
        Register this service with the service registry.

        Returns:
            bool: True if registration successful
        """
        if self.is_registered:
            logger.warning("Service is already registered")
            return True

        try:
            # Prepare registration data
            registration_data = {
                "service_name": self.service_name,
                "service_port": self.service_port,
                "service_url": f"http://localhost:{self.service_port}",
                "health_check_url": f"http://localhost:{self.service_port}/health",
                "api_version": "v1",
                "service_version": "1.0.0",
                "capabilities": [
                    "semantic_search",
                    "code_analysis",
                    "symbol_extraction",
                    "context_enrichment",
                ],
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "metadata": {
                    "description": (
                        "ACGS Code Analysis Engine for semantic code search and"
                        " analysis"
                    ),
                    "supported_languages": [
                        "python",
                        "javascript",
                        "typescript",
                        "yaml",
                        "json",
                        "sql",
                        "markdown",
                    ],
                    "performance_targets": {
                        "p99_latency_ms": 10,
                        "throughput_rps": 100,
                        "cache_hit_rate": 0.85,
                    },
                },
            }

            # Register with service registry
            response = await self.http_client.post(
                f"{self.registry_url}/api/v1/services/register",
                json=registration_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                },
            )

            if response.status_code == 200:
                result = response.json()
                self.registration_id = result.get("registration_id")
                self.is_registered = True

                logger.info(
                    "Service registered successfully",
                    extra={
                        "registration_id": self.registration_id,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

                # Start health check task
                await self._start_health_checks()

                return True
            else:
                logger.error(
                    f"Service registration failed: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "response": response.text,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
                return False

        except httpx.RequestError as e:
            logger.error(
                f"Service registration request error: {e}",
                extra={
                    "registry_url": self.registry_url,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )
            return False
        except Exception as e:
            logger.error(
                f"Service registration error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            return False

    async def deregister_service(self) -> bool:
        """
        Deregister this service from the service registry.

        Returns:
            bool: True if deregistration successful
        """
        if not self.is_registered or not self.registration_id:
            logger.warning("Service is not registered")
            return True

        try:
            # Stop health checks
            await self._stop_health_checks()

            # Deregister from service registry
            response = await self.http_client.delete(
                f"{self.registry_url}/api/v1/services/{self.registration_id}",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
            )

            if response.status_code in [200, 404]:
                self.is_registered = False
                self.registration_id = None

                logger.info(
                    "Service deregistered successfully",
                    extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                )

                return True
            else:
                logger.error(
                    f"Service deregistration failed: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
                return False

        except httpx.RequestError as e:
            logger.error(
                f"Service deregistration request error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            return False
        except Exception as e:
            logger.error(
                f"Service deregistration error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            return False

    async def discover_service(self, service_name: str) -> Optional[dict[str, Any]]:
        """
        Discover another service in the registry.

        Args:
            service_name: Name of the service to discover

        Returns:
            dict: Service information if found
        """
        try:
            response = await self.http_client.get(
                f"{self.registry_url}/api/v1/services/{service_name}",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
            )

            if response.status_code == 200:
                service_info = response.json()

                # Validate constitutional compliance
                if not self._validate_service_response(service_info):
                    logger.warning(
                        "Service discovery response failed constitutional validation:"
                        f" {service_name}",
                        extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                    )
                    return None

                logger.info(
                    f"Service discovered: {service_name}",
                    extra={
                        "service_name": service_name,
                        "service_url": service_info.get("service_url"),
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

                return service_info
            elif response.status_code == 404:
                logger.info(
                    f"Service not found: {service_name}",
                    extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                )
                return None
            else:
                logger.error(
                    f"Service discovery failed: {response.status_code}",
                    extra={
                        "service_name": service_name,
                        "status_code": response.status_code,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
                return None

        except httpx.RequestError as e:
            logger.error(
                f"Service discovery request error: {e}",
                extra={
                    "service_name": service_name,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                f"Service discovery error: {e}",
                extra={
                    "service_name": service_name,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )
            return None

    async def list_services(self) -> list[dict[str, Any]]:
        """
        List all registered services.

        Returns:
            list: List of registered services
        """
        try:
            response = await self.http_client.get(
                f"{self.registry_url}/api/v1/services",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
            )

            if response.status_code == 200:
                services = response.json()

                # Validate constitutional compliance
                valid_services = []
                for service in services:
                    if self._validate_service_response(service):
                        valid_services.append(service)

                logger.info(
                    f"Listed {len(valid_services)} services",
                    extra={
                        "services_count": len(valid_services),
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

                return valid_services
            else:
                logger.error(
                    f"Service listing failed: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
                return []

        except httpx.RequestError as e:
            logger.error(
                f"Service listing request error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            return []
        except Exception as e:
            logger.error(
                f"Service listing error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            return []

    async def _start_health_checks(self) -> None:
        """Start periodic health checks."""
        if self.health_check_task:
            return

        self.health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info(
            "Health check task started",
            extra={
                "interval_seconds": self.health_check_interval,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

    async def _stop_health_checks(self) -> None:
        """Stop periodic health checks."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None

            logger.info(
                "Health check task stopped",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
            )

    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._send_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Health check loop error: {e}",
                    extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                    exc_info=True,
                )

    async def _send_health_check(self) -> None:
        """Send health check to service registry."""
        if not self.is_registered or not self.registration_id:
            return

        try:
            health_data = {
                "registration_id": self.registration_id,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "metrics": await self._get_real_system_metrics(),
            }

            response = await self.http_client.post(
                f"{self.registry_url}/api/v1/services/{self.registration_id}/health",
                json=health_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                },
            )

            if response.status_code == 200:
                self.last_health_check = datetime.now(timezone.utc)

                performance_logger.log_cache_operation(
                    operation="health_check", cache_hit=True, key="service_registry"
                )
            else:
                logger.warning(
                    f"Health check failed: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

        except Exception as e:
            logger.error(
                f"Health check error: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )

    async def _get_real_system_metrics(self) -> dict[str, Any]:
        """Get real system metrics for health reporting."""
        try:
            import os

            import psutil

            # Get current process
            process = psutil.Process(os.getpid())

            # Calculate uptime
            if not hasattr(self, "_start_time"):
                self._start_time = time.time()
            uptime_seconds = int(time.time() - self._start_time)

            # Get memory usage
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / 1024 / 1024

            # Get CPU usage (averaged over last second)
            cpu_usage_percent = process.cpu_percent()

            # Get system load
            system_load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0

            # Get thread count
            thread_count = process.num_threads()

            # Get file descriptor count (Unix only)
            try:
                fd_count = process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                fd_count = 0

            return {
                "uptime_seconds": uptime_seconds,
                "memory_usage_mb": round(memory_usage_mb, 2),
                "cpu_usage_percent": round(cpu_usage_percent, 2),
                "system_load": round(system_load, 2),
                "thread_count": thread_count,
                "fd_count": fd_count,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "process_id": os.getpid(),
            }

        except ImportError:
            # Fallback if psutil is not available
            logger.warning("psutil not available, using basic metrics")
            return {
                "uptime_seconds": int(
                    time.time() - getattr(self, "_start_time", time.time())
                ),
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "system_load": 0,
                "thread_count": 1,
                "fd_count": 0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "metrics_available": False,
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {
                "uptime_seconds": 0,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

    def _validate_service_response(self, service_data: dict[str, Any]) -> bool:
        """Validate constitutional compliance of service response."""
        # Check for constitutional hash
        service_hash = service_data.get("constitutional_hash")
        if not service_hash or service_hash != CONSTITUTIONAL_HASH:
            return False

        # Check for required fields
        required_fields = ["service_name", "service_url", "health_check_url"]
        for field in required_fields:
            if field not in service_data:
                return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get service registry client status."""
        return ensure_constitutional_compliance({
            "is_registered": self.is_registered,
            "registration_id": self.registration_id,
            "registry_url": self.registry_url,
            "service_name": self.service_name,
            "service_port": self.service_port,
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "health_check_interval": self.health_check_interval,
        })

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.deregister_service()
        await self.http_client.aclose()
