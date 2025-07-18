#!/usr/bin/env python3
"""
Production Environment Configuration for 5-Tier Hybrid Inference Router

Configures production-specific settings, security hardening, and deployment
parameters for the 5-tier hybrid inference router system.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductionConfig:
    """Production environment configuration."""
    
    # Environment settings
    environment: str = "production"
    namespace: str = "acgs-production"
    
    # Security settings
    https_enabled: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/acgs.crt"
    ssl_key_path: str = "/etc/ssl/private/acgs.key"
    
    # Service ports (production)
    hybrid_router_port: int = 443  # HTTPS
    model_registry_port: int = 8443  # HTTPS
    postgresql_port: int = 5432  # Internal only
    redis_port: int = 6379  # Internal only
    
    # Performance settings
    max_connections: int = 1000
    connection_pool_size: int = 50
    cache_ttl_seconds: int = 3600
    
    # Monitoring settings
    prometheus_port: int = 9090
    grafana_port: int = 3000
    alertmanager_port: int = 9093
    
    # Security headers
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst: int = 20
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ProductionConfigurationManager:
    """Manages production environment configuration."""
    
    def __init__(self):
        self.config = ProductionConfig()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
    def configure_production_environment(self) -> Dict[str, Any]:
        """Configure complete production environment."""
        logger.info("🚀 Configuring Production Environment")
        logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        try:
            # Generate production configurations
            self._generate_production_docker_compose()
            self._generate_production_nginx_config()
            self._generate_production_env_file()
            self._generate_production_security_config()
            self._generate_production_monitoring_config()
            
            # Generate deployment scripts
            self._generate_production_deployment_script()
            self._generate_production_backup_script()
            self._generate_production_rollback_script()
            
            logger.info("✅ Production environment configured successfully")
            
            return {
                "status": "SUCCESS",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "environment": self.configconfig/environments/development.environment,
                "configurations_generated": [
                    "config/docker/docker-compose.production.yml",
                    "config/nginx.production.conf",
                    "config/environments/developmentconfig/environments/production.env.backup",
                    "config/security/production.yml",
                    "monitoring.production.yml",
                    "scripts/deployment/deploy_production.sh",
                    "scripts/deployment/backup_production.sh",
                    "scripts/deployment/rollback_production.sh"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Production configuration failed: {e}")
            raise
    
    def _generate_production_docker_compose(self):
        """Generate production Docker Compose configuration."""
        logger.info("🐳 Generating production Docker Compose configuration...")
        
        compose_config = {
            "version": "3.8",
            "networks": {
                "acgs-production": {
                    "driver": "bridge",
                    "name": "acgs-production-network"
                }
            },
            "volumes": {
                "prometheus_data": {},
                "grafana_data": {},
                "postgres_data": {},
                "redis_data": {},
                "ssl_certs": {}
            },
            "services": {
                # Nginx reverse proxy with SSL termination
                "nginx": {
                    "image": "nginx:alpine",
                    "container_name": "acgs-nginx-production",
                    "restart": "unless-stopped",
                    "ports": [
                        "80:80",
                        "443:443"
                    ],
                    "volumes": [
                        "./config/nginx.production.conf:/etc/nginx/nginx.conf:ro",
                        "ssl_certs:/etc/ssl:ro"
                    ],
                    "networks": ["acgs-production"],
                    "depends_on": ["hybrid-router"],
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}"
                    ]
                },
                
                # 5-Tier Hybrid Router
                "hybrid-router": {
                    "build": {
                        "context": "./services/shared/routing",
                        "dockerfile": "Dockerfile.production"
                    },
                    "container_name": "acgs-hybrid-router-production",
                    "restart": "unless-stopped",
                    "expose": ["8000"],
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}",
                        "ENVIRONMENT=production",
                        "OPENROUTER_API_KEY=${OPENROUTER_API_KEY}",
                        "GROQ_API_KEY=${GROQ_API_KEY}",
                        "REDIS_URL=redis://redis:6379/0",
                        "DATABASE_URL=postgresql+asyncpg://acgs_user:${POSTGRES_PASSWORD}@postgres:5432/acgs_production"
                    ],
                    "networks": ["acgs-production"],
                    "depends_on": ["postgres", "redis"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "40s"
                    }
                },
                
                # PostgreSQL Database
                "postgres": {
                    "image": "postgres:15-alpine",
                    "container_name": "acgs-postgres-production",
                    "restart": "unless-stopped",
                    "expose": ["5432"],
                    "environment": [
                        "POSTGRES_USER=acgs_user",
                        "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}",
                        "POSTGRES_DB=acgs_production",
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}"
                    ],
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data",
                        "./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro"
                    ],
                    "networks": ["acgs-production"],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "pg_isready -U acgs_user -d acgs_production"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }
                },
                
                # Redis Cache
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "acgs-redis-production",
                    "restart": "unless-stopped",
                    "expose": ["6379"],
                    "command": "redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}",
                    "volumes": ["redis_data:/data"],
                    "networks": ["acgs-production"],
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}"
                    ],
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "--raw", "incr", "ping"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                
                # Monitoring Stack
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "acgs-prometheus-production",
                    "restart": "unless-stopped",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus.production.yml:/etc/prometheus/prometheus.yml:ro",
                        "./monitoring/rules:/etc/prometheus/rules:ro",
                        "prometheus_data:/prometheus"
                    ],
                    "networks": ["acgs-production"],
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}"
                    ]
                },
                
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "acgs-grafana-production",
                    "restart": "unless-stopped",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro"
                    ],
                    "networks": ["acgs-production"],
                    "environment": [
                        "GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}",
                        "GF_USERS_ALLOW_SIGN_UP=false",
                        "GF_SECURITY_DISABLE_GRAVATAR=true",
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}"
                    ],
                    "depends_on": ["prometheus"]
                }
            }
        }
        
        with open("config/docker/docker-compose.production.yml", "w") as f:
            import yaml
            yaml.dump(compose_config, f, default_flow_style=False)
        
        logger.info("✅ Production Docker Compose configuration generated")
    
    def _generate_production_nginx_config(self):
        """Generate production Nginx configuration."""
        logger.info("🌐 Generating production Nginx configuration...")
        
        nginx_config = f"""
