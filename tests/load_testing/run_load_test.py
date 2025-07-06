"""
ACGS Load Test Execution Script

Script to run enterprise-scale load tests with constitutional compliance
monitoring and automated analysis.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import argparse
import subprocess
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from distributed_config import DistributedLoadTestConfig
from performance_analyzer import PerformanceAnalyzer

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoadTestExecutor:
    """Executes and manages ACGS load tests."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.config = DistributedLoadTestConfig()
        self.analyzer = PerformanceAnalyzer()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Override configuration if provided
        if config_override:
            for key, value in config_override.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        # Test execution state
        self.test_process = None
        self.test_start_time = None
        self.test_name = None
        
        logger.info(f"Load test executor initialized with constitutional hash: {CONSTITUTIONAL_HASH}")
    
    async def run_load_test(
        self,
        test_name: str,
        test_type: str = "enterprise",
        duration: str = "30m",
        users: int = 1000,
        spawn_rate: int = 10,
        auto_analyze: bool = True
    ) -> Dict[str, Any]:
        """Run load test with specified parameters."""
        
        try:
            logger.info(f"Starting load test: {test_name} (type: {test_type})")
            
            self.test_name = test_name
            self.test_start_time = time.time()
            
            # Validate target availability
            target_available = await self._check_target_availability()
            if not target_available:
                raise RuntimeError("Target system is not available")
            
            # Prepare test environment
            await self._prepare_test_environment()
            
            # Execute load test based on type
            if test_type == "enterprise":
                result = await self._run_enterprise_test(test_name, duration, users, spawn_rate)
            elif test_type == "distributed":
                result = await self._run_distributed_test(test_name, duration, users, spawn_rate)
            elif test_type == "spike":
                result = await self._run_spike_test(test_name)
            elif test_type == "stress":
                result = await self._run_stress_test(test_name)
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            # Analyze results if requested
            if auto_analyze and result.get("success", False):
                logger.info("Analyzing test results...")
                analysis = self.analyzer.analyze_load_test_results(test_name)
                result["analysis"] = analysis
            
            # Cleanup
            await self._cleanup_test_environment()
            
            logger.info(f"Load test completed: {test_name}")
            return result
            
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            await self._cleanup_test_environment()
            return {
                "success": False,
                "error": str(e),
                "test_name": test_name,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_target_availability(self) -> bool:
        """Check if target system is available."""
        
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.config.TARGET_HOST}/gateway/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    constitutional_hash = health_data.get("constitutional_hash")
                    
                    if constitutional_hash != self.constitutional_hash:
                        logger.warning(f"Constitutional hash mismatch: expected {self.constitutional_hash}, got {constitutional_hash}")
                        return False
                    
                    logger.info("Target system health check passed")
                    return True
                else:
                    logger.error(f"Target system health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Target system health check error: {e}")
            return False
    
    async def _prepare_test_environment(self):
        """Prepare test environment."""
        
        # Create results directory
        results_dir = Path("./results")
        results_dir.mkdir(exist_ok=True)
        
        # Create reports directory
        reports_dir = Path("./reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Validate configuration
        validation = self.config.validate_configuration()
        if not validation["valid"]:
            raise RuntimeError(f"Configuration validation failed: {validation['errors']}")
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                logger.warning(warning)
        
        logger.info("Test environment prepared")
    
    async def _cleanup_test_environment(self):
        """Cleanup test environment."""
        
        if self.test_process and self.test_process.poll() is None:
            logger.info("Terminating test process...")
            self.test_process.terminate()
            try:
                self.test_process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning("Force killing test process")
                self.test_process.kill()
        
        logger.info("Test environment cleaned up")
    
    async def _run_enterprise_test(self, test_name: str, duration: str, users: int, spawn_rate: int) -> Dict[str, Any]:
        """Run enterprise load test."""
        
        cmd = [
            "python", "-m", "locust",
            "-f", "locustfile.py",
            "--host", self.config.TARGET_HOST,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", duration,
            "--html", f"./reports/{test_name}_report.html",
            "--csv", f"./reports/{test_name}",
            "--headless"
        ]
        
        return await self._execute_test_command(cmd, test_name, "enterprise")
    
    async def _run_distributed_test(self, test_name: str, duration: str, users: int, spawn_rate: int) -> Dict[str, Any]:
        """Run distributed load test using Docker Compose."""
        
        # Generate Docker Compose configuration
        compose_config = self.config.get_docker_compose_config()
        compose_file = Path("./docker-compose.loadtest.yml")
        
        with open(compose_file, 'w') as f:
            import yaml
            yaml.dump(compose_config, f, default_flow_style=False)
        
        # Start distributed test
        cmd = [
            "docker-compose",
            "-f", str(compose_file),
            "up",
            "--scale", f"locust-worker={len(self.config.LOAD_TEST_NODES)}",
            "--abort-on-container-exit"
        ]
        
        return await self._execute_test_command(cmd, test_name, "distributed")
    
    async def _run_spike_test(self, test_name: str) -> Dict[str, Any]:
        """Run spike load test."""
        
        cmd = [
            "python", "-m", "locust",
            "-f", "locustfile.py",
            "--host", self.config.TARGET_HOST,
            "--headless",
            "--html", f"./reports/{test_name}_report.html",
            "--csv", f"./reports/{test_name}",
            "--users", "2000",
            "--spawn-rate", "100",
            "--run-time", "5m"
        ]
        
        return await self._execute_test_command(cmd, test_name, "spike")
    
    async def _run_stress_test(self, test_name: str) -> Dict[str, Any]:
        """Run stress load test."""
        
        cmd = [
            "python", "-m", "locust",
            "-f", "locustfile.py", 
            "--host", self.config.TARGET_HOST,
            "--headless",
            "--html", f"./reports/{test_name}_report.html",
            "--csv", f"./reports/{test_name}",
            "--users", "3000",
            "--spawn-rate", "50",
            "--run-time", "15m"
        ]
        
        return await self._execute_test_command(cmd, test_name, "stress")
    
    async def _execute_test_command(self, cmd: List[str], test_name: str, test_type: str) -> Dict[str, Any]:
        """Execute test command and monitor progress."""
        
        try:
            logger.info(f"Executing {test_type} test: {' '.join(cmd)}")
            
            # Start test process
            self.test_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent
            )
            
            # Monitor test execution
            stdout, stderr = self.test_process.communicate()
            return_code = self.test_process.returncode
            
            test_duration = time.time() - self.test_start_time
            
            if return_code == 0:
                logger.info(f"Test completed successfully in {test_duration:.2f} seconds")
                
                return {
                    "success": True,
                    "test_name": test_name,
                    "test_type": test_type,
                    "duration_seconds": test_duration,
                    "constitutional_hash": self.constitutional_hash,
                    "stdout": stdout,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.error(f"Test failed with return code {return_code}")
                logger.error(f"stderr: {stderr}")
                
                return {
                    "success": False,
                    "test_name": test_name,
                    "test_type": test_type,
                    "return_code": return_code,
                    "stderr": stderr,
                    "stdout": stdout,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error executing test command: {e}")
            return {
                "success": False,
                "test_name": test_name,
                "error": str(e),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
    
    def run_constitutional_compliance_test(self) -> Dict[str, Any]:
        """Run focused constitutional compliance load test."""
        
        logger.info("Running constitutional compliance focused load test")
        
        cmd = [
            "python", "-m", "locust",
            "-f", "locustfile.py",
            "--host", self.config.TARGET_HOST,
            "--headless",
            "--tags", "constitutional",
            "--users", "500",
            "--spawn-rate", "10",
            "--run-time", "10m",
            "--html", "./reports/constitutional_compliance_test_report.html",
            "--csv", "./reports/constitutional_compliance_test"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                # Analyze constitutional compliance specifically
                analysis = self.analyzer.analyze_load_test_results("constitutional_compliance_test")
                
                return {
                    "success": True,
                    "constitutional_hash": self.constitutional_hash,
                    "compliance_analysis": analysis.get("constitutional_compliance", {}),
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }


def main():
    """Main CLI interface for load testing."""
    
    parser = argparse.ArgumentParser(description="ACGS Enterprise Load Testing")
    parser.add_argument("--test-name", required=True, help="Name of the load test")
    parser.add_argument("--test-type", choices=["enterprise", "distributed", "spike", "stress", "constitutional"], 
                       default="enterprise", help="Type of load test to run")
    parser.add_argument("--duration", default="30m", help="Test duration (e.g., 30m, 1h)")
    parser.add_argument("--users", type=int, default=1000, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=10, help="User spawn rate per second")
    parser.add_argument("--target", help="Target host URL (overrides config)")
    parser.add_argument("--no-analysis", action="store_true", help="Skip automatic analysis")
    parser.add_argument("--config-file", help="Custom configuration file")
    
    args = parser.parse_args()
    
    # Load custom configuration if provided
    config_override = {}
    if args.config_file:
        with open(args.config_file) as f:
            config_override = json.load(f)
    
    if args.target:
        config_override["TARGET_HOST"] = args.target
    
    # Initialize executor
    executor = LoadTestExecutor(config_override)
    
    # Run test based on type
    if args.test_type == "constitutional":
        result = executor.run_constitutional_compliance_test()
    else:
        result = asyncio.run(executor.run_load_test(
            test_name=args.test_name,
            test_type=args.test_type,
            duration=args.duration,
            users=args.users,
            spawn_rate=args.spawn_rate,
            auto_analyze=not args.no_analysis
        ))
    
    # Print results
    print("\n" + "="*60)
    print("ACGS LOAD TEST RESULTS")
    print("="*60)
    print(f"Test: {args.test_name}")
    print(f"Type: {args.test_type}")
    print(f"Success: {'✅ PASSED' if result.get('success', False) else '❌ FAILED'}")
    print(f"Constitutional Hash: {result.get('constitutional_hash', 'N/A')}")
    
    if result.get("analysis"):
        analysis = result["analysis"]
        pass_fail = analysis.get("pass_fail_criteria", {})
        print(f"Performance: {pass_fail.get('summary', 'N/A')}")
        
        compliance = analysis.get("constitutional_compliance", {})
        print(f"Constitutional Compliance: {compliance.get('overall_compliance_score', 'N/A')}")
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    
    print("="*60)
    
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    exit(main())