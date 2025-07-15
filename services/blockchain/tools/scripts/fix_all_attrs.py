#!/usr/bin/env python3
"""
Comprehensive fix for Anchor max_len attributes
Constitutional Hash: cdd01ef066bc6cf2
"""

import re

def add_max_len_attributes(content):
    """Add max_len attributes to String and Vec fields in structs."""
    
    # Pattern to find struct definitions and add max_len to String/Vec fields
    lines = content.split('\n')
    result_lines = []
    in_struct = False
    
    for i, line in enumerate(lines):
        result_lines.append(line)
        
        # Check if we're entering a struct
        if re.match(r'pub struct \w+', line):
            in_struct = True
            continue
            
        # Check if we're exiting a struct
        if in_struct and line.strip() == '}':
            in_struct = False
            continue
            
        # If we're in a struct and find a pub field that's String or Vec without max_len
        if in_struct and re.match(r'\s+pub\s+\w+:\s+(String|Vec<[^>]+>),', line):
            # Check if the previous line already has max_len
            if i > 0 and '#[max_len(' not in lines[i-1]:
                # Insert max_len attribute before the field
                indent = re.match(r'(\s*)', line).group(1)
                if 'String' in line:
                    result_lines.insert(-1, f'{indent}#[max_len(64)]')
                else:  # Vec
                    result_lines.insert(-1, f'{indent}#[max_len(100)]')
    
    return '\n'.join(result_lines)

# Fix the files
for filename in ['cost_optimization/cost_analyzer.rs', 'monitoring/observability.rs']:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        fixed_content = add_max_len_attributes(content)
        
        with open(filename, 'w') as f:
            f.write(fixed_content)
        
        print(f"Fixed {filename}")
    except Exception as e:
        print(f"Error fixing {filename}: {e}")

print("Completed fixing all max_len attributes")