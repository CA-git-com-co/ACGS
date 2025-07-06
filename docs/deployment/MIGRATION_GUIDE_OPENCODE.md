# Migration Guide: Gemini CLI to OpenCode Adapter

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This guide helps you migrate from the Gemini CLI to the new OpenCode Adapter service while maintaining ACGS compliance and governance.

## Overview

The migration involves transitioning from a Google Gemini-based CLI to OpenCode, a provider-agnostic AI coding assistant. The OpenCode Adapter maintains all ACGS governance features while offering broader AI model support.

### Key Differences

| Feature | Gemini CLI | OpenCode Adapter |
|---------|------------|------------------|
| **AI Provider** | Google Gemini only | Multiple (Anthropic, OpenAI, Google, local) |
| **Architecture** | Direct CLI tool | Service-based adapter |
| **Interface** | Command line | REST API + CLI wrapper |
| **Deployment** | Local binary | Containerized service |
| **Port** | N/A | 8020 |

## Migration Steps

### Phase 1: Parallel Deployment

1. **Keep Gemini CLI Running**
   - Do not remove gemini-cli immediately
   - Maintain existing workflows during transition

2. **Deploy OpenCode Adapter**
   ```bash
   cd services/cli/opencode_adapter
   npm install --legacy-peer-deps
   npm run build
   npm start
   ```

3. **Verify Health**
   ```bash
   curl http://localhost:8020/health
   ```

### Phase 2: Update Client Applications

#### Before (Gemini CLI):
```bash
gemini-cli execute code --code "print('Hello')" --language python
gemini-cli agent create --name "assistant" --type "general"
gemini-cli verify constitutional "operation" --params params.json
```

#### After (OpenCode Adapter):
```bash
# Via HTTP API
curl -X POST http://localhost:8020/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "run",
    "args": ["script.py"],
    "context": {
      "agentId": "assistant",
      "language": "python"
    }
  }'
```

### Phase 3: Create CLI Wrapper (Optional)

For command-line compatibility, create a wrapper script:

```bash
#!/bin/bash
# opencode-cli wrapper

ADAPTER_URL=${OPENCODE_ADAPTER_URL:-http://localhost:8020}

case "$1" in
  execute)
    curl -X POST $ADAPTER_URL/execute \
      -H "Content-Type: application/json" \
      -d "{
        \"command\": \"$2\",
        \"args\": [${@:3}],
        \"context\": {
          \"agentId\": \"${ACGS_AGENT_ID:-default}\"
        }
      }"
    ;;
  check-permission)
    curl -X POST $ADAPTER_URL/check-permission \
      -H "Content-Type: application/json" \
      -d "{
        \"action\": \"$2\",
        \"context\": ${3:-\{\}}
      }"
    ;;
  *)
    echo "Usage: opencode-cli {execute|check-permission} ..."
    exit 1
    ;;
esac
```

## Configuration Migration

### Gemini CLI Config (Before):
```yaml
# ~/.gemini-cli/config.yaml
api_key: "gemini-api-key"
model: "gemini-pro"
acgs:
  auth_url: "http://localhost:8016"
  policy_url: "http://localhost:8002"
```

### OpenCode Adapter Config (After):
```bash
# .env file
ACGS_AUTH_SERVICE_URL=http://localhost:8016
ACGS_POLICY_SERVICE_URL=http://localhost:8002
ACGS_AUDIT_SERVICE_URL=http://localhost:8004
ACGS_HITL_SERVICE_URL=http://localhost:8006
ACGS_AGENT_ID=opencode-adapter
ACGS_AGENT_SECRET=your-secret
```

## Feature Mapping

### 1. Agent Management

**Gemini CLI:**
```bash
gemini-cli agent create --name "assistant"
gemini-cli agent list
gemini-cli agent get <agent-id>
```

**OpenCode Adapter:**
Agent management is now handled through ACGS Auth Service directly. The adapter uses a single agent identity configured via `ACGS_AGENT_ID`.

### 2. Code Execution

**Gemini CLI:**
```bash
gemini-cli execute code --code "print('Hello')" --language python
gemini-cli execute file script.py
gemini-cli execute assist "Write a function"
```

