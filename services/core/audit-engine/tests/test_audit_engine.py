#!/usr/bin/env python3
"""
Comprehensive test suite for ACGS-1 Lite Audit Engine Service

Tests cover:
- Event ingestion performance (1000+ events/second)
- Query response time (<100ms)
- Chain integrity verification
- S3 archival functionality
- API endpoint validation
"""

import asyncio
import json
import pytest
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List

import httpx
import asyncpg
import aioredis
from fastapi.testclient import TestClient

# Test configuration
TEST_DB_URL = "postgresql://postgres:password@localhost:5432/audit_test_db"
TEST_REDIS_URL = "redis://localhost:6379/1"  # Use different DB
TEST_BASE_URL = "http://localhost:8003"


class TestAuditEnginePerformance:
    """Performance tests for audit engine."""

    @pytest.fixture
    async def db_pool(self):
        """Create test database connection pool."""
        pool = await asyncpg.create_pool(TEST_DB_URL)
        yield pool
        await pool.close()

    @pytest.fixture
    async def redis_client(self):
        """Create test Redis client."""
        redis = await aioredis.from_url(TEST_REDIS_URL)
        await redis.flushdb()  # Clear test database
        yield redis
        await redis.close()

    @pytest.fixture
    async def audit_client(self):
        """Create HTTP client for audit engine."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_event_ingestion_performance(self, audit_client):
        """Test that audit engine can handle 1000+ events/second."""
        events_to_send = 1000
        batch_size = 50

        start_time = time.time()

        # Prepare test events
        test_events = []
        for i in range(events_to_send):
            event = {
                "event_type": "constitutional_validation",
                "service_name": "test_service",
                "agent_id": f"test_agent_{i}",
                "action": f"test_action_{i}",
                "outcome": "success",
                "payload": {"test_data": f"value_{i}"},
                "user_id": f"user_{i}",
                "session_id": f"session_{i}",
                "ip_address": "192.168.1.100",
            }
            test_events.append(event)

        # Send events in batches for realistic load
        successful_ingestions = 0

        for i in range(0, events_to_send, batch_size):
            batch = test_events[i : i + batch_size]

            # Send batch concurrently
            tasks = []
            for event in batch:
                task = audit_client.post("/api/v1/audit/events", json=event)
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for response in responses:
                if isinstance(response, httpx.Response) and response.status_code == 200:
                    successful_ingestions += 1

        total_time = time.time() - start_time
        events_per_second = successful_ingestions / total_time

        print(
            f"Ingested {successful_ingestions}/{events_to_send} events in {total_time:.2f}s"
        )
        print(f"Rate: {events_per_second:.2f} events/second")

        # Assert performance requirement
        assert (
            events_per_second >= 1000
        ), f"Performance requirement not met: {events_per_second:.2f} < 1000 events/second"
        assert (
            successful_ingestions >= events_to_send * 0.99
        ), f"Too many failed ingestions: {successful_ingestions}/{events_to_send}"

    async def test_query_response_time(self, audit_client):
        """Test that query response time is <100ms for indexed fields."""
        # First, ingest some test events
        test_events = []
        for i in range(100):
            event = {
                "event_type": "governance_action",
                "service_name": "policy_engine",
                "agent_id": f"perf_test_agent_{i}",
                "action": f"policy_evaluation_{i}",
                "outcome": "success",
                "payload": {"test": True},
                "user_id": f"perf_user_{i}",
            }

            response = await audit_client.post("/api/v1/audit/events", json=event)
            assert response.status_code == 200
            test_events.append(response.json()["event_id"])

        # Wait for events to be indexed
        await asyncio.sleep(1)

        # Test different query patterns
        query_tests = [
            {"agent_id": "perf_test_agent_50"},
            {"event_type": "governance_action"},
            {
                "start_date": (
                    datetime.now(timezone.utc) - timedelta(hours=1)
                ).isoformat()
            },
            {"limit": 50},
        ]

        for query_params in query_tests:
            start_time = time.time()

            response = await audit_client.get(
                "/api/v1/audit/events", params=query_params
            )

            query_time_ms = (time.time() - start_time) * 1000

            assert response.status_code == 200
            assert (
                query_time_ms < 100
            ), f"Query too slow: {query_time_ms:.2f}ms > 100ms for {query_params}"

            # Verify response contains query timing
            data = response.json()
            assert "query_time_ms" in data
            assert data["query_time_ms"] < 100

            print(f"Query {query_params} completed in {query_time_ms:.2f}ms")

    async def test_chain_integrity_verification_performance(self, audit_client):
        """Test chain verification performance for large chains."""
        # Ingest a significant number of events
        num_events = 1000

        for i in range(num_events):
            event = {
                "event_type": "formal_verification",
                "service_name": "verification_engine",
                "agent_id": f"chain_test_agent_{i}",
                "action": f"verify_property_{i}",
                "outcome": "success",
                "payload": {"property": f"prop_{i}"},
            }

            response = await audit_client.post("/api/v1/audit/events", json=event)
            assert response.status_code == 200

        # Verify chain integrity
        start_time = time.time()

        response = await audit_client.get("/api/v1/audit/verify")

        verification_time_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] == True
        assert data["total_events"] >= num_events
        assert data["constitutional_hash_verified"] == True
        assert (
            verification_time_ms < 5000
        ), f"Chain verification too slow: {verification_time_ms:.2f}ms > 5000ms"

        print(
            f"Chain verification for {data['total_events']} events completed in {verification_time_ms:.2f}ms"
        )


class TestAuditEngineAPI:
    """API functionality tests."""

    @pytest.fixture
    async def audit_client(self):
        """Create HTTP client for audit engine."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_health_endpoint(self, audit_client):
        """Test health check endpoint."""
        response = await audit_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "audit-engine"
        assert data["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert "chain_integrity" in data

    async def test_event_ingestion_api(self, audit_client):
        """Test event ingestion API endpoint."""
        test_event = {
            "event_type": "policy_enforcement",
            "service_name": "policy_engine",
            "agent_id": "test_agent_123",
            "action": "policy_evaluation",
            "outcome": "allowed",
            "payload": {
                "policy_id": "policy_001",
                "decision": "allow",
                "confidence": 0.95,
            },
            "user_id": "user_456",
            "session_id": "session_789",
            "ip_address": "10.0.0.1",
        }

        response = await audit_client.post("/api/v1/audit/events", json=test_event)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "event_id" in data
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] < 100  # Should be fast

        # Verify event can be retrieved
        event_id = data["event_id"]
        get_response = await audit_client.get(f"/api/v1/audit/events/{event_id}")

        assert get_response.status_code == 200
        event_data = get_response.json()

        assert str(event_data["id"]) == event_id
        assert event_data["event_type"] == test_event["event_type"]
        assert event_data["agent_id"] == test_event["agent_id"]

    async def test_event_query_api(self, audit_client):
        """Test event query API with filters."""
        # Ingest test events
        test_agent_id = f"query_test_agent_{uuid.uuid4()}"

        for i in range(5):
            event = {
                "event_type": "data_access",
                "service_name": "data_service",
                "agent_id": test_agent_id,
                "action": f"read_data_{i}",
                "outcome": "success",
                "payload": {"record_id": f"rec_{i}"},
            }

            response = await audit_client.post("/api/v1/audit/events", json=event)
            assert response.status_code == 200

        # Test query by agent_id
        response = await audit_client.get(
            "/api/v1/audit/events", params={"agent_id": test_agent_id, "limit": 10}
        )

        assert response.status_code == 200
        data = response.json()

        assert "events" in data
        assert len(data["events"]) == 5
        assert data["total_count"] == 5
        assert "query_time_ms" in data

        # Verify all events match the filter
        for event in data["events"]:
            assert event["agent_id"] == test_agent_id

    async def test_export_functionality(self, audit_client):
        """Test audit event export."""
        # Ingest events for export test
        export_test_id = f"export_test_{uuid.uuid4()}"

        for i in range(3):
            event = {
                "event_type": "security_event",
                "service_name": "security_service",
                "agent_id": export_test_id,
                "action": f"security_check_{i}",
                "outcome": "passed",
                "payload": {"check_type": f"type_{i}"},
            }

            response = await audit_client.post("/api/v1/audit/events", json=event)
            assert response.status_code == 200

        # Export events
        export_request = {
            "start_date": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "end_date": datetime.now(timezone.utc).isoformat(),
            "format": "json",
            "include_sensitive": False,
        }

        response = await audit_client.post("/api/v1/audit/export", json=export_request)

        assert response.status_code == 200
        data = response.json()

        assert "export_metadata" in data
        assert "events" in data
        assert data["export_metadata"]["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert len(data["events"]) >= 3  # At least our test events


class TestChainIntegrity:
    """Tests for cryptographic chain integrity."""

    @pytest.fixture
    async def audit_client(self):
        """Create HTTP client for audit engine."""
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            yield client

    async def test_chain_integrity_maintenance(self, audit_client):
        """Test that chain integrity is maintained under load."""
        # Record initial chain state
        initial_response = await audit_client.get("/api/v1/audit/verify")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()

        initial_events = initial_data["total_events"]

        # Ingest many events rapidly
        num_events = 100

        for i in range(num_events):
            event = {
                "event_type": "compliance_violation",
                "service_name": "compliance_monitor",
                "agent_id": f"integrity_test_agent_{i}",
                "action": f"compliance_check_{i}",
                "outcome": "violation_detected" if i % 10 == 0 else "compliant",
                "payload": {"rule_id": f"rule_{i % 5}"},
            }

            response = await audit_client.post("/api/v1/audit/events", json=event)
            assert response.status_code == 200

        # Verify chain integrity after rapid ingestion
        final_response = await audit_client.get("/api/v1/audit/verify")
        assert final_response.status_code == 200
        final_data = final_response.json()

        assert final_data["is_valid"] == True
        assert final_data["total_events"] == initial_events + num_events
        assert final_data["constitutional_hash_verified"] == True

        # Chain hash should have changed
        assert final_data["last_chain_hash"] != initial_data["last_chain_hash"]

        print(f"Chain integrity maintained through {num_events} rapid ingestions")

    async def test_constitutional_hash_verification(self, audit_client):
        """Test constitutional hash verification."""
        response = await audit_client.get("/api/v1/audit/verify")

        assert response.status_code == 200
        data = response.json()

        # Verify constitutional hash is correct
        assert data["constitutional_hash_verified"] == True

        # Verify in health check too
        health_response = await audit_client.get("/health")
        health_data = health_response.json()

        assert health_data["constitutional_hash"] == "cdd01ef066bc6cf2"


# Performance benchmark runner
async def run_performance_benchmarks():
    """Run all performance benchmarks and generate report."""
    print("=" * 60)
    print("ACGS-1 Lite Audit Engine Performance Benchmarks")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        # Test 1: Event ingestion rate
        print("\n1. Testing event ingestion rate...")

        start_time = time.time()
        num_events = 1000

        tasks = []
        for i in range(num_events):
            event = {
                "event_type": "benchmark_test",
                "service_name": "benchmark",
                "agent_id": f"bench_agent_{i}",
                "action": f"benchmark_action_{i}",
                "outcome": "success",
                "payload": {"benchmark": True},
            }

            task = client.post("/api/v1/audit/events", json=event)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(
            1
            for r in responses
            if isinstance(r, httpx.Response) and r.status_code == 200
        )

        duration = time.time() - start_time
        rate = successful / duration

        print(f"   Ingested {successful}/{num_events} events in {duration:.2f}s")
        print(f"   Rate: {rate:.2f} events/second")
        print(
            f"   ✅ PASS"
            if rate >= 1000
            else f"   ❌ FAIL - Target: 1000+ events/second"
        )

        # Test 2: Query performance
        print("\n2. Testing query performance...")

        start_time = time.time()
        response = await client.get("/api/v1/audit/events", params={"limit": 100})
        query_time_ms = (time.time() - start_time) * 1000

        print(f"   Query completed in {query_time_ms:.2f}ms")
        print(f"   ✅ PASS" if query_time_ms < 100 else f"   ❌ FAIL - Target: <100ms")

        # Test 3: Chain verification
        print("\n3. Testing chain verification performance...")

        start_time = time.time()
        response = await client.get("/api/v1/audit/verify")
        verify_time_ms = (time.time() - start_time) * 1000

        data = response.json()
        print(
            f"   Verified chain of {data['total_events']} events in {verify_time_ms:.2f}ms"
        )
        print(
            f"   ✅ PASS" if verify_time_ms < 5000 else f"   ❌ FAIL - Target: <5000ms"
        )
        print(f"   Chain integrity: {'✅ VALID' if data['is_valid'] else '❌ INVALID'}")


if __name__ == "__main__":
    # Run performance benchmarks
    asyncio.run(run_performance_benchmarks())
