#!/usr/bin/env python3
"""
Setup script for Academic Submission System.

This script configures the package for installation and distribution.
"""

import sys
from pathlib import Path

from setuptools import find_packages, setup

# Ensure we're in the right directory
if not Path("quality_assurance").exists():
    print("Error: setup.py must be run from the arxiv_submission_package directory")
    sys.exit(1)


# Read version from __init__.py
def get_version():
    """Extract version from package __init__.py."""
    init_file = Path("quality_assurance") / "__init__.py"
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip("\"'")
    return "1.0.0"


# Read long description from README
def get_long_description():
    """Get long description from README file."""
    readme_file = Path("README.md")
    if readme_file.exists():
        with open(readme_file, encoding="utf-8") as f:
            return f.read()
    return "Academic Submission System for validating and optimizing academic papers."


# Read requirements from requirements.txt
def get_requirements():
    """Get requirements from requirements.txt."""
    req_file = Path("requirements.txt")
    if req_file.exists():
        with open(req_file) as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


# Read test requirements
def get_test_requirements():
    """Get test requirements from requirements-test.txt."""
    req_file = Path("requirements-test.txt")
    if req_file.exists():
        with open(req_file) as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


# Package metadata
NAME = "academic-submission-system"
VERSION = get_version()
DESCRIPTION = (
    "Production-ready academic paper validation and compliance checking system"
)
LONG_DESCRIPTION = get_long_description()
AUTHOR = "Martin Honglin Lyu"
AUTHOR_EMAIL = "info@soln.ai"
URL = "https://github.com/CA-git-com-co/ACGS"
LICENSE = "MIT"

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
    "Topic :: Text Processing :: Markup :: LaTeX",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Education",
    "Environment :: Console",
    "Environment :: Web Environment",
]

# Keywords for PyPI
KEYWORDS = [
    "academic",
    "submission",
    "validation",
    "latex",
    "arxiv",
    "ieee",
    "acm",
    "paper",
    "research",
    "publishing",
    "compliance",
    "quality-assurance",
    "bibliography",
    "bibtex",
    "figures",
    "accessibility",
    "reproducibility",
]

# Entry points for command-line scripts
ENTRY_POINTS = {
    "console_scripts": [
        "academic-validate=cli.academic_cli:main",
        "academic-cli=cli.academic_cli:main",
    ],
}

# Package data to include
PACKAGE_DATA = {
    "quality_assurance": [
        "config/*.json",
        "templates/*.tex",
        "schemas/*.json",
    ],
    "web": [
        "templates/*.html",
        "static/css/*.css",
        "static/js/*.js",
        "static/images/*",
    ],
    "cli": [
        "templates/*.txt",
    ],
}

# Data files to include in distribution
DATA_FILES = [
    (
        "docs",
        [
            "docs/academic_submission_system/README.md",
            "docs/academic_submission_system/USER_GUIDE.md",
            "docs/academic_submission_system/API_REFERENCE.md",
            "docs/academic_submission_system/TUTORIAL.md",
            "docs/academic_submission_system/TESTING_GUIDE.md",
            "docs/academic_submission_system/EXAMPLES.md",
        ],
    ),
    (
        "config",
        [
            "config.json",
        ],
    ),
    (
        "examples",
        [
            "example_paper/main.tex",
            "example_paper/README.txt",
        ],
    ),
]

# Extra requirements for optional features
EXTRAS_REQUIRE = {
    "web": [
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
    ],
    "performance": [
        "psutil>=5.9.0",
        "memory-profiler>=0.61.0",
    ],
    "dev": get_test_requirements()
    + [
        "pre-commit>=3.3.0",
        "black>=23.7.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.5.0",
        "bandit>=1.7.5",
    ],
    "docs": [
        "sphinx>=7.1.0",
        "sphinx-rtd-theme>=1.3.0",
        "myst-parser>=2.0.0",
    ],
    "all": [],  # Will be populated below
}

# Populate 'all' extra with all other extras
EXTRAS_REQUIRE["all"] = list(
    set(
        req
        for extra_reqs in EXTRAS_REQUIRE.values()
        for req in extra_reqs
        if isinstance(req, str)
    )
)

# Python version requirement
PYTHON_REQUIRES = ">=3.9"

# Project URLs for PyPI
PROJECT_URLS = {
    "Homepage": URL,
    "Documentation": f"{URL}/tree/master/docs",
    "Source": URL,
    "Tracker": f"{URL}/issues",
    "Changelog": f"{URL}/blob/master/CHANGELOG.md",
}

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data=PACKAGE_DATA,
    data_files=DATA_FILES,
    include_package_data=True,
    # Dependencies
    install_requires=get_requirements(),
    extras_require=EXTRAS_REQUIRE,
    python_requires=PYTHON_REQUIRES,
    # Entry points
    entry_points=ENTRY_POINTS,
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    # Options
    zip_safe=False,
    platforms=["any"],
    # Testing
    test_suite="tests",
    tests_require=get_test_requirements(),
    # Command classes for custom commands
    cmdclass={},
)

# Post-installation message
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Academic Submission System Installation")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Author: {AUTHOR}")
    print(f"License: {LICENSE}")
    print("\nInstallation complete!")
    print("\nQuick start:")
    print("  academic-validate --help")
    print("  academic-validate /path/to/paper/")
    print("\nWeb interface:")
    print("  python -m web.app")
    print("\nDocumentation:")
    print("  See docs/ directory for comprehensive guides")
    print("=" * 60)
