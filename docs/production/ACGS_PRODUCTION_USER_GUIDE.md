# ACGS Production User Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Welcome to the Autonomous Coding Governance System (ACGS) production environment. This guide provides comprehensive instructions for system administrators, developers, and end users to effectively operate and maintain the ACGS system in production.

### Performance Targets
- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >85%
- **Constitutional Compliance**: 100%

## System Architecture

### Core Services
- **Authentication Service** (Port 8016): User authentication and authorization
- **Constitutional AI Service** (Port 8001): AI governance and compliance validation
- **Coordinator Service** (Port 8008): Multi-agent coordination and orchestration
- **Blackboard Service** (Port 8010): Shared state management and communication

### Infrastructure Services
- **PostgreSQL Database** (Port 5439): Primary data storage
- **Redis Cache** (Port 6389): Caching and session management
- **Prometheus** (Port 9090): Metrics collection and monitoring
- **Grafana** (Port 3000): Monitoring dashboards and visualization

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- Access to production environment variables
- Valid SSL certificates for HTTPS endpoints
- Network access to required ports

### Initial Setup

1. **Environment Configuration**
   ```bash
   # Copy production environment file
   cp .env.production.example .env.production
   
   # Edit with your production values
   nano .env.production
   ```

2. **Start Infrastructure Services**
   ```bash
   # Start PostgreSQL and Redis
   docker compose -f docker-compose.infrastructure.yml up -d
   
   # Verify services are running
   docker compose ps
   ```

3. **Start Monitoring Stack**
   ```bash
   # Start Prometheus and Grafana
   docker compose -f docker-compose.monitoring.yml up -d
   
   # Access Grafana at http://localhost:3000
   # Default credentials: admin/acgs_admin_2025
   ```

4. **Deploy ACGS Services**
   ```bash
   # Start all ACGS core services
   docker compose -f docker-compose.production.yml up -d
   
   # Check service health
   ./scripts/health_check.py
   ```

## User Roles and Permissions

### System Administrator
- **Responsibilities**: System deployment, monitoring, maintenance, security
- **Access**: Full system access, infrastructure management, log analysis
- **Key Tasks**:
  - Monitor system health and performance
  - Manage user accounts and permissions
  - Perform system updates and maintenance
  - Handle incident response and troubleshooting

### Developer
- **Responsibilities**: Application development, testing, code review
- **Access**: Development APIs, testing environments, code repositories
- **Key Tasks**:
  - Develop and test new features
  - Submit code for constitutional compliance review
  - Monitor application performance metrics
  - Participate in code reviews and governance decisions

### End User
- **Responsibilities**: Use ACGS features, report issues, follow governance policies
- **Access**: User interfaces, approved APIs, documentation
- **Key Tasks**:
  - Submit governance proposals and policies
  - Review constitutional compliance reports
  - Use AI-assisted development features
  - Report bugs and feature requests

## Daily Operations

### Health Monitoring

1. **System Health Dashboard**
   - Access Grafana at `http://localhost:3000`
   - Monitor key metrics: CPU, memory, disk, network
   - Check service availability and response times

2. **Constitutional Compliance Monitoring**
   ```bash
   # Check compliance status
   curl http://localhost:8001/health/compliance
   
   # View compliance metrics
   curl http://localhost:9090/api/v1/query?query=acgs_constitutional_compliance_rate
   ```

3. **Performance Monitoring**
   ```bash
   # Check P99 latency
   curl http://localhost:9090/api/v1/query?query=acgs_response_time_p99
   
   # Check throughput
   curl http://localhost:9090/api/v1/query?query=acgs_requests_per_second
   
   # Check cache hit rate
   curl http://localhost:9090/api/v1/query?query=acgs_cache_hit_rate
   ```

### Service Management

1. **Start Services**
   ```bash
   # Start all services
   docker compose up -d
   
   # Start specific service
   docker compose up -d auth-service
   ```

2. **Stop Services**
   ```bash
   # Stop all services
   docker compose down
   
   # Stop specific service
   docker compose stop constitutional-ai-service
   ```

3. **View Logs**
   ```bash
   # View all service logs
   docker compose logs -f
   
   # View specific service logs
   docker compose logs -f auth-service
   ```

4. **Scale Services**
   ```bash
   # Scale constitutional AI service
   docker compose up -d --scale constitutional-ai-service=3
   ```

### Database Operations

1. **Database Connection**
   ```bash
   # Connect to PostgreSQL
   psql -h localhost -p 5439 -U acgs_user -d acgs
   ```

