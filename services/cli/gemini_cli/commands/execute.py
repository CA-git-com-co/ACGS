"""
Code execution commands for Gemini CLI
"""

import argparse
import asyncio
import time
from pathlib import Path
from typing import Any


def add_arguments(parser: argparse.ArgumentParser):
    """Add execute command arguments"""
    subparsers = parser.add_subparsers(
        dest="execute_command", help="Execution commands"
    )

    # Execute code
    code_parser = subparsers.add_parser("code", help="Execute code snippet")
    code_parser.add_argument("--code", required=True, help="Code to execute")
    code_parser.add_argument(
        "--language", default="python", help="Programming language"
    )
    code_parser.add_argument(
        "--timeout", type=int, default=300, help="Execution timeout in seconds"
    )
    code_parser.add_argument(
        "--env", nargs="+", help="Environment variables (KEY=VALUE)"
    )

    # Execute file
    file_parser = subparsers.add_parser("file", help="Execute code from file")
    file_parser.add_argument("file_path", type=Path, help="Path to code file")
    file_parser.add_argument(
        "--language", help="Programming language (auto-detect if not specified)"
    )
    file_parser.add_argument(
        "--timeout", type=int, default=300, help="Execution timeout in seconds"
    )
    file_parser.add_argument(
        "--env", nargs="+", help="Environment variables (KEY=VALUE)"
    )

    # Execute with Gemini assistance
    assist_parser = subparsers.add_parser(
        "assist", help="Execute with Gemini AI assistance"
    )
    assist_parser.add_argument("prompt", help="What you want Gemini to help execute")
    assist_parser.add_argument(
        "--context-file", type=Path, help="Additional context file"
    )
    assist_parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode"
    )

    # Check execution status
    status_parser = subparsers.add_parser("status", help="Check execution status")
    status_parser.add_argument("operation_id", help="Operation ID")
    status_parser.add_argument(
        "--wait", action="store_true", help="Wait for completion"
    )


async def handle_command(args: argparse.Namespace, client) -> dict[str, Any]:
    """Handle execute commands"""

    if args.execute_command == "code":
        # Parse environment variables
        environment = {}
        if args.env:
            for env_var in args.env:
                if "=" in env_var:
                    key, value = env_var.split("=", 1)
                    environment[key] = value

        # Submit code execution
        result = client.execute_code(
            code=args.code, language=args.language, environment=environment
        )

        operation_id = result.get("operation_id")

        # Wait for completion if requested
        if operation_id:
            return await wait_for_operation(client, operation_id, args.timeout)

        return result

    if args.execute_command == "file":
        # Read code from file
        if not args.file_path.exists():
            return {"error": f"File not found: {args.file_path}"}

        code = args.file_path.read_text()

        # Auto-detect language if not specified
        language = args.language
        if not language:
            ext_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".go": "go",
                ".rs": "rust",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
            }
            language = ext_map.get(args.file_path.suffix, "text")

        # Parse environment variables
        environment = {}
        if args.env:
            for env_var in args.env:
                if "=" in env_var:
                    key, value = env_var.split("=", 1)
                    environment[key] = value

        # Submit execution
        result = client.execute_code(
            code=code, language=language, environment=environment
        )

        operation_id = result.get("operation_id")

        # Wait for completion
        if operation_id:
            return await wait_for_operation(client, operation_id, args.timeout)

        return result

    if args.execute_command == "assist":
        # Execute with Gemini assistance
        context = ""
        if args.context_file and args.context_file.exists():
            context = args.context_file.read_text()

        # This would integrate with Gemini API to generate and execute code
        # For now, return a placeholder
        return {
            "message": "Gemini-assisted execution",
            "prompt": args.prompt,
            "context_provided": bool(context),
            "interactive": args.interactive,
            "note": "Full Gemini integration pending",
        }

    if args.execute_command == "status":
        # Check execution status
        status = client.get_operation_status(args.operation_id)

        if args.wait and status.get("status") in ["pending", "running"]:
            return await wait_for_operation(client, args.operation_id, timeout=300)

        return status

    return {"error": "Unknown execute command"}


async def wait_for_operation(
    client, operation_id: str, timeout: int = 300
) -> dict[str, Any]:
    """Wait for operation to complete"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        status = client.get_operation_status(operation_id)

        if status.get("status") in ["completed", "failed", "rejected"]:
            return status

        await asyncio.sleep(2)

    return {
        "operation_id": operation_id,
        "status": "timeout",
        "message": f"Operation timed out after {timeout} seconds",
    }
