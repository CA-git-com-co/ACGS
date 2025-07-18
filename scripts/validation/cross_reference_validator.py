#!/usr/bin/env python3
"""
Cross-Reference Validator for ACGS-2 Documentation
Constitutional Hash: cdd01ef066bc6cf2

This script validates internal links and cross-references in documentation files.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse


class CrossReferenceValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Track all files in the project
        self.all_files = set()
        self.documentation_files = []
        self.broken_links = []
        self.valid_links = []
        
        # Patterns for different types of links
        self.link_patterns = [
            # Markdown links: [text](path)
            r'\[([^\]]*)\]\(([^)]+)\)',
            # Direct file references: ./path/file.ext
            r'(?:^|\s)(\.\/[^\s\)]+)',
            # Relative paths: path/file.ext
            r'(?:^|\s)([a-zA-Z][a-zA-Z0-9_\-\/]*\.[a-zA-Z]{2,4})(?:\s|$)',
        ]
        
        # File extensions to consider as documentation
        self.doc_extensions = {'.md', '.rst', '.txt'}
        
        # Directories to exclude from validation
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'build', 'dist', '.egg-info',
            'docs_consolidated_archive_20250710_120000'
        }

    def scan_project_files(self) -> None:
        """Scan the project to build a comprehensive file index"""
        print(f"🔍 Scanning project files in {self.project_root}")
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                # Skip excluded directories
                if any(exclude_dir in str(file_path) for exclude_dir in self.exclude_dirs):
                    continue
                
                # Add to all files set
                relative_path = file_path.relative_to(self.project_root)
                self.all_files.add(str(relative_path))
                
                # Track documentation files separately
                if file_path.suffix.lower() in self.doc_extensions:
                    self.documentation_files.append(file_path)
        
        print(f"📁 Found {len(self.all_files)} total files")
        print(f"📄 Found {len(self.documentation_files)} documentation files")

    def extract_links_from_content(self, content: str) -> List[Tuple[str, str]]:
        """Extract all potential file links from content"""
        links = []
        
        for pattern in self.link_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 2:
                    # Markdown link format [text](path)
                    link_text, link_path = match.groups()
                    links.append((link_text, link_path))
                else:
                    # Direct path reference
                    link_path = match.group(1)
                    links.append(("", link_path))
        
        return links

    def is_external_link(self, link_path: str) -> bool:
        """Check if a link is external (HTTP/HTTPS)"""
        return link_path.startswith(('http://', 'https://', 'mailto:', 'ftp://'))

    def is_anchor_link(self, link_path: str) -> bool:
        """Check if a link is an anchor link within the same document"""
        return link_path.startswith('#')

    def resolve_relative_path(self, base_file: Path, link_path: str) -> Path:
        """Resolve a relative path from a base file location"""
        base_dir = base_file.parent
        
        # Handle different path formats
        if link_path.startswith('./'):
            # Relative to current directory
            resolved = base_dir / link_path[2:]
        elif link_path.startswith('../'):
            # Relative to parent directory
            resolved = base_dir / link_path
        elif link_path.startswith('/'):
            # Absolute path from project root
            resolved = self.project_root / link_path[1:]
        else:
            # Relative to current directory (no ./ prefix)
            resolved = base_dir / link_path
        
        return resolved.resolve()

    def validate_file_link(self, base_file: Path, link_text: str, link_path: str) -> Dict:
        """Validate a single file link"""
        # Skip external links and anchors
        if self.is_external_link(link_path) or self.is_anchor_link(link_path):
            return {
                "type": "external" if self.is_external_link(link_path) else "anchor",
                "valid": True,
                "reason": "External link or anchor"
            }
        
        # Resolve the path
        try:
            resolved_path = self.resolve_relative_path(base_file, link_path)
            relative_resolved = resolved_path.relative_to(self.project_root)
            
            # Check if file exists
            if resolved_path.exists():
                return {
                    "type": "file",
                    "valid": True,
                    "resolved_path": str(relative_resolved),
                    "reason": "File exists"
                }
            else:
                return {
                    "type": "file",
                    "valid": False,
                    "resolved_path": str(relative_resolved),
                    "reason": "File not found"
                }
        except Exception as e:
            return {
                "type": "file",
                "valid": False,
                "resolved_path": link_path,
                "reason": f"Path resolution error: {e}"
            }

    def validate_documentation_file(self, file_path: Path) -> Dict:
        """Validate all links in a documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": f"Could not read file: {e}",
                "links": []
            }
        
        # Extract links
        links = self.extract_links_from_content(content)
        
        # Validate each link
        link_results = []
        for link_text, link_path in links:
            validation_result = self.validate_file_link(file_path, link_text, link_path)
            link_results.append({
                "text": link_text,
                "path": link_path,
                "validation": validation_result
            })
        
        return {
            "file": str(file_path.relative_to(self.project_root)),
            "links": link_results,
            "total_links": len(link_results),
            "broken_links": len([l for l in link_results if not l["validation"]["valid"]])
        }

    def validate_all_documentation(self) -> Dict:
        """Validate all documentation files"""
        print(f"\n🔗 Validating cross-references in {len(self.documentation_files)} files")
        
        results = []
        total_links = 0
        total_broken = 0
        
        for i, file_path in enumerate(self.documentation_files, 1):
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(self.documentation_files)} files processed")
            
            file_result = self.validate_documentation_file(file_path)
            results.append(file_result)
            
            total_links += file_result.get("total_links", 0)
            total_broken += file_result.get("broken_links", 0)
        
        return {
            "summary": {
                "total_files": len(self.documentation_files),
                "total_links": total_links,
                "broken_links": total_broken,
                "valid_links": total_links - total_broken,
                "link_validity_rate": ((total_links - total_broken) / total_links * 100) if total_links > 0 else 100,
                "constitutional_hash": self.constitutional_hash,
                "validation_timestamp": "2025-07-17T20:30:00Z"
            },
            "files": results
        }

    def generate_report(self, validation_results: Dict) -> None:
        """Generate a comprehensive cross-reference validation report"""
        summary = validation_results["summary"]
        
        print(f"\n✅ Cross-reference validation completed!")
        print(f"📊 Summary:")
        print(f"  - Files validated: {summary['total_files']}")
        print(f"  - Total links found: {summary['total_links']}")
        print(f"  - Valid links: {summary['valid_links']}")
        print(f"  - Broken links: {summary['broken_links']}")
        print(f"  - Link validity rate: {summary['link_validity_rate']:.1f}%")
        print(f"  - Constitutional hash: {summary['constitutional_hash']}")
        
        # Show files with broken links
        files_with_broken_links = [
            f for f in validation_results["files"] 
            if f.get("broken_links", 0) > 0
        ]
        
        if files_with_broken_links:
            print(f"\n❌ Files with broken links ({len(files_with_broken_links)}):")
            for file_result in files_with_broken_links[:10]:  # Show top 10
                print(f"  - {file_result['file']}: {file_result['broken_links']} broken links")
        
        # Save detailed report
        report_path = self.project_root / "reports" / "cross_reference_validation_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved: {report_path}")

    def execute_validation(self) -> None:
        """Execute the complete cross-reference validation"""
        print(f"🎯 Starting Cross-Reference Validation")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        # Scan project files
        self.scan_project_files()
        
        # Validate documentation
        validation_results = self.validate_all_documentation()
        
        # Generate report
        self.generate_report(validation_results)


if __name__ == "__main__":
    validator = CrossReferenceValidator("/home/dislove/ACGS-2")
    validator.execute_validation()
