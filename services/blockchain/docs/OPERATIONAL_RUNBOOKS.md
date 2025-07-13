<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS-1 Quantumagi Operational Runbooks

## 🎯 Overview

This document provides step-by-step operational procedures for maintaining and operating the ACGS-1 Quantumagi constitutional governance system in production environments.

## 🚀 Deployment Procedures

### Pre-Deployment Checklist

#### Security Validation

```bash
# 1. Run comprehensive security audit
cd blockchain
cargo audit --deny warnings

# 2. Verify no unsafe code
grep -r "unsafe" programs/ && echo "❌ Unsafe code found" || echo "✅ Safe"

# 3. Run comprehensive test suite
./scripts/run_comprehensive_tests.sh

# 4. Verify key management setup
./scripts/key_management.sh audit
```

#### Performance Validation

```bash
# 1. Check program sizes (must be < 200KB)
ls -la target/deploy/*.so

# 2. Run performance benchmarks
anchor run benchmark-governance

# 3. Validate transaction costs (< 0.01 SOL)
# 4. Verify response times (< 500ms)
```

### Devnet Deployment

#### Step 1: Environment Setup

```bash
# Configure Solana CLI for devnet
solana config set --url https://api.devnet.solana.com

# Verify connection
solana cluster-version

# Check deployer balance (need ≥ 10 SOL)
solana balance
```

#### Step 2: Program Deployment

```bash
# Build programs
anchor build

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Verify deployment
./scripts/smoke_test.sh
```

#### Step 3: Post-Deployment Validation

```bash
# Run smoke tests
./scripts/smoke_test.sh

# Verify program functionality
anchor test --skip-deploy

# Check program upgrade authorities
solana program show <program_id>
```

### Mainnet Deployment

#### Step 1: Final Security Review

```bash
# Complete security audit
cargo audit --deny warnings

# External security review (if required)
# Third-party penetration testing (if required)

# Multi-signature approval for deployment
```

#### Step 2: Mainnet Configuration

```bash
# Configure for mainnet
solana config set --url mainnet-beta

# Verify mainnet connection
solana cluster-version

# Check deployer balance (need ≥ 50 SOL for mainnet)
solana balance
```

#### Step 3: Controlled Deployment

```bash
# Deploy with production settings
anchor deploy --provider.cluster mainnet-beta

# Immediate post-deployment verification
./scripts/smoke_test.sh

# Monitor for 24 hours before full activation
```

## 🔧 Maintenance Procedures

### Daily Operations

#### Health Monitoring

```bash
# Check program status
./scripts/deployment_status.sh

# Verify RPC connectivity
solana cluster-version

# Monitor transaction costs
# Check for any unusual activity
```

#### Security Monitoring

```bash
# Daily security scan
cargo audit

# Check for new vulnerabilities
cargo deny check

# Review access logs (if applicable)
```

### Weekly Operations

#### Dependency Updates

```bash
# Check for dependency updates
cargo outdated

# Review security advisories
cargo audit

# Update non-breaking dependencies
cargo update

# Test after updates
./scripts/run_comprehensive_tests.sh
```

#### Performance Review

```bash
# Run performance benchmarks
anchor run benchmark-governance

# Review transaction costs and response times
# Check program size growth
# Monitor resource usage
```

### Monthly Operations

#### Security Review

```bash
# Comprehensive security audit
cargo audit --deny warnings

# Review key management
./scripts/key_management.sh audit

# Check authority configurations
# Review access controls
```

#### Backup Procedures

```bash
# Backup program keypairs
./scripts/key_management.sh backup-all

# Backup configuration files
# Document current program IDs and authorities
# Store backups in secure offline location
```

## 🔐 Key Management Procedures

### Key Generation

#### Initial Setup

```bash
# Create secure key directories
./scripts/key_management.sh init

# Generate program upgrade authorities
./scripts/key_management.sh generate-program

# Generate governance authorities
./scripts/key_management.sh generate-governance

# Setup multi-signature (if required)
./scripts/key_management.sh generate-multisig
```

#### Key Rotation Schedule

- **Program Upgrade Keys**: Every 6 months
- **Governance Keys**: Every 12 months
- **Emergency Keys**: Every 3 months

### Authority Transfer

#### Program Upgrade Authority

```bash
# Transfer upgrade authority
./scripts/key_management.sh transfer-authority \
  <program_id> \
  <new_authority_keypair> \
  <current_authority_keypair>

# Verify transfer
solana program show <program_id>
```

#### Governance Authority

```bash
# Update constitution authority
anchor run update-constitution-authority \
  --new-authority <new_authority_pubkey>

# Verify authority change
anchor run verify-constitution-authority
```

### Key Revocation (Immutable Programs)

#### Making Programs Immutable

```bash
# WARNING: This cannot be undone!
./scripts/key_management.sh revoke-program-authority \
  <program_id> \
  <current_authority_keypair>

# Verify immutability
solana program show <program_id>
# Should show "Upgrade Authority: None"
```

