#!/usr/bin/env python3
"""
Unit tests for SubmissionValidator class.

Tests individual validation methods and overall validation workflow.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from quality_assurance.submission_validator import (
    SubmissionValidator, 
    ValidationResult, 
    SubmissionReport,
    generate_validation_report
)


class TestSubmissionValidator:
    """Test cases for SubmissionValidator class."""
    
    @pytest.mark.unit
    def test_validator_initialization(self, minimal_paper):
        """Test validator initialization with valid path."""
        validator = SubmissionValidator(str(minimal_paper))
        
        assert validator.submission_path == minimal_paper
        assert validator.results == []
        assert validator.recommendations == []
    
    @pytest.mark.unit
    def test_validator_initialization_invalid_path(self):
        """Test validator initialization with invalid path."""
        with pytest.raises(FileNotFoundError):
            SubmissionValidator("/nonexistent/path")
    
    @pytest.mark.unit
    def test_file_structure_validation_pass(self, minimal_paper):
        """Test file structure validation with all required files."""
        validator = SubmissionValidator(str(minimal_paper))
        validator._validate_file_structure()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "File Structure"
        assert result.status == "PASS"
        assert "required files present" in result.message.lower()
    
    @pytest.mark.unit
    def test_file_structure_validation_missing_main_tex(self, temp_dir):
        """Test file structure validation with missing main.tex."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        (paper_dir / "README.txt").write_text("Test")
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_file_structure()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "File Structure"
        assert result.status == "FAIL"
        assert "main.tex" in result.message
    
    @pytest.mark.unit
    def test_file_structure_validation_missing_readme(self, temp_dir):
        """Test file structure validation with missing README."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        (paper_dir / "main.tex").write_text("\\documentclass{article}")
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_file_structure()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "File Structure"
        assert result.status == "FAIL"
        assert "README.txt" in result.message
    
    @pytest.mark.unit
    def test_latex_syntax_validation_valid(self, minimal_paper):
        """Test LaTeX syntax validation with valid content."""
        validator = SubmissionValidator(str(minimal_paper))
        validator._validate_latex_syntax()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "LaTeX Syntax"
        assert result.status == "PASS"
    
    @pytest.mark.unit
    def test_latex_syntax_validation_unmatched_braces(self, temp_dir):
        """Test LaTeX syntax validation with unmatched braces."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        
        # Create LaTeX with unmatched braces
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\title{Test Paper
        \\author{Test Author}
        \\end{document}
        """)
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_latex_syntax()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "LaTeX Syntax"
        assert result.status == "WARNING"
        assert "unmatched braces" in result.message.lower()
    
    @pytest.mark.unit
    def test_latex_syntax_validation_undefined_references(self, temp_dir):
        """Test LaTeX syntax validation with undefined references."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\section{Introduction}\\label{sec:intro}
        This references a non-existent section \\ref{sec:nonexistent}.
        \\end{document}
        """)
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_latex_syntax()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "LaTeX Syntax"
        assert result.status == "WARNING"
        assert "undefined references" in result.message.lower()
    
    @pytest.mark.unit
    def test_bibliography_validation_no_file(self, minimal_paper):
        """Test bibliography validation with no bib file."""
        validator = SubmissionValidator(str(minimal_paper))
        validator._validate_bibliography()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Bibliography"
        assert result.status == "WARNING"
        assert "no bibliography file" in result.message.lower()
    
    @pytest.mark.unit
    def test_bibliography_validation_valid_file(self, complete_paper):
        """Test bibliography validation with valid bib file."""
        validator = SubmissionValidator(str(complete_paper))
        validator._validate_bibliography()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Bibliography"
        assert result.status == "PASS"
        assert "entries" in result.message.lower()
    
    @pytest.mark.unit
    def test_figures_validation_no_figures(self, minimal_paper):
        """Test figures validation with no figures."""
        validator = SubmissionValidator(str(minimal_paper))
        validator._validate_figures()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Figures"
        assert result.status == "WARNING"
        assert "no figure files" in result.message.lower()
    
    @pytest.mark.unit
    def test_figures_validation_valid_figures(self, complete_paper):
        """Test figures validation with valid figures."""
        validator = SubmissionValidator(str(complete_paper))
        validator._validate_figures()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Figures"
        assert result.status == "PASS"
    
    @pytest.mark.unit
    def test_figures_validation_missing_referenced_figure(self, temp_dir):
        """Test figures validation with missing referenced figure."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\includegraphics{missing_figure.png}
        \\end{document}
        """)
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_figures()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Figures"
        assert result.status == "FAIL"
        assert "missing referenced figures" in result.message.lower()
    
    @pytest.mark.unit
    def test_arxiv_compliance_validation_pass(self, minimal_paper):
        """Test arXiv compliance validation with compliant submission."""
        validator = SubmissionValidator(str(minimal_paper))
        validator._validate_arxiv_compliance()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "arXiv Compliance"
        assert result.status == "PASS"
    
    @pytest.mark.unit
    def test_arxiv_compliance_validation_missing_title(self, temp_dir):
        """Test arXiv compliance validation with missing title."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        Content without title, author, or abstract.
        \\end{document}
        """)
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_arxiv_compliance()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "arXiv Compliance"
        assert result.status == "FAIL"
        assert "missing" in result.message.lower()
    
    @pytest.mark.unit
    def test_content_quality_validation_good_abstract(self, complete_paper):
        """Test content quality validation with good abstract."""
        validator = SubmissionValidator(str(complete_paper))
        validator._validate_content_quality()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Content Quality"
        assert result.status == "PASS"
    
    @pytest.mark.unit
    def test_content_quality_validation_short_abstract(self, temp_dir):
        """Test content quality validation with short abstract."""
        paper_dir = temp_dir / "test_paper"
        paper_dir.mkdir()
        
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\begin{abstract}
        Short.
        \\end{abstract}
        \\section{Introduction}
        \\end{document}
        """)
        
        validator = SubmissionValidator(str(paper_dir))
        validator._validate_content_quality()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Content Quality"
        assert result.status == "WARNING"
        assert "abstract too short" in result.message.lower()
    
    @pytest.mark.unit
    def test_accessibility_validation_pass(self, complete_paper):
        """Test accessibility validation with proper content."""
        validator = SubmissionValidator(str(complete_paper))
        validator._validate_accessibility()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Accessibility"
        assert result.status in ["PASS", "WARNING"]  # May have minor issues
    
    @pytest.mark.unit
    def test_reproducibility_validation_with_readme(self, complete_paper):
        """Test reproducibility validation with README."""
        validator = SubmissionValidator(str(complete_paper))
        validator._validate_reproducibility()
        
        assert len(validator.results) == 1
        result = validator.results[0]
        assert result.check_name == "Reproducibility"
        assert "reproducibility score" in result.message.lower()
    
    @pytest.mark.unit
    def test_calculate_overall_status_excellent(self):
        """Test overall status calculation for excellent submission."""
        validator = SubmissionValidator(".")
        validator.results = [
            ValidationResult("Test 1", "PASS", "Message 1"),
            ValidationResult("Test 2", "PASS", "Message 2"),
            ValidationResult("Test 3", "PASS", "Message 3"),
        ]
        
        status, score = validator._calculate_overall_status()
        
        assert status == "EXCELLENT"
        assert score == 100.0
    
    @pytest.mark.unit
    def test_calculate_overall_status_needs_improvement(self):
        """Test overall status calculation for poor submission."""
        validator = SubmissionValidator(".")
        validator.results = [
            ValidationResult("Test 1", "FAIL", "Message 1"),
            ValidationResult("Test 2", "FAIL", "Message 2"),
            ValidationResult("Test 3", "FAIL", "Message 3"),
        ]
        
        status, score = validator._calculate_overall_status()
        
        assert status == "NEEDS_IMPROVEMENT"
        assert score == 0.0
    
    @pytest.mark.unit
    def test_full_validation_workflow(self, complete_paper):
        """Test complete validation workflow."""
        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()
        
        # Check report structure
        assert isinstance(report, SubmissionReport)
        assert report.submission_path == str(complete_paper)
        assert len(report.validation_results) > 0
        assert report.overall_status in ["EXCELLENT", "GOOD", "ACCEPTABLE", "NEEDS_IMPROVEMENT"]
        assert 0 <= report.compliance_score <= 100
        assert isinstance(report.recommendations, list)
        assert report.timestamp is not None
        
        # Check that all validation categories are covered
        check_names = [r.check_name for r in report.validation_results]
        expected_checks = [
            "File Structure", "LaTeX Syntax", "Bibliography", "Figures",
            "arXiv Compliance", "Content Quality", "Accessibility", "Reproducibility"
        ]
        
        for expected_check in expected_checks:
            assert expected_check in check_names


