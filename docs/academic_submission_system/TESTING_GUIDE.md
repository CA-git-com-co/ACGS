# Academic Submission System Testing Guide

## Overview

This guide provides comprehensive testing strategies and examples for the Academic Submission System. It covers unit testing, integration testing, performance testing, and quality assurance procedures.

## Testing Framework Architecture

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_validator.py
│   ├── test_compliance.py
│   ├── test_cli.py
│   └── test_web_api.py
├── integration/             # Integration tests
│   ├── test_end_to_end.py
│   ├── test_venue_compliance.py
│   └── test_workflow.py
├── performance/             # Performance and load tests
│   ├── test_performance.py
│   ├── test_memory_usage.py
│   └── test_concurrent.py
├── fixtures/                # Test data and fixtures
│   ├── sample_papers/
│   ├── invalid_papers/
│   └── test_configs/
├── utils/                   # Testing utilities
│   ├── test_helpers.py
│   ├── mock_data.py
│   └── assertions.py
└── conftest.py             # Pytest configuration
```

## Unit Testing

### Testing the SubmissionValidator

```python
# tests/unit/test_validator.py

import pytest
import tempfile
import shutil
from pathlib import Path
from quality_assurance.submission_validator import SubmissionValidator, ValidationResult

class TestSubmissionValidator:

    @pytest.fixture
    def temp_paper_dir(self):
        """Create temporary paper directory for testing."""
        temp_dir = tempfile.mkdtemp()
        paper_dir = Path(temp_dir) / "test_paper"
        paper_dir.mkdir()

        # Create basic paper structure
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\title{Test Paper}
        \\author{Test Author}
        \\begin{abstract}
        This is a test abstract with sufficient length to pass validation.
        It contains multiple sentences and meets the minimum word requirements.
        \\end{abstract}
        \\section{Introduction}
        Test content here.
        \\end{document}
        """)

        (paper_dir / "README.txt").write_text("Test paper for validation")

        yield paper_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_validator_initialization(self, temp_paper_dir):
        """Test validator initialization."""
        validator = SubmissionValidator(str(temp_paper_dir))
        assert validator.submission_path == temp_paper_dir
        assert validator.results == []
        assert validator.recommendations == []

    def test_file_structure_validation_pass(self, temp_paper_dir):
        """Test file structure validation with valid structure."""
        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_file_structure()

        # Should have one PASS result for file structure
        file_structure_results = [r for r in validator.results if r.check_name == "File Structure"]
        assert len(file_structure_results) == 1
        assert file_structure_results[0].status == "PASS"

    def test_file_structure_validation_fail(self, temp_paper_dir):
        """Test file structure validation with missing files."""
        # Remove main.tex
        (temp_paper_dir / "main.tex").unlink()

        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_file_structure()

        # Should have one FAIL result
        file_structure_results = [r for r in validator.results if r.check_name == "File Structure"]
        assert len(file_structure_results) == 1
        assert file_structure_results[0].status == "FAIL"
        assert "main.tex" in file_structure_results[0].message

    def test_latex_syntax_validation(self, temp_paper_dir):
        """Test LaTeX syntax validation."""
        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_latex_syntax()

        latex_results = [r for r in validator.results if r.check_name == "LaTeX Syntax"]
        assert len(latex_results) == 1
        assert latex_results[0].status in ["PASS", "WARNING"]

    def test_latex_syntax_with_errors(self, temp_paper_dir):
        """Test LaTeX syntax validation with errors."""
        # Create LaTeX file with syntax errors
        (temp_paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\begin{document}
        \\title{Test Paper
        \\author{Test Author}
        Missing closing brace above
        \\end{document}
        """)

        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_latex_syntax()

        latex_results = [r for r in validator.results if r.check_name == "LaTeX Syntax"]
        assert len(latex_results) == 1
        assert latex_results[0].status == "WARNING"
        assert "brace" in latex_results[0].message.lower()

    def test_bibliography_validation_missing(self, temp_paper_dir):
        """Test bibliography validation with missing bib file."""
        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_bibliography()

        bib_results = [r for r in validator.results if r.check_name == "Bibliography"]
        assert len(bib_results) == 1
        assert bib_results[0].status == "WARNING"
        assert "No bibliography file" in bib_results[0].message

    def test_bibliography_validation_present(self, temp_paper_dir):
        """Test bibliography validation with valid bib file."""
        # Create bibliography file
        (temp_paper_dir / "references.bib").write_text("""
        @article{test2023,
            title={Test Article},
            author={Test Author},
            journal={Test Journal},
            year={2023}
        }
        """)

        validator = SubmissionValidator(str(temp_paper_dir))
        validator._validate_bibliography()

        bib_results = [r for r in validator.results if r.check_name == "Bibliography"]
        assert len(bib_results) == 1
        assert bib_results[0].status == "PASS"
        assert "1 entries" in bib_results[0].message

    def test_complete_validation(self, temp_paper_dir):
        """Test complete validation workflow."""
        validator = SubmissionValidator(str(temp_paper_dir))
        report = validator.validate_submission()

        # Check report structure
        assert report.submission_path == str(temp_paper_dir)
        assert len(report.validation_results) > 0
        assert report.overall_status in ["EXCELLENT", "GOOD", "ACCEPTABLE", "NEEDS_IMPROVEMENT"]
        assert 0 <= report.compliance_score <= 100
        assert isinstance(report.recommendations, list)
        assert report.timestamp is not None

