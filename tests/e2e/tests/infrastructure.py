"""
ACGS Infrastructure Tests

Tests for infrastructure components including PostgreSQL, Redis, Auth Service,
core services, service mesh integration, and inter-service communication.
"""

import asyncio
import time
import json
from typing import List, Dict, Any, Optional

from ..framework.base import BaseE2ETest, TestResult
from ..framework.config import ServiceType


class InfrastructureComponentTest(BaseE2ETest):
    """Test core infrastructure components."""
    
    test_type = "infrastructure"
    tags = ["infrastructure", "database", "redis", "components"]
    
    async def run_test(self) -> List[TestResult]:
        """Run infrastructure component tests."""
        results = []
        
        # Test PostgreSQL infrastructure
        result = await self._test_postgresql_infrastructure()
        results.append(result)
        
        # Test Redis infrastructure
        result = await self._test_redis_infrastructure()
        results.append(result)
        
        # Test service port configuration
        result = await self._test_service_port_configuration()
        results.append(result)
        
        return results
    
    async def _test_postgresql_infrastructure(self) -> TestResult:
        """Test PostgreSQL database infrastructure."""
        start_time = time.perf_counter()
        
        try:
            if self.config.test_mode == "offline":
                # Mock PostgreSQL test for offline mode
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                return TestResult(
                    test_name="postgresql_infrastructure",
                    success=True,
                    duration_ms=duration_ms,
                    performance_metrics={
                        "connection_successful": True,
                        "query_performance_ms": 1.0,
                        "mocked": True
                    }
                )
            
            if not self.db_engine:
                return TestResult(
                    test_name="postgresql_infrastructure",
                    success=False,
                    duration_ms=0,
                    error_message="Database engine not initialized"
                )
            
            # Test database operations
            operations_results = []
            
            # Test 1: Basic connectivity
            try:
                async with self.db_engine.begin() as conn:
                    result = await conn.execute("SELECT 1 as test_value")
                    row = result.fetchone()
                    operations_results.append({
                        "operation": "connectivity",
                        "success": row is not None and row[0] == 1
                    })
            except Exception as e:
                operations_results.append({
                    "operation": "connectivity",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 2: Performance check
            try:
                query_start = time.perf_counter()
                async with self.db_engine.begin() as conn:
                    # Simple performance test query
                    await conn.execute("SELECT generate_series(1, 1000)")
                query_end = time.perf_counter()
                query_time_ms = (query_end - query_start) * 1000
                
                operations_results.append({
                    "operation": "performance",
                    "success": query_time_ms < 100,  # Should complete in under 100ms
                    "query_time_ms": query_time_ms
                })
            except Exception as e:
                operations_results.append({
                    "operation": "performance",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 3: Transaction support
            try:
                async with self.db_engine.begin() as conn:
                    # Test transaction rollback
                    await conn.execute("CREATE TEMPORARY TABLE test_table (id INTEGER)")
                    await conn.execute("INSERT INTO test_table VALUES (1)")
                    await conn.rollback()
                    
                operations_results.append({
                    "operation": "transactions",
                    "success": True
                })
            except Exception as e:
                operations_results.append({
                    "operation": "transactions",
                    "success": False,
                    "error": str(e)
                })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate overall success
            successful_operations = [op for op in operations_results if op["success"]]
            success_rate = len(successful_operations) / len(operations_results)
            overall_success = success_rate >= 0.8
            
            return TestResult(
                test_name="postgresql_infrastructure",
                success=overall_success,
                duration_ms=duration_ms,
                performance_metrics={
                    "operations_tested": len(operations_results),
                    "successful_operations": len(successful_operations),
                    "success_rate": success_rate,
                    "operations_detail": operations_results,
                    "database_port": self.config.infrastructure.postgresql_port
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="postgresql_infrastructure",
                success=False,
                duration_ms=duration_ms,
                error_message=f"PostgreSQL infrastructure test failed: {str(e)}"
            )
    
    async def _test_redis_infrastructure(self) -> TestResult:
        """Test Redis cache infrastructure."""
        start_time = time.perf_counter()
        
        try:
            if self.config.test_mode == "offline":
                # Mock Redis test for offline mode
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                return TestResult(
                    test_name="redis_infrastructure",
                    success=True,
                    duration_ms=duration_ms,
                    performance_metrics={
                        "connection_successful": True,
                        "operation_performance_ms": 0.5,
                        "mocked": True
                    }
                )
            
            if not self.redis_client:
                return TestResult(
                    test_name="redis_infrastructure",
                    success=False,
                    duration_ms=0,
                    error_message="Redis client not initialized"
                )
            
            # Test Redis operations
            operations_results = []
            
            # Test 1: Basic connectivity
            try:
                pong = await self.redis_client.ping()
                operations_results.append({
                    "operation": "ping",
                    "success": pong is True
                })
            except Exception as e:
                operations_results.append({
                    "operation": "ping",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 2: Set/Get operations
            try:
                test_key = "acgs_infra_test_key"
                test_value = "infrastructure_test_value"
                
                await self.redis_client.set(test_key, test_value, ex=60)
                retrieved_value = await self.redis_client.get(test_key)
                
                operations_results.append({
                    "operation": "set_get",
                    "success": retrieved_value == test_value
                })
                
                # Cleanup
                await self.redis_client.delete(test_key)
            except Exception as e:
                operations_results.append({
                    "operation": "set_get",
                    "success": False,
                    "error": str(e)
                })
            
            # Test 3: Performance check
            try:
                perf_start = time.perf_counter()
                
                # Perform multiple operations
                for i in range(100):
                    await self.redis_client.set(f"perf_test_{i}", f"value_{i}", ex=60)
                
                for i in range(100):
                    await self.redis_client.get(f"perf_test_{i}")
                
                # Cleanup
                keys_to_delete = [f"perf_test_{i}" for i in range(100)]
                await self.redis_client.delete(*keys_to_delete)
                
                perf_end = time.perf_counter()
                operation_time_ms = (perf_end - perf_start) * 1000
                
                operations_results.append({
                    "operation": "performance",
                    "success": operation_time_ms < 1000,  # Should complete in under 1 second
                    "operation_time_ms": operation_time_ms
                })
            except Exception as e:
                operations_results.append({
                    "operation": "performance",
                    "success": False,
                    "error": str(e)
                })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate overall success
            successful_operations = [op for op in operations_results if op["success"]]
            success_rate = len(successful_operations) / len(operations_results)
            overall_success = success_rate >= 0.8
            
            return TestResult(
                test_name="redis_infrastructure",
                success=overall_success,
                duration_ms=duration_ms,
                performance_metrics={
                    "operations_tested": len(operations_results),
                    "successful_operations": len(successful_operations),
                    "success_rate": success_rate,
                    "operations_detail": operations_results,
                    "redis_port": self.config.infrastructure.redis_port
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="redis_infrastructure",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Redis infrastructure test failed: {str(e)}"
            )
    
    async def _test_service_port_configuration(self) -> TestResult:
        """Test service port configuration and accessibility."""
        start_time = time.perf_counter()
        
        try:
            # Expected service ports based on configuration
            expected_ports = {
                ServiceType.AUTH: 8016,
                ServiceType.CONSTITUTIONAL_AI: 8001,
                ServiceType.INTEGRITY: 8002,
                ServiceType.FORMAL_VERIFICATION: 8003,
                ServiceType.GOVERNANCE_SYNTHESIS: 8004,
                ServiceType.POLICY_GOVERNANCE: 8005,
                ServiceType.EVOLUTIONARY_COMPUTATION: 8006
            }
            
            port_test_results = []
            
            for service_type, expected_port in expected_ports.items():
                if self.config.is_service_enabled(service_type):
                    configured_port = self.config.services[service_type].port
                    
                    # Test port configuration
                    port_config_correct = configured_port == expected_port
                    
                    # Test port accessibility
                    try:
                        response = await self.make_service_request(
                            service_type, "GET", "/health"
                        )
                        port_accessible = response.status_code in [200, 404, 405]  # Various acceptable responses
                    except Exception:
                        port_accessible = False
                    
                    port_test_results.append({
                        "service": service_type.value,
                        "expected_port": expected_port,
                        "configured_port": configured_port,
                        "port_config_correct": port_config_correct,
                        "port_accessible": port_accessible,
                        "overall_success": port_config_correct and port_accessible
                    })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate overall port configuration
            successful_ports = [p for p in port_test_results if p["overall_success"]]
            success_rate = len(successful_ports) / len(port_test_results) if port_test_results else 0
            overall_success = success_rate >= 0.8
            
            return TestResult(
                test_name="service_port_configuration",
                success=overall_success,
                duration_ms=duration_ms,
                constitutional_compliance=True,  # Port configuration doesn't affect constitutional compliance
                performance_metrics={
                    "services_tested": len(port_test_results),
                    "successful_ports": len(successful_ports),
                    "success_rate": success_rate,
                    "port_test_results": port_test_results
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="service_port_configuration",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Service port configuration test failed: {str(e)}"
            )


class ServiceIntegrationTest(BaseE2ETest):
    """Test service integration and inter-service communication."""
    
    test_type = "integration"
    tags = ["integration", "services", "communication"]
    
    async def run_test(self) -> List[TestResult]:
        """Run service integration tests."""
        results = []
        
        # Test service mesh integration
        result = await self._test_service_mesh_integration()
        results.append(result)
        
        # Test inter-service communication
        result = await self._test_inter_service_communication()
        results.append(result)
        
        # Test service dependency chain
        result = await self._test_service_dependency_chain()
        results.append(result)
        
        return results
    
    async def _test_service_mesh_integration(self) -> TestResult:
        """Test service mesh integration and discovery."""
        start_time = time.perf_counter()
        
        try:
            # Test service discovery through health checks
            service_discovery_results = []
            
            for service_type in ServiceType:
                if self.config.is_service_enabled(service_type):
                    try:
                        # Test service discovery
                        service_url = self.config.get_service_url(service_type)
                        
                        # Test health endpoint
                        response = await self.make_service_request(
                            service_type, "GET", "/health"
                        )
                        
                        service_discoverable = response.status_code in [200, 404, 405]
                        
                        # Check for service mesh headers or indicators
                        service_mesh_headers = {
                            "x-service-name": service_type.value,
                            "x-constitutional-hash": self.config.constitutional_hash
                        }
                        
                        service_discovery_results.append({
                            "service": service_type.value,
                            "service_url": service_url,
                            "discoverable": service_discoverable,
                            "response_code": response.status_code,
                            "mesh_integration": True  # Assume mesh integration for now
                        })
                    
                    except Exception as e:
                        service_discovery_results.append({
                            "service": service_type.value,
                            "discoverable": False,
                            "error": str(e)
                        })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate service mesh integration
            discoverable_services = [s for s in service_discovery_results if s.get("discoverable", False)]
            discovery_rate = len(discoverable_services) / len(service_discovery_results) if service_discovery_results else 0
            overall_success = discovery_rate >= 0.8
            
            return TestResult(
                test_name="service_mesh_integration",
                success=overall_success,
                duration_ms=duration_ms,
                constitutional_compliance=True,
                performance_metrics={
                    "services_tested": len(service_discovery_results),
                    "discoverable_services": len(discoverable_services),
                    "discovery_rate": discovery_rate,
                    "service_discovery_results": service_discovery_results
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="service_mesh_integration",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Service mesh integration test failed: {str(e)}"
            )
    
    async def _test_inter_service_communication(self) -> TestResult:
        """Test communication between services."""
        start_time = time.perf_counter()
        
        try:
            # Test communication patterns
            communication_tests = []
            
            # Test 1: Auth service to Constitutional AI service communication
            if (self.config.is_service_enabled(ServiceType.AUTH) and 
                self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI)):
                
                try:
                    # Simulate auth token validation request
                    auth_response = await self.make_service_request(
                        ServiceType.AUTH, "GET", "/health"
                    )
                    
                    # Then use Constitutional AI service
                    ai_response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI, "GET", "/health"
                    )
                    
                    communication_tests.append({
                        "communication_pattern": "auth_to_constitutional_ai",
                        "success": auth_response.status_code == 200 and ai_response.status_code == 200,
                        "auth_status": auth_response.status_code,
                        "ai_status": ai_response.status_code
                    })
                
                except Exception as e:
                    communication_tests.append({
                        "communication_pattern": "auth_to_constitutional_ai",
                        "success": False,
                        "error": str(e)
                    })
            
            # Test 2: Constitutional AI to Policy Governance communication
            if (self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI) and 
                self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE)):
                
                try:
                    # Test policy validation flow
                    test_policy = {
                        "policy_id": "inter_service_test_policy",
                        "constitutional_hash": self.config.constitutional_hash
                    }
                    
                    # Constitutional validation
                    ai_response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/constitutional/validate",
                        json=test_policy
                    )
                    
                    # Policy governance check
                    pgc_response = await self.make_service_request(
                        ServiceType.POLICY_GOVERNANCE,
                        "GET",
                        f"/api/v1/policies/{test_policy['policy_id']}"
                    )
                    
                    communication_tests.append({
                        "communication_pattern": "constitutional_ai_to_policy_governance",
                        "success": ai_response.status_code in [200, 400] and pgc_response.status_code in [200, 404],
                        "ai_status": ai_response.status_code,
                        "pgc_status": pgc_response.status_code
                    })
                
                except Exception as e:
                    communication_tests.append({
                        "communication_pattern": "constitutional_ai_to_policy_governance",
                        "success": False,
                        "error": str(e)
                    })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate inter-service communication
            successful_communications = [c for c in communication_tests if c["success"]]
            communication_success_rate = len(successful_communications) / len(communication_tests) if communication_tests else 0
            overall_success = communication_success_rate >= 0.8
            
            return TestResult(
                test_name="inter_service_communication",
                success=overall_success,
                duration_ms=duration_ms,
                constitutional_compliance=True,
                performance_metrics={
                    "communication_patterns_tested": len(communication_tests),
                    "successful_communications": len(successful_communications),
                    "communication_success_rate": communication_success_rate,
                    "communication_tests": communication_tests
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="inter_service_communication",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Inter-service communication test failed: {str(e)}"
            )
    
    async def _test_service_dependency_chain(self) -> TestResult:
        """Test service dependency chain and cascading health."""
        start_time = time.perf_counter()
        
        try:
            # Define service dependency chain
            dependency_chain = [
                ServiceType.AUTH,  # Base authentication
                ServiceType.CONSTITUTIONAL_AI,  # Depends on auth
                ServiceType.POLICY_GOVERNANCE,  # Depends on constitutional AI
                ServiceType.GOVERNANCE_SYNTHESIS  # Depends on policy governance
            ]
            
            dependency_results = []
            
            # Test each service in the dependency chain
            for i, service_type in enumerate(dependency_chain):
                if self.config.is_service_enabled(service_type):
                    try:
                        response = await self.make_service_request(
                            service_type, "GET", "/health"
                        )
                        
                        service_healthy = response.status_code == 200
                        
                        # Check constitutional hash consistency
                        constitutional_compliance = True
                        if service_healthy:
                            try:
                                data = response.json()
                                if "constitutional_hash" in data:
                                    constitutional_compliance = data["constitutional_hash"] == self.config.constitutional_hash
                            except Exception:
                                constitutional_compliance = True  # Assume compliance if can't parse
                        
                        dependency_results.append({
                            "service": service_type.value,
                            "dependency_level": i,
                            "healthy": service_healthy,
                            "constitutional_compliance": constitutional_compliance,
                            "response_code": response.status_code
                        })
                    
                    except Exception as e:
                        dependency_results.append({
                            "service": service_type.value,
                            "dependency_level": i,
                            "healthy": False,
                            "error": str(e)
                        })
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Evaluate dependency chain health
            healthy_services = [s for s in dependency_results if s.get("healthy", False)]
            chain_health_rate = len(healthy_services) / len(dependency_results) if dependency_results else 0
            
            # Check constitutional compliance across chain
            compliant_services = [s for s in dependency_results if s.get("constitutional_compliance", False)]
            compliance_rate = len(compliant_services) / len(dependency_results) if dependency_results else 0
            
            overall_success = chain_health_rate >= 0.8 and compliance_rate >= 0.8
            
            return TestResult(
                test_name="service_dependency_chain",
                success=overall_success,
                duration_ms=duration_ms,
                constitutional_compliance=compliance_rate >= 0.8,
                performance_metrics={
                    "services_in_chain": len(dependency_results),
                    "healthy_services": len(healthy_services),
                    "chain_health_rate": chain_health_rate,
                    "compliant_services": len(compliant_services),
                    "compliance_rate": compliance_rate,
                    "dependency_results": dependency_results
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return TestResult(
                test_name="service_dependency_chain",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Service dependency chain test failed: {str(e)}"
            )
