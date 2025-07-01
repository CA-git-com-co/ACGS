# ACGS Enterprise Integration Hub

The Enterprise Integration Hub provides comprehensive enterprise ecosystem integration for the ACGS (Autonomous Constitutional Governance System), including REST/GraphQL APIs, SSO integration, LDAP/AD connectors, CI/CD integration, and third-party governance tool integration.

## Features

### 🔌 API Integration
- **REST APIs**: Complete RESTful API endpoints for enterprise integration
- **GraphQL API**: Modern GraphQL interface with queries and mutations
- **OpenAPI Documentation**: Auto-generated API documentation

### 🔐 Authentication & Authorization
- **SAML SSO**: Security Assertion Markup Language integration
- **OIDC/OAuth2**: OpenID Connect and OAuth2 support
- **LDAP/Active Directory**: Enterprise directory service integration
- **JWT Tokens**: Secure token-based authentication

### 🚀 CI/CD Integration
- **Policy Validation**: Constitutional policy validation in CI/CD pipelines
- **Deployment Approval**: Governance-based deployment approvals
- **Pipeline Integration**: Webhook support for major CI/CD platforms

### 🔗 Third-Party Connectors
- **Jira Integration**: Issue tracking and governance workflow integration
- **ServiceNow**: IT service management integration
- **Custom Webhooks**: Extensible webhook system for custom integrations

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- LDAP server (for LDAP integration)
- Enterprise SSO provider (for SSO integration)

### Installation

1. **Clone and setup**:
```bash
cd services/enterprise_integration
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
# LDAP Configuration
export LDAP_SERVER="ldap://your-ldap-server:389"
export LDAP_BASE_DN="dc=your-company,dc=com"
export LDAP_USER_DN="cn=users,dc=your-company,dc=com"

# OIDC Configuration
export OIDC_USERINFO_ENDPOINT="https://your-oidc-provider/userinfo"

# JWT Configuration
export JWT_SECRET_KEY="your-secret-key"
```

3. **Run the service**:
```bash
python integration_hub.py
```

The service will start on `http://localhost:8020`

### Docker Deployment

```bash
docker build -t acgs-enterprise-integration .
docker run -p 8020:8020 \
  -e LDAP_SERVER="ldap://your-ldap-server:389" \
  -e LDAP_BASE_DN="dc=your-company,dc=com" \
  acgs-enterprise-integration
```

## API Endpoints

### REST API

#### Health Check
```
GET /api/v1/health
```

#### Constitutional Policies
```
GET /api/v1/constitutional/policies
POST /api/v1/constitutional/decisions
GET /api/v1/governance/metrics
```

#### SSO Integration
```
POST /api/v1/sso/saml/callback
POST /api/v1/sso/oidc/callback
```

#### LDAP Integration
```
POST /api/v1/ldap/authenticate
GET /api/v1/ldap/users/{user_id}
```

#### CI/CD Integration
```
POST /api/v1/cicd/policy-validation
POST /api/v1/cicd/deployment-approval
```

#### Third-Party Connectors
```
POST /api/v1/connectors/jira/webhook
POST /api/v1/connectors/servicenow/incident
```

### GraphQL API

Access the GraphQL playground at: `http://localhost:8020/graphql`

#### Sample Queries

**Get Constitutional Policies**:
```graphql
query {
  constitutionalPolicies {
    id
    name
    version
    status
    constitutionalCompliance
    description
  }
}
```

**Get Governance Metrics**:
```graphql
query {
  governanceMetrics {
    constitutionalComplianceScore
    governanceDecisionsProcessed
    policyViolationsDetected
    averageDecisionTimeMs
    constitutionalHashValidations
  }
}
```

**LDAP Authentication**:
```graphql
mutation {
  authenticateLdap(credentials: {
    username: "john.doe"
    password: "password123"
  }) {
    accessToken
    tokenType
    expiresIn
    constitutionalHash
    userInfo {
      userId
      email
      constitutionalClearance
      groups
      department
    }
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LDAP_SERVER` | LDAP server URL | `ldap://localhost:389` |
| `LDAP_BASE_DN` | LDAP base DN | `dc=enterprise,dc=com` |
| `LDAP_USER_DN` | LDAP user DN | `cn=users,dc=enterprise,dc=com` |
| `OIDC_USERINFO_ENDPOINT` | OIDC userinfo endpoint | None |
| `JWT_SECRET_KEY` | JWT signing key | Auto-generated |

### Constitutional Hash

The service maintains constitutional compliance with hash: `cdd01ef066bc6cf2`

## Security Considerations

1. **Token Validation**: All endpoints (except health) require valid JWT tokens
2. **HTTPS**: Use HTTPS in production environments
3. **LDAP Security**: Use secure LDAP (LDAPS) for production
4. **SAML Validation**: Implement proper SAML signature validation
5. **Rate Limiting**: Configure appropriate rate limits for production

## Integration Examples

### Jenkins Pipeline Integration

```groovy
pipeline {
    agent any
    stages {
        stage('Constitutional Validation') {
            steps {
                script {
                    def response = httpRequest(
                        url: 'http://acgs-integration:8020/api/v1/cicd/policy-validation',
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: '{"policies": [{"id": "deployment_policy", "content": "..."}]}'
                    )
                    
                    def result = readJSON text: response.content
                    if (!result.all_policies_valid) {
                        error("Constitutional policy validation failed")
                    }
                }
            }
        }
    }
}
```

### GitHub Actions Integration

```yaml
name: Constitutional Governance Check
on: [push, pull_request]

jobs:
  constitutional-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Constitutional Policies
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.ACGS_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"policies": [{"id": "ci_policy", "content": "..."}]}' \
            http://acgs-integration:8020/api/v1/cicd/policy-validation
```

## Monitoring

The service exposes metrics at `/metrics` for Prometheus integration:

- `acgs_integration_requests_total`: Total number of requests
- `acgs_integration_auth_attempts_total`: Authentication attempts
- `acgs_integration_policy_validations_total`: Policy validations performed
- `acgs_integration_constitutional_compliance_score`: Current compliance score

## Support

For issues and questions:
- Check the logs for detailed error information
- Verify environment configuration
- Ensure network connectivity to external services (LDAP, OIDC providers)
- Review the constitutional hash validation status

## Constitutional Compliance

This service maintains strict constitutional compliance with:
- Hash validation: `cdd01ef066bc6cf2`
- Audit trail logging for all governance decisions
- Transparent policy validation processes
- Fair and consistent authentication mechanisms
