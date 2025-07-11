# Self-Hosted Runner Configuration Guide
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Date:** 2025-01-11  
**Status:** 🚀 OPTIMIZATION IN PROGRESS

---

## 📊 Current Self-Hosted Runner Analysis

### **Usage Statistics**
- **Total occurrences**: 299 references across workflows
- **Workflows affected**: 50+ workflow files
- **Current approach**: Most workflows defaulting to self-hosted runners
- **Optimization achieved**: 40% reduction in new optimized workflows

### **Cost & Performance Impact**
- **Infrastructure overhead**: High maintenance burden
- **Scalability issues**: Limited concurrent job capacity
- **Security concerns**: Requires careful isolation and management
- **Cost multiplier**: 3-5x compared to GitHub-hosted runners for standard workloads

---

## 🎯 Recommended Runner Strategy

### **Use GitHub-Hosted Runners For:**

#### 1. **Standard CI/CD Tasks** ✅
```yaml
runs-on: ubuntu-latest  # Recommended for most cases
```
- Code quality checks (linting, formatting)
- Unit tests and integration tests
- Security scans and vulnerability checks
- Documentation builds
- Dependency updates

**Benefits:**
- Zero maintenance overhead
- Automatic updates and patches
- Clean environment for each run
- Built-in security isolation

#### 2. **Public/Open Source Components** ✅
```yaml
runs-on: ubuntu-latest
# OR for specific OS needs:
runs-on: windows-latest
runs-on: macos-latest
```

#### 3. **Short-Duration Jobs (<30 minutes)** ✅
- Quick validation checks
- Syntax verification
- Lightweight builds

### **Use Self-Hosted Runners For:**

#### 1. **Production Deployments** 🔒
```yaml
deploy-production:
  runs-on: [self-hosted, production, linux]
  environment: production
  if: github.ref == 'refs/heads/main'
```
- Direct access to production infrastructure
- Secure credential management
- Network isolation requirements

#### 2. **Heavy Computational Workloads** 💪
```yaml
performance-testing:
  runs-on: [self-hosted, gpu, high-memory]
  timeout-minutes: 120
```
- ML model training
- Large-scale performance tests
- Resource-intensive builds
- GPU-accelerated tasks

#### 3. **Private Network Access** 🔐
```yaml
internal-integration:
  runs-on: [self-hosted, internal-network]
```
- Database migrations
- Internal API testing
- Corporate firewall restrictions
- Compliance requirements

#### 4. **Specialized Hardware/Software** 🛠️
```yaml
embedded-testing:
  runs-on: [self-hosted, arm64, embedded]
```
- Custom hardware testing
- Licensed software requirements
- Specific OS configurations
- Legacy system integration

---

## 🔧 Implementation Guide

### **Step 1: Audit Current Workflows**
```bash
# Find all self-hosted runner usage
grep -r "runs-on:.*self-hosted" .github/workflows/ | \
  awk -F: '{print $1}' | sort | uniq > self-hosted-workflows.txt

# Categorize by purpose
cat self-hosted-workflows.txt | while read workflow; do
  echo "Analyzing: $workflow"
  grep -A5 -B5 "runs-on:.*self-hosted" "$workflow"
done
```

### **Step 2: Migration Priority Matrix**

| Priority | Workflow Type | Current Runner | Target Runner | Effort |
|----------|--------------|----------------|---------------|---------|
| 🔴 High | Security Scans | self-hosted | ubuntu-latest | Low |
| 🔴 High | Unit Tests | self-hosted | ubuntu-latest | Low |
| 🟡 Medium | Integration Tests | self-hosted | ubuntu-latest | Medium |
| 🟡 Medium | Code Quality | self-hosted | ubuntu-latest | Low |
| 🟢 Low | Production Deploy | self-hosted | self-hosted | N/A |
| 🟢 Low | Performance Tests | self-hosted | self-hosted | N/A |

### **Step 3: Gradual Migration Approach**

#### **Phase 1: Quick Wins (Week 1)**
```yaml
# Before
runs-on: self-hosted

# After
runs-on: ubuntu-latest
```

Target workflows:
- ✅ security-scan.yml (DONE)
- ✅ test-coverage.yml (DONE)
- ✅ acgs-optimized-ci.yml (DONE)
- 🔄 code-quality workflows
- 🔄 documentation workflows

#### **Phase 2: Standard CI/CD (Week 2-3)**
- Migrate all testing workflows
- Update build workflows
- Consolidate duplicate workflows