class TestValidationResult:

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
```

### Testing the ComplianceChecker

```python
# tests/unit/test_compliance.py

import pytest
import tempfile
import shutil
from pathlib import Path
from quality_assurance.compliance_checker import ComplianceChecker

class TestComplianceChecker:

    @pytest.fixture
    def temp_paper_dir(self):
        """Create temporary paper directory for testing."""
        temp_dir = tempfile.mkdtemp()
        paper_dir = Path(temp_dir) / "test_paper"
        paper_dir.mkdir()

        # Create basic paper structure
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\usepackage{graphicx}
        \\title{Test Paper}
        \\author{Test Author}
        \\begin{document}
        \\maketitle
        \\begin{abstract}
        Test abstract content.
        \\end{abstract}
        \\section{Introduction}
        Test content.
        \\end{document}
        """)

        yield paper_dir
        shutil.rmtree(temp_dir)

    def test_checker_initialization(self):
        """Test ComplianceChecker initialization."""
        checker = ComplianceChecker()
        assert hasattr(checker, 'check_compliance')

    def test_arxiv_compliance_basic(self, temp_paper_dir):
        """Test basic arXiv compliance checking."""
        checker = ComplianceChecker()
        results = checker.check_compliance(str(temp_paper_dir), "arxiv")

        assert isinstance(results, list)
        assert len(results) > 0

        # Check that we have results for key arXiv requirements
        rule_ids = [r.rule_id for r in results]
        assert any("size" in rule_id.lower() for rule_id in rule_ids)
        assert any("title" in rule_id.lower() for rule_id in rule_ids)

    def test_ieee_compliance_basic(self, temp_paper_dir):
        """Test basic IEEE compliance checking."""
        checker = ComplianceChecker()
        results = checker.check_compliance(str(temp_paper_dir), "ieee")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_unsupported_venue(self, temp_paper_dir):
        """Test compliance checking with unsupported venue."""
        checker = ComplianceChecker()

        with pytest.raises(ValueError):
            checker.check_compliance(str(temp_paper_dir), "unsupported_venue")

    def test_nonexistent_path(self):
        """Test compliance checking with nonexistent path."""
        checker = ComplianceChecker()

        with pytest.raises(FileNotFoundError):
            checker.check_compliance("/nonexistent/path", "arxiv")
```

### Testing the CLI Interface

```python
# tests/unit/test_cli.py

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from cli.academic_cli import AcademicCLI

class TestAcademicCLI:

    @pytest.fixture
    def temp_paper_dir(self):
        """Create temporary paper directory for testing."""
        temp_dir = tempfile.mkdtemp()
        paper_dir = Path(temp_dir) / "test_paper"
        paper_dir.mkdir()

        (paper_dir / "main.tex").write_text("\\documentclass{article}\\begin{document}Test\\end{document}")
        (paper_dir / "README.txt").write_text("Test paper")

        yield paper_dir
        shutil.rmtree(temp_dir)

    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = AcademicCLI()
        assert cli.parser is not None
        assert cli.supported_venues == ["arxiv", "ieee", "acm"]

    def test_validate_command_help(self):
        """Test validate command help."""
        cli = AcademicCLI()

        # Test that help doesn't raise an exception
        with pytest.raises(SystemExit):
            cli.run(["validate", "--help"])

    @patch('cli.academic_cli.SubmissionValidator')
    def test_validate_command_success(self, mock_validator, temp_paper_dir):
        """Test successful validation command."""
        # Mock the validator
        mock_report = MagicMock()
        mock_report.overall_status = "GOOD"
        mock_report.compliance_score = 85.0
        mock_report.validation_results = []
        mock_report.recommendations = []

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate_submission.return_value = mock_report
        mock_validator.return_value = mock_validator_instance

        cli = AcademicCLI()
        result = cli.run(["validate", str(temp_paper_dir)])

        assert result == 0  # Success exit code
        mock_validator.assert_called_once_with(temp_paper_dir)

    def test_validate_command_nonexistent_path(self):
        """Test validation with nonexistent path."""
        cli = AcademicCLI()
        result = cli.run(["validate", "/nonexistent/path"])

        assert result == 1  # Error exit code

    @patch('cli.academic_cli.ComplianceChecker')
    def test_compliance_command(self, mock_checker, temp_paper_dir):
        """Test compliance command."""
        # Mock the compliance checker
        mock_results = [MagicMock()]
        mock_checker_instance = MagicMock()
        mock_checker_instance.check_compliance.return_value = mock_results
        mock_checker.return_value = mock_checker_instance

        cli = AcademicCLI()
        result = cli.run(["compliance", str(temp_paper_dir), "--venue", "arxiv"])

        assert result == 0
        mock_checker_instance.check_compliance.assert_called_once()

    def test_status_command(self, temp_paper_dir):
        """Test status command."""
        cli = AcademicCLI()
        result = cli.run(["status", str(temp_paper_dir)])

        # Status command should always succeed if path exists
        assert result == 0

    def test_invalid_command(self):
        """Test invalid command."""
        cli = AcademicCLI()
        result = cli.run(["invalid_command"])

        assert result == 1
```

## Integration Testing

### End-to-End Testing

```python
# tests/integration/test_end_to_end.py

import pytest
import tempfile
import shutil
import subprocess
import json
from pathlib import Path

class TestEndToEnd:

    @pytest.fixture
    def complete_paper(self):
        """Create a complete, valid paper for testing."""
        temp_dir = tempfile.mkdtemp()
        paper_dir = Path(temp_dir) / "complete_paper"
        paper_dir.mkdir()

        # Create main.tex
        (paper_dir / "main.tex").write_text("""
        \\documentclass{article}
        \\usepackage{graphicx}
        \\usepackage{cite}
        \\title{Complete Test Paper for End-to-End Validation}
        \\author{Test Author}
        \\begin{document}
        \\maketitle
        \\begin{abstract}
        This is a comprehensive test paper that includes all necessary components
        for academic submission validation. It has a proper abstract, multiple
        sections, figures, and references to demonstrate the complete validation
        workflow from start to finish.
        \\end{abstract}
        \\section{Introduction}
        This paper demonstrates end-to-end validation.
        \\section{Methodology}
        Our approach is comprehensive.
        \\section{Results}
        See Figure~\\ref{fig:test} for results.
        \\begin{figure}
        \\centering
        \\includegraphics[width=0.5\\textwidth]{figs/test_figure}
        \\caption{Test figure showing validation results.}
        \\label{fig:test}
        \\end{figure}
        \\section{Conclusion}
        This validates our approach as shown in~\\cite{test2023}.
        \\bibliographystyle{plain}
        \\bibliography{references}
        \\end{document}
        """)

        # Create bibliography
        (paper_dir / "references.bib").write_text("""
        @article{test2023,
            title={Test Article for Validation},
            author={Test, Author},
            journal={Journal of Testing},
            volume={1},
            number={1},
            pages={1--10},
            year={2023},
            doi={10.1000/test.2023.001}
        }
        """)

        # Create figures directory and figure
        figs_dir = paper_dir / "figs"
        figs_dir.mkdir()
        (figs_dir / "test_figure.png").write_bytes(b"fake_png_data")

        # Create README
        (paper_dir / "README.txt").write_text("""
        Complete Test Paper

        This is a test paper for end-to-end validation testing.

        Files:
        - main.tex: Main paper
        - references.bib: Bibliography
        - figs/test_figure.png: Test figure
        """)

        yield paper_dir
        shutil.rmtree(temp_dir)

    def test_cli_validation_workflow(self, complete_paper):
        """Test complete CLI validation workflow."""
        # Run validation
        result = subprocess.run([
            "python", "cli/academic_cli.py", "validate", str(complete_paper),
            "--format", "json", "--output", "test_validation.json"
        ], capture_output=True, text=True, cwd="arxiv_submission_package")

        assert result.returncode == 0

        # Check that report was generated
        report_path = Path("arxiv_submission_package/test_validation.json")
        assert report_path.exists()

        # Parse and validate report
        with open(report_path) as f:
            report_data = json.load(f)

        assert "overall_status" in report_data
        assert "compliance_score" in report_data
        assert "validation_results" in report_data

        # Cleanup
        report_path.unlink()

    def test_multi_venue_compliance(self, complete_paper):
        """Test compliance checking across multiple venues."""
        venues = ["arxiv", "ieee", "acm"]

        for venue in venues:
            result = subprocess.run([
                "python", "cli/academic_cli.py", "compliance", str(complete_paper),
                "--venue", venue, "--output", f"{venue}_compliance.md"
            ], capture_output=True, text=True, cwd="arxiv_submission_package")

            # Should succeed for all venues
            assert result.returncode in [0, 1]  # 0 = pass, 1 = fail but valid

            # Check report was generated
            report_path = Path(f"arxiv_submission_package/{venue}_compliance.md")
            assert report_path.exists()

            # Cleanup
            report_path.unlink()

    def test_status_command_integration(self, complete_paper):
        """Test status command integration."""
        result = subprocess.run([
            "python", "cli/academic_cli.py", "status", str(complete_paper)
        ], capture_output=True, text=True, cwd="arxiv_submission_package")

        assert result.returncode == 0
        assert "Academic Submission Status" in result.stdout
        assert "Key Files:" in result.stdout
        assert "Quick Validation:" in result.stdout
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_performance.py

import pytest
import time
import concurrent.futures
import tempfile
import shutil
from pathlib import Path
from quality_assurance.submission_validator import SubmissionValidator

class TestPerformance:

    @pytest.fixture
    def sample_paper(self):
        """Create sample paper for performance testing."""
        temp_dir = tempfile.mkdtemp()
        paper_dir = Path(temp_dir) / "perf_paper"
        paper_dir.mkdir()

        # Create a reasonably sized paper
        content = "\\section{Test Section}\n" + "Test content. " * 1000
        (paper_dir / "main.tex").write_text(f"""
        \\documentclass{{article}}
        \\title{{Performance Test Paper}}
        \\author{{Test Author}}
        \\begin{{document}}
        \\maketitle
        \\begin{{abstract}}
        {'This is a performance test abstract. ' * 20}
        \\end{{abstract}}
        {content}
        \\end{{document}}
        """)

        (paper_dir / "README.txt").write_text("Performance test paper")

        yield paper_dir
        shutil.rmtree(temp_dir)

    def test_validation_performance(self, sample_paper):
        """Test validation performance for single paper."""
        start_time = time.time()

        validator = SubmissionValidator(str(sample_paper))
        report = validator.validate_submission()

        end_time = time.time()
        validation_time = end_time - start_time

        # Validation should complete within reasonable time
        assert validation_time < 10.0  # 10 seconds max
        assert report.overall_status is not None

        print(f"Validation completed in {validation_time:.2f} seconds")

    def test_concurrent_validation(self, sample_paper):
        """Test concurrent validation performance."""
        num_workers = 5
        num_validations = 10

        def validate_paper():
            validator = SubmissionValidator(str(sample_paper))
            return validator.validate_submission()

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(validate_paper) for _ in range(num_validations)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # All validations should complete
        assert len(results) == num_validations
        assert all(r.overall_status is not None for r in results)

        # Should be faster than sequential
        avg_time_per_validation = total_time / num_validations
        assert avg_time_per_validation < 5.0  # 5 seconds per validation max

        print(f"Concurrent validation: {total_time:.2f}s total, {avg_time_per_validation:.2f}s average")

    def test_memory_usage(self, sample_paper):
        """Test memory usage during validation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run multiple validations
        for _ in range(10):
            validator = SubmissionValidator(str(sample_paper))
            report = validator.validate_submission()
            del validator, report

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase

        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
