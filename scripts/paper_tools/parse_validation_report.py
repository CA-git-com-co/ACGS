#!/usr/bin/env python3
"""
Paper Validation Report Parser

This script parses academic paper validation reports and extracts critical issues
into a structured YAML format for tracking and resolution.

Critical issues extracted:
- Missing figures
- LaTeX errors
- Abstract length violations
- Accessibility warnings

Output: paper_issues.yml with severity tags
"""

import yaml
import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
REPORT_PATH = '/home/dislove/ACGS-2/reports/paper_validation/latest_validation.md'
OUTPUT_PATH = '/home/dislove/ACGS-2/scripts/paper_tools/paper_issues.yml'

# Severity mapping
SEVERITY_MAP = {
    "PASS": "low",
    "WARNING": "medium",
    "FAIL": "high"
}

# Critical issue categories we care about
CRITICAL_CATEGORIES = {
    "Figures": "missing_figures",
    "LaTeX Syntax": "latex_errors", 
    "Content Quality": "content_issues",
    "Accessibility": "accessibility_warnings"
}

def parse_validation_report(report_path):
    """Parse the validation report and extract structured data."""
    
    if not os.path.exists(report_path):
        print(f"Error: Validation report not found at {report_path}")
        return {}
    
    with open(report_path, 'r') as file:
        content = file.read()
    
    sections = {}
    current_section = None
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Parse section headers
        if line.startswith('###'):
            # Extract section name (remove emoji and formatting)
            section_match = re.search(r'### [✅⚠️❌]+ (.+)', line)
            if section_match:
                current_section = section_match.group(1).strip()
                sections[current_section] = {
                    'status': None,
                    'message': '',
                    'details': {},
                    'raw_line': line
                }
        
        # Parse status
        elif line.startswith('- **Status**:') and current_section:
            status = line.split(':', 1)[1].strip()
            sections[current_section]['status'] = status
        
        # Parse message
        elif line.startswith('- **Message**:') and current_section:
            message = line.split(':', 1)[1].strip()
            sections[current_section]['message'] = message
        
        # Parse details (JSON)
        elif line.startswith('- **Details**:') and current_section:
            # Collect JSON lines - look for content between { and }
            json_lines = []
            i += 1
            brace_count = 0
            json_started = False
            
            while i < len(lines):
                json_line = lines[i]
                
                # Check if we hit a new section
                if json_line.strip().startswith('###') and json_started:
                    i -= 1  # Go back one line
                    break
                
                # Start collecting when we see opening brace
                if '{' in json_line:
                    json_started = True
                
                if json_started:
                    json_lines.append(json_line)
                    
                    # Count braces to find end of JSON
                    brace_count += json_line.count('{') - json_line.count('}')
                    
                    if brace_count == 0 and json_line.strip().endswith('}'):
                        break
                
                i += 1
            
            # Parse JSON
            json_content = '\n'.join(json_lines)
            try:
                details = json.loads(json_content)
                sections[current_section]['details'] = details
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON for {current_section}: {e}")
                # Try to extract key information manually
                details = {'raw': json_content, 'parsed': False}
                
                # Try to extract issues array
                if '"issues"' in json_content:
                    issues_match = re.search(r'"issues"\s*:\s*\[([^\]]+)\]', json_content, re.DOTALL)
                    if issues_match:
                        issues_text = issues_match.group(1)
                        # Extract quoted strings
                        issues = re.findall(r'"([^"]+)"', issues_text)
                        details['issues'] = issues
                
                # Try to extract missing_figures array
                if '"missing_figures"' in json_content:
                    missing_match = re.search(r'"missing_figures"\s*:\s*\[([^\]]+)\]', json_content, re.DOTALL)
                    if missing_match:
                        missing_text = missing_match.group(1)
                        missing_figures = re.findall(r'"([^"]+)"', missing_text)
                        details['missing_figures'] = missing_figures
                
                sections[current_section]['details'] = details
        
        i += 1
    
    return sections

def extract_critical_issues(sections):
    """Extract critical issues from parsed sections."""
    
    critical_issues = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_report': REPORT_PATH,
            'parser_version': '1.0.0'
        },
        'issues': {}
    }
    
    for section_name, section_data in sections.items():
        status = section_data.get('status', '')
        
        # Only process non-PASS statuses
        if status in ['WARNING', 'FAIL']:
            severity = SEVERITY_MAP.get(status, 'medium')
            
            # Categorize the issue
            category = CRITICAL_CATEGORIES.get(section_name, 'other')
            
            issue = {
                'severity': severity,
                'category': category,
                'section': section_name,
                'status': status,
                'message': section_data.get('message', ''),
                'details': section_data.get('details', {})
            }
            
            # Add specific processing for each critical category
            if section_name == 'Figures':
                issue['action_items'] = [
                    'Add missing figure files',
                    'Fix figure references in LaTeX',
                    'Verify figure paths are correct'
                ]
                missing_figures = section_data.get('details', {}).get('missing_figures', [])
                if missing_figures:
                    issue['missing_files'] = missing_figures
            
            elif section_name == 'LaTeX Syntax':
                issue['action_items'] = [
                    'Fix LaTeX syntax errors',
                    'Check for unmatched braces',
                    'Validate LaTeX compilation'
                ]
                latex_issues = section_data.get('details', {}).get('issues', [])
                if latex_issues:
                    issue['latex_errors'] = latex_issues
            
            elif section_name == 'Content Quality':
                issue['action_items'] = [
                    'Reduce abstract length',
                    'Review content quality standards',
                    'Check word count limits'
                ]
                content_issues = section_data.get('details', {}).get('issues', [])
                if content_issues:
                    issue['content_problems'] = content_issues
            
            elif section_name == 'Accessibility':
                issue['action_items'] = [
                    'Add captions to figures',
                    'Reduce reliance on color-only information',
                    'Improve accessibility compliance'
                ]
                accessibility_issues = section_data.get('details', {}).get('issues', [])
                if accessibility_issues:
                    issue['accessibility_problems'] = accessibility_issues
            
            # Add to critical issues
            issue_key = f"{category}_{status.lower()}"
            critical_issues['issues'][issue_key] = issue
    
    return critical_issues

def save_issues_yaml(issues, output_path):
    """Save issues to YAML file."""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as outfile:
        yaml.dump(issues, outfile, default_flow_style=False, sort_keys=False)
    
    print(f"Paper issues saved to: {output_path}")

def main():
    """Main function to parse validation report and generate issues YAML."""
    
    print("Parsing validation report...")
    sections = parse_validation_report(REPORT_PATH)
    
    if not sections:
        print("No sections found in validation report")
        return 1
    
    print(f"Found {len(sections)} sections in validation report")
    
    print("Extracting critical issues...")
    critical_issues = extract_critical_issues(sections)
    
    print(f"Found {len(critical_issues['issues'])} critical issues")
    
    print("Saving issues to YAML...")
    save_issues_yaml(critical_issues, OUTPUT_PATH)
    
    # Print summary
    print("\nCritical Issues Summary:")
    for issue_key, issue in critical_issues['issues'].items():
        print(f"  - {issue['section']}: {issue['severity']} ({issue['status']})")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