class TestValidationResult:
    """Test cases for ValidationResult dataclass."""
    
    @pytest.mark.unit
    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            check_name="Test Check",
            status="PASS",
            message="Test message"
        )
        
        assert result.check_name == "Test Check"
        assert result.status == "PASS"
        assert result.message == "Test message"
        assert result.details is None
        assert result.timestamp is not None
    
    @pytest.mark.unit
    def test_validation_result_with_details(self):
        """Test ValidationResult with details."""
        details = {"count": 5, "items": ["item1", "item2"]}
        result = ValidationResult(
            check_name="Test Check",
            status="WARNING",
            message="Test warning",
            details=details
        )
        
        assert result.details == details
        assert result.status == "WARNING"


class TestSubmissionReport:
    """Test cases for SubmissionReport dataclass."""
    
    @pytest.mark.unit
    def test_submission_report_creation(self, mock_validation_result):
        """Test SubmissionReport creation."""
        report = SubmissionReport(
            submission_path="/test/path",
            validation_results=[mock_validation_result],
            overall_status="GOOD",
            compliance_score=85.0,
            recommendations=["Test recommendation"]
        )
        
        assert report.submission_path == "/test/path"
        assert len(report.validation_results) == 1
        assert report.overall_status == "GOOD"
        assert report.compliance_score == 85.0
        assert len(report.recommendations) == 1
        assert report.timestamp is not None


class TestReportGeneration:
    """Test cases for report generation functions."""
    
    @pytest.mark.unit
    def test_generate_validation_report(self, mock_submission_report, temp_dir):
        """Test validation report generation."""
        output_path = temp_dir / "test_report.md"
        
        result_path = generate_validation_report(mock_submission_report, str(output_path))
        
        assert result_path == str(output_path)
        assert output_path.exists()
        
        # Check report content
        content = output_path.read_text()
        assert "Academic Submission Validation Report" in content
        assert "Overall Status: GOOD" in content
        assert "Compliance Score: 85.0%" in content
    
    @pytest.mark.unit
    def test_generate_validation_report_default_path(self, mock_submission_report, temp_dir):
        """Test validation report generation with default path."""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result_path = generate_validation_report(mock_submission_report)
            
            assert result_path == "validation_report.md"
            assert Path(result_path).exists()
        finally:
            os.chdir(original_cwd)
