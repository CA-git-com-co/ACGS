# ACGS-1 Workflow Transition & Deprecation Guide

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This guide provides complete instructions for transitioning from legacy workflows to modern unified workflows and safely deprecating old workflows.

## 🎯 **Transition Overview**

### Current Status
- ✅ **Modern workflows created** (4 new workflows)
- ✅ **Vulnerability fixes applied** (238 vulnerabilities across 36 files)
- ✅ **Branch protection guide created** (ready for when protection is enabled)
- ⚠️ **Billing/quota issues** preventing workflow execution testing
- 🔄 **Legacy deprecation pending** (waiting for modern workflow validation)

### Modern Workflow Architecture

#### Primary Workflows
1. **`unified-ci-modern.yml`** - Main CI/CD pipeline
   - Smart change detection and conditional execution
   - UV package manager for 3x faster installs
   - Quality gates with 80-90% coverage targets
   - Multi-environment deployment support

2. **`security-focused.yml`** - Comprehensive security scanning
   - Zero-tolerance policy for critical vulnerabilities
   - Multi-tool scanning (Safety, Bandit, Semgrep, Trivy)
   - Daily automated scans
   - SARIF integration for GitHub Security tab

3. **`deployment-modern.yml`** - Environment-specific deployment
   - Blue-green deployment for production
   - Canary deployment for staging
   - Rolling updates for development
   - Automated rollback capabilities

4. **`solana-anchor.yml`** - Blockchain-specific validation
   - Rust security audits
   - Anchor program building and testing
   - Solana validator integration

## 🚀 **Safe Deprecation Process**

### Prerequisites Checklist
Before deprecating legacy workflows, ensure:

- [ ] GitHub Actions billing/quota issues resolved
- [ ] Modern workflows running successfully for at least 1 week
- [ ] Branch protection rules updated to use new workflow names
- [ ] Team notified of upcoming changes
- [ ] Rollback plan prepared

### Step 1: Validate Modern Workflow Health

```bash
# Run the workflow monitoring script
python scripts/monitor_workflows.py

# Check for success rate > 80% for all modern workflows
```

### Step 2: Update Branch Protection Rules

```bash
# Run branch protection setup (when enabled)
python scripts/setup_branch_protection.py

# Or follow manual setup guide
cat BRANCH_PROTECTION_GUIDE.md
```

### Step 3: Execute Safe Deprecation

```bash
# First, run in dry-run mode to preview changes
python scripts/deprecate_legacy_workflows.py --dry-run

# If preview looks good, execute deprecation
python scripts/deprecate_legacy_workflows.py

# For emergency deprecation (skip health checks)
python scripts/deprecate_legacy_workflows.py --force
```

## 📊 **Legacy Workflows to be Deprecated**

### Automatic Deprecation (Safe)
These workflows will be automatically deprecated:

- `ci-legacy.yml` - Replaced by `unified-ci-modern.yml`
- `security-comprehensive.yml` - Replaced by `security-focused.yml`
- `enhanced-parallel-ci.yml` - Functionality merged into unified pipeline
- `cost-optimized-ci.yml` - Optimizations included in modern workflows
- `optimized-ci.yml` - Replaced by more comprehensive modern workflows
- `ci-uv.yml` - UV functionality integrated into unified pipeline
- `enterprise-ci.yml` - Enterprise features included in modern workflows
- `ci.yml` - Original CI workflow (deprecated)
- `security.yml` - Original security workflow (deprecated)

### Manual Review Required
These workflows require manual evaluation before deprecation:

- `release.yml` - Check if release automation is still needed
- `publish.yml` - Verify package publishing requirements
- `pages.yml` - GitHub Pages deployment (if used)
- `dependabot.yml` - Automated dependency updates

## 🔄 **Migration Mapping**

### Functionality Migration Table