## 🚨 Emergency Procedures

### Security Incident Response

#### Immediate Actions (0-1 hour)

1. **Assess Severity**: Critical/High/Medium/Low
2. **Contain Threat**: Disable affected components if necessary
3. **Notify Team**: Alert security team and stakeholders
4. **Document**: Record all actions and findings

#### Short-term Response (1-24 hours)

1. **Investigate**: Determine root cause and scope
2. **Develop Fix**: Create and test security patches
3. **Communicate**: Update stakeholders on progress
4. **Prepare Deployment**: Ready emergency deployment

#### Resolution (24-72 hours)

1. **Deploy Fix**: Apply security patches
2. **Validate**: Verify fix effectiveness
3. **Monitor**: Watch for any additional issues
4. **Document**: Complete incident report

### Emergency Governance Actions

#### Constitution Emergency Halt

```bash
# Execute emergency halt (authority required)
anchor run emergency-halt \
  --authority <emergency_authority_keypair> \
  --reason "Security incident - immediate halt required"

# Verify halt status
anchor run check-emergency-status
```

#### Emergency Authority Transfer

```bash
# Transfer emergency authority (multi-sig required)
anchor run emergency-authority-transfer \
  --new-authority <new_emergency_authority> \
  --multisig-signers <signer1,signer2,signer3>
```

### System Recovery

#### After Security Incident

1. **Verify Fix**: Confirm vulnerability is resolved
2. **Security Scan**: Run comprehensive security audit
3. **Test Suite**: Execute full test suite
4. **Gradual Restart**: Resume operations incrementally
5. **Monitor**: Enhanced monitoring for 48 hours

#### After Network Issues

1. **Check Connectivity**: Verify Solana network status
2. **Validate Programs**: Confirm program accessibility
3. **Test Transactions**: Execute test governance operations
4. **Resume Operations**: Return to normal operations

## 📊 Monitoring and Alerting

### Key Metrics to Monitor

#### Performance Metrics

- Transaction response times (target: < 500ms)
- Transaction costs (target: < 0.01 SOL)
- Program execution success rate (target: > 99.5%)
- Network connectivity uptime (target: > 99.9%)

#### Security Metrics

- Failed authentication attempts
- Unusual authority usage patterns
- Unexpected account modifications
- Dependency vulnerability counts

### Alerting Thresholds

#### Critical Alerts (Immediate Response)

- Security vulnerabilities detected
- Program execution failures > 1%
- Unauthorized authority usage
- Network connectivity loss > 5 minutes

#### Warning Alerts (Response within 4 hours)

- Transaction costs > 0.005 SOL
- Response times > 250ms
- Dependency updates available
- Key rotation due dates approaching

### Monitoring Tools Setup

#### Automated Monitoring

```bash
# Setup monitoring cron jobs
# Daily security scans
0 2 * * * cd /path/to/blockchain && cargo audit

# Weekly dependency checks
0 3 * * 1 cd /path/to/blockchain && cargo outdated

# Monthly key rotation reminders
0 4 1 * * cd /path/to/blockchain && ./scripts/key_management.sh audit
```

## 📋 Troubleshooting Guide

### Common Issues

#### Program Deployment Failures

```bash
# Check Solana network status
solana cluster-version

# Verify account balance
solana balance

# Check program size limits
ls -la target/deploy/*.so

# Rebuild and retry
anchor clean && anchor build && anchor deploy
```

#### Test Failures

```bash
# Check local validator status
solana cluster-version

# Restart local validator
solana-test-validator --reset

# Run individual test suites
anchor test --skip-deploy
npx mocha tests/governance_integration.ts
```

#### Key Management Issues

```bash
# Verify key permissions
./scripts/key_management.sh audit

# Check key file integrity
solana-keygen verify <keypair_file>

# Regenerate corrupted keys (with backup)
./scripts/key_management.sh generate-keypair <name> <purpose>
```

### Performance Issues

#### High Transaction Costs

1. Check network congestion
2. Optimize instruction data
3. Review account allocations
4. Consider batching operations

#### Slow Response Times

1. Check RPC endpoint performance
2. Verify network connectivity
3. Review program logic efficiency
4. Monitor validator performance

## 📞 Contact Information

### Emergency Contacts

- **Security Team**: security@quantumagi.org
- **Operations Team**: ops@quantumagi.org
- **Technical Lead**: tech-lead@quantumagi.org

### Escalation Procedures

1. **Level 1**: Operations team (response: 1 hour)
2. **Level 2**: Technical lead (response: 30 minutes)
3. **Level 3**: Security team (response: 15 minutes)
4. **Level 4**: Executive team (immediate)

---

**Last Updated**: 2025-06-13  
**Next Review**: 2025-07-13  
**Document Version**: 1.0
