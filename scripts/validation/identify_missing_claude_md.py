#!/usr/bin/env python3
"""
ACGS-2 Missing Claude.md Identifier
Constitutional Hash: cdd01ef066bc6cf2

This script identifies directories that should have claude.md files but don't.
"""

import os
from pathlib import Path
from typing import List, Set

def find_existing_claude_files(project_root: Path) -> Set[str]:
    """Find all existing claude.md files"""
    claude_files = set()
    for file_path in project_root.rglob("claude.md"):
        # Skip virtual environments and build directories
        if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
            continue
        
        # Get directory path relative to project root
        dir_path = file_path.parent.relative_to(project_root)
        claude_files.add(str(dir_path))
    
    return claude_files

def find_candidate_directories(project_root: Path) -> Set[str]:
    """Find directories that should have claude.md files"""
    candidates = set()
    
    # Major directory patterns that should have claude.md
    major_patterns = [
        'services',
        'docs', 
        'config',
        'tests',
        'tools',
        'infrastructure',
        'training_data',
        'training_outputs'
    ]
    
    # Find all directories matching patterns
    for pattern in major_patterns:
        for dir_path in project_root.rglob(pattern):
            if not dir_path.is_dir():
                continue
                
            # Skip virtual environments, build directories, and deep nested paths
            path_str = str(dir_path)
            if any(skip in path_str for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target', '.pytest_cache']):
                continue
            
            # Skip very deep nested paths (more than 4 levels)
            rel_path = dir_path.relative_to(project_root)
            if len(rel_path.parts) > 4:
                continue
            
            # Add directory if it has significant content
            if has_significant_content(dir_path):
                candidates.add(str(rel_path))
    
    # Add specific important subdirectories
    important_subdirs = [
        'services/shared',
        'services/cli', 
        'services/contexts',
        'infrastructure/docker',
        'infrastructure/monitoring',
        'infrastructure/terraform',
        'docs/development',
        'docs/operations', 
        'docs/production',
        'tests/performance',
        'tests/security',
        'tests/unit',
        'training_data',
        'training_outputs'
    ]
    
    for subdir in important_subdirs:
        subdir_path = project_root / subdir
        if subdir_path.exists() and subdir_path.is_dir():
            candidates.add(subdir)
    
    return candidates

def has_significant_content(dir_path: Path) -> bool:
    """Check if directory has significant content worth documenting"""
    try:
        contents = list(dir_path.iterdir())
        
        # Must have at least 2 items
        if len(contents) < 2:
            return False
        
        # Check for significant file types
        significant_files = 0
        for item in contents:
            if item.is_file():
                # Count Python, JavaScript, YAML, Markdown, etc.
                if item.suffix in ['.py', '.js', '.ts', '.yaml', '.yml', '.md', '.json', '.toml', '.rs', '.go']:
                    significant_files += 1
            elif item.is_dir() and not item.name.startswith('.'):
                # Count subdirectories
                significant_files += 1
        
        return significant_files >= 2
    except PermissionError:
        return False

def main():
    project_root = Path("/home/dislove/ACGS-2")
    
    print("🔍 Identifying missing claude.md files...")
    print(f"Project root: {project_root}")
    
    # Find existing claude.md files
    existing_claude = find_existing_claude_files(project_root)
    print(f"\n✅ Found {len(existing_claude)} existing claude.md files:")
    for path in sorted(existing_claude):
        print(f"  - {path}")
    
    # Find candidate directories
    candidates = find_candidate_directories(project_root)
    print(f"\n📁 Found {len(candidates)} candidate directories:")
    for path in sorted(candidates):
        print(f"  - {path}")
    
    # Find missing claude.md files
    missing = candidates - existing_claude
    print(f"\n❌ Missing claude.md files ({len(missing)} directories):")
    
    # Categorize missing files
    categories = {
        'Services': [],
        'Documentation': [],
        'Infrastructure': [],
        'Testing': [],
        'Tools': [],
        'Training': [],
        'Configuration': []
    }
    
    for path in sorted(missing):
        if path.startswith('services/'):
            categories['Services'].append(path)
        elif path.startswith('docs/'):
            categories['Documentation'].append(path)
        elif path.startswith('infrastructure/'):
            categories['Infrastructure'].append(path)
        elif path.startswith('tests/'):
            categories['Testing'].append(path)
        elif path.startswith('tools/'):
            categories['Tools'].append(path)
        elif path.startswith('training'):
            categories['Training'].append(path)
        elif path.startswith('config/'):
            categories['Configuration'].append(path)
        else:
            categories['Services'].append(path)  # Default category
    
    for category, paths in categories.items():
        if paths:
            print(f"\n  {category}:")
            for path in paths:
                print(f"    - {path}")
    
    print(f"\n📊 Summary:")
    print(f"  - Existing claude.md files: {len(existing_claude)}")
    print(f"  - Missing claude.md files: {len(missing)}")
    print(f"  - Total target coverage: {len(candidates)}")
    print(f"  - Current coverage: {len(existing_claude)/len(candidates)*100:.1f}%")
    
    # Generate priority list
    priority_missing = [
        'services/shared',
        'services/cli', 
        'services/contexts',
        'infrastructure/docker',
        'infrastructure/monitoring',
        'infrastructure/terraform',
        'docs/development',
        'docs/operations', 
        'docs/production',
        'tests/performance',
        'tests/security',
        'tests/unit',
        'training_data',
        'training_outputs'
    ]
    
    actual_priority = [path for path in priority_missing if path in missing]
    print(f"\n🎯 Priority missing files ({len(actual_priority)}):")
    for path in actual_priority:
        print(f"  - {path}")

if __name__ == "__main__":
    main()
