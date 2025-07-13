<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS-1 Blockchain Layer

This directory contains the Solana/Anchor programs that implement on-chain constitutional governance for ACGS-1.

## Overview

The blockchain layer provides decentralized, transparent, and immutable governance capabilities through Solana smart contracts built with the Anchor framework.

## 🔒 Security Policy

Found a security vulnerability? Please report it responsibly:

- **Email**: dev@quantumagi.org
- **GitHub**: Open a private security advisory
- **Response Time**: We aim to respond within 24 hours

**Do NOT** open public issues for security vulnerabilities.

## Directory Structure

```
blockchain/
├── programs/                    # Anchor programs (smart contracts)
│   ├── blockchain/        # Main governance program
│   ├── appeals/                # Appeals handling program
│   └── logging/                # Event logging program
├── client/                     # TypeScript client libraries
├── tests/                      # Anchor test suites
├── scripts/                    # Deployment and utility scripts
├── Anchor.toml                 # Anchor configuration
├── Cargo.toml                  # Rust workspace configuration
└── package.json                # Node.js dependencies
```

## Programs

### Quantumagi Core Program (`programs/blockchain/`)

**Purpose**: Main constitutional governance enforcement

- Constitutional principle storage and validation
- Policy proposal and voting mechanisms
- Real-time compliance checking (PGC)
- Democratic governance workflows

**Key Features**:

- Constitution account management
- Policy account creation and validation
- Voting and consensus mechanisms
- PGC (Protective Governance Controls) enforcement

**Program ID**: `QuantumagiCoreProgram111111111111111111111`

### Appeals Program (`programs/appeals/`)

**Purpose**: Governance appeals and dispute resolution

- Appeal submission and processing
- Dispute resolution workflows
- Appeal voting and consensus
- Resolution enforcement

**Key Features**:

- Appeal account management
- Dispute resolution mechanisms
- Appeal voting systems
- Resolution tracking

**Program ID**: `AppealsProgram1111111111111111111111111`

### Logging Program (`programs/logging/`)

**Purpose**: Comprehensive audit trail and event logging

- Governance event logging
- Audit trail maintenance
- Event querying and retrieval
- Compliance reporting

**Key Features**:

- Event log storage
- Query mechanisms
- Audit trail verification
- Compliance reporting

**Program ID**: `LoggingProgram1111111111111111111111111`

## Client Libraries (`client/`)

### TypeScript Client

Provides easy integration with the Anchor programs:

```typescript
import { QuantumagiClient } from './client/quantumagi-client';

const client = new QuantumagiClient(connection, wallet);

// Create constitution
await client.createConstitution(constitutionData);

// Submit policy proposal
await client.submitPolicyProposal(policyData);

// Vote on proposal
await client.voteOnProposal(proposalId, vote);
```

### Python Client

Python bindings for backend service integration:

```python
from quantumagi_client import QuantumagiClient

client = QuantumagiClient(rpc_url, keypair)

# Check policy compliance
result = await client.check_policy_compliance(policy_id)

# Get governance events
events = await client.get_governance_events(start_time, end_time)
```

## Development Setup (Rust-First)

### Prerequisites

- **Rust** 1.81.0+ (primary development language)
- **Solana CLI** v1.18.22+
- **Anchor Framework** v0.29.0+

### Installation

```bash
# Install Rust 1.81.0+
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup install 1.81.0
rustup default 1.81.0
rustup target add wasm32-unknown-unknown bpf-unknown-unknown

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"

# Install Anchor
npm install -g @coral-xyz/anchor-cli@0.29.0

# Build Rust tools
cd scripts && cargo build --release
```

### Building Programs (Rust-First)

```bash
# Build Rust tools and workspace
cd scripts && cargo build --release

# Build all Anchor programs
anchor build

# Build specific program
anchor build --program quantumagi-core
```

### Testing (Rust-First)

```bash
# Run Rust integration tests (primary)
cd scripts && cargo test --release

# Run legacy Anchor tests
anchor test

# Run specific Rust test module
cargo test governance_tests --release

# Run tests with detailed output
cargo test -- --nocapture
```

### Local Development (Rust-First)

```bash
# Start local Solana validator
solana-test-validator

# Deploy using Rust tools
cd scripts && cargo run --bin deploy_quantumagi -- deploy

# Validate deployment using Rust tools
cargo run --bin validate_deployment -- --cluster localhost

# Initialize constitution using Rust tools
cargo run --bin initialize_constitution -- --cluster localhost
```

## Deployment

### Devnet Deployment (Rust-First)

```bash
# Deploy complete stack using Rust tools
cd scripts && cargo run --bin deploy_quantumagi -- deploy --cluster devnet

# Or deploy step-by-step:
solana config set --url devnet
anchor deploy --provider.cluster devnet
cargo run --bin initialize_constitution -- --cluster devnet
cargo run --bin validate_deployment -- --cluster devnet
```

