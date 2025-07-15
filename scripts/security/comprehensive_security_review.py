#!/usr/bin/env python3
"""
Comprehensive Security Review for 5-Tier Hybrid Inference Router

Conducts final security review to ensure all security requirements are met
before production deployment.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityRequirements:
    """Security requirements for production deployment."""
    
    # API Security
    api_authentication_required: bool = True
    api_rate_limiting_enabled: bool = True
    api_input_validation: bool = True
    
    # Infrastructure Security
    https_only: bool = True
    secure_headers_enabled: bool = True
    cors_properly_configured: bool = True
    
    # Data Security
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    secure_key_management: bool = True
    
    # Constitutional Compliance
    constitutional_hash_validation: bool = True
    compliance_monitoring: bool = True
    audit_logging: bool = True
    
    # Network Security
    firewall_configured: bool = True
    network_segmentation: bool = True
    intrusion_detection: bool = True
    
    # Container Security
    container_scanning: bool = True
    minimal_base_images: bool = True
    non_root_execution: bool = True
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class SecurityFindings:
    """Security review findings."""
    
    critical_issues: List[str] = field(default_factory=list)
    high_issues: List[str] = field(default_factory=list)
    medium_issues: List[str] = field(default_factory=list)
    low_issues: List[str] = field(default_factory=list)
    
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    
    overall_score: float = 0.0
    production_ready: bool = False
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ComprehensiveSecurityReviewer:
    """Conducts comprehensive security review."""
    
    def __init__(self, router_url: str = "http://localhost:8020"):
        self.router_url = router_url
        self.requirements = SecurityRequirements()
        self.findings = SecurityFindings()
        
    async def conduct_security_review(self) -> SecurityFindings:
        """Conduct comprehensive security review."""
        logger.info("🔒 Starting Comprehensive Security Review")
        logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        try:
            # API Security Review
            await self._review_api_security()
            
            # Infrastructure Security Review
            await self._review_infrastructure_security()
            
            # Data Security Review
            await self._review_data_security()
            
            # Constitutional Compliance Review
            await self._review_constitutional_compliance()
            
            # Network Security Review
            await self._review_network_security()
            
            # Container Security Review
            await self._review_container_security()
            
            # Generate overall assessment
            self._generate_overall_assessment()
            
            logger.info("✅ Security review completed")
            return self.findings
            
        except Exception as e:
            logger.error(f"❌ Security review failed: {e}")
            raise
    
    async def _review_api_security(self):
        """Review API security configurations."""
        logger.info("🔐 Reviewing API security...")
        
        # Test authentication requirements
        try:
            async with aiohttp.ClientSession() as session:
                # Test unauthenticated access
                async with session.get(f"{self.router_url}/models") as response:
                    if response.status == 200:
                        # Check if authentication is properly implemented
                        headers = response.headers
                        if 'X-API-Key' not in headers and 'Authorization' not in headers:
                            self.findings.medium_issues.append("API endpoints may not require authentication")
                        else:
                            self.findings.passed_checks.append("API authentication configured")
                    else:
                        self.findings.passed_checks.append("API properly restricts unauthenticated access")
        except Exception as e:
            self.findings.high_issues.append(f"API security test failed: {e}")
        
        # Test rate limiting
        try:
            async with aiohttp.ClientSession() as session:
                # Send multiple rapid requests
                tasks = []
                for _ in range(20):
                    tasks.append(session.get(f"{self.router_url}/health"))
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                rate_limited = any(
                    hasattr(r, 'status') and r.status == 429 
                    for r in responses if not isinstance(r, Exception)
                )
                
                if rate_limited:
                    self.findings.passed_checks.append("Rate limiting is active")
                else:
                    self.findings.medium_issues.append("Rate limiting may not be configured")
                    
        except Exception as e:
            self.findings.medium_issues.append(f"Rate limiting test failed: {e}")
        
        # Test input validation
        try:
            async with aiohttp.ClientSession() as session:
                # Test malicious input
                malicious_payloads = [
                    {"query": "<script>alert('xss')</script>"},
                    {"query": "'; DROP TABLE users; --"},
                    {"query": "../../../etc/passwd"}
                ]
                
                for payload in malicious_payloads:
                    async with session.post(
                        f"{self.router_url}/route",
                        json=payload
                    ) as response:
                        if response.status in [400, 422]:  # Proper validation
                            self.findings.passed_checks.append("Input validation working")
                            break
                else:
                    self.findings.high_issues.append("Input validation may be insufficient")
                    
        except Exception as e:
            self.findings.medium_issues.append(f"Input validation test failed: {e}")
    
    async def _review_infrastructure_security(self):
        """Review infrastructure security."""
        logger.info("🏗️ Reviewing infrastructure security...")
        
        # Check HTTPS configuration
        if self.router_url.startswith("https://"):
            self.findings.passed_checks.append("HTTPS configured")
        else:
            self.findings.high_issues.append("HTTPS not configured for production")
        
        # Test security headers
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.router_url}/health") as response:
                    headers = response.headers
                    
                    security_headers = [
                        'X-Content-Type-Options',
                        'X-Frame-Options',
                        'X-XSS-Protection',
                        'Strict-Transport-Security',
                        'Content-Security-Policy'
                    ]
                    
                    missing_headers = [h for h in security_headers if h not in headers]
                    
                    if missing_headers:
                        self.findings.medium_issues.append(f"Missing security headers: {missing_headers}")
                    else:
                        self.findings.passed_checks.append("Security headers configured")
                        
        except Exception as e:
            self.findings.medium_issues.append(f"Security headers test failed: {e}")
        
        # Check CORS configuration
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Origin': 'https://malicious-site.com'}
                async with session.options(f"{self.router_url}/health", headers=headers) as response:
                    cors_header = response.headers.get('Access-Control-Allow-Origin', '')
                    
                    if cors_header == '*':
                        self.findings.medium_issues.append("CORS allows all origins - security risk")
                    elif cors_header:
                        self.findings.passed_checks.append("CORS properly configured")
                    else:
                        self.findings.passed_checks.append("CORS restrictive configuration")
                        
        except Exception as e:
            self.findings.low_issues.append(f"CORS test failed: {e}")
    
    async def _review_data_security(self):
        """Review data security measures."""
        logger.info("🔐 Reviewing data security...")
        
        # Check for sensitive data exposure
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.router_url}/models") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for exposed API keys or secrets
                        data_str = json.dumps(data).lower()
                        sensitive_patterns = ['api_key', 'secret', 'password', 'token']
                        
                        exposed_secrets = [p for p in sensitive_patterns if p in data_str]
                        
                        if exposed_secrets:
                            self.findings.critical_issues.append(f"Potential secret exposure: {exposed_secrets}")
                        else:
                            self.findings.passed_checks.append("No obvious secret exposure in API responses")
                            
        except Exception as e:
            self.findings.medium_issues.append(f"Data exposure test failed: {e}")
        
        # Check environment variable security
        env_files = ['config/environments/development.env', 'config/environments/development.env.staging', 'config/environments/developmentconfig/environments/production.env.backup']
        for env_file in env_files:
            if Path(env_file).exists():
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                        if 'password' in content.lower() or 'secret' in content.lower():
                            self.findings.medium_issues.append(f"Sensitive data in {env_file} - ensure proper protection")
                except Exception as e:
                    self.findings.low_issues.append(f"Could not check {env_file}: {e}")
    
    async def _review_constitutional_compliance(self):
        """Review constitutional compliance security."""
        logger.info("📜 Reviewing constitutional compliance...")
        
        # Test constitutional hash validation
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.router_url}/route",
                    json={"query": "test constitutional compliance"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                            self.findings.passed_checks.append("Constitutional hash validation working")
                        else:
                            self.findings.critical_issues.append("Constitutional hash validation failed")
                    else:
                        self.findings.medium_issues.append("Could not test constitutional compliance")
                        
        except Exception as e:
            self.findings.high_issues.append(f"Constitutional compliance test failed: {e}")
    
    async def _review_network_security(self):
        """Review network security configurations."""
        logger.info("🌐 Reviewing network security...")
        
        # Check for open ports (simplified check)
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            if result.returncode == 0:
                open_ports = result.stdout
                
                # Check for unnecessary open ports
                suspicious_ports = ['23', '21', '135', '139', '445']
                found_suspicious = [p for p in suspicious_ports if f":{p}" in open_ports]
                
                if found_suspicious:
                    self.findings.medium_issues.append(f"Potentially unnecessary open ports: {found_suspicious}")
                else:
                    self.findings.passed_checks.append("No obviously suspicious open ports")
            else:
                self.findings.low_issues.append("Could not check network ports")
                
        except Exception as e:
            self.findings.low_issues.append(f"Network security check failed: {e}")
    
    async def _review_container_security(self):
        """Review container security."""
        logger.info("🐳 Reviewing container security...")
        
        # Check Dockerfile security
        dockerfile_path = Path("services/shared/routing/Dockerfile")
        if dockerfile_path.exists():
            try:
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                    
                    # Check for security best practices
                    if 'USER' in content and 'USER root' not in content:
                        self.findings.passed_checks.append("Container runs as non-root user")
                    else:
                        self.findings.medium_issues.append("Container may run as root user")
                    
                    if 'COPY --chown=' in content:
                        self.findings.passed_checks.append("Proper file ownership in container")
                    
                    if 'apt-get update && apt-get install' in content and 'rm -rf /var/lib/apt/lists/*' in content:
                        self.findings.passed_checks.append("Package cache cleaned in container")
                    
            except Exception as e:
                self.findings.low_issues.append(f"Dockerfile security check failed: {e}")
        else:
            self.findings.medium_issues.append("Dockerfile not found for security review")
    
    def _generate_overall_assessment(self):
        """Generate overall security assessment."""
        logger.info("📊 Generating overall security assessment...")
        
        # Calculate security score
        total_checks = (
            len(self.findings.passed_checks) + 
            len(self.findings.failed_checks) + 
            len(self.findings.critical_issues) + 
            len(self.findings.high_issues) + 
            len(self.findings.medium_issues) + 
            len(self.findings.low_issues)
        )
        
        if total_checks > 0:
            # Weight different issue severities
            score = (
                len(self.findings.passed_checks) * 1.0 +
                len(self.findings.low_issues) * 0.8 +
                len(self.findings.medium_issues) * 0.5 +
                len(self.findings.high_issues) * 0.2 +
                len(self.findings.critical_issues) * 0.0
            ) / total_checks
            
            self.findings.overall_score = score
        else:
            self.findings.overall_score = 0.0
        
        # Determine production readiness
        self.findings.production_ready = (
            len(self.findings.critical_issues) == 0 and
            len(self.findings.high_issues) <= 1 and
            self.findings.overall_score >= 0.8
        )


async def main():
    """Main security review function."""
    reviewer = ComprehensiveSecurityReviewer()
    
    try:
        findings = await reviewer.conduct_security_review()
        
        # Save security review report
        report_path = f"security_review_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert findings to dict for JSON serialization
        findings_dict = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "review_timestamp": datetime.utcnow().isoformat(),
            "critical_issues": findings.critical_issues,
            "high_issues": findings.high_issues,
            "medium_issues": findings.medium_issues,
            "low_issues": findings.low_issues,
            "passed_checks": findings.passed_checks,
            "failed_checks": findings.failed_checks,
            "overall_score": findings.overall_score,
            "production_ready": findings.production_ready,
            "summary": {
                "total_issues": len(findings.critical_issues) + len(findings.high_issues) + len(findings.medium_issues) + len(findings.low_issues),
                "critical_count": len(findings.critical_issues),
                "high_count": len(findings.high_issues),
                "medium_count": len(findings.medium_issues),
                "low_count": len(findings.low_issues),
                "passed_count": len(findings.passed_checks)
            }
        }
        
        with open(report_path, "w") as f:
            json.dump(findings_dict, f, indent=2)
        
        print(f"\n🔒 Security Review Completed!")
        print(f"📊 Report saved to: {report_path}")
        print(f"🎯 Overall Score: {findings.overall_score:.2f}")
        print(f"🚀 Production Ready: {'✅ YES' if findings.production_ready else '❌ NO'}")
        
        if findings.critical_issues:
            print(f"🚨 Critical Issues: {len(findings.critical_issues)}")
        if findings.high_issues:
            print(f"⚠️ High Issues: {len(findings.high_issues)}")
        if findings.medium_issues:
            print(f"📋 Medium Issues: {len(findings.medium_issues)}")
        
        return 0 if findings.production_ready else 1
        
    except Exception as e:
        logger.error(f"Security review failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
