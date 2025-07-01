#!/usr/bin/env python3
"""
Academic Submission Compliance Checker

This module provides specialized compliance checking for various academic
venues including arXiv, IEEE, ACM, and other major publishers.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComplianceRule:
    """Represents a compliance rule for academic submissions."""

    rule_id: str
    venue: str
    category: str
    description: str
    severity: str  # CRITICAL, WARNING, INFO
    check_function: str
    parameters: Dict[str, Any] = None


@dataclass
class ComplianceResult:
    """Result of a compliance check."""

    rule_id: str
    status: str  # PASS, FAIL, WARNING
    message: str
    details: Optional[Dict[str, Any]] = None


class ComplianceChecker:
    """Comprehensive compliance checker for academic submissions."""

    def __init__(self):
        self.rules = self._load_compliance_rules()

    def _load_compliance_rules(self) -> Dict[str, List[ComplianceRule]]:
        """Load compliance rules for different venues."""
        return {
            "arxiv": [
                ComplianceRule(
                    rule_id="ARXIV_001",
                    venue="arXiv",
                    category="file_size",
                    description="Submission must be under 50MB",
                    severity="CRITICAL",
                    check_function="check_file_size",
                    parameters={"max_size_mb": 50},
                ),
                ComplianceRule(
                    rule_id="ARXIV_002",
                    venue="arXiv",
                    category="file_types",
                    description="No executable or archive files",
                    severity="CRITICAL",
                    check_function="check_prohibited_files",
                    parameters={
                        "prohibited_extensions": [".exe", ".zip", ".rar", ".tar.gz"]
                    },
                ),
                ComplianceRule(
                    rule_id="ARXIV_003",
                    venue="arXiv",
                    category="structure",
                    description="Must have title, author, and abstract",
                    severity="CRITICAL",
                    check_function="check_required_elements",
                ),
                ComplianceRule(
                    rule_id="ARXIV_004",
                    venue="arXiv",
                    category="bibliography",
                    description="Bibliography should use standard format",
                    severity="WARNING",
                    check_function="check_bibliography_format",
                ),
            ],
            "ieee": [
                ComplianceRule(
                    rule_id="IEEE_001",
                    venue="IEEE",
                    category="format",
                    description="Must use IEEE template",
                    severity="CRITICAL",
                    check_function="check_ieee_template",
                ),
                ComplianceRule(
                    rule_id="IEEE_002",
                    venue="IEEE",
                    category="length",
                    description="Page limit compliance",
                    severity="CRITICAL",
                    check_function="check_page_limit",
                    parameters={"max_pages": 8},
                ),
                ComplianceRule(
                    rule_id="IEEE_003",
                    venue="IEEE",
                    category="figures",
                    description="Figures must be high resolution",
                    severity="WARNING",
                    check_function="check_figure_quality",
                ),
            ],
            "acm": [
                ComplianceRule(
                    rule_id="ACM_001",
                    venue="ACM",
                    category="format",
                    description="Must use ACM template",
                    severity="CRITICAL",
                    check_function="check_acm_template",
                ),
                ComplianceRule(
                    rule_id="ACM_002",
                    venue="ACM",
                    category="ccs",
                    description="Must include CCS concepts",
                    severity="CRITICAL",
                    check_function="check_ccs_concepts",
                ),
                ComplianceRule(
                    rule_id="ACM_003",
                    venue="ACM",
                    category="keywords",
                    description="Must include keywords",
                    severity="WARNING",
                    check_function="check_keywords",
                ),
            ],
        }

    def check_compliance(
        self, submission_path: str, venue: str = "arxiv"
    ) -> List[ComplianceResult]:
        """Check compliance for a specific venue."""
        submission_path = Path(submission_path)
        results = []

        if venue not in self.rules:
            return [
                ComplianceResult(
                    rule_id="UNKNOWN_VENUE",
                    status="FAIL",
                    message=f"Unknown venue: {venue}",
                )
            ]

        for rule in self.rules[venue]:
            try:
                result = self._execute_check(rule, submission_path)
                results.append(result)
            except Exception as e:
                results.append(
                    ComplianceResult(
                        rule_id=rule.rule_id,
                        status="FAIL",
                        message=f"Check execution error: {str(e)}",
                    )
                )

        return results

    def _execute_check(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Execute a specific compliance check."""
        check_method = getattr(self, rule.check_function, None)
        if not check_method:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="FAIL",
                message=f"Check method not implemented: {rule.check_function}",
            )

        return check_method(rule, submission_path)

    def check_file_size(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check total submission file size."""
        total_size = sum(
            f.stat().st_size for f in submission_path.rglob("*") if f.is_file()
        )
        max_size = rule.parameters.get("max_size_mb", 50) * 1024 * 1024

        if total_size <= max_size:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="PASS",
                message=f"File size OK ({total_size/1024/1024:.1f}MB)",
                details={
                    "size_mb": total_size / 1024 / 1024,
                    "limit_mb": max_size / 1024 / 1024,
                },
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="FAIL",
                message=f"File size exceeds limit ({total_size/1024/1024:.1f}MB > {max_size/1024/1024}MB)",
                details={
                    "size_mb": total_size / 1024 / 1024,
                    "limit_mb": max_size / 1024 / 1024,
                },
            )

    def check_prohibited_files(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check for prohibited file types."""
        prohibited_extensions = rule.parameters.get("prohibited_extensions", [])
        prohibited_files = []

        for ext in prohibited_extensions:
            prohibited_files.extend(list(submission_path.rglob(f"*{ext}")))

        if not prohibited_files:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="PASS",
                message="No prohibited file types found",
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="FAIL",
                message=f"Prohibited files found: {[str(f) for f in prohibited_files]}",
                details={"prohibited_files": [str(f) for f in prohibited_files]},
            )

    def check_required_elements(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check for required document elements."""
        main_tex = submission_path / "main.tex"
        if not main_tex.exists():
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="main.tex not found"
            )

        with open(main_tex, "r", encoding="utf-8") as f:
            content = f.read()

        missing_elements = []

        if not re.search(r"\\title\{", content):
            missing_elements.append("title")

        if not re.search(r"\\author\{", content):
            missing_elements.append("author")

        if not re.search(r"\\begin\{abstract\}", content):
            missing_elements.append("abstract")

        if missing_elements:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="FAIL",
                message=f"Missing required elements: {missing_elements}",
                details={"missing_elements": missing_elements},
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="PASS",
                message="All required elements present",
            )

    def check_bibliography_format(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check bibliography format compliance."""
        bib_files = list(submission_path.glob("*.bib"))

        if not bib_files:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="WARNING",
                message="No bibliography file found",
            )

        issues = []
        for bib_file in bib_files:
            with open(bib_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for common formatting issues
            if re.search(r"@\w+\{[^,]*[^,]\s*\n", content):
                issues.append("Missing comma after entry key")

            if "url = {}" in content:
                issues.append("Empty URL fields")

        if issues:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="WARNING",
                message=f"Bibliography formatting issues: {issues}",
                details={"issues": issues},
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id, status="PASS", message="Bibliography format OK"
            )

    def check_ieee_template(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check IEEE template compliance."""
        main_tex = submission_path / "main.tex"
        if not main_tex.exists():
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="main.tex not found"
            )

        with open(main_tex, "r", encoding="utf-8") as f:
            content = f.read()

        ieee_indicators = [
            r"\\documentclass.*IEEEtran",
            r"\\usepackage.*IEEEtran",
            r"IEEEtran",
        ]

        has_ieee_template = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in ieee_indicators
        )

        if has_ieee_template:
            return ComplianceResult(
                rule_id=rule.rule_id, status="PASS", message="IEEE template detected"
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="FAIL",
                message="IEEE template not detected",
            )

    def check_page_limit(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check page limit compliance (requires PDF compilation)."""
        # This is a simplified check - in practice, you'd compile the PDF and count pages
        return ComplianceResult(
            rule_id=rule.rule_id,
            status="WARNING",
            message="Page limit check requires PDF compilation",
        )

    def check_figure_quality(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check figure quality and resolution."""
        fig_dirs = ["figs", "figures", "images"]
        low_res_figures = []

        for fig_dir in fig_dirs:
            fig_path = submission_path / fig_dir
            if fig_path.exists():
                for fig_file in fig_path.glob("*.*"):
                    if fig_file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                        # Simple size-based heuristic (actual implementation would check DPI)
                        if fig_file.stat().st_size < 50000:  # Less than 50KB
                            low_res_figures.append(str(fig_file))

        if low_res_figures:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="WARNING",
                message=f"Potentially low-resolution figures: {low_res_figures}",
                details={"low_res_figures": low_res_figures},
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id,
                status="PASS",
                message="Figure quality check passed",
            )

    def check_acm_template(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check ACM template compliance."""
        main_tex = submission_path / "main.tex"
        if not main_tex.exists():
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="main.tex not found"
            )

        with open(main_tex, "r", encoding="utf-8") as f:
            content = f.read()

        acm_indicators = [
            r"\\documentclass.*acmart",
            r"\\usepackage.*acmart",
            r"acmart",
        ]

        has_acm_template = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in acm_indicators
        )

        if has_acm_template:
            return ComplianceResult(
                rule_id=rule.rule_id, status="PASS", message="ACM template detected"
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="ACM template not detected"
            )

    def check_ccs_concepts(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check for ACM CCS concepts."""
        main_tex = submission_path / "main.tex"
        if not main_tex.exists():
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="main.tex not found"
            )

        with open(main_tex, "r", encoding="utf-8") as f:
            content = f.read()

        ccs_indicators = [r"\\ccsdesc", r"\\begin\{CCSXML\}", r"CCS concepts"]

        has_ccs = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in ccs_indicators
        )

        if has_ccs:
            return ComplianceResult(
                rule_id=rule.rule_id, status="PASS", message="CCS concepts found"
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="CCS concepts not found"
            )

    def check_keywords(
        self, rule: ComplianceRule, submission_path: Path
    ) -> ComplianceResult:
        """Check for keywords section."""
        main_tex = submission_path / "main.tex"
        if not main_tex.exists():
            return ComplianceResult(
                rule_id=rule.rule_id, status="FAIL", message="main.tex not found"
            )

        with open(main_tex, "r", encoding="utf-8") as f:
            content = f.read()

        keyword_indicators = [r"\\keywords\{", r"\\begin\{keywords\}", r"Keywords:"]

        has_keywords = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in keyword_indicators
        )

        if has_keywords:
            return ComplianceResult(
                rule_id=rule.rule_id, status="PASS", message="Keywords found"
            )
        else:
            return ComplianceResult(
                rule_id=rule.rule_id, status="WARNING", message="Keywords not found"
            )


def generate_compliance_report(
    results: List[ComplianceResult], venue: str, output_path: str = None
) -> str:
    """Generate a compliance report."""
    if output_path is None:
        output_path = f"compliance_report_{venue}.md"

    timestamp = datetime.now().isoformat()

    report_content = f"""# {venue.upper()} Compliance Report

**Generated**: {timestamp}  
**Venue**: {venue}

## Compliance Results

"""

    for result in results:
        status_icon = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}.get(
            result.status, "❓"
        )
        report_content += f"### {status_icon} {result.rule_id}\n"
        report_content += f"- **Status**: {result.status}\n"
        report_content += f"- **Message**: {result.message}\n"
        if result.details:
            report_content += f"- **Details**: {json.dumps(result.details, indent=2)}\n"
        report_content += "\n"

    # Summary
    pass_count = sum(1 for r in results if r.status == "PASS")
    warning_count = sum(1 for r in results if r.status == "WARNING")
    fail_count = sum(1 for r in results if r.status == "FAIL")

    report_content += f"""## Summary

- **Total Checks**: {len(results)}
- **Passed**: {pass_count}
- **Warnings**: {warning_count}
- **Failed**: {fail_count}
- **Compliance Rate**: {(pass_count / len(results) * 100):.1f}%

---
Generated by Academic Compliance Checker
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python compliance_checker.py <submission_path> [venue]")
        sys.exit(1)

    submission_path = sys.argv[1]
    venue = sys.argv[2] if len(sys.argv) > 2 else "arxiv"

    checker = ComplianceChecker()
    results = checker.check_compliance(submission_path, venue)

    report_file = generate_compliance_report(results, venue)
    print(f"Compliance check complete. Report saved to: {report_file}")

    fail_count = sum(1 for r in results if r.status == "FAIL")
    if fail_count == 0:
        print("✅ All compliance checks passed!")
    else:
        print(f"❌ {fail_count} compliance issues found.")
