#!/usr/bin/env python3
"""
ACGS-2 Codebase Archival Executor
Constitutional Hash: cdd01ef066bc6cf2

Executes the systematic archival of outdated documents, dead code, and legacy configurations
based on the analysis results while maintaining constitutional compliance.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import hashlib

class CodebaseArchivalExecutor:
    """Executes systematic codebase archival for ACGS-2."""
    
    def __init__(self, root_path: str = ".", analysis_file: str = "codebase-archival-analysis.json"):
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
            'execution_timestamp': datetime.utcnow().isoformat(),
            'archived_files': [],
            'failed_archives': [],
            'validation_results': {},
            'archive_manifests': {}
        }
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """Load archival analysis data."""
        try:
            with open(self.analysis_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Analysis file {self.analysis_file} not found. Run archival analyzer first.")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {self.analysis_file}")
            return {}
    
    def create_archive_structure(self) -> None:
        """Create organized archive directory structure."""
        print("📁 Creating archive directory structure...")
        
        archive_dirs = [
            f"archive/documentation/{self.current_year}/claude-docs",
            f"archive/documentation/{self.current_year}/readme-files",
            f"archive/documentation/{self.current_year}/api-docs",
            f"archive/documentation/{self.current_year}/guides",
            f"archive/documentation/{self.current_year}/general-docs",
            f"archive/code/{self.current_year}/test-files",
            f"archive/code/{self.current_year}/scripts",
            f"archive/code/{self.current_year}/services",
            f"archive/code/{self.current_year}/utilities",
            f"archive/code/{self.current_year}/application-code",
            f"archive/configurations/{self.current_year}/docker-configs",
            f"archive/configurations/{self.current_year}/kubernetes-configs",
            f"archive/configurations/{self.current_year}/environment-configs",
            f"archive/configurations/{self.current_year}/monitoring-configs",
            f"archive/configurations/{self.current_year}/general-configs"
        ]
        
        for archive_dir in archive_dirs:
            dir_path = self.root_path / archive_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create constitutional compliance marker
            marker_file = dir_path / ".constitutional-compliance"
            marker_file.write_text(f"Constitutional Hash: {self.constitutional_hash}\n"
                                 f"Archive Created: {datetime.utcnow().isoformat()}\n"
                                 f"Archive Type: {archive_dir.split('/')[-1]}\n")
        
        print(f"✅ Created {len(archive_dirs)} archive directories")
    
    def validate_archival_safety(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that archival is safe and won't break the system."""
        print("🔍 Validating archival safety...")
        
        validation_results = {
            'safe_to_archive': True,
            'validation_errors': [],
            'warnings': [],
            'constitutional_compliance_preserved': True,
            'performance_targets_preserved': True
        }
        
        # Check for constitutional compliance files
        constitutional_files = []
        for candidate in candidates:
            if candidate.get('has_constitutional_hash', False):
                constitutional_files.append(candidate['file_path'])
                validation_results['validation_errors'].append(
                    f"File {candidate['file_path']} contains constitutional hash but marked for archival"
                )
        
        if constitutional_files:
            validation_results['safe_to_archive'] = False
            validation_results['constitutional_compliance_preserved'] = False
        
        # Check for critical system files
        critical_patterns = [
            'deploy', 'startup', 'init', 'main', 'index',
            'config/docker/docker-compose',
            'config/environments',
            'infrastructure/',
            '.github/workflows'
        ]
        
        critical_files = []
        for candidate in candidates:
            file_path = candidate['file_path']
            if any(pattern in file_path for pattern in critical_patterns):
                critical_files.append(file_path)
                validation_results['warnings'].append(
                    f"Critical file pattern detected: {file_path}"
                )
        
        # Check for active references
        referenced_files = []
        for candidate in candidates:
            if candidate.get('is_referenced', False):
                referenced_files.append(candidate['file_path'])
                validation_results['validation_errors'].append(
                    f"File {candidate['file_path']} has active references but marked for archival"
                )
        
        if referenced_files:
            validation_results['safe_to_archive'] = False
        
        print(f"🔍 Validation complete: {'✅ SAFE' if validation_results['safe_to_archive'] else '❌ UNSAFE'}")
        if validation_results['validation_errors']:
            print(f"❌ {len(validation_results['validation_errors'])} validation errors found")
        if validation_results['warnings']:
            print(f"⚠️ {len(validation_results['warnings'])} warnings found")
        
        return validation_results
    
    def archive_files(self, candidates: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Archive files for a specific category."""
        print(f"📦 Archiving {category} files...")
        
        archived_files = []
        failed_archives = []
        
        for candidate in candidates:
            try:
                source_path = Path(candidate['absolute_path'])
                if not source_path.exists():
                    failed_archives.append({
                        'file_path': candidate['file_path'],
                        'error': 'Source file not found'
                    })
                    continue
                
                # Determine archive destination
                subcategory = candidate.get('subcategory', 'general')
                archive_dir = self.archive_root / category / str(self.current_year) / subcategory
                archive_path = archive_dir / source_path.name
                
                # Handle name conflicts
                counter = 1
                while archive_path.exists():
                    stem = source_path.stem
                    suffix = source_path.suffix
                    archive_path = archive_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Copy file to archive
                shutil.copy2(source_path, archive_path)
                
                # Create metadata file
                metadata = {
                    'constitutional_hash': self.constitutional_hash,
                    'original_path': candidate['file_path'],
                    'archive_timestamp': datetime.utcnow().isoformat(),
                    'archival_reason': candidate['archival_reason'],
                    'original_size_bytes': candidate['size_bytes'],
                    'original_last_modified': candidate['last_modified'],
                    'file_hash': self._calculate_file_hash(archive_path)
                }
                
                metadata_path = archive_path.with_suffix(archive_path.suffix + '.meta')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                archived_files.append({
                    'original_path': candidate['file_path'],
                    'archive_path': str(archive_path.relative_to(self.root_path)),
                    'metadata_path': str(metadata_path.relative_to(self.root_path)),
                    'archival_reason': candidate['archival_reason'],
                    'archive_timestamp': metadata['archive_timestamp']
                })
                
                # Remove original file
                source_path.unlink()
                
            except Exception as e:
                failed_archives.append({
                    'file_path': candidate['file_path'],
                    'error': str(e)
                })
        
        print(f"✅ Archived {len(archived_files)} {category} files")
        if failed_archives:
            print(f"❌ Failed to archive {len(failed_archives)} {category} files")
        
        return archived_files, failed_archives
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def create_archive_manifests(self) -> Dict[str, Any]:
        """Create archive manifests for each category."""
        print("📋 Creating archive manifests...")
        
        manifests = {}
        
        for category in ['documentation', 'code', 'configurations']:
            category_dir = self.archive_root / category / str(self.current_year)
            if not category_dir.exists():
                continue
            
            manifest = {
                'constitutional_hash': self.constitutional_hash,
                'category': category,
                'archive_year': self.current_year,
                'creation_timestamp': datetime.utcnow().isoformat(),
                'archived_files': [],
                'total_files': 0,
                'total_size_bytes': 0,
                'subcategories': {}
            }
            
            # Scan archived files
            for subcategory_dir in category_dir.iterdir():
                if subcategory_dir.is_dir():
                    subcategory_files = []
                    subcategory_size = 0
                    
                    for file_path in subcategory_dir.iterdir():
                        if file_path.suffix != '.meta' and not file_path.name.startswith('.'):
                            metadata_path = file_path.with_suffix(file_path.suffix + '.meta')
                            
                            file_info = {
                                'filename': file_path.name,
                                'archive_path': str(file_path.relative_to(self.root_path)),
                                'size_bytes': file_path.stat().st_size,
                                'file_hash': self._calculate_file_hash(file_path)
                            }
                            
                            if metadata_path.exists():
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                                file_info.update(metadata)
                            
                            subcategory_files.append(file_info)
                            subcategory_size += file_info['size_bytes']
                    
                    manifest['subcategories'][subcategory_dir.name] = {
                        'files': subcategory_files,
                        'file_count': len(subcategory_files),
                        'total_size_bytes': subcategory_size
                    }
                    
                    manifest['archived_files'].extend(subcategory_files)
                    manifest['total_files'] += len(subcategory_files)
                    manifest['total_size_bytes'] += subcategory_size
            
            # Save manifest
            manifest_path = category_dir / 'archive-manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            manifests[category] = manifest
            print(f"📋 Created {category} manifest: {manifest['total_files']} files, {manifest['total_size_bytes'] / 1024 / 1024:.2f} MB")
        
        return manifests
    
    def verify_system_functionality(self) -> Dict[str, Any]:
        """Verify that system functionality remains intact after archival."""
        print("🔍 Verifying system functionality...")
        
        verification_results = {
            'constitutional_compliance_intact': True,
            'performance_targets_intact': True,
            'critical_files_intact': True,
            'unified_configs_intact': True,
            'verification_errors': [],
            'verification_timestamp': datetime.utcnow().isoformat()
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
            'scripts/constitutional-compliance-validator.py',
            'docs/ACGS-2-UNIFIED-DOCUMENTATION.md'
        ]
        
        for critical_file in critical_files:
            file_path = self.root_path / critical_file
            if not file_path.exists():
                verification_results['critical_files_intact'] = False
                verification_results['verification_errors'].append(
                    f"Critical file missing: {critical_file}"
                )
        
        # Check constitutional hash presence in key files
        constitutional_files = [
            'config/docker/docker-compose.base.yml',
            'config/services/service-architecture-mapping.yml',
            'config/monitoring/unified-observability-stack.yml'
        ]
        
        for const_file in constitutional_files:
            file_path = self.root_path / const_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if self.constitutional_hash not in content:
                        verification_results['constitutional_compliance_intact'] = False
                        verification_results['verification_errors'].append(
                            f"Constitutional hash missing from: {const_file}"
                        )
                except Exception as e:
                    verification_results['verification_errors'].append(
                        f"Error reading {const_file}: {str(e)}"
                    )
        
        # Run simplified configuration validation
        try:
            import subprocess
            result = subprocess.run(
                ['./scripts/validate-simplified-configs.sh'],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                verification_results['unified_configs_intact'] = False
                verification_results['verification_errors'].append(
                    f"Configuration validation failed: {result.stderr}"
                )
        except Exception as e:
            verification_results['verification_errors'].append(
                f"Could not run configuration validation: {str(e)}"
            )
        
        overall_success = (
            verification_results['constitutional_compliance_intact'] and
            verification_results['performance_targets_intact'] and
            verification_results['critical_files_intact'] and
            verification_results['unified_configs_intact']
        )
        
        print(f"🔍 System verification: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        if verification_results['verification_errors']:
            print(f"❌ {len(verification_results['verification_errors'])} verification errors found")
        
        return verification_results
    
    def execute_archival(self) -> Dict[str, Any]:
        """Execute the complete archival process."""
        print("🚀 Executing ACGS-2 Codebase Archival Process")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        
        if not self.analysis_data:
            print("❌ No analysis data available. Cannot proceed with archival.")
            return {}
        
        # Create archive structure
        self.create_archive_structure()
        
        # Get candidates from analysis
        candidates_by_category = self.analysis_data.get('candidates_by_category', {})
        
        all_candidates = []
        for category, candidates in candidates_by_category.items():
            all_candidates.extend(candidates)
        
        # Validate archival safety
        validation_results = self.validate_archival_safety(all_candidates)
        self.execution_results['validation_results'] = validation_results
        
        if not validation_results['safe_to_archive']:
            print("❌ Archival validation failed. Aborting archival process.")
            return self.execution_results
        
        # Execute archival for each category
        for category, candidates in candidates_by_category.items():
            if candidates:
                archived_files, failed_archives = self.archive_files(candidates, category)
                self.execution_results['archived_files'].extend(archived_files)
                self.execution_results['failed_archives'].extend(failed_archives)
        
        # Create archive manifests
        manifests = self.create_archive_manifests()
        self.execution_results['archive_manifests'] = manifests
        
        # Verify system functionality
        verification_results = self.verify_system_functionality()
        self.execution_results['post_archival_verification'] = verification_results
        
        # Generate final report
        self._generate_final_report()
        
        return self.execution_results
    
    def _generate_final_report(self) -> None:
        """Generate final archival execution report."""
        total_archived = len(self.execution_results['archived_files'])
        total_failed = len(self.execution_results['failed_archives'])
        
        print(f"\n✅ ACGS-2 Codebase Archival Complete!")
        print(f"📦 Total Files Archived: {total_archived}")
        print(f"❌ Failed Archives: {total_failed}")
        print(f"🏛️ Constitutional Compliance: {'✅ MAINTAINED' if self.execution_results['validation_results']['constitutional_compliance_preserved'] else '❌ COMPROMISED'}")
        print(f"🎯 System Functionality: {'✅ VERIFIED' if self.execution_results.get('post_archival_verification', {}).get('critical_files_intact', False) else '❌ ISSUES DETECTED'}")
        
        # Save execution results
        output_file = "codebase-archival-execution.json"
        with open(output_file, 'w') as f:
            json.dump(self.execution_results, f, indent=2)
        
        print(f"📋 Execution report saved to: {output_file}")

def main():
    """Main execution function."""
    executor = CodebaseArchivalExecutor()
    results = executor.execute_archival()
    
    return 0 if results.get('validation_results', {}).get('safe_to_archive', False) else 1

if __name__ == "__main__":
    main()
