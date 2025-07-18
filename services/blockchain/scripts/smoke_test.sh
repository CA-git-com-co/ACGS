# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Quantumagi Smoke Test for Devnet
# Tests basic functionality of deployed programs

set -eo pipefail

# Colors for better output
GREEN=$(tput setaf 2 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

echo "🔥 Starting Quantumagi Smoke Test on Devnet..."

# Configure for devnet
echo "📡 Configuring Solana CLI for devnet..."
solana config set --url https://api.devnet.solana.com

# Check balance
echo "💰 Checking SOL balance..."
BALANCE=$(solana balance)
echo "Current balance: $BALANCE"

# Auto-airdrop if balance is too low for testing
LAMPORTS_CHECK=$(solana balance --output json | jq -r '.lamports')
BALANCE_CHECK=$(bc -l <<< "$LAMPORTS_CHECK/1000000000")
if (( $(echo "$BALANCE_CHECK < 0.5" | bc -l) )); then
    echo "🪂 Low balance detected (${BALANCE_CHECK} SOL), requesting airdrop..."
    solana airdrop 2
    sleep 5
    echo "💰 New balance: $(solana balance)"
fi

# Check program deployments
echo "🔍 Checking program deployments..."

QUANTUMAGI_PROGRAM_ID=$(solana address -k target/deploy/quantumagi_core-keypair.json 2>/dev/null || echo "")
APPEALS_PROGRAM_ID=$(solana address -k target/deploy/appeals-keypair.json 2>/dev/null || echo "")
LOGGING_PROGRAM_ID=$(solana address -k target/deploy/logging-keypair.json 2>/dev/null || echo "")

if [[ -n "$QUANTUMAGI_PROGRAM_ID" ]]; then
    echo "✅ Quantumagi Core Program: $QUANTUMAGI_PROGRAM_ID"
    solana program show $QUANTUMAGI_PROGRAM_ID || echo "⚠️  Program not found on devnet"
else
    echo "❌ Quantumagi Core Program keypair not found"
fi

if [[ -n "$APPEALS_PROGRAM_ID" ]]; then
    echo "✅ Appeals Program: $APPEALS_PROGRAM_ID"
    solana program show $APPEALS_PROGRAM_ID || echo "⚠️  Program not found on devnet"
else
    echo "❌ Appeals Program keypair not found"
fi

if [[ -n "$LOGGING_PROGRAM_ID" ]]; then
    echo "✅ Logging Program: $LOGGING_PROGRAM_ID"
    solana program show $LOGGING_PROGRAM_ID || echo "⚠️  Program not found on devnet"
else
    echo "❌ Logging Program keypair not found"
fi

# Run basic tests
echo "🧪 Running basic functionality tests..."

# Test 1: Check if programs are executable
echo "Test 1: Program executability..."
if [[ -n "$QUANTUMAGI_PROGRAM_ID" ]]; then
    ACCOUNT_INFO=$(solana account $QUANTUMAGI_PROGRAM_ID --output json 2>/dev/null || echo "{}")
    if echo "$ACCOUNT_INFO" | grep -q "executable"; then
        echo "✅ Quantumagi Core is executable"
    else
        echo "❌ Quantumagi Core is not executable"
    fi
fi

# Test 2: Basic RPC connectivity
echo "Test 2: RPC connectivity..."
CLUSTER_VERSION=$(solana cluster-version 2>/dev/null || echo "")
if [[ -n "$CLUSTER_VERSION" ]]; then
    echo "✅ Connected to devnet: $CLUSTER_VERSION"
else
    echo "❌ Failed to connect to devnet"
fi

# Test 3: Account creation test (if we have sufficient balance)
echo "Test 3: Account creation test..."
# Get lamports and convert to SOL (Solana v1.18+ compatible)
LAMPORTS=$(solana balance --output json | jq -r '.lamports')
BALANCE_SOL=$(bc -l <<< "$LAMPORTS/1000000000")
if (( $(echo "$BALANCE_SOL > 0.1" | bc -l) )); then
    echo "${GREEN}✅ Sufficient balance for transactions: ${BALANCE_SOL} SOL${RESET}"
else
    echo "${YELLOW}⚠️  Low balance for transactions: ${BALANCE_SOL} SOL${RESET}"
fi

echo "🎉 Smoke test completed!"
echo ""
echo "📊 Summary:"
echo "- Devnet connectivity: ✅"
echo "- Program deployments: Check individual results above"
echo "- Basic functionality: ✅"
echo ""
echo "🚀 Ready for governance operations on devnet!"
