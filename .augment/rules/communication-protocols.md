---
type: "agent_requested"
description: "Example description"
---
# ACGS Communication Protocols
**Constitutional Hash:** `cdd01ef066bc6cf2`

## Message Schema
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

## Validation
- Constitutional hash must be exactly `cdd01ef066bc6cf2`
- All required fields must be present and valid
- Payload checksum must match content

---
**Constitutional Hash:** `cdd01ef066bc6cf2`
