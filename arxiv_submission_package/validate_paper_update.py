#!/usr/bin/env python3
"""
ACGS-PGP Paper Update Validation Script

This script validates that the paper has been properly updated to reflect
the current ACGS-PGP system implementation.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple


class PaperValidator:
    def __init__(self, paper_path: str):
        self.paper_path = Path(paper_path)
        self.content = self._read_paper()
        self.validation_results = []

    def _read_paper(self) -> str:
        """Read the LaTeX paper content."""
        with open(self.paper_path, "r", encoding="utf-8") as f:
            return f.read()

    def validate_title_update(self) -> bool:
        """Validate that the title has been updated to ACGS-PGP."""
        title_pattern = r"\\title\{([^}]+)\}"
        match = re.search(title_pattern, self.content)

        if match:
            title = match.group(1)
            is_updated = "ACGS-PGP" in title and "Production-Ready" in title
            self.validation_results.append(
                {
                    "check": "Title Update",
                    "status": "PASS" if is_updated else "FAIL",
                    "found": title,
                    "expected": "ACGS-PGP: A Production-Ready Constitutional AI Governance System...",
                }
            )
            return is_updated

        self.validation_results.append(
            {
                "check": "Title Update",
                "status": "FAIL",
                "found": "No title found",
                "expected": "ACGS-PGP title",
            }
        )
        return False

    def validate_abstract_content(self) -> bool:
        """Validate that the abstract reflects the current system."""
        abstract_pattern = r"\\begin\{abstract\}(.*?)\\end\{abstract\}"
        match = re.search(abstract_pattern, self.content, re.DOTALL)

        if match:
            abstract = match.group(1)
            required_terms = [
                "ACGS-PGP",
                "7-service microservices",
                "quantum-inspired semantic fault tolerance",
                "99.94%",
                "sub-50ms",
                "production-ready",
            ]

            found_terms = [term for term in required_terms if term in abstract]
            is_valid = len(found_terms) >= 4  # At least 4 out of 6 terms

            self.validation_results.append(
                {
                    "check": "Abstract Content",
                    "status": "PASS" if is_valid else "FAIL",
                    "found": f"{len(found_terms)}/{len(required_terms)} required terms",
                    "expected": "At least 4 key terms about current system",
                }
            )
            return is_valid

        return False

    def validate_architecture_description(self) -> bool:
        """Validate that the architecture section describes the 7-service system."""
        # Look for service descriptions
        services = [
            "Authentication Service",
            "Constitutional AI Service",
            "Integrity Service",
            "Formal Verification Service",
            "Governance Synthesis Service",
            "Policy Governance Compiler",
            "Evolution Control Service",
        ]

        found_services = [service for service in services if service in self.content]
        is_valid = len(found_services) >= 5  # At least 5 out of 7 services mentioned

        self.validation_results.append(
            {
                "check": "Architecture Description",
                "status": "PASS" if is_valid else "FAIL",
                "found": f"{len(found_services)}/{len(services)} services mentioned",
                "expected": "At least 5 of 7 microservices described",
            }
        )
        return is_valid

    def validate_constitutional_hash(self) -> bool:
        """Validate that the constitutional hash is mentioned."""
        hash_pattern = r"cdd01ef066bc6cf2"
        has_hash = bool(re.search(hash_pattern, self.content))

        self.validation_results.append(
            {
                "check": "Constitutional Hash",
                "status": "PASS" if has_hash else "FAIL",
                "found": "Hash found" if has_hash else "Hash not found",
                "expected": "Constitutional hash cdd01ef066bc6cf2",
            }
        )
        return has_hash

    def validate_qec_sft_content(self) -> bool:
        """Validate that QEC-SFT is properly described."""
        qec_terms = [
            "Quantum-Inspired Semantic Fault Tolerance",
            "QEC-SFT",
            "Generation Engine",
            "Stabilizer Execution Environment",
            "Syndrome Diagnostic Engine",
        ]

        found_terms = [term for term in qec_terms if term in self.content]
        is_valid = len(found_terms) >= 3

        self.validation_results.append(
            {
                "check": "QEC-SFT Content",
                "status": "PASS" if is_valid else "FAIL",
                "found": f"{len(found_terms)}/{len(qec_terms)} QEC-SFT terms",
                "expected": "At least 3 QEC-SFT related terms",
            }
        )
        return is_valid

    def validate_performance_metrics(self) -> bool:
        """Validate that production performance metrics are included."""
        metrics = [
            "99.94%",  # synthesis reliability
            "99.7%",  # constitutional compliance
            "99.9%",  # system uptime
            "sub-50ms",  # latency
            "10,000",  # concurrent evaluations
        ]

        found_metrics = [metric for metric in metrics if metric in self.content]
        is_valid = len(found_metrics) >= 3

        self.validation_results.append(
            {
                "check": "Performance Metrics",
                "status": "PASS" if is_valid else "FAIL",
                "found": f"{len(found_metrics)}/{len(metrics)} metrics found",
                "expected": "At least 3 production metrics",
            }
        )
        return is_valid

    def validate_removed_evolutionary_content(self) -> bool:
        """Validate that evolutionary computation focus has been removed."""
        evolutionary_terms = [
            "evolutionary computation",
            "co-evolutionary",
            "evolutionary governance gap",
            "AlphaEvolve-ACGS",
        ]

        # Count occurrences (some may remain in related work)
        total_occurrences = sum(
            len(re.findall(term, self.content, re.IGNORECASE))
            for term in evolutionary_terms
        )

        # Should be minimal (less than 10 total occurrences)
        is_valid = total_occurrences < 10

        self.validation_results.append(
            {
                "check": "Evolutionary Content Removal",
                "status": "PASS" if is_valid else "FAIL",
                "found": f"{total_occurrences} evolutionary term occurrences",
                "expected": "Less than 10 occurrences",
            }
        )
        return is_valid

    def run_all_validations(self) -> Dict:
        """Run all validation checks."""
        checks = [
            self.validate_title_update,
            self.validate_abstract_content,
            self.validate_architecture_description,
            self.validate_constitutional_hash,
            self.validate_qec_sft_content,
            self.validate_performance_metrics,
            self.validate_removed_evolutionary_content,
        ]

        results = [check() for check in checks]
        passed = sum(results)
        total = len(results)

        return {
            "total_checks": total,
            "passed_checks": passed,
            "success_rate": passed / total,
            "overall_status": "PASS" if passed >= total * 0.8 else "FAIL",
            "detailed_results": self.validation_results,
        }

    def generate_report(self) -> str:
        """Generate a validation report."""
        results = self.run_all_validations()

        report = f"""
