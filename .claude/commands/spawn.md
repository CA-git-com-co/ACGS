<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Purpose**: Parallel specialized agents



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

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Spawn specialized sub-agents for focused tasks with parallel execution capabilities.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/spawn --agent researcher "OAuth 2.0 best practices"` - Research then implement
- `/spawn --mode parallel --agent builder "User auth, Profile API"` - Parallel development
- `/spawn --mode sequential "Research → Build → Review payment"` - Full cycle workflow
- `/spawn --mode collaborative --ultrathink "Design microservices"` - Collaborative design

## Agent Types

Researcher Agent:
- Deep dive into topics
- Compare solutions
- Analyze trade-offs
- Find best practices
- Document findings

Builder Agent:
- Generate code
- Implement features
- Create tests
- Build prototypes
- Integrate systems

Reviewer Agent:
- Code quality checks
- Security analysis
- Performance review
- Best practice validation
- Suggest improvements

Optimizer Agent:
- Performance profiling
- Resource optimization
- Algorithm improvements
- Database tuning
- Cache strategies

Documenter Agent:
- API documentation
- User guides
- Code comments
- Architecture docs
- README files

## Execution Modes

Sequential Mode:
```yaml
Flow: Agent1 → Agent2 → Agent3
Use: When tasks depend on each other
Example: Research → Build → Review
```

Parallel Mode:
```yaml
Flow: Agent1 | Agent2 | Agent3
Use: For independent tasks
Example: Multiple feature builds
```

Collaborative Mode:
```yaml
Flow: Agents work together
Use: Complex problems
Example: System design session
```

## Best Practices

Task Definition:
- Clear objectives
- Specific deliverables
- Success criteria
- Resource limits
- Time constraints

Agent Selection:
- Match expertise to task
- Consider dependencies
- Plan coordination
- Set boundaries
- Define handoffs

Coordination:
- Clear communication
- Shared context
- Progress tracking
- Result integration
- Quality control

## Examples

```bash
# Research then implement
/spawn --agent researcher "OAuth 2.0 best practices"
/spawn --agent builder "Implement OAuth based on research"

# Parallel feature development
/spawn --mode parallel --agent builder "User auth, Profile API, Settings UI"

# Full cycle with review
/spawn --mode sequential "Research → Build → Review payment integration"

# Collaborative system design
/spawn --mode collaborative --ultrathink "Design microservices architecture"
```

## Integration

Works with:
- All command flags pass through
- Inherits persona preferences
- Shares project context
- Accumulates findings
- Coordinates outputs

## Deliverables

- Agent execution logs
- Task completion reports
- Integrated results
- Performance metrics
- Lessons learned
- Handoff documentation

@include shared/universal-constants.yml#Standard_Messages_Templates