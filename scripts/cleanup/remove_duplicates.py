#!/usr/bin/env python3

"""
ACGS-2 Duplicate Removal Script
Removes duplicate documentation, scripts, and configurations identified in the audit
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple
import logging
import json
from datetime import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DuplicateRemover:
    """Removes duplicate files and consolidates configurations"""
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.removed_files: List[str] = []
        self.consolidated_files: List[str] = []
        self.errors: List[str] = []
        
        # Define duplicate categories as identified in the audit
        self.duplicates = {
            'backup_directories': [
                'docs_backup_20250717_155154',
                'docs_consolidated_archive_*',
                'migration_backup_*'
            ],
            'duplicate_scripts': [
                'scripts/development/start_missing_services.sh',
                'scripts/development/start_acgs_services_simple.sh',
                'scripts/deployment/start_router_system.sh',
                'scripts/development/validate_reorganization.py',
                'scripts/development/validate_documentation_update.py',
                'scripts/development/validate_fixes.sh',
                'scripts/development/validate_constitutional_compliance.py',
                'scripts/development/cleanup_duplicate_requirements.py',
                'scripts/development/acgs_documentation_orchestrator.py',
                'scripts/development/code_quality_validator.py',
                'scripts/development/health-check.sh'
            ],
            'duplicate_dockerfiles': [
                'infrastructure/docker/Dockerfile.uv',
                'infrastructure/docker/Dockerfile.groq-policy-integration',
                'infrastructure/docker/Dockerfile.acgs'
            ],
            'duplicate_compose_files': [
                'docker-compose.cache-integrated.yml',
                'docker-compose.constitution.yml',
                'docker-compose.override.yml',
                'docker-compose.production.yml',
                'docker-compose.staging.yml',
                'docker-compose.testing.yml'
            ],
            'duplicate_auth_configs': [
                'services/core/constitutional-ai/ac_service/config/auth_config.yaml',
                'services/core/governance-synthesis/gs_service/config/auth_config.yaml',
                'services/core/policy-governance/pgc_service/config/auth_config.yaml',
                'services/core/formal-verification/config/auth_config.yaml',
                'services/core/evolutionary-computation/config/auth_config.yaml',
                'services/platform_services/integrity/config/auth_config.yaml'
                # Keep services/platform_services/authentication/auth_service/config/auth_config.yaml as master
            ],
            'duplicate_documentation': [
                'docs/architecture/AGENTS.md',  # Keep only one
                'docs/architecture/GEMINI.md',  # Keep only one
                'docs/AGENTS.md',
                'docs/GEMINI.md'
            ],
            'legacy_directories': [
                'services/core/governance-synthesis',  # Consolidated into governance-engine
                'services/core/policy-governance',     # Consolidated into governance-engine
                'services/core/evolution-compiler'     # Consolidated into evolutionary-computation
            ]
        }
        
    def scan_for_duplicates(self) -> Dict[str, List[Path]]:
        """Scan for duplicate files based on patterns"""
        found_duplicates = {}
        
        for category, patterns in self.duplicates.items():
            found_duplicates[category] = []
            
            for pattern in patterns:
                if '*' in pattern:
                    # Handle glob patterns
                    for path in self.project_root.glob(pattern):
                        if path.exists():
                            found_duplicates[category].append(path)
                else:
                    # Handle exact paths
                    path = self.project_root / pattern
                    if path.exists():
                        found_duplicates[category].append(path)
                        
        return found_duplicates
        
    def remove_backup_directories(self, backup_dirs: List[Path]) -> None:
        """Remove backup directories"""
        logger.info("Removing backup directories...")
        
        for backup_dir in backup_dirs:
            if backup_dir.is_dir():
                logger.info(f"Removing backup directory: {backup_dir}")
                
                if not self.dry_run:
                    try:
                        shutil.rmtree(backup_dir)
                        self.removed_files.append(str(backup_dir))
                    except Exception as e:
                        error_msg = f"Failed to remove {backup_dir}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {backup_dir}")
                    
    def remove_duplicate_scripts(self, script_files: List[Path]) -> None:
        """Remove duplicate scripts"""
        logger.info("Removing duplicate scripts...")
        
        for script_file in script_files:
            if script_file.is_file():
                logger.info(f"Removing duplicate script: {script_file}")
                
                if not self.dry_run:
                    try:
                        script_file.unlink()
                        self.removed_files.append(str(script_file))
                    except Exception as e:
                        error_msg = f"Failed to remove {script_file}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {script_file}")
                    
    def remove_duplicate_dockerfiles(self, docker_files: List[Path]) -> None:
        """Remove duplicate Dockerfiles"""
        logger.info("Removing duplicate Dockerfiles...")
        
        for docker_file in docker_files:
            if docker_file.is_file():
                logger.info(f"Removing duplicate Dockerfile: {docker_file}")
                
                if not self.dry_run:
                    try:
                        docker_file.unlink()
                        self.removed_files.append(str(docker_file))
                    except Exception as e:
                        error_msg = f"Failed to remove {docker_file}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {docker_file}")
                    
    def remove_duplicate_compose_files(self, compose_files: List[Path]) -> None:
        """Remove duplicate Docker Compose files"""
        logger.info("Removing duplicate Docker Compose files...")
        
        for compose_file in compose_files:
            if compose_file.is_file():
                logger.info(f"Removing duplicate compose file: {compose_file}")
                
                if not self.dry_run:
                    try:
                        compose_file.unlink()
                        self.removed_files.append(str(compose_file))
                    except Exception as e:
                        error_msg = f"Failed to remove {compose_file}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {compose_file}")
                    
    def consolidate_auth_configs(self, auth_config_files: List[Path]) -> None:
        """Consolidate duplicate auth config files"""
        logger.info("Consolidating duplicate auth config files...")
        
        # Master auth config (keep this one)
        master_auth_config = self.project_root / "config/shared/auth_config.yml"
        
        if not master_auth_config.exists():
            logger.warning("Master auth config not found, skipping consolidation")
            return
            
        for auth_config in auth_config_files:
            if auth_config.is_file():
                logger.info(f"Replacing auth config: {auth_config}")
                
                if not self.dry_run:
                    try:
                        # Create symbolic link to master config
                        auth_config.unlink()
                        
                        # Create relative symlink
                        rel_path = os.path.relpath(master_auth_config, auth_config.parent)
                        auth_config.symlink_to(rel_path)
                        
                        self.consolidated_files.append(str(auth_config))
                        
                    except Exception as e:
                        error_msg = f"Failed to consolidate {auth_config}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would link {auth_config} to {master_auth_config}")
                    
    def remove_duplicate_documentation(self, doc_files: List[Path]) -> None:
        """Remove duplicate documentation files"""
        logger.info("Removing duplicate documentation files...")
        
        for doc_file in doc_files:
            if doc_file.is_file():
                logger.info(f"Removing duplicate documentation: {doc_file}")
                
                if not self.dry_run:
                    try:
                        doc_file.unlink()
                        self.removed_files.append(str(doc_file))
                    except Exception as e:
                        error_msg = f"Failed to remove {doc_file}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {doc_file}")
                    
    def remove_legacy_directories(self, legacy_dirs: List[Path]) -> None:
        """Remove legacy service directories"""
        logger.info("Removing legacy service directories...")
        
        for legacy_dir in legacy_dirs:
            if legacy_dir.is_dir():
                logger.info(f"Removing legacy directory: {legacy_dir}")
                
                if not self.dry_run:
                    try:
                        shutil.rmtree(legacy_dir)
                        self.removed_files.append(str(legacy_dir))
                    except Exception as e:
                        error_msg = f"Failed to remove {legacy_dir}: {e}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                else:
                    logger.info(f"[DRY RUN] Would remove: {legacy_dir}")
                    
    def cleanup_requirements_duplicates(self) -> None:
        """Clean up duplicate entries in config/environments/requirements.txt files"""
        logger.info("Cleaning up duplicate requirements...")
        
        requirements_files = list(self.project_root.glob("**/config/environments/requirements.txt"))
        
        for req_file in requirements_files:
            try:
                with open(req_file, 'r') as f:
                    lines = f.readlines()
                    
                # Remove duplicates while preserving order
                seen = set()
                unique_lines = []
                
                for line in lines:
                    cleaned_line = line.strip()
                    if cleaned_line and not cleaned_line.startswith('#'):
                        if cleaned_line not in seen:
                            seen.add(cleaned_line)
                            unique_lines.append(line)
                    else:
                        unique_lines.append(line)
                        
                # Write back if changes were made
                if len(unique_lines) != len(lines):
                    logger.info(f"Removing duplicate requirements in: {req_file}")
                    
                    if not self.dry_run:
                        with open(req_file, 'w') as f:
                            f.writelines(unique_lines)
                        self.consolidated_files.append(str(req_file))
                    else:
                        logger.info(f"[DRY RUN] Would clean: {req_file}")
                        
            except Exception as e:
                error_msg = f"Failed to clean requirements in {req_file}: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                
    def run_cleanup(self) -> None:
        """Run the complete cleanup process"""
        logger.info("Starting ACGS-2 duplicate removal process...")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Dry run: {self.dry_run}")
        
        # Scan for duplicates
        found_duplicates = self.scan_for_duplicates()
        
        # Report what was found
        total_duplicates = sum(len(files) for files in found_duplicates.values())
        logger.info(f"Found {total_duplicates} duplicate items to remove")
        
        for category, files in found_duplicates.items():
            if files:
                logger.info(f"{category}: {len(files)} items")
                
        # Remove duplicates by category
        if found_duplicates.get('backup_directories'):
            self.remove_backup_directories(found_duplicates['backup_directories'])
            
        if found_duplicates.get('duplicate_scripts'):
            self.remove_duplicate_scripts(found_duplicates['duplicate_scripts'])
            
        if found_duplicates.get('duplicate_dockerfiles'):
            self.remove_duplicate_dockerfiles(found_duplicates['duplicate_dockerfiles'])
            
        if found_duplicates.get('duplicate_compose_files'):
            self.remove_duplicate_compose_files(found_duplicates['duplicate_compose_files'])
            
        if found_duplicates.get('duplicate_auth_configs'):
            self.consolidate_auth_configs(found_duplicates['duplicate_auth_configs'])
            
        if found_duplicates.get('duplicate_documentation'):
            self.remove_duplicate_documentation(found_duplicates['duplicate_documentation'])
            
        if found_duplicates.get('legacy_directories'):
            self.remove_legacy_directories(found_duplicates['legacy_directories'])
            
        # Clean up config/environments/requirements.txt duplicates
        self.cleanup_requirements_duplicates()
        
        # Generate report
        self.generate_report()
        
    def generate_report(self) -> None:
        """Generate cleanup report"""
        report = {
            'cleanup_timestamp': datetime.now().isoformat(),
            'constitutional_hash': CONSTITUTIONAL_HASH,
            'project_root': str(self.project_root),
            'dry_run': self.dry_run,
            'summary': {
                'files_removed': len(self.removed_files),
                'files_consolidated': len(self.consolidated_files),
                'errors': len(self.errors)
            },
            'removed_files': self.removed_files,
            'consolidated_files': self.consolidated_files,
            'errors': self.errors
        }
        
        report_file = self.project_root / 'duplicate_removal_report.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Cleanup report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("ACGS-2 DUPLICATE REMOVAL SUMMARY")
        print("="*60)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Dry Run: {self.dry_run}")
        print(f"Files Removed: {len(self.removed_files)}")
        print(f"Files Consolidated: {len(self.consolidated_files)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.dry_run:
            print("\n⚠️  This was a dry run. No files were actually modified.")
            print("Run with --execute to perform the actual cleanup.")
        else:
            print("\n✅ Cleanup completed successfully!")
            
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS-2 Duplicate Removal Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
This script removes duplicate files and configurations identified in the architectural audit.

Categories of duplicates removed:
- Backup directories (docs_backup_*, migration_backup_*)
- Duplicate scripts (validation, deployment, documentation)
- Duplicate Dockerfiles and compose files
- Duplicate authentication configurations
- Legacy service directories
- Duplicate documentation files

Constitutional Hash: {CONSTITUTIONAL_HASH}
        """
    )
    
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Root directory of the ACGS-2 project"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the cleanup (default is dry run)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize remover
    remover = DuplicateRemover(
        project_root=Path(args.project_root),
        dry_run=not args.execute
    )
    
    # Run cleanup
    remover.run_cleanup()


if __name__ == "__main__":
    main()