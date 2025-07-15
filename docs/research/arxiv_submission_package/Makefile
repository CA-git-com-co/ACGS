# Makefile for Academic Submission System
# Provides convenient commands for development, testing, and deployment

.PHONY: help install install-dev test test-unit test-integration test-performance test-all
.PHONY: lint format type-check security-check clean coverage docs
.PHONY: build package deploy validate-example run-web run-cli
.PHONY: benchmark profile debug compile compile-latex compile-package compile-all
.PHONY: latex-watch latex-clean latex-optimize

# Default target
help:
	@echo "Academic Submission System - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  clean            Clean up temporary files and caches"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests (unit + integration)"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests"
	@echo "  test-all         Run all tests including slow ones"
	@echo "  coverage         Generate test coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint             Run linting checks (flake8)"
	@echo "  format           Format code (black + isort)"
	@echo "  type-check       Run type checking (mypy)"
	@echo "  security-check   Run security scans (bandit + safety)"
	@echo ""
	@echo "Application Commands:"
	@echo "  run-web          Start web interface"
	@echo "  run-cli          Run CLI with example"
	@echo "  validate-example Validate example paper"
	@echo ""
	@echo "Compilation Commands:"
	@echo "  compile          Compile everything (LaTeX + package)"
	@echo "  compile-latex    Compile LaTeX paper only"
	@echo "  compile-package  Build Python package only"
	@echo "  compile-all      Full compilation with report"
	@echo "  latex-watch      Watch LaTeX files and auto-compile"
	@echo "  latex-clean      Clean LaTeX build artifacts"
	@echo "  latex-optimize   Optimize LaTeX for arXiv"
	@echo ""
	@echo "Performance Commands:"
	@echo "  benchmark        Run performance benchmarks"
	@echo "  profile          Profile application performance"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  docs             Generate documentation"
	@echo ""
	@echo "Build Commands:"
	@echo "  build            Build distribution packages"
	@echo "  package          Create deployment package"

# Python and pip commands
PYTHON := python3
PIP := pip3
PYTEST := pytest

# Directories
SRC_DIRS := quality_assurance cli web
TEST_DIRS := tests
ALL_DIRS := $(SRC_DIRS) $(TEST_DIRS)

# Installation targets
install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-test.txt
	$(PIP) install -e .

# Testing targets
test: test-unit test-integration

test-unit:
	@echo "Running unit tests..."
	$(PYTEST) tests/unit/ -v --tb=short

test-integration:
	@echo "Running integration tests..."
	$(PYTEST) tests/integration/ -v --tb=short -m "not slow"

test-performance:
	@echo "Running performance tests..."
	$(PYTEST) tests/performance/ -v --tb=short -m "not slow and not benchmark"

test-all:
	@echo "Running all tests including slow ones..."
	$(PYTEST) tests/ -v --tb=short

coverage:
	@echo "Generating test coverage report..."
	$(PYTEST) tests/ --cov=$(SRC_DIRS) --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in reports/coverage/htmlcov/"

# Code quality targets
lint:
	@echo "Running linting checks..."
	flake8 $(ALL_DIRS) --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 $(ALL_DIRS) --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "Formatting code..."
	black $(ALL_DIRS)
	isort $(ALL_DIRS)

format-check:
	@echo "Checking code formatting..."
	black --check --diff $(ALL_DIRS)
	isort --check-only --diff $(ALL_DIRS)

type-check:
	@echo "Running type checks..."
	mypy $(SRC_DIRS) --ignore-missing-imports

security-check:
	@echo "Running security checks..."
	bandit -r $(SRC_DIRS) -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "Security reports generated: bandit-report.json, safety-report.json"

# Application targets
run-web:
	@echo "Starting web interface..."
	$(PYTHON) web/app.py

run-cli:
	@echo "Running CLI with help..."
	$(PYTHON) cli/academic_cli.py --help

validate-example:
	@echo "Validating example paper..."
	@if [ ! -d "example_paper" ]; then \
		echo "Creating example paper..."; \
		mkdir -p example_paper; \
		echo '\documentclass{article}\usepackage[utf8]{inputenc}\title{Example Paper for Academic Validation}\author{Example Author}\begin{document}\maketitle\begin{abstract}This is an example paper for demonstrating the Academic Submission System validation capabilities. The abstract contains sufficient content to pass validation requirements.\end{abstract}\section{Introduction}This is the introduction section.\section{Methodology}This section describes the methodology.\section{Results}This section presents the results.\section{Conclusion}This section concludes the paper.\end{document}' > example_paper/main.tex; \
		echo 'Example Paper\n\nThis is an example paper for testing the Academic Submission System.\n\nFiles:\n- main.tex: Main LaTeX source\n- README.txt: This file\n\nCompilation:\n1. pdflatex main.tex' > example_paper/README.txt; \
	fi
	$(PYTHON) cli/academic_cli.py validate example_paper/ --output example_validation.md
	$(PYTHON) cli/academic_cli.py compliance example_paper/ --venue arxiv --output example_compliance.md
	@echo "Validation complete! Check example_validation.md and example_compliance.md"

# Performance targets
benchmark:
	@echo "Running performance benchmarks..."
	$(PYTEST) tests/performance/ --benchmark-only --benchmark-json=benchmark.json
	@echo "Benchmark results saved to benchmark.json"

profile:
	@echo "Profiling application performance..."
	$(PYTHON) -m cProfile -o profile.stats cli/academic_cli.py validate example_paper/
	@echo "Profile saved to profile.stats"
	@echo "View with: python -m pstats profile.stats"

