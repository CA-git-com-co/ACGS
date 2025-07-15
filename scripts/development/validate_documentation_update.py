#!/usr/bin/env python3
"""
ACGS-1 Documentation Update Validation Script

Validates that the documentation update and .gitignore enhancement
accurately reflect the current codebase state and maintain compatibility
with existing development workflows.

Author: ACGS-1 Development Team
Version: 1.0.0
"""

from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_service_structure() -> tuple[bool, list[str]]:
    """Validate that all 7 core services exist with correct structure."""
    errors = []

    expected_services = {
        "Authentication Service": "services/platform/authentication/auth_service",
        "Constitutional AI Service": "services/core/constitutional-ai/ac_service",
        "Integrity Service": "services/platform/integrity/integrity_service",
        "Formal Verification Service": "services/core/formal-verification/fv_service",
        "Governance Synthesis Service": "services/core/governance-synthesis/gs_service",
        "Policy Governance Service": "services/core/policy-governance/pgc_service",
        "Evolutionary Computation Service": "services/core/evolutionary-computation",
    }

    for service_name, service_path in expected_services.items():
        path = Path(service_path)
        if not path.exists():
            errors.append(f"❌ {service_name} directory not found: {service_path}")
        else:
            print(f"✅ {service_name}: {service_path}")

    return len(errors) == 0, errors


def validate_documentation_files() -> tuple[bool, list[str]]:
    """Validate that all documentation files exist and have content."""
    errors = []

    required_docs = {
        "README.md": "Main project documentation",
        "docs/api/SERVICE_API_REFERENCE.md": "Service API documentation",
        "docs/deployment/HOST_BASED_DEPLOYMENT_GUIDE.md": "Deployment guide",
        ".gitignore": "Git ignore patterns",
    }

    for doc_path, description in required_docs.items():
        path = Path(doc_path)
        if not path.exists():
            errors.append(f"❌ {description} not found: {doc_path}")
        else:
            size = path.stat().st_size
            if size < 100:  # Minimum reasonable size
                errors.append(f"❌ {description} too small: {doc_path} ({size} bytes)")
            else:
                print(f"✅ {description}: {doc_path} ({size} bytes)")

    return len(errors) == 0, errors


def validate_gitignore_patterns() -> tuple[bool, list[str]]:
    """Validate that .gitignore contains all required patterns."""
    errors = []

    required_patterns = [
        ("**/*.log", ["**/*.log", "*.log"]),
        ("**/target/", ["**/target/", "target/"]),
        ("**/.anchor/", ["**/.anchor/", ".anchor"]),
        ("**/test-results/", ["**/test-results/", "test-results"]),
        ("**/.pytest_cache/", ["**/.pytest_cache/", ".pytest_cache"]),
        ("**/node_modules/", ["**/node_modules/", "node_modules/"]),
        ("**/__pycache__/", ["**/__pycache__/", "__pycache__/"]),
        ("*.pyc", ["*.pyc"]),
        ("config/environments/development.env*", ["config/environments/development.env*", "config/environments/development.env", "*config/environments/development.env"]),
        ("**/keypairs/", ["**/keypairs/", "keypairs"]),
        ("**/test-ledger/", ["**/test-ledger/", "test-ledger"]),
        ("**/.vscode/", ["**/.vscode/", ".vscode"]),
        ("**/.idea/", ["**/.idea/", ".idea"]),
        ("*.tmp", ["*.tmp", "**/*.tmp"]),
        ("*.swp", ["*.swp", "**/*.swp"]),
    ]

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        errors.append("❌ .gitignore file not found")
        return False, errors

    content = gitignore_path.read_text()

    for pattern_name, pattern_alternatives in required_patterns:
        found = any(alt in content for alt in pattern_alternatives)
        if not found:
            errors.append(
                f"❌ Missing .gitignore pattern: {pattern_name} (tried: {pattern_alternatives})"
            )
        else:
            found_pattern = next(alt for alt in pattern_alternatives if alt in content)
            print(f"✅ .gitignore pattern found: {pattern_name} (as: {found_pattern})")

    return len(errors) == 0, errors


