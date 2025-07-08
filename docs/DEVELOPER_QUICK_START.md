# ACGS Developer Quick Start Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

Welcome to the ACGS (Autonomous Coding Governance System) project! This guide will help you get started quickly.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- Basic understanding of FastAPI and async/await patterns

## Quick Setup (5 minutes)

### 1. Clone and Setup Environment
```bash
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Infrastructure Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker ps
```

### 3. Run Tests
```bash
# Run basic tests to verify setup
pytest tests/ -v
```

### 4. Start Development Server
```bash
# Start a service (example: constitutional-ai)
cd services/core/constitutional-ai
uvicorn main:app --reload --port 8001
```

## Key Concepts

### Constitutional Compliance
- **Hash**: `cdd01ef066bc6cf2` must be present in all critical files
- **Validation**: All services validate constitutional compliance
- **Monitoring**: Prometheus tracks compliance metrics

### Service Architecture
- **FastAPI**: All services use FastAPI with Pydantic v2
- **Async/Await**: Asynchronous patterns throughout
- **Performance**: P99 latency <5ms, >100 RPS, >85% cache hit rate

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes with constitutional compliance
3. Run tests: `pytest tests/`
4. Submit PR with constitutional hash validation

## Essential Documentation

- [CLAUDE.md](../CLAUDE.md) - Claude agent configuration
- [AGENTS.md](../AGENTS.md) - Multi-agent coordination
- [Infrastructure Monitoring](../infrastructure/monitoring/README.md)
- [Service Documentation](../services/)

## Getting Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Review [Infrastructure Documentation](../infrastructure/)
- Ask questions in team channels with constitutional compliance context

## Next Steps

1. Explore service documentation in `services/`
2. Review monitoring dashboards at http://localhost:3001 (Grafana)
3. Check Prometheus metrics at http://localhost:9091
4. Read constitutional compliance documentation

Happy coding! 🚀
