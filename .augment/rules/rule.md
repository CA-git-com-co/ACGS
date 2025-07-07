---
type: "always_apply"
---

# ACGS Multi-Agent Rules
**Constitutional Hash:** `cdd01ef066bc6cf2`

## 1. Agent Roles

**Claude Agents:**
- Strategic planning, constitutional compliance
- MCP orchestration, cross-service integration
- P99 <5ms decisions, 100% compliance rate

**OpenCode Agents:**
- Direct execution, file operations, testing
- P99 <100ms file ops, <5ms validation overhead

## 2. Message Schema
```typescript
interface ACGSMessage {
  message_id: string
  constitutional_hash: "cdd01ef066bc6cf2"
  sender: { agent_id: string, agent_type: "claude" | "opencode" }
  recipient: { agent_id: string, agent_type: "claude" | "opencode" }
  message_type: "task_request" | "task_response" | "escalation"
  payload: { content: any, checksum: string }
  compliance: { safety_level: string, audit_required: boolean }
}
```

## 3. Constitutional Compliance
```python
def validate_constitutional_hash(message: ACGSMessage) -> bool:
    return message.constitutional_hash == "cdd01ef066bc6cf2"
```

**Escalation Triggers:**
- P99 latency >10ms for 3 consecutive measurements
- Constitutional hash validation failure
- Resource exhaustion (CPU >90%, Memory >95%)
- Error rate >5% over 5-minute window

## 4. Performance Targets
- Coordination latency: P99 <5ms
- Task handoffs: >100 RPS
- Cache hit rate: >85%
- Constitutional compliance: 100%

## 5. Services
- ACGS: Auth 8016, Constitutional AI 8001, Coordinator 8008, Blackboard 8010
- MCP: Aggregator 3000, Filesystem 3001, GitHub 3002, Browser 3003
- Database: PostgreSQL 5439, Cache: Redis 6389

---
**Constitutional Hash:** `cdd01ef066bc6cf2`
