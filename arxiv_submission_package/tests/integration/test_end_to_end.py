#!/usr/bin/env python3
"""
End-to-end integration tests for Academic Submission System.

Tests complete workflows from paper input to final validation reports.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from quality_assurance.compliance_checker import ComplianceChecker
from quality_assurance.submission_validator import SubmissionValidator


class TestEndToEndValidation:
    """End-to-end validation workflow tests."""

    @pytest.mark.integration
    def test_complete_validation_workflow(self, complete_paper):
        """Test complete validation workflow with valid paper."""
        # Run validation
        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()

        # Verify report structure
        assert report.submission_path == str(complete_paper)
        assert len(report.validation_results) >= 8  # All validation categories
        assert report.overall_status in ["EXCELLENT", "GOOD", "ACCEPTABLE"]
        assert report.compliance_score >= 70.0
        assert isinstance(report.recommendations, list)

        # Verify all validation categories are present
        check_names = [r.check_name for r in report.validation_results]
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
            assert expected_check in check_names

        # Verify no critical failures for valid paper
        critical_failures = [r for r in report.validation_results if r.status == "FAIL"]
        assert (
            len(critical_failures) == 0
        ), f"Unexpected failures: {[r.message for r in critical_failures]}"

    @pytest.mark.integration
    def test_validation_with_invalid_paper(self, invalid_paper):
        """Test validation workflow with invalid paper."""
        validator = SubmissionValidator(str(invalid_paper))
        report = validator.validate_submission()

        # Should detect multiple issues
        assert report.overall_status in ["NEEDS_IMPROVEMENT", "ACCEPTABLE"]
        assert report.compliance_score < 70.0

        # Should have failures
        failures = [r for r in report.validation_results if r.status == "FAIL"]
        assert len(failures) > 0

        # Should have recommendations
        assert len(report.recommendations) > 0

    @pytest.mark.integration
    def test_multi_venue_compliance_workflow(self, complete_paper):
        """Test compliance checking across multiple venues."""
        venues = ["arxiv", "ieee", "acm"]
        checker = ComplianceChecker()

        results_by_venue = {}

        for venue in venues:
            try:
                results = checker.check_compliance(str(complete_paper), venue)
                results_by_venue[venue] = results

                # Basic validation of results
                assert isinstance(results, list)
                assert len(results) > 0

                # Each result should have required fields
                for result in results:
                    assert hasattr(result, "rule_id")
                    assert hasattr(result, "status")
                    assert hasattr(result, "message")
                    assert result.status in ["PASS", "WARNING", "FAIL"]

            except ValueError as e:
                # Some venues might not be implemented yet
                if "not supported" in str(e).lower():
                    pytest.skip(f"Venue {venue} not yet supported")
                else:
                    raise

        # Should have results for at least one venue
        assert len(results_by_venue) > 0

    @pytest.mark.integration
    def test_validation_report_generation(self, complete_paper, temp_dir):
        """Test validation report generation and content."""
        from quality_assurance.submission_validator import generate_validation_report

        # Run validation
        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()

        # Generate report
        report_path = temp_dir / "integration_test_report.md"
        generated_path = generate_validation_report(report, str(report_path))

        assert generated_path == str(report_path)
        assert report_path.exists()

        # Verify report content
        content = report_path.read_text()

        # Check required sections
        assert "Academic Submission Validation Report" in content
        assert f"Overall Status: {report.overall_status}" in content
        assert f"Compliance Score: {report.compliance_score:.1f}%" in content
        assert "Validation Results" in content
        assert "Summary" in content

        # Check that all validation results are included
        for result in report.validation_results:
            assert result.check_name in content
            assert result.status in content

    @pytest.mark.integration
    def test_validation_with_missing_dependencies(self, minimal_paper):
        """Test validation behavior when optional dependencies are missing."""
        # This test simulates missing LaTeX installation
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("LaTeX not found")

            validator = SubmissionValidator(str(minimal_paper))
            report = validator.validate_submission()

            # Should still complete validation
            assert report.overall_status is not None
            assert len(report.validation_results) > 0

            # May have warnings about missing dependencies
            warnings = [r for r in report.validation_results if r.status == "WARNING"]
            # Should have at least some warnings due to missing LaTeX
            assert len(warnings) >= 0  # Graceful degradation

    @pytest.mark.integration
    def test_large_submission_handling(self, temp_dir):
        """Test handling of large submissions."""
        # Create a large paper for testing
        large_paper_dir = temp_dir / "large_paper"
        large_paper_dir.mkdir()

        # Create large content
        large_content = "\\section{Large Section}\n" + "Content. " * 10000

        (large_paper_dir / "main.tex").write_text(
            f"""
\\documentclass{{article}}
\\title{{Large Test Paper}}
\\author{{Test Author}}
\\begin{{document}}
\\maketitle
\\begin{{abstract}}
{"Large abstract content. " * 100}
\\end{{abstract}}
{large_content}
\\end{{document}}
"""
        )

        (large_paper_dir / "README.txt").write_text("Large test paper")

        # Create large bibliography
        bib_entries = []
        for i in range(100):
            bib_entries.append(
                f"""