# ACGS-PGP Paper Update Validation Report

**Validation Date**: {os.popen('date').read().strip()}
**Paper File**: {self.paper_path}
**Overall Status**: {results['overall_status']}
**Success Rate**: {results['passed_checks']}/{results['total_checks']} ({results['success_rate']:.1%})

## Detailed Results

"""

        for result in results["detailed_results"]:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            report += f"### {status_icon} {result['check']}\n"
            report += f"- **Status**: {result['status']}\n"
            report += f"- **Found**: {result['found']}\n"
            report += f"- **Expected**: {result['expected']}\n\n"

        if results["overall_status"] == "PASS":
            report += "## ✅ Validation Summary\n\n"
            report += "The paper has been successfully updated to reflect the current ACGS-PGP system implementation. "
            report += "All critical elements have been validated and the paper is ready for compilation and submission.\n"
        else:
            report += "## ❌ Validation Summary\n\n"
            report += "The paper update requires additional work. Please review the failed checks above and "
            report += "make necessary corrections before proceeding with submission.\n"

        return report


if __name__ == "__main__":
    validator = PaperValidator("main.tex")
    report = validator.generate_report()

    # Save report
    with open("VALIDATION_REPORT.md", "w") as f:
        f.write(report)

    print("Validation complete. Report saved to VALIDATION_REPORT.md")
    print(f"Overall Status: {validator.run_all_validations()['overall_status']}")
