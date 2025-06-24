#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Academic Submission System tests.

This module provides shared fixtures and configuration for all test modules.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "tests" / "fixtures"

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_DATA_DIR

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test isolation."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def minimal_paper(temp_dir: Path) -> Path:
    """Create minimal valid paper for testing."""
    paper_dir = temp_dir / "minimal_paper"
    paper_dir.mkdir()
    
    # Create main.tex
    (paper_dir / "main.tex").write_text("""
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\title{Minimal Test Paper for Academic Validation}
\\author{Test Author}
\\date{\\today}

\\begin{document}
\\maketitle

\\begin{abstract}
This is a minimal test paper with sufficient content to pass basic validation.
The abstract contains enough words to meet the minimum requirements for academic
submission validation. It describes the purpose and scope of the test paper.
\\end{abstract}

\\section{Introduction}
This is the introduction section with minimal content.

\\section{Methodology}
This section describes the methodology used in the test.

\\section{Results}
This section presents the results of the test.

\\section{Conclusion}
This section concludes the test paper.

\\end{document}
""")
    
    # Create README.txt
    (paper_dir / "README.txt").write_text("""
Minimal Test Paper

This is a minimal test paper for the Academic Submission System.

Files:
- main.tex: Main LaTeX source file
- README.txt: This file

Compilation:
1. pdflatex main.tex
""")
    
    return paper_dir

@pytest.fixture
def complete_paper(temp_dir: Path) -> Path:
    """Create complete paper with all components for testing."""
    paper_dir = temp_dir / "complete_paper"
    paper_dir.mkdir()
    
    # Create main.tex
    (paper_dir / "main.tex").write_text("""
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{cite}
\\usepackage{amsmath}

\\title{Complete Test Paper for Academic Validation System}
\\author{Test Author\\\\Test University\\\\\\texttt{test@example.com}}
\\date{\\today}

\\begin{document}
\\maketitle

\\begin{abstract}
This is a comprehensive test paper that includes all necessary components for
academic submission validation. The paper demonstrates proper structure with
multiple sections, figures, references, and mathematical content. It serves
as a complete example for testing the validation system's capabilities across
all validation categories including LaTeX syntax, bibliography management,
figure handling, and content quality assessment.
\\end{abstract}

\\section{Introduction}
\\label{sec:introduction}

This paper serves as a comprehensive test case for the Academic Submission
System validation framework. The introduction provides context and motivation
for the validation system.

\\section{Related Work}
\\label{sec:related}

Previous work in academic submission systems has been limited~\\cite{smith2023}.
Our approach builds upon these foundations.

\\section{Methodology}
\\label{sec:methodology}

Our methodology involves comprehensive validation as shown in Figure~\\ref{fig:workflow}.

\\begin{figure}[htbp]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{figs/workflow}
    \\caption{Validation workflow showing the multi-stage process.}
    \\label{fig:workflow}
\\end{figure}

The validation process includes:
\\begin{enumerate}
    \\item File structure analysis
    \\item LaTeX syntax checking
    \\item Bibliography validation
    \\item Figure reference verification
\\end{enumerate}

\\section{Results}
\\label{sec:results}

The results demonstrate the effectiveness of our approach. Mathematical
expressions are properly formatted:

\\begin{equation}
    \\text{Score} = \\frac{\\text{Passed} + 0.5 \\times \\text{Warnings}}{\\text{Total}} \\times 100
\\end{equation}

\\section{Discussion}
\\label{sec:discussion}

The validation system successfully identifies common issues in academic
submissions as referenced in Section~\\ref{sec:methodology}.

\\section{Conclusion}
\\label{sec:conclusion}

This paper demonstrates a complete academic submission suitable for validation
testing. Future work will extend the system capabilities~\\cite{jones2023}.

\\section*{Acknowledgments}

We thank the reviewers for their valuable feedback.

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}
""")
    
    # Create bibliography
    (paper_dir / "references.bib").write_text("""
@article{smith2023,
    title={Academic Submission Validation: A Comprehensive Study},
    author={Smith, John A. and Doe, Jane B.},
    journal={Journal of Academic Publishing},
    volume={15},
    number={3},
    pages={123--145},
    year={2023},
    publisher={Academic Press},
    doi={10.1000/jap.2023.123456}
}

@inproceedings{jones2023,
    title={Future Directions in Academic Validation Systems},
    author={Jones, Alice C. and Brown, Robert D.},
    booktitle={Proceedings of the International Conference on Academic Tools},
    pages={67--82},
    year={2023},
    organization={IEEE},
    doi={10.1109/ICAT.2023.987654}
}
""")
    
    # Create figures directory and placeholder figure
    figs_dir = paper_dir / "figs"
    figs_dir.mkdir()
    (figs_dir / "workflow.png").write_bytes(b"fake_png_data_for_testing")
    
    # Create README.txt
    (paper_dir / "README.txt").write_text("""
Complete Test Paper for Academic Validation

This is a comprehensive test paper for the Academic Submission System.

Files:
- main.tex: Main LaTeX source file
- references.bib: Bibliography file
- figs/workflow.png: Workflow diagram
- README.txt: This file

Compilation:
1. pdflatex main.tex
2. bibtex main
3. pdflatex main.tex
4. pdflatex main.tex

This paper includes all components needed for comprehensive validation testing.
""")
    
    return paper_dir

