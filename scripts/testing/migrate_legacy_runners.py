#!/usr/bin/env python3
"""
Legacy Test Runner Migration Script
Constitutional Hash: cdd01ef066bc6cf2

Script to help migrate from legacy test runners to the unified test orchestrator.
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Mapping of legacy scripts to new orchestrator commands
LEGACY_MIGRATION_MAP = {
    "run_comprehensive_tests.py": {
        "description": "Comprehensive test runner with all categories",
        "new_command": "python scripts/cli/test.py --all",
        "notes": "Runs all test suites in the new unified framework"
    },
    "run_improved_tests.py": {
        "description": "Improved test runner with coverage",
        "new_command": "python scripts/cli/test.py --with-coverage",
        "notes": "Runs test suites that include coverage analysis"
    },
    "run_integration_tests.py": {
        "description": "Integration test runner",
        "new_command": "python scripts/cli/test.py --suite integration_tests",
        "notes": "Runs integration tests with service availability checking"
    },
    "run_e2e_with_coverage.py": {
        "description": "E2E test runner with coverage options",
        "new_command": "python scripts/cli/test.py --suite e2e_tests",
        "notes": "Runs end-to-end tests through the unified framework"
    },
    "run_testing_suite.py": {
        "description": "General testing suite runner",
        "new_command": "python scripts/cli/test.py --all --parallel",
        "notes": "Runs all tests with parallel execution for better performance"
    }
}


class LegacyTestRunnerMigrator:
    """Helper for migrating from legacy test runners."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts"
        self.testing_dir = self.scripts_dir / "testing"
        
    def analyze_legacy_usage(self) -> Dict[str, List[str]]:
        """Analyze how legacy test runners are being used."""
        usage_analysis = {}
        
        # Look for references to legacy scripts in various files
        search_patterns = [
            "*.py", "*.sh", "*.yml", "*.yaml", "*.md", "*.txt"
        ]
        
        for pattern in search_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        for legacy_script in LEGACY_MIGRATION_MAP.keys():
                            if legacy_script in content:
                                if legacy_script not in usage_analysis:
                                    usage_analysis[legacy_script] = []
                                usage_analysis[legacy_script].append(str(file_path.relative_to(self.project_root)))
                                
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        continue
        
        return usage_analysis
    
    def generate_migration_guide(self) -> str:
        """Generate a comprehensive migration guide."""
        
        guide = f"""# ACGS Test Runner Migration Guide
Constitutional Hash: {CONSTITUTIONAL_HASH}

## Overview

This guide helps you migrate from legacy test runners to the new unified test orchestrator.
The new system provides better performance, more consistent reporting, and unified configuration.

## Legacy Script Mapping

"""
        
        for legacy_script, migration_info in LEGACY_MIGRATION_MAP.items():
            guide += f"""### {legacy_script}

**Description**: {migration_info['description']}
**New Command**: `{migration_info['new_command']}`
**Notes**: {migration_info['notes']}

"""
        
        # Add usage analysis
        usage_analysis = self.analyze_legacy_usage()
        if usage_analysis:
            guide += """## Current Usage Analysis

The following files reference legacy test runners:

"""
            for script, files in usage_analysis.items():
                guide += f"""### {script}
Referenced in:
"""
                for file_path in files:
                    guide += f"- {file_path}\n"
                guide += "\n"
        
        guide += f"""## New Unified Test CLI

The new test CLI provides all functionality of the legacy runners with additional features:

### Basic Usage
```bash
# List available test suites
python scripts/cli/test.py --list

# Run all tests
python scripts/cli/test.py --all

# Run specific test suite
python scripts/cli/test.py --suite unit_tests

# Run multiple specific suites
python scripts/cli/test.py --suites unit_tests integration_tests

# Run with filters
python scripts/cli/test.py --critical-only     # Only critical tests
python scripts/cli/test.py --with-coverage     # Only tests with coverage
python scripts/cli/test.py --fast              # Exclude slow tests

# Run with execution options
python scripts/cli/test.py --all --parallel    # Parallel execution
python scripts/cli/test.py --all --fail-fast   # Stop on critical failure

# Output options
python scripts/cli/test.py --all --format json --output results.json
python scripts/cli/test.py --all --verbose
```

### Available Test Suites

- `constitutional_compliance` - Constitutional compliance validation [critical]
- `unit_tests` - Unit tests with coverage analysis [coverage]
- `integration_tests` - Service integration tests
- `performance_tests` - Performance benchmarks and latency validation
- `security_tests` - Security hardening and vulnerability tests
- `multi_tenant_tests` - Multi-tenant isolation tests
- `e2e_tests` - End-to-end workflow tests

### Advanced Features

- **Parallel Execution**: Non-critical tests can run in parallel for faster execution
- **Fail-Fast Mode**: Stop execution on critical test failures
- **Unified Reporting**: Consistent JSON and text output formats
- **Service Availability Checking**: Automatic service health checks before tests
- **Constitutional Compliance**: Built-in constitutional hash validation
- **Timeout Management**: Configurable timeouts per test suite
- **Coverage Integration**: Automatic coverage collection and reporting

## Migration Steps

1. **Review Current Usage**: Check which legacy scripts you're currently using
2. **Update CI/CD Pipelines**: Replace legacy script calls with new CLI commands
3. **Update Documentation**: Update any documentation that references legacy scripts
4. **Test the Migration**: Run equivalent commands to ensure they work as expected
5. **Archive Legacy Scripts**: Move legacy scripts to a backup location

## Backward Compatibility

The legacy scripts will continue to work during the transition period, but they are deprecated.
The new unified orchestrator provides all functionality with improved performance and reporting.

## Support

For questions about migration:
1. Check the CLI help: `python scripts/cli/test.py --help`
2. Review the orchestrator documentation in `scripts/testing/orchestrator.py`
3. Test new commands in a development environment first

Constitutional Hash: {CONSTITUTIONAL_HASH}
"""
        
        return guide
    
    def create_migration_aliases(self) -> None:
        """Create shell aliases to help with migration."""
        
        aliases_script = self.scripts_dir / "test_aliases.sh"
        
        alias_content = f"""#!/bin/bash
# ACGS Test Runner Migration Aliases
# Constitutional Hash: {CONSTITUTIONAL_HASH}
#
# Source this file to get convenient aliases for the new test CLI:
# source scripts/test_aliases.sh

# Basic test suite aliases
alias acgs-test-all='python scripts/cli/test.py --all'
alias acgs-test-unit='python scripts/cli/test.py --suite unit_tests'
alias acgs-test-integration='python scripts/cli/test.py --suite integration_tests'
alias acgs-test-performance='python scripts/cli/test.py --suite performance_tests'
alias acgs-test-security='python scripts/cli/test.py --suite security_tests'
alias acgs-test-e2e='python scripts/cli/test.py --suite e2e_tests'
alias acgs-test-constitutional='python scripts/cli/test.py --suite constitutional_compliance'

# Filtered test aliases
alias acgs-test-critical='python scripts/cli/test.py --critical-only'
alias acgs-test-coverage='python scripts/cli/test.py --with-coverage'
alias acgs-test-fast='python scripts/cli/test.py --fast'

# Execution mode aliases
alias acgs-test-parallel='python scripts/cli/test.py --all --parallel'
alias acgs-test-fail-fast='python scripts/cli/test.py --all --fail-fast'

# Legacy script replacements
alias run-comprehensive-tests='python scripts/cli/test.py --all'
alias run-improved-tests='python scripts/cli/test.py --with-coverage'
alias run-integration-tests='python scripts/cli/test.py --suite integration_tests'
alias run-e2e-tests='python scripts/cli/test.py --suite e2e_tests'

# Utility aliases
alias acgs-test-list='python scripts/cli/test.py --list'
alias acgs-test-help='python scripts/cli/test.py --help'

echo "ACGS Test CLI aliases loaded successfully!"
echo "Use 'acgs-test-list' to see available test suites"
echo "Use 'acgs-test-help' for detailed help"
"""
        
        aliases_script.write_text(alias_content)
        print(f"Created migration aliases: {aliases_script}")
    
    def backup_legacy_scripts(self, backup_dir: Path) -> None:
        """Backup legacy test scripts to a specified directory."""
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        backed_up = []
        
        for legacy_script in LEGACY_MIGRATION_MAP.keys():
            legacy_path = self.testing_dir / legacy_script
            if legacy_path.exists():
                backup_path = backup_dir / legacy_script
                shutil.copy2(legacy_path, backup_path)
                backed_up.append(legacy_script)
                print(f"Backed up: {legacy_script} -> {backup_path}")
        
        # Also backup the main testing suite runner
        main_runner = self.scripts_dir / "run_testing_suite.py"
        if main_runner.exists():
            backup_path = backup_dir / "run_testing_suite.py"
            shutil.copy2(main_runner, backup_path)
            backed_up.append("run_testing_suite.py")
            print(f"Backed up: run_testing_suite.py -> {backup_path}")
        
        return backed_up
    
    def validate_new_setup(self) -> bool:
        """Validate that the new unified test setup is working."""
        
        required_files = [
            self.scripts_dir / "cli" / "test.py",
            self.scripts_dir / "testing" / "orchestrator.py", 
            self.scripts_dir / "testing" / "__init__.py",
            self.scripts_dir / "core" / "__init__.py",
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing required files for new test setup:")
            for file_path in missing_files:
                print(f"  - {file_path}")
            return False
        
        print("✅ New test setup validation passed")
        return True


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(
        description="ACGS Legacy Test Runner Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="ACGS project root directory"
    )
    parser.add_argument(
        "--generate-guide",
        action="store_true",
        help="Generate migration guide"
    )
    parser.add_argument(
        "--create-aliases", 
        action="store_true",
        help="Create shell aliases for migration"
    )
    parser.add_argument(
        "--backup-legacy",
        type=Path,
        help="Backup legacy scripts to specified directory"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate new test setup"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for migration guide"
    )
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = LegacyTestRunnerMigrator(args.project_root)
    
    # Handle different actions
    if args.generate_guide:
        guide = migrator.generate_migration_guide()
        
        if args.output:
            args.output.write_text(guide)
            print(f"Migration guide written to: {args.output}")
        else:
            print(guide)
    
    if args.create_aliases:
        migrator.create_migration_aliases()
    
    if args.backup_legacy:
        backed_up = migrator.backup_legacy_scripts(args.backup_legacy)
        print(f"Backed up {len(backed_up)} legacy scripts to {args.backup_legacy}")
    
    if args.validate:
        if migrator.validate_new_setup():
            print("✅ Ready to use new unified test orchestrator")
        else:
            print("❌ New test setup needs attention")
            sys.exit(1)
    
    if not any([args.generate_guide, args.create_aliases, args.backup_legacy, args.validate]):
        # Default action: show summary
        print(f"ACGS Legacy Test Runner Migration Tool")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print()
        print("Available actions:")
        print("  --generate-guide    Generate comprehensive migration guide") 
        print("  --create-aliases    Create shell aliases for easier migration")
        print("  --backup-legacy     Backup legacy scripts")
        print("  --validate          Validate new test setup")
        print()
        print("Use --help for detailed usage information")


if __name__ == "__main__":
    main()