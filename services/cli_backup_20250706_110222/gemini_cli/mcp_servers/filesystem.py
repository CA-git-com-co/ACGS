"""
Filesystem MCP Server for Gemini CLI
Enhanced file system operations with security controls
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import hashlib
import logging
import mimetypes
from pathlib import Path
from typing import Any

# Simplified MCP implementation for filesystem operations
logger = logging.getLogger(__name__)


class FilesystemMCPServer:
    """MCP server for secure filesystem operations"""

    def __init__(self, root_path: str = "/"):
        self.root_path = Path(root_path).resolve()
        self.allowed_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".json",
            ".yaml",
            ".yml",
            ".xml",
            ".csv",
            ".log",
            ".conf",
            ".cfg",
            ".ini",
            ".sh",
            ".bat",
            ".sql",
            ".html",
            ".css",
            ".ts",
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the MCP server"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access"""
        try:
            resolved = path.resolve()
            return str(resolved).startswith(str(self.root_path))
        except Exception:
            return False

    def get_file_info(self, path: Path) -> dict[str, Any]:
        """Get file information"""
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))

        return {
            "name": path.name,
            "path": str(path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_directory": path.is_dir(),
            "is_file": path.is_file(),
            "mime_type": mime_type,
            "extension": path.suffix.lower(),
        }

    def calculate_hash(self, content: bytes) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content).hexdigest()

    async def list_directory(self, path_str: str, pattern: str = "*") -> dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(path_str)
            if not self.is_safe_path(path):
                return {"error": "Path not allowed"}

            if not path.exists():
                return {"error": "Path does not exist"}

            if not path.is_dir():
                return {"error": "Path is not a directory"}

            items = []
            for item in path.glob(pattern):
                if item.name.startswith("."):
                    continue  # Skip hidden files

                try:
                    info = self.get_file_info(item)
                    items.append(info)
                except Exception as e:
                    logger.warning(f"Error getting info for {item}: {e}")

            return {
                "path": str(path),
                "items": sorted(
                    items, key=lambda x: (not x["is_directory"], x["name"])
                ),
                "count": len(items),
            }

        except Exception as e:
            logger.error(f"Error listing directory {path_str}: {e}")
            return {"error": str(e)}

    async def read_file(self, path_str: str, encoding: str = "utf-8") -> dict[str, Any]:
        """Read file content"""
        try:
            path = Path(path_str)
            if not self.is_safe_path(path):
                return {"error": "Path not allowed"}

            if not path.exists():
                return {"error": "File does not exist"}

            if not path.is_file():
                return {"error": "Path is not a file"}

            # Check file size
            if path.stat().st_size > self.max_file_size:
                return {"error": f"File too large (max {self.max_file_size} bytes)"}

            # Check extension
            if path.suffix.lower() not in self.allowed_extensions:
                return {"error": f"File extension not allowed: {path.suffix}"}

            # Read content
            if encoding == "binary":
                content = path.read_bytes()
                content_hash = self.calculate_hash(content)
                return {
                    "path": str(path),
                    "content": content.hex(),
                    "encoding": "binary",
                    "size": len(content),
                    "hash": content_hash,
                }
            content = path.read_text(encoding=encoding)
            content_hash = self.calculate_hash(content.encode(encoding))
            return {
                "path": str(path),
                "content": content,
                "encoding": encoding,
                "size": len(content),
                "hash": content_hash,
                "lines": content.count("\n") + 1,
            }

        except Exception as e:
            logger.error(f"Error reading file {path_str}: {e}")
            return {"error": str(e)}

    async def write_file(
        self,
        path_str: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> dict[str, Any]:
        """Write content to file"""
        try:
            path = Path(path_str)
            if not self.is_safe_path(path):
                return {"error": "Path not allowed"}

            # Check extension
            if path.suffix.lower() not in self.allowed_extensions:
                return {"error": f"File extension not allowed: {path.suffix}"}

            # Check content size
            if len(content.encode(encoding)) > self.max_file_size:
                return {"error": f"Content too large (max {self.max_file_size} bytes)"}

            # Create directories if needed
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            path.write_text(content, encoding=encoding)

            # Calculate hash
            content_hash = self.calculate_hash(content.encode(encoding))

            return {
                "path": str(path),
                "written": len(content),
                "encoding": encoding,
                "hash": content_hash,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error writing file {path_str}: {e}")
            return {"error": str(e)}

    async def search_files(
        self, query: str, path_str: str = None, case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Search for files containing query"""
        try:
            search_path = Path(path_str) if path_str else self.root_path
            if not self.is_safe_path(search_path):
                return {"error": "Path not allowed"}

            results = []

            for file_path in search_path.rglob("*"):
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() not in self.allowed_extensions:
                    continue

                if file_path.stat().st_size > self.max_file_size:
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    # Search for query
                    search_content = content if case_sensitive else content.lower()
                    search_query = query if case_sensitive else query.lower()

                    if search_query in search_content:
                        # Find line numbers
                        lines = content.split("\n")
                        matching_lines = []

                        for i, line in enumerate(lines):
                            line_search = line if case_sensitive else line.lower()
                            if search_query in line_search:
                                matching_lines.append(
                                    {"line_number": i + 1, "content": line.strip()}
                                )

                        results.append(
                            {
                                "path": str(file_path),
                                "matches": len(matching_lines),
                                "matching_lines": matching_lines[:10],  # Limit results
                            }
                        )

                except Exception as e:
                    logger.debug(f"Error searching in {file_path}: {e}")
                    continue

            return {
                "query": query,
                "search_path": str(search_path),
                "results": results,
                "total_files": len(results),
            }

        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return {"error": str(e)}

    async def get_file_stats(self, path_str: str) -> dict[str, Any]:
        """Get detailed file statistics"""
        try:
            path = Path(path_str)
            if not self.is_safe_path(path):
                return {"error": "Path not allowed"}

            if not path.exists():
                return {"error": "Path does not exist"}

            info = self.get_file_info(path)

            if path.is_file():
                # Additional file stats
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    info.update(
                        {
                            "lines": content.count("\n") + 1,
                            "characters": len(content),
                            "words": len(content.split()),
                            "hash": self.calculate_hash(content.encode("utf-8")),
                        }
                    )
                except Exception as e:
                    logger.debug(f"Error getting file stats: {e}")

            elif path.is_dir():
                # Directory stats
                file_count = 0
                dir_count = 0
                total_size = 0

                for item in path.rglob("*"):
                    if item.is_file():
                        file_count += 1
                        try:
                            total_size += item.stat().st_size
                        except Exception:
                            pass
                    elif item.is_dir():
                        dir_count += 1

                info.update(
                    {
                        "files": file_count,
                        "directories": dir_count,
                        "total_size": total_size,
                    }
                )

            return info

        except Exception as e:
            logger.error(f"Error getting file stats for {path_str}: {e}")
            return {"error": str(e)}

    async def handle_request(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle MCP requests"""
        try:
            if method == "list_directory":
                return await self.list_directory(
                    params.get("path", "."), params.get("pattern", "*")
                )

            if method == "read_file":
                return await self.read_file(
                    params["path"], params.get("encoding", "utf-8")
                )

            if method == "write_file":
                return await self.write_file(
                    params["path"],
                    params["content"],
                    params.get("encoding", "utf-8"),
                    params.get("create_dirs", True),
                )

            if method == "search_files":
                return await self.search_files(
                    params["query"],
                    params.get("path"),
                    params.get("case_sensitive", False),
                )

            if method == "get_file_stats":
                return await self.get_file_stats(params["path"])

            return {"error": f"Unknown method: {method}"}

        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return {"error": str(e)}


async def main():
    """Main function to run the filesystem MCP server"""
    import argparse

    parser = argparse.ArgumentParser(description="Filesystem MCP Server")
    parser.add_argument("--root", default="/", help="Root directory path")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    args = parser.parse_args()

    server = FilesystemMCPServer(args.root)
    logger.info(f"Starting Filesystem MCP Server on port {args.port}")
    logger.info(f"Root path: {server.root_path}")

    # Simple server loop for demonstration
    # In a real implementation, this would use proper MCP protocol
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
