#!/usr/bin/env python3
"""
ACGS Documentation Team Certification Assessment
Constitutional Hash: cdd01ef066bc6cf2

This script provides an interactive certification assessment for team members
to validate their understanding of ACGS documentation procedures.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
PASSING_SCORE = 80
TOTAL_POINTS = 100


class CertificationAssessment:
    def __init__(self):
        self.score = 0
        self.max_score = TOTAL_POINTS
        self.results = []

    def print_header(self):
        """Print assessment header."""
        print("🎓 ACGS Documentation Team Certification Assessment")
        print("=" * 60)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Passing Score: {PASSING_SCORE}%")
        print(f"Total Points: {TOTAL_POINTS}")
        print(f"Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def task_1_constitutional_compliance(self) -> int:
        """Task 1: Constitutional Compliance (25 points)."""
        print("📋 TASK 1: Constitutional Compliance (25 points)")
        print("-" * 50)

        points = 0

        # Create a temporary test file
        test_file = REPO_ROOT / "docs" / "training" / "assessment_test.md"

        print("1.1 Create a documentation file with constitutional hash (10 points)")
        print(f"Create file: {test_file}")
        print("Add proper constitutional hash comment")

        input("Press Enter when you've created the file...")

        # Check if file exists and has constitutional hash
        if test_file.exists():
            points += 5
            print("✅ File created (+5 points)")

            try:
                with open(test_file) as f:
                    content = f.read()
                    if CONSTITUTIONAL_HASH in content:
                        points += 5
                        print("✅ Constitutional hash found (+5 points)")
                    else:
                        print("❌ Constitutional hash missing (0 points)")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
        else:
            print("❌ File not created (0 points)")

        print("\n1.2 Validate compliance using tools (10 points)")
        print("Run: ./tools/validation/quick_validation.sh")

        validation_result = input(
            "Enter the number of files with constitutional hash: "
        )
        try:
            file_count = int(validation_result)
            if file_count >= 110:  # Should be at least 110 with the new test file
                points += 10
                print("✅ Validation successful (+10 points)")
            else:
                points += 5
                print("⚠️ Partial validation (+5 points)")
        except ValueError:
            print("❌ Invalid validation result (0 points)")

        print("\n1.3 API Response Format (5 points)")
        print("Write a JSON response example with constitutional hash:")

        api_response = input("Enter JSON response (one line): ")
        if (
            CONSTITUTIONAL_HASH in api_response
            and "constitutional_hash" in api_response
        ):
            points += 5
            print("✅ Correct API response format (+5 points)")
        else:
            print("❌ Incorrect API response format (0 points)")

        # Cleanup
        if test_file.exists():
            test_file.unlink()

        print(f"\nTask 1 Score: {points}/25")
        self.results.append(("Constitutional Compliance", points, 25))
        return points

    def task_2_documentation_standards(self) -> int:
        """Task 2: Documentation Standards (25 points)."""
        print("\n📋 TASK 2: Documentation Standards (25 points)")
        print("-" * 50)

        points = 0

        print("2.1 API Documentation Structure (15 points)")
        print("List the required sections for API documentation (one per line):")
        print("Enter 'done' when finished")

        required_sections = {
            "service overview",
            "constitutional hash",
            "authentication",
            "endpoints",
            "error handling",
            "performance targets",
            "monitoring",
        }

        user_sections = set()
        while True:
            section = input("Section: ").lower().strip()
            if section == "done":
                break
            user_sections.add(section)

        # Check for key sections
        matches = 0
        for section in required_sections:
            if any(section in user_section for user_section in user_sections):
                matches += 1

        section_points = min(15, (matches / len(required_sections)) * 15)
        points += int(section_points)
        print(
            "✅ Section knowledge:"
            f" {matches}/{len(required_sections)} (+{int(section_points)} points)"
        )

        print("\n2.2 Performance Targets (10 points)")
        print("What are the standard ACGS performance targets?")

        latency = input("P99 Latency target: ").strip()
        throughput = input("Throughput target: ").strip()
        cache_hit = input("Cache hit rate target: ").strip()

        perf_points = 0
        if "5ms" in latency or "≤5ms" in latency:
            perf_points += 3
        if "100" in throughput and "rps" in throughput.lower():
            perf_points += 3
        if "85%" in cache_hit or "≥85%" in cache_hit:
            perf_points += 4

        points += perf_points
        print(f"✅ Performance targets: {perf_points}/10 (+{perf_points} points)")

        print(f"\nTask 2 Score: {points}/25")
        self.results.append(("Documentation Standards", points, 25))
        return points

    def task_3_validation_tools(self) -> int:
        """Task 3: Validation Tools (25 points)."""
        print("\n📋 TASK 3: Validation Tools (25 points)")
        print("-" * 50)

        points = 0

        print("3.1 Tool Knowledge (15 points)")
        tools = {
            "quick validation": "./tools/validation/quick_validation.sh",
            "quarterly audit": "./tools/audit/quarterly_audit.sh",
            "daily metrics": "./tools/metrics/collect_daily_metrics.sh",
            "quality alerts": "python tools/monitoring/quality_alert_monitor.py",
        }

        correct_tools = 0
        for tool_name, expected_command in tools.items():
            user_command = input(f"Command for {tool_name}: ").strip()
            if expected_command in user_command or user_command in expected_command:
                correct_tools += 1
                print("✅ Correct")
            else:
                print(f"❌ Expected: {expected_command}")

        tool_points = int((correct_tools / len(tools)) * 15)
        points += tool_points
        print(f"Tool knowledge: {correct_tools}/{len(tools)} (+{tool_points} points)")

        print("\n3.2 Metric Interpretation (10 points)")
        print("What does an overall quality score of 73% indicate?")
        print("a) EXCELLENT  b) GOOD  c) NEEDS IMPROVEMENT  d) CRITICAL")

        answer = input("Answer (a/b/c/d): ").lower().strip()
        if answer == "c":
            points += 10
            print("✅ Correct interpretation (+10 points)")
        else:
            print("❌ Incorrect. 73% = NEEDS IMPROVEMENT (70-84%)")

        print(f"\nTask 3 Score: {points}/25")
        self.results.append(("Validation Tools", points, 25))
        return points

    def task_4_quality_metrics(self) -> int:
        """Task 4: Quality Metrics (25 points)."""
        print("\n📋 TASK 4: Quality Metrics (25 points)")
        print("-" * 50)

        points = 0

        print("4.1 Metric Weights (10 points)")
        print("What are the weights for overall quality score calculation?")

        weights = {
            "constitutional compliance": 30,
            "link validity": 25,
            "documentation freshness": 25,
            "documentation coverage": 20,
        }

        correct_weights = 0
        for metric, expected_weight in weights.items():
            try:
                user_weight = int(input(f"{metric.title()} weight (%): "))
                if user_weight == expected_weight:
                    correct_weights += 1
                    print("✅ Correct")
                else:
                    print(f"❌ Expected: {expected_weight}%")
            except ValueError:
                print("❌ Invalid number")

        weight_points = int((correct_weights / len(weights)) * 10)
        points += weight_points
        print(
            "Weight knowledge:"
            f" {correct_weights}/{len(weights)} (+{weight_points} points)"
        )

        print("\n4.2 Quality Score Calculation (15 points)")
        print("Calculate overall quality score:")
        print("Constitutional Compliance: 95%")
        print("Link Validity: 100%")
        print("Documentation Freshness: 80%")
        print("Documentation Coverage: 90%")

        try:
            user_score = float(input("Overall Quality Score (%): "))
            expected_score = (95 * 0.30) + (100 * 0.25) + (80 * 0.25) + (90 * 0.20)

            if abs(user_score - expected_score) <= 1:  # Allow 1% tolerance
                points += 15
                print(f"✅ Correct calculation: {expected_score:.1f}% (+15 points)")
            else:
                points += 5
                print(f"❌ Expected: {expected_score:.1f}% (+5 points for attempt)")
        except ValueError:
            print("❌ Invalid calculation (0 points)")

        print(f"\nTask 4 Score: {points}/25")
        self.results.append(("Quality Metrics", points, 25))
        return points

    def generate_certificate(self, total_score: int, passed: bool):
        """Generate certification results."""
        print("\n" + "=" * 60)
        print("🎓 CERTIFICATION RESULTS")
        print("=" * 60)

        for task_name, score, max_score in self.results:
            percentage = (score / max_score) * 100
            status = "✅ PASS" if percentage >= 60 else "❌ FAIL"
            print(
                f"{task_name:25} {score:2d}/{max_score:2d} ({percentage:5.1f}%)"
                f" {status}"
            )

        print("-" * 60)
        final_percentage = (total_score / self.max_score) * 100
        print(
            f"{'TOTAL SCORE':25} {total_score:2d}/{self.max_score:2d} ({final_percentage:5.1f}%)"
        )

        if passed:
            print("\n🎉 CERTIFICATION PASSED!")
            print(f"✅ Score: {final_percentage:.1f}% (Required: {PASSING_SCORE}%)")
            print("✅ You are now certified to contribute to ACGS documentation")
            print("✅ Certification valid for 6 months")
        else:
            print("\n❌ CERTIFICATION FAILED")
            print(f"❌ Score: {final_percentage:.1f}% (Required: {PASSING_SCORE}%)")
            print("❌ Please review training materials and retake assessment")

        # Save results
        results_file = (
            REPO_ROOT
            / "docs"
            / "training"
            / f"certification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        results_data = {
            "date": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_score": total_score,
            "max_score": self.max_score,
            "percentage": final_percentage,
            "passed": passed,
            "passing_score": PASSING_SCORE,
            "task_results": [
                {
                    "task": task_name,
                    "score": score,
                    "max_score": max_score,
                    "percentage": (score / max_score) * 100,
                }
                for task_name, score, max_score in self.results
            ],
        }

        with open(results_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n📄 Results saved to: {results_file}")
        print(f"🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    def run_assessment(self):
        """Run the complete certification assessment."""
        self.print_header()

        print("📚 INSTRUCTIONS:")
        print("- Complete all 4 tasks")
        print("- Each task is worth 25 points")
        print("- You need 80% (80 points) to pass")
        print("- Have validation tools ready to use")
        print()

        input("Press Enter to begin the assessment...")
        print()

        # Run all tasks
        score1 = self.task_1_constitutional_compliance()
        score2 = self.task_2_documentation_standards()
        score3 = self.task_3_validation_tools()
        score4 = self.task_4_quality_metrics()

        total_score = score1 + score2 + score3 + score4
        passed = total_score >= PASSING_SCORE

        self.generate_certificate(total_score, passed)

        return 0 if passed else 1


def main():
    """Main execution function."""
    assessment = CertificationAssessment()
    return assessment.run_assessment()


if __name__ == "__main__":
    sys.exit(main())
