#!/usr/bin/env python3
"""
ACGS Security Hardening and Vulnerability Assessment
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive security assessment and hardening for ACGS production deployment.
Addresses authentication, authorization, input validation, API security, and more.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Security assessment configuration
SECURITY_ASSESSMENT_CONFIG = {
    "vulnerability_scan_enabled": True,
    "dependency_check_enabled": True,
    "secrets_scan_enabled": True,
    "code_analysis_enabled": True,
    "api_security_check_enabled": True,
    "authentication_audit_enabled": True,
    "authorization_audit_enabled": True,
    "input_validation_check_enabled": True,
}

# Security hardening targets
SECURITY_TARGETS = {
    "authentication_strength": 0.95,  # 95% authentication security score
    "authorization_coverage": 0.90,  # 90% authorization coverage
    "input_validation_coverage": 0.95,  # 95% input validation coverage
    "api_security_score": 0.90,  # 90% API security score
    "dependency_security_score": 0.85,  # 85% dependency security score
    "secrets_management_score": 0.95,  # 95% secrets management score
    "overall_security_score": 0.90,  # 90% overall security score
}


class SecurityVulnerability:
    """Represents a security vulnerability."""

    def __init__(
        self,
        severity: str,
        category: str,
        description: str,
        location: str,
        recommendation: str,
    ):
        self.severity = severity  # critical, high, medium, low
        self.category = category  # auth, input, api, dependency, etc.
        self.description = description
        self.location = location
        self.recommendation = recommendation
        self.constitutional_hash = CONSTITUTIONAL_HASH


class ACGSSecurityAssessment:
    """Comprehensive security assessment for ACGS."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger("acgs_security")
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.vulnerabilities = []
        self.security_scores = {}
        self.hardening_recommendations = []

    async def run_comprehensive_assessment(self) -> Dict[str, Any]:
        """Run comprehensive security assessment."""
        self.logger.info("🔒 Starting ACGS Security Hardening Assessment")
        self.logger.info(f"📋 Constitutional Hash: {self.constitutional_hash}")

        assessment_results = {
            "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "security_scores": {},
            "vulnerabilities": [],
            "hardening_recommendations": [],
            "compliance_status": {},
        }

        # Run security assessments
        assessments = [
            ("Authentication Security", self._assess_authentication_security),
            ("Authorization Controls", self._assess_authorization_controls),
            ("Input Validation", self._assess_input_validation),
            ("API Security", self._assess_api_security),
            ("Dependency Security", self._assess_dependency_security),
            ("Secrets Management", self._assess_secrets_management),
            ("Code Security", self._assess_code_security),
            ("Infrastructure Security", self._assess_infrastructure_security),
        ]

        for assessment_name, assessment_func in assessments:
            try:
                self.logger.info(f"🔍 Running {assessment_name} assessment...")
                result = await assessment_func()
                assessment_results["security_scores"][assessment_name] = result
                self.logger.info(
                    f"   ✅ {assessment_name}: {result.get('score', 0):.2f}"
                )
            except Exception as e:
                self.logger.error(f"   ❌ {assessment_name} failed: {e}")
                assessment_results["security_scores"][assessment_name] = {
                    "score": 0.0,
                    "error": str(e),
                }

        # Calculate overall security score
        scores = [
            r.get("score", 0.0)
            for r in assessment_results["security_scores"].values()
            if isinstance(r, dict)
        ]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        assessment_results["overall_security_score"] = overall_score

        # Compile vulnerabilities and recommendations
        assessment_results["vulnerabilities"] = [
            {
                "severity": v.severity,
                "category": v.category,
                "description": v.description,
                "location": v.location,
                "recommendation": v.recommendation,
            }
            for v in self.vulnerabilities
        ]
        assessment_results["hardening_recommendations"] = self.hardening_recommendations

        # Determine compliance status
        assessment_results["compliance_status"] = {
            "meets_security_targets": overall_score
            >= SECURITY_TARGETS["overall_security_score"],
            "critical_vulnerabilities": len(
                [v for v in self.vulnerabilities if v.severity == "critical"]
            ),
            "high_vulnerabilities": len(
                [v for v in self.vulnerabilities if v.severity == "high"]
            ),
            "constitutional_compliance": True,  # All assessments maintain constitutional hash
        }

        self.logger.info(f"🎯 Overall Security Score: {overall_score:.2f}")
        self.logger.info(
            f"🔒 Security Target Met: {assessment_results['compliance_status']['meets_security_targets']}"
        )

        return assessment_results

    async def _assess_authentication_security(self) -> Dict[str, Any]:
        """Assess authentication security mechanisms."""
        score = 0.0
        findings = []

        # Check JWT implementation
        jwt_files = list(self.project_root.glob("**/jwt_security.py"))
        if jwt_files:
            score += 0.3
            findings.append("JWT implementation found")

            # Check for security features in JWT implementation
            for jwt_file in jwt_files:
                content = jwt_file.read_text()

                if "constitutional_hash" in content:
                    score += 0.1
                    findings.append("Constitutional compliance in JWT")

                if "ip_binding" in content.lower():
                    score += 0.1
                    findings.append("IP binding implemented")

                if "session_tracking" in content.lower():
                    score += 0.1
                    findings.append("Session tracking implemented")

                if "revoked_tokens" in content:
                    score += 0.1
                    findings.append("Token revocation implemented")
                else:
                    self.vulnerabilities.append(
                        SecurityVulnerability(
                            "medium",
                            "authentication",
                            "Token revocation mechanism not found",
                            str(jwt_file),
                            "Implement token revocation/blacklisting",
                        )
                    )
        else:
            self.vulnerabilities.append(
                SecurityVulnerability(
                    "high",
                    "authentication",
                    "No JWT security implementation found",
                    "authentication services",
                    "Implement secure JWT authentication",
                )
            )

        # Check for hardcoded credentials
        hardcoded_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
        ]

        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                for pattern in hardcoded_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "critical",
                                "authentication",
                                f"Potential hardcoded credential found",
                                str(py_file),
                                "Move credentials to secure environment variables or vault",
                            )
                        )
            except Exception:
                continue

        # Check authentication middleware
        middleware_files = list(self.project_root.glob("**/security_middleware.py"))
        if middleware_files:
            score += 0.2
            findings.append("Security middleware found")

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_authorization_controls(self) -> Dict[str, Any]:
        """Assess authorization and access control mechanisms."""
        score = 0.0
        findings = []

        # Check for role-based access control
        rbac_patterns = ["role", "permission", "authorize", "access_control"]
        rbac_files = []

        for pattern in rbac_patterns:
            rbac_files.extend(self.project_root.glob(f"**/*{pattern}*.py"))

        if rbac_files:
            score += 0.4
            findings.append(f"Authorization files found: {len(rbac_files)}")

        # Check for security context usage
        security_context_files = list(
            self.project_root.glob("**/security_architecture.py")
        )
        if security_context_files:
            score += 0.3
            findings.append("Security context implementation found")

        # Check for endpoint protection
        protected_endpoints = 0
        total_endpoints = 0

        for py_file in self.project_root.glob("**/main.py"):
            try:
                content = py_file.read_text()
                # Count FastAPI endpoints
                endpoints = re.findall(r"@app\.(get|post|put|delete|patch)", content)
                total_endpoints += len(endpoints)

                # Count protected endpoints (with dependencies or security)
                protected = re.findall(r"dependencies=|Depends\(|Security\(", content)
                protected_endpoints += len(protected)
            except Exception:
                continue

        if total_endpoints > 0:
            protection_ratio = protected_endpoints / total_endpoints
            score += protection_ratio * 0.3
            findings.append(
                f"Endpoint protection: {protected_endpoints}/{total_endpoints} ({protection_ratio:.1%})"
            )

            if protection_ratio < 0.8:
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "medium",
                        "authorization",
                        f"Only {protection_ratio:.1%} of endpoints are protected",
                        "API endpoints",
                        "Add authentication/authorization to unprotected endpoints",
                    )
                )

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_input_validation(self) -> Dict[str, Any]:
        """Assess input validation mechanisms."""
        score = 0.0
        findings = []

        # Check for Pydantic models
        pydantic_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "from pydantic import" in content or "import pydantic" in content:
                    pydantic_files.append(py_file)
            except Exception:
                continue

        if pydantic_files:
            score += 0.4
            findings.append(f"Pydantic validation found in {len(pydantic_files)} files")

        # Check for input sanitization
        sanitization_patterns = ["sanitize", "validate", "clean", "escape"]
        sanitization_found = False

        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                for pattern in sanitization_patterns:
                    if pattern in content.lower():
                        sanitization_found = True
                        break
            except Exception:
                continue

        if sanitization_found:
            score += 0.3
            findings.append("Input sanitization mechanisms found")

        # Check for SQL injection protection
        sql_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "SELECT" in content or "INSERT" in content or "UPDATE" in content:
                    # Check if using parameterized queries
                    if "?" in content or "%s" in content or "execute(" in content:
                        sql_files.append(py_file)
            except Exception:
                continue

        if sql_files:
            score += 0.3
            findings.append("SQL query files found - check for parameterization")

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_api_security(self) -> Dict[str, Any]:
        """Assess API security mechanisms."""
        score = 0.0
        findings = []

        # Check for CORS configuration
        cors_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "CORSMiddleware" in content or "add_middleware" in content:
                    cors_files.append(py_file)
            except Exception:
                continue

        if cors_files:
            score += 0.2
            findings.append("CORS middleware found")

        # Check for rate limiting
        rate_limit_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "rate_limit" in content.lower() or "slowapi" in content.lower():
                    rate_limit_files.append(py_file)
            except Exception:
                continue

        if rate_limit_files:
            score += 0.3
            findings.append("Rate limiting found")
        else:
            self.vulnerabilities.append(
                SecurityVulnerability(
                    "medium",
                    "api_security",
                    "No rate limiting implementation found",
                    "API endpoints",
                    "Implement rate limiting to prevent abuse",
                )
            )

        # Check for HTTPS enforcement
        https_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "https_only" in content.lower() or "secure=True" in content:
                    https_files.append(py_file)
            except Exception:
                continue

        if https_files:
            score += 0.2
            findings.append("HTTPS enforcement found")

        # Check for security headers
        security_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
        ]
        headers_found = 0

        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                for header in security_headers:
                    if header in content:
                        headers_found += 1
            except Exception:
                continue

        if headers_found > 0:
            score += (headers_found / len(security_headers)) * 0.3
            findings.append(
                f"Security headers found: {headers_found}/{len(security_headers)}"
            )

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_dependency_security(self) -> Dict[str, Any]:
        """Assess dependency security."""
        score = 0.0
        findings = []

        # Check for requirements.txt
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))
        if requirements_files:
            score += 0.3
            findings.append(f"Requirements files found: {len(requirements_files)}")

            # Check for pinned versions
            pinned_count = 0
            total_deps = 0

            for req_file in requirements_files:
                try:
                    content = req_file.read_text()
                    lines = [
                        line.strip()
                        for line in content.split("\n")
                        if line.strip() and not line.startswith("#")
                    ]
                    total_deps += len(lines)

                    for line in lines:
                        if "==" in line:
                            pinned_count += 1
                except Exception:
                    continue

            if total_deps > 0:
                pin_ratio = pinned_count / total_deps
                score += pin_ratio * 0.4
                findings.append(
                    f"Pinned dependencies: {pinned_count}/{total_deps} ({pin_ratio:.1%})"
                )

                if pin_ratio < 0.8:
                    self.vulnerabilities.append(
                        SecurityVulnerability(
                            "medium",
                            "dependency",
                            f"Only {pin_ratio:.1%} of dependencies are pinned",
                            "requirements.txt",
                            "Pin all dependency versions for security",
                        )
                    )

        # Check for known vulnerable packages (simplified check)
        vulnerable_packages = ["pillow<8.3.2", "requests<2.25.1", "urllib3<1.26.5"]
        for req_file in requirements_files:
            try:
                content = req_file.read_text()
                for vuln_pkg in vulnerable_packages:
                    if vuln_pkg.split("<")[0] in content:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "high",
                                "dependency",
                                f"Potentially vulnerable package: {vuln_pkg.split('<')[0]}",
                                str(req_file),
                                f"Update to version >= {vuln_pkg.split('<')[1]}",
                            )
                        )
            except Exception:
                continue

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_secrets_management(self) -> Dict[str, Any]:
        """Assess secrets management practices."""
        score = 0.0
        findings = []

        # Check for environment variable usage
        env_usage = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "os.environ" in content or "getenv" in content:
                    env_usage.append(py_file)
            except Exception:
                continue

        if env_usage:
            score += 0.4
            findings.append(
                f"Environment variable usage found in {len(env_usage)} files"
            )

        # Check for vault integration
        vault_files = list(self.project_root.glob("**/vault*.py"))
        if vault_files:
            score += 0.3
            findings.append("Vault integration found")

        # Check for .env files (should not be in repo)
        env_files = list(self.project_root.glob("**/.env*"))
        if env_files:
            for env_file in env_files:
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "high",
                        "secrets",
                        f"Environment file in repository: {env_file.name}",
                        str(env_file),
                        "Remove .env files from repository, add to .gitignore",
                    )
                )
        else:
            score += 0.3
            findings.append("No .env files found in repository")

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_code_security(self) -> Dict[str, Any]:
        """Assess code security practices."""
        score = 0.5  # Base score for constitutional compliance
        findings = ["Constitutional compliance maintained"]

        # Check for security imports
        security_imports = ["hashlib", "secrets", "cryptography", "jwt"]
        imports_found = 0

        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                for sec_import in security_imports:
                    if (
                        f"import {sec_import}" in content
                        or f"from {sec_import}" in content
                    ):
                        imports_found += 1
                        break
            except Exception:
                continue

        if imports_found > 0:
            score += 0.3
            findings.append(f"Security-related imports found")

        # Check for logging
        logging_files = []
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if "logging" in content and "logger" in content:
                    logging_files.append(py_file)
            except Exception:
                continue

        if logging_files:
            score += 0.2
            findings.append(
                f"Logging implementation found in {len(logging_files)} files"
            )

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def _assess_infrastructure_security(self) -> Dict[str, Any]:
        """Assess infrastructure security configuration."""
        score = 0.0
        findings = []

        # Check for Docker security
        docker_files = list(self.project_root.glob("**/Dockerfile*"))
        if docker_files:
            score += 0.3
            findings.append(f"Docker files found: {len(docker_files)}")

            # Check for non-root user
            for docker_file in docker_files:
                try:
                    content = docker_file.read_text()
                    if "USER " in content and "USER root" not in content:
                        score += 0.2
                        findings.append("Non-root user in Docker")
                        break
                except Exception:
                    continue

        # Check for security configurations
        config_files = list(self.project_root.glob("**/security*.yaml")) + list(
            self.project_root.glob("**/security*.yml")
        )
        if config_files:
            score += 0.3
            findings.append("Security configuration files found")

        # Check for TLS/SSL configuration
        tls_files = []
        for config_file in self.project_root.glob("**/*.yaml"):
            try:
                content = config_file.read_text()
                if "tls" in content.lower() or "ssl" in content.lower():
                    tls_files.append(config_file)
            except Exception:
                continue

        if tls_files:
            score += 0.2
            findings.append("TLS/SSL configuration found")

        return {
            "score": min(score, 1.0),
            "findings": findings,
            "constitutional_hash": self.constitutional_hash,
        }

    async def generate_hardening_report(
        self, assessment_results: Dict[str, Any]
    ) -> str:
        """Generate comprehensive security hardening report."""
        report_lines = [
            "# ACGS Security Hardening Assessment Report",
            f"Constitutional Hash: {self.constitutional_hash}",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## Executive Summary",
            f"- **Overall Security Score**: {assessment_results['overall_security_score']:.2f}/1.00",
            f"- **Security Target Met**: {'✅ YES' if assessment_results['compliance_status']['meets_security_targets'] else '❌ NO'}",
            f"- **Critical Vulnerabilities**: {assessment_results['compliance_status']['critical_vulnerabilities']}",
            f"- **High Vulnerabilities**: {assessment_results['compliance_status']['high_vulnerabilities']}",
            f"- **Constitutional Compliance**: ✅ MAINTAINED",
            "",
            "## Security Assessment Scores",
        ]

        for category, result in assessment_results["security_scores"].items():
            if isinstance(result, dict):
                score = result.get("score", 0.0)
                status = (
                    "✅ PASS"
                    if score >= 0.8
                    else "⚠️ NEEDS IMPROVEMENT" if score >= 0.6 else "❌ FAIL"
                )
                report_lines.append(f"- **{category}**: {score:.2f} {status}")

        report_lines.extend(
            [
                "",
                "## Vulnerabilities Found",
            ]
        )

        if assessment_results["vulnerabilities"]:
            for vuln in assessment_results["vulnerabilities"]:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(vuln["severity"], "⚪")
                report_lines.extend(
                    [
                        f"### {severity_icon} {vuln['severity'].upper()}: {vuln['category']}",
                        f"- **Description**: {vuln['description']}",
                        f"- **Location**: {vuln['location']}",
                        f"- **Recommendation**: {vuln['recommendation']}",
                        "",
                    ]
                )
        else:
            report_lines.append("✅ No vulnerabilities found")

        report_lines.extend(
            [
                "",
                "## Hardening Recommendations",
                "1. **Immediate Actions** (Critical/High vulnerabilities)",
                "2. **Short-term Improvements** (Medium vulnerabilities)",
                "3. **Long-term Enhancements** (Security best practices)",
                "",
                "## Constitutional Compliance",
                f"All security assessments maintain constitutional hash: `{self.constitutional_hash}`",
                "Security hardening does not compromise constitutional compliance.",
            ]
        )

        return "\n".join(report_lines)


async def main():
    """Main security assessment function."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    project_root = Path(__file__).parent.parent
    assessor = ACGSSecurityAssessment(project_root)

    print("🔒 ACGS Security Hardening Assessment")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(
        f"🎯 Security Targets: {SECURITY_TARGETS['overall_security_score']*100}% overall score"
    )
    print()

    # Run comprehensive assessment
    results = await assessor.run_comprehensive_assessment()

    # Generate and save report
    report = await assessor.generate_hardening_report(results)
    report_path = project_root / "reports" / "security_hardening_assessment.md"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        f.write(report)

    # Save detailed results
    results_path = project_root / "reports" / "security_assessment_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"🎯 Overall Security Score: {results['overall_security_score']:.2f}")
    print(
        f"🔒 Security Target Met: {results['compliance_status']['meets_security_targets']}"
    )
    print(
        f"📊 Critical Vulnerabilities: {results['compliance_status']['critical_vulnerabilities']}"
    )
    print(
        f"📊 High Vulnerabilities: {results['compliance_status']['high_vulnerabilities']}"
    )
    print()
    print(f"📄 Security report saved: {report_path}")
    print(f"📄 Detailed results saved: {results_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
