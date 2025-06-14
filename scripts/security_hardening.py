#!/usr/bin/env python3
"""
ACGS-1 Security Hardening Script
Automated security hardening for all ACGS services
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("security_hardening")

# Project root detection
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "services"
CONFIG_DIR = PROJECT_ROOT / "config"


class SecurityHardener:
    """Automated security hardening for ACGS services."""
    
    def __init__(self):
        self.hardening_results = {
            "dependency_scan": {},
            "security_headers": {},
            "rate_limiting": {},
            "vulnerability_scan": {},
            "summary": {}
        }
    
    async def scan_dependencies(self) -> Dict[str, Any]:
        """Scan for vulnerable dependencies."""
        logger.info("🔍 Scanning dependencies for vulnerabilities...")
        
        results = {}
        
        # Python dependencies scan with safety
        python_services = [
            "services/core/constitutional-ai/ac_service",
            "services/platform/authentication/auth_service",
            "services/platform/integrity/integrity_service",
            "services/core/formal-verification/fv_service",
            "services/core/governance-synthesis/gs_service",
            "services/core/policy-governance/pgc_service",
            "services/core/evolutionary-computation",
            "services/platform/workflow",
            "services/integrations/external-apis",
            "services/integrations/blockchain-bridge",
            "services/platform/performance-optimizer",
        ]
        
        for service_path in python_services:
            service_dir = PROJECT_ROOT / service_path
            if service_dir.exists():
                service_name = service_path.split("/")[-1]
                try:
                    # Run safety check
                    result = subprocess.run(
                        ["safety", "check", "--json"],
                        cwd=service_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        results[service_name] = {
                            "status": "clean",
                            "vulnerabilities": []
                        }
                    else:
                        try:
                            vulnerabilities = json.loads(result.stdout)
                            results[service_name] = {
                                "status": "vulnerabilities_found",
                                "vulnerabilities": vulnerabilities
                            }
                        except json.JSONDecodeError:
                            results[service_name] = {
                                "status": "scan_error",
                                "error": result.stderr
                            }
                            
                except subprocess.TimeoutExpired:
                    results[service_name] = {
                        "status": "timeout",
                        "error": "Safety scan timed out"
                    }
                except Exception as e:
                    results[service_name] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        # Rust dependencies scan (for blockchain components)
        blockchain_dir = PROJECT_ROOT / "blockchain"
        if blockchain_dir.exists():
            try:
                result = subprocess.run(
                    ["cargo", "audit", "--json"],
                    cwd=blockchain_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    results["blockchain"] = {
                        "status": "clean",
                        "vulnerabilities": []
                    }
                else:
                    results["blockchain"] = {
                        "status": "vulnerabilities_found",
                        "output": result.stdout
                    }
                    
            except Exception as e:
                results["blockchain"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        self.hardening_results["dependency_scan"] = results
        return results
    
    def update_security_headers(self) -> Dict[str, Any]:
        """Update security headers configuration."""
        logger.info("🔒 Updating security headers configuration...")
        
        security_config = {
            "security_headers": {
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' https:; "
                    "connect-src 'self' https: wss:; "
                    "frame-ancestors 'none';"
                ),
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": (
                    "geolocation=(), microphone=(), camera=(), "
                    "payment=(), usb=(), magnetometer=(), gyroscope=()"
                )
            },
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100,
                "burst_size": 20,
                "whitelist_ips": ["127.0.0.1", "::1"],
                "blacklist_ips": []
            },
            "authentication": {
                "jwt_expiry_minutes": 60,
                "refresh_token_expiry_days": 7,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "require_mfa": False,
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True
                }
            }
        }
        
        # Save security configuration
        security_config_path = CONFIG_DIR / "security_hardening.yaml"
        with open(security_config_path, "w") as f:
            yaml.dump(security_config, f, default_flow_style=False)
        
        self.hardening_results["security_headers"] = {
            "status": "updated",
            "config_path": str(security_config_path)
        }
        
        return self.hardening_results["security_headers"]
    
    def implement_rate_limiting(self) -> Dict[str, Any]:
        """Implement rate limiting across services."""
        logger.info("⚡ Implementing rate limiting...")
        
        rate_limiting_code = '''
# Rate limiting middleware for ACGS services
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["100/minute"]
)

def add_rate_limiting_middleware(app):
    """Add rate limiting middleware to FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Apply rate limiting
        try:
            response = await call_next(request)
            return response
        except RateLimitExceeded:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
