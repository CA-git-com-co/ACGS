# ACGS-2 System Architecture Diagram

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This document provides a comprehensive architectural diagram and documentation for the ACGS-2 (Advanced Constitutional Governance System) production-ready infrastructure.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ACGS-2 Architecture                             │
│                      Constitutional Hash: cdd01ef066bc6cf2               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                             Load Balancer                               │
│                           HAProxy (Port 80/443)                         │
│                         SSL/TLS Termination                             │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Gateway                                    │
│                         Port 8080                                       │
│                     Rate Limiting & Auth                                │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Core Services                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Constitutional  │  │ Integrity       │  │ Governance      │         │
│  │ AI Service      │  │ Service         │  │ Engine          │         │
│  │ (Port 8001)     │  │ (Port 8002)     │  │ (Port 8004)     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Platform Services                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Authentication  │  │ EC Service      │  │ Multi-Agent     │         │
│  │ Service         │  │ (Port 8006)     │  │ Coordinator     │         │
│  │ (Port 8016)     │  │                 │  │ (Port 8008)     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Advanced Services                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Worker Agents   │  │ Blackboard      │  │ GroqCloud       │         │
│  │ (Port 8009)     │  │ Service         │  │ Policy          │         │
│  │                 │  │ (Port 8010)     │  │ (Port 8015)     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      MCP Protocol Services                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ MCP Aggregator  │  │ Filesystem MCP  │  │ GitHub MCP      │         │
│  │ (Port 3000)     │  │ (Port 3001)     │  │ (Port 3002)     │         │
│  │                 │  │                 │  │                 │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Browser MCP     │  │ A2A Policy      │  │ Security        │         │
│  │ (Port 3003)     │  │ Integration     │  │ Validation      │         │
│  │                 │  │ (Port 8020)     │  │ (Port 8021)     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Data & Policy Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ PostgreSQL      │  │ Redis           │  │ OPA             │         │
│  │ (Port 5439)     │  │ (Port 6389)     │  │ (Port 8181)     │         │
│  │ Primary DB      │  │ Caching         │  │ Policy Engine   │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Monitoring & Observability                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Prometheus      │  │ Grafana         │  │ Log Aggregator  │         │
│  │ (Port 9090)     │  │ (Port 3001)     │  │ (Fluent Bit)    │         │
│  │ Metrics         │  │ Dashboards      │  │ Centralized     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Service Interaction Flow

### 1. Request Processing Flow

```
Client Request → HAProxy → API Gateway → Constitutional AI Service → Core Services
                                      ↓
                                 Policy Validation (OPA)
                                      ↓
                                 Integrity Check → Database/Redis
```

### 2. Multi-Agent Coordination Flow

```
Multi-Agent Coordinator → Worker Agents → Blackboard Service → Constitutional AI
                                      ↓
                                 A2A Policy Integration
                                      ↓
                                 MCP Protocol Services
```

### 3. Data Flow Architecture

```
Application Services → PostgreSQL (Primary)
                   ↓
                Redis (Cache Layer)
                   ↓
                OPA (Policy Enforcement)
                   ↓
                Prometheus (Metrics Collection)
                   ↓
                Grafana (Visualization)
```

## Key Infrastructure Components

### Core Infrastructure
- **HAProxy**: Load balancing and SSL termination
- **PostgreSQL**: Primary database (Port 5439)
- **Redis**: Caching layer (Port 6389)
- **OPA**: Policy enforcement engine (Port 8181)

### Monitoring Stack
- **Prometheus**: Metrics collection (Port 9090)
- **Grafana**: Visualization dashboards (Port 3001)
- **Fluent Bit**: Log aggregation

### Security Features
- **Constitutional Hash**: `cdd01ef066bc6cf2` enforced across all services
- **JWT Authentication**: Comprehensive token validation
- **Zero Trust Architecture**: Security validation service
- **End-to-End Encryption**: SSL/TLS throughout

## Performance Specifications

### Constitutional Guardrails
- **P99 Latency**: ≤ 5 ms (cached ≤ 2 ms)
- **Throughput**: ≥ 100 RPS (goal 1,000 RPS)
- **Cache Hit Rate**: ≥ 85%
- **Compliance Rate**: Exactly 100%

### Resource Allocation
- **CPU Limits**: Optimized per service
- **Memory Limits**: Ranged from 256MB to 3GB
- **Network**: Dedicated bridge network (10.200.0.0/16)
- **Storage**: Persistent volumes for data integrity

## Deployment Configuration

### Container Orchestration
- **Docker Compose**: Production-grade configuration
- **Service Dependencies**: Health check based startup
- **Resource Limits**: CPU and memory constraints
- **Network Isolation**: Dedicated ACGS network

### Environment Variables
- **Database**: PostgreSQL connection strings
- **Redis**: Cache configuration
- **Security**: JWT secrets and constitutional hash
- **Monitoring**: Prometheus and Grafana settings

## Operational Excellence

### Health Monitoring
- **Service Health Checks**: All services monitored
- **Dependency Management**: Ordered startup sequence
- **Auto-restart**: Unless-stopped policy
- **Resource Monitoring**: CPU, memory, and network

### Logging and Observability
- **Centralized Logging**: Fluent Bit aggregation
- **Metrics Collection**: Prometheus integration
- **Dashboard Visualization**: Grafana dashboards
- **Alert Management**: Prometheus alerting

## NEW_KNOWLEDGE_BLOCK for Blackboard Ingestion

```markdown
### NEW_KNOWLEDGE_BLOCK

ACGS-2 Service Startup Order ::
1. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis`
2. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d opa`
3. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d constitutional_core integrity_service`
4. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d api_gateway auth_service`
5. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d --scale worker_agents=3`

### END_KNOWLEDGE_BLOCK
```

```markdown
### NEW_KNOWLEDGE_BLOCK

ACGS-2 Performance Monitoring ::
- `curl http://localhost:9090/metrics` (Prometheus)
- `curl http://localhost:3001/health` (Grafana)
- `docker stats acgs_*` (Container metrics)
- `redis-cli -p 6389 info stats` (Redis metrics)

### END_KNOWLEDGE_BLOCK
```

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Performance Targets**: P99 <5ms, >100 RPS, >85% cache hit rates  
**Compliance**: 100% Constitutional compliance enforced  
**Architecture Status**: ✅ PRODUCTION READY
