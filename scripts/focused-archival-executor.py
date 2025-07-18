#!/usr/bin/env python3
"""
ACGS-2 Focused Archival Executor
Constitutional Hash: cdd01ef066bc6cf2

Executes focused archival of outdated files while maintaining constitutional compliance.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class FocusedArchivalExecutor:
    """Executes focused archival for ACGS-2."""
    
    def __init__(self, root_path: str = ".", analysis_file: str = "focused-archival-analysis.json"):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.analysis_file = analysis_file
        
        # Archive directory structure
        self.archive_root = self.root_path / "archive"
        self.current_year = datetime.now().year
        
        # Load analysis results
        self.analysis_data = self._load_analysis_data()
        
        # Execution results
        self.execution_results = {
            'constitutional_hash': self.constitutional_hash,
            'execution_timestamp': datetime.now().isoformat(),
            'archived_files': [],
            'skipped_files': [],
            'failed_archives': [],
            'validation_results': {},
            'archive_summary': {}
        }
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """Load archival analysis data."""
        try:
            with open(self.analysis_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Analysis file {self.analysis_file} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {self.analysis_file}")
            return {}
    
    def create_archive_structure(self) -> None:
        """Create organized archive directory structure."""
        print("📁 Creating archive directory structure...")
        
        archive_dirs = [
            f"archive/node_modules/{self.current_year}",
            f"archive/temporary_files/{self.current_year}",
            f"archive/deprecated_code/{self.current_year}",
            f"archive/old_configs/{self.current_year}",
            f"archive/miscellaneous/{self.current_year}"
        ]
        
        for archive_dir in archive_dirs:
            dir_path = self.root_path / archive_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create constitutional compliance marker
            marker_file = dir_path / ".constitutional-compliance"
            marker_file.write_text(f"Constitutional Hash: {self.constitutional_hash}\n"
                                 f"Archive Created: {datetime.now().isoformat()}\n"
                                 f"Archive Type: {archive_dir.split('/')[-2]}\n")
        
        print(f"✅ Created {len(archive_dirs)} archive directories")
    
    def categorize_for_archival(self, candidates: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize candidates for efficient archival."""
        categorized = {
            'node_modules': [],
            'temporary_files': [],
            'deprecated_code': [],
            'old_configs': [],
            'skip': []
        }
        
        for candidate in candidates:
            file_path = candidate['file_path']
            
            # Skip files with constitutional hash (safety check)
            if candidate.get('has_constitutional_hash', False):
                categorized['skip'].append(candidate)
                continue
            
            # Categorize based on path patterns
            if 'node_modules' in file_path:
                categorized['node_modules'].append(candidate)
            elif any(ext in file_path for ext in ['.tmp', '.temp', '.bak', '.backup', '~']):
                categorized['temporary_files'].append(candidate)
            elif any(word in file_path.lower() for word in ['deprecated', 'obsolete', 'old']):
                categorized['deprecated_code'].append(candidate)
            elif 'env.' in file_path or 'config.' in file_path:
                categorized['old_configs'].append(candidate)
            else:
                categorized['temporary_files'].append(candidate)  # Default to temporary
        
        return categorized
    
    def archive_node_modules(self, candidates: List[Dict[str, Any]]) -> None:
        """Archive entire node_modules directories efficiently."""
        print("📦 Archiving node_modules directories...")
        
        # Group by node_modules directory
        node_modules_dirs = set()
        for candidate in candidates:
            file_path = candidate['file_path']
            if 'node_modules' in file_path:
                # Find the node_modules directory
                parts = Path(file_path).parts
                for i, part in enumerate(parts):
                    if part == 'node_modules':
                        node_modules_path = '/'.join(parts[:i+1])
                        node_modules_dirs.add(node_modules_path)
                        break
        
        # Archive each node_modules directory
        for node_modules_dir in node_modules_dirs:
            source_path = self.root_path / node_modules_dir
            if source_path.exists() and source_path.is_dir():
                
                # Create archive path
                relative_parts = Path(node_modules_dir).parts[:-1]  # Exclude 'node_modules'
                if relative_parts:
                    archive_subdir = '_'.join(relative_parts)
                else:
                    archive_subdir = 'root'
                
                archive_path = self.archive_root / f"node_modules/{self.current_year}/{archive_subdir}_node_modules"
                
                try:
                    # Move the entire directory
                    shutil.move(str(source_path), str(archive_path))
                    
                    # Create metadata
                    metadata = {
                        'constitutional_hash': self.constitutional_hash,
                        'original_path': node_modules_dir,
                        'archive_timestamp': datetime.now().isoformat(),
                        'archival_reason': 'Node.js dependencies - not part of core ACGS codebase',
                        'directory_size_estimate': 'Large (node_modules)'
                    }
                    
                    metadata_path = archive_path.with_suffix('.meta')
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    self.execution_results['archived_files'].append({
                        'type': 'directory',
                        'original_path': node_modules_dir,
                        'archive_path': str(archive_path.relative_to(self.root_path)),
                        'archival_reason': metadata['archival_reason']
                    })
                    
                    print(f"✅ Archived: {node_modules_dir}")
                    
                except Exception as e:
                    self.execution_results['failed_archives'].append({
                        'path': node_modules_dir,
                        'error': str(e)
                    })
                    print(f"❌ Failed to archive: {node_modules_dir} - {str(e)}")
    
    def archive_individual_files(self, candidates: List[Dict[str, Any]], category: str) -> None:
        """Archive individual files by category."""
        print(f"📦 Archiving {category} files...")
        
        archive_dir = self.archive_root / category / str(self.current_year)
        
        for candidate in candidates:
            try:
                source_path = Path(candidate['absolute_path'])
                if not source_path.exists():
                    continue
                
                # Create unique archive filename
                archive_filename = source_path.name
                counter = 1
                archive_path = archive_dir / archive_filename
                
                while archive_path.exists():
                    stem = source_path.stem
                    suffix = source_path.suffix
                    archive_path = archive_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Copy file to archive
                shutil.copy2(source_path, archive_path)
                
                # Create metadata
                metadata = {
                    'constitutional_hash': self.constitutional_hash,
                    'original_path': candidate['file_path'],
                    'archive_timestamp': datetime.now().isoformat(),
                    'archival_reason': candidate['archival_reason'],
                    'original_size_bytes': candidate['size_bytes'],
                    'pattern_matched': candidate.get('pattern_matched', 'unknown')
                }
                
                metadata_path = archive_path.with_suffix(archive_path.suffix + '.meta')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Remove original file
                source_path.unlink()
                
                self.execution_results['archived_files'].append({
                    'type': 'file',
                    'original_path': candidate['file_path'],
                    'archive_path': str(archive_path.relative_to(self.root_path)),
                    'archival_reason': candidate['archival_reason']
                })
                
            except Exception as e:
                self.execution_results['failed_archives'].append({
                    'path': candidate['file_path'],
                    'error': str(e)
                })
    
    def validate_post_archival(self) -> Dict[str, Any]:
        """Validate system after archival."""
        print("🔍 Validating system after archival...")
        
        validation_results = {
            'constitutional_compliance_intact': True,
            'critical_files_intact': True,
            'unified_configs_intact': True,
            'validation_errors': []
        }
        
        # Check critical files still exist
        critical_files = [
            'config/docker/docker-compose.base.yml',
            'config/docker/docker-compose.development.yml',
            'config/docker/docker-compose.staging.yml',
            'config/docker/docker-compose.production.yml',
            'config/services/service-architecture-mapping.yml',
            'config/monitoring/unified-observability-stack.yml',
            'scripts/deploy-acgs.sh',
            'scripts/constitutional-compliance-validator.py'
        ]
        
        for critical_file in critical_files:
            file_path = self.root_path / critical_file
            if not file_path.exists():
                validation_results['critical_files_intact'] = False
                validation_results['validation_errors'].append(f"Critical file missing: {critical_file}")
        
        # Check constitutional hash in key files
        key_files = [
            'config/docker/docker-compose.base.yml',
            'config/services/service-architecture-mapping.yml'
        ]
        
        for key_file in key_files:
            file_path = self.root_path / key_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if self.constitutional_hash not in content:
                        validation_results['constitutional_compliance_intact'] = False
                        validation_results['validation_errors'].append(f"Constitutional hash missing from: {key_file}")
                except Exception as e:
                    validation_results['validation_errors'].append(f"Error reading {key_file}: {str(e)}")
        
        overall_success = (
            validation_results['constitutional_compliance_intact'] and
            validation_results['critical_files_intact'] and
            validation_results['unified_configs_intact']
        )
        
        print(f"🔍 Validation: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        return validation_results
    
    def execute_focused_archival(self) -> Dict[str, Any]:
        """Execute the focused archival process."""
        print("🚀 Executing ACGS-2 Focused Codebase Archival")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        
        if not self.analysis_data:
            print("❌ No analysis data available.")
            return self.execution_results
        
        # Create archive structure
        self.create_archive_structure()
        
        # Get all candidates
        all_candidates = []
        candidates_by_category = self.analysis_data.get('candidates_by_category', {})
        for category, candidates in candidates_by_category.items():
            all_candidates.extend(candidates)
        
        print(f"📊 Processing {len(all_candidates)} archival candidates")
        
        # Categorize for efficient archival
        categorized = self.categorize_for_archival(all_candidates)
        
        # Report categorization
        for category, candidates in categorized.items():
            if candidates:
                print(f"  {category}: {len(candidates)} files")
        
        # Archive node_modules directories (most efficient)
        if categorized['node_modules']:
            self.archive_node_modules(categorized['node_modules'])
        
        # Archive other categories
        for category in ['temporary_files', 'deprecated_code', 'old_configs']:
            if categorized[category]:
                self.archive_individual_files(categorized[category], category)
        
        # Record skipped files
        self.execution_results['skipped_files'] = categorized['skip']
        
        # Validate post-archival state
        validation_results = self.validate_post_archival()
        self.execution_results['validation_results'] = validation_results
        
        # Generate summary
        self.execution_results['archive_summary'] = {
            'total_processed': len(all_candidates),
            'total_archived': len(self.execution_results['archived_files']),
            'total_skipped': len(self.execution_results['skipped_files']),
            'total_failed': len(self.execution_results['failed_archives']),
            'node_modules_archived': len(categorized['node_modules']),
            'individual_files_archived': len(self.execution_results['archived_files']) - len(categorized['node_modules'])
        }
        
        # Save results
        output_file = "focused-archival-execution.json"
        with open(output_file, 'w') as f:
            json.dump(self.execution_results, f, indent=2)
        
        # Print final summary
        summary = self.execution_results['archive_summary']
        print(f"\n✅ ACGS-2 Focused Archival Complete!")
        print(f"📦 Total Archived: {summary['total_archived']}")
        print(f"⏭️ Skipped (Constitutional Hash): {summary['total_skipped']}")
        print(f"❌ Failed: {summary['total_failed']}")
        print(f"🏛️ Constitutional Compliance: {'✅ MAINTAINED' if validation_results['constitutional_compliance_intact'] else '❌ COMPROMISED'}")
        print(f"📋 Execution report saved to: {output_file}")
        
        return self.execution_results

def main():
    """Main execution function."""
    executor = FocusedArchivalExecutor()
    results = executor.execute_focused_archival()
    
    return 0 if results.get('validation_results', {}).get('constitutional_compliance_intact', False) else 1

if __name__ == "__main__":
    main()
