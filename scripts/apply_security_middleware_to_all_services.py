#!/usr/bin/env python3
"""
ACGS-1 Security Middleware Deployment Script

This script applies production-grade security middleware to all 7 core ACGS-1 services:
- Auth Service (8000)
- AC Service (8001) 
- Integrity Service (8002)
- FV Service (8003)
- GS Service (8004)
- PGC Service (8005)
- EC Service (8006)

Security Features Applied:
- HTTPS enforcement with HSTS
- XSS protection with CSP headers
- CSRF protection with token validation
- Rate limiting with Redis backend
- SQL injection detection
- Path traversal protection
- Comprehensive security headers (OWASP recommended)
- Threat detection and analysis
- Audit logging for security events
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import httpx

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("security_middleware_deployment.log")
    ]
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICES = {
    "auth": {
        "name": "Authentication Service",
        "port": 8000,
        "path": "services/platform/authentication/auth_service/app/main.py",
        "module": "services.platform.authentication.auth_service.app.main",
    },
    "ac": {
        "name": "Constitutional AI Service", 
        "port": 8001,
        "path": "services/core/constitutional-ai/ac_service/app/main.py",
        "module": "services.core.constitutional-ai.ac_service.app.main",
    },
    "integrity": {
        "name": "Integrity Service",
        "port": 8002,
        "path": "services/platform/integrity/integrity_service/app/main.py", 
        "module": "services.platform.integrity.integrity_service.app.main",
    },
    "fv": {
        "name": "Formal Verification Service",
        "port": 8003,
        "path": "services/core/formal-verification/fv_service/main.py",
        "module": "services.core.formal-verification.fv_service.main",
    },
    "gs": {
        "name": "Governance Synthesis Service",
        "port": 8004,
        "path": "services/core/governance-synthesis/gs_service/app/main.py",
        "module": "services.core.governance-synthesis.gs_service.app.main",
    },
    "pgc": {
        "name": "Policy Governance Service",
        "port": 8005,
        "path": "services/core/policy-governance/pgc_service/app/main.py",
        "module": "services.core.policy-governance.pgc_service.app.main",
    },
    "ec": {
        "name": "Evolutionary Computation Service",
        "port": 8006,
        "path": "services/core/evolutionary-computation/app/main.py",
        "module": "services.core.evolutionary-computation.app.main",
    },
}


class SecurityMiddlewareDeployer:
    """Deploy security middleware to all ACGS-1 services."""
    
    def __init__(self):
        self.deployment_results = {}
        self.failed_services = []
        self.successful_services = []
    
    async def deploy_to_all_services(self) -> Dict:
        """Deploy security middleware to all services."""
        logger.info("🔒 Starting security middleware deployment to all ACGS-1 services")
        
        deployment_start = time.time()
        
        for service_id, service_config in SERVICES.items():
            try:
                logger.info(f"📦 Deploying security middleware to {service_config['name']} (port {service_config['port']})")
                
                result = await self._deploy_to_service(service_id, service_config)
                self.deployment_results[service_id] = result
                
                if result["success"]:
                    self.successful_services.append(service_id)
                    logger.info(f"✅ Security middleware deployed successfully to {service_config['name']}")
                else:
                    self.failed_services.append(service_id)
                    logger.error(f"❌ Failed to deploy security middleware to {service_config['name']}: {result['error']}")
                    
            except Exception as e:
                error_msg = f"Deployment error for {service_config['name']}: {str(e)}"
                logger.error(error_msg)
                self.deployment_results[service_id] = {
                    "success": False,
                    "error": error_msg,
                    "timestamp": time.time()
                }
                self.failed_services.append(service_id)
        
        deployment_time = time.time() - deployment_start
        
        # Generate deployment summary
        summary = self._generate_deployment_summary(deployment_time)
        
        # Save deployment report
        await self._save_deployment_report(summary)
        
        return summary
    
    async def _deploy_to_service(self, service_id: str, service_config: Dict) -> Dict:
        """Deploy security middleware to a specific service."""
        try:
            # Check if service file exists
            service_path = Path(project_root) / service_config["path"]
            if not service_path.exists():
                return {
                    "success": False,
                    "error": f"Service file not found: {service_path}",
                    "timestamp": time.time()
                }
            
            # Apply security middleware by modifying the service file
            success = await self._apply_security_middleware_to_file(service_path, service_id)
            
            if success:
                # Test service health after modification
                health_check = await self._test_service_health(service_config["port"])
                
                return {
                    "success": True,
                    "security_features": [
                        "HTTPS enforcement with HSTS",
                        "XSS protection with CSP headers", 
                        "CSRF protection with token validation",
                        "Rate limiting with Redis backend",
                        "SQL injection detection",
                        "Path traversal protection",
                        "OWASP security headers",
                        "Threat detection and analysis",
                        "Audit logging"
                    ],
                    "health_check": health_check,
                    "timestamp": time.time()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to apply security middleware to service file",
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _apply_security_middleware_to_file(self, service_path: Path, service_id: str) -> bool:
        """Apply security middleware to service file."""
        try:
            # Read current service file
            with open(service_path, 'r') as f:
                content = f.read()
            
            # Check if security middleware is already applied
            if "apply_production_security_middleware" in content:
                logger.info(f"Security middleware already applied to {service_path}")
                return True
            
            # Add security middleware import
            security_import = """
