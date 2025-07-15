#!/usr/bin/env python3
"""
ACGS-2 Claude.md Cross-Reference Validation
Constitutional Hash: cdd01ef066bc6cf2

This script validates cross-references and navigation links across all claude.md files
in the ACGS-2 project for:
- Link integrity and accuracy
- Navigation consistency
- Cross-reference completeness
- Constitutional compliance in navigation
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CrossReferenceResult:
    """Cross-reference validation result"""
    file_path: str
    total_links: int
    valid_links: int
    broken_links: List[str]
    missing_references: List[str]
    navigation_consistency: bool
    constitutional_compliance: bool

class CrossReferenceValidator:
    """Validator for cross-references in claude.md files"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.claude_files = self.find_claude_md_files()
        self.results: List[CrossReferenceResult] = []
    
    def find_claude_md_files(self) -> Dict[str, Path]:
        """Find all CLAUDE.md files and create a mapping"""
        claude_files = {}
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip virtual environments and build directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules']):
                continue

            # Create relative path key
            rel_path = file_path.relative_to(self.project_root)
            claude_files[str(rel_path)] = file_path

        return claude_files
    
    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract all markdown links from content"""
        # Pattern to match markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        return re.findall(link_pattern, content)
    
    def validate_link(self, link_url: str, source_file: Path) -> bool:
        """Validate if a link exists"""
        if link_url.startswith('http'):
            # External link - assume valid for now
            return True
        
        if link_url.startswith('#'):
            # Anchor link - would need content parsing to validate
            return True
        
        # Internal link - resolve relative to source file
        if link_url.startswith('../') or link_url.startswith('./'):
            target_path = source_file.parent / link_url
            return target_path.exists()
        
        # Absolute path from project root
        target_path = self.project_root / link_url
        return target_path.exists()
    
    def check_expected_references(self, file_path: Path, content: str) -> List[str]:
        """Check for expected cross-references based on directory structure"""
        missing_refs = []
        rel_path = file_path.relative_to(self.project_root)
        
        # Expected references based on directory level
        if rel_path.name == "claude.md":
            if rel_path.parent != Path("."):
                # Should reference parent directory
                parent_claude = rel_path.parent.parent / "claude.md"
                if parent_claude in self.claude_files and f"../{parent_claude.name}" not in content:
                    missing_refs.append(f"Missing parent reference: {parent_claude}")
        
        return missing_refs
    
    def check_navigation_consistency(self, content: str) -> bool:
        """Check if navigation footer is consistent"""
        navigation_pattern = r'\*\*Navigation\*\*:'
        constitutional_pattern = r'\*\*Constitutional Compliance\*\*:'
        
        has_navigation = bool(re.search(navigation_pattern, content))
        has_constitutional = bool(re.search(constitutional_pattern, content))
        
        return has_navigation and has_constitutional
    
    def check_constitutional_compliance_in_navigation(self, content: str) -> bool:
        """Check if constitutional compliance is mentioned in navigation"""
        return self.CONSTITUTIONAL_HASH in content
    
    def validate_file(self, file_path: Path) -> CrossReferenceResult:
        """Validate cross-references in a single claude.md file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return CrossReferenceResult(
                file_path=str(file_path),
                total_links=0,
                valid_links=0,
                broken_links=[f"Failed to read file: {e}"],
                missing_references=[],
                navigation_consistency=False,
                constitutional_compliance=False
            )
        
        # Extract all links
        links = self.extract_links(content)
        total_links = len(links)
        
        # Validate each link
        broken_links = []
        valid_links = 0
        
        for link_text, link_url in links:
            if self.validate_link(link_url, file_path):
                valid_links += 1
            else:
                broken_links.append(f"{link_text} -> {link_url}")
        
        # Check for missing expected references
        missing_references = self.check_expected_references(file_path, content)
        
        # Check navigation consistency
        navigation_consistency = self.check_navigation_consistency(content)
        
        # Check constitutional compliance in navigation
        constitutional_compliance = self.check_constitutional_compliance_in_navigation(content)
        
        return CrossReferenceResult(
            file_path=str(file_path.relative_to(self.project_root)),
            total_links=total_links,
            valid_links=valid_links,
            broken_links=broken_links,
            missing_references=missing_references,
            navigation_consistency=navigation_consistency,
            constitutional_compliance=constitutional_compliance
        )
    
    def validate_all(self) -> Dict[str, any]:
        """Validate all claude.md files and return summary"""
        print(f"Found {len(self.claude_files)} claude.md files")
        print("Validating cross-references and navigation...")
        
        for file_path in self.claude_files.values():
            result = self.validate_file(file_path)
            self.results.append(result)
            
            # Print summary for each file
            status = "✅ VALID" if len(result.broken_links) == 0 else "❌ BROKEN LINKS"
            nav_status = "✅ CONSISTENT" if result.navigation_consistency else "❌ INCONSISTENT"
            const_status = "✅ COMPLIANT" if result.constitutional_compliance else "❌ NON-COMPLIANT"
            
            print(f"{status} | {nav_status} | {const_status}: {result.file_path}")
            
            if result.broken_links:
                for broken_link in result.broken_links:
                    print(f"  BROKEN: {broken_link}")
            
            if result.missing_references:
                for missing_ref in result.missing_references:
                    print(f"  MISSING: {missing_ref}")
        
        # Generate summary
        total_files = len(self.results)
        files_with_broken_links = sum(1 for r in self.results if r.broken_links)
        files_with_consistent_nav = sum(1 for r in self.results if r.navigation_consistency)
        files_with_constitutional_compliance = sum(1 for r in self.results if r.constitutional_compliance)
        total_links = sum(r.total_links for r in self.results)
        total_valid_links = sum(r.valid_links for r in self.results)
        
        summary = {
            "total_files": total_files,
            "files_with_broken_links": files_with_broken_links,
            "files_with_valid_links": total_files - files_with_broken_links,
            "link_validity_rate": (total_valid_links / total_links * 100) if total_links > 0 else 100,
            "navigation_consistency_rate": (files_with_consistent_nav / total_files * 100) if total_files > 0 else 0,
            "constitutional_compliance_rate": (files_with_constitutional_compliance / total_files * 100) if total_files > 0 else 0,
            "total_links": total_links,
            "valid_links": total_valid_links,
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH
        }
        
        return summary
    
    def generate_report(self, output_file: str = "claude_md_cross_reference_report.json"):
        """Generate detailed cross-reference validation report"""
        summary = self.validate_all()
        
        report = {
            "summary": summary,
            "results": [
                {
                    "file_path": r.file_path,
                    "total_links": r.total_links,
                    "valid_links": r.valid_links,
                    "broken_links": r.broken_links,
                    "missing_references": r.missing_references,
                    "navigation_consistency": r.navigation_consistency,
                    "constitutional_compliance": r.constitutional_compliance,
                    "link_validity_rate": (r.valid_links / r.total_links * 100) if r.total_links > 0 else 100
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nCross-reference validation report saved to: {output_file}")
        print(f"Summary:")
        print(f"  Files: {summary['total_files']}")
        print(f"  Link validity: {summary['link_validity_rate']:.1f}% ({summary['valid_links']}/{summary['total_links']})")
        print(f"  Navigation consistency: {summary['navigation_consistency_rate']:.1f}%")
        print(f"  Constitutional compliance: {summary['constitutional_compliance_rate']:.1f}%")
        print(f"  Files with broken links: {summary['files_with_broken_links']}")
        
        return report

def main():
    """Main validation function"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = CrossReferenceValidator(project_root)
    validator.generate_report()

if __name__ == "__main__":
    main()
