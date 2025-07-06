# ACGS-1 Branch Protection Configuration Guide

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


Since branch protection is currently disabled on this repository, here's a comprehensive guide for setting up proper branch protection rules when it's enabled.

## 🛡️ **Recommended Branch Protection Settings**

### **Master/Main Branch (Production)**
Configure the following protection rules for the production branch:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required checks:**
  - `quality-gates` (from unified-ci-modern.yml)
  - `security-summary` (from security-focused.yml) 
  - `blockchain-validation` (from unified-ci-modern.yml)
  - `container-security` (from unified-ci-modern.yml)

#### Pull Request Reviews
- ✅ **Require pull request reviews before merging**
- **Required approving reviews:** `2`
- ✅ **Dismiss stale reviews when new commits are pushed**
- ✅ **Require review from code owners**
- ✅ **Require approval of the most recent reviewable push**

#### Additional Settings
- ❌ **Allow force pushes** (disabled for security)
- ❌ **Allow deletions** (disabled for safety)
- ⚠️ **Do not allow bypassing the above settings** (optional for admins)

### **Develop Branch (Staging)**
Configure the following protection rules for the development branch:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required checks:**
  - `quality-gates` (from unified-ci-modern.yml)
  - `security-summary` (from security-focused.yml)

#### Pull Request Reviews
- ✅ **Require pull request reviews before merging**
- **Required approving reviews:** `1`
- ✅ **Dismiss stale reviews when new commits are pushed**

### **Feature Branches**
For feature branches, minimal protection:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- **Required checks:**
  - `quality-gates` (from unified-ci-modern.yml)

## 🔧 **Setup Instructions**

### Step 1: Enable Branch Protection
1. Go to **Settings** → **Branches** in your GitHub repository
2. Click **Add rule** to create a new protection rule
3. Enter the branch name pattern (e.g., `master`, `main`, `develop`)

### Step 2: Configure Status Checks
Add the following workflow job names as required status checks:

#### Primary Workflows (Always Required)
```
quality-gates                 # From unified-ci-modern.yml
security-summary             # From security-focused.yml
```

#### Additional Checks (Production Only)
```
blockchain-validation        # From unified-ci-modern.yml  
container-security          # From unified-ci-modern.yml
integration-tests           # From unified-ci-modern.yml
```

### Step 3: Set Up Code Owners
Create a `.github/CODEOWNERS` file with the following content:

```
# ACGS-1 Code Owners
* @acgs-team

# GitHub Actions workflows
.github/workflows/ @acgs-devops @acgs-security

# Security-related files  
/security/ @acgs-security
SECURITY*.md @acgs-security

# Blockchain and smart contracts
/blockchain/ @acgs-blockchain @acgs-security

# Core services
/services/core/ @acgs-core-team

# Infrastructure and deployment
/infrastructure/ @acgs-devops
docker-compose*.yml @acgs-devops

# Configuration and secrets
/config/ @acgs-security @acgs-devops
*requirements*.txt @acgs-security
```

## ⚠️ **Legacy Workflow Cleanup**

**Remove these legacy workflow requirements** if they exist:
- `ci-legacy.yml`
- `security-comprehensive.yml` 
- `enhanced-parallel-ci.yml`
- `cost-optimized-ci.yml`
- `optimized-ci.yml`

## 🚀 **Modern Workflow Names**

**Use these modern workflow job names** as required status checks:

### From `unified-ci-modern.yml`:
- `preflight` - Change detection and environment setup
- `quality-gates` - Code quality and security validation
- `blockchain-validation` - Rust/Solana program validation  
- `container-security` - Container and infrastructure security
- `integration-tests` - End-to-end testing
- `deployment` - Multi-environment deployment

### From `security-focused.yml`:
- `security-triage` - Security scan scope determination
- `python-security` - Python dependency and code security
- `rust-security` - Rust/blockchain security validation
- `container-security` - Container vulnerability scanning
- `security-summary` - Comprehensive security reporting

### From `deployment-modern.yml`:
- `pre-deployment` - Deployment validation and configuration
- `image-operations` - Container image build and registry
- `deployment-execution` - Environment-specific deployment
- `post-deployment` - Deployment verification and reporting

## 📊 **Verification Checklist**

After setting up branch protection, verify:

- [ ] Required status checks are configured for each branch
- [ ] Pull request reviews are required with appropriate counts
- [ ] Code owner reviews are enabled for critical branches
- [ ] Force pushes and deletions are disabled
- [ ] Legacy workflow requirements are removed
- [ ] Modern workflow names are used as status checks
- [ ] CODEOWNERS file is properly configured

## 🔒 **Security Benefits**

Proper branch protection provides:

✅ **Code Quality Assurance** - No code merges without passing quality gates
✅ **Security Validation** - All code scanned for vulnerabilities before merge
✅ **Peer Review** - Human oversight for all changes
✅ **Deployment Safety** - Controlled releases to different environments
✅ **Audit Trail** - Complete history of who approved what changes
✅ **Compliance** - Meets enterprise governance requirements

## 🚨 **Emergency Procedures**

In case of critical hotfixes:

1. **Create hotfix branch** from master/main
2. **Apply minimal fix** addressing only the critical issue
3. **Request emergency review** from designated emergency reviewers
4. **Temporary bypass** (admin only) if absolutely necessary
5. **Full retrospective** after emergency resolution

## 📞 **Support**

For questions about branch protection setup:
1. Review GitHub's branch protection documentation
2. Check the workflow status in Actions tab
3. Verify required status check names match job names
4. Consult with DevOps team for complex configurations

---

*This guide ensures enterprise-grade protection for the ACGS-1 repository while maintaining development velocity and security standards.*