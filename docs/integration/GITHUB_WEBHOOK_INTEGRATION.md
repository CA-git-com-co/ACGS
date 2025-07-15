# GitHub Webhook Integration for ACGS Integrity Service

**Constitutional Hash:** `cdd01ef066bc6cf2`

## Overview

The ACGS Integrity Service provides comprehensive GitHub webhook integration to maintain constitutional compliance across all repository activities. This integration automatically processes GitHub events and validates them against constitutional requirements.

## Features

### 🔐 **Constitutional Compliance Validation**
- Automatic validation of governance-related changes
- Constitutional hash verification in commits and pull requests
- Compliance violation detection and reporting

### 🔍 **Security Event Processing**
- Security advisory monitoring with severity-based escalation
- Code scanning alert processing
- Threat assessment integration with audit trail

### 📊 **Comprehensive Event Support**
- Push events with constitutional compliance checking
- Pull request governance validation
- Repository management tracking
- Release and issue management

### 🛡️ **Security & Authentication**
- HMAC signature verification for webhook authenticity
- Structured audit trail integration
- Constitutional hash validation across all operations

## Configuration

### Webhook Setup

Configure your GitHub webhook with the following settings:

```json
{
  "payload_url": "https://your-domain.com/api/v1/webhooks/github",
  "content_type": "application/json",
  "secret": "your-secure-webhook-secret",
  "events": [
    "push",
    "pull_request", 
    "security_advisory",
    "code_scanning_alert",
    "repository",
    "release",
    "issues"
  ]
}
```

### Environment Configuration

Add to your `config/environments/developmentconfig/environments/acgs.env` file:

```bash
# GitHub Webhook Configuration
GITHUB_WEBHOOK_SECRET=your-secure-webhook-secret
GITHUB_WEBHOOK_SIGNATURE_VERIFICATION=true
GITHUB_CONSTITUTIONAL_VALIDATION=true
GITHUB_AUDIT_TRAIL_ENABLED=true

# Constitutional compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
```

## API Endpoints

### Core Webhook Endpoint

**POST** `/api/v1/webhooks/github`

Primary webhook endpoint for receiving GitHub events.

**Headers Required:**
- `X-GitHub-Event`: Event type (push, pull_request, etc.)
- `X-GitHub-Delivery`: Unique delivery ID
- `X-Hub-Signature-256`: HMAC signature for verification
- `Content-Type`: application/json

**Response:**
```json
{
  "status": "processed",
  "event_type": "push",
  "delivery_id": "12345678-1234-1234-1234-123456789abc",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "audit_recorded": true,
  "processed_data": {
    "event_type": "push",
    "repository": "owner/repo",
    "commit_count": 3,
    "compliance_violations": [],
    "constitutional_hash": "cdd01ef066bc6cf2",
    "processed_at": "2025-01-10T12:00:00Z"
  }
}
```

### Configuration Endpoint

**GET** `/api/v1/webhooks/github/config`

Returns webhook configuration and setup instructions.

### Health Check Endpoint

**GET** `/api/v1/webhooks/github/health`

Health status for GitHub webhook service.

### Test Endpoint

**POST** `/api/v1/webhooks/github/test`

Test webhook processing without GitHub integration.

## Event Processing

### Push Events

Processes code push events with constitutional compliance validation:

