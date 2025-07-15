#!/usr/bin/env python3
"""
Fix claude.md references to CLAUDE.md in all CLAUDE.md files
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_claude_md_files(project_root: Path) -> List[Path]:
    """Find all CLAUDE.md files in the project"""
    claude_files = []
    for file_path in project_root.rglob("CLAUDE.md"):
        # Skip virtual environments and build directories
        if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules']):
            continue
        claude_files.append(file_path)
    return claude_files

def fix_references_in_file(file_path: Path) -> Tuple[int, List[str]]:
    """Fix claude.md references to CLAUDE.md in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Pattern to match claude.md references in markdown links
        patterns = [
            (r'\[([^\]]+)\]\(([^)]*?)claude\.md\)', r'[\1](\2CLAUDE.md)'),
            (r'\[([^\]]+)\]\(([^)]*?)claude\.md#([^)]+)\)', r'[\1](\2CLAUDE.md#\3)'),
            (r'claude\.md', 'CLAUDE.md'),  # Simple text references
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes.extend([f"Fixed reference: {match}" for match in matches])
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(changes), changes
        
        return 0, []
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, []

def main():
    """Main function to fix all claude.md references"""
    project_root = Path("/home/dislove/ACGS-2")
    
    print("🔧 Fixing claude.md references to CLAUDE.md...")
    print("=" * 50)
    
    claude_files = find_claude_md_files(project_root)
    print(f"Found {len(claude_files)} CLAUDE.md files")
    
    total_changes = 0
    files_modified = 0
    
    for file_path in claude_files:
        rel_path = file_path.relative_to(project_root)
        changes_count, changes = fix_references_in_file(file_path)
        
        if changes_count > 0:
            files_modified += 1
            total_changes += changes_count
            print(f"✅ {rel_path}: {changes_count} references fixed")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   - {change}")
            if len(changes) > 3:
                print(f"   - ... and {len(changes) - 3} more")
        else:
            print(f"⚪ {rel_path}: No changes needed")
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Files processed: {len(claude_files)}")
    print(f"   Files modified: {files_modified}")
    print(f"   Total references fixed: {total_changes}")
    print(f"   Constitutional Hash: cdd01ef066bc6cf2")

if __name__ == "__main__":
    main()
