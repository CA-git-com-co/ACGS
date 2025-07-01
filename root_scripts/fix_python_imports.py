#!/usr/bin/env python3
"""
Fix Python Import Issues for ACGS-1 Services
Creates proper Python module structure for services with hyphened directory names.
"""

import os
import sys
from pathlib import Path


def create_init_files():
    """Create __init__.py files to make directories proper Python packages."""
    print("🔧 Creating __init__.py files for Python packages...")

    # Define directories that need __init__.py files
    directories_to_fix = [
        # Core services with hyphens
        "services/core/constitutional-ai",
        "services/core/constitutional-ai/ac_service",
        "services/core/constitutional-ai/ac_service/app",
        "services/core/constitutional-ai/ac_service/app/core",
        "services/core/governance-synthesis",
        "services/core/governance-synthesis/gs_service",
        "services/core/governance-synthesis/gs_service/app",
        "services/core/governance-synthesis/gs_service/app/core",
        "services/core/governance-synthesis/gs_service/app/services",
        "services/core/formal-verification",
        "services/core/formal-verification/fv_service",
        "services/core/formal-verification/fv_service/app",
        "services/core/formal-verification/fv_service/app/core",
        "services/core/policy-governance",
        "services/core/policy-governance/pgc_service",
        "services/core/policy-governance/pgc_service/app",
        "services/core/policy-governance/pgc_service/app/core",
        "services/core/self-evolving-ai",
        "services/core/self-evolving-ai/app",
        "services/core/evolutionary-computation",
        "services/core/evolutionary-computation/app",
        # Platform services
        "services/platform",
        "services/platform/pgc",
        "services/platform/pgc/pgc_service",
        "services/platform/pgc/pgc_service/app",
        "services/platform/pgc/pgc_service/app/core",
        # Integration services
        "integrations/alphaevolve_engine",
        "integrations/alphaevolve_engine/services",
        "integrations/alphaevolve_engine/services/qec_enhancement",
    ]

    created_count = 0
    for directory in directories_to_fix:
        init_file = Path(directory) / "__init__.py"

        if not init_file.parent.exists():
            print(f"  ⏭️  Directory does not exist: {directory}")
            continue

        if not init_file.exists():
            try:
                init_file.write_text(f'"""Python package for {directory}."""\n')
                print(f"  ✅ Created: {init_file}")
                created_count += 1
            except Exception as e:
                print(f"  ❌ Failed to create {init_file}: {e}")
        else:
            print(f"  ⏭️  Already exists: {init_file}")

    print(f"📊 Created {created_count} __init__.py files")
    return created_count


def create_symbolic_links():
    """Create symbolic links with underscores pointing to hyphenated directories."""
    print("\n🔗 Creating symbolic links for hyphenated directories...")

    # Define symbolic links to create
    symlinks = [
        ("services/core/constitutional_ai", "services/core/constitutional-ai"),
        ("services/core/governance_synthesis", "services/core/governance-synthesis"),
        ("services/core/formal_verification", "services/core/formal-verification"),
        ("services/core/policy_governance", "services/core/policy-governance"),
        ("services/core/self_evolving_ai", "services/core/self-evolving-ai"),
        (
            "services/core/evolutionary_computation",
            "services/core/evolutionary-computation",
        ),
        ("services/core/governance_workflows", "services/core/governance-workflows"),
    ]

    created_count = 0
    for link_name, target in symlinks:
        link_path = Path(link_name)
        target_path = Path(target)

        if not target_path.exists():
            print(f"  ⏭️  Target does not exist: {target}")
            continue

        if link_path.exists():
            if link_path.is_symlink():
                print(f"  ⏭️  Symlink already exists: {link_name}")
            else:
                print(f"  ⚠️  Path exists but is not a symlink: {link_name}")
            continue

        try:
            # Create relative symlink
            relative_target = os.path.relpath(target_path, link_path.parent)
            link_path.symlink_to(relative_target)
            print(f"  ✅ Created symlink: {link_name} -> {target}")
            created_count += 1
        except Exception as e:
            print(f"  ❌ Failed to create symlink {link_name}: {e}")

    print(f"📊 Created {created_count} symbolic links")
    return created_count


def setup_python_path():
    """Add necessary directories to Python path."""
    print("\n🐍 Setting up Python path...")

    # Get project root
    project_root = Path.cwd()

    # Directories to add to Python path
    paths_to_add = [
        project_root,
        project_root / "services",
        project_root / "services/shared",
        project_root / "services/core",
        project_root / "services/platform",
        project_root / "integrations",
    ]

    added_count = 0
    for path in paths_to_add:
        if path.exists():
            path_str = str(path.absolute())
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                print(f"  ✅ Added to Python path: {path_str}")
                added_count += 1
            else:
                print(f"  ⏭️  Already in Python path: {path_str}")
        else:
            print(f"  ⚠️  Path does not exist: {path}")

    print(f"📊 Added {added_count} paths to Python path")
    return added_count


def create_conftest_py():
    """Create conftest.py to set up Python path for pytest."""
    print("\n🧪 Creating conftest.py for pytest...")

    conftest_content = '''"""
Pytest configuration for ACGS-1 test suite.
Sets up Python path and imports for services with hyphened directory names.
"""

import sys
from pathlib import Path

# Add project root and service directories to Python path
project_root = Path(__file__).parent
paths_to_add = [
    project_root,
    project_root / "services",
    project_root / "services/shared", 
    project_root / "services/core",
    project_root / "services/platform",
    project_root / "integrations",
]

for path in paths_to_add:
    if path.exists():
        path_str = str(path.absolute())
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

# Import pytest fixtures and configuration
import pytest

# Configure pytest markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration  
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.e2e = pytest.mark.e2e
'''

    conftest_path = Path("conftest.py")
    try:
        conftest_path.write_text(conftest_content)
        print(f"  ✅ Created: {conftest_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create conftest.py: {e}")
        return False


def main():
    """Main execution function."""
    print("🔧 ACGS-1 Python Import Fixer")
    print("=" * 50)

    # Step 1: Create __init__.py files
    init_count = create_init_files()

    # Step 2: Create symbolic links
    symlink_count = create_symbolic_links()

    # Step 3: Setup Python path
    path_count = setup_python_path()

    # Step 4: Create conftest.py
    conftest_created = create_conftest_py()

    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    print(f"✅ __init__.py files created: {init_count}")
    print(f"🔗 Symbolic links created: {symlink_count}")
    print(f"🐍 Python paths added: {path_count}")
    print(f"🧪 conftest.py created: {'Yes' if conftest_created else 'No'}")

    if init_count > 0 or symlink_count > 0 or conftest_created:
        print("\n🎉 Python import structure has been fixed!")
        print("🧪 You can now run the test suite:")
        print("   python -m pytest tests/ --tb=short -v")
    else:
        print(
            "\n⚠️  No changes were made. Import issues may require manual intervention."
        )


if __name__ == "__main__":
    main()
