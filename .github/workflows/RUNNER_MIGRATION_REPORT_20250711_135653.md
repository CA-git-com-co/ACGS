# GitHub Actions Runner Migration Report
**Date:** 2025-07-11 13:56:53
**Constitutional Hash:** `cdd01ef066bc6cf2`

## 📊 Summary
- **Total workflows analyzed:** 72
- **Workflows migrated:** 0
- **Workflows skipped:** 0
- **Errors encountered:** 0
- **Total self-hosted instances:** 289
- **Total GitHub-hosted instances:** 14

## ✅ Workflows Migrated
These workflows were successfully migrated to GitHub-hosted runners:

- **robust-connectivity-check.yml** (1 instances)
- **validation-full.yml** (4 instances)
- **enhanced-parallel-ci.yml** (4 instances)
- **acgs-e2e-testing.yml** (3 instances)
- **advanced-caching.yml** (6 instances)
- **quality-gates.yml** (1 instances)
- **solana-anchor.yml** (5 instances)
- **acgs-performance-monitoring.yml** (5 instances)
- **fixed-connectivity-check.yml** (1 instances)
- **testing.yml** (3 instances)
- **pr-documentation-validation.yml** (1 instances)
- **continuous-security-scanning.yml** (2 instances)
- **comprehensive-testing.yml** (8 instances)
- **daily-metrics-collection.yml** (1 instances)
- **cost-monitoring.yml** (1 instances)
- **cicd-monitoring.yml** (1 instances)
- **ci_cd_20250701_000659.yml** (3 instances)
- **quarterly-security-review.yml** (1 instances)

## 🔒 Workflows Keeping Self-Hosted Runners
These workflows require self-hosted runners due to specialized requirements:

- **dependency-monitoring.yml** (4 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **deployment-automation.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **documentation-quality.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **e2e-tests.yml** (10 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **cross-reference-validation.yml** (7 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **unified-ci.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **ci.yml** (9 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **database-migration.yml** (4 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **unified-ci-optimized.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **security-focused.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **enterprise-parallel-jobs.yml** (8 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **acgs-ci-cd.yml** (2 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **quality-assurance.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **documentation-automation.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **deployment-modern.yml** (4 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **docker-build-push.yml** (2 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **documentation-validation.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **enterprise-ci.yml** (10 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **pr-documentation-check.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **claude-code-review.yml** (2 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **workflow-coordinator.yml** (4 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **workflow-config-validation.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **deployment-validation.yml** (3 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **test.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **optimized-ci.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **security-automation.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **unified-ci-modern.yml** (7 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **quarterly-audit.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **api-versioning-ci.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **performance-benchmarking.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **secret-scanning.yml** (2 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **production-deploy.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **performance-monitoring.yml** (3 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **security-scanning.yml** (5 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **security-comprehensive.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **ci-legacy.yml** (10 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **ci-uv.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **setup-environments.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **acgs-comprehensive-testing.yml** (7 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **acgs_comprehensive_ci.yml** (8 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **image-build.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **staging-deployment.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **api-compatibility-matrix.yml** (3 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **production-deployment.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **promotion-gates.yml** (7 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **dependency-update.yml** (1 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **test-automation-enhanced.yml** (7 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **cost-optimized-ci.yml** (6 instances)
  - Keep self-hosted: Contains production/specialized requirements
- **security-updates.yml** (2 instances)
  - Keep self-hosted: Contains production/specialized requirements

## 💰 Cost Impact Estimation
- **Current self-hosted cost:** $4,913.00/month
- **New self-hosted cost:** $4,913.00/month
- **GitHub-hosted cost:** $0.00/month
- **Estimated savings:** $0.00/month

## 🎯 Recommendations

1. **Review migrated workflows** in the next CI/CD run
2. **Monitor performance** differences between runner types
3. **Update documentation** with new runner strategy
4. **Consider caching** strategies for GitHub-hosted runners
5. **Set up alerts** for workflow failures during transition
