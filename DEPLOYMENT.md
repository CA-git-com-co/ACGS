# ACGS Multi-Agent Coordination System - MCP Server Stack
## Operational Deployment Runbook
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Version:** 1.0  
**Last Updated:** 2025-01-06  

---

## Prerequisites

### System Requirements
- **Host OS**: Ubuntu 22.04 LTS (or compatible Linux distribution)
- **Docker Engine**: Version ≥ 24.0
- **Docker Compose**: Version ≥ 2.20
- **Memory**: Minimum 8 GB RAM (16 GB recommended for production)
- **CPU**: Multi-core processor (4+ cores recommended)
- **Storage**: 50 GB available disk space
- **Network**: Internet access for GitHub API and external services

### Required Tools
```bash
# Install required tools
sudo apt update
sudo apt install -y curl wget git apache2-utils

# Verify Docker installation
docker --version
docker-compose --version

# Verify system resources
free -h
df -h
nproc
```

---

## Step-by-Step Deployment

### Step 1: Environment Preparation

1. **Clone or prepare the deployment directory:**
```bash
mkdir -p acgs-mcp-stack
cd acgs-mcp-stack

# Copy the required files:
# - docker-compose.yml
# - .env.template
# - docs/coordination-policy.md
```

2. **Create environment configuration:**
```bash
# Copy template and customize
cp .env.template .env

# Edit environment variables (REQUIRED)
nano .env

# Minimum required changes:
# - Set GITHUB_TOKEN with your GitHub Personal Access Token
# - Update passwords and secrets for production
# - Verify CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
```

3. **Create required directories:**
```bash
# Create workspace and data directories
mkdir -p workspace logs cache
chmod 755 workspace logs cache

# Set proper ownership (non-root user)
sudo chown -R 1000:1000 workspace logs cache
```

### Step 2: Security Configuration

1. **Generate GitHub Personal Access Token:**
   - Visit: https://github.com/settings/tokens
   - Create token with scopes: `repo`, `read:org`, `read:user`
   - Add token to `.env` file: `GITHUB_TOKEN=ghp_your_token_here`

2. **Verify security settings:**
```bash
# Check file permissions
ls -la .env
# Should show: -rw------- (600 permissions)

# Set secure permissions if needed
chmod 600 .env
```

### Step 3: Service Deployment

1. **Start the MCP server stack:**
```bash
# Pull latest images
docker-compose pull

# Start services in detached mode
docker-compose up -d

# Monitor startup logs
docker-compose logs -f
```

2. **Verify service startup:**
```bash
# Check service status
docker-compose ps

# Expected output:
# NAME                    STATUS
# acgs_mcp_aggregator     Up (healthy)
# acgs_mcp_filesystem     Up (healthy)
# acgs_mcp_github         Up (healthy)
# acgs_mcp_browser        Up (healthy)
```

### Step 4: ACGS Integration Validation

1. **Verify ACGS services are running (if using ACGS integration):**
```bash
# Check if ACGS services are available
curl -f http://localhost:8016/health || echo "ACGS Auth Service not available"
curl -f http://localhost:8001/health || echo "ACGS Constitutional AI not available"
curl -f http://localhost:8008/health || echo "ACGS Multi-Agent Coordinator not available"
curl -f http://localhost:8010/health || echo "ACGS Blackboard Service not available"

# If ACGS services are not running, start them:
# docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d
```

### Step 5: Health Validation

1. **System startup validation:**
```bash
# Wait for services to be healthy (may take 1-2 minutes)
sleep 60

# Test aggregator health
curl -f http://localhost:3000/health || echo "FAILED: Aggregator health check"

# Test service integration
curl -f http://localhost:3000/mcp/filesystem/status || echo "FAILED: Filesystem integration"
curl -f http://localhost:3000/mcp/github/status || echo "FAILED: GitHub integration"
curl -f http://localhost:3000/mcp/browser/status || echo "FAILED: Browser integration"

# Test ACGS integration (if enabled)
if [[ "${CLAUDE_MCP_INTEGRATION_ENABLED:-false}" == "true" ]]; then
  curl -f http://localhost:3000/acgs/health || echo "FAILED: ACGS integration"
  curl -f http://localhost:3000/acgs/validate || echo "FAILED: Constitutional validation"
fi
```

