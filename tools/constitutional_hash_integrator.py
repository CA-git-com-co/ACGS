#!/usr/bin/env python3
"""
Constitutional Hash Integrator for ACGS

Systematically integrates the constitutional hash "cdd01ef066bc6cf2" 
across all Python files in the ACGS codebase to achieve 100% compliance.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ConstitutionalHashIntegrator:
    """Integrates constitutional hash across ACGS codebase."""
    
    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.processed_files: Set[str] = set()
        self.integration_stats = {
            "files_processed": 0,
            "files_updated": 0,
            "files_already_compliant": 0,
            "files_skipped": 0,
            "errors": 0
        }
        
        # Directories to process
        self.target_directories = [
            "services/core",
            "services/platform_services", 
            "services/shared",
            "infrastructure",
            "tools"
        ]
        
        # Files to skip
        self.skip_patterns = [
            "__pycache__",
            ".pyc",
            ".git",
            ".venv",
            "node_modules",
            ".pytest_cache",
            "htmlcov",
            ".coverage"
        ]
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        file_str = str(file_path)
        
        # Skip non-Python files
        if not file_str.endswith('.py'):
            return True
        
        # Skip files matching skip patterns
        for pattern in self.skip_patterns:
            if pattern in file_str:
                return True
        
        # Skip test files for now (they have their own constitutional hash)
        if '/test' in file_str or file_str.endswith('_test.py'):
            return True
        
        return False
    
    def has_constitutional_hash(self, content: str) -> bool:
        """Check if content already has constitutional hash."""
        return self.constitutional_hash in content
    
    def add_constitutional_hash_to_content(self, content: str, file_path: Path) -> str:
        """Add constitutional hash to file content."""
        lines = content.split('\n')
        
        # Find the best place to insert the constitutional hash
        insert_line = 0
        
        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            if line.startswith('#!') or 'coding:' in line or 'encoding:' in line:
                insert_line = i + 1
                continue
            break
        
        # Skip docstrings
        in_docstring = False
        docstring_quotes = None
        
        for i in range(insert_line, len(lines)):
            line = lines[i].strip()
            
            # Handle docstrings
            if not in_docstring:
                if line.startswith('"""') or line.startswith("'''"):
                    docstring_quotes = line[:3]
                    in_docstring = True
                    if line.count(docstring_quotes) >= 2:  # Single line docstring
                        in_docstring = False
                        insert_line = i + 1
                    continue
                elif line.startswith('"') and line.endswith('"') and len(line) > 2:
                    # Single line docstring with double quotes
                    insert_line = i + 1
                    continue
            else:
                if docstring_quotes in line:
                    in_docstring = False
                    insert_line = i + 1
                continue
            
            # Skip imports
            if line.startswith('import ') or line.startswith('from '):
                insert_line = i + 1
                continue
            
            # Found a good place to insert
            if line and not line.startswith('#'):
                break
        
        # Insert constitutional hash
        constitutional_comment = f"\n# Constitutional compliance hash for ACGS\nCONSTITUTIONAL_HASH = \"{self.constitutional_hash}\"\n"
        
        # Insert after imports and docstrings
        lines.insert(insert_line, constitutional_comment)
        
        return '\n'.join(lines)
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has constitutional hash
            if self.has_constitutional_hash(content):
                self.integration_stats["files_already_compliant"] += 1
                logger.debug(f"✅ Already compliant: {file_path}")
                return True
            
            # Add constitutional hash
            updated_content = self.add_constitutional_hash_to_content(content, file_path)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.integration_stats["files_updated"] += 1
            logger.info(f"🔧 Updated: {file_path}")
            return True
            
        except Exception as e:
            self.integration_stats["errors"] += 1
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files to process."""
        python_files = []
        
        for directory in self.target_directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                logger.warning(f"Directory not found: {dir_path}")
                continue
            
            for file_path in dir_path.rglob("*.py"):
                if not self.should_skip_file(file_path):
                    python_files.append(file_path)
        
        return python_files
    
    def run_integration(self) -> Dict[str, int]:
        """Run constitutional hash integration across all files."""
        logger.info("🚀 Starting Constitutional Hash Integration")
        logger.info(f"📋 Constitutional Hash: {self.constitutional_hash}")
        
        # Find all Python files
        python_files = self.find_python_files()
        logger.info(f"📁 Found {len(python_files)} Python files to process")
        
        # Process each file
        for file_path in python_files:
            self.integration_stats["files_processed"] += 1
            self.process_file(file_path)
        
        # Calculate compliance rate
        total_files = len(python_files)
        compliant_files = self.integration_stats["files_already_compliant"] + self.integration_stats["files_updated"]
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        # Log summary
        logger.info("=" * 60)
        logger.info("🎯 CONSTITUTIONAL HASH INTEGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📊 Files Processed: {self.integration_stats['files_processed']}")
        logger.info(f"🔧 Files Updated: {self.integration_stats['files_updated']}")
        logger.info(f"✅ Already Compliant: {self.integration_stats['files_already_compliant']}")
        logger.info(f"⏭️ Files Skipped: {self.integration_stats['files_skipped']}")
        logger.info(f"❌ Errors: {self.integration_stats['errors']}")
        logger.info(f"📈 Compliance Rate: {compliance_rate:.1f}%")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        return self.integration_stats
    
    def validate_integration(self) -> Dict[str, any]:
        """Validate constitutional hash integration."""
        logger.info("🔍 Validating Constitutional Hash Integration")
        
        python_files = self.find_python_files()
        compliant_files = 0
        non_compliant_files = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if self.has_constitutional_hash(content):
                    compliant_files += 1
                else:
                    non_compliant_files.append(str(file_path))
            
            except Exception as e:
                logger.error(f"Error validating {file_path}: {e}")
        
        total_files = len(python_files)
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        validation_result = {
            "total_files": total_files,
            "compliant_files": compliant_files,
            "non_compliant_files": non_compliant_files,
            "compliance_rate": compliance_rate,
            "constitutional_hash": self.constitutional_hash
        }
        
        logger.info(f"📊 Validation Results:")
        logger.info(f"   Total Files: {total_files}")
        logger.info(f"   Compliant Files: {compliant_files}")
        logger.info(f"   Compliance Rate: {compliance_rate:.1f}%")
        
        if non_compliant_files:
            logger.warning(f"⚠️ Non-compliant files ({len(non_compliant_files)}):")
            for file_path in non_compliant_files[:10]:  # Show first 10
                logger.warning(f"   - {file_path}")
            if len(non_compliant_files) > 10:
                logger.warning(f"   ... and {len(non_compliant_files) - 10} more")
        
        return validation_result

def main():
    """Main integration entry point."""
    integrator = ConstitutionalHashIntegrator()
    
    try:
        # Run integration
        stats = integrator.run_integration()
        
        # Validate results
        validation = integrator.validate_integration()
        
        # Check if we achieved target compliance
        if validation["compliance_rate"] >= 90.0:
            logger.info("🎉 SUCCESS: Constitutional hash integration achieved >90% compliance!")
            return 0
        else:
            logger.warning(f"⚠️ WARNING: Compliance rate {validation['compliance_rate']:.1f}% below 90% target")
            return 1
            
    except Exception as e:
        logger.error(f"Constitutional hash integration failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
