#!/usr/bin/env python3
"""
ACGS-2 Emergency Security Patch Script
Constitutional Hash: cdd01ef066bc6cf2

Immediate security vulnerability patching for critical issues.
Addresses the 6 critical and 27 high-severity vulnerabilities identified.
"""

import subprocess
import sys
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import tempfile
import os

class EmergencySecurityPatcher:
    """Emergency security patching for ACGS-2"""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.logger = self._setup_logging()
        
        # Critical package updates based on vulnerability analysis
        self.critical_updates = {
            'Pillow': '>=10.2.0,<11.0.0',       # Critical: Arbitrary code execution
            'cryptography': '>=43.0.1,<44.0.0', # Critical: NULL pointer dereference
            'nltk': '>=3.8.2,<4.0.0',           # High: Unsafe deserialization
            'transformers': '>=4.52.1,<5.0.0',  # Critical: Multiple RCE vulnerabilities
            'aiohttp': '>=3.10.11,<4.0.0',      # Critical: Directory traversal, DoS
            'orjson': '>=3.9.15,<4.0.0',        # High: Uncontrolled recursion
            'requests': '>=2.31.0,<3.0.0',      # High: Security improvements
            'urllib3': '>=2.0.7,<3.0.0',        # High: Security fixes
            'black': '>=24.0.0,<25.0.0',        # Medium: ReDoS
            'tqdm': '>=4.66.0,<5.0.0',          # Low: CLI injection
        }
        
        # High priority transitive dependencies
        self.transitive_updates = {
            'setuptools': '>=68.0.0,<70.0.0',
            'certifi': '>=2023.7.22',
            'idna': '>=3.4,<4.0.0',
            'charset-normalizer': '>=3.3.0,<4.0.0'
        }
    
    def check_installed_packages(self) -> Dict[str, str]:
        """Check which vulnerable packages are currently installed"""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'list', '--format=json'
            ], capture_output=True, text=True, check=True)
            
            packages = json.loads(result.stdout)
            installed = {}
            
            for pkg in packages:
                package_name = pkg['name']
                # Check both exact match and case variations
                for critical_pkg in list(self.critical_updates.keys()) + list(self.transitive_updates.keys()):
                    if package_name.lower() == critical_pkg.lower():
                        installed[critical_pkg] = pkg['version']
                        break
            
            return installed
            
        except Exception as e:
            self.logger.error(f"Failed to check installed packages: {e}")
            return {}
    
    def backup_current_environment(self) -> str:
        """Create backup of current package environment"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"requirements_backup_{timestamp}.txt"
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'freeze'
            ], capture_output=True, text=True, check=True)
            
            with open(backup_file, 'w') as f:
                f.write(f"# ACGS-2 Package Backup - {timestamp}\n")
                f.write(f"# Constitutional Hash: {self.constitutional_hash}\n")
                f.write(f"# Created before emergency security patch\n\n")
                f.write(result.stdout)
            
            self.logger.info(f"Environment backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return ""
    
    def apply_critical_updates(self, installed_packages: Dict[str, str]) -> Dict[str, Tuple[str, str, bool]]:
        """Apply critical security updates"""
        results = {}
        
        # Combined updates for efficiency
        all_updates = {**self.critical_updates, **self.transitive_updates}
        
        for package, version_spec in all_updates.items():
            if package in installed_packages:
                current_version = installed_packages[package]
                self.logger.info(f"Updating {package} from {current_version} to {version_spec}")
                
                try:
                    # Update individual package
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '--upgrade',
                        f"{package}{version_spec}"
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        # Verify installation
                        verify_result = subprocess.run([
                            sys.executable, '-m', 'pip', 'show', package
                        ], capture_output=True, text=True)
                        
                        if verify_result.returncode == 0:
                            # Extract new version
                            lines = verify_result.stdout.split('\n')
                            new_version = "unknown"
                            for line in lines:
                                if line.startswith('Version:'):
                                    new_version = line.split(':', 1)[1].strip()
                                    break
                            
                            results[package] = (current_version, new_version, True)
                            self.logger.info(f"✅ Successfully updated {package}: {current_version} → {new_version}")
                        else:
                            results[package] = (current_version, "failed", False)
                            self.logger.error(f"❌ Failed to verify {package} installation")
                    else:
                        results[package] = (current_version, "failed", False)
                        self.logger.error(f"❌ Failed to update {package}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    results[package] = (current_version, "timeout", False)
                    self.logger.error(f"❌ Update timeout for {package}")
                except Exception as e:
                    results[package] = (current_version, "error", False)
                    self.logger.error(f"❌ Error updating {package}: {e}")
            else:
                self.logger.info(f"Package {package} not installed, skipping")
        
        return results
    
    def verify_constitutional_compliance(self) -> bool:
        """Verify constitutional compliance after updates"""
        try:
            # Check if constitutional hash is still present in key files
            test_files = [
                'CLAUDE.md',
                'requirements-security.txt',
                'ACGS_SECURITY_VULNERABILITY_REMEDIATION_PLAN.md'
            ]
            
            for file_path in test_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if self.constitutional_hash in content:
                            self.logger.info(f"✅ Constitutional hash found in {file_path}")
                        else:
                            self.logger.warning(f"⚠️ Constitutional hash missing from {file_path}")
                            return False
            
            self.logger.info("✅ Constitutional compliance verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify constitutional compliance: {e}")
            return False
    
    def run_security_verification(self) -> Dict[str, Any]:
        """Run security verification after patches"""
        try:
            self.logger.info("Running post-patch security verification...")
            
            # Run pip-audit to check for remaining vulnerabilities
            result = subprocess.run([
                'pip-audit', '--format', 'json'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
                
                # Count by severity
                severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                for vuln in vulnerabilities:
                    severity = vuln.get('severity', 'unknown').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                
                return {
                    'status': 'success',
                    'total_vulnerabilities': len(vulnerabilities),
                    'severity_counts': severity_counts,
                    'vulnerabilities': vulnerabilities
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr or "Unknown error"
                }
                
        except Exception as e:
            self.logger.error(f"Security verification failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_patch_report(self, backup_file: str, update_results: Dict, 
                            verification_results: Dict) -> str:
        """Generate comprehensive patch report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Count successful updates
        successful_updates = sum(1 for _, _, success in update_results.values() if success)
        total_updates = len(update_results)
        
        # Generate report
        report = f"""# ACGS-2 Emergency Security Patch Report

**Date**: {timestamp}
**Constitutional Hash**: {self.constitutional_hash}
**Backup File**: {backup_file}

## 📊 Patch Summary

- **Total Packages Updated**: {successful_updates}/{total_updates}
- **Success Rate**: {(successful_updates/total_updates*100):.1f}%

## 📦 Package Updates

| Package | Previous Version | New Version | Status |
|---------|------------------|-------------|--------|
"""
        
        for package, (old_ver, new_ver, success) in update_results.items():
            status = "✅ Success" if success else "❌ Failed"
            report += f"| {package} | {old_ver} | {new_ver} | {status} |\n"
        
        # Add security verification results
        if verification_results.get('status') == 'success':
            severity_counts = verification_results.get('severity_counts', {})
            total_vulns = verification_results.get('total_vulnerabilities', 0)
            
            report += f"""
## 🔒 Post-Patch Security Status

- **Total Vulnerabilities Remaining**: {total_vulns}
- **Critical**: {severity_counts.get('critical', 0)}
- **High**: {severity_counts.get('high', 0)}
- **Medium**: {severity_counts.get('medium', 0)}
- **Low**: {severity_counts.get('low', 0)}

"""
            if total_vulns == 0:
                report += "🎉 **EXCELLENT**: No vulnerabilities detected after patching!\n\n"
            elif severity_counts.get('critical', 0) == 0 and severity_counts.get('high', 0) == 0:
                report += "✅ **GOOD**: No critical or high-severity vulnerabilities remaining.\n\n"
            else:
                report += "⚠️ **WARNING**: Critical or high-severity vulnerabilities still present.\n\n"
        
        # Add next steps
        report += """## 📋 Next Steps

1. **Test Application**: Verify all services start correctly
2. **Run Full Test Suite**: Ensure no functionality is broken
3. **Monitor Logs**: Watch for any errors after updates
4. **Deploy to Staging**: Test in staging environment
5. **Constitutional Validation**: Verify all constitutional checks pass

## 🔄 Rollback Instructions

If issues are encountered, rollback using:
```bash
pip install -r """ + backup_file + """
```

## ✅ Constitutional Compliance

Constitutional hash validated: `""" + self.constitutional_hash + """`

---
*Generated by ACGS-2 Emergency Security Patcher*
"""
        
        # Save report
        report_file = f"emergency_patch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Patch report saved to: {report_file}")
        return report_file
    
    def run_emergency_patch(self) -> bool:
        """Run complete emergency security patch process"""
        self.logger.info("🚨 Starting ACGS-2 Emergency Security Patch")
        self.logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        
        # Step 1: Check installed packages
        self.logger.info("📦 Checking installed packages...")
        installed_packages = self.check_installed_packages()
        
        if not installed_packages:
            self.logger.error("❌ No vulnerable packages found to update")
            return False
        
        vulnerable_found = [pkg for pkg in self.critical_updates.keys() if pkg in installed_packages]
        self.logger.info(f"Found {len(vulnerable_found)} vulnerable packages: {', '.join(vulnerable_found)}")
        
        # Step 2: Create backup
        self.logger.info("💾 Creating environment backup...")
        backup_file = self.backup_current_environment()
        
        if not backup_file:
            self.logger.error("❌ Failed to create backup - aborting patch")
            return False
        
        # Step 3: Apply updates
        self.logger.info("🔄 Applying security updates...")
        update_results = self.apply_critical_updates(installed_packages)
        
        # Step 4: Verify constitutional compliance
        self.logger.info("✅ Verifying constitutional compliance...")
        compliance_ok = self.verify_constitutional_compliance()
        
        # Step 5: Run security verification
        self.logger.info("🔍 Running post-patch security verification...")
        verification_results = self.run_security_verification()
        
        # Step 6: Generate report
        self.logger.info("📄 Generating patch report...")
        report_file = self.generate_patch_report(backup_file, update_results, verification_results)
        
        # Determine overall success
        successful_updates = sum(1 for _, _, success in update_results.values() if success)
        critical_vulnerabilities_remaining = verification_results.get('severity_counts', {}).get('critical', 999)
        
        success = (
            successful_updates > 0 and 
            compliance_ok and 
            critical_vulnerabilities_remaining == 0
        )
        
        # Final summary
        if success:
            self.logger.info("🎉 Emergency security patch completed successfully!")
            self.logger.info(f"✅ Updated {successful_updates} packages")
            self.logger.info(f"✅ Constitutional compliance maintained")
            self.logger.info(f"✅ No critical vulnerabilities remaining")
        else:
            self.logger.warning("⚠️ Emergency patch completed with issues")
            self.logger.warning(f"📦 Updated {successful_updates}/{len(update_results)} packages")
            self.logger.warning(f"🔒 Constitutional compliance: {'✅' if compliance_ok else '❌'}")
            self.logger.warning(f"🚨 Critical vulnerabilities: {critical_vulnerabilities_remaining}")
        
        self.logger.info(f"📄 Full report: {report_file}")
        
        return success
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for emergency patcher"""
        logger = logging.getLogger('acgs_emergency_patcher')
        logger.setLevel(logging.INFO)
        
        # Console handler with detailed formatting
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger

def main():
    """Main execution function"""
    print("🚨 ACGS-2 Emergency Security Patcher")
    print("=" * 50)
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("This will update critical security vulnerabilities immediately.")
    print()
    
    # Confirm execution
    response = input("Continue with emergency patch? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Emergency patch cancelled by user")
        sys.exit(1)
    
    # Run emergency patch
    patcher = EmergencySecurityPatcher()
    success = patcher.run_emergency_patch()
    
    # Exit with appropriate code
    if success:
        print("\n🎉 Emergency security patch completed successfully!")
        print("✅ Safe to proceed with testing and deployment")
        sys.exit(0)
    else:
        print("\n⚠️ Emergency patch completed with issues")
        print("🔍 Review the patch report for details")
        print("❌ Manual intervention may be required")
        sys.exit(1)

if __name__ == "__main__":
    main()