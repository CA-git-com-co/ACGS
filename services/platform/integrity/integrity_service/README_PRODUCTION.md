# ACGS-PGP Integrity Service - Production Documentation

## Overview

The Integrity Service provides enterprise-grade cryptographic integrity, digital signature management, audit trail capabilities, and PGP assurance for the ACGS-PGP (Autonomous Constitutional Governance System - Policy Generation Platform). It ensures data integrity, traceability, and verifiability across all governance operations with blockchain-style verification.

**Service Details:**
- **Port**: 8002
- **Version**: 3.0.0
- **Constitutional Hash**: `cdd01ef066bc6cf2`
- **Resource Limits**: CPU 100m-300m, Memory 256Mi-512Mi
- **Health Check**: `/health`

## Architecture

### Core Components
- **Cryptographic Integrity Verification**: SHA-256 hashing and digital signatures
- **Digital Signature Management**: PGP/GPG signature creation and validation
- **Audit Trail with Blockchain Verification**: Immutable audit logging
- **PGP Assurance and Key Management**: Enterprise key management system
- **Appeals and Dispute Resolution**: Integrity-verified dispute handling
- **Research Data Pipeline**: Secure data export and analysis

### Dependencies
- **Database**: PostgreSQL (audit logs, signatures, keys)
- **Authentication Service**: Port 8000 (JWT token validation)
- **Blockchain Integration**: Solana network (immutable proof storage)
- **Cryptographic Libraries**: PGP/GPG, OpenSSL

## API Endpoints

### Core Service Information

#### GET /
Service information and capabilities overview.

**Response:**
```json
{
  "service": "ACGS-1 Production Integrity Service",
  "version": "3.0.0",
  "status": "operational",
  "port": 8002,
  "phase": "Phase A3 - Production Implementation",
  "capabilities": [
    "Cryptographic Integrity Verification",
    "Digital Signature Management",
    "Audit Trail with Blockchain Verification",
    "PGP Assurance and Key Management",
    "Appeals and Dispute Resolution",
    "Research Data Pipeline",
    "Enterprise Security"
  ],
  "api_documentation": "/docs"
}
```

#### GET /health
Comprehensive health check with dependency status.

**Response:**
```json
{
  "status": "healthy",
  "service": "integrity_service",
  "version": "3.0.0",
  "port": 8002,
  "uptime_seconds": 3600.5,
  "dependencies": {
    "database": "connected",
    "crypto_service": "operational",
    "pgp_service": "operational"
  },
  "performance_metrics": {
    "uptime_seconds": 3600.5,
    "routers_available": true,
    "api_endpoints": 15
  }
}
```

### Constitutional Compliance

#### GET /api/v1/constitutional/validate
Constitutional hash validation and integrity verification.

**Response:**
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_status": "valid",
  "service": "integrity_service",
  "version": "3.0.0",
  "timestamp": 1750820294.86,
  "compliance_framework": {
    "hash_algorithm": "SHA-256",
    "validation_level": "enterprise",
    "integrity_verified": true
  },
  "constitutional_state": {
    "active": true,
    "cryptographic_integrity": true,
    "audit_trail": true,
    "digital_signatures": true
  },
  "integrity_capabilities": {
    "pgp_assurance": true,
    "appeals_processing": true,
    "research_pipeline": true,
    "blockchain_verification": true
  }
}
```

### Integrity Verification

#### POST /api/v1/integrity/policy-rules/{rule_id}/sign
Sign a policy rule with digital signature and timestamp.

**Request:**
```json
{
  "signature_algorithm": "RSA-SHA256",
  "include_timestamp": true,
  "metadata": {
    "signer_role": "policy_admin",
    "approval_level": "executive"
  }
}
```

**Response:**
```json
{
  "signature_id": "SIG-1750820294",
  "rule_id": 123,
  "signature": "-----BEGIN PGP SIGNATURE-----...",
  "timestamp": "2025-06-25T03:00:00Z",
  "hash": "sha256:abc123...",
  "verification_status": "signed",
  "blockchain_proof": {
    "transaction_id": "tx_abc123",
    "block_height": 12345,
    "merkle_proof": "proof_xyz789"
  }
}
```

#### POST /api/v1/integrity/policy-rules/{rule_id}/verify
Verify the integrity and signature of a policy rule.

**Response:**
```json
{
  "verification_id": "VER-1750820294",
  "rule_id": 123,
  "integrity_verified": true,
  "signature_valid": true,
  "timestamp_verified": true,
  "verification_details": {
    "hash_match": true,
    "signature_algorithm": "RSA-SHA256",
    "signer_identity": "policy_admin@acgs.ai",
    "verification_time": "2025-06-25T03:00:00Z"
  },
  "blockchain_verification": {
    "proof_verified": true,
    "immutable_record": true
  }
}
```

#### POST /api/v1/integrity/audit-logs/{log_id}/sign
Sign an audit log entry with digital signature and chain integrity.

#### POST /api/v1/integrity/audit-logs/{log_id}/verify
Verify the integrity and signature of an audit log entry.

### Cryptographic Operations

#### POST /api/v1/crypto/sign
Generate digital signature for data.

**Request:**
```json
{
  "data": "Policy content to sign",
  "algorithm": "RSA-SHA256",
  "key_id": "key_123",
  "include_timestamp": true
}
```

#### POST /api/v1/crypto/verify
Verify digital signature.

**Request:**
```json
{
  "data": "Original data",
  "signature": "-----BEGIN PGP SIGNATURE-----...",
  "public_key": "-----BEGIN PGP PUBLIC KEY-----..."
}
```

#### POST /api/v1/crypto/merkle/build
Build Merkle tree for data integrity verification.

#### POST /api/v1/crypto/merkle/verify
Verify Merkle tree proof.

### System Integrity

#### GET /api/v1/integrity/system-integrity-report
Generate comprehensive system integrity report.

**Parameters:**
- `include_policy_rules`: Include policy rule integrity (default: true)
- `include_audit_logs`: Include audit log integrity (default: true)
- `sample_size`: Number of entries to verify (default: 100)

**Response:**
```json
{
  "report_generated_at": "2025-06-25T03:00:00Z",
  "overall_system_integrity": true,
  "policy_rules": {
    "total_verified": 150,
    "integrity_violations": 0,
    "signature_failures": 0,
    "integrity_score": 100.0
  },
  "audit_logs": {
    "total_verified": 500,
    "chain_integrity": true,
    "signature_failures": 0,
    "integrity_score": 100.0
  },
  "cryptographic_health": {
    "key_rotation_status": "current",
    "certificate_validity": "valid",
    "encryption_strength": "enterprise"
  }
}
```

### PGP Assurance

#### POST /api/v1/pgp/generate-keys
Generate new PGP key pair.

#### POST /api/v1/pgp/verify-signature
Verify PGP signature and integrity package.

**Request:**
```json
{
  "data": "Data to verify",
  "integrity_package": {
    "signature": "-----BEGIN PGP SIGNATURE-----...",
    "hash": "sha256:abc123...",
    "timestamp": "2025-06-25T03:00:00Z"
  }
}
```

### Appeals & Dispute Resolution

#### GET /api/v1/appeals
List integrity-verified appeals.

#### POST /api/v1/appeals
Create new appeal with integrity verification.

#### POST /api/v1/appeals/{appeal_id}/vote
Submit integrity-verified vote on appeal.

## Configuration

### Environment Variables

```bash
# Service Configuration
SERVICE_NAME=integrity_service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8002
HOST=127.0.0.1  # Secure default

