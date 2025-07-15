#!/usr/bin/env python3
"""
ACGS-2 Claude.md Validation Framework
Constitutional Hash: cdd01ef066bc6cf2

This script validates claude.md files across the ACGS-2 project for:
- Constitutional compliance requirements
- Structural consistency
- Cross-reference integrity
- Performance indicator accuracy
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """Validation result for a claude.md file"""
    file_path: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    constitutional_hash_present: bool
    required_sections_present: List[str]
    missing_sections: List[str]
    cross_references: List[str]
    broken_links: List[str]

class ClaudeMdValidator:
    """Validator for claude.md files in ACGS-2 project"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    REQUIRED_SECTIONS = [
        "Directory Overview",
        "File Inventory", 
        "Dependencies & Interactions",
        "Key Components",
        "Constitutional Compliance Status",
        "Performance Considerations",
        "Implementation Status",
        "Cross-References & Navigation"
    ]
    
    REQUIRED_PATTERNS = {
        "constitutional_hash": r"<!-- Constitutional Hash: cdd01ef066bc6cf2 -->",
        "navigation_footer": r"\*\*Navigation\*\*:",
        "compliance_statement": r"\*\*Constitutional Compliance\*\*:",
        "status_indicators": r"[✅🔄❌]",
        "implementation_status": r"### (✅ IMPLEMENTED|🔄 IN PROGRESS|❌ PLANNED)"
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results: List[ValidationResult] = []
    
    def find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the project"""
        claude_files = []
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip virtual environments and build directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules']):
                continue
            claude_files.append(file_path)
        return sorted(claude_files)
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single claude.md file"""
        errors = []
        warnings = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(
                file_path=str(file_path),
                is_valid=False,
                errors=[f"Failed to read file: {e}"],
                warnings=[],
                constitutional_hash_present=False,
                required_sections_present=[],
                missing_sections=self.REQUIRED_SECTIONS,
                cross_references=[],
                broken_links=[]
            )
        
        # Check constitutional hash
        constitutional_hash_present = self.CONSTITUTIONAL_HASH in content
        if not constitutional_hash_present:
            errors.append("Constitutional hash cdd01ef066bc6cf2 not found")
        
        # Check required sections
        present_sections = []
        missing_sections = []
        
        for section in self.REQUIRED_SECTIONS:
            if f"## {section}" in content:
                present_sections.append(section)
            else:
                missing_sections.append(section)
                errors.append(f"Required section missing: {section}")
        
        # Check required patterns
        for pattern_name, pattern in self.REQUIRED_PATTERNS.items():
            if not re.search(pattern, content):
                warnings.append(f"Pattern not found: {pattern_name}")
        
        # Extract cross-references
        cross_references = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        # Check for broken internal links
        broken_links = []
        for link_text, link_url in cross_references:
            if link_url.startswith('../') or link_url.startswith('./'):
                # Check if internal link exists
                link_path = file_path.parent / link_url
                if not link_path.exists():
                    broken_links.append(f"{link_text} -> {link_url}")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            file_path=str(file_path),
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            constitutional_hash_present=constitutional_hash_present,
            required_sections_present=present_sections,
            missing_sections=missing_sections,
            cross_references=[f"{text} -> {url}" for text, url in cross_references],
            broken_links=broken_links
        )
    
    def validate_all(self) -> Dict[str, any]:
        """Validate all claude.md files and return summary"""
        claude_files = self.find_claude_md_files()
        
        print(f"Found {len(claude_files)} claude.md files")
        
        for file_path in claude_files:
            result = self.validate_file(file_path)
            self.results.append(result)
            
            status = "✅ VALID" if result.is_valid else "❌ INVALID"
            print(f"{status}: {file_path.relative_to(self.project_root)}")
            
            if result.errors:
                for error in result.errors:
                    print(f"  ERROR: {error}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"  WARNING: {warning}")
        
        # Generate summary
        valid_count = sum(1 for r in self.results if r.is_valid)
        total_count = len(self.results)
        
        summary = {
            "total_files": total_count,
            "valid_files": valid_count,
            "invalid_files": total_count - valid_count,
            "validation_rate": (valid_count / total_count * 100) if total_count > 0 else 0,
            "constitutional_compliance_rate": sum(1 for r in self.results if r.constitutional_hash_present) / total_count * 100 if total_count > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH
        }
        
        return summary
    
    def generate_report(self, output_file: str = "claude_md_validation_report.json"):
        """Generate detailed validation report"""
        summary = self.validate_all()
        
        report = {
            "summary": summary,
            "results": [
                {
                    "file_path": r.file_path,
                    "is_valid": r.is_valid,
                    "errors": r.errors,
                    "warnings": r.warnings,
                    "constitutional_hash_present": r.constitutional_hash_present,
                    "required_sections_present": r.required_sections_present,
                    "missing_sections": r.missing_sections,
                    "cross_references_count": len(r.cross_references),
                    "broken_links_count": len(r.broken_links),
                    "broken_links": r.broken_links
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nValidation report saved to: {output_file}")
        print(f"Summary: {summary['valid_files']}/{summary['total_files']} files valid ({summary['validation_rate']:.1f}%)")
        print(f"Constitutional compliance: {summary['constitutional_compliance_rate']:.1f}%")
        
        return report

def main():
    """Main validation function"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = ClaudeMdValidator(project_root)
    validator.generate_report()

if __name__ == "__main__":
    main()
