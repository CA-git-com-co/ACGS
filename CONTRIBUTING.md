# Contributing to ACGS-1

Welcome to the ACGS-1 (Autonomous Constitutional Governance System) project! This guide will help you get started with contributing to our blockchain-focused constitutional governance platform.

## 🏗️ Project Structure

ACGS-1 follows a blockchain-first architecture:

```
ACGS-1/
├── blockchain/                 # 🔗 Solana/Anchor Programs
├── services/                   # 🏗️ Backend Microservices
├── applications/               # 🖥️ Frontend Applications
├── integrations/               # 🔗 Integration Layer
├── infrastructure/             # 🏗️ Infrastructure & Ops
├── tools/                      # 🛠️ Development Tools
├── tests/                      # 🧪 Test Suites
└── docs/                       # 📚 Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Rust** 1.75.0+ (for Anchor programs)
- **Solana CLI** 1.18.22+ (for blockchain development)
- **Anchor CLI** 0.29.0+ (for smart contract framework)
- **Node.js** 18+ (for TypeScript/React development)
- **Python** 3.11+ (for backend services)
- **Docker** & **Docker Compose** (for containerization)

### Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CA-git-com-co/ACGS.git
   cd ACGS-1
   ```

2. **Install Solana & Anchor** (for blockchain development):
   ```bash
   # Install Solana CLI
   sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
   
   # Install Anchor CLI
   cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
   avm install 0.29.0
   avm use 0.29.0
   ```

3. **Set up Python environment** (for backend services):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies** (for frontend applications):
   ```bash
   cd applications/governance-dashboard
   npm install
   cd ../..
   ```

5. **Build Anchor programs**:
   ```bash
   cd blockchain
   anchor build
   cd ..
   ```

## 🎯 Development Workflows

### Blockchain Development

**Location**: `blockchain/programs/`

1. **Program Development**:
   ```bash
   cd blockchain
   anchor build                    # Build all programs
   anchor test                     # Run tests
   anchor deploy --provider.cluster devnet  # Deploy to devnet
   ```

2. **Adding New Programs**:
   - Create program in `blockchain/programs/your-program/`
   - Update `blockchain/Anchor.toml`
   - Add tests in `blockchain/tests/`

### Backend Service Development

**Location**: `services/core/` or `services/platform/`

1. **Core Services** (Constitutional AI, Governance Synthesis, etc.):
   ```bash
   cd services/core/your-service
   python -m uvicorn app.main:app --reload --port 800X
   ```

2. **Platform Services** (Authentication, Integrity, etc.):
   ```bash
   cd services/platform/your-service
   python -m uvicorn app.main:app --reload --port 800X
   ```

3. **Service Communication**:
   - Use `services/shared/` for common utilities
   - Follow port conventions (8000-8006 for core services)
   - Implement health checks at `/health` endpoint

### Frontend Development

**Location**: `applications/`

1. **Governance Dashboard**:
   ```bash
   cd applications/governance-dashboard
   npm start                       # Development server
   npm run build                   # Production build
   ```

2. **Component Development**:
   - Follow React best practices
   - Use TypeScript for type safety
   - Integrate with Anchor client libraries

### Integration Development

**Location**: `integrations/`

1. **Quantumagi Bridge**: Blockchain-backend integration
2. **AlphaEvolve Engine**: AI governance integration

## 🧪 Testing Guidelines

### Test Organization

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **End-to-End Tests**: `tests/e2e/`
- **Performance Tests**: `tests/performance/`

### Running Tests

```bash
# Anchor program tests
cd blockchain && anchor test

# Python service tests
python -m pytest tests/unit/
python -m pytest tests/integration/

# Frontend tests
cd applications/governance-dashboard && npm test

# Full test suite
./run_tests.sh
```

### Test Requirements

- **Anchor Programs**: >80% test coverage
- **Backend Services**: Comprehensive unit and integration tests
- **Frontend**: Component and integration tests
- **End-to-End**: Complete governance workflow validation

## 📋 Code Review Guidelines

### Service Boundaries

1. **Blockchain Components**: Focus on Solana/Anchor best practices
2. **Core Services**: Ensure constitutional governance compliance
3. **Platform Services**: Maintain security and scalability standards
4. **Frontend**: Prioritize user experience and accessibility

### Review Checklist

- [ ] Code follows project structure conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Constitutional compliance maintained

## 🔧 Development Tools

### Available Scripts

- `./run_tests.sh` - Run comprehensive test suite
- `./scripts/health_check.sh` - Check service health
- `./blockchain/quantumagi-deployment/deploy_quantumagi_devnet.sh` - Deploy to Solana devnet

### IDE Configuration

- **VS Code**: Recommended extensions for Rust, Python, TypeScript
- **Rust Analyzer**: For Anchor program development
- **Python Language Server**: For backend service development

## 🚀 Deployment Process

### Development Deployment

1. **Local Development**:
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.yml up -d
   ```

2. **Solana Devnet**:
   ```bash
   cd blockchain/quantumagi-deployment
   ./deploy_quantumagi_devnet.sh
   ```

### Production Deployment

- Follow deployment guides in `docs/deployment/`
- Use CI/CD pipelines in `.github/workflows/`
- Ensure all tests pass before deployment

## 🎯 Performance Targets

- **Response Times**: <2s for 95% of requests
- **Availability**: >99.5% uptime
- **Governance Costs**: <0.01 SOL per governance action
- **Test Coverage**: >80% for Anchor programs
- **Concurrent Users**: >1000 simultaneous governance actions

## 🤝 Community Guidelines

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions with detailed descriptions
- **Discussions**: Architecture and design conversations

### Code of Conduct

- Respectful and inclusive communication
- Focus on constitutional governance principles
- Collaborative problem-solving approach
- Commitment to transparency and accountability

## 📚 Additional Resources

- **Architecture Overview**: `docs/architecture/REORGANIZED_ARCHITECTURE.md`
- **API Documentation**: `docs/api/`
- **Deployment Guides**: `docs/deployment/`
- **Developer Guides**: `docs/development/`

## 🆘 Getting Help

1. **Documentation**: Check relevant docs in `docs/` directory
2. **Issues**: Search existing GitHub issues
3. **Discussions**: Start a GitHub discussion for questions
4. **Code Review**: Request review from maintainers

Thank you for contributing to ACGS-1! Together, we're building the future of constitutional governance on the blockchain.
