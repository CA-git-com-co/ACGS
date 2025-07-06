"""
Mock Service Manager for ACGS E2E Testing

Provides mock implementations of ACGS services for offline testing,
enabling comprehensive testing without requiring live infrastructure.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from .config import E2ETestConfig, ServiceType


@dataclass
class MockResponse:
    """Mock service response."""
    status_code: int
    data: Dict[str, Any]
    latency_ms: float = 1.0


class MockServiceBase:
    """Base class for mock services."""
    
    def __init__(self, service_type: ServiceType, config: E2ETestConfig):
        self.service_type = service_type
        self.config = config
        self.app = FastAPI(title=f"Mock {service_type.value} Service")
        self.request_count = 0
        self.error_rate = 0.0  # Configurable error rate for testing
        
        # Setup basic endpoints
        self._setup_endpoints()
    
    def _setup_endpoints(self):
        """Setup basic service endpoints."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": self.service_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "constitutional_hash": self.config.constitutional_hash,
                "request_count": self.request_count
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Metrics endpoint."""
            return {
                "request_count": self.request_count,
                "error_rate": self.error_rate,
                "uptime_seconds": time.time(),
                "constitutional_hash": self.config.constitutional_hash
            }
    
    async def simulate_latency(self):
        """Simulate realistic service latency."""
        # Simulate sub-5ms latency as per requirements
        latency = min(0.001 + (time.time() % 0.004), 0.005)  # 1-5ms
        await asyncio.sleep(latency)
    
    def should_simulate_error(self) -> bool:
        """Determine if should simulate an error."""
        import random
        return random.random() < self.error_rate
    
    def increment_request_count(self):
        """Increment request counter."""
        self.request_count += 1


class MockAuthService(MockServiceBase):
    """Mock authentication service."""
    
    def __init__(self, config: E2ETestConfig):
        super().__init__(ServiceType.AUTH, config)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._setup_auth_endpoints()
    
    def _setup_auth_endpoints(self):
        """Setup authentication-specific endpoints."""
        
        @self.app.post("/api/v1/auth/login")
        async def login(credentials: Dict[str, str]):
            """Mock login endpoint."""
            await self.simulate_latency()
            self.increment_request_count()
            
            if self.should_simulate_error():
                raise HTTPException(status_code=500, detail="Internal server error")
            
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username or not password:
                raise HTTPException(status_code=400, detail="Missing credentials")
            
            # Mock token generation
            token = f"mock_token_{username}_{int(time.time())}"
            self.tokens[token] = {
                "username": username,
                "expires_at": time.time() + 3600,
                "constitutional_hash": self.config.constitutional_hash
            }
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600,
                "constitutional_hash": self.config.constitutional_hash
            }
        
        @self.app.get("/api/v1/auth/verify")
        async def verify_token(authorization: str = None):
            """Mock token verification."""
            await self.simulate_latency()
            self.increment_request_count()
            
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.replace("Bearer ", "")
            
            if token not in self.tokens:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            token_data = self.tokens[token]
            
            if time.time() > token_data["expires_at"]:
                raise HTTPException(status_code=401, detail="Token expired")
            
            return {
                "valid": True,
                "username": token_data["username"],
                "constitutional_hash": self.config.constitutional_hash
            }


class MockConstitutionalAIService(MockServiceBase):
    """Mock Constitutional AI service."""
    
    def __init__(self, config: E2ETestConfig):
        super().__init__(ServiceType.CONSTITUTIONAL_AI, config)
        self._setup_ai_endpoints()
    
    def _setup_ai_endpoints(self):
        """Setup AI-specific endpoints."""
        
        @self.app.post("/api/v1/constitutional/validate")
        async def validate_policy(policy_data: Dict[str, Any]):
            """Mock policy validation."""
            await self.simulate_latency()
            self.increment_request_count()
            
            if self.should_simulate_error():
                raise HTTPException(status_code=500, detail="AI service error")
            
            # Mock constitutional validation
            compliance_score = 0.95  # High compliance for testing
            
            return {
                "constitutional_compliance": True,
                "compliance_score": compliance_score,
                "constitutional_hash": self.config.constitutional_hash,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "policy_id": policy_data.get("policy_id", "mock_policy"),
                "recommendations": [
                    "Policy aligns with constitutional principles",
                    "No violations detected"
                ]
            }
        
        @self.app.post("/api/v1/hitl/assess")
        async def assess_uncertainty(request_data: Dict[str, Any]):
            """Mock HITL uncertainty assessment."""
            await self.simulate_latency()
            self.increment_request_count()
            
            # Mock uncertainty assessment with sub-5ms response
            uncertainty_score = 0.15  # Low uncertainty
            
            return {
                "uncertainty_score": uncertainty_score,
                "requires_human_review": uncertainty_score > 0.5,
                "confidence_level": 1.0 - uncertainty_score,
                "constitutional_hash": self.config.constitutional_hash,
                "assessment_timestamp": datetime.utcnow().isoformat(),
                "latency_ms": 2.5  # Mock sub-5ms latency
            }


class MockPolicyGovernanceService(MockServiceBase):
    """Mock Policy Governance service with WINA optimization."""
    
    def __init__(self, config: E2ETestConfig):
        super().__init__(ServiceType.POLICY_GOVERNANCE, config)
        self.policy_cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._setup_governance_endpoints()
    
    def _setup_governance_endpoints(self):
        """Setup governance-specific endpoints."""
        
        @self.app.get("/api/v1/policies/{policy_id}")
        async def get_policy(policy_id: str):
            """Mock policy retrieval with O(1) lookup."""
            await self.simulate_latency()
            self.increment_request_count()
            
            # Simulate cache lookup (O(1) as required)
            if policy_id in self.policy_cache:
                self.cache_hits += 1
                cache_hit = True
                policy_data = self.policy_cache[policy_id]
            else:
                self.cache_misses += 1
                cache_hit = False
                # Mock policy data
                policy_data = {
                    "policy_id": policy_id,
                    "name": f"Mock Policy {policy_id}",
                    "version": "1.0.0",
                    "constitutional_compliance": True,
                    "wina_optimized": True
                }
                self.policy_cache[policy_id] = policy_data
            
            cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses)
            
            return {
                **policy_data,
                "constitutional_hash": self.config.constitutional_hash,
                "cache_hit": cache_hit,
                "cache_hit_rate": cache_hit_rate,
                "lookup_time_ms": 0.5,  # O(1) lookup time
                "wina_optimization_active": True
            }
        
        @self.app.post("/api/v1/governance/policy")
        async def validate_policy_governance():
            """Mock policy governance validation endpoint."""
            await self.simulate_latency()
            self.increment_request_count()

            # For mock service, we'll use default values
            # In a real implementation, this would parse the request body
            policy_id = 'test_policy'
            context = 'test_context'

            # Simulate governance validation with constitutional compliance
            governance_result = {
                "policy_id": policy_id,
                "context": context,
                "constitutional_compliance": True,
                "constitutional_hash": self.config.constitutional_hash,
                "governance_score": 0.92,
                "wina_optimization_applied": True,
                "validation_status": "approved",
                "validation_time_ms": 1.2,  # Sub-5ms as required
                "cache_utilized": True,
                "compliance_checks": {
                    "constitutional_alignment": True,
                    "policy_consistency": True,
                    "governance_rules": True,
                    "security_validation": True
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            return governance_result

        @self.app.get("/api/v1/governance/metrics")
        async def get_governance_metrics():
            """Get governance performance metrics."""
            cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0

            return {
                "cache_hit_rate": cache_hit_rate,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "total_requests": self.request_count,
                "constitutional_hash": self.config.constitutional_hash,
                "wina_optimization_enabled": True,
                "average_lookup_time_ms": 0.8  # Sub-5ms as required
            }


class MockServiceManager:
    """Manages all mock services for testing."""
    
    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.services: Dict[ServiceType, MockServiceBase] = {}
        self.servers: Dict[ServiceType, Any] = {}
        
        # Initialize mock services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all required mock services."""
        self.services[ServiceType.AUTH] = MockAuthService(self.config)
        self.services[ServiceType.CONSTITUTIONAL_AI] = MockConstitutionalAIService(self.config)
        self.services[ServiceType.POLICY_GOVERNANCE] = MockPolicyGovernanceService(self.config)
        
        # Add other services as needed
        for service_type in [ServiceType.INTEGRITY, ServiceType.FORMAL_VERIFICATION, 
                           ServiceType.GOVERNANCE_SYNTHESIS, ServiceType.EVOLUTIONARY_COMPUTATION]:
            self.services[service_type] = MockServiceBase(service_type, self.config)
    
    async def start(self):
        """Start all mock services."""
        for service_type, service in self.services.items():
            if self.config.is_service_enabled(service_type):
                endpoint = self.config.services[service_type]
                
                # Start service in background
                config = uvicorn.Config(
                    service.app,
                    host="127.0.0.1",
                    port=endpoint.port,
                    log_level="warning"  # Reduce noise
                )
                server = uvicorn.Server(config)
                
                # Start server in background task
                task = asyncio.create_task(server.serve())
                self.servers[service_type] = (server, task)
                
                # Give server time to start
                await asyncio.sleep(0.1)
    
    async def stop(self):
        """Stop all mock services."""
        for service_type, (server, task) in self.servers.items():
            server.should_exit = True
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.servers.clear()
    
    def get_service(self, service_type: ServiceType) -> Optional[MockServiceBase]:
        """Get a specific mock service."""
        return self.services.get(service_type)
    
    def set_error_rate(self, service_type: ServiceType, error_rate: float):
        """Set error rate for a specific service."""
        if service_type in self.services:
            self.services[service_type].error_rate = error_rate
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from all services."""
        metrics = {}
        
        for service_type, service in self.services.items():
            metrics[service_type.value] = {
                "request_count": service.request_count,
                "error_rate": service.error_rate
            }
            
            # Add service-specific metrics
            if isinstance(service, MockPolicyGovernanceService):
                cache_hit_rate = service.cache_hits / (service.cache_hits + service.cache_misses) if (service.cache_hits + service.cache_misses) > 0 else 0
                metrics[service_type.value]["cache_hit_rate"] = cache_hit_rate
        
        return metrics
