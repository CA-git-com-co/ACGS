#!/usr/bin/env python3
"""
API Documentation Generator for ACGS-1 Services
Generates comprehensive API documentation for all services.
"""

import os
from pathlib import Path
from datetime import datetime

def create_service_api_doc(service_name, port, description, endpoints):
    """Create API documentation for a service."""
    
    service_slug = service_name.lower().replace(' ', '_').replace('-', '_')
    
    content = f"""# {service_name} API Documentation

## Overview

{description}

**Base URL**: `http://localhost:{port}`
**Interactive Docs**: `http://localhost:{port}/docs`
**Service Version**: 2.1.0
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Authentication

All endpoints (except `/health` and `/metrics`) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Health Check

#### GET /health

Returns the current health status of the {service_name}.

**Authentication**: Not required

**Response (200 OK)**:
```json
{{
  "status": "healthy",
  "service": "{service_slug}",
  "version": "2.1.0",
  "uptime": 3600,
  "dependencies": {{
    "database": "connected",
    "redis": "connected"
  }}
}}
```

"""
    
    # Add endpoint documentation
    for endpoint in endpoints:
        content += f"""### {endpoint['name']}

#### {endpoint['method']} {endpoint['path']}

{endpoint['description']}

**Authentication**: {'Required' if endpoint.get('auth', True) else 'Not required'}

"""
        
        if 'request' in endpoint:
            content += f"""**Request Body**:
```json
{endpoint['request']}
```

"""
        
        if 'response' in endpoint:
            content += f"""**Response (200 OK)**:
```json
{endpoint['response']}
```

"""
    
    # Add common sections
    content += f"""## Error Responses

### 400 Bad Request
```json
{{
  "status": "error",
  "error": {{
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters"
  }},
  "timestamp": "{datetime.now().isoformat()}Z",
  "request_id": "req_error_123"
}}
```

### 401 Unauthorized
```json
{{
  "status": "error",
  "error": {{
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  }},
  "timestamp": "{datetime.now().isoformat()}Z",
  "request_id": "req_error_456"
}}
```

## Rate Limits

- **Standard requests**: 100 requests per minute per user
- **Heavy operations**: 20 requests per minute per user

## Examples

### cURL Examples
```bash
# Health check
curl http://localhost:{port}/health

# Example API call (replace with actual endpoint)
curl -X POST http://localhost:{port}/api/v1/example \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"example": "data"}}'
```

### Python Client Example
```python
import httpx
import asyncio

class {service_name.replace(' ', '').replace('-', '')}Client:
    def __init__(self, base_url="http://localhost:{port}", token=None):
        self.base_url = base_url
        self.headers = {{"Authorization": f"Bearer {{token}}"}} if token else {{}}
    
    async def health_check(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{{self.base_url}}/health")
            return response.json()

# Usage
async def main():
    client = {service_name.replace(' ', '').replace('-', '')}Client(token="your_jwt_token")
    result = await client.health_check()
    print(result)

asyncio.run(main())
```

## Monitoring

### Metrics Endpoint

#### GET /metrics

Returns Prometheus-formatted metrics for monitoring.

**Authentication**: Not required

---

**For additional support or questions, please refer to the [ACGS-1 Documentation](../README.md) or contact the development team.**
"""
    
    return content

