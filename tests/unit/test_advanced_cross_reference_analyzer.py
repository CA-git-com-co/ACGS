import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tools.validation.advanced_cross_reference_analyzer import (
    AdvancedCrossReferenceAnalyzer,
)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestAdvancedCrossReferenceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = AdvancedCrossReferenceAnalyzer()

    def test_cross_reference_extraction(self):
        """Test extraction of cross-references using the pattern registry."""
        content = """
        This is a test document.

        [Valid link](docs/valid.md)
        [Another link](docs/another.md)

        ![Image](images/example.png)

        `GET /api/v1/resource`

        See also: [Referenced Doc](docs/referenced.md)"""

        # Use a path within the project directory
        file_path = Path(__file__).parent.parent.parent / "docs" / "test.md"
        lines = content.split("\n")

        extracted_references = self.analyzer._extract_cross_references(
            file_path, content, lines
        )

        self.assertEqual(len(extracted_references), 4)

        reference_targets = {ref.target_file for ref in extracted_references}
        expected_targets = {
            "docs/valid.md",
            "docs/another.md",
            "images/example.png",
            "docs/referenced.md",
        }

        self.assertEqual(reference_targets, expected_targets)

        for ref in extracted_references:
            self.assertGreaterEqual(ref.confidence, 0.1)
            self.assertLessEqual(ref.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
