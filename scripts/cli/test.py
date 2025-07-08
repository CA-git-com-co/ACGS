#!/usr/bin/env python3
"""
ACGS Test CLI
Constitutional Hash: cdd01ef066bc6cf2

Command-line interface for ACGS unified test orchestrator.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_logger
from testing.orchestrator import ACGSTestOrchestrator, TestSuiteConfig

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="ACGS Unified Test Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} --all                           # Run all test suites
  {sys.argv[0]} --suite constitutional          # Run specific suite
  {sys.argv[0]} --list                          # List available test suites
  {sys.argv[0]} --parallel --fail-fast          # Run in parallel, stop on critical failure
  {sys.argv[0]} --coverage --output results.json # Run with coverage, save to file

Available Test Suites:
  constitutional_compliance  - Constitutional compliance validation
  unit_tests                - Unit tests with coverage analysis
  integration_tests         - Service integration tests
  performance_tests         - Performance benchmarks and latency validation
  security_tests            - Security hardening and vulnerability tests
  multi_tenant_tests        - Multi-tenant isolation tests
  e2e_tests                 - End-to-end workflow tests

Constitutional Hash: {CONSTITUTIONAL_HASH}
        """
    )
    
    # Suite selection
    suite_group = parser.add_mutually_exclusive_group()
    suite_group.add_argument(
        "--all", 
        action="store_true",
        help="Run all test suites"
    )
    suite_group.add_argument(
        "--suite",
        type=str,
        help="Run specific test suite by name"
    )
    suite_group.add_argument(
        "--suites",
        nargs="+",
        help="Run multiple specific test suites"
    )
    suite_group.add_argument(
        "--list",
        action="store_true", 
        help="List all available test suites"
    )
    
    # Test type filters
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Run only critical test suites"
    )
    parser.add_argument(
        "--with-coverage",
        action="store_true",
        help="Include only test suites with coverage analysis"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast test suites (exclude performance and e2e)"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run non-critical test suites in parallel"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first critical test suite failure"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Override default timeout for test suites (seconds)"
    )
    
    # Output options
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Quiet output (errors only)"
    )
    
    # Configuration
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="ACGS project root directory"
    )
    
    # Additional pytest options
    parser.add_argument(
        "--pytest-args",
        type=str,
        help="Additional arguments to pass to pytest (quoted string)"
    )
    
    return parser


def get_standard_suites() -> List[TestSuiteConfig]:
    """Get list of standard test suites with their configurations."""
    return [
        TestSuiteConfig(
            name="constitutional_compliance",
            description="Constitutional compliance validation across all services",
            command=[], # Will be populated by orchestrator
            critical=True
        ),
        TestSuiteConfig(
            name="unit_tests",
            description="Unit tests with comprehensive coverage analysis",
            command=[],
            coverage_enabled=True
        ),
        TestSuiteConfig(
            name="integration_tests", 
            description="Service integration and communication tests",
            command=[]
        ),
        TestSuiteConfig(
            name="performance_tests",
            description="Performance benchmarks and latency validation",
            command=[],
            timeout=1800
        ),
        TestSuiteConfig(
            name="security_tests",
            description="Security hardening and vulnerability tests",
            command=[]
        ),
        TestSuiteConfig(
            name="multi_tenant_tests",
            description="Multi-tenant isolation and security tests",
            command=[]
        ),
        TestSuiteConfig(
            name="e2e_tests",
            description="End-to-end workflow and integration tests",
            command=[],
            timeout=1800,
            required_files=[Path("tests/e2e")]
        ),
    ]


def filter_suites(
    suites: List[TestSuiteConfig], 
    args
) -> List[TestSuiteConfig]:
    """Filter test suites based on command line arguments."""
    filtered = suites
    
    if args.critical_only:
        filtered = [s for s in filtered if s.critical]
    
    if args.with_coverage:
        filtered = [s for s in filtered if s.coverage_enabled]
    
    if args.fast:
        # Exclude long-running suites
        exclude_names = ["performance_tests", "e2e_tests"]
        filtered = [s for s in filtered if s.name not in exclude_names]
    
    return filtered


