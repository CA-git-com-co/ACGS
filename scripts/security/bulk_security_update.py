#!/usr/bin/env python3
"""
ACGS-2 Bulk Security Update Script
Constitutional Hash: cdd01ef066bc6cf2

Updates all requirements.txt files with secure package versions
to address the 161 security vulnerabilities identified by GitHub.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

class BulkSecurityUpdater:
    """Updates all requirements files with secure package versions"""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.project_root = Path("/home/dislove/ACGS-2")
        
        # Security updates mapping - package name to minimum secure version
        self.security_updates = {
            'transformers': '4.52.1',
            'aiohttp': '3.10.11',
            'cryptography': '43.0.1',
            'orjson': '3.9.15',
            'urllib3': '2.5.0',
            'requests': '2.32.4',
            'certifi': '2025.6.15',
            'setuptools': '80.9.0',
            'torch': '2.7.1',
            'fastapi': '0.115.6',
            'uvicorn': '0.34.0',
            'pydantic': '2.10.5',
            'black': '24.3.0',
            'ruff': '0.8.4',
            'mypy': '1.13.0',
            'pytest': '8.3.4',
            'numpy': '1.24.4',
            'scipy': '1.11.1',
            'sentence-transformers': '3.1.0',
            'scikit-learn': '1.5.0',
            'pyjwt': '2.10.1',
            'mkdocs-material': '9.5.32',
            'gunicorn': '23.0.0',
            'anyio': '4.4.0',
            'idna': '3.7',
            'h11': '0.16.0',
        }
    
    def find_requirements_files(self) -> List[Path]:
        """Find all requirements.txt files in the project"""
        return list(self.project_root.rglob("requirements*.txt"))
    
    def update_package_version(self, content: str, package: str, new_version: str) -> str:
        """Update package version in requirements content"""
        # Pattern to match package specifications
        patterns = [
            rf'^({package})\s*([><=!~]+)\s*([0-9.]+.*?)(\s*#.*)?$',  # With version constraint
            rf'^({package})\s*==\s*([0-9.]+.*?)(\s*#.*)?$',         # Exact version
            rf'^({package})\s*>=\s*([0-9.]+.*?)(\s*#.*)?$',         # Minimum version
            rf'^({package})\s*$',                                    # Package name only
        ]
        
        lines = content.split('\n')
        updated_lines = []
        package_found = False
        
        for line in lines:
            updated_line = line
            
            for pattern in patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    package_found = True
                    comment = match.group(4) if len(match.groups()) >= 4 and match.group(4) else ""
                    if comment is None:
                        comment = ""
                    
                    # Preserve indentation
                    indent = len(line) - len(line.lstrip())
                    updated_line = f"{' ' * indent}{package}>={new_version}{comment}"
                    break
            
            updated_lines.append(updated_line)
        
        return '\n'.join(updated_lines)
    
    def update_requirements_file(self, req_file: Path) -> bool:
        """Update a single requirements file with security fixes"""
        try:
            # Read current content
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            updates_made = []
            
            # Apply security updates
            for package, version in self.security_updates.items():
                # Check if package exists in file
                if re.search(rf'\b{package}\b', content, re.IGNORECASE):
                    new_content = self.update_package_version(content, package, version)
                    if new_content != content:
                        content = new_content
                        updates_made.append(f"{package}>={version}")
            
            # Only write if changes were made
            if content != original_content:
                # Create backup
                backup_file = req_file.with_suffix('.txt.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write updated content
                with open(req_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {req_file}")
                for update in updates_made:
                    print(f"   • {update}")
                return True
            else:
                print(f"⏭️  No updates needed for {req_file}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating {req_file}: {e}")
            return False
    
    def validate_constitutional_compliance(self, req_file: Path) -> bool:
        """Ensure constitutional hash is present in requirements file"""
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.constitutional_hash not in content:
                # Add constitutional hash comment at the top
                lines = content.split('\n')
                
                # Find the right place to insert (after existing comments)
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('#') or line.strip() == '':
                        insert_index = i + 1
                    else:
                        break
                
                # Insert constitutional hash
                hash_comment = f"# Constitutional Hash: {self.constitutional_hash}"
                lines.insert(insert_index, hash_comment)
                
                # Write updated content
                with open(req_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"📋 Added constitutional hash to {req_file}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error validating {req_file}: {e}")
            return False
    
    def run_bulk_update(self) -> Dict[str, int]:
        """Run bulk security update on all requirements files"""
        print("🔒 ACGS-2 Bulk Security Update")
        print("=" * 50)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target packages: {', '.join(self.security_updates.keys())}")
        print()
        
        req_files = self.find_requirements_files()
        print(f"Found {len(req_files)} requirements files")
        print()
        
        stats = {
            'total_files': len(req_files),
            'files_updated': 0,
            'files_with_constitutional_hash_added': 0,
            'errors': 0
        }
        
        # Update each file
        for req_file in req_files:
            try:
                # Update package versions
                if self.update_requirements_file(req_file):
                    stats['files_updated'] += 1
                
                # Ensure constitutional compliance
                if self.validate_constitutional_compliance(req_file):
                    stats['files_with_constitutional_hash_added'] += 1
                    
            except Exception as e:
                print(f"❌ Error processing {req_file}: {e}")
                stats['errors'] += 1
        
        # Print summary
        print()
        print("📊 BULK UPDATE SUMMARY")
        print("=" * 30)
        print(f"Total files processed: {stats['total_files']}")
        print(f"Files updated with security fixes: {stats['files_updated']}")
        print(f"Files with constitutional hash added: {stats['files_with_constitutional_hash_added']}")
        print(f"Errors encountered: {stats['errors']}")
        
        if stats['files_updated'] > 0:
            print()
            print("🎯 NEXT STEPS:")
            print("1. Run security validation: python scripts/security/validate_security_fixes.py")
            print("2. Test critical services to ensure compatibility")
            print("3. Run comprehensive test suite")
            print("4. Deploy to staging environment for validation")
        
        return stats

def main():
    """Main function"""
    updater = BulkSecurityUpdater()
    
    # Confirm before proceeding
    print("⚠️  This will update ALL requirements.txt files with security fixes.")
    print("Backups will be created with .backup extension.")
    print()
    
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    print()
    stats = updater.run_bulk_update()
    
    # Exit with appropriate code
    if stats['errors'] > 0:
        sys.exit(1)
    elif stats['files_updated'] == 0:
        print("\n✅ All files are already up to date!")
        sys.exit(0)
    else:
        print(f"\n✅ Successfully updated {stats['files_updated']} files!")
        sys.exit(0)

if __name__ == "__main__":
    main()
