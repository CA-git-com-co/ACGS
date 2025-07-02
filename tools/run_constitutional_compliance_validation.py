#!/usr/bin/env python3
"""
Constitutional Compliance Validation Runner

Executes comprehensive constitutional compliance validation for the ACGS-PGP system.
Validates hash integrity, compliance scoring, audit trails, and DGM safety patterns.

Constitutional Hash: cdd01ef066bc6cf2
Compliance Targets: >95% constitutional compliance, 100% hash integrity, 98% audit coverage
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "tests" / "validation"))

try:
    from constitutional_compliance_validation import ConstitutionalComplianceValidator
except ImportError as e:
    print(f"❌ Failed to import constitutional compliance validation module: {e}")
    print("Please ensure all dependencies are installed and paths are correct.")
    sys.exit(1)


def main():
    """Main function for constitutional compliance validation runner."""
    parser = argparse.ArgumentParser(
        description="Constitutional Compliance Validation Runner"
    )
    parser.add_argument("--output", type=str, help="Output file for validation report")
    parser.add_argument(
        "--constitutional-hash",
        type=str,
        default="cdd01ef066bc6cf2",
        help="Constitutional hash for verification",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("🔒 ACGS-PGP Constitutional Compliance Validation")
    print("=" * 60)
    print(f"Constitutional Hash: {args.constitutional_hash}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    try:
        # Initialize validator
        validator = ConstitutionalComplianceValidator(
            constitutional_hash=args.constitutional_hash
        )

        # Run comprehensive compliance validation
        print("\n🔍 Starting comprehensive constitutional compliance validation...")
        validation_report = validator.run_comprehensive_compliance_validation()

        # Check for errors
        if "error" in validation_report:
            print(f"❌ Validation failed: {validation_report['error']}")
            sys.exit(1)

        # Save report if output file specified
        if args.output:
            output_file = Path(args.output)
            with open(output_file, "w") as f:
                json.dump(validation_report, f, indent=2, default=str)
            print(f"\n📄 Compliance validation report saved to: {output_file}")
        else:
            # Generate default output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = (
                project_root / f"constitutional_compliance_report_{timestamp}.json"
            )
            with open(output_file, "w") as f:
                json.dump(validation_report, f, indent=2, default=str)
            print(f"\n📄 Compliance validation report saved to: {output_file}")

        # Check overall validation status
        validation_summary = validation_report.get("validation_summary", {})
        all_targets_met = validation_summary.get("all_targets_met", False)
        constitutional_hash_verified = validation_summary.get(
            "constitutional_hash_verified", False
        )

        # Validate constitutional hash
        if not constitutional_hash_verified:
            print("\n❌ CRITICAL: Constitutional hash verification failed!")
            print("System does not meet constitutional compliance requirements.")
            sys.exit(1)

        if all_targets_met:
            print("\n🎉 SUCCESS: All constitutional compliance targets met!")
            print("✅ System meets all constitutional compliance requirements")
            print("✅ Constitutional hash integrity verified")
            print("✅ Ready for production deployment")
            sys.exit(0)
        else:
            print("\n⚠️  WARNING: Some constitutional compliance targets not met")
            print("❌ Review compliance results before production deployment")

            # Print specific failures
            overall_compliance = validation_report.get("overall_compliance", {})
            targets_met = overall_compliance.get("targets_met", {})

            for target, met in targets_met.items():
                if not met:
                    print(f"   - {target}: Target not met")

            # Print recommendations
            recommendations = validation_report.get("recommendations", [])
            if recommendations:
                print("\n📋 Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                    print(f"   {i}. {rec}")

            sys.exit(1)

    except Exception as e:
        print(f"❌ Constitutional compliance validation failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