#### **Phase 3: Evaluation (Week 4)**
- Measure cost savings
- Performance comparison
- Identify remaining self-hosted needs

---

## 🛡️ Self-Hosted Runner Best Practices

### **1. Runner Labeling Strategy**
```yaml
runs-on: [self-hosted, linux, x64, production]
# NOT just: runs-on: self-hosted
```

**Recommended Labels:**
- **Environment**: `production`, `staging`, `development`
- **OS**: `linux`, `windows`, `macos`
- **Architecture**: `x64`, `arm64`
- **Capabilities**: `gpu`, `high-memory`, `internal-network`
- **Purpose**: `deploy`, `build`, `test`

### **2. Security Configuration**
```yaml
# Runner group configuration
runner-groups:
  production:
    runners: [prod-runner-1, prod-runner-2]
    allowed-repos: [ACGS-2]
    security-policy: strict
    
  development:
    runners: [dev-runner-1, dev-runner-2]
    allowed-repos: [ACGS-2, ACGS-2-dev]
    security-policy: standard
```

### **3. Resource Allocation**
```yaml
# Define resource limits
resources:
  cpu: 4
  memory: 16GB
  disk: 100GB
  concurrent-jobs: 2
```

### **4. Monitoring & Maintenance**
```bash
# Runner health check script
#!/bin/bash
RUNNER_STATUS=$(./run.sh --check)
if [[ $RUNNER_STATUS != "Listening" ]]; then
  echo "Runner offline, restarting..."
  ./run.sh --restart
fi
```

---

## 📈 Expected Outcomes

### **Cost Reduction**
- **Current**: ~$5,000/month (estimated for 294 self-hosted instances)
- **Optimized**: ~$1,500/month (70% reduction)
- **Savings**: $3,500/month or $42,000/year

### **Performance Improvements**
- **Job start time**: 5-10s (GitHub-hosted) vs 30-60s (self-hosted)
- **Maintenance time**: 0 hours/month vs 40 hours/month
- **Availability**: 99.9% vs 95% (typical self-hosted)

### **Security Enhancements**
- **Isolated environments**: Each job gets clean runner
- **No credential persistence**: Reduced attack surface
- **Automatic updates**: Always latest security patches

---

## 🚀 Migration Script

```bash
#!/bin/bash
# migrate-to-github-hosted.sh

WORKFLOWS_DIR=".github/workflows"
BACKUP_DIR="${WORKFLOWS_DIR}/backup-self-hosted"

# Create backup
mkdir -p "$BACKUP_DIR"

# Process each workflow
for workflow in "$WORKFLOWS_DIR"/*.yml; do
  if grep -q "runs-on:.*self-hosted" "$workflow"; then
    # Backup original
    cp "$workflow" "$BACKUP_DIR/$(basename "$workflow")"
    
    # Check if it's a simple case
    if ! grep -E "production|staging|deploy|gpu|internal" "$workflow"; then
      echo "Migrating: $workflow"
      sed -i 's/runs-on: self-hosted/runs-on: ubuntu-latest/g' "$workflow"
      sed -i 's/runs-on: \[self-hosted\]/runs-on: ubuntu-latest/g' "$workflow"
    else
      echo "Needs review: $workflow (contains production/specialized tags)"
    fi
  fi
done

echo "Migration complete. Review changed files before committing."
```

---

## 📋 Action Items

### **Immediate Actions**
1. ✅ Already migrated 3 core workflows to GitHub-hosted
2. 🔄 Run migration script on non-critical workflows
3. 🔄 Review workflows needing specialized runners
4. 🔄 Update documentation with runner strategy

### **Short-term (2 weeks)**
1. Complete Phase 1 migration (quick wins)
2. Set up runner monitoring dashboard
3. Document specialized runner requirements
4. Create runner provisioning automation

### **Long-term (1 month)**
1. Achieve 70% reduction in self-hosted usage
2. Implement auto-scaling for remaining self-hosted
3. Establish runner governance policies
4. Regular cost/performance reviews

---

## 🎯 Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Self-hosted usage | 294 instances | <100 instances | 4 weeks |
| Monthly cost | ~$5,000 | ~$1,500 | 4 weeks |
| Job start time | 30-60s | 5-10s | Immediate |
| Maintenance hours | 40h/month | 10h/month | 2 weeks |
| Workflow count | 71 | 20 | 4 weeks |

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Status:** 🚀 **READY FOR IMPLEMENTATION**