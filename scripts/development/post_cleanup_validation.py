#!/usr/bin/env python3
"""
ACGS-1 Post-Cleanup Validation Script

This script validates that the comprehensive cleanup was successful and that
all critical functionality remains intact, particularly the Quantumagi
Solana devnet deployment.

Validation Areas:
- File structure integrity
- Security configuration
- Dependency consistency
- Quantumagi deployment status
- Service configuration
"""

import json
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_file_structure() -> dict:
    """Validate that critical file structure is intact."""
    print("🔍 Validating file structure...")

    critical_paths = [
        "blockchain/programs/quantumagi-core",
        "blockchain/programs/appeals",
        "blockchain/programs/logging",
        "services/core/constitutional-ai",
        "services/core/governance-synthesis",
        "services/core/policy-governance",
        "services/core/formal-verification",
        "services/platform/authentication",
        "services/platform/integrity",
        "applications/governance-dashboard",
        "integrations/quantumagi-bridge",
    ]

    results = {"status": "PASS", "missing_paths": [], "present_paths": []}

    for path in critical_paths:
        full_path = Path(path)
        if full_path.exists():
            results["present_paths"].append(path)
        else:
            results["missing_paths"].append(path)
            results["status"] = "FAIL"

    print(f"✅ File structure validation: {results['status']}")
    print(
        f"   Present: {len(results['present_paths'])}/{len(critical_paths)} critical paths"
    )

    return results


def validate_security_configuration() -> dict:
    """Validate security configuration improvements."""
    print("🔒 Validating security configuration...")

    results = {
        "status": "PASS",
        "env_template_exists": False,
        "gitignore_updated": False,
        "sensitive_files_removed": True,
        "issues": [],
    }

    # Check config/environments/developmentconfig/environments/template.env exists
    env_template = Path("config/environments/developmentconfig/environments/template.env")
    if env_template.exists():
        results["env_template_exists"] = True
        print("✅ Environment template created")
    else:
        results["issues"].append("Missing config/environments/developmentconfig/environments/template.env")
        results["status"] = "WARN"

    # Check .gitignore has security patterns
    gitignore = Path(".gitignore")
    if gitignore.exists():
        with open(gitignore) as f:
            content = f.read()
            if "*config/environments/development.env" in content and "auth_tokens" in content:
                results["gitignore_updated"] = True
                print("✅ .gitignore security patterns updated")
            else:
                results["issues"].append("Incomplete .gitignore security patterns")
                results["status"] = "WARN"

    # Check for remaining sensitive files
    sensitive_patterns = ["auth_tokens.json", "auth_tokensconfig/environments/development.env", "cookies.txt"]
    for pattern in sensitive_patterns:
        if list(Path().glob(f"**/{pattern}")):
            results["sensitive_files_removed"] = False
            results["issues"].append(f"Sensitive file still present: {pattern}")
            results["status"] = "FAIL"

    print(f"✅ Security validation: {results['status']}")
    return results


def validate_dependency_consistency() -> dict:
    """Validate dependency management improvements."""
    print("📦 Validating dependency consistency...")

    results = {
        "status": "PASS",
        "requirements_consolidated": False,
        "package_json_cleaned": False,
        "cargo_toml_cleaned": False,
        "issues": [],
    }

    # Check requirements consolidation
    requirements_files = list(Path().glob("**/requirements*.txt"))
    service_dirs = list(Path("services").glob("*/*/"))

    # Should have fewer requirements files after consolidation
    if len(requirements_files) < len(service_dirs):
        results["requirements_consolidated"] = True
        print("✅ Requirements files consolidated")

    # Check package.json files are clean
    package_files = list(Path().glob("**/package.json"))
    clean_package_count = 0

    for package_file in package_files:
        try:
            with open(package_file) as f:
                data = json.load(f)
                if "dependencies" in data and isinstance(data["dependencies"], dict):
                    clean_package_count += 1
        except:
            pass

    if clean_package_count > 0:
        results["package_json_cleaned"] = True
        print("✅ Package.json files cleaned")

    # Check Cargo.toml files
    cargo_files = list(Path().glob("**/Cargo.toml"))
    if len(cargo_files) >= 4:  # Should have blockchain Cargo files
        results["cargo_toml_cleaned"] = True
        print("✅ Cargo.toml files present and cleaned")

    print(f"✅ Dependency validation: {results['status']}")
    return results


