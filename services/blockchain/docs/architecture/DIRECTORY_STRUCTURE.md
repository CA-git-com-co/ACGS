# ACGS-2 Blockchain Service - Directory Structure

**Constitutional Hash: `cdd01ef066bc6cf2`**

This document describes the organized directory structure of the ACGS-2 Blockchain Service.

## 📁 Top-Level Structure

### Core Components

#### `programs/` - Solana Programs (Smart Contracts)
- **quantumagi-core/**: Main governance smart contract
- **appeals/**: Appeals handling system
- **logging/**: Immutable event logging

#### `client/` - Client Libraries
- **rust/**: Rust SDK for blockchain interaction
- **python/**: Python SDK for integration

#### `shared/` - Shared Libraries
- **constitutional/**: Constitutional compliance utilities
- **types/**: Common type definitions
- **monitoring/**: Shared monitoring components

### Infrastructure

#### `infrastructure/` - Infrastructure Components
- **monitoring/**: Observability, metrics, and health checks
- **security/**: Security infrastructure and formal verification
- **cache/**: Caching layer and optimization
- **cost_optimization/**: Cost analysis and optimization
- **connection_pool/**: Database connection management
- **governance/**: Advanced governance features
- **deployment/**: Deployment configurations

### Development & Testing

#### `tests/` - Test Suites
- **unit/**: Rust unit tests
- **integration/**: JavaScript/TypeScript integration tests  
- **performance/**: Python performance and load tests

#### `tools/` - Development Tools
- **scripts/**: Deployment and utility scripts
- **benchmarks/**: Performance benchmarking tools
- **validation/**: Testing and validation utilities

### Documentation & Configuration

#### `docs/` - Documentation
- **reports/**: Test reports, audit results, validation summaries
- **architecture/**: Architecture documentation and guides
- **deployment/**: Deployment guides and runbooks

#### `config/` - Configuration Files
- **docker/**: Docker and container configurations
- **environment/**: Environment-specific configurations
- **deployment/**: Deployment scripts and configurations

#### `artifacts/` - Build Artifacts
- **images/**: Generated charts, diagrams, visualizations
- **data/**: Test data, benchmarks, performance metrics
- **configuration/**: Runtime configuration files

## 🏗️ Detailed Structure

```
blockchain/
├── 📋 Core Configuration
│   ├── Cargo.toml              # Rust workspace configuration
│   ├── package.json            # Node.js dependencies
│   ├── Anchor.toml             # Anchor framework configuration
│   ├── tsconfig.json           # TypeScript configuration
│   └── README.md               # Main documentation
│
├── 🔧 Infrastructure Components
│   ├── infrastructure/
│   │   ├── monitoring/         # System observability
│   │   ├── security/           # Security infrastructure
│   │   ├── cache/              # Performance caching
│   │   ├── cost_optimization/  # Cost analysis
│   │   ├── connection_pool/    # Database connections
│   │   └── governance/         # Advanced governance
│   │
│   ├── shared/                 # Shared utilities
│   │   ├── constitutional/     # Constitutional compliance
│   │   ├── types/              # Common type definitions
│   │   └── monitoring/         # Monitoring utilities
│   │
│   └── expert-service/         # Expert system integration
│       ├── crates/             # Expert system crates
│       └── bin/                # Binary executables
│
├── 💻 Programs & Clients
│   ├── programs/               # Solana smart contracts
│   │   ├── quantumagi-core/    # Main governance program
│   │   ├── appeals/            # Appeals system
│   │   └── logging/            # Event logging
│   │
│   └── client/                 # Client libraries
│       ├── rust/               # Rust SDK
│       └── python/             # Python SDK
│
├── 🧪 Testing & Tools
│   ├── tests/                  # Test suites
│   │   ├── unit/               # Rust unit tests
│   │   ├── integration/        # JS/TS integration tests
│   │   └── performance/        # Python performance tests
│   │
│   └── tools/                  # Development tools
│       ├── scripts/            # Utility scripts
│       ├── benchmarks/         # Performance tools
│       └── validation/         # Testing tools
│
├── 📚 Documentation & Config
│   ├── docs/                   # Documentation
│   │   ├── reports/            # Reports & summaries
│   │   ├── architecture/       # Architecture docs
│   │   └── deployment/         # Deployment guides
│   │
│   ├── config/                 # Configuration
│   │   ├── docker/             # Container configs
│   │   ├── environment/        # Environment configs
│   │   └── deployment/         # Deployment configs
│   │
│   └── artifacts/              # Build artifacts
│       ├── images/             # Charts & diagrams
│       ├── data/               # Test data
│       └── configuration/      # Runtime configs
```

## 🔗 Component Relationships

### Core Program Dependencies
- **quantumagi-core** → shared/constitutional, shared/types
- **appeals** → quantumagi-core, shared/constitutional  
- **logging** → shared/types, shared/monitoring

### Infrastructure Dependencies
- **monitoring** → shared/monitoring, shared/types
- **cache** → shared/types
- **cost_optimization** → programs/*, shared/types
- **security** → shared/constitutional

### Client Dependencies
- **rust client** → programs/*, shared/types
- **python client** → programs/*, configuration files

## 📋 File Organization Principles

### 1. **Separation of Concerns**
- Core blockchain logic in `programs/`
- Infrastructure components in `infrastructure/`
- Client libraries in `client/`
- Testing isolated in `tests/`

### 2. **Constitutional Compliance**
- All components reference constitutional hash `cdd01ef066bc6cf2`
- Shared constitutional utilities in `shared/constitutional/`
- Compliance validation throughout all layers

### 3. **Development Workflow**
- Development tools centralized in `tools/`
- Configuration separated by environment in `config/`
- Documentation organized by type in `docs/`

### 4. **Build & Deployment**
- Artifacts generated in `artifacts/`
- Deployment configurations in `config/deployment/`
- Build outputs isolated from source code

## 🚀 Getting Started

### Quick Navigation
- **Start here**: [README.md](../../README.md)
- **Build instructions**: [docs/deployment/](../deployment/)
- **Testing guide**: [tests/README.md](../../tests/README.md)
- **API documentation**: [Generated from code]

### Common Tasks
```bash
# Build all components
cargo build --workspace

# Run all tests
./tools/validation/run_comprehensive_tests.sh

# Deploy to devnet
./config/deployment/deploy_to_devnet.sh

# Monitor system health
./tools/validation/health_check.sh
```

---
**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Directory Structure Version**: 2.0 - Organized & Optimized