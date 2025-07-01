#!/usr/bin/env python3
"""
Setup script for Gemini CLI
"""

from pathlib import Path

from setuptools import setup

# Read README
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "Gemini CLI - AI Constitutional Governance System Integration"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = []

setup(
    name="gemini-cli-acgs",
    version="1.0.0",
    description="Gemini CLI with ACGS integration for maximum AI capability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ACGS Team",
    author_email="team@acgs.ai",
    url="https://github.com/your-org/acgs-2",
    packages=[
        "gemini_cli",
        "gemini_cli.commands",
        "gemini_cli.formatters",
        "gemini_cli.tools",
        "gemini_cli.mcp_servers",
    ],
    package_dir={"gemini_cli": "."},
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gemini-cli=gemini_cli.gemini_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    keywords="gemini cli ai constitutional governance acgs mcp",
)