### Mainnet Deployment (Rust-First)

```bash
# Deploy to mainnet using Rust tools
cd scripts && cargo run --bin deploy_quantumagi -- deploy --cluster mainnet-beta

# Validate mainnet deployment
cargo run --bin validate_deployment -- --cluster mainnet-beta --verbose
```

### Deployment Tools

All deployment operations now use native Rust tools:

- **deploy_quantumagi**: Complete deployment orchestration
- **initialize_constitution**: Constitution setup and validation
- **validate_deployment**: Deployment verification and testing
- **key_management**: Keypair generation and management
- **generate_program_ids**: Program ID management

### Dependency Management (Rust-First)

```bash
# Update Rust dependencies (primary)
cd scripts && cargo update

# Build all Rust tools
cargo build --release

# Security audit (Rust-first)
cargo audit --deny warnings
cargo deny check

# Check for outdated dependencies
cargo outdated

# Legacy Node.js dependencies (minimal usage)
npm update --legacy-peer-deps
```

## Account Structure

### Constitution Account

```rust
#[account]
pub struct Constitution {
    pub authority: Pubkey,
    pub principles: Vec<Principle>,
    pub meta_rules: Vec<MetaRule>,
    pub created_at: i64,
    pub updated_at: i64,
    pub version: u32,
}
```

### Policy Account

```rust
#[account]
pub struct Policy {
    pub id: Pubkey,
    pub constitution: Pubkey,
    pub content: String,
    pub status: PolicyStatus,
    pub votes: Vec<Vote>,
    pub created_at: i64,
}
```

### Appeal Account

```rust
#[account]
pub struct Appeal {
    pub id: Pubkey,
    pub policy: Pubkey,
    pub appellant: Pubkey,
    pub reason: String,
    pub status: AppealStatus,
    pub resolution: Option<String>,
}
```

## Integration with Backend Services

### Quantumagi Bridge

The blockchain layer integrates with backend services through the Quantumagi Bridge:

```typescript
// Event monitoring
client.onGovernanceEvent((event) => {
  // Forward to backend services
  backendClient.processGovernanceEvent(event);
});

// Policy compliance checking
const compliance = await client.checkPolicyCompliance(policyId);
```

### Real-time Synchronization

- **Event Listeners**: Monitor on-chain events
- **State Synchronization**: Keep backend services in sync
- **Cross-chain Coordination**: Coordinate with other blockchains

## Security Considerations

### Program Security

- **Access Control**: Multi-signature requirements for critical operations
- **Input Validation**: Comprehensive validation of all inputs
- **Reentrancy Protection**: Protection against reentrancy attacks
- **Overflow Protection**: Safe arithmetic operations

### Key Management

- **Hardware Security Modules**: Secure key storage
- **Multi-signature Wallets**: Distributed key management
- **Key Rotation**: Regular key rotation procedures
- **Backup and Recovery**: Secure key backup procedures

### Audit and Compliance

- **Code Audits**: Regular security audits
- **Formal Verification**: Mathematical proof of correctness
- **Compliance Monitoring**: Continuous compliance checking
- **Incident Response**: Security incident response procedures

## Monitoring and Analytics

### On-chain Metrics

- **Transaction Volume**: Governance transaction metrics
- **Account Growth**: Constitution and policy account growth
- **Voting Participation**: Democratic participation metrics
- **Compliance Rates**: Policy compliance statistics

### Performance Monitoring

- **Transaction Latency**: Transaction confirmation times
- **Throughput**: Transactions per second
- **Error Rates**: Failed transaction analysis
- **Resource Usage**: Compute unit consumption

## Documentation

- **[Program Documentation](programs/README.md)**: Detailed program documentation
- **[Client Documentation](client/README.md)**: Client library documentation
- **[API Reference](../docs/api/README.md)**: Complete API reference
- **[Deployment Guide](../docs/deployment/README.md)**: Deployment instructions

## Examples

### Basic Usage

```typescript
// Initialize client
const client = new QuantumagiClient(connection, wallet);

// Create constitution
const constitution = await client.createConstitution({
  principles: [
    { name: 'Transparency', description: 'All governance actions must be transparent' },
    { name: 'Accountability', description: 'All actors must be accountable' },
  ],
});

// Submit policy proposal
const proposal = await client.submitPolicyProposal({
  constitution: constitution.publicKey,
  content: 'Policy content here',
  metadata: { category: 'governance' },
});

// Vote on proposal
await client.voteOnProposal(proposal.publicKey, { approve: {} });
```

---

**Blockchain Layer**: Decentralized constitutional governance on Solana ⚡🏛️
