#!/usr/bin/env python3
"""
ACGS-1 Multi-Tenant Management API Service
Provides REST API endpoints for enterprise multi-tenant management
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the data classes we need
from dataclasses import dataclass, asdict

@dataclass
class TenantConfig:
    """Tenant configuration with constitutional governance settings"""
    tenant_id: str
    name: str
    constitution_hash: str
    max_users: int
    max_policies: int
    max_governance_actions_per_hour: int
    storage_quota_gb: int
    features: List[str]
    created_at: datetime
    status: str = "active"

@dataclass
class TenantMetrics:
    """Tenant usage metrics"""
    tenant_id: str
    active_users: int
    total_policies: int
    governance_actions_last_hour: int
    storage_used_gb: float
    response_time_avg_ms: float
    uptime_percentage: float
    constitutional_compliance_score: float
    last_updated: datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class TenantCreateRequest(BaseModel):
    """Request model for creating a new tenant"""
    name: str = Field(..., description="Tenant name")
    constitution_hash: str = Field(default="cdd01ef066bc6cf2", description="Constitution hash")
    max_users: int = Field(default=1000, description="Maximum users allowed")
    max_policies: int = Field(default=10000, description="Maximum policies allowed")
    max_governance_actions_per_hour: int = Field(default=1000, description="Max governance actions per hour")
    storage_quota_gb: int = Field(default=100, description="Storage quota in GB")
    features: List[str] = Field(default=["basic_governance", "policy_creation"], description="Enabled features")

class TenantUpdateRequest(BaseModel):
    """Request model for updating a tenant"""
    name: Optional[str] = None
    max_users: Optional[int] = None
    max_policies: Optional[int] = None
    max_governance_actions_per_hour: Optional[int] = None
    storage_quota_gb: Optional[int] = None
    features: Optional[List[str]] = None
    status: Optional[str] = None

class TenantResponse(BaseModel):
    """Response model for tenant data"""
    tenant_id: str
    name: str
    constitution_hash: str
    max_users: int
    max_policies: int
    max_governance_actions_per_hour: int
    storage_quota_gb: int
    features: List[str]
    created_at: str
    status: str

class TenantMetricsResponse(BaseModel):
    """Response model for tenant metrics"""
    tenant_id: str
    active_users: int
    total_policies: int
    governance_actions_last_hour: int
    storage_used_gb: float
    response_time_avg_ms: float
    uptime_percentage: float
    constitutional_compliance_score: float
    last_updated: str

# Global tenant manager
tenant_manager = None

async def get_tenant_manager():
    """Dependency to get tenant manager instance"""
    global tenant_manager
    if tenant_manager is None:
        # For now, create a mock tenant manager for API endpoints
        tenant_manager = MockTenantManager()
    return tenant_manager

class MockTenantManager:
    """Mock tenant manager for API demonstration"""

    def __init__(self):
        self.tenants = {
            "default": TenantConfig(
                tenant_id="default",
                name="Default Tenant",
                constitution_hash="cdd01ef066bc6cf2",
                max_users=1000,
                max_policies=10000,
                max_governance_actions_per_hour=1000,
                storage_quota_gb=100,
                features=["basic_governance", "policy_creation", "constitutional_compliance"],
                created_at=datetime.now(),
                status="active"
            )
        }

    async def create_tenant(self, tenant_data: Dict[str, Any]) -> TenantConfig:
        """Create new tenant"""
        import uuid
        tenant_id = str(uuid.uuid4())

        tenant = TenantConfig(
            tenant_id=tenant_id,
            name=tenant_data['name'],
            constitution_hash=tenant_data.get('constitution_hash', 'cdd01ef066bc6cf2'),
            max_users=tenant_data.get('max_users', 1000),
            max_policies=tenant_data.get('max_policies', 10000),
            max_governance_actions_per_hour=tenant_data.get('max_governance_actions_per_hour', 1000),
            storage_quota_gb=tenant_data.get('storage_quota_gb', 100),
            features=tenant_data.get('features', ['basic_governance', 'policy_creation']),
            created_at=datetime.now(),
            status="active"
        )

        self.tenants[tenant_id] = tenant
        return tenant

    async def list_tenants(self, limit: int = 100, offset: int = 0) -> List[TenantConfig]:
        """List all tenants"""
        return list(self.tenants.values())[offset:offset+limit]

    async def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)

    async def update_tenant(self, tenant_id: str, update_data: Dict[str, Any]) -> Optional[TenantConfig]:
        """Update tenant"""
        if tenant_id not in self.tenants:
            return None

        tenant = self.tenants[tenant_id]
        for key, value in update_data.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        return tenant

    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant"""
        if tenant_id in self.tenants:
            self.tenants[tenant_id].status = "deleted"
            return True
        return False

    async def get_tenant_metrics(self, tenant_id: str) -> Optional[TenantMetrics]:
        """Get tenant metrics"""
        if tenant_id not in self.tenants:
            return None

        return TenantMetrics(
            tenant_id=tenant_id,
            active_users=25,
            total_policies=150,
            governance_actions_last_hour=12,
            storage_used_gb=15.5,
            response_time_avg_ms=45.2,
            uptime_percentage=99.95,
            constitutional_compliance_score=98.5,
            last_updated=datetime.now()
        )

    async def validate_tenant_limits(self, tenant_id: str, action_type: str) -> bool:
        """Validate tenant limits"""
        return tenant_id in self.tenants

