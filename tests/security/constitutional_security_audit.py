#!/usr/bin/env python3
"""
ACGS-2 Constitutional Security Audit Suite
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive security audit framework for validating the security posture
of all ACGS-2 services with constitutional compliance verification.
"""

import asyncio
import aiohttp
import json
import re
import ssl
import socket
import subprocess
import time
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import logging
import sys
import os

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class SecurityVulnerability:
    """Individual security vulnerability finding"""
    service_name: str
    vulnerability_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: str
    description: str
    endpoint: Optional[str] = None
    remediation: Optional[str] = None
    cve_id: Optional[str] = None
    constitutional_impact: bool = False
    timestamp: datetime = None

@dataclass
class ServiceSecurityReport:
    """Security report for a single service"""
    service_name: str
    service_url: str
    scan_timestamp: datetime
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    constitutional_compliance_secure: bool
    https_enforced: bool
    authentication_required: bool
    authorization_working: bool
    input_validation_secure: bool
    constitutional_hash_validated: bool
    security_headers_present: bool
    vulnerabilities: List[SecurityVulnerability]
    security_score: float  # 0-100
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW

@dataclass
class SystemSecurityAuditReport:
    """Complete system security audit report"""
    audit_timestamp: datetime
    total_services_scanned: int
    services_with_critical_vulnerabilities: int
    services_with_constitutional_violations: int
    overall_security_score: float
    constitutional_compliance_rate: float
    system_risk_level: str
    services_requiring_immediate_attention: List[str]
    constitutional_violations: List[str]
    service_reports: List[ServiceSecurityReport]
    audit_duration_seconds: float

