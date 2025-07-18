# ACGS-2 Infrastructure Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "External"
        Client[Client Applications]
        Admin[Admin Interface]
    end
    
    subgraph "Load Balancing Layer"
        HAProxy[HAProxy<br/>Load Balancer]
    end
    
    subgraph "Application Layer"
        API1[API Server 1]
        API2[API Server 2]
        API3[API Server N]
    end
    
    subgraph "Policy & Governance"
        OPA[OPA<br/>Open Policy Agent<br/>Constitutional Validation]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>Primary Database)]
        Redis[(Redis<br/>Cache Layer)]
    end
    
    subgraph "Monitoring & Observability"
        Prometheus[Prometheus<br/>Metrics Collection]
        Grafana[Grafana<br/>Dashboards & Alerts]
    end
    
    %% Connections
    Client --> HAProxy
    Admin --> HAProxy
    
    HAProxy --> API1
    HAProxy --> API2
    HAProxy --> API3
    
    API1 --> OPA
    API2 --> OPA
    API3 --> OPA
    
    API1 --> PostgreSQL
    API2 --> PostgreSQL
    API3 --> PostgreSQL
    
    API1 --> Redis
    API2 --> Redis
    API3 --> Redis
    
    API1 --> Prometheus
    API2 --> Prometheus
    API3 --> Prometheus
    
    HAProxy --> Prometheus
    PostgreSQL --> Prometheus
    Redis --> Prometheus
    OPA --> Prometheus
    
    Prometheus --> Grafana
    
    %% Styling
    classDef database fill:#e1f5fe
    classDef monitoring fill:#f3e5f5
    classDef policy fill:#fff3e0
    classDef loadbalancer fill:#e8f5e8
    
    class PostgreSQL,Redis database
    class Prometheus,Grafana monitoring
    class OPA policy
    class HAProxy loadbalancer
```

## Component Responsibilities

### Load Balancing Layer
- **HAProxy**: Distributes incoming requests across multiple API servers
- Implements health checks and failover mechanisms
- Provides SSL termination and request routing

### Application Layer
- **API Servers**: Handle business logic and request processing
- Implement constitutional validation through OPA integration
- Manage database connections and caching strategies

### Policy & Governance
- **OPA (Open Policy Agent)**: Enforces constitutional guardrails
- Validates all requests against defined policies
- Ensures 100% compliance rate requirement

### Data Layer
- **PostgreSQL**: Primary data persistence with ACID guarantees
- **Redis**: High-performance caching layer for sub-5ms response times

### Monitoring & Observability
- **Prometheus**: Collects and stores metrics from all components
- **Grafana**: Provides real-time dashboards and alerting

## Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| P99 Latency | ≤ 5ms | ≤ 2ms (cached) |
| Throughput | ≥ 100 RPS | Goal: 1,000 RPS |
| Cache Hit Rate | ≥ 85% | Must maintain |
| Compliance Rate | 100% | Zero tolerance |

## Constitutional Guardrails

All components must validate against constitutional hash: `cdd01ef066bc6cf2`

- **Zero-tolerance policy violations**: Any compliance failure triggers immediate escalation
- **Performance monitoring**: Continuous validation of latency and throughput targets
- **Audit trail**: Complete traceability of all decisions and actions
- **Fail-safe mechanisms**: Automatic escalation when guardrails are violated