async def run_tests(args) -> int:
    """Run tests based on command-line arguments."""
    # Set up logging
    log_level = "DEBUG" if args.verbose else "ERROR" if args.quiet else "INFO"
    logger = get_logger("test-cli", level=log_level)
    
    # Validate project root
    if not args.project_root.exists():
        logger.error(f"Project root does not exist: {args.project_root}")
        return 1
    
    # Initialize orchestrator
    orchestrator = ACGSTestOrchestrator(args.project_root)
    orchestrator.register_standard_suites()
    
    # Handle list command
    if args.list:
        suites = get_standard_suites()
        
        if args.format == "json":
            import json
            suite_info = [
                {
                    "name": suite.name,
                    "description": suite.description,
                    "critical": suite.critical,
                    "coverage_enabled": suite.coverage_enabled,
                    "timeout": suite.timeout
                }
                for suite in suites
            ]
            output = json.dumps(suite_info, indent=2)
        else:
            output = "Available Test Suites:\n"
            for suite in suites:
                tags = []
                if suite.critical:
                    tags.append("critical")
                if suite.coverage_enabled:
                    tags.append("coverage")
                
                tag_str = f" [{', '.join(tags)}]" if tags else ""
                output += f"  {suite.name}: {suite.description}{tag_str}\n"
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            logger.success(f"Suite list written to {args.output}")
        else:
            print(output)
        
        return 0
    
    # Determine which suites to run
    suite_filter = None
    
    if args.suite:
        suite_filter = [args.suite]
    elif args.suites:
        suite_filter = args.suites
    elif not args.all:
        logger.error("Must specify --all, --suite, --suites, or --list")
        return 1
    
    # Apply additional filters
    if suite_filter or args.critical_only or args.with_coverage or args.fast:
        available_suites = [s.name for s in orchestrator.test_suites]
        
        if suite_filter:
            # Validate suite names
            invalid_suites = [s for s in suite_filter if s not in available_suites]
            if invalid_suites:
                logger.error(f"Invalid test suites: {invalid_suites}")
                logger.error(f"Available suites: {available_suites}")
                return 1
        
        # Apply filters
        standard_suites = get_standard_suites()
        filtered_suites = filter_suites(standard_suites, args)
        
        if suite_filter:
            filtered_suites = [s for s in filtered_suites if s.name in suite_filter]
        
        suite_filter = [s.name for s in filtered_suites]
        
        if not suite_filter:
            logger.warning("No test suites match the specified filters")
            return 0
        
        logger.info(f"Running filtered suites: {suite_filter}")
    
    # Apply global timeout override
    if args.timeout:
        for suite in orchestrator.test_suites:
            suite.timeout = args.timeout
        logger.info(f"Set global timeout to {args.timeout} seconds")
    
    # Add custom pytest arguments
    if args.pytest_args:
        pytest_args = args.pytest_args.split()
        for suite in orchestrator.test_suites:
            suite.command.extend(pytest_args)
        logger.info(f"Added pytest arguments: {args.pytest_args}")
    
    try:
        # Run test orchestration
        result = await orchestrator.run_all_suites(
            suite_filter=suite_filter,
            fail_fast=args.fail_fast,
            parallel=args.parallel
        )
        
        # Handle output
        if args.format == "json":
            import json
            output = json.dumps(result.to_dict(), indent=2)
        else:
            # Text output handled by orchestrator.print_summary()
            output = None
        
        if args.output:
            if output:
                with open(args.output, 'w') as f:
                    f.write(output)
                logger.success(f"Test results written to {args.output}")
            else:
                # Save JSON report for text format too
                orchestrator.save_report(result, args.output)
        else:
            if output:
                print(output)
            else:
                # Print text summary to console
                orchestrator.print_summary(result)
        
        # Return appropriate exit code
        return 0 if result.overall_success else 1
        
    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Run tests
    try:
        exit_code = asyncio.run(run_tests(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest execution interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()