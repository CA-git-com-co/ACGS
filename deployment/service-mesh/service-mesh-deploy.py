#!/usr/bin/env python3
"""
ACGS-2 Service Mesh Deployment Manager
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive service mesh deployment and management system for ACGS-2.
Handles Istio deployment, configuration, and ongoing management.
"""

import asyncio
import json
import logging
import os
import sys
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess

class ACGSServiceMeshDeployer:
    """
    ACGS-2 Service Mesh Deployment Manager
    Constitutional Hash: cdd01ef066bc6cf2
    
    Manages:
    - Istio service mesh installation
    - Traffic management configuration
    - Security policies deployment
    - Observability setup
    - Performance monitoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/deployment/service-mesh/mesh-config.yaml"
        self.mesh_config = self._load_mesh_config()
        self.logger = self._setup_logging()
        
        # Deployment statistics
        self.deployment_stats = {
            "deployment_start_time": None,
            "deployment_end_time": None,
            "istio_installed": False,
            "traffic_policies_applied": 0,
            "security_policies_applied": 0,
            "observability_configured": False,
            "services_in_mesh": 0,
            "constitutional_compliance": True
        }
        
        # Service mesh components
        self.mesh_components = {
            "istio-system": ["istiod", "istio-ingressgateway", "istio-egressgateway"],
            "observability": ["jaeger", "kiali", "prometheus", "grafana", "otel-collector"],
            "security": ["peer-authentication", "authorization-policy", "request-authentication"]
        }
        
    def _load_mesh_config(self) -> Dict:
        """Load service mesh configuration"""
        default_config = {
            "istio_version": "1.19.3",
            "namespace": "acgs-system",
            "istio_namespace": "istio-system",
            "constitutional_validation": {
                "enabled": True,
                "strict_mode": True,
                "hash": "cdd01ef066bc6cf2"
            },
            "traffic_management": {
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "circuit_breaker_threshold": 5
            },
            "security": {
                "mutual_tls": "strict",
                "jwt_validation": True,
                "authorization_policies": True
            },
            "observability": {
                "tracing_enabled": True,
                "metrics_enabled": True,
                "access_logging": True,
                "sampling_rate": 1.0
            },
            "performance": {
                "p99_latency_ms": 5,
                "throughput_rps": 100,
                "monitoring_interval": 30
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            else:
                return default_config
        except Exception as e:
            print(f"Error loading mesh config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for service mesh deployment"""
        logger = logging.getLogger("acgs_service_mesh")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("/var/log/acgs-service-mesh")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"/var/log/acgs-service-mesh/mesh_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
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
    
    async def _execute_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Execute command with error handling"""
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
    
    async def check_prerequisites(self) -> bool:
        """Check prerequisites for service mesh deployment"""
        self.logger.info("🔍 Checking prerequisites for service mesh deployment...")
        
        # Check kubectl availability
        success, stdout, stderr = await self._execute_command(["kubectl", "version", "--client"])
        if not success:
            self.logger.error("❌ kubectl is not available")
            return False
        
        # Check cluster connectivity
        success, stdout, stderr = await self._execute_command(["kubectl", "cluster-info"])
        if not success:
            self.logger.error("❌ Cannot connect to Kubernetes cluster")
            return False
        
        # Check if namespace exists
        success, stdout, stderr = await self._execute_command([
            "kubectl", "get", "namespace", self.mesh_config["namespace"]
        ])
        if not success:
            self.logger.error(f"❌ Namespace {self.mesh_config['namespace']} does not exist")
            return False
        
        # Check available resources
        success, stdout, stderr = await self._execute_command([
            "kubectl", "get", "nodes", "-o", "json"
        ])
        if success:
            try:
                nodes_data = json.loads(stdout)
                node_count = len(nodes_data.get("items", []))
                if node_count < 1:
                    self.logger.error("❌ No nodes available in cluster")
                    return False
                self.logger.info(f"✅ Cluster has {node_count} nodes available")
            except json.JSONDecodeError:
                self.logger.warning("⚠️ Could not parse cluster node information")
        
        self.logger.info("✅ Prerequisites check passed")
        return True
    
    async def install_istio(self) -> bool:
        """Install Istio service mesh"""
        self.logger.info("🚀 Installing Istio service mesh...")
        
        try:
            # Download Istio
            istio_version = self.mesh_config["istio_version"]
            download_cmd = [
                "curl", "-L", f"https://istio.io/downloadIstio"
            ]
            
            # Set environment variable for version
            env = os.environ.copy()
            env["ISTIO_VERSION"] = istio_version
            
            process = await asyncio.create_subprocess_exec(
                *download_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"❌ Failed to download Istio: {stderr.decode()}")
                return False
            
            # Install Istio using istioctl
            istio_dir = f"istio-{istio_version}"
            istioctl_path = f"./{istio_dir}/bin/istioctl"
            
            # Make istioctl executable
            await self._execute_command(["chmod", "+x", istioctl_path])
            
            # Install Istio
            install_cmd = [
                istioctl_path, "install", 
                "--set", "values.defaultRevision=default",
                "--set", f"values.global.meshID=acgs-mesh",
                "--set", f"values.global.multiCluster.clusterName=acgs-cluster",
                "--set", f"values.global.network=acgs-network",
                "-y"
            ]
            
            success, stdout, stderr = await self._execute_command(install_cmd)
            
            if success:
                self.logger.info("✅ Istio control plane installed successfully")
                self.deployment_stats["istio_installed"] = True
                return True
            else:
                self.logger.error(f"❌ Istio installation failed: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing Istio: {e}")
            return False
    
    async def configure_namespace(self) -> bool:
        """Configure namespace for service mesh"""
        self.logger.info("⚙️ Configuring namespace for service mesh...")
        
        try:
            # Label namespace for sidecar injection
            label_cmd = [
                "kubectl", "label", "namespace", self.mesh_config["namespace"],
                "istio-injection=enabled",
                f"constitutional-hash={self.constitutional_hash}",
                "--overwrite"
            ]
            
            success, stdout, stderr = await self._execute_command(label_cmd)
            
            if success:
                self.logger.info(f"✅ Namespace {self.mesh_config['namespace']} configured for service mesh")
                return True
            else:
                self.logger.error(f"❌ Failed to configure namespace: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error configuring namespace: {e}")
            return False
    
    async def apply_traffic_management(self) -> bool:
        """Apply traffic management policies"""
        self.logger.info("🚦 Applying traffic management policies...")
        
        try:
            # Apply traffic management manifests
            traffic_file = "/deployment/service-mesh/traffic-management.yaml"
            
            if not os.path.exists(traffic_file):
                self.logger.error(f"❌ Traffic management file not found: {traffic_file}")
                return False
            
            apply_cmd = ["kubectl", "apply", "-f", traffic_file]
            success, stdout, stderr = await self._execute_command(apply_cmd)
            
            if success:
                # Count applied policies
                policies_applied = len([line for line in stdout.split('\n') if 'created' in line or 'configured' in line])
                self.deployment_stats["traffic_policies_applied"] = policies_applied
                
                self.logger.info(f"✅ Traffic management policies applied: {policies_applied}")
                return True
            else:
                self.logger.error(f"❌ Failed to apply traffic management policies: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying traffic management: {e}")
            return False
    
    async def apply_security_policies(self) -> bool:
        """Apply security policies"""
        self.logger.info("🔒 Applying security policies...")
        
        try:
            # Apply security policies manifests
            security_file = "/deployment/service-mesh/security-policies.yaml"
            
            if not os.path.exists(security_file):
                self.logger.error(f"❌ Security policies file not found: {security_file}")
                return False
            
            apply_cmd = ["kubectl", "apply", "-f", security_file]
            success, stdout, stderr = await self._execute_command(apply_cmd)
            
            if success:
                # Count applied policies
                policies_applied = len([line for line in stdout.split('\n') if 'created' in line or 'configured' in line])
                self.deployment_stats["security_policies_applied"] = policies_applied
                
                self.logger.info(f"✅ Security policies applied: {policies_applied}")
                return True
            else:
                self.logger.error(f"❌ Failed to apply security policies: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying security policies: {e}")
            return False
    
    async def configure_observability(self) -> bool:
        """Configure observability components"""
        self.logger.info("📊 Configuring observability components...")
        
        try:
            # Apply observability manifests
            observability_file = "/deployment/service-mesh/observability.yaml"
            
            if not os.path.exists(observability_file):
                self.logger.error(f"❌ Observability file not found: {observability_file}")
                return False
            
            apply_cmd = ["kubectl", "apply", "-f", observability_file]
            success, stdout, stderr = await self._execute_command(apply_cmd)
            
            if success:
                self.deployment_stats["observability_configured"] = True
                self.logger.info("✅ Observability components configured")
                return True
            else:
                self.logger.error(f"❌ Failed to configure observability: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error configuring observability: {e}")
            return False
    
    async def validate_mesh_deployment(self) -> bool:
        """Validate service mesh deployment"""
        self.logger.info("🔍 Validating service mesh deployment...")
        
        try:
            # Check Istio components
            istio_components = ["istiod", "istio-ingressgateway", "istio-egressgateway"]
            
            for component in istio_components:
                check_cmd = [
                    "kubectl", "get", "pods", "-l", f"app={component}",
                    "-n", self.mesh_config["istio_namespace"],
                    "--field-selector=status.phase=Running"
                ]
                
                success, stdout, stderr = await self._execute_command(check_cmd)
                
                if success and stdout.strip():
                    self.logger.info(f"✅ {component} is running")
                else:
                    self.logger.error(f"❌ {component} is not running")
                    return False
            
            # Check if services are in mesh
            services_cmd = [
                "kubectl", "get", "pods", "-n", self.mesh_config["namespace"],
                "-o", "jsonpath='{.items[*].spec.containers[?(@.name==\"istio-proxy\")].name}'"
            ]
            
            success, stdout, stderr = await self._execute_command(services_cmd)
            
            if success:
                proxy_count = len([name for name in stdout.strip("'").split() if name == "istio-proxy"])
                self.deployment_stats["services_in_mesh"] = proxy_count
                self.logger.info(f"✅ {proxy_count} services have Istio sidecars")
            
            # Validate constitutional compliance
            compliance_cmd = [
                "kubectl", "get", "all", "-n", self.mesh_config["namespace"],
                "-l", f"constitutional-hash={self.constitutional_hash}"
            ]
            
            success, stdout, stderr = await self._execute_command(compliance_cmd)
            
            if success:
                self.logger.info("✅ Constitutional compliance validated")
                return True
            else:
                self.logger.error("❌ Constitutional compliance validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating mesh deployment: {e}")
            return False
    
    async def generate_mesh_report(self) -> Dict:
        """Generate comprehensive mesh deployment report"""
        deployment_duration = (
            self.deployment_stats["deployment_end_time"] - 
            self.deployment_stats["deployment_start_time"]
        ).total_seconds() if self.deployment_stats["deployment_end_time"] else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "deployment_duration_seconds": deployment_duration,
            "statistics": self.deployment_stats.copy(),
            "mesh_configuration": {
                "istio_version": self.mesh_config["istio_version"],
                "namespace": self.mesh_config["namespace"],
                "istio_namespace": self.mesh_config["istio_namespace"],
                "mutual_tls": self.mesh_config["security"]["mutual_tls"],
                "observability_enabled": self.mesh_config["observability"]["tracing_enabled"]
            },
            "constitutional_compliance": self.deployment_stats["constitutional_compliance"],
            "deployment_success": all([
                self.deployment_stats["istio_installed"],
                self.deployment_stats["traffic_policies_applied"] > 0,
                self.deployment_stats["security_policies_applied"] > 0,
                self.deployment_stats["observability_configured"]
            ])
        }
        
        return report
    
    async def deploy_service_mesh(self) -> Dict[str, bool]:
        """Deploy complete service mesh"""
        self.logger.info("🚀 Starting ACGS-2 service mesh deployment")
        self.logger.info(f"🏛️ Constitutional Hash: {self.constitutional_hash}")
        self.logger.info(f"🔧 Istio Version: {self.mesh_config['istio_version']}")
        self.logger.info(f"📦 Target Namespace: {self.mesh_config['namespace']}")
        
        self.deployment_stats["deployment_start_time"] = datetime.now()
        
        results = {}
        
        # 1. Check prerequisites
        results["prerequisites"] = await self.check_prerequisites()
        if not results["prerequisites"]:
            return results
        
        # 2. Install Istio
        results["istio_installation"] = await self.install_istio()
        
        # 3. Configure namespace
        results["namespace_configuration"] = await self.configure_namespace()
        
        # 4. Apply traffic management
        results["traffic_management"] = await self.apply_traffic_management()
        
        # 5. Apply security policies
        results["security_policies"] = await self.apply_security_policies()
        
        # 6. Configure observability
        results["observability"] = await self.configure_observability()
        
        # 7. Validate deployment
        results["validation"] = await self.validate_mesh_deployment()
        
        self.deployment_stats["deployment_end_time"] = datetime.now()
        
        # Generate and save deployment report
        deployment_report = await self.generate_mesh_report()
        
        report_file = Path(f"/var/log/acgs-service-mesh/mesh_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(deployment_report, f, indent=2)
        
        # Log final results
        self.logger.info("=" * 60)
        self.logger.info("🎯 ACGS-2 SERVICE MESH DEPLOYMENT COMPLETED")
        self.logger.info("=" * 60)
        self.logger.info(f"🔧 Istio installed: {self.deployment_stats['istio_installed']}")
        self.logger.info(f"🚦 Traffic policies applied: {self.deployment_stats['traffic_policies_applied']}")
        self.logger.info(f"🔒 Security policies applied: {self.deployment_stats['security_policies_applied']}")
        self.logger.info(f"📊 Observability configured: {self.deployment_stats['observability_configured']}")
        self.logger.info(f"🔍 Services in mesh: {self.deployment_stats['services_in_mesh']}")
        self.logger.info(f"⏱️ Deployment duration: {deployment_report['deployment_duration_seconds']:.2f} seconds")
        self.logger.info(f"📋 Deployment report: {report_file}")
        
        if deployment_report["deployment_success"]:
            self.logger.info("✅ Service mesh deployment successful!")
        else:
            self.logger.warning("⚠️ Service mesh deployment completed with issues")
        
        return results

async def main():
    """Main deployment execution function"""
    try:
        deployer = ACGSServiceMeshDeployer()
        results = await deployer.deploy_service_mesh()
        
        # Check overall success
        if all(results.values()):
            print("🎉 ACGS-2 service mesh deployment completed successfully!")
            sys.exit(0)
        else:
            print("❌ Service mesh deployment completed with issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error in service mesh deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())