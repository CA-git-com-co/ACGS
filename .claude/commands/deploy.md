**Purpose**: Constitutional application deployment with mandatory compliance validation


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

---

**CONSTITUTIONAL COMPLIANCE CRITICAL:**
- ALL deployments MUST validate constitutional hash `cdd01ef066bc6cf2` 
- Production deployments REQUIRE constitutional compliance certification
- Deployment audit trail MUST integrate with ACGS Integrity Service (port 8002)
- Constitutional violations IMMEDIATELY halt deployment process

@include shared/universal-constants.yml#Universal_Legend
@include shared/acgs-constitutional-compliance.yml#Constitutional_Framework

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Deploy application to env specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/deploy --env staging --think --constitutional-hash cdd01ef066bc6cf2` - Constitutional staging deployment
- `/deploy --env prod --think-hard --constitutional-compliance --constitutional-certification` - Constitutional production deployment
- `/deploy --rollback --ultrathink --constitutional-oversight` - Constitutional rollback with compliance verification

Deployment modes:

**--env:** Specify target environment
- dev: Deploy→dev env for testing
- staging: Deploy→staging for pre-prod validation  
- prod: Deploy→prod w/ all safety checks

**--rollback:** Revert→previous stable deployment | Maintain deployment history→audit trail | Verify rollback success w/ health checks

Pre-deploy cleanup:
- Clean previous artifacts | Remove dev-only files (config/environments/development.env.local, debug cfgs)
- Validate prod cfg (no debug flags, correct URLs) | Clean old versions→free space

Deployment workflow:
1. Validate→Check prerequisites & cfg 2. Build→Create artifacts 3. Test→Run smoke tests
4. Deploy→Execute strategy 5. Verify→Confirm health & functionality

Deployment strategies:
- Blue-green: Two envs, switch traffic→zero downtime | Canary: Gradual rollout→% users
- Rolling: Update instances sequentially w/ health checks

Pre-deployment checks:
- Verify tests pass | Check deployment cfg | Ensure rollback plan exists
- Validate env vars | Confirm DB migrations completed

Post-deployment:
- Run health checks & smoke tests | Monitor error rates & perf
- Check critical user journeys | Verify logging & monitoring | Ready→rollback if issues

## Safety & Best Practices

Safety:
- Always have rollback plan | Backups before deployment
- Monitor key metrics during deployment | Gradual rollout→major changes

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates


## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Constitutional Compliance**: All operations maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS, >85% cache hit rates).

**Last Updated**: 2025-07-17 - Constitutional compliance enhancement
