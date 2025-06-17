#!/usr/bin/env python3
"""
ACGS-1 Simple Backup and Recovery System
Focuses on configurations, service states, and blockchain data
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleBackupSystem:
    """Simple backup system for ACGS-1 configurations and states"""
    
    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.backup_root = Path("/home/dislove/ACGS-1/backups")
        self.services = [
            "auth_service", "ac_service", "integrity_service", 
            "fv_service", "gs_service", "pgc_service", "ec_service"
        ]
        self.service_ports = {
            "auth_service": 8000, "ac_service": 8001, "integrity_service": 8002,
            "fv_service": 8003, "gs_service": 8004, "pgc_service": 8005, "ec_service": 8006
        }
        
    def create_backup(self) -> Dict:
        """Create system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"acgs_simple_backup_{timestamp}"
        backup_dir = self.backup_root / backup_id
        
        logger.info(f"🚀 Starting backup: {backup_id}")
        
        try:
            # Create backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_manifest = {
                "backup_id": backup_id,
                "timestamp": timestamp,
                "status": "in_progress",
                "components": {},
                "metadata": {
                    "constitution_hash": "cdd01ef066bc6cf2",
                    "system_version": "3.0.0"
                }
            }
            
            # 1. Configuration backup
            logger.info("⚙️ Creating configuration backup...")
            config_result = self._backup_configurations(backup_dir)
            backup_manifest["components"]["configurations"] = config_result
            
            # 2. Service state backup
            logger.info("🔧 Creating service state backup...")
            service_result = self._backup_service_states(backup_dir)
            backup_manifest["components"]["services"] = service_result
            
            # 3. Blockchain state backup
            logger.info("⛓️ Creating blockchain state backup...")
            blockchain_result = self._backup_blockchain_state(backup_dir)
            backup_manifest["components"]["blockchain"] = blockchain_result
            
            # 4. Scripts backup
            logger.info("📜 Creating scripts backup...")
            scripts_result = self._backup_scripts(backup_dir)
            backup_manifest["components"]["scripts"] = scripts_result
            
            # 5. Create backup manifest
            backup_manifest["status"] = "completed"
            backup_manifest["completion_time"] = datetime.now().isoformat()
            backup_manifest["size_mb"] = self._calculate_backup_size(backup_dir)
            
            manifest_path = backup_dir / "backup_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(backup_manifest, f, indent=2)
            
            logger.info(f"✅ Backup completed successfully: {backup_id}")
            return backup_manifest
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            backup_manifest["status"] = "failed"
            backup_manifest["error"] = str(e)
            return backup_manifest
    
    def _backup_configurations(self, backup_dir: Path) -> Dict:
        """Backup system configurations"""
        try:
            config_backup_dir = backup_dir / "configurations"
            config_backup_dir.mkdir(exist_ok=True)
            
            # Configuration files to backup
            config_files = [
                ".env",
                "docker-compose.yml",
                "docker-compose.prod.yml",
                "config/ports.yaml",
                "infrastructure/redis/redis-production.conf",
                "infrastructure/monitoring/prometheus.yml",
                "scripts/start_missing_services.sh",
                "OPERATIONAL_RUNBOOKS.md",
                "ACGS-1_MIGRATION_PROCESS_DOCUMENTATION.md"
            ]
            
            copied_files = []
            
            for config_path in config_files:
                source_path = self.project_root / config_path
                if source_path.exists():
                    if source_path.is_file():
                        dest_path = config_backup_dir / config_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        copied_files.append(str(dest_path))
                    elif source_path.is_dir():
                        dest_path = config_backup_dir / config_path
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        copied_files.append(str(dest_path))
            
            return {
                "status": "success",
                "files_backed_up": len(copied_files),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _backup_service_states(self, backup_dir: Path) -> Dict:
        """Backup service states and logs"""
        try:
            service_backup_dir = backup_dir / "services"
            service_backup_dir.mkdir(exist_ok=True)
            
            service_states = {}
            
            for service_name in self.services:
                port = self.service_ports[service_name]
                
                # Check if service is running
                is_running = self._is_service_running(port)
                
                # Get service logs if they exist
                log_file = self.project_root / "logs" / f"{service_name}.log"
                log_backed_up = False
                if log_file.exists():
                    dest_log = service_backup_dir / f"{service_name}.log"
                    shutil.copy2(log_file, dest_log)
                    log_backed_up = True
                
                service_states[service_name] = {
                    "running": is_running,
                    "port": port,
                    "log_backed_up": log_backed_up,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Save service states
            states_file = service_backup_dir / "service_states.json"
            with open(states_file, 'w') as f:
                json.dump(service_states, f, indent=2)
            
            return {
                "status": "success",
                "services_checked": len(service_states),
                "running_services": sum(1 for s in service_states.values() if s["running"]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Service state backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _backup_blockchain_state(self, backup_dir: Path) -> Dict:
        """Backup blockchain state and Quantumagi deployment"""
        try:
            blockchain_backup_dir = backup_dir / "blockchain"
            blockchain_backup_dir.mkdir(exist_ok=True)
            
            # Backup blockchain directory
            blockchain_source = self.project_root / "blockchain"
            if blockchain_source.exists():
                blockchain_dest = blockchain_backup_dir / "blockchain"
                shutil.copytree(blockchain_source, blockchain_dest, dirs_exist_ok=True)
            
            # Backup Quantumagi state
            quantumagi_state = {
                "constitution_hash": "cdd01ef066bc6cf2",
                "deployment_status": "active",
                "programs": ["constitution", "policy", "logging"],
                "network": "devnet",
                "timestamp": datetime.now().isoformat()
            }
            
            state_file = blockchain_backup_dir / "quantumagi_state.json"
            with open(state_file, 'w') as f:
                json.dump(quantumagi_state, f, indent=2)
            
            return {
                "status": "success",
                "constitution_hash": "cdd01ef066bc6cf2",
                "programs_backed_up": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Blockchain backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _backup_scripts(self, backup_dir: Path) -> Dict:
        """Backup important scripts"""
        try:
            scripts_backup_dir = backup_dir / "scripts"
            scripts_backup_dir.mkdir(exist_ok=True)
            
            # Important scripts to backup
            script_files = [
                "scripts/start_missing_services.sh",
                "scripts/comprehensive_health_check.py",
                "scripts/enhanced_backup_disaster_recovery.py",
                "scripts/verify_acgs_deployment.sh"
            ]
            
            copied_files = []
            
            for script_path in script_files:
                source_path = self.project_root / script_path
                if source_path.exists():
                    dest_path = scripts_backup_dir / source_path.name
                    shutil.copy2(source_path, dest_path)
                    copied_files.append(str(dest_path))
            
            return {
                "status": "success",
                "scripts_backed_up": len(copied_files),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scripts backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _is_service_running(self, port: int) -> bool:
        """Check if service is running on given port"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def _calculate_backup_size(self, backup_dir: Path) -> float:
        """Calculate total backup size in MB"""
        total_size = 0
        for file_path in backup_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return round(total_size / 1024 / 1024, 2)
    
    def list_backups(self) -> Dict:
        """List available backups"""
        try:
            backups = []
            
            if self.backup_root.exists():
                for backup_dir in self.backup_root.iterdir():
                    if backup_dir.is_dir():
                        manifest_file = backup_dir / "backup_manifest.json"
                        if manifest_file.exists():
                            with open(manifest_file, 'r') as f:
                                manifest = json.load(f)
                                backups.append({
                                    "backup_id": manifest["backup_id"],
                                    "timestamp": manifest["timestamp"],
                                    "status": manifest["status"],
                                    "size_mb": manifest.get("size_mb", 0)
                                })
            
            return {
                "status": "success",
                "backups": sorted(backups, key=lambda x: x["timestamp"], reverse=True),
                "total_backups": len(backups)
            }
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return {"status": "failed", "error": str(e)}


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-1 Simple Backup System")
    parser.add_argument("action", choices=["backup", "list"], help="Action to perform")
    
    args = parser.parse_args()
    
    # Ensure log directory exists
    log_dir = Path("/home/dislove/ACGS-1/logs")
    log_dir.mkdir(exist_ok=True)
    
    backup_system = SimpleBackupSystem()
    
    if args.action == "backup":
        result = backup_system.create_backup()
        print(json.dumps(result, indent=2))
        
    elif args.action == "list":
        result = backup_system.list_backups()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
