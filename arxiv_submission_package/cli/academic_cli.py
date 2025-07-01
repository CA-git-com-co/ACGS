#!/usr/bin/env python3
"""
Academic Submission CLI Tool

A comprehensive command-line interface for academic paper submission preparation,
validation, and optimization for arXiv and other venues.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from quality_assurance.compliance_checker import (
        ComplianceChecker,
        generate_compliance_report,
    )
    from quality_assurance.submission_validator import (
        SubmissionValidator,
        generate_validation_report,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running from the correct directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class AcademicCLI:
    """Main CLI application for academic submission tools."""

    def __init__(self):
        self.parser = self._create_parser()
        self.supported_venues = ["arxiv", "ieee", "acm"]

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            description="Academic Submission CLI Tool - Validate and optimize academic papers for submission",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s validate /path/to/paper/
  %(prog)s validate /path/to/paper/ --venue arxiv --output report.md
  %(prog)s compliance /path/to/paper/ --venue ieee
  %(prog)s optimize /path/to/paper/ --fix-warnings
  %(prog)s package /path/to/paper/ --output submission.zip
  %(prog)s status /path/to/paper/
            """,
        )

        # Global options
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )

        parser.add_argument(
            "--quiet", "-q", action="store_true", help="Suppress non-essential output"
        )

        parser.add_argument("--config", type=str, help="Path to configuration file")

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate", help="Validate academic submission"
        )
        validate_parser.add_argument(
            "path", type=str, help="Path to submission directory"
        )
        validate_parser.add_argument(
            "--venue",
            choices=self.supported_venues,
            default="arxiv",
            help="Target venue for submission (default: arxiv)",
        )
        validate_parser.add_argument(
            "--output", "-o", type=str, help="Output file for validation report"
        )
        validate_parser.add_argument(
            "--format",
            choices=["markdown", "json", "html"],
            default="markdown",
            help="Output format for report (default: markdown)",
        )

        # Compliance command
        compliance_parser = subparsers.add_parser(
            "compliance", help="Check venue-specific compliance"
        )
        compliance_parser.add_argument(
            "path", type=str, help="Path to submission directory"
        )
        compliance_parser.add_argument(
            "--venue",
            choices=self.supported_venues,
            default="arxiv",
            help="Target venue for compliance check (default: arxiv)",
        )
        compliance_parser.add_argument(
            "--output", "-o", type=str, help="Output file for compliance report"
        )

        # Optimize command
        optimize_parser = subparsers.add_parser(
            "optimize", help="Optimize submission for better compliance"
        )
        optimize_parser.add_argument(
            "path", type=str, help="Path to submission directory"
        )
        optimize_parser.add_argument(
            "--fix-warnings",
            action="store_true",
            help="Automatically fix common warnings",
        )
        optimize_parser.add_argument(
            "--backup",
            action="store_true",
            default=True,
            help="Create backup before optimization (default: True)",
        )

        # Package command
        package_parser = subparsers.add_parser(
            "package", help="Package submission for upload"
        )
        package_parser.add_argument(
            "path", type=str, help="Path to submission directory"
        )
        package_parser.add_argument(
            "--output", "-o", type=str, help="Output file for packaged submission"
        )
        package_parser.add_argument(
            "--venue",
            choices=self.supported_venues,
            default="arxiv",
            help="Target venue for packaging (default: arxiv)",
        )

        # Status command
        status_parser = subparsers.add_parser(
            "status", help="Show submission status and quick overview"
        )
        status_parser.add_argument(
            "path", type=str, help="Path to submission directory"
        )

        # Init command
        init_parser = subparsers.add_parser(
            "init", help="Initialize new academic submission"
        )
        init_parser.add_argument(
            "path", type=str, help="Path for new submission directory"
        )
        init_parser.add_argument(
            "--template",
            choices=["basic", "arxiv", "ieee", "acm"],
            default="basic",
            help="Template to use for initialization (default: basic)",
        )

        # Help command
        help_parser = subparsers.add_parser(
            "help", help="Show detailed help for commands"
        )
        help_parser.add_argument(
            "topic",
            nargs="?",
            choices=["validate", "compliance", "optimize", "package", "status", "init"],
            help="Show help for specific command",
        )

        return parser

    def run(self, args: list[str] | None = None) -> int:
        """Run the CLI application."""
        try:
            parsed_args = self.parser.parse_args(args)

            # Configure logging based on verbosity
            if parsed_args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            elif parsed_args.quiet:
                logging.getLogger().setLevel(logging.WARNING)

            # Load configuration if provided
            config = self._load_config(parsed_args.config) if parsed_args.config else {}

            # Execute command
            if parsed_args.command == "validate":
                return self._validate_command(parsed_args, config)
            if parsed_args.command == "compliance":
                return self._compliance_command(parsed_args, config)
            if parsed_args.command == "optimize":
                return self._optimize_command(parsed_args, config)
            if parsed_args.command == "package":
                return self._package_command(parsed_args, config)
            if parsed_args.command == "status":
                return self._status_command(parsed_args, config)
            if parsed_args.command == "init":
                return self._init_command(parsed_args, config)
            self.parser.print_help()
            return 1

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 130
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if parsed_args.verbose if "parsed_args" in locals() else False:
                import traceback

                traceback.print_exc()
            return 1

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config file {config_path}: {e}")
            return {}

    def _validate_command(self, args, config: dict[str, Any]) -> int:
        """Execute validate command."""
        submission_path = Path(args.path)

        if not submission_path.exists():
            logger.error(f"Submission path does not exist: {submission_path}")
            return 1

        if not submission_path.is_dir():
            logger.error(f"Submission path is not a directory: {submission_path}")
            return 1

        logger.info(f"Validating submission: {submission_path}")
        logger.info(f"Target venue: {args.venue}")

        try:
            # Run validation
            validator = SubmissionValidator(submission_path)
            report = validator.validate_submission()

            # Generate output
            if args.output:
                output_path = args.output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"validation_report_{timestamp}.{args.format.replace('markdown', 'md')}"

            if args.format == "markdown":
                report_file = generate_validation_report(report, output_path)
                logger.info(f"Validation report saved to: {report_file}")
            elif args.format == "json":
                with open(output_path, "w") as f:
                    json.dump(
                        {
                            "submission_path": report.submission_path,
                            "timestamp": report.timestamp,
                            "overall_status": report.overall_status,
                            "compliance_score": report.compliance_score,
                            "validation_results": [
                                {
                                    "check_name": r.check_name,
                                    "status": r.status,
                                    "message": r.message,
                                    "details": r.details,
                                    "timestamp": r.timestamp,
                                }
                                for r in report.validation_results
                            ],
                            "recommendations": report.recommendations,
                        },
                        f,
                        indent=2,
                    )
                logger.info(f"Validation report (JSON) saved to: {output_path}")

            # Print summary
            self._print_validation_summary(report)

            # Return appropriate exit code
            fail_count = sum(1 for r in report.validation_results if r.status == "FAIL")
            return 0 if fail_count == 0 else 1

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 1

    def _compliance_command(self, args, config: dict[str, Any]) -> int:
        """Execute compliance command."""
        submission_path = Path(args.path)

        if not submission_path.exists():
            logger.error(f"Submission path does not exist: {submission_path}")
            return 1

        logger.info(f"Checking {args.venue.upper()} compliance: {submission_path}")

        try:
            # Run compliance check
            checker = ComplianceChecker()
            results = checker.check_compliance(str(submission_path), args.venue)

            # Generate output
            if args.output:
                output_path = args.output
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"compliance_report_{args.venue}_{timestamp}.md"

            report_file = generate_compliance_report(results, args.venue, output_path)
            logger.info(f"Compliance report saved to: {report_file}")

            # Print summary
            self._print_compliance_summary(results, args.venue)

            # Return appropriate exit code
            fail_count = sum(1 for r in results if r.status == "FAIL")
            return 0 if fail_count == 0 else 1

        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return 1

    def _optimize_command(self, args, config: dict[str, Any]) -> int:
        """Execute optimize command."""
        logger.info("Optimization feature coming soon!")
        logger.info("This will include automatic fixing of common LaTeX issues,")
        logger.info("bibliography optimization, and figure compression.")
        return 0

    def _package_command(self, args, config: dict[str, Any]) -> int:
        """Execute package command."""
        logger.info("Packaging feature coming soon!")
        logger.info("This will create submission-ready archives for various venues.")
        return 0

    def _status_command(self, args, config: dict[str, Any]) -> int:
        """Execute status command."""
        submission_path = Path(args.path)

        if not submission_path.exists():
            logger.error(f"Submission path does not exist: {submission_path}")
            return 1

        print("\n📄 Academic Submission Status")
        print(f"{'=' * 50}")
        print(f"Path: {submission_path}")
        print(
            f"Last modified: {datetime.fromtimestamp(submission_path.stat().st_mtime)}"
        )

        # Quick file check
        files = list(submission_path.glob("*"))
        print(f"Files: {len(files)}")

        # Check for key files
        key_files = {
            "main.tex": submission_path / "main.tex",
            "README": next(submission_path.glob("README*"), None),
            "Bibliography": next(submission_path.glob("*.bib"), None),
            "Figures": (
                submission_path / "figs"
                if (submission_path / "figs").exists()
                else None
            ),
        }

        print("\n📋 Key Files:")
        for name, path in key_files.items():
            status = "✅" if path and path.exists() else "❌"
            print(f"  {status} {name}")

        # Quick validation
        try:
            validator = SubmissionValidator(submission_path)
            report = validator.validate_submission()

            print("\n🔍 Quick Validation:")
            print(f"  Overall Status: {report.overall_status}")
            print(f"  Compliance Score: {report.compliance_score:.1f}%")

            fail_count = sum(1 for r in report.validation_results if r.status == "FAIL")
            warning_count = sum(
                1 for r in report.validation_results if r.status == "WARNING"
            )

            if fail_count > 0:
                print(f"  ❌ {fail_count} critical issues")
            if warning_count > 0:
                print(f"  ⚠️  {warning_count} warnings")
            if fail_count == 0 and warning_count == 0:
                print("  ✅ No issues found")

        except Exception as e:
            print(f"  ❌ Validation error: {e}")

        print()
        return 0

    def _init_command(self, args, config: dict[str, Any]) -> int:
        """Execute init command."""
        logger.info("Initialization feature coming soon!")
        logger.info("This will create new submission templates for various venues.")
        return 0

    def _print_validation_summary(self, report):
        """Print validation summary to console."""
        print("\n📊 Validation Summary")
        print(f"{'=' * 50}")
        print(f"Overall Status: {report.overall_status}")
        print(f"Compliance Score: {report.compliance_score:.1f}%")

        # Count results by status
        pass_count = sum(1 for r in report.validation_results if r.status == "PASS")
        warning_count = sum(
            1 for r in report.validation_results if r.status == "WARNING"
        )
        fail_count = sum(1 for r in report.validation_results if r.status == "FAIL")

        print("\nResults:")
        print(f"  ✅ Passed: {pass_count}")
        print(f"  ⚠️  Warnings: {warning_count}")
        print(f"  ❌ Failed: {fail_count}")

        # Show failed checks
        if fail_count > 0:
            print("\n❌ Critical Issues:")
            for result in report.validation_results:
                if result.status == "FAIL":
                    print(f"  • {result.check_name}: {result.message}")

        # Show recommendations
        if report.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):  # Show top 5
                print(f"  {i}. {rec}")
            if len(report.recommendations) > 5:
                print(f"  ... and {len(report.recommendations) - 5} more")

    def _print_compliance_summary(self, results, venue):
        """Print compliance summary to console."""
        print(f"\n📋 {venue.upper()} Compliance Summary")
        print(f"{'=' * 50}")

        # Count results by status
        pass_count = sum(1 for r in results if r.status == "PASS")
        warning_count = sum(1 for r in results if r.status == "WARNING")
        fail_count = sum(1 for r in results if r.status == "FAIL")

        compliance_rate = (pass_count / len(results) * 100) if results else 0

        print(f"Compliance Rate: {compliance_rate:.1f}%")
        print("\nResults:")
        print(f"  ✅ Passed: {pass_count}")
        print(f"  ⚠️  Warnings: {warning_count}")
        print(f"  ❌ Failed: {fail_count}")

        # Show failed checks
        if fail_count > 0:
            print("\n❌ Compliance Issues:")
            for result in results:
                if result.status == "FAIL":
                    print(f"  • {result.rule_id}: {result.message}")


def main():
    """Main entry point for the CLI."""
    cli = AcademicCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
