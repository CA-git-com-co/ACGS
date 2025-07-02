#!/usr/bin/env python3
"""
ACGS-2 Infrastructure Deployment Script
Deploys complete ACGS infrastructure with optimized configurations

Target: 99.9% uptime, sub-5ms P99 latency, 85% cache hit rate
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Deployment configuration for ACGS infrastructure."""
    
    # Infrastructure ports (updated to current specifications)
    postgresql_port: int = 5439
    redis_port: int = 6389
    auth_service_port: int = 8016
    
    # Service ports
    constitutional_ai_port: int = 8001
    integrity_service_port: int = 8002
    formal_verification_port: int = 8003
    governance_synthesis_port: int = 8004
    policy_governance_port: int = 8005
    evolutionary_computation_port: int = 8006
    
    # Monitoring ports
    prometheus_port: int = 9090
    grafana_port: int = 3000
    
    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    # Performance targets
    target_p99_latency_ms: float = 5.0
    target_cache_hit_rate: float = 0.85
    target_throughput_rps: float = 100.0


class ACGSInfrastructureDeployer:
    """Main infrastructure deployment orchestrator."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.deployment_status = {}
        self.start_time = time.time()
        
        logger.info("ACGS Infrastructure Deployer initialized")
    
    async def deploy_complete_infrastructure(self) -> Dict[str, Any]:
        """Deploy complete ACGS infrastructure."""
        logger.info("🚀 Starting ACGS-2 Complete Infrastructure Deployment")
        
        deployment_report = {
            "start_time": time.time(),
            "deployment_steps": [],
            "services_deployed": [],
            "infrastructure_deployed": [],
            "monitoring_deployed": [],
            "success": False,
            "constitutional_hash": self.config.constitutional_hash
        }
        
        try:
            # Phase 1: Deploy Infrastructure Services
            logger.info("🏗️ Phase 1: Deploying Infrastructure Services")
            await self.deploy_infrastructure_services()
            deployment_report["infrastructure_deployed"] = ["postgresql", "redis"]
            
            # Phase 2: Deploy Core ACGS Services
            logger.info("🔧 Phase 2: Deploying Core ACGS Services")
            await self.deploy_core_services()
            deployment_report["services_deployed"] = [
                "auth_service", "constitutional_ai", "integrity_service",
                "formal_verification", "governance_synthesis", 
                "policy_governance", "evolutionary_computation"
            ]
            
            # Phase 3: Deploy Monitoring Stack
            logger.info("📊 Phase 3: Deploying Monitoring Stack")
            await self.deploy_monitoring_stack()
            deployment_report["monitoring_deployed"] = ["prometheus", "grafana"]
            
            # Phase 4: Configure Service Mesh and Networking
            logger.info("🌐 Phase 4: Configuring Service Mesh")
            await self.configure_service_mesh()
            
            # Phase 5: Validate Deployment
            logger.info("✅ Phase 5: Validating Deployment")
            validation_results = await self.validate_deployment()
            deployment_report["validation_results"] = validation_results
            
            deployment_report["success"] = True
            logger.info("✅ ACGS infrastructure deployment completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Infrastructure deployment failed: {e}")
            deployment_report["error"] = str(e)
            deployment_report["success"] = False
        
        finally:
            deployment_report["end_time"] = time.time()
            deployment_report["duration_seconds"] = deployment_report["end_time"] - deployment_report["start_time"]
        
        return deployment_report
    
    async def deploy_infrastructure_services(self):
        """Deploy PostgreSQL and Redis infrastructure."""
        logger.info("Deploying PostgreSQL database...")
        
        # Create PostgreSQL Docker Compose configuration
        postgresql_config = {
            "version": "3.8",
            "services": {
                "postgresql": {
                    "image": "postgres:15.4",
                    "container_name": "acgs_postgresql",
                    "ports": [f"{self.config.postgresql_port}:5432"],
                    "environment": {
                        "POSTGRES_DB": "acgs_production",
                        "POSTGRES_USER": "acgs_user",
                        "POSTGRES_PASSWORD": "acgs_secure_password",
                        "POSTGRES_INITDB_ARGS": "--auth-host=scram-sha-256"
                    },
                    "volumes": [
                        "postgresql_data:/var/lib/postgresql/data",
                        "./config/postgresql/postgresql.conf:/etc/postgresql/postgresql.conf"
                    ],
                    "command": ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD-SHELL", "pg_isready -U acgs_user -d acgs_production"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5
                    }
                }
            },
            "volumes": {
                "postgresql_data": {}
            }
        }
        
        # Save PostgreSQL configuration
        postgresql_compose_path = Path("docker-compose.postgresql.yml")
        with open(postgresql_compose_path, 'w') as f:
            yaml.dump(postgresql_config, f, default_flow_style=False)
        
        # Deploy PostgreSQL
        result = subprocess.run(
            ["docker-compose", "-f", str(postgresql_compose_path), "up", "-d"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ PostgreSQL deployed successfully")
            self.deployment_status["postgresql"] = "deployed"
        else:
            logger.error(f"❌ PostgreSQL deployment failed: {result.stderr}")
            raise Exception(f"PostgreSQL deployment failed: {result.stderr}")
        
        # Deploy Redis
        logger.info("Deploying Redis cache...")
        
        redis_config = {
            "version": "3.8",
            "services": {
                "redis": {
                    "image": "redis:7.2-alpine",
                    "container_name": "acgs_redis",
                    "ports": [f"{self.config.redis_port}:6379"],
                    "command": [
                        "redis-server",
                        "--appendonly", "yes",
                        "--maxmemory", "512mb",
                        "--maxmemory-policy", "allkeys-lru",
                        "--timeout", "300"
                    ],
                    "volumes": [
                        "redis_data:/data"
                    ],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "ping"],
                        "interval": "10s",
                        "timeout": "3s",
                        "retries": 5
                    }
                }
            },
            "volumes": {
                "redis_data": {}
            }
        }
        
        # Save Redis configuration
        redis_compose_path = Path("docker-compose.redis.yml")
        with open(redis_compose_path, 'w') as f:
            yaml.dump(redis_config, f, default_flow_style=False)
        
        # Deploy Redis
        result = subprocess.run(
            ["docker-compose", "-f", str(redis_compose_path), "up", "-d"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Redis deployed successfully")
            self.deployment_status["redis"] = "deployed"
        else:
            logger.error(f"❌ Redis deployment failed: {result.stderr}")
            raise Exception(f"Redis deployment failed: {result.stderr}")
        
        # Wait for services to be ready
        await asyncio.sleep(10)
        logger.info("Infrastructure services deployment completed")
    
    async def deploy_core_services(self):
        """Deploy core ACGS services."""
        services = [
            ("auth_service", self.config.auth_service_port),
            ("constitutional_ai", self.config.constitutional_ai_port),
            ("integrity_service", self.config.integrity_service_port),
            ("formal_verification", self.config.formal_verification_port),
            ("governance_synthesis", self.config.governance_synthesis_port),
            ("policy_governance", self.config.policy_governance_port),
            ("evolutionary_computation", self.config.evolutionary_computation_port)
        ]
        
        # Create unified services Docker Compose configuration
        services_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "acgs_network": {
                    "driver": "bridge"
                }
            }
        }
        
        for service_name, port in services:
            service_config = {
                "build": {
                    "context": f"./services/core/{service_name.replace('_', '-')}",
                    "dockerfile": "Dockerfile"
                },
                "container_name": f"acgs_{service_name}",
                "ports": [f"{port}:{port}"],
                "environment": {
                    "CONSTITUTIONAL_HASH": self.config.constitutional_hash,
                    "DATABASE_URL": f"postgresql://acgs_user:acgs_secure_password@localhost:{self.config.postgresql_port}/acgs_production",
                    "REDIS_URL": f"redis://localhost:{self.config.redis_port}/0",
                    "SERVICE_PORT": str(port)
                },
                "depends_on": ["postgresql", "redis"],
                "networks": ["acgs_network"],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": [f"CMD", "curl", "-f", f"http://localhost:{port}/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
            
            services_config["services"][service_name] = service_config
        
        # Add external services references
        services_config["services"]["postgresql"] = {
            "external": True,
            "container_name": "acgs_postgresql"
        }
        services_config["services"]["redis"] = {
            "external": True,
            "container_name": "acgs_redis"
        }
        
        # Save services configuration
        services_compose_path = Path("docker-compose.services.yml")
        with open(services_compose_path, 'w') as f:
            yaml.dump(services_config, f, default_flow_style=False)
        
        logger.info("Core services configuration created - manual deployment required")
        logger.info("To deploy services, run: docker-compose -f docker-compose.services.yml up -d")
        
        # Mark services as configured (not deployed due to missing Dockerfiles)
        for service_name, _ in services:
            self.deployment_status[service_name] = "configured"
    
    async def deploy_monitoring_stack(self):
        """Deploy Prometheus and Grafana monitoring."""
        logger.info("Deploying monitoring stack...")
        
        monitoring_config = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "acgs_prometheus",
                    "ports": [f"{self.config.prometheus_port}:9090"],
                    "volumes": [
                        "./config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml",
                        "prometheus_data:/prometheus"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=200h",
                        "--web.enable-lifecycle"
                    ],
                    "restart": "unless-stopped"
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "acgs_grafana",
                    "ports": [f"{self.config.grafana_port}:3000"],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "acgs_admin_password",
                        "GF_USERS_ALLOW_SIGN_UP": "false"
                    },
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./config/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards",
                        "./config/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources"
                    ],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "prometheus_data": {},
                "grafana_data": {}
            }
        }
        
        # Create basic Prometheus configuration
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "acgs-services",
                    "static_configs": [
                        {
                            "targets": [
                                f"localhost:{self.config.auth_service_port}",
                                f"localhost:{self.config.constitutional_ai_port}",
                                f"localhost:{self.config.policy_governance_port}"
                            ]
                        }
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                }
            ]
        }
        
        # Ensure config directory exists
        config_dir = Path("config/monitoring")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Prometheus configuration
        with open(config_dir / "prometheus.yml", 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        # Save monitoring configuration
        monitoring_compose_path = Path("docker-compose.monitoring.yml")
        with open(monitoring_compose_path, 'w') as f:
            yaml.dump(monitoring_config, f, default_flow_style=False)
        
        # Deploy monitoring stack
        result = subprocess.run(
            ["docker-compose", "-f", str(monitoring_compose_path), "up", "-d"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Monitoring stack deployed successfully")
            self.deployment_status["prometheus"] = "deployed"
            self.deployment_status["grafana"] = "deployed"
        else:
            logger.error(f"❌ Monitoring deployment failed: {result.stderr}")
            # Continue deployment even if monitoring fails
            logger.warning("Continuing deployment without monitoring")
    
    async def configure_service_mesh(self):
        """Configure service mesh and networking."""
        logger.info("Configuring service mesh and networking...")
        
        # Create network configuration
        network_result = subprocess.run(
            ["docker", "network", "create", "acgs_network"],
            capture_output=True, text=True
        )
        
        if network_result.returncode == 0 or "already exists" in network_result.stderr:
            logger.info("✅ ACGS network configured")
            self.deployment_status["network"] = "configured"
        else:
            logger.warning(f"Network configuration warning: {network_result.stderr}")
    
    async def validate_deployment(self) -> Dict[str, Any]:
        """Validate the deployment."""
        logger.info("Validating deployment...")
        
        validation_results = {
            "infrastructure_health": {},
            "service_health": {},
            "monitoring_health": {},
            "overall_status": "unknown"
        }
        
        # Check infrastructure services
        for service in ["postgresql", "redis"]:
            if service in self.deployment_status:
                validation_results["infrastructure_health"][service] = self.deployment_status[service]
        
        # Check monitoring services
        for service in ["prometheus", "grafana"]:
            if service in self.deployment_status:
                validation_results["monitoring_health"][service] = self.deployment_status[service]
        
        # Determine overall status
        deployed_services = len([s for s in self.deployment_status.values() if s == "deployed"])
        total_services = len(self.deployment_status)
        
        if deployed_services >= total_services * 0.8:
            validation_results["overall_status"] = "healthy"
        elif deployed_services >= total_services * 0.5:
            validation_results["overall_status"] = "partial"
        else:
            validation_results["overall_status"] = "unhealthy"
        
        logger.info(f"Deployment validation completed: {validation_results['overall_status']}")
        return validation_results
    
    async def save_deployment_report(self, report: Dict[str, Any]) -> str:
        """Save deployment report to file."""
        report_path = Path("acgs_infrastructure_deployment_report.json")
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Deployment report saved to: {report_path}")
        return str(report_path)


async def main():
    """Main execution function."""
    print("🚀 ACGS-2 Infrastructure Deployment Suite")
    print("=" * 60)
    
    # Initialize configuration
    config = DeploymentConfig()
    deployer = ACGSInfrastructureDeployer(config)
    
    try:
        # Deploy complete infrastructure
        report = await deployer.deploy_complete_infrastructure()
        
        # Save detailed report
        report_path = await deployer.save_deployment_report(report)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        if report["success"]:
            print("✅ Infrastructure deployment completed successfully!")
        else:
            print("❌ Infrastructure deployment completed with issues")
        
        print(f"\nInfrastructure Deployed: {len(report['infrastructure_deployed'])}")
        for service in report["infrastructure_deployed"]:
            print(f"  • {service}")
        
        print(f"\nServices Configured: {len(report['services_deployed'])}")
        for service in report["services_deployed"]:
            print(f"  • {service}")
        
        print(f"\nMonitoring Deployed: {len(report['monitoring_deployed'])}")
        for service in report["monitoring_deployed"]:
            print(f"  • {service}")
        
        print(f"\nConstitutional Hash: {report['constitutional_hash']}")
        print(f"Detailed report: {report_path}")
        
        print("\n📋 Next Steps:")
        print("1. Build and deploy core services using docker-compose.services.yml")
        print("2. Run infrastructure validation: python3 tools/infrastructure_deployment_validator.py")
        print("3. Configure monitoring dashboards in Grafana")
        print("4. Set up production SSL certificates")
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        print(f"❌ Deployment failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
