#!/usr/bin/env python3
"""
Security Vulnerability Scanner for ACGS Dependencies
Constitutional Hash: cdd01ef066bc6cf2
"""

import subprocess
import sys
from pathlib import Path
import json
import re

def run_safety_check():
    """Run safety check on all requirements files."""
    print("Running safety check on all requirements files...")
    
    req_files = list(Path("/home/dislove/ACGS-2").rglob("requirements*.txt"))
    
    vulnerabilities = []
    
    for req_file in req_files:
        try:
            result = subprocess.run(
                ["python", "-m", "safety", "check", "-r", str(req_file), "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    if data:
                        vulnerabilities.append({
                            "file": str(req_file),
                            "vulnerabilities": data
                        })
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"Error checking {req_file}: {e}")
    
    return vulnerabilities

def check_outdated_packages():
    """Check for commonly outdated packages."""
    print("\nChecking for commonly outdated packages...")
    
    # Known security-sensitive packages and their minimum secure versions
    security_packages = {
        "cryptography": "45.0.4",
        "urllib3": "2.5.0", 
        "requests": "2.32.4",
        "certifi": "2025.6.15",
        "pyjwt": "2.10.0",
        "tornado": "6.4.1",
        "flask": "3.0.0",
        "django": "5.0.0",
        "sqlalchemy": "2.0.23",
        "pydantic": "2.10.5"
    }
    
    req_files = list(Path("/home/dislove/ACGS-2").rglob("requirements*.txt"))
    outdated_found = []
    
    for req_file in req_files:
        try:
            with open(req_file, 'r') as f:
                content = f.read()
                
            for package, min_version in security_packages.items():
                pattern = rf'{package}[>=!~<]*([0-9.]+)'
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    if compare_versions(match, min_version) < 0:
                        outdated_found.append({
                            "file": str(req_file),
                            "package": package,
                            "current": match,
                            "recommended": min_version
                        })
                        
        except Exception as e:
            print(f"Error checking {req_file}: {e}")
    
    return outdated_found

def compare_versions(v1, v2):
    """Simple version comparison."""
    def version_tuple(v):
        return tuple(map(int, v.split('.')))
    
    try:
        return -1 if version_tuple(v1) < version_tuple(v2) else 1 if version_tuple(v1) > version_tuple(v2) else 0
    except:
        return 0

def main():
    print("ACGS Security Vulnerability Scanner")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 50)
    
    # Check for safety tool
    try:
        subprocess.run(["python", "-m", "safety", "--version"], capture_output=True, check=True)
    except:
        print("Safety tool not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "safety"])
    
    # Run safety checks
    vulnerabilities = run_safety_check()
    
    # Check for outdated packages
    outdated = check_outdated_packages()
    
    # Report findings
    print("\n" + "="*50)
    print("SECURITY VULNERABILITY REPORT")
    print("="*50)
    
    if vulnerabilities:
        print(f"\nFound {len(vulnerabilities)} files with security vulnerabilities:")
        for vuln in vulnerabilities:
            print(f"\n{vuln['file']}:")
            for v in vuln['vulnerabilities']:
                print(f"  - {v.get('package', 'Unknown')}: {v.get('vulnerability', 'Unknown vulnerability')}")
    else:
        print("\nNo security vulnerabilities found by safety scanner.")
    
    if outdated:
        print(f"\n\nFound {len(outdated)} outdated security-sensitive packages:")
        for pkg in outdated:
            print(f"  {pkg['file']}: {pkg['package']} {pkg['current']} -> {pkg['recommended']}")
    else:
        print("\nNo outdated security-sensitive packages found.")
    
    # Summary recommendations
    print("\n" + "="*50)
    print("RECOMMENDATIONS")
    print("="*50)
    
    print("\n1. IMMEDIATE ACTIONS NEEDED:")
    if vulnerabilities or outdated:
        print("   - Update security-sensitive packages immediately")
        print("   - Review and test all services after updates")
        print("   - Run full security audit")
    else:
        print("   - No immediate security actions required")
    
    print("\n2. PREVENTIVE MEASURES:")
    print("   - Implement automated dependency scanning in CI/CD")
    print("   - Set up Dependabot for automatic security updates")
    print("   - Regular security audits (monthly)")
    print("   - Use dependency pinning for critical packages")
    
    print("\n3. MONITORING:")
    print("   - Monitor CVE databases for package vulnerabilities")
    print("   - Set up alerts for security advisories")
    print("   - Regular penetration testing")

if __name__ == "__main__":
    main()