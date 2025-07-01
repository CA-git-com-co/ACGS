"""
Gemini CLI Tools Manager
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gemini_config import GeminiConfig

logger = logging.getLogger(__name__)


class ToolManager:
    """Manager for Gemini tools integration"""

    def __init__(self, config: GeminiConfig):
        self.config = config
        self.enabled_tools = self._get_enabled_tools()

    def _get_enabled_tools(self) -> list[str]:
        """Get list of enabled tools"""
        tools = []
        if self.config.tools.file_system:
            tools.append("file_system")
        if self.config.tools.web_fetch:
            tools.append("web_fetch")
        if self.config.tools.web_search:
            tools.append("web_search")
        if self.config.tools.shell_execution:
            tools.append("shell_execution")
        if self.config.tools.memory:
            tools.append("memory")
        if self.config.tools.multi_file_read:
            tools.append("multi_file_read")
        if self.config.tools.sandbox_execution:
            tools.append("sandbox_execution")
        return tools

    async def execute_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.enabled_tools:
            return {"error": f"Tool '{tool_name}' is not enabled"}

        try:
            if tool_name == "file_system":
                return await self._execute_file_system(parameters)
            if tool_name == "web_fetch":
                return await self._execute_web_fetch(parameters)
            if tool_name == "web_search":
                return await self._execute_web_search(parameters)
            if tool_name == "shell_execution":
                return await self._execute_shell(parameters)
            if tool_name == "memory":
                return await self._execute_memory(parameters)
            if tool_name == "multi_file_read":
                return await self._execute_multi_file_read(parameters)
            if tool_name == "sandbox_execution":
                return await self._execute_sandbox(parameters)
            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}

    async def _execute_file_system(self, params: dict) -> dict:
        """Execute file system operations"""
        operation = params.get("operation")

        if operation == "read":
            path = Path(params.get("path"))
            if path.exists():
                content = path.read_text()
                return {"path": str(path), "content": content, "size": len(content)}
            return {"error": f"File not found: {path}"}

        if operation == "write":
            path = Path(params.get("path"))
            content = params.get("content", "")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return {"path": str(path), "written": len(content), "status": "success"}

        if operation == "list":
            path = Path(params.get("path", "."))
            if path.is_dir():
                items = []
                for item in path.iterdir():
                    items.append(
                        {
                            "name": item.name,
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None,
                        }
                    )
                return {"path": str(path), "items": items, "count": len(items)}
            return {"error": f"Not a directory: {path}"}

        return {"error": f"Unknown file system operation: {operation}"}

    async def _execute_web_fetch(self, params: dict) -> dict:
        """Fetch content from web URL"""
        url = params.get("url")
        if not url:
            return {"error": "URL is required"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    content = await response.text()
                    return {
                        "url": url,
                        "status_code": response.status,
                        "content": content[:5000],  # Limit content size
                        "content_type": response.headers.get("Content-Type"),
                        "truncated": len(content) > 5000,
                    }
            except aiohttp.ClientError as e:
                return {"error": f"Failed to fetch URL: {e}"}

    async def _execute_web_search(self, params: dict) -> dict:
        """Execute web search (placeholder)"""
        query = params.get("query")
        if not query:
            return {"error": "Query is required"}

        # This would integrate with actual search API
        return {
            "query": query,
            "results": [
                {
                    "title": f"Result 1 for: {query}",
                    "url": "https://example.com/1",
                    "snippet": "This is a mock search result...",
                },
                {
                    "title": f"Result 2 for: {query}",
                    "url": "https://example.com/2",
                    "snippet": "Another mock search result...",
                },
            ],
            "total_results": 2,
        }

    async def _execute_shell(self, params: dict) -> dict:
        """Execute shell command"""
        import subprocess

        command = params.get("command")
        if not command:
            return {"error": "Command is required"}

        # Security check
        forbidden_commands = ["rm -rf", "format", "dd", "mkfs"]
        if any(forbidden in command for forbidden in forbidden_commands):
            return {"error": "Command contains forbidden operations"}

        try:
            result = subprocess.run(
                command,
                check=False,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )

            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:1000],
                "truncated": len(result.stdout) > 5000,
            }

        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 60 seconds"}
        except Exception as e:
            return {"error": f"Command execution failed: {e}"}

    async def _execute_memory(self, params: dict) -> dict:
        """Execute memory operations"""
        operation = params.get("operation")
        memory_file = Path.home() / ".gemini_cli" / "memory.json"

        if operation == "save":
            key = params.get("key")
            value = params.get("value")

            if not key:
                return {"error": "Key is required"}

            # Load existing memory
            memory = {}
            if memory_file.exists():
                memory = json.loads(memory_file.read_text())

            # Save new value
            memory[key] = value
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            memory_file.write_text(json.dumps(memory, indent=2))

            return {"operation": "save", "key": key, "status": "success"}

        if operation == "load":
            key = params.get("key")

            if not memory_file.exists():
                return {"error": "No memory found"}

            memory = json.loads(memory_file.read_text())

            if key:
                if key in memory:
                    return {"operation": "load", "key": key, "value": memory[key]}
                return {"error": f"Key not found: {key}"}
            return {"operation": "load", "memory": memory}

        return {"error": f"Unknown memory operation: {operation}"}

    async def _execute_multi_file_read(self, params: dict) -> dict:
        """Read multiple files"""
        paths = params.get("paths", [])
        results = {}
        errors = []

        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                try:
                    results[str(path)] = path.read_text()
                except Exception as e:
                    errors.append(f"Failed to read {path}: {e}")
            else:
                errors.append(f"File not found: {path}")

        return {"files_read": len(results), "results": results, "errors": errors}

    async def _execute_sandbox(self, params: dict) -> dict:
        """Execute code in ACGS sandbox"""
        # This integrates with ACGS sandbox service
        from acgs_client import ACGSClient

        client = ACGSClient(self.config)

        code = params.get("code")
        language = params.get("language", "python")

        if not code:
            return {"error": "Code is required"}

        # Submit to sandbox
        result = client.execute_code(
            code=code, language=language, environment=params.get("environment", {})
        )

        return result

    def get_tool_schema(self, tool_name: str) -> dict:
        """Get schema for a tool"""
        schemas = {
            "file_system": {
                "description": "File system operations",
                "parameters": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "list"],
                        "description": "Operation to perform",
                    },
                    "path": {"type": "string", "description": "File or directory path"},
                    "content": {
                        "type": "string",
                        "description": "Content for write operation",
                    },
                },
            },
            "web_fetch": {
                "description": "Fetch content from web URL",
                "parameters": {
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL to fetch",
                    }
                },
            },
            "web_search": {
                "description": "Search the web",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"}
                },
            },
            "shell_execution": {
                "description": "Execute shell commands",
                "parameters": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    }
                },
            },
            "memory": {
                "description": "Persistent memory operations",
                "parameters": {
                    "operation": {
                        "type": "string",
                        "enum": ["save", "load"],
                        "description": "Memory operation",
                    },
                    "key": {"type": "string", "description": "Memory key"},
                    "value": {"description": "Value to save (for save operation)"},
                },
            },
            "sandbox_execution": {
                "description": "Execute code in ACGS sandbox",
                "parameters": {
                    "code": {"type": "string", "description": "Code to execute"},
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                    "environment": {
                        "type": "object",
                        "description": "Environment variables",
                    },
                },
            },
        }

        return schemas.get(tool_name, {})