# Production Nginx Configuration for 5-Tier Hybrid Inference Router
# Constitutional Hash: {CONSTITUTIONAL_HASH}

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections 1024;
    use epoll;
    multi_accept on;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'constitutional_hash="{CONSTITUTIONAL_HASH}"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Security headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Constitutional-Hash "{CONSTITUTIONAL_HASH}" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate={self.config.rate_limit_requests_per_minute}r/m;
    limit_req_status 429;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Redirect HTTP to HTTPS
    server {{
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }}
    
    # Main HTTPS server
    server {{
        listen 443 ssl http2;
        server_name _;
        
        ssl_certificate {self.config.ssl_cert_path};
        ssl_certificate_key {self.config.ssl_key_path};
        
        # Rate limiting
        limit_req zone=api burst={self.config.rate_limit_burst} nodelay;
        
        # 5-Tier Router API
        location /api/ {{
            proxy_pass http://hybrid-router:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Constitutional-Hash "{CONSTITUTIONAL_HASH}";
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }}
        
        # Health check endpoint
        location /health {{
            proxy_pass http://hybrid-router:8000/health;
            proxy_set_header Constitutional-Hash "{CONSTITUTIONAL_HASH}";
            access_log off;
        }}
        
        # Monitoring endpoints (restricted)
        location /metrics {{
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
            
            proxy_pass http://hybrid-router:8000/metrics;
            proxy_set_header Constitutional-Hash "{CONSTITUTIONAL_HASH}";
        }}
        
        # Default location
        location / {{
            return 404;
        }}
    }}
}}
"""
        
        with open("config/nginx.production.conf", "w") as f:
            f.write(nginx_config)
        
        logger.info("✅ Production Nginx configuration generated")
    
    def _generate_production_env_file(self):
        """Generate production environment file template."""
        logger.info("🔧 Generating production environment file...")
        
        env_content = f"""# ACGS-2 Production Environment Configuration
