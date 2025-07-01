"""
Distributed Policy Cache with Raft Consensus for ACGS

This module implements a distributed caching system with Raft consensus for
AI governance policies and decisions. It ensures consistency across multiple
nodes while providing high availability and fault tolerance.

Key Features:
- Raft consensus algorithm for distributed consistency
- Policy caching with versioning
- Multi-node coordination
- Fault tolerance and leader election
- Performance optimization for AI governance
- Integration with existing ACGS infrastructure

Based on the Raft consensus algorithm and distributed systems best practices.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
import numpy as np

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """Raft node states."""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class LogEntryType(Enum):
    """Types of log entries."""

    POLICY_UPDATE = "policy_update"
    POLICY_DELETE = "policy_delete"
    CACHE_INVALIDATE = "cache_invalidate"
    CONFIGURATION_CHANGE = "configuration_change"


@dataclass
class LogEntry:
    """Raft log entry."""

    term: int
    index: int
    entry_type: LogEntryType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: str = ""

    def __post_init__(self):
        """Calculate checksum for integrity verification."""
        import hashlib

        content = f"{self.term}:{self.index}:{self.entry_type.value}:{json.dumps(self.data, sort_keys=True)}"
        self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class PolicyCacheEntry:
    """Cached policy entry with metadata."""

    policy_id: str
    policy_data: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl: Optional[int] = None  # Time to live in seconds
    tags: Set[str] = field(default_factory=set)

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if not self.ttl:
            return False

        if not self.last_accessed:
            return False

        elapsed = (datetime.now(timezone.utc) - self.last_accessed).total_seconds()
        return elapsed > self.ttl


@dataclass
class RaftConfig:
    """Configuration for Raft consensus."""

    # Node configuration
    node_id: str
    cluster_nodes: List[str]  # List of node addresses

    # Timing parameters
    election_timeout_min: float = 150.0  # milliseconds
    election_timeout_max: float = 300.0  # milliseconds
    heartbeat_interval: float = 50.0  # milliseconds

    # Performance parameters
    max_log_entries_per_request: int = 100
    snapshot_threshold: int = 1000
    max_cache_size: int = 10000

    # Network configuration
    request_timeout: float = 5.0  # seconds
    max_retries: int = 3


class DistributedPolicyCache:
    """
    Distributed Policy Cache with Raft Consensus.

    Implements a distributed caching system for AI governance policies
    with strong consistency guarantees through Raft consensus.
    """

    def __init__(self, config: RaftConfig):
        """Initialize distributed policy cache."""
        self.config = config
        self.node_id = config.node_id
        self.cluster_nodes = set(config.cluster_nodes)

        # Raft state
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0

        # Leader state
        self.state = NodeState.FOLLOWER
        self.leader_id: Optional[str] = None
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Cache storage
        self.cache: Dict[str, PolicyCacheEntry] = {}
        self.version_vector: Dict[str, int] = {}

        # Timing
        self.last_heartbeat = time.time()
        self.election_timeout = self._random_election_timeout()

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "consensus_operations": 0,
            "leader_elections": 0,
            "log_entries": 0,
        }

        # Network session
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"Initialized distributed cache node {self.node_id}")

    async def start(self):
        """Start the distributed cache node."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
        )

        # Start Raft consensus loop
        asyncio.create_task(self._raft_consensus_loop())

        logger.info(f"Started distributed cache node {self.node_id}")

    async def stop(self):
        """Stop the distributed cache node."""
        if self.session:
            await self.session.close()

        logger.info(f"Stopped distributed cache node {self.node_id}")

    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy from cache with consistency guarantees."""
        self.metrics["total_requests"] += 1

        # Check local cache first
        cache_entry = self.cache.get(policy_id)

        if cache_entry and not cache_entry.is_expired():
            # Update access statistics
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now(timezone.utc)

            self.metrics["cache_hits"] += 1

            logger.debug(f"Cache hit for policy {policy_id}")
            return cache_entry.policy_data

        # Cache miss - need to fetch from leader or consensus
        self.metrics["cache_misses"] += 1

        if self.state == NodeState.LEADER:
            # We are the leader, check if we have the latest version
            return await self._fetch_policy_as_leader(policy_id)
        else:
            # Forward request to leader
            return await self._fetch_policy_from_leader(policy_id)

    async def update_policy(
        self, policy_id: str, policy_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Update policy with distributed consensus."""
        if self.state != NodeState.LEADER:
            # Forward to leader
            return await self._forward_update_to_leader(policy_id, policy_data, ttl)

        # We are the leader, propose the update
        proposal = {
            "type": "policy_update",
            "policy_id": policy_id,
            "policy_data": policy_data,
            "ttl": ttl,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposer": self.node_id,
        }

        # Create log entry
        log_entry = LogEntry(
            term=self.current_term,
            index=len(self.log),
            entry_type=LogEntryType.POLICY_UPDATE,
            data=proposal,
        )

        # Append to local log
        self.log.append(log_entry)
        self.metrics["log_entries"] += 1

        # Replicate to followers
        success = await self._replicate_log_entry(log_entry)

        if success:
            # Apply to local cache
            await self._apply_log_entry(log_entry)
            self.metrics["consensus_operations"] += 1

            logger.info(f"Successfully updated policy {policy_id} via consensus")
            return True
        else:
            # Rollback local log
            self.log.pop()
            self.metrics["log_entries"] -= 1

            logger.warning(f"Failed to achieve consensus for policy {policy_id}")
            return False

    async def delete_policy(self, policy_id: str) -> bool:
        """Delete policy with distributed consensus."""
        if self.state != NodeState.LEADER:
            return await self._forward_delete_to_leader(policy_id)

        proposal = {
            "type": "policy_delete",
            "policy_id": policy_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposer": self.node_id,
        }

        log_entry = LogEntry(
            term=self.current_term,
            index=len(self.log),
            entry_type=LogEntryType.POLICY_DELETE,
            data=proposal,
        )

        self.log.append(log_entry)
        success = await self._replicate_log_entry(log_entry)

        if success:
            await self._apply_log_entry(log_entry)
            logger.info(f"Successfully deleted policy {policy_id} via consensus")
            return True
        else:
            self.log.pop()
            logger.warning(
                f"Failed to achieve consensus for deleting policy {policy_id}"
            )
            return False

    async def _raft_consensus_loop(self):
        """Main Raft consensus loop."""
        while True:
            try:
                if self.state == NodeState.LEADER:
                    await self._leader_heartbeat()
                    await asyncio.sleep(self.config.heartbeat_interval / 1000.0)

                elif self.state == NodeState.FOLLOWER:
                    await self._follower_check_timeout()
                    await asyncio.sleep(0.01)  # 10ms check interval

                elif self.state == NodeState.CANDIDATE:
                    await self._candidate_election()
                    await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in Raft consensus loop: {e}")
                await asyncio.sleep(1.0)

    async def _leader_heartbeat(self):
        """Send heartbeat to all followers."""
        if not self.cluster_nodes:
            return

        heartbeat_tasks = []
        for node in self.cluster_nodes:
            if node != self.node_id:
                task = self._send_heartbeat(node)
                heartbeat_tasks.append(task)

        if heartbeat_tasks:
            await asyncio.gather(*heartbeat_tasks, return_exceptions=True)

    async def _send_heartbeat(self, node: str):
        """Send heartbeat to a specific node."""
        try:
            if not self.session:
                return

            heartbeat_data = {
                "term": self.current_term,
                "leader_id": self.node_id,
                "prev_log_index": len(self.log) - 1 if self.log else -1,
                "prev_log_term": self.log[-1].term if self.log else 0,
                "entries": [],  # Empty for heartbeat
                "leader_commit": self.commit_index,
            }

            async with self.session.post(
                f"http://{node}/raft/append_entries", json=heartbeat_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("term", 0) > self.current_term:
                        # Higher term discovered, step down
                        await self._step_down(result["term"])

        except Exception as e:
            logger.debug(f"Heartbeat failed to {node}: {e}")

    async def _follower_check_timeout(self):
        """Check for election timeout as follower."""
        current_time = time.time()

        if (current_time - self.last_heartbeat) * 1000 > self.election_timeout:
            # Election timeout, become candidate
            logger.info(f"Election timeout, becoming candidate")
            await self._become_candidate()

    async def _become_candidate(self):
        """Transition to candidate state and start election."""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.election_timeout = self._random_election_timeout()
        self.last_heartbeat = time.time()

        logger.info(f"Starting election for term {self.current_term}")
        self.metrics["leader_elections"] += 1

    async def _candidate_election(self):
        """Conduct leader election as candidate."""
        votes_received = 1  # Vote for self

        # Request votes from other nodes
        vote_tasks = []
        for node in self.cluster_nodes:
            if node != self.node_id:
                task = self._request_vote(node)
                vote_tasks.append(task)

        if vote_tasks:
            results = await asyncio.gather(*vote_tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, dict) and result.get("vote_granted"):
                    votes_received += 1

        # Check if we have majority
        majority = len(self.cluster_nodes) // 2 + 1

        if votes_received >= majority:
            await self._become_leader()
        else:
            # Election failed, become follower
            await self._become_follower()

    async def _request_vote(self, node: str) -> Dict[str, Any]:
        """Request vote from a node."""
        try:
            if not self.session:
                return {"vote_granted": False}

            vote_request = {
                "term": self.current_term,
                "candidate_id": self.node_id,
                "last_log_index": len(self.log) - 1 if self.log else -1,
                "last_log_term": self.log[-1].term if self.log else 0,
            }

            async with self.session.post(
                f"http://{node}/raft/request_vote", json=vote_request
            ) as response:
                if response.status == 200:
                    return await response.json()

        except Exception as e:
            logger.debug(f"Vote request failed to {node}: {e}")

        return {"vote_granted": False}

    async def _become_leader(self):
        """Transition to leader state."""
        self.state = NodeState.LEADER
        self.leader_id = self.node_id

        # Initialize leader state
        for node in self.cluster_nodes:
            if node != self.node_id:
                self.next_index[node] = len(self.log)
                self.match_index[node] = 0

        logger.info(f"Became leader for term {self.current_term}")

    async def _become_follower(self, term: Optional[int] = None):
        """Transition to follower state."""
        self.state = NodeState.FOLLOWER

        if term is not None:
            self.current_term = term

        self.voted_for = None
        self.leader_id = None
        self.last_heartbeat = time.time()

        logger.info(f"Became follower for term {self.current_term}")

    async def _step_down(self, new_term: int):
        """Step down from leader/candidate to follower."""
        if new_term > self.current_term:
            await self._become_follower(new_term)

    def _random_election_timeout(self) -> float:
        """Generate random election timeout."""
        return np.random.uniform(
            self.config.election_timeout_min, self.config.election_timeout_max
        )

    async def _replicate_log_entry(self, log_entry: LogEntry) -> bool:
        """Replicate log entry to majority of followers."""
        if not self.cluster_nodes or len(self.cluster_nodes) == 1:
            # Single node cluster, no replication needed
            return True

        replication_tasks = []
        for node in self.cluster_nodes:
            if node != self.node_id:
                task = self._replicate_to_node(node, log_entry)
                replication_tasks.append(task)

        if not replication_tasks:
            return True

        results = await asyncio.gather(*replication_tasks, return_exceptions=True)

        # Count successful replications
        successful_replications = sum(
            1 for result in results if isinstance(result, bool) and result
        )

        # Need majority including self
        majority = len(self.cluster_nodes) // 2 + 1
        total_success = successful_replications + 1  # +1 for self

        return total_success >= majority

    async def _replicate_to_node(self, node: str, log_entry: LogEntry) -> bool:
        """Replicate log entry to a specific node."""
        try:
            if not self.session:
                return False

            # Prepare append entries request
            prev_log_index = log_entry.index - 1
            prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0

            append_request = {
                "term": self.current_term,
                "leader_id": self.node_id,
                "prev_log_index": prev_log_index,
                "prev_log_term": prev_log_term,
                "entries": [
                    {
                        "term": log_entry.term,
                        "index": log_entry.index,
                        "entry_type": log_entry.entry_type.value,
                        "data": log_entry.data,
                        "timestamp": log_entry.timestamp.isoformat(),
                        "checksum": log_entry.checksum,
                    }
                ],
                "leader_commit": self.commit_index,
            }

            async with self.session.post(
                f"http://{node}/raft/append_entries", json=append_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("success", False)

        except Exception as e:
            logger.warning(f"Replication failed to {node}: {e}")

        return False

    async def _apply_log_entry(self, log_entry: LogEntry):
        """Apply log entry to local cache."""
        try:
            if log_entry.entry_type == LogEntryType.POLICY_UPDATE:
                await self._apply_policy_update(log_entry.data)
            elif log_entry.entry_type == LogEntryType.POLICY_DELETE:
                await self._apply_policy_delete(log_entry.data)
            elif log_entry.entry_type == LogEntryType.CACHE_INVALIDATE:
                await self._apply_cache_invalidate(log_entry.data)

            self.last_applied = log_entry.index

        except Exception as e:
            logger.error(f"Failed to apply log entry {log_entry.index}: {e}")

    async def _apply_policy_update(self, data: Dict[str, Any]):
        """Apply policy update to local cache."""
        policy_id = data["policy_id"]
        policy_data = data["policy_data"]
        ttl = data.get("ttl")

        # Get current version
        current_version = self.version_vector.get(policy_id, 0)
        new_version = current_version + 1

        # Create cache entry
        cache_entry = PolicyCacheEntry(
            policy_id=policy_id,
            policy_data=policy_data,
            version=new_version,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            ttl=ttl,
        )

        # Update cache and version vector
        self.cache[policy_id] = cache_entry
        self.version_vector[policy_id] = new_version

        logger.debug(f"Applied policy update for {policy_id}, version {new_version}")

    async def _apply_policy_delete(self, data: Dict[str, Any]):
        """Apply policy deletion to local cache."""
        policy_id = data["policy_id"]

        # Remove from cache and version vector
        self.cache.pop(policy_id, None)
        self.version_vector.pop(policy_id, None)

        logger.debug(f"Applied policy deletion for {policy_id}")

    async def _apply_cache_invalidate(self, data: Dict[str, Any]):
        """Apply cache invalidation."""
        policy_ids = data.get("policy_ids", [])

        for policy_id in policy_ids:
            self.cache.pop(policy_id, None)

        logger.debug(f"Applied cache invalidation for {len(policy_ids)} policies")

    async def _fetch_policy_as_leader(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Fetch policy as leader (authoritative source)."""
        # As leader, our cache is authoritative
        cache_entry = self.cache.get(policy_id)

        if cache_entry and not cache_entry.is_expired():
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now(timezone.utc)
            return cache_entry.policy_data

        return None

    async def _fetch_policy_from_leader(
        self, policy_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch policy from leader node."""
        if not self.leader_id or not self.session:
            return None

        try:
            async with self.session.get(
                f"http://{self.leader_id}/cache/policy/{policy_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    # Update local cache with leader's data
                    if result.get("policy_data"):
                        await self._update_local_cache_from_leader(policy_id, result)

                    return result.get("policy_data")

        except Exception as e:
            logger.warning(f"Failed to fetch policy from leader: {e}")

        return None

    async def _update_local_cache_from_leader(
        self, policy_id: str, leader_data: Dict[str, Any]
    ):
        """Update local cache with data from leader."""
        policy_data = leader_data["policy_data"]
        version = leader_data.get("version", 1)
        ttl = leader_data.get("ttl")

        cache_entry = PolicyCacheEntry(
            policy_id=policy_id,
            policy_data=policy_data,
            version=version,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            ttl=ttl,
        )

        self.cache[policy_id] = cache_entry
        self.version_vector[policy_id] = version

    async def _forward_update_to_leader(
        self, policy_id: str, policy_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Forward update request to leader."""
        if not self.leader_id or not self.session:
            return False

        try:
            update_data = {
                "policy_id": policy_id,
                "policy_data": policy_data,
                "ttl": ttl,
            }

            async with self.session.post(
                f"http://{self.leader_id}/cache/policy", json=update_data
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.warning(f"Failed to forward update to leader: {e}")
            return False

    async def _forward_delete_to_leader(self, policy_id: str) -> bool:
        """Forward delete request to leader."""
        if not self.leader_id or not self.session:
            return False

        try:
            async with self.session.delete(
                f"http://{self.leader_id}/cache/policy/{policy_id}"
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.warning(f"Failed to forward delete to leader: {e}")
            return False

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())

        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "current_term": self.current_term,
            "leader_id": self.leader_id,
            "cluster_size": len(self.cluster_nodes),
            "cache_statistics": {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "total_access_count": sum(
                    entry.access_count for entry in self.cache.values()
                ),
                "average_version": (
                    sum(self.version_vector.values()) / len(self.version_vector)
                    if self.version_vector
                    else 0
                ),
            },
            "raft_statistics": {
                "log_length": len(self.log),
                "commit_index": self.commit_index,
                "last_applied": self.last_applied,
                "next_index": dict(self.next_index),
                "match_index": dict(self.match_index),
            },
            "performance_metrics": self.metrics,
        }

    async def cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        expired_policies = [
            policy_id for policy_id, entry in self.cache.items() if entry.is_expired()
        ]

        for policy_id in expired_policies:
            del self.cache[policy_id]
            self.version_vector.pop(policy_id, None)

        if expired_policies:
            logger.info(f"Cleaned up {len(expired_policies)} expired cache entries")

    def is_version_current(self, policy_id: str, version: int) -> bool:
        """Check if a policy version is current."""
        current_version = self.version_vector.get(policy_id, 0)
        return version >= current_version
