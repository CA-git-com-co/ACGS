#!/usr/bin/env python3
"""
Unit tests for AdvancedCrossReferenceAnalyzer with pluggable pattern engine.
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import yaml

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tools.validation.advanced_cross_reference_analyzer import (
    AdvancedCrossReferenceAnalyzer,
    CrossReference,
)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestCrossReferencePatterns(unittest.TestCase):
    """Test the refactored cross-reference analyzer with pattern registry."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_pattern_registry = {
            "version": "1.0",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "categories": {
                "markdown_links": {
                    "description": "Standard markdown link formats",
                    "base_confidence": 0.8,
                },
                "image_media": {
                    "description": "Image and media file references",
                    "base_confidence": 0.9,
                },
                "semantic_relationships": {
                    "description": "Context-based semantic relationships",
                    "base_confidence": 0.6,
                },
            },
            "patterns": [
                {
                    "name": "markdown_link",
                    "category": "markdown_links",
                    "regex": r"\[([^\]]+)\]\(([^)]+)\)",
                    "capture_groups": {"text": 1, "url": 2},
                    "reference_type": "direct",
                    "exclusions": [r"^https?://", r"^mailto:"],
                },
                {
                    "name": "image_reference",
                    "category": "image_media",
                    "regex": r"!\[([^\]]*)\]\(([^)]+)\)",
                    "capture_groups": {"alt_text": 1, "url": 2},
                    "reference_type": "media",
                    "exclusions": [r"^https?://", r"^data:"],
                },
                {
                    "name": "bidirectional_reference",
                    "category": "semantic_relationships",
                    "regex": r"(?:see also|related|refer to)\s*:?\s*\[([^\]]+)\]\(([^)]+)\)",
                    "capture_groups": {"text": 1, "url": 2},
                    "reference_type": "semantic",
                    "exclusions": [],
                },
            ],
            "confidence_scoring": {
                "base_confidence": 1.0,
                "max_confidence": 1.0,
                "min_confidence": 0.1,
                "text_quality": {
                    "generic_terms": ["here", "link", "click here", "this"],
                    "descriptive_terms": {"min_length": 5, "modifier": 0.2},
                    "action_terms": {
                        "terms": ["see", "refer", "documentation"],
                        "modifier": 0.1,
                    },
                },
            },
        }

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_pattern_registry_loading(self, mock_path):
        """Test loading of pattern registry from YAML file."""

        # Mock the YAML content
        yaml_content = yaml.dump(self.test_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            # Verify pattern registry is loaded
            self.assertIsNotNone(analyzer.pattern_registry)
            self.assertEqual(
                analyzer.pattern_registry["constitutional_hash"], CONSTITUTIONAL_HASH
            )
            self.assertEqual(len(analyzer.pattern_registry["patterns"]), 3)

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_pattern_compilation(self, mock_path):
        """Test compilation of regex patterns from registry."""

        yaml_content = yaml.dump(self.test_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            # Verify patterns are compiled
            self.assertEqual(len(analyzer.compiled_patterns), 3)

            # Check compiled pattern structure
            for pattern_info in analyzer.compiled_patterns:
                self.assertIn("pattern", pattern_info)
                self.assertIn("type", pattern_info)
                self.assertIn("groups", pattern_info)
                self.assertIn("base_confidence", pattern_info)

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_cross_reference_extraction(self, mock_path):
        """Test extraction of cross-references using pattern registry."""

        yaml_content = yaml.dump(self.test_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            # Test content with various reference types
            test_content = """
            # Test Document
            
            This is a test document with various references.
            
            [Standard Link](docs/example.md)
            ![Image](images/diagram.png)
            See also: [Related Document](docs/related.md)
            [External Link](https://example.com)
            """

            test_file_path = Path("/test/docs/test.md")
            lines = test_content.split("\n")

            # Mock the relative_to method
            with patch.object(
                test_file_path, "relative_to", return_value=Path("test/docs/test.md")
            ):
                references = analyzer._extract_cross_references(
                    test_file_path, test_content, lines
                )

            # Verify extracted references
            self.assertGreater(len(references), 0)

            # Check reference types
            reference_types = {ref.reference_type for ref in references}
            expected_types = {"direct", "media", "semantic"}
            self.assertTrue(reference_types.intersection(expected_types))

            # Verify confidence scores are within bounds
            for ref in references:
                self.assertGreaterEqual(ref.confidence, 0.1)
                self.assertLessEqual(ref.confidence, 1.0)

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_confidence_scoring(self, mock_path):
        """Test confidence scoring based on pattern modifiers."""

        yaml_content = yaml.dump(self.test_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            # Test confidence calculation
            pattern_info = {"base_confidence": 0.8, "groups": {"text": 1, "url": 2}}

            # Test with descriptive text
            confidence1 = analyzer._calculate_confidence(
                "Documentation Guide",
                "See [Documentation Guide](docs/guide.md)",
                "",
                pattern_info,
            )

            # Test with generic text
            confidence2 = analyzer._calculate_confidence(
                "here", "Click [here](docs/guide.md)", "", pattern_info
            )

            # Descriptive text should have higher confidence
            self.assertGreater(confidence1, confidence2)

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_exclusion_patterns(self, mock_path):
        """Test that exclusion patterns properly filter out unwanted references."""

        yaml_content = yaml.dump(self.test_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            test_content = """
            [Local Link](docs/local.md)
            [External Link](https://example.com)
            [Email Link](mailto:test@example.com)
            """

            test_file_path = Path("/test/docs/test.md")
            lines = test_content.split("\n")

            with patch.object(
                test_file_path, "relative_to", return_value=Path("test/docs/test.md")
            ):
                references = analyzer._extract_cross_references(
                    test_file_path, test_content, lines
                )

            # Only local link should be extracted (external and email should be excluded)
            local_refs = [
                ref for ref in references if ref.target_file == "docs/local.md"
            ]
            external_refs = [ref for ref in references if "https://" in ref.target_file]
            email_refs = [ref for ref in references if "mailto:" in ref.target_file]

            self.assertGreater(len(local_refs), 0)
            self.assertEqual(len(external_refs), 0)
            self.assertEqual(len(email_refs), 0)

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_error_handling(self, mock_path):
        """Test error handling during pattern matching."""

        # Create pattern with invalid regex
        invalid_pattern_registry = self.test_pattern_registry.copy()
        invalid_pattern_registry["patterns"][0]["regex"] = r"[invalid regex("

        yaml_content = yaml.dump(invalid_pattern_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            # This should handle the regex compilation error gracefully
            try:
                analyzer = AdvancedCrossReferenceAnalyzer()
                # If we get here, error handling worked
                self.assertTrue(True)
            except Exception:
                # If exception propagates, error handling failed
                self.fail("Error handling failed for invalid regex pattern")

    @patch("tools.validation.advanced_cross_reference_analyzer.Path")
    def test_new_pattern_types(self, mock_path):
        """Test new pattern types from Step 2 implementation."""

        # Add new patterns to registry
        enhanced_registry = self.test_pattern_registry.copy()
        enhanced_registry["patterns"].extend(
            [
                {
                    "name": "include_directive",
                    "category": "markdown_links",
                    "regex": r"@include\s+([^\s]+)",
                    "capture_groups": {"path": 1},
                    "reference_type": "include",
                    "exclusions": [],
                },
                {
                    "name": "anchor_link",
                    "category": "markdown_links",
                    "regex": r"\[([^\]]+)\]\(#([^)]+)\)",
                    "capture_groups": {"text": 1, "anchor": 2},
                    "reference_type": "anchor",
                    "exclusions": [],
                },
            ]
        )

        yaml_content = yaml.dump(enhanced_registry)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            analyzer = AdvancedCrossReferenceAnalyzer()

            test_content = """
            @include shared/common.yml
            [Section Link](#introduction)
            """

            test_file_path = Path("/test/docs/test.md")
            lines = test_content.split("\n")

            with patch.object(
                test_file_path, "relative_to", return_value=Path("test/docs/test.md")
            ):
                references = analyzer._extract_cross_references(
                    test_file_path, test_content, lines
                )

            # Verify new pattern types are detected
            include_refs = [
                ref for ref in references if ref.reference_type == "include"
            ]
            anchor_refs = [ref for ref in references if ref.reference_type == "anchor"]

            self.assertGreater(len(include_refs), 0)
            self.assertGreater(len(anchor_refs), 0)


class TestPatternRegistryIntegration(unittest.TestCase):
    """Integration tests for pattern registry functionality."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pattern_file = Path(self.temp_dir) / "cross_reference_patterns.yaml"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_end_to_end_pattern_processing(self):
        """Test end-to-end pattern processing with real YAML file."""

        # Create a minimal pattern registry
        minimal_registry = {
            "version": "1.0",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "categories": {"markdown_links": {"base_confidence": 0.8}},
            "patterns": [
                {
                    "name": "test_pattern",
                    "category": "markdown_links",
                    "regex": r"\[([^\]]+)\]\(([^)]+)\)",
                    "capture_groups": {"text": 1, "url": 2},
                    "reference_type": "test",
                    "exclusions": [r"^https?://"],
                }
            ],
            "confidence_scoring": {
                "base_confidence": 1.0,
                "max_confidence": 1.0,
                "min_confidence": 0.1,
                "text_quality": {
                    "generic_terms": ["here"],
                    "descriptive_terms": {"min_length": 5, "modifier": 0.2},
                    "action_terms": {"terms": ["see"], "modifier": 0.1},
                },
            },
        }

        # Write registry to file
        with open(self.pattern_file, "w") as f:
            yaml.dump(minimal_registry, f)

        # Patch the pattern file path
        with patch(
            "tools.validation.advanced_cross_reference_analyzer.REPO_ROOT",
            self.temp_dir,
        ):
            with patch(
                "tools.validation.advanced_cross_reference_analyzer.Path"
            ) as mock_path_class:
                mock_path_class.return_value = self.temp_dir

                # This should work end-to-end
                analyzer = AdvancedCrossReferenceAnalyzer()

                self.assertIsNotNone(analyzer.pattern_registry)
                self.assertEqual(len(analyzer.compiled_patterns), 1)


if __name__ == "__main__":
    unittest.main()
