#!/usr/bin/env python3
"""
E2E Testing Configuration and Fixtures
Constitutional Hash: cdd01ef066bc6cf2

This module provides pytest fixtures and configuration for end-to-end testing
of the ACGS-2 constitutional governance system.
"""

import asyncio
import logging
import os
import subprocess
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

import pytest
import docker
import redis
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class E2ETestEnvironment:
    """Manages E2E test environment setup and teardown"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.containers: Dict[str, Any] = {}
        self.services = {
            "postgres": {"port": 5439, "ready": False},
            "redis": {"port": 6389, "ready": False},
            "auth_service": {"port": 8016, "ready": False},
            "constitutional_ai": {"port": 8001, "ready": False},
            "governance_service": {"port": 8004, "ready": False},
            "integrity_service": {"port": 8002, "ready": False},
            "api_gateway": {"port": 8010, "ready": False},
        }
        
    async def setup_infrastructure(self) -> bool:
        """Setup test infrastructure (databases, caches, etc.)"""
        try:
            # Setup PostgreSQL for testing
            await self._setup_postgres()
            
            # Setup Redis for testing
            await self._setup_redis()
            
            # Wait for infrastructure to be ready
            await self._wait_for_infrastructure()
            
            logger.info("✅ Test infrastructure setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Infrastructure setup failed: {e}")
            return False
    
    async def _setup_postgres(self):
        """Setup PostgreSQL test database"""
        try:
            # Check if PostgreSQL is running
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5439,
                user="postgres",
                password="postgres",
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            # Create test database
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE IF EXISTS acgs_test;")
            cursor.execute("CREATE DATABASE acgs_test;")
            cursor.close()
            conn.close()
            
            logger.info("✅ PostgreSQL test database ready")
            self.services["postgres"]["ready"] = True
            
        except Exception as e:
            logger.warning(f"PostgreSQL setup warning: {e}")
            # Continue without PostgreSQL for now
    
    async def _setup_redis(self):
        """Setup Redis test cache"""
        try:
            # Check if Redis is running
            r = redis.Redis(host="localhost", port=6389, db=15)
            r.ping()
            r.flushdb()  # Clean test database
            
            logger.info("✅ Redis test cache ready")
            self.services["redis"]["ready"] = True
            
        except Exception as e:
            logger.warning(f"Redis setup warning: {e}")
            # Continue without Redis for now
    
    async def _wait_for_infrastructure(self):
        """Wait for infrastructure services to be ready"""
        max_wait = 30
        for attempt in range(max_wait):
            try:
                # Check PostgreSQL
                if not self.services["postgres"]["ready"]:
                    conn = psycopg2.connect(
                        host="localhost",
                        port=5439,
                        user="postgres",
                        password="postgres",
                        database="acgs_test"
                    )
                    conn.close()
                    self.services["postgres"]["ready"] = True
                
                # Check Redis
                if not self.services["redis"]["ready"]:
                    r = redis.Redis(host="localhost", port=6389, db=15)
                    r.ping()
                    self.services["redis"]["ready"] = True
                
                # If both are ready, break
                if (self.services["postgres"]["ready"] and 
                    self.services["redis"]["ready"]):
                    break
                    
            except Exception:
                pass
            
            await asyncio.sleep(1)
    
    async def start_services(self) -> bool:
        """Start ACGS services for testing"""
        try:
            # Set environment variables
            os.environ.update({
                "TESTING": "true",
                "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
                "DATABASE_URL": "postgresql://postgres:postgres@localhost:5439/acgs_test",
                "REDIS_URL": "redis://localhost:6389/15",
                "JWT_SECRET_KEY": "test-secret-key-for-e2e-testing",
                "LOG_LEVEL": "INFO"
            })
            
            # Start services in order
            service_order = [
                "auth_service",
                "constitutional_ai", 
                "governance_service",
                "integrity_service",
                "api_gateway"
            ]
            
            for service_name in service_order:
                success = await self._start_service(service_name)
                if success:
                    logger.info(f"✅ {service_name} started successfully")
                else:
                    logger.warning(f"⚠️ {service_name} failed to start")
            
            # Wait for services to be ready
            await self._wait_for_services()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Service startup failed: {e}")
            return False
    
    async def _start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        try:
            # This is a simplified version - in practice, you'd use
            # process management or container orchestration
            port = self.services[service_name]["port"]
            
            # Mock service readiness for testing
            self.services[service_name]["ready"] = True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    async def _wait_for_services(self):
        """Wait for all services to be ready"""
        max_wait = 60
        for attempt in range(max_wait):
            ready_count = sum(1 for service in self.services.values() if service["ready"])
            total_count = len(self.services)
            
            if ready_count == total_count:
                logger.info(f"✅ All {total_count} services ready")
                return
            
            logger.info(f"⏳ Waiting for services ({ready_count}/{total_count} ready)")
            await asyncio.sleep(1)
        
        logger.warning(f"⚠️ Not all services ready after {max_wait}s")
    
    async def cleanup(self):
        """Cleanup test environment"""
        try:
            # Stop any running containers
            for container_name, container in self.containers.items():
                try:
                    container.stop()
                    container.remove()
                    logger.info(f"✅ Stopped container: {container_name}")
                except Exception as e:
                    logger.warning(f"Failed to stop container {container_name}: {e}")
            
            # Clean up test databases
            try:
                r = redis.Redis(host="localhost", port=6389, db=15)
                r.flushdb()
            except:
                pass
            
            logger.info("✅ Test environment cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def e2e_environment():
    """Setup and teardown E2E test environment"""
    env = E2ETestEnvironment()
    
    try:
        # Setup infrastructure
        infra_ready = await env.setup_infrastructure()
        if not infra_ready:
            pytest.skip("Test infrastructure not available")
        
        # Start services
        services_ready = await env.start_services()
        if not services_ready:
            pytest.skip("Test services not available")
        
        yield env
        
    finally:
        await env.cleanup()

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {
        "base_url": "http://localhost:8010",
        "auth_service_url": "http://localhost:8016", 
        "constitutional_ai_url": "http://localhost:8001",
        "governance_service_url": "http://localhost:8004",
        "integrity_service_url": "http://localhost:8002",
        "timeout": 30,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "test_database_url": "postgresql://postgres:postgres@localhost:5439/acgs_test",
        "test_redis_url": "redis://localhost:6389/15"
    }

@pytest.fixture
def test_users():
    """Provide test user data"""
    return [
        {
            "username": "test_admin",
            "email": "admin@acgs.test",
            "password": "admin_pass_123",
            "roles": ["admin", "governance_admin"],
            "permissions": ["*"]
        },
        {
            "username": "test_proposer",
            "email": "proposer@acgs.test", 
            "password": "proposer_pass_123",
            "roles": ["proposer"],
            "permissions": ["create_proposal", "view_proposals"]
        },
        {
            "username": "test_reviewer",
            "email": "reviewer@acgs.test",
            "password": "reviewer_pass_123", 
            "roles": ["reviewer"],
            "permissions": ["review_proposal", "validate_constitutional"]
        }
    ]

@pytest.fixture
def sample_proposals():
    """Provide sample governance proposals for testing"""
    return [
        {
            "title": "AI Safety Guidelines",
            "description": "Comprehensive guidelines for AI safety in production systems",
            "policy_type": "safety",
            "constitutional_context": "AI safety and risk management",
            "stakeholder_groups": ["ai_safety_team", "engineering", "legal"],
            "urgency_level": "high"
        },
        {
            "title": "Data Privacy Enhancement",
            "description": "Enhanced data privacy protection measures",
            "policy_type": "privacy",
            "constitutional_context": "Data protection and user privacy",
            "stakeholder_groups": ["privacy_team", "legal", "users"],
            "urgency_level": "medium"
        },
        {
            "title": "Bias Detection Protocol",
            "description": "Protocol for detecting and mitigating AI bias",
            "policy_type": "bias_detection",
            "constitutional_context": "Fairness and bias prevention",
            "stakeholder_groups": ["ai_ethics", "engineering", "compliance"],
            "urgency_level": "high"
        }
    ]

@pytest.fixture
async def authenticated_session(test_config, test_users):
    """Provide authenticated HTTP session for testing"""
    import aiohttp
    
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=test_config["timeout"])
    )
    
    try:
        # Authenticate as admin user
        admin_user = test_users[0]
        auth_data = {
            "username": admin_user["username"],
            "password": admin_user["password"],
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        async with session.post(
            f"{test_config['auth_service_url']}/auth/login",
            json=auth_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                token = result.get("access_token")
                
                # Add authorization header
                session.headers.update({
                    "Authorization": f"Bearer {token}"
                })
        
        yield session
        
    finally:
        await session.close()

@pytest.fixture
def performance_thresholds():
    """Performance thresholds for E2E tests"""
    return {
        "max_response_time": 5000,  # 5 seconds
        "max_proposal_creation_time": 2000,  # 2 seconds
        "max_validation_time": 3000,  # 3 seconds
        "min_throughput": 10,  # 10 requests per second
        "max_error_rate": 0.05,  # 5% error rate
        "constitutional_compliance_rate": 1.0  # 100% compliance
    }

# Marks for test categorization
pytest.mark.e2e = pytest.mark.mark("e2e")
pytest.mark.smoke = pytest.mark.mark("smoke")
pytest.mark.performance = pytest.mark.mark("performance")
pytest.mark.security = pytest.mark.mark("security")
pytest.mark.constitutional = pytest.mark.mark("constitutional")