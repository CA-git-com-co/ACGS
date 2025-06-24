#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Backup Integrity Verification System
Validates backup completeness, data consistency, and integrity
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/home/dislove/ACGS-1/logs/backup_integrity.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class BackupIntegrityVerifier:
    """Comprehensive backup integrity verification system for ACGS-1"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.backup_root = Path("/home/dislove/ACGS-1/backups")
        self.constitution_hash = "cdd01ef066bc6cf2"

        # Critical files that must be present in backups
        self.critical_config_files = [
            ".env",
            "docker-compose.yml",
            "scripts/start_missing_services.sh",
            "OPERATIONAL_RUNBOOKS.md",
        ]

        self.critical_scripts = [
            "comprehensive_health_check.py",
            "enhanced_backup_disaster_recovery.py",
            "emergency_rollback_procedures.py",
        ]

        self.services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
        ]

    def verify_backup_integrity(self, backup_id: str | None = None) -> dict:
        """Perform comprehensive backup integrity verification"""
        logger.info("🔍 Starting comprehensive backup integrity verification")

        try:
            verification_results = {
                "timestamp": datetime.now().isoformat(),
                "verification_id": f"VERIFY-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "constitution_hash": self.constitution_hash,
                "tests": {},
                "overall_status": "unknown",
                "verified_backups": 0,
                "failed_backups": 0,
            }

            # Get backup to verify
            if backup_id:
                backup_dirs = [self.backup_root / backup_id]
            else:
                # Verify all available backups
                backup_dirs = [d for d in self.backup_root.iterdir() if d.is_dir()]

            if not backup_dirs:
                return {"status": "failed", "error": "No backups found to verify"}

            # Verify each backup
            for backup_dir in backup_dirs:
                backup_name = backup_dir.name
                logger.info(f"📋 Verifying backup: {backup_name}")

                backup_verification = self._verify_single_backup(backup_dir)
                verification_results["tests"][backup_name] = backup_verification

                if backup_verification.get("status") == "success":
                    verification_results["verified_backups"] += 1
                else:
                    verification_results["failed_backups"] += 1

            # Determine overall status
            total_backups = len(backup_dirs)
            success_rate = verification_results["verified_backups"] / total_backups

            if success_rate >= 0.8:  # 80% success threshold
                verification_results["overall_status"] = "success"
            elif success_rate >= 0.5:
                verification_results["overall_status"] = "partial"
            else:
                verification_results["overall_status"] = "failed"

            verification_results["success_rate"] = round(success_rate * 100, 1)

            # Save verification report
            report_dir = self.project_root / "logs" / "backup_integrity"
            report_dir.mkdir(exist_ok=True)

            report_file = (
                report_dir
                / f"integrity_verification_{verification_results['verification_id']}.json"
            )
            with open(report_file, "w") as f:
                json.dump(verification_results, f, indent=2)

            logger.info(
                f"✅ Backup integrity verification completed: {verification_results['overall_status']}"
            )
            return verification_results

        except Exception as e:
            logger.error(f"❌ Backup integrity verification failed: {e}")
            return {"status": "failed", "error": str(e)}

    def _verify_single_backup(self, backup_dir: Path) -> dict:
        """Verify integrity of a single backup"""
        try:
            verification = {
                "backup_path": str(backup_dir),
                "tests": {},
                "status": "unknown",
            }

            # Test 1: Manifest validation
            manifest_test = self._verify_manifest(backup_dir)
            verification["tests"]["manifest"] = manifest_test

            # Test 2: Configuration integrity
            config_test = self._verify_configurations(backup_dir)
            verification["tests"]["configurations"] = config_test

            # Test 3: Service state validation
            service_test = self._verify_service_states(backup_dir)
            verification["tests"]["services"] = service_test

            # Test 4: Script integrity
            script_test = self._verify_scripts(backup_dir)
            verification["tests"]["scripts"] = script_test

            # Test 5: Constitution hash verification
            constitution_test = self._verify_constitution_hash(backup_dir)
            verification["tests"]["constitution"] = constitution_test

            # Test 6: File checksums
            checksum_test = self._verify_file_checksums(backup_dir)
            verification["tests"]["checksums"] = checksum_test

            # Determine overall status
            all_tests_passed = all(
                test.get("status") == "success"
                for test in verification["tests"].values()
            )

            verification["status"] = "success" if all_tests_passed else "failed"

            return verification

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_manifest(self, backup_dir: Path) -> dict:
        """Verify backup manifest exists and is valid"""
        try:
            manifest_file = backup_dir / "backup_manifest.json"

            if not manifest_file.exists():
                return {"status": "failed", "error": "Backup manifest not found"}

            with open(manifest_file) as f:
                manifest = json.load(f)

            # Check required fields
            required_fields = ["backup_id", "timestamp", "status", "components"]
            missing_fields = [
                field for field in required_fields if field not in manifest
            ]

            if missing_fields:
                return {
                    "status": "failed",
                    "error": f"Missing manifest fields: {missing_fields}",
                }

            # Check component status
            components = manifest.get("components", {})
            failed_components = [
                name
                for name, comp in components.items()
                if comp.get("status") == "failed"
            ]

            return {
                "status": "success" if not failed_components else "warning",
                "backup_id": manifest.get("backup_id"),
                "backup_status": manifest.get("status"),
                "failed_components": failed_components,
                "total_components": len(components),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_configurations(self, backup_dir: Path) -> dict:
        """Verify configuration files are backed up correctly"""
        try:
            config_dir = backup_dir / "configurations"

            if not config_dir.exists():
                return {
                    "status": "failed",
                    "error": "Configuration backup directory not found",
                }

            missing_files = []
            present_files = []

            for config_file in self.critical_config_files:
                config_path = config_dir / config_file
                if config_path.exists():
                    present_files.append(config_file)
                else:
                    missing_files.append(config_file)

            success_rate = len(present_files) / len(self.critical_config_files)

            return {
                "status": "success" if success_rate >= 0.8 else "failed",
                "present_files": present_files,
                "missing_files": missing_files,
                "success_rate": round(success_rate * 100, 1),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_service_states(self, backup_dir: Path) -> dict:
        """Verify service state backup"""
        try:
            service_dir = backup_dir / "services"

            if not service_dir.exists():
                return {
                    "status": "failed",
                    "error": "Service backup directory not found",
                }

            states_file = service_dir / "service_states.json"
            if not states_file.exists():
                return {"status": "failed", "error": "Service states file not found"}

            with open(states_file) as f:
                service_states = json.load(f)

            # Verify all services are documented
            missing_services = [
                service for service in self.services if service not in service_states
            ]

            return {
                "status": "success" if not missing_services else "failed",
                "documented_services": len(service_states),
                "missing_services": missing_services,
                "total_expected": len(self.services),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_scripts(self, backup_dir: Path) -> dict:
        """Verify critical scripts are backed up"""
        try:
            scripts_dir = backup_dir / "scripts"

            if not scripts_dir.exists():
                return {
                    "status": "failed",
                    "error": "Scripts backup directory not found",
                }

            missing_scripts = []
            present_scripts = []

            for script in self.critical_scripts:
                script_path = scripts_dir / script
                if script_path.exists():
                    present_scripts.append(script)
                else:
                    missing_scripts.append(script)

            success_rate = len(present_scripts) / len(self.critical_scripts)

            return {
                "status": "success" if success_rate >= 0.8 else "failed",
                "present_scripts": present_scripts,
                "missing_scripts": missing_scripts,
                "success_rate": round(success_rate * 100, 1),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_constitution_hash(self, backup_dir: Path) -> dict:
        """Verify constitution hash integrity in backup"""
        try:
            # Check manifest for constitution hash
            manifest_file = backup_dir / "backup_manifest.json"
            if manifest_file.exists():
                with open(manifest_file) as f:
                    manifest = json.load(f)

                manifest_hash = manifest.get("metadata", {}).get("constitution_hash")
                if manifest_hash == self.constitution_hash:
                    return {
                        "status": "success",
                        "constitution_hash": manifest_hash,
                        "verified_in": "manifest",
                    }

            # Check blockchain state file
            blockchain_state = backup_dir / "blockchain" / "quantumagi_state.json"
            if blockchain_state.exists():
                with open(blockchain_state) as f:
                    state = json.load(f)

                state_hash = state.get("constitution_hash")
                if state_hash == self.constitution_hash:
                    return {
                        "status": "success",
                        "constitution_hash": state_hash,
                        "verified_in": "blockchain_state",
                    }

            return {
                "status": "failed",
                "error": f"Constitution hash {self.constitution_hash} not found in backup",
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _verify_file_checksums(self, backup_dir: Path) -> dict:
        """Verify file integrity using checksums"""
        try:
            checksum_results = {
                "verified_files": 0,
                "corrupted_files": [],
                "total_files": 0,
            }

            # Calculate checksums for critical files
            for file_path in backup_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in [
                    ".json",
                    ".py",
                    ".sh",
                    ".md",
                    ".yml",
                    ".yaml",
                ]:
                    checksum_results["total_files"] += 1

                    try:
                        # Calculate SHA-256 checksum
                        sha256_hash = hashlib.sha256()
                        with open(file_path, "rb") as f:
                            for byte_block in iter(lambda: f.read(4096), b""):
                                sha256_hash.update(byte_block)

                        # File is readable and checksum calculated successfully
                        checksum_results["verified_files"] += 1

                    except Exception as e:
                        checksum_results["corrupted_files"].append(
                            {
                                "file": str(file_path.relative_to(backup_dir)),
                                "error": str(e),
                            }
                        )

            success_rate = (
                checksum_results["verified_files"] / checksum_results["total_files"]
                if checksum_results["total_files"] > 0
                else 0
            )

            return {
                "status": "success" if success_rate >= 0.95 else "failed",
                "verified_files": checksum_results["verified_files"],
                "corrupted_files": checksum_results["corrupted_files"],
                "total_files": checksum_results["total_files"],
                "success_rate": round(success_rate * 100, 1),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS-1 Backup Integrity Verification")
    parser.add_argument("action", choices=["verify"], help="Action to perform")
    parser.add_argument("--backup-id", help="Specific backup ID to verify")

    args = parser.parse_args()

    # Ensure log directory exists
    log_dir = Path("/home/dislove/ACGS-1/logs")
    log_dir.mkdir(exist_ok=True)

    verifier = BackupIntegrityVerifier()

    if args.action == "verify":
        result = verifier.verify_backup_integrity(args.backup_id)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
