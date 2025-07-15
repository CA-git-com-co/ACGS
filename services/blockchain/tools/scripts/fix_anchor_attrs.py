#!/usr/bin/env python3
"""
Fix Anchor max_len attributes for String and Vec fields
Constitutional Hash: cdd01ef066bc6cf2
"""

import re
import os

def fix_anchor_attributes(file_path):
    """Add max_len attributes to String and Vec fields in Anchor structs."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match pub field_name: String, without existing max_len
    string_pattern = r'(\s+)(pub\s+\w+:\s+String,)(?!\s*#\[max_len)'
    # Pattern to match pub field_name: Vec<Type>, without existing max_len  
    vec_pattern = r'(\s+)(pub\s+\w+:\s+Vec<[^>]+>,)(?!\s*#\[max_len)'
    
    # Add max_len attributes for String fields
    content = re.sub(string_pattern, r'\1#[max_len(64)]\n\1\2', content)
    
    # Add max_len attributes for Vec fields  
    content = re.sub(vec_pattern, r'\1#[max_len(100)]\n\1\2', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed max_len attributes in {file_path}")

# Files that need fixing based on compilation errors
files_to_fix = [
    'cost_optimization/cost_analyzer.rs',
    'monitoring/observability.rs',
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_anchor_attributes(file_path)
    else:
        print(f"File not found: {file_path}")

print("All Anchor attribute fixes completed!")