#!/usr/bin/env python3
"""
ACGS-2 Critical Missing Files Identifier
Constitutional Hash: cdd01ef066bc6cf2

This script identifies the most critical missing files based on cross-reference frequency.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

def analyze_broken_links(report_file: str = "claude_md_cross_reference_report.json") -> Dict[str, int]:
    """Analyze broken links to find most frequently referenced missing files"""
    try:
        with open(report_file, 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"Report file {report_file} not found. Run cross-reference validator first.")
        return {}
    
    # Count broken link frequencies
    broken_link_counter = Counter()
    
    for result in report['results']:
        for broken_link in result['broken_links']:
            # Extract the URL part after " -> "
            if " -> " in broken_link:
                url = broken_link.split(" -> ")[1]
                broken_link_counter[url] += 1
    
    return dict(broken_link_counter)

def categorize_missing_files(broken_links: Dict[str, int]) -> Dict[str, List[Tuple[str, int]]]:
    """Categorize missing files by type and priority"""
    categories = {
        'API Documentation': [],
        'Deployment Guides': [],
        'Configuration Files': [],
        'Testing Documentation': [],
        'Architecture Documentation': [],
        'Security Documentation': [],
        'Operations Documentation': [],
        'Development Documentation': [],
        'Other': []
    }
    
    for url, count in broken_links.items():
        if any(keyword in url.lower() for keyword in ['api', 'openapi', 'swagger']):
            categories['API Documentation'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['deploy', 'installation', 'setup']):
            categories['Deployment Guides'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['config', 'settings', 'env']):
            categories['Configuration Files'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['test', 'testing', 'spec']):
            categories['Testing Documentation'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['architecture', 'design', 'system']):
            categories['Architecture Documentation'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['security', 'auth', 'rbac']):
            categories['Security Documentation'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['operations', 'ops', 'monitoring']):
            categories['Operations Documentation'].append((url, count))
        elif any(keyword in url.lower() for keyword in ['development', 'dev', 'contributing']):
            categories['Development Documentation'].append((url, count))
        else:
            categories['Other'].append((url, count))
    
    # Sort each category by frequency (descending)
    for category in categories:
        categories[category].sort(key=lambda x: x[1], reverse=True)
    
    return categories

def generate_priority_list(categories: Dict[str, List[Tuple[str, int]]], top_n: int = 20) -> List[Tuple[str, int, str]]:
    """Generate priority list of files to create"""
    priority_files = []
    
    # Priority order for categories
    category_priority = [
        'API Documentation',
        'Deployment Guides', 
        'Configuration Files',
        'Architecture Documentation',
        'Security Documentation',
        'Operations Documentation',
        'Testing Documentation',
        'Development Documentation',
        'Other'
    ]
    
    for category in category_priority:
        for url, count in categories[category][:5]:  # Top 5 from each category
            priority_files.append((url, count, category))
            if len(priority_files) >= top_n:
                break
        if len(priority_files) >= top_n:
            break
    
    return priority_files

def main():
    print("🔍 Analyzing critical missing files...")
    
    # Analyze broken links
    broken_links = analyze_broken_links()
    if not broken_links:
        print("No broken links data available.")
        return
    
    print(f"Found {len(broken_links)} unique broken links")
    
    # Categorize missing files
    categories = categorize_missing_files(broken_links)
    
    print("\n📊 Missing Files by Category:")
    total_missing = 0
    for category, files in categories.items():
        if files:
            total_missing += len(files)
            print(f"\n  {category} ({len(files)} files):")
            for url, count in files[:3]:  # Show top 3 in each category
                print(f"    - {url} (referenced {count} times)")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    print(f"\nTotal missing files: {total_missing}")
    
    # Generate priority list
    priority_files = generate_priority_list(categories, 20)
    
    print(f"\n🎯 Top 20 Priority Files to Create:")
    for i, (url, count, category) in enumerate(priority_files, 1):
        print(f"  {i:2d}. {url}")
        print(f"      Category: {category}")
        print(f"      Referenced: {count} times")
        print()
    
    # Generate creation suggestions
    print("💡 Suggested Creation Order:")
    print("Phase 2A - High Impact Documentation (References > 5):")
    high_impact = [(url, count, cat) for url, count, cat in priority_files if count > 5]
    for i, (url, count, category) in enumerate(high_impact, 1):
        print(f"  {i}. {url} ({count} refs)")
    
    print(f"\nPhase 2B - Medium Impact Documentation (References 2-5):")
    medium_impact = [(url, count, cat) for url, count, cat in priority_files if 2 <= count <= 5]
    for i, (url, count, category) in enumerate(medium_impact, 1):
        print(f"  {i}. {url} ({count} refs)")
    
    print(f"\nPhase 2C - Low Impact Documentation (References 1):")
    low_impact = [(url, count, cat) for url, count, cat in priority_files if count == 1]
    print(f"  {len(low_impact)} files with single references")
    
    # Save detailed report
    report = {
        'summary': {
            'total_broken_links': len(broken_links),
            'total_categories': len([cat for cat, files in categories.items() if files]),
            'high_impact_files': len(high_impact),
            'medium_impact_files': len(medium_impact),
            'low_impact_files': len(low_impact)
        },
        'categories': {cat: [(url, count) for url, count in files] for cat, files in categories.items()},
        'priority_files': [(url, count, cat) for url, count, cat in priority_files]
    }
    
    with open('critical_missing_files_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed analysis saved to: critical_missing_files_analysis.json")

if __name__ == "__main__":
    main()
