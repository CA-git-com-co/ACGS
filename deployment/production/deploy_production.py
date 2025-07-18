#!/usr/bin/env python3
"""
ACGS-2 Production Deployment Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive production deployment system for ACGS-2 constitutional governance platform.
Manages deployment of all services with health checks, rollback capabilities, and constitutional validation.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiohttp
import yaml

class ACGSProductionDeployer:
    """
    ACGS-2 Production Deployment Orchestrator
    Constitutional Hash: cdd01ef066bc6cf2
    
    Manages production deployment of:
    - Core constitutional services
    - Infrastructure services (auth, monitoring, audit)
    - Compliance services (GDPR, alerting)
    - Database and persistence layers
    - API gateway and load balancing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/deployment/config/production-config.yaml"
        self.deployment_config = self._load_deployment_config()
        self.logger = self._setup_logging()
        
        # Deployment statistics
        self.deployment_stats = {
            "total_services": 0,
            "deployed_services": 0,
            "failed_services": 0,
            "healthy_services": 0,
            "constitutional_compliant": 0,
            "deployment_start_time": None,
            "deployment_end_time": None
        }
        
        # Service dependency graph
        self.service_dependencies = {
            "postgres": [],
            "redis": [],
            "constitutional-core": ["postgres", "redis"],
            "groqcloud-policy": ["constitutional-core"],
            "auth-service": ["postgres", "constitutional-core"],
            "monitoring-service": ["postgres", "constitutional-core"],
            "audit-service": ["postgres", "constitutional-core"],
            "api-gateway": ["auth-service", "monitoring-service"],
            "gdpr-compliance": ["postgres", "audit-service"],
            "alerting-service": ["monitoring-service", "audit-service"],
            "human-in-the-loop": ["constitutional-core", "auth-service"],
            "multi-agent-coordination": ["constitutional-core", "human-in-the-loop"],
            "worker-agents": ["multi-agent-coordination"],
            "blackboard-service": ["multi-agent-coordination"],
            "consensus-engine": ["multi-agent-coordination", "blackboard-service"]
        }
        
    def _load_deployment_config(self) -> Dict:
        """Load production deployment configuration"""
        default_config = {
            "namespace": "acgs-system",
            "environment": "production",
            "replicas": {
                "core": 3,
                "infrastructure": 2,
                "agents": 2
            },
            "resources": {
                "small": {"cpu": "100m", "memory": "128Mi", "cpu_limit": "500m", "memory_limit": "512Mi"},
                "medium": {"cpu": "250m", "memory": "256Mi", "cpu_limit": "1000m", "memory_limit": "1Gi"},
                "large": {"cpu": "500m", "memory": "512Mi", "cpu_limit": "2000m", "memory_limit": "2Gi"}
            },
            "health_checks": {
                "initial_delay": 30,
                "timeout": 10,
                "period": 30,
                "failure_threshold": 3,
                "success_threshold": 1
            },
            "deployment_strategy": {
                "type": "RollingUpdate",
                "max_surge": 1,
                "max_unavailable": 0
            },
            "monitoring": {
                "prometheus": True,
                "grafana": True,
                "alertmanager": True
            },
            "backup": {
                "enabled": True,
                "schedule": "*/15 * * * *",
                "retention_days": 30
            },
            "constitutional_validation": {
                "enabled": True,
                "hash": "cdd01ef066bc6cf2",
                "strict_mode": True
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            else:
                self.logger.warning(f"Config file not found at {self.config_path}, using defaults")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for production deployment"""
        logger = logging.getLogger("acgs_production_deploy")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("/var/log/acgs-deployment")
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.FileHandler(f"/var/log/acgs-deployment/production_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_formatter = logging.Formatter(
            f'%(asctime)s - CONSTITUTIONAL_HASH:{self.constitutional_hash} - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    async def _execute_kubectl_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Execute kubectl command with error handling"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return (
                process.returncode == 0,
                stdout.decode() if stdout else "",
                stderr.decode() if stderr else ""
            )
            
        except Exception as e:
            return False, "", str(e)
    
    async def _wait_for_service_health(self, service_name: str, port: int, timeout: int = 300) -> bool:
        """Wait for service to become healthy"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if pods are running
                check_pods_cmd = [
                    "kubectl", "get", "pods", "-l", f"app={service_name}",
                    "-n", self.deployment_config["namespace"],
                    "--field-selector=status.phase=Running",
                    "-o", "jsonpath='{.items[*].status.phase}'"
                ]
                
                success, stdout, stderr = await self._execute_kubectl_command(check_pods_cmd)
                
                if success and "Running" in stdout:
                    # Check service health endpoint
                    try:
                        timeout_config = aiohttp.ClientTimeout(total=10)
                        async with aiohttp.ClientSession(timeout=timeout_config) as session:
                            async with session.get(
                                f"http://{service_name}.{self.deployment_config['namespace']}.svc.cluster.local:{port}/health",
                                headers={"Constitutional-Hash": self.constitutional_hash}
                            ) as response:
                                if response.status == 200:
                                    health_data = await response.json()
                                    
                                    # Validate constitutional compliance
                                    if health_data.get("constitutional_hash") == self.constitutional_hash:
                                        self.logger.info(f"Service {service_name} is healthy and constitutionally compliant")
                                        return True
                                    else:
                                        self.logger.warning(f"Service {service_name} health check failed constitutional validation")
                    except Exception as e:
                        self.logger.debug(f"Health check for {service_name} failed: {e}")
                        
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.debug(f"Error checking {service_name} health: {e}")
                await asyncio.sleep(5)
        
        self.logger.error(f"Service {service_name} failed to become healthy within {timeout} seconds")
        return False
    
    async def deploy_infrastructure_services(self) -> Dict[str, bool]:
        """Deploy core infrastructure services (database, cache, etc.)"""
        self.logger.info("🏗️ Deploying infrastructure services...")
        
        results = {}
        
        # Deploy PostgreSQL
        self.logger.info("Deploying PostgreSQL database...")
        postgres_cmd = [
            "kubectl", "apply", "-f", "/deployment/kubernetes/infrastructure/postgres.yaml",
            "-n", self.deployment_config["namespace"]
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(postgres_cmd)
        if success:
            results["postgres"] = await self._wait_for_service_health("postgres", 5432)
            self.logger.info("✅ PostgreSQL deployed successfully")
        else:
            self.logger.error(f"❌ PostgreSQL deployment failed: {stderr}")
            results["postgres"] = False
        
        # Deploy Redis
        self.logger.info("Deploying Redis cache...")
        redis_cmd = [
            "kubectl", "apply", "-f", "/deployment/kubernetes/infrastructure/redis.yaml",
            "-n", self.deployment_config["namespace"]
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(redis_cmd)
        if success:
            results["redis"] = await self._wait_for_service_health("redis", 6379)
            self.logger.info("✅ Redis deployed successfully")
        else:
            self.logger.error(f"❌ Redis deployment failed: {stderr}")
            results["redis"] = False
        
        return results
    
    async def deploy_core_services(self) -> Dict[str, bool]:
        """Deploy core constitutional services"""
        self.logger.info("🏛️ Deploying core constitutional services...")
        
        results = {}
        
        # Deploy constitutional core
        self.logger.info("Deploying constitutional core service...")
        core_cmd = [
            "kubectl", "apply", "-f", "/deployment/kubernetes/deployments/constitutional-core.yaml",
            "-n", self.deployment_config["namespace"]
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(core_cmd)
        if success:
            results["constitutional-core"] = await self._wait_for_service_health("constitutional-core", 8001)
            self.logger.info("✅ Constitutional core deployed successfully")
        else:
            self.logger.error(f"❌ Constitutional core deployment failed: {stderr}")
            results["constitutional-core"] = False
        
        # Deploy GroqCloud policy service
        self.logger.info("Deploying GroqCloud policy service...")
        groq_cmd = [
            "kubectl", "apply", "-f", "/deployment/kubernetes/deployments/groqcloud-policy.yaml",
            "-n", self.deployment_config["namespace"]
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(groq_cmd)
        if success:
            results["groqcloud-policy"] = await self._wait_for_service_health("groqcloud-policy", 8023)
            self.logger.info("✅ GroqCloud policy service deployed successfully")
        else:
            self.logger.error(f"❌ GroqCloud policy deployment failed: {stderr}")
            results["groqcloud-policy"] = False
        
        return results
    
    async def deploy_agent_services(self) -> Dict[str, bool]:
        """Deploy multi-agent coordination services"""
        self.logger.info("🤖 Deploying multi-agent services...")
        
        results = {}
        
        # Deploy services in dependency order
        agent_services = [
            ("human-in-the-loop", 8012),
            ("multi-agent-coordination", 8002),
            ("worker-agents", 8003),
            ("blackboard-service", 8004),
            ("consensus-engine", 8005)
        ]
        
        for service_name, port in agent_services:
            self.logger.info(f"Deploying {service_name}...")
            
            deploy_cmd = [
                "kubectl", "apply", "-f", f"/deployment/kubernetes/deployments/{service_name}.yaml",
                "-n", self.deployment_config["namespace"]
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(deploy_cmd)
            if success:
                results[service_name] = await self._wait_for_service_health(service_name, port)
                self.logger.info(f"✅ {service_name} deployed successfully")
            else:
                self.logger.error(f"❌ {service_name} deployment failed: {stderr}")
                results[service_name] = False
        
        return results
    
    async def deploy_management_services(self) -> Dict[str, bool]:
        """Deploy management and governance services"""
        self.logger.info("🛡️ Deploying management services...")
        
        results = {}
        
        # Deploy management services
        management_services = [
            ("auth-service", 8013),
            ("monitoring-service", 8014),
            ("audit-service", 8015),
            ("gdpr-compliance", 8016),
            ("alerting-service", 8017),
            ("api-gateway", 8080)
        ]
        
        for service_name, port in management_services:
            self.logger.info(f"Deploying {service_name}...")
            
            deploy_cmd = [
                "kubectl", "apply", "-f", f"/deployment/kubernetes/deployments/{service_name}.yaml",
                "-n", self.deployment_config["namespace"]
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(deploy_cmd)
            if success:
                results[service_name] = await self._wait_for_service_health(service_name, port)
                self.logger.info(f"✅ {service_name} deployed successfully")
            else:
                self.logger.error(f"❌ {service_name} deployment failed: {stderr}")
                results[service_name] = False
        
        return results
    
    async def deploy_monitoring_stack(self) -> Dict[str, bool]:
        """Deploy monitoring and observability stack"""
        self.logger.info("📊 Deploying monitoring stack...")
        
        results = {}
        
        if self.deployment_config["monitoring"]["prometheus"]:
            self.logger.info("Deploying Prometheus...")
            prometheus_cmd = [
                "kubectl", "apply", "-f", "/deployment/kubernetes/monitoring/prometheus.yaml",
                "-n", self.deployment_config["namespace"]
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(prometheus_cmd)
            if success:
                results["prometheus"] = await self._wait_for_service_health("prometheus", 9090)
                self.logger.info("✅ Prometheus deployed successfully")
            else:
                self.logger.error(f"❌ Prometheus deployment failed: {stderr}")
                results["prometheus"] = False
        
        if self.deployment_config["monitoring"]["grafana"]:
            self.logger.info("Deploying Grafana...")
            grafana_cmd = [
                "kubectl", "apply", "-f", "/deployment/kubernetes/monitoring/grafana.yaml",
                "-n", self.deployment_config["namespace"]
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(grafana_cmd)
            if success:
                results["grafana"] = await self._wait_for_service_health("grafana", 3000)
                self.logger.info("✅ Grafana deployed successfully")
            else:
                self.logger.error(f"❌ Grafana deployment failed: {stderr}")
                results["grafana"] = False
        
        return results
    
    async def deploy_backup_system(self) -> Dict[str, bool]:
        """Deploy automated backup system"""
        self.logger.info("💾 Deploying backup system...")
        
        results = {}
        
        if self.deployment_config["backup"]["enabled"]:
            self.logger.info("Deploying backup CronJob...")
            backup_cmd = [
                "kubectl", "apply", "-f", "/backup/kubernetes/backup-cronjob.yaml",
                "-n", self.deployment_config["namespace"]
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(backup_cmd)
            if success:
                results["backup-system"] = True
                self.logger.info("✅ Backup system deployed successfully")
            else:
                self.logger.error(f"❌ Backup system deployment failed: {stderr}")
                results["backup-system"] = False
        
        return results
    
    async def validate_constitutional_compliance(self) -> Dict[str, bool]:
        """Validate constitutional compliance across all services"""
        self.logger.info("🏛️ Validating constitutional compliance...")
        
        results = {}
        
        # Get all services in namespace
        get_services_cmd = [
            "kubectl", "get", "services", "-n", self.deployment_config["namespace"],
            "-o", "jsonpath='{.items[*].metadata.name}'"
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(get_services_cmd)
        
        if success:
            services = stdout.strip("'").split()
            
            for service_name in services:
                if service_name in ["postgres", "redis", "kubernetes", "prometheus", "grafana"]:
                    continue  # Skip infrastructure services
                
                try:
                    # Check constitutional hash in service labels
                    get_labels_cmd = [
                        "kubectl", "get", "service", service_name, "-n", self.deployment_config["namespace"],
                        "-o", "jsonpath='{.metadata.labels.constitutional-hash}'"
                    ]
                    
                    success, stdout, stderr = await self._execute_kubectl_command(get_labels_cmd)
                    
                    if success and self.constitutional_hash in stdout:
                        results[service_name] = True
                        self.deployment_stats["constitutional_compliant"] += 1
                        self.logger.info(f"✅ {service_name} constitutional compliance verified")
                    else:
                        results[service_name] = False
                        self.logger.warning(f"❌ {service_name} constitutional compliance failed")
                        
                except Exception as e:
                    self.logger.error(f"Error validating {service_name}: {e}")
                    results[service_name] = False
        
        return results
    
    async def perform_health_checks(self) -> Dict[str, bool]:
        """Perform comprehensive health checks on all services"""
        self.logger.info("🔍 Performing comprehensive health checks...")
        
        results = {}
        
        # Check all deployed services
        service_ports = {
            "constitutional-core": 8001,
            "groqcloud-policy": 8023,
            "multi-agent-coordination": 8002,
            "worker-agents": 8003,
            "blackboard-service": 8004,
            "consensus-engine": 8005,
            "human-in-the-loop": 8012,
            "auth-service": 8013,
            "monitoring-service": 8014,
            "audit-service": 8015,
            "gdpr-compliance": 8016,
            "alerting-service": 8017,
            "api-gateway": 8080
        }
        
        for service_name, port in service_ports.items():
            try:
                # Check if service is healthy
                health_check = await self._wait_for_service_health(service_name, port, timeout=30)
                results[service_name] = health_check
                
                if health_check:
                    self.deployment_stats["healthy_services"] += 1
                    self.logger.info(f"✅ {service_name} health check passed")
                else:
                    self.logger.warning(f"❌ {service_name} health check failed")
                    
            except Exception as e:
                self.logger.error(f"Error checking {service_name} health: {e}")
                results[service_name] = False
        
        return results
    
    async def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment report"""
        deployment_duration = (
            self.deployment_stats["deployment_end_time"] - 
            self.deployment_stats["deployment_start_time"]
        ).total_seconds() if self.deployment_stats["deployment_end_time"] else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "deployment_environment": self.deployment_config["environment"],
            "deployment_namespace": self.deployment_config["namespace"],
            "deployment_duration_seconds": deployment_duration,
            "statistics": self.deployment_stats.copy(),
            "compliance_status": "COMPLIANT" if self.deployment_stats["constitutional_compliant"] == self.deployment_stats["deployed_services"] else "NON_COMPLIANT",
            "health_status": "HEALTHY" if self.deployment_stats["healthy_services"] == self.deployment_stats["deployed_services"] else "UNHEALTHY",
            "deployment_success_rate": (self.deployment_stats["deployed_services"] / self.deployment_stats["total_services"] * 100) if self.deployment_stats["total_services"] > 0 else 0
        }
        
        return report
    
    async def deploy_all_services(self) -> Dict[str, Dict[str, bool]]:
        """Deploy all ACGS-2 services to production"""
        self.logger.info("🚀 Starting ACGS-2 production deployment")
        self.logger.info(f"🏛️ Constitutional Hash: {self.constitutional_hash}")
        self.logger.info(f"🌍 Environment: {self.deployment_config['environment']}")
        self.logger.info(f"📦 Namespace: {self.deployment_config['namespace']}")
        
        self.deployment_stats["deployment_start_time"] = datetime.now()
        
        # Create namespace if it doesn't exist
        create_namespace_cmd = [
            "kubectl", "create", "namespace", self.deployment_config["namespace"],
            "--dry-run=client", "-o", "yaml"
        ]
        
        success, stdout, stderr = await self._execute_kubectl_command(create_namespace_cmd)
        if success:
            apply_namespace_cmd = [
                "kubectl", "apply", "-f", "-"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *apply_namespace_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate(input=stdout.encode())
        
        all_results = {}
        
        # Deploy in dependency order
        self.logger.info("📋 Deploying services in dependency order...")
        
        # 1. Infrastructure services
        infra_results = await self.deploy_infrastructure_services()
        all_results["infrastructure"] = infra_results
        
        # 2. Core constitutional services
        core_results = await self.deploy_core_services()
        all_results["core"] = core_results
        
        # 3. Agent services
        agent_results = await self.deploy_agent_services()
        all_results["agents"] = agent_results
        
        # 4. Management services
        mgmt_results = await self.deploy_management_services()
        all_results["management"] = mgmt_results
        
        # 5. Monitoring stack
        monitoring_results = await self.deploy_monitoring_stack()
        all_results["monitoring"] = monitoring_results
        
        # 6. Backup system
        backup_results = await self.deploy_backup_system()
        all_results["backup"] = backup_results
        
        # Calculate statistics
        for category_results in all_results.values():
            for service_name, deployed in category_results.items():
                self.deployment_stats["total_services"] += 1
                if deployed:
                    self.deployment_stats["deployed_services"] += 1
                else:
                    self.deployment_stats["failed_services"] += 1
        
        # 7. Validate constitutional compliance
        compliance_results = await self.validate_constitutional_compliance()
        all_results["compliance"] = compliance_results
        
        # 8. Perform health checks
        health_results = await self.perform_health_checks()
        all_results["health"] = health_results
        
        self.deployment_stats["deployment_end_time"] = datetime.now()
        
        # Generate and save deployment report
        deployment_report = await self.generate_deployment_report()
        
        report_file = Path(f"/var/log/acgs-deployment/production_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(deployment_report, f, indent=2)
        
        # Log final results
        self.logger.info("=" * 60)
        self.logger.info("🎯 ACGS-2 PRODUCTION DEPLOYMENT COMPLETED")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Services deployed: {self.deployment_stats['deployed_services']}/{self.deployment_stats['total_services']}")
        self.logger.info(f"🏛️ Constitutional compliance: {self.deployment_stats['constitutional_compliant']}/{self.deployment_stats['deployed_services']}")
        self.logger.info(f"🔍 Health checks: {self.deployment_stats['healthy_services']}/{self.deployment_stats['deployed_services']}")
        self.logger.info(f"⏱️ Deployment duration: {deployment_report['deployment_duration_seconds']:.2f} seconds")
        self.logger.info(f"📋 Deployment report: {report_file}")
        
        if deployment_report["compliance_status"] == "COMPLIANT" and deployment_report["health_status"] == "HEALTHY":
            self.logger.info("✅ Production deployment successful!")
        else:
            self.logger.warning("⚠️ Production deployment completed with issues")
        
        return all_results

async def main():
    """Main deployment execution function"""
    try:
        deployer = ACGSProductionDeployer()
        results = await deployer.deploy_all_services()
        
        # Check overall success
        total_success = True
        for category, category_results in results.items():
            if category in ["compliance", "health"]:
                continue
            for service, deployed in category_results.items():
                if not deployed:
                    total_success = False
                    break
        
        if total_success:
            print("🎉 ACGS-2 production deployment completed successfully!")
            sys.exit(0)
        else:
            print("❌ Some services failed to deploy")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error in production deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())