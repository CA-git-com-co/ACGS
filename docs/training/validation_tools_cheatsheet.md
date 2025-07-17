# ACGS Validation Tools Cheat Sheet

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Quick Reference**: Essential commands for ACGS documentation validation
**Constitutional Hash**: `cdd01ef066bc6cf2`

## Quick Validation Script

### Command
```bash
./tools/validation/quick_validation.sh
```

### What it checks
- ✅ Constitutional hash consistency (target: 100%)
- ✅ Port configuration alignment
- ✅ Performance targets consistency
- ✅ Documentation completeness
- ✅ Service status documentation
- ✅ Service configuration alignment (Docker Compose, Kubernetes, config files)
- ✅ Cross-reference validation using PATTERN_REGISTRY

### Expected Output
```
🚀 ACGS Documentation Quick Validation
======================================
✅ Constitutional hash found in 109 documentation files
✅ All critical validation checks PASSED!
```

### Common Issues
- ❌ Constitutional hash missing → Add to files
- ❌ Port mapping incorrect → Check docker-compose.acgs.yml
- ⚠️ Performance targets missing → Add to documentation

## Quarterly Audit Script

### Command
```bash
./tools/audit/quarterly_audit.sh
```

### What it audits
- Infrastructure alignment (PostgreSQL 5439, Redis 6389, Auth 8016, Constitutional AI 8001, Integrity 8002, Formal Verification 8003, Governance Synthesis 8004, Policy Governance 8005, Evolutionary Computation 8006, Consensus Engine 8007, Multi-Agent Coordinator 8008, Worker Agents 8009, Blackboard Service 8010, Code Analysis Service 8011, Context Service 8012)
- Service API documentation accuracy
- Cross-reference validation
- Performance metrics consistency
- Constitutional compliance verification

### Output Location
```
audit_reports/quarterly_audit_Q3_2025_YYYYMMDD.md
```

### Score Interpretation
- **≥95%**: 🟢 EXCELLENT
- **85-94%**: 🟡 GOOD
- **70-84%**: 🟠 NEEDS IMPROVEMENT
- **<70%**: 🔴 CRITICAL

## Daily Metrics Collection

### Command
```bash
./tools/metrics/collect_daily_metrics.sh
```

### Metrics Collected
1. **Constitutional Compliance**: 100% target
2. **Link Validity**: 100% target
3. **Documentation Freshness**: 85% target
4. **Documentation Coverage**: 80% target
5. **Overall Quality Score**: 85% target

### Output Files
```
metrics/daily_metrics_YYYY-MM-DD.json
metrics/latest_metrics.json (symlink)
```

### Sample Output
```
📊 Summary:
  Constitutional Compliance: 100% (Target: 100%)
  Link Validity: 100% (Target: 100%)
  Documentation Freshness: 100% (Target: 85%)
  Documentation Coverage: 100% (Target: 80%)
  Overall Quality Score: 100%
  Status: EXCELLENT
```

## Quality Alert Monitor

### Command
```bash
python tools/monitoring/quality_alert_monitor.py
```

### Alert Thresholds
- **Constitutional Compliance**: <100% → 🚨 CRITICAL
- **Link Validity**: <100% → ⚠️ HIGH
- **Documentation Freshness**: <85% → 📋 MEDIUM
- **Documentation Coverage**: <80% → 📋 MEDIUM
- **Overall Quality**: <85% → Variable severity

### Output
```
metrics/quality_alert_YYYY-MM-DD.md
```

### Exit Codes
- `0`: All metrics within acceptable ranges
- `1`: High priority issues detected
- `2`: Critical issues require immediate attention

## GitHub Actions Workflows

### Daily Metrics Collection
**File**: `.github/workflows/daily-metrics-collection.yml`
**Schedule**: Daily at 1 AM UTC
**Trigger**: `workflow_dispatch` for manual runs

### Documentation Validation
**Runs on**: Pull requests
**Validates**: Constitutional compliance, standards

## Common Validation Workflows

### Before Committing
```bash
# 1. Quick validation
./tools/validation/quick_validation.sh

# 2. Check specific file
grep -q "cdd01ef066bc6cf2" docs/new-file.md && echo "✅" || echo "❌"

# 3. Collect metrics
./tools/metrics/collect_daily_metrics.sh
```

### Weekly Quality Check
```bash
# 1. Run quarterly audit
./tools/audit/quarterly_audit.sh

# 2. Generate quality alert
python tools/monitoring/quality_alert_monitor.py

# 3. Review reports
ls -la audit_reports/
ls -la metrics/
```

### Troubleshooting Issues

#### Constitutional Compliance Failure
```bash
# Find files missing hash
find docs/ -name "*.md" -exec grep -L "cdd01ef066bc6cf2" {} \;

# Add hash to file
echo "<!-- Constitutional Hash: cdd01ef066bc6cf2 -->" >> docs/file.md

# Verify fix
./tools/validation/quick_validation.sh
```

#### Link Validation Failure
```bash
# Check for broken links manually
# find docs/ -name "*.md" -exec grep -H "\[.*\](.*\.md" {} \;

# Validate specific file links
# Validate specific file links (command disabled)
```

##
## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets Missing
```bash
# Search for performance targets in docs
grep -r "≥100.*RPS\|≤5ms\|≥85%.*cache\|≥80%.*coverage" docs/

# Add missing targets to documentation
```

## Advanced Validation Tools

