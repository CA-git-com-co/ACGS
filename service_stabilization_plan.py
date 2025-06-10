#!/usr/bin/env python3
"""
ACGS-1 Service Infrastructure Stabilization Plan
Phase 1: Full System Activation and Validation
"""

import os
import subprocess
import requests
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceStabilizer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        
        # Service configuration with startup commands
        self.services = {
            "authentication": {
                "port": 8000,
                "path": "services/platform/authentication/auth_service",
                "status": "running"  # Already running
            },
            "constitutional-ai": {
                "port": 8001,
                "path": "services/core/constitutional-ai/ac_service",
                "status": "down"
            },
            "governance-synthesis": {
                "port": 8002,
                "path": "services/core/governance-synthesis/gs_service",
                "status": "down"
            },
            "policy-governance": {
                "port": 8003,
                "path": "services/core/policy-governance/pgc_service",
                "status": "down"
            },
            "formal-verification": {
                "port": 8004,
                "path": "services/core/formal-verification/fv_service",
                "status": "down"
            },
            "integrity": {
                "port": 8005,
                "path": "services/platform/integrity/integrity_service",
                "status": "running"  # Already running
            },
            "evolutionary-computation": {
                "port": 8006,
                "path": "services/core/evolutionary-computation/ec_service",
                "status": "running"  # Already running
            }
        }
        
        # Performance targets
        self.targets = {
            "availability_threshold": 99.5,
            "response_time_threshold": 2.0,
            "startup_timeout": 60
        }

    def install_missing_dependencies(self):
        """Install missing Python dependencies"""
        logger.info("Installing missing Python dependencies...")
        
        missing_packages = [
            "aiosqlite",
            "websockets", 
            "grpcio",
            "grpcio-tools",
            "pytest-asyncio",
            "httpx"
        ]
        
        try:
            # Activate virtual environment and install packages
            venv_python = self.project_root / "venv/bin/python"
            if not venv_python.exists():
                venv_python = self.project_root / ".venv/bin/python"
            if not venv_python.exists():
                venv_python = "python"  # Use system python

            for package in missing_packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [str(venv_python), "-m", "pip", "install", package],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Installed {package}")
                else:
                    logger.warning(f"⚠️ Failed to install {package}: {result.stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False

    def check_service_health(self, service_name, port, timeout=5):
        """Check if a service is healthy"""
        try:
            response = requests.get(
                f"http://localhost:{port}/health",
                timeout=timeout
            )
            return {
                "healthy": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "response_time": None
            }

    def start_service(self, service_name, config):
        """Start a single service"""
        if config["status"] == "running":
            logger.info(f"✅ {service_name} already running on port {config['port']}")
            return True
        
        logger.info(f"Starting {service_name} on port {config['port']}...")
        
        service_path = self.project_root / config["path"]
        
        # Check if service directory exists
        if not service_path.exists():
            logger.error(f"❌ Service path not found: {service_path}")
            return False
        
        # Check if main.py exists
        main_py = service_path / "app/main.py"
        if not main_py.exists():
            main_py = service_path / "main.py"
            if not main_py.exists():
                logger.error(f"❌ main.py not found in {service_path}")
                return False
        
        try:
            # Start service using uvicorn
            venv_python = self.project_root / "venv/bin/python"
            if not venv_python.exists():
                venv_python = self.project_root / ".venv/bin/python"
            if not venv_python.exists():
                venv_python = "python"  # Use system python

            cmd = [
                str(venv_python), "-m", "uvicorn",
                "app.main:app" if (service_path / "app/main.py").exists() else "main:app",
                "--host", "0.0.0.0",
                "--port", str(config["port"]),
                "--reload"
            ]
            
            # Start service in background
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONPATH": str(self.project_root)}
            )
            
            # Wait for service to start
            for attempt in range(12):  # 60 seconds total
                time.sleep(5)
                health = self.check_service_health(service_name, config["port"])
                if health["healthy"]:
                    logger.info(f"✅ {service_name} started successfully")
                    return True
                logger.info(f"⏳ Waiting for {service_name} to start... (attempt {attempt + 1}/12)")
            
            logger.error(f"❌ {service_name} failed to start within timeout")
            process.terminate()
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False

    def start_all_services(self):
        """Start all services that are not running"""
        logger.info("Starting all ACGS-1 services...")
        
        results = {}
        
        # Start services sequentially to avoid resource conflicts
        for service_name, config in self.services.items():
            if config["status"] == "down":
                results[service_name] = self.start_service(service_name, config)
            else:
                results[service_name] = True
        
        return results

    def validate_service_mesh(self):
        """Validate all services are healthy and communicating"""
        logger.info("Validating service mesh health...")
        
        health_results = {}
        
        # Check all services concurrently
        with ThreadPoolExecutor(max_workers=7) as executor:
            future_to_service = {
                executor.submit(self.check_service_health, name, config["port"]): name
                for name, config in self.services.items()
            }

            for future in future_to_service:
                service_name = future_to_service[future]
                try:
                    result = future.result(timeout=10)
                    health_results[service_name] = result
                    
                    if result["healthy"]:
                        response_time = result.get("response_time", 0)
                        logger.info(f"✅ {service_name}: Healthy ({response_time:.3f}s)")
                    else:
                        logger.warning(f"⚠️ {service_name}: Unhealthy - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"❌ {service_name}: Health check failed - {e}")
                    health_results[service_name] = {"healthy": False, "error": str(e)}
        
        # Calculate metrics
        healthy_count = sum(1 for result in health_results.values() if result["healthy"])
        total_count = len(health_results)
        availability = (healthy_count / total_count) * 100
        
        avg_response_time = sum(
            result["response_time"] for result in health_results.values()
            if result["healthy"] and result["response_time"] is not None
        ) / max(healthy_count, 1)
        
        metrics = {
            "healthy_services": healthy_count,
            "total_services": total_count,
            "availability_percentage": availability,
            "average_response_time": avg_response_time,
            "meets_availability_target": availability >= self.targets["availability_threshold"],
            "meets_response_time_target": avg_response_time <= self.targets["response_time_threshold"]
        }
        
        logger.info(f"📊 Service Mesh Status: {healthy_count}/{total_count} healthy ({availability:.1f}%)")
        logger.info(f"📊 Average Response Time: {avg_response_time:.3f}s")
        
        return health_results, metrics

    def test_governance_workflows(self):
        """Test basic governance workflow endpoints"""
        logger.info("Testing governance workflow endpoints...")
        
        workflow_tests = {
            "Policy Creation": {
                "service": "governance-synthesis",
                "endpoint": "/api/v1/policies/create",
                "method": "POST",
                "data": {"title": "Test Policy", "description": "Test"}
            },
            "Constitutional Compliance": {
                "service": "constitutional-ai",
                "endpoint": "/api/v1/compliance/check",
                "method": "POST",
                "data": {"policy": "Test policy content"}
            },
            "Policy Enforcement": {
                "service": "policy-governance",
                "endpoint": "/api/v1/enforcement/validate",
                "method": "POST",
                "data": {"action": "test_action"}
            },
            "Formal Verification": {
                "service": "formal-verification",
                "endpoint": "/api/v1/verify/policy",
                "method": "POST",
                "data": {"policy": "Test policy"}
            }
        }
        
        results = {}
        
        for workflow_name, test_config in workflow_tests.items():
            service_name = test_config["service"]
            service_port = self.services[service_name]["port"]
            
            try:
                url = f"http://localhost:{service_port}{test_config['endpoint']}"
                
                if test_config["method"] == "POST":
                    response = requests.post(url, json=test_config["data"], timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                
                results[workflow_name] = {
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if results[workflow_name]["success"]:
                    logger.info(f"✅ {workflow_name}: Working ({response.status_code})")
                else:
                    logger.warning(f"⚠️ {workflow_name}: Issues ({response.status_code})")
                    
            except Exception as e:
                results[workflow_name] = {
                    "success": False,
                    "error": str(e)
                }
                logger.warning(f"⚠️ {workflow_name}: Failed - {e}")
        
        return results

    def deploy_monitoring_stack(self):
        """Deploy monitoring infrastructure"""
        logger.info("Deploying monitoring stack...")
        
        try:
            # Start monitoring stack
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.monitoring.yml", "up", "-d"],
                cwd=self.project_root / "infrastructure/monitoring",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Monitoring stack deployed successfully")
                logger.info("📊 Grafana available at: http://localhost:3000")
                logger.info("📊 Prometheus available at: http://localhost:9090")
                return True
            else:
                logger.warning(f"⚠️ Monitoring deployment issues: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to deploy monitoring: {e}")
            return False

    def run_comprehensive_tests(self):
        """Run comprehensive test suite with fixed dependencies"""
        logger.info("Running comprehensive test suite...")
        
        test_results = {}
        
        # Run unit tests
        venv_python = self.project_root / "venv/bin/python"
        if not venv_python.exists():
            venv_python = self.project_root / ".venv/bin/python"
        if not venv_python.exists():
            venv_python = "python"  # Use system python

        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pytest", "tests/unit/", "-v", "--tb=short", "-x"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            test_results["unit_tests"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            if result.returncode == 0:
                logger.info("✅ Unit tests passed")
            else:
                logger.warning("⚠️ Unit tests had issues")
                
        except Exception as e:
            logger.warning(f"Unit tests failed: {e}")
            test_results["unit_tests"] = {"success": False, "error": str(e)}
        
        # Run integration tests (with better error handling)
        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pytest", "tests/integration/", "-v", "--tb=short", "-x", "--continue-on-collection-errors"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            test_results["integration_tests"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            if result.returncode == 0:
                logger.info("✅ Integration tests passed")
            else:
                logger.warning("⚠️ Integration tests had issues")
                
        except Exception as e:
            logger.warning(f"Integration tests failed: {e}")
            test_results["integration_tests"] = {"success": False, "error": str(e)}
        
        return test_results

    def generate_stabilization_report(self):
        """Generate comprehensive stabilization report"""
        logger.info("Generating stabilization report...")
        
        # Get current system status
        health_results, metrics = self.validate_service_mesh()
        workflow_results = self.test_governance_workflows()
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "phase": "Service Infrastructure Stabilization",
            "service_health": health_results,
            "performance_metrics": metrics,
            "governance_workflows": workflow_results,
            "targets": self.targets,
            "success_criteria": {
                "all_services_healthy": metrics["healthy_services"] == metrics["total_services"],
                "availability_target_met": metrics["meets_availability_target"],
                "response_time_target_met": metrics["meets_response_time_target"],
                "governance_workflows_functional": all(
                    result.get("success", False) for result in workflow_results.values()
                )
            }
        }
        
        # Calculate overall success
        success_criteria = report["success_criteria"]
        overall_success = all(success_criteria.values())
        report["overall_success"] = overall_success
        
        # Save report
        report_file = self.project_root / "service_stabilization_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Stabilization report saved to {report_file}")
        
        return report, overall_success

    def execute_stabilization_plan(self):
        """Execute the complete service stabilization plan"""
        logger.info("🚀 Starting ACGS-1 Service Infrastructure Stabilization...")
        logger.info("=" * 60)
        
        try:
            # Phase 1: Install missing dependencies
            logger.info("Phase 1: Installing missing dependencies...")
            deps_success = self.install_missing_dependencies()
            
            # Phase 2: Start all services
            logger.info("Phase 2: Starting all services...")
            service_results = self.start_all_services()
            
            # Phase 3: Validate service mesh
            logger.info("Phase 3: Validating service mesh...")
            health_results, metrics = self.validate_service_mesh()
            
            # Phase 4: Test governance workflows
            logger.info("Phase 4: Testing governance workflows...")
            workflow_results = self.test_governance_workflows()
            
            # Phase 5: Deploy monitoring
            logger.info("Phase 5: Deploying monitoring stack...")
            monitoring_success = self.deploy_monitoring_stack()
            
            # Phase 6: Run comprehensive tests
            logger.info("Phase 6: Running comprehensive tests...")
            test_results = self.run_comprehensive_tests()
            
            # Phase 7: Generate final report
            logger.info("Phase 7: Generating stabilization report...")
            report, overall_success = self.generate_stabilization_report()
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("SERVICE STABILIZATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Dependencies: {'✅ SUCCESS' if deps_success else '❌ FAILED'}")
            logger.info(f"Service Health: {metrics['healthy_services']}/{metrics['total_services']} ({metrics['availability_percentage']:.1f}%)")
            logger.info(f"Response Times: {metrics['average_response_time']:.3f}s (target <2s)")
            logger.info(f"Monitoring: {'✅ DEPLOYED' if monitoring_success else '❌ FAILED'}")
            logger.info(f"Governance Workflows: {sum(1 for r in workflow_results.values() if r.get('success', False))}/{len(workflow_results)} working")
            logger.info("=" * 60)
            
            if overall_success:
                logger.info("🎉 SERVICE STABILIZATION: ✅ SUCCESS")
                logger.info("🚀 ACGS-1 is now fully operational and ready for production!")
            else:
                logger.warning("⚠️ SERVICE STABILIZATION: ❌ PARTIAL SUCCESS")
                logger.warning("🔧 Some issues remain - check the stabilization report")
            
            return overall_success
            
        except Exception as e:
            logger.error(f"Service stabilization failed: {e}")
            return False

if __name__ == "__main__":
    stabilizer = ServiceStabilizer()
    success = stabilizer.execute_stabilization_plan()
    exit(0 if success else 1)
