#!/usr/bin/env python3
"""
ACGS-1 Security Fixes Verification Script

Verifies that HIGH severity security findings have been properly resolved.
Checks for specific security patterns and validates the fixes.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityVerifier:
    """Verifies security fixes in ACGS-1 codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.verification_results = []
        
        # Security patterns that should NOT be found (vulnerabilities)
        self.vulnerability_patterns = {
            'hardcoded_bind_all': r'["\']0\.0\.0\.0["\']',
            'empty_except_pass': r'except[^:]*:\s*\n\s*pass\s*$',
            'pickle_import': r'import\s+pickle(?!\s*#\s*SECURITY)',
            'eval_usage': r'eval\s*\(',
            'exec_usage': r'exec\s*\(',
            'md5_usage': r'hashlib\.md5\(',
            'insecure_random': r'random\.(random|randint|choice)\(',
            'hardcoded_password': r'password\s*=\s*["\'][^"\']+["\']',
            'flask_debug_true': r'debug\s*=\s*True',
            'assert_usage': r'assert\s+[^#]',
            'input_usage': r'\binput\s*\(',
            'mktemp_usage': r'tempfile\.mktemp\(',
            'unverified_ssl': r'ssl\._create_unverified_context\(\)'
        }
        
        # Security patterns that SHOULD be found (fixes)
        self.security_patterns = {
            'secure_bind': r'127\.0\.0\.1',
            'proper_logging': r'logger\.(warning|error|info)',
            'json_usage': r'import\s+json',
            'sha256_usage': r'hashlib\.sha256\(',
            'getpass_usage': r'getpass\.getpass\(',
            'environment_vars': r'os\.getenv\(',
            'secure_temp': r'tempfile\.mkstemp\(',
            'ssl_context': r'ssl\.create_default_context\(\)'
        }
        
        # Files that were processed
        self.processed_files = [
            "services/core/constitutional-ai/ac_service/app/main.py",
            "services/core/governance-synthesis/gs_service/app/core/llm_reliability_framework.py",
            "services/core/governance-synthesis/gs_service/app/core/opa_integration.py",
            "services/core/governance-synthesis/gs_service/app/services/advanced_cache.py"
        ]
    
    def verify_security_fixes(self) -> Dict[str, Any]:
        """Verify all security fixes"""
        logger.info("🔍 Verifying ACGS-1 Security Fixes")
        logger.info("=" * 50)
        
        results = {
            "status": "success",
            "vulnerabilities_found": [],
            "security_improvements": [],
            "files_verified": 0,
            "total_issues": 0,
            "resolved_issues": 0
        }
        
        try:
            # Verify each processed file
            for file_path in self.processed_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    logger.info(f"🔍 Verifying: {file_path}")
                    file_results = self._verify_file(full_path)
                    self.verification_results.append(file_results)
                    results["files_verified"] += 1
                    
                    # Count issues
                    results["total_issues"] += len(file_results["vulnerabilities"])
                    results["resolved_issues"] += len(file_results["security_improvements"])
                    
                    if file_results["vulnerabilities"]:
                        results["vulnerabilities_found"].extend(file_results["vulnerabilities"])
                    
                    if file_results["security_improvements"]:
                        results["security_improvements"].extend(file_results["security_improvements"])
                else:
                    logger.warning(f"⚠️  File not found: {file_path}")
            
            # Verify security infrastructure
            self._verify_security_infrastructure(results)
            
            # Generate final assessment
            if results["vulnerabilities_found"]:
                results["status"] = "issues_found"
                logger.warning(f"⚠️  {len(results['vulnerabilities_found'])} vulnerabilities still found")
            else:
                logger.info("✅ No HIGH severity vulnerabilities found")
            
            logger.info(f"📊 Verification Summary:")
            logger.info(f"   Files Verified: {results['files_verified']}")
            logger.info(f"   Security Improvements: {len(results['security_improvements'])}")
            logger.info(f"   Remaining Vulnerabilities: {len(results['vulnerabilities_found'])}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _verify_file(self, file_path: Path) -> Dict[str, Any]:
        """Verify security fixes in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_results = {
                "file": str(file_path),
                "vulnerabilities": [],
                "security_improvements": []
            }
            
            # Check for remaining vulnerabilities
            for vuln_name, pattern in self.vulnerability_patterns.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = self._get_line_number(content, match.start())
                    file_results["vulnerabilities"].append({
                        "type": vuln_name,
                        "line": line_num,
                        "code": match.group(0).strip()
                    })
                    logger.warning(f"  ⚠️  {vuln_name} found at line {line_num}")
            
            # Check for security improvements
            for security_name, pattern in self.security_patterns.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = self._get_line_number(content, match.start())
                    file_results["security_improvements"].append({
                        "type": security_name,
                        "line": line_num,
                        "code": match.group(0).strip()
                    })
                    logger.info(f"  ✅ {security_name} found at line {line_num}")
            
            if not file_results["vulnerabilities"] and not file_results["security_improvements"]:
                logger.info(f"  ℹ️  No security patterns found in {file_path.name}")
            
            return file_results
            
        except Exception as e:
            logger.error(f"❌ Failed to verify {file_path}: {e}")
            return {
                "file": str(file_path),
                "error": str(e),
                "vulnerabilities": [],
                "security_improvements": []
            }
    
    def _verify_security_infrastructure(self, results: Dict[str, Any]):
        """Verify security infrastructure components"""
        logger.info("🔍 Verifying security infrastructure...")
        
        # Check security configuration
        security_config = self.project_root / "config" / "security.py"
        if security_config.exists():
            logger.info("  ✅ Security configuration found")
            results["security_improvements"].append({
                "type": "security_config",
                "description": "Security configuration framework created"
            })
        else:
            logger.warning("  ⚠️  Security configuration not found")
            results["vulnerabilities_found"].append({
                "type": "missing_security_config",
                "description": "Security configuration framework missing"
            })
        
        # Check security middleware
        security_middleware = self.project_root / "services" / "shared" / "middleware" / "security.py"
        if security_middleware.exists():
            logger.info("  ✅ Security middleware found")
            results["security_improvements"].append({
                "type": "security_middleware",
                "description": "Security middleware implemented"
            })
        else:
            logger.warning("  ⚠️  Security middleware not found")
            results["vulnerabilities_found"].append({
                "type": "missing_security_middleware",
                "description": "Security middleware missing"
            })
        
        # Check security requirements
        security_requirements = self.project_root / "requirements-security.txt"
        if security_requirements.exists():
            logger.info("  ✅ Security requirements found")
            results["security_improvements"].append({
                "type": "security_requirements",
                "description": "Security-focused requirements created"
            })
        else:
            logger.warning("  ⚠️  Security requirements not found")
            results["vulnerabilities_found"].append({
                "type": "missing_security_requirements",
                "description": "Security requirements missing"
            })
        
        # Check ELK security monitoring
        elk_config = self.project_root / "infrastructure" / "monitoring" / "docker-compose.elk-security.yml"
        if elk_config.exists():
            logger.info("  ✅ ELK security monitoring configuration found")
            results["security_improvements"].append({
                "type": "elk_security_monitoring",
                "description": "ELK security monitoring stack configured"
            })
        else:
            logger.warning("  ⚠️  ELK security monitoring not found")
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for a character position"""
        return content[:position].count('\n') + 1
    
    def generate_report(self) -> str:
        """Generate detailed verification report"""
        report = []
        report.append("# ACGS-1 Security Fixes Verification Report")
        report.append(f"Generated: {os.popen('date').read().strip()}")
        report.append("")
        
        # Summary
        total_vulns = sum(len(r.get("vulnerabilities", [])) for r in self.verification_results)
        total_improvements = sum(len(r.get("security_improvements", [])) for r in self.verification_results)
        
        report.append("## Summary")
        report.append(f"- Files Verified: {len(self.verification_results)}")
        report.append(f"- Vulnerabilities Found: {total_vulns}")
        report.append(f"- Security Improvements: {total_improvements}")
        report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        for result in self.verification_results:
            file_name = Path(result["file"]).name
            report.append(f"### {file_name}")
            
            if result.get("error"):
                report.append(f"❌ Error: {result['error']}")
            else:
                if result["vulnerabilities"]:
                    report.append("**Vulnerabilities Found:**")
                    for vuln in result["vulnerabilities"]:
                        report.append(f"- Line {vuln['line']}: {vuln['type']} - `{vuln['code']}`")
                
                if result["security_improvements"]:
                    report.append("**Security Improvements:**")
                    for improvement in result["security_improvements"]:
                        report.append(f"- Line {improvement['line']}: {improvement['type']} - `{improvement['code']}`")
                
                if not result["vulnerabilities"] and not result["security_improvements"]:
                    report.append("✅ No security issues found")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python verify_security_fixes.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    
    if not os.path.exists(project_root):
        print(f"Error: Project root '{project_root}' does not exist")
        sys.exit(1)
    
    # Run verification
    verifier = SecurityVerifier(project_root)
    results = verifier.verify_security_fixes()
    
    # Save results
    results_file = Path(project_root) / "security_verification_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = verifier.generate_report()
    report_file = Path(project_root) / "security_verification_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"📄 Results saved to: {results_file}")
    logger.info(f"📄 Report saved to: {report_file}")
    
    if results["status"] == "success":
        print("✅ Security verification completed successfully!")
        print(f"📊 {len(results['security_improvements'])} security improvements verified")
        if results["vulnerabilities_found"]:
            print(f"⚠️  {len(results['vulnerabilities_found'])} issues still need attention")
        sys.exit(0)
    else:
        print("❌ Security verification found issues!")
        print(f"🔍 Check {report_file} for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
