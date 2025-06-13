# ACGS-1: AI Compliance Governance System

[![Build Status](https://github.com/CA-git-com-co/ACGS/workflows/CI/badge.svg)](https://github.com/CA-git-com-co/ACGS/actions)
[![Security Scan](https://github.com/CA-git-com-co/ACGS/workflows/Secret%20Scanning%20and%20Security%20Validation/badge.svg)](https://github.com/CA-git-com-co/ACGS/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Solana](https://img.shields.io/badge/Solana-Devnet-purple)](https://explorer.solana.com/?cluster=devnet)
[![CI/CD Health](https://img.shields.io/badge/CI%2FCD%20Health-100%25-brightgreen)](https://github.com/CA-git-com-co/ACGS/actions)

**AI Compliance Governance System (ACGS)** with **Quantumagi** integration - A comprehensive constitutional AI governance framework deployed on Solana blockchain.

## 🏗️ Architecture Overview

ACGS-1 implements a modular, blockchain-integrated governance system with the following components:

- **🔗 Blockchain Layer**: Solana programs for on-chain governance enforcement
- **🏛️ Core Services**: Constitutional AI, governance synthesis, and policy enforcement
- **🖥️ Applications**: Web interfaces for governance participation and administration  
- **🔌 Integrations**: Bridges between blockchain and off-chain services
- **🛠️ Infrastructure**: Deployment, monitoring, and development tools

## 📁 Directory Structure

```
ACGS-1/
├── blockchain/                          # 🔗 Solana/Anchor Programs
│   ├── programs/                        # On-chain programs
│   │   ├── quantumagi-core/            # Main governance program
│   │   ├── appeals/                    # Appeals handling
│   │   └── logging/                    # Event logging
│   ├── client/                         # Blockchain client libraries
│   ├── tests/                          # Anchor tests
│   └── scripts/                        # Deployment scripts
│
├── services/                           # 🏗️ Backend Microservices
│   ├── core/                           # Core governance services
│   │   ├── constitutional-ai/          # Constitutional principles & compliance
│   │   ├── governance-synthesis/       # Policy synthesis & validation
│   │   ├── policy-governance/          # Real-time policy enforcement
│   │   └── formal-verification/        # Mathematical verification
│   ├── platform/                       # Platform services
│   │   ├── authentication/             # User authentication & authorization
│   │   ├── integrity/                  # Cryptographic integrity
│   │   └── workflow/                   # Workflow orchestration
│   ├── research/                       # Research services
│   │   ├── federated-evaluation/       # Distributed evaluation
│   │   └── research-platform/          # Research infrastructure
│   └── shared/                         # Shared libraries & utilities
│
├── applications/                       # 🖥️ Frontend Applications
│   ├── governance-dashboard/           # Main governance interface
│   ├── constitutional-council/         # Council management interface
│   ├── public-consultation/            # Public participation portal
│   └── admin-panel/                    # Administrative interface
│
├── integrations/                       # 🔌 Integration Layer
│   ├── quantumagi-bridge/             # Blockchain-Backend bridge
│   ├── alphaevolve-engine/            # AlphaEvolve integration
│   ├── data-flywheel/                 # NVIDIA AI Blueprints Data Flywheel
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

## 🚀 Quick Start

### Prerequisites

- **Solana CLI** v1.18.22+
- **Anchor Framework** v0.29.0+
- **Node.js** v18+
- **Python** 3.9+
- **PostgreSQL** 15+
- **Redis** 7+

### 1. Clone and Setup

```bash
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-1

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Build Blockchain Programs

```bash
cd blockchain
npm install
anchor build
anchor test
```

### 3. Start Backend Services (Host-based)

```bash
# Start Authentication Service (Port 8000)
cd services/platform/authentication/auth_service
python -m uvicorn app.main:app --reload --port 8000

# Start Constitutional AI Service (Port 8001)
cd services/core/constitutional-ai/ac_service
python -m uvicorn app.main:app --reload --port 8001

# Start Integrity Service (Port 8002)
cd services/platform/integrity/integrity_service
python -m uvicorn app.main:app --reload --port 8002

# Start Formal Verification Service (Port 8003)
cd services/core/formal-verification/fv_service
python -m uvicorn main:app --reload --port 8003

# Start Governance Synthesis Service (Port 8004)
cd services/core/governance-synthesis/gs_service
python -m uvicorn app.main:app --reload --port 8004

# Start Policy Governance Service (Port 8005)
cd services/core/policy-governance/pgc_service
python -m uvicorn app.main:app --reload --port 8005

# Start Evolutionary Computation Service (Port 8006)
cd services/core/evolutionary-computation
python -m uvicorn app.main:app --reload --port 8006
```

### 4. Launch Frontend Applications

```bash
cd applications/governance-dashboard
npm install
npm start
```

### 5. Deploy to Solana Devnet

```bash
cd blockchain
anchor deploy --provider.cluster devnet
python scripts/initialize_constitution.py
```

## 🏛️ Core Components

### Blockchain Layer (`blockchain/`)

**Quantumagi Core Program**: Main governance enforcement
- Constitutional principle storage and validation
- Policy proposal and voting mechanisms
- Real-time compliance checking (PGC)
- Democratic governance workflows

**Appeals Program**: Governance appeals and dispute resolution
**Logging Program**: Comprehensive audit trail and event logging

### 7 Core Services Architecture

**Authentication Service** (Port 8000) - `services/platform/authentication/auth_service/`
- Enterprise-grade authentication with MFA
- OAuth 2.0 & OpenID Connect integration
- API key management and JWT token validation
- Role-based access control (RBAC)

**Constitutional AI Service** (Port 8001) - `services/core/constitutional-ai/ac_service/`
- Constitutional principle management and validation
- Human-in-the-loop sampling for uncertainty resolution
- Collective Constitutional AI integration
- Democratic participation mechanisms and voting workflows

**Integrity Service** (Port 8002) - `services/platform/integrity/integrity_service/`
- Cryptographic integrity verification
- PGP assurance and digital signatures
- Appeals and dispute resolution processing
- Research data pipeline integration

**Formal Verification Service** (Port 8003) - `services/core/formal-verification/fv_service/`
- Z3 SMT solver integration for mathematical verification
- Safety property checking and formal validation
- Cross-domain testing and adversarial robustness
- Parallel validation pipeline processing

**Governance Synthesis Service** (Port 8004) - `services/core/governance-synthesis/gs_service/`
- LLM-powered policy synthesis from constitutional principles
- Multi-model validation with 99.92% reliability
- QEC-inspired error correction and bias detection
- AlphaEvolve integration for enhanced synthesis

**Policy Governance Service** (Port 8005) - `services/core/policy-governance/pgc_service/`
- Real-time policy enforcement using Open Policy Agent (OPA)
- Sub-200ms policy decisions with incremental compilation
- Constitutional amendment integration and workflow orchestration
- Multi-stakeholder governance coordination

**Evolutionary Computation Service** (Port 8006) - `services/core/evolutionary-computation/`
- WINA-optimized oversight and performance monitoring
- Constitutional compliance verification and optimization
- Evolutionary governance strategies and learning feedback
- Performance optimization alerts and constitutional updates

## 🔄 5 Core Governance Workflows

ACGS-1 implements five comprehensive governance workflows that orchestrate constitutional AI governance:

### 1. Policy Creation Workflow
**Implementation**: `services/core/policy-governance/pgc_service/app/api/v1/governance_workflows.py`
- **Draft Preparation**: Initial policy drafting using GS service
- **Stakeholder Review**: Coordinated review process with multiple stakeholders
- **Constitutional Validation**: Validation against constitutional principles via AC service
- **Voting Process**: Democratic voting with weighted stakeholder input
- **Implementation**: Policy activation and enforcement setup

### 2. Constitutional Compliance Workflow
**Implementation**: `services/core/constitutional-ai/ac_service/app/workflows/`
- **Validation**: Constitutional principle compliance checking
- **Assessment**: LLM-powered constitutional analysis and conflict detection
- **Enforcement**: Automated compliance enforcement and remediation

### 3. Policy Enforcement Workflow
**Implementation**: `services/core/policy-governance/pgc_service/app/main.py`
- **Monitoring**: Real-time policy compliance monitoring
- **Violation Detection**: Automated detection of policy violations
- **Remediation**: Corrective actions and enforcement measures

### 4. WINA Oversight Workflow
**Implementation**: `services/core/evolutionary-computation/ec_service/app/core/wina_oversight_coordinator.py`
- **Performance Monitoring**: WINA-optimized governance performance tracking
- **Optimization**: Evolutionary computation for governance improvement
- **Reporting**: Comprehensive performance and compliance reporting

### 5. Audit/Transparency Workflow
**Implementation**: `services/core/policy-governance/pgc_service/app/api/v1/governance_workflows.py`
- **Data Collection**: Comprehensive governance data gathering
- **Analysis**: Transparency analysis and audit trail generation
- **Public Reporting**: Public transparency reports and accountability measures

### Integration Layer (`integrations/`)

**Quantumagi Bridge** (`quantumagi-bridge/`)
- Seamless integration between Solana programs and backend services
- Event monitoring and real-time synchronization
- Cross-chain governance coordination

**Data Flywheel Integration** (`data-flywheel/`)
- NVIDIA AI Blueprints Data Flywheel implementation
- Autonomous AI model optimization for governance processes
- Constitutional compliance validation for AI outputs
- Production traffic analysis and model improvement
- Cost optimization (up to 98.6% inference cost reduction)

## 🔧 Development

### Running Tests

```bash
# Blockchain tests
cd blockchain && anchor test

# Backend service tests (from project root)
python -m pytest tests/ -v

# Individual service tests
cd services/core/constitutional-ai/ac_service && python -m pytest tests/
cd services/platform/integrity/integrity_service && python -m pytest tests/

# Frontend tests
cd applications/governance-dashboard && npm test

# Integration tests
python scripts/comprehensive_integration_test_runner.py
python scripts/validate_service_health.sh
```

### Code Quality

```bash
# Security audit
python scripts/security_audit.py

# Performance testing
python scripts/phase2_performance_validation.py

# Health checks
python scripts/comprehensive_health_check.py

# Service validation
./scripts/validate_service_stack.py
```

### Adding New Services

1. Create service directory in `services/core/`, `services/platform/`, or `services/research/`
2. Follow existing service patterns (FastAPI with uvicorn)
3. Update service registry in `service_registry_config.json`
4. Add service to monitoring in `scripts/priority3_monitoring_infrastructure.py`
5. Update integration tests and health checks

## 📊 Monitoring & Observability

- **Prometheus**: Metrics collection (`infrastructure/monitoring/prometheus.yml`)
- **Grafana**: Dashboards and visualization
- **Jaeger**: Distributed tracing
- **ELK Stack**: Centralized logging

Access monitoring dashboards at:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Jaeger: http://localhost:16686

## 🔐 Security

- **Multi-signature governance**: Constitutional changes require multiple approvals
- **Hardware security modules**: Cryptographic key protection
- **Zero-knowledge proofs**: Privacy-preserving governance participation
- **Formal verification**: Mathematical proof of policy correctness
- **Audit trails**: Comprehensive logging of all governance actions
- **Automated secret scanning**: 4-tool security validation (detect-secrets, TruffleHog, GitLeaks, Semgrep)
- **SARIF integration**: Security findings uploaded to GitHub Security tab
- **Custom ACGS rules**: Constitutional governance and Solana-specific security patterns

## 🔄 CI/CD Pipeline

ACGS-1 features a comprehensive CI/CD pipeline with **100% health score** and enterprise-grade security:

### **Automated Workflows**
- **🔧 Main CI/CD** (`ci.yml`): Comprehensive testing across Rust, Python, TypeScript, and Docker
- **⛓️ Solana/Anchor** (`solana-anchor.yml`): Dedicated blockchain program testing and validation
- **🔒 Security Scanning** (`secret-scanning.yml`): Multi-tool secret detection with custom ACGS rules
- **🏭 Production Deploy** (`production-deploy.yml`): Blue-green deployment with health checks
- **🔍 CodeQL Analysis** (`codeql.yml`): Advanced static analysis for multiple languages
- **🐳 Image Building** (`image-build.yml`): Docker image validation for all services
- **🛡️ Microsoft Security** (`defender-for-devops.yml`): Microsoft Security DevOps integration
- **⚙️ Config Validation** (`workflow-config-validation.yml`): Workflow structure validation

### **Security Features**
- **Multi-tool scanning**: detect-secrets, TruffleHog, GitLeaks, Semgrep
- **Custom security rules**: ACGS-1 governance secrets, Solana keypairs, constitutional patterns
- **SARIF reporting**: Automated upload to GitHub Security tab
- **Daily security scans**: Scheduled comprehensive security validation
- **Configuration validation**: Automated workflow structure and syntax checking

### **Performance Optimization**
- **Intelligent caching**: GitHub Actions cache for dependencies and build artifacts
- **Parallel execution**: Optimized job dependencies for faster builds
- **Path-based triggers**: Workflows only run when relevant files change
- **Matrix strategies**: Parallel testing across multiple environments
- **Conditional execution**: Smart change detection to minimize unnecessary runs

### **Constitutional Governance Integration**
- **Quantumagi deployment**: Automated Solana devnet deployment validation
- **Service health checks**: All 7 core services validation (Auth, AC, Integrity, FV, GS, PGC, EC)
- **Governance workflow testing**: 5 constitutional workflows validation
- **Blockchain security**: Solana keypair and program security validation
- **Policy compliance**: Constitutional compliance checking in CI/CD

## 🌐 Deployment

### Host-based Development Environment
```bash
# Start all services using the quick start script
./scripts/quick_start.sh

# Or start services individually (see Quick Start section above)
# Each service runs on its designated port (8000-8006)
```

### Solana Devnet Deployment
```bash
cd blockchain
anchor deploy --provider.cluster devnet
python scripts/initialize_constitution.py
python scripts/validate_devnet_deployment.py
```

### Production Environment
```bash
# Host-based production deployment
./scripts/phase3_host_based_deployment.sh

# Or use Docker Compose for containerized deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure database and services
export DATABASE_URL="postgresql://user:password@localhost:5432/acgs_db"
export REDIS_URL="redis://localhost:6379"

# Set API keys for LLM services
export OPENAI_API_KEY="your_openai_key"
export GEMINI_API_KEY="your_gemini_key"
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture/README.md)**: System design and components
- **[API Reference](docs/api/README.md)**: Complete API documentation
- **[Deployment Guide](docs/deployment/README.md)**: Deployment instructions
- **[Developer Guide](docs/development/README.md)**: Development workflows
- **[Research Documentation](docs/research/README.md)**: Research papers and findings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[AlphaEvolve Framework](https://github.com/alphaevolve/framework)**: Core constitutional AI framework
- **[Solana Programs Library](https://github.com/solana-labs/solana-program-library)**: Solana development resources
- **[Anchor Framework](https://github.com/coral-xyz/anchor)**: Solana development framework

## 📞 Support

- **Documentation**: [docs.acgs.ai](https://docs.acgs.ai)
- **Discord**: [ACGS Community](https://discord.gg/acgs)
- **Issues**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)
- **Email**: support@acgs.ai

---

**ACGS-1**: Bringing Constitutional AI Governance to Solana 🏛️⚡
