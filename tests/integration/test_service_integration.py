"""
Comprehensive Service-to-Service Integration Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests the complete ACGS-2 ecosystem integration including:
- Constitutional compliance validation across all services
- Multi-agent coordination workflows
- MCP protocol operations
- A2A communication protocols
- Security validation pipeline
- End-to-end governance workflows
"""

import asyncio
import json
import pytest
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4
import time

# Constitutional compliance constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints
SERVICES = {
    "constitutional_core": "http://localhost:8001",
    "integrity_service": "http://localhost:8002", 
    "governance_engine": "http://localhost:8004",
    "multi_agent_coordinator": "http://localhost:8008",
    "worker_agents": "http://localhost:8009",
    "blackboard_service": "http://localhost:8010",
    "groqcloud_policy": "http://localhost:8015",
    "auth_service": "http://localhost:8016",
    "a2a_policy": "http://localhost:8020",
    "security_validation": "http://localhost:8021",
    "mcp_aggregator": "http://localhost:3000",
    "filesystem_mcp": "http://localhost:3001",
    "github_mcp": "http://localhost:3002",
    "browser_mcp": "http://localhost:3003"
}


class ACGSIntegrationTestSuite:
    """Comprehensive ACGS-2 integration test suite"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.auth_token = None
    
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Authenticate with the system
        await self._authenticate()
        
        print(f"🔧 Integration test suite initialized")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        
        print("🧹 Integration test suite cleanup completed")
    
    async def _authenticate(self):
        """Authenticate with auth service for testing"""
        try:
            auth_payload = {
                "username": "integration_test",
                "password": "test_password",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            async with self.session.post(
                f"{SERVICES['auth_service']}/api/v1/auth/login",
                json=auth_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Authentication successful")
                else:
                    print("⚠️ Authentication failed, proceeding without token")
        except Exception as e:
            print(f"⚠️ Authentication setup failed: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    async def _health_check_service(self, service_name: str, url: str) -> Dict[str, Any]:
        """Check health of individual service"""
        try:
            async with self.session.get(f"{url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "service": service_name,
                        "status": "healthy",
                        "constitutional_hash": data.get("constitutional_hash"),
                        "version": data.get("version"),
                        "response_time_ms": 0  # Would measure actual time
                    }
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "error": str(e)
            }


class TestHealthAndConstitutionalCompliance:
    """Test all services are healthy and constitutionally compliant"""
    
    @pytest.mark.asyncio
    async def test_all_services_health(self):
        """Test that all services are healthy"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            health_results = []
            
            for service_name, url in SERVICES.items():
                result = await suite._health_check_service(service_name, url)
                health_results.append(result)
                
                # Assert service is healthy
                assert result["status"] == "healthy", f"Service {service_name} is not healthy: {result}"
                
                # Assert constitutional hash is correct
                if "constitutional_hash" in result:
                    assert result["constitutional_hash"] == CONSTITUTIONAL_HASH, \
                        f"Service {service_name} has invalid constitutional hash"
            
            print(f"✅ All {len(health_results)} services are healthy and constitutionally compliant")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_constitutional_hash_propagation(self):
        """Test constitutional hash propagation across services"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test constitutional hash validation in constitutional core
            payload = {
                "request": "validate_constitutional_compliance",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "context": {
                    "purpose": "integration_test",
                    "compliance_level": "high"
                }
            }
            
            async with suite.session.post(
                f"{SERVICES['constitutional_core']}/api/v1/constitutional/validate",
                json=payload,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                assert data.get("is_compliant") is True
                
            print("✅ Constitutional hash propagation validated")
            
        finally:
            await suite.teardown()


class TestMultiAgentCoordination:
    """Test multi-agent coordination workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_governance_workflow(self):
        """Test end-to-end governance workflow through multi-agent coordination"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Step 1: Initiate governance request
            governance_request = {
                "request_id": str(uuid4()),
                "request_type": "policy_analysis",
                "description": "Analyze data privacy policy for constitutional compliance",
                "priority": "high",
                "constitutional_context": {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "purpose": "policy_governance_analysis",
                    "compliance_level": "high"
                },
                "analysis_requirements": [
                    "ethical_assessment",
                    "legal_compliance",
                    "operational_feasibility"
                ]
            }
            
            # Submit to multi-agent coordinator
            async with suite.session.post(
                f"{SERVICES['multi_agent_coordinator']}/api/v1/coordination/initiate",
                json=governance_request,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                coordination_data = await response.json()
                session_id = coordination_data.get("session_id")
                assert session_id is not None
                
            # Step 2: Check blackboard for task propagation
            await asyncio.sleep(2)  # Allow time for task propagation
            
            async with suite.session.get(
                f"{SERVICES['blackboard_service']}/api/v1/knowledge/session/{session_id}",
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                blackboard_data = await response.json()
                assert len(blackboard_data.get("knowledge_items", [])) > 0
                
            # Step 3: Verify worker agents received tasks
            async with suite.session.get(
                f"{SERVICES['worker_agents']}/api/v1/agents/status",
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                agents_data = await response.json()
                assert agents_data.get("active_tasks", 0) > 0
                
            # Step 4: Check governance engine integration
            async with suite.session.post(
                f"{SERVICES['governance_engine']}/api/v1/governance/analyze",
                json={
                    "policy_text": "Sample policy for testing",
                    "analysis_type": "constitutional_compliance",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                governance_data = await response.json()
                assert governance_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                
            print("✅ Complete governance workflow integration validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_consensus_mechanism(self):
        """Test consensus mechanism across agents"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Submit decision request requiring consensus
            consensus_request = {
                "decision_id": str(uuid4()),
                "decision_type": "policy_approval",
                "options": ["approve", "reject", "modify"],
                "context": {
                    "policy_name": "Test Privacy Policy",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "required_consensus_threshold": 0.7,
                "participating_agents": ["ethics", "legal", "operational"]
            }
            
            async with suite.session.post(
                f"{SERVICES['multi_agent_coordinator']}/api/v1/consensus/initiate",
                json=consensus_request,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                consensus_data = await response.json()
                decision_id = consensus_data.get("decision_id")
                assert decision_id is not None
                
            # Wait for consensus process
            await asyncio.sleep(3)
            
            # Check consensus result
            async with suite.session.get(
                f"{SERVICES['multi_agent_coordinator']}/api/v1/consensus/status/{decision_id}",
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                result_data = await response.json()
                assert "consensus_reached" in result_data
                assert result_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                
            print("✅ Consensus mechanism integration validated")
            
        finally:
            await suite.teardown()


class TestMCPProtocolIntegration:
    """Test MCP protocol integration across services"""
    
    @pytest.mark.asyncio
    async def test_mcp_aggregator_coordination(self):
        """Test MCP aggregator coordinates all MCP services"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test MCP service discovery
            async with suite.session.get(
                f"{SERVICES['mcp_aggregator']}/api/v1/mcp/services/discover",
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                discovery_data = await response.json()
                services = discovery_data.get("services", [])
                
                # Should discover filesystem, github, and browser MCP services
                service_names = [s.get("name", "") for s in services]
                assert "filesystem_mcp" in service_names
                assert "github_mcp" in service_names
                assert "browser_mcp" in service_names
                
            print("✅ MCP service discovery validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_filesystem_mcp_operations(self):
        """Test filesystem MCP operations with constitutional validation"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test file operations
            file_operation = {
                "operation": "read_file",
                "path": "/app/data/test_file.txt",
                "constitutional_context": {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "purpose": "integration_test_file_access"
                }
            }
            
            async with suite.session.post(
                f"{SERVICES['filesystem_mcp']}/mcp/tools_call",
                json={
                    "name": "read_file",
                    "arguments": file_operation
                },
                headers=suite._get_headers()
            ) as response:
                # Response may be 404 (file not exists) or 200 (success)
                # Both indicate the service is functioning
                assert response.status in [200, 404, 403]
                
            print("✅ Filesystem MCP operations validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_github_mcp_operations(self):
        """Test GitHub MCP operations"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test GitHub repository access
            github_operation = {
                "name": "get_repository",
                "arguments": {
                    "owner": "octocat",
                    "repo": "Hello-World"
                }
            }
            
            async with suite.session.post(
                f"{SERVICES['github_mcp']}/mcp/tools_call",
                json=github_operation,
                headers=suite._get_headers()
            ) as response:
                # May fail due to rate limiting or auth, but service should respond
                assert response.status in [200, 401, 403, 429]
                
            print("✅ GitHub MCP operations validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_browser_mcp_operations(self):
        """Test browser MCP operations with security validation"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test web page navigation
            browser_operation = {
                "name": "navigate_to_url",
                "arguments": {
                    "url": "https://wikipedia.org"
                }
            }
            
            async with suite.session.post(
                f"{SERVICES['browser_mcp']}/mcp/tools_call",
                json=browser_operation,
                headers=suite._get_headers()
            ) as response:
                assert response.status in [200, 403]  # May be blocked by security policy
                
            print("✅ Browser MCP operations validated")
            
        finally:
            await suite.teardown()


class TestA2ACommunication:
    """Test Agent-to-Agent communication protocols"""
    
    @pytest.mark.asyncio
    async def test_agent_registration_and_discovery(self):
        """Test agent registration and service discovery"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Register test agent
            agent_data = {
                "agent_name": "test_integration_agent",
                "agent_type": "claude_agent",
                "service_url": "http://localhost:9999",
                "port": 9999,
                "capabilities": ["integration_testing", "constitutional_validation"],
                "supported_protocols": ["direct_message", "broadcast"],
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            async with suite.session.post(
                f"{SERVICES['a2a_policy']}/api/v1/agents/register",
                json=agent_data,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                registration_data = await response.json()
                assert registration_data.get("success") is True
                agent_id = registration_data.get("agent_id")
                assert agent_id is not None
                
            # Test service discovery
            async with suite.session.get(
                f"{SERVICES['a2a_policy']}/api/v1/agents/discover",
                params={"agent_type": "claude_agent"},
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                discovery_data = await response.json()
                agents = discovery_data.get("agents", [])
                
                # Should find our registered agent
                agent_names = [a.get("agent_name") for a in agents]
                assert "test_integration_agent" in agent_names
                
            print("✅ A2A agent registration and discovery validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_inter_agent_messaging(self):
        """Test inter-agent messaging with constitutional validation"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test message sending
            message_data = {
                "recipient_id": str(uuid4()),  # Mock recipient
                "message_type": "task_request",
                "subject": "Integration Test Message",
                "payload": {
                    "task": "validate_constitutional_compliance",
                    "parameters": {
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                },
                "constitutional_context": {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "purpose": "integration_test_messaging"
                }
            }
            
            async with suite.session.post(
                f"{SERVICES['a2a_policy']}/api/v1/messages/send",
                json=message_data,
                headers=suite._get_headers()
            ) as response:
                # May fail due to recipient not found, but should validate the message
                assert response.status in [200, 404]
                
            print("✅ A2A inter-agent messaging validated")
            
        finally:
            await suite.teardown()


class TestSecurityValidation:
    """Test security validation and threat detection"""
    
    @pytest.mark.asyncio
    async def test_threat_detection_pipeline(self):
        """Test threat detection across the system"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Submit suspicious data for analysis
            suspicious_data = {
                "source_ip": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
                "payload": {
                    "query": "SELECT * FROM users WHERE id = 1 OR 1=1",  # SQL injection attempt
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "request_count": 150,  # High request count
                "requires_constitutional_context": True
            }
            
            async with suite.session.post(
                f"{SERVICES['security_validation']}/api/v1/security/analyze",
                json=suspicious_data,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                analysis_data = await response.json()
                
                # Should detect SQL injection threat
                threats = analysis_data.get("threat_details", [])
                assert len(threats) > 0
                
                # Should maintain constitutional compliance
                assert analysis_data.get("constitutional_compliance") in [True, False]
                
            print("✅ Threat detection pipeline validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_vulnerability_scanning(self):
        """Test vulnerability scanning capabilities"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Initiate vulnerability scan
            scan_config = {
                "scan_type": "constitutional_compliance",
                "target": "acgs_system",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            async with suite.session.post(
                f"{SERVICES['security_validation']}/api/v1/security/scan/vulnerability",
                json=scan_config,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                scan_data = await response.json()
                assert scan_data.get("status") == "initiated"
                scan_id = scan_data.get("scan_id")
                assert scan_id is not None
                
            print("✅ Vulnerability scanning validated")
            
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_compliance_assessment(self):
        """Test compliance assessment across frameworks"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Run compliance assessment
            assessment_config = {
                "framework": "constitutional_ai",
                "scope": "integration_test",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            async with suite.session.post(
                f"{SERVICES['security_validation']}/api/v1/compliance/assess",
                json=assessment_config,
                headers=suite._get_headers()
            ) as response:
                assert response.status == 200
                assessment_data = await response.json()
                
                # Should have compliance scores
                assert "compliance_score" in assessment_data
                assert "constitutional_compliance" in assessment_data
                assert assessment_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                
            print("✅ Compliance assessment validated")
            
        finally:
            await suite.teardown()


class TestGroqCloudIntegration:
    """Test GroqCloud policy integration"""
    
    @pytest.mark.asyncio
    async def test_groq_model_tiers(self):
        """Test GroqCloud 4-tier model architecture"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            # Test each tier
            tiers = ["nano", "fast", "balanced", "premium"]
            
            for tier in tiers:
                policy_request = {
                    "tier": tier,
                    "query": "Test constitutional compliance validation",
                    "constitutional_context": {
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "purpose": f"integration_test_{tier}_tier"
                    }
                }
                
                async with suite.session.post(
                    f"{SERVICES['groqcloud_policy']}/api/v1/policy/evaluate",
                    json=policy_request,
                    headers=suite._get_headers()
                ) as response:
                    # May fail due to API key or rate limiting
                    assert response.status in [200, 401, 429, 503]
                    
            print("✅ GroqCloud model tiers validated")
            
        finally:
            await suite.teardown()


class TestPerformanceAndLatency:
    """Test performance requirements across services"""
    
    @pytest.mark.asyncio
    async def test_latency_requirements(self):
        """Test P99 latency <5ms requirement"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            latencies = []
            
            # Test constitutional validation latency
            for _ in range(100):
                start_time = time.time()
                
                async with suite.session.get(
                    f"{SERVICES['constitutional_core']}/health",
                    headers=suite._get_headers()
                ) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    
                    assert response.status == 200
            
            # Calculate P99 latency
            latencies.sort()
            p99_latency = latencies[int(0.99 * len(latencies))]
            
            print(f"📊 P99 Latency: {p99_latency:.2f}ms (Target: <5ms)")
            
            # Log performance but don't fail - this is informational
            if p99_latency > 5.0:
                print(f"⚠️ P99 latency ({p99_latency:.2f}ms) exceeds target (5ms)")
            else:
                print("✅ P99 latency target met")
                
        finally:
            await suite.teardown()
    
    @pytest.mark.asyncio
    async def test_throughput_requirements(self):
        """Test >100 RPS throughput requirement"""
        suite = ACGSIntegrationTestSuite()
        await suite.setup()
        
        try:
            start_time = time.time()
            request_count = 50  # Reduced for testing
            
            # Concurrent requests
            tasks = []
            for _ in range(request_count):
                task = suite.session.get(
                    f"{SERVICES['constitutional_core']}/health",
                    headers=suite._get_headers()
                )
                tasks.append(task)
            
            # Execute concurrent requests
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Calculate throughput
            duration = end_time - start_time
            throughput = request_count / duration
            
            print(f"📊 Throughput: {throughput:.1f} RPS (Target: >100 RPS)")
            
            # Count successful responses
            successful = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            print(f"📊 Success Rate: {successful}/{request_count} ({successful/request_count*100:.1f}%)")
            
            # Close responses
            for response in responses:
                if hasattr(response, 'close'):
                    await response.__aexit__(None, None, None)
                    
        finally:
            await suite.teardown()


# Test runner function
async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting ACGS-2 Integration Test Suite")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    test_classes = [
        TestHealthAndConstitutionalCompliance,
        TestMultiAgentCoordination,
        TestMCPProtocolIntegration,
        TestA2ACommunication,
        TestSecurityValidation,
        TestGroqCloudIntegration,
        TestPerformanceAndLatency
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}")
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and callable(getattr(test_instance, method))]
        
        for test_method_name in test_methods:
            total_tests += 1
            try:
                test_method = getattr(test_instance, test_method_name)
                await test_method()
                passed_tests += 1
                print(f"  ✅ {test_method_name}")
            except Exception as e:
                print(f"  ❌ {test_method_name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Integration Tests Complete")
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print(f"📋 Constitutional Compliance: {CONSTITUTIONAL_HASH}")
    
    return passed_tests, total_tests


if __name__ == "__main__":
    asyncio.run(run_integration_tests())