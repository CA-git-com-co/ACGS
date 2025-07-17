#!/usr/bin/env python3
"""
ACGS Research Paper Quality Validator
Constitutional Hash: cdd01ef066bc6cf2

Validates the quality of OCR-converted research papers and identifies
papers that need manual review or re-conversion.
"""

import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from loguru import logger


@dataclass
class QualityAssessment:
    """Quality assessment results for a converted paper."""

    filename: str
    quality_score: float
    word_count: int
    page_count: int
    has_constitutional_hash: bool
    has_abstract: bool
    has_references: bool
    has_sections: bool
    has_equations: bool
    has_tables: bool
    has_figures: bool
    conversion_issues: List[str]
    recommendations: List[str]
    constitutional_hash: str = "cdd01ef066bc6cf2"


class QualityValidator:
    """Validates quality of converted research papers."""

    def __init__(self, markdown_dir: Path):
        self.markdown_dir = Path(markdown_dir)
        self.constitutional_hash = "cdd01ef066bc6cf2"

    def assess_paper_quality(self, md_file: Path) -> QualityAssessment:
        """Assess the quality of a single converted paper."""
        logger.info(f"Assessing quality of {md_file.name}")

        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {md_file.name}: {e}")
            return QualityAssessment(
                filename=md_file.name,
                quality_score=0.0,
                word_count=0,
                page_count=0,
                has_constitutional_hash=False,
                has_abstract=False,
                has_references=False,
                has_sections=False,
                has_equations=False,
                has_tables=False,
                has_figures=False,
                conversion_issues=["Failed to read file"],
                recommendations=["Manual review required"],
            )

        # Basic metrics
        word_count = len(content.split())
        page_count = content.count("## Page")

        # Constitutional compliance
        has_constitutional_hash = self.constitutional_hash in content

        # Content structure analysis
        has_abstract = self._check_abstract(content)
        has_references = self._check_references(content)
        has_sections = self._check_sections(content)
        has_equations = self._check_equations(content)
        has_tables = self._check_tables(content)
        has_figures = self._check_figures(content)

        # Identify conversion issues
        conversion_issues = self._identify_issues(content)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            word_count,
            has_abstract,
            has_references,
            has_sections,
            has_equations,
            has_tables,
            conversion_issues,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            quality_score, conversion_issues, has_constitutional_hash
        )

        return QualityAssessment(
            filename=md_file.name,
            quality_score=quality_score,
            word_count=word_count,
            page_count=page_count,
            has_constitutional_hash=has_constitutional_hash,
            has_abstract=has_abstract,
            has_references=has_references,
            has_sections=has_sections,
            has_equations=has_equations,
            has_tables=has_tables,
            has_figures=has_figures,
            conversion_issues=conversion_issues,
            recommendations=recommendations,
        )

    def _check_abstract(self, content: str) -> bool:
        """Check if paper has an abstract section."""
        abstract_patterns = [
            r"\babstract\b",
            r"## Abstract",
            r"# Abstract",
            r"ABSTRACT",
        ]
        return any(
            re.search(pattern, content, re.IGNORECASE) for pattern in abstract_patterns
        )

    def _check_references(self, content: str) -> bool:
        """Check if paper has references section."""
        ref_patterns = [
            r"\breferences\b",
            r"\bbibliography\b",
            r"\bcitations\b",
            r"## References",
            r"# References",
            r"REFERENCES",
        ]
        return any(
            re.search(pattern, content, re.IGNORECASE) for pattern in ref_patterns
        )

    def _check_sections(self, content: str) -> bool:
        """Check if paper has proper section structure."""
        section_count = content.count("#")
        return section_count > 5  # Should have multiple sections

    def _check_equations(self, content: str) -> bool:
        """Check if paper contains mathematical equations."""
        equation_patterns = [
            r"\$\$.*?\$\$",  # Display math
            r"\$.*?\$",  # Inline math
            r"\\begin\{equation\}",
            r"\\begin\{align\}",
            r"\\[.*?\\]",  # LaTeX display math
            r"\\(.*?\\)",  # LaTeX inline math
            r"equation",
            r"formula",
        ]
        return any(
            re.search(pattern, content, re.IGNORECASE) for pattern in equation_patterns
        )

    def _check_tables(self, content: str) -> bool:
        """Check if paper contains tables."""
        table_patterns = [
            r"\|.*\|.*\|",  # Markdown table
            r"\\begin\{table\}",
            r"\\begin\{tabular\}",
            r"Table \d+",
            r"table",
            r"tabular",
        ]
        return any(
            re.search(pattern, content, re.IGNORECASE) for pattern in table_patterns
        )

    def _check_figures(self, content: str) -> bool:
        """Check if paper references figures."""
        figure_patterns = [
            r"Figure \d+",
            r"Fig\. \d+",
            r"figure",
            r"diagram",
            r"plot",
            r"graph",
        ]
        return any(
            re.search(pattern, content, re.IGNORECASE) for pattern in figure_patterns
        )

    def _identify_issues(self, content: str) -> List[str]:
        """Identify potential conversion issues."""
        issues = []

        # Check for garbled text
        if re.search(r"[^\x00-\x7F]{10,}", content):
            issues.append("Contains non-ASCII characters (possible encoding issues)")

        # Check for repeated characters (OCR artifacts)
        if re.search(r"(.)\1{10,}", content):
            issues.append("Contains repeated characters (OCR artifacts)")

        # Check for very short lines (broken formatting)
        lines = content.split("\n")
        short_lines = sum(1 for line in lines if 0 < len(line.strip()) < 10)
        if short_lines > len(lines) * 0.3:
            issues.append("Many very short lines (formatting issues)")

        # Check for missing spaces
        if re.search(r"[a-z][A-Z]", content):
            issues.append("Missing spaces between words")

        # Check for broken equations
        if "$$" in content and content.count("$$") % 2 != 0:
            issues.append("Unmatched equation delimiters")

        # Check for table formatting issues
        if "|" in content:
            table_lines = [line for line in lines if "|" in line]
            if table_lines:
                # Check if tables have consistent column counts
                col_counts = [line.count("|") for line in table_lines]
                if len(set(col_counts)) > 2:  # Allow some variation
                    issues.append("Inconsistent table formatting")

        # Check for very low word density (mostly page headers)
        if len(content.split()) < 100:
            issues.append("Very low word count (incomplete conversion)")

        return issues

    def _calculate_quality_score(
        self,
        word_count: int,
        has_abstract: bool,
        has_references: bool,
        has_sections: bool,
        has_equations: bool,
        has_tables: bool,
        conversion_issues: List[str],
    ) -> float:
        """Calculate overall quality score (0-1)."""
        score = 0.0

        # Content completeness (40%)
        if word_count > 500:
            score += 0.2
        elif word_count > 100:
            score += 0.1

        if has_abstract:
            score += 0.1
        if has_references:
            score += 0.1

        # Structure quality (30%)
        if has_sections:
            score += 0.15
        if has_equations or has_tables:
            score += 0.15

        # Conversion quality (30%)
        issue_penalty = min(len(conversion_issues) * 0.05, 0.3)
        score += max(0, 0.3 - issue_penalty)

        return min(score, 1.0)

    def _generate_recommendations(
        self,
        quality_score: float,
        conversion_issues: List[str],
        has_constitutional_hash: bool,
    ) -> List[str]:
        """Generate recommendations for improvement."""
        recommendations = []

        if not has_constitutional_hash:
            recommendations.append("Add constitutional hash (cdd01ef066bc6cf2)")

        if quality_score < 0.5:
            recommendations.append("Consider re-conversion with different OCR method")
            recommendations.append("Manual review and correction required")
        elif quality_score < 0.8:
            recommendations.append("Review for accuracy and completeness")

        if "encoding issues" in str(conversion_issues):
            recommendations.append("Fix character encoding issues")

        if "OCR artifacts" in str(conversion_issues):
            recommendations.append("Clean up OCR artifacts and repeated characters")

        if "formatting issues" in str(conversion_issues):
            recommendations.append("Improve formatting and structure")

        if "equation" in str(conversion_issues):
            recommendations.append("Manually verify mathematical equations")

        if "table" in str(conversion_issues):
            recommendations.append("Manually verify table structure and content")

        return recommendations

    def validate_all_papers(self) -> List[QualityAssessment]:
        """Validate all converted papers."""
        md_files = list(self.markdown_dir.glob("*.md"))
        if "README.md" in [f.name for f in md_files]:
            md_files = [f for f in md_files if f.name != "README.md"]

        logger.info(f"Validating {len(md_files)} converted papers")

        assessments = []
        for md_file in md_files:
            assessment = self.assess_paper_quality(md_file)
            assessments.append(assessment)

        return assessments

    def save_validation_report(self, assessments: List[QualityAssessment]) -> None:
        """Save validation report."""
        report_path = (
            self.markdown_dir.parent
            / "papers_metadata"
            / "quality_validation_report.json"
        )

        # Calculate summary statistics
        total_papers = len(assessments)
        low_quality = sum(1 for a in assessments if a.quality_score < 0.8)
        missing_hash = sum(1 for a in assessments if not a.has_constitutional_hash)
        avg_quality = (
            sum(a.quality_score for a in assessments) / total_papers
            if total_papers > 0
            else 0
        )

        report = {
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_papers": total_papers,
                "low_quality_papers": low_quality,
                "missing_constitutional_hash": missing_hash,
                "average_quality_score": avg_quality,
                "papers_needing_review": low_quality,
            },
            "assessments": [asdict(a) for a in assessments],
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Validation report saved to {report_path}")

        # Print summary
        print(f"\n{'='*60}")
        print("QUALITY VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total papers validated: {total_papers}")
        print(f"Papers with quality < 0.8: {low_quality}")
        print(f"Papers missing constitutional hash: {missing_hash}")
        print(f"Average quality score: {avg_quality:.3f}")
        print(f"Papers needing review: {low_quality}")
        print(f"{'='*60}")

        # Show low-quality papers
        if low_quality > 0:
            print("\nLOW-QUALITY PAPERS (< 0.8):")
            print("-" * 40)
            for assessment in sorted(assessments, key=lambda x: x.quality_score):
                if assessment.quality_score < 0.8:
                    print(f"{assessment.filename}: {assessment.quality_score:.3f}")
                    if assessment.conversion_issues:
                        print(
                            f"  Issues: {', '.join(assessment.conversion_issues[:2])}"
                        )
                    print()


def main():
    """Main validation function."""
    markdown_dir = Path("../papers_markdown")

    if not markdown_dir.exists():
        logger.error(f"Markdown directory does not exist: {markdown_dir}")
        return

    validator = QualityValidator(markdown_dir)
    assessments = validator.validate_all_papers()
    validator.save_validation_report(assessments)


if __name__ == "__main__":
    main()
