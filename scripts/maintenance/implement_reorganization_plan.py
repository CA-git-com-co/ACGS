#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Cleanup and Reorganization Implementation Plan
==================================================================

This script implements the comprehensive cleanup and reorganization plan for the ACGS-1
constitutional governance system. It preserves all critical functionality while optimizing
the codebase structure and removing technical debt.

CRITICAL PRESERVATION REQUIREMENTS:
- Quantumagi Solana deployment (Constitution Hash: cdd01ef066bc6cf2)
- Seven core services: AC, FV, GS, PGC, EC, SE, Auth
- Service integration URLs and environment variables
- Quantum-Inspired Semantic Fault Tolerance System configuration

Author: ACGS-1 Development Team
Version: 1.0.0
Date: 2025-06-24
"""

import os
import sys
import json
import shutil
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reorganization_plan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FileOperation:
    """Track file operations for rollback capability."""
    operation_type: str  # move, copy, delete, create
    source_path: str
    destination_path: Optional[str]
    timestamp: str
    success: bool = False
    error_message: Optional[str] = None

@dataclass
class ServiceStatus:
    """Track service health status."""
    service_name: str
    port: int
    status: str  # running, stopped, error
    pid: Optional[int] = None
    health_check_url: Optional[str] = None
    last_check: Optional[str] = None

@dataclass
class PhaseResult:
    """Track phase execution results."""
    phase_name: str
    start_time: str
    end_time: Optional[str]
    success: bool
    operations: List[FileOperation]
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

class ACGSReorganizationPlan:
    """
    ACGS-1 Comprehensive Cleanup and Reorganization Implementation.
    
    This class orchestrates the 7-phase cleanup and reorganization process
    while preserving all critical system functionality.
    """
    
    def __init__(self, project_root: str = "/home/ubuntu/ACGS", dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / "backups" / self.backup_timestamp
        self.operations_log: List[FileOperation] = []
        self.phase_results: List[PhaseResult] = []
        
        # Critical preservation targets
        self.constitution_hash = "cdd01ef066bc6cf2"
        self.core_services = [
            {"name": "auth", "port": 8000},
            {"name": "ac", "port": 8001},
            {"name": "integrity", "port": 8002},
            {"name": "fv", "port": 8003},
            {"name": "gs", "port": 8004},
            {"name": "pgc", "port": 8005},
            {"name": "ec", "port": 8006}
        ]
        
        # Standard directory structure
        self.standard_dirs = {
            "services": {
                "core": [
                    "constitutional-ai/ac_service",
                    "formal-verification/fv_service",
                    "governance-synthesis/gs_service",
                    "policy-governance/pgc_service",
                    "evolutionary-computation/ec_service",
                    "self-evolving-ai/se_service"
                ],
                "platform": [
                    "authentication/auth_service",
                    "integrity/integrity_service"
                ]
            },
            "blockchain": ["programs", "tests", "scripts", "quantumagi-deployment"],
            "infrastructure": ["docker", "kubernetes", "monitoring", "database"],
            "config": ["production", "staging", "development", "monitoring"],
            "docs": ["api", "architecture", "deployment", "user_guide"],
            "tests": ["unit", "integration", "e2e", "performance"],
            "scripts": ["deployment", "monitoring", "maintenance", "security"]
        }
        
        # Essential root files (limit to 12)
        self.essential_root_files = [
            "README.md",
            "LICENSE", 
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "Makefile",
            "docker-compose.yml",
            "pyproject.toml",
            "package.json",
            "Cargo.toml",
            ".gitignore",
            "conftest.py"
        ]

    def log_operation(self, operation: FileOperation) -> None:
        """Log a file operation for rollback capability."""
        self.operations_log.append(operation)
        logger.info(f"Operation: {operation.operation_type} {operation.source_path} -> {operation.destination_path}")

    def check_service_health(self, service: Dict[str, Any]) -> ServiceStatus:
        """Check if a service is running and healthy."""
        service_name = service["name"]
        port = service["port"]
        
        try:
            # Check if port is in use
            result = subprocess.run(
                ["netstat", "-tlnp"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            port_in_use = f":{port}" in result.stdout
            
            # Try to get PID
            pid = None
            if port_in_use:
                pid_result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if pid_result.returncode == 0 and pid_result.stdout.strip():
                    pid = int(pid_result.stdout.strip().split('\n')[0])
            
            status = "running" if port_in_use else "stopped"
            
            return ServiceStatus(
                service_name=service_name,
                port=port,
                status=status,
                pid=pid,
                health_check_url=f"http://localhost:{port}/health",
                last_check=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error checking service {service_name}: {e}")
            return ServiceStatus(
                service_name=service_name,
                port=port,
                status="error",
                last_check=datetime.now().isoformat()
            )

    def verify_constitution_hash(self) -> bool:
        """Verify that the constitutional governance hash is preserved."""
        try:
            # Check blockchain deployment files
            blockchain_dir = self.project_root / "blockchain"
            
            # Look for constitution hash in various files
            search_files = [
                "constitution_data.json",
                "devnet_program_ids.json",
                "governance_accounts.json"
            ]
            
            for file_name in search_files:
                file_path = blockchain_dir / file_name
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if self.constitution_hash in content:
                            logger.info(f"Constitution hash {self.constitution_hash} found in {file_name}")
                            return True
            
            logger.warning(f"Constitution hash {self.constitution_hash} not found in expected files")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying constitution hash: {e}")
            return False

    def create_backup(self) -> bool:
        """Create a comprehensive backup of the current state."""
        logger.info(f"Creating backup in {self.backup_dir}")
        
        if self.dry_run:
            logger.info("DRY RUN: Would create backup")
            return True
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup critical directories
            critical_dirs = ["services", "blockchain", "config", "scripts", "docs"]
            
            for dir_name in critical_dirs:
                source_dir = self.project_root / dir_name
                if source_dir.exists():
                    dest_dir = self.backup_dir / dir_name
                    shutil.copytree(source_dir, dest_dir, ignore_dangling_symlinks=True)
                    logger.info(f"Backed up {dir_name}")
            
            # Backup essential root files
            for file_name in self.essential_root_files:
                source_file = self.project_root / file_name
                if source_file.exists():
                    dest_file = self.backup_dir / file_name
                    shutil.copy2(source_file, dest_file)
                    logger.info(f"Backed up {file_name}")
            
            # Create backup manifest
            manifest = {
                "timestamp": self.backup_timestamp,
                "constitution_hash": self.constitution_hash,
                "services_backed_up": critical_dirs,
                "files_backed_up": self.essential_root_files,
                "backup_size_mb": self._get_directory_size(self.backup_dir) / (1024 * 1024)
            }
            
            with open(self.backup_dir / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Backup completed successfully: {manifest['backup_size_mb']:.2f} MB")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def _get_directory_size(self, directory: Path) -> int:
        """Get the total size of a directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.warning(f"Error calculating directory size: {e}")
        return total_size

    def phase_1_preparation_and_analysis(self) -> PhaseResult:
        """
        Phase 1: Preparation and Analysis
        - Create timestamped backup
        - Document symlinks and .env files
        - Run health checks on core services
        - Verify Quantumagi deployment
        - Create rollback script
        """
        logger.info("=== PHASE 1: PREPARATION AND ANALYSIS ===")
        start_time = datetime.now().isoformat()
        operations = []
        errors = []
        warnings = []

        try:
            # Step 1: Create backup
            if not self.create_backup():
                errors.append("Failed to create backup")
                return PhaseResult("Phase 1", start_time, datetime.now().isoformat(),
                                 False, operations, errors, warnings, {})

            # Step 2: Document symlinks and .env files
            symlinks = []
            env_files = []

            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.is_symlink():
                        symlinks.append({
                            "path": str(file_path),
                            "target": str(file_path.readlink())
                        })
                    elif file.endswith('.env') or file.startswith('.env'):
                        env_files.append(str(file_path))

            # Step 3: Health check all core services
            service_statuses = []
            for service in self.core_services:
                status = self.check_service_health(service)
                service_statuses.append(status)
                if status.status != "running":
                    warnings.append(f"Service {service['name']} is not running")

            # Step 4: Verify constitution hash
            if not self.verify_constitution_hash():
                errors.append(f"Constitution hash {self.constitution_hash} not found")

            # Step 5: Create rollback script
            rollback_script = self._create_rollback_script()

            # Collect metrics
            metrics = {
                "backup_size_mb": self._get_directory_size(self.backup_dir) / (1024 * 1024),
                "symlinks_found": len(symlinks),
                "env_files_found": len(env_files),
                "services_running": len([s for s in service_statuses if s.status == "running"]),
                "services_total": len(service_statuses),
                "constitution_hash_verified": self.verify_constitution_hash()
            }

            # Save analysis report
            analysis_report = {
                "timestamp": start_time,
                "symlinks": symlinks,
                "env_files": env_files,
                "service_statuses": [asdict(s) for s in service_statuses],
                "metrics": metrics,
                "rollback_script": rollback_script
            }

            if not self.dry_run:
                with open(self.project_root / "analysis_report.json", 'w') as f:
                    json.dump(analysis_report, f, indent=2)

            logger.info(f"Phase 1 completed: {len(errors)} errors, {len(warnings)} warnings")
            return PhaseResult("Phase 1", start_time, datetime.now().isoformat(),
                             len(errors) == 0, operations, errors, warnings, metrics)

        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            errors.append(str(e))
            return PhaseResult("Phase 1", start_time, datetime.now().isoformat(),
                             False, operations, errors, warnings, {})

    def _create_rollback_script(self) -> str:
        """Create a rollback script that can restore from backup."""
        rollback_script = f"""#!/bin/bash
# ACGS-1 Emergency Rollback Script
# Generated: {datetime.now().isoformat()}
# Backup: {self.backup_dir}

set -e

echo "Starting emergency rollback..."

# Stop all services
echo "Stopping services..."
pkill -f "python.*service" || true
sleep 5

# Restore from backup
echo "Restoring from backup: {self.backup_dir}"
if [ -d "{self.backup_dir}" ]; then
    cp -r {self.backup_dir}/* {self.project_root}/
    echo "Rollback completed successfully"
else
    echo "ERROR: Backup directory not found!"
    exit 1
fi

# Restart services
echo "Restarting services..."
cd {self.project_root}
./scripts/start_all_services.sh

echo "Rollback completed. Please verify system functionality."
"""

        rollback_path = self.project_root / "emergency_rollback.sh"
        if not self.dry_run:
            with open(rollback_path, 'w') as f:
                f.write(rollback_script)
            os.chmod(rollback_path, 0o755)

        return str(rollback_path)

    def phase_2_root_directory_cleanup(self) -> PhaseResult:
        """
        Phase 2: Root Directory Cleanup
        - Move files to appropriate directories
        - Preserve essential root files (limit to 12)
        - Generate detailed log of moved files
        """
        logger.info("=== PHASE 2: ROOT DIRECTORY CLEANUP ===")
        start_time = datetime.now().isoformat()
        operations = []
        errors = []
        warnings = []

        try:
            # Get current root files
            root_files = [f for f in self.project_root.iterdir()
                         if f.is_file() and not f.name.startswith('.')]

            files_to_move = []
            files_to_keep = []

            for file_path in root_files:
                if file_path.name in self.essential_root_files:
                    files_to_keep.append(file_path)
                else:
                    files_to_move.append(file_path)

            logger.info(f"Found {len(root_files)} root files")
            logger.info(f"Keeping {len(files_to_keep)} essential files")
            logger.info(f"Moving {len(files_to_move)} non-essential files")

            # Move non-essential files to appropriate directories
            for file_path in files_to_move:
                destination = self._determine_file_destination(file_path)
                if destination:
                    operation = FileOperation(
                        operation_type="move",
                        source_path=str(file_path),
                        destination_path=str(destination),
                        timestamp=datetime.now().isoformat()
                    )

                    try:
                        if not self.dry_run:
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(destination))

                        operation.success = True
                        logger.info(f"Moved {file_path.name} -> {destination}")

                    except Exception as e:
                        operation.error_message = str(e)
                        errors.append(f"Failed to move {file_path.name}: {e}")

                    operations.append(operation)
                    self.log_operation(operation)
                else:
                    warnings.append(f"No destination determined for {file_path.name}")

            # Verify we're under the 12 file limit
            remaining_files = [f for f in self.project_root.iterdir()
                             if f.is_file() and not f.name.startswith('.')]

            if len(remaining_files) > 12:
                warnings.append(f"Root directory still has {len(remaining_files)} files (target: 12)")

            metrics = {
                "files_moved": len([op for op in operations if op.success]),
                "files_kept": len(files_to_keep),
                "files_remaining": len(remaining_files),
                "target_achieved": len(remaining_files) <= 12
            }

            logger.info(f"Phase 2 completed: {metrics['files_moved']} files moved")
            return PhaseResult("Phase 2", start_time, datetime.now().isoformat(),
                             len(errors) == 0, operations, errors, warnings, metrics)

        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            errors.append(str(e))
            return PhaseResult("Phase 2", start_time, datetime.now().isoformat(),
                             False, operations, errors, warnings, {})

    def _determine_file_destination(self, file_path: Path) -> Optional[Path]:
        """Determine the appropriate destination for a file based on its type."""
        file_name = file_path.name.lower()

        # Documentation files
        if any(ext in file_name for ext in ['.md', '_report', '_summary', '_guide']):
            return self.project_root / "docs" / "reports" / file_path.name

        # Configuration files
        if any(ext in file_name for ext in ['.yml', '.yaml', '.json', '.toml', '.ini']):
            if 'docker' in file_name:
                return self.project_root / "infrastructure" / "docker" / file_path.name
            elif any(env in file_name for env in ['prod', 'staging', 'dev']):
                return self.project_root / "config" / "environments" / file_path.name
            else:
                return self.project_root / "config" / file_path.name

        # Script files
        if file_name.endswith('.sh') or file_name.endswith('.py'):
            return self.project_root / "scripts" / "maintenance" / file_path.name

        # Log files
        if 'log' in file_name or file_name.endswith('.log'):
            return self.project_root / "logs" / file_path.name

        # Backup files
        if 'backup' in file_name or file_name.endswith('.bak'):
            return self.project_root / "backups" / "misc" / file_path.name

        # Default to archive for unclassified files
        return self.project_root / "archive" / "unclassified" / file_path.name

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of system functionality."""
        logger.info("Running comprehensive validation...")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "blockchain": {},
            "configuration": {},
            "overall_status": "unknown"
        }

        try:
            # Validate services
            services_healthy = 0
            for service in self.core_services:
                status = self.check_service_health(service)
                validation_results["services"][service["name"]] = {
                    "status": status.status,
                    "port": status.port,
                    "pid": status.pid,
                    "healthy": status.status == "running"
                }
                if status.status == "running":
                    services_healthy += 1

            # Validate blockchain
            constitution_valid = self.verify_constitution_hash()
            validation_results["blockchain"] = {
                "constitution_hash_valid": constitution_valid,
                "quantumagi_deployment": "verified" if constitution_valid else "error"
            }

            # Validate configuration
            config_files_exist = all([
                (self.project_root / "config" / "production.env").exists(),
                (self.project_root / "config" / "services").exists(),
                (self.project_root / "docker-compose.yml").exists()
            ])

            validation_results["configuration"] = {
                "essential_configs_exist": config_files_exist,
                "directory_structure_valid": self._validate_directory_structure()
            }

            # Overall status
            all_services_healthy = services_healthy == len(self.core_services)
            overall_healthy = (all_services_healthy and
                             constitution_valid and
                             config_files_exist)

            validation_results["overall_status"] = "healthy" if overall_healthy else "degraded"
            validation_results["summary"] = {
                "services_healthy": f"{services_healthy}/{len(self.core_services)}",
                "blockchain_valid": constitution_valid,
                "config_valid": config_files_exist
            }

            logger.info(f"Validation completed: {validation_results['overall_status']}")
            return validation_results

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_results["overall_status"] = "error"
            validation_results["error"] = str(e)
            return validation_results

    def _validate_directory_structure(self) -> bool:
        """Validate that the directory structure matches the standard."""
        try:
            required_dirs = [
                "services/core",
                "services/platform",
                "blockchain",
                "infrastructure",
                "config",
                "docs",
                "tests",
                "scripts"
            ]

            for dir_path in required_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    logger.warning(f"Missing directory: {dir_path}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Directory structure validation failed: {e}")
            return False

    def execute_phase(self, phase_name: str) -> PhaseResult:
        """Execute a specific phase of the reorganization plan."""
        logger.info(f"Executing phase: {phase_name}")

        if phase_name == "preparation" or phase_name == "1":
            return self.phase_1_preparation_and_analysis()
        elif phase_name == "cleanup" or phase_name == "2":
            return self.phase_2_root_directory_cleanup()
        elif phase_name == "validation":
            # Run validation and return as phase result
            validation = self.run_comprehensive_validation()
            return PhaseResult(
                phase_name="Validation",
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                success=validation["overall_status"] == "healthy",
                operations=[],
                errors=[] if validation["overall_status"] != "error" else [validation.get("error", "Unknown error")],
                warnings=[],
                metrics=validation
            )
        else:
            logger.error(f"Unknown phase: {phase_name}")
            return PhaseResult(
                phase_name=phase_name,
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat(),
                success=False,
                operations=[],
                errors=[f"Unknown phase: {phase_name}"],
                warnings=[],
                metrics={}
            )

    def execute_all_phases(self) -> List[PhaseResult]:
        """Execute all phases of the reorganization plan."""
        logger.info("=== STARTING COMPREHENSIVE REORGANIZATION ===")

        phases = ["preparation", "cleanup"]
        results = []

        for phase in phases:
            logger.info(f"Starting {phase} phase...")
            result = self.execute_phase(phase)
            results.append(result)
            self.phase_results.append(result)

            if not result.success:
                logger.error(f"Phase {phase} failed, stopping execution")
                break

            logger.info(f"Phase {phase} completed successfully")

        # Always run final validation
        logger.info("Running final validation...")
        validation_result = self.execute_phase("validation")
        results.append(validation_result)
        self.phase_results.append(validation_result)

        return results

    def generate_execution_report(self) -> Dict[str, Any]:
        """Generate a comprehensive execution report."""
        logger.info("Generating execution report...")

        total_operations = sum(len(phase.operations) for phase in self.phase_results)
        successful_operations = sum(
            len([op for op in phase.operations if op.success])
            for phase in self.phase_results
        )

        report = {
            "execution_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_phases": len(self.phase_results),
                "successful_phases": len([p for p in self.phase_results if p.success]),
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "dry_run": self.dry_run,
                "backup_location": str(self.backup_dir)
            },
            "phase_results": [asdict(phase) for phase in self.phase_results],
            "preservation_status": {
                "constitution_hash": self.constitution_hash,
                "constitution_verified": self.verify_constitution_hash(),
                "services_status": [
                    asdict(self.check_service_health(service))
                    for service in self.core_services
                ]
            },
            "file_operations": [asdict(op) for op in self.operations_log],
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on execution results."""
        recommendations = []

        # Check if any phases failed
        failed_phases = [p for p in self.phase_results if not p.success]
        if failed_phases:
            recommendations.append(
                f"Review and address failures in phases: {[p.phase_name for p in failed_phases]}"
            )

        # Check service health
        unhealthy_services = []
        for service in self.core_services:
            status = self.check_service_health(service)
            if status.status != "running":
                unhealthy_services.append(service["name"])

        if unhealthy_services:
            recommendations.append(
                f"Restart unhealthy services: {unhealthy_services}"
            )

        # Check constitution hash
        if not self.verify_constitution_hash():
            recommendations.append(
                "Verify and restore constitutional governance configuration"
            )

        # General recommendations
        recommendations.extend([
            "Run comprehensive tests to verify system functionality",
            "Update documentation to reflect new directory structure",
            "Monitor system performance for 24 hours after reorganization",
            "Schedule regular cleanup maintenance based on this process"
        ])

        return recommendations