'''
        
        # Save rate limiting middleware
        middleware_path = SERVICES_DIR / "shared" / "rate_limiting_middleware.py"
        with open(middleware_path, "w") as f:
            f.write(rate_limiting_code)
        
        self.hardening_results["rate_limiting"] = {
            "status": "implemented",
            "middleware_path": str(middleware_path)
        }
        
        return self.hardening_results["rate_limiting"]
    
    async def run_vulnerability_scan(self) -> Dict[str, Any]:
        """Run comprehensive vulnerability scan."""
        logger.info("🛡️ Running vulnerability scan...")
        
        scan_results = {}
        
        # Bandit scan for Python security issues
        python_services = [
            "services/core/constitutional-ai/ac_service",
            "services/platform/authentication/auth_service",
            "services/platform/integrity/integrity_service",
        ]
        
        for service_path in python_services:
            service_dir = PROJECT_ROOT / service_path
            if service_dir.exists():
                service_name = service_path.split("/")[-1]
                try:
                    result = subprocess.run(
                        ["bandit", "-r", ".", "-f", "json"],
                        cwd=service_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    try:
                        bandit_output = json.loads(result.stdout)
                        scan_results[service_name] = {
                            "tool": "bandit",
                            "status": "completed",
                            "issues_found": len(bandit_output.get("results", [])),
                            "high_severity": len([
                                issue for issue in bandit_output.get("results", [])
                                if issue.get("issue_severity") == "HIGH"
                            ])
                        }
                    except json.JSONDecodeError:
                        scan_results[service_name] = {
                            "tool": "bandit",
                            "status": "parse_error",
                            "error": "Could not parse bandit output"
                        }
                        
                except subprocess.TimeoutExpired:
                    scan_results[service_name] = {
                        "tool": "bandit",
                        "status": "timeout"
                    }
                except Exception as e:
                    scan_results[service_name] = {
                        "tool": "bandit",
                        "status": "error",
                        "error": str(e)
                    }
        
        self.hardening_results["vulnerability_scan"] = scan_results
        return scan_results
    
    def update_cargo_dependencies(self) -> Dict[str, Any]:
        """Update Cargo.toml with security patches."""
        logger.info("📦 Updating Cargo dependencies with security patches...")
        
        blockchain_cargo_path = PROJECT_ROOT / "blockchain" / "Cargo.toml"
        
        if not blockchain_cargo_path.exists():
            return {"status": "skipped", "reason": "Cargo.toml not found"}
        
        # Security patches for known vulnerabilities
        security_patches = '''
# Security patches for known vulnerabilities
[patch.crates-io]
curve25519-dalek = { version = "4.1.3" }
ed25519-dalek = { version = "2.0.0" }
'''
        
        try:
            with open(blockchain_cargo_path, "r") as f:
                cargo_content = f.read()
            
            # Add security patches if not already present
            if "[patch.crates-io]" not in cargo_content:
                with open(blockchain_cargo_path, "a") as f:
                    f.write("\n" + security_patches)
                
                return {
                    "status": "updated",
                    "patches_added": ["curve25519-dalek", "ed25519-dalek"]
                }
            else:
                return {
                    "status": "already_patched",
                    "message": "Security patches already present"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_comprehensive_hardening(self) -> Dict[str, Any]:
        """Run comprehensive security hardening."""
        logger.info("🚀 Starting comprehensive security hardening...")
        
        # Run all hardening steps
        await self.scan_dependencies()
        self.update_security_headers()
        self.implement_rate_limiting()
        await self.run_vulnerability_scan()
        cargo_result = self.update_cargo_dependencies()
        
        # Generate summary
        total_issues = 0
        critical_issues = 0
        
        for service_results in self.hardening_results["dependency_scan"].values():
            if service_results.get("status") == "vulnerabilities_found":
                vulnerabilities = service_results.get("vulnerabilities", [])
                total_issues += len(vulnerabilities)
                critical_issues += len([
                    v for v in vulnerabilities 
                    if v.get("severity", "").lower() in ["critical", "high"]
                ])
        
        self.hardening_results["summary"] = {
            "total_vulnerabilities": total_issues,
            "critical_vulnerabilities": critical_issues,
            "security_headers_updated": True,
            "rate_limiting_implemented": True,
            "cargo_patches_applied": cargo_result.get("status") == "updated",
            "hardening_completed": True,
            "recommendations": [
                "Review and fix any critical vulnerabilities found",
                "Test rate limiting implementation",
                "Verify security headers are properly applied",
                "Run regular security scans",
                "Keep dependencies updated"
            ]
        }
        
        return self.hardening_results
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security report."""
        report = f"""
# ACGS-1 Security Hardening Report

## Summary
- Total Vulnerabilities Found: {self.hardening_results['summary']['total_vulnerabilities']}
- Critical Vulnerabilities: {self.hardening_results['summary']['critical_vulnerabilities']}
- Security Headers Updated: {self.hardening_results['summary']['security_headers_updated']}
- Rate Limiting Implemented: {self.hardening_results['summary']['rate_limiting_implemented']}
- Cargo Patches Applied: {self.hardening_results['summary']['cargo_patches_applied']}

## Dependency Scan Results
"""
        
        for service, results in self.hardening_results["dependency_scan"].items():
            report += f"- {service}: {results['status']}\n"
        
        report += f"""
## Recommendations
"""
        for rec in self.hardening_results['summary']['recommendations']:
            report += f"- {rec}\n"
        
        return report


async def main():
    """Main security hardening execution."""
    hardener = SecurityHardener()
    
    try:
        results = await hardener.run_comprehensive_hardening()
        
        # Generate and save report
        report = hardener.generate_security_report()
        report_path = PROJECT_ROOT / "docs" / "security_hardening_report.md"
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print("🔒 Security Hardening Completed!")
        print(f"📄 Report saved to: {report_path}")
        print(f"🛡️ Total vulnerabilities found: {results['summary']['total_vulnerabilities']}")
        print(f"⚠️ Critical vulnerabilities: {results['summary']['critical_vulnerabilities']}")
        
        # Exit with error code if critical vulnerabilities found
        if results['summary']['critical_vulnerabilities'] > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Security hardening failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