@pytest.fixture
def invalid_paper(temp_dir: Path) -> Path:
    """Create invalid paper for testing error cases."""
    paper_dir = temp_dir / "invalid_paper"
    paper_dir.mkdir()
    
    # Create invalid LaTeX with syntax errors
    (paper_dir / "main.tex").write_text("""
\\documentclass{article}
\\begin{document}
\\title{Invalid Test Paper
\\author{Test Author}
Missing closing brace above and other issues.
\\section{Introduction}\\label{sec:intro}
This references a non-existent section \\ref{sec:nonexistent}.
\\includegraphics{missing_figure.png}
\\cite{missing_reference}
\\end{document}
""")
    
    # No README.txt file (missing required file)
    # No bibliography file (but citations present)
    # No figures directory (but figure referenced)
    
    return paper_dir

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide mock configuration for testing."""
    return {
        "size_limits": {
            "arxiv": 52428800,  # 50MB
            "ieee": 10485760,   # 10MB
            "acm": 20971520     # 20MB
        },
        "abstract_limits": {
            "min_words": 50,
            "max_words": 300
        },
        "required_sections": 3,
        "strict_mode": False,
        "venue_specific": {
            "arxiv": {
                "require_abstract": True,
                "max_figures": 20,
                "allowed_formats": ["png", "pdf", "eps"]
            }
        }
    }

@pytest.fixture
def mock_validation_result():
    """Create mock validation result for testing."""
    from quality_assurance.submission_validator import ValidationResult
    return ValidationResult(
        check_name="Test Check",
        status="PASS",
        message="Test validation passed",
        details={"test_key": "test_value"}
    )

@pytest.fixture
def mock_submission_report(mock_validation_result):
    """Create mock submission report for testing."""
    from quality_assurance.submission_validator import SubmissionReport
    return SubmissionReport(
        submission_path="/test/path",
        validation_results=[mock_validation_result],
        overall_status="GOOD",
        compliance_score=85.0,
        recommendations=["Test recommendation"]
    )

@pytest.fixture
def mock_flask_app():
    """Create mock Flask app for web interface testing."""
    from web.app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def flask_client(mock_flask_app):
    """Create Flask test client."""
    with mock_flask_app.test_client() as client:
        yield client

@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mock output"
        mock_run.return_value.stderr = ""
        yield mock_run

@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system operations for testing."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        yield temp_dir
    finally:
        os.chdir(original_cwd)

@pytest.fixture(scope="session")
def latex_available():
    """Check if LaTeX is available for testing."""
    import shutil
    return shutil.which("pdflatex") is not None

@pytest.fixture
def skip_if_no_latex(latex_available):
    """Skip test if LaTeX is not available."""
    if not latex_available:
        pytest.skip("LaTeX not available")

# Performance testing fixtures
@pytest.fixture
def performance_paper(temp_dir: Path) -> Path:
    """Create large paper for performance testing."""
    paper_dir = temp_dir / "performance_paper"
    paper_dir.mkdir()
    
    # Create large content for performance testing
    large_content = "\\section{Performance Test Section}\n" + "Test content. " * 1000
    
    (paper_dir / "main.tex").write_text(f"""
\\documentclass{{article}}
\\title{{Performance Test Paper}}
\\author{{Test Author}}
\\begin{{document}}
\\maketitle
\\begin{{abstract}}
{'Performance test abstract content. ' * 50}
\\end{{abstract}}
{large_content}
\\end{{document}}
""")
    
    (paper_dir / "README.txt").write_text("Performance test paper")
    
    return paper_dir

# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark slow tests
        if "performance" in item.nodeid or "slow" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)

def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Skip network tests if no network
    if "network" in item.keywords and not hasattr(item.config, "network_available"):
        pytest.skip("Network not available")

def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print("\n" + "="*50)
    print("Academic Submission System Test Suite")
    print("="*50)

def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    print("\n" + "="*50)
    print(f"Test session finished with exit status: {exitstatus}")
    print("="*50)

# Custom assertions
def assert_validation_result(result, expected_status, expected_check_name=None):
    """Custom assertion for validation results."""
    assert result.status == expected_status
    if expected_check_name:
        assert result.check_name == expected_check_name
    assert result.message is not None
    assert result.timestamp is not None

def assert_compliance_score(score, min_score=0, max_score=100):
    """Custom assertion for compliance scores."""
    assert isinstance(score, (int, float))
    assert min_score <= score <= max_score
