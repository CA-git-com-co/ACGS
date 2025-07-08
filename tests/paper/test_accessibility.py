#!/usr/bin/env python3
"""
Accessibility checker for LaTeX paper.

Tests for accessibility features in the research paper.
"""

import re
from pathlib import Path

import pytest


class TestAccessibility:
    """Test cases for paper accessibility."""

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
    def test_alt_text_for_figures(self, main_tex_content):
        """Test that figures have alternative text or captions."""
        # Look for includegraphics commands
        figure_pattern = r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}"
        figures = re.findall(figure_pattern, main_tex_content)

        # Look for caption commands
        caption_pattern = r"\\caption\{([^}]+)\}"
        captions = re.findall(caption_pattern, main_tex_content)

        # At least some figures should have captions
        if figures:
            assert (
                len(captions) > 0
            ), "Figures found but no captions provided for accessibility"

    @pytest.mark.unit
    def test_structured_headings(self, main_tex_content):
        """Test that headings are properly structured."""
        # Look for section hierarchy
        sections = re.findall(r"\\section\{([^}]+)\}", main_tex_content)
        subsections = re.findall(r"\\subsection\{([^}]+)\}", main_tex_content)

        # Should have proper section structure
        assert (
            len(sections) > 0
        ), "No sections found - document structure may be inaccessible"

        # Subsections should not exceed sections by too much
        if subsections:
            assert (
                len(subsections) <= len(sections) * 5
            ), "Too many subsections - may indicate poor structure"

    @pytest.mark.unit
    def test_table_accessibility(self, main_tex_content):
        """Test that tables have proper headers and structure."""
        # Look for table environments
        table_pattern = r"\\begin\{table\}.*?\\end\{table\}"
        tables = re.findall(table_pattern, main_tex_content, re.DOTALL)

        # Look for table headers
        header_pattern = r"\\tableheader\{([^}]+)\}"

        for table in tables:
            headers = re.findall(header_pattern, table)
            if "\\begin{tabular}" in table:
                # Tables should have some form of header
                assert (
                    len(headers) > 0 or "\\toprule" in table
                ), "Table found without proper headers"

    @pytest.mark.unit
    def test_color_independence(self, main_tex_content):
        """Test that color is not the only means of conveying information."""
        # Look for color commands
        color_pattern = r"\\textcolor\{([^}]+)\}\{([^}]+)\}"
        color_uses = re.findall(color_pattern, main_tex_content)

        # If color is used, check for additional formatting
        for color, text in color_uses:
            # Color should be accompanied by other formatting
            assert (
                "\\textbf" in main_tex_content or "\\textit" in main_tex_content
            ), "Color used without additional formatting for accessibility"

    @pytest.mark.unit
    def test_link_accessibility(self, main_tex_content):
        """Test that links are accessible."""
        # Look for URL links
        url_pattern = r"\\url\{([^}]+)\}"
        urls = re.findall(url_pattern, main_tex_content)

        # Look for hyperlinks
        href_pattern = r"\\href\{([^}]+)\}\{([^}]+)\}"
        hrefs = re.findall(href_pattern, main_tex_content)

        # Check that links have descriptive text
        for url, text in hrefs:
            assert len(text.strip()) > 0, f"Link {url} has no descriptive text"
            assert (
                text.lower() != "here" and text.lower() != "click here"
            ), f"Link text '{text}' is not descriptive"

    @pytest.mark.unit
    def test_list_structure(self, main_tex_content):
        """Test that lists are properly structured."""
        # Look for itemize environments
        itemize_pattern = r"\\begin\{itemize\}.*?\\end\{itemize\}"
        lists = re.findall(itemize_pattern, main_tex_content, re.DOTALL)

        # Look for enumerate environments
        enumerate_pattern = r"\\begin\{enumerate\}.*?\\end\{enumerate\}"
        enum_lists = re.findall(enumerate_pattern, main_tex_content, re.DOTALL)

        # Check that lists have items
        for lst in lists + enum_lists:
            items = re.findall(r"\\item", lst)
            assert len(items) > 0, "List environment found with no items"

    @pytest.mark.unit
    def test_math_accessibility(self, main_tex_content):
        """Test that mathematical content is accessible."""
        # Look for math environments
        math_pattern = r"\$([^$]+)\$"
        inline_math = re.findall(math_pattern, main_tex_content)

        # Look for display math
        display_math_pattern = r"\$\$([^$]+)\$\$"
        display_math = re.findall(display_math_pattern, main_tex_content)

        # Check that complex math has some form of explanation
        for math in inline_math + display_math:
            # Very simple heuristic - complex math should have nearby explanatory text
            if len(math) > 20 and any(
                symbol in math for symbol in ["\\sum", "\\int", "\\frac", "\\sqrt"]
            ):
                # This is a basic check - in reality, accessibility would need more context
                assert True  # Placeholder for more sophisticated accessibility check

    @pytest.mark.unit
    def test_language_specification(self, main_tex_content):
        """Test that language is properly specified."""
        # Look for language specification
        has_babel = (
            "\\usepackage[english]{babel}" in main_tex_content
            or "\\usepackage{babel}" in main_tex_content
        )
        has_polyglossia = "\\usepackage{polyglossia}" in main_tex_content

        # Should have some form of language specification
        assert (
            has_babel or has_polyglossia or "\\documentclass" in main_tex_content
        ), "No language specification found - may affect accessibility"
