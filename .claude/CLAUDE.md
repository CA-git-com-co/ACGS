# CLAUDE.md - ACGS-SuperClaude Integration

This file provides enhanced guidance to Claude Code integrating SuperClaude's specialized development framework with ACGS's constitutional AI governance.

## Constitutional Compliance (CRITICAL)
**IMMUTABLE REQUIREMENTS:**
- **ALWAYS** validate constitutional hash `cdd01ef066bc6cf2` in all agent communications
- **NEVER** bypass constitutional compliance validation for any operation
- **ALWAYS** implement pre-execution, runtime, and post-execution compliance checks
- **ESCALATE** to human oversight immediately for constitutional violations

## Multi-Agent Coordination Guidelines

### Agent Communication Patterns
- Use hierarchical coordination: Claude agents for strategic planning, OpenCode agents for execution
- Implement document-based communication following MetaGPT assembly line paradigm
- Use MCP (Model Context Protocol) for Claude agent integration with services
- Follow A2A (Agent2Agent) protocol for external framework interoperability
- Maintain complete audit trail for all agent interactions
- **ALL COMMUNICATIONS MUST INCLUDE constitutional hash `cdd01ef066bc6cf2`**

### Performance Requirements (NON-NEGOTIABLE)
- **P99 Latency**: <5ms for coordination operations, <2ms for cached decisions
- **Throughput**: >100 RPS for task handoffs between agents
- **Cache Hit Rate**: >85% for constitutional decisions and agent capabilities
- **Constitutional Compliance Rate**: 100% (no exceptions)
- **Escalation Response**: <30 seconds for human-in-the-loop triggers

## SuperClaude Integration

### Core Configuration
@include shared/superclaude-core.yml#Core_Philosophy
@include shared/acgs-constitutional-compliance.yml#Constitutional_Framework

### Enhanced Command Framework
SuperClaude provides 19 specialized commands with constitutional compliance integration:

#### Development Commands
- `/build` - Project builder with constitutional validation
- `/dev-setup` - Environment setup with ACGS compliance
- `/test` - Testing framework with audit integration

#### Analysis & Quality Commands
- `/review` - Code review with constitutional compliance checks
- `/analyze` - System analysis with governance validation
- `/troubleshoot` - Debugging with audit trail
- `/improve` - Optimization with compliance verification
- `/explain` - Documentation with constitutional context

#### Operations & Security Commands  
- `/deploy` - Deployment with constitutional validation
- `/migrate` - Migrations with compliance checks
- `/scan` - Security audits with governance integration
- `/estimate` - Planning with constitutional context
- `/cleanup` - Maintenance with audit trail
- `/git` - Git operations with compliance tracking

#### Design & Workflow Commands
- `/design` - Architecture with constitutional principles
- `/spawn` - Parallel execution with governance oversight
- `/document` - Documentation with compliance validation
- `/load` - Context loading with audit integration
- `/task` - Task management with constitutional tracking

### Cognitive Personas with Constitutional Compliance

#### Available Personas (All Constitutional Hash Validated)
| Persona | Constitutional Focus | ACGS Integration | Use Cases |
|---------|---------------------|------------------|-----------|
| **architect** | Constitutional system design | Governance framework integration | Architecture with compliance |
| **frontend** | Constitutional UX principles | Audit-enabled UI | Compliant user interfaces |
| **backend** | Constitutional API design | Service governance | Compliant backend systems |
| **security** | Constitutional security | ACGS security framework | Security with governance |
| **analyzer** | Constitutional analysis | Audit trail integration | Compliant debugging |
| **qa** | Constitutional quality | Compliance testing | Quality with governance |
| **performance** | Constitutional optimization | Performance governance | Compliant optimization |
| **refactorer** | Constitutional code quality | Governance-aware refactoring | Compliant code improvement |
| **mentor** | Constitutional knowledge sharing | Audit-enabled documentation | Compliant knowledge transfer |

