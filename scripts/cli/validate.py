#!/usr/bin/env python3
"""
ACGS Validation CLI
Constitutional Hash: cdd01ef066bc6cf2

Command-line interface for ACGS validation framework.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_logger, set_config, Config
from validation import (
    ACGSValidator,
    ConstitutionalComplianceCheck,
    EnvironmentConfigCheck,
    InfrastructureIntegrationCheck,
    MonitoringCheck,
    PerformanceTargetsCheck,
    PortNumbersCheck,
)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="ACGS Validation Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} --all                    # Run all validation checks
  {sys.argv[0]} --check constitutional   # Run specific check
  {sys.argv[0]} --list                   # List available checks
  {sys.argv[0]} --parallel --timeout 60  # Run in parallel with timeout

Constitutional Hash: {CONSTITUTIONAL_HASH}
        """
    )
    
    # Check selection
    check_group = parser.add_mutually_exclusive_group()
    check_group.add_argument(
        "--all", 
        action="store_true",
        help="Run all validation checks"
    )
    check_group.add_argument(
        "--check",
        type=str,
        help="Run specific validation check by name"
    )
    check_group.add_argument(
        "--list",
        action="store_true", 
        help="List all available validation checks"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run checks in parallel (default: sequential)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent checks when running in parallel (default: 5)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout for individual checks in seconds (default: 60)"
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
        "--config",
        type=Path,
        help="Configuration file path"
    )
    
    return parser


def get_all_checks() -> List:
    """Get all available validation checks."""
    return [
        ConstitutionalComplianceCheck(),
        EnvironmentConfigCheck(),
        InfrastructureIntegrationCheck(),
        MonitoringCheck(),
        PerformanceTargetsCheck(),
        PortNumbersCheck(),
    ]


def format_text_output(summary, verbose: bool = False) -> str:
    """Format validation summary as text."""
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("ACGS Validation Results")
    output.append(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    output.append("=" * 60)
    
    # Summary
    output.append(f"Total Checks: {summary.total_checks}")
    output.append(f"Passed: {summary.passed_checks}")
    output.append(f"Failed: {summary.failed_checks}")
    output.append(f"Success Rate: {summary.success_rate:.1f}%")
    output.append(f"Duration: {summary.total_duration_ms:.0f}ms")
    output.append("")
    
    # Overall result
    if summary.all_passed:
        output.append("🎉 All validation checks PASSED!")
    else:
        output.append("❌ Some validation checks FAILED!")
    
    output.append("")
    
    # Individual results
    for result in summary.results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        output.append(f"{status} {result.check_name} ({result.duration_ms:.0f}ms)")
        output.append(f"    {result.message}")
        
        if verbose and result.details:
            output.append("    Details:")
            for key, value in result.details.items():
                if isinstance(value, (list, dict)):
                    output.append(f"      {key}: {json.dumps(value, indent=8)}")
                else:
                    output.append(f"      {key}: {value}")
        
        if result.error:
            output.append(f"    Error: {result.error}")
        
        output.append("")
    
    return "\n".join(output)


async def run_validation(args) -> int:
    """Run validation based on command-line arguments."""
    # Set up logging
    log_level = "DEBUG" if args.verbose else "ERROR" if args.quiet else "INFO"
    logger = get_logger("validate-cli", level=log_level)
    
    # Load configuration if specified
    if args.config:
        try:
            config = Config.from_file(args.config)
            set_config(config)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return 1
    
    # Create validator
    validator = ACGSValidator()
    
    try:
        async with validator:
            # Handle list command
            if args.list:
                all_checks = get_all_checks()
                validator.add_checks(all_checks)
                
                checks_info = validator.list_checks()
                
                if args.format == "json":
                    output = json.dumps(checks_info, indent=2)
                else:
                    output = "Available Validation Checks:\n"
                    for check in checks_info:
                        output += f"  {check['name']}: {check['description']}\n"
                
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(output)
                    logger.success(f"Check list written to {args.output}")
                else:
                    print(output)
                
                return 0
            
            # Add checks based on arguments
            if args.all:
                validator.add_checks(get_all_checks())
                logger.info("Running all validation checks")
            elif args.check:
                all_checks = get_all_checks()
                check_found = False
                for check in all_checks:
                    if check.name == args.check:
                        validator.add_check(check)
                        check_found = True
                        break
                
                if not check_found:
                    logger.error(f"Unknown validation check: {args.check}")
                    available = [c.name for c in all_checks]
                    logger.error(f"Available checks: {', '.join(available)}")
                    return 1
                
                logger.info(f"Running validation check: {args.check}")
            else:
                logger.error("Must specify --all, --check, or --list")
                return 1
            
            # Run validation
            summary = await validator.run_all(
                parallel=args.parallel,
                max_concurrent=args.max_concurrent
            )
            
            # Format output
            if args.format == "json":
                output = json.dumps(summary.to_dict(), indent=2)
            else:
                output = format_text_output(summary, args.verbose)
            
            # Write output
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                logger.success(f"Validation results written to {args.output}")
            else:
                print(output)
            
            # Return appropriate exit code
            return 0 if summary.all_passed else 1
            
    except KeyboardInterrupt:
        logger.warning("Validation interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Run validation
    try:
        exit_code = asyncio.run(run_validation(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nValidation interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()