**OpenCode Adapter:**
```bash
# Execute command
curl -X POST http://localhost:8020/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "run",
    "args": ["script.py"],
    "context": {"language": "python"}
  }'
```

### 3. Policy Verification

**Gemini CLI:**
```bash
gemini-cli verify constitutional "operation" --params params.json
gemini-cli verify policy policy.rego --context context.json
```

**OpenCode Adapter:**
```bash
# Check permission
curl -X POST http://localhost:8020/check-permission \
  -H "Content-Type: application/json" \
  -d '{
    "action": "operation",
    "context": {...}
  }'
```

### 4. Monitoring

**Gemini CLI:**
```bash
gemini-cli monitor status --detailed
gemini-cli monitor health --continuous
```

**OpenCode Adapter:**
```bash
# Health check
curl http://localhost:8020/health

# Metrics
curl http://localhost:8020/metrics
```

## Docker Compose Migration

### Before (Gemini CLI):
```yaml
version: '3.8'
services:
  gemini-cli:
    build: ./services/cli/gemini_cli
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/data
```

### After (OpenCode Adapter):
```yaml
version: '3.8'
services:
  opencode-adapter:
    build: ./services/cli/opencode_adapter
    ports:
      - "8020:8020"
    environment:
      - ACGS_AUTH_SERVICE_URL=http://auth-service:8016
      - ACGS_POLICY_SERVICE_URL=http://policy-service:8002
      - ACGS_AUDIT_SERVICE_URL=http://audit-service:8004
      - ACGS_HITL_SERVICE_URL=http://hitl-service:8006
      - ACGS_AGENT_SECRET=${ACGS_AGENT_SECRET}
    depends_on:
      - auth-service
      - policy-service
```

## Testing the Migration

1. **Functional Tests**
   ```bash
   # Test basic execution
   curl -X POST http://localhost:8020/execute \
     -H "Content-Type: application/json" \
     -d '{"command": "version", "args": []}'

   # Test permission check
   curl -X POST http://localhost:8020/check-permission \
     -H "Content-Type: application/json" \
     -d '{"action": "read-file", "context": {}}'
   ```

2. **Performance Validation**
   ```bash
   # Check metrics
   curl http://localhost:8020/metrics | jq .

   # Verify P99 latency < 5ms
   # Verify cache hit rate > 85%
   ```

3. **Governance Validation**
   - Verify audit logs are being created
   - Test HITL escalation for high-risk operations
   - Confirm constitutional compliance checks

## Rollback Plan

If issues arise during migration:

1. **Stop OpenCode Adapter**
   ```bash
   docker-compose stop opencode-adapter
   ```

2. **Revert to Gemini CLI**
   ```bash
   docker-compose up -d gemini-cli
   ```

3. **Restore configurations**
   - Revert any client application changes
   - Restore original environment variables

## Common Issues

### 1. Authentication Errors
- Ensure `ACGS_AGENT_SECRET` is correctly set
- Verify agent is registered in ACGS Auth Service

### 2. Performance Degradation
- Check OpenCode Adapter metrics endpoint
- Verify cache configuration
- Review operation complexity

### 3. Policy Conflicts
- Compare policy evaluations between old and new systems
- Update policy rules if needed for OpenCode operations

## Support

For migration assistance:
1. Check OpenCode Adapter logs: `docker logs opencode-adapter`
2. Review ACGS service logs for governance issues
3. Monitor performance metrics dashboard

## Timeline

Recommended migration timeline:
- Week 1-2: Deploy OpenCode Adapter in parallel
- Week 3-4: Migrate non-critical workflows
- Week 5-6: Migrate critical workflows with monitoring
- Week 7-8: Decommission Gemini CLI

## Final Checklist

- [ ] OpenCode Adapter deployed and healthy
- [ ] All client applications updated
- [ ] Performance benchmarks met (P99 < 5ms, cache > 85%)
- [ ] Audit trails verified
- [ ] HITL integration tested
- [ ] Monitoring dashboards updated
- [ ] Team trained on new system
- [ ] Rollback plan tested
- [ ] Gemini CLI safely decommissioned
