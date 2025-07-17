# GroqCloud Integration Configuration

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This document provides comprehensive configuration guidance for the GroqCloud Policy Integration service, which combines ultra-low latency Language Processing Units (LPUs) with WebAssembly-compiled policy enforcement for constitutional AI governance at scale.

## Configuration Structure

### Environment Variables

#### Core GroqCloud Settings
```bash
# GroqCloud API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_POLICY_INTEGRATION_PORT=8015

# Model Configuration
GROQ_DEFAULT_MODEL=qwen/qwen3-32b
GROQ_TIER_MAPPING=nano:allam-2-7b,fast:llama-3.1-8b-instant,balanced:qwen/qwen3-32b,premium:llama-3.3-70b-versatile

# Constitutional Compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_VALIDATION_ENABLED=true
```

#### WASM Policy Engine Configuration
```bash
# WASM Runtime Settings
WASM_POLICY_ENGINE_ENABLED=true
WASM_POLICY_COMPILATION_TIMEOUT=30
WASM_POLICY_CACHE_SIZE=1000
WASM_RUNTIME=wasmtime

# OPA-WASM Integration
OPA_WASM_ENABLED=true
OPA_WASM_POLICIES_PATH=/app/policies
OPA_WASM_CACHE_SIZE=500
OPA_WASM_EVALUATION_TIMEOUT=5
```

#### Performance Configuration
```bash
# Performance Targets
GROQ_P99_LATENCY_TARGET=5
GROQ_THROUGHPUT_TARGET=100
GROQ_CACHE_HIT_RATE_TARGET=85

# Circuit Breaker Settings
GROQ_CIRCUIT_BREAKER_ENABLED=true
GROQ_CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
GROQ_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=30
GROQ_CIRCUIT_BREAKER_RETRY_TIMEOUT=10
```

#### Caching Configuration
```bash
# Semantic Cache Settings
GROQ_SEMANTIC_CACHE_ENABLED=true
GROQ_SEMANTIC_CACHE_TTL=3600
GROQ_SEMANTIC_CACHE_SIZE=1000
GROQ_SEMANTIC_CACHE_SIMILARITY_THRESHOLD=0.85

# Response Cache Settings
GROQ_RESPONSE_CACHE_ENABLED=true
GROQ_RESPONSE_CACHE_TTL=1800
GROQ_RESPONSE_CACHE_SIZE=500
```

### Model Tier Configuration

#### Tier 1: Nano (Ultra-Fast)
```yaml
nano:
  model_id: "allam-2-7b"
  model_name: "Allam 2 7B"
  context_length: 4096
  avg_latency_ms: 50
  cost_per_token: 0.00000005
  use_cases:
    - "Simple queries"
    - "Basic reasoning"
    - "Quick responses"
  constitutional_compliance_score: 0.82
```

#### Tier 2: Fast
```yaml
fast:
  model_id: "llama-3.1-8b-instant"
  model_name: "Llama 3.1 8B Instant"
  context_length: 131072
  avg_latency_ms: 80
  cost_per_token: 0.00000015
  use_cases:
    - "Code generation"
    - "Moderate reasoning"
    - "Content creation"
  constitutional_compliance_score: 0.87
```

#### Tier 3: Balanced
```yaml
balanced:
  model_id: "qwen/qwen3-32b"
  model_name: "Qwen3 32B"
  context_length: 131072
  avg_latency_ms: 200
  cost_per_token: 0.0000008
  use_cases:
    - "Complex analysis"
    - "Constitutional review"
    - "Policy synthesis"
  constitutional_compliance_score: 0.90
```

#### Tier 4: Premium
```yaml
premium:
  model_id: "llama-3.3-70b-versatile"
  model_name: "Llama 3.3 70B Versatile"
  context_length: 131072
  avg_latency_ms: 300
  cost_per_token: 0.0000009
  use_cases:
    - "Advanced reasoning"
    - "Governance synthesis"
    - "Legal analysis"
  constitutional_compliance_score: 0.92
```

### Policy Configuration

#### Constitutional Compliance Policies
```rego
# Constitutional Compliance Policy
package constitutional_compliance

import rego.v1

# Allow if content meets constitutional standards
allow if {
    input.constitutional_hash == "cdd01ef066bc6cf2"
    compliance_score >= 0.8
    no_harmful_content
}

# Calculate compliance score
compliance_score := score if {
    checks := [
        ethical_check,
        legal_check,
        safety_check,
        transparency_check
    ]
    passed := count([check | check := checks[_]; check == true])
    score := passed / count(checks)
}
```