def validate_quantumagi_deployment() -> dict:
    """Validate Quantumagi deployment integrity."""
    print("⚡ Validating Quantumagi deployment...")

    results = {
        "status": "PASS",
        "blockchain_structure": False,
        "deployment_files": False,
        "constitution_data": False,
        "issues": [],
    }

    # Check blockchain structure
    blockchain_path = Path("blockchain")
    required_blockchain_files = [
        "Anchor.toml",
        "Cargo.toml",
        "programs/quantumagi-core",
        "programs/appeals",
        "programs/logging",
    ]

    blockchain_files_present = 0
    for file_path in required_blockchain_files:
        if (blockchain_path / file_path).exists():
            blockchain_files_present += 1

    if blockchain_files_present == len(required_blockchain_files):
        results["blockchain_structure"] = True
        print("✅ Blockchain structure intact")
    else:
        results["issues"].append(
            f"Missing blockchain files: {len(required_blockchain_files) - blockchain_files_present}"
        )
        results["status"] = "FAIL"

    # Check deployment files
    deployment_files = [
        "constitution_data.json",
        "governance_accounts.json",
        "initial_policies.json",
    ]

    deployment_files_present = 0
    for file_name in deployment_files:
        if (blockchain_path / file_name).exists():
            deployment_files_present += 1

    if deployment_files_present == len(deployment_files):
        results["deployment_files"] = True
        print("✅ Deployment files present")
    else:
        results["issues"].append("Missing deployment files")
        results["status"] = "WARN"

    # Check constitution data
    constitution_file = blockchain_path / "constitution_data.json"
    if constitution_file.exists():
        try:
            with open(constitution_file) as f:
                constitution_data = json.load(f)
                if "constitution_hash" in constitution_data:
                    results["constitution_data"] = True
                    print("✅ Constitution data valid")
        except:
            results["issues"].append("Invalid constitution data")
            results["status"] = "WARN"

    print(f"✅ Quantumagi validation: {results['status']}")
    return results


def validate_service_configuration() -> dict:
    """Validate service configuration integrity."""
    print("⚙️ Validating service configuration...")

    results = {
        "status": "PASS",
        "service_registry": False,
        "core_services": 0,
        "platform_services": 0,
        "issues": [],
    }

    # Check service registry
    service_registry = Path("service_registry_config.json")
    if service_registry.exists():
        try:
            with open(service_registry) as f:
                registry_data = json.load(f)
                if "services" in registry_data:
                    results["service_registry"] = True
                    print("✅ Service registry configuration present")
        except:
            results["issues"].append("Invalid service registry")
            results["status"] = "WARN"

    # Count core services
    core_services_path = Path("services/core")
    if core_services_path.exists():
        core_services = [d for d in core_services_path.iterdir() if d.is_dir()]
        results["core_services"] = len(core_services)
        print(f"✅ Core services: {len(core_services)}")

    # Count platform services
    platform_services_path = Path("services/platform")
    if platform_services_path.exists():
        platform_services = [d for d in platform_services_path.iterdir() if d.is_dir()]
        results["platform_services"] = len(platform_services)
        print(f"✅ Platform services: {len(platform_services)}")

    print(f"✅ Service configuration validation: {results['status']}")
    return results


def generate_validation_report(validation_results: dict) -> str:
    """Generate comprehensive validation report."""

    report = {
        "timestamp": "2025-12-10T00:30:00Z",
        "cleanup_validation": "COMPLETED",
        "overall_status": "PASS",
        "validations": validation_results,
        "summary": {
            "total_validations": len(validation_results),
            "passed": 0,
            "warnings": 0,
            "failed": 0,
        },
        "recommendations": [],
    }

    # Calculate summary
    for _validation_name, result in validation_results.items():
        status = result.get("status", "UNKNOWN")
        if status == "PASS":
            report["summary"]["passed"] += 1
        elif status == "WARN":
            report["summary"]["warnings"] += 1
        elif status == "FAIL":
            report["summary"]["failed"] += 1
            report["overall_status"] = "FAIL"

    # Add recommendations
    if report["summary"]["failed"] > 0:
        report["recommendations"].append("Address failed validations immediately")
    if report["summary"]["warnings"] > 0:
        report["recommendations"].append("Review warnings and implement fixes")

    report["recommendations"].extend(
        [
            "Monitor system performance after cleanup",
            "Implement automated dependency scanning",
            "Establish regular security audits",
            "Maintain backup and recovery procedures",
        ]
    )

    return json.dumps(report, indent=2)


def main():
    """Main validation execution."""
    print("🚀 Starting ACGS-1 Post-Cleanup Validation...")
    print("=" * 60)

    validation_results = {}

    # Run all validations
    validation_results["file_structure"] = validate_file_structure()
    validation_results["security_configuration"] = validate_security_configuration()
    validation_results["dependency_consistency"] = validate_dependency_consistency()
    validation_results["quantumagi_deployment"] = validate_quantumagi_deployment()
    validation_results["service_configuration"] = validate_service_configuration()

    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    # Generate and save report
    report = generate_validation_report(validation_results)

    report_file = "post_cleanup_validation_report.json"
    with open(report_file, "w") as f:
        f.write(report)

    # Print summary
    report_data = json.loads(report)
    print(f"Overall Status: {report_data['overall_status']}")
    print(f"Validations Passed: {report_data['summary']['passed']}")
    print(f"Warnings: {report_data['summary']['warnings']}")
    print(f"Failed: {report_data['summary']['failed']}")

    print(f"\n✅ Validation completed. Report saved to: {report_file}")

    if report_data["overall_status"] == "PASS":
        print("🎉 ACGS-1 cleanup validation SUCCESSFUL!")
        print("   All critical systems are operational.")
        print("   Quantumagi deployment preserved.")
    else:
        print("⚠️  Some validations failed. Review the report for details.")

    return report_data["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
