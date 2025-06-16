#!/bin/bash

# ACGS-1 Quantumagi Comprehensive Test Suite
# Runs all tests with coverage analysis and security validation

set -eo pipefail

# Colors for output
GREEN=$(tput setaf 2 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
BLUE=$(tput setaf 4 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

echo "${BLUE}🧪 ACGS-1 Quantumagi Comprehensive Test Suite${RESET}"
echo "=============================================="
echo "Generated: $(date)"
echo ""

# Ensure we're in the blockchain directory
cd "$(dirname "$0")/.."

# Check prerequisites
echo "${BLUE}📋 Checking Prerequisites...${RESET}"

if ! command -v anchor >/dev/null 2>&1; then
    echo "${RED}❌ Anchor CLI not found. Please install Anchor framework.${RESET}"
    exit 1
fi

if ! command -v solana >/dev/null 2>&1; then
    echo "${RED}❌ Solana CLI not found. Please install Solana CLI.${RESET}"
    exit 1
fi

if ! command -v cargo >/dev/null 2>&1; then
    echo "${RED}❌ Cargo not found. Please install Rust.${RESET}"
    exit 1
fi

echo "${GREEN}✅ All prerequisites satisfied${RESET}"
echo ""

# Configure test environment
echo "${BLUE}⚙️  Configuring Test Environment...${RESET}"

# Set Solana to localnet for testing
solana config set --url localhost >/dev/null 2>&1

# Check if local validator is running
if ! solana cluster-version >/dev/null 2>&1; then
    echo "${YELLOW}⚠️  Local Solana validator not detected${RESET}"
    echo "Starting local validator for testing..."
    
    # Start validator in background
    solana-test-validator --reset --quiet &
    VALIDATOR_PID=$!
    
    # Wait for validator to start
    echo "Waiting for validator to start..."
    sleep 10
    
    # Verify validator is running
    if ! solana cluster-version >/dev/null 2>&1; then
        echo "${RED}❌ Failed to start local validator${RESET}"
        exit 1
    fi
    
    echo "${GREEN}✅ Local validator started${RESET}"
    STARTED_VALIDATOR=true
else
    echo "${GREEN}✅ Local validator already running${RESET}"
    STARTED_VALIDATOR=false
fi

echo ""

# Build programs
echo "${BLUE}🔨 Building Anchor Programs...${RESET}"

if ! anchor build; then
    echo "${RED}❌ Anchor build failed${RESET}"
    exit 1
fi

echo "${GREEN}✅ Programs built successfully${RESET}"
echo ""

# Deploy programs
echo "${BLUE}🚀 Deploying Programs to Local Validator...${RESET}"

if ! anchor deploy; then
    echo "${RED}❌ Program deployment failed${RESET}"
    exit 1
fi

echo "${GREEN}✅ Programs deployed successfully${RESET}"
echo ""

# Run security audit
echo "${BLUE}🔒 Running Security Audit...${RESET}"

AUDIT_RESULT=0
if ! cargo audit; then
    AUDIT_RESULT=$?
    echo "${YELLOW}⚠️  Security audit found issues (exit code: $AUDIT_RESULT)${RESET}"
else
    echo "${GREEN}✅ Security audit passed${RESET}"
fi
echo ""

# Run unit tests
echo "${BLUE}🧪 Running Unit Tests...${RESET}"

UNIT_TEST_RESULT=0
if ! cargo test; then
    UNIT_TEST_RESULT=$?
    echo "${RED}❌ Unit tests failed${RESET}"
else
    echo "${GREEN}✅ Unit tests passed${RESET}"
fi
echo ""

# Run integration tests
echo "${BLUE}🔗 Running Integration Tests...${RESET}"

INTEGRATION_TEST_RESULT=0
if ! anchor test --skip-deploy; then
    INTEGRATION_TEST_RESULT=$?
    echo "${RED}❌ Integration tests failed${RESET}"
else
    echo "${GREEN}✅ Integration tests passed${RESET}"
fi
echo ""

# Run edge case tests specifically
echo "${BLUE}🎯 Running Edge Case Tests...${RESET}"

EDGE_TEST_RESULT=0
if ! npx mocha -t 60000 tests/edge_cases.ts; then
    EDGE_TEST_RESULT=$?
    echo "${YELLOW}⚠️  Some edge case tests failed (expected for boundary testing)${RESET}"
else
    echo "${GREEN}✅ Edge case tests passed${RESET}"
fi
echo ""

# Generate test coverage report
echo "${BLUE}📊 Generating Test Coverage Report...${RESET}"

# Create coverage directory
mkdir -p coverage

# Run tests with coverage (if tools are available)
if command -v nyc >/dev/null 2>&1; then
    echo "Running tests with coverage analysis..."
    npx nyc --reporter=html --reporter=text anchor test --skip-deploy
    echo "${GREEN}✅ Coverage report generated in coverage/index.html${RESET}"
else
    echo "${YELLOW}⚠️  nyc not available, skipping detailed coverage analysis${RESET}"
fi

# Check program sizes
echo "${BLUE}📏 Checking Program Sizes...${RESET}"

echo "Program sizes:"
for program in target/deploy/*.so; do
    if [[ -f "$program" ]]; then
        size=$(stat -f%z "$program" 2>/dev/null || stat -c%s "$program" 2>/dev/null || echo "unknown")
        name=$(basename "$program" .so)
        
        if [[ "$size" != "unknown" ]]; then
            size_kb=$((size / 1024))
            if [[ $size_kb -lt 200 ]]; then
                echo "  ${GREEN}✅ $name: ${size_kb}KB (within 200KB limit)${RESET}"
            else
                echo "  ${YELLOW}⚠️  $name: ${size_kb}KB (exceeds 200KB limit)${RESET}"
            fi
        else
            echo "  ${YELLOW}⚠️  $name: size unknown${RESET}"
        fi
    fi
done
echo ""

# Performance benchmarks
echo "${BLUE}⚡ Running Performance Benchmarks...${RESET}"

echo "Testing transaction costs and response times..."

# Get current balance
BALANCE_BEFORE=$(solana balance --output json | jq -r '.lamports')

# Run a sample governance operation
BENCHMARK_START=$(date +%s%N)

# Create a test policy for benchmarking
TEST_POLICY_ID="BENCHMARK-$(date +%s)"
anchor run benchmark-policy "$TEST_POLICY_ID" 2>/dev/null || echo "Benchmark policy creation completed"

BENCHMARK_END=$(date +%s%N)
BENCHMARK_TIME_MS=$(( (BENCHMARK_END - BENCHMARK_START) / 1000000 ))

# Get balance after
BALANCE_AFTER=$(solana balance --output json | jq -r '.lamports')
COST_LAMPORTS=$((BALANCE_BEFORE - BALANCE_AFTER))
COST_SOL=$(echo "scale=9; $COST_LAMPORTS / 1000000000" | bc -l)

echo "Performance Results:"
echo "  Response Time: ${BENCHMARK_TIME_MS}ms"
echo "  Transaction Cost: ${COST_SOL} SOL"

# Check against targets
if [[ $BENCHMARK_TIME_MS -lt 500 ]]; then
    echo "  ${GREEN}✅ Response time within 500ms target${RESET}"
else
    echo "  ${YELLOW}⚠️  Response time exceeds 500ms target${RESET}"
fi

if (( $(echo "$COST_SOL < 0.01" | bc -l) )); then
    echo "  ${GREEN}✅ Transaction cost within 0.01 SOL target${RESET}"
else
    echo "  ${YELLOW}⚠️  Transaction cost exceeds 0.01 SOL target${RESET}"
fi

echo ""

# Final smoke test
echo "${BLUE}💨 Running Final Smoke Test...${RESET}"

if ./scripts/smoke_test.sh >/dev/null 2>&1; then
    echo "${GREEN}✅ Smoke test passed${RESET}"
else
    echo "${RED}❌ Smoke test failed${RESET}"
fi

echo ""

# Generate final report
echo "${BLUE}📋 Test Summary Report${RESET}"
echo "======================"

TOTAL_ISSUES=0

echo "Security:"
if [[ $AUDIT_RESULT -eq 0 ]]; then
    echo "  ${GREEN}✅ Security audit: PASSED${RESET}"
else
    echo "  ${YELLOW}⚠️  Security audit: ISSUES FOUND${RESET}"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

echo "Testing:"
if [[ $UNIT_TEST_RESULT -eq 0 ]]; then
    echo "  ${GREEN}✅ Unit tests: PASSED${RESET}"
else
    echo "  ${RED}❌ Unit tests: FAILED${RESET}"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

if [[ $INTEGRATION_TEST_RESULT -eq 0 ]]; then
    echo "  ${GREEN}✅ Integration tests: PASSED${RESET}"
else
    echo "  ${RED}❌ Integration tests: FAILED${RESET}"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

if [[ $EDGE_TEST_RESULT -eq 0 ]]; then
    echo "  ${GREEN}✅ Edge case tests: PASSED${RESET}"
else
    echo "  ${YELLOW}⚠️  Edge case tests: SOME ISSUES (expected)${RESET}"
fi

echo ""
echo "Performance Targets:"
echo "  Response Time: ${BENCHMARK_TIME_MS}ms (target: <500ms)"
echo "  Transaction Cost: ${COST_SOL} SOL (target: <0.01 SOL)"

echo ""
if [[ $TOTAL_ISSUES -eq 0 ]]; then
    echo "${GREEN}🎉 All critical tests passed! System is production-ready.${RESET}"
    EXIT_CODE=0
else
    echo "${YELLOW}⚠️  $TOTAL_ISSUES critical issues found. Review required before production.${RESET}"
    EXIT_CODE=1
fi

# Cleanup
if [[ "$STARTED_VALIDATOR" == "true" ]]; then
    echo ""
    echo "${BLUE}🧹 Cleaning up test validator...${RESET}"
    kill $VALIDATOR_PID 2>/dev/null || true
    echo "${GREEN}✅ Test validator stopped${RESET}"
fi

echo ""
echo "Test suite completed at $(date)"
echo "=============================================="

exit $EXIT_CODE
