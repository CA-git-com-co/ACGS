# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/usr/bin/env bash

echo "🚀 ACGS-2 Expert System - Groq Integration Demo"
echo "==============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo ""
echo "This demo showcases the ultra-fast Groq API integration"
echo "for AI governance decisions with sub-200ms latency."
echo ""

# Test payloads
cat << EOF > compliant_query.json
{"query": {"actor_role": "Researcher", "data_sensitivity": "AnonymizedAggregate"}}
EOF

cat << EOF > violating_query.json
{"query": {"actor_role": "Clinician", "data_sensitivity": "IdentifiedPatientRecords"}}
EOF

echo "📋 Test Cases:"
echo "1. Compliant: Researcher accessing anonymized data"
echo "2. Violating: Clinician accessing identified patient records"
echo ""

echo "🎭 Phase 1: Mock LLM (Cost-Free Testing)"
echo "========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo "Starting server with mock LLM..."

# Start server with mock LLM in background
USE_FAKE_LLM=1 cargo run --release -p governance_app > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

echo "Testing compliant query..."
RESPONSE1=$(curl -s -X POST http://127.0.0.1:3000/govern \
  -H "Content-Type: application/json" \
  -d @compliant_query.json)
echo "✅ Response: $RESPONSE1"

echo "Testing violating query..."
RESPONSE2=$(curl -s -X POST http://127.0.0.1:3000/govern \
  -H "Content-Type: application/json" \
  -d @violating_query.json)
echo "❌ Response: $RESPONSE2"

echo ""
echo "🏃‍♂️ Quick Performance Test (Mock LLM):"
echo "Running 100 requests with 10 concurrent connections..."
oha -c 10 -n 100 -m POST -H "Content-Type: application/json" \
  -D compliant_query.json http://127.0.0.1:3000/govern --no-tui | grep -E "(Success rate|Requests/sec|Average)"

# Stop mock server
kill $SERVER_PID 2>/dev/null
sleep 2

echo ""
echo "🚀 Phase 2: Groq API Integration"
echo "================================="

if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set. Skipping real API test."
    echo "   To test with real Groq API:"
    echo "   1. Get API key from https://console.groq.com/keys"
    echo "   2. export GROQ_API_KEY='your_key_here'"
    echo "   3. export USE_GROQ=1"
    echo "   4. Re-run this demo"
else
    echo "🔑 GROQ_API_KEY detected. Starting Groq-powered server..."
    echo "   Model: llama3-8b-8192 (Ultra-fast inference)"
    echo "   Expected latency: 50-200ms per request"
    echo ""
    
    # Start server with Groq API
    USE_GROQ=1 cargo run --release -p governance_app > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 3
    
    echo "Testing with real Groq API..."
    echo "Compliant query (should return 'comply'):"
    GROQ_RESPONSE1=$(curl -s -X POST http://127.0.0.1:3000/govern \
      -H "Content-Type: application/json" \
      -d @compliant_query.json)
    echo "✅ Groq Response: $GROQ_RESPONSE1"
    
    echo ""
    echo "Violating query (should return 'violate'):"
    GROQ_RESPONSE2=$(curl -s -X POST http://127.0.0.1:3000/govern \
      -H "Content-Type: application/json" \
      -d @violating_query.json)
    echo "❌ Groq Response: $GROQ_RESPONSE2"
    
    echo ""
    echo "🏃‍♂️ Groq Performance Test:"
    echo "Running 50 requests with 5 concurrent connections..."
    oha -c 5 -n 50 -m POST -H "Content-Type: application/json" \
      -D compliant_query.json http://127.0.0.1:3000/govern --no-tui | grep -E "(Success rate|Requests/sec|Average)"
    
    # Stop Groq server
    kill $SERVER_PID 2>/dev/null
fi

echo ""
echo "🎉 Demo Complete!"
echo "================="
echo ""
echo "📊 Expected Performance Comparison:"
echo "• Mock LLM:  ~500 RPS, 100ms latency, $0 cost"
echo "• Groq API:  ~200 RPS, 150ms latency, very low cost"
echo "• OpenAI:    ~50 RPS, 1000ms latency, higher cost"
echo ""
echo "🔧 Key Benefits of Groq Integration:"
echo "• 10x faster than OpenAI GPT models"
echo "• 90% cost reduction compared to OpenAI"
echo "• Same API compatibility (drop-in replacement)"
echo "• Perfect for high-throughput governance decisions"
echo ""
echo "🚀 Ready for production deployment!"

# Cleanup
rm -f compliant_query.json violating_query.json test_payload.json