# Create FastAPI application
app = FastAPI(
    title="ACGS-1 Multi-Tenant Management API",
    description="Enterprise multi-tenant management endpoints for ACGS-1 Constitutional Governance System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup initialization removed for simplicity

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "multi-tenant-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "constitution_hash": "cdd01ef066bc6cf2"
    }

@app.post("/api/v1/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreateRequest,
    manager = Depends(get_tenant_manager)
):
    """Create a new tenant"""
    try:
        tenant = await manager.create_tenant(tenant_data.dict())
        return TenantResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            constitution_hash=tenant.constitution_hash,
            max_users=tenant.max_users,
            max_policies=tenant.max_policies,
            max_governance_actions_per_hour=tenant.max_governance_actions_per_hour,
            storage_quota_gb=tenant.storage_quota_gb,
            features=tenant.features,
            created_at=tenant.created_at.isoformat(),
            status=tenant.status
        )
    except Exception as e:
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

@app.get("/api/v1/tenants", response_model=List[TenantResponse])
async def list_tenants(
    limit: int = 100,
    offset: int = 0,
    manager = Depends(get_tenant_manager)
):
    """List all tenants"""
    try:
        tenants = await manager.list_tenants(limit=limit, offset=offset)
        return [
            TenantResponse(
                tenant_id=tenant.tenant_id,
                name=tenant.name,
                constitution_hash=tenant.constitution_hash,
                max_users=tenant.max_users,
                max_policies=tenant.max_policies,
                max_governance_actions_per_hour=tenant.max_governance_actions_per_hour,
                storage_quota_gb=tenant.storage_quota_gb,
                features=tenant.features,
                created_at=tenant.created_at.isoformat(),
                status=tenant.status
            )
            for tenant in tenants
        ]
    except Exception as e:
        logger.error(f"Failed to list tenants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tenants: {str(e)}")

@app.get("/api/v1/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    manager = Depends(get_tenant_manager)
):
    """Get tenant by ID"""
    try:
        tenant = await manager.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        return TenantResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            constitution_hash=tenant.constitution_hash,
            max_users=tenant.max_users,
            max_policies=tenant.max_policies,
            max_governance_actions_per_hour=tenant.max_governance_actions_per_hour,
            storage_quota_gb=tenant.storage_quota_gb,
            features=tenant.features,
            created_at=tenant.created_at.isoformat(),
            status=tenant.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tenant: {str(e)}")

@app.put("/api/v1/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    update_data: TenantUpdateRequest,
    manager = Depends(get_tenant_manager)
):
    """Update tenant configuration"""
    try:
        tenant = await manager.update_tenant(tenant_id, update_data.dict(exclude_unset=True))
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        return TenantResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            constitution_hash=tenant.constitution_hash,
            max_users=tenant.max_users,
            max_policies=tenant.max_policies,
            max_governance_actions_per_hour=tenant.max_governance_actions_per_hour,
            storage_quota_gb=tenant.storage_quota_gb,
            features=tenant.features,
            created_at=tenant.created_at.isoformat(),
            status=tenant.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update tenant: {str(e)}")

@app.delete("/api/v1/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    manager = Depends(get_tenant_manager)
):
    """Delete tenant (soft delete - sets status to 'deleted')"""
    try:
        success = await manager.delete_tenant(tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        return {"message": f"Tenant {tenant_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")

@app.get("/api/v1/tenants/{tenant_id}/metrics", response_model=TenantMetricsResponse)
async def get_tenant_metrics(
    tenant_id: str,
    manager = Depends(get_tenant_manager)
):
    """Get tenant usage metrics"""
    try:
        metrics = await manager.get_tenant_metrics(tenant_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Tenant metrics not found")
        
        return TenantMetricsResponse(
            tenant_id=metrics.tenant_id,
            active_users=metrics.active_users,
            total_policies=metrics.total_policies,
            governance_actions_last_hour=metrics.governance_actions_last_hour,
            storage_used_gb=metrics.storage_used_gb,
            response_time_avg_ms=metrics.response_time_avg_ms,
            uptime_percentage=metrics.uptime_percentage,
            constitutional_compliance_score=metrics.constitutional_compliance_score,
            last_updated=metrics.last_updated.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tenant metrics: {str(e)}")

@app.post("/api/v1/tenants/{tenant_id}/validate-limits")
async def validate_tenant_limits(
    tenant_id: str,
    action_type: str = "governance_action",
    manager = Depends(get_tenant_manager)
):
    """Validate tenant resource limits"""
    try:
        is_valid = await manager.validate_tenant_limits(tenant_id, action_type)
        return {
            "tenant_id": tenant_id,
            "action_type": action_type,
            "within_limits": is_valid,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to validate limits for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate tenant limits: {str(e)}")

@app.get("/api/v1/status")
async def get_service_status():
    """Get multi-tenant service status"""
    try:
        manager = await get_tenant_manager()
        tenant_count = len(await manager.list_tenants(limit=1000))
        
        return {
            "status": "functional",
            "service": "multi-tenant-management",
            "version": "1.0.0",
            "total_tenants": tenant_count,
            "constitution_hash": "cdd01ef066bc6cf2",
            "features": [
                "tenant_creation",
                "tenant_management", 
                "resource_isolation",
                "usage_metrics",
                "constitutional_governance"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "multi_tenant_api:app",
        host="0.0.0.0",
        port=8008,
        reload=False,
        log_level="info"
    )