2. **Performance baseline testing:**
```bash
# Install Apache Bench if not available
sudo apt install -y apache2-utils

# Run performance test
ab -n 100 -c 10 http://localhost:3000/health

# Expected results:
# - Requests per second: >50
# - Time per request: <200ms
# - Failed requests: 0
```

### Step 6: Integration Testing

1. **Run comprehensive integration validation:**
```bash
# Execute the comprehensive validation script
./scripts/validate_claude_mcp_integration.sh

# This script validates:
# - Service health and availability
# - Constitutional compliance (hash: cdd01ef066bc6cf2)
# - ACGS service integration
# - MCP tool functionality
# - Performance targets
# - Coordination workflow
```

2. **Manual MCP service functionality testing:**
```bash
# Test filesystem operations
curl -X POST http://localhost:3000/mcp/filesystem/list \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace"}'

# Test GitHub API integration (requires valid token)
curl -X GET http://localhost:3000/mcp/github/user \
  -H "Authorization: Bearer ${GITHUB_TOKEN}"

# Test browser functionality
curl -X POST http://localhost:3000/mcp/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

3. **Constitutional compliance validation:**
```bash
# Verify constitutional hash in all services
docker-compose exec mcp_aggregator env | grep CONSTITUTIONAL_HASH
docker-compose exec mcp_filesystem env | grep CONSTITUTIONAL_HASH
docker-compose exec mcp_github env | grep CONSTITUTIONAL_HASH
docker-compose exec mcp_browser env | grep CONSTITUTIONAL_HASH

# All should return: CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
```

4. **ACGS integration validation:**
```bash
# Test ACGS service connectivity from MCP aggregator
docker-compose exec mcp_aggregator curl -f http://host.docker.internal:8016/health
docker-compose exec mcp_aggregator curl -f http://host.docker.internal:8001/health
docker-compose exec mcp_aggregator curl -f http://host.docker.internal:8008/health

# Test coordination workflow
curl -X POST http://localhost:3000/acgs/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "claude_agent_id": "test_agent",
    "coordination_type": "task_delegation",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }'
```

---

## Monitoring and Maintenance

### Health Monitoring

1. **Continuous health checks:**
```bash
# Create monitoring script
cat > monitor_health.sh << 'EOF'
#!/bin/bash
while true; do
  echo "$(date): Checking MCP stack health..."
  
  # Check aggregator
  if curl -sf http://localhost:3000/health > /dev/null; then
    echo "✓ Aggregator: Healthy"
  else
    echo "✗ Aggregator: Unhealthy"
  fi
  
  # Check service integrations
  for service in filesystem github browser; do
    if curl -sf http://localhost:3000/mcp/${service}/status > /dev/null; then
      echo "✓ ${service}: Healthy"
    else
      echo "✗ ${service}: Unhealthy"
    fi
  done
  
  echo "---"
  sleep 30
done
EOF

chmod +x monitor_health.sh
./monitor_health.sh
```

2. **Resource monitoring:**
```bash
# Monitor container resources
docker stats --no-stream

# Monitor disk usage
df -h

# Monitor system resources
htop
```

### Log Management

1. **View service logs:**
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs mcp_aggregator
docker-compose logs mcp_filesystem
docker-compose logs mcp_github
docker-compose logs mcp_browser

# Follow logs in real-time
docker-compose logs -f --tail=100
```

2. **Log rotation and cleanup:**
```bash
# Clean up old logs (run weekly)
docker system prune -f
docker volume prune -f

# Archive logs if needed
tar -czf logs-$(date +%Y%m%d).tar.gz logs/
```

---

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Service won't start** | Container exits immediately | Check logs: `docker-compose logs [service]`<br>Verify environment variables in `.env` |
| **Health check failing** | Service shows as unhealthy | Wait 2-3 minutes for startup<br>Check port conflicts: `netstat -tulpn` |
| **GitHub integration fails** | 401/403 errors in logs | Verify `GITHUB_TOKEN` is valid<br>Check token scopes and rate limits |
| **Browser service crashes** | Browser container restarts frequently | Increase memory limit in `.env`<br>Check shared memory: `df -h /dev/shm` |
| **High memory usage** | System becomes slow | Adjust memory limits in `docker-compose.yml`<br>Monitor with `docker stats` |
| **Network connectivity issues** | Services can't communicate | Check Docker network: `docker network ls`<br>Verify firewall settings |

### Diagnostic Commands

