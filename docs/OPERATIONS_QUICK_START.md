# ACGS Operations Quick Start Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

Quick reference for ACGS operations, monitoring, and troubleshooting.

## Service Status Check

### Health Endpoints
```bash
# Check all services
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Integrity Service
curl http://localhost:8016/health  # Auth Service
curl http://localhost:8008/health  # Multi-Agent Coordinator
```

### Docker Services
```bash
# Check running containers
docker ps

# Check service logs
docker logs acgs_constitutional_ai
docker logs acgs_prometheus_production
docker logs acgs_grafana_production
```

## Monitoring Dashboards

### Grafana (Port 3001)
- **URL**: http://localhost:3001
- **Login**: admin/admin
- **Key Dashboards**:
  - ACGS Constitutional Compliance
  - Service Health Overview
  - Performance Metrics

### Prometheus (Port 9091)
- **URL**: http://localhost:9091
- **Key Metrics**:
  - `constitutional_compliance_rate`
  - `http_request_duration_seconds`
  - `http_requests_total`

## Performance Targets

- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >85%
- **Constitutional Compliance**: 100%

## Troubleshooting

### Service Down
1. Check Docker container status: `docker ps`
2. Review service logs: `docker logs <container_name>`
3. Verify configuration files have constitutional hash
4. Restart service: `docker-compose restart <service_name>`

### Performance Issues
1. Check Grafana performance dashboard
2. Query Prometheus for latency metrics
3. Verify cache hit rates
4. Review constitutional compliance metrics

### Constitutional Compliance Issues
1. Validate hash presence: `grep -r "cdd01ef066bc6cf2" .`
2. Run compliance validation: `python acgs_constitutional_compliance_enhancement.py`
3. Check monitoring alerts for compliance violations

## Emergency Procedures

### Service Restart
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart constitutional-ai
```

### Database Issues
```bash
# Check PostgreSQL status
docker exec acgs_postgres pg_isready

# Access database
docker exec -it acgs_postgres psql -U acgs_user -d acgs
```

### Monitoring Recovery
```bash
# Restart monitoring stack
docker-compose restart prometheus grafana

# Reload Prometheus config
curl -X POST http://localhost:9091/-/reload
```

## Key Files and Locations

- **Services**: `services/core/`, `services/shared/`
- **Infrastructure**: `infrastructure/`
- **Monitoring**: `infrastructure/monitoring/`
- **Documentation**: `docs/`
- **Configuration**: `config/`

For detailed runbooks, see [infrastructure/monitoring/runbooks/](../infrastructure/monitoring/runbooks/).
