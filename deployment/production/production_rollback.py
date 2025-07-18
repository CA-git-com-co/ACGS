#!/usr/bin/env python3
"""
ACGS-2 Production Rollback System
Constitutional Hash: cdd01ef066bc6cf2

Emergency rollback system for ACGS-2 production services.
Provides safe rollback to previous stable versions with constitutional compliance validation.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiohttp
import yaml

class ACGSProductionRollback:
    """
    ACGS-2 Production Rollback System
    Constitutional Hash: cdd01ef066bc6cf2
    
    Provides:
    - Safe rollback to previous stable versions
    - Constitutional compliance validation during rollback
    - Service dependency-aware rollback ordering
    - Health validation after rollback
    - Automated rollback triggers
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/deployment/config/rollback-config.yaml"
        self.rollback_config = self._load_rollback_config()
        self.logger = self._setup_logging()
        
        # Rollback statistics
        self.rollback_stats = {
            "rollback_start_time": None,
            "rollback_end_time": None,
            "services_rolled_back": 0,
            "services_failed_rollback": 0,
            "constitutional_violations": 0,
            "health_check_failures": 0
        }
        
        # Service rollback order (reverse dependency order)
        self.rollback_order = [
            "api-gateway",
            "alerting-service",
            "gdpr-compliance",
            "audit-service",
            "monitoring-service",
            "auth-service",
            "human-in-the-loop",
            "consensus-engine",
            "blackboard-service",
            "worker-agents",
            "multi-agent-coordination",
            "groqcloud-policy",
            "constitutional-core"
        ]
        
        # Service deployment history
        self.deployment_history = {}
        
    def _load_rollback_config(self) -> Dict:
        """Load rollback configuration"""
        default_config = {
            "namespace": "acgs-system",
            "rollback_timeout_seconds": 600,
            "health_check_timeout": 30,
            "validation_retries": 3,
            "rollback_strategy": "safe",  # safe, fast, emergency
            "constitutional_validation": {
                "enabled": True,
                "strict_mode": True,
                "hash": "cdd01ef066bc6cf2"
            },
            "backup_before_rollback": True,
            "auto_rollback_triggers": {
                "health_check_failures": 3,
                "constitutional_violations": 1,
                "performance_degradation": True
            },
            "notification": {
                "enabled": True,
                "webhook_url": "http://alerting-service:8017/webhook"
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
            print(f"Error loading rollback config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for rollback operations"""
        logger = logging.getLogger("acgs_rollback")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("/var/log/acgs-rollback")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"/var/log/acgs-rollback/rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
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
    
    async def _send_notification(self, message: str, severity: str = "warning") -> bool:
        """Send rollback notification"""
        if not self.rollback_config["notification"]["enabled"]:
            return False
        
        try:
            notification_data = {
                "timestamp": datetime.now().isoformat(),
                "constitutional_hash": self.constitutional_hash,
                "event_type": "rollback",
                "message": message,
                "severity": severity,
                "environment": "production"
            }
            
            webhook_url = self.rollback_config["notification"]["webhook_url"]
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(webhook_url, json=notification_data) as response:
                    if response.status == 200:
                        self.logger.info(f"Notification sent: {message}")
                        return True
                    else:
                        self.logger.error(f"Failed to send notification: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    async def get_deployment_history(self, service_name: str) -> List[Dict]:
        """Get deployment history for a service"""
        try:
            # Get deployment rollout history
            history_cmd = [
                "kubectl", "rollout", "history", f"deployment/{service_name}",
                "-n", self.rollback_config["namespace"],
                "-o", "json"
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(history_cmd)
            
            if success:
                history_data = json.loads(stdout)
                return history_data.get("items", [])
            else:
                self.logger.error(f"Failed to get deployment history for {service_name}: {stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting deployment history for {service_name}: {e}")
            return []
    
    async def get_previous_stable_version(self, service_name: str) -> Optional[str]:
        """Get previous stable version for rollback"""
        try:
            # Get current deployment
            current_cmd = [
                "kubectl", "get", "deployment", service_name,
                "-n", self.rollback_config["namespace"],
                "-o", "jsonpath='{.metadata.annotations.deployment\\.kubernetes\\.io/revision}'"
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(current_cmd)
            
            if success:
                current_revision = stdout.strip("'")
                
                # Get previous revision
                if current_revision.isdigit():
                    previous_revision = str(int(current_revision) - 1)
                    
                    # Check if previous revision exists
                    check_cmd = [
                        "kubectl", "rollout", "history", f"deployment/{service_name}",
                        "-n", self.rollback_config["namespace"],
                        "--revision", previous_revision
                    ]
                    
                    success, stdout, stderr = await self._execute_kubectl_command(check_cmd)
                    
                    if success:
                        return previous_revision
                    else:
                        self.logger.warning(f"Previous revision {previous_revision} not found for {service_name}")
                        return None
                else:
                    self.logger.error(f"Invalid current revision format: {current_revision}")
                    return None
            else:
                self.logger.error(f"Failed to get current revision for {service_name}: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting previous stable version for {service_name}: {e}")
            return None
    
    async def rollback_service(self, service_name: str, target_revision: Optional[str] = None) -> bool:
        """Rollback a specific service to previous version"""
        try:
            self.logger.info(f"🔄 Rolling back service: {service_name}")
            
            # Get target revision if not provided
            if target_revision is None:
                target_revision = await self.get_previous_stable_version(service_name)
                if target_revision is None:
                    self.logger.error(f"No previous stable version found for {service_name}")
                    return False
            
            # Perform rollback
            if target_revision:
                rollback_cmd = [
                    "kubectl", "rollout", "undo", f"deployment/{service_name}",
                    "-n", self.rollback_config["namespace"],
                    "--to-revision", target_revision
                ]
            else:
                rollback_cmd = [
                    "kubectl", "rollout", "undo", f"deployment/{service_name}",
                    "-n", self.rollback_config["namespace"]
                ]
            
            success, stdout, stderr = await self._execute_kubectl_command(rollback_cmd)
            
            if success:
                self.logger.info(f"Rollback initiated for {service_name}")
                
                # Wait for rollback to complete
                wait_cmd = [
                    "kubectl", "rollout", "status", f"deployment/{service_name}",
                    "-n", self.rollback_config["namespace"],
                    "--timeout", f"{self.rollback_config['rollback_timeout_seconds']}s"
                ]
                
                success, stdout, stderr = await self._execute_kubectl_command(wait_cmd)
                
                if success:
                    self.logger.info(f"✅ Rollback completed for {service_name}")
                    self.rollback_stats["services_rolled_back"] += 1
                    return True
                else:
                    self.logger.error(f"❌ Rollback timeout for {service_name}: {stderr}")
                    self.rollback_stats["services_failed_rollback"] += 1
                    return False
            else:
                self.logger.error(f"❌ Failed to initiate rollback for {service_name}: {stderr}")
                self.rollback_stats["services_failed_rollback"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Error rolling back {service_name}: {e}")
            self.rollback_stats["services_failed_rollback"] += 1
            return False
    
    async def validate_service_health_after_rollback(self, service_name: str, port: int) -> bool:
        """Validate service health after rollback"""
        try:
            self.logger.info(f"🔍 Validating {service_name} health after rollback...")
            
            # Wait for service to be ready
            await asyncio.sleep(10)
            
            # Check service health
            timeout = aiohttp.ClientTimeout(total=self.rollback_config["health_check_timeout"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                health_url = f"http://{service_name}.{self.rollback_config['namespace']}.svc.cluster.local:{port}/health"
                
                async with session.get(
                    health_url,
                    headers={"Constitutional-Hash": self.constitutional_hash}
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Check constitutional compliance
                        if health_data.get("constitutional_hash") == self.constitutional_hash:
                            self.logger.info(f"✅ {service_name} health validated after rollback")
                            return True
                        else:
                            self.logger.error(f"❌ {service_name} constitutional compliance failed after rollback")
                            self.rollback_stats["constitutional_violations"] += 1
                            return False
                    else:
                        self.logger.error(f"❌ {service_name} health check failed after rollback: HTTP {response.status}")
                        self.rollback_stats["health_check_failures"] += 1
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error validating {service_name} health after rollback: {e}")
            self.rollback_stats["health_check_failures"] += 1
            return False
    
    async def perform_emergency_rollback(self, failed_services: List[str] = None) -> Dict[str, bool]:
        """Perform emergency rollback of all or specified services"""
        self.logger.info("🚨 EMERGENCY ROLLBACK INITIATED")
        self.rollback_stats["rollback_start_time"] = datetime.now()
        
        await self._send_notification(
            "EMERGENCY ROLLBACK INITIATED - Rolling back ACGS-2 services to previous stable versions",
            "critical"
        )
        
        results = {}
        
        # Determine services to rollback
        if failed_services:
            services_to_rollback = failed_services
        else:
            services_to_rollback = self.rollback_order
        
        # Service ports for health validation
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
        
        # Rollback services in reverse dependency order
        for service_name in services_to_rollback:
            if service_name in service_ports:
                self.logger.info(f"🔄 Rolling back {service_name}...")
                
                # Perform rollback
                rollback_success = await self.rollback_service(service_name)
                
                if rollback_success:
                    # Validate health after rollback
                    port = service_ports[service_name]
                    health_success = await self.validate_service_health_after_rollback(service_name, port)
                    
                    results[service_name] = health_success
                    
                    if health_success:
                        self.logger.info(f"✅ {service_name} rollback successful and healthy")
                    else:
                        self.logger.error(f"❌ {service_name} rollback completed but health validation failed")
                else:
                    results[service_name] = False
                    self.logger.error(f"❌ {service_name} rollback failed")
                
                # Add delay between rollbacks for stability
                await asyncio.sleep(5)
        
        self.rollback_stats["rollback_end_time"] = datetime.now()
        
        # Generate rollback summary
        successful_rollbacks = sum(1 for success in results.values() if success)
        total_rollbacks = len(results)
        
        self.logger.info("=" * 60)
        self.logger.info("🎯 EMERGENCY ROLLBACK COMPLETED")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Successful rollbacks: {successful_rollbacks}/{total_rollbacks}")
        self.logger.info(f"🏛️ Constitutional violations: {self.rollback_stats['constitutional_violations']}")
        self.logger.info(f"🔍 Health check failures: {self.rollback_stats['health_check_failures']}")
        
        rollback_duration = (
            self.rollback_stats["rollback_end_time"] - 
            self.rollback_stats["rollback_start_time"]
        ).total_seconds()
        
        self.logger.info(f"⏱️ Rollback duration: {rollback_duration:.2f} seconds")
        
        # Send completion notification
        if successful_rollbacks == total_rollbacks:
            await self._send_notification(
                f"EMERGENCY ROLLBACK COMPLETED SUCCESSFULLY - All {total_rollbacks} services rolled back and healthy",
                "info"
            )
        else:
            await self._send_notification(
                f"EMERGENCY ROLLBACK COMPLETED WITH ISSUES - {successful_rollbacks}/{total_rollbacks} services successfully rolled back",
                "warning"
            )
        
        return results
    
    async def perform_targeted_rollback(self, service_name: str, target_revision: Optional[str] = None) -> bool:
        """Perform targeted rollback of a specific service"""
        self.logger.info(f"🎯 TARGETED ROLLBACK: {service_name}")
        
        await self._send_notification(
            f"TARGETED ROLLBACK INITIATED - Rolling back {service_name} to previous stable version",
            "warning"
        )
        
        # Perform rollback
        rollback_success = await self.rollback_service(service_name, target_revision)
        
        if rollback_success:
            # Validate health after rollback
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
            
            if service_name in service_ports:
                port = service_ports[service_name]
                health_success = await self.validate_service_health_after_rollback(service_name, port)
                
                if health_success:
                    self.logger.info(f"✅ {service_name} targeted rollback successful")
                    await self._send_notification(
                        f"TARGETED ROLLBACK COMPLETED - {service_name} rolled back successfully and healthy",
                        "info"
                    )
                    return True
                else:
                    self.logger.error(f"❌ {service_name} targeted rollback completed but health validation failed")
                    await self._send_notification(
                        f"TARGETED ROLLBACK ISSUES - {service_name} rolled back but health validation failed",
                        "warning"
                    )
                    return False
            else:
                self.logger.warning(f"Unknown service port for {service_name}, skipping health validation")
                return True
        else:
            self.logger.error(f"❌ {service_name} targeted rollback failed")
            await self._send_notification(
                f"TARGETED ROLLBACK FAILED - {service_name} rollback failed",
                "critical"
            )
            return False
    
    async def check_rollback_triggers(self) -> List[str]:
        """Check for automatic rollback triggers"""
        triggered_services = []
        
        # This would integrate with the health monitoring system
        # For now, return empty list as placeholder
        return triggered_services

async def main():
    """Main rollback execution function"""
    if len(sys.argv) < 2:
        print("Usage: python3 production_rollback.py <emergency|targeted> [service_name] [revision]")
        sys.exit(1)
    
    rollback_type = sys.argv[1]
    
    try:
        rollback_system = ACGSProductionRollback()
        
        if rollback_type == "emergency":
            # Emergency rollback of all services
            results = await rollback_system.perform_emergency_rollback()
            
            if all(results.values()):
                print("🎉 Emergency rollback completed successfully!")
                sys.exit(0)
            else:
                print("❌ Emergency rollback completed with issues")
                sys.exit(1)
                
        elif rollback_type == "targeted":
            if len(sys.argv) < 3:
                print("Usage: python3 production_rollback.py targeted <service_name> [revision]")
                sys.exit(1)
            
            service_name = sys.argv[2]
            target_revision = sys.argv[3] if len(sys.argv) > 3 else None
            
            # Targeted rollback of specific service
            success = await rollback_system.perform_targeted_rollback(service_name, target_revision)
            
            if success:
                print(f"🎉 Targeted rollback of {service_name} completed successfully!")
                sys.exit(0)
            else:
                print(f"❌ Targeted rollback of {service_name} failed")
                sys.exit(1)
        else:
            print("Invalid rollback type. Use 'emergency' or 'targeted'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error in rollback system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())