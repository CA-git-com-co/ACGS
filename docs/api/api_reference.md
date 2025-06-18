# ACGS-1 API Reference

Complete API documentation for all ACGS-1 services.

## Core Services APIs

### Auth Service (Port 8000)
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user

### Constitutional AI Service (Port 8001)
- `GET /api/constitutional-ai/principles` - Get principles
- `POST /api/constitutional-ai/principles` - Create principle
- `GET /api/constitutional-ai/compliance` - Check compliance

### Governance Synthesis Service (Port 8004)
- `POST /api/governance-synthesis/synthesize` - Synthesize policy
- `GET /api/governance-synthesis/policies` - Get policies
- `POST /api/governance-synthesis/validate` - Validate policy

### Policy Governance & Compliance Service (Port 8005)
- `POST /api/pgc/enforce` - Enforce policy
- `GET /api/pgc/compliance` - Check compliance
- `GET /api/pgc/workflows` - Get governance workflows

