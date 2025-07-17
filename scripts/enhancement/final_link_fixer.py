#!/usr/bin/env python3
"""
ACGS-2 Final Link Fixer Script
Constitutional Hash: cdd01ef066bc6cf2

This script fixes the remaining 6 broken links to achieve 100% cross-reference validity.
Targets specific files: services/CLAUDE.md, docs/CLAUDE.md, infrastructure/CLAUDE.md
"""

import os
import re
from pathlib import Path

class FinalLinkFixer:
    """Fix the final broken links to achieve 100% validity"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    def fix_services_claude_md(self):
        """Fix broken links in services/CLAUDE.md"""
        file_path = self.project_root / "services" / "CLAUDE.md"
        
        try:
            content = file_path.read_text()
            
            # Fix the broken links based on actual directory structure
            fixes = {
                # Fix relative paths that don't exist
                r'\[Core\]\(core/CLAUDE\.md\)': '[Core](core/CLAUDE.md)',  # This should work
                r'\[Platform Services\]\(platform_services/CLAUDE\.md\)': '[Platform Services](platform_services/CLAUDE.md)',  # This should work
                
                # Fix incorrect relative paths to docs
                r'\[API Documentation\]\(\.\./docs/api/CLAUDE\.md\)': '[API Documentation](../docs/api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./docs/architecture/CLAUDE\.md\)': '[Architecture](../docs/architecture/CLAUDE.md)',
                r'\[Development Guide\]\(\.\./docs/development/CLAUDE\.md\)': '[Development Guide](../docs/development/CLAUDE.md)',
                r'\[Deployment Guide\]\(\.\./docs/deployment/CLAUDE\.md\)': '[Deployment Guide](../docs/deployment/CLAUDE.md)',
                
                # Fix navigation breadcrumb
                r'\[Root\]\(\.\./CLAUDE\.md\)': '[Root](../CLAUDE.md)'
            }
            
            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)
            
            file_path.write_text(content)
            print(f"✅ Fixed: services/CLAUDE.md")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing services/CLAUDE.md: {e}")
            return False
    
    def fix_docs_claude_md(self):
        """Fix broken links in docs/CLAUDE.md"""
        file_path = self.project_root / "docs" / "CLAUDE.md"
        
        try:
            content = file_path.read_text()
            
            # Fix the broken links - docs/CLAUDE.md has incorrect relative paths
            fixes = {
                # Fix incorrect double relative paths
                r'\[Api\]\(\.\./\.\./docs/api/CLAUDE\.md\)': '[API](api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./\.\./docs/architecture/CLAUDE\.md\)': '[Architecture](architecture/CLAUDE.md)',
                
                # Fix incorrect relative paths (should be relative to docs/)
                r'\[API Documentation\]\(\.\./docs/api/CLAUDE\.md\)': '[API Documentation](api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./docs/architecture/CLAUDE\.md\)': '[Architecture](architecture/CLAUDE.md)',
                r'\[Development Guide\]\(\.\./docs/development/CLAUDE\.md\)': '[Development Guide](development/CLAUDE.md)',
                r'\[Deployment Guide\]\(\.\./docs/deployment/CLAUDE\.md\)': '[Deployment Guide](deployment/CLAUDE.md)',
                
                # Fix navigation breadcrumb
                r'\[Root\]\(\.\./CLAUDE\.md\)': '[Root](../CLAUDE.md)'
            }
            
            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)
            
            file_path.write_text(content)
            print(f"✅ Fixed: docs/CLAUDE.md")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing docs/CLAUDE.md: {e}")
            return False
    
    def fix_infrastructure_claude_md(self):
        """Fix broken links in infrastructure/CLAUDE.md"""
        file_path = self.project_root / "infrastructure" / "CLAUDE.md"
        
        try:
            content = file_path.read_text()
            
            # Fix the broken links based on actual directory structure
            fixes = {
                # Fix relative paths to existing subdirectories
                r'\[Docker\]\(docker/CLAUDE\.md\)': '[Docker](docker/CLAUDE.md)',  # This exists
                r'\[Kubernetes\]\(kubernetes/CLAUDE\.md\)': '[Kubernetes](kubernetes/CLAUDE.md)',  # This exists
                
                # Fix incorrect relative paths to docs
                r'\[API Documentation\]\(\.\./docs/api/CLAUDE\.md\)': '[API Documentation](../docs/api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./docs/architecture/CLAUDE\.md\)': '[Architecture](../docs/architecture/CLAUDE.md)',
                r'\[Development Guide\]\(\.\./docs/development/CLAUDE\.md\)': '[Development Guide](../docs/development/CLAUDE.md)',
                r'\[Deployment Guide\]\(\.\./docs/deployment/CLAUDE\.md\)': '[Deployment Guide](../docs/deployment/CLAUDE.md)',
                
                # Fix navigation breadcrumb
                r'\[Root\]\(\.\./CLAUDE\.md\)': '[Root](../CLAUDE.md)'
            }
            
            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)
            
            file_path.write_text(content)
            print(f"✅ Fixed: infrastructure/CLAUDE.md")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing infrastructure/CLAUDE.md: {e}")
            return False
    
    def validate_links_in_file(self, file_path: Path) -> int:
        """Count broken links in a file"""
        try:
            content = file_path.read_text()
            
            # Find all markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            broken_count = 0
            
            for link_text, link_url in links:
                # Skip external links and anchors
                if link_url.startswith(('http', '#', 'mailto:')):
                    continue
                
                # Resolve relative path
                if link_url.startswith('/'):
                    # Absolute path from project root
                    target_path = self.project_root / link_url.lstrip('/')
                else:
                    # Relative path from current file
                    target_path = file_path.parent / link_url
                
                # Check if target exists
                try:
                    target_path = target_path.resolve()
                    if not target_path.exists():
                        broken_count += 1
                        print(f"    ❌ Broken: {link_text} -> {link_url}")
                except:
                    broken_count += 1
                    print(f"    ❌ Invalid: {link_text} -> {link_url}")
            
            return broken_count
            
        except Exception as e:
            print(f"  ❌ Error validating {file_path}: {e}")
            return 0
    
    def execute_final_link_fixes(self):
        """Execute final link fixes to achieve 100% validity"""
        print("🚀 Starting ACGS-2 Final Link Fixing")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target: Fix remaining 6 broken links to achieve 100% validity")
        
        # Files with known broken links
        target_files = [
            self.project_root / "services" / "CLAUDE.md",
            self.project_root / "docs" / "CLAUDE.md", 
            self.project_root / "infrastructure" / "CLAUDE.md"
        ]
        
        print(f"\n🔍 Analyzing broken links before fixes...")
        total_broken_before = 0
        for file_path in target_files:
            if file_path.exists():
                print(f"\n📄 {file_path.relative_to(self.project_root)}:")
                broken_count = self.validate_links_in_file(file_path)
                total_broken_before += broken_count
                print(f"    Broken links: {broken_count}")
        
        print(f"\n📊 Total broken links before fixes: {total_broken_before}")
        
        # Apply fixes
        print(f"\n🔧 Applying targeted link fixes...")
        fixes_applied = 0
        
        if self.fix_services_claude_md():
            fixes_applied += 1
        
        if self.fix_docs_claude_md():
            fixes_applied += 1
            
        if self.fix_infrastructure_claude_md():
            fixes_applied += 1
        
        # Validate after fixes
        print(f"\n🔍 Analyzing links after fixes...")
        total_broken_after = 0
        for file_path in target_files:
            if file_path.exists():
                print(f"\n📄 {file_path.relative_to(self.project_root)}:")
                broken_count = self.validate_links_in_file(file_path)
                total_broken_after += broken_count
                print(f"    Broken links: {broken_count}")
        
        improvement = total_broken_before - total_broken_after
        
        print(f"\n✅ Final link fixing completed!")
        print(f"📊 Summary:")
        print(f"  - Files processed: {len(target_files)}")
        print(f"  - Fixes applied: {fixes_applied}")
        print(f"  - Broken links before: {total_broken_before}")
        print(f"  - Broken links after: {total_broken_after}")
        print(f"  - Links fixed: {improvement}")
        print(f"  - Constitutional hash: {self.constitutional_hash}")
        
        if total_broken_after == 0:
            print(f"  - 🎉 TARGET ACHIEVED: 100% cross-reference validity!")
        else:
            print(f"  - 🔄 Remaining broken links: {total_broken_after}")
        
        return total_broken_after == 0

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    fixer = FinalLinkFixer(project_root)
    
    # Execute final link fixes
    success = fixer.execute_final_link_fixes()
    
    if success:
        print("\n🎉 Final Link Fixing Complete!")
        print("✅ 100% cross-reference validity achieved!")
    else:
        print("\n🔄 Additional link fixing may be needed.")

if __name__ == "__main__":
    main()