2. **Database Backup**
   ```bash
   # Create backup
   pg_dump -h localhost -p 5439 -U acgs_user acgs > backup_$(date +%Y%m%d).sql
   ```

3. **Database Restore**
   ```bash
   # Restore from backup
   psql -h localhost -p 5439 -U acgs_user acgs < backup_20250107.sql
   ```

### Cache Management

1. **Redis Connection**
   ```bash
   # Connect to Redis
   redis-cli -h localhost -p 6389 -a acgs_production_password_2025
   ```

2. **Cache Statistics**
   ```bash
   # View cache info
   redis-cli -h localhost -p 6389 -a acgs_production_password_2025 INFO
   
   # View cache hit rate
   redis-cli -h localhost -p 6389 -a acgs_production_password_2025 INFO stats
   ```

3. **Clear Cache**
   ```bash
   # Clear all cache (use with caution)
   redis-cli -h localhost -p 6389 -a acgs_production_password_2025 FLUSHALL
   ```

## API Usage

### Authentication

1. **Obtain Access Token**
   ```bash
   curl -X POST http://localhost:8016/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
   ```

2. **Use Access Token**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/api/v1/constitutional/validate
   ```

### Constitutional AI Service

1. **Validate Code Compliance**
   ```bash
   curl -X POST http://localhost:8001/api/v1/constitutional/validate \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"code": "your_code_here", "policy": "governance_policy"}'
   ```

2. **Submit Governance Proposal**
   ```bash
   curl -X POST http://localhost:8001/api/v1/governance/propose \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "New Policy", "description": "Policy description", "content": "Policy content"}'
   ```

### Coordinator Service

1. **Check Agent Status**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8008/api/v1/agents/status
   ```

2. **Submit Task**
   ```bash
   curl -X POST http://localhost:8008/api/v1/tasks \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"type": "code_review", "payload": {"repository": "repo_name", "branch": "main"}}'
   ```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   - Check Docker daemon is running
   - Verify port availability
   - Check environment variables
   - Review service logs

2. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check connection parameters
   - Verify network connectivity
   - Check firewall settings

3. **High Latency**
   - Check system resources (CPU, memory)
   - Monitor database performance
   - Verify cache hit rates
   - Review network connectivity

4. **Constitutional Compliance Failures**
   - Check constitutional hash consistency
   - Verify policy configurations
   - Review compliance logs
   - Validate governance rules

### Emergency Procedures

1. **Service Restart**
   ```bash
   # Quick service restart
   docker compose restart
   ```

2. **Emergency Shutdown**
   ```bash
   # Stop all services immediately
   docker compose down --remove-orphans
   ```

3. **Rollback Deployment**
   ```bash
   # Rollback to previous version
   docker compose down
   docker compose -f docker-compose.previous.yml up -d
   ```

4. **Contact Support**
   - Email: support@acgs.ai
   - Emergency Hotline: +1-555-ACGS-911
   - Slack: #acgs-production-support

## Security Guidelines

### Access Control
- Use strong passwords and multi-factor authentication
- Regularly rotate API keys and tokens
- Follow principle of least privilege
- Monitor access logs regularly

### Data Protection
- Encrypt sensitive data at rest and in transit
- Regular security audits and penetration testing
- Backup encryption and secure storage
- Compliance with data protection regulations

### Network Security
- Use HTTPS for all external communications
- Implement proper firewall rules
- Regular security updates and patches
- Monitor for suspicious network activity

## Performance Optimization

### Monitoring
- Set up alerts for performance thresholds
- Regular performance testing and benchmarking
- Monitor resource utilization trends
- Analyze slow query logs

### Optimization
- Optimize database queries and indexes
- Implement proper caching strategies
- Scale services based on demand
- Regular performance tuning

## Support and Resources

### Documentation
- [ACGS Technical Specifications](../TECHNICAL_SPECIFICATIONS_2025.md)
- [API Documentation](../api/README.md)
- [Deployment Guide](../deployment/README.md)
- [Security Guide](../security/README.md)

### Training Resources
- ACGS Administrator Certification Course
- Developer Onboarding Program
- Constitutional Governance Training
- Performance Optimization Workshop

### Community
- ACGS User Forum: https://forum.acgs.ai
- GitHub Repository: https://github.com/acgs/acgs
- Documentation Wiki: https://wiki.acgs.ai
- Slack Community: https://acgs.slack.com

---

**Constitutional Hash**: cdd01ef066bc6cf2  
**Document Version**: 1.0  
**Last Updated**: 2025-07-07  
**Next Review**: 2025-10-07