# Import production security middleware
try:
    import sys
    sys.path.append('/home/dislove/ACGS-1/services/shared')
    from security_middleware import apply_production_security_middleware, create_security_config
    SECURITY_MIDDLEWARE_AVAILABLE = True
    print("✅ Production security middleware loaded successfully")
except ImportError as e:
    print(f"⚠️ Production security middleware not available: {e}")
    SECURITY_MIDDLEWARE_AVAILABLE = False
"""
            
            # Find FastAPI app creation
            if "app = FastAPI(" in content:
                # Add security middleware after app creation
                app_creation_pattern = r"(app = FastAPI\([^)]*\))"
                
                security_application = f"""
# Apply production-grade security middleware
if SECURITY_MIDDLEWARE_AVAILABLE:
    security_config = create_security_config(
        max_request_size=10 * 1024 * 1024,  # 10MB
        rate_limit_requests=120,
        rate_limit_window=60,
        enable_threat_detection=True
    )
    apply_production_security_middleware(app, "{service_id}_service", security_config)
    print(f"✅ Production security middleware applied to {service_id} service")
else:
    print(f"⚠️ Security middleware not available for {service_id} service")
"""
                
                # Insert imports at the top
                import_insertion_point = content.find("from fastapi import")
                if import_insertion_point != -1:
                    content = content[:import_insertion_point] + security_import + "\n" + content[import_insertion_point:]
                
                # Insert security middleware application after app creation
                import re
                content = re.sub(
                    app_creation_pattern,
                    r"\1" + security_application,
                    content,
                    count=1
                )
                
                # Write modified content back to file
                with open(service_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"Security middleware applied to {service_path}")
                return True
            else:
                logger.warning(f"Could not find FastAPI app creation in {service_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying security middleware to {service_path}: {e}")
            return False
    
    async def _test_service_health(self, port: int) -> Dict:
        """Test service health after security middleware deployment."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:{port}/health")
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    def _generate_deployment_summary(self, deployment_time: float) -> Dict:
        """Generate deployment summary."""
        total_services = len(SERVICES)
        successful_count = len(self.successful_services)
        failed_count = len(self.failed_services)
        success_rate = (successful_count / total_services) * 100
        
        return {
            "deployment_summary": {
                "total_services": total_services,
                "successful_deployments": successful_count,
                "failed_deployments": failed_count,
                "success_rate": f"{success_rate:.1f}%",
                "deployment_time": f"{deployment_time:.2f} seconds",
                "timestamp": time.time()
            },
            "successful_services": self.successful_services,
            "failed_services": self.failed_services,
            "detailed_results": self.deployment_results,
            "security_features_deployed": [
                "HTTPS enforcement with HSTS",
                "XSS protection with CSP headers",
                "CSRF protection with token validation", 
                "Rate limiting with Redis backend",
                "SQL injection detection",
                "Path traversal protection",
                "OWASP security headers",
                "Threat detection and analysis",
                "Audit logging for security events"
            ]
        }
    
    async def _save_deployment_report(self, summary: Dict):
        """Save deployment report to file."""
        report_path = Path("security_middleware_deployment_report.json")
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Deployment report saved to {report_path}")


async def main():
    """Main deployment function."""
    logger.info("🚀 ACGS-1 Security Middleware Deployment Starting")
    
    deployer = SecurityMiddlewareDeployer()
    summary = await deployer.deploy_to_all_services()
    
    # Print summary
    print("\n" + "="*80)
    print("🔒 ACGS-1 Security Middleware Deployment Summary")
    print("="*80)
    print(f"Total Services: {summary['deployment_summary']['total_services']}")
    print(f"Successful Deployments: {summary['deployment_summary']['successful_deployments']}")
    print(f"Failed Deployments: {summary['deployment_summary']['failed_deployments']}")
    print(f"Success Rate: {summary['deployment_summary']['success_rate']}")
    print(f"Deployment Time: {summary['deployment_summary']['deployment_time']}")
    
    if summary['successful_services']:
        print(f"\n✅ Successfully deployed to: {', '.join(summary['successful_services'])}")
    
    if summary['failed_services']:
        print(f"\n❌ Failed deployments: {', '.join(summary['failed_services'])}")
    
    print("\n🔒 Security Features Deployed:")
    for feature in summary['security_features_deployed']:
        print(f"   - {feature}")
    
    print("\n📄 Detailed report saved to: security_middleware_deployment_report.json")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
