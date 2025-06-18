#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Root Directory Cleanup Script
Systematically organizes all files in the root directory while preserving critical system files.
"""

import os
import json
import shutil
import re
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'root_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RootDirectoryCleanup:
    def __init__(self):
        self.root_path = Path('.')
        self.cleanup_log = {
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'preserved_files': [],
            'moved_files': [],
            'deleted_files': [],
            'errors': []
        }
        
        # Critical files that must be preserved in root
        self.critical_files = {
            'package.json', 'package-lock.json', 'requirements.txt', 'requirements-test.txt', 
            'requirements-security.txt', 'Cargo.toml', 'Cargo.lock', 'pyproject.toml', 
            'uv.lock', 'Makefile', 'README.md', 'SECURITY.md', 'LICENSE', 'CONTRIBUTING.md', 
            'CHANGELOG.md', 'jest.config.js', 'pytest.ini', 'tsconfig.json', 'conftest.py'
        }
        
        # Docker and CI/CD files to preserve
        self.docker_cicd_patterns = [
            r'^docker-compose.*\.yml$', r'^docker-compose.*\.yaml$', r'^Dockerfile.*',
            r'^\.github.*', r'^\.pre-commit-config\.yaml$', r'^\.gitleaks\.toml$'
        ]
        
        # Files to move to specific directories
        self.file_mappings = {
            'root_logs': [
                r'.*\.log$', r'.*_\d{8}_\d{6}\.log$', r'.*_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.log$'
            ],
            'root_reports': [
                r'.*_report.*\.json$', r'.*_report.*\.md$', r'.*_analysis.*\.json$',
                r'.*_results.*\.json$', r'.*_summary.*\.json$', r'.*_completion.*\.md$',
                r'.*REPORT.*\.md$', r'.*ANALYSIS.*\.md$', r'.*SUMMARY.*\.md$',
                r'.*_validation.*\.json$', r'.*_audit.*\.json$'
            ],
            'root_scripts': [
                r'.*\.py$', r'.*\.sh$'  # Will filter out critical files separately
            ],
            'archive/old_configs': [
                r'.*\.json$', r'.*\.yaml$', r'.*\.yml$', r'.*\.toml$', r'.*\.ini$'
            ]
        }
        
        # Temporary files to delete
        self.temp_patterns = [
            r'__pycache__', r'\.pyc$', r'\.pyo$', r'\.tmp$', r'\.temp$', 
            r'_temp_', r'test-ledger', r'venv/', r'node_modules/', r'coverage_demo_html'
        ]

    def is_critical_file(self, file_path):
        """Check if a file is critical and should be preserved in root."""
        file_name = file_path.name
        
        # Check critical files list
        if file_name in self.critical_files:
            return True
            
        # Check docker/CI patterns
        for pattern in self.docker_cicd_patterns:
            if re.match(pattern, file_name):
                return True
                
        return False

    def is_temp_file(self, file_path):
        """Check if a file/directory is temporary and should be deleted."""
        file_name = file_path.name
        for pattern in self.temp_patterns:
            if re.search(pattern, file_name):
                return True
        return False

    def get_target_directory(self, file_path):
        """Determine the target directory for a file."""
        file_name = file_path.name
        
        # Check each mapping category
        for target_dir, patterns in self.file_mappings.items():
            for pattern in patterns:
                if re.search(pattern, file_name):
                    # Special handling for scripts - exclude critical files
                    if target_dir == 'root_scripts' and self.is_critical_file(file_path):
                        continue
                    # Special handling for configs - exclude critical files
                    if target_dir == 'archive/old_configs' and self.is_critical_file(file_path):
                        continue
                    return target_dir
        
        return None

    def move_file(self, source_path, target_dir):
        """Move a file to the target directory."""
        try:
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            destination = target_path / source_path.name
            
            # Handle name conflicts
            counter = 1
            while destination.exists():
                name_parts = source_path.stem, counter, source_path.suffix
                destination = target_path / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.move(str(source_path), str(destination))
            
            self.cleanup_log['moved_files'].append({
                'source': str(source_path),
                'destination': str(destination),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Moved: {source_path} -> {destination}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to move {source_path}: {str(e)}"
            logger.error(error_msg)
            self.cleanup_log['errors'].append(error_msg)
            return False

    def delete_temp_file(self, file_path):
        """Delete a temporary file or directory."""
        try:
            if file_path.is_dir():
                shutil.rmtree(str(file_path))
            else:
                file_path.unlink()
                
            self.cleanup_log['deleted_files'].append({
                'path': str(file_path),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Deleted: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete {file_path}: {str(e)}"
            logger.error(error_msg)
            self.cleanup_log['errors'].append(error_msg)
            return False

    def cleanup_root_directory(self):
        """Main cleanup function."""
        logger.info("Starting ACGS-1 root directory cleanup...")
        
        # Get all items in root directory
        root_items = list(self.root_path.iterdir())
        
        # Filter out existing organized directories
        organized_dirs = {
            'applications', 'blockchain', 'config', 'docs', 'infrastructure', 
            'integrations', 'logs', 'monitoring', 'reports', 'scripts', 'services', 
            'tests', 'tools', 'migrations', 'backups', 'archive', 'root_logs', 
            'root_reports', 'root_scripts', 'temp_cleanup', 'hooks', 'pages', 
            'mcp-servers', 'ssl', 'pids', 'deploy', 'core', 'dgm_output', 
            'coverage_demo_html', 'security_scans'
        }
        
        files_to_process = []
        for item in root_items:
            if item.is_file() or (item.is_dir() and item.name not in organized_dirs):
                files_to_process.append(item)
        
        logger.info(f"Processing {len(files_to_process)} items...")
        
        # Process each file/directory
        for item in files_to_process:
            try:
                # Skip if it's our own analysis/cleanup files
                if 'root_directory_analysis' in item.name or 'comprehensive_root_cleanup' in item.name:
                    continue
                
                # Check if critical file - preserve in root
                if self.is_critical_file(item):
                    self.cleanup_log['preserved_files'].append(str(item))
                    logger.info(f"Preserved: {item}")
                    continue
                
                # Check if temporary file - delete
                if self.is_temp_file(item):
                    self.delete_temp_file(item)
                    continue
                
                # Determine target directory
                target_dir = self.get_target_directory(item)
                if target_dir:
                    self.move_file(item, target_dir)
                else:
                    # Move unclassified files to archive
                    if item.is_file():
                        self.move_file(item, 'archive/unclassified')
                    else:
                        logger.info(f"Skipped directory: {item}")
                        
            except Exception as e:
                error_msg = f"Error processing {item}: {str(e)}"
                logger.error(error_msg)
                self.cleanup_log['errors'].append(error_msg)

    def generate_report(self):
        """Generate cleanup report."""
        report_file = f"root_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add summary statistics
        self.cleanup_log['summary'] = {
            'total_preserved': len(self.cleanup_log['preserved_files']),
            'total_moved': len(self.cleanup_log['moved_files']),
            'total_deleted': len(self.cleanup_log['deleted_files']),
            'total_errors': len(self.cleanup_log['errors'])
        }
        
        with open(report_file, 'w') as f:
            json.dump(self.cleanup_log, f, indent=2)
        
        logger.info(f"Cleanup report saved to: {report_file}")
        
        # Print summary
        print(f"\n🎯 ACGS-1 Root Directory Cleanup Complete!")
        print(f"📊 Summary:")
        print(f"   • Files preserved in root: {self.cleanup_log['summary']['total_preserved']}")
        print(f"   • Files moved to organized directories: {self.cleanup_log['summary']['total_moved']}")
        print(f"   • Temporary files deleted: {self.cleanup_log['summary']['total_deleted']}")
        print(f"   • Errors encountered: {self.cleanup_log['summary']['total_errors']}")
        print(f"📄 Detailed report: {report_file}")
        
        return report_file

def main():
    """Main execution function."""
    cleanup = RootDirectoryCleanup()
    cleanup.cleanup_root_directory()
    report_file = cleanup.generate_report()
    return report_file

if __name__ == "__main__":
    main()
