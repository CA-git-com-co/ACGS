#!/usr/bin/env python3
"""
ACGS-2 Configuration References Update Script
Constitutional Hash: cdd01ef066bc6cf2

This script updates all references to moved configuration files throughout the codebase
to maintain system functionality after reorganization.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ConfigReferencesUpdater:
    """Update configuration file references after reorganization"""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "updated_files": [],
            "errors": [],
            "summary": {}
        }
        
        # Define path mappings for moved files
        self.path_mappings = {
            # Docker Compose files
            "config/docker/docker-compose.local.yml": "config/docker/config/docker/docker-compose.local.yml",
            "config/docker/docker-compose.test.yml": "config/docker/config/docker/docker-compose.test.yml",
            "./config/docker/docker-compose.local.yml": "./config/docker/config/docker/docker-compose.local.yml",
            "./config/docker/docker-compose.test.yml": "./config/docker/config/docker/docker-compose.test.yml",
            
            # Requirements files
            "config/environments/requirements.txt": "config/environments/config/environments/requirements.txt",
            "config/environments/requirements-security.txt": "config/environments/config/environments/requirements-security.txt",
            "./config/environments/requirements.txt": "./config/environments/config/environments/requirements.txt",
            "./config/environments/requirements-security.txt": "./config/environments/config/environments/requirements-security.txt",
            "-r config/environments/requirements.txt": "-r config/environments/config/environments/requirements.txt",
            
            # Python configuration
            "config/environments/pyproject.toml": "config/environments/config/environments/pyproject.toml",
            "./config/environments/pyproject.toml": "./config/environments/config/environments/pyproject.toml",
            
            # Test configuration
            "config/environments/pytest.ini": "config/environments/config/environments/pytest.ini",
            "config/environments/pytest.benchmark.ini": "config/environments/config/environments/pytest.benchmark.ini",
            "./config/environments/pytest.ini": "./config/environments/config/environments/pytest.ini",
            
            # Package management
            "config/environments/pnpm-lock.yaml": "config/environments/config/environments/pnpm-lock.yaml",
            "config/environments/pnpm-workspace.yaml": "config/environments/config/environments/pnpm-workspace.yaml",
            "config/environments/uv.lock": "config/environments/config/environments/uv.lock",
            "config/environments/uv.toml": "config/environments/config/environments/uv.toml",
            
            # Nginx
            "config/nginx.production.conf": "config/config/nginx.production.conf"
        }
        
    def find_files_to_update(self) -> List[Path]:
        """Find files that might contain configuration references"""
        patterns = [
            "*.py", "*.sh", "*.yml", "*.yaml", "*.md", "*.json",
            "*.js", "*.ts", "*.rs", "*.toml", "*.cfg", "*.ini"
        ]
        
        files_to_check = []
        
        # Search in key directories
        search_dirs = [
            "scripts", ".github", "tools", "docs", "services",
            "infrastructure", "deployment", "tests"
        ]
        
        for search_dir in search_dirs:
            dir_path = self.project_root / search_dir
            if dir_path.exists():
                for pattern in patterns:
                    files_to_check.extend(dir_path.rglob(pattern))
                    
        # Also check root level files
        for pattern in patterns:
            files_to_check.extend(self.project_root.glob(pattern))
            
        return list(set(files_to_check))  # Remove duplicates
        
    def update_file_references(self, file_path: Path) -> bool:
        """Update configuration references in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            updated = False
            
            # Apply path mappings
            for old_path, new_path in self.path_mappings.items():
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    updated = True
                    
            # Special handling for specific file types
            if file_path.suffix in ['.yml', '.yaml']:
                content = self.update_yaml_references(content)
                if content != original_content:
                    updated = True
                    
            elif file_path.suffix == '.py':
                content = self.update_python_references(content)
                if content != original_content:
                    updated = True
                    
            elif file_path.suffix == '.sh':
                content = self.update_shell_references(content)
                if content != original_content:
                    updated = True
                    
            # Write back if updated
            if updated:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                if not backup_path.exists():  # Don't overwrite existing backups
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                        
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Updated: {file_path.relative_to(self.project_root)}")
                self.report["updated_files"].append(str(file_path.relative_to(self.project_root)))
                return True
                
            return False
            
        except Exception as e:
            error_msg = f"Failed to update {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.report["errors"].append(error_msg)
            return False
            
    def update_yaml_references(self, content: str) -> str:
        """Update YAML-specific configuration references"""
        # Update docker-compose file references in CI/CD
        content = re.sub(
            r'docker-compose -f docker-compose\.([^\.]+)\.yml',
            r'docker-compose -f config/docker/docker-compose.\1.yml',
            content
        )
        
        # Update paths in GitHub Actions
        content = re.sub(
            r'requirements\*\.txt',
            r'config/environments/requirements*.txt',
            content
        )
        
        return content
        
    def update_python_references(self, content: str) -> str:
        """Update Python-specific configuration references"""
        # Update requirements file references in Python scripts
        content = re.sub(
            r'open\(["\']requirements\.txt["\']',
            r'open("config/environments/config/environments/requirements.txt"',
            content
        )
        
        # Update config/environments/pyproject.toml references
        content = re.sub(
            r'["\']pyproject\.toml["\']',
            r'"config/environments/config/environments/pyproject.toml"',
            content
        )
        
        return content
        
    def update_shell_references(self, content: str) -> str:
        """Update shell script configuration references"""
        # Update docker-compose commands
        content = re.sub(
            r'docker-compose -f docker-compose\.([^\.]+)\.yml',
            r'docker-compose -f config/docker/docker-compose.\1.yml',
            content
        )
        
        # Update pip install commands
        content = re.sub(
            r'pip install -r requirements\.txt',
            r'pip install -r config/environments/config/environments/requirements.txt',
            content
        )
        
        # Update pytest commands
        content = re.sub(
            r'pytest -c pytest\.ini',
            r'pytest -c config/environments/config/environments/pytest.ini',
            content
        )
        
        return content
        
    def update_all_references(self):
        """Update all configuration references in the project"""
        print(f"\n🔄 Updating configuration references...")
        print(f"📍 Project root: {self.project_root}")
        print(f"🔒 Constitutional hash: {self.CONSTITUTIONAL_HASH}")
        
        files_to_update = self.find_files_to_update()
        print(f"📁 Found {len(files_to_update)} files to check")
        
        updated_count = 0
        for file_path in files_to_update:
            if self.update_file_references(file_path):
                updated_count += 1
                
        print(f"\n✅ Updated {updated_count} files")
        
    def generate_report(self):
        """Generate update report"""
        self.report["summary"] = {
            "total_updated": len(self.report["updated_files"]),
            "total_errors": len(self.report["errors"]),
            "path_mappings": self.path_mappings
        }
        
        report_path = self.project_root / "reports" / f"config_references_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        print(f"\n📋 Report saved: {report_path}")
        
    def run(self):
        """Execute the complete update process"""
        self.update_all_references()
        self.generate_report()
        print(f"\n🎉 Configuration references update completed!")
        print(f"🔒 Constitutional compliance maintained: {self.CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    updater = ConfigReferencesUpdater()
    updater.run()
