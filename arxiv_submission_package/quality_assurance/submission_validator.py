#!/usr/bin/env python3
"""
Academic Submission Quality Assurance and Validation Pipeline

This module provides comprehensive validation and quality checks for academic
paper submissions, ensuring compliance with arXiv and journal requirements.
"""

import os
import re
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check."""

    check_name: str
    status: str  # PASS, FAIL, WARNING
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SubmissionReport:
    """Comprehensive submission validation report."""

    submission_path: str
    validation_results: List[ValidationResult]
    overall_status: str
    compliance_score: float
    recommendations: List[str]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SubmissionValidator:
    """Comprehensive academic submission validator."""

    def __init__(self, submission_path: str):
        self.submission_path = Path(submission_path)
        self.results: List[ValidationResult] = []
        self.recommendations: List[str] = []

    def validate_submission(self) -> SubmissionReport:
        """Run comprehensive validation on academic submission."""
        logger.info(f"Starting validation of submission: {self.submission_path}")

        # Core validation checks
        self._validate_file_structure()
        self._validate_latex_syntax()
        self._validate_bibliography()
        self._validate_figures()
        self._validate_arxiv_compliance()
        self._validate_content_quality()
        self._validate_accessibility()
        self._validate_reproducibility()

        # Calculate overall status and compliance score
        overall_status, compliance_score = self._calculate_overall_status()

        return SubmissionReport(
            submission_path=str(self.submission_path),
            validation_results=self.results,
            overall_status=overall_status,
            compliance_score=compliance_score,
            recommendations=self.recommendations,
        )

    def _validate_file_structure(self):
        """Validate submission file structure and organization."""
        required_files = ["main.tex", "README.txt"]
        optional_files = ["*.bib", "figs/", "figures/"]

        missing_files = []
        for file_pattern in required_files:
            if not list(self.submission_path.glob(file_pattern)):
                missing_files.append(file_pattern)

        if missing_files:
            self.results.append(
                ValidationResult(
                    check_name="File Structure",
                    status="FAIL",
                    message=f"Missing required files: {', '.join(missing_files)}",
                    details={"missing_files": missing_files},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="File Structure",
                    status="PASS",
                    message="All required files present",
                )
            )

    def _validate_latex_syntax(self):
        """Validate LaTeX syntax and compilation."""
        main_tex = self.submission_path / "main.tex"
        if not main_tex.exists():
            self.results.append(
                ValidationResult(
                    check_name="LaTeX Syntax",
                    status="FAIL",
                    message="main.tex not found",
                )
            )
            return

        try:
            # Check for common LaTeX issues
            with open(main_tex, "r", encoding="utf-8") as f:
                content = f.read()

            issues = []

            # Check for unmatched braces
            brace_count = content.count("{") - content.count("}")
            if brace_count != 0:
                issues.append(f"Unmatched braces: {brace_count} difference")

            # Check for undefined references
            undefined_refs = re.findall(r"\\ref\{([^}]+)\}", content)
            defined_labels = re.findall(r"\\label\{([^}]+)\}", content)
            missing_refs = [ref for ref in undefined_refs if ref not in defined_labels]
            if missing_refs:
                issues.append(f"Undefined references: {missing_refs}")

            # Check for missing citations
            citations = re.findall(r"\\cite\{([^}]+)\}", content)
            if citations and not any(self.submission_path.glob("*.bib")):
                issues.append("Citations found but no bibliography file")

            if issues:
                self.results.append(
                    ValidationResult(
                        check_name="LaTeX Syntax",
                        status="WARNING",
                        message="LaTeX syntax issues detected",
                        details={"issues": issues},
                    )
                )
                self.recommendations.extend(
                    [f"Fix LaTeX issue: {issue}" for issue in issues]
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="LaTeX Syntax",
                        status="PASS",
                        message="LaTeX syntax validation passed",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="LaTeX Syntax",
                    status="FAIL",
                    message=f"LaTeX validation error: {str(e)}",
                )
            )

    def _validate_bibliography(self):
        """Validate bibliography completeness and formatting."""
        bib_files = list(self.submission_path.glob("*.bib"))

        if not bib_files:
            self.results.append(
                ValidationResult(
                    check_name="Bibliography",
                    status="WARNING",
                    message="No bibliography file found",
                )
            )
            return

        try:
            total_entries = 0
            issues = []

            for bib_file in bib_files:
                with open(bib_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Count bibliography entries
                entries = re.findall(r"@\w+\{[^,]+,", content)
                total_entries += len(entries)

                # Check for common issues
                if "url = {}" in content or "doi = {}" in content:
                    issues.append("Empty URL or DOI fields found")

                # Check for missing required fields
                incomplete_entries = re.findall(
                    r"@article\{[^}]+\}[^@]*(?!.*author.*=).*?(?=@|\Z)",
                    content,
                    re.DOTALL,
                )
                if incomplete_entries:
                    issues.append("Articles missing author field")

            details = {
                "total_entries": total_entries,
                "bib_files": [str(f) for f in bib_files],
            }

            if issues:
                self.results.append(
                    ValidationResult(
                        check_name="Bibliography",
                        status="WARNING",
                        message="Bibliography issues detected",
                        details={**details, "issues": issues},
                    )
                )
                self.recommendations.extend(
                    [f"Fix bibliography: {issue}" for issue in issues]
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="Bibliography",
                        status="PASS",
                        message=f"Bibliography validation passed ({total_entries} entries)",
                        details=details,
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Bibliography",
                    status="FAIL",
                    message=f"Bibliography validation error: {str(e)}",
                )
            )

    def _validate_figures(self):
        """Validate figures and their references."""
        fig_dirs = ["figs", "figures", "images"]
        figure_files = []

        for fig_dir in fig_dirs:
            fig_path = self.submission_path / fig_dir
            if fig_path.exists():
                figure_files.extend(list(fig_path.glob("*.*")))

        # Also check for figures in root directory
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.pdf", "*.eps"]:
            figure_files.extend(list(self.submission_path.glob(ext)))

        if not figure_files:
            self.results.append(
                ValidationResult(
                    check_name="Figures",
                    status="WARNING",
                    message="No figure files found",
                )
            )
            return

        try:
            main_tex = self.submission_path / "main.tex"
            if main_tex.exists():
                with open(main_tex, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check figure references
                figure_refs = re.findall(
                    r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", content
                )
                missing_figures = []

                for ref in figure_refs:
                    # Remove path prefixes and check if file exists
                    filename = Path(ref).name
                    if not any(filename in str(fig_file) for fig_file in figure_files):
                        missing_figures.append(ref)

                details = {
                    "total_figures": len(figure_files),
                    "referenced_figures": len(figure_refs),
                    "figure_files": [str(f) for f in figure_files],
                }

                if missing_figures:
                    self.results.append(
                        ValidationResult(
                            check_name="Figures",
                            status="FAIL",
                            message="Missing referenced figures",
                            details={**details, "missing_figures": missing_figures},
                        )
                    )
                    self.recommendations.append(
                        "Add missing figure files or fix references"
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name="Figures",
                            status="PASS",
                            message=f"Figure validation passed ({len(figure_files)} files)",
                            details=details,
                        )
                    )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Figures",
                    status="FAIL",
                    message=f"Figure validation error: {str(e)}",
                )
            )

    def _validate_arxiv_compliance(self):
        """Validate arXiv submission compliance."""
        compliance_issues = []

        # Check file size limits (arXiv has ~50MB limit)
        total_size = sum(
            f.stat().st_size for f in self.submission_path.rglob("*") if f.is_file()
        )
        if total_size > 50 * 1024 * 1024:  # 50MB
            compliance_issues.append(
                f"Submission size ({total_size/1024/1024:.1f}MB) exceeds arXiv limit"
            )

        # Check for prohibited file types
        prohibited_extensions = [".exe", ".zip", ".rar", ".tar.gz"]
        prohibited_files = []
        for ext in prohibited_extensions:
            prohibited_files.extend(list(self.submission_path.rglob(f"*{ext}")))

        if prohibited_files:
            compliance_issues.append(
                f"Prohibited file types found: {[str(f) for f in prohibited_files]}"
            )

        # Check main.tex structure
        main_tex = self.submission_path / "main.tex"
        if main_tex.exists():
            with open(main_tex, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for required elements
            if not re.search(r"\\title\{", content):
                compliance_issues.append("Missing \\title command")

            if not re.search(r"\\author\{", content):
                compliance_issues.append("Missing \\author command")

            if not re.search(r"\\begin\{abstract\}", content):
                compliance_issues.append("Missing abstract")

        details = {
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "file_count": len(list(self.submission_path.rglob("*"))),
        }

        if compliance_issues:
            self.results.append(
                ValidationResult(
                    check_name="arXiv Compliance",
                    status="FAIL",
                    message="arXiv compliance issues detected",
                    details={**details, "issues": compliance_issues},
                )
            )
            self.recommendations.extend(
                [f"Fix arXiv compliance: {issue}" for issue in compliance_issues]
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="arXiv Compliance",
                    status="PASS",
                    message="arXiv compliance validation passed",
                    details=details,
                )
            )

    def _validate_content_quality(self):
        """Validate content quality and completeness."""
        main_tex = self.submission_path / "main.tex"
        if not main_tex.exists():
            return

        try:
            with open(main_tex, "r", encoding="utf-8") as f:
                content = f.read()

            quality_issues = []

            # Check abstract length
            abstract_match = re.search(
                r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL
            )
            if abstract_match:
                abstract_words = len(abstract_match.group(1).split())
                if abstract_words < 50:
                    quality_issues.append(
                        f"Abstract too short ({abstract_words} words)"
                    )
                elif abstract_words > 300:
                    quality_issues.append(f"Abstract too long ({abstract_words} words)")

            # Check for placeholder text
            placeholders = ["TODO", "FIXME", "XXX", "lorem ipsum"]
            found_placeholders = []
            for placeholder in placeholders:
                if placeholder.lower() in content.lower():
                    found_placeholders.append(placeholder)

            if found_placeholders:
                quality_issues.append(f"Placeholder text found: {found_placeholders}")

            # Check section structure
            sections = re.findall(r"\\section\{([^}]+)\}", content)
            if len(sections) < 3:
                quality_issues.append(
                    "Insufficient section structure (minimum 3 sections recommended)"
                )

            details = {
                "word_count": len(content.split()),
                "section_count": len(sections),
                "sections": sections,
            }

            if quality_issues:
                self.results.append(
                    ValidationResult(
                        check_name="Content Quality",
                        status="WARNING",
                        message="Content quality issues detected",
                        details={**details, "issues": quality_issues},
                    )
                )
                self.recommendations.extend(
                    [f"Improve content: {issue}" for issue in quality_issues]
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="Content Quality",
                        status="PASS",
                        message="Content quality validation passed",
                        details=details,
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Content Quality",
                    status="FAIL",
                    message=f"Content quality validation error: {str(e)}",
                )
            )

    def _validate_accessibility(self):
        """Validate accessibility compliance."""
        main_tex = self.submission_path / "main.tex"
        if not main_tex.exists():
            return

        try:
            with open(main_tex, "r", encoding="utf-8") as f:
                content = f.read()

            accessibility_issues = []

            # Check for alt text on figures
            figures_without_alt = re.findall(
                r"\\includegraphics[^{]*\{[^}]+\}(?!\s*\\caption)", content
            )
            if figures_without_alt:
                accessibility_issues.append(
                    f"Figures without captions: {len(figures_without_alt)}"
                )

            # Check for proper heading structure
            if "\\section*{" in content:
                accessibility_issues.append(
                    "Unnumbered sections may affect accessibility"
                )

            # Check for color-only information
            color_references = re.findall(
                r"\b(red|blue|green|yellow|color)\b", content.lower()
            )
            if len(color_references) > 5:
                accessibility_issues.append(
                    "Heavy reliance on color information detected"
                )

            details = {
                "figures_with_captions": len(re.findall(r"\\caption\{", content)),
                "color_references": len(color_references),
            }

            if accessibility_issues:
                self.results.append(
                    ValidationResult(
                        check_name="Accessibility",
                        status="WARNING",
                        message="Accessibility issues detected",
                        details={**details, "issues": accessibility_issues},
                    )
                )
                self.recommendations.extend(
                    [
                        f"Improve accessibility: {issue}"
                        for issue in accessibility_issues
                    ]
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="Accessibility",
                        status="PASS",
                        message="Accessibility validation passed",
                        details=details,
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Accessibility",
                    status="FAIL",
                    message=f"Accessibility validation error: {str(e)}",
                )
            )

    def _validate_reproducibility(self):
        """Validate reproducibility and FAIR compliance."""
        reproducibility_score = 0
        max_score = 10

        # Check for README
        readme_files = list(self.submission_path.glob("README*"))
        if readme_files:
            reproducibility_score += 2

        # Check for code availability
        code_files = (
            list(self.submission_path.glob("*.py"))
            + list(self.submission_path.glob("*.R"))
            + list(self.submission_path.glob("*.m"))
        )
        if code_files:
            reproducibility_score += 2

        # Check for data availability mentions
        main_tex = self.submission_path / "main.tex"
        if main_tex.exists():
            with open(main_tex, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for reproducibility keywords
            repro_keywords = [
                "github",
                "zenodo",
                "doi",
                "dataset",
                "code",
                "reproducible",
            ]
            found_keywords = [
                kw for kw in repro_keywords if kw.lower() in content.lower()
            ]
            reproducibility_score += min(len(found_keywords), 4)

            # Check for proper citations
            citations = len(re.findall(r"\\cite\{", content))
            if citations >= 10:
                reproducibility_score += 2

        reproducibility_percentage = (reproducibility_score / max_score) * 100

        details = {
            "reproducibility_score": reproducibility_score,
            "max_score": max_score,
            "percentage": reproducibility_percentage,
            "readme_present": len(readme_files) > 0,
            "code_files": len(code_files),
        }

        if reproducibility_percentage >= 70:
            status = "PASS"
            message = f"Good reproducibility score ({reproducibility_percentage:.1f}%)"
        elif reproducibility_percentage >= 50:
            status = "WARNING"
            message = (
                f"Moderate reproducibility score ({reproducibility_percentage:.1f}%)"
            )
            self.recommendations.append(
                "Improve reproducibility by adding code, data links, or documentation"
            )
        else:
            status = "FAIL"
            message = f"Low reproducibility score ({reproducibility_percentage:.1f}%)"
            self.recommendations.append(
                "Significantly improve reproducibility documentation"
            )

        self.results.append(
            ValidationResult(
                check_name="Reproducibility",
                status=status,
                message=message,
                details=details,
            )
        )

    def _calculate_overall_status(self) -> Tuple[str, float]:
        """Calculate overall validation status and compliance score."""
        if not self.results:
            return "UNKNOWN", 0.0

        pass_count = sum(1 for r in self.results if r.status == "PASS")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")

        total_checks = len(self.results)
        compliance_score = (
            ((pass_count * 1.0) + (warning_count * 0.5) + (fail_count * 0.0))
            / total_checks
            * 100
        )

        if fail_count == 0 and warning_count <= 2:
            overall_status = "EXCELLENT"
        elif fail_count == 0:
            overall_status = "GOOD"
        elif fail_count <= 2:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "NEEDS_IMPROVEMENT"

        return overall_status, compliance_score


def generate_validation_report(
    report: SubmissionReport, output_path: str = None
) -> str:
    """Generate a comprehensive validation report."""
    if output_path is None:
        output_path = "validation_report.md"

    report_content = f"""# Academic Submission Validation Report

