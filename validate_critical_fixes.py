#!/usr/bin/env python3
"""
ACGS-2 Critical Vulnerability Validation Script
Constitutional Hash: cdd01ef066bc6cf2

Validates that critical security vulnerabilities have been properly fixed.
"""

import re
from pathlib import Path

def main():
    # Check for remaining critical vulnerabilities
    critical_packages = {
        'python-jose': '3.4.0',
        'torch': '2.6.0', 
        'vllm': '0.8.0',
        'next': '14.2.25',
        'h11': '0.16.0',
        'mlflow': '2.10.0'
    }

    print('🔍 Checking critical vulnerability fixes...')
    print('=' * 50)

    issues_found = []
    files_checked = 0

    # Check Python requirements files
    for req_file in Path('.').rglob('requirements*.txt'):
        if any(skip in str(req_file) for skip in ['backup', 'temp', '__pycache__', '.git']):
            continue
            
        files_checked += 1
        try:
            content = req_file.read_text()
            for package, min_version in critical_packages.items():
                if package == 'next':  # Skip Next.js for Python files
                    continue
                    
                # Look for package references
                pattern = rf'{package}[>=!~<]*([0-9.]+)'
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Simple version comparison (major.minor.patch)
                    try:
                        current_parts = [int(x) for x in match.split('.')]
                        min_parts = [int(x) for x in min_version.split('.')]
                        
                        # Pad shorter version with zeros
                        max_len = max(len(current_parts), len(min_parts))
                        current_parts += [0] * (max_len - len(current_parts))
                        min_parts += [0] * (max_len - len(min_parts))
                        
                        if current_parts < min_parts:
                            issues_found.append(f'{req_file}: {package} {match} < {min_version}')
                    except ValueError:
                        pass
        except Exception as e:
            print(f'Warning: Could not read {req_file}: {e}')

    # Check package.json files
    for pkg_file in Path('.').rglob('package.json'):
        if any(skip in str(pkg_file) for skip in ['backup', 'temp', 'node_modules', '.git']):
            continue
            
        files_checked += 1
        try:
            content = pkg_file.read_text()
            if 'next' in content:
                # Look for Next.js version
                pattern = r'"next"\s*:\s*"([0-9.]+)"'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    try:
                        current_parts = [int(x) for x in match.split('.')]
                        min_parts = [int(x) for x in '14.2.25'.split('.')]
                        
                        max_len = max(len(current_parts), len(min_parts))
                        current_parts += [0] * (max_len - len(current_parts))
                        min_parts += [0] * (max_len - len(min_parts))
                        
                        if current_parts < min_parts:
                            issues_found.append(f'{pkg_file}: next {match} < 14.2.25')
                    except ValueError:
                        pass
        except Exception as e:
            print(f'Warning: Could not read {pkg_file}: {e}')

    # Report results
    print(f'📊 Checked {files_checked} files')
    
    if issues_found:
        print('❌ Critical vulnerabilities still found:')
        for issue in issues_found:
            print(f'  - {issue}')
        return 1
    else:
        print('✅ All critical vulnerabilities appear to be fixed!')
        
    print(f'\n📋 Checked packages: {list(critical_packages.keys())}')
    print('\n🎯 Constitutional Hash: cdd01ef066bc6cf2')
    return 0

if __name__ == '__main__':
    exit(main())
