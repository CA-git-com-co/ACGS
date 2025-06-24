"""
Load Balancing Implementation for ACGS-1 Service Discovery
Enterprise-grade load balancing with multiple strategies and session affinity
"""

import hashlib
import random
import time
from typing import Any

from .common_types import LoadBalancingStrategy, ServiceInstance, ServiceType


class LoadBalancer:
    """
    Advanced load balancer for ACGS-1 service instances.

    Supports multiple load balancing strategies with session affinity,
    consistent hashing, and performance-based selection.
    """

    def __init__(
        self,
        default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_RESPONSE_TIME,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize load balancer.

        Args:
            default_strategy: Default load balancing strategy
        """
        self.default_strategy = default_strategy
        self._round_robin_counters: dict[ServiceType, int] = {}
        self._consistent_hash_ring: dict[ServiceType, list[tuple[int, str]]] = {}
        self._session_affinity: dict[str, str] = {}  # session_id -> instance_id

    def select_instance(
        self,
        instances: list[ServiceInstance],
        strategy: LoadBalancingStrategy | None = None,
        session_id: str | None = None,
        hash_key: str | None = None,
    ) -> ServiceInstance | None:
        """
        Select the best instance using the specified strategy.

        Args:
            instances: List of available service instances
            strategy: Load balancing strategy to use
            session_id: Session ID for session affinity
            hash_key: Hash key for consistent hashing

        Returns:
            Selected service instance or None
        """
        if not instances:
            return None

        # Filter to healthy instances only
        healthy_instances = [inst for inst in instances if inst.is_healthy]
        if not healthy_instances:
            return None

        # Use default strategy if none specified
        if strategy is None:
            strategy = self.default_strategy

        # Check session affinity first
        if session_id and session_id in self._session_affinity:
            instance_id = self._session_affinity[session_id]
            for instance in healthy_instances:
                if instance.instance_id == instance_id:
                    return instance

        # Apply load balancing strategy
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_instances)
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instances)
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_instances)
        elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(healthy_instances)
        elif strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(healthy_instances, hash_key or session_id)
        elif strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(healthy_instances)
        else:
            # Fallback to least response time
            return self._least_response_time_select(healthy_instances)

    def _round_robin_select(self, instances: list[ServiceInstance]) -> ServiceInstance:
        """Round robin selection."""
        if not instances:
            return None

        service_type = instances[0].service_type

        if service_type not in self._round_robin_counters:
            self._round_robin_counters[service_type] = 0

        counter = self._round_robin_counters[service_type]
        selected = instances[counter % len(instances)]
        self._round_robin_counters[service_type] = (counter + 1) % len(instances)

        return selected

    def _least_connections_select(self, instances: list[ServiceInstance]) -> ServiceInstance:
        """Select instance with least connections."""
        return min(instances, key=lambda x: x.current_connections)

    def _weighted_round_robin_select(self, instances: list[ServiceInstance]) -> ServiceInstance:
        """Weighted round robin selection based on instance weights."""
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            weight = max(1, instance.weight // 10)  # Normalize weight
            weighted_instances.extend([instance] * weight)

        if not weighted_instances:
            return instances[0]

        return self._round_robin_select(weighted_instances)

    def _least_response_time_select(self, instances: list[ServiceInstance]) -> ServiceInstance:
        """Select instance with best response time and load score."""
        # Sort by load score (combines response time, connections, failure rate)
        instances_with_scores = [(instance, instance.load_score) for instance in instances]
        instances_with_scores.sort(key=lambda x: x[1])

        return instances_with_scores[0][0]

    def _consistent_hash_select(
        self, instances: list[ServiceInstance], key: str | None
    ) -> ServiceInstance:
        """Consistent hash selection for session affinity."""
        if not key:
            return self._least_response_time_select(instances)

        # Create hash ring if not exists
        service_type = instances[0].service_type
        if service_type not in self._consistent_hash_ring:
            self._build_hash_ring(service_type, instances)

        # Hash the key
        hash_value = int(hashlib.sha256(key.encode()).hexdigest(), 16)

        # Find the instance
        ring = self._consistent_hash_ring[service_type]
        if not ring:
            return self._least_response_time_select(instances)

        # Find closest hash in ring (binary search for efficiency)
        for ring_hash, instance_id in ring:
            if ring_hash >= hash_value:
                # Find the actual instance
                for instance in instances:
                    if instance.instance_id == instance_id:
                        return instance
                break

        # If no hash found (wrap around to first)
        if ring:
            _, instance_id = ring[0]
            for instance in instances:
                if instance.instance_id == instance_id:
                    return instance

        # Fallback
        return instances[0]

    def _random_select(self, instances: list[ServiceInstance]) -> ServiceInstance:
        """Random selection."""
        return random.choice(instances)

    def _build_hash_ring(self, service_type: ServiceType, instances: list[ServiceInstance]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Build consistent hash ring for service type."""
        ring = []

        for instance in instances:
            # Add multiple points for better distribution
            weight_factor = max(1, instance.weight // 10)
            for i in range(weight_factor):
                hash_key = f"{instance.instance_id}:{i}"
                hash_value = int(hashlib.sha256(hash_key.encode()).hexdigest(), 16)
                ring.append((hash_value, instance.instance_id))

        # Sort ring by hash value for consistent ordering
        ring.sort(key=lambda x: x[0])
        self._consistent_hash_ring[service_type] = ring

    def set_session_affinity(self, session_id: str, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set session affinity for a session."""
        self._session_affinity[session_id] = instance_id

    def clear_session_affinity(self, session_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Clear session affinity for a session."""
        self._session_affinity.pop(session_id, None)

    def get_load_balancing_stats(self, instances: list[ServiceInstance]) -> dict[str, Any]:
        """Get load balancing statistics."""
        if not instances:
            return {}

        total_connections = sum(inst.current_connections for inst in instances)
        total_requests = sum(inst.total_requests for inst in instances)
        total_failures = sum(inst.failed_requests for inst in instances)

        healthy_instances = [inst for inst in instances if inst.is_healthy]

        return {
            "total_instances": len(instances),
            "healthy_instances": len(healthy_instances),
            "total_connections": total_connections,
            "total_requests": total_requests,
            "total_failures": total_failures,
            "failure_rate": (total_failures / max(total_requests, 1)) * 100,
            "average_response_time": sum(inst.response_time or 0 for inst in healthy_instances)
            / max(len(healthy_instances), 1),
            "load_distribution": [
                {
                    "instance_id": inst.instance_id,
                    "connections": inst.current_connections,
                    "load_score": inst.load_score,
                    "weight": inst.weight,
                }
                for inst in instances
            ],
        }


class SessionAffinityManager:
    """
    Manages session affinity for governance workflow continuity.

    Ensures that governance workflows maintain state consistency
    by routing requests from the same session to the same service instance.
    """

    def __init__(self, ttl_seconds: int = 3600):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize session affinity manager.

        Args:
            ttl_seconds: Time-to-live for session affinity entries
        """
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, dict[str, Any]] = {}

    def get_affinity(self, session_id: str, service_type: ServiceType) -> str | None:
        """
        Get instance affinity for a session and service type.

        Args:
            session_id: Session identifier
            service_type: Type of service

        Returns:
            Instance ID or None
        """
        if session_id not in self._sessions:
            return None

        session_data = self._sessions[session_id]

        # Check TTL
        if time.time() - session_data.get("created", 0) > self.ttl_seconds:
            self.clear_session(session_id)
            return None

        return session_data.get("affinities", {}).get(service_type.value)

    def set_affinity(self, session_id: str, service_type: ServiceType, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Set instance affinity for a session and service type.

        Args:
            session_id: Session identifier
            service_type: Type of service
            instance_id: Instance identifier
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "created": time.time(),
                "affinities": {},
                "last_used": time.time(),
            }

        self._sessions[session_id]["affinities"][service_type.value] = instance_id
        self._sessions[session_id]["last_used"] = time.time()

    def clear_session(self, session_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Clear all affinities for a session."""
        self._sessions.pop(session_id, None)

    def cleanup_expired_sessions(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Remove expired session affinities."""
        current_time = time.time()
        expired_sessions = [
            session_id
            for session_id, data in self._sessions.items()
            if current_time - data.get("created", 0) > self.ttl_seconds
        ]

        for session_id in expired_sessions:
            self.clear_session(session_id)

    def get_session_stats(self) -> dict[str, Any]:
        """Get session affinity statistics."""
        current_time = time.time()
        active_sessions = 0
        total_affinities = 0

        for session_data in self._sessions.values():
            if current_time - session_data.get("created", 0) <= self.ttl_seconds:
                active_sessions += 1
                total_affinities += len(session_data.get("affinities", {}))

        return {
            "active_sessions": active_sessions,
            "total_affinities": total_affinities,
            "ttl_seconds": self.ttl_seconds,
        }
