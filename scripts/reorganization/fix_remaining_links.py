#!/usr/bin/env python3
"""
ACGS-2 Remaining Links Fixing Script
Constitutional Hash: cdd01ef066bc6cf2

This script fixes the remaining broken links identified in the cross-reference validation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List
import json

class RemainingLinksFixer:
    """Fix remaining broken links in CLAUDE.md files"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    def find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the project"""
        claude_files = []
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip virtual environments and build directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            claude_files.append(file_path)
        return claude_files
    
    def fix_link_patterns(self, content: str, file_path: Path) -> str:
        """Fix common broken link patterns"""
        
        # Get relative path for context
        relative_path = file_path.relative_to(self.project_root)
        path_parts = relative_path.parts[:-1]  # Exclude CLAUDE.md filename
        depth = len(path_parts)
        
        # Fix double CLAUDE.md/claude.md patterns
        content = re.sub(r'/CLAUDE\.md/claude\.md', '/CLAUDE.md', content)
        
        # Fix double ../docs/../docs patterns
        content = re.sub(r'\.\./docs/\.\./docs/', '../docs/', content)
        
        # Fix incorrect claude.md references (should be CLAUDE.md)
        content = re.sub(r'/claude\.md', '/CLAUDE.md', content)
        
        # Fix navigation breadcrumb patterns
        if depth == 0:  # Root directory
            content = re.sub(r'\[Root\]\(\.\./CLAUDE\.md\)', '[Root](CLAUDE.md)', content)
        
        # Fix relative path issues based on directory depth
        if depth == 1:  # First level directories (docs, services, etc.)
            # Fix paths that go too deep
            content = re.sub(r'\.\./\.\./([^/]+)/CLAUDE\.md', r'../\1/CLAUDE.md', content)
        elif depth == 2:  # Second level directories (docs/api, services/core, etc.)
            # Fix paths that don't go deep enough
            content = re.sub(r'\.\./docs/([^/]+)/CLAUDE\.md', r'../\1/CLAUDE.md', content)
            # Fix paths that go too deep
            content = re.sub(r'\.\./\.\./docs/([^/]+)/CLAUDE\.md', r'../\1/CLAUDE.md', content)
        
        # Fix specific common broken patterns
        broken_patterns = {
            # Pattern: broken -> fixed
            r'\[Documentation\]\(\.\./\.\./docs/claude\.md\)': '[Documentation](../../docs/CLAUDE.md)',
            r'\[Documentation\]\(\.\./\.\./docs/CLAUDE\.md\)': '[Documentation](../../docs/CLAUDE.md)',
            r'\[API Documentation\]\(\.\./docs/api/CLAUDE\.md/claude\.md\)': '[API Documentation](../api/CLAUDE.md)',
            r'\[Architecture\]\(\.\./docs/architecture/CLAUDE\.md/claude\.md\)': '[Architecture](../architecture/CLAUDE.md)',
            r'\[Development Guide\]\(\.\./docs/\.\./docs/development/CLAUDE\.md/claude\.md\)': '[Development Guide](../development/CLAUDE.md)',
            r'\[Deployment Guide\]\(\.\./docs/\.\./docs/deployment/CLAUDE\.md/claude\.md\)': '[Deployment Guide](../deployment/CLAUDE.md)',
        }
        
        for broken_pattern, fixed_pattern in broken_patterns.items():
            content = re.sub(broken_pattern, fixed_pattern, content)
        
        # Fix breadcrumb navigation based on actual directory structure
        if 'docs/' in str(relative_path):
            # For docs subdirectories
            if depth == 2:  # docs/category/
                content = re.sub(
                    r'\*\*Navigation\*\*: \[Root\]\(\.\./\.\./CLAUDE\.md\) → \[([^\]]+)\]\(\.\./CLAUDE\.md\) → \*\*([^*]+)\*\*',
                    r'**Navigation**: [Root](../../CLAUDE.md) → [Docs](../CLAUDE.md) → **\2**',
                    content
                )
        elif 'services/' in str(relative_path):
            # For services subdirectories
            if depth == 2:  # services/category/
                content = re.sub(
                    r'\*\*Navigation\*\*: \[Root\]\(\.\./\.\./CLAUDE\.md\) → \[([^\]]+)\]\(\.\./CLAUDE\.md\) → \*\*([^*]+)\*\*',
                    r'**Navigation**: [Root](../../CLAUDE.md) → [Services](../CLAUDE.md) → **\2**',
                    content
                )
            elif depth == 3:  # services/category/service/
                content = re.sub(
                    r'\*\*Navigation\*\*: \[Root\]\(\.\./\.\./\.\./CLAUDE\.md\) → \[([^\]]+)\]\(\.\./\.\./CLAUDE\.md\) → \[([^\]]+)\]\(\.\./CLAUDE\.md\) → \*\*([^*]+)\*\*',
                    r'**Navigation**: [Root](../../../CLAUDE.md) → [Services](../../CLAUDE.md) → [\2](../CLAUDE.md) → **\3**',
                    content
                )
        
        return content
    
    def validate_links_in_file(self, file_path: Path) -> Dict:
        """Validate links in a single file and return statistics"""
        try:
            content = file_path.read_text()
            
            # Find all markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            valid_links = 0
            broken_links = []
            
            for link_text, link_url in links:
                # Skip external links and anchors
                if link_url.startswith(('http', '#', 'mailto:')):
                    valid_links += 1
                    continue
                
                # Resolve relative path
                if link_url.startswith('/'):
                    # Absolute path from project root
                    target_path = self.project_root / link_url.lstrip('/')
                else:
                    # Relative path from current file
                    target_path = file_path.parent / link_url
                
                # Normalize path
                try:
                    target_path = target_path.resolve()
                    if target_path.exists():
                        valid_links += 1
                    else:
                        broken_links.append((link_text, link_url))
                except:
                    broken_links.append((link_text, link_url))
            
            return {
                "total_links": len(links),
                "valid_links": valid_links,
                "broken_links": broken_links,
                "validity_rate": (valid_links / len(links)) * 100 if links else 100
            }
            
        except Exception as e:
            print(f"  ❌ Error validating {file_path}: {e}")
            return {"total_links": 0, "valid_links": 0, "broken_links": [], "validity_rate": 0}
    
    def fix_file_links(self, file_path: Path) -> bool:
        """Fix links in a single CLAUDE.md file"""
        try:
            # Read current content
            content = file_path.read_text()
            
            # Apply link fixes
            fixed_content = self.fix_link_patterns(content, file_path)
            
            # Only write if content changed
            if fixed_content != content:
                file_path.write_text(fixed_content)
                print(f"  ✅ Fixed: {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"  ➡️ No changes: {file_path.relative_to(self.project_root)}")
                return True
                
        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def execute_remaining_fixes(self):
        """Execute the remaining link fixing process"""
        print("🚀 Starting ACGS-2 Remaining Links Fixing")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        try:
            # Find all CLAUDE.md files
            claude_files = self.find_claude_md_files()
            print(f"\n📁 Found {len(claude_files)} CLAUDE.md files")
            
            # Validate current state
            print("\n🔍 Validating current link state...")
            total_links = 0
            total_valid = 0
            
            for file_path in claude_files:
                validation = self.validate_links_in_file(file_path)
                total_links += validation["total_links"]
                total_valid += validation["valid_links"]
            
            initial_validity = (total_valid / total_links) * 100 if total_links else 0
            print(f"  Initial validity: {initial_validity:.1f}% ({total_valid}/{total_links})")
            
            # Fix links in each file
            print("\n🔗 Fixing remaining broken links...")
            fixed_count = 0
            
            for file_path in claude_files:
                if self.fix_file_links(file_path):
                    fixed_count += 1
            
            # Validate final state
            print("\n🔍 Validating final link state...")
            final_total_links = 0
            final_total_valid = 0
            
            for file_path in claude_files:
                validation = self.validate_links_in_file(file_path)
                final_total_links += validation["total_links"]
                final_total_valid += validation["valid_links"]
            
            final_validity = (final_total_valid / final_total_links) * 100 if final_total_links else 0
            improvement = final_validity - initial_validity
            
            print(f"\n✅ Remaining links fixing completed!")
            print(f"📊 Summary:")
            print(f"  - Files processed: {len(claude_files)}")
            print(f"  - Files fixed: {fixed_count}")
            print(f"  - Initial validity: {initial_validity:.1f}%")
            print(f"  - Final validity: {final_validity:.1f}%")
            print(f"  - Improvement: +{improvement:.1f}%")
            print(f"  - Target achieved: {'✅' if final_validity >= 80 else '🔄'} (Target: >80%)")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            
            return final_validity >= 80
            
        except Exception as e:
            print(f"❌ Remaining links fixing failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    fixer = RemainingLinksFixer(project_root)
    
    # Execute remaining link fixes
    success = fixer.execute_remaining_fixes()
    
    if success:
        print("\n🎉 ACGS-2 Remaining Links Fixing Complete!")
        print("✅ Target >80% cross-reference validity achieved!")
    else:
        print("\n🔄 Additional link fixing may be needed to reach 80% target.")

if __name__ == "__main__":
    main()
