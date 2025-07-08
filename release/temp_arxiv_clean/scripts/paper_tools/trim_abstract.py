#!/usr/bin/env python3
"""
Abstract trimming script for LaTeX documents.
Trims abstract to specified character limit while preserving key claims.
"""

import argparse
import re
import sys


def trim_abstract(text, max_chars=1900):
    """Trim abstract to maximum character count while preserving key claims."""
    if len(text) <= max_chars:
        return text

    # Split into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Priority order: keep key contribution sentences
    priority_patterns = [
        r"We present ACGS",
        r"demonstrates.*contributions?",
        r"key.*contributions?",
        r"research.*contributions?",
        r"Implementation Status",
        r"Availability",
    ]

    # Start with high-priority sentences
    result = []
    total_chars = 0

    # Add high-priority sentences first
    for sentence in sentences:
        for pattern in priority_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                if total_chars + len(sentence) + 1 <= max_chars:
                    result.append(sentence)
                    total_chars += len(sentence) + 1
                break

    # Add remaining sentences if space allows
    for sentence in sentences:
        if sentence not in result and total_chars + len(sentence) + 1 <= max_chars:
            result.append(sentence)
            total_chars += len(sentence) + 1

    return " ".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Trim LaTeX abstract to character limit"
    )
    parser.add_argument(
        "--max-chars", type=int, default=1900, help="Maximum character count"
    )
    parser.add_argument(
        "--file", type=str, default="main.tex", help="LaTeX file to process"
    )
    args = parser.parse_args()

    # Read LaTeX file
    with open(args.file, encoding="utf-8") as f:
        content = f.read()

    # Extract abstract
    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL
    )
    if not abstract_match:
        print("No abstract found in LaTeX file")
        return 1

    original_abstract = abstract_match.group(1).strip()
    print(f"Original abstract length: {len(original_abstract)} characters")

    # Trim abstract
    trimmed_abstract = trim_abstract(original_abstract, args.max_chars)
    print(f"Trimmed abstract length: {len(trimmed_abstract)} characters")

    # Replace in content
    new_content = content.replace(
        f"\\begin{{abstract}}{original_abstract}\\end{{abstract}}",
        f"\\begin{{abstract}}\n{trimmed_abstract}\n\\end{{abstract}}",
    )

    # Write back
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Abstract trimmed and saved to {args.file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
