<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - Integrity Service

## Directory Overview

The Integrity Service provides cryptographic audit trails, data integrity validation, and immutable logging for all ACGS-2 constitutional AI governance operations. It ensures complete auditability and constitutional compliance tracking.

## File Inventory

- **CLAUDE.md**: This documentation file
- **app/**: FastAPI application and API endpoints
- **integrity_service/**: Core integrity service implementation
- **integrity_service_standardized/**: Standardized integrity components
- **simple_integrity_main.py**: Simplified integrity service main application
- **config/**: Configuration files and settings

## Dependencies & Interactions

- **Constitutional AI Service**: Audit trail for constitutional decisions
- **All Core Services**: Integrity validation for all operations
- **Database**: PostgreSQL for audit log storage
- **Cryptographic Libraries**: Digital signatures and hash validation
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`

## Key Components

### Audit Trail Engine
- **Immutable Logging**: Cryptographically secured audit logs
- **Digital Signatures**: Tamper-proof operation signatures
- **Hash Chains**: Linked audit records for integrity verification
- **Constitutional Tracking**: Specific tracking of constitutional compliance
- **Real-time Auditing**: Live audit trail generation

### Integrity Validation
- **Data Integrity Checks**: Validation of data consistency and accuracy
- **Constitutional Hash Validation**: Verification of constitutional compliance
- **Cryptographic Verification**: Digital signature and hash validation
- **Audit Log Verification**: Validation of audit trail integrity
- **Cross-Service Validation**: Integrity checks across service boundaries

### Compliance Monitoring
- **Constitutional Compliance Tracking**: Real-time constitutional adherence monitoring
- **Violation Detection**: Automatic detection of integrity violations
- **Alerting System**: Real-time alerts for integrity issues
- **Compliance Reporting**: Comprehensive compliance status reporting
- **Audit Analytics**: Analysis of audit patterns and trends

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: Immutable audit trail generation
✅ **IMPLEMENTED**: Cryptographic integrity validation
✅ **IMPLEMENTED**: Real-time compliance monitoring
🔄 **IN PROGRESS**: Advanced audit analytics
🔄 **IN PROGRESS**: Cross-service integrity validation
❌ **PLANNED**: AI-driven integrity analysis
❌ **PLANNED**: Predictive integrity monitoring

## Performance Considerations

- **Audit Latency**: <3ms for audit record creation
- **Constitutional Validation**: <1ms for hash validation
- **Throughput**: >2000 audit records per second
- **Storage Efficiency**: Optimized audit log compression
- **Query Performance**: Fast audit trail queries and searches

## Implementation Status

### ✅ IMPLEMENTED
- Core integrity service with audit trail generation
- Cryptographic validation and digital signatures
- Constitutional compliance tracking
- Basic monitoring and alerting
- Database integration for audit storage

### 🔄 IN PROGRESS
- Advanced audit analytics and reporting
- Cross-service integrity validation
- Enhanced cryptographic features
- Real-time integrity monitoring dashboard
- Automated compliance reporting

### ❌ PLANNED
- AI-driven integrity analysis and anomaly detection
- Predictive integrity monitoring
- Advanced audit pattern recognition
- Blockchain integration for immutable storage
- Zero-knowledge proof integration

## API Endpoints

### Audit Trail Management
- **POST /audit**: Create new audit record
- **GET /audit/{id}**: Retrieve specific audit record
- **GET /audit/search**: Search audit records with filters
- **POST /audit/verify**: Verify audit record integrity
- **GET /audit/chain/{id}**: Get audit chain for record

### Integrity Validation
- **POST /validate/hash**: Validate constitutional hash
- **POST /validate/signature**: Verify digital signature
- **POST /validate/data**: Validate data integrity
- **GET /validate/status**: Get validation status

### Monitoring and Health
- **GET /health**: Service health check
- **GET /metrics**: Prometheus metrics endpoint
- **GET /compliance/status**: Constitutional compliance status
- **GET /integrity/stats**: Integrity validation statistics

## Configuration

```yaml
# Integrity Service Configuration
integrity:
  constitutional_hash: cdd01ef066bc6cf2
  audit_retention_days: 2555  # 7 years
  signature_algorithm: RSA-PSS
  hash_algorithm: SHA-256

database:
  url: postgresql://localhost:5439/acgs_integrity
  pool_size: 20
  audit_table: audit_trail
  enable_encryption: true

cryptography:
  private_key_path: /etc/acgs/integrity/private.pem
  public_key_path: /etc/acgs/integrity/public.pem
  signature_validity_days: 365

monitoring:
  enable_real_time_alerts: true
  compliance_check_interval: 60s
  integrity_scan_interval: 300s
  log_level: INFO
```

## Usage Examples

```python
# Create audit record
audit_record = {
    "operation": "constitutional_validation",
    "service": "constitutional-ai",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "request_id": "req-123",
        "validation_result": "compliant"
    }
}

audit_id = await integrity_service.create_audit(audit_record)

# Verify audit integrity
verification_result = await integrity_service.verify_audit(audit_id)

# Search audit trail
search_results = await integrity_service.search_audit({
    "service": "constitutional-ai",
    "date_range": "2024-01-15",
    "constitutional_hash": "cdd01ef066bc6cf2"
})
```

## Security Features

### Cryptographic Security
- **Digital Signatures**: RSA-PSS signatures for all audit records
- **Hash Chains**: Linked audit records preventing tampering
- **Encryption**: AES-256 encryption for sensitive audit data
- **Key Management**: Secure key storage and rotation

### Access Control
- **Role-Based Access**: Granular access control for audit data
- **Service Authentication**: Secure service-to-service communication
- **Audit Log Protection**: Immutable audit log storage
- **Constitutional Context**: Access control based on constitutional compliance

## Cross-References & Navigation

**Navigation**:
- [Platform Services](../CLAUDE.md)
- [API Gateway](../api_gateway/CLAUDE.md)
- [Authentication Service](../authentication/CLAUDE.md)
- [Audit Aggregator](../audit_aggregator/CLAUDE.md)

**Related Components**:
- [Constitutional AI Service](../../core/constitutional-ai/CLAUDE.md)
- [Database Infrastructure](../../../database/CLAUDE.md)
- [Security Framework](../../../security/CLAUDE.md)

**External References**:
- [Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [Audit Trail Best Practices](https://www.sans.org/white-papers/1168/)

---

**Constitutional Compliance**: All integrity operations maintain constitutional hash `cdd01ef066bc6cf2` validation
