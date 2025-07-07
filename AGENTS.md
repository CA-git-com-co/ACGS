# ACGS Agent Guidelines

## Commands
- **Install**: `uv sync`
- **Test**: `make test` (90% coverage required)
- **Lint**: `ruff check --fix && ruff format`
- **Type**: `mypy services/ scripts/`

## Code Style
- Black (88 chars), strict mypy, Pydantic models
- Include constitutional hash `cdd01ef066bc6cf2` in docstrings
- Use `services/shared/middleware/error_handling.py` exceptions

## Services
- **Start**: `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d`
- **MCP**: `docker-compose up -d` (ports 3000-3003)
- **Health**: `curl http://localhost:8001/health`
- **Constitutional hash**: `cdd01ef066bc6cf2` required in all operations

## Architecture
- ACGS services: ports 8001-8016
- MCP services: ports 3000-3003
- PostgreSQL: 5439, Redis: 6389
- Multi-tenant with Row-Level Security
- Performance: P99 <5ms, >100 RPS