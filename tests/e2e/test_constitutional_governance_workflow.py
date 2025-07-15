#!/usr/bin/env python3
"""
End-to-End Constitutional Governance Workflow Tests
Constitutional Hash: cdd01ef066bc6cf2

This module tests complete user workflows through the ACGS-2 constitutional
governance system, validating the entire pipeline from user input to
constitutional compliance validation.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid

import pytest
import aiohttp
import websockets
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class E2ETestConfig:
    """Configuration for E2E tests"""
    base_url: str = "http://localhost:8010"
    auth_service_url: str = "http://localhost:8016"
    constitutional_ai_url: str = "http://localhost:8001"
    integrity_service_url: str = "http://localhost:8002"
    governance_service_url: str = "http://localhost:8004"
    timeout: int = 30
    retry_count: int = 3
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class TestUser:
    """Test user for E2E scenarios"""
    username: str
    email: str
    password: str
    roles: List[str]
    permissions: List[str]

@dataclass
class GovernanceProposal:
    """Test governance proposal"""
    title: str
    description: str
    policy_type: str
    constitutional_context: str
    stakeholder_groups: List[str]
    urgency_level: str = "medium"

class E2ETestSuite:
    """Comprehensive E2E test suite for ACGS-2"""
    
    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_data: Dict[str, Any] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def wait_for_service(self, service_url: str, max_retries: int = 30) -> bool:
        """Wait for service to be available"""
        for attempt in range(max_retries):
            try:
                async with self.session.get(f"{service_url}/health") as response:
                    if response.status == 200:
                        logger.info(f"Service {service_url} is ready")
                        return True
            except Exception as e:
                logger.debug(f"Service {service_url} not ready (attempt {attempt + 1}): {e}")
                await asyncio.sleep(1)
        
        logger.error(f"Service {service_url} failed to become ready after {max_retries} attempts")
        return False
    
    async def authenticate_user(self, user: TestUser) -> bool:
        """Authenticate test user and obtain JWT token"""
        auth_data = {
            "username": user.username,
            "password": user.password,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        try:
            async with self.session.post(
                f"{self.config.auth_service_url}/auth/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    logger.info(f"User {user.username} authenticated successfully")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def create_governance_proposal(self, proposal: GovernanceProposal) -> Optional[str]:
        """Create a governance proposal"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        proposal_data = {
            **asdict(proposal),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "created_at": datetime.utcnow().isoformat(),
            "proposal_id": str(uuid.uuid4())
        }
        
        try:
            async with self.session.post(
                f"{self.config.governance_service_url}/proposals",
                json=proposal_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    proposal_id = result.get("proposal_id")
                    logger.info(f"Proposal created: {proposal_id}")
                    return proposal_id
                else:
                    logger.error(f"Proposal creation failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Proposal creation error: {e}")
            return None
    
    async def validate_constitutional_compliance(self, proposal_id: str) -> Dict[str, Any]:
        """Validate constitutional compliance of a proposal"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.post(
                f"{self.config.constitutional_ai_url}/validate",
                json={
                    "proposal_id": proposal_id,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "validation_type": "comprehensive"
                },
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Constitutional validation completed: {result.get('compliance_score', 'N/A')}")
                    return result
                else:
                    logger.error(f"Constitutional validation failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Constitutional validation error: {e}")
            return {}
    
    async def verify_audit_trail(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Verify audit trail for a proposal"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{self.config.integrity_service_url}/audit/{proposal_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    audit_entries = result.get("audit_entries", [])
                    logger.info(f"Audit trail verified: {len(audit_entries)} entries")
                    return audit_entries
                else:
                    logger.error(f"Audit trail verification failed: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Audit trail verification error: {e}")
            return []
    
    async def monitor_workflow_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Monitor workflow performance metrics"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{self.config.base_url}/metrics/workflow/{workflow_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Workflow performance: {result.get('execution_time', 'N/A')}ms")
                    return result
                else:
                    logger.error(f"Performance monitoring failed: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            return {}

# E2E Test Scenarios

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_governance_workflow():
    """Test complete governance workflow from proposal to approval"""
    config = E2ETestConfig()
    
    # Test user
    test_user = TestUser(
        username="governance_admin",
        email="admin@acgs.test",
        password="test_password_123",
        roles=["governance_admin", "constitutional_reviewer"],
        permissions=["create_proposal", "validate_constitutional", "approve_policy"]
    )
    
    # Test proposal
    test_proposal = GovernanceProposal(
        title="AI Ethics Review Policy",
        description="Comprehensive policy for AI ethics review and approval process",
        policy_type="ethics",
        constitutional_context="AI governance and ethical compliance",
        stakeholder_groups=["ai_developers", "ethics_committee", "legal_team"],
        urgency_level="high"
    )
    
    async with E2ETestSuite(config) as e2e:
        # Step 1: Wait for services to be ready
        services_ready = await asyncio.gather(
            e2e.wait_for_service(config.auth_service_url),
            e2e.wait_for_service(config.constitutional_ai_url),
            e2e.wait_for_service(config.governance_service_url),
            e2e.wait_for_service(config.integrity_service_url)
        )
        
        if not all(services_ready):
            pytest.skip("Required services not available")
        
        # Step 2: Authenticate user
        auth_success = await e2e.authenticate_user(test_user)
        assert auth_success, "User authentication failed"
        
        # Step 3: Create governance proposal
        proposal_id = await e2e.create_governance_proposal(test_proposal)
        assert proposal_id is not None, "Proposal creation failed"
        
        # Step 4: Validate constitutional compliance
        compliance_result = await e2e.validate_constitutional_compliance(proposal_id)
        assert compliance_result, "Constitutional validation failed"
        assert compliance_result.get("constitutional_hash") == CONSTITUTIONAL_HASH
        
        # Step 5: Verify audit trail
        audit_entries = await e2e.verify_audit_trail(proposal_id)
        assert len(audit_entries) > 0, "Audit trail verification failed"
        
        # Step 6: Monitor performance
        performance_metrics = await e2e.monitor_workflow_performance(proposal_id)
        assert performance_metrics, "Performance monitoring failed"
        
        # Validate performance targets
        execution_time = performance_metrics.get("execution_time", 0)
        assert execution_time < 5000, f"Execution time {execution_time}ms exceeds 5s target"
        
        logger.info("✅ Complete governance workflow test passed")

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_user_collaboration():
    """Test multi-user collaboration on governance proposals"""
    config = E2ETestConfig()
    
    # Multiple test users
    users = [
        TestUser("proposer", "proposer@acgs.test", "pass123", ["proposer"], ["create_proposal"]),
        TestUser("reviewer", "reviewer@acgs.test", "pass123", ["reviewer"], ["review_proposal"]),
        TestUser("approver", "approver@acgs.test", "pass123", ["approver"], ["approve_proposal"])
    ]
    
    proposal = GovernanceProposal(
        title="Multi-User Collaboration Test",
        description="Testing collaborative governance workflow",
        policy_type="collaboration",
        constitutional_context="Multi-stakeholder decision making",
        stakeholder_groups=["proposers", "reviewers", "approvers"]
    )
    
    async with E2ETestSuite(config) as e2e:
        # Wait for services
        services_ready = await asyncio.gather(
            e2e.wait_for_service(config.auth_service_url),
            e2e.wait_for_service(config.governance_service_url)
        )
        
        if not all(services_ready):
            pytest.skip("Required services not available")
        
        # Test workflow with multiple users
        proposal_id = None
        
        # User 1: Create proposal
        auth_success = await e2e.authenticate_user(users[0])
        assert auth_success, "Proposer authentication failed"
        
        proposal_id = await e2e.create_governance_proposal(proposal)
        assert proposal_id is not None, "Proposal creation failed"
        
        # User 2: Review proposal
        auth_success = await e2e.authenticate_user(users[1])
        assert auth_success, "Reviewer authentication failed"
        
        compliance_result = await e2e.validate_constitutional_compliance(proposal_id)
        assert compliance_result, "Constitutional validation failed"
        
        # User 3: Approve proposal
        auth_success = await e2e.authenticate_user(users[2])
        assert auth_success, "Approver authentication failed"
        
        audit_entries = await e2e.verify_audit_trail(proposal_id)
        assert len(audit_entries) >= 3, "Insufficient audit trail entries"
        
        logger.info("✅ Multi-user collaboration test passed")

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_constitutional_compliance_edge_cases():
    """Test constitutional compliance with edge cases"""
    config = E2ETestConfig()
    
    test_user = TestUser(
        username="compliance_tester",
        email="compliance@acgs.test",
        password="test_pass_123",
        roles=["compliance_tester"],
        permissions=["create_proposal", "validate_constitutional"]
    )
    
    # Edge case proposals
    edge_case_proposals = [
        GovernanceProposal(
            title="Empty Policy Test",
            description="",
            policy_type="test",
            constitutional_context="minimal",
            stakeholder_groups=["test"]
        ),
        GovernanceProposal(
            title="Maximum Length Policy Test",
            description="X" * 10000,  # Very long description
            policy_type="stress_test",
            constitutional_context="maximum_length_testing",
            stakeholder_groups=["stress_testers"]
        ),
        GovernanceProposal(
            title="Special Characters Test",
            description="Test with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?",
            policy_type="special_chars",
            constitutional_context="character_encoding_test",
            stakeholder_groups=["encoding_testers"]
        )
    ]
    
    async with E2ETestSuite(config) as e2e:
        # Wait for services
        services_ready = await asyncio.gather(
            e2e.wait_for_service(config.auth_service_url),
            e2e.wait_for_service(config.constitutional_ai_url)
        )
        
        if not all(services_ready):
            pytest.skip("Required services not available")
        
        # Authenticate
        auth_success = await e2e.authenticate_user(test_user)
        assert auth_success, "User authentication failed"
        
        # Test each edge case
        for i, proposal in enumerate(edge_case_proposals):
            proposal_id = await e2e.create_governance_proposal(proposal)
            
            if proposal_id:  # Some edge cases might be rejected
                compliance_result = await e2e.validate_constitutional_compliance(proposal_id)
                
                # Verify constitutional hash is always present
                assert compliance_result.get("constitutional_hash") == CONSTITUTIONAL_HASH
                
                logger.info(f"✅ Edge case {i+1} handled correctly")
        
        logger.info("✅ Constitutional compliance edge cases test passed")

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_system_resilience():
    """Test system resilience under load and failure conditions"""
    config = E2ETestConfig()
    
    test_user = TestUser(
        username="resilience_tester",
        email="resilience@acgs.test",
        password="test_pass_123",
        roles=["resilience_tester"],
        permissions=["create_proposal", "validate_constitutional"]
    )
    
    async with E2ETestSuite(config) as e2e:
        # Wait for services
        services_ready = await asyncio.gather(
            e2e.wait_for_service(config.auth_service_url),
            e2e.wait_for_service(config.governance_service_url)
        )
        
        if not all(services_ready):
            pytest.skip("Required services not available")
        
        # Authenticate
        auth_success = await e2e.authenticate_user(test_user)
        assert auth_success, "User authentication failed"
        
        # Test concurrent proposal creation
        concurrent_proposals = [
            GovernanceProposal(
                title=f"Concurrent Proposal {i}",
                description=f"Testing concurrent processing {i}",
                policy_type="concurrency_test",
                constitutional_context="concurrent_processing",
                stakeholder_groups=["concurrent_testers"]
            )
            for i in range(10)
        ]
        
        # Submit proposals concurrently
        proposal_tasks = [
            e2e.create_governance_proposal(proposal)
            for proposal in concurrent_proposals
        ]
        
        proposal_ids = await asyncio.gather(*proposal_tasks, return_exceptions=True)
        
        # Count successful proposals
        successful_proposals = [pid for pid in proposal_ids if isinstance(pid, str)]
        
        # At least 70% should succeed under load
        success_rate = len(successful_proposals) / len(concurrent_proposals)
        assert success_rate >= 0.7, f"Success rate {success_rate:.2f} below 70% threshold"
        
        logger.info(f"✅ System resilience test passed (success rate: {success_rate:.2f})")

if __name__ == "__main__":
    # Run E2E tests
    pytest.main([__file__, "-v", "--tb=short"])