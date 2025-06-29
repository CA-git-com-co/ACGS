#!/bin/bash
# OPA Policy Bundle Build Script for ACGS-1 Lite
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🔧 Building ACGS-1 Lite OPA Policy Bundle"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "========================================"

# Configuration
BUNDLE_NAME="acgs-constitutional-policies"
VERSION="1.0.0"
OUTPUT_DIR="build"
BUNDLE_FILE="${BUNDLE_NAME}-${VERSION}.tar.gz"

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if OPA is available
if ! command -v opa &> /dev/null; then
    echo "❌ OPA is not installed or not in PATH"
    echo "💡 Install OPA: https://www.openpolicyagent.org/docs/latest/get-started/"
    exit 1
fi

echo "✅ OPA found: $(opa version)"

# Create output directory
echo "📁 Creating output directory..."
rm -rf ${OUTPUT_DIR}
mkdir -p ${OUTPUT_DIR}

# Validate policies
echo "🔍 Validating policy syntax..."

# Check main policy
echo "   Validating main.rego..."
opa fmt --diff main.rego || (echo "❌ main.rego format issues" && exit 1)

# Check constitutional policies
echo "   Validating constitutional policies..."
opa fmt --diff constitutional/core_principles.rego || (echo "❌ core_principles.rego format issues" && exit 1)
opa fmt --diff constitutional/safety_rules.rego || (echo "❌ safety_rules.rego format issues" && exit 1)

# Check evolution policies
echo "   Validating evolution policies..."
opa fmt --diff evolution/approval_rules.rego || (echo "❌ approval_rules.rego format issues" && exit 1)

# Check data policies
echo "   Validating data policies..."
opa fmt --diff data/privacy_rules.rego || (echo "❌ privacy_rules.rego format issues" && exit 1)

echo "✅ All policies validated"

# Run tests
echo "🧪 Running policy tests..."

# Constitutional tests
echo "   Running constitutional tests..."
opa test tests/constitutional_test.rego constitutional/ main.rego -v || (echo "❌ Constitutional tests failed" && exit 1)

# Evolution tests
echo "   Running evolution tests..."
opa test tests/evolution_test.rego evolution/ main.rego -v || (echo "❌ Evolution tests failed" && exit 1)

# Data privacy tests
echo "   Running data privacy tests..."
opa test tests/data_privacy_test.rego data/ main.rego -v || (echo "❌ Data privacy tests failed" && exit 1)

echo "✅ All tests passed"

# Build optimized bundle
echo "📦 Building optimized policy bundle..."

opa build \
    --bundle . \
    --output ${OUTPUT_DIR}/${BUNDLE_FILE} \
    --optimize 2 \
    --entrypoints acgs/main/decision \
    --entrypoints acgs/main/allow \
    --entrypoints acgs/main/health

if [ $? -ne 0 ]; then
    echo "❌ Bundle build failed"
    exit 1
fi

echo "✅ Bundle built successfully"

# Generate bundle metadata
echo "📋 Generating bundle metadata..."

cat > ${OUTPUT_DIR}/bundle-metadata.json << EOF
{
  "name": "${BUNDLE_NAME}",
  "version": "${VERSION}",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "build_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "policies": {
    "constitutional": {
      "core_principles": "Core constitutional principles and safety rules",
      "safety_rules": "Enhanced safety evaluation and pattern detection"
    },
    "evolution": {
      "approval_rules": "Evolution approval workflows and risk assessment"
    },
    "data": {
      "privacy_rules": "Data access control and privacy protection"
    }
  },
  "entry_points": [
    "acgs/main/decision",
    "acgs/main/allow", 
    "acgs/main/health"
  ],
  "optimization_level": 2,
  "test_coverage": {
    "constitutional_tests": "$(opa test tests/constitutional_test.rego constitutional/ main.rego --count 2>/dev/null | grep -o '[0-9]* tests' || echo 'N/A')",
    "evolution_tests": "$(opa test tests/evolution_test.rego evolution/ main.rego --count 2>/dev/null | grep -o '[0-9]* tests' || echo 'N/A')",
    "data_privacy_tests": "$(opa test tests/data_privacy_test.rego data/ main.rego --count 2>/dev/null | grep -o '[0-9]* tests' || echo 'N/A')"
  }
}
EOF

# Generate performance benchmark
echo "⚡ Running performance benchmark..."

