#!/usr/bin/env python3
"""
ACGS-2 Distributed Tracing Deployment Manager
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive deployment and management system for ACGS-2 distributed tracing
infrastructure including Jaeger, OpenTelemetry, and trace analysis.
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
import time

class ACGSTracingDeployer:
    """
    ACGS-2 Distributed Tracing Deployment Manager
    Constitutional Hash: cdd01ef066bc6cf2
    
    Manages:
    - Jaeger deployment and configuration
    - OpenTelemetry collector setup
    - Elasticsearch backend for trace storage
    - Trace analysis and monitoring
    - Performance optimization
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/observability/distributed-tracing/tracing-config.yaml"
        self.tracing_config = self._load_tracing_config()
        self.logger = self._setup_logging()
        
        # Deployment statistics
        self.deployment_stats = {
            "deployment_start_time": None,
            "deployment_end_time": None,
            "jaeger_deployed": False,
            "elasticsearch_deployed": False,
            "otel_collector_deployed": False,
            "instrumentation_configured": False,
            "trace_analyzer_deployed": False,
            "services_instrumented": 0,
            "constitutional_compliance": True
        }
        
        # Tracing components
        self.tracing_components = {
            "jaeger": ["jaeger-collector", "jaeger-query", "jaeger-agent"],
            "elasticsearch": ["elasticsearch"],
            "otel_collector": ["otel-collector"],
            "analysis": ["trace-analyzer"]
        }
        
        # Service instrumentation mapping
        self.service_instrumentation = {
            "constitutional-core": {
                "port": 8001,
                "tracing_enabled": True,
                "constitutional_compliance": True,
                "sampling_rate": 1.0
            },
            "groqcloud-policy": {
                "port": 8023,
                "tracing_enabled": True,
                "constitutional_compliance": True,
                "sampling_rate": 1.0
            },
            "auth-service": {
                "port": 8013,
                "tracing_enabled": True,
                "constitutional_compliance": True,
                "sampling_rate": 1.0
            },
            "api-gateway": {
                "port": 8080,
                "tracing_enabled": True,
                "constitutional_compliance": True,
                "sampling_rate": 1.0
            },
            "monitoring-service": {
                "port": 8014,
                "tracing_enabled": True,
                "constitutional_compliance": True,
                "sampling_rate": 0.5
            }
        }
        
    def _load_tracing_config(self) -> Dict:
        """Load tracing configuration"""
        default_config = {
            "jaeger": {
                "version": "1.49.0",
                "namespace": "jaeger-system",
                "storage": "elasticsearch",
                "sampling_rate": 1.0,
                "max_traces_per_second": 1000
            },
            "elasticsearch": {
                "version": "7.17.12",
                "replicas": 3,
                "storage_per_node": "20Gi",
                "heap_size": "1g",
                "index_prefix": "acgs-traces"
            },
            "otel_collector": {
                "version": "0.86.0",
                "replicas": 3,
                "memory_limit": "2Gi",
                "cpu_limit": "1000m",
                "batch_size": 1024,
                "timeout": "1s"
            },
            "constitutional_validation": {
                "enabled": True,
                "strict_mode": True,
                "hash": "cdd01ef066bc6cf2"
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
            print(f"Error loading tracing config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for tracing deployment"""
        logger = logging.getLogger("acgs_tracing_deployer")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("/var/log/acgs-tracing")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"/var/log/acgs-tracing/tracing_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
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
        """Check prerequisites for tracing deployment"""
        self.logger.info("🔍 Checking prerequisites for distributed tracing deployment...")
        
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
        
        # Check if ACGS namespace exists
        success, stdout, stderr = await self._execute_command([
            "kubectl", "get", "namespace", "acgs-system"
        ])
        if not success:
            self.logger.error("❌ ACGS namespace does not exist")
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
    
    async def deploy_jaeger(self) -> bool:
        """Deploy Jaeger tracing infrastructure"""
        self.logger.info("🚀 Deploying Jaeger tracing infrastructure...")
        
        try:
            # Create Jaeger namespace
            namespace_cmd = [
                "kubectl", "create", "namespace", "jaeger-system", "--dry-run=client", "-o", "yaml"
            ]
            success, stdout, stderr = await self._execute_command(namespace_cmd)
            
            if success:
                # Apply namespace with labels
                apply_cmd = ["kubectl", "apply", "-f", "-"]
                process = await asyncio.create_subprocess_exec(
                    *apply_cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                namespace_yaml = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: jaeger-system
  labels:
    constitutional-hash: {self.constitutional_hash}
    name: jaeger-system
"""
                
                stdout, stderr = await process.communicate(namespace_yaml.encode())
            
            # Deploy Jaeger manifests
            jaeger_file = "/observability/distributed-tracing/jaeger-deployment.yaml"
            
            if not os.path.exists(jaeger_file):
                self.logger.error(f"❌ Jaeger deployment file not found: {jaeger_file}")
                return False
            
            apply_cmd = ["kubectl", "apply", "-f", jaeger_file]
            success, stdout, stderr = await self._execute_command(apply_cmd)
            
            if success:
                self.logger.info("✅ Jaeger infrastructure deployed successfully")
                self.deployment_stats["jaeger_deployed"] = True
                
                # Wait for Jaeger components to be ready
                await self._wait_for_jaeger_ready()
                
                return True
            else:
                self.logger.error(f"❌ Failed to deploy Jaeger: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying Jaeger: {e}")
            return False
    
    async def _wait_for_jaeger_ready(self, timeout: int = 300):
        """Wait for Jaeger components to be ready"""
        self.logger.info("⏳ Waiting for Jaeger components to be ready...")
        
        components = ["jaeger-collector", "jaeger-query", "elasticsearch"]
        
        for component in components:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                check_cmd = [
                    "kubectl", "get", "pods", "-l", f"app={component}",
                    "-n", "jaeger-system", "--field-selector=status.phase=Running"
                ]
                
                success, stdout, stderr = await self._execute_command(check_cmd)
                
                if success and stdout.strip():
                    self.logger.info(f"✅ {component} is ready")
                    break
                    
                await asyncio.sleep(10)
            else:
                self.logger.error(f"❌ {component} failed to become ready within {timeout}s")
                return False
        
        self.logger.info("✅ All Jaeger components are ready")
        return True
    
    async def deploy_otel_collector(self) -> bool:
        """Deploy OpenTelemetry collector"""
        self.logger.info("🚀 Deploying OpenTelemetry collector...")
        
        try:
            # Deploy OpenTelemetry collector manifests
            otel_file = "/observability/distributed-tracing/opentelemetry-collector.yaml"
            
            if not os.path.exists(otel_file):
                self.logger.error(f"❌ OpenTelemetry collector file not found: {otel_file}")
                return False
            
            apply_cmd = ["kubectl", "apply", "-f", otel_file]
            success, stdout, stderr = await self._execute_command(apply_cmd)
            
            if success:
                self.logger.info("✅ OpenTelemetry collector deployed successfully")
                self.deployment_stats["otel_collector_deployed"] = True
                
                # Wait for collector to be ready
                await self._wait_for_otel_collector_ready()
                
                return True
            else:
                self.logger.error(f"❌ Failed to deploy OpenTelemetry collector: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying OpenTelemetry collector: {e}")
            return False
    
    async def _wait_for_otel_collector_ready(self, timeout: int = 180):
        """Wait for OpenTelemetry collector to be ready"""
        self.logger.info("⏳ Waiting for OpenTelemetry collector to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            check_cmd = [
                "kubectl", "get", "pods", "-l", "app=otel-collector",
                "-n", "acgs-system", "--field-selector=status.phase=Running"
            ]
            
            success, stdout, stderr = await self._execute_command(check_cmd)
            
            if success and stdout.strip():
                self.logger.info("✅ OpenTelemetry collector is ready")
                return True
                
            await asyncio.sleep(10)
        
        self.logger.error(f"❌ OpenTelemetry collector failed to become ready within {timeout}s")
        return False
    
    async def configure_service_instrumentation(self) -> bool:
        """Configure service instrumentation"""
        self.logger.info("⚙️ Configuring service instrumentation...")
        
        try:
            instrumented_services = 0
            
            for service_name, config in self.service_instrumentation.items():
                # Check if service exists
                check_cmd = [
                    "kubectl", "get", "deployment", service_name,
                    "-n", "acgs-system"
                ]
                
                success, stdout, stderr = await self._execute_command(check_cmd)
                
                if success:
                    # Add tracing annotations to service
                    annotations = {
                        "instrumentation.opentelemetry.io/inject-python": "true",
                        "instrumentation.opentelemetry.io/container-names": service_name,
                        "constitutional-hash": self.constitutional_hash,
                        "tracing.enabled": "true",
                        "tracing.sampling-rate": str(config["sampling_rate"])
                    }
                    
                    annotation_cmd = ["kubectl", "annotate", "deployment", service_name, "-n", "acgs-system"]
                    for key, value in annotations.items():
                        annotation_cmd.extend([f"{key}={value}"])
                    
                    success, stdout, stderr = await self._execute_command(annotation_cmd)
                    
                    if success:
                        self.logger.info(f"✅ Instrumentation configured for {service_name}")
                        instrumented_services += 1
                    else:
                        self.logger.warning(f"⚠️ Failed to configure instrumentation for {service_name}: {stderr}")
                else:
                    self.logger.warning(f"⚠️ Service {service_name} not found")
            
            self.deployment_stats["services_instrumented"] = instrumented_services
            self.deployment_stats["instrumentation_configured"] = instrumented_services > 0
            
            self.logger.info(f"✅ Service instrumentation configured for {instrumented_services} services")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring service instrumentation: {e}")
            return False
    
    async def deploy_trace_analyzer(self) -> bool:
        """Deploy trace analyzer"""
        self.logger.info("🚀 Deploying trace analyzer...")
        
        try:
            # Create trace analyzer deployment
            analyzer_deployment = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trace-analyzer
  namespace: acgs-system
  labels:
    app: trace-analyzer
    constitutional-hash: {self.constitutional_hash}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trace-analyzer
  template:
    metadata:
      labels:
        app: trace-analyzer
        constitutional-hash: {self.constitutional_hash}
    spec:
      containers:
      - name: trace-analyzer
        image: python:3.11-slim
        command: ["python3", "/app/trace-analyzer.py"]
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: CONSTITUTIONAL_HASH
          value: "{self.constitutional_hash}"
        - name: JAEGER_QUERY_URL
          value: "http://jaeger-query.jaeger-system.svc.cluster.local:16686"
        - name: ELASTICSEARCH_URL
          value: "http://elasticsearch.jaeger-system.svc.cluster.local:9200"
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: analyzer-code
          mountPath: /app
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: analyzer-code
        configMap:
          name: trace-analyzer-code
---
apiVersion: v1
kind: Service
metadata:
  name: trace-analyzer
  namespace: acgs-system
  labels:
    app: trace-analyzer
    constitutional-hash: {self.constitutional_hash}
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    name: http
  selector:
    app: trace-analyzer
"""
            
            # Apply deployment
            apply_cmd = ["kubectl", "apply", "-f", "-"]
            process = await asyncio.create_subprocess_exec(
                *apply_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(analyzer_deployment.encode())
            
            if process.returncode == 0:
                self.logger.info("✅ Trace analyzer deployed successfully")
                self.deployment_stats["trace_analyzer_deployed"] = True
                return True
            else:
                self.logger.error(f"❌ Failed to deploy trace analyzer: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying trace analyzer: {e}")
            return False
    
    async def validate_tracing_deployment(self) -> bool:
        """Validate tracing deployment"""
        self.logger.info("🔍 Validating tracing deployment...")
        
        try:
            # Check Jaeger components
            jaeger_components = ["jaeger-collector", "jaeger-query", "elasticsearch"]
            
            for component in jaeger_components:
                check_cmd = [
                    "kubectl", "get", "pods", "-l", f"app={component}",
                    "-n", "jaeger-system", "--field-selector=status.phase=Running"
                ]
                
                success, stdout, stderr = await self._execute_command(check_cmd)
                
                if success and stdout.strip():
                    self.logger.info(f"✅ {component} is running")
                else:
                    self.logger.error(f"❌ {component} is not running")
                    return False
            
            # Check OpenTelemetry collector
            otel_check_cmd = [
                "kubectl", "get", "pods", "-l", "app=otel-collector",
                "-n", "acgs-system", "--field-selector=status.phase=Running"
            ]
            
            success, stdout, stderr = await self._execute_command(otel_check_cmd)
            
            if success and stdout.strip():
                self.logger.info("✅ OpenTelemetry collector is running")
            else:
                self.logger.error("❌ OpenTelemetry collector is not running")
                return False
            
            # Validate constitutional compliance
            compliance_cmd = [
                "kubectl", "get", "all", "-n", "jaeger-system",
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
            self.logger.error(f"Error validating tracing deployment: {e}")
            return False
    
    async def generate_tracing_report(self) -> Dict:
        """Generate comprehensive tracing deployment report"""
        deployment_duration = (
            self.deployment_stats["deployment_end_time"] - 
            self.deployment_stats["deployment_start_time"]
        ).total_seconds() if self.deployment_stats["deployment_end_time"] else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "deployment_duration_seconds": deployment_duration,
            "statistics": self.deployment_stats.copy(),
            "tracing_configuration": {
                "jaeger_version": self.tracing_config["jaeger"]["version"],
                "elasticsearch_replicas": self.tracing_config["elasticsearch"]["replicas"],
                "otel_collector_replicas": self.tracing_config["otel_collector"]["replicas"],
                "constitutional_validation": self.tracing_config["constitutional_validation"]["enabled"]
            },
            "constitutional_compliance": self.deployment_stats["constitutional_compliance"],
            "deployment_success": all([
                self.deployment_stats["jaeger_deployed"],
                self.deployment_stats["otel_collector_deployed"],
                self.deployment_stats["instrumentation_configured"]
            ]),
            "service_instrumentation": self.service_instrumentation,
            "performance_targets": self.tracing_config["performance"]
        }
        
        return report
    
    async def deploy_distributed_tracing(self) -> Dict[str, bool]:
        """Deploy complete distributed tracing infrastructure"""
        self.logger.info("🚀 Starting ACGS-2 distributed tracing deployment")
        self.logger.info(f"🏛️ Constitutional Hash: {self.constitutional_hash}")
        self.logger.info(f"🔧 Jaeger Version: {self.tracing_config['jaeger']['version']}")
        self.logger.info(f"📊 Target Namespace: acgs-system")
        
        self.deployment_stats["deployment_start_time"] = datetime.now()
        
        results = {}
        
        # 1. Check prerequisites
        results["prerequisites"] = await self.check_prerequisites()
        if not results["prerequisites"]:
            return results
        
        # 2. Deploy Jaeger infrastructure
        results["jaeger_deployment"] = await self.deploy_jaeger()
        
        # 3. Deploy OpenTelemetry collector
        results["otel_collector_deployment"] = await self.deploy_otel_collector()
        
        # 4. Configure service instrumentation
        results["service_instrumentation"] = await self.configure_service_instrumentation()
        
        # 5. Deploy trace analyzer
        results["trace_analyzer_deployment"] = await self.deploy_trace_analyzer()
        
        # 6. Validate deployment
        results["validation"] = await self.validate_tracing_deployment()
        
        self.deployment_stats["deployment_end_time"] = datetime.now()
        
        # Generate and save deployment report
        deployment_report = await self.generate_tracing_report()
        
        report_file = Path(f"/var/log/acgs-tracing/tracing_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(deployment_report, f, indent=2)
        
        # Log final results
        self.logger.info("==" * 30)
        self.logger.info("🎯 ACGS-2 DISTRIBUTED TRACING DEPLOYMENT COMPLETED")
        self.logger.info("==" * 30)
        self.logger.info(f"🚀 Jaeger deployed: {self.deployment_stats['jaeger_deployed']}")
        self.logger.info(f"📊 OpenTelemetry collector deployed: {self.deployment_stats['otel_collector_deployed']}")
        self.logger.info(f"⚙️ Service instrumentation configured: {self.deployment_stats['instrumentation_configured']}")
        self.logger.info(f"🔍 Trace analyzer deployed: {self.deployment_stats['trace_analyzer_deployed']}")
        self.logger.info(f"🎯 Services instrumented: {self.deployment_stats['services_instrumented']}")
        self.logger.info(f"⏱️ Deployment duration: {deployment_report['deployment_duration_seconds']:.2f} seconds")
        self.logger.info(f"📋 Deployment report: {report_file}")
        
        if deployment_report["deployment_success"]:
            self.logger.info("✅ Distributed tracing deployment successful!")
        else:
            self.logger.warning("⚠️ Distributed tracing deployment completed with issues")
        
        return results

async def main():
    """Main deployment execution function"""
    try:
        deployer = ACGSTracingDeployer()
        results = await deployer.deploy_distributed_tracing()
        
        # Check overall success
        if all(results.values()):
            print("🎉 ACGS-2 distributed tracing deployment completed successfully!")
            sys.exit(0)
        else:
            print("❌ Distributed tracing deployment completed with issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error in distributed tracing deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())