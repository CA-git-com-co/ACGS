# ACGS Secret Management Setup

## Overview

This guide provides secure methods for managing API keys and secrets in ACGS.

## ⚠️ SECURITY ALERT

**CRITICAL**: API keys were previously hardcoded in .env files. They have been removed and must be configured securely.

## Setup Methods

### Method 1: Environment Variables (Recommended for Development)

```bash
# Set environment variables in your shell
export OPENROUTER_API_KEY="your_actual_openrouter_key"
export NGC_API_KEY="your_actual_ngc_key"
export GITHUB_PERSONAL_ACCESS_TOKEN="your_actual_github_token"
export BRAVE_API_KEY="your_actual_brave_key"
export HUGGINGFACE_API_KEY="your_actual_huggingface_key"

# For persistent setup, add to ~/.bashrc or ~/.zshrc
echo 'export OPENROUTER_API_KEY="your_actual_openrouter_key"' >> ~/.bashrc
```

### Method 2: Docker Secrets (Recommended for Production)

```bash
# Create Docker secrets
echo "your_actual_openrouter_key" | docker secret create openrouter_api_key -
echo "your_actual_ngc_key" | docker secret create ngc_api_key -
echo "your_actual_github_token" | docker secret create github_token -

# Mount secrets in docker-compose.yml:
services:
  ac_service:
    secrets:
      - openrouter_api_key
      - ngc_api_key
    environment:
      - OPENROUTER_API_KEY_FILE=/run/secrets/openrouter_api_key
```

### Method 3: Kubernetes Secrets (Recommended for K8s)

```yaml
# Create secret
apiVersion: v1
kind: Secret
metadata:
  name: acgs-api-keys
type: Opaque
stringData:
  openrouter-api-key: 'your_actual_openrouter_key'
  ngc-api-key: 'your_actual_ngc_key'
  github-token: 'your_actual_github_token'

---
# Use in deployment
spec:
  containers:
    - name: ac-service
      env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: acgs-api-keys
              key: openrouter-api-key
```

### Method 4: HashiCorp Vault (Enterprise)

```bash
# Store secrets in Vault
vault kv put secret/acgs/api-keys \
  openrouter_api_key="your_actual_openrouter_key" \
  ngc_api_key="your_actual_ngc_key"

# Retrieve in application
vault kv get -field=openrouter_api_key secret/acgs/api-keys
```

## Quick Start (Development)

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Set your environment variables:

   ```bash
   export OPENROUTER_API_KEY="your_key_here"
   export NGC_API_KEY="your_key_here"
   # ... etc
   ```

3. The services will automatically pick up these environment variables.

## Security Best Practices

1. **Never commit secrets to git**
2. **Use different keys for different environments**
3. **Rotate keys regularly**
4. **Use least-privilege API keys**
5. **Monitor API key usage**
6. **Use secret scanning tools**

## Verification

Check that secrets are properly configured:

```bash
# Test service startup with secrets
cd services/core/constitutional-ai
python -c "import os; print('✓' if os.getenv('OPENROUTER_API_KEY') else '✗ Missing OPENROUTER_API_KEY')"
```

## Emergency Procedures

If API keys are compromised:

1. **Immediately revoke** the compromised keys from their respective services
2. **Generate new keys** with minimal required permissions
3. **Update the secret management system** with new keys
4. **Audit logs** for any unauthorized usage
5. **Review access controls** and monitoring

## Support

For additional help:

- Review the [Security Documentation](../security/security-config.yml)
- Check the [Authentication Service Documentation](../../services/platform/authentication/README.md)
- Contact the security team for enterprise secret management setup