# Documentation targets
docs:
	@echo "Documentation is available in docs/ directory"
	@echo "Key files:"
	@echo "  - docs/academic_submission_system/README.md"
	@echo "  - docs/academic_submission_system/USER_GUIDE.md"
	@echo "  - docs/academic_submission_system/API_REFERENCE.md"
	@echo "  - docs/academic_submission_system/TUTORIAL.md"
	@echo "  - docs/academic_submission_system/TESTING_GUIDE.md"

# Build targets
build:
	@echo "Building distribution packages..."
	$(PYTHON) setup.py sdist bdist_wheel

package: clean build
	@echo "Creating deployment package..."
	mkdir -p dist/academic_submission_system
	cp -r quality_assurance cli web requirements.txt README.md dist/academic_submission_system/
	cd dist && tar -czf academic_submission_system.tar.gz academic_submission_system/
	@echo "Deployment package created: dist/academic_submission_system.tar.gz"

# Cleanup targets
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf reports/coverage/htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -f *.log
	rm -f *.json
	rm -f *.stats
	rm -f validation_report.md
	rm -f *_compliance.md
	@echo "Cleanup complete!"

# Development workflow targets
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

dev-check: format-check lint type-check test-unit
	@echo "Development checks complete!"

ci-test: lint type-check test coverage security-check
	@echo "CI test suite complete!"

# Quick validation workflow
quick-test: test-unit lint
	@echo "Quick test suite complete!"

# Full validation workflow
full-test: clean install-dev test-all coverage security-check
	@echo "Full test suite complete!"

# Example workflows
demo: validate-example
	@echo "Demo complete! Example paper validated."

# Compilation targets
compile: compile-latex compile-package
	@echo "Complete compilation finished!"

compile-latex:
	@echo "Compiling LaTeX paper..."
	$(PYTHON) latex_compiler.py --verbose

compile-package:
	@echo "Building Python package..."
	$(PYTHON) compiler.py package --verbose

compile-all:
	@echo "Running full compilation with reports..."
	$(PYTHON) compiler.py all --verbose --report
	$(PYTHON) latex_compiler.py --verbose --report

latex-watch:
	@echo "Starting LaTeX watch mode (Ctrl+C to stop)..."
	$(PYTHON) latex_compiler.py --watch --verbose

latex-clean:
	@echo "Cleaning LaTeX artifacts..."
	rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.synctex.gz
	@echo "LaTeX cleanup complete!"

latex-optimize:
	@echo "Optimizing LaTeX for arXiv submission..."
	$(PYTHON) latex_compiler.py --optimize arxiv --verbose --report

# Debug targets
debug:
	@echo "Debug information:"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Working directory: $$(pwd)"
	@echo "Python path: $$(which $(PYTHON))"
	@echo "LaTeX available: $$(which pdflatex || echo 'Not found')"
	@echo "Available make targets:"
	@$(MAKE) help

# Continuous integration targets
ci-setup:
	$(PIP) install --upgrade pip
	$(MAKE) install-dev

ci-test-unit:
	$(PYTEST) tests/unit/ -v --tb=short --cov=$(SRC_DIRS) --cov-report=xml

ci-test-integration:
	$(PYTEST) tests/integration/ -v --tb=short -m "not slow"

ci-test-performance:
	$(PYTEST) tests/performance/ -v --tb=short -m "not slow and not benchmark"

# Release targets
pre-release: clean full-test package
	@echo "Pre-release checks complete!"

release: pre-release
	@echo "Release package ready in dist/"

# Help for specific categories
help-test:
	@echo "Testing Commands:"
	@echo "  test             Run unit and integration tests"
	@echo "  test-unit        Run only unit tests"
	@echo "  test-integration Run only integration tests"
	@echo "  test-performance Run performance tests"
	@echo "  test-all         Run all tests including slow ones"
	@echo "  coverage         Generate coverage report"
	@echo "  quick-test       Run unit tests and linting"
	@echo "  full-test        Run complete test suite"

help-quality:
	@echo "Code Quality Commands:"
	@echo "  lint             Check code with flake8"
	@echo "  format           Format code with black and isort"
	@echo "  format-check     Check if code is properly formatted"
	@echo "  type-check       Run mypy type checking"
	@echo "  security-check   Run bandit and safety scans"
	@echo "  dev-check        Run all quality checks"

help-dev:
	@echo "Development Commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  dev-setup        Complete development setup"
	@echo "  clean            Clean temporary files"
	@echo "  debug            Show debug information"

help-compile:
	@echo "Compilation Commands:"
	@echo "  compile          Compile everything (LaTeX + package)"
	@echo "  compile-latex    Compile LaTeX paper only"
	@echo "  compile-package  Build Python package only"
	@echo "  compile-all      Full compilation with reports"
	@echo "  latex-watch      Watch LaTeX files and auto-compile"
	@echo "  latex-clean      Clean LaTeX build artifacts"
	@echo "  latex-optimize   Optimize LaTeX for arXiv"
	@echo ""
	@echo "Compilation Tools:"
	@echo "  ./compile.sh     Cross-platform shell script"
	@echo "  python3 latex_compiler.py    Advanced LaTeX compiler"
	@echo "  python3 compiler.py          General compiler"
	@echo "  python3 build.py             Build orchestrator"
	@echo ""
	@echo "Examples:"
	@echo "  make compile                 # Full compilation"
	@echo "  make latex-watch             # Watch mode"
	@echo "  ./compile.sh latex --venue arxiv  # Shell script"
	@echo "  python3 build.py --release  # Release build"