# Constitutional Framework
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
INTEGRITY_VERIFICATION_LEVEL=enterprise

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_integrity
REDIS_URL=redis://localhost:6379/2

# Cryptographic Configuration
PGP_KEY_SIZE=4096
SIGNATURE_ALGORITHM=RSA-SHA256
HASH_ALGORITHM=SHA-256
KEY_ROTATION_DAYS=90

# Blockchain Integration
BLOCKCHAIN_PROVIDER_URL=https://api.mainnet-beta.solana.com
BLOCKCHAIN_VERIFICATION_ENABLED=true
MERKLE_TREE_DEPTH=16

# Performance Configuration
MAX_CONCURRENT_OPERATIONS=25
VERIFICATION_TIMEOUT_SECONDS=15
CACHE_TTL_SECONDS=1800
```

### Resource Limits (Kubernetes)

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "300m"
```

## Security

### Cryptographic Security
- **Digital Signatures**: RSA-4096 and ECDSA-P256 support
- **Hash Algorithms**: SHA-256, SHA-512 for data integrity
- **Key Management**: Automated key rotation every 90 days
- **PGP/GPG Integration**: Enterprise-grade signature verification

### Blockchain Integration
- **Immutable Proof Storage**: Solana blockchain integration
- **Merkle Tree Verification**: Efficient batch verification
- **Transaction Integrity**: Cryptographic proof of operations
- **Audit Trail**: Blockchain-backed audit logging

### Access Control
- **JWT Authentication**: Integration with auth service
- **Role-Based Permissions**: Auditor, admin, internal service roles
- **API Rate Limiting**: Protection against abuse
- **Secure Key Storage**: Hardware security module (HSM) support

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t acgs-integrity-service:latest .

# Run container
docker run -d \
  --name acgs-integrity-service \
  -p 8002:8002 \
  -e CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  acgs-integrity-service:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: integrity-service
  labels:
    app: integrity-service
    constitutional-hash: cdd01ef066bc6cf2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: integrity-service
  template:
    metadata:
      labels:
        app: integrity-service
    spec:
      containers:
      - name: integrity-service
        image: acgs-integrity-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "300m"
```

## Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Frequency**: Every 30 seconds
- **Dependencies**: Database, crypto service, PGP service

### Metrics
- **Signature Operations**: Creation and verification rates
- **Integrity Verifications**: Success/failure rates
- **Blockchain Operations**: Transaction success rates
- **Key Management**: Key rotation and certificate status

### Alerts
- **Critical**: Service down, cryptographic failures, blockchain connectivity
- **High**: Signature verification failures, key expiration warnings
- **Moderate**: High verification latency, cache misses

## Troubleshooting

### Common Issues

1. **Cryptographic Operation Failures**
   ```bash
   # Check crypto service status
   curl -s http://localhost:8002/health | jq '.dependencies.crypto_service'
   ```

2. **PGP Key Issues**
   ```bash
   # Verify PGP service
   curl -s http://localhost:8002/health | jq '.dependencies.pgp_service'
   ```

3. **Blockchain Connectivity**
   ```bash
   # Check blockchain integration
   curl -s http://localhost:8002/api/v1/status | jq '.capabilities.blockchain_verification'
   ```

## Performance Targets

- **Response Time**: ≤2 seconds (P95)
- **Signature Operations**: 100 ops/second
- **Verification Success Rate**: >99.9%
- **Blockchain Proof Success**: >95%
- **Availability**: >99.9%

## Contact & Support

- **Team**: ACGS Integrity Team
- **Documentation**: https://docs.acgs.ai/integrity-service
- **Runbooks**: https://docs.acgs.ai/runbooks/integrity-service
- **Monitoring**: Grafana Dashboard "ACGS Integrity Service"
- **OpenAPI Spec**: `/services/platform/integrity/integrity_service/openapi.yaml`