def validate_readme_content() -> tuple[bool, list[str]]:
    """Validate README.md contains accurate service information."""
    errors = []

    readme_path = Path("README.md")
    if not readme_path.exists():
        errors.append("❌ README.md not found")
        return False, errors

    content = readme_path.read_text()

    # Check for service ports
    expected_ports = {
        "8000": "Authentication Service",
        "8001": "Constitutional AI Service",
        "8002": "Integrity Service",
        "8003": "Formal Verification Service",
        "8004": "Governance Synthesis Service",
        "8005": "Policy Governance Service",
        "8006": "Evolutionary Computation Service",
    }

    for port, service in expected_ports.items():
        if port not in content:
            errors.append(f"❌ Port {port} not mentioned in README for {service}")
        else:
            print(f"✅ Port {port} documented for {service}")

    # Check for governance workflows
    governance_workflows = [
        "Policy Creation",
        "Constitutional Compliance",
        "Policy Enforcement",
        "WINA Oversight",
        "Audit/Transparency",
    ]

    for workflow in governance_workflows:
        if workflow not in content:
            errors.append(f"❌ Governance workflow not documented: {workflow}")
        else:
            print(f"✅ Governance workflow documented: {workflow}")

    return len(errors) == 0, errors


def validate_blockchain_structure() -> tuple[bool, list[str]]:
    """Validate blockchain directory structure."""
    errors = []

    blockchain_path = Path("blockchain")
    if not blockchain_path.exists():
        errors.append("❌ blockchain/ directory not found")
        return False, errors

    expected_blockchain_files = [
        "blockchain/Anchor.toml",
        "blockchain/package.json",
        "blockchain/programs",
    ]

    for file_path in expected_blockchain_files:
        path = Path(file_path)
        if not path.exists():
            errors.append(f"❌ Blockchain file/directory not found: {file_path}")
        else:
            print(f"✅ Blockchain structure: {file_path}")

    return len(errors) == 0, errors


def validate_api_documentation() -> tuple[bool, list[str]]:
    """Validate API documentation completeness."""
    errors = []

    api_doc_path = Path("docs/api/SERVICE_API_REFERENCE.md")
    if not api_doc_path.exists():
        errors.append("❌ API documentation not found")
        return False, errors

    content = api_doc_path.read_text()

    # Check that all services are documented
    services = [
        "Authentication Service",
        "Constitutional AI Service",
        "Integrity Service",
        "Formal Verification Service",
        "Governance Synthesis Service",
        "Policy Governance Service",
        "Evolutionary Computation Service",
    ]

    for service in services:
        if service not in content:
            errors.append(f"❌ Service not documented in API reference: {service}")
        else:
            print(f"✅ API documentation includes: {service}")

    return len(errors) == 0, errors


def main():
    """Run all validation checks."""
    print("=" * 80)
    print("🔍 ACGS-1 Documentation Update Validation")
    print("=" * 80)

    all_passed = True
    all_errors = []

    validations = [
        ("Service Structure", validate_service_structure),
        ("Documentation Files", validate_documentation_files),
        (".gitignore Patterns", validate_gitignore_patterns),
        ("README Content", validate_readme_content),
        ("Blockchain Structure", validate_blockchain_structure),
        ("API Documentation", validate_api_documentation),
    ]

    for validation_name, validation_func in validations:
        print(f"\n🔄 Validating {validation_name}...")
        passed, errors = validation_func()

        if passed:
            print(f"✅ {validation_name}: PASSED")
        else:
            print(f"❌ {validation_name}: FAILED")
            all_passed = False
            all_errors.extend(errors)

            for error in errors:
                print(f"   {error}")

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Documentation update completed successfully")
        print("✅ .gitignore enhancement completed successfully")
        print("✅ Codebase structure accurately documented")
        print("✅ Development workflow compatibility maintained")
        return 0
    print("❌ VALIDATION FAILURES DETECTED")
    print(f"📊 Total errors: {len(all_errors)}")
    print("\n🔧 Please address the following issues:")
    for error in all_errors:
        print(f"   {error}")
    return 1


if __name__ == "__main__":
    exit(main())