### Persona Activation with Constitutional Validation
```bash
# All personas automatically include constitutional compliance
/analyze --code --persona-architect     # Constitutional systems thinking
/build --react --persona-frontend       # Constitutional UX development  
/scan --security --persona-security     # Constitutional security analysis
/troubleshoot --prod --persona-analyzer # Constitutional root cause analysis
```

### Constitutional MCP Integration

#### Enhanced MCP Architecture
@include commands/shared/flag-inheritance.yml#Universal Flags (All Commands)
@include commands/shared/execution-patterns.yml#Servers
@include shared/acgs-mcp-integration.yml#Constitutional_MCP_Framework

#### MCP Services with Constitutional Compliance
- **Context7**: Library documentation with constitutional validation
- **Sequential**: Multi-step reasoning with audit trails
- **Magic**: AI components with governance oversight
- **Puppeteer**: Browser automation with compliance tracking

#### Constitutional MCP Workflow
```mermaid
graph TD
    A[Claude Agent Request] --> B{Constitutional Validation}
    B --> C{MCP Aggregator :3000}
    C --> D[Constitutional AI :8001]
    D --> E{Multi-Agent Coordinator :8008}
    E --> F[SuperClaude Command Processing]
    F --> G[Persona-Specific Analysis]
    G --> H[MCP Tool Integration]
    H --> I[Constitutional Compliance Check]
    I --> J[Audit Trail :8002]
    J --> K[Response with Hash Validation]
```

### Advanced Token Economy with Constitutional Oversight
@include shared/superclaude-core.yml#Advanced_Token_Economy
@include shared/acgs-constitutional-compliance.yml#Token_Economy_Governance

### Thinking Modes with Constitutional Context
@include commands/shared/flag-inheritance.yml#Universal Flags (All Commands)

#### Constitutional Thinking Depth Control
```bash
# Standard constitutional analysis
/analyze --think --constitutional-hash cdd01ef066bc6cf2

# Deep constitutional analysis  
/design --think-hard --constitutional-compliance

# Maximum constitutional depth
/troubleshoot --ultrathink --constitutional-oversight
```

### Evidence-Based Development with Constitutional Compliance
@include shared/superclaude-core.yml#Evidence_Based_Standards
@include shared/acgs-constitutional-compliance.yml#Evidence_Framework

SuperClaude with ACGS encourages:
- Constitutional documentation for all design decisions
- Compliance testing for all quality improvements
- Governance metrics for all performance work
- Constitutional validation for all deployments
- Constitutional analysis for all architectural choices

### Performance Standards with Constitutional Compliance
@include shared/superclaude-core.yml#Performance_Standards
@include commands/shared/compression-performance-patterns.yml#Performance_Baselines

**Constitutional Performance Targets:**
- **Throughput**: ≥1000 RPS with 100% constitutional compliance
- **Latency**: P99 ≤ 5ms with constitutional validation
- **Cache Hit Rate**: 85%+ with constitutional cache validation
- **Constitutional Compliance**: 100% (no exceptions)
- **Audit Trail Completeness**: 100% for all operations

### Security Standards with Constitutional Framework
@include shared/superclaude-rules.yml#Security_Standards
@include commands/shared/security-patterns.yml#OWASP_Top_10
@include commands/shared/security-patterns.yml#Validation_Levels
@include shared/acgs-constitutional-compliance.yml#Security_Framework

### Constitutional Error Recovery
@include shared/superclaude-mcp.yml#Error_Recovery
@include shared/acgs-constitutional-compliance.yml#Error_Handling

### Session Management with Constitutional Tracking
@include shared/superclaude-core.yml#Session_Management
@include commands/shared/system-config.yml#Session_Settings
@include shared/acgs-constitutional-compliance.yml#Session_Governance

## ACGS Service Architecture Integration

### Production-Grade Services with SuperClaude Integration

