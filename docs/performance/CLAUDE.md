<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - Performance Guide Documentation

## Directory Overview

The Performance Guide provides comprehensive documentation for performance optimization, monitoring, and benchmarking within the ACGS-2 constitutional AI governance framework. This includes performance targets, optimization strategies, and monitoring procedures.

## File Inventory

- **CLAUDE.md**: This documentation file
- **performance-targets.md**: Detailed performance targets and SLAs
- **optimization-guide.md**: Performance optimization strategies and techniques
- **monitoring-setup.md**: Performance monitoring configuration and procedures
- **benchmarking-guide.md**: Performance benchmarking methodologies
- **troubleshooting.md**: Performance issue diagnosis and resolution

## Dependencies & Interactions

- **ACGS-2 Core Services**: Performance monitoring for all constitutional AI services
- **Monitoring Infrastructure**: Prometheus, Grafana, and alerting systems
- **Constitutional Framework**: Performance compliance with hash `cdd01ef066bc6cf2`
- **Load Testing Tools**: Performance validation and stress testing
- **Database Systems**: PostgreSQL and Redis performance optimization

## Key Components

### Performance Targets Framework
- **P99 Latency**: <5ms for all core operations
- **Throughput**: >100 RPS for governance decisions
- **Cache Hit Rate**: >85% for constitutional decisions
- **Constitutional Compliance**: 100% with <1ms overhead
- **Availability**: 99.9% uptime with graceful degradation

### Performance Monitoring Stack
- **Prometheus**: Metrics collection and storage
- **Grafana**: Performance dashboards and visualization
- **AlertManager**: Performance threshold alerting
- **Jaeger**: Distributed tracing for latency analysis
- **Custom Metrics**: Constitutional compliance performance tracking

### Optimization Strategies
- **Caching**: Multi-tier caching with Redis and in-memory stores
- **Database Optimization**: Connection pooling, query optimization
- **Async Processing**: Non-blocking operations and event-driven architecture
- **Load Balancing**: Intelligent request distribution
- **Resource Management**: CPU, memory, and I/O optimization

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: Performance monitoring infrastructure
✅ **IMPLEMENTED**: Core performance targets
✅ **IMPLEMENTED**: Automated performance testing
🔄 **IN PROGRESS**: Advanced performance analytics
🔄 **IN PROGRESS**: Predictive performance scaling
❌ **PLANNED**: AI-driven performance optimization
❌ **PLANNED**: Real-time performance tuning

## Performance Considerations

- **Monitoring Overhead**: <1% impact on system performance
- **Constitutional Validation**: <1ms additional latency
- **Metrics Collection**: Optimized for minimal resource usage
- **Dashboard Rendering**: Real-time updates with efficient queries
- **Alerting Latency**: <30 seconds for critical performance issues

## Implementation Status

### ✅ IMPLEMENTED
- Core performance monitoring infrastructure
- Basic performance targets and SLAs
- Automated performance testing suite
- Performance dashboards and alerting
- Constitutional compliance performance tracking

### 🔄 IN PROGRESS
- Advanced performance analytics and insights
- Predictive performance scaling algorithms
- Real-time performance optimization
- Enhanced performance troubleshooting tools
- Cross-service performance correlation

### ❌ PLANNED
- AI-driven performance optimization
- Automated performance tuning
- Advanced capacity planning tools
- Performance regression detection
- Intelligent performance alerting

## Performance Targets

### Core Service Performance
```yaml
# ACGS-2 Performance Targets
constitutional_ai_service:
  p99_latency: 5ms
  throughput: 1000rps
  availability: 99.9%
  cache_hit_rate: 95%

integrity_service:
  p99_latency: 3ms
  throughput: 2000rps
  availability: 99.9%
  audit_latency: 10ms

multi_agent_coordinator:
  p99_latency: 10ms
  throughput: 500rps
  coordination_overhead: 5ms
  agent_response_time: 100ms

expert_service:
  groq_api_latency: 150ms
  mock_llm_latency: 103ms
  throughput: 485rps
  constitutional_compliance: 100%
```

### Infrastructure Performance
```yaml
# Infrastructure Performance Targets
database:
  postgresql_query_time: 1ms
  redis_cache_latency: 0.1ms
  connection_pool_efficiency: 95%

monitoring:
  metrics_collection_overhead: 0.5%
  dashboard_load_time: 2s
  alert_delivery_time: 30s

network:
  service_to_service_latency: 1ms
  external_api_timeout: 5s
  load_balancer_overhead: 0.1ms
```

## Performance Monitoring

### Key Metrics
- **Request Latency**: P50, P95, P99 percentiles
- **Throughput**: Requests per second by service
- **Error Rates**: 4xx and 5xx error percentages
- **Resource Utilization**: CPU, memory, disk, network
- **Constitutional Compliance**: Validation success rate and latency

### Monitoring Setup
```bash
# Start performance monitoring stack
docker-compose -f infrastructure/docker/docker-compose.monitoring.yml up -d

# Access performance dashboards
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
open http://localhost:16686 # Jaeger

# Run performance tests
python tests/performance/run_performance_suite.py
```

## Cross-References & Navigation

**Navigation**:
- [Main Documentation](../CLAUDE.md)
- [Architecture Documentation](../architecture/CLAUDE.md)
- [Operations Documentation](../operations/CLAUDE.md)
- [Development Documentation](../development/CLAUDE.md)

**Related Components**:
- [Performance Testing](../../tests/performance/CLAUDE.md)
- [Monitoring Infrastructure](../../infrastructure/monitoring/CLAUDE.md)
- [Expert Service Performance](../../services/blockchain/expert-service/CLAUDE.md)
- [Database Performance](../../database/CLAUDE.md)

**Performance Tools**:
- [Monitoring Tools](../../monitoring/CLAUDE.md)
- [Performance Scripts](../../scripts/CLAUDE.md)
- [Load Testing](../../performance/CLAUDE.md)

---

**Constitutional Compliance**: All performance monitoring maintains constitutional hash `cdd01ef066bc6cf2` validation
