# ACGS-PGP Operational Runbook

## Service Management

### Starting Services
```bash
# Start all services
cd /home/ubuntu/ACGS
./scripts/start_all_services.sh

# Start individual service
cd services/platform/authentication/auth_service
PYTHONPATH=/home/ubuntu/ACGS:/home/ubuntu/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages python3.10 simple_main.py
```

### Health Monitoring
```bash
# Check all services
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo -n "Port $port: "
  curl -s http://localhost:$port/health | jq -r '.status // .service // "FAILED"'
done

# Detailed health check
curl -s http://localhost:8005/health | jq '.'
```

### Performance Testing
```bash
# Run load tests
cd /home/ubuntu/ACGS/scripts
python3.10 load_test_acgs_pgp.py --concurrent 15

# Security scan
python3.10 simple_security_scanner.py
```

### Configuration Management
```bash
# Validate configurations
ls -la /home/ubuntu/ACGS/config/shared/
cat /home/ubuntu/ACGS/config/shared/resource-limits.yaml

# Environment configs
ls -la /home/ubuntu/ACGS/config/environments/
```

### Troubleshooting

#### Service Won't Start
1. Check Python path: `which python3.10`
2. Verify dependencies: `pip list | grep fastapi`
3. Check logs: `tail -f /home/ubuntu/ACGS/logs/<service>.log`
4. Verify ports: `netstat -tlnp | grep 800`

#### Performance Issues
1. Check system resources: `htop`
2. Monitor service metrics: `curl http://localhost:<port>/metrics`
3. Review load test results
4. Check database connections

#### Security Alerts
1. Run security scan: `python3.10 simple_security_scanner.py`
2. Check for vulnerabilities: `grep -r "shell=True" services/`
3. Verify security headers: `curl -I http://localhost:8000/`

### Emergency Procedures

#### Service Restart
```bash
# Stop all services
pkill -f 'uvicorn.*:800[0-6]'

# Restart specific service
cd services/platform/authentication/auth_service
PYTHONPATH=/home/ubuntu/ACGS:/home/ubuntu/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages python3.10 simple_main.py &
```

#### Rollback Configuration
```bash
# Restore from backup
cp -r /home/ubuntu/ACGS/config_backup_20250623_220151/config/* /home/ubuntu/ACGS/config/
```

#### Emergency Contacts
- System Administrator: Check service logs first
- Security Team: For security-related issues
- Development Team: For application bugs

### Maintenance Schedule

#### Daily
- Check service health endpoints
- Monitor system resources
- Review error logs

#### Weekly  
- Run security scans
- Performance testing
- Configuration backup

#### Monthly
- Dependency updates
- Security patches
- Documentation review

### Performance Targets

- Response Time: ≤2s P99
- Constitutional Compliance: >95%
- Service Availability: >99%
- Security Scan: Zero critical issues

### Constitutional Governance

- **Hash**: cdd01ef066bc6cf2
- **Compliance Threshold**: 0.8 (80%)
- **Validation**: All services must validate against constitutional principles
- **Monitoring**: Real-time compliance tracking

Last Updated: 2025-06-23 23:13:48
