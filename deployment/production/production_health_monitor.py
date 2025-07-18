#!/usr/bin/env python3
"""
ACGS-2 Production Health Monitor
Constitutional Hash: cdd01ef066bc6cf2

Continuous health monitoring and alerting for production ACGS-2 services.
Monitors constitutional compliance, service health, and performance metrics.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiohttp
import yaml

class ACGSProductionHealthMonitor:
    """
    ACGS-2 Production Health Monitor
    Constitutional Hash: cdd01ef066bc6cf2
    
    Monitors:
    - Service health and availability
    - Constitutional compliance validation
    - Performance metrics and SLA adherence
    - Resource utilization
    - Security compliance
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/deployment/config/health-monitor-config.yaml"
        self.monitor_config = self._load_monitor_config()
        self.logger = self._setup_logging()
        
        # Health monitoring statistics
        self.health_stats = {
            "monitoring_start_time": datetime.now(),
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "constitutional_violations": 0,
            "performance_violations": 0,
            "alerts_sent": 0,
            "last_check_time": None
        }
        
        # Service health status
        self.service_health = {}
        
        # Performance thresholds
        self.performance_thresholds = {
            "response_time_ms": 5000,  # P99 < 5ms constitutional requirement
            "throughput_rps": 100,     # > 100 RPS constitutional requirement
            "error_rate_percent": 1.0,  # < 1% error rate
            "cpu_usage_percent": 80.0,  # < 80% CPU usage
            "memory_usage_percent": 85.0  # < 85% memory usage
        }
        
        # Service endpoints for health checks
        self.service_endpoints = {
            "constitutional-core": {"port": 8001, "critical": True},
            "groqcloud-policy": {"port": 8023, "critical": True},
            "multi-agent-coordination": {"port": 8002, "critical": True},
            "worker-agents": {"port": 8003, "critical": False},
            "blackboard-service": {"port": 8004, "critical": False},
            "consensus-engine": {"port": 8005, "critical": True},
            "human-in-the-loop": {"port": 8012, "critical": True},
            "auth-service": {"port": 8013, "critical": True},
            "monitoring-service": {"port": 8014, "critical": True},
            "audit-service": {"port": 8015, "critical": True},
            "gdpr-compliance": {"port": 8016, "critical": False},
            "alerting-service": {"port": 8017, "critical": False},
            "api-gateway": {"port": 8080, "critical": True}
        }
        
    def _load_monitor_config(self) -> Dict:
        """Load health monitoring configuration"""
        default_config = {
            "namespace": "acgs-system",
            "check_interval_seconds": 30,
            "alert_threshold_failures": 3,
            "alert_cooldown_minutes": 15,
            "health_check_timeout": 10,
            "constitutional_validation": {
                "enabled": True,
                "strict_mode": True,
                "hash": "cdd01ef066bc6cf2"
            },
            "performance_monitoring": {
                "enabled": True,
                "sla_p99_latency_ms": 5,
                "sla_throughput_rps": 100,
                "sla_availability_percent": 99.9
            },
            "alerting": {
                "enabled": True,
                "webhook_url": "http://alerting-service:8017/webhook",
                "email_enabled": False,
                "slack_enabled": False
            },
            "logging": {
                "level": "INFO",
                "retention_days": 30
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
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for health monitoring"""
        logger = logging.getLogger("acgs_health_monitor")
        logger.setLevel(getattr(logging, self.monitor_config["logging"]["level"]))
        
        # Create logs directory
        log_dir = Path("/var/log/acgs-health")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"/var/log/acgs-health/health_monitor_{datetime.now().strftime('%Y%m%d')}.log")
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
    
    async def _send_alert(self, alert_type: str, service_name: str, message: str, severity: str = "warning") -> bool:
        """Send alert to configured alerting systems"""
        if not self.monitor_config["alerting"]["enabled"]:
            return False
        
        try:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "constitutional_hash": self.constitutional_hash,
                "alert_type": alert_type,
                "service_name": service_name,
                "message": message,
                "severity": severity,
                "environment": "production"
            }
            
            # Send to webhook
            webhook_url = self.monitor_config["alerting"]["webhook_url"]
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(webhook_url, json=alert_data) as response:
                    if response.status == 200:
                        self.health_stats["alerts_sent"] += 1
                        self.logger.info(f"Alert sent for {service_name}: {message}")
                        return True
                    else:
                        self.logger.error(f"Failed to send alert: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
            return False
    
    async def check_service_health(self, service_name: str, endpoint_info: Dict) -> Dict:
        """Check health of a specific service"""
        port = endpoint_info["port"]
        critical = endpoint_info["critical"]
        
        health_result = {
            "service_name": service_name,
            "timestamp": datetime.now().isoformat(),
            "healthy": False,
            "constitutional_compliant": False,
            "response_time_ms": 0,
            "status_code": 0,
            "error_message": None,
            "critical_service": critical
        }
        
        try:
            start_time = time.time()
            
            timeout = aiohttp.ClientTimeout(total=self.monitor_config["health_check_timeout"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                health_url = f"http://{service_name}.{self.monitor_config['namespace']}.svc.cluster.local:{port}/health"
                
                async with session.get(
                    health_url,
                    headers={"Constitutional-Hash": self.constitutional_hash}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    health_result["response_time_ms"] = response_time
                    health_result["status_code"] = response.status
                    
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Check constitutional compliance
                        if health_data.get("constitutional_hash") == self.constitutional_hash:
                            health_result["constitutional_compliant"] = True
                            health_result["healthy"] = True
                            
                            # Check performance thresholds
                            if response_time > self.performance_thresholds["response_time_ms"]:
                                self.health_stats["performance_violations"] += 1
                                await self._send_alert(
                                    "performance_violation",
                                    service_name,
                                    f"Response time {response_time:.2f}ms exceeds threshold {self.performance_thresholds['response_time_ms']}ms",
                                    "warning"
                                )
                            
                        else:
                            health_result["constitutional_compliant"] = False
                            health_result["error_message"] = "Constitutional hash mismatch"
                            self.health_stats["constitutional_violations"] += 1
                            
                            await self._send_alert(
                                "constitutional_violation",
                                service_name,
                                f"Constitutional hash mismatch: expected {self.constitutional_hash}, got {health_data.get('constitutional_hash')}",
                                "critical"
                            )
                    else:
                        health_result["error_message"] = f"HTTP {response.status}"
                        
                        if critical:
                            await self._send_alert(
                                "service_unhealthy",
                                service_name,
                                f"Critical service health check failed: HTTP {response.status}",
                                "critical"
                            )
                        
        except asyncio.TimeoutError:
            health_result["error_message"] = "Health check timeout"
            
            if critical:
                await self._send_alert(
                    "service_timeout",
                    service_name,
                    f"Critical service health check timeout after {self.monitor_config['health_check_timeout']}s",
                    "critical"
                )
                
        except Exception as e:
            health_result["error_message"] = str(e)
            
            if critical:
                await self._send_alert(
                    "service_error",
                    service_name,
                    f"Critical service health check error: {str(e)}",
                    "critical"
                )
        
        return health_result
    
    async def check_kubernetes_health(self) -> Dict:
        """Check Kubernetes cluster health"""
        try:
            # Check node status
            node_check_cmd = [
                "kubectl", "get", "nodes",
                "-o", "jsonpath='{.items[*].status.conditions[?(@.type==\"Ready\")].status}'"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *node_check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                node_statuses = stdout.decode().strip("'").split()
                healthy_nodes = len([status for status in node_statuses if status == "True"])
                total_nodes = len(node_statuses)
                
                # Check pod status in namespace
                pod_check_cmd = [
                    "kubectl", "get", "pods", "-n", self.monitor_config["namespace"],
                    "-o", "jsonpath='{.items[*].status.phase}'"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *pod_check_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    pod_statuses = stdout.decode().strip("'").split()
                    running_pods = len([status for status in pod_statuses if status == "Running"])
                    total_pods = len(pod_statuses)
                    
                    return {
                        "healthy": healthy_nodes == total_nodes and running_pods == total_pods,
                        "healthy_nodes": healthy_nodes,
                        "total_nodes": total_nodes,
                        "running_pods": running_pods,
                        "total_pods": total_pods,
                        "timestamp": datetime.now().isoformat()
                    }
            
            return {
                "healthy": False,
                "error": stderr.decode() if stderr else "Unknown error",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_resource_utilization(self) -> Dict:
        """Check resource utilization across the cluster"""
        try:
            # Get resource usage metrics
            metrics_cmd = [
                "kubectl", "top", "pods", "-n", self.monitor_config["namespace"],
                "--no-headers"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *metrics_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                
                total_cpu = 0
                total_memory = 0
                pod_count = 0
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            cpu_str = parts[1].replace('m', '')
                            memory_str = parts[2].replace('Mi', '')
                            
                            try:
                                total_cpu += int(cpu_str)
                                total_memory += int(memory_str)
                                pod_count += 1
                            except ValueError:
                                continue
                
                avg_cpu = total_cpu / pod_count if pod_count > 0 else 0
                avg_memory = total_memory / pod_count if pod_count > 0 else 0
                
                return {
                    "healthy": True,
                    "total_cpu_millicores": total_cpu,
                    "total_memory_mi": total_memory,
                    "average_cpu_millicores": avg_cpu,
                    "average_memory_mi": avg_memory,
                    "pod_count": pod_count,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "healthy": False,
                "error": stderr.decode() if stderr else "Metrics unavailable",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def perform_comprehensive_health_check(self) -> Dict:
        """Perform comprehensive health check across all services"""
        self.logger.info("🔍 Performing comprehensive health check...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "services": {},
            "kubernetes": {},
            "resources": {},
            "summary": {
                "healthy_services": 0,
                "total_services": 0,
                "constitutional_compliant": 0,
                "critical_services_healthy": 0,
                "critical_services_total": 0,
                "overall_health": "UNKNOWN"
            }
        }
        
        # Check all services
        for service_name, endpoint_info in self.service_endpoints.items():
            self.health_stats["total_checks"] += 1
            
            service_health = await self.check_service_health(service_name, endpoint_info)
            health_report["services"][service_name] = service_health
            
            # Update summary
            health_report["summary"]["total_services"] += 1
            
            if service_health["healthy"]:
                health_report["summary"]["healthy_services"] += 1
                self.health_stats["successful_checks"] += 1
            else:
                self.health_stats["failed_checks"] += 1
            
            if service_health["constitutional_compliant"]:
                health_report["summary"]["constitutional_compliant"] += 1
            
            if endpoint_info["critical"]:
                health_report["summary"]["critical_services_total"] += 1
                if service_health["healthy"]:
                    health_report["summary"]["critical_services_healthy"] += 1
        
        # Check Kubernetes health
        health_report["kubernetes"] = await self.check_kubernetes_health()
        
        # Check resource utilization
        health_report["resources"] = await self.check_resource_utilization()
        
        # Determine overall health
        critical_services_healthy = (
            health_report["summary"]["critical_services_healthy"] == 
            health_report["summary"]["critical_services_total"]
        )
        
        kubernetes_healthy = health_report["kubernetes"]["healthy"]
        
        constitutional_compliant = (
            health_report["summary"]["constitutional_compliant"] == 
            health_report["summary"]["total_services"]
        )
        
        if critical_services_healthy and kubernetes_healthy and constitutional_compliant:
            health_report["summary"]["overall_health"] = "HEALTHY"
        elif critical_services_healthy and kubernetes_healthy:
            health_report["summary"]["overall_health"] = "DEGRADED"
        else:
            health_report["summary"]["overall_health"] = "UNHEALTHY"
        
        # Log summary
        self.logger.info(f"Health check complete: {health_report['summary']['healthy_services']}/{health_report['summary']['total_services']} services healthy")
        self.logger.info(f"Constitutional compliance: {health_report['summary']['constitutional_compliant']}/{health_report['summary']['total_services']} services compliant")
        self.logger.info(f"Overall health: {health_report['summary']['overall_health']}")
        
        self.health_stats["last_check_time"] = datetime.now()
        
        return health_report
    
    async def save_health_report(self, health_report: Dict) -> None:
        """Save health report to file"""
        try:
            report_dir = Path("/var/log/acgs-health/reports")
            report_dir.mkdir(exist_ok=True)
            
            report_file = report_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(health_report, f, indent=2)
            
            self.logger.debug(f"Health report saved to {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
    
    async def run_continuous_monitoring(self) -> None:
        """Run continuous health monitoring"""
        self.logger.info("🚀 Starting ACGS-2 production health monitoring")
        self.logger.info(f"🏛️ Constitutional Hash: {self.constitutional_hash}")
        self.logger.info(f"⏱️ Check interval: {self.monitor_config['check_interval_seconds']} seconds")
        
        while True:
            try:
                health_report = await self.perform_comprehensive_health_check()
                await self.save_health_report(health_report)
                
                # Check for critical issues
                if health_report["summary"]["overall_health"] == "UNHEALTHY":
                    await self._send_alert(
                        "system_unhealthy",
                        "acgs-system",
                        f"System overall health is UNHEALTHY: {health_report['summary']['healthy_services']}/{health_report['summary']['total_services']} services healthy",
                        "critical"
                    )
                
                await asyncio.sleep(self.monitor_config["check_interval_seconds"])
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring cycle: {e}")
                await asyncio.sleep(self.monitor_config["check_interval_seconds"])

async def main():
    """Main monitoring function"""
    try:
        monitor = ACGSProductionHealthMonitor()
        await monitor.run_continuous_monitoring()
    except KeyboardInterrupt:
        print("🛑 Health monitoring stopped by user")
    except Exception as e:
        print(f"❌ Fatal error in health monitoring: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())