def main():
    """Generate API documentation for all services."""
    
    # Define services and their endpoints
    services = [
        {
            "name": "Authentication Service",
            "port": 8000,
            "description": "Provides user authentication, authorization, and session management for the ACGS-1 system.",
            "endpoints": [
                {
                    "name": "User Login",
                    "method": "POST",
                    "path": "/auth/login",
                    "description": "Authenticate user and return JWT token.",
                    "auth": False,
                    "request": '{"username": "user", "password": "password"}',
                    "response": '{"access_token": "jwt_token", "token_type": "bearer", "expires_in": 3600}'
                },
                {
                    "name": "Token Refresh",
                    "method": "POST", 
                    "path": "/auth/refresh",
                    "description": "Refresh an existing JWT token.",
                    "request": '{"refresh_token": "refresh_token"}',
                    "response": '{"access_token": "new_jwt_token", "expires_in": 3600}'
                },
                {
                    "name": "User Profile",
                    "method": "GET",
                    "path": "/auth/profile",
                    "description": "Get current user profile information.",
                    "response": '{"user_id": "123", "username": "user", "roles": ["citizen"], "permissions": ["read", "write"]}'
                }
            ]
        },
        {
            "name": "Integrity Service",
            "port": 8002,
            "description": "Provides digital signature, verification, and audit trail capabilities for ensuring data integrity.",
            "endpoints": [
                {
                    "name": "Digital Signature",
                    "method": "POST",
                    "path": "/api/v1/sign",
                    "description": "Create digital signature for document or data.",
                    "request": '{"document": "content", "signer_id": "user123"}',
                    "response": '{"signature": "digital_signature", "signature_id": "sig_123", "timestamp": "2024-06-20T10:30:00Z"}'
                },
                {
                    "name": "Signature Verification",
                    "method": "POST",
                    "path": "/api/v1/verify",
                    "description": "Verify digital signature authenticity.",
                    "request": '{"document": "content", "signature": "digital_signature"}',
                    "response": '{"valid": true, "signer_id": "user123", "timestamp": "2024-06-20T10:30:00Z"}'
                }
            ]
        },
        {
            "name": "Formal Verification Service",
            "port": 8003,
            "description": "Provides formal verification and consistency checking for policies and governance rules.",
            "endpoints": [
                {
                    "name": "Policy Verification",
                    "method": "POST",
                    "path": "/api/v1/verify-policy",
                    "description": "Formally verify policy consistency and completeness.",
                    "request": '{"policy": "policy_text", "rules": ["consistency", "completeness"]}',
                    "response": '{"verified": true, "issues": [], "confidence": 0.95}'
                }
            ]
        },
        {
            "name": "Governance Synthesis Service",
            "port": 8004,
            "description": "Synthesizes policies and governance solutions from multiple inputs and stakeholder requirements.",
            "endpoints": [
                {
                    "name": "Policy Synthesis",
                    "method": "POST",
                    "path": "/api/v1/synthesize",
                    "description": "Synthesize policy from multiple inputs and requirements.",
                    "request": '{"inputs": ["req1", "req2"], "stakeholders": ["citizens"], "principles": ["fairness"]}',
                    "response": '{"synthesized_policy": "policy_text", "confidence": 0.88, "alternatives": []}'
                }
            ]
        },
        {
            "name": "Policy Governance Service",
            "port": 8005,
            "description": "Manages policy lifecycle, voting, and governance processes within the ACGS-1 system.",
            "endpoints": [
                {
                    "name": "Create Policy",
                    "method": "POST",
                    "path": "/api/v1/policies",
                    "description": "Create a new policy for governance.",
                    "request": '{"title": "Policy Title", "description": "Description", "category": "governance"}',
                    "response": '{"policy_id": "pol_123", "status": "draft", "created_at": "2024-06-20T10:30:00Z"}'
                },
                {
                    "name": "Vote on Policy",
                    "method": "POST",
                    "path": "/api/v1/policies/{id}/vote",
                    "description": "Cast vote on a policy proposal.",
                    "request": '{"vote": "approve", "comment": "Supports transparency"}',
                    "response": '{"vote_id": "vote_123", "status": "recorded", "timestamp": "2024-06-20T10:30:00Z"}'
                }
            ]
        },
        {
            "name": "Evolutionary Computation Service",
            "port": 8006,
            "description": "Applies evolutionary algorithms to optimize policies and governance solutions.",
            "endpoints": [
                {
                    "name": "Start Evolution",
                    "method": "POST",
                    "path": "/api/v1/evolve",
                    "description": "Start evolutionary optimization process.",
                    "request": '{"initial_policies": ["pol1"], "fitness_criteria": ["effectiveness"], "generations": 10}',
                    "response": '{"evolution_id": "evo_123", "status": "running", "estimated_completion": "2024-06-20T11:00:00Z"}'
                }
            ]
        },
        {
            "name": "Darwin Gödel Machine Service",
            "port": 8007,
            "description": "Provides self-improving AI capabilities for continuous system optimization.",
            "endpoints": [
                {
                    "name": "Trigger Improvement",
                    "method": "POST",
                    "path": "/api/v1/improve",
                    "description": "Trigger self-improvement process.",
                    "request": '{"target_component": "policy_analysis", "improvement_type": "performance"}',
                    "response": '{"improvement_id": "imp_123", "status": "initiated", "expected_benefit": 0.15}'
                }
            ]
        },
        {
            "name": "OCR Service",
            "port": 8020,
            "description": "Provides optical character recognition for document processing and analysis.",
            "endpoints": [
                {
                    "name": "Extract Text",
                    "method": "POST",
                    "path": "/api/v1/ocr/extract",
                    "description": "Extract text from image or document.",
                    "request": '{"image_data": "base64_encoded_image", "format": "pdf"}',
                    "response": '{"extracted_text": "Document text content", "confidence": 0.95, "processing_time_ms": 1200}'
                }
            ]
        }
    ]
    
    # Create docs directory if it doesn't exist
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate documentation for each service
    for service in services:
        filename = f"{service['name'].lower().replace(' ', '_').replace('-', '_')}_api.md"
        filepath = docs_dir / filename
        
        content = create_service_api_doc(
            service['name'],
            service['port'],
            service['description'],
            service['endpoints']
        )
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated API documentation: {filepath}")
    
    print(f"\n🎉 API documentation generation complete!")
    print(f"📁 Documentation files created in: {docs_dir}")

if __name__ == "__main__":
    main()