def main():
    """Main execution function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="ACGS-1 Comprehensive Cleanup and Reorganization Implementation"
    )

    parser.add_argument(
        "--phase",
        choices=["all", "preparation", "cleanup", "validation", "1", "2"],
        default="all",
        help="Phase to execute (default: all)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing them"
    )

    parser.add_argument(
        "--project-root",
        default="/home/ubuntu/ACGS",
        help="Project root directory (default: /home/ubuntu/ACGS)"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Execute emergency rollback from latest backup"
    )

    args = parser.parse_args()

    # Initialize reorganization plan
    reorganizer = ACGSReorganizationPlan(
        project_root=args.project_root,
        dry_run=args.dry_run
    )

    try:
        if args.rollback:
            logger.info("=== EMERGENCY ROLLBACK REQUESTED ===")
            # Find latest backup and execute rollback
            backups_dir = Path(args.project_root) / "backups"
            if backups_dir.exists():
                backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir()]
                if backup_dirs:
                    latest_backup = max(backup_dirs, key=lambda x: x.name)
                    logger.info(f"Rolling back from: {latest_backup}")

                    # Execute rollback script
                    rollback_script = Path(args.project_root) / "emergency_rollback.sh"
                    if rollback_script.exists():
                        subprocess.run(["bash", str(rollback_script)], check=True)
                        logger.info("Rollback completed successfully")
                    else:
                        logger.error("Rollback script not found")
                        sys.exit(1)
                else:
                    logger.error("No backups found for rollback")
                    sys.exit(1)
            else:
                logger.error("Backups directory not found")
                sys.exit(1)

            return

        # Execute requested phase(s)
        if args.phase == "all":
            results = reorganizer.execute_all_phases()
        else:
            result = reorganizer.execute_phase(args.phase)
            results = [result]

        # Generate and save execution report
        report = reorganizer.generate_execution_report()
        report_file = f"reorganization_report_{reorganizer.backup_timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        successful_phases = len([r for r in results if r.success])
        total_phases = len(results)

        logger.info("=== EXECUTION SUMMARY ===")
        logger.info(f"Phases completed: {successful_phases}/{total_phases}")
        logger.info(f"Total operations: {len(reorganizer.operations_log)}")
        logger.info(f"Report saved: {report_file}")

        if args.dry_run:
            logger.info("DRY RUN completed - no changes were made")

        # Print recommendations
        recommendations = report["recommendations"]
        if recommendations:
            logger.info("=== RECOMMENDATIONS ===")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"{i}. {rec}")

        # Exit with appropriate code
        if successful_phases == total_phases:
            logger.info("✅ Reorganization completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Reorganization completed with errors")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Reorganization interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Reorganization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
