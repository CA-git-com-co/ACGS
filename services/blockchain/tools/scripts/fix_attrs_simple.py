#!/usr/bin/env python3
"""
Simple fix for Anchor max_len attributes
Constitutional Hash: cdd01ef066bc6cf2
"""

import re

def fix_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Remove lines that only contain #[max_len(...)] followed by whitespace
    content = re.sub(r'\n\s*#\[max_len\([^\]]+\)\]\s*\n\s*\n', '\n', content)
    
    # Fix lines where max_len is on its own line before a field
    content = re.sub(r'(\s*)#\[max_len\([^\]]+\)\]\s*\n\s*\n(\s*pub\s+\w+:\s+(?:String|Vec<[^>]+>),)', r'\1#[max_len(64)]\n\2', content)
    
    with open(filename, 'w') as f:
        f.write(content)

# Fix the files
fix_file('cost_optimization/cost_analyzer.rs')
fix_file('monitoring/observability.rs')

print("Fixed attribute formatting")