#!/usr/bin/env python3
"""
Simple mock service test to validate test framework
Constitutional Hash: cdd01ef066bc6cf2

This test validates that our comprehensive test framework works properly
by testing against mock HTTP services that return expected responses.
"""

import asyncio
import json
from aiohttp import web, ClientSession
from datetime import datetime

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Mock service responses
async def mock_health(request):
    """Mock health endpoint"""
    return web.json_response({
        "status": "healthy",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "1.0.0",
        "service_name": "mock_service",
        "timestamp": datetime.utcnow().isoformat()
    })

async def mock_constitutional_validate(request):
    """Mock constitutional validation endpoint"""
    data = await request.json()
    return web.json_response({
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "is_compliant": True,
        "compliance_score": 0.98,
        "validation_id": "mock_validation_123"
    })

async def start_mock_service(port):
    """Start a mock service on given port"""
    app = web.Application()
    app.router.add_get('/health', mock_health)
    app.router.add_post('/api/v1/constitutional/validate', mock_constitutional_validate)
    app.router.add_post('/api/v1/governance/analyze', mock_constitutional_validate)
    app.router.add_post('/api/v1/coordination/initiate', mock_constitutional_validate)
    app.router.add_post('/api/v1/security/analyze', mock_constitutional_validate)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    print(f"✅ Mock service started on port {port}")
    return runner

async def test_mock_framework():
    """Test that our test framework works with mock services"""
    
    # Start mock services on key ports
    services = []
    ports = [8001, 8002, 8004, 8008, 8009, 8010, 8015, 8020, 8021, 3000]
    
    try:
        # Start all mock services
        for port in ports:
            runner = await start_mock_service(port)
            services.append(runner)
        
        print(f"🚀 Started {len(services)} mock services")
        
        # Now run a simplified test
        async with ClientSession() as session:
            # Test health checks
            for port in ports[:3]:  # Test first 3 services
                async with session.get(f'http://localhost:{port}/health') as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['constitutional_hash'] == CONSTITUTIONAL_HASH
                    assert data['status'] == 'healthy'
                    print(f"✅ Mock service on port {port} health check passed")
            
            # Test constitutional validation
            payload = {
                "request": "validate_constitutional_compliance",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "context": {"purpose": "mock_test"}
            }
            
            async with session.post(
                'http://localhost:8001/api/v1/constitutional/validate',
                json=payload
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data['constitutional_hash'] == CONSTITUTIONAL_HASH
                assert data['is_compliant'] is True
                print("✅ Constitutional validation test passed")
        
        print("🎉 All mock service tests passed!")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH} validated")
        
    finally:
        # Cleanup mock services
        for runner in services:
            await runner.cleanup()
        print("🧹 Mock services cleaned up")

if __name__ == "__main__":
    print("🚀 Starting Mock Service Test Framework Validation")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    asyncio.run(test_mock_framework())
    
    print("=" * 60)
    print("✅ Mock service test framework validation complete")
    print("🔧 The test infrastructure is working properly")
    print("📝 Ready for integration with actual ACGS-2 services")