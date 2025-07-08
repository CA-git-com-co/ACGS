#!/usr/bin/env python3
"""Find commented out code blocks in Python files."""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_commented_code_blocks(file_path: Path) -> List[Tuple[int, int, str]]:
    """Find potential commented code blocks in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return []
    
    commented_blocks = []
    in_block_comment = False
    block_start = 0
    block_lines = []
    
    # Pattern to detect likely code in comments
    code_patterns = [
        r'^\s*#\s*(if|for|while|def|class|import|from|return|print|raise|try|except|with)',
        r'^\s*#\s*\w+\s*=',  # assignments
        r'^\s*#\s*\w+\(',    # function calls
        r'^\s*#\s*@\w+',     # decorators
    ]
    
    for i, line in enumerate(lines):
        # Skip lines that are likely documentation
        if re.match(r'^\s*#\s*(TODO|NOTE|FIXME|XXX|HACK|WARNING):', line, re.IGNORECASE):
            continue
        
        # Check if line looks like commented code
        is_code_comment = any(re.match(pattern, line) for pattern in code_patterns)
        
        if is_code_comment:
            if not in_block_comment:
                in_block_comment = True
                block_start = i + 1
                block_lines = [line]
            else:
                block_lines.append(line)
        else:
            if in_block_comment and len(block_lines) >= 3:  # Only report blocks of 3+ lines
                preview = ''.join(block_lines[:3]).strip()
                if len(block_lines) > 3:
                    preview += '...'
                commented_blocks.append((block_start, i, preview))
            in_block_comment = False
            block_lines = []
    
    # Handle case where file ends with commented block
    if in_block_comment and len(block_lines) >= 3:
        preview = ''.join(block_lines[:3]).strip()
        if len(block_lines) > 3:
            preview += '...'
        commented_blocks.append((block_start, len(lines), preview))
    
    return commented_blocks

def main():
    directories = ['services/core', 'services/shared']
    
    total_files = 0
    files_with_commented_code = 0
    total_blocks = 0
    
    for directory in directories:
        if not Path(directory).exists():
            continue
        
        print(f"\n{'='*80}")
        print(f"Analyzing {directory} for commented code blocks")
        print(f"{'='*80}\n")
        
        for file_path in Path(directory).rglob("*.py"):
            # Skip certain directories
            if any(skip in str(file_path) for skip in [
                "__pycache__", ".venv", ".git", "node_modules",
                ".pytest_cache", ".mypy_cache", "build", "dist", "alembic"
            ]):
                continue
            
            total_files += 1
            blocks = find_commented_code_blocks(file_path)
            
            if blocks:
                files_with_commented_code += 1
                total_blocks += len(blocks)
                
                print(f"\n{file_path}")
                print("-" * len(str(file_path)))
                print(f"Found {len(blocks)} commented code blocks:")
                
                for start, end, preview in blocks:
                    lines = end - start + 1
                    print(f"\n  Lines {start}-{end} ({lines} lines):")
                    for line in preview.split('\n')[:3]:
                        if line.strip():
                            print(f"    {line.strip()}")
    
    print(f"\n{'='*80}")
    print(f"Summary: Found {total_blocks} commented code blocks in {files_with_commented_code}/{total_files} files")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()