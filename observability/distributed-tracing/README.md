# ACGS-2 Distributed Tracing Implementation
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive distributed tracing implementation for ACGS-2 (Advanced Constitutional Governance System). This system provides end-to-end observability across all ACGS-2 services with constitutional compliance monitoring, performance analysis, and advanced trace analytics.

## Constitutional Compliance

All distributed tracing components maintain constitutional hash `cdd01ef066bc6cf2` validation and enforce performance targets:
- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Trace Sampling**: 100% for constitutional operations
- **Compliance Monitoring**: Real-time constitutional hash validation

## Architecture

### Distributed Tracing Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Constitutional│  │ GroqCloud   │  │    Auth     │        │
│  │    Core     │  │   Policy    │  │  Service    │        │
│  │  + Tracing  │  │  + Tracing  │  │  + Tracing  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 OpenTelemetry Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    OTEL     │  │ Instrumentation│  │   Trace    │        │
│  │  Collector  │  │   Libraries   │  │  Analyzer  │        │
│  │  (3 replicas│  │  (Auto-inject)│  │ (Analysis) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Jaeger Backend                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Jaeger    │  │   Jaeger    │  │   Jaeger    │        │
│  │  Collector  │  │    Query    │  │    Agent    │        │
│  │ (2 replicas)│  │ (2 replicas)│  │ (DaemonSet) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Elasticsearch Storage                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Elasticsearch│  │Elasticsearch│  │Elasticsearch│        │
│  │   Node 1    │  │   Node 2    │  │   Node 3    │        │
│  │  (20GB SSD) │  │  (20GB SSD) │  │  (20GB SSD) │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## System Components

### 1. Jaeger Deployment (`jaeger-deployment.yaml`)
- **Jaeger Collector**: Receives and processes trace data
- **Jaeger Query**: Provides query interface and web UI
- **Jaeger Agent**: Collects traces from application sidecars
- **Elasticsearch Backend**: Persistent storage for trace data
- **Constitutional Compliance**: Hash validation and performance monitoring

### 2. OpenTelemetry Collector (`opentelemetry-collector.yaml`)
- **Multi-protocol Support**: OTLP, Jaeger, Zipkin protocols
- **Trace Processing**: Filtering, sampling, and enrichment
- **Constitutional Validation**: Hash compliance checking
- **Performance Monitoring**: Latency and throughput analysis
- **Batch Processing**: Optimized for high-throughput scenarios

### 3. Tracing Instrumentation (`tracing-instrumentation.py`)
- **Automatic Instrumentation**: FastAPI, HTTP clients, databases
- **Constitutional Decorators**: @trace_constitutional, @trace_consensus
- **Performance Monitoring**: P99 latency tracking
- **Custom Attributes**: Constitutional hash, compliance status
- **Error Handling**: Exception tracking and correlation

### 4. Trace Analyzer (`trace-analyzer.py`)
- **Constitutional Compliance Analysis**: Hash validation monitoring
- **Performance Analysis**: Latency distribution and anomaly detection
- **Security Analysis**: Authentication and authorization tracking
- **Dependency Analysis**: Service communication patterns
- **Anomaly Detection**: Statistical deviation analysis

### 5. Deployment Manager (`distributed-tracing-deploy.py`)
- **Automated Deployment**: Complete infrastructure setup
- **Configuration Management**: Service-specific instrumentation
- **Health Monitoring**: Component availability verification
- **Performance Validation**: Constitutional compliance checking

## Installation

### Prerequisites
```bash
# Kubernetes cluster v1.25+
kubectl version --short

# Sufficient resources (minimum 8 CPUs, 16GB RAM)
kubectl get nodes

# ACGS-2 namespace exists
kubectl get namespace acgs-system
```

### Automated Deployment
```bash
# Run complete deployment
cd /observability/distributed-tracing
python3 distributed-tracing-deploy.py

# Verify deployment
kubectl get pods -n jaeger-system
kubectl get pods -n acgs-system -l app=otel-collector
```

### Manual Installation
```bash
# 1. Deploy Jaeger infrastructure
kubectl apply -f jaeger-deployment.yaml

# 2. Deploy OpenTelemetry collector
kubectl apply -f opentelemetry-collector.yaml

# 3. Configure service instrumentation
kubectl annotate deployment constitutional-core -n acgs-system \
  instrumentation.opentelemetry.io/inject-python=true \
  constitutional-hash=cdd01ef066bc6cf2

# 4. Deploy trace analyzer
kubectl apply -f trace-analyzer-deployment.yaml
```

## Configuration

### Tracing Configuration
```yaml
# tracing-config.yaml
jaeger:
  version: "1.49.0"
  namespace: "jaeger-system"
  sampling_rate: 1.0
  max_traces_per_second: 1000
  
elasticsearch:
  replicas: 3
  storage_per_node: "20Gi"
  index_prefix: "acgs-traces"
  
otel_collector:
  replicas: 3
  batch_size: 1024
  timeout: "1s"
  
constitutional_validation:
  enabled: true
  strict_mode: true
  hash: "cdd01ef066bc6cf2"
```

### Service Instrumentation
```yaml
# Service-specific configuration
services:
  constitutional-core:
    sampling_rate: 1.0
    constitutional_compliance: true
    performance_monitoring: true
    
  groqcloud-policy:
    sampling_rate: 1.0
    constitutional_compliance: true
    external_api_tracing: true
    
  auth-service:
    sampling_rate: 1.0
    constitutional_compliance: true
    security_monitoring: true
```

## Usage

### Application Instrumentation

#### Python Services
```python
from observability.distributed_tracing.tracing_instrumentation import (
    initialize_tracing, trace_constitutional, trace_consensus
)

# Initialize tracing
tracing = initialize_tracing("constitutional-core")

# Trace constitutional operations
@trace_constitutional("constitutional_validation")
async def validate_constitutional_compliance(data):
    # Constitutional processing logic
    return validation_result

# Trace consensus operations
@trace_consensus("consensus_agreement")
async def process_consensus(proposals):
    # Consensus processing logic
    return consensus_result

# Manual tracing
async def complex_operation():
    with tracing.trace_constitutional_operation(
        "complex_constitutional_operation",
        TraceCategory.CONSTITUTIONAL,
        ConstitutionalComplianceLevel.COMPLIANT
    ) as span:
        span.set_attribute("operation_type", "complex")
        # Operation logic
        return result
```

#### Database Operations
```python
# Trace database operations
async def update_constitutional_data():
    with tracing.trace_database_operation(
        "update_constitutional_record",
        "constitutional_data",
        constitutional_data=True
    ) as span:
        # Database operation
        result = await db.execute(query)
        span.set_attribute("rows_affected", result.rowcount)
        return result
```

#### External API Calls
```python
# Trace external API calls
async def call_groq_api():
    with tracing.trace_external_api_call(
        "groq",
        "https://api.groq.com/openai/v1/chat/completions",
        "POST",
        constitutional_headers=True
    ) as span:
        # API call with constitutional headers
        response = await http_client.post(
            url,
            headers={"constitutional-hash": "cdd01ef066bc6cf2"}
        )
        span.set_attribute("response_status", response.status_code)
        return response
```

### Trace Analysis

#### Constitutional Compliance Analysis
```python
from observability.distributed_tracing.trace_analyzer import ACGSTraceAnalyzer

# Initialize analyzer
analyzer = ACGSTraceAnalyzer()
await analyzer.initialize()

# Run compliance analysis
traces = await analyzer.fetch_traces(service_name="constitutional-core")
compliance_results = await analyzer.analyze_constitutional_compliance(traces)

# Check for violations
violations = [r for r in compliance_results if not r.constitutional_compliance]
print(f"Found {len(violations)} constitutional violations")
```

#### Performance Analysis
```python
# Analyze performance patterns
performance_results = await analyzer.analyze_performance(traces)

# Check for latency issues
high_latency = [r for r in performance_results if "High P99 Latency" in r.title]
print(f"High latency services: {len(high_latency)}")
```

#### Comprehensive Analysis
```python
# Run full analysis
summary = await analyzer.run_comprehensive_analysis(
    service_name="constitutional-core",
    lookback_minutes=60
)

print(f"Analyzed {summary['traces_analyzed']} traces")
print(f"Found {summary['results']['total_issues']} issues")
print(f"Compliance rate: {summary['constitutional_compliance']['compliance_rate']:.2f}%")
```

## Monitoring and Alerting

### Constitutional Compliance Monitoring
```yaml
# Constitutional compliance alerts
alerts:
  - name: "ConstitutionalHashViolation"
    condition: "constitutional_hash_mismatch > 0"
    severity: "critical"
    description: "Constitutional hash validation failed"
    
  - name: "ConstitutionalComplianceRate"
    condition: "constitutional_compliance_rate < 0.95"
    severity: "warning"
    description: "Constitutional compliance rate below 95%"
```

### Performance Monitoring
```yaml
# Performance alerts
alerts:
  - name: "HighTraceLatency"
    condition: "p99_trace_latency > 5ms"
    severity: "warning"
    description: "P99 trace latency exceeds constitutional requirement"
    
  - name: "LowTraceThroughput"
    condition: "trace_throughput < 100rps"
    severity: "warning"
    description: "Trace throughput below minimum requirement"
```

### Jaeger UI Access
```bash
# Port forward to Jaeger UI
kubectl port-forward -n jaeger-system svc/jaeger-query 16686:16686

# Access UI at http://localhost:16686
# Search for traces with constitutional-hash tag
```

## Performance Optimization

### Sampling Strategies
```yaml
# Sampling configuration
sampling:
  default_strategy:
    type: "probabilistic"
    param: 1.0
    
  per_service_strategies:
    - service: "constitutional-core"
      type: "probabilistic"
      param: 1.0  # 100% sampling
      
    - service: "health-check"
      type: "probabilistic"
      param: 0.01  # 1% sampling
```

### Batch Processing
```yaml
# Batch processing configuration
processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
    send_batch_max_size: 2048
    
  memory_limiter:
    check_interval: 1s
    limit_mib: 1024
```

### Storage Optimization
```yaml
# Elasticsearch optimization
elasticsearch:
  settings:
    number_of_shards: 3
    number_of_replicas: 1
    refresh_interval: "30s"
    
  retention:
    default_ttl: "168h"  # 7 days
    constitutional_ttl: "720h"  # 30 days
```

## Troubleshooting

### Common Issues

1. **Traces Not Appearing**
```bash
# Check OpenTelemetry collector logs
kubectl logs -n acgs-system -l app=otel-collector

# Check Jaeger collector logs
kubectl logs -n jaeger-system -l app=jaeger-collector

# Verify service instrumentation
kubectl get deployment constitutional-core -n acgs-system -o yaml | grep -A 10 annotations
```

2. **High Memory Usage**
```bash
# Check OpenTelemetry collector resource usage
kubectl top pods -n acgs-system -l app=otel-collector

# Adjust memory limits
kubectl patch deployment otel-collector -n acgs-system -p '{"spec":{"template":{"spec":{"containers":[{"name":"otel-collector","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
```

3. **Constitutional Hash Violations**
```bash
# Check for missing constitutional headers
kubectl logs -n acgs-system constitutional-core | grep "constitutional-hash"

# Verify service mesh configuration
kubectl get envoyfilter -n acgs-system acgs-constitutional-header -o yaml
```

### Debugging Commands
```bash
# Check Jaeger health
kubectl exec -n jaeger-system deployment/jaeger-query -- wget -q --spider http://localhost:16686/

# Test OpenTelemetry collector
kubectl exec -n acgs-system deployment/otel-collector -- curl -s http://localhost:13133/

# Check Elasticsearch cluster health
kubectl exec -n jaeger-system deployment/elasticsearch -- curl -s http://localhost:9200/_cluster/health

# View trace statistics
kubectl exec -n acgs-system deployment/trace-analyzer -- python3 -c "
import asyncio
from trace_analyzer import ACGSTraceAnalyzer
async def main():
    analyzer = ACGSTraceAnalyzer()
    await analyzer.initialize()
    summary = await analyzer.run_comprehensive_analysis()
    print(summary)
asyncio.run(main())
"
```

## Best Practices

### Constitutional Compliance
- Always include constitutional hash in trace attributes
- Use dedicated sampling strategies for constitutional operations
- Monitor compliance rates continuously
- Alert on constitutional violations immediately

### Performance Optimization
- Monitor P99 latency and maintain <5ms target
- Use appropriate sampling rates for different services
- Implement batch processing for high-throughput scenarios
- Regular performance baseline updates

### Security Considerations
- Ensure TLS encryption for all trace data
- Implement proper authentication for Jaeger UI
- Regular security audits of trace data
- Sanitize sensitive information in trace attributes

### Operational Excellence
- Implement automated deployment and rollback
- Monitor component health and availability
- Regular backup and disaster recovery testing
- Comprehensive documentation and runbooks

---

**Navigation**: [Root](../../CLAUDE.md) | [Observability](../README.md) | [Service Mesh](../../deployment/service-mesh/README.md)

**Constitutional Compliance**: All distributed tracing components maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS, 100% constitutional sampling).

**Last Updated**: 2025-07-18 - Distributed tracing implementation complete