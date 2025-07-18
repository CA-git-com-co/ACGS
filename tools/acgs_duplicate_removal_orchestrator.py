#!/usr/bin/env python3
"""
ACGS-2 Duplicate Removal Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Systematically removes duplicate implementations while preserving
constitutional compliance and performance requirements.

Features:
- Safe duplicate file removal with backup
- Configuration consolidation
- Requirements.txt deduplication
- Database pattern standardization
- Constitutional compliance validation
"""

import hashlib
import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
log_handlers = [logging.StreamHandler()]
try:
    # Try to create logs directory and add file handler
    Path("logs").mkdir(exist_ok=True)
    log_handlers.append(logging.FileHandler("logs/duplicate_removal.log"))
except (PermissionError, OSError):
    # Fall back to console only if file logging fails
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)


class ACGSDuplicateRemovalOrchestrator:
    """
    Orchestrates systematic removal of duplicate implementations
    while maintaining constitutional compliance.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.backup_dir = self.project_root / f"backup_duplicates_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Track operations for rollback
        self.operations_log = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "removed_files": [],
            "consolidated_configs": [],
            "fixed_requirements": [],
            "errors": []
        }

        # Critical exact duplicates to remove
        self.exact_duplicates = [
            ("tools/acgs_documentation_orchestrator.py", "scripts/development/acgs_documentation_orchestrator.py"),
            ("tools/code_quality_validator.py", "scripts/development/code_quality_validator.py"),
            ("tools/health-check.sh", "scripts/development/health-check.sh"),
            ("tools/database_query_optimization.py", "scripts/development/database_query_optimization.py"),
            ("tools/DUPLICATE_ANALYSIS_REPORT.md", "scripts/development/DUPLICATE_ANALYSIS_REPORT.md"),
        ]

        # Configuration files with duplicate patterns
        self.config_duplicates = [
            "services/core/evolutionary-computation/ec_service_standardized/config.py",
            "services/core/policy-governance/pgc_service_standardized/config.py",
            "services/core/constitutional-ai/ac_service_standardized/config.py",
            "services/core/governance-synthesis/gs_service_standardized/config.py",
        ]

    def create_backup(self) -> None:
        """Create backup of files before removal."""
        logger.info(f"🔄 Creating backup directory: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup all files that will be modified
        for primary, duplicate in self.exact_duplicates:
            if (self.project_root / duplicate).exists():
                backup_path = self.backup_dir / duplicate
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.project_root / duplicate, backup_path)
                logger.info(f"✅ Backed up: {duplicate}")

    def verify_exact_duplicates(self) -> List[Tuple[str, str, bool]]:
        """Verify that files are exact duplicates before removal."""
        logger.info("🔍 Verifying exact duplicates...")
        verification_results = []
        
        for primary, duplicate in self.exact_duplicates:
            primary_path = self.project_root / primary
            duplicate_path = self.project_root / duplicate
            
            if not primary_path.exists():
                logger.warning(f"⚠️ Primary file missing: {primary}")
                verification_results.append((primary, duplicate, False))
                continue
                
            if not duplicate_path.exists():
                logger.warning(f"⚠️ Duplicate file missing: {duplicate}")
                verification_results.append((primary, duplicate, False))
                continue
            
            # Compare file hashes
            primary_hash = self._calculate_file_hash(primary_path)
            duplicate_hash = self._calculate_file_hash(duplicate_path)
            
            is_identical = primary_hash == duplicate_hash
            verification_results.append((primary, duplicate, is_identical))
            
            if is_identical:
                logger.info(f"✅ Verified identical: {primary} == {duplicate}")
            else:
                logger.warning(f"⚠️ Files differ: {primary} != {duplicate}")
        
        return verification_results

    def remove_exact_duplicates(self) -> None:
        """Remove verified exact duplicate files."""
        logger.info("🗑️ Removing exact duplicate files...")
        
        verification_results = self.verify_exact_duplicates()
        
        for primary, duplicate, is_identical in verification_results:
            if is_identical:
                duplicate_path = self.project_root / duplicate
                try:
                    duplicate_path.unlink()
                    logger.info(f"✅ Removed duplicate: {duplicate}")
                    self.operations_log["removed_files"].append(duplicate)
                except Exception as e:
                    logger.error(f"❌ Failed to remove {duplicate}: {e}")
                    self.operations_log["errors"].append(f"Failed to remove {duplicate}: {e}")
            else:
                logger.warning(f"⚠️ Skipped non-identical files: {primary} != {duplicate}")

    def fix_requirements_duplicates(self) -> None:
        """Fix duplicate entries in requirements.txt files."""
        logger.info("🔧 Fixing requirements.txt duplicates...")
        
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))
        
        for req_file in requirements_files:
            try:
                # Read current content
                content = req_file.read_text()
                lines = content.splitlines()
                
                # Remove duplicate lines while preserving order
                seen = set()
                unique_lines = []
                duplicates_found = False
                
                for line in lines:
                    line_clean = line.strip()
                    if line_clean and not line_clean.startswith('#'):
                        if line_clean in seen:
                            duplicates_found = True
                            logger.info(f"🔍 Found duplicate in {req_file}: {line_clean}")
                        else:
                            seen.add(line_clean)
                            unique_lines.append(line)
                    else:
                        unique_lines.append(line)
                
                if duplicates_found:
                    # Write cleaned content
                    req_file.write_text('\n'.join(unique_lines) + '\n')
                    logger.info(f"✅ Fixed duplicates in: {req_file}")
                    self.operations_log["fixed_requirements"].append(str(req_file))
                    
            except Exception as e:
                logger.error(f"❌ Failed to fix {req_file}: {e}")
                self.operations_log["errors"].append(f"Failed to fix {req_file}: {e}")

    def create_shared_database_config(self) -> None:
        """Create shared database configuration template."""
        logger.info("🔧 Creating shared database configuration...")
        
        shared_config_dir = self.project_root / "services/shared/config"
        shared_config_dir.mkdir(parents=True, exist_ok=True)
        
        shared_config_content = f'''"""
