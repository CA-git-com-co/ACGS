#!/usr/bin/env python3
"""
ACGS-1 OPA DNS Resolution Fix
Addresses PGC service OPA dependency failures
"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OPADNSResolver:
    """Resolves OPA DNS issues and validates PGC service health"""
    
    def __init__(self):
        self.opa_endpoints = [
            "http://localhost:8181",
            "http://opa:8181",
            "http://127.0.0.1:8181"
        ]
        self.pgc_endpoint = "http://localhost:8005"
        
    async def fix_opa_dns_resolution(self):
        """Fix OPA DNS resolution issues"""
        logger.info("🔧 Starting OPA DNS resolution fix...")
        
        # Step 1: Check current OPA status
        opa_status = await self.check_opa_connectivity()
        
        if not opa_status["accessible"]:
            # Step 2: Restart OPA service
            await self.restart_opa_service()
            
            # Step 3: Update DNS resolution
            await self.update_dns_resolution()
            
            # Step 4: Verify connectivity
            await asyncio.sleep(5)
            opa_status = await self.check_opa_connectivity()
        
        # Step 5: Restart PGC service if OPA is healthy
        if opa_status["accessible"]:
            await self.restart_pgc_service()
            
        return await self.validate_fix()
    
    async def check_opa_connectivity(self):
        """Check OPA service connectivity"""
        logger.info("🔍 Checking OPA connectivity...")
        
        async with aiohttp.ClientSession() as session:
            for endpoint in self.opa_endpoints:
                try:
                    async with session.get(f"{endpoint}/health", timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"✅ OPA accessible at {endpoint}")
                            return {"accessible": True, "endpoint": endpoint}
                except Exception as e:
                    logger.warning(f"❌ OPA not accessible at {endpoint}: {e}")
        
        return {"accessible": False, "endpoint": None}
    
    async def restart_opa_service(self):
        """Restart OPA service"""
        logger.info("🔄 Restarting OPA service...")
        
        try:
            # Stop existing OPA processes
            subprocess.run(["pkill", "-f", "opa"], check=False)
            await asyncio.sleep(2)
            
            # Start OPA service
            opa_cmd = [
                "opa", "run", "--server",
                "--addr", "0.0.0.0:8181",
                "--config-file", "config/opa/config.yaml"
            ]
            
            subprocess.Popen(opa_cmd, cwd="/home/dislove/ACGS-1")
            await asyncio.sleep(5)
            
            logger.info("✅ OPA service restarted")
            
        except Exception as e:
            logger.error(f"❌ Failed to restart OPA: {e}")
    
    async def update_dns_resolution(self):
        """Update DNS resolution for OPA service"""
        logger.info("🌐 Updating DNS resolution...")
        
        try:
            # Add localhost entry for OPA
<<<<<<< HEAD
            hosts_entry = "127.0.0.1 opa\\n"
=======
            hosts_entry = "127.0.0.1 opa\n"
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
            
            # Check if entry already exists
            with open("/etc/hosts", "r") as f:
                hosts_content = f.read()
            
            if "127.0.0.1 opa" not in hosts_content:
                # Add entry (requires sudo)
                subprocess.run([
                    "sudo", "sh", "-c", 
                    f"echo '{hosts_entry.strip()}' >> /etc/hosts"
                ], check=True)
                
                logger.info("✅ DNS resolution updated")
            else:
                logger.info("✅ DNS resolution already configured")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not update /etc/hosts: {e}")
            logger.info("💡 Manual DNS resolution may be needed")
    
    async def restart_pgc_service(self):
        """Restart PGC service to reconnect to OPA"""
        logger.info("🔄 Restarting PGC service...")
        
        try:
            # Stop PGC service
            subprocess.run(["pkill", "-f", "pgc_service"], check=False)
            await asyncio.sleep(2)
            
            # Start PGC service
            pgc_cmd = [
                "python", "-m", "uvicorn",
                "services.core.policy-governance-control.pgc_service.app.main:app",
                "--host", "0.0.0.0",
                "--port", "8005",
                "--reload"
            ]
            
            subprocess.Popen(pgc_cmd, cwd="/home/dislove/ACGS-1")
            await asyncio.sleep(5)
            
            logger.info("✅ PGC service restarted")
            
        except Exception as e:
            logger.error(f"❌ Failed to restart PGC service: {e}")
    
    async def validate_fix(self):
        """Validate that the fix was successful"""
        logger.info("✅ Validating OPA DNS fix...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "opa_connectivity": False,
            "pgc_health": False,
            "fix_successful": False
        }
        
        # Check OPA connectivity
        opa_status = await self.check_opa_connectivity()
        results["opa_connectivity"] = opa_status["accessible"]
        
        # Check PGC health
        if opa_status["accessible"]:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.pgc_endpoint}/health", timeout=10) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            results["pgc_health"] = health_data.get("status") == "healthy"
                except Exception as e:
                    logger.error(f"❌ PGC health check failed: {e}")
        
        results["fix_successful"] = results["opa_connectivity"] and results["pgc_health"]
        
        # Save results
        with open("opa_dns_fix_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        if results["fix_successful"]:
            logger.info("🎉 OPA DNS fix successful!")
        else:
            logger.error("❌ OPA DNS fix failed - manual intervention required")
        
        return results

async def main():
    """Main execution function"""
    resolver = OPADNSResolver()
    results = await resolver.fix_opa_dns_resolution()
    
<<<<<<< HEAD
    print("\\n" + "="*60)
=======
    print("\n" + "="*60)
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
    print("🔧 OPA DNS RESOLUTION FIX RESULTS")
    print("="*60)
    print(f"OPA Connectivity: {'✅' if results['opa_connectivity'] else '❌'}")
    print(f"PGC Health: {'✅' if results['pgc_health'] else '❌'}")
    print(f"Fix Successful: {'✅' if results['fix_successful'] else '❌'}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
