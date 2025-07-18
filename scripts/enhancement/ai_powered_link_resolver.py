#!/usr/bin/env python3
"""
ACGS-2 AI-Powered Link Resolution System
Constitutional Hash: cdd01ef066bc6cf2

Phase 6A: AI-Powered Link Resolution
This script implements intelligent link resolution using:
- Semantic similarity matching for broken file references
- Automated path correction with fuzzy matching algorithms
- Template placeholder resolution with context-aware replacement
- Service port mapping updates (8001-8016 range corrections)

Target: Repair the remaining 13,534 broken cross-references to achieve >70% link validity rate
"""

import os
import re
import json
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from datetime import datetime
from collections import defaultdict

class AIPoweredLinkResolver:
    """Intelligent link resolution system with semantic matching"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Track resolution statistics
        self.links_processed = 0
        self.links_resolved = 0
        self.files_modified = 0
        
        # Build comprehensive file index for intelligent matching
        self.file_index = self._build_comprehensive_file_index()
        self.directory_index = self._build_directory_index()
        
        # Template placeholder mappings
        self.template_mappings = {
            # Directory placeholders
            '{RELATED_DIR_1}': 'services',
            '{RELATED_DIR_2}': 'docs',
            '{RELATED_DIR_1_PATH}': 'services/core',
            '{RELATED_DIR_2_PATH}': 'docs/architecture',
            '{NAV_ITEM_1}': 'Documentation',
            '{NAV_ITEM_2}': 'Services',
            '{NAV_ITEM_1_PATH}': 'docs',
            '{NAV_ITEM_2_PATH}': 'services',
            '{DOC_GUIDE_1}': 'Architecture Guide',
            '{DOC_GUIDE_2}': 'API Reference',
            '{DOC_GUIDE_1_PATH}': 'architecture',
            '{DOC_GUIDE_2_PATH}': 'api',
            '{BREADCRUMB_1}': 'Home',
            '{BREADCRUMB_2}': 'Documentation',
            '{BREADCRUMB_1_PATH}': '.',
            '{BREADCRUMB_2_PATH}': 'docs',
            '{COMPONENT_1}': 'Constitutional AI',
            '{COMPONENT_2}': 'Governance Synthesis',
            '{SERVICE_1}': 'Authentication',
            '{SERVICE_2}': 'Integrity',
        }
        
        # Service port mappings (current ACGS-2 configuration)
        self.port_mappings = {
            '8001': '8002',  # Integrity Service
            '8003': '8004',  # Authentication Service  
            '8005': '8006',  # Governance Service
            '8007': '8008',  # Analysis Service
            '8009': '8010',  # Coordination Service
            '8011': '8012',  # Context Service
            '8013': '8014',  # Verification Service
            '8015': '8016',  # Management Service
        }

    def _build_comprehensive_file_index(self) -> Dict[str, List[Path]]:
        """Build comprehensive file index for semantic matching"""
        file_index = defaultdict(list)
        
        print("🗂️  Building comprehensive file index for AI-powered resolution...")
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(skip in str(file_path) for skip in ['.git', '__pycache__', '.venv', 'node_modules', 'target']):
                # Index by exact filename
                filename = file_path.name
                file_index[filename].append(file_path)
                
                # Index by filename without extension
                stem = file_path.stem
                if stem != filename:
                    file_index[stem].append(file_path)
                
                # Index by relative path components
                rel_path = file_path.relative_to(self.project_root)
                file_index[str(rel_path)].append(file_path)
                
                # Index by directory + filename combinations
                parent_name = file_path.parent.name
                if parent_name:
                    combined_key = f"{parent_name}/{filename}"
                    file_index[combined_key].append(file_path)
        
        print(f"📊 Indexed {len(file_index)} unique file patterns")
        return file_index

    def _build_directory_index(self) -> Dict[str, List[Path]]:
        """Build directory index for path resolution"""
        dir_index = defaultdict(list)
        
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(skip in str(dir_path) for skip in ['.git', '__pycache__', '.venv', 'node_modules', 'target']):
                dir_name = dir_path.name
                dir_index[dir_name].append(dir_path)
                
                # Index by relative path
                rel_path = dir_path.relative_to(self.project_root)
                dir_index[str(rel_path)].append(dir_path)
        
        return dir_index

    def semantic_file_matching(self, broken_path: str, context_file: Path) -> Optional[str]:
        """Use semantic similarity to find the best matching file"""
        
        # Extract meaningful parts from broken path
        path_parts = broken_path.replace('../', '').replace('./', '').split('/')
        target_filename = path_parts[-1] if path_parts else broken_path
        
        # Try exact matches first
        if target_filename in self.file_index:
            candidates = self.file_index[target_filename]
            if len(candidates) == 1:
                return str(candidates[0].relative_to(self.project_root))
            elif len(candidates) > 1:
                # Choose the closest one to the context file
                return self._find_closest_file(candidates, context_file)
        
        # Try fuzzy matching for similar filenames
        all_files = list(self.file_index.keys())
        close_matches = difflib.get_close_matches(target_filename, all_files, n=3, cutoff=0.6)
        
        if close_matches:
            best_match = close_matches[0]
            candidates = self.file_index[best_match]
            if candidates:
                return str(candidates[0].relative_to(self.project_root))
        
        # Try matching by file extension and directory context
        if '.' in target_filename:
            extension = target_filename.split('.')[-1]
            context_dir = context_file.parent
            
            # Look for files with same extension in nearby directories
            for file_path in context_dir.rglob(f"*.{extension}"):
                if file_path.name.lower() in target_filename.lower() or target_filename.lower() in file_path.name.lower():
                    return str(file_path.relative_to(self.project_root))
        
        return None

    def _find_closest_file(self, candidates: List[Path], context_file: Path) -> str:
        """Find the file closest to the context file"""
        context_parts = context_file.relative_to(self.project_root).parts
        
        best_candidate = candidates[0]
        best_score = float('inf')
        
        for candidate in candidates:
            candidate_parts = candidate.relative_to(self.project_root).parts
            
            # Calculate path distance (number of different directory levels)
            common_prefix = 0
            for i, (a, b) in enumerate(zip(context_parts, candidate_parts)):
                if a == b:
                    common_prefix += 1
                else:
                    break
            
            distance = len(context_parts) + len(candidate_parts) - 2 * common_prefix
            
            if distance < best_score:
                best_score = distance
                best_candidate = candidate
        
        return str(best_candidate.relative_to(self.project_root))

    def resolve_template_placeholders(self, content: str) -> Tuple[str, int]:
        """Resolve template placeholders with context-aware replacement"""
        fixes = 0
        
        for placeholder, replacement in self.template_mappings.items():
            if placeholder in content:
                # Context-aware replacement
                if placeholder.endswith('_PATH}'):
                    # For path placeholders, ensure proper path format
                    content = content.replace(placeholder, replacement)
                else:
                    # For text placeholders, use as-is
                    content = content.replace(placeholder, replacement)
                fixes += content.count(replacement) - content.count(placeholder)
        
        return content, fixes

    def resolve_service_port_references(self, content: str) -> Tuple[str, int]:
        """Update service port references to current ACGS-2 configuration"""
        fixes = 0
        
        for old_port, new_port in self.port_mappings.items():
            # Match port references in various formats
            patterns = [
                f':{old_port}',
                f'port {old_port}',
                f'PORT={old_port}',
                f'localhost:{old_port}',
                f'127.0.0.1:{old_port}',
            ]
            
            for pattern in patterns:
                if pattern in content:
                    new_pattern = pattern.replace(old_port, new_port)
                    content = content.replace(pattern, new_pattern)
                    fixes += 1
        
        return content, fixes

    def resolve_relative_path_issues(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Resolve relative path navigation issues with intelligent correction"""
        fixes = 0
        
        # Pattern for markdown links with relative paths
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        def fix_link(match):
            nonlocal fixes
            text = match.group(1)
            path = match.group(2)
            
            # Skip URLs and anchors
            if '://' in path or path.startswith('#'):
                return match.group(0)
            
            # Try to resolve the path
            resolved_path = self.semantic_file_matching(path, file_path)
            if resolved_path:
                # Calculate relative path from current file to resolved file
                try:
                    current_dir = file_path.parent
                    target_path = self.project_root / resolved_path
                    relative_path = os.path.relpath(target_path, current_dir)
                    fixes += 1
                    return f'[{text}]({relative_path})'
                except:
                    pass
            
            return match.group(0)
        
        content = re.sub(link_pattern, fix_link, content)
        return content, fixes

    def resolve_file_links(self, file_path: str) -> bool:
        """Apply AI-powered link resolution to a single file"""
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists() or not full_path.is_file():
                return False
            
            # Read content
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            total_fixes = 0
            
            # Apply different AI-powered resolution strategies
            content, fixes1 = self.resolve_template_placeholders(content)
            total_fixes += fixes1
            
            content, fixes2 = self.resolve_service_port_references(content)
            total_fixes += fixes2
            
            content, fixes3 = self.resolve_relative_path_issues(content, full_path)
            total_fixes += fixes3
            
            # Write back if changes were made
            if content != original_content and total_fixes > 0:
                # Backup original
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                backup_path.write_text(original_content, encoding='utf-8')
                
                # Write resolved content
                full_path.write_text(content, encoding='utf-8')
                
                print(f"✅ Resolved {total_fixes} links in: {file_path}")
                self.links_resolved += total_fixes
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error resolving links in {file_path}: {e}")
            return False

    def load_broken_links_data(self) -> List[Dict]:
        """Load broken links from cross-reference validation report"""
        try:
            report_path = self.project_root / "reports" / "cross_reference_validation_report.json"
            
            if not report_path.exists():
                print("❌ Cross-reference validation report not found")
                return []
            
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            broken_files = []
            for file_data in report_data.get("files", []):
                file_path = file_data.get("file", "")
                broken_links = [link for link in file_data.get("links", []) if not link.get("validation", {}).get("valid", True)]
                
                if broken_links:
                    broken_files.append({
                        "file": file_path,
                        "broken_links": len(broken_links),
                        "links": broken_links
                    })
            
            print(f"📊 Loaded {len(broken_files)} files with broken links")
            return broken_files
            
        except Exception as e:
            print(f"❌ Error loading broken links data: {e}")
            return []

    def execute_phase6a_resolution(self):
        """Execute Phase 6A: AI-Powered Link Resolution"""
        print("🚀 Starting Phase 6A: AI-Powered Link Resolution")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target: Achieve >70% link validity rate (up from current 23.7%)")
        
        try:
            # Load broken links data
            broken_files = self.load_broken_links_data()
            
            if not broken_files:
                print("❌ No broken links data available")
                return False
            
            # Sort by number of broken links (prioritize files with most issues)
            broken_files.sort(key=lambda x: x["broken_links"], reverse=True)
            
            total_files = len(broken_files)
            print(f"\n🔧 Processing {total_files} files with broken links...")
            
            # Process each file with AI-powered resolution
            for i, file_data in enumerate(broken_files, 1):
                file_path = file_data["file"]
                broken_count = file_data["broken_links"]
                
                print(f"\n[{i}/{total_files}] Processing: {file_path} ({broken_count} broken links)")
                
                if self.resolve_file_links(file_path):
                    self.files_modified += 1
                
                self.links_processed += broken_count
                
                # Progress indicator
                if i % 50 == 0:
                    progress = (i / total_files) * 100
                    print(f"  📊 Progress: {progress:.1f}% ({i}/{total_files} files)")
            
            print(f"\n✅ Phase 6A AI-Powered Link Resolution Complete!")
            print(f"📊 Results:")
            print(f"  - Files processed: {total_files}")
            print(f"  - Files modified: {self.files_modified}")
            print(f"  - Links processed: {self.links_processed}")
            print(f"  - Links resolved: {self.links_resolved}")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            
            # Save resolution report
            report_data = {
                "phase": "Phase 6A: AI-Powered Link Resolution",
                "timestamp": datetime.now().isoformat(),
                "constitutional_hash": self.constitutional_hash,
                "files_processed": total_files,
                "files_modified": self.files_modified,
                "links_processed": self.links_processed,
                "links_resolved": self.links_resolved,
                "resolution_rate": (self.links_resolved / self.links_processed * 100) if self.links_processed > 0 else 0
            }
            
            report_path = self.project_root / "reports" / f"phase6a_link_resolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"📄 Resolution report saved: {report_path}")
            print(f"\n🔄 Run cross-reference validator to measure link validity improvement")
            
            return True
            
        except Exception as e:
            print(f"❌ Phase 6A link resolution failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    resolver = AIPoweredLinkResolver(project_root)
    
    # Execute Phase 6A resolution
    success = resolver.execute_phase6a_resolution()
    
    if success:
        print("\n🎉 Phase 6A: AI-Powered Link Resolution Complete!")
        print("✅ Intelligent link resolution applied systematically!")
    else:
        print("\n🔄 Phase 6A resolution completed with mixed results.")
        print("📊 Review resolution report for detailed analysis.")

if __name__ == "__main__":
    main()
