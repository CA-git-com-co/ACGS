# ACGS-1 Grafana Dashboards

## Overview

This directory contains comprehensive Grafana dashboards for the ACGS-1 (Autonomous Constitutional Governance System) monitoring and observability platform. The dashboards are organized into logical categories and provide real-time visibility into all aspects of the constitutional governance system.

## Dashboard Architecture

### Folder Structure

```
dashboards/
├── system-overview/           # High-level system dashboards
├── services/                  # Service-specific dashboards (7 ACGS services)
├── governance-workflows/      # Constitutional governance workflow monitoring
├── infrastructure/           # Infrastructure component dashboards
├── performance/              # Performance and SLA monitoring
├── blockchain/               # Quantumagi Solana integration dashboards
├── security/                 # Security and compliance dashboards
└── alerting/                 # Alert and incident management dashboards
```

## Service-Specific Dashboards

### 1. Authentication Service Dashboard
**File:** `services/authentication-service-dashboard.json`

**Key Metrics:**
- Service health and availability
- Authentication attempt rates and success rates
- MFA operations performance
- API key usage analytics
- Security event monitoring
- Session management metrics
- Database connection pool status

**Performance Targets:**
- Response time: <500ms (95th percentile)
- Availability: >99.9%
- Authentication success rate: >95%

### 2. Constitutional AI Service Dashboard
**File:** `services/constitutional-ai-service-dashboard.json`

**Key Metrics:**
- AI processing performance and latency
- Constitutional compliance scoring
- Compliance validation accuracy
- LLM reliability metrics
- Constitutional hash validations
- Council activity monitoring

**Performance Targets:**
- AI processing time: <2s (95th percentile)
- Compliance accuracy: >99%
- Constitutional compliance score: >95%

### 3. Integrity Service Dashboard
**File:** `services/integrity-service-dashboard.json`

**Key Metrics:**
- Cryptographic operation performance
- Audit trail integrity monitoring
- Data integrity scoring
- Hash verification operations
- Digital signature performance
- Tamper detection events

**Performance Targets:**
- Integrity validation: <1s (95th percentile)
- Data integrity score: >99%
- Tamper detection: Real-time

### 4. Formal Verification Service Dashboard
**File:** `services/formal-verification-service-dashboard.json`

**Key Metrics:**
- Z3 SMT solver performance
- Mathematical proof operations
- Verification duration and complexity
- Theorem proving success rates
- Verification cache performance

**Performance Targets:**
- Verification duration: <10s (95th percentile)
- Proof success rate: >95%
- Cache hit rate: >80%

### 5. Governance Synthesis Service Dashboard
**File:** `services/governance-synthesis-service-dashboard.json`

**Key Metrics:**
- LLM processing performance
- Policy synthesis success rates
- Multi-model consensus scoring
- Risk assessment operations
- Token usage analytics
- Governance workflow orchestration

**Performance Targets:**
- LLM response time: <2s (95th percentile)
- Policy synthesis success: >95%
- Multi-model consensus: >90%

### 6. Policy Governance Control (PGC) Service Dashboard
**File:** `services/pgc-service-dashboard.json`

**Key Metrics:**
- PGC validation latency (target <50ms)
- Constitutional compliance scoring
- Policy enforcement actions
- Real-time compliance monitoring
- Blockchain integration operations

**Performance Targets:**
- PGC validation: <50ms (95th percentile)
- Compliance score: 100%
- Enforcement response: <500ms

### 7. Evolutionary Computation Service Dashboard
**File:** `services/evolutionary-computation-service-dashboard.json`

**Key Metrics:**
- WINA optimization performance
- Evolutionary algorithm metrics
- Population diversity analysis
- Fitness function evaluations
- Genetic operator performance
- System performance scoring

**Performance Targets:**
- Optimization convergence: >90%
- Algorithm performance: <30s
- System performance score: >95%

## Governance Workflow Dashboards

### 1. Policy Creation Workflow
**File:** `governance-workflows/policy-creation-workflow-dashboard.json`