class ConstitutionalSecurityAuditor:
    """Constitutional security audit engine"""
    
    def __init__(self):
        self.vulnerabilities: List[SecurityVulnerability] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Service configurations for security testing
        self.services = [
            {
                "name": "constitutional-core",
                "base_url": "http://localhost:8001",
                "constitutional_critical": True,
                "endpoints": ["/health", "/api/v1/constitutional/validate"],
                "auth_required": True
            },
            {
                "name": "auth-service",
                "base_url": "http://localhost:8013",
                "constitutional_critical": True,
                "endpoints": ["/health", "/api/v1/auth/login", "/api/v1/auth/users"],
                "auth_required": False  # Auth service handles its own auth
            },
            {
                "name": "monitoring-service",
                "base_url": "http://localhost:8014",
                "constitutional_critical": True,
                "endpoints": ["/health", "/api/v1/services/health"],
                "auth_required": True
            },
            {
                "name": "audit-service",
                "base_url": "http://localhost:8015",
                "constitutional_critical": True,
                "endpoints": ["/health", "/api/v1/audit/logs"],
                "auth_required": True
            },
            {
                "name": "gdpr-compliance",
                "base_url": "http://localhost:8016",
                "constitutional_critical": False,
                "endpoints": ["/health", "/api/v1/gdpr/subjects"],
                "auth_required": True
            },
            {
                "name": "alerting-service",
                "base_url": "http://localhost:8017",
                "constitutional_critical": True,
                "endpoints": ["/health", "/api/v1/alerts"],
                "auth_required": True
            },
            {
                "name": "api-gateway",
                "base_url": "http://localhost:8080",
                "constitutional_critical": True,
                "endpoints": ["/health", "/gateway/metrics"],
                "auth_required": False
            }
        ]
        
        # Common security headers to check
        self.required_security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        # SQL injection payloads for testing
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL,NULL,NULL--",
            "admin'--",
            "' OR 1=1#"
        ]
        
        # XSS payloads for testing
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'>><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>"
        ]
        
        # Path traversal payloads
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    
    async def initialize_session(self):
        """Initialize HTTP session for security testing"""
        connector = aiohttp.TCPConnector(
            ssl=False,  # Allow testing of HTTP endpoints
            limit=100,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def check_constitutional_compliance(self, service: Dict[str, Any]) -> Tuple[bool, List[SecurityVulnerability]]:
        """Check constitutional hash compliance and security"""
        vulnerabilities = []
        constitutional_valid = False
        
        try:
            async with self.session.get(f"{service['base_url']}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    constitutional_hash = data.get("constitutional_hash")
                    
                    if constitutional_hash == CONSTITUTIONAL_HASH:
                        constitutional_valid = True
                    else:
                        vulnerabilities.append(SecurityVulnerability(
                            service_name=service["name"],
                            vulnerability_type="Constitutional Compliance",
                            severity="CRITICAL",
                            title="Constitutional Hash Mismatch",
                            description=f"Service returned incorrect constitutional hash: {constitutional_hash}",
                            endpoint="/health",
                            remediation="Update service to use correct constitutional hash",
                            constitutional_impact=True,
                            timestamp=datetime.utcnow()
                        ))
                else:
                    vulnerabilities.append(SecurityVulnerability(
                        service_name=service["name"],
                        vulnerability_type="Availability",
                        severity="HIGH",
                        title="Health Endpoint Not Accessible",
                        description=f"Health endpoint returned status {response.status}",
                        endpoint="/health",
                        remediation="Ensure health endpoint is properly configured and accessible",
                        constitutional_impact=service["constitutional_critical"],
                        timestamp=datetime.utcnow()
                    ))
        
        except Exception as e:
            vulnerabilities.append(SecurityVulnerability(
                service_name=service["name"],
                vulnerability_type="Availability",
                severity="CRITICAL",
                title="Service Not Accessible",
                description=f"Cannot connect to service: {str(e)}",
                endpoint=service["base_url"],
                remediation="Ensure service is running and accessible",
                constitutional_impact=service["constitutional_critical"],
                timestamp=datetime.utcnow()
            ))
        
        return constitutional_valid, vulnerabilities
    
    async def check_https_enforcement(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Check if HTTPS is properly enforced"""
        vulnerabilities = []
        
        # Check if HTTP redirects to HTTPS
        http_url = service["base_url"].replace("https://", "http://")
        
        try:
            async with self.session.get(http_url, allow_redirects=False) as response:
                if response.status not in [301, 302, 307, 308]:
                    vulnerabilities.append(SecurityVulnerability(
                        service_name=service["name"],
                        vulnerability_type="Transport Security",
                        severity="MEDIUM",
                        title="HTTPS Not Enforced",
                        description="Service does not redirect HTTP to HTTPS",
                        endpoint=http_url,
                        remediation="Configure service to redirect all HTTP traffic to HTTPS",
                        constitutional_impact=service["constitutional_critical"],
                        timestamp=datetime.utcnow()
                    ))
                
                # Check if redirect location is HTTPS
                location = response.headers.get("Location", "")
                if location and not location.startswith("https://"):
                    vulnerabilities.append(SecurityVulnerability(
                        service_name=service["name"],
                        vulnerability_type="Transport Security",
                        severity="HIGH",
                        title="Insecure Redirect",
                        description="HTTP redirect does not enforce HTTPS",
                        endpoint=http_url,
                        remediation="Ensure redirects use HTTPS protocol",
                        constitutional_impact=service["constitutional_critical"],
                        timestamp=datetime.utcnow()
                    ))
        
        except Exception:
            # If connection fails to HTTP, that's actually good - means HTTPS is enforced
            pass
        
        return vulnerabilities
    
    async def check_security_headers(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Check for presence of security headers"""
        vulnerabilities = []
        
        try:
            async with self.session.get(f"{service['base_url']}/health") as response:
                headers = response.headers
                
                for required_header in self.required_security_headers:
                    if required_header not in headers:
                        severity = "MEDIUM"
                        if required_header in ["Strict-Transport-Security", "Content-Security-Policy"]:
                            severity = "HIGH"
                        
                        vulnerabilities.append(SecurityVulnerability(
                            service_name=service["name"],
                            vulnerability_type="Security Headers",
                            severity=severity,
                            title=f"Missing Security Header: {required_header}",
                            description=f"Response does not include {required_header} header",
                            endpoint="/health",
                            remediation=f"Add {required_header} header to all responses",
                            constitutional_impact=service["constitutional_critical"],
                            timestamp=datetime.utcnow()
                        ))
                
                # Check for information disclosure headers
                disclosure_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
                for header in disclosure_headers:
                    if header in headers:
                        vulnerabilities.append(SecurityVulnerability(
                            service_name=service["name"],
                            vulnerability_type="Information Disclosure",
                            severity="LOW",
                            title=f"Information Disclosure: {header}",
                            description=f"Response includes {header} header that may reveal server information",
                            endpoint="/health",
                            remediation=f"Remove or modify {header} header to avoid information disclosure",
                            constitutional_impact=False,
                            timestamp=datetime.utcnow()
                        ))
        
        except Exception as e:
            self.logger.warning(f"Error checking security headers for {service['name']}: {e}")
        
        return vulnerabilities
    
    async def test_sql_injection(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in service["endpoints"]:
            if "api" not in endpoint:
                continue  # Skip non-API endpoints
            
            for payload in self.sql_injection_payloads:
                try:
                    # Test with query parameter
                    test_url = f"{service['base_url']}{endpoint}?id={payload}"
                    async with self.session.get(test_url) as response:
                        response_text = await response.text()
                        
                        # Look for SQL error indicators
                        sql_errors = [
                            "sql syntax",
                            "mysql_fetch",
                            "postgresql",
                            "ora-00",
                            "sqlite",
                            "syntax error"
                        ]
                        
                        for error in sql_errors:
                            if error.lower() in response_text.lower():
                                vulnerabilities.append(SecurityVulnerability(
                                    service_name=service["name"],
                                    vulnerability_type="SQL Injection",
                                    severity="CRITICAL",
                                    title="SQL Injection Vulnerability",
                                    description=f"SQL error exposed with payload: {payload}",
                                    endpoint=endpoint,
                                    remediation="Use parameterized queries and input validation",
                                    constitutional_impact=service["constitutional_critical"],
                                    timestamp=datetime.utcnow()
                                ))
                                break
                
                except Exception:
                    pass  # Expected for many payloads
        
        return vulnerabilities
    
    async def test_xss_vulnerability(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in service["endpoints"]:
            if "api" not in endpoint:
                continue
            
            for payload in self.xss_payloads:
                try:
                    # Test with query parameter
                    test_url = f"{service['base_url']}{endpoint}?search={payload}"
                    async with self.session.get(test_url) as response:
                        response_text = await response.text()
                        
                        # Check if payload is reflected without encoding
                        if payload in response_text:
                            vulnerabilities.append(SecurityVulnerability(
                                service_name=service["name"],
                                vulnerability_type="Cross-Site Scripting",
                                severity="HIGH",
                                title="Reflected XSS Vulnerability",
                                description=f"User input reflected without proper encoding: {payload}",
                                endpoint=endpoint,
                                remediation="Implement proper input validation and output encoding",
                                constitutional_impact=service["constitutional_critical"],
                                timestamp=datetime.utcnow()
                            ))
                
                except Exception:
                    pass
        
        return vulnerabilities
    
    async def test_authentication_bypass(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []
        
        if not service.get("auth_required", False):
            return vulnerabilities
        
        for endpoint in service["endpoints"]:
            if endpoint == "/health":
                continue  # Health endpoints are typically public
            
            try:
                # Test access without authentication
                async with self.session.get(f"{service['base_url']}{endpoint}") as response:
                    if response.status == 200:
                        vulnerabilities.append(SecurityVulnerability(
                            service_name=service["name"],
                            vulnerability_type="Authentication Bypass",
                            severity="CRITICAL",
                            title="Authentication Not Required",
                            description=f"Protected endpoint accessible without authentication: {endpoint}",
                            endpoint=endpoint,
                            remediation="Implement proper authentication checks for all protected endpoints",
                            constitutional_impact=service["constitutional_critical"],
                            timestamp=datetime.utcnow()
                        ))
                
                # Test with invalid token
                headers = {"Authorization": "Bearer invalid_token_12345"}
                async with self.session.get(f"{service['base_url']}{endpoint}", headers=headers) as response:
                    if response.status == 200:
                        vulnerabilities.append(SecurityVulnerability(
                            service_name=service["name"],
                            vulnerability_type="Authentication Bypass",
                            severity="HIGH",
                            title="Invalid Token Accepted",
                            description=f"Endpoint accepts invalid authentication token: {endpoint}",
                            endpoint=endpoint,
                            remediation="Implement proper token validation",
                            constitutional_impact=service["constitutional_critical"],
                            timestamp=datetime.utcnow()
                        ))
            
            except Exception:
                pass
        
        return vulnerabilities
    
    async def test_path_traversal(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for path traversal vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in service["endpoints"]:
            for payload in self.path_traversal_payloads:
                try:
                    # Test with path parameter
                    test_url = f"{service['base_url']}{endpoint}?file={payload}"
                    async with self.session.get(test_url) as response:
                        response_text = await response.text()
                        
                        # Look for signs of file system access
                        file_indicators = [
                            "root:",
                            "[boot loader]",
                            "# /etc/passwd",
                            "daemon:",
                            "Windows Registry Editor"
                        ]
                        
                        for indicator in file_indicators:
                            if indicator in response_text:
                                vulnerabilities.append(SecurityVulnerability(
                                    service_name=service["name"],
                                    vulnerability_type="Path Traversal",
                                    severity="HIGH",
                                    title="Path Traversal Vulnerability",
                                    description=f"File system access detected with payload: {payload}",
                                    endpoint=endpoint,
                                    remediation="Implement proper file path validation and sandboxing",
                                    constitutional_impact=service["constitutional_critical"],
                                    timestamp=datetime.utcnow()
                                ))
                                break
                
                except Exception:
                    pass
        
        return vulnerabilities
    
    async def check_rate_limiting(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Check if rate limiting is properly implemented"""
        vulnerabilities = []
        
        endpoint = service["endpoints"][0]  # Test first endpoint
        requests_count = 0
        rate_limited = False
        
        try:
            # Send multiple rapid requests
            for i in range(50):
                async with self.session.get(f"{service['base_url']}{endpoint}") as response:
                    requests_count += 1
                    if response.status == 429:  # Too Many Requests
                        rate_limited = True
                        break
            
            if not rate_limited and requests_count >= 50:
                severity = "MEDIUM"
                if service["constitutional_critical"]:
                    severity = "HIGH"
                
                vulnerabilities.append(SecurityVulnerability(
                    service_name=service["name"],
                    vulnerability_type="Rate Limiting",
                    severity=severity,
                    title="Rate Limiting Not Implemented",
                    description="Service does not implement rate limiting protection",
                    endpoint=endpoint,
                    remediation="Implement rate limiting to prevent abuse",
                    constitutional_impact=service["constitutional_critical"],
                    timestamp=datetime.utcnow()
                ))
        
        except Exception as e:
            self.logger.warning(f"Error testing rate limiting for {service['name']}: {e}")
        
        return vulnerabilities
    
    def check_port_security(self, service: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Check for open ports and services"""
        vulnerabilities = []
        
        try:
            # Extract host and port from URL
            from urllib.parse import urlparse
            parsed = urlparse(service["base_url"])
            host = parsed.hostname or "localhost"
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            
            # Check if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result != 0:
                vulnerabilities.append(SecurityVulnerability(
                    service_name=service["name"],
                    vulnerability_type="Service Availability",
                    severity="HIGH",
                    title="Service Port Not Accessible",
                    description=f"Cannot connect to {host}:{port}",
                    endpoint=service["base_url"],
                    remediation="Ensure service is running and accessible on configured port",
                    constitutional_impact=service["constitutional_critical"],
                    timestamp=datetime.utcnow()
                ))
        
        except Exception as e:
            self.logger.warning(f"Error checking port security for {service['name']}: {e}")
        
        return vulnerabilities
    
    async def audit_service_security(self, service: Dict[str, Any]) -> ServiceSecurityReport:
        """Perform comprehensive security audit on a single service"""
        self.logger.info(f"🔍 Auditing security for {service['name']}...")
        
        scan_start = datetime.utcnow()
        all_vulnerabilities = []
        
        # 1. Constitutional compliance check
        constitutional_valid, const_vulns = await self.check_constitutional_compliance(service)
        all_vulnerabilities.extend(const_vulns)
        
        # 2. HTTPS enforcement check
        https_vulns = await self.check_https_enforcement(service)
        all_vulnerabilities.extend(https_vulns)
        
        # 3. Security headers check
        header_vulns = await self.check_security_headers(service)
        all_vulnerabilities.extend(header_vulns)
        
        # 4. SQL injection testing
        sql_vulns = await self.test_sql_injection(service)
        all_vulnerabilities.extend(sql_vulns)
        
        # 5. XSS testing
        xss_vulns = await self.test_xss_vulnerability(service)
        all_vulnerabilities.extend(xss_vulns)
        
        # 6. Authentication bypass testing
        auth_vulns = await self.test_authentication_bypass(service)
        all_vulnerabilities.extend(auth_vulns)
        
        # 7. Path traversal testing
        path_vulns = await self.test_path_traversal(service)
        all_vulnerabilities.extend(path_vulns)
        
        # 8. Rate limiting check
        rate_vulns = await self.check_rate_limiting(service)
        all_vulnerabilities.extend(rate_vulns)
        
        # 9. Port security check
        port_vulns = self.check_port_security(service)
        all_vulnerabilities.extend(port_vulns)
        
        # Calculate vulnerability counts by severity
        critical_count = len([v for v in all_vulnerabilities if v.severity == "CRITICAL"])
        high_count = len([v for v in all_vulnerabilities if v.severity == "HIGH"])
        medium_count = len([v for v in all_vulnerabilities if v.severity == "MEDIUM"])
        low_count = len([v for v in all_vulnerabilities if v.severity == "LOW"])
        
        # Calculate security score (0-100)
        base_score = 100
        score_penalties = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 5,
            "LOW": 1
        }
        
        security_score = base_score
        for vuln in all_vulnerabilities:
            security_score -= score_penalties.get(vuln.severity, 0)
        
        security_score = max(0, security_score)
        
        # Determine risk level
        if critical_count > 0:
            risk_level = "CRITICAL"
        elif high_count > 0:
            risk_level = "HIGH"
        elif medium_count > 0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Determine security characteristics
        https_enforced = len([v for v in https_vulns if "HTTPS" in v.title]) == 0
        auth_working = len([v for v in auth_vulns if "Authentication" in v.vulnerability_type]) == 0
        headers_present = len([v for v in header_vulns if "Missing" in v.title]) < 3
        
        return ServiceSecurityReport(
            service_name=service["name"],
            service_url=service["base_url"],
            scan_timestamp=scan_start,
            total_vulnerabilities=len(all_vulnerabilities),
            critical_vulnerabilities=critical_count,
            high_vulnerabilities=high_count,
            medium_vulnerabilities=medium_count,
            low_vulnerabilities=low_count,
            constitutional_compliance_secure=constitutional_valid,
            https_enforced=https_enforced,
            authentication_required=service.get("auth_required", False),
            authorization_working=auth_working,
            input_validation_secure=len([v for v in sql_vulns + xss_vulns + path_vulns]) == 0,
            constitutional_hash_validated=constitutional_valid,
            security_headers_present=headers_present,
            vulnerabilities=all_vulnerabilities,
            security_score=security_score,
            risk_level=risk_level
        )
    
    async def run_comprehensive_security_audit(self) -> SystemSecurityAuditReport:
        """Run comprehensive security audit across all services"""
        self.logger.info(f"🏛️ Starting ACGS-2 Constitutional Security Audit")
        self.logger.info(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        self.logger.info(f"🔍 Auditing {len(self.services)} services")
        print("=" * 80)
        
        audit_start = time.time()
        await self.initialize_session()
        
        try:
            service_reports = []
            
            # Audit each service
            for service in self.services:
                report = await self.audit_service_security(service)
                service_reports.append(report)
                
                # Quick status update
                status = "✅ SECURE" if report.risk_level == "LOW" else f"⚠️ {report.risk_level} RISK"
                print(f"   {status} {service['name']}: "
                      f"{report.total_vulnerabilities} vulns, "
                      f"Score: {report.security_score:.0f}/100")
            
            # Calculate system-wide metrics
            total_services = len(service_reports)
            services_with_critical = len([r for r in service_reports if r.critical_vulnerabilities > 0])
            services_with_constitutional_violations = len([
                r for r in service_reports 
                if not r.constitutional_compliance_secure
            ])
            
            overall_security_score = sum(r.security_score for r in service_reports) / total_services if total_services > 0 else 0
            
            constitutional_compliant_services = len([
                r for r in service_reports 
                if r.constitutional_compliance_secure
            ])
            constitutional_compliance_rate = (constitutional_compliant_services / total_services * 100) if total_services > 0 else 0
            
            # Determine system risk level
            if services_with_critical > 0:
                system_risk_level = "CRITICAL"
            elif any(r.risk_level == "HIGH" for r in service_reports):
                system_risk_level = "HIGH"
            elif any(r.risk_level == "MEDIUM" for r in service_reports):
                system_risk_level = "MEDIUM"
            else:
                system_risk_level = "LOW"
            
            # Identify services requiring immediate attention
            critical_services = [
                r.service_name for r in service_reports 
                if r.risk_level in ["CRITICAL", "HIGH"]
            ]
            
            # Identify constitutional violations
            constitutional_violations = [
                f"{r.service_name}: {v.title}" 
                for r in service_reports 
                for v in r.vulnerabilities 
                if v.constitutional_impact
            ]
            
            audit_duration = time.time() - audit_start
            
            return SystemSecurityAuditReport(
                audit_timestamp=datetime.utcnow(),
                total_services_scanned=total_services,
                services_with_critical_vulnerabilities=services_with_critical,
                services_with_constitutional_violations=services_with_constitutional_violations,
                overall_security_score=overall_security_score,
                constitutional_compliance_rate=constitutional_compliance_rate,
                system_risk_level=system_risk_level,
                services_requiring_immediate_attention=critical_services,
                constitutional_violations=constitutional_violations,
                service_reports=service_reports,
                audit_duration_seconds=audit_duration
            )
        
        finally:
            await self.cleanup_session()
    
    def generate_security_report(self, audit_report: SystemSecurityAuditReport) -> str:
        """Generate detailed security audit report"""
        
        lines = [
            "=" * 100,
            "🏛️ ACGS-2 CONSTITUTIONAL SECURITY AUDIT REPORT",
            "=" * 100,
            f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}",
            f"⏰ Audit Completed: {audit_report.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"⏱️ Audit Duration: {audit_report.audit_duration_seconds:.1f} seconds",
            "",
            "🚨 EXECUTIVE SECURITY SUMMARY",
            "─" * 50,
            f"Overall System Risk Level: {audit_report.system_risk_level}",
            f"Overall Security Score: {audit_report.overall_security_score:.1f}/100",
            f"Constitutional Compliance Rate: {audit_report.constitutional_compliance_rate:.1f}%",
            f"Services Scanned: {audit_report.total_services_scanned}",
            f"Services with Critical Vulnerabilities: {audit_report.services_with_critical_vulnerabilities}",
            f"Services with Constitutional Violations: {audit_report.services_with_constitutional_violations}",
            ""
        ]
        
        # Constitutional compliance status
        if audit_report.constitutional_compliance_rate == 100.0:
            lines.extend([
                "⚖️ CONSTITUTIONAL COMPLIANCE STATUS: ✅ COMPLIANT",
                "All services properly implement constitutional hash validation"
            ])
        else:
            lines.extend([
                "⚖️ CONSTITUTIONAL COMPLIANCE STATUS: ❌ VIOLATIONS DETECTED",
                "The following constitutional violations require immediate attention:"
            ])
            for violation in audit_report.constitutional_violations:
                lines.append(f"   🚨 {violation}")
        
        lines.append("")
        
        # Services requiring immediate attention
        if audit_report.services_requiring_immediate_attention:
            lines.extend([
                "🚨 SERVICES REQUIRING IMMEDIATE ATTENTION",
                "─" * 50
            ])
            for service in audit_report.services_requiring_immediate_attention:
                lines.append(f"   ⚠️ {service}")
            lines.append("")
        
        # Detailed service reports
        lines.extend([
            "📊 DETAILED SERVICE SECURITY ANALYSIS",
            "─" * 100,
            f"{'Service':<25} {'Risk':<10} {'Score':<7} {'Vulns':<7} {'Critical':<10} {'Constitutional':<15}",
            "─" * 100
        ])
        
        for report in sorted(audit_report.service_reports, key=lambda x: x.security_score):
            constitutional_status = "✅ VALID" if report.constitutional_compliance_secure else "❌ INVALID"
            
            lines.append(
                f"{report.service_name:<25} "
                f"{report.risk_level:<10} "
                f"{report.security_score:<6.0f} "
                f"{report.total_vulnerabilities:<7} "
                f"{report.critical_vulnerabilities:<10} "
                f"{constitutional_status:<15}"
            )
        
        lines.extend([
            "",
            "🔍 VULNERABILITY BREAKDOWN BY SERVICE",
            "─" * 100
        ])
        
        for report in audit_report.service_reports:
            if report.total_vulnerabilities > 0:
                lines.extend([
                    f"\n❌ {report.service_name.upper()} - {report.total_vulnerabilities} VULNERABILITIES FOUND",
                    f"   Risk Level: {report.risk_level}",
                    f"   Security Score: {report.security_score:.0f}/100",
                    f"   Constitutional Compliance: {'✅ Valid' if report.constitutional_compliance_secure else '❌ Invalid'}",
                    f"   Vulnerabilities: {report.critical_vulnerabilities} Critical, {report.high_vulnerabilities} High, {report.medium_vulnerabilities} Medium, {report.low_vulnerabilities} Low",
                    ""
                ])
                
                # List critical and high vulnerabilities
                critical_high_vulns = [
                    v for v in report.vulnerabilities 
                    if v.severity in ["CRITICAL", "HIGH"]
                ]
                
                for vuln in critical_high_vulns:
                    constitutional_marker = "⚖️" if vuln.constitutional_impact else ""
                    lines.extend([
                        f"   🚨 {vuln.severity}: {vuln.title} {constitutional_marker}",
                        f"      Type: {vuln.vulnerability_type}",
                        f"      Endpoint: {vuln.endpoint or 'N/A'}",
                        f"      Description: {vuln.description}",
                        f"      Remediation: {vuln.remediation or 'Contact security team'}",
                        ""
                    ])
        
        # Security recommendations
        lines.extend([
            "💡 SECURITY RECOMMENDATIONS",
            "─" * 50
        ])
        
        if audit_report.overall_security_score < 70:
            lines.extend([
                "🚨 URGENT SECURITY IMPROVEMENTS REQUIRED:",
                "1. Address all CRITICAL and HIGH severity vulnerabilities immediately",
                "2. Implement comprehensive input validation across all endpoints",
                "3. Ensure proper authentication and authorization on all protected endpoints",
                "4. Add security headers to all HTTP responses",
                "5. Implement rate limiting to prevent abuse",
                ""
            ])
        
        if audit_report.constitutional_compliance_rate < 100:
            lines.extend([
                "⚖️ CONSTITUTIONAL COMPLIANCE IMPROVEMENTS:",
                "1. Update all services to use correct constitutional hash",
                "2. Implement constitutional hash validation in health endpoints",
                "3. Add constitutional compliance monitoring and alerting",
                "4. Review and update constitutional governance procedures",
                ""
            ])
        
        lines.extend([
            "🔒 GENERAL SECURITY BEST PRACTICES:",
            "1. Regularly update dependencies and frameworks",
            "2. Implement automated security scanning in CI/CD pipeline",
            "3. Conduct regular penetration testing",
            "4. Implement comprehensive logging and monitoring",
            "5. Train development team on secure coding practices",
            "6. Implement secrets management for API keys and tokens",
            "7. Regular security awareness training for all team members",
            "",
            "=" * 100,
            f"📋 Audit Completed: {audit_report.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}",
            "=" * 100
        ])
        
        return "\n".join(lines)

async def main():
    """Main security audit entry point"""
    parser = argparse.ArgumentParser(description="ACGS-2 Constitutional Security Audit Suite")
    parser.add_argument("--output", type=str, default="security_audit_report.txt", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Also output JSON report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize auditor
    auditor = ConstitutionalSecurityAuditor()
    
    try:
        # Run comprehensive security audit
        audit_report = await auditor.run_comprehensive_security_audit()
        
        # Generate detailed report
        detailed_report = auditor.generate_security_report(audit_report)
        
        # Save text report
        with open(args.output, 'w') as f:
            f.write(detailed_report)
        
        print(f"\n📄 Detailed security report saved to: {args.output}")
        
        # Save JSON report if requested
        if args.json:
            json_file = args.output.replace('.txt', '.json')
            with open(json_file, 'w') as f:
                # Convert to JSON-serializable format
                json_data = {
                    "audit_timestamp": audit_report.audit_timestamp.isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "overall_security_score": audit_report.overall_security_score,
                    "system_risk_level": audit_report.system_risk_level,
                    "constitutional_compliance_rate": audit_report.constitutional_compliance_rate,
                    "services_with_critical_vulnerabilities": audit_report.services_with_critical_vulnerabilities,
                    "services_requiring_immediate_attention": audit_report.services_requiring_immediate_attention,
                    "constitutional_violations": audit_report.constitutional_violations,
                    "services": [
                        {
                            "name": s.service_name,
                            "risk_level": s.risk_level,
                            "security_score": s.security_score,
                            "total_vulnerabilities": s.total_vulnerabilities,
                            "critical_vulnerabilities": s.critical_vulnerabilities,
                            "constitutional_compliance_secure": s.constitutional_compliance_secure,
                            "vulnerabilities": [
                                {
                                    "type": v.vulnerability_type,
                                    "severity": v.severity,
                                    "title": v.title,
                                    "description": v.description,
                                    "constitutional_impact": v.constitutional_impact
                                }
                                for v in s.vulnerabilities
                            ]
                        }
                        for s in audit_report.service_reports
                    ]
                }
                json.dump(json_data, f, indent=2)
            
            print(f"📊 JSON report saved to: {json_file}")
        
        # Print summary
        print(f"\n🏛️ CONSTITUTIONAL SECURITY AUDIT COMPLETE")
        print(f"{'='*60}")
        
        if audit_report.system_risk_level in ["CRITICAL", "HIGH"]:
            status = f"❌ {audit_report.system_risk_level} RISK"
        else:
            status = f"✅ {audit_report.system_risk_level} RISK"
        
        print(f"Overall Status: {status}")
        print(f"Security Score: {audit_report.overall_security_score:.1f}/100")
        print(f"Constitutional Compliance: {audit_report.constitutional_compliance_rate:.1f}%")
        print(f"Services with Critical Vulnerabilities: {audit_report.services_with_critical_vulnerabilities}")
        
        if audit_report.constitutional_violations:
            print(f"Constitutional Violations: {len(audit_report.constitutional_violations)}")
        
        # Exit with appropriate code
        if (audit_report.system_risk_level in ["CRITICAL", "HIGH"] or 
            audit_report.constitutional_compliance_rate < 100.0):
            sys.exit(1)
        else:
            sys.exit(0)
        
    except Exception as e:
        print(f"❌ Security audit failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())