Shared Database Configuration for ACGS Services
Constitutional Hash: {self.constitutional_hash}
"""

from pydantic import BaseSettings, Field


class SharedDatabaseConfig(BaseSettings):
    """Shared database configuration for all ACGS services."""
    
    constitutional_hash: str = "{self.constitutional_hash}"
    
    # Connection settings
    url: str = Field(
        default="postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db",
        env="DATABASE_URL",
        description="Database connection URL",
    )
    
    # Enhanced connection pool settings (optimized for >200 concurrent connections)
    pool_size: int = Field(
        default=50,
        env="DATABASE_POOL_SIZE", 
        description="Database connection pool size",
    )
    
    max_overflow: int = Field(
        default=50,
        env="DATABASE_MAX_OVERFLOW",
        description="Maximum connection pool overflow",
    )
    
    pool_timeout: int = Field(
        default=30,
        env="DATABASE_POOL_TIMEOUT",
        description="Connection pool timeout in seconds",
    )
    
    pool_recycle: int = Field(
        default=3600,
        env="DATABASE_POOL_RECYCLE",
        description="Connection pool recycle time in seconds",
    )
    
    # Performance settings
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Enable SQL query logging",
    )
    
    class Config:
        env_prefix = "ACGS_DB_"
        case_sensitive = False
'''
        
        shared_config_path = shared_config_dir / "database_config.py"
        shared_config_path.write_text(shared_config_content)
        logger.info(f"✅ Created shared database config: {shared_config_path}")

    def validate_constitutional_compliance(self) -> bool:
        """Validate that constitutional hash is preserved in all remaining files."""
        logger.info("🔍 Validating constitutional compliance...")
        
        python_files = list(self.project_root.glob("**/*.py"))
        sql_files = list(self.project_root.glob("**/*.sql"))
        
        missing_hash_files = []
        
        for file_path in python_files + sql_files:
            if self._should_check_file(file_path) and file_path.is_file():
                try:
                    content = file_path.read_text(errors='ignore')
                    if self.constitutional_hash not in content:
                        missing_hash_files.append(str(file_path))
                except (IsADirectoryError, PermissionError, OSError):
                    # Skip files that can't be read
                    continue
        
        if missing_hash_files:
            logger.warning(f"⚠️ Files missing constitutional hash: {len(missing_hash_files)}")
            for file_path in missing_hash_files[:5]:  # Show first 5
                logger.warning(f"  - {file_path}")
            return False
        else:
            logger.info("✅ Constitutional compliance validated")
            return True

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def _should_check_file(self, file_path: Path) -> bool:
        """Check if file should be validated for constitutional compliance."""
        # Skip certain directories and files
        skip_patterns = [
            "__pycache__", ".git", "node_modules", "target", ".pytest_cache",
            "htmlcov", ".coverage", "backup_", "logs/"
        ]
        
        file_str = str(file_path)
        return not any(pattern in file_str for pattern in skip_patterns)

    def generate_report(self) -> None:
        """Generate comprehensive duplicate removal report."""
        report_path = self.project_root / "reports" / f"duplicate_removal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add summary statistics
        self.operations_log.update({
            "summary": {
                "files_removed": len(self.operations_log["removed_files"]),
                "configs_consolidated": len(self.operations_log["consolidated_configs"]),
                "requirements_fixed": len(self.operations_log["fixed_requirements"]),
                "errors_encountered": len(self.operations_log["errors"]),
                "constitutional_compliance": self.validate_constitutional_compliance()
            }
        })
        
        report_path.write_text(json.dumps(self.operations_log, indent=2))
        logger.info(f"📊 Report generated: {report_path}")

    def execute_duplicate_removal(self) -> None:
        """Execute complete duplicate removal process."""
        logger.info(f"🚀 Starting ACGS-2 Duplicate Removal (Constitutional Hash: {self.constitutional_hash})")
        
        try:
            # Phase 1: Backup and verification
            self.create_backup()
            
            # Phase 2: Remove exact duplicates
            self.remove_exact_duplicates()
            
            # Phase 3: Fix requirements duplicates
            self.fix_requirements_duplicates()
            
            # Phase 4: Create shared configurations
            self.create_shared_database_config()
            
            # Phase 5: Validation
            compliance_valid = self.validate_constitutional_compliance()
            
            # Phase 6: Generate report
            self.generate_report()
            
            if compliance_valid and not self.operations_log["errors"]:
                logger.info("🎉 Duplicate removal completed successfully!")
            else:
                logger.warning("⚠️ Duplicate removal completed with warnings. Check report for details.")
                
        except Exception as e:
            logger.error(f"❌ Duplicate removal failed: {e}")
            self.operations_log["errors"].append(f"Critical error: {e}")
            raise


def main():
    """Main execution function."""
    orchestrator = ACGSDuplicateRemovalOrchestrator()
    orchestrator.execute_duplicate_removal()


if __name__ == "__main__":
    main()