**Workflow Stages:**
- Draft → Review → Voting → Implementation
- Stage transition rates and success metrics
- Constitutional compliance validation
- End-to-end pipeline monitoring

### 2. Constitutional Compliance Workflow
**File:** `governance-workflows/constitutional-compliance-workflow-dashboard.json`

**Workflow Stages:**
- Validation → Assessment → Enforcement
- Compliance scoring and accuracy metrics
- Hash validation operations
- Real-time monitoring

### 3. Policy Enforcement Workflow
**File:** `governance-workflows/policy-enforcement-workflow-dashboard.json`

**Workflow Stages:**
- Monitoring → Violation Detection → Remediation
- Enforcement action tracking
- Violation detection rates
- Remediation success metrics

## Infrastructure Dashboards

### 1. Load Balancing & Circuit Breaker Dashboard
**File:** `infrastructure/load-balancing-dashboard.json`

**Key Metrics:**
- HAProxy performance and health
- Request distribution across services
- Circuit breaker status and operations
- Backend server health monitoring
- Session affinity performance
- Failover event tracking

### 2. Redis Caching Performance Dashboard
**File:** `infrastructure/redis-caching-dashboard.json`

**Key Metrics:**
- Cache hit/miss rates
- Redis connection pool usage
- Cache response times
- Memory usage and eviction rates
- Write-through/write-behind operations
- Cache invalidation events

## Executive and Business Dashboards

### 1. Executive Dashboard
**File:** `performance/executive-dashboard.json`

**Business Metrics:**
- System availability (SLA: 99.9%)
- Constitutional compliance effectiveness
- Democratic participation analytics
- Governance workflow success rates
- Concurrent user capacity (target: >1000)
- Response time performance

## Blockchain Integration Dashboards

### 1. Quantumagi Integration Dashboard
**File:** `blockchain/quantumagi-integration-dashboard.json`

**Blockchain Metrics:**
- Solana network health
- Quantumagi program invocations
- Constitutional governance on-chain validation
- Transaction latency and costs
- PGC on-chain validation
- Blockchain integration health

## Dashboard Features

### Interactive Elements
- Time range selectors (30s, 1h, 6h, 24h)
- Service filters and drill-down capabilities
- Real-time refresh (30s intervals)
- Alert integration and status indicators

### Performance Optimization
- Dashboard load times: <2 seconds
- Efficient Prometheus query patterns
- Optimized metric aggregation
- Mobile-responsive design

### Alert Integration
- Visual alert status indicators
- Incident correlation and tracking
- Escalation workflow integration
- Performance threshold monitoring

## Deployment and Configuration

### Prerequisites
- Grafana 9.3.8 or later
- Prometheus datasource configured
- ACGS custom metrics from Subtask 13.3

### Deployment
```bash
# Validate dashboards
./infrastructure/monitoring/grafana/deploy-dashboards.sh

# Import via Grafana API (when Grafana is running)
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

### Configuration Files
- `dashboard-config.yml`: Dashboard provisioning configuration
- `prometheus.yml`: Prometheus datasource configuration

## Success Criteria Achieved

✅ **Service-Specific Dashboards**: 7 comprehensive dashboards for all ACGS services
✅ **Governance Workflows**: 3+ workflow monitoring dashboards
✅ **Infrastructure Integration**: Load balancing, caching, and database monitoring
✅ **Executive Dashboards**: Business-level insights and KPIs
✅ **Blockchain Integration**: Quantumagi Solana devnet monitoring
✅ **Performance Targets**: <2s dashboard load times, <500ms response time monitoring
✅ **Custom Metrics Integration**: Full integration with Subtask 13.3 metrics
✅ **Constitutional Governance**: End-to-end workflow visibility

## Maintenance and Updates

### Regular Tasks
- Monitor dashboard performance
- Update metric queries as services evolve
- Validate alert thresholds
- Review and optimize slow queries

### Version Control
All dashboards are version-controlled and follow JSON schema validation.

## Support and Documentation

For additional information:
- ACGS-1 Documentation: https://docs.acgs.ai
- Grafana Documentation: https://grafana.com/docs/
- Prometheus Metrics: See `services/shared/metrics.py`