| Legacy Workflow | Modern Replacement | Key Improvements |
|----------------|-------------------|------------------|
| `ci-legacy.yml` | `unified-ci-modern.yml` | UV package manager, smart change detection |
| `security-comprehensive.yml` | `security-focused.yml` | Zero-tolerance policy, SARIF integration |
| `enhanced-parallel-ci.yml` | `unified-ci-modern.yml` | Better parallelization, conditional execution |
| `cost-optimized-ci.yml` | All modern workflows | Built-in cost optimization |
| `deploy.yml` | `deployment-modern.yml` | Multi-environment strategies |

### Required Status Check Updates

Replace these legacy checks in branch protection:
```yaml
# OLD (remove these)
- ci-legacy.yml
- security-comprehensive.yml
- enhanced-parallel-ci.yml

# NEW (add these)
- quality-gates
- security-summary
- blockchain-validation
- container-security
```

## ⚠️ **Rollback Procedures**

### If Modern Workflows Fail

1. **Immediate Response**
   ```bash
   # Copy workflow from archive
   cp .github/workflows/deprecated/ci-legacy.yml .github/workflows/

   # Remove deprecation notice from file header
   # Update GitHub Actions versions if needed
   ```

2. **Emergency Rollback Script**
   ```bash
   # Restore all legacy workflows
   cp .github/workflows/deprecated/*.yml .github/workflows/

   # Update branch protection to use legacy workflow names
   # Notify team of rollback
   ```

3. **Post-Rollback Actions**
   - Investigate root cause of modern workflow failures
   - Fix issues in modern workflows
   - Plan re-migration timeline
   - Document lessons learned

### Rollback Decision Matrix

| Scenario | Action | Timeline |
|----------|--------|----------|
| Single workflow failure | Fix specific workflow | 1-2 hours |
| Multiple workflow failures | Partial rollback | 4-6 hours |
| Complete pipeline failure | Full rollback | Immediate |
| Security scan failures | Continue with warnings | Monitor closely |

## 📋 **Post-Deprecation Checklist**

### Immediate Actions (Day 1)
- [ ] Verify all modern workflows running successfully
- [ ] Confirm branch protection rules updated
- [ ] Check that no builds are blocked
- [ ] Monitor for any regression issues

### Short-term Actions (Week 1)
- [ ] Team training on new workflow structure
- [ ] Update CI/CD documentation
- [ ] Remove legacy workflow references from README
- [ ] Clean up old workflow run history (optional)

### Long-term Actions (Month 1)
- [ ] Performance comparison analysis
- [ ] Cost optimization review
- [ ] Team feedback collection
- [ ] Process improvement recommendations

## 🛡️ **Security Considerations**

### During Transition
- All security scans continue running
- Zero-tolerance policy for critical vulnerabilities maintained
- Enhanced scanning capabilities in modern workflows
- SARIF integration provides better visibility

### Post-Deprecation
- Regular security scan monitoring
- Dependency vulnerability tracking
- Container security validation
- Compliance reporting automation

## 📞 **Support & Troubleshooting**

### Common Issues

1. **"Workflow not found" errors**
   - Update branch protection rules
   - Clear cached workflow references
   - Restart pending runs

2. **Permission denied errors**
   - Check GitHub token permissions
   - Verify repository access levels
   - Review organization security policies

3. **Build failures**
   - Check dependency conflicts
   - Verify environment variables
   - Review timeout configurations

### Getting Help

1. **Check Documentation**
   - Review workflow logs in GitHub Actions tab
   - Consult `.github/workflows/README.md`
   - Read individual workflow file comments

2. **Run Diagnostic Scripts**
   ```bash
   python scripts/monitor_workflows.py
   python scripts/fix_vulnerabilities.py --dry-run
   ```

3. **Contact Support**
   - Create GitHub issue with workflow logs
   - Include environment details
   - Specify exact error messages

## 📞 **Support & Troubleshooting**

### Common Issues

1. **"Workflow not found" errors**
   - Update branch protection rules
   - Clear cached workflow references
   - Restart pending runs

2. **Permission denied errors**
   - Check GitHub token permissions
   - Verify repository access levels
   - Review organization security policies

3. **Build failures**
   - Check dependency conflicts
   - Verify environment variables
   - Review timeout configurations

