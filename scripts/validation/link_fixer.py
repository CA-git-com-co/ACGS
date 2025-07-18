#!/usr/bin/env python3
"""
Link Fixer for ACGS-2 Documentation
Constitutional Hash: cdd01ef066bc6cf2

This script fixes common broken link patterns in documentation files.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LinkFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Common broken link patterns and their fixes
        self.link_fixes = {
            # Fix common path issues
            r'docs/performance-metrics\.md': 'docs/performance/PERFORMANCE_METRICS.md',
            r'docs/testing\.md': 'docs/testing/TESTING_STRATEGY.md',
            r'docs/security\.md': 'docs/security/SECURITY_FRAMEWORK.md',
            r'docs/constitutional-framework\.md': 'docs/governance/CONSTITUTIONAL_FRAMEWORK.md',
            
            # Fix service references
            r'services/([^/]+)/README\.md': r'services/core/\1/README.md',
            
            # Fix common documentation references
            r'\.github/workflows/([^)]+)': r'.github/workflows/\1',
            r'frontend/README\.md': 'frontend/README.md',
            
            # Fix relative path issues
            r'\.\./\.\./([^)]+)': r'\1',
            r'\./([^)]+)': r'\1',
        }
        
        # Files to exclude from fixing
        self.exclude_files = {
            'claude_md_template.md',  # Template file with placeholders
        }

    def fix_links_in_content(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Fix broken links in content and return updated content and fix count"""
        fixed_content = content
        fix_count = 0
        
        # Apply each fix pattern
        for broken_pattern, fix_replacement in self.link_fixes.items():
            # Find markdown links with the broken pattern
            markdown_link_pattern = rf'\[([^\]]*)\]\(([^)]*{broken_pattern}[^)]*)\)'
            
            def replace_link(match):
                nonlocal fix_count
                link_text = match.group(1)
                old_path = match.group(2)
                
                # Apply the fix
                new_path = re.sub(broken_pattern, fix_replacement, old_path)
                
                # Check if the new path exists
                resolved_path = self.resolve_path(file_path, new_path)
                if resolved_path and resolved_path.exists():
                    fix_count += 1
                    return f'[{link_text}]({new_path})'
                else:
                    # Keep original if fix doesn't resolve to existing file
                    return match.group(0)
            
            fixed_content = re.sub(markdown_link_pattern, replace_link, fixed_content)
        
        return fixed_content, fix_count

    def resolve_path(self, base_file: Path, link_path: str) -> Path:
        """Resolve a relative path from a base file location"""
        try:
            base_dir = base_file.parent
            
            if link_path.startswith('./'):
                resolved = base_dir / link_path[2:]
            elif link_path.startswith('../'):
                resolved = base_dir / link_path
            elif link_path.startswith('/'):
                resolved = self.project_root / link_path[1:]
            else:
                resolved = base_dir / link_path
            
            return resolved.resolve()
        except:
            return None

    def fix_file(self, file_path: Path) -> Dict:
        """Fix links in a single file"""
        if file_path.name in self.exclude_files:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "skipped": True,
                "reason": "Excluded file"
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": f"Could not read file: {e}"
            }
        
        # Fix links in content
        fixed_content, fix_count = self.fix_links_in_content(original_content, file_path)
        
        # Write back if changes were made
        if fix_count > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                return {
                    "file": str(file_path.relative_to(self.project_root)),
                    "fixes_applied": fix_count,
                    "success": True
                }
            except Exception as e:
                return {
                    "file": str(file_path.relative_to(self.project_root)),
                    "error": f"Could not write file: {e}",
                    "fixes_attempted": fix_count
                }
        else:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "fixes_applied": 0,
                "no_changes": True
            }

    def fix_documentation_files(self) -> Dict:
        """Fix links in all documentation files"""
        print(f"🔧 Starting link fixing process")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        
        # Find documentation files
        doc_files = []
        for file_path in self.project_root.rglob('*.md'):
            if file_path.is_file():
                # Skip excluded directories
                if any(exclude_dir in str(file_path) for exclude_dir in [
                    '.git', '__pycache__', '.pytest_cache', 'node_modules',
                    'docs_consolidated_archive_20250710_120000'
                ]):
                    continue
                doc_files.append(file_path)
        
        print(f"📄 Found {len(doc_files)} documentation files to process")
        
        # Process each file
        results = []
        total_fixes = 0
        files_modified = 0
        
        for i, file_path in enumerate(doc_files, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(doc_files)} files processed")
            
            result = self.fix_file(file_path)
            results.append(result)
            
            if result.get("fixes_applied", 0) > 0:
                total_fixes += result["fixes_applied"]
                files_modified += 1
        
        return {
            "summary": {
                "total_files_processed": len(doc_files),
                "files_modified": files_modified,
                "total_fixes_applied": total_fixes,
                "constitutional_hash": self.constitutional_hash
            },
            "results": results
        }

    def generate_report(self, fix_results: Dict) -> None:
        """Generate a report of the link fixing process"""
        summary = fix_results["summary"]
        
        print(f"\n✅ Link fixing completed!")
        print(f"📊 Summary:")
        print(f"  - Files processed: {summary['total_files_processed']}")
        print(f"  - Files modified: {summary['files_modified']}")
        print(f"  - Total fixes applied: {summary['total_fixes_applied']}")
        print(f"  - Constitutional hash: {summary['constitutional_hash']}")
        
        # Show files that were modified
        modified_files = [
            r for r in fix_results["results"] 
            if r.get("fixes_applied", 0) > 0
        ]
        
        if modified_files:
            print(f"\n✅ Files modified ({len(modified_files)}):")
            for result in modified_files[:10]:  # Show top 10
                print(f"  - {result['file']}: {result['fixes_applied']} fixes")
        
        # Save detailed report
        report_path = self.project_root / "reports" / "link_fixing_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(fix_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved: {report_path}")

    def execute_fixing(self) -> None:
        """Execute the complete link fixing process"""
        print(f"🎯 Starting Link Fixing Process")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        # Fix documentation files
        fix_results = self.fix_documentation_files()
        
        # Generate report
        self.generate_report(fix_results)


if __name__ == "__main__":
    fixer = LinkFixer("/home/dislove/ACGS-2")
    fixer.execute_fixing()
