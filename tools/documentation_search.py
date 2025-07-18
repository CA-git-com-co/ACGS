#!/usr/bin/env python3
'''
ACGS-2 Documentation Search Tool
Constitutional Hash: cdd01ef066bc6cf2
'''

import re
import json
from pathlib import Path
from typing import List, Dict

class DocumentationSearcher:
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self):
        self.project_root = Path(".").resolve()
        
    def search_documentation(self, query: str, file_types: List[str] = None) -> List[Dict]:
        '''Search across all documentation files'''
        
        if file_types is None:
            file_types = ["*.md", "*.py", "*.yml", "*.yaml"]
            
        results = []
        
        for pattern in file_types:
            for file_path in self.project_root.rglob(pattern):
                if self.should_skip_file(file_path):
                    continue
                    
                matches = self.search_file(file_path, query)
                if matches:
                    results.extend(matches)
                    
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
        
    def should_skip_file(self, file_path: Path) -> bool:
        '''Check if file should be skipped'''
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'target'}
        return any(skip in str(file_path) for skip in skip_dirs)
        
    def search_file(self, file_path: Path, query: str) -> List[Dict]:
        '''Search within a single file'''
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Search for query (case insensitive)
            query_lower = query.lower()
            
            for line_num, line in enumerate(lines, 1):
                if query_lower in line.lower():
                    # Calculate relevance score
                    relevance = self.calculate_relevance(line, query)
                    
                    matches.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'relevance': relevance,
                        'context': self.get_context(lines, line_num - 1)
                    })
                    
        except Exception as e:
            pass  # Skip files that can't be read
            
        return matches
        
    def calculate_relevance(self, line: str, query: str) -> float:
        '''Calculate relevance score for a match'''
        line_lower = line.lower()
        query_lower = query.lower()
        
        # Base score for containing the query
        score = 1.0
        
        # Boost for exact matches
        if query_lower == line_lower.strip():
            score += 5.0
            
        # Boost for header matches
        if line.strip().startswith('#'):
            score += 2.0
            
        # Boost for constitutional hash matches
        if self.CONSTITUTIONAL_HASH in line:
            score += 1.0
            
        return score
        
    def get_context(self, lines: List[str], line_index: int, context_size: int = 2) -> List[str]:
        '''Get context lines around a match'''
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        return lines[start:end]

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 documentation_search.py <query>")
        sys.exit(1)
        
    query = ' '.join(sys.argv[1:])
    searcher = DocumentationSearcher()
    results = searcher.search_documentation(query)
    
    print(f"🔍 Search results for: '{query}'")
    print(f"📊 Found {len(results)} matches")
    print()
    
    for i, result in enumerate(results[:20], 1):  # Show top 20 results
        print(f"{i}. {result['file']}:{result['line_number']}")
        print(f"   {result['line_content']}")
        print(f"   Relevance: {result['relevance']:.1f}")
        print()

if __name__ == "__main__":
    main()
