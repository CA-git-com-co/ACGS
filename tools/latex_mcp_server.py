#!/usr/bin/env python3
"""
MCP Server for LaTeX compilation in ACGS-1
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def handle_compile_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle LaTeX compilation request via MCP protocol"""
    try:
        # Extract parameters from request
        request.get("tex_file", "ACGS-PGP-Enhanced.tex")
        request.get("output_dir", "compiled")

        # Run the compilation script
        result = subprocess.run(
            ["python", "/home/dislove/ACGS-1/scripts/compile_latex_paper.py"],
            check=False,
            capture_output=True,
            text=True,
        )

        # Check if compilation was successful
        success = result.returncode == 0
        pdf_path = Path(
            "/home/dislove/ACGS-1/docs/research/enhanced/compiled/ACGS-PGP-Enhanced.pdf"
        )

        return {
            "success": success,
            "pdf_exists": pdf_path.exists(),
            "pdf_path": str(pdf_path) if pdf_path.exists() else None,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main MCP server loop"""
    # Read request from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line)
            command = request.get("command")

            if command == "compile":
                response = handle_compile_request(request)
            else:
                response = {"success": False, "error": f"Unknown command: {command}"}

            # Write response to stdout
            print(json.dumps(response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            print(json.dumps({"success": False, "error": "Invalid JSON request"}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
