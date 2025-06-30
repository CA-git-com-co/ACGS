# Environment Variables Reference

## Core Application Variables

### Database Configuration
```bash
# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Database SSL Configuration
DATABASE_SSL_MODE=require
DATABASE_SSL_CERT=/path/to/client-cert.pem
DATABASE_SSL_KEY=/path/to/client-key.pem
DATABASE_SSL_ROOT_CERT=/path/to/ca-cert.pem
```

### Redis Configuration
```bash
# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_MAX_CONNECTIONS=100
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# Redis Cluster (if using cluster mode)
REDIS_CLUSTER_NODES=redis1:6379,redis2:6379,redis3:6379
REDIS_CLUSTER_PASSWORD=cluster_password
```

### Security Configuration
```bash
# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption Keys
ENCRYPTION_KEY=your_32_byte_encryption_key_here
FERNET_KEY=your_fernet_key_for_symmetric_encryption

# CORS Configuration
CORS_ORIGINS=https://acgs.domain.com,https://admin.acgs.domain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
```

### Service Configuration
```bash
# Constitutional AI Service
CONSTITUTIONAL_AI_SERVICE_URL=http://localhost:8001
CONSTITUTIONAL_AI_API_KEY=your_constitutional_ai_api_key
CONSTITUTIONAL_AI_TIMEOUT=30

# Policy Governance Service
POLICY_GOVERNANCE_SERVICE_URL=http://localhost:8005
POLICY_GOVERNANCE_API_KEY=your_policy_governance_api_key
POLICY_GOVERNANCE_TIMEOUT=30

# Governance Synthesis Service
GOVERNANCE_SYNTHESIS_SERVICE_URL=http://localhost:8004
GOVERNANCE_SYNTHESIS_API_KEY=your_governance_synthesis_api_key
GOVERNANCE_SYNTHESIS_TIMEOUT=60

# External LLM Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
COHERE_API_KEY=your_cohere_api_key
```

### Monitoring Configuration
```bash
# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s

# Grafana Configuration
GRAFANA_URL=http://localhost:3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# Alertmanager Configuration
ALERTMANAGER_URL=http://localhost:9093
ALERTMANAGER_WEBHOOK_URL=http://localhost:5001/alerts
```

### Logging Configuration
```bash
# Log Levels
LOG_LEVEL=INFO
ROOT_LOG_LEVEL=WARNING
DATABASE_LOG_LEVEL=WARNING
CACHE_LOG_LEVEL=INFO

# Log Formats
LOG_FORMAT=json
LOG_TIMESTAMP_FORMAT=iso

# Log Destinations
LOG_FILE=/var/log/acgs/application.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
LOG_ROTATION=daily
```

## Environment-Specific Variables

### Production Environment
```bash
ENVIRONMENT=production
DEBUG=false
TESTING=false
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=acgs.domain.com,api.acgs.domain.com
```

### Staging Environment
```bash
ENVIRONMENT=staging
DEBUG=false
TESTING=true
SECRET_KEY=your_staging_secret_key
ALLOWED_HOSTS=staging.acgs.domain.com,staging-api.acgs.domain.com
```

### Development Environment
```bash
ENVIRONMENT=development
DEBUG=true
TESTING=true
SECRET_KEY=development_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## Security Best Practices

### Secret Management
- Use environment-specific secret management (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly (quarterly for production)
- Never commit secrets to version control
- Use different secrets for each environment

### Access Control
- Limit environment variable access to necessary personnel
- Use IAM roles and policies for cloud deployments
- Implement least privilege access principles
- Audit secret access regularly
