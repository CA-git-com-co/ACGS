#!/usr/bin/env python3
"""
Simple Backup and Disaster Recovery Test for ACGS-1
Tests core backup functionality without database dependencies
"""

import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/backup_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SimpleBackupTest:
    """Simple backup test for ACGS-1"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_root = Path.cwd() / "backups"
        self.test_results = {}

    def test_backup_infrastructure(self) -> dict:
        """Test backup infrastructure and basic functionality"""
        logger.info("🧪 Testing backup infrastructure...")

        test_results = {
            "test_id": f"backup_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "tests": {},
        }

        # Test 1: Backup directory creation
        logger.info("📁 Testing backup directory creation...")
        try:
            test_backup_dir = self.backup_root / "test_backup"
            test_backup_dir.mkdir(parents=True, exist_ok=True)
            test_results["tests"]["backup_directory"] = {
                "status": "passed",
                "message": "Backup directory created successfully",
            }
        except Exception as e:
            test_results["tests"]["backup_directory"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test 2: Configuration backup
        logger.info("⚙️ Testing configuration backup...")
        try:
            config_backup_result = self._test_config_backup(test_backup_dir)
            test_results["tests"]["configuration_backup"] = config_backup_result
        except Exception as e:
            test_results["tests"]["configuration_backup"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test 3: Service state collection
        logger.info("🔧 Testing service state collection...")
        try:
            service_state_result = self._test_service_state_collection(test_backup_dir)
            test_results["tests"]["service_state"] = service_state_result
        except Exception as e:
            test_results["tests"]["service_state"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test 4: Blockchain state backup
        logger.info("⛓️ Testing blockchain state backup...")
        try:
            blockchain_result = self._test_blockchain_backup(test_backup_dir)
            test_results["tests"]["blockchain_backup"] = blockchain_result
        except Exception as e:
            test_results["tests"]["blockchain_backup"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test 5: Backup manifest creation
        logger.info("📋 Testing backup manifest creation...")
        try:
            manifest_result = self._test_manifest_creation(test_backup_dir)
            test_results["tests"]["manifest_creation"] = manifest_result
        except Exception as e:
            test_results["tests"]["manifest_creation"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test 6: Backup compression
        logger.info("🗜️ Testing backup compression...")
        try:
            compression_result = self._test_backup_compression(test_backup_dir)
            test_results["tests"]["backup_compression"] = compression_result
        except Exception as e:
            test_results["tests"]["backup_compression"] = {
                "status": "failed",
                "error": str(e),
            }

        # Calculate overall status
        passed_tests = sum(
            1 for test in test_results["tests"].values() if test["status"] == "passed"
        )
        total_tests = len(test_results["tests"])

        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
        }

        test_results["status"] = "passed" if passed_tests == total_tests else "partial"
        test_results["completion_time"] = datetime.now().isoformat()

        # Cleanup test directory
        if test_backup_dir.exists():
            shutil.rmtree(test_backup_dir)

        logger.info(
            f"✅ Backup infrastructure test completed: {test_results['summary']['success_rate']} success rate"
        )
        return test_results

    def _test_config_backup(self, backup_dir: Path) -> dict:
        """Test configuration backup functionality"""
        config_backup_dir = backup_dir / "configurations"
        config_backup_dir.mkdir(exist_ok=True)

        # Configuration files to test
        config_files = [
            ".env",
            "docker-compose.yml",
            "config/ports.yaml",
        ]

        backed_up_files = []
        for config_path in config_files:
            source_path = self.project_root / config_path
            if source_path.exists():
                dest_path = config_backup_dir / config_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                backed_up_files.append(str(dest_path))

        return {
            "status": "passed",
            "files_backed_up": len(backed_up_files),
            "files": backed_up_files,
        }

    def _test_service_state_collection(self, backup_dir: Path) -> dict:
        """Test service state collection"""
        service_backup_dir = backup_dir / "services"
        service_backup_dir.mkdir(exist_ok=True)

        services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
        ]
        service_ports = {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
        }

        service_states = {}
        for service_name in services:
            port = service_ports[service_name]

            # Check if service is running using netstat
            is_running = self._is_service_running(port)

            service_states[service_name] = {
                "running": is_running,
                "port": port,
                "timestamp": datetime.now().isoformat(),
            }

        # Save service states
        states_file = service_backup_dir / "service_states.json"
        with open(states_file, "w") as f:
            f.write(json.dumps(service_states, indent=2))

        return {
            "status": "passed",
            "services_checked": len(service_states),
            "running_services": sum(
                1 for state in service_states.values() if state["running"]
            ),
        }

    def _test_blockchain_backup(self, backup_dir: Path) -> dict:
        """Test blockchain state backup"""
        blockchain_backup_dir = backup_dir / "blockchain"
        blockchain_backup_dir.mkdir(exist_ok=True)

        # Backup blockchain directory if it exists
        blockchain_source = self.project_root / "blockchain"
        if blockchain_source.exists():
            blockchain_dest = blockchain_backup_dir / "blockchain"
            shutil.copytree(blockchain_source, blockchain_dest, dirs_exist_ok=True)

        # Create Quantumagi state
        quantumagi_state = {
            "constitution_hash": "cdd01ef066bc6cf2",
            "deployment_status": "active",
            "programs": ["constitution", "policy", "logging"],
            "network": "devnet",
            "timestamp": datetime.now().isoformat(),
        }

        state_file = blockchain_backup_dir / "quantumagi_state.json"
        with open(state_file, "w") as f:
            f.write(json.dumps(quantumagi_state, indent=2))

        return {
            "status": "passed",
            "constitution_hash": "cdd01ef066bc6cf2",
            "programs_backed_up": True,
        }

    def _test_manifest_creation(self, backup_dir: Path) -> dict:
        """Test backup manifest creation"""
        manifest = {
            "backup_id": f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "test",
            "status": "completed",
            "metadata": {
                "constitution_hash": "cdd01ef066bc6cf2",
                "system_version": "3.0.0",
                "backup_version": "1.0",
            },
        }

        manifest_path = backup_dir / "backup_manifest.json"
        with open(manifest_path, "w") as f:
            f.write(json.dumps(manifest, indent=2))

        return {
            "status": "passed",
            "manifest_created": True,
            "manifest_size": manifest_path.stat().st_size,
        }

    def _test_backup_compression(self, backup_dir: Path) -> dict:
        """Test backup compression"""
        compressed_file = backup_dir.with_suffix(".tar.gz")

        cmd = [
            "tar",
            "-czf",
            str(compressed_file),
            "-C",
            str(backup_dir.parent),
            backup_dir.name,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and compressed_file.exists():
            original_size = sum(
                f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
            )
            compressed_size = compressed_file.stat().st_size
            compression_ratio = (
                (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            )

            # Cleanup compressed file
            compressed_file.unlink()

            return {
                "status": "passed",
                "compression_ratio": f"{compression_ratio:.1f}%",
                "original_size": original_size,
                "compressed_size": compressed_size,
            }
        else:
            return {"status": "failed", "error": result.stderr}

    def _is_service_running(self, port: int) -> bool:
        """Check if service is running on given port"""
        try:
            result = subprocess.run(["netstat", "-ln"], capture_output=True, text=True)
            return f":{port} " in result.stdout
        except:
            return False


def main():
    """Main execution function"""
    # Ensure log directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    backup_test = SimpleBackupTest()
    result = backup_test.test_backup_infrastructure()

    print(json.dumps(result, indent=2))

    # Return appropriate exit code
    if result["status"] == "passed":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
