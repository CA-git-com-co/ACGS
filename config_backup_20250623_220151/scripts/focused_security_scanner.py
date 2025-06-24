#!/usr/bin/env python3
"""
ACGS-1 Focused Security Scanner

A fast, targeted security scanner that focuses on critical security issues
in the ACGS-1 system without scanning the entire codebase.
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/focused_security_scan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FocusedSecurityScanner:
    """Focused security scanner for ACGS-1."""
    
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.scan_id = f"focused_security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "scan_id": self.scan_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": str(self.project_root),
            "scans": {},
            "summary": {
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "total_findings": 0
            },
            "compliance_status": "UNKNOWN",
            "recommendations": []
        }
        
        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("reports/security", exist_ok=True)
    
    def run_focused_scan(self) -> Dict[str, Any]:
        """Run focused security scan on critical components."""
        logger.info(f"🔍 Starting focused security scan: {self.scan_id}")
        
        # Run targeted scans
        self._run_targeted_bandit_scan()
        self._run_safety_scan()
        self._run_service_security_check()
        self._run_infrastructure_scan()
        self._run_configuration_scan()
        
        # Generate assessment
        self._assess_compliance()
        self._generate_recommendations()
        self._save_results()
        
        logger.info(f"🎯 Focused security scan completed: {self.scan_id}")
        return self.results
    
    def _run_targeted_bandit_scan(self) -> None:
        """Run Bandit scan on critical directories only."""
        try:
            logger.info("🔍 Running targeted Bandit scan...")
            
            # Focus on critical directories
            target_dirs = [
                "services/shared",
                "services/core",
                "scripts",
                "core"
            ]
            
            all_findings = []
            
            for target_dir in target_dirs:
                target_path = self.project_root / target_dir
                if not target_path.exists():
                    continue
                
                cmd = [
                    "/home/dislove/.local/bin/bandit", "-r", str(target_path),
                    "-f", "json", "-q"  # Quiet mode for faster execution
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.stdout:
                    try:
                        bandit_results = json.loads(result.stdout)
                        
                        for result_item in bandit_results.get("results", []):
                            severity = result_item.get("issue_severity", "UNKNOWN").upper()
                            all_findings.append({
                                "file": result_item.get("filename"),
                                "line": result_item.get("line_number"),
                                "severity": severity,
                                "confidence": result_item.get("issue_confidence", "UNKNOWN").upper(),
                                "test_id": result_item.get("test_id"),
                                "test_name": result_item.get("test_name"),
                                "issue_text": result_item.get("issue_text"),
                                "directory": target_dir
                            })
                            
                            # Update summary
                            if severity == "HIGH":
                                self.results["summary"]["high_findings"] += 1
                            elif severity == "MEDIUM":
                                self.results["summary"]["medium_findings"] += 1
                            elif severity == "LOW":
                                self.results["summary"]["low_findings"] += 1
                    
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse Bandit results for {target_dir}")
            
            self.results["scans"]["bandit_targeted"] = {
                "status": "SUCCESS",
                "tool": "bandit",
                "target_directories": target_dirs,
                "findings_count": len(all_findings),
                "findings": all_findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Targeted Bandit scan completed: {len(all_findings)} findings")
            
        except Exception as e:
            logger.error(f"❌ Targeted Bandit scan failed: {e}")
            self.results["scans"]["bandit_targeted"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _run_safety_scan(self) -> None:
        """Run Safety scan for Python dependencies."""
        try:
            logger.info("🔍 Running Safety scan...")
            
            cmd = ["/home/dislove/.local/bin/safety", "check", "--json"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            findings = []
            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)
                    
                    for vuln in safety_results:
                        findings.append({
                            "package": vuln.get("package_name"),
                            "version": vuln.get("analyzed_version"),
                            "vulnerability_id": vuln.get("vulnerability_id"),
                            "advisory": vuln.get("advisory"),
                            "severity": "HIGH",
                            "cve": vuln.get("cve")
                        })
                        self.results["summary"]["high_findings"] += 1
                
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Safety results")
            
            self.results["scans"]["safety"] = {
                "status": "SUCCESS",
                "tool": "safety",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Safety scan completed: {len(findings)} findings")
            
        except Exception as e:
            logger.error(f"❌ Safety scan failed: {e}")
            self.results["scans"]["safety"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _run_service_security_check(self) -> None:
        """Run security check on running services."""
        try:
            logger.info("🔍 Running service security check...")
            
            import requests
            
            services = [
                ("auth", 8000), ("ac", 8001), ("integrity", 8002),
                ("fv", 8003), ("gs", 8004), ("pgc", 8005), ("ec", 8006)
            ]
            
            findings = []
            
            for service_name, port in services:
                try:
                    # Check health endpoint
                    response = requests.get(f"http://localhost:{port}/health", timeout=3)
                    headers = dict(response.headers)
                    
                    # Check for missing security headers
                    required_headers = [
                        "X-Content-Type-Options",
                        "X-Frame-Options", 
                        "X-XSS-Protection",
                        "Strict-Transport-Security",
                        "Content-Security-Policy"
                    ]
                    
                    missing_headers = []
                    for header in required_headers:
                        if header not in headers:
                            missing_headers.append(header)
                    
                    if missing_headers:
                        findings.append({
                            "service": service_name,
                            "port": port,
                            "type": "missing_security_headers",
                            "severity": "MEDIUM",
                            "issue": f"Missing security headers: {', '.join(missing_headers)}",
                            "missing_headers": missing_headers,
                            "recommendation": "Implement security middleware"
                        })
                        self.results["summary"]["medium_findings"] += 1
                    
                    # Check for HTTP instead of HTTPS
                    if response.url.startswith("http://"):
                        findings.append({
                            "service": service_name,
                            "port": port,
                            "type": "insecure_protocol",
                            "severity": "HIGH",
                            "issue": "Service accessible over HTTP instead of HTTPS",
                            "recommendation": "Enforce HTTPS for all services"
                        })
                        self.results["summary"]["high_findings"] += 1
                
                except Exception as e:
                    findings.append({
                        "service": service_name,
                        "port": port,
                        "type": "service_unavailable",
                        "severity": "LOW",
                        "issue": f"Service not accessible: {e}",
                        "recommendation": "Verify service is running and accessible"
                    })
                    self.results["summary"]["low_findings"] += 1
            
            self.results["scans"]["service_security"] = {
                "status": "SUCCESS",
                "tool": "service-security-check",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Service security check completed: {len(findings)} findings")
            
        except Exception as e:
            logger.error(f"❌ Service security check failed: {e}")
            self.results["scans"]["service_security"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _run_infrastructure_scan(self) -> None:
        """Run infrastructure security scan."""
        try:
            logger.info("🔍 Running infrastructure scan...")
            
            findings = []
            
            # Check SSL/TLS configuration
            ssl_cert_path = self.project_root / "ssl" / "certs" / "acgs.pem"
            ssl_key_path = self.project_root / "ssl" / "private" / "acgs.key"
            
            if not ssl_cert_path.exists():
                findings.append({
                    "type": "ssl_configuration",
                    "severity": "HIGH",
                    "issue": "SSL certificate not found",
                    "file": str(ssl_cert_path),
                    "recommendation": "Generate or install SSL certificate"
                })
                self.results["summary"]["high_findings"] += 1
            
            if not ssl_key_path.exists():
                findings.append({
                    "type": "ssl_configuration",
                    "severity": "HIGH",
                    "issue": "SSL private key not found",
                    "file": str(ssl_key_path),
                    "recommendation": "Generate or install SSL private key"
                })
                self.results["summary"]["high_findings"] += 1
            
            # Check for exposed configuration files in root
            sensitive_patterns = ["*.env", "*.key", "*.pem", "secrets.*", "config.json"]
            
            for pattern in sensitive_patterns:
                for found_file in self.project_root.glob(pattern):
                    if found_file.is_file():
                        findings.append({
                            "type": "sensitive_file_exposure",
                            "severity": "MEDIUM",
                            "issue": f"Potentially sensitive file in root: {found_file.name}",
                            "file": str(found_file.relative_to(self.project_root)),
                            "recommendation": "Move to secure location or add to .gitignore"
                        })
                        self.results["summary"]["medium_findings"] += 1
            
            self.results["scans"]["infrastructure"] = {
                "status": "SUCCESS",
                "tool": "infrastructure-scan",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Infrastructure scan completed: {len(findings)} findings")
            
        except Exception as e:
            logger.error(f"❌ Infrastructure scan failed: {e}")
            self.results["scans"]["infrastructure"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _run_configuration_scan(self) -> None:
        """Run configuration security scan."""
        try:
            logger.info("🔍 Running configuration scan...")

            findings = []

            # Check for hardcoded secrets in configuration files
            config_files = [
                "config/security.py",
                "services/shared/security_config.py",
                "services/shared/config.py"
            ]

            secret_patterns = [
                "password", "secret", "key", "token", "api_key",
                "private_key", "access_key", "auth_token"
            ]

            for config_file in config_files:
                config_path = self.project_root / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read().lower()

                            for pattern in secret_patterns:
                                if f"{pattern}=" in content or f'"{pattern}"' in content:
                                    findings.append({
                                        "type": "potential_hardcoded_secret",
                                        "severity": "MEDIUM",
                                        "issue": f"Potential hardcoded secret pattern: {pattern}",
                                        "file": config_file,
                                        "recommendation": "Use environment variables or secure vault"
                                    })
                                    self.results["summary"]["medium_findings"] += 1

                    except Exception as e:
                        logger.warning(f"Could not read {config_file}: {e}")

            self.results["scans"]["configuration"] = {
                "status": "SUCCESS",
                "tool": "configuration-scan",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info(f"✅ Configuration scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Configuration scan failed: {e}")
            self.results["scans"]["configuration"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        # Update total findings
        self.results["summary"]["total_findings"] = (
            self.results["summary"]["critical_findings"] +
            self.results["summary"]["high_findings"] +
            self.results["summary"]["medium_findings"] +
            self.results["summary"]["low_findings"]
        )

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif high > 10:
            self.results["compliance_status"] = "NON_COMPLIANT_HIGH"
        elif high > 0:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate security recommendations based on findings."""
        recommendations = []

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]
        medium = self.results["summary"]["medium_findings"]

        if critical > 0:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Immediately address all critical security vulnerabilities",
                "timeline": "Within 24 hours",
                "impact": "System compromise risk"
            })

        if high > 0:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Address {high} high-severity security findings",
                "timeline": "Within 1 week",
                "impact": "Significant security risk"
            })

        # Specific recommendations based on scan results
        service_scan = self.results["scans"].get("service_security", {})
        if service_scan.get("status") == "SUCCESS":
            missing_headers_count = sum(1 for finding in service_scan.get("findings", [])
                                      if finding.get("type") == "missing_security_headers")
            if missing_headers_count > 0:
                recommendations.append({
                    "priority": "HIGH",
                    "action": f"Implement security middleware on {missing_headers_count} services",
                    "timeline": "Within 3 days",
                    "impact": "XSS, CSRF, and other web vulnerabilities"
                })

        # SSL/TLS recommendations
        infra_scan = self.results["scans"].get("infrastructure", {})
        if infra_scan.get("status") == "SUCCESS":
            ssl_issues = sum(1 for finding in infra_scan.get("findings", [])
                           if finding.get("type") == "ssl_configuration")
            if ssl_issues > 0:
                recommendations.append({
                    "priority": "HIGH",
                    "action": "Configure SSL/TLS certificates for secure communication",
                    "timeline": "Within 2 days",
                    "impact": "Data transmission security"
                })

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save scan results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.scan_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.scan_id}_summary.json"
        summary = {
            "scan_id": self.scan_id,
            "timestamp": self.results["timestamp"],
            "summary": self.results["summary"],
            "compliance_status": self.results["compliance_status"],
            "recommendations": self.results["recommendations"]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📊 Results saved to {results_file}")
        logger.info(f"📋 Summary saved to {summary_file}")


def main():
    """Main execution function."""
    scanner = FocusedSecurityScanner()

    try:
        results = scanner.run_focused_scan()

        # Print summary
        print("\n" + "="*80)
        print("🔍 ACGS-1 FOCUSED SECURITY SCAN RESULTS")
        print("="*80)
        print(f"Scan ID: {results['scan_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nFindings Summary:")
        print(f"  Critical: {results['summary']['critical_findings']}")
        print(f"  High:     {results['summary']['high_findings']}")
        print(f"  Medium:   {results['summary']['medium_findings']}")
        print(f"  Low:      {results['summary']['low_findings']}")
        print(f"  Total:    {results['summary']['total_findings']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nScan Status:")
        for scan_name, scan_result in results['scans'].items():
            status = scan_result.get('status', 'UNKNOWN')
            findings_count = scan_result.get('findings_count', 0)
            print(f"  {scan_name}: {status} ({findings_count} findings)")

        print("="*80)

        return 0 if results['summary']['critical_findings'] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

    def _run_configuration_scan(self) -> None:
        """Run configuration security scan."""
        try:
            logger.info("🔍 Running configuration scan...")

            findings = []

            # Check for hardcoded secrets in configuration files
            config_files = [
                "config/security.py",
                "services/shared/security_config.py",
                "services/shared/config.py"
            ]

            secret_patterns = [
                "password", "secret", "key", "token", "api_key",
                "private_key", "access_key", "auth_token"
            ]

            for config_file in config_files:
                config_path = self.project_root / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read().lower()

                            for pattern in secret_patterns:
                                if f"{pattern}=" in content or f'"{pattern}"' in content:
                                    findings.append({
                                        "type": "potential_hardcoded_secret",
                                        "severity": "MEDIUM",
                                        "issue": f"Potential hardcoded secret pattern: {pattern}",
                                        "file": config_file,
                                        "recommendation": "Use environment variables or secure vault"
                                    })
                                    self.results["summary"]["medium_findings"] += 1

                    except Exception as e:
                        logger.warning(f"Could not read {config_file}: {e}")

            # Check for default/weak configurations
            security_middleware_path = self.project_root / "services/shared/security_middleware.py"
            if security_middleware_path.exists():
                try:
                    with open(security_middleware_path, 'r') as f:
                        content = f.read()

                        # Check for weak session settings
                        if "max_age=3600" in content:
                            findings.append({
                                "type": "weak_session_config",
                                "severity": "LOW",
                                "issue": "Session timeout set to 1 hour (consider shorter for high-security)",
                                "file": "services/shared/security_middleware.py",
                                "recommendation": "Consider shorter session timeout for sensitive operations"
                            })
                            self.results["summary"]["low_findings"] += 1

                        # Check for development mode indicators
                        if "development" in content.lower() or "debug=true" in content.lower():
                            findings.append({
                                "type": "development_mode_indicators",
                                "severity": "MEDIUM",
                                "issue": "Development mode indicators found in security middleware",
                                "file": "services/shared/security_middleware.py",
                                "recommendation": "Ensure production mode is enabled"
                            })
                            self.results["summary"]["medium_findings"] += 1

                except Exception as e:
                    logger.warning(f"Could not analyze security middleware: {e}")

            self.results["scans"]["configuration"] = {
                "status": "SUCCESS",
                "tool": "configuration-scan",
                "findings_count": len(findings),
                "findings": findings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info(f"✅ Configuration scan completed: {len(findings)} findings")

        except Exception as e:
            logger.error(f"❌ Configuration scan failed: {e}")
            self.results["scans"]["configuration"] = {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _assess_compliance(self) -> None:
        """Assess overall compliance status."""
        # Update total findings
        self.results["summary"]["total_findings"] = (
            self.results["summary"]["critical_findings"] +
            self.results["summary"]["high_findings"] +
            self.results["summary"]["medium_findings"] +
            self.results["summary"]["low_findings"]
        )

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]

        if critical > 0:
            self.results["compliance_status"] = "NON_COMPLIANT_CRITICAL"
        elif high > 10:
            self.results["compliance_status"] = "NON_COMPLIANT_HIGH"
        elif high > 0:
            self.results["compliance_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["compliance_status"] = "COMPLIANT"

    def _generate_recommendations(self) -> None:
        """Generate security recommendations based on findings."""
        recommendations = []

        critical = self.results["summary"]["critical_findings"]
        high = self.results["summary"]["high_findings"]
        medium = self.results["summary"]["medium_findings"]

        if critical > 0:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Immediately address all critical security vulnerabilities",
                "timeline": "Within 24 hours",
                "impact": "System compromise risk"
            })

        if high > 0:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Address {high} high-severity security findings",
                "timeline": "Within 1 week",
                "impact": "Significant security risk"
            })

        # Specific recommendations based on scan results
        service_scan = self.results["scans"].get("service_security", {})
        if service_scan.get("status") == "SUCCESS":
            missing_headers_count = sum(1 for finding in service_scan.get("findings", [])
                                      if finding.get("type") == "missing_security_headers")
            if missing_headers_count > 0:
                recommendations.append({
                    "priority": "HIGH",
                    "action": f"Implement security middleware on {missing_headers_count} services",
                    "timeline": "Within 3 days",
                    "impact": "XSS, CSRF, and other web vulnerabilities"
                })

        # SSL/TLS recommendations
        infra_scan = self.results["scans"].get("infrastructure", {})
        if infra_scan.get("status") == "SUCCESS":
            ssl_issues = sum(1 for finding in infra_scan.get("findings", [])
                           if finding.get("type") == "ssl_configuration")
            if ssl_issues > 0:
                recommendations.append({
                    "priority": "HIGH",
                    "action": "Configure SSL/TLS certificates for secure communication",
                    "timeline": "Within 2 days",
                    "impact": "Data transmission security"
                })

        self.results["recommendations"] = recommendations

    def _save_results(self) -> None:
        """Save scan results to files."""
        # Save detailed results
        results_file = f"reports/security/{self.scan_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save summary report
        summary_file = f"reports/security/{self.scan_id}_summary.json"
        summary = {
            "scan_id": self.scan_id,
            "timestamp": self.results["timestamp"],
            "summary": self.results["summary"],
            "compliance_status": self.results["compliance_status"],
            "recommendations": self.results["recommendations"]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📊 Results saved to {results_file}")
        logger.info(f"📋 Summary saved to {summary_file}")


def main():
    """Main execution function."""
    scanner = FocusedSecurityScanner()

    try:
        results = scanner.run_focused_scan()

        # Print summary
        print("\n" + "="*80)
        print("🔍 ACGS-1 FOCUSED SECURITY SCAN RESULTS")
        print("="*80)
        print(f"Scan ID: {results['scan_id']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Compliance Status: {results['compliance_status']}")
        print("\nFindings Summary:")
        print(f"  Critical: {results['summary']['critical_findings']}")
        print(f"  High:     {results['summary']['high_findings']}")
        print(f"  Medium:   {results['summary']['medium_findings']}")
        print(f"  Low:      {results['summary']['low_findings']}")
        print(f"  Total:    {results['summary']['total_findings']}")

        print("\nTop Priority Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Timeline: {rec['timeline']}")
            print(f"     Impact: {rec['impact']}")

        print("\nScan Status:")
        for scan_name, scan_result in results['scans'].items():
            status = scan_result.get('status', 'UNKNOWN')
            findings_count = scan_result.get('findings_count', 0)
            print(f"  {scan_name}: {status} ({findings_count} findings)")

        print("="*80)

        return 0 if results['summary']['critical_findings'] == 0 else 1

    except Exception as e:
        logger.error(f"❌ Security scan failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
