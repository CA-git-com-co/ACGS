"""
Leader Election Service for ACGS-PGP

Implements distributed leader election pattern for singleton services
like Evolutionary Computation and Democratic Governance Model services.

Key Features:
- Kubernetes-based leader election using lease coordination
- Automatic failover and recovery
- Health monitoring and heartbeat
- Graceful leadership handover
- Constitutional compliance tracking
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Callable
from enum import Enum

# For Kubernetes leader election (when available)
try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException

    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False


class LeadershipState(Enum):
    """Leadership states for the service."""

    CANDIDATE = "candidate"
    LEADER = "leader"
    FOLLOWER = "follower"
    UNAVAILABLE = "unavailable"


@dataclass
class LeaderElectionConfig:
    """Configuration for leader election."""

    service_name: str
    namespace: str = "default"
    lease_duration_seconds: int = 30
    renew_deadline_seconds: int = 10
    retry_period_seconds: int = 5
    health_check_interval: int = 5
    constitutional_hash: str = "cdd01ef066bc6cf2"
    cluster_name: str = "acgs-cluster"

    # Callbacks
    on_started_leading: Optional[Callable] = None
    on_stopped_leading: Optional[Callable] = None
    on_new_leader: Optional[Callable[[str], None]] = None


@dataclass
class LeadershipInfo:
    """Information about current leadership."""

    is_leader: bool = False
    leader_identity: Optional[str] = None
    leadership_acquired_at: Optional[datetime] = None
    lease_expires_at: Optional[datetime] = None
    election_count: int = 0
    state: LeadershipState = LeadershipState.CANDIDATE
    last_heartbeat: Optional[datetime] = None
    health_status: str = "unknown"


class LeaderElectionService:
    """
    Distributed leader election service for ACGS-PGP singleton services.

    Provides leadership coordination for services that need to run as singletons
    in a distributed environment, such as Evolutionary Computation and Democratic
    Governance Model services.
    """

    def __init__(self, config: LeaderElectionConfig):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.config = config
        self.logger = logging.getLogger(f"leader_election.{config.service_name}")

        # Leadership state
        self.leadership_info = LeadershipInfo()
        self.identity = self._generate_identity()
        self.running = False
        self.election_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None

        # Kubernetes client (if available)
        self.k8s_client: Optional[client.CoordinationV1Api] = None
        self.lease_name = f"{config.service_name}-leader"

        # Fallback storage for non-Kubernetes environments
        self.fallback_leader_file = f"/tmp/{self.lease_name}.leader"

        self._initialize_kubernetes_client()

    def _generate_identity(self) -> str:
        """Generate unique identity for this service instance."""
        import socket

        hostname = os.getenv("HOSTNAME", socket.gethostname())
        pid = os.getpid()
        timestamp = int(time.time())

        return f"{hostname}-{pid}-{timestamp}"

    def _initialize_kubernetes_client(self):
        """Initialize Kubernetes client if available."""
        if not KUBERNETES_AVAILABLE:
            self.logger.warning(
                "Kubernetes client not available, using fallback file-based election"
            )
            return

        try:
            # Try in-cluster config first, then local config
            try:
                config.load_incluster_config()
                self.logger.info("Using in-cluster Kubernetes configuration")
            except:
                config.load_kube_config()
                self.logger.info("Using local Kubernetes configuration")

            self.k8s_client = client.CoordinationV1Api()
            self.logger.info("Kubernetes leader election enabled")

        except Exception as e:
            self.logger.warning(f"Failed to initialize Kubernetes client: {e}")
            self.k8s_client = None

    async def start_leader_election(self):
        """Start the leader election process."""
        if self.running:
            self.logger.warning("Leader election already running")
            return

        self.running = True
        self.leadership_info.state = LeadershipState.CANDIDATE

        self.logger.info(f"Starting leader election for {self.config.service_name}")
        self.logger.info(f"Service identity: {self.identity}")
        self.logger.info(f"Constitutional hash: {self.config.constitutional_hash}")

        # Start election and heartbeat tasks
        self.election_task = asyncio.create_task(self._election_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        await asyncio.gather(
            self.election_task, self.heartbeat_task, return_exceptions=True
        )

    async def stop_leader_election(self):
        """Stop the leader election process."""
        self.logger.info("Stopping leader election")
        self.running = False

        # Cancel tasks
        if self.election_task:
            self.election_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Release leadership if we're the leader
        if self.leadership_info.is_leader:
            await self._release_leadership()

    async def _election_loop(self):
        """Main leader election loop."""
        while self.running:
            try:
                if self.k8s_client:
                    await self._kubernetes_election_cycle()
                else:
                    await self._fallback_election_cycle()

                await asyncio.sleep(self.config.retry_period_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Election loop error: {e}")
                await asyncio.sleep(self.config.retry_period_seconds)

    async def _kubernetes_election_cycle(self):
        """Kubernetes-based leader election cycle."""
        try:
            # Try to get existing lease
            lease = await self._get_lease()

            if lease is None:
                # No lease exists, try to create one
                await self._create_lease()
            else:
                # Lease exists, check if we can acquire or renew it
                await self._process_existing_lease(lease)

        except ApiException as e:
            self.logger.error(f"Kubernetes API error: {e}")
            self.leadership_info.state = LeadershipState.UNAVAILABLE
        except Exception as e:
            self.logger.error(f"Election cycle error: {e}")
            self.leadership_info.state = LeadershipState.UNAVAILABLE

    async def _get_lease(self):
        """Get the current lease from Kubernetes."""
        try:
            return self.k8s_client.read_namespaced_lease(
                name=self.lease_name, namespace=self.config.namespace
            )
        except ApiException as e:
            if e.status == 404:
                return None
            raise

    async def _create_lease(self):
        """Create a new lease and become leader."""
        now = datetime.now(timezone.utc)
        lease_body = client.V1Lease(
            metadata=client.V1ObjectMeta(
                name=self.lease_name,
                namespace=self.config.namespace,
            ),
            spec=client.V1LeaseSpec(
                holder_identity=self.identity,
                lease_duration_seconds=self.config.lease_duration_seconds,
                acquire_time=now,
                renew_time=now,
            ),
        )

        try:
            self.k8s_client.create_namespaced_lease(
                namespace=self.config.namespace, body=lease_body
            )
            await self._become_leader()
            self.logger.info("Created lease and became leader")
        except ApiException as e:
            if e.status == 409:
                # Lease was created by another instance
                self.logger.debug("Lease creation conflict, will retry")
            else:
                raise

    async def _process_existing_lease(self, lease):
        """Process an existing lease."""
        holder = lease.spec.holder_identity
        renew_time = lease.spec.renew_time
        lease_duration = (
            lease.spec.lease_duration_seconds or self.config.lease_duration_seconds
        )

        now = datetime.now(timezone.utc)
        lease_expired = (renew_time + timedelta(seconds=lease_duration)) < now

        if holder == self.identity:
            # We're the current leader, renew the lease
            await self._renew_lease(lease)
        elif lease_expired:
            # Lease has expired, try to acquire it
            await self._acquire_lease(lease)
        else:
            # Another service is the leader
            await self._follow_leader(holder)

    async def _renew_lease(self, lease):
        """Renew our lease as the current leader."""
        try:
            lease.spec.renew_time = datetime.now(timezone.utc)

            self.k8s_client.replace_namespaced_lease(
                name=self.lease_name, namespace=self.config.namespace, body=lease
            )

            self.leadership_info.lease_expires_at = lease.spec.renew_time + timedelta(
                seconds=lease.spec.lease_duration_seconds
            )

            if not self.leadership_info.is_leader:
                await self._become_leader()

        except ApiException as e:
            self.logger.error(f"Failed to renew lease: {e}")
            if self.leadership_info.is_leader:
                await self._lose_leadership()

    async def _acquire_lease(self, lease):
        """Try to acquire an expired lease."""
        try:
            now = datetime.now(timezone.utc)
            lease.spec.holder_identity = self.identity
            lease.spec.acquire_time = now
            lease.spec.renew_time = now

            self.k8s_client.replace_namespaced_lease(
                name=self.lease_name, namespace=self.config.namespace, body=lease
            )

            await self._become_leader()
            self.logger.info("Acquired expired lease and became leader")

        except ApiException as e:
            self.logger.debug(f"Failed to acquire lease: {e}")
            if self.leadership_info.is_leader:
                await self._lose_leadership()

    async def _follow_leader(self, leader_identity: str):
        """Follow another leader."""
        if self.leadership_info.is_leader:
            await self._lose_leadership()

        self.leadership_info.leader_identity = leader_identity
        self.leadership_info.state = LeadershipState.FOLLOWER

        # Notify of new leader if changed
        if (
            self.leadership_info.leader_identity != leader_identity
            and self.config.on_new_leader
        ):
            self.config.on_new_leader(leader_identity)

    async def _fallback_election_cycle(self):
        """File-based fallback leader election for non-Kubernetes environments."""
        try:
            now = time.time()

            if os.path.exists(self.fallback_leader_file):
                # Read existing leader info
                with open(self.fallback_leader_file, "r") as f:
                    data = f.read().strip().split(",")
                    if len(data) >= 2:
                        leader_identity = data[0]
                        last_renewal = float(data[1])

                        # Check if lease has expired
                        if (now - last_renewal) > self.config.lease_duration_seconds:
                            # Lease expired, try to acquire
                            await self._acquire_fallback_lease()
                        elif leader_identity == self.identity:
                            # We're the leader, renew
                            await self._renew_fallback_lease()
                        else:
                            # Follow existing leader
                            await self._follow_leader(leader_identity)
                    else:
                        # Invalid file, try to acquire
                        await self._acquire_fallback_lease()
            else:
                # No leader file, try to create
                await self._acquire_fallback_lease()

        except Exception as e:
            self.logger.error(f"Fallback election error: {e}")
            self.leadership_info.state = LeadershipState.UNAVAILABLE

    async def _acquire_fallback_lease(self):
        """Acquire leadership using file-based fallback."""
        try:
            now = time.time()
            temp_file = f"{self.fallback_leader_file}.tmp"

            # Write to temp file first for atomicity
            with open(temp_file, "w") as f:
                f.write(f"{self.identity},{now}")

            # Rename to actual file (atomic operation)
            os.rename(temp_file, self.fallback_leader_file)

            await self._become_leader()
            self.logger.info("Acquired fallback lease and became leader")

        except Exception as e:
            self.logger.error(f"Failed to acquire fallback lease: {e}")

    async def _renew_fallback_lease(self):
        """Renew leadership using file-based fallback."""
        try:
            now = time.time()
            with open(self.fallback_leader_file, "w") as f:
                f.write(f"{self.identity},{now}")

            if not self.leadership_info.is_leader:
                await self._become_leader()

        except Exception as e:
            self.logger.error(f"Failed to renew fallback lease: {e}")
            if self.leadership_info.is_leader:
                await self._lose_leadership()

    async def _become_leader(self):
        """Transition to leader state."""
        if not self.leadership_info.is_leader:
            self.leadership_info.is_leader = True
            self.leadership_info.leader_identity = self.identity
            self.leadership_info.leadership_acquired_at = datetime.now(timezone.utc)
            self.leadership_info.election_count += 1
            self.leadership_info.state = LeadershipState.LEADER

            self.logger.info(f"🏛️ Became leader for {self.config.service_name}")
            self.logger.info(
                f"📋 Constitutional hash: {self.config.constitutional_hash}"
            )
            self.logger.info(
                f"🔢 Election count: {self.leadership_info.election_count}"
            )

            if self.config.on_started_leading:
                try:
                    await self.config.on_started_leading()
                except Exception as e:
                    self.logger.error(f"Error in on_started_leading callback: {e}")

    async def _lose_leadership(self):
        """Transition from leader to follower state."""
        if self.leadership_info.is_leader:
            self.logger.info(f"Lost leadership for {self.config.service_name}")

            self.leadership_info.is_leader = False
            self.leadership_info.state = LeadershipState.FOLLOWER

            if self.config.on_stopped_leading:
                try:
                    await self.config.on_stopped_leading()
                except Exception as e:
                    self.logger.error(f"Error in on_stopped_leading callback: {e}")

    async def _release_leadership(self):
        """Explicitly release leadership."""
        if self.leadership_info.is_leader:
            try:
                if self.k8s_client:
                    # Delete the lease
                    self.k8s_client.delete_namespaced_lease(
                        name=self.lease_name, namespace=self.config.namespace
                    )
                else:
                    # Remove fallback file
                    if os.path.exists(self.fallback_leader_file):
                        os.remove(self.fallback_leader_file)

                await self._lose_leadership()
                self.logger.info("Released leadership")

            except Exception as e:
                self.logger.error(f"Error releasing leadership: {e}")

    async def _heartbeat_loop(self):
        """Health check and heartbeat loop."""
        while self.running:
            try:
                self.leadership_info.last_heartbeat = datetime.now(timezone.utc)

                # Perform health check
                self.leadership_info.health_status = await self._health_check()

                await asyncio.sleep(self.config.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                self.leadership_info.health_status = "unhealthy"
                await asyncio.sleep(self.config.health_check_interval)

    async def _health_check(self) -> str:
        """Perform health check for the service."""
        try:
            # Basic health checks
            if not self.running:
                return "stopped"

            # Check if we can access our lease (if Kubernetes)
            if self.k8s_client and self.leadership_info.is_leader:
                lease = await self._get_lease()
                if lease and lease.spec.holder_identity != self.identity:
                    return "lease_lost"

            # Check constitutional compliance
            constitutional_valid = self.config.constitutional_hash == "cdd01ef066bc6cf2"
            if not constitutional_valid:
                return "constitutional_violation"

            return "healthy"

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return "unhealthy"

    # Public API methods

    def is_leader(self) -> bool:
        """Check if this instance is the current leader."""
        return self.leadership_info.is_leader

    def get_leader_identity(self) -> Optional[str]:
        """Get the identity of the current leader."""
        return self.leadership_info.leader_identity

    def get_leadership_info(self) -> LeadershipInfo:
        """Get detailed leadership information."""
        return self.leadership_info

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information."""
        return {
            "service_name": self.config.service_name,
            "identity": self.identity,
            "is_leader": self.leadership_info.is_leader,
            "leader_identity": self.leadership_info.leader_identity,
            "state": self.leadership_info.state.value,
            "health_status": self.leadership_info.health_status,
            "last_heartbeat": (
                self.leadership_info.last_heartbeat.isoformat()
                if self.leadership_info.last_heartbeat
                else None
            ),
            "leadership_acquired_at": (
                self.leadership_info.leadership_acquired_at.isoformat()
                if self.leadership_info.leadership_acquired_at
                else None
            ),
            "election_count": self.leadership_info.election_count,
            "constitutional_hash": self.config.constitutional_hash,
            "kubernetes_available": KUBERNETES_AVAILABLE
            and self.k8s_client is not None,
        }