#### Safety Guardrails Policy
```rego
# Safety Guardrails Policy
package safety_guardrails

import rego.v1

# Block harmful content
deny[reason] if {
    contains_harmful_content(input.content)
    reason := "Content contains harmful suggestions"
}

# Block privacy violations
deny[reason] if {
    contains_personal_data(input.content)
    reason := "Content contains personal information"
}

# Block misinformation
deny[reason] if {
    contains_misinformation(input.content)
    reason := "Content contains potential misinformation"
}
```

### Kubernetes Configuration

#### Deployment Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: groq-policy-integration
  namespace: acgs-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: groq-policy-integration
  template:
    metadata:
      labels:
        app: groq-policy-integration
    spec:
      containers:
      - name: groq-policy-integration
        image: acgs/groq-policy-integration:latest
        ports:
        - containerPort: 8015
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: groq-secrets
              key: api-key
        - name: GROQ_POLICY_INTEGRATION_PORT
          value: "8015"
        - name: WASM_POLICY_ENGINE_ENABLED
          value: "true"
        - name: OPA_WASM_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8015
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8015
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: groq-policy-integration
  namespace: acgs-system
spec:
  selector:
    app: groq-policy-integration
  ports:
  - port: 8015
    targetPort: 8015
    name: http
  type: ClusterIP
```

#### ConfigMap for Policies
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: groq-policies
  namespace: acgs-system
data:
  constitutional_compliance.rego: |
    package constitutional_compliance
    
    import rego.v1
    
    # Constitutional compliance rules
    allow if {
        input.constitutional_hash == "cdd01ef066bc6cf2"
        compliance_score >= 0.8
    }
    
    compliance_score := score if {
        # Implementation details...
    }
  
  safety_guardrails.rego: |
    package safety_guardrails
    
    import rego.v1
    
    # Safety guardrail rules
    deny[reason] if {
        contains_harmful_content(input.content)
        reason := "Content violates safety guidelines"
    }
```

### Docker Compose Configuration

#### Development Environment
```yaml
version: '3.8'
services:
  groq-policy-integration:
    build: 
      context: .
      dockerfile: services/core/governance-synthesis/Dockerfile
    ports:
      - "8015:8015"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GROQ_POLICY_INTEGRATION_PORT=8015
      - WASM_POLICY_ENGINE_ENABLED=true
      - OPA_WASM_ENABLED=true
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
      - postgresql
    volumes:
      - ./services/core/governance-synthesis/policies:/app/policies
    networks:
      - acgs-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - acgs-network

  postgresql:
    image: postgres:15
    environment:
      - POSTGRES_DB=acgs
      - POSTGRES_USER=acgs_user
      - POSTGRES_PASSWORD=acgs_password
    ports:
      - "5432:5432"
    networks:
      - acgs-network

networks:
  acgs-network:
    driver: bridge
```

### Monitoring Configuration

#### Prometheus Metrics
```yaml
# Prometheus scrape configuration
- job_name: 'groq-policy-integration'
  static_configs:
    - targets: ['groq-policy-integration:8015']
  metrics_path: '/metrics'
  scrape_interval: 15s
  scrape_timeout: 10s
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "GroqCloud Policy Integration",
    "panels": [
      {
        "title": "Request Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "groq_request_duration_seconds",
            "legendFormat": "{{quantile}}"
          }
        ]
      },
      {
        "title": "Policy Evaluation Time",
        "type": "graph",
        "targets": [
          {
            "expr": "groq_policy_evaluation_duration_seconds",
            "legendFormat": "Policy Evaluation"
          }
        ]
      },
      {
        "title": "Constitutional Compliance Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "groq_constitutional_compliance_rate",
            "legendFormat": "Compliance Rate"
          }
        ]
      }
    ]
  }
}
```

#### Alerting Rules
```yaml
groups:
- name: groq-policy-integration
  rules:
  - alert: GroqHighLatency
    expr: groq_request_duration_seconds{quantile="0.99"} > 0.005
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "GroqCloud Policy Integration high latency"
      description: "P99 latency is {{ $value }}s, exceeding 5ms target"

  - alert: GroqPolicyViolation
    expr: groq_constitutional_compliance_rate < 0.95
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Constitutional compliance rate below threshold"
      description: "Compliance rate is {{ $value }}, below 95% threshold"

  - alert: GroqServiceDown
    expr: up{job="groq-policy-integration"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "GroqCloud Policy Integration service down"
      description: "Service has been down for more than 1 minute"
```

### Security Configuration

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: groq-policy-integration-netpol
  namespace: acgs-system
