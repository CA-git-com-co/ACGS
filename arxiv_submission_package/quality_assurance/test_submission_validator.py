#!/usr/bin/env python3
"""
Test suite for the Academic Submission Validator

This module provides comprehensive tests for the submission validation pipeline.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from submission_validator import SubmissionReport, SubmissionValidator, ValidationResult


class TestSubmissionValidator(unittest.TestCase):
    """Test cases for SubmissionValidator."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.validator = SubmissionValidator(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def create_test_file(self, filename: str, content: str):
        """Create a test file with given content."""
        file_path = self.test_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_file_structure_validation_pass(self):
        """Test file structure validation with all required files."""
        self.create_test_file("main.tex", "\\documentclass{article}")
        self.create_test_file("README.txt", "Test submission")

        self.validator._validate_file_structure()

        # Should have one result with PASS status
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")
        self.assertEqual(self.validator.results[0].check_name, "File Structure")

    def test_file_structure_validation_fail(self):
        """Test file structure validation with missing files."""
        # Only create README, missing main.tex
        self.create_test_file("README.txt", "Test submission")

        self.validator._validate_file_structure()

        # Should have one result with FAIL status
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "FAIL")
        self.assertIn("main.tex", self.validator.results[0].message)

    def test_latex_syntax_validation_pass(self):
        """Test LaTeX syntax validation with valid content."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\title{Test Paper}
\\author{Test Author}
\\section{Introduction}\\label{sec:intro}
This is a test paper with proper references \\ref{sec:intro}.
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_latex_syntax()

        # Should pass validation
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")

    def test_latex_syntax_validation_unmatched_braces(self):
        """Test LaTeX syntax validation with unmatched braces."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\title{Test Paper
\\author{Test Author}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_latex_syntax()

        # Should detect unmatched braces
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "WARNING")
        self.assertIn("Unmatched braces", self.validator.results[0].message)

    def test_latex_syntax_validation_undefined_references(self):
        """Test LaTeX syntax validation with undefined references."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\title{Test Paper}
\\section{Introduction}\\label{sec:intro}
This references a non-existent section \\ref{sec:nonexistent}.
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_latex_syntax()

        # Should detect undefined reference
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "WARNING")
        self.assertIn("Undefined references", self.validator.results[0].message)

    def test_bibliography_validation_pass(self):
        """Test bibliography validation with valid bib file."""
        bib_content = """
@article{test2023,
  title={Test Article},
  author={Test Author},
  journal={Test Journal},
  year={2023}
}
"""
        self.create_test_file("references.bib", bib_content)

        self.validator._validate_bibliography()

        # Should pass validation
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")
        self.assertIn("1 entries", self.validator.results[0].message)

    def test_bibliography_validation_no_file(self):
        """Test bibliography validation with no bib file."""
        self.validator._validate_bibliography()

        # Should warn about missing bibliography
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "WARNING")
        self.assertIn("No bibliography file", self.validator.results[0].message)

    def test_figures_validation_pass(self):
        """Test figures validation with proper figures."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\includegraphics{test_figure.png}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)
        self.create_test_file("figs/test_figure.png", "fake image content")

        self.validator._validate_figures()

        # Should pass validation
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")

    def test_figures_validation_missing_figure(self):
        """Test figures validation with missing referenced figure."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\includegraphics{missing_figure.png}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_figures()

        # Should fail due to missing figure
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "FAIL")
        self.assertIn("Missing referenced figures", self.validator.results[0].message)

    def test_arxiv_compliance_validation_pass(self):
        """Test arXiv compliance validation with compliant submission."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\title{Test Paper}
\\author{Test Author}
\\begin{abstract}
This is a test abstract.
\\end{abstract}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_arxiv_compliance()

        # Should pass compliance
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")

    def test_arxiv_compliance_validation_missing_elements(self):
        """Test arXiv compliance validation with missing required elements."""
        latex_content = """
\\documentclass{article}
\\begin{document}
Some content without title, author, or abstract.
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_arxiv_compliance()

        # Should fail compliance
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "FAIL")
        self.assertIn("Missing", self.validator.results[0].message)

    def test_content_quality_validation_good_abstract(self):
        """Test content quality validation with good abstract length."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\begin{abstract}
This is a test abstract with sufficient length to pass the quality check.
It contains multiple sentences and provides adequate description of the work.
The abstract explains the problem, methodology, and key findings in a clear manner.
This should be long enough to meet the minimum word count requirements.
\\end{abstract}
\\section{Introduction}
\\section{Methods}
\\section{Results}
\\section{Conclusion}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_content_quality()

        # Should pass quality check
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")

    def test_content_quality_validation_short_abstract(self):
        """Test content quality validation with short abstract."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\begin{abstract}
Short abstract.
\\end{abstract}
\\section{Introduction}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_content_quality()

        # Should warn about short abstract
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "WARNING")
        self.assertIn("Abstract too short", self.validator.results[0].message)

    def test_content_quality_validation_placeholder_text(self):
        """Test content quality validation with placeholder text."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\begin{abstract}
