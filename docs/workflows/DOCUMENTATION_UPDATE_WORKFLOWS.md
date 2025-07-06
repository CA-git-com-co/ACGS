# ACGS Documentation Update Workflows

**Date**: 2025-07-05
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Status**: Production Ready

## 🎯 Overview

This document defines specific workflows for updating ACGS documentation when services, configurations, or performance targets change. Each workflow ensures constitutional compliance and maintains documentation-implementation synchronization.

## 🔧 Service Configuration Changes Workflow

### Trigger Events
- Port number changes
- Environment variable modifications
- Service dependency updates
- Database connection changes
- Redis configuration updates

### Required Actions

#### 1. Pre-Change Assessment
```bash
# Document current state
./tools/validation/quick_validation.sh > pre_change_validation.log

# Identify affected documentation
grep -r "old_port_number" docs/
grep -r "old_config_value" docs/
```

#### 2. Implementation Steps
1. **Update Infrastructure Configuration**
   - Modify `infrastructure/docker/docker-compose.acgs.yml`
   - Ensure constitutional hash `cdd01ef066bc6cf2` is preserved
   - Update port mappings and environment variables

2. **Update Documentation Files**
   - `docs/configuration/README.md` - Configuration specifications
   - `README.md` - Quick start instructions
   - `docs/operations/SERVICE_STATUS.md` - Service endpoints
   - `docs/api/index.md` - API base URLs

3. **Validation and Testing**
   ```bash
   # Validate configuration consistency
   ./tools/validation/quick_validation.sh

   # Test deployment with new configuration
   docker-compose -f infrastructure/docker/docker-compose.acgs.yml down
   docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d

   # Verify service health
   curl http://localhost:NEW_PORT/health
   ```

#### 3. Documentation Update Checklist
- [ ] Port numbers updated in all documentation files
- [ ] Environment variables documented with correct values
- [ ] Constitutional hash `cdd01ef066bc6cf2` maintained
- [ ] Service URLs updated in API documentation
- [ ] Health check endpoints verified
- [ ] Deployment procedures tested

## 🚀 Performance Target Changes Workflow

### Trigger Events
- SLA modifications
- Performance requirement updates
- Monitoring threshold changes
- Capacity planning adjustments

### Required Actions

#### 1. Performance Analysis
```bash
# Document current performance metrics
curl http://localhost:8016/metrics > current_metrics.json
curl http://localhost:8001/health > current_health.json

# Analyze performance trends
grep -r "≥.*RPS\|≤.*ms\|≥.*%" docs/ > current_targets.txt
```

#### 2. Synchronized Updates
1. **Update Performance Documentation**
   - `README.md` - Performance targets section
   - `docs/configuration/README.md` - Performance configuration
   - `docs/operations/SERVICE_STATUS.md` - Current metrics and targets

2. **Update Monitoring Configuration**
   - Alerting thresholds
   - Dashboard configurations
   - SLA definitions

3. **Update Validation Scripts**
   - `tools/validation/quick_validation.sh`
   - `.github/workflows/documentation-validation.yml`

#### 3. Performance Update Checklist
- [ ] All performance targets updated consistently
- [ ] Monitoring thresholds aligned with new targets
- [ ] Validation scripts updated with new criteria
- [ ] Documentation reflects achievable targets
- [ ] Constitutional compliance maintained

## 🔌 API Changes Workflow

### Trigger Events
- New API endpoints
- Request/response format changes
- Authentication modifications
- Error response updates

### Required Actions

#### 1. API Documentation Updates
1. **Update Service-Specific Documentation**
   - `docs/api/[service-name].md` - Endpoint specifications
   - Add constitutional hash to all response examples
   - Update request/response schemas

2. **Update API Index**
   - `docs/api/index.md` - Service catalog
   - Add new endpoints to overview
   - Update service descriptions

