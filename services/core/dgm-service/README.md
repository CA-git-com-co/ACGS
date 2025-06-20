# Darwin Gödel Machine (DGM) Service

## Overview

The Darwin Gödel Machine (DGM) Service is a core component of the ACGS platform that implements self-improving AI systems with constitutional governance compliance. This service operates on port 8007 and provides evolutionary computation capabilities for continuous system improvement.

## Features

- **Self-Improving Algorithms**: Implements Darwin Gödel Machine principles for autonomous system evolution
- **Constitutional Compliance**: Ensures all improvements adhere to constitutional governance principles
- **Performance Monitoring**: Tracks system performance and triggers improvement cycles
- **Safe Exploration**: Uses conservative bandit algorithms for safe system exploration
- **Archive Management**: Maintains historical records of improvements and their outcomes
- **Integration Hub**: Seamlessly integrates with all 7 ACGS core services

## Architecture

### Core Components

1. **DGM Engine**: Core evolutionary computation engine
2. **Constitutional Validator**: Ensures compliance with governance principles
3. **Performance Monitor**: Tracks system metrics and performance indicators
4. **Archive Manager**: Manages improvement history and rollback capabilities
5. **Safety Controller**: Implements conservative exploration strategies
6. **Integration Layer**: Handles communication with ACGS services

### Technology Stack

- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for performance optimization
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Security**: JWT authentication with RBAC
- **Containerization**: Docker with Kubernetes support

## API Endpoints

### Health and Status
- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /status` - Detailed service status

### DGM Operations
- `POST /api/v1/dgm/improve` - Trigger improvement cycle
- `GET /api/v1/dgm/archive` - Retrieve improvement archive
- `POST /api/v1/dgm/rollback` - Rollback to previous state
- `GET /api/v1/dgm/performance` - Performance metrics

### Constitutional Compliance
- `POST /api/v1/constitutional/validate` - Validate improvement against constitution
- `GET /api/v1/constitutional/compliance` - Compliance status

## Configuration

The service is configured through environment variables and YAML configuration files:

- `DGM_SERVICE_PORT`: Service port (default: 8007)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `AUTH_SERVICE_URL`: ACGS Auth Service URL
- `CONSTITUTIONAL_COMPLIANCE_THRESHOLD`: Minimum compliance score (default: 0.8)

## Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker 24.0+

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the service:
   ```bash
   python -m dgm_service.main
   ```

### Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=dgm_service tests/
```

## Deployment

### Docker

```bash
# Build image
docker build -t acgs/dgm-service:latest .

# Run container
docker run -p 8007:8007 acgs/dgm-service:latest
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

## Monitoring

The service exposes Prometheus metrics on `/metrics` endpoint and includes:

- Request latency and throughput
- Improvement cycle success rates
- Constitutional compliance scores
- System performance indicators
- Error rates and types

## Security

- JWT token validation with ACGS Auth Service
- Role-based access control (RBAC)
- Input validation and sanitization
- Audit logging for all operations
- Encrypted communication with TLS

## Contributing

Please refer to the main ACGS contributing guidelines and ensure all improvements maintain constitutional compliance.

## License

This service is part of the ACGS platform and follows the same licensing terms.