### Service Configuration Alignment Validator

#### Command
```bash
python tools/validation/service_config_alignment_validator.py [--repo-root PATH] [--output REPORT] [--json]
```

#### What it validates
- ✅ Port consistency across Docker Compose, Kubernetes, and code
- ✅ Image tag alignment between configurations
- ✅ Environment variable consistency
- ✅ API documentation URL patterns
- ✅ Constitutional compliance across all config files

#### Sample Output
```
📊 Service Configuration Alignment Summary:
  Total Checks: 5
  Passed: 4
  Failed: 1
  Success Rate: 80.0%
  Duration: 1.23s
  Performance Score: 89.2/100
```

### Cross-Reference Analysis Tool

#### Command
```bash
python tools/validation/advanced_cross_reference_analyzer.py [--output-dir REPORTS]
```

#### Capabilities
- 🔍 **Pattern-Based Link Detection**: Uses extensible PATTERN_REGISTRY
- 🔗 **Broken Link Detection**: Identifies and suggests fixes for broken references
- 📋 **Semantic Relationship Analysis**: Detects related documents based on content
- 🎯 **Confidence Scoring**: Prioritizes issues based on link quality and context
- 📊 **Comprehensive Reporting**: Detailed analysis with actionable recommendations

#### Pattern Registry (PATTERN_REGISTRY)

Location: `tools/validation/cross_reference_patterns.yaml`

**Supported Pattern Categories:**
- `markdown_links`: Standard markdown link formats
- `code_references`: Import statements and file references  
- `configuration_references`: YAML/JSON config file references
- `semantic_relationships`: Context-based semantic relationships
- `image_media`: Image and media file references

**Adding New Validation Rules:**

1. **Edit Pattern Registry**:
   ```yaml
   patterns:
     - name: "custom_pattern"
       category: "code_references"
       regex: "your_regex_pattern_here"
       capture_groups:
         text: 1
         url: 2
       reference_type: "custom"
       confidence_modifiers:
         descriptive_text: 0.2
   ```

2. **Test New Pattern**:
   ```bash
   python tools/validation/advanced_cross_reference_analyzer.py --test-pattern "custom_pattern"
   ```

3. **Validate Changes**:
   ```bash
   ./tools/validation/quick_validation.sh
   ```

### PATTERN_REGISTRY Configuration

#### Core Pattern Structure
```yaml
patterns:
  - name: "pattern_identifier"           # Unique pattern name
    category: "pattern_category"          # Category for organization
    regex: "regex_pattern"               # Pattern to match
    capture_groups:                      # Named capture groups
      text: 1                           # Group for link text
      url: 2                            # Group for URL/path
    reference_type: "type"               # Classification type
    confidence_modifiers:                # Score adjustments
      descriptive_text: 0.2             # Boost for descriptive text
      generic_text: -0.3                # Penalty for generic text
    exclusions:                         # Patterns to exclude
      - "^https?://"                    # External URLs
      - "^mailto:"                      # Email links
```

#### Confidence Scoring System
- **Base Confidence**: Set per category (0.6-0.9)
- **Text Quality Modifiers**: 
  - Descriptive text: +0.2
  - Generic terms ("here", "link"): -0.3
  - Action terms ("see", "refer"): +0.1
- **Context Modifiers**:
  - Structured context: +0.1
  - Code blocks: +0.2
  - Documentation sections: +0.15

#### Built-in Pattern Examples

**Markdown Links:**
```yaml
regex: "\\[([^\\]]+)\\]\\(([^)]+)\\)"
capture_groups:
  text: 1
  url: 2
```

**Code Imports:**
```yaml
regex: "(?:import|from)\\s+[\"']([^\"']+)[\"']"
capture_groups:
  module_path: 1
```

**API Endpoints:**
```yaml
regex: "(?:GET|POST|PUT|DELETE|PATCH)\\s+(/api/[^\\s\\n]+)"
capture_groups:
  endpoint: 1
```

## Related Information

For a comprehensive overview of the documentation implementation and the services validated by these tools, refer to:

- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [Service Configuration Alignment Guide](../validation/SERVICE_CONFIG_ALIGNMENT.md)

## Emergency Procedures

### Critical Quality Failure
1. **Stop**: Don't commit/deploy
2. **Assess**: Run all validation tools
3. **Fix**: Address critical issues first
4. **Validate**: Re-run tools to confirm fixes
5. **Escalate**: Contact Documentation Team Lead

### Constitutional Compliance Emergency
1. **Immediate**: Add constitutional hash to all missing files
2. **Validate**: Run quick validation script
3. **Verify**: Ensure 100% compliance
4. **Report**: Notify Security Team
5. **Document**: Record incident and resolution

## Tool Locations

```
tools/
├── validation/
│   └── quick_validation.sh
├── audit/
│   └── quarterly_audit.sh
├── metrics/
│   └── collect_daily_metrics.sh
└── monitoring/
    └── quality_alert_monitor.py
```


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets Reference

| Metric | Target | Critical Threshold |
|--------|--------|--------------------|
| Latency (P99) | ≤5ms | >10ms |
| Throughput | ≥100 RPS | <50 RPS |
| Cache Hit Rate | ≥85% | <70% |
| Test Coverage | ≥80% | <60% |
| Availability | 99.9% | <99% |

---

**Quick Help**: Run any tool with `--help` or `-h` for usage information
**Constitutional Hash**: `cdd01ef066bc6cf2` ✅