#### 2. Example Updates
```yaml
# Ensure all API examples include constitutional hash
{
  "status": "success",
  "data": {...},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### 3. API Update Checklist
- [ ] All new endpoints documented
- [ ] Request/response examples updated
- [ ] Constitutional hash in all response examples
- [ ] Authentication requirements documented
- [ ] Error responses documented
- [ ] Integration examples provided

## 🏗️ Infrastructure Changes Workflow

### Trigger Events
- Docker image updates
- Container orchestration changes
- Network configuration modifications
- Storage configuration updates

### Required Actions

#### 1. Infrastructure Documentation Updates
1. **Update Deployment Documentation**
   - `docs/deployment/` - Deployment procedures
   - `README.md` - Infrastructure requirements
   - `docs/configuration/README.md` - System requirements

2. **Update Operational Documentation**
   - `docs/operations/SERVICE_STATUS.md` - Service health
   - `docs/operations/SERVICE_ISSUE_RESOLUTION_GUIDE.md` - Troubleshooting

#### 2. Infrastructure Update Checklist
- [ ] Deployment procedures updated and tested
- [ ] System requirements documented
- [ ] Troubleshooting guides updated
- [ ] Health check procedures verified
- [ ] Rollback procedures documented

## 📊 Monitoring and Alerting Changes Workflow

### Trigger Events
- New monitoring metrics
- Alert threshold modifications
- Dashboard updates
- Log format changes

### Required Actions

#### 1. Monitoring Documentation Updates
1. **Update Operations Documentation**
   - `docs/operations/SERVICE_STATUS.md` - Monitoring information
   - `docs/operations/MONITORING_GUIDE.md` - Monitoring procedures

2. **Update Troubleshooting Guides**
   - Alert response procedures
   - Escalation procedures
   - Metric interpretation guides

#### 2. Monitoring Update Checklist
- [ ] New metrics documented
- [ ] Alert thresholds documented
- [ ] Response procedures updated
- [ ] Dashboard configurations documented
- [ ] Log analysis procedures updated

## 🔄 Automated Workflow Integration

### GitHub Actions Integration

#### 1. Pre-commit Validation
```yaml
# .github/workflows/documentation-validation.yml
- name: Validate Documentation Changes
  run: |
    ./tools/validation/quick_validation.sh
    if [ $? -ne 0 ]; then
      echo "Documentation validation failed"
      exit 1
    fi
```

#### 2. PR Documentation Requirements
```yaml
# .github/workflows/pr-documentation-check.yml
- name: Check Documentation Updates
  run: |
    # Check if infrastructure changes require doc updates
    if git diff --name-only origin/main...HEAD | grep -q "infrastructure/"; then
      if ! git diff --name-only origin/main...HEAD | grep -q "docs/"; then
        echo "Infrastructure changes require documentation updates"
        exit 1
      fi
    fi
```

### Automated Notifications

#### 1. Slack Integration
```bash
# Send notification when documentation is updated
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"📚 ACGS Documentation Updated: Constitutional Hash cdd01ef066bc6cf2 validated"}' \
  $SLACK_WEBHOOK_URL
```

#### 2. GitHub Issue Creation
```bash
# Create issue for missing documentation
gh issue create \
  --title "Documentation Update Required" \
  --body "Constitutional hash validation required for recent changes" \
  --label "documentation,constitutional-compliance"
```

## 📋 Workflow Execution Templates

### Service Configuration Change Template
```bash
#!/bin/bash
# Service Configuration Change Workflow

echo "🔧 Starting service configuration change workflow..."
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Pre-change validation
./tools/validation/quick_validation.sh

# 2. Update configuration
# [Manual step: Update infrastructure/docker/docker-compose.acgs.yml]

# 3. Update documentation
# [Manual step: Update docs/configuration/README.md]
# [Manual step: Update README.md]
# [Manual step: Update docs/operations/SERVICE_STATUS.md]

# 4. Post-change validation
./tools/validation/quick_validation.sh

# 5. Test deployment
docker-compose -f infrastructure/docker/docker-compose.acgs.yml down
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d

echo "✅ Service configuration change workflow completed"
```

### Performance Target Change Template
```bash
#!/bin/bash
# Performance Target Change Workflow

echo "📊 Starting performance target change workflow..."
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Document current targets
grep -r "≥.*RPS\|≤.*ms\|≥.*%" docs/ > current_targets.backup

# 2. Update all performance documentation
# [Manual step: Update README.md performance section]
# [Manual step: Update docs/configuration/README.md]
# [Manual step: Update docs/operations/SERVICE_STATUS.md]

# 3. Validate consistency
./tools/validation/quick_validation.sh

# 4. Update monitoring
# [Manual step: Update alerting thresholds]

echo "✅ Performance target change workflow completed"
```

## 🎯 Success Criteria

### Workflow Completion Criteria
- [ ] All affected documentation files updated
- [ ] Constitutional hash `cdd01ef066bc6cf2` consistency maintained
- [ ] Validation scripts pass successfully
- [ ] Deployment procedures tested and verified
- [ ] Team notifications sent
- [ ] Changes reviewed and approved

### Quality Assurance
- [ ] Documentation accuracy verified
- [ ] Links and references validated
- [ ] Examples tested and working
- [ ] Performance targets achievable
- [ ] Security requirements maintained

---

<!-- Constitutional Hash: cdd01ef066bc6cf2 --> ✅
**Next Review**: 2025-08-05
**Owner**: Documentation Team
