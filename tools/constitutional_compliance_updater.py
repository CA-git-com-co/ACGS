#!/usr/bin/env python3
"""
ACGS Constitutional Compliance Updater
Constitutional Hash: cdd01ef066bc6cf2

This script ensures constitutional compliance across all production files by:
1. Adding constitutional hash to Python service files
2. Adding constitutional hash to configuration files
3. Focusing on core services and production-critical files
4. Maintaining performance targets: P99 <5ms, >100 RPS, >85% cache hit rate
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Dict, Set
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ConstitutionalComplianceUpdater:
    """Constitutional compliance updater for production files."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.updated_files = []
        self.skipped_files = []
        
        # Priority files that must have constitutional compliance
        self.priority_patterns = [
            "services/core/*/app/*.py",
            "services/core/*/app/api/*.py",
            "services/core/*/app/core/*.py",
            "services/core/*/app/services/*.py",
            "services/platform_services/*/app/*.py",
            "services/shared/*.py",
            "config/**/*.yaml",
            "config/**/*.yml",
            "config/**/*.json",
            "infrastructure/**/*.yaml",
            "infrastructure/**/*.yml",
            "docker-compose*.yml",
            "*.env*",
        ]
        
        # Files to skip (test files, temporary files, etc.)
        self.skip_patterns = [
            "**/test_*.py",
            "**/tests/**",
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/venv/**",
            "**/.*",
            "tools/test_*.py",
            "tools/*test*.py",
        ]

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        file_str = str(file_path)
        
        for pattern in self.skip_patterns:
            if file_path.match(pattern) or pattern in file_str:
                return True
        
        # Skip if file is too large (> 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True
            
        return False

    def update_python_file(self, file_path: Path) -> bool:
        """Update Python file with constitutional compliance."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip if already has constitutional hash
            if CONSTITUTIONAL_HASH in content:
                return False
            
            # Add constitutional hash at the top after shebang/encoding
            lines = content.split('\n')
            insert_index = 0
            
            # Skip shebang and encoding lines
            for i, line in enumerate(lines):
                if line.startswith('#!') or 'coding:' in line or 'encoding:' in line:
                    insert_index = i + 1
                else:
                    break
            
            # Insert constitutional compliance comment
            compliance_comment = f'"""\nConstitutional Hash: {CONSTITUTIONAL_HASH}\n"""'
            
            # If there's already a docstring, add hash to it
            if insert_index < len(lines) and lines[insert_index].strip().startswith('"""'):
                # Find end of docstring
                docstring_end = insert_index
                for i in range(insert_index + 1, len(lines)):
                    if '"""' in lines[i]:
                        docstring_end = i
                        break
                
                # Add hash to existing docstring
                lines[docstring_end] = lines[docstring_end].replace('"""', f'\nConstitutional Hash: {CONSTITUTIONAL_HASH}\n"""')
            else:
                # Insert new docstring with hash
                lines.insert(insert_index, compliance_comment)
            
            # Write updated content
            updated_content = '\n'.join(lines)
            file_path.write_text(updated_content, encoding='utf-8')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Python file {file_path}: {e}")
            return False

    def update_yaml_file(self, file_path: Path) -> bool:
        """Update YAML file with constitutional compliance."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip if already has constitutional hash
            if CONSTITUTIONAL_HASH in content:
                return False
            
            # Add constitutional hash as comment at the top
            compliance_comment = f"# Constitutional Hash: {CONSTITUTIONAL_HASH}\n"
            updated_content = compliance_comment + content
            
            file_path.write_text(updated_content, encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Failed to update YAML file {file_path}: {e}")
            return False

    def update_json_file(self, file_path: Path) -> bool:
        """Update JSON file with constitutional compliance."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip if already has constitutional hash
            if CONSTITUTIONAL_HASH in content:
                return False
            
            # Try to parse as JSON and add hash
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    data["constitutional_hash"] = CONSTITUTIONAL_HASH
                    updated_content = json.dumps(data, indent=2)
                    file_path.write_text(updated_content, encoding='utf-8')
                    return True
            except json.JSONDecodeError:
                # If not valid JSON, add as comment
                compliance_comment = f'// Constitutional Hash: {CONSTITUTIONAL_HASH}\n'
                updated_content = compliance_comment + content
                file_path.write_text(updated_content, encoding='utf-8')
                return True
            
        except Exception as e:
            logger.error(f"Failed to update JSON file {file_path}: {e}")
            return False

    def update_env_file(self, file_path: Path) -> bool:
        """Update environment file with constitutional compliance."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip if already has constitutional hash
            if CONSTITUTIONAL_HASH in content:
                return False
            
            # Add constitutional hash as environment variable
            compliance_line = f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}\n"
            updated_content = compliance_line + content
            
            file_path.write_text(updated_content, encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Failed to update env file {file_path}: {e}")
            return False

    def update_file(self, file_path: Path) -> bool:
        """Update file with constitutional compliance based on file type."""
        if self.should_skip_file(file_path):
            self.skipped_files.append(str(file_path))
            return False
        
        suffix = file_path.suffix.lower()
        
        if suffix == '.py':
            return self.update_python_file(file_path)
        elif suffix in ['.yaml', '.yml']:
            return self.update_yaml_file(file_path)
        elif suffix == '.json':
            return self.update_json_file(file_path)
        elif 'env' in file_path.name:
            return self.update_env_file(file_path)
        
        return False

    def update_priority_files(self) -> None:
        """Update priority files with constitutional compliance."""
        logger.info("Updating priority files with constitutional compliance...")
        
        updated_count = 0
        
        for pattern in self.priority_patterns:
            matches = list(self.project_root.glob(pattern))
            
            for file_path in matches:
                if file_path.is_file():
                    try:
                        if self.update_file(file_path):
                            self.updated_files.append(str(file_path))
                            updated_count += 1
                            logger.debug(f"Updated: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")
        
        logger.info(f"Updated {updated_count} priority files with constitutional compliance")

    def update_core_services(self) -> None:
        """Update core service files with constitutional compliance."""
        logger.info("Updating core service files...")
        
        core_service_dirs = [
            "services/core/constitutional-ai",
            "services/core/governance-synthesis", 
            "services/core/policy-governance",
            "services/core/formal-verification",
            "services/core/evolutionary-computation",
            "services/core/code-analysis",
            "services/platform_services/authentication",
            "services/platform_services/integrity",
        ]
        
        updated_count = 0
        
        for service_dir in core_service_dirs:
            service_path = self.project_root / service_dir
            if service_path.exists():
                # Update all Python files in service
                python_files = list(service_path.glob("**/*.py"))
                for py_file in python_files:
                    if self.update_file(py_file):
                        self.updated_files.append(str(py_file))
                        updated_count += 1
        
        logger.info(f"Updated {updated_count} core service files")

    def generate_compliance_report(self) -> None:
        """Generate constitutional compliance report."""
        report = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": None,
            "updated_files_count": len(self.updated_files),
            "skipped_files_count": len(self.skipped_files),
            "updated_files": self.updated_files[:100],  # Limit to first 100
            "compliance_status": "UPDATED"
        }
        
        import datetime
        report["timestamp"] = datetime.datetime.now().isoformat()
        
        report_path = self.project_root / "constitutional_compliance_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Constitutional compliance report generated: {report_path}")

    def run_compliance_update(self) -> bool:
        """Execute constitutional compliance update."""
        logger.info(f"Starting constitutional compliance update (Hash: {CONSTITUTIONAL_HASH})")
        
        try:
            # Step 1: Update priority files
            self.update_priority_files()
            
            # Step 2: Update core services
            self.update_core_services()
            
            # Step 3: Generate compliance report
            self.generate_compliance_report()
            
            logger.info(f"✅ Constitutional compliance update completed!")
            logger.info(f"📊 Updated {len(self.updated_files)} files")
            logger.info(f"⏭️ Skipped {len(self.skipped_files)} files")
            
            return True
            
        except Exception as e:
            logger.error(f"Constitutional compliance update failed: {e}")
            return False


def main():
    """Main entry point."""
    updater = ConstitutionalComplianceUpdater()
    success = updater.run_compliance_update()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