**Submission**: {report.submission_path}  
**Validation Date**: {report.timestamp}  
**Overall Status**: {report.overall_status}  
**Compliance Score**: {report.compliance_score:.1f}%

## Validation Results

"""

    for result in report.validation_results:
        status_icon = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}.get(
            result.status, "❓"
        )
        report_content += f"### {status_icon} {result.check_name}\n"
        report_content += f"- **Status**: {result.status}\n"
        report_content += f"- **Message**: {result.message}\n"
        if result.details:
            report_content += f"- **Details**: {json.dumps(result.details, indent=2)}\n"
        report_content += "\n"

    if report.recommendations:
        report_content += "## Recommendations\n\n"
        for i, rec in enumerate(report.recommendations, 1):
            report_content += f"{i}. {rec}\n"
        report_content += "\n"

    report_content += f"""## Summary

- **Total Checks**: {len(report.validation_results)}
- **Passed**: {sum(1 for r in report.validation_results if r.status == 'PASS')}
- **Warnings**: {sum(1 for r in report.validation_results if r.status == 'WARNING')}
- **Failed**: {sum(1 for r in report.validation_results if r.status == 'FAIL')}
- **Compliance Score**: {report.compliance_score:.1f}%

---
Generated by Academic Submission Validator
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python submission_validator.py <submission_path>")
        sys.exit(1)

    submission_path = sys.argv[1]
    validator = SubmissionValidator(submission_path)
    report = validator.validate_submission()

    report_file = generate_validation_report(report)
    print(f"Validation complete. Report saved to: {report_file}")
    print(f"Overall Status: {report.overall_status}")
    print(f"Compliance Score: {report.compliance_score:.1f}%")
