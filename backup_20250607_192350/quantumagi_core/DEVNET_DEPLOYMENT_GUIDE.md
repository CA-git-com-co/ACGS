# 🚀 Quantumagi Solana Devnet Deployment Guide

This guide provides step-by-step instructions for deploying the Quantumagi Constitutional Governance System to Solana devnet.

## 📋 Prerequisites

### Required Software
- **Rust & Cargo** (1.70+)
- **Node.js** (16+) with npm
- **Python** (3.8+)
- **Git**

### Automatically Installed
- **Solana CLI** (1.18.22) - Multiple fallback installation methods
- **Anchor Framework** (0.29.0) - Already installed
- **Dependencies** - Automatically installed during deployment

## 🚀 Quick Start Deployment

### Option 1: One-Command Deployment (Recommended)

```bash
# Navigate to quantumagi_core directory
cd quantumagi_core

# Execute master deployment orchestrator
./deploy_quantumagi_devnet.sh
```

This single command will:
1. ✅ Validate project structure and dependencies
2. ✅ Install Solana CLI using multiple fallback methods
3. ✅ Initialize constitutional framework
4. ✅ Deploy all three smart contracts to Solana devnet
5. ✅ Run comprehensive validation tests
6. ✅ Generate detailed deployment report

### Option 2: Step-by-Step Deployment

If you prefer to run each phase manually:

```bash
# Phase 1: Install Solana CLI
./scripts/install_solana_cli.sh

# Phase 2: Initialize Constitution
python3 scripts/initialize_constitution.py --cluster devnet

# Phase 3: Deploy to Devnet
./scripts/deploy_to_devnet.sh

# Phase 4: Validate Deployment
python3 scripts/validate_devnet_deployment.py --cluster devnet
```

## 📊 Deployment Components

### Smart Contracts Deployed
1. **Quantumagi Core** - Main constitutional governance program
2. **Appeals Program** - Governance appeals and dispute resolution
3. **Logging Program** - Audit trail and compliance logging

### Constitutional Framework
1. **Constitution Document** - Core governance principles and procedures
2. **Initial Policies** - 3 foundational governance policies
3. **Governance Accounts** - Voting, appeals, and compliance structures

### Validation Systems
1. **Program Accessibility** - Verify all contracts are live on devnet
2. **Constitution Integrity** - Validate constitutional framework
3. **Policy Enforcement** - Test real-time compliance checking (PGC)
4. **Client Connectivity** - Ensure integration readiness

## 🔧 Troubleshooting

### Common Issues

#### Solana CLI Installation Fails
The deployment script includes 5 fallback installation methods:
1. Standard Solana installation
2. Package manager installation (apt/yum/brew)
3. Manual binary download
4. Anchor's embedded Solana
5. Docker-based Solana CLI

If all methods fail, install manually:
```bash
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

#### Anchor Build Fails
```bash
# Clean and rebuild
anchor clean
anchor build
```

#### Devnet Connection Issues
```bash
# Check Solana configuration
solana config get

# Set devnet cluster
solana config set --url https://api.devnet.solana.com

# Request airdrop if needed
solana airdrop 2
```

#### Python Dependencies Issues
```bash
# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r gs_engine/requirements.txt
```

## 📁 Generated Files

After successful deployment, you'll find:

### Program Information
- `devnet_program_ids.json` - Deployed program identifiers
- `devnet_deployment_report_*.json` - Detailed deployment results

### Constitutional Framework
- `constitution_data.json` - Constitutional framework data
- `initial_policies.json` - Initial governance policies
- `governance_accounts.json` - Account structure configuration

### Validation Results
- `devnet_validation_report_devnet.json` - Comprehensive validation results
- `QUANTUMAGI_DEVNET_DEPLOYMENT_COMPLETE.md` - Final deployment report

### Logs
- `master_deployment_*.log` - Complete deployment log
- `deployment_*.log` - Individual phase logs

## 🧪 Testing Your Deployment

### 1. View Programs on Solana Explorer
```bash
# Get your program IDs
cat devnet_program_ids.json

# Visit Solana Explorer
# https://explorer.solana.com/?cluster=devnet
# Search for your program IDs
```

### 2. Test Client Connectivity
```bash
# Test Python client
cd client
python3 solana_client.py --cluster devnet

# Test governance workflows
python3 test_governance_workflow.py
```

### 3. Validate Compliance Checking
```bash
# Run PGC compliance tests
python3 scripts/test_compliance_checking.py --cluster devnet
```

## 🚀 Next Steps After Deployment

### Immediate Actions
1. **Review Deployment Report** - Check `QUANTUMAGI_DEVNET_DEPLOYMENT_COMPLETE.md`
2. **Test Governance Workflows** - Submit test proposals and votes
3. **Validate Appeals Process** - Test dispute resolution mechanisms
4. **Monitor Performance** - Check transaction costs and execution times

### Integration Development
1. **Frontend Integration** - Connect React components to devnet programs
2. **ACGS Backend Integration** - Link to production ACGS services
3. **Real-time Monitoring** - Set up governance event listeners
4. **User Interface** - Develop governance dashboard and tools

### Production Preparation
1. **Security Audit** - Comprehensive smart contract review
2. **Load Testing** - Validate system performance under stress
3. **Gas Optimization** - Minimize transaction costs
4. **Mainnet Planning** - Prepare for production deployment

## 📞 Support

### Deployment Issues
- Check deployment logs in `master_deployment_*.log`
- Review validation report for specific failures
- Ensure all prerequisites are installed

### Technical Questions
- Review generated documentation in `docs/`
- Check client examples in `client/`
- Consult Anchor and Solana documentation

### System Validation
- Run validation script: `python3 scripts/validate_devnet_deployment.py`
- Check program accessibility on Solana Explorer
- Test governance workflows with client libraries

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ **All three smart contracts are deployed and accessible on Solana devnet**  
✅ **Constitutional framework is initialized with valid hash**  
✅ **Initial governance policies are active and enforceable**  
✅ **Validation tests pass with 100% success rate**  
✅ **Client libraries can connect and interact with deployed programs**  
✅ **Real-time compliance checking (PGC) is operational**

**🏛️ Welcome to the future of on-chain constitutional governance!**
