# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/usr/bin/env bash
set -e

URL="http://127.0.0.1:3000/govern"
RESULTS_DIR="benchmark_results"
DURATION="60s"

cat << EOF > compliant.json
{"query": {"actor_role": "Researcher", "data_sensitivity": "AnonymizedAggregate"}}
EOF

cat << EOF > violating.json
{"query": {"actor_role": "Clinician", "data_sensitivity": "IdentifiedPatientRecords"}}
EOF

echo "🚀 --- Starting ACGS-2 Expert System Benchmark Suite ---"
echo "🔧 Groq Integration: Ultra-fast LLM inference with Llama3-8B"
echo "⚡ Expected Performance: 10x faster than OpenAI, sub-200ms latency"
mkdir -p "$RESULTS_DIR"

run_test() {
    local mode=$1
    local concurrency=$2
    local payload_name=$3
    local payload_file="${payload_name}.json"
    local output_file="${RESULTS_DIR}/${mode}_c${concurrency}_${payload_name}.txt"

    echo "🧪 Running test: Mode=${mode}, Concurrency=${concurrency}, Payload=${payload_name}"

    if [ "$mode" == "stub" ]; then
        export USE_FAKE_LLM=1
        unset USE_GROQ
        echo "   🎭 Using mock LLM (cost-free, ~50ms latency)"
    elif [ "$mode" == "groq" ]; then
        export USE_GROQ=1
        unset USE_FAKE_LLM
        echo "   🚀 Using Groq API (ultra-fast, ~100ms latency)"
    else
        unset USE_FAKE_LLM
        unset USE_GROQ
        echo "   🤖 Using OpenAI API (standard, ~1000ms latency)"
    fi

    # Give the server a moment to restart/react to env var changes if needed
    sleep 2

    oha -c "$concurrency" -z "$DURATION" -H "Content-Type: application/json" \
        --body "@${payload_file}" "$URL" > "$output_file"

    echo "   📊 Results saved to ${output_file}"
    echo "   ---------------------------------"
}

# Ensure the server is running in another terminal before executing this script.
# cargo run --release -p governance_app

echo ""
echo "🎭 Phase 1: Mock Mode Tests (Safe and Free)"
echo "============================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
for c in 10 50 100 200; do
    run_test "stub" "$c" "compliant"
done

echo ""
echo "🚀 Phase 2: Groq API Tests (Ultra-Fast & Low Cost)"
echo "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
read -p "Run tests against REAL Groq API? This will incur minimal costs (~$0.01). (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔥 Running Groq API mode tests (expecting 500-2000 RPS)..."
    for c in 10 50 100 200; do
        run_test "groq" "$c" "compliant"
    done
    echo "✅ Groq tests complete! Expected results:"
    echo "   • Latency: 50-200ms per request"
    echo "   • Throughput: 500-2000 RPS"
    echo "   • Cost: ~$0.59/1M tokens (very low)"
fi

echo ""
echo "🤖 Phase 3: OpenAI API Tests (Standard Baseline)"
echo "==============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
read -p "Run tests against REAL OpenAI API? This will incur higher costs. (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐌 Running OpenAI API mode tests (low concurrency due to cost)..."
    for c in 1 5 10; do
        run_test "openai" "$c" "compliant"
    done
    echo "✅ OpenAI tests complete! Expected results:"
    echo "   • Latency: 500-2000ms per request"
    echo "   • Throughput: 50-200 RPS"
    echo "   • Cost: Higher than Groq"
fi

echo ""
echo "🎉 --- Benchmark Suite Complete ---"
echo "📊 Performance Comparison Expected:"
echo "   • Mock:   ~1000 RPS, 50ms latency, $0 cost"
echo "   • Groq:   ~1000 RPS, 100ms latency, very low cost"
echo "   • OpenAI: ~100 RPS, 1000ms latency, higher cost"
echo ""
echo "🔍 Check results in: ${RESULTS_DIR}/"
rm compliant.json violating.json