### Getting Help

1. **Check Documentation**
   - Review workflow logs in GitHub Actions tab
   - Consult `.github/workflows/README.md`
   - Read individual workflow file comments

2. **Run Diagnostic Scripts**
   ```bash
   python scripts/monitor_workflows.py
   python scripts/fix_vulnerabilities.py --dry-run
   ```

3. **Contact Support**
   - Create GitHub issue with workflow logs
   - Include environment details
   - Specify exact error messages

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)
- [ACGS GitOps Task Completion Report](../architecture/ACGS_GITOPS_TASK_COMPLETION_REPORT.md)
- [ACGS GitOps Comprehensive Validation Report](../architecture/ACGS_GITOPS_COMPREHENSIVE_VALIDATION_REPORT.md)
- [ACGS-PGP Setup Scripts Architecture Analysis Report](../architecture/ACGS_PGP_SETUP_SCRIPTS_ANALYSIS_REPORT.md)
- [ACGS Documentation Quality Metrics and Continuous Improvement](../DOCUMENTATION_QUALITY_METRICS.md)
- [Quarterly Documentation Audit Procedures](../QUARTERLY_DOCUMENTATION_AUDIT_PROCEDURES.md)
- [ACGE Security Assessment and Compliance Validation](../security/ACGE_SECURITY_ASSESSMENT_COMPLIANCE.md)
- [ACGE Phase 3: Edge Infrastructure & Deployment](../architecture/ACGE_PHASE3_EDGE_INFRASTRUCTURE.md)
- [ACGE Phase 4: Cross-Domain Modules & Production Validation](../architecture/ACGE_PHASE4_CROSS_DOMAIN_PRODUCTION.md)
- [ACGS Next Phase Development Roadmap](../architecture/NEXT_PHASE_DEVELOPMENT_ROADMAP.md)
- [ACGS Remaining Tasks Completion Summary](../REMAINING_TASKS_COMPLETION_SUMMARY.md)
- [GitHub Actions Systematic Fixes - Final Report](workflow_systematic_fixes_final_report.md)
- [GitHub Actions Workflow Systematic Fixes Summary](workflow_fixes_summary.md)
- [Security Input Validation Integration - Completion Report](../security_validation_completion_report.md)
- [Phase 2: Enhanced Production Readiness - COMPLETION REPORT](../phase2_completion_report.md)
- [Phase 1: Critical Path to Basic Production Readiness - COMPLETION REPORT](../phase1_completion_report.md)
- [Free Model Usage Guide for ACGS OpenRouter Integration](../free_model_usage.md)

## 📈 **Success Metrics****

### Key Performance Indicators

1. **Reliability**
   - Target: >95% workflow success rate
   - Measurement: Weekly success rate monitoring

2. **Performance**
   - Target: <15 minutes total pipeline time
   - Measurement: Average workflow duration

3. **Security**
   - Target: Zero critical vulnerabilities
   - Measurement: Daily security scan results

4. **Cost Efficiency**
   - Target: 30% reduction in compute minutes
   - Measurement: Monthly billing analysis

### Monitoring Dashboard

Track these metrics:
- Workflow success rates
- Build time trends
- Security scan results
- Deployment frequency
- Failure recovery time

## 🎉 **Benefits of Modern Workflows**

### Technical Improvements
- **3x faster installs** with UV package manager
- **Smart change detection** reduces unnecessary runs
- **Enhanced security scanning** with multiple tools
- **Better error handling** with retry logic
- **Improved caching** for faster builds

### Operational Benefits
- **Unified pipeline** reduces complexity
- **Environment-specific deployments** improve reliability
- **Comprehensive reporting** enhances visibility
- **Automated rollback** reduces downtime
- **Cost optimization** built-in by default

### Developer Experience
- **Clearer workflow structure** easier to understand
- **Better error messages** faster debugging
- **Conditional execution** reduces noise
- **Modern tooling** improved productivity
- **Comprehensive documentation** self-service support

---

*This guide ensures a smooth transition from legacy to modern workflows while maintaining system reliability and security.*
