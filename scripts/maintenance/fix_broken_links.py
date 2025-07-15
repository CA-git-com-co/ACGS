#!/usr/bin/env python3
"""
ACGS-2 Broken Links Repair Tool
Constitutional Hash: cdd01ef066bc6cf2

This tool identifies and fixes broken internal links in ACGS-2 documentation
to improve navigation and documentation quality.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
import subprocess

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class BrokenLinksRepairer:
    """Repair broken internal links in ACGS-2 documentation."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # File patterns to check
        self.include_patterns = [
            "**/*.md",
            "**/*.rst"
        ]
        
        # Exclude patterns
        self.exclude_patterns = [
            "**/node_modules/**",
            "**/venv/**",
            "**/.venv/**",
            "**/target/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/vendor/**",
            "**/__pycache__/**",
            "**/.pytest_cache/**",
            "**/site-packages/**",
            "**/dist-info/**",
            "**/egg-info/**"
        ]
        
        # Critical files that need working links
        self.critical_files = [
            "docs/README.md",
            "docs/claude.md", 
            "services/claude.md",
            "docs/api/claude.md",
            "infrastructure/claude.md",
            "config/claude.md"
        ]

    def find_documentation_files(self) -> List[Path]:
        """Find all documentation files to check."""
        files = []
        for pattern in self.include_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in self.exclude_patterns:
                    if file_path.match(exclude_pattern):
                        should_exclude = True
                        break
                
                if not should_exclude and file_path.is_file():
                    files.append(file_path)
        
        return sorted(files)

    def extract_internal_links(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract internal links from a file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Pattern for markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            internal_links = []
            
            for line_num, line in enumerate(lines, 1):
                matches = re.findall(link_pattern, line)
                
                for link_text, link_url in matches:
                    # Skip external URLs
                    if link_url.startswith(('http://', 'https://', 'mailto:')):
                        continue
                    
                    # Skip anchors
                    if link_url.startswith('#'):
                        continue
                    
                    internal_links.append((link_text, link_url, line_num))
            
            return internal_links
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []

    def check_link_target(self, source_file: Path, link_url: str) -> bool:
        """Check if a link target exists."""
        try:
            # Handle relative paths
            if link_url.startswith('./') or link_url.startswith('../'):
                target_path = (source_file.parent / link_url).resolve()
            else:
                target_path = (self.project_root / link_url).resolve()
            
            return target_path.exists()
            
        except Exception:
            return False

    def suggest_link_fix(self, source_file: Path, link_url: str) -> str:
        """Suggest a fix for a broken link."""
        # Extract filename from broken link
        filename = Path(link_url).name
        
        # Search for files with similar names
        for pattern in self.include_patterns:
            for candidate in self.project_root.rglob(pattern):
                if candidate.name == filename:
                    # Calculate relative path from source to candidate
                    try:
                        rel_path = os.path.relpath(candidate, source_file.parent)
                        return rel_path
                    except ValueError:
                        continue
        
        return None

    def analyze_broken_links(self) -> Dict[str, List[Tuple[str, str, int, str]]]:
        """Analyze all broken links in documentation."""
        print(f"🔍 ACGS-2 Broken Links Analysis")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print("=" * 60)
        
        files = self.find_documentation_files()
        print(f"📁 Analyzing {len(files)} documentation files...")
        
        broken_links = {}
        total_links = 0
        broken_count = 0
        
        for file_path in files:
            internal_links = self.extract_internal_links(file_path)
            file_broken_links = []
            
            for link_text, link_url, line_num in internal_links:
                total_links += 1
                
                if not self.check_link_target(file_path, link_url):
                    broken_count += 1
                    suggested_fix = self.suggest_link_fix(file_path, link_url)
                    file_broken_links.append((link_text, link_url, line_num, suggested_fix))
            
            if file_broken_links:
                broken_links[str(file_path.relative_to(self.project_root))] = file_broken_links
        
        print(f"📊 Analysis Results:")
        print(f"   Total internal links: {total_links}")
        print(f"   Broken links: {broken_count}")
        print(f"   Files with broken links: {len(broken_links)}")
        print(f"   Broken link rate: {(broken_count/total_links*100):.1f}%" if total_links > 0 else "   No links found")
        
        return broken_links

    def fix_critical_broken_links(self, broken_links: Dict[str, List[Tuple[str, str, int, str]]], dry_run: bool = False) -> int:
        """Fix broken links in critical files."""
        print(f"\n🔧 Fixing Critical Broken Links")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE REPAIR'}")
        print("-" * 40)
        
        fixes_applied = 0
        
        # Focus on critical files first
        for file_path_str, file_broken_links in broken_links.items():
            file_path = self.project_root / file_path_str
            
            # Check if this is a critical file
            is_critical = any(cf in file_path_str for cf in self.critical_files)
            
            if not is_critical:
                continue
            
            print(f"\n📝 Processing critical file: {file_path_str}")
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                modified_content = content
                
                for link_text, broken_url, line_num, suggested_fix in file_broken_links:
                    if suggested_fix:
                        # Replace the broken link with the suggested fix
                        old_link = f"[{link_text}]({broken_url})"
                        new_link = f"[{link_text}]({suggested_fix})"
                        
                        if old_link in modified_content:
                            modified_content = modified_content.replace(old_link, new_link)
                            fixes_applied += 1
                            
                            if dry_run:
                                print(f"   🔍 Would fix: {broken_url} → {suggested_fix}")
                            else:
                                print(f"   ✅ Fixed: {broken_url} → {suggested_fix}")
                        else:
                            print(f"   ⚠️  Could not locate link: {old_link}")
                    else:
                        print(f"   ❌ No fix found for: {broken_url}")
                
                # Write the modified content back to file
                if not dry_run and modified_content != content:
                    file_path.write_text(modified_content, encoding='utf-8')
                    print(f"   💾 Updated file: {file_path_str}")
                
            except Exception as e:
                print(f"   ❌ Error processing {file_path_str}: {e}")
        
        return fixes_applied

    def create_missing_critical_files(self, broken_links: Dict[str, List[Tuple[str, str, int, str]]], dry_run: bool = False) -> int:
        """Create missing critical files that are frequently referenced."""
        print(f"\n📁 Creating Missing Critical Files")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE CREATION'}")
        print("-" * 40)
        
        # Count references to missing files
        missing_file_refs = {}
        
        for file_path_str, file_broken_links in broken_links.items():
            for link_text, broken_url, line_num, suggested_fix in file_broken_links:
                if not suggested_fix:  # No existing file found
                    target_path = Path(broken_url)
                    if target_path.suffix in ['.md', '.rst']:
                        if broken_url not in missing_file_refs:
                            missing_file_refs[broken_url] = []
                        missing_file_refs[broken_url].append((file_path_str, link_text))
        
        # Create files that are referenced multiple times
        files_created = 0
        
        for missing_file, references in missing_file_refs.items():
            if len(references) >= 2:  # Referenced by at least 2 files
                target_path = self.project_root / missing_file
                
                if dry_run:
                    print(f"   🔍 Would create: {missing_file} (referenced {len(references)} times)")
                else:
                    try:
                        # Create directory if it doesn't exist
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Create basic file content
                        content = f"""# {target_path.stem.replace('_', ' ').replace('-', ' ').title()}

<!-- Constitutional Hash: {self.constitutional_hash} -->

## Overview

This documentation file was automatically created to resolve broken links in the ACGS-2 documentation system.

## Referenced By

"""
                        for ref_file, link_text in references:
                            content += f"- [{link_text}]({ref_file})\n"
                        
                        content += f"""
## Status

❌ **PLACEHOLDER** - This file needs to be properly documented.

---

**Constitutional Hash**: `{self.constitutional_hash}`  
**Auto-generated**: {Path(__file__).name}  
**Purpose**: Resolve broken documentation links
"""
                        
                        target_path.write_text(content, encoding='utf-8')
                        files_created += 1
                        print(f"   ✅ Created: {missing_file} (referenced {len(references)} times)")
                        
                    except Exception as e:
                        print(f"   ❌ Error creating {missing_file}: {e}")
        
        return files_created

def main():
    """Main repair function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix broken links in ACGS-2 documentation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze broken links without fixing')
    parser.add_argument('--create-missing', action='store_true', help='Create missing files that are frequently referenced')
    
    args = parser.parse_args()
    
    repairer = BrokenLinksRepairer()
    
    # Analyze broken links
    broken_links = repairer.analyze_broken_links()
    
    if args.analyze_only:
        # Show detailed analysis
        print(f"\n📋 Detailed Broken Links Report:")
        print("=" * 60)
        
        for file_path, file_broken_links in list(broken_links.items())[:10]:  # Show first 10 files
            print(f"\n📄 {file_path}:")
            for link_text, broken_url, line_num, suggested_fix in file_broken_links[:5]:  # Show first 5 links
                print(f"   Line {line_num}: [{link_text}]({broken_url})")
                if suggested_fix:
                    print(f"      → Suggested fix: {suggested_fix}")
                else:
                    print(f"      → No fix found")
        
        if len(broken_links) > 10:
            print(f"\n... and {len(broken_links) - 10} more files with broken links")
        
        return 0
    
    # Fix critical broken links
    fixes_applied = repairer.fix_critical_broken_links(broken_links, dry_run=args.dry_run)
    
    # Create missing files if requested
    files_created = 0
    if args.create_missing:
        files_created = repairer.create_missing_critical_files(broken_links, dry_run=args.dry_run)
    
    print(f"\n" + "=" * 60)
    print(f"📊 REPAIR SUMMARY")
    print("=" * 60)
    print(f"Broken links fixed: {fixes_applied}")
    print(f"Missing files created: {files_created}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE REPAIR'}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
