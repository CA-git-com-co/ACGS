# Governance Engine Service Migration Guide
**Constitutional Hash: cdd01ef066bc6cf2**


**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

This document outlines the migration from separate governance-synthesis and policy-governance services to the unified governance-engine service.

## Changes Made

### Service Consolidation

| Old Services | New Service |
|-------------|----------

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---|
| `gs_service` (Port 8004) | `governance_engine` (Port 8004) |
| `pgc_service` (Port 8005) | ~~Removed~~ |

### Docker Compose Changes

**Before:**
```yaml
gs_service:
  ports: ["8004:8004"]
pgc_service:
  ports: ["8005:8005"]
```

**After:**
```yaml
governance_engine:
  ports: ["8004:8004"]
```

### Environment Variable Updates

**Old:**
- `GS_SERVICE_URL=http://gs_service:8004`
- `PGC_SERVICE_URL=http://pgc_service:8005`

**New:**
- `GOVERNANCE_ENGINE_URL=http://governance_engine:8004`

## API Endpoint Migration

### Governance Synthesis APIs (formerly gs_service)
- **Old:** `http://gs_service:8004/api/v1/synthesize`
- **New:** `http://governance_engine:8004/api/v1/synthesis/synthesize`

### Policy Enforcement APIs (formerly pgc_service)
- **Old:** `http://pgc_service:8005/api/v1/enforce`
- **New:** `http://governance_engine:8004/api/v1/enforcement/enforce`

### New Unified APIs

#### Policy Synthesis
```bash
POST /api/v1/synthesis/synthesize
GET  /api/v1/synthesis/policies
```

#### Policy Enforcement
```bash
POST /api/v1/enforcement/enforce
GET  /api/v1/enforcement/policies/{policy_id}
```

#### Compliance Monitoring
```bash
POST /api/v1/compliance/check
GET  /api/v1/compliance/status
```

#### Governance Workflows
```bash
GET  /api/v1/workflows
POST /api/v1/workflows/{workflow_id}/execute
```

## Client Code Updates

### Service Registry Updates

**Before:**
```python
gs_client = await get_service_client("governance-synthesis")
pgc_client = await get_service_client("policy-governance")
```

**After:**
```python
governance_client = await get_service_client("governance-engine")
```

### Service Client Configuration

Add to `/home/dislove/ACGS-2/services/shared/service_clients/registry.py`:

```python
_service_urls = {
    # ... existing services
    "governance-engine": os.getenv("GOVERNANCE_ENGINE_URL", "http://localhost:8004"),
    # Remove: "governance-synthesis" and "policy-governance"
}
```

### Client Usage Examples

#### Policy Synthesis
```python
# Old way (gs_service)
response = await gs_client.request("POST", "/api/v1/synthesize", data=synthesis_request)

# New way (governance_engine)
response = await governance_client.request("POST", "/api/v1/synthesis/synthesize", data=synthesis_request)
```

#### Policy Enforcement
```python
# Old way (pgc_service)
response = await pgc_client.request("POST", "/api/v1/enforce", data=enforcement_request)

# New way (governance_engine)
response = await governance_client.request("POST", "/api/v1/enforcement/enforce", data=enforcement_request)
```

## Configuration Updates

### Docker Environment Variables

Update the following services in `docker-compose.acgs.yml`:

1. **opa service:**
   - Remove: `PGC_SERVICE_URL`, `GS_SERVICE_URL`
   - Add: `GOVERNANCE_ENGINE_URL=http://governance_engine:8004`

2. **ec_service:**
   - Remove: `GS_SERVICE_URL`, `PGC_SERVICE_URL`
   - Add: `GOVERNANCE_ENGINE_URL=http://governance_engine:8004`

3. **Dependencies:**
   - Replace `pgc_service` dependencies with `governance_engine`

### Service Registry Updates

Update service registry configurations to remove old service references:

```python
# In services/shared/service_clients/base_client.py
# Remove: GovernanceSynthesisClient, PolicyGovernanceClient
# Add: GovernanceEngineClient

class GovernanceEngineClient(BaseServiceClient):
    """Client for unified Governance Engine service"""
    
    async def synthesize_policy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", "/api/v1/synthesis/synthesize", data=request_data)
    
    async def enforce_policy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", "/api/v1/enforcement/enforce", data=request_data)
    
    async def check_compliance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.request("POST", "/api/v1/compliance/check", data=request_data)
```

## Testing

### Validate Migration
```bash
# Test unified service health
curl http://localhost:8004/health

# Test synthesis endpoint
curl -X POST http://localhost:8004/api/v1/synthesis/synthesize \
  -H "Content-Type: application/json" \
  -d '{"context": "test", "policy_type": "authorization", "requirements": ["authenticated"]}'

# Test enforcement endpoint
curl -X POST http://localhost:8004/api/v1/enforcement/enforce \
  -H "Content-Type: application/json" \
  -d '{"policy_id": "test", "context": {}, "action": "read"}'
```

### Run Service Tests
```bash
cd services/core/governance-engine
python3 -m pytest tests/ -v
```

## Backward Compatibility

The unified governance-engine service maintains backward compatibility through:

1. **API Compatibility**: Old API endpoints can be proxied to new ones
2. **Service Discovery**: Service registry handles client routing
3. **Configuration Overlap**: Environment variables support both old and new formats

## Rollback Plan

If rollback is needed:

1. Restore original `gs_service` and `pgc_service` containers
2. Revert Docker Compose changes
3. Update environment variables back to original format
4. Restart dependent services

## Performance Impact

The unified service provides:

- **Reduced Memory**: Single service vs. two services (768Mi vs. 1Gi + 1Gi)
- **Lower Latency**: Direct internal calls vs. network calls
- **Simplified Dependencies**: Fewer service-to-service connections
- **Better Resource Utilization**: Combined 750m CPU vs. 500m + 500m

## Monitoring

Update monitoring configurations:

1. **Prometheus**: Update service discovery for `governance_engine:8004`
2. **Grafana**: Update dashboards to track unified service metrics
3. **Logging**: Consolidate log collection for single service
4. **Health Checks**: Monitor single endpoint instead of two

## Constitutional Compliance

All changes maintain constitutional compliance with hash `cdd01ef066bc6cf2`:

- ✅ Service consolidation preserves all constitutional validation
- ✅ API endpoints maintain constitutional hash verification
- ✅ Audit trails continue to track all governance decisions
- ✅ Performance targets meet constitutional requirements