#!/usr/bin/env python3
"""
ACGS-2 Advanced Link Fixing Script
Constitutional Hash: cdd01ef066bc6cf2

This script implements targeted fixes for the remaining 7% of broken links to achieve >80% cross-reference validity.
Focus areas:
1. Service directory navigation issues
2. Docs subdirectory path corrections
3. Missing directory references
4. Relative path calculation errors
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime

class AdvancedLinkFixer:
    """Advanced link fixing with intelligent path resolution"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Build actual directory structure map
        self.directory_map = self._build_directory_map()
        
        # Common broken link patterns and their fixes
        self.link_fixes = {
            # Services directory issues
            "../../core/CLAUDE.md": "../core/CLAUDE.md",
            "../../platform_services/CLAUDE.md": "../platform_services/CLAUDE.md", 
            "../../blockchain/CLAUDE.md": "../blockchain/CLAUDE.md",
            "../../shared/CLAUDE.md": "../shared/CLAUDE.md",
            
            # Docs subdirectory issues
            "../api/CLAUDE.md": "../../docs/api/CLAUDE.md",
            "../architecture/CLAUDE.md": "../../docs/architecture/CLAUDE.md",
            "../development/CLAUDE.md": "../../docs/development/CLAUDE.md",
            "../deployment/CLAUDE.md": "../../docs/deployment/CLAUDE.md",
            "../security/CLAUDE.md": "../../docs/security/CLAUDE.md",
            "../testing/CLAUDE.md": "../../docs/testing/CLAUDE.md",
            
            # Infrastructure directory issues
            "../../docker/CLAUDE.md": "../docker/CLAUDE.md",
            "../../kubernetes/CLAUDE.md": "../kubernetes/CLAUDE.md",
            "../../terraform/CLAUDE.md": "../terraform/CLAUDE.md",
            "../../monitoring/CLAUDE.md": "../monitoring/CLAUDE.md"
        }
    
    def _build_directory_map(self) -> Dict[str, Path]:
        """Build a map of all directories containing CLAUDE.md files"""
        directory_map = {}
        
        for claude_file in self.project_root.rglob("CLAUDE.md"):
            if any(skip in str(claude_file) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            
            # Get directory relative to project root
            dir_path = claude_file.parent
            relative_dir = dir_path.relative_to(self.project_root)
            
            # Store both the full path and just the directory name
            directory_map[str(relative_dir)] = dir_path
            directory_map[relative_dir.name] = dir_path
            
        return directory_map
    
    def calculate_correct_path(self, from_file: Path, target_dir: str) -> str:
        """Calculate the correct relative path from one file to another directory"""
        from_dir = from_file.parent
        from_relative = from_dir.relative_to(self.project_root)
        
        # Try to find target directory in our map
        target_path = None
        
        # First try exact match
        if target_dir in self.directory_map:
            target_path = self.directory_map[target_dir]
        else:
            # Try partial matches
            for dir_key, dir_path in self.directory_map.items():
                if target_dir.lower() in dir_key.lower() or dir_key.lower() in target_dir.lower():
                    target_path = dir_path
                    break
        
        if not target_path:
            return None
        
        target_relative = target_path.relative_to(self.project_root)
        
        # Calculate relative path
        try:
            # Get common path
            common_parts = []
            from_parts = list(from_relative.parts)
            target_parts = list(target_relative.parts)
            
            # Find common prefix
            min_len = min(len(from_parts), len(target_parts))
            for i in range(min_len):
                if from_parts[i] == target_parts[i]:
                    common_parts.append(from_parts[i])
                else:
                    break
            
            # Calculate ups needed
            ups_needed = len(from_parts) - len(common_parts)
            
            # Calculate path to target
            remaining_target = target_parts[len(common_parts):]
            
            # Build relative path
            path_parts = [".."] * ups_needed + list(remaining_target) + ["CLAUDE.md"]
            return "/".join(path_parts)
            
        except Exception:
            return None
    
    def fix_service_directory_links(self, content: str, file_path: Path) -> str:
        """Fix links within services directory structure"""
        relative_path = file_path.relative_to(self.project_root)
        
        if not str(relative_path).startswith('services/'):
            return content
        
        path_parts = relative_path.parts
        
        # Fix core service links
        if len(path_parts) >= 3 and path_parts[1] in ['cli', 'contexts']:
            # These are at services/category/ level, need to go to services/core/
            content = re.sub(
                r'\[Core\]\(\.\./\.\./core/CLAUDE\.md\)',
                '[Core](../core/CLAUDE.md)',
                content
            )
            content = re.sub(
                r'\[Platform Services\]\(\.\./\.\./platform_services/CLAUDE\.md\)',
                '[Platform Services](../platform_services/CLAUDE.md)',
                content
            )
        
        # Fix docs references from services
        if str(relative_path).startswith('services/'):
            depth = len(path_parts) - 1  # Exclude CLAUDE.md
            docs_prefix = "../" * depth + "docs/"
            
            # Fix common docs references
            docs_fixes = {
                r'\[API Documentation\]\(\.\./api/CLAUDE\.md\)': f'[API Documentation]({docs_prefix}api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./architecture/CLAUDE\.md\)': f'[Architecture]({docs_prefix}architecture/CLAUDE.md)',
                r'\[Development Guide\]\(\.\./development/CLAUDE\.md\)': f'[Development Guide]({docs_prefix}development/CLAUDE.md)',
                r'\[Deployment Guide\]\(\.\./deployment/CLAUDE\.md\)': f'[Deployment Guide]({docs_prefix}deployment/CLAUDE.md)'
            }
            
            for pattern, replacement in docs_fixes.items():
                content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_docs_subdirectory_links(self, content: str, file_path: Path) -> str:
        """Fix links within docs subdirectories"""
        relative_path = file_path.relative_to(self.project_root)
        
        if not str(relative_path).startswith('docs/'):
            return content
        
        path_parts = relative_path.parts
        
        if len(path_parts) == 3:  # docs/category/CLAUDE.md
            # Fix sibling directory references
            sibling_fixes = {
                r'\[API Documentation\]\(\.\./api/CLAUDE\.md\)': '[API Documentation](../api/CLAUDE.md)',
                r'\[Architecture\]\(\.\./architecture/CLAUDE\.md\)': '[Architecture](../architecture/CLAUDE.md)',
                r'\[Development Guide\]\(\.\./development/CLAUDE\.md\)': '[Development Guide](../development/CLAUDE.md)',
                r'\[Deployment Guide\]\(\.\./deployment/CLAUDE\.md\)': '[Deployment Guide](../deployment/CLAUDE.md)',
                r'\[Security\]\(\.\./security/CLAUDE\.md\)': '[Security](../security/CLAUDE.md)',
                r'\[Testing\]\(\.\./testing/CLAUDE\.md\)': '[Testing](../testing/CLAUDE.md)'
            }
            
            for pattern, replacement in sibling_fixes.items():
                content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_infrastructure_links(self, content: str, file_path: Path) -> str:
        """Fix links within infrastructure directory"""
        relative_path = file_path.relative_to(self.project_root)
        
        if not str(relative_path).startswith('infrastructure/'):
            return content
        
        # Fix infrastructure subdirectory references
        infra_fixes = {
            r'\[Docker\]\(\.\./\.\./docker/CLAUDE\.md\)': '[Docker](../docker/CLAUDE.md)',
            r'\[Kubernetes\]\(\.\./\.\./kubernetes/CLAUDE\.md\)': '[Kubernetes](../kubernetes/CLAUDE.md)',
            r'\[Terraform\]\(\.\./\.\./terraform/CLAUDE\.md\)': '[Terraform](../terraform/CLAUDE.md)',
            r'\[Monitoring\]\(\.\./\.\./monitoring/CLAUDE\.md\)': '[Monitoring](../monitoring/CLAUDE.md)'
        }
        
        for pattern, replacement in infra_fixes.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def validate_and_fix_specific_links(self, content: str, file_path: Path) -> str:
        """Validate and fix specific broken links"""
        
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def fix_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links
            if link_url.startswith(('http', '#', 'mailto:')):
                return match.group(0)
            
            # Check if link exists
            if link_url.startswith('/'):
                # Absolute path
                target_path = self.project_root / link_url.lstrip('/')
            else:
                # Relative path
                target_path = file_path.parent / link_url
            
            try:
                target_path = target_path.resolve()
                if target_path.exists():
                    return match.group(0)  # Link is valid
            except:
                pass
            
            # Try to fix the link
            if link_url in self.link_fixes:
                fixed_url = self.link_fixes[link_url]
                return f'[{link_text}]({fixed_url})'
            
            # Try intelligent path calculation
            if link_url.endswith('/CLAUDE.md'):
                target_dir = link_url.replace('/CLAUDE.md', '').split('/')[-1]
                correct_path = self.calculate_correct_path(file_path, target_dir)
                if correct_path:
                    return f'[{link_text}]({correct_path})'
            
            return match.group(0)  # Return original if can't fix
        
        return re.sub(link_pattern, fix_link, content)
    
    def fix_file_links(self, file_path: Path) -> bool:
        """Fix all links in a single file"""
        try:
            content = file_path.read_text()
            original_content = content
            
            # Apply different fixing strategies
            content = self.fix_service_directory_links(content, file_path)
            content = self.fix_docs_subdirectory_links(content, file_path)
            content = self.fix_infrastructure_links(content, file_path)
            content = self.validate_and_fix_specific_links(content, file_path)
            
            # Only write if content changed
            if content != original_content:
                file_path.write_text(content)
                print(f"  ✅ Fixed: {file_path.relative_to(self.project_root)}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def execute_advanced_link_fixing(self):
        """Execute advanced link fixing to reach >80% validity"""
        print("🚀 Starting ACGS-2 Advanced Link Fixing")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target: >80% cross-reference validity")
        
        try:
            # Find all CLAUDE.md files
            claude_files = []
            for file_path in self.project_root.rglob("CLAUDE.md"):
                if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                    continue
                claude_files.append(file_path)
            
            print(f"\n📁 Found {len(claude_files)} CLAUDE.md files")
            print(f"📊 Directory map: {len(self.directory_map)} directories indexed")
            
            # Fix links in each file
            print("\n🔗 Applying advanced link fixes...")
            fixed_count = 0
            
            for file_path in claude_files:
                if self.fix_file_links(file_path):
                    fixed_count += 1
            
            print(f"\n✅ Advanced link fixing completed!")
            print(f"📊 Summary:")
            print(f"  - Files processed: {len(claude_files)}")
            print(f"  - Files with fixes applied: {fixed_count}")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            
            return True
            
        except Exception as e:
            print(f"❌ Advanced link fixing failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    fixer = AdvancedLinkFixer(project_root)
    
    # Execute advanced link fixing
    success = fixer.execute_advanced_link_fixing()
    
    if success:
        print("\n🎉 Advanced Link Fixing Complete!")
        print("Next: Run cross-reference validation to verify >80% target achievement")
    else:
        print("\n❌ Advanced link fixing encountered issues.")

if __name__ == "__main__":
    main()
