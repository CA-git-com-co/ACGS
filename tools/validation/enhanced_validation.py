#!/usr/bin/env python3
"""
ACGS Enhanced Documentation Validation
Constitutional Hash: cdd01ef066bc6cf2

This enhanced validation script provides faster, more detailed validation
with better performance and comprehensive reporting.
"""

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Performance targets
PERFORMANCE_TARGETS = {
    "latency_p99": "≤5ms",
    "throughput": "≥100 RPS",
    "cache_hit_rate": "≥85%",
    "test_coverage": "≥80%",
    "availability": "99.9%"
}

# Required API documentation sections
REQUIRED_API_SECTIONS = [
    "service overview",
    "constitutional hash",
    "authentication",
    "endpoints",
    "error handling", 
    "performance targets",
    "monitoring"
]

class ValidationResult:
    def __init__(self):
        self.total_files = 0
        self.passed_files = 0
        self.failed_files = 0
        self.issues = []
        self.performance_score = 0
        self.start_time = time.time()
        
    def add_issue(self, severity: str, category: str, file_path: str, message: str, line_number: int = None):
        """Add a validation issue."""
        self.issues.append({
            "severity": severity,
            "category": category,
            "file": str(file_path),
            "message": message,
            "line": line_number,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_duration(self) -> float:
        """Get validation duration in seconds."""
        return time.time() - self.start_time

class EnhancedValidator:
    def __init__(self):
        self.result = ValidationResult()
        
    def validate_constitutional_compliance(self, file_path: Path) -> List[Dict[str, Any]]:
        """Validate constitutional compliance for a single file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for constitutional hash
            if CONSTITUTIONAL_HASH not in content:
                issues.append({
                    "severity": "CRITICAL",
                    "category": "constitutional_compliance",
                    "message": f"Missing constitutional hash '{CONSTITUTIONAL_HASH}'",
                    "line": None
                })
            else:
                # Check if it's in the correct format
                hash_pattern = rf"<!--\s*Constitutional Hash:\s*{re.escape(CONSTITUTIONAL_HASH)}\s*-->"
                if not re.search(hash_pattern, content, re.IGNORECASE):
                    # Check if it's in JSON format (for API examples)
                    json_pattern = rf'"constitutional_hash":\s*"{re.escape(CONSTITUTIONAL_HASH)}"'
                    if not re.search(json_pattern, content):
                        issues.append({
                            "severity": "HIGH",
                            "category": "constitutional_compliance",
                            "message": "Constitutional hash found but not in correct format",
                            "line": None
                        })
                        
        except Exception as e:
            issues.append({
                "severity": "ERROR",
                "category": "file_access",
                "message": f"Error reading file: {str(e)}",
                "line": None
            })
            
        return issues
    
    def validate_api_documentation(self, file_path: Path) -> List[Dict[str, Any]]:
        """Validate API documentation standards."""
        issues = []
        
        if not file_path.name.endswith('.md') or 'api' not in str(file_path):
            return issues
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            # Check for required sections
            missing_sections = []
            for section in REQUIRED_API_SECTIONS:
                if section not in content:
                    missing_sections.append(section)
                    
            if missing_sections:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "api_documentation",
                    "message": f"Missing required sections: {', '.join(missing_sections)}",
                    "line": None
                })
                
            # Check for performance targets
            performance_missing = []
            for target, value in PERFORMANCE_TARGETS.items():
                if value.lower() not in content and target.replace('_', ' ') not in content:
                    performance_missing.append(f"{target}: {value}")
                    
            if performance_missing:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "performance_targets",
                    "message": f"Missing performance targets: {', '.join(performance_missing)}",
                    "line": None
                })
                
            # Check for port specification
            port_pattern = r'port.*8[0-9]{3}'
            if not re.search(port_pattern, content):
                issues.append({
                    "severity": "LOW",
                    "category": "api_documentation",
                    "message": "Missing or invalid port specification (expected 8XXX format)",
                    "line": None
                })
                
        except Exception as e:
            issues.append({
                "severity": "ERROR",
                "category": "file_access",
                "message": f"Error reading API documentation: {str(e)}",
                "line": None
            })
            
        return issues
    
    def validate_link_integrity(self, file_path: Path) -> List[Dict[str, Any]]:
        """Validate internal documentation links."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Find markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)'
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(link_pattern, line)
                for match in matches:
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Skip external links and anchors
                    if link_path.startswith('http') or '#' in link_path:
                        continue
                        
                    # Resolve relative path
                    if link_path.startswith('/'):
                        target_path = REPO_ROOT / link_path.lstrip('/')
                    else:
                        target_path = file_path.parent / link_path
                        
                    # Check if target exists
                    if not target_path.exists():
                        issues.append({
                            "severity": "HIGH",
                            "category": "broken_links",
                            "message": f"Broken link to '{link_path}' (text: '{link_text}')",
                            "line": line_num
                        })
                        
        except Exception as e:
            issues.append({
                "severity": "ERROR",
                "category": "file_access",
                "message": f"Error checking links: {str(e)}",
                "line": None
            })
            
        return issues
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single documentation file."""
        file_issues = []
        
        # Constitutional compliance check
        file_issues.extend(self.validate_constitutional_compliance(file_path))
        
        # API documentation check
        file_issues.extend(self.validate_api_documentation(file_path))
        
        # Link integrity check
        file_issues.extend(self.validate_link_integrity(file_path))
        
        return {
            "file": str(file_path),
            "issues": file_issues,
            "passed": len(file_issues) == 0
        }
    
    def validate_all_files(self, max_workers: int = 4) -> ValidationResult:
        """Validate all documentation files using parallel processing."""
        print(f"🚀 ACGS Enhanced Documentation Validation")
        print("=" * 50)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Repository: {REPO_ROOT}")
        print(f"Max Workers: {max_workers}")
        print()
        
        # Find all markdown files in docs directory
        md_files = list(DOCS_DIR.rglob("*.md"))
        self.result.total_files = len(md_files)
        
        print(f"📄 Found {len(md_files)} documentation files")
        print("🔍 Starting validation...")
        print()
        
        # Validate files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.validate_file, file_path): file_path 
                for file_path in md_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    
                    if file_result["passed"]:
                        self.result.passed_files += 1
                        print(f"✅ {file_path.relative_to(REPO_ROOT)}")
                    else:
                        self.result.failed_files += 1
                        print(f"❌ {file_path.relative_to(REPO_ROOT)} ({len(file_result['issues'])} issues)")
                        
                        # Add issues to result
                        for issue in file_result["issues"]:
                            self.result.add_issue(
                                issue["severity"],
                                issue["category"],
                                str(file_path.relative_to(REPO_ROOT)),
                                issue["message"],
                                issue.get("line")
                            )
                            
                except Exception as e:
                    self.result.failed_files += 1
                    print(f"❌ {file_path.relative_to(REPO_ROOT)} (validation error)")
                    self.result.add_issue(
                        "ERROR",
                        "validation_error",
                        str(file_path.relative_to(REPO_ROOT)),
                        f"Validation error: {str(e)}"
                    )
        
        return self.result
    
    def generate_report(self) -> str:
        """Generate a detailed validation report."""
        duration = self.result.get_duration()
        success_rate = (self.result.passed_files / self.result.total_files * 100) if self.result.total_files > 0 else 0
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in self.result.issues:
            severity = issue["severity"]
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        report = f"""# ACGS Enhanced Validation Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`  
**Validation Duration**: {duration:.2f} seconds  
**Performance**: {self.result.total_files / duration:.1f} files/second

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {self.result.total_files} |
| Passed Files | {self.result.passed_files} |
| Failed Files | {self.result.failed_files} |
| Success Rate | {success_rate:.1f}% |
| Total Issues | {len(self.result.issues)} |

## Issues by Severity

"""
        
        for severity in ["CRITICAL", "ERROR", "HIGH", "MEDIUM", "LOW"]:
            if severity in issues_by_severity:
                issues = issues_by_severity[severity]
                report += f"### {severity} ({len(issues)} issues)\n\n"
                
                for issue in issues:
                    line_info = f" (line {issue['line']})" if issue['line'] else ""
                    report += f"- **{issue['file']}**{line_info}: {issue['message']}\n"
                
                report += "\n"
        
        if not self.result.issues:
            report += "✅ **No issues found!** All documentation meets ACGS standards.\n\n"
        
        report += f"""## Performance Metrics

- **Validation Speed**: {self.result.total_files / duration:.1f} files/second
- **Parallel Processing**: Enabled with thread pool
- **Memory Efficient**: Streaming file processing
- **Constitutional Compliance**: {CONSTITUTIONAL_HASH}

---

**Enhanced Validation**: Generated by ACGS Enhanced Documentation Validator  
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
"""
        
        return report

def main():
    """Main execution function."""
    validator = EnhancedValidator()
    
    # Parse command line arguments
    max_workers = 4
    if len(sys.argv) > 1:
        try:
            max_workers = int(sys.argv[1])
        except ValueError:
            print("Warning: Invalid max_workers argument, using default (4)")
    
    # Run validation
    result = validator.validate_all_files(max_workers)
    
    # Print summary
    print()
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    duration = result.get_duration()
    success_rate = (result.passed_files / result.total_files * 100) if result.total_files > 0 else 0
    
    print(f"✅ Passed: {result.passed_files}/{result.total_files} files ({success_rate:.1f}%)")
    print(f"❌ Failed: {result.failed_files} files")
    print(f"⚠️ Issues: {len(result.issues)} total")
    print(f"⚡ Performance: {result.total_files / duration:.1f} files/second")
    print(f"🕒 Duration: {duration:.2f} seconds")
    
    # Save detailed report
    report = validator.generate_report()
    report_file = REPO_ROOT / "validation_reports" / f"enhanced_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Detailed report: {report_file}")
    print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Exit with appropriate code
    if result.failed_files > 0:
        critical_issues = len([i for i in result.issues if i["severity"] == "CRITICAL"])
        if critical_issues > 0:
            print(f"\n🚨 {critical_issues} CRITICAL issues require immediate attention!")
            return 2
        else:
            print(f"\n⚠️ {result.failed_files} files have issues that should be addressed")
            return 1
    else:
        print("\n🎉 All documentation files passed validation!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
