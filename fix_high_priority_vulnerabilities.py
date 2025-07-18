#!/usr/bin/env python3
"""
ACGS-2 High Priority Vulnerability Fixes
Constitutional Hash: cdd01ef066bc6cf2

Systematically fixes high-priority security vulnerabilities:
- Starlette DoS (CVE-2024-47874) via FastAPI updates
- python-multipart vulnerabilities (CVE-2024-53981, CVE-2024-24762)
"""

import re
from pathlib import Path

def main():
    print('🔧 Fixing high-priority security vulnerabilities...')
    print('=' * 60)
    
    # High-priority vulnerability fixes
    vulnerability_fixes = {
        'python-multipart': {
            'pattern': r'python-multipart[>=!~<]*([0-9.]+)',
            'min_version': '0.0.18',
            'description': 'DoS vulnerabilities (CVE-2024-53981, CVE-2024-24762)'
        },
        'fastapi': {
            'pattern': r'fastapi[>=!~<]*([0-9.]+)',
            'min_version': '0.115.6',
            'description': 'Ensures Starlette ≥ 0.40.0 (CVE-2024-47874)'
        },
        'cryptography': {
            'pattern': r'cryptography[>=!~<]*([0-9.]+)',
            'min_version': '42.0.4',
            'description': 'NULL pointer dereference (CVE-2024-26130)'
        }
    }
    
    files_updated = 0
    vulnerabilities_fixed = 0
    
    # Find all requirements files
    for req_file in Path('.').rglob('requirements*.txt'):
        if any(skip in str(req_file) for skip in ['backup', 'temp', '__pycache__', '.git']):
            continue
            
        try:
            content = req_file.read_text()
            original_content = content
            file_updated = False
            
            for package, fix_info in vulnerability_fixes.items():
                pattern = fix_info['pattern']
                min_version = fix_info['min_version']
                
                # Find all matches for this package
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in reversed(matches):  # Reverse to maintain positions
                    current_version = match.group(1)
                    
                    # Simple version comparison
                    try:
                        current_parts = [int(x) for x in current_version.split('.')]
                        min_parts = [int(x) for x in min_version.split('.')]
                        
                        # Pad shorter version with zeros
                        max_len = max(len(current_parts), len(min_parts))
                        current_parts += [0] * (max_len - len(current_parts))
                        min_parts += [0] * (max_len - len(min_parts))
                        
                        if current_parts < min_parts:
                            # Update the version
                            old_spec = match.group(0)
                            new_spec = f'{package}>={min_version}'
                            
                            content = content[:match.start()] + new_spec + content[match.end():]
                            
                            print(f'  📦 {req_file}: {old_spec} → {new_spec}')
                            file_updated = True
                            vulnerabilities_fixed += 1
                            
                    except ValueError:
                        # Skip if version parsing fails
                        continue
            
            # Write updated content if changes were made
            if file_updated:
                req_file.write_text(content)
                files_updated += 1
                
        except Exception as e:
            print(f'⚠️ Error processing {req_file}: {e}')
    
    print(f'\n📊 Summary:')
    print(f'  Files updated: {files_updated}')
    print(f'  Vulnerabilities fixed: {vulnerabilities_fixed}')
    
    if vulnerabilities_fixed > 0:
        print(f'\n✅ High-priority vulnerabilities fixed!')
        print(f'\n🔍 Fixed vulnerabilities:')
        for package, fix_info in vulnerability_fixes.items():
            print(f'  - {package} ≥ {fix_info["min_version"]}: {fix_info["description"]}')
    else:
        print(f'\n✅ No high-priority vulnerabilities found!')
    
    print(f'\n🎯 Constitutional Hash: cdd01ef066bc6cf2')
    return 0

if __name__ == '__main__':
    exit(main())