This is a test abstract with TODO: add more content here.
\\end{abstract}
\\section{Introduction}
FIXME: Write introduction.
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_content_quality()

        # Should warn about placeholder text
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "WARNING")
        self.assertIn("Placeholder text", self.validator.results[0].message)

    def test_accessibility_validation_figures_with_captions(self):
        """Test accessibility validation with properly captioned figures."""
        latex_content = """
\\documentclass{article}
\\begin{document}
\\begin{figure}
\\includegraphics{test.png}
\\caption{This is a proper figure caption.}
\\end{figure}
\\end{document}
"""
        self.create_test_file("main.tex", latex_content)

        self.validator._validate_accessibility()

        # Should pass accessibility check
        self.assertEqual(len(self.validator.results), 1)
        self.assertEqual(self.validator.results[0].status, "PASS")

    def test_reproducibility_validation_with_readme(self):
        """Test reproducibility validation with README file."""
        self.create_test_file(
            "README.md", "# Test Project\nThis is a reproducible project."
        )
        self.create_test_file(
            "main.tex", "\\documentclass{article}\\begin{document}\\end{document}"
        )

        self.validator._validate_reproducibility()

        # Should have some reproducibility score
        self.assertEqual(len(self.validator.results), 1)
        result = self.validator.results[0]
        self.assertIn("reproducibility score", result.message.lower())

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        # Create a complete, valid submission
        latex_content = """
\\documentclass{article}
\\usepackage{graphicx}
\\begin{document}
\\title{Test Paper: A Comprehensive Study}
\\author{Test Author}
\\begin{abstract}
This is a comprehensive test abstract that provides sufficient detail about the research.
It describes the problem, methodology, key findings, and implications of the work.
The abstract is long enough to meet quality requirements and provides clear information.
This ensures the paper meets academic standards for abstract length and content quality.
\\end{abstract}
\\section{Introduction}
\\section{Methods}
\\section{Results}
\\begin{figure}
\\includegraphics{test_figure.png}
\\caption{Test figure with proper caption.}
\\end{figure}
\\section{Conclusion}
\\end{document}
"""

        bib_content = """
@article{test2023,
  title={Test Article},
  author={Test Author},
  journal={Test Journal},
  year={2023}
}
"""

        self.create_test_file("main.tex", latex_content)
        self.create_test_file("references.bib", bib_content)
        self.create_test_file("README.txt", "Test submission package")
        self.create_test_file("figs/test_figure.png", "fake image content")

        # Run full validation
        report = self.validator.validate_submission()

        # Check that we got results for all validation categories
        check_names = [result.check_name for result in report.validation_results]
        expected_checks = [
            "File Structure",
            "LaTeX Syntax",
            "Bibliography",
            "Figures",
            "arXiv Compliance",
            "Content Quality",
            "Accessibility",
            "Reproducibility",
        ]

        for expected_check in expected_checks:
            self.assertIn(expected_check, check_names)

        # Should have overall good status
        self.assertIn(report.overall_status, ["EXCELLENT", "GOOD", "ACCEPTABLE"])
        self.assertGreater(report.compliance_score, 70.0)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation and timestamp."""
        result = ValidationResult(
            check_name="Test Check", status="PASS", message="Test message"
        )

        self.assertEqual(result.check_name, "Test Check")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.message, "Test message")
        self.assertIsNotNone(result.timestamp)

    def test_validation_result_with_details(self):
        """Test ValidationResult with details."""
        details = {"key": "value", "count": 42}
        result = ValidationResult(
            check_name="Test Check",
            status="WARNING",
            message="Test message",
            details=details,
        )

        self.assertEqual(result.details, details)


class TestSubmissionReport(unittest.TestCase):
    """Test cases for SubmissionReport dataclass."""

    def test_submission_report_creation(self):
        """Test SubmissionReport creation."""
        results = [
            ValidationResult("Test 1", "PASS", "Message 1"),
            ValidationResult("Test 2", "FAIL", "Message 2"),
        ]

        report = SubmissionReport(
            submission_path="/test/path",
            validation_results=results,
            overall_status="ACCEPTABLE",
            compliance_score=75.0,
            recommendations=["Fix issue 1", "Improve issue 2"],
        )

        self.assertEqual(report.submission_path, "/test/path")
        self.assertEqual(len(report.validation_results), 2)
        self.assertEqual(report.overall_status, "ACCEPTABLE")
        self.assertEqual(report.compliance_score, 75.0)
        self.assertEqual(len(report.recommendations), 2)
        self.assertIsNotNone(report.timestamp)


if __name__ == "__main__":
    # Run the test suite
    unittest.main(verbosity=2)
