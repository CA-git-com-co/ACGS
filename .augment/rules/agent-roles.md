---
type: "agent_coordination"
constitutional_hash: "cdd01ef066bc6cf2"
---

# ACGS Agent Roles
**Constitutional Hash:** `cdd01ef066bc6cf2`

## Claude Agents
**Responsibilities:**
- Strategic planning, constitutional compliance validation
- MCP orchestration, cross-service integration
- Human-in-the-loop coordination and escalation

**Capabilities:**
- ACGS service stack access (ports 8001-8016)
- Constitutional AI validation through service mesh
- Advanced reasoning with context retention

**Performance:**
- Decision latency: P99 <5ms, compliance: 100%
- Escalation response: <30 seconds

**Constraints:**
- Cannot execute system commands directly
- Must validate through constitutional framework
- Requires MCP services for file operations

## OpenCode Agents
**Responsibilities:**
- Direct code execution and file operations
- Real-time development environment interaction
- Tool-based task execution and testing

**Capabilities:**
- Native file system access with constitutional validation
- Direct command execution through secure sandboxing
- Integration with development tools (LSP, formatters)

**Performance:**
- Command execution: P99 <100ms file ops, P99 <1s complex
- Constitutional validation: <5ms overhead

**Constraints:**
- Limited to local workspace operations
- Cannot make autonomous architectural decisions
- Must escalate complex decisions to Claude agents

## Services
- Auth 8016, Constitutional AI 8001, Coordinator 8008
- MCP Aggregator 3000, PostgreSQL 5439, Redis 6389

---
**Constitutional Hash:** `cdd01ef066bc6cf2`
