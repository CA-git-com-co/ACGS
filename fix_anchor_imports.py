#!/usr/bin/env python3
"""
Fix Anchor imports in test files to use the new @coral-xyz/anchor package
"""

from pathlib import Path


def fix_anchor_imports():
    """Fix Anchor imports in all TypeScript test files."""

    # Find all TypeScript test files
    test_files = list(Path("blockchain/tests").glob("*.ts"))

    for test_file in test_files:
        print(f"Fixing imports in {test_file}")

        try:
            with open(test_file, "r") as f:
                content = f.read()

            # Replace old import with new one
            content = content.replace(
                'import * as anchor from "@project-serum/anchor";',
                'import * as anchor from "@coral-xyz/anchor";',
            )
            content = content.replace(
                'import { Program } from "@project-serum/anchor";',
                'import { Program } from "@coral-xyz/anchor";',
            )

            # Write back the fixed content
            with open(test_file, "w") as f:
                f.write(content)

            print(f"✅ Fixed {test_file}")

        except Exception as e:
            print(f"❌ Error fixing {test_file}: {e}")


if __name__ == "__main__":
    fix_anchor_imports()
    print("🎉 All Anchor imports fixed!")