```

## Test Configuration

### Pytest Configuration

```python
# conftest.py

import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Create test data directory for the session."""
    test_dir = Path(__file__).parent / "fixtures" / "test_papers"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir

@pytest.fixture
def minimal_paper():
    """Create minimal valid paper for testing."""
    temp_dir = tempfile.mkdtemp()
    paper_dir = Path(temp_dir) / "minimal_paper"
    paper_dir.mkdir()

    (paper_dir / "main.tex").write_text("""
    \\documentclass{article}
    \\title{Minimal Test Paper}
    \\author{Test Author}
    \\begin{document}
    \\maketitle
    \\begin{abstract}
    This is a minimal test paper with just enough content to pass basic validation.
    \\end{abstract}
    \\section{Introduction}
    Minimal content.
    \\end{document}
    """)

    (paper_dir / "README.txt").write_text("Minimal test paper")

    yield paper_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def invalid_paper():
    """Create invalid paper for testing error cases."""
    temp_dir = tempfile.mkdtemp()
    paper_dir = Path(temp_dir) / "invalid_paper"
    paper_dir.mkdir()

    # Missing main.tex intentionally
    (paper_dir / "README.txt").write_text("Invalid test paper")

    yield paper_dir
    shutil.rmtree(temp_dir)

# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage
pytest --cov=quality_assurance --cov-report=html

# Run performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run performance tests
        run: pytest tests/performance/ -v -m "not slow"

      - name: Generate coverage report
        run: pytest --cov=quality_assurance --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

This comprehensive testing guide ensures the Academic Submission System maintains high quality and reliability across all components and use cases.
