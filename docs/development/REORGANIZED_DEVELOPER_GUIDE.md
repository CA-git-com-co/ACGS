# ACGS-1 Reorganized Developer Guide

This comprehensive guide provides instructions and best practices for developers contributing to the reorganized ACGS-1 system with blockchain integration.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Reorganized Project Structure](#reorganized-project-structure)
3. [Development Environment Setup](#development-environment-setup)
4. [Blockchain Development](#blockchain-development)
5. [Service Development](#service-development)
6. [Frontend Development](#frontend-development)
7. [Testing Guidelines](#testing-guidelines)
8. [Development Workflow](#development-workflow)
9. [Security Guidelines](#security-guidelines)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- **Rust 1.81.0+**: Primary blockchain development language
- **Solana CLI v1.18.22+**: Blockchain development
- **Anchor Framework v0.29.0+**: Solana program framework
- **Python 3.9+**: Backend service development
- **Node.js 18+**: Frontend development only
- **Docker & Docker Compose**: Containerization and local development
- **PostgreSQL 15+**: Primary database
- **Redis 7+**: Caching and session storage
- **Git**: Version control

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-1

# Install blockchain dependencies
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
npm install -g @coral-xyz/anchor-cli@0.29.0

# Install project dependencies
./scripts/setup/install_dependencies.sh

# Set up environment
cp config/environments/.env.example .env
# Edit .env with your configuration

# Start development environment
./scripts/setup/start_development.sh

# Verify setup
./scripts/validation/validate_deployment.py
```

## Reorganized Project Structure

```
ACGS-1/
├── blockchain/                          # 🔗 Solana/Anchor Programs
│   ├── programs/                        # Smart contracts
│   │   ├── blockchain/            # Main governance program
│   │   ├── appeals/                    # Appeals handling
│   │   └── logging/                    # Event logging
│   ├── client/                         # Blockchain client libraries
│   ├── tests/                          # Anchor tests
│   └── scripts/                        # Deployment scripts
│
├── services/                           # 🏗️ Backend Microservices
│   ├── core/                           # Core governance services
│   │   ├── constitutional-ai/          # Constitutional principles
│   │   ├── governance-synthesis/       # Policy synthesis
│   │   ├── policy-governance/          # Real-time enforcement
│   │   └── formal-verification/        # Mathematical verification
│   ├── platform/                       # Platform services
│   │   ├── authentication/             # User auth & authorization
│   │   ├── integrity/                  # Cryptographic integrity
│   │   └── workflow/                   # Workflow orchestration
│   ├── research/                       # Research services
│   │   ├── federated-evaluation/       # Distributed evaluation
│   │   └── research-platform/          # Research infrastructure
│   └── shared/                         # Shared libraries
│
├── applications/                       # 🖥️ Frontend Applications
│   ├── governance-dashboard/           # Main governance interface
│   ├── constitutional-council/         # Council management
│   ├── public-consultation/            # Public participation
│   └── admin-panel/                    # Administrative interface
│
├── integrations/                       # 🔌 Integration Layer
│   ├── quantumagi-bridge/             # Blockchain-Backend bridge
│   ├── alphaevolve-engine/            # AlphaEvolve integration
│   └── external-apis/                 # External service integrations
│
├── infrastructure/                     # 🏗️ Infrastructure
│   ├── docker/                        # Container configurations
│   ├── kubernetes/                    # Kubernetes manifests
│   ├── monitoring/                    # Monitoring & observability
│   └── deployment/                    # Deployment automation
│
├── tools/                             # 🛠️ Development Tools
├── docs/                              # 📚 Documentation
├── tests/                             # 🧪 Testing
├── scripts/                           # 📜 Utility Scripts
└── config/                            # ⚙️ Configuration
```

## Development Environment Setup

### Blockchain Development Setup (Rust-First)

```bash
# Set up Rust blockchain development environment
cd blockchain

# Build Rust tools and workspace
cd scripts && cargo build --release && cd ..

# Start local validator
solana-test-validator &

# Build programs
anchor build

# Run Rust integration tests (primary)
cd scripts && cargo test --release

# Run legacy Anchor tests (if needed)
anchor test

# Deploy using Rust tools
cd scripts && cargo run --bin deploy_quantumagi -- deploy --cluster localhost
```

### Backend Services Setup

```bash
# Set up Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Start individual services
cd services/core/constitutional-ai
python -m uvicorn app.main:app --reload --port 8001

# Or start all services with Docker
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

### Frontend Applications Setup

```bash
# Set up governance dashboard
cd applications/governance-dashboard
npm install
npm start

# Set up constitutional council interface
cd applications/constitutional-council
npm install
npm start
```

## Blockchain Development

### Anchor Program Development

```rust
// Example: Quantumagi Core Program
use anchor_lang::prelude::*;

#[program]
pub mod quantumagi_core {
    use super::*;

    pub fn create_constitution(
        ctx: Context<CreateConstitution>,
        principles: Vec<Principle>,
    ) -> Result<()> {
        let constitution = &mut ctx.accounts.constitution;
        constitution.authority = ctx.accounts.authority.key();
        constitution.principles = principles;
        constitution.created_at = Clock::get()?.unix_timestamp;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct CreateConstitution<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Constitution::INIT_SPACE
    )]
    pub constitution: Account<'info, Constitution>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

### Client Library Development

```typescript
// TypeScript client example
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import { QuantumagiCore } from './types/quantumagi_core';

export class QuantumagiClient {
  constructor(
    private program: Program<QuantumagiCore>,
    private provider: AnchorProvider
  ) {}

  async createConstitution(principles: Principle[]) {
    const constitution = Keypair.generate();

    return await this.program.methods
      .createConstitution(principles)
      .accounts({
        constitution: constitution.publicKey,
        authority: this.provider.wallet.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([constitution])
      .rpc();
  }
}
```

## Service Development

### Core Service Structure

```python
# Example: Constitutional AI Service
from fastapi import FastAPI, Depends
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title="Constitutional AI Service",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "constitutional-ai"}
```

### Service Communication

```python
# Inter-service communication example
import httpx
from app.core.config import settings

class GovernanceSynthesisClient:
    def __init__(self):
        self.base_url = settings.GOVERNANCE_SYNTHESIS_URL

    async def synthesize_policy(self, principles: List[Principle]) -> Policy:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/synthesize",
                json={"principles": [p.dict() for p in principles]}
            )
            return Policy(**response.json())
```

## Frontend Development

### React Component Structure

```typescript
// Example: Governance Dashboard Component
import React, { useState, useEffect } from 'react';
import { useQuantumagiClient } from '../hooks/useQuantumagiClient';

export const GovernanceDashboard: React.FC = () => {
    const [policies, setPolicies] = useState<Policy[]>([]);
    const client = useQuantumagiClient();

    useEffect(() => {
        const loadPolicies = async () => {
            const policies = await client.getPolicies();
            setPolicies(policies);
        };
        loadPolicies();
    }, [client]);

    return (
        <div className="governance-dashboard">
            <h1>Governance Dashboard</h1>
            <PolicyList policies={policies} />
        </div>
    );
};
```

### Blockchain Integration

```typescript
// Frontend blockchain integration
import { useWallet } from '@solana/wallet-adapter-react';
import { QuantumagiClient } from '../lib/quantumagi-client';

export const useQuantumagiClient = () => {
  const { connection, wallet } = useWallet();

  return useMemo(() => {
    if (!wallet || !connection) return null;
    return new QuantumagiClient(connection, wallet);
  }, [connection, wallet]);
};
```

## Testing Guidelines

### Blockchain Testing

```typescript
// Anchor test example
describe('quantumagi-core', () => {
  it('Creates a constitution', async () => {
    const constitution = Keypair.generate();
    const principles = [{ name: 'Transparency', description: 'All actions must be transparent' }];

    await program.methods
      .createConstitution(principles)
      .accounts({
        constitution: constitution.publicKey,
        authority: provider.wallet.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([constitution])
      .rpc();

    const constitutionAccount = await program.account.constitution.fetch(constitution.publicKey);

    expect(constitutionAccount.principles).toEqual(principles);
  });
});
```

### Service Testing

```python
# Service test example
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_principle():
    principle_data = {
        "name": "Transparency",
        "description": "All governance actions must be transparent"
    }

    response = client.post("/api/v1/principles", json=principle_data)
    assert response.status_code == 201
    assert response.json()["name"] == principle_data["name"]
```

### Integration Testing

```python
# Integration test example
async def test_policy_synthesis_workflow():
    # Create principle
    principle = await constitutional_ai_client.create_principle(principle_data)

    # Synthesize policy
    policy = await governance_synthesis_client.synthesize_policy([principle])

    # Verify policy
    verification = await formal_verification_client.verify_policy(policy)
    assert verification.is_valid

    # Deploy to blockchain
    tx_hash = await quantumagi_bridge.deploy_policy(policy)
    assert tx_hash is not None
```

## Development Workflow

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-governance-feature

# Make changes and commit
git add .
git commit -m "feat: add new governance feature"

# Push and create PR
git push origin feature/new-governance-feature
# Create PR on GitHub
```

### Code Quality

```bash
# Run linting and formatting
./scripts/maintenance/lint_and_format.sh

# Run security audit
./scripts/validation/security_audit.py

# Run tests
./scripts/validation/run_tests.sh
```

### Continuous Integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Solana
        run: sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
      - name: Setup Anchor
        run: npm install -g @coral-xyz/anchor-cli@0.29.0
      - name: Run blockchain tests
        run: cd blockchain && anchor test
      - name: Run service tests
        run: python -m pytest tests/
```

## Security Guidelines

### Blockchain Security

- **Access Control**: Use PDA-based authorization
- **Input Validation**: Validate all program inputs
- **Reentrancy Protection**: Prevent reentrancy attacks
- **Overflow Protection**: Use safe arithmetic operations

### Service Security

- **Authentication**: JWT token validation
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Prevent abuse and DoS attacks

### Data Protection

- **Encryption**: Encrypt sensitive data at rest and in transit
- **Key Management**: Secure key storage and rotation
- **Audit Logging**: Log all security-relevant events
- **Privacy**: Implement privacy-preserving mechanisms

## Troubleshooting

### Common Issues

**Blockchain Connection Issues**:

```bash
# Check Solana RPC connection
solana cluster-version

# Check program deployment
solana program show <program_id>
```

**Service Communication Issues**:

```bash
# Check service health
curl http://localhost:8001/health

# Check service logs
docker logs acgs-constitutional-ai
```

**Database Issues**:

```bash
# Check database connection
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Run migrations
cd migrations && alembic upgrade head
```

### Performance Optimization

```bash
# Monitor service performance
./scripts/monitoring/performance_monitor.sh

# Optimize database queries
./scripts/optimization/optimize_database.py

# Scale services
kubectl scale deployment constitutional-ai --replicas=3
```

---

**ACGS-1 Development**: Building the future of constitutional governance 🚀🏛️
