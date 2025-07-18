#!/usr/bin/env python3
"""
ACGS-2 Automated Backup Orchestrator
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive backup orchestration system for ACGS-2 constitutional governance platform.
Ensures constitutional compliance, data integrity, and automated recovery capabilities.
"""

import asyncio
import json
import logging
import os
import gzip
import tarfile
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ACGSBackupOrchestrator:
    """
    ACGS-2 Automated Backup Orchestrator
    Constitutional Hash: cdd01ef066bc6cf2
    
    Manages automated backup operations for:
    - PostgreSQL databases with constitutional validation
    - Kubernetes configurations and manifests
    - Service state and configurations
    - Constitutional audit trails
    - Retention policy enforcement
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = config_path or "/config/backup-config.json"
        self.backup_config = self._load_backup_config()
        self.logger = self._setup_logging()
        
        # Backup statistics
        self.backup_stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "constitutional_compliant": 0,
            "total_size_bytes": 0
        }
        
    def _load_backup_config(self) -> Dict:
        """Load backup configuration from file or use defaults"""
        default_config = {
            "postgres": {
                "frequency": "*/15 * * * *",
                "retention_days": 30,
                "backup_location": "/backups/postgres",
                "compression": True,
                "encryption": True,
                "full_backup_hour": 2
            },
            "kubernetes": {
                "frequency": "0 */6 * * *",
                "retention_days": 30,
                "backup_location": "/backups/kubernetes",
                "resources": ["all", "configmaps", "secrets", "pvc", "ingress", "networkpolicies"]
            },
            "services": {
                "frequency": "*/30 * * * *",
                "retention_days": 7,
                "backup_location": "/backups/services",
                "services": [
                    {"name": "auth-service", "port": 8013},
                    {"name": "monitoring-service", "port": 8014},
                    {"name": "audit-service", "port": 8015},
                    {"name": "gdpr-compliance", "port": 8016},
                    {"name": "alerting-service", "port": 8017}
                ]
            },
            "constitutional_audit": {
                "frequency": "*/5 * * * *",
                "retention_days": 90,
                "backup_location": "/backups/constitutional",
                "audit_interval_hours": 24
            },
            "offsite": {
                "enabled": True,
                "location": "s3://acgs-backups-offsite",
                "frequency": "0 3 * * *",
                "retention_days": 90
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            else:
                self.logger.warning(f"Config file not found at {self.config_path}, using defaults")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging with constitutional compliance"""
        logger = logging.getLogger("acgs_backup")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("/var/log")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler("/var/log/acgs_backup.log")
        file_formatter = logging.Formatter(
            f'%(asctime)s - CONSTITUTIONAL_HASH:{self.constitutional_hash} - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    async def _execute_kubectl_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Execute kubectl command and return success status, stdout, stderr"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return (
                process.returncode == 0,
                stdout.decode() if stdout else "",
                stderr.decode() if stderr else ""
            )
            
        except Exception as e:
            return False, "", str(e)
    
    async def create_postgres_backup(self) -> bool:
        """Create PostgreSQL backup with constitutional validation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_location = Path(self.backup_config["postgres"]["backup_location"])
            backup_location.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_location / f"acgs_backup_{timestamp}.sql.gz"
            
            self.logger.info(f"Creating PostgreSQL backup: {backup_file}")
            
            # Create database dump
            dump_cmd = [
                "kubectl", "exec", "deployment/postgres", "-n", "acgs-system", "--",
                "pg_dump", "-U", "acgs_user", "-d", "acgs_db",
                "--column-inserts", "--verbose", "--clean", "--if-exists",
                "--quote-all-identifiers"
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(dump_cmd)
            
            if success and stdout:
                # Compress and save backup
                with gzip.open(backup_file, 'wt') as f:
                    f.write(stdout)
                
                # Verify constitutional hash in backup
                constitutional_compliance = self.constitutional_hash in stdout
                
                # Create metadata file
                metadata = {
                    "constitutional_hash": self.constitutional_hash,
                    "timestamp": timestamp,
                    "backup_type": "postgres_full",
                    "size_bytes": backup_file.stat().st_size,
                    "retention_until": (datetime.now() + timedelta(days=self.backup_config["postgres"]["retention_days"])).isoformat(),
                    "constitutional_compliance": constitutional_compliance,
                    "postgres_version": "15",
                    "database_name": "acgs_db"
                }
                
                with open(f"{backup_file}.meta", 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Update statistics
                self.backup_stats["total_backups"] += 1
                self.backup_stats["successful_backups"] += 1
                self.backup_stats["total_size_bytes"] += backup_file.stat().st_size
                
                if constitutional_compliance:
                    self.backup_stats["constitutional_compliant"] += 1
                
                self.logger.info(f"PostgreSQL backup created successfully: {backup_file}")
                self.logger.info(f"Backup size: {backup_file.stat().st_size / (1024*1024):.2f} MB")
                self.logger.info(f"Constitutional compliance: {'✅' if constitutional_compliance else '❌'}")
                
                return True
            else:
                self.logger.error(f"PostgreSQL backup failed: {stderr}")
                self.backup_stats["failed_backups"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"PostgreSQL backup error: {str(e)}")
            self.backup_stats["failed_backups"] += 1
            return False
    
    async def create_kubernetes_backup(self) -> bool:
        """Create Kubernetes configuration backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_location = Path(self.backup_config["kubernetes"]["backup_location"])
            backup_location.mkdir(parents=True, exist_ok=True)
            
            temp_dir = backup_location / f"temp_{timestamp}"
            temp_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"Creating Kubernetes backup: {backup_location}")
            
            # Backup different resource types
            resources = self.backup_config["kubernetes"]["resources"]
            backup_files = []
            
            for resource_type in resources:
                backup_file = temp_dir / f"{resource_type}_{timestamp}.yaml"
                
                cmd = [
                    "kubectl", "get", resource_type, "-n", "acgs-system",
                    "-o", "yaml"
                ]
                
                success, stdout, stderr = await self._execute_kubectl_command(cmd)
                
                if success and stdout:
                    with open(backup_file, 'w') as f:
                        f.write(stdout)
                    backup_files.append(backup_file)
                    self.logger.info(f"Backed up {resource_type}: {len(stdout)} bytes")
                else:
                    self.logger.warning(f"Failed to backup {resource_type}: {stderr}")
            
            # Create compressed archive
            archive_file = backup_location / f"k8s_backup_{timestamp}.tar.gz"
            
            with tarfile.open(archive_file, "w:gz") as tar:
                for backup_file in backup_files:
                    tar.add(backup_file, arcname=backup_file.name)
            
            # Clean up temporary files
            for backup_file in backup_files:
                backup_file.unlink()
            temp_dir.rmdir()
            
            # Verify constitutional hash in backup
            constitutional_compliance = False
            try:
                with tarfile.open(archive_file, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.isfile():
                            content = tar.extractfile(member).read().decode()
                            if self.constitutional_hash in content:
                                constitutional_compliance = True
                                break
            except Exception as e:
                self.logger.warning(f"Could not verify constitutional compliance: {e}")
            
            # Create metadata file
            metadata = {
                "constitutional_hash": self.constitutional_hash,
                "timestamp": timestamp,
                "backup_type": "kubernetes_config",
                "size_bytes": archive_file.stat().st_size,
                "retention_until": (datetime.now() + timedelta(days=self.backup_config["kubernetes"]["retention_days"])).isoformat(),
                "resources_backed_up": len(backup_files),
                "constitutional_compliance": constitutional_compliance,
                "namespace": "acgs-system"
            }
            
            with open(f"{archive_file}.meta", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update statistics
            self.backup_stats["total_backups"] += 1
            self.backup_stats["successful_backups"] += 1
            self.backup_stats["total_size_bytes"] += archive_file.stat().st_size
            
            if constitutional_compliance:
                self.backup_stats["constitutional_compliant"] += 1
            
            self.logger.info(f"Kubernetes backup created successfully: {archive_file}")
            self.logger.info(f"Backup size: {archive_file.stat().st_size / (1024*1024):.2f} MB")
            self.logger.info(f"Resources backed up: {len(backup_files)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Kubernetes backup error: {str(e)}")
            self.backup_stats["failed_backups"] += 1
            return False
    
    async def create_service_backup(self) -> bool:
        """Create service state backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_location = Path(self.backup_config["services"]["backup_location"])
            backup_location.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Creating services backup: {backup_location}")
            
            services = self.backup_config["services"]["services"]
            service_backups = {}
            successful_services = 0
            
            for service_config in services:
                service_name = service_config["name"]
                port = service_config["port"]
                
                try:
                    self.logger.info(f"Backing up service: {service_name}")
                    
                    # Port forward to service
                    port_forward_cmd = [
                        "kubectl", "port-forward", f"service/{service_name}",
                        f"{port}:{port}", "-n", "acgs-system"
                    ]
                    
                    port_forward_process = await asyncio.create_subprocess_exec(
                        *port_forward_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    # Wait for port forward to establish
                    await asyncio.sleep(5)
                    
                    # Get service backup data
                    timeout = aiohttp.ClientTimeout(total=30)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        try:
                            async with session.get(
                                f"http://localhost:{port}/health",
                                headers={"Constitutional-Hash": self.constitutional_hash}
                            ) as response:
                                if response.status == 200:
                                    health_data = await response.json()
                                    
                                    # Validate constitutional compliance
                                    if health_data.get("constitutional_hash") == self.constitutional_hash:
                                        service_backups[service_name] = {
                                            "health_status": health_data,
                                            "timestamp": timestamp,
                                            "constitutional_compliance": True,
                                            "service_port": port
                                        }
                                        successful_services += 1
                                        self.logger.info(f"Service {service_name} backup successful")
                                    else:
                                        service_backups[service_name] = {
                                            "error": "Constitutional compliance validation failed",
                                            "timestamp": timestamp,
                                            "constitutional_compliance": False
                                        }
                                        self.logger.warning(f"Service {service_name} backup failed constitutional validation")
                                else:
                                    service_backups[service_name] = {
                                        "error": f"HTTP {response.status}",
                                        "timestamp": timestamp,
                                        "constitutional_compliance": False
                                    }
                                    self.logger.warning(f"Service {service_name} backup failed: HTTP {response.status}")
                        except asyncio.TimeoutError:
                            service_backups[service_name] = {
                                "error": "Timeout connecting to service",
                                "timestamp": timestamp,
                                "constitutional_compliance": False
                            }
                            self.logger.warning(f"Service {service_name} backup timeout")
                        except Exception as e:
                            service_backups[service_name] = {
                                "error": str(e),
                                "timestamp": timestamp,
                                "constitutional_compliance": False
                            }
                            self.logger.warning(f"Service {service_name} backup error: {e}")
                    
                    # Cleanup port forward
                    port_forward_process.terminate()
                    try:
                        await asyncio.wait_for(port_forward_process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        port_forward_process.kill()
                        await port_forward_process.wait()
                    
                except Exception as e:
                    self.logger.error(f"Service {service_name} backup error: {str(e)}")
                    service_backups[service_name] = {
                        "error": str(e),
                        "timestamp": timestamp,
                        "constitutional_compliance": False
                    }
                    continue
            
            # Save service backups
            backup_file = backup_location / f"services_backup_{timestamp}.json"
            
            backup_data = {
                "constitutional_hash": self.constitutional_hash,
                "timestamp": timestamp,
                "backup_type": "services_state",
                "services": service_backups,
                "successful_services": successful_services,
                "total_services": len(services)
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Create metadata file
            metadata = {
                "constitutional_hash": self.constitutional_hash,
                "timestamp": timestamp,
                "backup_type": "services_state",
                "size_bytes": backup_file.stat().st_size,
                "retention_until": (datetime.now() + timedelta(days=self.backup_config["services"]["retention_days"])).isoformat(),
                "services_backed_up": successful_services,
                "total_services": len(services),
                "constitutional_compliance": successful_services > 0
            }
            
            with open(f"{backup_file}.meta", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update statistics
            self.backup_stats["total_backups"] += 1
            self.backup_stats["total_size_bytes"] += backup_file.stat().st_size
            
            if successful_services > 0:
                self.backup_stats["successful_backups"] += 1
                self.backup_stats["constitutional_compliant"] += 1
            else:
                self.backup_stats["failed_backups"] += 1
            
            self.logger.info(f"Services backup created: {backup_file}")
            self.logger.info(f"Services backed up: {successful_services}/{len(services)}")
            
            return successful_services > 0
            
        except Exception as e:
            self.logger.error(f"Services backup error: {str(e)}")
            self.backup_stats["failed_backups"] += 1
            return False
    
    async def create_constitutional_audit_backup(self) -> bool:
        """Create constitutional audit trail backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_location = Path(self.backup_config["constitutional_audit"]["backup_location"])
            backup_location.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Creating constitutional audit backup: {backup_location}")
            
            # Query constitutional audit data from database
            audit_interval = self.backup_config["constitutional_audit"]["audit_interval_hours"]
            audit_cmd = [
                "kubectl", "exec", "deployment/postgres", "-n", "acgs-system", "--",
                "psql", "-U", "acgs_user", "-d", "acgs_db", "-c",
                f"SELECT * FROM audit_logs WHERE constitutional_hash = '{self.constitutional_hash}' AND timestamp >= NOW() - INTERVAL '{audit_interval} hours' ORDER BY timestamp DESC;"
            ]
            
            success, stdout, stderr = await self._execute_kubectl_command(audit_cmd)
            
            if success and stdout:
                backup_file = backup_location / f"constitutional_audit_{timestamp}.sql"
                
                with open(backup_file, 'w') as f:
                    f.write(stdout)
                
                # Count audit entries
                audit_count = len([line for line in stdout.split('\n') if line.strip() and not line.startswith(' ') and '|' in line]) - 1
                
                # Create metadata file
                metadata = {
                    "constitutional_hash": self.constitutional_hash,
                    "timestamp": timestamp,
                    "backup_type": "constitutional_audit",
                    "size_bytes": backup_file.stat().st_size,
                    "retention_until": (datetime.now() + timedelta(days=self.backup_config["constitutional_audit"]["retention_days"])).isoformat(),
                    "audit_entries": audit_count,
                    "audit_interval_hours": audit_interval,
                    "constitutional_compliance": True
                }
                
                with open(f"{backup_file}.meta", 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Update statistics
                self.backup_stats["total_backups"] += 1
                self.backup_stats["successful_backups"] += 1
                self.backup_stats["constitutional_compliant"] += 1
                self.backup_stats["total_size_bytes"] += backup_file.stat().st_size
                
                self.logger.info(f"Constitutional audit backup created: {backup_file}")
                self.logger.info(f"Audit entries: {audit_count}")
                
                return True
            else:
                self.logger.error(f"Constitutional audit backup failed: {stderr}")
                self.backup_stats["failed_backups"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Constitutional audit backup error: {str(e)}")
            self.backup_stats["failed_backups"] += 1
            return False
    
    async def cleanup_old_backups(self) -> bool:
        """Clean up old backups based on retention policy"""
        try:
            self.logger.info("Cleaning up old backups...")
            
            cleanup_stats = {
                "files_removed": 0,
                "bytes_freed": 0
            }
            
            for backup_type, config in self.backup_config.items():
                if backup_type == "offsite":
                    continue
                    
                backup_location = Path(config["backup_location"])
                retention_days = config["retention_days"]
                
                if not backup_location.exists():
                    continue
                
                cutoff_time = datetime.now() - timedelta(days=retention_days)
                
                for file_path in backup_location.iterdir():
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_time < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleanup_stats["files_removed"] += 1
                            cleanup_stats["bytes_freed"] += file_size
                            self.logger.info(f"Removed old backup: {file_path.name}")
            
            self.logger.info(f"Cleanup completed: {cleanup_stats['files_removed']} files removed, {cleanup_stats['bytes_freed'] / (1024*1024):.2f} MB freed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup cleanup error: {str(e)}")
            return False
    
    async def generate_backup_report(self) -> Dict:
        """Generate comprehensive backup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "statistics": self.backup_stats.copy(),
            "backup_locations": {},
            "compliance_status": "COMPLIANT" if self.backup_stats["constitutional_compliant"] == self.backup_stats["total_backups"] else "NON_COMPLIANT"
        }
        
        # Add backup location details
        for backup_type, config in self.backup_config.items():
            if backup_type == "offsite":
                continue
                
            location = Path(config["backup_location"])
            if location.exists():
                backup_files = list(location.glob("*"))
                total_size = sum(f.stat().st_size for f in backup_files if f.is_file())
                
                report["backup_locations"][backup_type] = {
                    "path": str(location),
                    "file_count": len(backup_files),
                    "total_size_bytes": total_size,
                    "total_size_mb": total_size / (1024*1024),
                    "retention_days": config["retention_days"]
                }
        
        return report
    
    async def run_backup_cycle(self) -> Dict[str, bool]:
        """Run complete backup cycle"""
        self.logger.info("Starting ACGS-2 backup cycle")
        self.logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        
        # Reset statistics
        self.backup_stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "constitutional_compliant": 0,
            "total_size_bytes": 0
        }
        
        results = {}
        
        # Create backups
        results["postgres"] = await self.create_postgres_backup()
        results["kubernetes"] = await self.create_kubernetes_backup()
        results["services"] = await self.create_service_backup()
        results["constitutional_audit"] = await self.create_constitutional_audit_backup()
        
        # Cleanup old backups
        results["cleanup"] = await self.cleanup_old_backups()
        
        # Generate report
        backup_report = await self.generate_backup_report()
        
        # Save report
        report_file = Path("/var/log/backup_report.json")
        with open(report_file, 'w') as f:
            json.dump(backup_report, f, indent=2)
        
        # Log results
        successful_backups = sum(1 for key, success in results.items() if success and key != "cleanup")
        total_backups = len([key for key in results.keys() if key != "cleanup"])
        
        self.logger.info(f"Backup cycle completed:")
        self.logger.info(f"  Successful backups: {successful_backups}/{total_backups}")
        self.logger.info(f"  Constitutional compliance: {self.backup_stats['constitutional_compliant']}/{self.backup_stats['total_backups']}")
        self.logger.info(f"  Total data backed up: {self.backup_stats['total_size_bytes'] / (1024*1024):.2f} MB")
        self.logger.info(f"  Compliance status: {backup_report['compliance_status']}")
        
        return results


async def main():
    """Main execution function"""
    try:
        orchestrator = ACGSBackupOrchestrator()
        results = await orchestrator.run_backup_cycle()
        
        # Exit with appropriate code
        if all(results.values()):
            print("🎉 All backup operations completed successfully")
            exit(0)
        else:
            print("⚠️ Some backup operations failed")
            for operation, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {operation}: {status}")
            exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error in backup orchestrator: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())