BENCHMARK_RESULT=$(opa bench \
    --data <(echo '{}') \
    --input <(echo '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"test","explanation":"Performance benchmark test"}}') \
    'data.acgs.main.decision' \
    --count 1000 2>/dev/null | tail -1 || echo "N/A")

cat > ${OUTPUT_DIR}/performance-benchmark.json << EOF
{
  "benchmark_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "test_iterations": 1000,
  "benchmark_result": "${BENCHMARK_RESULT}",
  "target_latency": "< 1ms P99",
  "test_input": {
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public"
  }
}
EOF

# Generate policy documentation
echo "📚 Generating policy documentation..."

cat > ${OUTPUT_DIR}/policy-documentation.md << 'EOF'
# ACGS-1 Lite Constitutional Policies Documentation

## Overview

This bundle contains comprehensive constitutional policies for the ACGS-1 Lite governance system.

## Policy Modules

### Constitutional (`acgs.constitutional`)
- **Core Principles**: Autonomy, beneficence, non-maleficence, transparency, fairness, privacy, accountability
- **Safety Rules**: Critical safety patterns, behavioral analysis, isolation requirements
- **Resource Limits**: CPU, memory, disk, network, execution time constraints

### Evolution (`acgs.evolution`)  
- **Approval Rules**: Auto-approval (≥95%), fast-track (90-95%), human review (<90%)
- **Risk Assessment**: Base risk levels, risk factors, mitigation factors
- **Rollback Requirements**: Plan completeness, testing, automation

### Data Privacy (`acgs.data`)
- **Classification Control**: Public (0) to Top Secret (4) clearance levels
- **Consent Management**: User consent verification, purpose limitation, expiration
- **Data Minimization**: Excessive data detection, bulk access patterns
- **Encryption Requirements**: Algorithm strength, key management, sensitive data protection

## Entry Points

- `acgs/main/decision` - Main policy decision with full context
- `acgs/main/allow` - Simple boolean allow/deny
- `acgs/main/health` - Policy bundle health check

## Usage Examples

### Constitutional Evaluation
```json
{
  "type": "constitutional_evaluation",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "action": "data.process_user",
  "context": {
    "environment": {"sandbox_enabled": true, "audit_enabled": true},
    "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
    "responsible_party": "system_admin",
    "explanation": "Processing user data for analytics"
  }
}
```

### Evolution Approval
```json
{
  "type": "evolution_approval",
  "evolution_request": {
    "type": "patch",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "changes": {"code_changes": ["Bug fix"]},
    "performance_analysis": {"complexity_delta": 0.01},
    "rollback_plan": {"procedure": "Git revert", "tested": true}
  }
}
```

### Data Access
```json
{
  "type": "data_access",
  "data_request": {
    "data_fields": [{"name": "user_email", "classification_level": 2}],
    "requester_clearance_level": 3,
    "purpose": "user_communication",
    "consent_records": [{"subject_id": "user123", "status": "granted"}]
  }
}
```
EOF

# Calculate bundle size and file count
BUNDLE_SIZE=$(ls -lh ${OUTPUT_DIR}/${BUNDLE_FILE} | awk '{print $5}')
POLICY_COUNT=$(find . -name "*.rego" -not -path "./tests/*" | wc -l)
TEST_COUNT=$(find tests/ -name "*_test.rego" | wc -l)

# Display build summary
echo ""
echo "🎉 ACGS-1 Lite Policy Bundle Build Complete!"
echo ""
echo "Build Summary:"
echo "  📦 Bundle: ${BUNDLE_FILE}"
echo "  📏 Size: ${BUNDLE_SIZE}"
echo "  📋 Policy Files: ${POLICY_COUNT}"
echo "  🧪 Test Files: ${TEST_COUNT}"
echo "  🔒 Constitutional Hash: cdd01ef066bc6cf2"
echo ""
echo "Output Files:"
echo "  🗂️  ${OUTPUT_DIR}/${BUNDLE_FILE}"
echo "  📋 ${OUTPUT_DIR}/bundle-metadata.json"
echo "  ⚡ ${OUTPUT_DIR}/performance-benchmark.json" 
echo "  📚 ${OUTPUT_DIR}/policy-documentation.md"
echo ""
echo "Deployment Command:"
echo "  opa run --server --bundle ${OUTPUT_DIR}/${BUNDLE_FILE}"
echo ""
echo "Test Command:"
echo "  curl http://localhost:8181/v1/data/acgs/main/health"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"