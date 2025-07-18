#!/usr/bin/env python3
"""
ACGS-2 Archival Verification Script
Constitutional Hash: cdd01ef066bc6cf2

Verifies the success of the archival process and system integrity.
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ArchivalVerification:
    """Verifies ACGS-2 archival process success."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Load execution results
        self.execution_file = "focused-archival-execution.json"
        self.execution_data = self._load_execution_data()
        
        self.verification_results = {
            'constitutional_hash': self.constitutional_hash,
            'verification_timestamp': datetime.now().isoformat(),
            'archive_integrity': {},
            'system_integrity': {},
            'constitutional_compliance': {},
            'overall_success': False
        }
    
    def _load_execution_data(self) -> dict:
        """Load archival execution data."""
        try:
            with open(self.execution_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Execution file {self.execution_file} not found")
            return {}
    
    def verify_archive_structure(self) -> dict:
        """Verify archive directory structure."""
        print("🔍 Verifying archive structure...")
        
        results = {
            'structure_exists': True,
            'constitutional_markers': True,
            'metadata_files': True,
            'archived_files_count': 0,
            'missing_directories': [],
            'missing_markers': [],
            'verification_errors': []
        }
        
        # Expected archive directories
        expected_dirs = [
            'archive/node_modules/2025',
            'archive/temporary_files/2025',
            'archive/deprecated_code/2025',
            'archive/old_configs/2025',
            'archive/miscellaneous/2025'
        ]
        
        # Check directory structure
        for dir_path in expected_dirs:
            full_path = self.root_path / dir_path
            if not full_path.exists():
                results['structure_exists'] = False
                results['missing_directories'].append(dir_path)
            else:
                # Check constitutional compliance marker
                marker_file = full_path / '.constitutional-compliance'
                if not marker_file.exists():
                    results['constitutional_markers'] = False
                    results['missing_markers'].append(dir_path)
                else:
                    # Verify marker content
                    try:
                        content = marker_file.read_text()
                        if self.constitutional_hash not in content:
                            results['constitutional_markers'] = False
                            results['verification_errors'].append(
                                f"Constitutional hash missing from marker: {dir_path}"
                            )
                    except Exception as e:
                        results['verification_errors'].append(
                            f"Error reading marker {dir_path}: {str(e)}"
                        )
        
        # Count archived files
        archive_root = self.root_path / 'archive'
        if archive_root.exists():
            for file_path in archive_root.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    results['archived_files_count'] += 1
        
        print(f"📁 Archive directories: {len(expected_dirs) - len(results['missing_directories'])}/{len(expected_dirs)}")
        print(f"🏛️ Constitutional markers: {len(expected_dirs) - len(results['missing_markers'])}/{len(expected_dirs)}")
        print(f"📦 Archived files found: {results['archived_files_count']}")
        
        return results
    
    def verify_system_integrity(self) -> dict:
        """Verify system integrity after archival."""
        print("🔍 Verifying system integrity...")
        
        results = {
            'critical_files_exist': True,
            'constitutional_compliance': True,
            'unified_configs_intact': True,
            'missing_critical_files': [],
            'constitutional_violations': [],
            'verification_errors': []
        }
        
        # Critical files that must exist
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
        
        # Check critical files
        for critical_file in critical_files:
            file_path = self.root_path / critical_file
            if not file_path.exists():
                results['critical_files_exist'] = False
                results['missing_critical_files'].append(critical_file)
        
        # Check constitutional compliance in key files
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
                        results['constitutional_compliance'] = False
                        results['constitutional_violations'].append(const_file)
                except Exception as e:
                    results['verification_errors'].append(
                        f"Error reading {const_file}: {str(e)}"
                    )
        
        print(f"📋 Critical files: {len(critical_files) - len(results['missing_critical_files'])}/{len(critical_files)}")
        print(f"🏛️ Constitutional compliance: {len(constitutional_files) - len(results['constitutional_violations'])}/{len(constitutional_files)}")
        
        return results
    
    def verify_archival_execution(self) -> dict:
        """Verify archival execution results."""
        print("🔍 Verifying archival execution...")
        
        results = {
            'execution_data_valid': bool(self.execution_data),
            'archival_success': False,
            'files_processed': 0,
            'files_archived': 0,
            'files_failed': 0,
            'constitutional_compliance_maintained': False,
            'verification_errors': []
        }
        
        if self.execution_data:
            try:
                # Check execution summary
                summary = self.execution_data.get('archive_summary', {})
                results['files_processed'] = summary.get('total_processed', 0)
                results['files_archived'] = summary.get('total_archived', 0)
                results['files_failed'] = summary.get('total_failed', 0)
                
                # Check success criteria
                results['archival_success'] = (
                    results['files_archived'] > 0 and
                    results['files_failed'] == 0
                )
                
                # Check constitutional compliance
                validation = self.execution_data.get('validation_results', {})
                results['constitutional_compliance_maintained'] = validation.get(
                    'constitutional_compliance_intact', False
                )
                
            except Exception as e:
                results['verification_errors'].append(f"Error parsing execution data: {str(e)}")
        
        print(f"📊 Files processed: {results['files_processed']}")
        print(f"📦 Files archived: {results['files_archived']}")
        print(f"❌ Files failed: {results['files_failed']}")
        print(f"🏛️ Constitutional compliance: {'✅' if results['constitutional_compliance_maintained'] else '❌'}")
        
        return results
    
    def verify_no_active_node_modules(self) -> dict:
        """Verify that active node_modules directories were properly archived."""
        print("🔍 Verifying node_modules archival...")
        
        results = {
            'active_node_modules_removed': True,
            'remaining_node_modules': [],
            'verification_errors': []
        }
        
        # Search for remaining node_modules directories (excluding archives)
        for node_modules_dir in self.root_path.rglob('node_modules'):
            if node_modules_dir.is_dir():
                # Skip if in archive directory
                if 'archive' in str(node_modules_dir):
                    continue
                
                # This is an active node_modules directory
                results['active_node_modules_removed'] = False
                results['remaining_node_modules'].append(str(node_modules_dir.relative_to(self.root_path)))
        
        print(f"📦 Active node_modules removed: {'✅' if results['active_node_modules_removed'] else '❌'}")
        if results['remaining_node_modules']:
            print(f"⚠️ Remaining node_modules: {len(results['remaining_node_modules'])}")
        
        return results
    
    def generate_verification_report(self) -> dict:
        """Generate comprehensive verification report."""
        print("📊 Generating verification report...")
        
        # Run all verifications
        archive_results = self.verify_archive_structure()
        system_results = self.verify_system_integrity()
        execution_results = self.verify_archival_execution()
        node_modules_results = self.verify_no_active_node_modules()
        
        # Compile results
        self.verification_results.update({
            'archive_integrity': archive_results,
            'system_integrity': system_results,
            'execution_verification': execution_results,
            'node_modules_verification': node_modules_results
        })
        
        # Determine overall success
        self.verification_results['overall_success'] = (
            archive_results['structure_exists'] and
            archive_results['constitutional_markers'] and
            system_results['critical_files_exist'] and
            system_results['constitutional_compliance'] and
            execution_results['archival_success'] and
            execution_results['constitutional_compliance_maintained'] and
            node_modules_results['active_node_modules_removed']
        )
        
        return self.verification_results
    
    def print_summary(self) -> None:
        """Print verification summary."""
        results = self.verification_results
        
        print(f"\n✅ ACGS-2 Archival Verification Complete!")
        print(f"🎯 Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
        print(f"📁 Archive Structure: {'✅' if results['archive_integrity']['structure_exists'] else '❌'}")
        print(f"🏛️ Constitutional Markers: {'✅' if results['archive_integrity']['constitutional_markers'] else '❌'}")
        print(f"📋 System Integrity: {'✅' if results['system_integrity']['critical_files_exist'] else '❌'}")
        print(f"⚖️ Constitutional Compliance: {'✅' if results['system_integrity']['constitutional_compliance'] else '❌'}")
        print(f"📦 Archival Success: {'✅' if results['execution_verification']['archival_success'] else '❌'}")
        print(f"🗂️ Node.js Dependencies: {'✅' if results['node_modules_verification']['active_node_modules_removed'] else '❌'}")
        
        # Print statistics
        exec_results = results['execution_verification']
        print(f"\n📊 Archival Statistics:")
        print(f"   Files Processed: {exec_results['files_processed']}")
        print(f"   Files Archived: {exec_results['files_archived']}")
        print(f"   Files Failed: {exec_results['files_failed']}")
        print(f"   Archive Files Found: {results['archive_integrity']['archived_files_count']}")

def main():
    """Main execution function."""
    print("🚀 ACGS-2 Archival Verification")
    print(f"📋 Constitutional Hash: cdd01ef066bc6cf2")
    
    verifier = ArchivalVerification()
    results = verifier.generate_verification_report()
    
    # Save verification report
    output_file = "archival-verification-report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    verifier.print_summary()
    print(f"📋 Verification report saved to: {output_file}")
    
    return 0 if results['overall_success'] else 1

if __name__ == "__main__":
    main()
