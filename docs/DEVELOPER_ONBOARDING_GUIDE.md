# ACGS-1 Developer Onboarding & Contribution Guide

**Version**: 3.0.0  
**Date**: 2025-06-16  
**Constitution Hash**: cdd01ef066bc6cf2

## Table of Contents

1. [Welcome to ACGS-1](#welcome-to-acgs-1)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [Coding Standards](#coding-standards)
5. [Testing Procedures](#testing-procedures)
6. [Governance Workflow Development](#governance-workflow-development)
7. [Quantumagi Solana Integration](#quantumagi-solana-integration)
8. [Contribution Guidelines](#contribution-guidelines)
9. [Code Review Process](#code-review-process)
10. [Deployment & Release Process](#deployment--release-process)

## Welcome to ACGS-1

ACGS-1 (AI Compliance Governance System) is a production-grade constitutional governance platform that combines AI-driven policy synthesis with blockchain-based constitutional compliance. Our system ensures democratic governance through technological innovation while maintaining constitutional integrity.

### Core Principles

- **Constitutional Compliance**: All actions must comply with Constitution Hash `cdd01ef066bc6cf2`
- **Democratic Governance**: Multi-signature validation and transparent decision-making
- **Performance Excellence**: <500ms response times, >99.5% uptime
- **Security First**: Zero-trust architecture with comprehensive validation
- **Open Source**: Transparent, auditable, and community-driven development

### System Overview

- **8 Core Services**: Auth (8000), AC (8001), Integrity (8002), FV (8003), GS (8004), PGC (8005), EC (8006), DGM (8007)
- **5 Governance Workflows**: Policy Creation, Constitutional Compliance, Policy Enforcement, WINA Oversight, Audit/Transparency
- **Blockchain Integration**: Quantumagi Solana programs for immutable governance
- **Multi-Model AI**: Qwen3-32B, DeepSeek Chat v3 for policy synthesis
- **DGM Integration**: Darwin Gödel Machine for self-evolving AI governance with event-driven architecture

## Development Environment Setup

### Prerequisites

```bash
# System Requirements
- Ubuntu 20.04+ or macOS 12+
- Rust 1.81.0+ (primary blockchain development)
- Python 3.11+ (required for all services)
- Node.js 18+ (frontend applications only)
- PostgreSQL 15+
- Redis 7+
- Docker 24.0+
- Solana CLI 1.18.22+
- Anchor 0.29.0+
- UV Package Manager (recommended for Python dependency management)
```

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# 2. Install UV package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 3. Set up Python environment with UV
uv sync

# Alternative: Traditional Python setup
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Start core services (requires Docker)
docker-compose up -d postgres redis

# 6. Run database migrations
uv run alembic upgrade head

# 7. Start individual services for development
cd services/platform/authentication && uv run uvicorn main:app --port 8000 --reload
cd services/core/ac-service && uv run uvicorn main:app --port 8001 --reload
cd services/core/dgm-service && uv run uvicorn dgm_service.main:app --port 8007 --reload

# 4. Set up Node.js environment
npm install

# 5. Set up Solana/Anchor environment
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
npm install -g @coral-xyz/anchor-cli@0.29.0

# 6. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 7. Initialize database
python scripts/setup_database.py

# 8. Start services (including DGM service)
bash scripts/start_missing_services.sh

# 9. Verify installation
python3 scripts/comprehensive_health_check.py
```

### Development Tools Setup

**IDE Configuration**:

```bash
# VS Code extensions
code --install-extension ms-python.python
code --install-extension bradlc.vscode-tailwindcss
code --install-extension rust-lang.rust-analyzer
code --install-extension ms-vscode.vscode-typescript-next
```

**Git Hooks**:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Architecture Overview

### Service Architecture

```
Frontend (React) → API Gateway (HAProxy) → Core Services → Infrastructure
                                        ↓
                                   Blockchain Layer
```

### Service Responsibilities

**Auth Service (8000)**: Authentication, authorization, user management
**AC Service (8001)**: Constitutional AI, compliance validation
**Integrity Service (8002)**: Cryptographic verification, hash validation
**FV Service (8003)**: Formal verification, mathematical proofs
**GS Service (8004)**: Governance synthesis, policy generation
**PGC Service (8005)**: Policy governance, compliance enforcement
**EC Service (8006)**: Executive council, oversight management
**DGM Service (8007)**: Darwin Gödel Machine, self-evolving AI governance

### Data Flow

1. **User Request** → Auth Service (authentication)
2. **Authenticated Request** → Target Service
3. **Constitutional Validation** → PGC Service
4. **Policy Synthesis** → GS Service (if needed)
5. **Formal Verification** → FV Service (if needed)
6. **DGM Evolution** → DGM Service (self-improvement)
7. **Event Broadcasting** → NATS Message Broker
8. **Blockchain Recording** → Quantumagi Programs

### DGM Event-Driven Architecture

```
NATS Message Broker ← → DGM Service (8007)
        ↓                    ↓
Service Mesh (Istio)    LSU Interface
        ↓                    ↓
Core Services          SEE Platform
        ↓                    ↓
Constitutional      Archive-backed
Validation          Evolution Loops
```

## Coding Standards

### Python Standards

```python
# File structure
"""
Module docstring describing purpose and usage.
"""

import os
import sys
from typing import Dict, List, Optional
import asyncio

# Constants
CONSTITUTION_HASH = "cdd01ef066bc6cf2"
DEFAULT_TIMEOUT = 30

class ServiceManager:
    """Manages ACGS service lifecycle."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize service manager.

        Args:
            config: Service configuration dictionary
        """
        self.config = config
        self._services: List[Service] = []

    async def start_service(self, service_name: str) -> bool:
        """Start a specific service.

        Args:
            service_name: Name of service to start

        Returns:
            True if service started successfully

        Raises:
            ServiceError: If service fails to start
        """
        try:
            # Implementation
            return True
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            raise ServiceError(f"Service startup failed: {e}")
```

### TypeScript/React Standards

```typescript
// Component structure
import React, { useState, useEffect } from 'react';
import { ConstitutionalPrinciple, GovernanceWorkflow } from '../types';

interface PolicyCreationProps {
  /** Current user context */
  user: User;
  /** Callback when policy is created */
  onPolicyCreated: (policy: Policy) => void;
  /** Optional initial policy data */
  initialData?: Partial<Policy>;
}

/**
 * Policy creation component with constitutional validation
 */
export const PolicyCreation: React.FC<PolicyCreationProps> = ({
  user,
  onPolicyCreated,
  initialData
}) => {
  const [policy, setPolicy] = useState<Partial<Policy>>(initialData || {});
  const [isValidating, setIsValidating] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsValidating(true);

    try {
      // Validate constitutional compliance
      const validation = await validateConstitutionalCompliance(policy);
      if (!validation.compliant) {
        throw new Error('Policy violates constitutional principles');
      }

      // Create policy
      const createdPolicy = await createPolicy(policy);
      onPolicyCreated(createdPolicy);
    } catch (error) {
      console.error('Policy creation failed:', error);
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="policy-creation">
      {/* Component implementation */}
    </form>
  );
};
```

### Rust/Solana Standards

```rust
//! Quantumagi Constitution Program
//!
//! Manages constitutional governance on Solana blockchain

use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};

declare_id!("ConstitutionProgramId");

/// Constitution account storing governance hash
#[account]
pub struct Constitution {
    /// Constitutional hash for validation
    pub hash: [u8; 32],
    /// Authority that can update constitution
    pub authority: Pubkey,
    /// Timestamp of last update
    pub last_updated: i64,
    /// Version number
    pub version: u64,
}

/// Initialize constitution with hash cdd01ef066bc6cf2
#[derive(Accounts)]
pub struct InitializeConstitution<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 32 + 8 + 8
    )]
    pub constitution: Account<'info, Constitution>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[program]
pub mod constitution {
    use super::*;

    /// Initialize constitution with specific hash
    pub fn initialize(
        ctx: Context<InitializeConstitution>,
        hash: [u8; 32],
    ) -> Result<()> {
        let constitution = &mut ctx.accounts.constitution;
        constitution.hash = hash;
        constitution.authority = ctx.accounts.authority.key();
        constitution.last_updated = Clock::get()?.unix_timestamp;
        constitution.version = 1;

        msg!("Constitution initialized with hash: {:?}", hash);
        Ok(())
    }
}
```

## Testing Procedures

### Unit Testing

```bash
# Python tests
pytest tests/unit/ -v --cov=src --cov-report=html

# TypeScript tests
npm test -- --coverage

# Rust tests
cd blockchain && cargo test
```

### Integration Testing

```bash
# Service integration tests
pytest tests/integration/ -v

# End-to-end governance workflow tests
python3 tests/e2e/test_governance_workflows.py

# Blockchain integration tests
cd blockchain && anchor test
```

### Performance Testing

```bash
# Load testing
python3 tests/performance/load_test.py --concurrent-users 1000

# Response time testing
python3 tests/performance/response_time_test.py --target-latency 500ms
```

### Constitutional Compliance Testing

```bash
# Validate constitution hash integrity
python3 tests/constitutional/test_hash_validation.py

# Test governance workflow compliance
python3 tests/constitutional/test_workflow_compliance.py
```

## Governance Workflow Development

### Policy Creation Workflow

```python
async def create_policy_workflow(policy_data: Dict) -> WorkflowResult:
    """Complete policy creation workflow with constitutional validation."""

    # 1. Constitutional compliance check
    compliance = await validate_constitutional_compliance(policy_data)
    if not compliance.valid:
        raise ConstitutionalViolationError(compliance.violations)

    # 2. Policy synthesis (if needed)
    if policy_data.get('auto_generate'):
        synthesized = await synthesize_policy(policy_data['requirements'])
        policy_data.update(synthesized)

    # 3. Formal verification
    verification = await formally_verify_policy(policy_data)
    if not verification.valid:
        raise VerificationError(verification.errors)

    # 4. Multi-signature approval
    approval = await request_council_approval(policy_data)
    if not approval.approved:
        raise ApprovalError("Insufficient council signatures")

    # 5. Blockchain recording
    tx_hash = await record_on_blockchain(policy_data)

    return WorkflowResult(
        policy_id=policy_data['id'],
        status='approved',
        tx_hash=tx_hash,
        constitutional_hash=CONSTITUTION_HASH
    )
```

### Adding New Governance Workflows

1. **Define Workflow Schema**: Create workflow definition in `schemas/workflows/`
2. **Implement Workflow Logic**: Add workflow handler in `services/core/policy-governance/`
3. **Add Constitutional Validation**: Ensure compliance with Constitution Hash
4. **Create Tests**: Unit, integration, and end-to-end tests
5. **Update Documentation**: API docs and user guides

## Quantumagi Solana Integration

### Program Development

```bash
# Initialize new program
cd blockchain/programs
anchor init new_program

# Build and test
anchor build
anchor test

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

### Client Integration

```typescript
// Connect to Quantumagi programs
import { Program, AnchorProvider, web3 } from '@coral-xyz/anchor';
import { Constitution } from '../target/types/constitution';

const provider = AnchorProvider.env();
const program = new Program<Constitution>(idl, programId, provider);

// Validate constitution hash
const validateConstitution = async (hash: string) => {
  const [constitutionPDA] = web3.PublicKey.findProgramAddressSync(
    [Buffer.from('constitution')],
    program.programId
  );

  const constitution = await program.account.constitution.fetch(constitutionPDA);
  return constitution.hash.toString() === hash;
};
```

### Testing Blockchain Integration

```bash
# Test constitution program
cd blockchain && anchor test tests/constitution.ts

# Test policy program
cd blockchain && anchor test tests/policy.ts

# Test logging program
cd blockchain && anchor test tests/logging.ts

# Integration test with off-chain services
python3 tests/blockchain/test_integration.py
```

## Contribution Guidelines

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/constitutional-validation-enhancement

# 2. Make changes with atomic commits
git add .
git commit -m "feat(pgc): enhance constitutional validation with caching

- Add Redis caching for validation results
- Implement cache invalidation on constitution updates
- Improve response times by 60%
- Maintain Constitution Hash cdd01ef066bc6cf2 integrity

Closes #123"

# 3. Push and create PR
git push origin feature/constitutional-validation-enhancement
```

### Commit Message Format

```
type(scope): brief description

- Detailed change 1
- Detailed change 2
- Performance impact or security considerations

Closes #issue_number
```

**Types**: feat, fix, docs, style, refactor, test, chore  
**Scopes**: auth, ac, integrity, fv, gs, pgc, ec, blockchain, docs

### Pull Request Process

1. **Create PR** with descriptive title and detailed description
2. **Link Issues** using "Closes #123" syntax
3. **Add Labels** for type, priority, and affected services
4. **Request Reviews** from relevant team members
5. **Pass CI/CD** checks including tests and security scans
6. **Address Feedback** and update PR as needed
7. **Merge** after approval (squash and merge preferred)

### Code Review Checklist

- [ ] Constitutional compliance maintained
- [ ] Performance targets met (<500ms response times)
- [ ] Security best practices followed
- [ ] Tests added/updated with >80% coverage
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Backward compatibility considered

## Deployment & Release Process

### Development Deployment

```bash
# Deploy to development environment
bash scripts/deploy_development.sh

# Run health checks
python3 scripts/comprehensive_health_check.py

# Validate governance workflows
python3 tests/e2e/test_governance_workflows.py
```

### Production Deployment

```bash
# Create release branch
git checkout -b release/v3.1.0

# Update version numbers
./scripts/update_version.sh 3.1.0

# Deploy to staging
bash scripts/deploy_staging.sh

# Run full test suite
bash scripts/run_full_tests.sh

# Deploy to production (after approval)
bash scripts/deploy_production.sh
```

### Release Checklist

- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Constitutional compliance verified
- [ ] Backup procedures tested
- [ ] Rollback plan prepared

---

**Welcome to the ACGS-1 development team! Together, we're building the future of democratic governance through technology.**

**Questions?** Contact the development team or check our internal documentation.

## Development Best Practices

### Constitutional Compliance Development

Every feature must maintain constitutional compliance:

```python
# Always validate constitutional compliance
async def implement_feature(data: Dict) -> Result:
    # 1. Check constitutional compliance first
    compliance = await validate_constitutional_compliance(data)
    if not compliance.valid:
        raise ConstitutionalViolationError(
            f"Feature violates constitution: {compliance.violations}"
        )

    # 2. Implement feature logic
    result = await process_feature(data)

    # 3. Record governance action on blockchain
    await record_governance_action(result, CONSTITUTION_HASH)

    return result
```

### Performance Optimization Guidelines

- **Response Time Target**: <500ms for 95% of requests
- **Concurrent Users**: Support >1000 concurrent governance actions
- **Database Queries**: Optimize for <100ms execution time
- **Cache Strategy**: Implement Redis caching for frequently accessed data
- **Memory Usage**: Monitor and optimize service memory consumption

### Security Development Practices

- **Input Validation**: Validate all inputs at service boundaries
- **Authentication**: Use JWT tokens with proper expiration
- **Authorization**: Implement role-based access control
- **Encryption**: Use TLS 1.3 for all communications
- **Audit Logging**: Log all governance actions with constitutional hash

### Monitoring & Observability

```python
# Add metrics to all new features
from prometheus_client import Counter, Histogram

feature_requests = Counter(
    'acgs_feature_requests_total',
    'Total feature requests',
    ['feature_name', 'status']
)

feature_duration = Histogram(
    'acgs_feature_duration_seconds',
    'Feature execution time',
    ['feature_name']
)

@feature_duration.time()
async def new_feature():
    try:
        result = await implement_feature()
        feature_requests.labels(feature_name='new_feature', status='success').inc()
        return result
    except Exception as e:
        feature_requests.labels(feature_name='new_feature', status='error').inc()
        raise
```

## Troubleshooting Development Issues

### Common Development Problems

**Service Won't Start**:

```bash
# Check port conflicts
netstat -tulpn | grep :8005

# Check dependencies
pip check
npm audit

# Check environment variables
env | grep ACGS
```

**Tests Failing**:

```bash
# Run specific test with verbose output
pytest tests/test_specific.py -v -s

# Check test database
psql -h localhost -p 5432 -U acgs_user -d acgs_test_db

# Reset test environment
python scripts/reset_test_environment.py
```

**Constitutional Validation Errors**:

```bash
# Verify constitution hash
curl -s http://localhost:8005/api/v1/constitutional/validate | jq '.constitutional_hash'

# Check blockchain connectivity
cd blockchain && solana config get

# Validate Quantumagi programs
cd blockchain && anchor test --skip-build
```

### Getting Help

- **Internal Documentation**: Check `/docs` directory
- **Team Chat**: Use internal communication channels
- **Code Reviews**: Ask for help in PR comments
- **Architecture Questions**: Contact system architects
- **Emergency Issues**: Follow escalation procedures in operational runbooks

---

**Document Maintained By**: ACGS-1 Development Team
**Last Updated**: 2025-06-16
**Next Review**: 2025-07-16