```bash
# Check Docker daemon status
sudo systemctl status docker

# Inspect Docker networks
docker network inspect acgs-mcp-stack_mcp_network

# Check container resource usage
docker stats --no-stream

# Inspect service configuration
docker-compose config

# Test internal service connectivity
docker-compose exec mcp_aggregator ping mcp_filesystem
docker-compose exec mcp_aggregator ping mcp_github
docker-compose exec mcp_aggregator ping mcp_browser
```

### Emergency Procedures

1. **Service restart:**
```bash
# Restart specific service
docker-compose restart mcp_aggregator

# Restart all services
docker-compose restart

# Force recreation of services
docker-compose down
docker-compose up -d
```

2. **Emergency shutdown:**
```bash
# Graceful shutdown
docker-compose down

# Force shutdown (if graceful fails)
docker-compose down --timeout 10

# Complete cleanup (removes volumes - USE WITH CAUTION)
docker-compose down -v
```

3. **Rollback procedure:**
```bash
# Stop current deployment
docker-compose down

# Restore from backup (if available)
cp docker-compose.yml.backup docker-compose.yml
cp .env.backup .env

# Restart with previous configuration
docker-compose up -d
```

---

## Performance Optimization

### Resource Tuning

1. **Memory optimization:**
```bash
# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Adjust limits in docker-compose.yml if needed
# Typical production values:
# - Aggregator: 512M-1G
# - Filesystem: 256M-512M
# - GitHub: 512M-1G
# - Browser: 1G-2G
```

2. **CPU optimization:**
```bash
# Monitor CPU usage
htop

# Adjust CPU limits based on load
# Typical production values:
# - Aggregator: 0.5-1.0 cores
# - Filesystem: 0.25-0.5 cores
# - GitHub: 0.5-1.0 cores
# - Browser: 0.75-1.5 cores
```

### Scaling Considerations

1. **Horizontal scaling:**
```bash
# Scale specific services (if supported)
docker-compose up -d --scale mcp_filesystem=2

# Note: Aggregator handles load balancing automatically
```

2. **Vertical scaling:**
```bash
# Increase resource limits in docker-compose.yml
# Restart services to apply changes
docker-compose down
docker-compose up -d
```

---

## Security Maintenance

### Regular Security Tasks

1. **Token rotation (every 90 days):**
```bash
# Generate new GitHub token
# Update .env file
# Restart GitHub service
docker-compose restart mcp_github
```

2. **Security audit:**
```bash
# Check for security updates
docker-compose pull

# Scan for vulnerabilities
docker scout cves

# Update base images
docker-compose build --pull
```

3. **Access control review:**
```bash
# Review file permissions
ls -la .env
ls -la workspace/

# Review network access
netstat -tulpn | grep :3000
```

---

## Backup and Recovery

### Backup Procedures

1. **Configuration backup:**
```bash
# Backup configuration files
tar -czf acgs-mcp-config-$(date +%Y%m%d).tar.gz \
  docker-compose.yml .env docs/

# Store in secure location
```

2. **Data backup:**
```bash
# Backup workspace and logs
tar -czf acgs-mcp-data-$(date +%Y%m%d).tar.gz \
  workspace/ logs/ cache/
```

### Recovery Procedures

1. **Configuration recovery:**
```bash
# Stop services
docker-compose down

# Restore configuration
tar -xzf acgs-mcp-config-YYYYMMDD.tar.gz

# Restart services
docker-compose up -d
```

2. **Data recovery:**
```bash
# Stop services
docker-compose down

# Restore data
tar -xzf acgs-mcp-data-YYYYMMDD.tar.gz

# Fix permissions
sudo chown -R 1000:1000 workspace logs cache

# Restart services
docker-compose up -d
```

---

## Support and Documentation

### Additional Resources

- **MCP Protocol Specification**: https://modelcontextprotocol.io/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **ACGS Documentation**: `docs/coordination-policy.md`

### Getting Help

1. **Check logs first:**
```bash
docker-compose logs --tail=100
```

2. **Verify configuration:**
```bash
docker-compose config --quiet
```

3. **Test connectivity:**
```bash
curl -v http://localhost:3000/health
```

### Constitutional Compliance

**CRITICAL**: Always verify constitutional compliance hash `cdd01ef066bc6cf2` is present in all service configurations and logs. Any deviation indicates a security breach and requires immediate investigation.
