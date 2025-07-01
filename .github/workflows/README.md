# ACGS-1 GitHub Actions Workflows

This directory contains the CI/CD workflows for the ACGS-1 project. Due to modernization efforts, many workflows have been consolidated.

## 🚀 **PRIMARY WORKFLOWS** (Use These)

### Core CI/CD
- **`unified-ci-modern.yml`** - Main CI/CD pipeline with quality gates, security scanning, and deployment
- **`deployment-modern.yml`** - Dedicated deployment workflow with environment-specific strategies
- **`security-focused.yml`** - Comprehensive security scanning (daily + on-demand)

### Specialized
- **`solana-anchor.yml`** - Blockchain/Rust specific validation and testing

## ⚠️ **DEPRECATED WORKFLOWS** (Do Not Use)

The following workflows are deprecated and should not be used:
- `ci-legacy.yml` - Replaced by `unified-ci-modern.yml`
- `enhanced-parallel-ci.yml` - Consolidated into `unified-ci-modern.yml`
- `cost-optimized-ci.yml` - Features merged into `unified-ci-modern.yml`
- `optimized-ci.yml` - Replaced by `unified-ci-modern.yml`
- `ci-uv.yml` - UV package manager now integrated into main workflows
- `enterprise-ci.yml` - Enterprise features moved to `unified-ci-modern.yml`
- `security-comprehensive.yml` - Replaced by `security-focused.yml`

## 📋 **WORKFLOW USAGE GUIDE**

### For Regular Development
Use `unified-ci-modern.yml` - it automatically triggers on:
- Push to main/master/develop branches
- Pull requests to main/master/develop
- Weekly scheduled runs
- Manual dispatch with environment selection

### For Security Audits
Use `security-focused.yml` - it provides:
- Daily automated security scans
- On-demand security validation
- Critical vulnerability detection
- Compliance reporting

### For Deployment
Use `deployment-modern.yml` - it supports:
- Blue-green deployment (production)
- Canary deployment (staging)
- Rolling deployment (development)
- Health check validation

## 🔧 **ENVIRONMENT VARIABLES**

Key environment variables used across workflows:

```yaml
# Core versions
PYTHON_VERSION: '3.11'
NODE_VERSION: '20'
RUST_TOOLCHAIN: '1.81.0'
SOLANA_CLI_VERSION: '1.18.22'
ANCHOR_CLI_VERSION: '0.29.0'

# Performance thresholds
COVERAGE_THRESHOLD: 80
COVERAGE_TARGET: 90
ENTERPRISE_BUILD_TARGET_MINUTES: 8

# Security settings
SECURITY_SCAN_ENABLED: true
CRITICAL_THRESHOLD: 0
HIGH_THRESHOLD: 5
```

## 🏗️ **WORKFLOW ARCHITECTURE**

```
unified-ci-modern.yml
├── preflight (change detection)
├── quality-gates (parallel)
│   ├── code quality
│   ├── security scanning
│   └── test coverage
├── blockchain-validation (conditional)
├── container-security (parallel)
├── integration-tests
├── deployment (conditional)
└── reporting
```

## 📊 **PERFORMANCE OPTIMIZATIONS**

The modern workflows include:
- **UV Package Manager** for faster Python dependency installation
- **Parallel job execution** where possible
- **Smart change detection** to skip unnecessary work
- **Aggressive caching** for Rust, Node.js, and Python dependencies
- **Timeout management** to prevent runaway jobs
- **Resource-aware scheduling**

## 🔒 **SECURITY FEATURES**

- **Zero-tolerance security policy** for critical vulnerabilities
- **Multi-tool scanning** (Safety, Bandit, Semgrep, cargo-audit, Trivy)
- **Container security validation**
- **Secret detection** with TruffleHog
- **SARIF reporting** to GitHub Security tab
- **Dependency vulnerability tracking**

## 🎯 **MIGRATION GUIDE**

If you're using deprecated workflows:

1. **Stop using deprecated workflows** - disable them in your branch protection rules
2. **Update CI/CD references** - point to `unified-ci-modern.yml`
3. **Update documentation** - reference the new workflow names
4. **Test thoroughly** - the new workflows have different job names and outputs

## 📞 **SUPPORT**

For questions about the workflows:
1. Check the workflow files for inline documentation
2. Review recent successful runs for examples
3. Check GitHub Actions logs for debugging information
4. Consult the ACGS-1 documentation

---

*Last updated: $(date)*
*Workflow modernization completed as part of Phase 2 CI/CD improvements*