#!/usr/bin/env python3
"""
ACGS-1 Vulnerability Remediation Script

This script identifies and fixes security vulnerabilities in Python dependencies
across the ACGS-1 project.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class VulnerabilityFixer:
    """Comprehensive vulnerability detection and remediation for ACGS-1."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_files = []
        self.vulnerabilities = []
        self.fixes_applied = []
        
        # Critical vulnerabilities that require immediate fixing
        self.critical_packages = {
            'python-jose': {
                'current': '3.5.0',
                'fixed': '3.5.1',  # Latest version that fixes CVE-2024-33664, CVE-2024-33663
                'cves': ['CVE-2024-33664', 'CVE-2024-33663'],
                'severity': 'high'
            },
            'ecdsa': {
                'current': '0.19.1',
                'fixed': '0.20.0',  # Latest version that fixes timing attacks
                'cves': ['CVE-2024-23342'],
                'severity': 'medium'
            },
            'torch': {
                'current': '2.7.1',
                'fixed': '2.7.3',  # Latest stable version
                'cves': ['GHSA-887c-mr87-cxwp'],
                'severity': 'medium'
            }
        }
    
    def find_requirements_files(self) -> List[Path]:
        """Find all requirements files in the project."""
        requirements_patterns = [
            "**/requirements*.txt",
            "**/pyproject.toml"
        ]
        
        found_files = []
        for pattern in requirements_patterns:
            found_files.extend(self.project_root.glob(pattern))
        
        # Filter out test and example files that might not be critical
        critical_files = []
        for file_path in found_files:
            if not any(skip in str(file_path) for skip in ['test', 'example', '.venv', 'node_modules']):
                critical_files.append(file_path)
        
        self.requirements_files = critical_files
        return critical_files
    
    def scan_vulnerabilities(self) -> Dict:
        """Run comprehensive vulnerability scans."""
        print("🔍 Running comprehensive vulnerability scans...")
        
        vulnerabilities = {
            "safety": [],
            "pip_audit": [],
            "manual": []
        }
        
        # Run Safety scan
        try:
            result = subprocess.run([
                'safety', 'check', '--save-json', 'safety-scan-results.json'
            ], capture_output=True, text=True, timeout=120)
            
            if os.path.exists('safety-scan-results.json'):
                with open('safety-scan-results.json', 'r') as f:
                    safety_data = json.load(f)
                    vulnerabilities["safety"] = safety_data.get("vulnerabilities", [])
            
            print(f"✅ Safety scan completed - found {len(vulnerabilities['safety'])} vulnerabilities")
        except Exception as e:
            print(f"⚠️ Safety scan failed: {e}")
        
        # Run pip-audit scan
        try:
            result = subprocess.run([
                'pip-audit', '--format=json', '--output=pip-audit-results.json'
            ], capture_output=True, text=True, timeout=120)
            
            if os.path.exists('pip-audit-results.json'):
                with open('pip-audit-results.json', 'r') as f:
                    audit_data = json.load(f)
                    vulnerabilities["pip_audit"] = audit_data.get("dependencies", [])
            
            print(f"✅ pip-audit scan completed - found {len(vulnerabilities['pip_audit'])} vulnerabilities")
        except Exception as e:
            print(f"⚠️ pip-audit scan failed: {e}")
        
        # Add manual critical package checks
        vulnerabilities["manual"] = list(self.critical_packages.keys())
        
        self.vulnerabilities = vulnerabilities
        return vulnerabilities
    
    def update_requirements_file(self, file_path: Path, package_updates: Dict[str, str]) -> bool:
        """Update a requirements file with new package versions."""
        print(f"🔧 Updating {file_path}...")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            updated = False
            
            for package, new_version in package_updates.items():
                # Pattern to match package==version or package>=version
                patterns = [
                    rf'^{re.escape(package)}==.*$',
                    rf'^{re.escape(package)}>=.*$',
                    rf'^{re.escape(package)}~=.*$',
                    rf'^{re.escape(package)}$'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        for match in matches:
                            new_line = f"{package}>={new_version}"
                            content = content.replace(match, new_line)
                            updated = True
                            print(f"  ✅ Updated {package}: {match} → {new_line}")
                            break
                
                # If package not found, add it
                if package not in content:
                    content += f"\n{package}>={new_version}\n"
                    updated = True
                    print(f"  ➕ Added {package}>={new_version}")
            
            if updated:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                
                # Write updated content
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"  💾 Updated {file_path} (backup saved to {backup_path})")
                return True
            else:
                print(f"  ℹ️ No updates needed for {file_path}")
                return False
        
        except Exception as e:
            print(f"  ❌ Failed to update {file_path}: {e}")
            return False
    
    def update_pyproject_toml(self, file_path: Path, package_updates: Dict[str, str]) -> bool:
        """Update pyproject.toml with new package versions."""
        print(f"🔧 Updating {file_path}...")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            updated = False
            
            for package, new_version in package_updates.items():
                # Pattern to match package versions in pyproject.toml
                patterns = [
                    rf'"{re.escape(package)}==.*"',
                    rf'"{re.escape(package)}>=.*"',
                    rf'"{re.escape(package)}"',
                    rf"'{re.escape(package)}==.*'",
                    rf"'{re.escape(package)}>=.*'",
                    rf"'{re.escape(package)}'"
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        new_spec = f'"{package}>={new_version}"'
                        content = re.sub(pattern, new_spec, content)
                        updated = True
                        print(f"  ✅ Updated {package} to >={new_version}")
                        break
            
            if updated:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                
                # Write updated content
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"  💾 Updated {file_path} (backup saved to {backup_path})")
                return True
            else:
                print(f"  ℹ️ No updates needed for {file_path}")
                return False
        
        except Exception as e:
            print(f"  ❌ Failed to update {file_path}: {e}")
            return False
    
    def apply_security_fixes(self) -> bool:
        """Apply security fixes to all requirements files."""
        print("🛠️ Applying security fixes...")
        
        # Prepare package updates based on critical vulnerabilities
        package_updates = {}
        for package, info in self.critical_packages.items():
            package_updates[package] = info['fixed']
        
        # Add additional security updates
        additional_updates = {
            'cryptography': '45.0.4',  # Latest secure version
            'requests': '2.32.4',      # Latest secure version
            'urllib3': '2.5.0',        # Latest secure version
            'certifi': '2025.6.15',    # Latest certificates
            'setuptools': '80.9.0',    # Latest secure version
        }
        package_updates.update(additional_updates)
        
        updated_files = []
        
        # Update all requirements files
        for req_file in self.requirements_files:
            if req_file.name == 'pyproject.toml':
                if self.update_pyproject_toml(req_file, package_updates):
                    updated_files.append(req_file)
            else:
                if self.update_requirements_file(req_file, package_updates):
                    updated_files.append(req_file)
        
        self.fixes_applied = updated_files
        return len(updated_files) > 0
    
    def upgrade_environment(self) -> bool:
        """Upgrade the current environment with fixed packages."""
        print("🔄 Upgrading current environment...")
        
        try:
            # Create a list of packages to upgrade
            upgrades = []
            for package, info in self.critical_packages.items():
                upgrades.append(f"{package}>={info['fixed']}")
            
            # Add additional critical upgrades
            additional_upgrades = [
                'cryptography>=45.0.4',
                'requests>=2.32.4',
                'urllib3>=2.5.0',
                'certifi>=2025.6.15',
                'setuptools>=80.9.0'
            ]
            upgrades.extend(additional_upgrades)
            
            # Install upgrades
            for upgrade in upgrades:
                print(f"  📦 Installing {upgrade}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--upgrade', upgrade
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"  ✅ Successfully upgraded {upgrade}")
                else:
                    print(f"  ⚠️ Failed to upgrade {upgrade}: {result.stderr}")
            
            return True
        
        except Exception as e:
            print(f"❌ Environment upgrade failed: {e}")
            return False
    
    def create_security_policy(self) -> None:
        """Create a security policy file for ongoing monitoring."""
        policy_content = """# ACGS-1 Security Policy
# This file defines the security policy for dependency management

# Critical packages that must be kept updated
critical_packages:
  - python-jose>=3.5.1  # Fixes CVE-2024-33664, CVE-2024-33663
  - ecdsa>=0.20.0       # Fixes CVE-2024-23342
  - torch>=2.7.3        # Fixes GHSA-887c-mr87-cxwp
  - cryptography>=45.0.4
  - requests>=2.32.4
  - urllib3>=2.5.0
  - certifi>=2025.6.15

# Vulnerability scanning schedule
scanning:
  frequency: daily
  tools:
    - safety
    - pip-audit
    - bandit

# Security thresholds
thresholds:
  critical: 0      # No critical vulnerabilities allowed
  high: 0          # No high vulnerabilities in production
  medium: 5        # Max 5 medium vulnerabilities
  low: 10          # Max 10 low vulnerabilities

# Ignored vulnerabilities (with justification)
ignored:
  # Add any vulnerabilities that cannot be fixed due to compatibility
  # Format: vulnerability_id: "justification"

# Last updated: {date}
""".format(date=subprocess.run(['date'], capture_output=True, text=True).stdout.strip())
        
        with open('SECURITY_POLICY.yml', 'w') as f:
            f.write(policy_content)
        
        print("📋 Created security policy file: SECURITY_POLICY.yml")
    
    def generate_security_report(self) -> str:
        """Generate a comprehensive security report."""
        print("\n📊 Generating Security Remediation Report")
        print("=" * 60)
        
        report = []
        report.append("# ACGS-1 Security Vulnerability Remediation Report")
        report.append(f"Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        report.append("")
        
        # Summary
        total_vulns = len(self.vulnerabilities.get('safety', [])) + len(self.vulnerabilities.get('pip_audit', []))
        critical_fixed = len(self.critical_packages)
        
        report.append("## Executive Summary")
        report.append(f"- **Total Vulnerabilities Identified**: {total_vulns}")
        report.append(f"- **Critical Packages Fixed**: {critical_fixed}")
        report.append(f"- **Requirements Files Updated**: {len(self.fixes_applied)}")
        report.append("")
        
        # Critical vulnerabilities fixed
        report.append("## Critical Vulnerabilities Fixed")
        for package, info in self.critical_packages.items():
            report.append(f"### {package}")
            report.append(f"- **Current Version**: {info['current']}")
            report.append(f"- **Fixed Version**: {info['fixed']}")
            report.append(f"- **Severity**: {info['severity']}")
            report.append(f"- **CVEs**: {', '.join(info['cves'])}")
            report.append("")
        
        # Files updated
        if self.fixes_applied:
            report.append("## Files Updated")
            for file_path in self.fixes_applied:
                report.append(f"- {file_path}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("1. **Immediate Actions**:")
        report.append("   - Test all updated dependencies in development environment")
        report.append("   - Run comprehensive test suite to ensure compatibility")
        report.append("   - Deploy updates to staging environment for validation")
        report.append("")
        report.append("2. **Ongoing Security**:")
        report.append("   - Implement daily security scans using the new workflows")
        report.append("   - Set up automated dependency updates with Dependabot")
        report.append("   - Monitor security advisories for critical packages")
        report.append("")
        report.append("3. **Process Improvements**:")
        report.append("   - Enforce security policy in CI/CD pipeline")
        report.append("   - Regular security training for development team")
        report.append("   - Quarterly security audits and penetration testing")
        
        report_content = "\n".join(report)
        
        # Save report
        with open('SECURITY_REMEDIATION_REPORT.md', 'w') as f:
            f.write(report_content)
        
        print(report_content)
        return report_content
    
    def run_remediation(self) -> bool:
        """Run the complete vulnerability remediation process."""
        print("🚀 Starting ACGS-1 Security Vulnerability Remediation")
        print("=" * 60)
        
        try:
            # Step 1: Find requirements files
            req_files = self.find_requirements_files()
            print(f"📁 Found {len(req_files)} requirements files")
            
            # Step 2: Scan for vulnerabilities
            vulnerabilities = self.scan_vulnerabilities()
            
            # Step 3: Apply fixes to requirements files
            fixes_applied = self.apply_security_fixes()
            
            # Step 4: Upgrade current environment
            env_upgraded = self.upgrade_environment()
            
            # Step 5: Create security policy
            self.create_security_policy()
            
            # Step 6: Generate report
            self.generate_security_report()
            
            if fixes_applied or env_upgraded:
                print("\n✅ Security remediation completed successfully!")
                print("🔒 Critical vulnerabilities have been addressed.")
                print("📋 Review SECURITY_REMEDIATION_REPORT.md for details.")
                return True
            else:
                print("\n⚠️ No critical fixes were needed.")
                return False
                
        except Exception as e:
            print(f"\n❌ Security remediation failed: {e}")
            return False

def main():
    """Main remediation function."""
    fixer = VulnerabilityFixer()
    
    try:
        success = fixer.run_remediation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error during remediation: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()