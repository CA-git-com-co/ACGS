# ACGS-1 Integrity Service

**Status**: ✅ **Production Ready**  
**Last Updated**: 2025-06-27

## Overview

The Integrity Service provides enterprise-grade cryptographic integrity, digital signature management, audit trail capabilities, and PGP assurance for the ACGS-PGP system. It ensures data integrity, traceability, and verifiability across all governance operations with blockchain-style verification.

**Service Port**: 8002
**Service Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8002/health

## Core Features

### Cryptographic Operations

- **Digital Signatures**: RSA, ECDSA signature generation and verification
- **Hash Verification**: SHA-256, SHA-512 integrity checking
- **PGP Assurance**: PGP key management and certificate validation
- **Encryption Services**: Data encryption at rest and in transit
- **Key Management**: Secure key generation, storage, and rotation

### Data Integrity & Audit

- **Policy Storage**: Secure policy document storage with versioning
- **Audit Logging**: Comprehensive audit trail with blockchain-style verification
- **Research Data**: Secure storage for governance research and analysis
- **Integrity Checks**: Continuous data integrity validation
- **Tamper Detection**: Real-time detection of data modifications

### Enterprise Features

- **Backup & Recovery**: Automated backup with integrity verification
- **Compliance Reporting**: Audit reports for regulatory compliance
- **Performance Monitoring**: Real-time performance metrics and alerting
- **High Availability**: Multi-node deployment with failover support

## API Endpoints

### Cryptographic Operations

- `POST /api/v1/crypto/sign` - Generate digital signature
- `POST /api/v1/crypto/verify` - Verify digital signature
- `POST /api/v1/crypto/hash` - Generate cryptographic hash
- `POST /api/v1/verify/hash` - Verify hash integrity
- `POST /api/v1/crypto/encrypt` - Encrypt data
- `POST /api/v1/crypto/decrypt` - Decrypt data

### PGP Assurance

- `GET /api/v1/pgp-assurance/certificates` - List PGP certificates
- `POST /api/v1/pgp-assurance/certificates` - Add new PGP certificate
- `POST /api/v1/pgp-assurance/verify` - Verify PGP signature
- `DELETE /api/v1/pgp-assurance/certificates/{id}` - Revoke certificate
- `GET /api/v1/pgp-assurance/trust-chain` - View trust chain

### Policy Management

- `GET /api/v1/policies` - List stored policies
- `POST /api/v1/policies` - Store new policy with signature
- `GET /api/v1/policies/{id}` - Retrieve specific policy
- `PUT /api/v1/policies/{id}` - Update policy (creates new version)
- `GET /api/v1/policies/{id}/versions` - View policy version history
- `POST /api/v1/policies/{id}/verify` - Verify policy integrity

### Audit & Logging

- `GET /api/v1/audit/logs` - Retrieve audit logs
- `POST /api/v1/audit/event` - Log audit event
- `GET /api/v1/audit/trail/{entity_id}` - Get audit trail for entity
- `GET /api/v1/audit/compliance-report` - Generate compliance report
- `POST /api/v1/audit/verify-trail` - Verify audit trail integrity

### Research Data

- `POST /api/v1/research/store` - Store research data securely
- `GET /api/v1/research/{id}` - Retrieve research data
- `POST /api/v1/research/{id}/verify` - Verify research data integrity
- `GET /api/v1/research/metadata` - List research metadata

### Integrity Checks

- `POST /api/v1/integrity/check` - Perform integrity check
- `GET /api/v1/integrity/status` - Overall integrity status
- `POST /api/v1/integrity/repair` - Repair integrity issues
- `GET /api/v1/integrity/reports` - Integrity check reports

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_integrity
REDIS_URL=redis://localhost:6379/2

# Service Configuration
SERVICE_NAME=integrity-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8002
APP_ENV=production
LOG_LEVEL=INFO

# Cryptographic Configuration
ENCRYPTION_KEY=your-encryption-key-here
SIGNATURE_ALGORITHM=RSA
HASH_ALGORITHM=SHA256
KEY_SIZE=2048

# PGP Configuration
PGP_KEY_DIR=/var/lib/acgs/pgp/keys
PGP_TRUST_DB=/var/lib/acgs/pgp/trustdb.gpg
PGP_DEFAULT_KEY_ID=your-default-key-id

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AUDIT_RETENTION_DAYS=2555  # 7 years
INTEGRITY_CHECK_INTERVAL=3600  # 1 hour

# Service Integration
AUTH_SERVICE_URL=http://localhost:8000
AC_SERVICE_URL=http://localhost:8001

# Security Configuration
ENABLE_AUDIT_LOGGING=true
BACKUP_ENCRYPTION_ENABLED=true
TAMPER_DETECTION_ENABLED=true
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

## Installation & Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- GnuPG 2.2+
- OpenSSL 1.1.1+

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# 2. Setup database
createdb acgs_integrity
alembic upgrade head

# 3. Setup PGP environment
mkdir -p /var/lib/acgs/pgp/keys
chmod 700 /var/lib/acgs/pgp/keys

# 4. Configure environment
cp config/environments/developmentconfig/environments/example.env config/environments/development.env
# Edit config/environments/development.env with your configuration

# 5. Start service
uv run uvicorn main:app --reload --port 8002
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-integrity-service .
docker run -p 8002:8002 --env-file config/environments/development.env acgs-integrity-service

# Using systemd
sudo cp integrity-service.service /etc/systemd/system/
sudo systemctl enable integrity-service
sudo systemctl start integrity-service
```

## Testing

### Unit Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Integration Tests

```bash
# Test cryptographic operations
uv run pytest tests/test_crypto_integration.py -v

# Test PGP functionality
uv run pytest tests/test_pgp_integration.py -v

# Test audit trail
uv run pytest tests/test_audit_integration.py -v
```

### Security Tests

```bash
# Test signature verification
python scripts/test_signature_verification.py

# Test integrity checks
python scripts/test_integrity_validation.py
```
