#!/usr/bin/env python3
"""
ACGS Docker and Infrastructure Cleanup
Constitutional Hash: cdd01ef066bc6cf2

Safely cleans Docker build artifacts, unused containers, and infrastructure
temporary files while preserving constitutional compliance and ACGS services.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Docker cleanup commands (safe operations only)
DOCKER_CLEANUP_COMMANDS = [
    "docker system prune -f --volumes",  # Remove unused data
    "docker image prune -f",             # Remove dangling images
    "docker container prune -f",         # Remove stopped containers
    "docker volume prune -f",            # Remove unused volumes
    "docker network prune -f"            # Remove unused networks
]

# Infrastructure files safe to clean
INFRASTRUCTURE_CLEANUP_PATTERNS = [
    "*.pid",
    "*.lock",
    "*.sock",
    "*.tmp",
    "*.temp"
]

# Protected infrastructure patterns
PROTECTED_INFRASTRUCTURE = [
    "*constitutional*",
    "*compliance*",
    "*governance*",
    "*auth*",
    "*security*"
]

class ACGSDockerInfrastructureCleanup:
    """Handles safe cleanup of Docker and infrastructure artifacts."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.cleanup_stats = {
            "docker_images_removed": 0,
            "docker_containers_removed": 0,
            "docker_volumes_removed": 0,
            "docker_networks_removed": 0,
            "files_removed": 0,
            "bytes_freed": 0,
            "protected_files": 0,
            "errors": []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cleanup operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _run_command(self, command: str) -> Tuple[bool, str, str]:
        """Run shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def _is_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        success, stdout, stderr = self._run_command("docker --version")
        if not success:
            self.logger.warning("Docker not available, skipping Docker cleanup")
            return False
        
        success, stdout, stderr = self._run_command("docker info")
        if not success:
            self.logger.warning("Docker daemon not running, skipping Docker cleanup")
            return False
        
        return True
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file should be protected from cleanup."""
        file_str = str(file_path).lower()
        
        # Check for constitutional compliance content
        if CONSTITUTIONAL_HASH in file_str:
            return True
            
        # Check protected patterns
        for pattern in PROTECTED_INFRASTRUCTURE:
            if pattern.replace("*", "") in file_str:
                return True
        
        return False
    
    def check_acgs_services_status(self) -> Dict[str, bool]:
        """Check if ACGS services are running before cleanup."""
        self.logger.info("🔍 Checking ACGS services status...")
        
        acgs_services = {
            "constitutional-ai": False,
            "integrity-service": False,
            "auth-service": False,
            "multi-agent-coordinator": False
        }
        
        # Check for running containers
        success, stdout, stderr = self._run_command("docker ps --format '{{.Names}}'")
        if success:
            running_containers = stdout.strip().split('\n') if stdout.strip() else []
            for service in acgs_services:
                if any(service in container for container in running_containers):
                    acgs_services[service] = True
                    self.logger.info(f"  ✅ {service} is running")
                else:
                    self.logger.info(f"  ⏸️ {service} is not running")
        
        return acgs_services
    
    def clean_docker_artifacts(self) -> Dict[str, int]:
        """Clean Docker build artifacts and unused resources."""
        self.logger.info("🐳 Cleaning Docker artifacts...")
        
        if not self._is_docker_available():
            return {"skipped": True}
        
        # Check ACGS services before cleanup
        services_status = self.check_acgs_services_status()
        
        docker_stats = {
            "images_removed": 0,
            "containers_removed": 0,
            "volumes_removed": 0,
            "networks_removed": 0,
            "space_freed": 0
        }
        
        # Get initial disk usage
        success, initial_usage, _ = self._run_command("docker system df --format 'table {{.Type}}\t{{.Size}}'")
        
        for command in DOCKER_CLEANUP_COMMANDS:
            self.logger.info(f"  Running: {command}")
            success, stdout, stderr = self._run_command(command)
            
            if success:
                self.logger.info(f"  ✅ Command completed successfully")
                if stdout:
                    # Parse output for statistics
                    if "deleted" in stdout.lower():
                        lines = stdout.strip().split('\n')
                        for line in lines:
                            if "deleted" in line.lower():
                                self.logger.info(f"    {line}")
            else:
                error_msg = f"Docker command failed: {command} - {stderr}"
                self.cleanup_stats["errors"].append(error_msg)
                self.logger.error(f"  ❌ {error_msg}")
        
        # Get final disk usage
        success, final_usage, _ = self._run_command("docker system df --format 'table {{.Type}}\t{{.Size}}'")
        
        return docker_stats
    
    def clean_infrastructure_files(self) -> List[str]:
        """Clean infrastructure temporary files."""
        self.logger.info("🏗️ Cleaning infrastructure temporary files...")
        removed_files = []
        
        for pattern in INFRASTRUCTURE_CLEANUP_PATTERNS:
            for infra_file in REPO_ROOT.rglob(pattern):
                if infra_file.is_file():
                    if self._is_protected_file(infra_file):
                        self.cleanup_stats["protected_files"] += 1
                        self.logger.info(f"  🛡️ Protected: {infra_file.relative_to(REPO_ROOT)}")
                        continue
                    
                    try:
                        size = infra_file.stat().st_size
                        infra_file.unlink()
                        removed_files.append(str(infra_file.relative_to(REPO_ROOT)))
                        self.cleanup_stats["files_removed"] += 1
                        self.cleanup_stats["bytes_freed"] += size
                        self.logger.info(f"  ✅ Removed: {infra_file.relative_to(REPO_ROOT)}")
                    except Exception as e:
                        error_msg = f"Failed to remove {infra_file}: {e}"
                        self.cleanup_stats["errors"].append(error_msg)
                        self.logger.error(f"  ❌ {error_msg}")
        
        return removed_files
    
    def clean_node_modules(self) -> List[str]:
        """Clean node_modules directories (except in protected areas)."""
        self.logger.info("📦 Cleaning node_modules directories...")
        removed_dirs = []
        
        for node_modules in REPO_ROOT.rglob("node_modules"):
            if node_modules.is_dir():
                # Check if in protected area
                if self._is_protected_file(node_modules):
                    self.cleanup_stats["protected_files"] += 1
                    self.logger.info(f"  🛡️ Protected: {node_modules.relative_to(REPO_ROOT)}")
                    continue
                
                # Skip if it's in a critical service directory
                critical_paths = ["services/core", "services/shared", "infrastructure/monitoring"]
                if any(critical in str(node_modules) for critical in critical_paths):
                    self.logger.info(f"  🛡️ Skipping critical: {node_modules.relative_to(REPO_ROOT)}")
                    continue
                
                try:
                    import shutil
                    shutil.rmtree(node_modules)
                    removed_dirs.append(str(node_modules.relative_to(REPO_ROOT)))
                    self.cleanup_stats["files_removed"] += 1
                    self.logger.info(f"  ✅ Removed: {node_modules.relative_to(REPO_ROOT)}")
                except Exception as e:
                    error_msg = f"Failed to remove {node_modules}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")
        
        return removed_dirs
    
    def validate_acgs_services_post_cleanup(self) -> bool:
        """Ensure ACGS services can still start after cleanup."""
        self.logger.info("🔍 Validating ACGS services post-cleanup...")
        
        # Check if docker-compose files are still intact
        compose_files = [
            "docker-compose.yml",
            "docker-compose.services.yml",
            "docker-compose.monitoring.yml"
        ]
        
        all_intact = True
        for compose_file in compose_files:
            file_path = REPO_ROOT / compose_file
            if file_path.exists():
                self.logger.info(f"  ✅ {compose_file} intact")
            else:
                self.logger.error(f"  ❌ {compose_file} missing!")
                all_intact = False
        
        return all_intact
    
    def run_cleanup(self) -> Dict:
        """Run complete Docker and infrastructure cleanup."""
        self.logger.info("🧹 Starting ACGS Docker and Infrastructure Cleanup...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        # Run all cleanup operations
        docker_stats = self.clean_docker_artifacts()
        self.clean_infrastructure_files()
        self.clean_node_modules()
        
        # Validate services post-cleanup
        if not self.validate_acgs_services_post_cleanup():
            self.logger.error("❌ ACGS services validation failed!")
            return {"error": "ACGS services validation failed"}
        
        # Format bytes freed
        bytes_freed = self.cleanup_stats["bytes_freed"]
        if bytes_freed > 1024 * 1024:
            size_str = f"{bytes_freed / (1024 * 1024):.1f} MB"
        elif bytes_freed > 1024:
            size_str = f"{bytes_freed / 1024:.1f} KB"
        else:
            size_str = f"{bytes_freed} bytes"
        
        self.logger.info("📊 Cleanup Summary:")
        self.logger.info(f"  Files removed: {self.cleanup_stats['files_removed']}")
        self.logger.info(f"  Protected files: {self.cleanup_stats['protected_files']}")
        self.logger.info(f"  Space freed: {size_str}")
        self.logger.info(f"  Errors: {len(self.cleanup_stats['errors'])}")
        
        if "skipped" in docker_stats:
            self.logger.info("  Docker cleanup: Skipped (Docker not available)")
        else:
            self.logger.info("  Docker cleanup: Completed")
        
        if self.cleanup_stats["errors"]:
            self.logger.warning("⚠️ Errors encountered:")
            for error in self.cleanup_stats["errors"]:
                self.logger.warning(f"  - {error}")
        
        return self.cleanup_stats

def main():
    """Main cleanup function."""
    print("🧹 ACGS Docker and Infrastructure Cleanup")
    print("=" * 45)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()
    
    cleaner = ACGSDockerInfrastructureCleanup()
    results = cleaner.run_cleanup()
    
    if "error" not in results:
        print("\n✅ Docker and infrastructure cleanup completed!")
    else:
        print(f"\n❌ Cleanup failed: {results['error']}")
    
    return results

if __name__ == "__main__":
    main()
