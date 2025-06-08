#!/bin/bash

# Quantumagi Deployment Status Verification Script
# Verifies the current status of all deployed components

set -e

echo "🔍 QUANTUMAGI DEPLOYMENT STATUS VERIFICATION"
echo "============================================="

# Set up environment
export PATH="/home/dislove/.local/share/solana/install/active_release/bin:$PATH"

echo ""
echo "📋 Network Configuration:"
solana config get
echo ""

echo "💰 Current SOL Balance:"
solana balance
echo ""

echo "🔍 Program Deployment Status:"
echo "------------------------------"

# Check Quantumagi Core Program
echo "1. Quantumagi Core Program:"
CORE_PROGRAM_ID="8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4"
if solana program show $CORE_PROGRAM_ID >/dev/null 2>&1; then
    echo "   ✅ DEPLOYED: $CORE_PROGRAM_ID"
    echo "   📊 Program Info:"
    solana program show $CORE_PROGRAM_ID | head -5 | sed 's/^/      /'
else
    echo "   ❌ NOT DEPLOYED: $CORE_PROGRAM_ID"
fi
echo ""

# Check Appeals Program
echo "2. Appeals Program:"
APPEALS_PROGRAM_ID="CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ"
if solana program show $APPEALS_PROGRAM_ID >/dev/null 2>&1; then
    echo "   ✅ DEPLOYED: $APPEALS_PROGRAM_ID"
    echo "   📊 Program Info:"
    solana program show $APPEALS_PROGRAM_ID | head -5 | sed 's/^/      /'
else
    echo "   ❌ NOT DEPLOYED: $APPEALS_PROGRAM_ID"
fi
echo ""

# Check Logging Program
echo "3. Logging Program:"
LOGGING_PROGRAM_ID="4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo"
if solana program show $LOGGING_PROGRAM_ID >/dev/null 2>&1; then
    echo "   ✅ DEPLOYED: $LOGGING_PROGRAM_ID"
    echo "   📊 Program Info:"
    solana program show $LOGGING_PROGRAM_ID | head -5 | sed 's/^/      /'
else
    echo "   ⏳ PENDING DEPLOYMENT: $LOGGING_PROGRAM_ID"
    echo "      Status: Ready for deployment (requires ~2.1 SOL)"
fi
echo ""

echo "📄 Constitution & Governance Status:"
echo "------------------------------------"

# Check constitution initialization
if [ -f "constitution_data.json" ]; then
    echo "✅ Constitution Data: Found"
    CONST_HASH=$(jq -r '.constitution.hash' constitution_data.json 2>/dev/null || echo "unknown")
    CONST_VERSION=$(jq -r '.constitution.version' constitution_data.json 2>/dev/null || echo "unknown")
    echo "   📋 Hash: $CONST_HASH"
    echo "   🔢 Version: $CONST_VERSION"
else
    echo "❌ Constitution Data: Missing"
fi

# Check initial policies
if [ -f "initial_policies.json" ]; then
    echo "✅ Initial Policies: Found"
    POLICY_COUNT=$(jq '. | length' initial_policies.json 2>/dev/null || echo "unknown")
    echo "   📊 Policy Count: $POLICY_COUNT"
else
    echo "❌ Initial Policies: Missing"
fi

# Check governance accounts
if [ -f "governance_accounts.json" ]; then
    echo "✅ Governance Accounts: Configured"
else
    echo "❌ Governance Accounts: Missing"
fi

echo ""
echo "🧪 Test Results Status:"
echo "-----------------------"

# Check for test reports
if ls quantumagi_demo_report_*.json >/dev/null 2>&1; then
    LATEST_REPORT=$(ls -t quantumagi_demo_report_*.json | head -1)
    echo "✅ End-to-End Tests: Completed"
    echo "   📄 Latest Report: $LATEST_REPORT"
    
    # Extract key metrics if jq is available
    if command -v jq >/dev/null 2>&1; then
        POLICIES_CREATED=$(jq -r '.metrics.policies_created // "unknown"' "$LATEST_REPORT" 2>/dev/null)
        COMPLIANCE_CHECKS=$(jq -r '.metrics.compliance_checks // "unknown"' "$LATEST_REPORT" 2>/dev/null)
        APPEALS_PROCESSED=$(jq -r '.metrics.appeals_processed // "unknown"' "$LATEST_REPORT" 2>/dev/null)
        
        echo "   📊 Policies Created: $POLICIES_CREATED"
        echo "   🔍 Compliance Checks: $COMPLIANCE_CHECKS"
        echo "   ⚖️  Appeals Processed: $APPEALS_PROCESSED"
    fi
else
    echo "❌ End-to-End Tests: Not completed"
fi

echo ""
echo "📊 DEPLOYMENT SUMMARY:"
echo "======================"

# Count deployed programs
DEPLOYED_COUNT=0
if solana program show $CORE_PROGRAM_ID >/dev/null 2>&1; then
    ((DEPLOYED_COUNT++))
fi
if solana program show $APPEALS_PROGRAM_ID >/dev/null 2>&1; then
    ((DEPLOYED_COUNT++))
fi
if solana program show $LOGGING_PROGRAM_ID >/dev/null 2>&1; then
    ((DEPLOYED_COUNT++))
fi

DEPLOYMENT_PERCENTAGE=$((DEPLOYED_COUNT * 100 / 3))

echo "🚀 Programs Deployed: $DEPLOYED_COUNT/3 ($DEPLOYMENT_PERCENTAGE%)"

if [ $DEPLOYED_COUNT -eq 3 ]; then
    echo "🎉 STATUS: FULLY DEPLOYED"
elif [ $DEPLOYED_COUNT -eq 2 ]; then
    echo "⏳ STATUS: NEARLY COMPLETE (Logging program pending)"
else
    echo "⚠️  STATUS: INCOMPLETE"
fi

# Check constitution status
if [ -f "constitution_data.json" ] && [ -f "initial_policies.json" ]; then
    echo "✅ Constitution: INITIALIZED"
else
    echo "❌ Constitution: NOT INITIALIZED"
fi

# Check test status
if ls quantumagi_demo_report_*.json >/dev/null 2>&1; then
    echo "✅ Testing: COMPLETED"
else
    echo "❌ Testing: NOT COMPLETED"
fi

echo ""
echo "🔧 Next Actions:"
echo "---------------"

if [ $DEPLOYED_COUNT -lt 3 ]; then
    echo "1. Complete logging program deployment:"
    echo "   ./complete_deployment.sh"
fi

if [ ! -f "constitution_data.json" ]; then
    echo "2. Initialize constitution:"
    echo "   python3 scripts/initialize_constitution.py --cluster devnet"
fi

if ! ls quantumagi_demo_report_*.json >/dev/null 2>&1; then
    echo "3. Run end-to-end tests:"
    echo "   python3 scripts/demo_end_to_end.py"
fi

if [ $DEPLOYED_COUNT -eq 3 ] && [ -f "constitution_data.json" ] && ls quantumagi_demo_report_*.json >/dev/null 2>&1; then
    echo "🎉 ALL TASKS COMPLETE!"
    echo "   Quantumagi is fully operational on Solana devnet"
    echo "   Ready for production use and frontend integration"
fi

echo ""
echo "📅 Verification completed: $(date)"
echo "🌐 Network: Solana Devnet"
echo "🔗 RPC: https://api.devnet.solana.com"