- **Constitutional AI Service** (port 8001): SuperClaude command validation
- **Integrity Service** (port 8002): SuperClaude audit integration
- **Multi-Agent Coordinator** (port 8008): SuperClaude persona coordination
- **Worker Agents** (port 8009): SuperClaude specialized agent integration
- **Blackboard Service** (port 8010): SuperClaude knowledge sharing

### SuperClaude-ACGS Coordination Workflow

```mermaid
graph TD
    A[SuperClaude Command] --> B{Constitutional Validation cdd01ef066bc6cf2}
    B --> C[Multi-Agent Coordinator :8008]
    C --> D[Persona-Specific Processing]
    D --> E[ACGS Worker Agents :8009]
    E --> F[Blackboard Knowledge Sharing :8010]
    F --> G[MCP Tool Integration]
    G --> H[Constitutional Compliance Check]
    H --> I[Audit Trail :8002]
    I --> J[Response with Constitutional Hash]
```

## Development Environment Setup

```bash
# Initial setup with SuperClaude integration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start ACGS infrastructure with SuperClaude support
docker compose -f infrastructure/docker/docker-compose.acgs.yml up -d

# Validate SuperClaude-ACGS integration
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8008/health  # Multi-Agent Coordinator
curl http://localhost:3000/health  # MCP Aggregator

# Test SuperClaude commands with constitutional compliance
/load                              # Load project with constitutional context
/analyze --code --constitutional-hash cdd01ef066bc6cf2  # Constitutional analysis
/analyze --persona-architect --constitutional-compliance  # Constitutional architecture
```

## Testing Commands with Constitutional Compliance

```bash
# Constitutional compliance testing
make test-constitutional
make test-superclaude-integration

# Multi-agent coordination with SuperClaude
python tests/multi_agent_test_runner.py --superclaude --constitutional-hash cdd01ef066bc6cf2
pytest tests/unit/superclaude_acgs_coordination/ -v
pytest tests/integration/constitutional_superclaude/ -v

# SuperClaude performance validation
python tests/performance/test_superclaude_performance.py --constitutional-compliance
```

## Constitutional Compliance Validation

All SuperClaude operations must:
1. Include constitutional hash `cdd01ef066bc6cf2` in requests
2. Validate constitutional compliance pre-execution
3. Monitor constitutional adherence during execution
4. Log constitutional compliance post-execution
5. Escalate constitutional violations immediately

## Command Categories with Constitutional Context

### Development (Constitutional Framework)
- `/build` - Constitutional project development
- `/dev-setup` - Constitutional environment setup
- `/test` - Constitutional testing framework

### Analysis & Improvement (Constitutional Governance)
- `/review` - Constitutional code review
- `/analyze` - Constitutional system analysis
- `/troubleshoot` - Constitutional debugging
- `/improve` - Constitutional optimization
- `/explain` - Constitutional documentation

### Operations (Constitutional Security)
- `/deploy` - Constitutional deployment
- `/migrate` - Constitutional migrations
- `/scan` - Constitutional security validation
- `/estimate` - Constitutional project planning
- `/cleanup` - Constitutional maintenance
- `/git` - Constitutional version control

### Design & Workflow (Constitutional Architecture)
- `/design` - Constitutional system design
- `/spawn` - Constitutional parallel execution
- `/document` - Constitutional documentation
- `/load` - Constitutional context management
- `/task` - Constitutional task coordination

## Research Context

This integration demonstrates constitutional AI governance with SuperClaude's specialized development framework, providing production-ready multi-agent coordination while maintaining 100% constitutional compliance with hash `cdd01ef066bc6cf2`.

---
*ACGS-SuperClaude Integration v1.0 | Constitutional AI Governance | Evidence-based methodology | Enhanced Claude Code configuration*
*Constitutional Hash: cdd01ef066bc6cf2 - ALWAYS VALIDATE*