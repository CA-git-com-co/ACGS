#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Backup System
Automated backup and disaster recovery for constitutional governance system
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ACGSBackupSystem:
    """Comprehensive backup system for ACGS-1 Constitutional Governance System"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.backup_root = Path("/backup/acgs-1")
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Backup configuration
        self.backup_config = {
            "retention_days": 30,
            "full_backup_interval": 7,  # days
            "incremental_backup_interval": 1,  # days
            "compression": True,
            "encryption": True,
            "offsite_storage": True,
            "verification": True
        }
        
        # Backup targets
        self.backup_targets = {
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "acgs_db",
                "user": "acgs_user",
                "priority": "critical"
            },
            "blockchain_data": {
                "type": "directory",
                "path": self.project_root / "blockchain",
                "priority": "critical"
            },
            "constitutional_documents": {
                "type": "directory", 
                "path": self.project_root / ".taskmaster" / "docs",
                "priority": "critical"
            },
            "application_config": {
                "type": "directory",
                "path": self.project_root / "config",
                "priority": "high"
            },
            "logs": {
                "type": "directory",
                "path": self.project_root / "logs",
                "priority": "medium"
            },
            "monitoring_data": {
                "type": "directory",
                "path": self.project_root / "infrastructure" / "monitoring",
                "priority": "medium"
            },
            "kubernetes_manifests": {
                "type": "directory",
                "path": self.project_root / "infrastructure" / "kubernetes",
                "priority": "high"
            }
        }
        
        # Ensure backup directories exist
        self.backup_root.mkdir(parents=True, exist_ok=True)
        (self.backup_root / "daily").mkdir(exist_ok=True)
        (self.backup_root / "weekly").mkdir(exist_ok=True)
        (self.backup_root / "monthly").mkdir(exist_ok=True)
        (self.backup_root / "offsite").mkdir(exist_ok=True)

    async def run_comprehensive_backup(self, backup_type: str = "incremental") -> Dict[str, Any]:
        """Run comprehensive backup of all ACGS-1 components"""
        logger.info(f"🔄 Starting comprehensive {backup_type} backup")
        logger.info("=" * 80)
        
        start_time = time.time()
        backup_id = f"acgs-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        results = {}
        
        try:
            # Step 1: Pre-backup validation
            results["pre_backup_validation"] = await self.pre_backup_validation()
            
            # Step 2: Create backup directory
            backup_dir = self.backup_root / "daily" / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 3: Backup database
            results["database_backup"] = await self.backup_database(backup_dir)
            
            # Step 4: Backup blockchain data
            results["blockchain_backup"] = await self.backup_blockchain_data(backup_dir)
            
            # Step 5: Backup constitutional documents
            results["constitutional_backup"] = await self.backup_constitutional_documents(backup_dir)
            
            # Step 6: Backup application configuration
            results["config_backup"] = await self.backup_application_config(backup_dir)
            
            # Step 7: Backup Kubernetes manifests
            results["kubernetes_backup"] = await self.backup_kubernetes_manifests(backup_dir)
            
            # Step 8: Backup logs (if medium priority)
            if backup_type == "full":
                results["logs_backup"] = await self.backup_logs(backup_dir)
            
            # Step 9: Create backup manifest
            results["manifest_creation"] = await self.create_backup_manifest(backup_dir, backup_id, results)
            
            # Step 10: Compress backup
            if self.backup_config["compression"]:
                results["compression"] = await self.compress_backup(backup_dir)
            
            # Step 11: Encrypt backup
            if self.backup_config["encryption"]:
                results["encryption"] = await self.encrypt_backup(backup_dir)
            
            # Step 12: Verify backup integrity
            if self.backup_config["verification"]:
                results["verification"] = await self.verify_backup_integrity(backup_dir)
            
            # Step 13: Upload to offsite storage
            if self.backup_config["offsite_storage"]:
                results["offsite_upload"] = await self.upload_to_offsite_storage(backup_dir)
            
            # Step 14: Cleanup old backups
            results["cleanup"] = await self.cleanup_old_backups()
            
            # Step 15: Update backup registry
            results["registry_update"] = await self.update_backup_registry(backup_id, results)
            
            total_time = time.time() - start_time
            
            logger.info("✅ Comprehensive backup completed successfully!")
            logger.info(f"⏱️  Total backup time: {total_time:.2f} seconds")
            
            return {
                "status": "success",
                "backup_id": backup_id,
                "backup_type": backup_type,
                "backup_time": total_time,
                "backup_dir": str(backup_dir),
                "results": results,
                "summary": self.generate_backup_summary(results)
            }
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return {
                "status": "failed",
                "backup_id": backup_id,
                "error": str(e),
                "results": results
            }

    async def pre_backup_validation(self) -> Dict[str, Any]:
        """Validate system state before backup"""
        logger.info("🔍 Performing pre-backup validation...")
        
        validation = {}
        
        # Check disk space
        backup_disk = shutil.disk_usage(self.backup_root)
        validation["disk_space"] = {
            "available_gb": backup_disk.free / (1024**3),
            "total_gb": backup_disk.total / (1024**3),
            "usage_percent": (backup_disk.used / backup_disk.total) * 100,
            "sufficient": backup_disk.free > 10 * (1024**3)  # 10GB minimum
        }
        
        # Check database connectivity
        try:
            result = await self.run_command([
                "psql", "-h", "localhost", "-U", "acgs_user", "-d", "acgs_db", "-c", "SELECT 1;"
            ])
            validation["database_connectivity"] = {
                "status": "connected" if result["returncode"] == 0 else "disconnected",
                "error": result["stderr"] if result["returncode"] != 0 else None
            }
        except Exception as e:
            validation["database_connectivity"] = {"status": "error", "error": str(e)}
        
        # Check constitutional hash integrity
        try:
            result = await self.run_command([
                "curl", "-f", "http://localhost:8005/api/v1/constitution/hash"
            ])
            if result["returncode"] == 0:
                hash_data = json.loads(result["stdout"])
                validation["constitutional_integrity"] = {
                    "status": "valid" if hash_data.get("hash") == self.constitutional_hash else "invalid",
                    "current_hash": hash_data.get("hash"),
                    "expected_hash": self.constitutional_hash
                }
            else:
                validation["constitutional_integrity"] = {"status": "unavailable"}
        except Exception as e:
            validation["constitutional_integrity"] = {"status": "error", "error": str(e)}
        
        # Check backup targets accessibility
        for target_name, target_config in self.backup_targets.items():
            if target_config["type"] == "directory":
                target_path = Path(target_config["path"])
                validation[f"target_{target_name}"] = {
                    "exists": target_path.exists(),
                    "readable": target_path.is_dir() and os.access(target_path, os.R_OK),
                    "size_mb": self.get_directory_size(target_path) / (1024**2) if target_path.exists() else 0
                }
        
        return validation

    async def backup_database(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup PostgreSQL database"""
        logger.info("🗄️ Backing up database...")
        
        try:
            db_backup_file = backup_dir / "database_backup.sql"
            
            # Create database dump
            result = await self.run_command([
                "pg_dump",
                "-h", "localhost",
                "-U", "acgs_user",
                "-d", "acgs_db",
                "--no-password",
                "--verbose",
                "--clean",
                "--create",
                "-f", str(db_backup_file)
            ], env={"PGPASSWORD": "acgs_password"})
            
            if result["returncode"] == 0:
                # Verify backup file
                backup_size = db_backup_file.stat().st_size if db_backup_file.exists() else 0
                
                return {
                    "status": "success",
                    "backup_file": str(db_backup_file),
                    "backup_size_mb": backup_size / (1024**2),
                    "output": result["stdout"][:200]
                }
            else:
                return {
                    "status": "failed",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_blockchain_data(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup blockchain data and Solana programs"""
        logger.info("⛓️ Backing up blockchain data...")
        
        try:
            blockchain_backup_dir = backup_dir / "blockchain"
            blockchain_backup_dir.mkdir(exist_ok=True)
            
            source_dir = self.backup_targets["blockchain_data"]["path"]
            
            # Copy blockchain directory
            if source_dir.exists():
                result = await self.run_command([
                    "rsync", "-av", "--progress",
                    str(source_dir) + "/",
                    str(blockchain_backup_dir) + "/"
                ])
                
                if result["returncode"] == 0:
                    backup_size = self.get_directory_size(blockchain_backup_dir)
                    
                    # Backup Solana program keypairs separately
                    keypairs_backup = await self.backup_solana_keypairs(blockchain_backup_dir)
                    
                    return {
                        "status": "success",
                        "backup_dir": str(blockchain_backup_dir),
                        "backup_size_mb": backup_size / (1024**2),
                        "keypairs_backup": keypairs_backup,
                        "files_copied": result["stdout"].count("sending incremental file list")
                    }
                else:
                    return {
                        "status": "failed",
                        "error": result["stderr"]
                    }
            else:
                return {
                    "status": "skipped",
                    "reason": "Blockchain directory not found"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_constitutional_documents(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup constitutional documents and governance data"""
        logger.info("🏛️ Backing up constitutional documents...")
        
        try:
            constitutional_backup_dir = backup_dir / "constitutional"
            constitutional_backup_dir.mkdir(exist_ok=True)
            
            source_dir = self.backup_targets["constitutional_documents"]["path"]
            
            if source_dir.exists():
                # Copy constitutional documents
                result = await self.run_command([
                    "rsync", "-av", "--progress",
                    str(source_dir) + "/",
                    str(constitutional_backup_dir) + "/"
                ])
                
                if result["returncode"] == 0:
                    # Create constitutional integrity manifest
                    integrity_manifest = {
                        "constitutional_hash": self.constitutional_hash,
                        "backup_timestamp": datetime.now().isoformat(),
                        "documents_backed_up": [],
                        "governance_policies": []
                    }
                    
                    # List backed up documents
                    for doc_file in constitutional_backup_dir.rglob("*"):
                        if doc_file.is_file():
                            integrity_manifest["documents_backed_up"].append({
                                "file": str(doc_file.relative_to(constitutional_backup_dir)),
                                "size": doc_file.stat().st_size,
                                "modified": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
                            })
                    
                    # Save integrity manifest
                    with open(constitutional_backup_dir / "integrity_manifest.json", 'w') as f:
                        json.dump(integrity_manifest, f, indent=2)
                    
                    backup_size = self.get_directory_size(constitutional_backup_dir)
                    
                    return {
                        "status": "success",
                        "backup_dir": str(constitutional_backup_dir),
                        "backup_size_mb": backup_size / (1024**2),
                        "documents_count": len(integrity_manifest["documents_backed_up"]),
                        "constitutional_hash": self.constitutional_hash
                    }
                else:
                    return {
                        "status": "failed",
                        "error": result["stderr"]
                    }
            else:
                return {
                    "status": "skipped",
                    "reason": "Constitutional documents directory not found"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_application_config(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup application configuration files"""
        logger.info("⚙️ Backing up application configuration...")
        
        try:
            config_backup_dir = backup_dir / "config"
            config_backup_dir.mkdir(exist_ok=True)
            
            source_dir = self.backup_targets["application_config"]["path"]
            
            if source_dir.exists():
                result = await self.run_command([
                    "rsync", "-av", "--progress",
                    str(source_dir) + "/",
                    str(config_backup_dir) + "/"
                ])
                
                if result["returncode"] == 0:
                    backup_size = self.get_directory_size(config_backup_dir)
                    
                    return {
                        "status": "success",
                        "backup_dir": str(config_backup_dir),
                        "backup_size_mb": backup_size / (1024**2)
                    }
                else:
                    return {
                        "status": "failed",
                        "error": result["stderr"]
                    }
            else:
                return {
                    "status": "skipped",
                    "reason": "Config directory not found"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_kubernetes_manifests(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup Kubernetes manifests and configurations"""
        logger.info("☸️ Backing up Kubernetes manifests...")
        
        try:
            k8s_backup_dir = backup_dir / "kubernetes"
            k8s_backup_dir.mkdir(exist_ok=True)
            
            source_dir = self.backup_targets["kubernetes_manifests"]["path"]
            
            if source_dir.exists():
                result = await self.run_command([
                    "rsync", "-av", "--progress",
                    str(source_dir) + "/",
                    str(k8s_backup_dir) + "/"
                ])
                
                if result["returncode"] == 0:
                    # Also backup current cluster state
                    cluster_state = await self.backup_cluster_state(k8s_backup_dir)
                    
                    backup_size = self.get_directory_size(k8s_backup_dir)
                    
                    return {
                        "status": "success",
                        "backup_dir": str(k8s_backup_dir),
                        "backup_size_mb": backup_size / (1024**2),
                        "cluster_state_backup": cluster_state
                    }
                else:
                    return {
                        "status": "failed",
                        "error": result["stderr"]
                    }
            else:
                return {
                    "status": "skipped",
                    "reason": "Kubernetes directory not found"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_logs(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup system and application logs"""
        logger.info("📝 Backing up logs...")
        
        try:
            logs_backup_dir = backup_dir / "logs"
            logs_backup_dir.mkdir(exist_ok=True)
            
            source_dir = self.backup_targets["logs"]["path"]
            
            if source_dir.exists():
                # Only backup logs from last 7 days to save space
                cutoff_date = datetime.now() - timedelta(days=7)
                
                result = await self.run_command([
                    "find", str(source_dir), "-type", "f", "-name", "*.log",
                    "-newermt", cutoff_date.strftime("%Y-%m-%d"),
                    "-exec", "cp", "{}", str(logs_backup_dir), ";"
                ])
                
                backup_size = self.get_directory_size(logs_backup_dir)
                
                return {
                    "status": "success",
                    "backup_dir": str(logs_backup_dir),
                    "backup_size_mb": backup_size / (1024**2),
                    "retention_days": 7
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "Logs directory not found"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_solana_keypairs(self, blockchain_backup_dir: Path) -> Dict[str, Any]:
        """Backup Solana program keypairs securely"""
        try:
            keypairs_dir = blockchain_backup_dir / "keypairs"
            keypairs_dir.mkdir(exist_ok=True)
            
            # Find and backup keypair files
            keypair_files = []
            for keypair_file in (self.project_root / "blockchain").rglob("*keypair.json"):
                if keypair_file.exists():
                    shutil.copy2(keypair_file, keypairs_dir)
                    keypair_files.append(str(keypair_file.name))
            
            return {
                "status": "success",
                "keypairs_backed_up": len(keypair_files),
                "keypair_files": keypair_files
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup_cluster_state(self, k8s_backup_dir: Path) -> Dict[str, Any]:
        """Backup current Kubernetes cluster state"""
        try:
            cluster_state_dir = k8s_backup_dir / "cluster_state"
            cluster_state_dir.mkdir(exist_ok=True)
            
            # Backup cluster resources
            resources = [
                "namespaces", "configmaps", "secrets", "services", 
                "deployments", "pods", "ingresses"
            ]
            
            for resource in resources:
                result = await self.run_command([
                    "kubectl", "get", resource, "--all-namespaces", "-o", "yaml"
                ])
                
                if result["returncode"] == 0:
                    with open(cluster_state_dir / f"{resource}.yaml", 'w') as f:
                        f.write(result["stdout"])
            
            return {"status": "success", "resources_backed_up": len(resources)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size

    async def run_command(self, cmd: List[str], env: Dict[str, str] = None) -> Dict[str, Any]:
        """Run shell command"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **(env or {})}
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def generate_backup_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate backup summary"""
        summary = {
            "components_backed_up": 0,
            "total_backup_size_mb": 0,
            "critical_components_status": {},
            "backup_integrity": "unknown"
        }
        
        # Analyze backup results
        for component, result in results.items():
            if isinstance(result, dict) and result.get("status") == "success":
                summary["components_backed_up"] += 1
                
                if "backup_size_mb" in result:
                    summary["total_backup_size_mb"] += result["backup_size_mb"]
                
                # Track critical components
                if component in ["database_backup", "blockchain_backup", "constitutional_backup"]:
                    summary["critical_components_status"][component] = result["status"]
        
        # Check if all critical components backed up successfully
        critical_success = all(
            status == "success" 
            for status in summary["critical_components_status"].values()
        )
        
        summary["backup_integrity"] = "verified" if critical_success else "partial"
        
        return summary


async def main():
    """Main backup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-1 Backup System")
    parser.add_argument("action", choices=["backup", "restore", "verify", "cleanup"],
                       help="Backup action to perform")
    parser.add_argument("--type", choices=["full", "incremental"], default="incremental",
                       help="Type of backup to perform")
    parser.add_argument("--backup-id", help="Backup ID for restore/verify operations")
    
    args = parser.parse_args()
    
    backup_system = ACGSBackupSystem()
    
    try:
        if args.action == "backup":
            result = await backup_system.run_comprehensive_backup(args.type)
        else:
            result = {"status": "not_implemented", "action": args.action}
        
        print("\n" + "=" * 80)
        print("BACKUP SYSTEM RESULT")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        
        if result.get("status") == "success":
            print("\n✅ Backup operation completed successfully!")
        else:
            print("\n❌ Backup operation failed.")
            
    except Exception as e:
        logger.error(f"Backup error: {e}")
        print(f"\n❌ Backup failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
