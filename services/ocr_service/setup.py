#!/usr/bin/env python3
"""
Setup script for the OCR service client package.
"""

from setuptools import setup, find_packages
import os

# Read the package version from __init__.py
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "__init__.py"), encoding="utf-8") as f:
    exec(f.read(), about)

# Read the long description from README.md
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="acgs-ocr-client",
    version=about["__version__"],
    description="OCR Service Client for ACGS-1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email="acgs-team@example.com",
    url="https://github.com/acgs/ocr-service-client",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.5b2",
            "mypy>=0.812",
            "ruff>=0.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "acgs-ocr=services.ocr_service.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    keywords="ocr, text extraction, document analysis, ai, vllm",
)
