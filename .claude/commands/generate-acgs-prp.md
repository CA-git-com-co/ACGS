# Generate ACGS PRP Command

This command generates a comprehensive Product Requirements Prompt (PRP) for ACGS features with constitutional compliance, performance validation, and multi-agent coordination integration.

## Usage

Use this command when you have an INITIAL.md file describing a feature you want to implement in the ACGS system.

```
/generate-acgs-prp INITIAL.md
```

## What this command does

This command will:

1. **Read the INITIAL.md feature request** and understand the requirements
2. **Research the ACGS codebase** to understand existing patterns and integration points
3. **Gather constitutional compliance context** including hash validation requirements
4. **Analyze performance requirements** for sub-5ms P99 latency targets
5. **Review multi-agent coordination patterns** for blackboard and consensus integration
6. **Create a comprehensive PRP** using the ACGS PRP template with full context

## ACGS-Specific Research Process

### Constitutional Compliance Research
- Validate constitutional hash requirements: `cdd01ef066bc6cf2`
- Review constitutional AI service integration patterns
- Analyze constitutional policy framework requirements
- Identify audit logging and compliance monitoring needs

### Performance Requirements Research
- Review ACGS performance targets (P99 < 5ms, >100 RPS, >85% cache hit rate)
- Analyze existing performance optimization patterns
- Identify caching strategies for constitutional validation
- Review performance monitoring and alerting requirements

### Multi-Agent Coordination Research
- Analyze blackboard service integration patterns (port 8010)
- Review multi-agent coordinator service patterns (port 8008)
- Study worker agent communication protocols (port 8009)
- Understand consensus engine coordination requirements

### ACGS Infrastructure Research
- Review service architecture and integration patterns
- Analyze existing FastAPI + Pydantic v2 patterns
- Study PostgreSQL Row-Level Security with multi-tenant isolation
- Review Redis caching patterns with constitutional compliance

## Research Steps

### Step 1: Codebase Analysis
I will thoroughly analyze the ACGS codebase to understand:
- Existing service patterns in `services/core/` and `services/platform_services/`
- Constitutional compliance patterns in `services/shared/constitutional/`
- Multi-agent coordination patterns in `services/core/multi_agent_coordinator/`
- Testing patterns in `tests/` and examples in `services/examples/context_engineering/`

### Step 2: Constitutional Framework Analysis
I will review the constitutional framework to understand:
- Constitutional hash validation requirements across all services
- Constitutional AI service integration at port 8001
- Constitutional policy library in governance synthesis service
- Audit logging requirements for constitutional compliance

### Step 3: Performance Pattern Analysis
I will analyze performance requirements including:
- Sub-5ms P99 latency targets for all coordination operations
- Throughput requirements >100 RPS for multi-agent handoffs
- Caching strategies with >85% hit rate requirements
- Performance monitoring and regression testing patterns

### Step 4: Integration Point Analysis
I will identify integration requirements with:
- **API Gateway** (port 8010): Request routing and security
- **Constitutional AI** (port 8001): Constitutional compliance validation
- **Integrity Service** (port 8002): Audit trail and cryptographic validation
- **Multi-Agent Coordinator** (port 8008): Agent orchestration
- **Worker Agents** (port 8009): Specialized domain agents
- **Blackboard Service** (port 8010): Shared knowledge coordination
- **Context Service** (port 8012): Governance workflow integration
- **Authentication** (port 8016): Multi-tenant JWT authentication

### Step 5: Context Gathering
I will gather comprehensive context including:
- **Documentation URLs**: Relevant ACGS documentation and architectural decisions
- **Code Examples**: Working patterns from existing ACGS services
- **Gotchas**: ACGS-specific considerations and common pitfalls
- **Anti-patterns**: What to avoid in ACGS implementations
- **Testing Patterns**: Constitutional test case patterns and validation requirements

## PRP Generation Process

### Constitutional Compliance Integration
Every generated PRP will include:
- Mandatory constitutional hash validation: `cdd01ef066bc6cf2`
- Constitutional AI service integration patterns
- Comprehensive audit logging for constitutional events
- Constitutional policy compliance validation
- Constitutional error handling and escalation

### Performance Validation Integration
Every generated PRP will include:
- Sub-5ms P99 latency targets and validation
- Throughput requirements and measurement
- Caching strategies with constitutional compliance
- Performance monitoring with Prometheus metrics
- Performance regression testing requirements

### Multi-Agent Coordination Integration
Every generated PRP will include:
- Blackboard service integration for shared knowledge
- Multi-agent coordinator service registration
- Worker agent communication protocols
- Consensus engine integration where applicable
- Agent lifecycle management and monitoring

### Testing Framework Integration
Every generated PRP will include:
- ConstitutionalTestCase inheritance requirements
- Constitutional compliance test patterns
- Performance validation test requirements
- Multi-agent coordination test patterns
- Integration test specifications

## Implementation Blueprint Generation

The generated PRP will include a comprehensive implementation blueprint with:

### Data Models
- Pydantic models inheriting from ACGS base classes
- Constitutional compliance validation in all models
- Performance optimization considerations
- Multi-tenant isolation support

### Architecture Diagrams
- Service integration with existing ACGS infrastructure
- Constitutional compliance validation flow
- Multi-agent coordination patterns
- Performance monitoring integration

### Validation Commands
- Constitutional compliance validation commands
- Performance regression testing commands
- Multi-agent coordination testing commands
- Integration testing specifications

### Quality Gates
- Constitutional compliance checkpoints
- Performance target validation
- Multi-agent coordination verification
- Security and isolation validation

## Output

The command will generate a complete PRP file in the `PRPs/` directory with:
- **Full constitutional compliance integration** including hash validation
- **Comprehensive performance requirements** with sub-5ms targets
- **Multi-agent coordination specifications** with blackboard integration
- **Complete testing framework** with constitutional test patterns
- **Production readiness checklist** with ACGS-specific requirements

The generated PRP will serve as a comprehensive implementation guide that can be used with the `/execute-acgs-prp` command for systematic implementation with constitutional compliance and performance validation.

## ACGS Context Engineering Principles

This command embodies ACGS Context Engineering principles:
- **Context is King**: Comprehensive context gathering from ACGS codebase
- **Constitutional Compliance**: Mandatory constitutional framework integration
- **Performance Assurance**: Sub-5ms latency and throughput requirements
- **Multi-Agent Coordination**: Blackboard and consensus integration
- **Progressive Implementation**: Start simple, validate, enhance
- **Self-Validation**: Executable test commands and validation loops

---

**Constitutional Hash**: `cdd01ef066bc6cf2` - All generated PRPs include constitutional compliance validation