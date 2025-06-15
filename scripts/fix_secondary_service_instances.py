#!/usr/bin/env python3
"""
ACGS-1 Secondary Service Instance Health Fix
Addresses health check failures for backup service instances
"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecondaryServiceManager:
    """Manages secondary service instances and health checks"""
    
    def __init__(self):
        self.services = {
            "pgc_service_2": {"port": 8005, "backup_port": 8015},
            "integrity_service_2": {"port": 8002, "backup_port": 8012},
            "fv_service_1": {"port": 8003, "backup_port": 8013},
            "gs_service_2": {"port": 8004, "backup_port": 8014},
            "auth_service_2": {"port": 8000, "backup_port": 8010},
            "ac_service_2": {"port": 8001, "backup_port": 8011},
            "ec_service_2": {"port": 8006, "backup_port": 8016}
        }
        
    async def fix_secondary_instances(self):
        """Fix all secondary service instance health issues"""
        logger.info("🔧 Starting secondary service instance fixes...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "services_fixed": [],
            "services_failed": [],
            "overall_success": False
        }
        
        for service_name, config in self.services.items():
            try:
                success = await self.fix_service_instance(service_name, config)
                if success:
                    results["services_fixed"].append(service_name)
                else:
                    results["services_failed"].append(service_name)
            except Exception as e:
                logger.error(f"❌ Failed to fix {service_name}: {e}")
                results["services_failed"].append(service_name)
        
        results["overall_success"] = len(results["services_failed"]) == 0
        
        # Save results
        with open("secondary_instances_fix_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    async def fix_service_instance(self, service_name, config):
        """Fix individual service instance"""
        logger.info(f"🔄 Fixing {service_name}...")
        
        # Step 1: Check if primary service is healthy
        primary_healthy = await self.check_service_health("localhost", config["port"])
        
        if not primary_healthy:
            logger.warning(f"⚠️ Primary service for {service_name} is unhealthy")
            return False
        
        # Step 2: Start secondary instance on backup port
        success = await self.start_secondary_instance(service_name, config)
        
        if success:
            # Step 3: Validate health
            await asyncio.sleep(5)
            secondary_healthy = await self.check_service_health("localhost", config["backup_port"])
            
            if secondary_healthy:
                logger.info(f"✅ {service_name} secondary instance healthy")
                return True
            else:
                logger.error(f"❌ {service_name} secondary instance unhealthy")
                return False
        
        return False
    
    async def start_secondary_instance(self, service_name, config):
        """Start secondary service instance"""
        try:
            # Map service names to module paths
            service_modules = {
                "pgc_service_2": "services.core.policy-governance-control.pgc_service.app.main:app",
                "integrity_service_2": "services.core.integrity.integrity_service.app.main:app",
                "fv_service_1": "services.core.formal-verification.fv_service.app.main:app",
                "gs_service_2": "services.core.governance-synthesis.gs_service.app.main:app",
                "auth_service_2": "services.core.auth.auth_service.app.main:app",
                "ac_service_2": "services.core.constitutional-ai.ac_service.app.main:app",
                "ec_service_2": "services.core.evolutionary-computation.app.main:app"
            }
            
            module_path = service_modules.get(service_name)
            if not module_path:
                logger.error(f"❌ Unknown service: {service_name}")
                return False
            
            # Kill existing secondary instance
            subprocess.run([
                "pkill", "-f", f":{config['backup_port']}"
            ], check=False)
            
            await asyncio.sleep(2)
            
            # Start secondary instance
            cmd = [
                "python", "-m", "uvicorn",
                module_path,
                "--host", "0.0.0.0",
                "--port", str(config["backup_port"]),
                "--reload"
            ]
            
            # Set environment variables for secondary instance
            env = {
                "SECONDARY_INSTANCE": "true",
                "PRIMARY_PORT": str(config["port"]),
                "BACKUP_PORT": str(config["backup_port"]),
                "SERVICE_NAME": service_name
            }
            
            subprocess.Popen(cmd, cwd="/home/dislove/ACGS-1", env={**subprocess.os.environ, **env})
            
            logger.info(f"✅ Started {service_name} on port {config['backup_port']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False
    
    async def check_service_health(self, host, port):
        """Check service health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{host}:{port}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def update_load_balancer_config(self):
        """Update load balancer configuration for secondary instances"""
        logger.info("🔄 Updating load balancer configuration...")
        
        # This would update HAProxy configuration to use backup ports
        # For now, we'll create a configuration snippet
        config_snippet = """
# Updated backend configurations with secondary instances
# Add these to haproxy.cfg

# Auth Service Backend with secondary instance
backend auth_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    hash-type consistent
    server auth1 auth_service:8000 check inter 5s fall 2 rise 3 weight 100
    server auth2 localhost:8010 check inter 5s fall 2 rise 3 weight 100 backup
    timeout server 30s
    retries 3

# Similar configurations for other services...
"""
        
        with open("haproxy_secondary_instances.cfg", "w") as f:
            f.write(config_snippet)
        
        logger.info("✅ Load balancer configuration snippet created")

async def main():
    """Main execution function"""
    manager = SecondaryServiceManager()
    results = await manager.fix_secondary_instances()
    
<<<<<<< HEAD
    print("\\n" + "="*60)
=======
    print("\n" + "="*60)
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
    print("🔧 SECONDARY SERVICE INSTANCES FIX RESULTS")
    print("="*60)
    print(f"Services Fixed: {len(results['services_fixed'])}")
    print(f"Services Failed: {len(results['services_failed'])}")
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    
    if results['services_fixed']:
<<<<<<< HEAD
        print("\\n✅ Successfully Fixed:")
=======
        print("\n✅ Successfully Fixed:")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        for service in results['services_fixed']:
            print(f"  - {service}")
    
    if results['services_failed']:
<<<<<<< HEAD
        print("\\n❌ Failed to Fix:")
=======
        print("\n❌ Failed to Fix:")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        for service in results['services_failed']:
            print(f"  - {service}")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
