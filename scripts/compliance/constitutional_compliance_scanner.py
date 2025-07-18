#!/usr/bin/env python3

"""
ACGS-2 Constitutional Compliance Scanner
Automated scan to verify constitutional hash compliance across the entire codebase
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import subprocess

# Constitutional compliance requirements
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REQUIRED_HASH_PATTERNS = [
    rf"constitutional.hash.*{CONSTITUTIONAL_HASH}",
    rf"Constitutional Hash.*{CONSTITUTIONAL_HASH}",
    rf"hash.*{CONSTITUTIONAL_HASH}",
    rf"{CONSTITUTIONAL_HASH}",
]

@dataclass
class ComplianceResult:
    """Compliance scan result for a single file"""
    file_path: str
    is_compliant: bool
    hash_found: bool
    patterns_matched: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)
    file_type: str = ""
    size_bytes: int = 0
    last_modified: str = ""
    issues: List[str] = field(default_factory=list)

@dataclass
class ComplianceReport:
    """Overall compliance report"""
    total_files: int = 0
    compliant_files: int = 0
    non_compliant_files: int = 0
    compliance_rate: float = 0.0
    files_by_type: Dict[str, int] = field(default_factory=dict)
    compliant_by_type: Dict[str, int] = field(default_factory=dict)
    results: List[ComplianceResult] = field(default_factory=list)
    scan_timestamp: str = ""
    scan_duration: float = 0.0


class ConstitutionalComplianceScanner:
    """Scanner for constitutional compliance across the ACGS-2 codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.hash_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in REQUIRED_HASH_PATTERNS]
        
        # File types that require constitutional compliance
        self.required_extensions = {
            '.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp', '.c', '.h',
            '.yml', '.yaml', '.json', '.md', '.toml', '.ini', '.conf',
            '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
            '.dockerfile', '.containerfile', '.sql', '.proto'
        }
        
        # Directories to exclude from scanning
        self.exclude_dirs = {
            '.git', '.github', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', '.idea', '.vscode', '.DS_Store',
            'build', 'dist', 'target', 'out', 'bin', 'obj',
            'migration_backup_*', 'docs_backup_*', 'docs_consolidated_archive_*',
            '.terraform', '.vagrant', 'logs', 'tmp', 'temp'
        }
        
        # Files to exclude from scanning
        self.exclude_files = {
            '.gitignore', '.dockerignore', '.env*', '*.log', '*.tmp',
            'package-lock.json', 'yarn.lock', 'Cargo.lock', 'go.sum',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx'
        }
        
    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned for constitutional compliance"""
        # Check if file extension requires compliance
        if file_path.suffix.lower() not in self.required_extensions:
            return False
            
        # Check if file is in excluded patterns
        for pattern in self.exclude_files:
            if file_path.match(pattern):
                return False
                
        # Check if file is in excluded directories
        for part in file_path.parts:
            if any(part.startswith(exclude) for exclude in self.exclude_dirs):
                return False
                
        # Check if file is readable
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to read first 100 bytes to check if it's a text file
                content = f.read(100)
                if '\x00' in content:  # Binary file
                    return False
            return True
        except (PermissionError, UnicodeDecodeError, OSError):
            return False
            
    def scan_file(self, file_path: Path) -> ComplianceResult:
        """Scan a single file for constitutional compliance"""
        result = ComplianceResult(
            file_path=str(file_path.relative_to(self.project_root)),
            is_compliant=False,
            hash_found=False,
            file_type=file_path.suffix.lower(),
            size_bytes=0,
            last_modified=""
        )
        
        try:
            # Get file stats
            stat = file_path.stat()
            result.size_bytes = stat.st_size
            result.last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for constitutional hash
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern in self.hash_patterns:
                    if pattern.search(line):
                        result.hash_found = True
                        result.patterns_matched.append(pattern.pattern)
                        result.line_numbers.append(line_num)
                        
            # Determine compliance
            result.is_compliant = result.hash_found
            
            # Check for specific issues
            if not result.hash_found:
                result.issues.append("Missing constitutional hash")
                
            # Check for secrets in example files
            if 'example' in file_path.name.lower() or 'template' in file_path.name.lower():
                secret_patterns = [
                    r'secret.*=.*[a-zA-Z0-9]{20,}',
                    r'key.*=.*[a-zA-Z0-9]{20,}',
                    r'password.*=.*[a-zA-Z0-9]{8,}',
                    r'token.*=.*[a-zA-Z0-9]{20,}'
                ]
                
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        result.issues.append("Potential secret in example file")
                        break
                        
        except Exception as e:
            result.issues.append(f"Scan error: {str(e)}")
            
        return result
        
    def scan_directory(self, directory: Path = None) -> List[ComplianceResult]:
        """Scan a directory recursively for constitutional compliance"""
        if directory is None:
            directory = self.project_root
            
        results = []
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and self.should_scan_file(file_path):
                    result = self.scan_file(file_path)
                    results.append(result)
                    
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
            
        return results
        
    def generate_report(self, results: List[ComplianceResult]) -> ComplianceReport:
        """Generate a comprehensive compliance report"""
        report = ComplianceReport(
            scan_timestamp=datetime.now().isoformat(),
            results=results
        )
        
        # Calculate basic metrics
        report.total_files = len(results)
        report.compliant_files = sum(1 for r in results if r.is_compliant)
        report.non_compliant_files = report.total_files - report.compliant_files
        
        if report.total_files > 0:
            report.compliance_rate = (report.compliant_files / report.total_files) * 100
            
        # Group by file type
        for result in results:
            file_type = result.file_type or 'unknown'
            report.files_by_type[file_type] = report.files_by_type.get(file_type, 0) + 1
            
            if result.is_compliant:
                report.compliant_by_type[file_type] = report.compliant_by_type.get(file_type, 0) + 1
                
        return report
        
    def print_report(self, report: ComplianceReport, verbose: bool = False):
        """Print a formatted compliance report"""
        print("\n" + "="*80)
        print("ACGS-2 CONSTITUTIONAL COMPLIANCE SCAN REPORT")
        print("="*80)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Scan Timestamp: {report.scan_timestamp}")
        print(f"Project Root: {self.project_root}")
        print()
        
        # Overall compliance
        print("OVERALL COMPLIANCE")
        print("-" * 40)
        print(f"Total Files Scanned: {report.total_files}")
        print(f"Compliant Files: {report.compliant_files}")
        print(f"Non-Compliant Files: {report.non_compliant_files}")
        print(f"Compliance Rate: {report.compliance_rate:.1f}%")
        print()
        
        # Compliance by file type
        print("COMPLIANCE BY FILE TYPE")
        print("-" * 40)
        for file_type in sorted(report.files_by_type.keys()):
            total = report.files_by_type[file_type]
            compliant = report.compliant_by_type.get(file_type, 0)
            rate = (compliant / total) * 100 if total > 0 else 0
            print(f"{file_type:>8}: {compliant:>3}/{total:<3} ({rate:>5.1f}%)")
        print()
        
        # Non-compliant files
        non_compliant = [r for r in report.results if not r.is_compliant]
        if non_compliant:
            print("NON-COMPLIANT FILES")
            print("-" * 40)
            for result in non_compliant[:20]:  # Show first 20
                print(f"❌ {result.file_path}")
                if result.issues:
                    for issue in result.issues:
                        print(f"   └─ {issue}")
            
            if len(non_compliant) > 20:
                print(f"   ... and {len(non_compliant) - 20} more files")
            print()
        
        # Files with issues
        issues = [r for r in report.results if r.issues]
        if issues and verbose:
            print("FILES WITH ISSUES")
            print("-" * 40)
            for result in issues:
                print(f"⚠️  {result.file_path}")
                for issue in result.issues:
                    print(f"   └─ {issue}")
            print()
            
        # Constitutional compliance status
        print("CONSTITUTIONAL COMPLIANCE STATUS")
        print("-" * 40)
        if report.compliance_rate >= 100.0:
            print("✅ FULLY COMPLIANT - All files contain constitutional hash")
        elif report.compliance_rate >= 95.0:
            print("🟡 MOSTLY COMPLIANT - Minor compliance gaps remain")
        else:
            print("❌ NON-COMPLIANT - Significant compliance gaps detected")
        print()
        
        # Recommendations
        if report.compliance_rate < 100.0:
            print("RECOMMENDATIONS")
            print("-" * 40)
            print("1. Add constitutional hash to all non-compliant files")
            print("2. Integrate this scanner into CI/CD pipeline")
            print("3. Set up pre-commit hooks to prevent non-compliant commits")
            print("4. Remove or secure any secrets found in example files")
            print()
            
    def save_report(self, report: ComplianceReport, output_file: str):
        """Save the compliance report to a file"""
        report_data = {
            'constitutional_hash': self.constitutional_hash,
            'scan_timestamp': report.scan_timestamp,
            'total_files': report.total_files,
            'compliant_files': report.compliant_files,
            'non_compliant_files': report.non_compliant_files,
            'compliance_rate': report.compliance_rate,
            'files_by_type': report.files_by_type,
            'compliant_by_type': report.compliant_by_type,
            'non_compliant_files': [
                {
                    'file_path': r.file_path,
                    'file_type': r.file_type,
                    'issues': r.issues,
                    'size_bytes': r.size_bytes,
                    'last_modified': r.last_modified
                }
                for r in report.results if not r.is_compliant
            ],
            'files_with_issues': [
                {
                    'file_path': r.file_path,
                    'file_type': r.file_type,
                    'issues': r.issues,
                    'is_compliant': r.is_compliant
                }
                for r in report.results if r.issues
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
    def fix_compliance_issues(self, report: ComplianceReport, dry_run: bool = True) -> int:
        """Automatically fix compliance issues where possible"""
        fixes_applied = 0
        
        for result in report.results:
            if not result.is_compliant and "Missing constitutional hash" in result.issues:
                file_path = self.project_root / result.file_path
                
                if not dry_run:
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Add constitutional hash comment based on file type
                        if result.file_type in ['.py']:
                            hash_comment = f'# Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.js', '.ts']:
                            hash_comment = f'// Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.rs']:
                            hash_comment = f'// Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.go']:
                            hash_comment = f'// Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.yml', '.yaml']:
                            hash_comment = f'# Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.sh', '.bash']:
                            hash_comment = f'# Constitutional Hash: {self.constitutional_hash}\n'
                        elif result.file_type in ['.md']:
                            hash_comment = f'<!-- Constitutional Hash: {self.constitutional_hash} -->\n'
                        else:
                            hash_comment = f'# Constitutional Hash: {self.constitutional_hash}\n'
                        
                        # Add hash comment at the top of the file
                        if not content.startswith(hash_comment):
                            content = hash_comment + content
                            
                            # Write back to file
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                                
                            fixes_applied += 1
                            print(f"✅ Fixed: {result.file_path}")
                            
                    except Exception as e:
                        print(f"❌ Failed to fix {result.file_path}: {e}")
                else:
                    print(f"Would fix: {result.file_path}")
                    fixes_applied += 1
                    
        return fixes_applied


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS-2 Constitutional Compliance Scanner"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Root directory of the ACGS-2 project"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for JSON report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including all issues"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix compliance issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run in CI mode (exit with error if compliance < 100%)"
    )
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = ConstitutionalComplianceScanner(args.project_root)
    
    print(f"Scanning {scanner.project_root} for constitutional compliance...")
    print(f"Constitutional Hash: {scanner.constitutional_hash}")
    
    # Scan all files
    results = scanner.scan_directory()
    
    # Generate report
    report = scanner.generate_report(results)
    
    # Print report
    scanner.print_report(report, args.verbose)
    
    # Save report if requested
    if args.output:
        scanner.save_report(report, args.output)
        print(f"Report saved to: {args.output}")
    
    # Fix issues if requested
    if args.fix or args.dry_run:
        fixes = scanner.fix_compliance_issues(report, args.dry_run)
        if args.dry_run:
            print(f"\nDry run: Would fix {fixes} files")
        else:
            print(f"\nFixed {fixes} compliance issues")
    
    # CI mode - exit with error if not fully compliant
    if args.ci:
        if report.compliance_rate < 100.0:
            print(f"\n❌ CI FAILURE: Compliance rate {report.compliance_rate:.1f}% < 100%")
            sys.exit(1)
        else:
            print(f"\n✅ CI SUCCESS: Full compliance achieved ({report.compliance_rate:.1f}%)")
    
    return 0 if report.compliance_rate >= 100.0 else 1


if __name__ == "__main__":
    sys.exit(main())