```json
{
  "event_type": "push",
  "repository": "owner/repo",
  "ref": "refs/heads/main",
  "commit_count": 2,
  "compliance_violations": [
    {
      "commit_id": "abc123",
      "message": "Constitutional changes without hash",
      "violation": "Missing constitutional hash in constitutional change"
    }
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Pull Request Events

Validates pull requests for governance compliance:

```json
{
  "event_type": "pull_request",
  "action": "opened",
  "repository": "owner/repo", 
  "pr_number": 42,
  "pr_title": "Constitutional policy updates",
  "governance_flags": ["constitutional", "policy"],
  "requires_constitutional_validation": true,
  "has_constitutional_hash": true,
  "constitutional_compliance": true,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Security Events

Processes security advisories and code scanning alerts:

```json
{
  "event_type": "security_advisory",
  "repository": "owner/repo",
  "advisory_id": "GHSA-xxxx-xxxx-xxxx",
  "severity": "high",
  "summary": "Critical security vulnerability",
  "requires_immediate_attention": true,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Constitutional Compliance Rules

### Governance-Related Changes

The system automatically flags pull requests and commits containing:
- "constitutional" keywords
- "governance" related terms
- "policy" modifications 
- "compliance" updates
- "security" changes

### Validation Requirements

For governance-related changes:
1. **Constitutional Hash Required**: Must include `cdd01ef066bc6cf2` in PR description or commit message
2. **Audit Trail**: All changes logged with constitutional context
3. **Compliance Validation**: Automatic constitutional compliance checking
4. **Escalation**: Non-compliant changes trigger alerts

### Security Event Handling

Security events trigger immediate processing:
- **High/Critical Severity**: Immediate attention flags
- **Audit Integration**: Security events logged in integrity service
- **Constitutional Context**: All security events include constitutional hash

## Integration Examples

### Basic Webhook Handler

```python
import hmac
import hashlib
import json
from fastapi import Request, HTTPException

async def handle_github_webhook(request: Request):
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    payload = await request.body()
    
    if not verify_signature(payload, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process event
    event_type = request.headers.get('X-GitHub-Event')
    payload_data = json.loads(payload)
    
    # Constitutional compliance validation
    result = await process_webhook_event(event_type, payload_data)
    
    return {"status": "processed", "constitutional_hash": "cdd01ef066bc6cf2"}
```

### Constitutional Compliance Check

```python
def check_constitutional_compliance(pr_data):
    title = pr_data.get('title', '').lower()
    body = pr_data.get('body', '')
    
    # Check for governance keywords
    governance_keywords = ['constitutional', 'governance', 'policy']
    has_governance_content = any(keyword in title for keyword in governance_keywords)
    
    # Check for constitutional hash
    has_constitutional_hash = 'cdd01ef066bc6cf2' in body
    
    return {
        'requires_validation': has_governance_content,
        'has_constitutional_hash': has_constitutional_hash,
        'compliant': has_constitutional_hash or not has_governance_content
    }
```

## Monitoring and Metrics

### Performance Metrics

- **Processing Latency**: Webhook processing time (target: <100ms)
- **Constitutional Compliance Rate**: Percentage of compliant events
- **Event Processing Volume**: Number of events processed per hour
- **Audit Trail Success Rate**: Percentage of successful audit entries

### Health Indicators

- Service availability and response time
- Webhook signature verification success rate
- Constitutional validation accuracy
- Integration with audit trail services

## Security Considerations

### Webhook Security

1. **Signature Verification**: Always verify HMAC signatures
2. **HTTPS Only**: Only accept webhooks over HTTPS
3. **Secret Management**: Store webhook secrets securely
4. **Rate Limiting**: Implement rate limiting for webhook endpoints

### Constitutional Security

1. **Hash Validation**: Validate constitutional hash in all operations
2. **Audit Trail**: Maintain complete audit trail for governance events
3. **Access Control**: Restrict webhook configuration to authorized users
4. **Compliance Monitoring**: Continuous monitoring of constitutional compliance

## Troubleshooting

### Common Issues

**Webhook Signature Verification Failures**
- Verify webhook secret configuration
- Check HMAC calculation implementation
- Ensure payload is raw bytes for signature verification

**Constitutional Compliance Violations**
- Check for constitutional hash in PR descriptions
- Verify governance keyword detection
- Review constitutional compliance rules

**Performance Issues**
- Monitor webhook processing latency
- Check audit trail service availability
- Optimize constitutional validation logic

### Debugging

Enable detailed logging:

```python
import logging
logging.getLogger('github_webhooks').setLevel(logging.DEBUG)
```

Check service health:
```bash
curl http://localhost:8002/api/v1/webhooks/github/health
```

Test webhook processing:
```bash
curl -X POST http://localhost:8002/api/v1/webhooks/github/test \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## Development

### Running Tests

```bash
# Run GitHub webhook integration tests
python -m pytest tests/integration/test_github_webhook_integration.py -v

# Run with constitutional compliance validation
python -m pytest tests/integration/test_github_webhook_integration.py::TestGitHubWebhookIntegration::test_constitutional_compliance_validation -v
```

### Local Development

```bash
# Start integrity service with GitHub webhook support
docker compose -f infrastructure/docker/docker-compose.acgs.yml up integrity

# Test webhook endpoint
curl http://localhost:8002/api/v1/webhooks/github/config
```

## Conclusion

The GitHub webhook integration provides robust constitutional compliance validation and security monitoring for ACGS repositories. It ensures all governance-related changes maintain constitutional compliance while providing comprehensive audit trails and security event processing.

For additional support or configuration questions, refer to the ACGS documentation or contact the constitutional compliance team.

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Last Updated:** 2025-01-10  
**Version:** 1.0.0