#!/usr/bin/env python3
"""
Metric consistency unit tests for the research paper.

Tests for ensuring consistency of metrics, figures, and data across the paper.
"""

import re
from pathlib import Path

import pytest


class TestMetricConsistency:
    """Test cases for metric consistency across the paper."""

    @pytest.fixture
    def paper_dir(self):
        """Get the paper directory path."""
        return (
            Path(__file__).parent.parent.parent
            / "docs"
            / "research"
            / "arxiv_submission_package"
        )

    @pytest.fixture
    def main_tex_content(self, paper_dir):
        """Load the main.tex content."""
        main_tex_path = paper_dir / "main.tex"
        if main_tex_path.exists():
            return main_tex_path.read_text()
        return ""

    @pytest.mark.unit
    def test_paper_directory_exists(self, paper_dir):
        """Test that the paper directory exists."""
        assert paper_dir.exists(), f"Paper directory not found: {paper_dir}"

    @pytest.mark.unit
    def test_main_tex_exists(self, paper_dir):
        """Test that main.tex exists."""
        main_tex_path = paper_dir / "main.tex"
        assert main_tex_path.exists(), "main.tex file not found"

    @pytest.mark.unit
    def test_constitutional_hash_consistency(self, main_tex_content):
        """Test that constitutional hash is consistent throughout the paper."""
        # Expected constitutional hash from the system
        expected_hash = "cdd01ef066bc6cf2"

        # Look for hash references in the paper
        hash_pattern = r"[a-f0-9]{16}"
        found_hashes = re.findall(hash_pattern, main_tex_content)

        # If hashes are found, they should match the expected hash
        for found_hash in found_hashes:
            if len(found_hash) == 16:  # Constitutional hash length
                assert (
                    found_hash == expected_hash
                ), f"Found inconsistent hash: {found_hash}"

    @pytest.mark.unit
    def test_figure_references_consistency(self, main_tex_content):
        """Test that all figure references have corresponding figure definitions."""
        # Find all figure references
        fig_refs = re.findall(r"\\ref\{fig:(\w+)\}", main_tex_content)

        # Find all figure labels
        fig_labels = re.findall(r"\\label\{fig:(\w+)\}", main_tex_content)

        # Check that all references have corresponding labels
        for ref in fig_refs:
            assert (
                ref in fig_labels
            ), f"Figure reference 'fig:{ref}' has no corresponding label"

    @pytest.mark.unit
    def test_section_references_consistency(self, main_tex_content):
        """Test that all section references have corresponding section definitions."""
        # Find all section references
        sec_refs = re.findall(r"\\ref\{sec:(\w+)\}", main_tex_content)

        # Find all section labels
        sec_labels = re.findall(r"\\label\{sec:(\w+)\}", main_tex_content)

        # Check that all references have corresponding labels
        for ref in sec_refs:
            assert (
                ref in sec_labels
            ), f"Section reference 'sec:{ref}' has no corresponding label"

    @pytest.mark.unit
    def test_equation_references_consistency(self, main_tex_content):
        """Test that all equation references have corresponding equation definitions."""
        # Find all equation references
        eq_refs = re.findall(r"\\ref\{eq:(\w+)\}", main_tex_content)

        # Find all equation labels
        eq_labels = re.findall(r"\\label\{eq:(\w+)\}", main_tex_content)

        # Check that all references have corresponding labels
        for ref in eq_refs:
            assert (
                ref in eq_labels
            ), f"Equation reference 'eq:{ref}' has no corresponding label"

    @pytest.mark.unit
    def test_table_references_consistency(self, main_tex_content):
        """Test that all table references have corresponding table definitions."""
        # Find all table references
        table_refs = re.findall(r"\\ref\{tab:(\w+)\}", main_tex_content)

        # Find all table labels
        table_labels = re.findall(r"\\label\{tab:(\w+)\}", main_tex_content)

        # Check that all references have corresponding labels
        for ref in table_refs:
            assert (
                ref in table_labels
            ), f"Table reference 'tab:{ref}' has no corresponding label"

    @pytest.mark.unit
    def test_bibliography_consistency(self, paper_dir, main_tex_content):
        """Test that all citations have corresponding bibliography entries."""
        # Check if bibliography file exists
        bib_files = list(paper_dir.glob("*.bib"))

        # Find all citations in the text
        citations = re.findall(r"\\cite\{([^}]+)\}", main_tex_content)

        if bib_files and citations:
            # Read bibliography content
            bib_content = ""
            for bib_file in bib_files:
                bib_content += bib_file.read_text()

            # Find all bibliography entries
            bib_entries = re.findall(r"@\w+\{([^,]+),", bib_content)

            # Check that all citations have corresponding entries
            for citation in citations:
                # Handle multiple citations in one command
                for cite_key in citation.split(","):
                    cite_key = cite_key.strip()
                    assert (
                        cite_key in bib_entries
                    ), f"Citation '{cite_key}' has no corresponding bibliography entry"

    @pytest.mark.unit
    def test_performance_metrics_consistency(self, main_tex_content):
        """Test that performance metrics are consistent throughout the paper."""
        # Look for latency metrics
        latency_pattern = r"(\d+(?:\.\d+)?)\s*ms"
        latency_matches = re.findall(latency_pattern, main_tex_content)

        # Look for throughput metrics
        throughput_pattern = r"(\d+(?:\.\d+)?)\s*RPS"
        throughput_matches = re.findall(throughput_pattern, main_tex_content)

        # Basic consistency check - metrics should be reasonable
        for latency in latency_matches:
            latency_val = float(latency)
            assert (
                0 <= latency_val < 10000
            ), f"Unreasonable latency value: {latency_val}ms"

        for throughput in throughput_matches:
            throughput_val = float(throughput)
            assert (
                0 <= throughput_val < 100000
            ), f"Unreasonable throughput value: {throughput_val}RPS"

    @pytest.mark.unit
    def test_version_consistency(self, main_tex_content):
        """Test that version numbers are consistent throughout the paper."""
        # Look for version patterns specifically for ACGS
        acgs_version_pattern = r"ACGS[\s\-]?(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?)"
        acgs_versions = re.findall(acgs_version_pattern, main_tex_content, re.IGNORECASE)

        # Check that ACGS version is consistent
        if acgs_versions:
            # All ACGS versions should be the same
            unique_versions = set(acgs_versions)
            assert (
                len(unique_versions) <= 1
            ), f"Inconsistent ACGS versions found: {unique_versions}"

    @pytest.mark.unit
    def test_acronym_consistency(self, main_tex_content):
        """Test that acronyms are used consistently."""
        # Common acronyms that should be consistent
        acronyms = {
            "ACGS": r"\bACGS\b",
            "AI": r"\bAI\b",
            "API": r"\bAPI\b",
            "CI": r"\bCI\b",
            "RPS": r"\bRPS\b",
        }

        for acronym, pattern in acronyms.items():
            matches = re.findall(pattern, main_tex_content)
            if matches:
                # Check that the acronym is used consistently (not mixed with lowercase)
                lowercase_pattern = pattern.replace(acronym, acronym.lower())
                lowercase_matches = re.findall(lowercase_pattern, main_tex_content)
                assert (
                    len(lowercase_matches) == 0
                ), f"Inconsistent case for acronym '{acronym}'"