# Constitutional Hash: {CONSTITUTIONAL_HASH}

# Environment
ENVIRONMENT=production
CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}

# API Keys (REQUIRED - Set these before deployment)
OPENROUTER_API_KEY=your_production_openrouter_api_key
GROQ_API_KEY=your_production_groq_api_key

# Database Configuration
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=your_secure_postgres_password
POSTGRES_DB=acgs_production
DATABASE_URL=postgresql+asyncpg://acgs_user:your_secure_postgres_password@postgres:5432/acgs_production

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password
REDIS_URL=redis://:your_secure_redis_password@redis:6379/0

# Monitoring
GRAFANA_PASSWORD=your_secure_grafana_password

# Performance Settings
MAX_CONNECTIONS={self.config.max_connections}
CONNECTION_POOL_SIZE={self.config.connection_pool_size}
CACHE_TTL_SECONDS={self.config.cache_ttl_seconds}

# Security Settings
RATE_LIMIT_RPM={self.config.rate_limit_requests_per_minute}
RATE_LIMIT_BURST={self.config.rate_limit_burst}

# SSL Configuration
SSL_CERT_PATH={self.config.ssl_cert_path}
SSL_KEY_PATH={self.config.ssl_key_path}
"""
        
        with open("config/environments/developmentconfig/environments/production.template.env", "w") as f:
            f.write(env_content)
        
        logger.info("✅ Production environment file template generated")
    
    def _generate_production_security_config(self):
        """Generate production security configuration."""
        logger.info("🔒 Generating production security configuration...")
        
        security_config = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "security_policies": {
                "authentication": {
                    "required": True,
                    "methods": ["api_key", "jwt"],
                    "session_timeout": 3600
                },
                "authorization": {
                    "rbac_enabled": True,
                    "default_role": "user",
                    "admin_roles": ["admin", "operator"]
                },
                "encryption": {
                    "at_rest": True,
                    "in_transit": True,
                    "algorithm": "AES-256-GCM"
                },
                "audit_logging": {
                    "enabled": True,
                    "retention_days": 90,
                    "log_level": "INFO"
                }
            },
            "network_security": {
                "firewall_rules": [
                    {"port": 80, "protocol": "tcp", "action": "redirect"},
                    {"port": 443, "protocol": "tcp", "action": "allow"},
                    {"port": 22, "protocol": "tcp", "action": "allow", "source": "admin_ips"},
                    {"port": 9090, "protocol": "tcp", "action": "allow", "source": "monitoring_ips"}
                ],
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": self.config.rate_limit_requests_per_minute,
                    "burst_size": self.config.rate_limit_burst
                }
            },
            "compliance": {
                "constitutional_validation": True,
                "data_protection": True,
                "privacy_controls": True
            }
        }
        
        with open("config/security/production.yml", "w") as f:
            import yaml
            yaml.dump(security_config, f, default_flow_style=False)
        
        logger.info("✅ Production security configuration generated")
    
    def _generate_production_monitoring_config(self):
        """Generate production monitoring configuration."""
        logger.info("📊 Generating production monitoring configuration...")
        
        monitoring_config = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "prometheus": {
                "global": {
                    "scrape_interval": "15s",
                    "evaluation_interval": "15s"
                },
                "scrape_configs": [
                    {
                        "job_name": "5-tier-router",
                        "static_configs": [{"targets": ["hybrid-router:8000"]}],
                        "metrics_path": "/metrics",
                        "scrape_interval": "10s"
                    },
                    {
                        "job_name": "nginx",
                        "static_configs": [{"targets": ["nginx:80"]}],
                        "metrics_path": "/nginx_status"
                    },
                    {
                        "job_name": "postgres",
                        "static_configs": [{"targets": ["postgres-exporter:9187"]}]
                    },
                    {
                        "job_name": "redis",
                        "static_configs": [{"targets": ["redis-exporter:9121"]}]
                    }
                ]
            },
            "alerting": {
                "rules": [
                    {
                        "alert": "RouterHighLatency",
                        "expr": "histogram_quantile(0.99, router_latency_seconds) > 0.005",
                        "for": "5m",
                        "labels": {"severity": "warning"},
                        "annotations": {
                            "summary": "5-Tier Router high latency detected",
                            "constitutional_hash": CONSTITUTIONAL_HASH
                        }
                    },
                    {
                        "alert": "ConstitutionalComplianceFailure",
                        "expr": "router_constitutional_compliance_score < 0.82",
                        "for": "1m",
                        "labels": {"severity": "critical"},
                        "annotations": {
                            "summary": "Constitutional compliance failure",
                            "constitutional_hash": CONSTITUTIONAL_HASH
                        }
                    }
                ]
            }
        }
        
        with open("monitoring.production.yml", "w") as f:
            import yaml
            yaml.dump(monitoring_config, f, default_flow_style=False)
        
        logger.info("✅ Production monitoring configuration generated")
    
    def _generate_production_deployment_script(self):
        """Generate production deployment script."""
        logger.info("🚀 Generating production deployment script...")
        
        script_content = f'''#!/bin/bash
# Production Deployment Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: {CONSTITUTIONAL_HASH}

set -e

CONSTITUTIONAL_HASH="{CONSTITUTIONAL_HASH}"
ENVIRONMENT="production"

echo "🚀 Starting Production Deployment"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check required files
required_files=("config/environments/developmentconfig/environments/production.env.backup" "config/docker/docker-compose.production.yml" "config/nginx.production.conf")
for file in "${{required_files[@]}}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file not found: $file"
        exit 1
    fi
done

# Check environment variables
if [[ -z "$OPENROUTER_API_KEY" ]] || [[ -z "$GROQ_API_KEY" ]]; then
    echo "❌ Required API keys not set"
    exit 1
fi

# Backup current deployment
echo "💾 Creating backup..."
./scripts/deployment/backup_production.sh

# Deploy new version
echo "🚀 Deploying production services..."
docker-compose -f config/docker/docker-compose.production.yml --env-file config/environments/developmentconfig/environments/production.env.backup up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🔍 Running health checks..."
for i in {{1..10}}; do
    if curl -f -s https://localhost/health > /dev/null; then
        echo "✅ Health check passed"
        break
    fi
    if [[ $i -eq 10 ]]; then
        echo "❌ Health check failed after 10 attempts"
        echo "🔄 Rolling back..."
        ./scripts/deployment/rollback_production.sh
        exit 1
    fi
    sleep 10
done

# Validate constitutional compliance
echo "🔒 Validating constitutional compliance..."
response=$(curl -s https://localhost/api/health)
if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
    echo "✅ Constitutional compliance validated"
else
    echo "❌ Constitutional compliance validation failed"
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "🔗 Service URL: https://localhost"
echo "📊 Monitoring: http://localhost:3000"
'''
        
        with open("scripts/deployment/deploy_production.sh", "w") as f:
            f.write(script_content)
        
        os.chmod("scripts/deployment/deploy_production.sh", 0o755)
        logger.info("✅ Production deployment script generated")
    
    def _generate_production_backup_script(self):
        """Generate production backup script."""
        logger.info("💾 Generating production backup script...")
        
        script_content = f'''#!/bin/bash
# Production Backup Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: {CONSTITUTIONAL_HASH}

set -e

CONSTITUTIONAL_HASH="{CONSTITUTIONAL_HASH}"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

echo "💾 Starting Production Backup"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "📊 Backing up database..."
docker exec acgs-postgres-production pg_dump -U acgs_user acgs_production > "$BACKUP_DIR/database.sql"

# Backup Redis data
echo "🔄 Backing up Redis data..."
docker exec acgs-redis-production redis-cli --rdb - > "$BACKUP_DIR/redis.rdb"

# Backup configuration files
echo "⚙️ Backing up configuration files..."
cp config/docker/docker-compose.production.yml "$BACKUP_DIR/"
cp config/environments/developmentconfig/environments/production.env.backup "$BACKUP_DIR/"
cp config/nginx.production.conf "$BACKUP_DIR/"

# Backup volumes
echo "💽 Backing up Docker volumes..."
docker run --rm -v acgs_prometheus_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/prometheus_data.tar.gz -C /data .
docker run --rm -v acgs_grafana_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/grafana_data.tar.gz -C /data .

# Create backup manifest
cat > "$BACKUP_DIR/manifest.json" << EOF
{{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "backup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "production",
  "files": [
    "database.sql",
    "redis.rdb",
    "config/docker/docker-compose.production.yml",
    "config/environments/developmentconfig/environments/production.env.backup",
    "config/nginx.production.conf",
    "prometheus_data.tar.gz",
    "grafana_data.tar.gz"
  ]
}}
EOF

echo "✅ Backup completed: $BACKUP_DIR"
'''
        
        with open("scripts/deployment/backup_production.sh", "w") as f:
            f.write(script_content)
        
        os.chmod("scripts/deployment/backup_production.sh", 0o755)
        logger.info("✅ Production backup script generated")
    
    def _generate_production_rollback_script(self):
        """Generate production rollback script."""
        logger.info("🔄 Generating production rollback script...")
        
        script_content = f'''#!/bin/bash
# Production Rollback Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: {CONSTITUTIONAL_HASH}

set -e

CONSTITUTIONAL_HASH="{CONSTITUTIONAL_HASH}"
BACKUP_DIR="${{1:-$(ls -t backups/ | head -1)}}"

if [[ -z "$BACKUP_DIR" ]]; then
    echo "❌ No backup directory specified or found"
    exit 1
fi

echo "🔄 Starting Production Rollback"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "📁 Using backup: $BACKUP_DIR"

# Stop current services
echo "🛑 Stopping current services..."
docker-compose -f config/docker/docker-compose.production.yml down

# Restore configuration files
echo "⚙️ Restoring configuration files..."
cp "backups/$BACKUP_DIR/config/docker/docker-compose.production.yml" .
cp "backups/$BACKUP_DIR/config/environments/developmentconfig/environments/production.env.backup" .
cp "backups/$BACKUP_DIR/config/nginx.production.conf" .

# Restore volumes
echo "💽 Restoring Docker volumes..."
docker run --rm -v acgs_prometheus_data:/data -v "$PWD/backups/$BACKUP_DIR":/backup alpine tar xzf /backup/prometheus_data.tar.gz -C /data
docker run --rm -v acgs_grafana_data:/data -v "$PWD/backups/$BACKUP_DIR":/backup alpine tar xzf /backup/grafana_data.tar.gz -C /data

# Start services
echo "🚀 Starting restored services..."
docker-compose -f config/docker/docker-compose.production.yml --env-file config/environments/developmentconfig/environments/production.env.backup up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# Restore database
echo "📊 Restoring database..."
docker exec -i acgs-postgres-production psql -U acgs_user acgs_production < "backups/$BACKUP_DIR/database.sql"

# Restore Redis data
echo "🔄 Restoring Redis data..."
docker exec -i acgs-redis-production redis-cli --pipe < "backups/$BACKUP_DIR/redis.rdb"

# Health check
echo "🔍 Running health check..."
if curl -f -s https://localhost/health > /dev/null; then
    echo "✅ Rollback completed successfully"
else
    echo "❌ Rollback health check failed"
    exit 1
fi
'''
        
        with open("scripts/deployment/rollback_production.sh", "w") as f:
            f.write(script_content)
        
        os.chmod("scripts/deployment/rollback_production.sh", 0o755)
        logger.info("✅ Production rollback script generated")


def main():
    """Main configuration function."""
    manager = ProductionConfigurationManager()
    
    try:
        result = manager.configure_production_environment()
        
        print(f"\n🎉 Production environment configured successfully!")
        print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"📁 Generated configurations:")
        for config in result["configurations_generated"]:
            print(f"  - {config}")
        
        print(f"\n📋 Next steps:")
        print(f"1. Review and customize config/environments/developmentconfig/environments/production.template.env")
        print(f"2. Obtain SSL certificates for HTTPS")
        print(f"3. Set up production API keys")
        print(f"4. Run ./scripts/deployment/deploy_production.sh")
        
        return 0
        
    except Exception as e:
        logger.error(f"Production configuration failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