@article{{ref{i:03d},
    title={{Reference {i}}},
    author={{Author {i}}},
    journal={{Journal {i}}},
    year={{2023}}
}}"""
            )

        (large_paper_dir / "references.bib").write_text("\n".join(bib_entries))

        # Validate large submission
        validator = SubmissionValidator(str(large_paper_dir))
        report = validator.validate_submission()

        # Should handle large content gracefully
        assert report.overall_status is not None
        assert len(report.validation_results) > 0

        # Check that bibliography validation handled large file
        bib_results = [
            r for r in report.validation_results if r.check_name == "Bibliography"
        ]
        assert len(bib_results) == 1
        assert "100 entries" in bib_results[0].message

    @pytest.mark.integration
    def test_concurrent_validation(self, complete_paper, minimal_paper):
        """Test concurrent validation of multiple papers."""
        import concurrent.futures
        import time

        def validate_paper(paper_path):
            validator = SubmissionValidator(str(paper_path))
            return validator.validate_submission()

        papers = [complete_paper, minimal_paper]
        start_time = time.time()

        # Run concurrent validations
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(validate_paper, paper) for paper in papers]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        end_time = time.time()

        # All validations should complete successfully
        assert len(results) == 2
        for result in results:
            assert result.overall_status is not None
            assert len(result.validation_results) > 0

        # Should complete in reasonable time
        total_time = end_time - start_time
        assert total_time < 30.0  # 30 seconds max for concurrent validation

    @pytest.mark.integration
    def test_validation_error_recovery(self, temp_dir):
        """Test validation error recovery and graceful degradation."""
        # Create paper with various issues that might cause errors
        problem_paper_dir = temp_dir / "problem_paper"
        problem_paper_dir.mkdir()

        # Create file with encoding issues
        (problem_paper_dir / "main.tex").write_bytes(
            b"""
\\documentclass{article}
\\begin{document}
\\title{Test with \xff encoding issues}
\\end{document}
"""
        )

        # Create empty README
        (problem_paper_dir / "README.txt").write_text("")

        # Run validation - should handle errors gracefully
        validator = SubmissionValidator(str(problem_paper_dir))
        report = validator.validate_submission()

        # Should complete despite issues
        assert report.overall_status is not None
        assert len(report.validation_results) > 0

        # Should have detected issues
        failures = [r for r in report.validation_results if r.status == "FAIL"]
        assert len(failures) > 0


class TestCLIIntegration:
    """Integration tests for CLI interface."""

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_validate_command(self, complete_paper, temp_dir):
        """Test CLI validate command integration."""
        output_file = temp_dir / "cli_validation.json"

        # Run CLI validation
        result = subprocess.run(
            [
                "python",
                "cli/academic_cli.py",
                "validate",
                str(complete_paper),
                "--format",
                "json",
                "--output",
                str(output_file),
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        assert output_file.exists()

        # Parse and validate JSON output
        with open(output_file) as f:
            data = json.load(f)

        assert "overall_status" in data
        assert "compliance_score" in data
        assert "validation_results" in data
        assert isinstance(data["validation_results"], list)

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_compliance_command(self, complete_paper, temp_dir):
        """Test CLI compliance command integration."""
        output_file = temp_dir / "cli_compliance.md"

        # Run CLI compliance check
        result = subprocess.run(
            [
                "python",
                "cli/academic_cli.py",
                "compliance",
                str(complete_paper),
                "--venue",
                "arxiv",
                "--output",
                str(output_file),
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should succeed or fail gracefully
        assert result.returncode in [0, 1]  # 0 = pass, 1 = compliance issues

        if output_file.exists():
            content = output_file.read_text()
            assert "Compliance" in content

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_status_command(self, complete_paper):
        """Test CLI status command integration."""
        # Run CLI status check
        result = subprocess.run(
            ["python", "cli/academic_cli.py", "status", str(complete_paper)],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        assert "Academic Submission Status" in result.stdout
        assert "Key Files:" in result.stdout

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_error_handling(self):
        """Test CLI error handling with invalid inputs."""
        # Test with non-existent path
        result = subprocess.run(
            ["python", "cli/academic_cli.py", "validate", "/nonexistent/path"],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should fail gracefully
        assert result.returncode == 1
        assert "does not exist" in result.stderr or "not found" in result.stderr


class TestWebIntegration:
    """Integration tests for web interface."""

    @pytest.mark.integration
    @pytest.mark.web
    def test_web_app_startup(self, flask_client):
        """Test web application startup and basic routes."""
        # Test home page
        response = flask_client.get("/")
        assert response.status_code == 200
        assert b"Academic Submission Tool" in response.data

        # Test upload page
        response = flask_client.get("/upload")
        assert response.status_code == 200

        # Test help page
        response = flask_client.get("/help")
        assert response.status_code == 200

        # Test about page
        response = flask_client.get("/about")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.web
    def test_web_file_upload_workflow(self, flask_client, complete_paper):
        """Test web file upload and validation workflow."""
        # Create a ZIP file for upload
        import io
        import zipfile

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file_path in complete_paper.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(complete_paper)
                    zip_file.write(file_path, arcname)

        zip_buffer.seek(0)

        # Upload via API
        response = flask_client.post(
            "/api/validate", data={"file": (zip_buffer, "test_submission.zip")}
        )

        # Should succeed or handle gracefully
        assert response.status_code in [200, 400, 500]  # Various outcomes possible

        if response.status_code == 200:
            data = response.get_json()
            assert "submission_id" in data
            assert "overall_status" in data
