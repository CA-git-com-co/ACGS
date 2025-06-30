# Infrastructure Setup Guide

## Production Architecture

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │   Auth Service  │
│   (nginx/HAProxy│────│   (Kong/Envoy)  │────│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │Constitutional AI│ │Policy Governance│ │Governance Synth │
    │   (Port 8001)   │ │   (Port 8005)   │ │   (Port 8004)   │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                ┌─────────────────────────────────┐
                │         Data Layer              │
                │  ┌─────────────┐ ┌─────────────┐│
                │  │ PostgreSQL  │ │    Redis    ││
                │  │ (Port 5432) │ │ (Port 6379) ││
                │  └─────────────┘ └─────────────┘│
                └─────────────────────────────────┘
```

### Network Configuration
- Production VPC: 10.0.0.0/16
- Public Subnet: 10.0.1.0/24 (Load balancers)
- Private Subnet: 10.0.2.0/24 (Application services)
- Database Subnet: 10.0.3.0/24 (Data layer)

### Security Groups
- Load Balancer: Ports 80, 443 from 0.0.0.0/0
- Application: Ports 8000-8010 from Load Balancer SG
- Database: Port 5432 from Application SG
- Redis: Port 6379 from Application SG

## Hardware Requirements

### Production Environment
- **Load Balancer**: 2 vCPU, 4GB RAM, 20GB SSD
- **Application Servers**: 4 vCPU, 16GB RAM, 100GB SSD (3 instances)
- **Database Server**: 8 vCPU, 32GB RAM, 500GB SSD
- **Redis Server**: 2 vCPU, 8GB RAM, 50GB SSD
- **Monitoring Server**: 4 vCPU, 8GB RAM, 200GB SSD

### Staging Environment
- **Application Server**: 2 vCPU, 8GB RAM, 50GB SSD
- **Database Server**: 4 vCPU, 16GB RAM, 200GB SSD
- **Redis Server**: 1 vCPU, 4GB RAM, 20GB SSD

## SSL/TLS Configuration

### Certificate Requirements
- Wildcard certificate for *.acgs.domain.com
- Minimum TLS 1.2, prefer TLS 1.3
- Strong cipher suites only

### nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name acgs.domain.com;
    
    ssl_certificate /etc/ssl/certs/acgs.crt;
    ssl_certificate_key /etc/ssl/private/acgs.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup Strategy

### Database Backups
- Full backup: Daily at 2 AM UTC
- Incremental backup: Every 6 hours
- Point-in-time recovery: 7 days
- Backup retention: 30 days

### Application Backups
- Configuration files: Daily
- Application logs: 7 days retention
- Monitoring data: 30 days retention

## Disaster Recovery

### RTO/RPO Targets
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 1 hour

### Recovery Procedures
1. Assess damage and determine recovery strategy
2. Restore database from latest backup
3. Deploy application services to backup infrastructure
4. Update DNS to point to backup environment
5. Verify system functionality
6. Communicate status to stakeholders
