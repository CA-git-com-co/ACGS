#!/bin/bash

# Quantumagi Deployment Completion Script
# This script completes the deployment of the logging program and initializes the governance system

set -e

echo "🚀 Quantumagi Deployment Completion Script"
echo "=========================================="

# Set up environment
export PATH="/home/dislove/.local/share/solana/install/active_release/bin:$PATH"

# Check current configuration
echo "📋 Current Solana Configuration:"
solana config get
echo ""

# Check current balance
echo "💰 Current SOL Balance:"
BALANCE=$(solana balance)
echo "$BALANCE"
echo ""

# Check if we have enough SOL for logging program deployment
REQUIRED_SOL="2.1"
CURRENT_SOL=$(echo $BALANCE | cut -d' ' -f1)

if (( $(echo "$CURRENT_SOL < $REQUIRED_SOL" | bc -l) )); then
    echo "⚠️  Insufficient SOL for logging program deployment"
    echo "   Required: $REQUIRED_SOL SOL"
    echo "   Current:  $CURRENT_SOL SOL"
    echo "   Requesting airdrop..."
    
    # Try to get more SOL
    solana airdrop 3 || {
        echo "❌ Airdrop failed. Please manually fund the wallet or wait for rate limit reset."
        echo "   Wallet address: $(solana address)"
        echo "   You can use the Solana devnet faucet: https://faucet.solana.com/"
        exit 1
    }
    
    echo "✅ Airdrop successful"
    echo "💰 New balance: $(solana balance)"
    echo ""
fi

# Deploy the logging program
echo "🔄 Deploying Logging Program..."
echo "Program ID: 4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo"

solana program deploy target/deploy/logging.so --program-id target/deploy/logging-keypair.json

if [ $? -eq 0 ]; then
    echo "✅ Logging program deployed successfully!"
    LOGGING_PROGRAM_ID="4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo"
else
    echo "❌ Logging program deployment failed"
    exit 1
fi

echo ""
echo "🎉 ALL PROGRAMS DEPLOYED SUCCESSFULLY!"
echo "====================================="
echo "✅ Quantumagi Core:  8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4"
echo "✅ Appeals:          CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ"
echo "✅ Logging:          4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo"
echo ""

# Verify deployments
echo "🔍 Verifying Program Deployments..."
echo "Quantumagi Core Program Info:"
solana program show 8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4 || echo "⚠️  Program info not available"

echo ""
echo "Appeals Program Info:"
solana program show CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ || echo "⚠️  Program info not available"

echo ""
echo "Logging Program Info:"
solana program show $LOGGING_PROGRAM_ID || echo "⚠️  Program info not available"

echo ""
echo "🏁 Deployment Complete!"
echo "Next steps:"
echo "1. Initialize constitution with: anchor run initialize-constitution"
echo "2. Set up initial policies"
echo "3. Test governance workflows"
echo "4. Deploy frontend interface"
echo ""
echo "📊 Final SOL Balance: $(solana balance)"
echo "🌐 Network: Solana Devnet"
echo "🔗 RPC: https://api.devnet.solana.com"