# Utility functions for easy integration


async def create_leader_election_service(
    service_name: str,
    namespace: str = "default",
    on_started_leading: Optional[Callable] = None,
    on_stopped_leading: Optional[Callable] = None,
    on_new_leader: Optional[Callable[[str], None]] = None,
    **kwargs,
) -> LeaderElectionService:
    """
    Create and configure a leader election service.

    Args:
        service_name: Name of the service (e.g., "ec-service", "gs-service")
        namespace: Kubernetes namespace
        on_started_leading: Callback when becoming leader
        on_stopped_leading: Callback when losing leadership
        on_new_leader: Callback when a new leader is elected
        **kwargs: Additional configuration parameters

    Returns:
        Configured LeaderElectionService instance
    """
    config = LeaderElectionConfig(
        service_name=service_name,
        namespace=namespace,
        on_started_leading=on_started_leading,
        on_stopped_leading=on_stopped_leading,
        on_new_leader=on_new_leader,
        **kwargs,
    )

    return LeaderElectionService(config)


def leader_required(func):
    """
    Decorator to ensure a function only runs on the leader instance.

    Usage:
        @leader_required
        async def critical_operation(self):
            # This only runs on the leader
            pass
    """

    async def wrapper(self, *args, **kwargs):
        if hasattr(self, "leader_election") and self.leader_election.is_leader():
            return await func(self, *args, **kwargs)
        else:
            raise Exception(f"Operation {func.__name__} requires leadership")

    return wrapper