spec:
  podSelector:
    matchLabels:
      app: groq-policy-integration
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: acgs-system
    ports:
    - protocol: TCP
      port: 8015
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS to GroqCloud API
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 5432  # PostgreSQL
```

#### RBAC Configuration
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: groq-policy-integration
  namespace: acgs-system
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: groq-policy-integration
  namespace: acgs-system
subjects:
- kind: ServiceAccount
  name: groq-policy-integration
  namespace: acgs-system
roleRef:
  kind: Role
  name: groq-policy-integration
  apiGroup: rbac.authorization.k8s.io
```

### Configuration Validation

#### Schema Validation
```yaml
# Configuration schema for validation
groq_config_schema:
  type: object
  required:
    - groq_api_key
    - constitutional_hash
    - port
  properties:
    groq_api_key:
      type: string
      pattern: "^gsk_[a-zA-Z0-9]{48}$"
    constitutional_hash:
      type: string
      pattern: "^cdd01ef066bc6cf2$"
    port:
      type: integer
      minimum: 1024
      maximum: 65535
    wasm_enabled:
      type: boolean
      default: true
    opa_enabled:
      type: boolean
      default: true
```

#### Validation Script
```python
#!/usr/bin/env python3
"""
GroqCloud configuration validation script
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import yaml
import json
from jsonschema import validate, ValidationError

def validate_groq_config():
    """Validate GroqCloud configuration"""
    
    # Load configuration
    config = {
        'groq_api_key': os.environ.get('GROQ_API_KEY'),
        'constitutional_hash': os.environ.get('CONSTITUTIONAL_HASH'),
        'port': int(os.environ.get('GROQ_POLICY_INTEGRATION_PORT', 8015)),
        'wasm_enabled': os.environ.get('WASM_POLICY_ENGINE_ENABLED', 'true').lower() == 'true',
        'opa_enabled': os.environ.get('OPA_WASM_ENABLED', 'true').lower() == 'true'
    }
    
    # Validation schema
    schema = {
        "type": "object",
        "required": ["groq_api_key", "constitutional_hash", "port"],
        "properties": {
            "groq_api_key": {
                "type": "string",
                "pattern": "^gsk_[a-zA-Z0-9]{48}$"
            },
            "constitutional_hash": {
                "type": "string",
                "pattern": "^cdd01ef066bc6cf2$"
            },
            "port": {
                "type": "integer",
                "minimum": 1024,
                "maximum": 65535
            }
        }
    }
    
    try:
        validate(config, schema)
        print("✅ GroqCloud configuration validation passed")
        return True
    except ValidationError as e:
        print(f"❌ Configuration validation failed: {e.message}")
        return False

if __name__ == "__main__":
    if not validate_groq_config():
        sys.exit(1)
```

### Troubleshooting

#### Common Issues

1. **API Key Authentication Failure**
   ```bash
   # Check API key format
   echo $GROQ_API_KEY | grep -E "^gsk_[a-zA-Z0-9]{48}$"
   
   # Test API connectivity
   curl -H "Authorization: Bearer $GROQ_API_KEY" \
        https://api.groq.com/openai/v1/models
   ```

2. **WASM Policy Compilation Issues**
   ```bash
   # Check WASM runtime availability
   wasmtime --version
   
   # Validate policy syntax
   opa fmt --diff services/core/governance-synthesis/policies/
   ```

3. **High Latency Issues**
   ```bash
   # Check circuit breaker status
   curl http://localhost:8015/health | jq '.circuit_breaker'
   
   # Monitor cache hit rates
   curl http://localhost:8015/metrics | grep cache_hit_rate
   ```

#### Performance Tuning

1. **Optimize Cache Settings**
   ```bash
   # Increase cache sizes for better performance
   export GROQ_SEMANTIC_CACHE_SIZE=2000
   export GROQ_RESPONSE_CACHE_SIZE=1000
   export WASM_POLICY_CACHE_SIZE=1500
   ```

2. **Tune Circuit Breaker**
   ```bash
   # Adjust circuit breaker thresholds
   export GROQ_CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
   export GROQ_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=15
   ```

3. **Memory Optimization**
   ```bash
   # Increase memory limits for better performance
   # In Kubernetes deployment
   resources:
     limits:
       memory: "1Gi"
       cpu: "1000m"
   ```


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

---

**Constitutional Compliance**: This configuration maintains constitutional hash `cdd01ef066bc6cf2` validation with comprehensive performance monitoring, security enforcement, and policy compliance for production-ready ACGS-2 GroqCloud integration.

**Last Updated**: July 15, 2025 - Initial GroqCloud integration configuration documentation