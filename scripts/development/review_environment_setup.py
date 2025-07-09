#!/usr/bin/env python3
"""
ACGS-2 Repository Review Environment Setup and Indexing
Constitutional Hash: cdd01ef066bc6cf2

This script loads the full repository into a review environment, indexes service
directories, config files, and documentation, and verifies availability of analysis tools.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Constitutional compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSRepositoryIndexer:
    """
    Comprehensive repository indexing and analysis tool with constitutional compliance.
    """

    def __init__(self, repo_root: str = "/home/dislove/ACGS-2"):
        self.repo_root = Path(repo_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.start_time = time.time()

        # Initialize indexing structures
        self.services_index = {}
        self.config_index = {}
        self.docs_index = {}
        self.constitutional_files = set()
        self.analysis_tools = {}

        # File type mappings
        self.service_patterns = [
            "*/services/*",
            "*/main.py",
            "*/app.py",
            "*/server.py",
            "*_service.py",
            "*/Dockerfile*",
            "*/docker-compose*.yml",
            "*/requirements*.txt",
        ]

        self.config_patterns = [
            "*.yml",
            "*.yaml",
            "*.json",
            "*.toml",
            "*.ini",
            "*.conf",
            "*.env*",
            "*/config/*",
            "*/configs/*",
            "*/configuration/*",
        ]

        self.docs_patterns = [
            "*.md",
            "*.rst",
            "*.txt",
            "*/docs/*",
            "*/documentation/*",
            "README*",
        ]

    def log_status(self, message: str, level: str = "INFO"):
        """Log with constitutional hash validation."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{timestamp}] [{level}] [Constitutional Hash: {self.constitutional_hash}] {message}"
        )

    def validate_constitutional_hash(self) -> bool:
        """Verify constitutional hash integration throughout the repository."""
        self.log_status("Starting constitutional hash validation...")

        try:
            # Use grep to find all occurrences
            result = subprocess.run(
                [
                    "grep",
                    "-r",
                    "--include=*.py",
                    "--include=*.yml",
                    "--include=*.yaml",
                    "--include=*.json",
                    "--include=*.md",
                    self.constitutional_hash,
                    str(self.repo_root),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                constitutional_files = set()
                for line in lines:
                    if ":" in line:
                        file_path = line.split(":")[0]
                        constitutional_files.add(file_path)

                self.constitutional_files = constitutional_files
                self.log_status(
                    f"Constitutional hash found in {len(constitutional_files)} files"
                )
                return len(constitutional_files) > 0
            else:
                self.log_status("Constitutional hash not found in repository!", "ERROR")
                return False

        except Exception as e:
            self.log_status(f"Error validating constitutional hash: {e}", "ERROR")
            return False

    def check_analysis_tools(self) -> Dict[str, bool]:
        """Check availability of static analysis, search, and graph-mapping tools."""
        self.log_status("Checking static analysis and search tools availability...")

        tools = {
            # Search tools
            "grep": self._check_command("grep --version"),
            "find": self._check_command("find --version"),
            "git": self._check_command("git --version"),
            "jq": self._check_command("jq --version"),
            "tree": self._check_command("tree --version"),
            # Python static analysis
            "mypy": self._check_python_module("mypy"),
            "black": self._check_python_module("black"),
            "isort": self._check_python_module("isort"),
            "safety": self._check_python_module("safety"),
            # Graph mapping tools
            "networkx": self._check_python_module("networkx"),
            # Missing but useful tools
            "ripgrep": self._check_command("rg --version"),
            "pyright": self._check_command("pyright --version"),
            "fd": self._check_command("fd --version"),
        }

        self.analysis_tools = tools

        available = sum(1 for v in tools.values() if v)
        total = len(tools)
        self.log_status(f"Analysis tools: {available}/{total} available")

        return tools

    def _check_command(self, cmd: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(cmd.split(), capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _check_python_module(self, module: str) -> bool:
        """Check if a Python module is available."""
        try:
            __import__(module)
            return True
        except ImportError:
            return False

    def index_services(self) -> Dict[str, Any]:
        """Index all service directories and components."""
        self.log_status("Indexing service directories...")

        services_dir = self.repo_root / "services"
        if not services_dir.exists():
            self.log_status("Services directory not found!", "ERROR")
            return {}

        services = {}

        # Index main service categories
        for category_dir in services_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                services[category_name] = {
                    "path": str(category_dir),
                    "services": {},
                    "configs": [],
                    "dockerfiles": [],
                    "requirements": [],
                }

                # Index individual services within category
                for service_dir in category_dir.iterdir():
                    if service_dir.is_dir():
                        service_info = self._analyze_service(service_dir)
                        services[category_name]["services"][
                            service_dir.name
                        ] = service_info

        self.services_index = services
        self.log_status(f"Indexed {len(services)} service categories")
        return services

    def _analyze_service(self, service_path: Path) -> Dict[str, Any]:
        """Analyze individual service structure."""
        service_info = {
            "path": str(service_path),
            "main_files": [],
            "config_files": [],
            "docker_files": [],
            "api_files": [],
            "model_files": [],
            "test_files": [],
            "has_constitutional_hash": False,
        }

        # Scan for important files
        for file_path in service_path.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                relative_path = str(file_path.relative_to(service_path))

                # Categorize files
                if file_name in ["main.py", "app.py", "server.py", "__init__.py"]:
                    service_info["main_files"].append(relative_path)
                elif file_name.startswith("dockerfile"):
                    service_info["docker_files"].append(relative_path)
                elif file_name.startswith("requirements"):
                    service_info["config_files"].append(relative_path)
                elif "api" in relative_path.lower():
                    service_info["api_files"].append(relative_path)
                elif "model" in relative_path.lower():
                    service_info["model_files"].append(relative_path)
                elif "test" in relative_path.lower():
                    service_info["test_files"].append(relative_path)

                # Check for constitutional hash
                if str(file_path) in self.constitutional_files:
                    service_info["has_constitutional_hash"] = True

        return service_info

    def index_configuration(self) -> Dict[str, Any]:
        """Index all configuration files and infrastructure configs."""
        self.log_status("Indexing configuration files...")

        config_index = {
            "infrastructure": {},
            "services": {},
            "environments": {},
            "monitoring": {},
            "security": {},
        }

        # Key configuration directories
        config_dirs = [
            ("infrastructure", ["infrastructure", "k8s", "kubernetes", "docker"]),
            ("monitoring", ["monitoring", "prometheus", "grafana", "alerting"]),
            ("security", ["security", "auth", "authentication", "secrets"]),
            ("environments", ["config", "configs", "env", "environments"]),
        ]

        for category, dir_patterns in config_dirs:
            for pattern in dir_patterns:
                for config_dir in self.repo_root.rglob(pattern):
                    if config_dir.is_dir():
                        config_files = self._scan_config_directory(config_dir)
                        if config_files:
                            config_index[category][config_dir.name] = {
                                "path": str(config_dir),
                                "files": config_files,
                            }

        self.config_index = config_index
        self.log_status(f"Indexed configuration across {len(config_index)} categories")
        return config_index

    def _scan_config_directory(self, config_dir: Path) -> List[Dict[str, str]]:
        """Scan a configuration directory for relevant files."""
        config_files = []

        config_extensions = {".yml", ".yaml", ".json", ".toml", ".ini", ".conf", ".env"}

        for file_path in config_dir.rglob("*"):
            if file_path.is_file():
                if (
                    file_path.suffix in config_extensions
                    or "docker-compose" in file_path.name.lower()
                    or file_path.name.lower().startswith(("dockerfile", ".env"))
                ):

                    config_files.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path.relative_to(config_dir)),
                            "full_path": str(file_path),
                            "has_constitutional_hash": str(file_path)
                            in self.constitutional_files,
                        }
                    )

        return config_files

    def index_documentation(self) -> Dict[str, Any]:
        """Index all documentation files and their relationships."""
        self.log_status("Indexing documentation...")

        docs_index = {
            "main_docs": {},
            "api_docs": {},
            "deployment_docs": {},
            "architecture_docs": {},
            "research_docs": {},
            "readme_files": [],
        }

        # Documentation patterns and categories
        doc_patterns = {
            "api_docs": ["**/api/**/*.md", "**/openapi/**/*", "**/*api*.md"],
            "deployment_docs": [
                "**/deployment/**/*.md",
                "**/*deploy*.md",
                "**/*installation*.md",
            ],
            "architecture_docs": [
                "**/architecture/**/*.md",
                "**/*architecture*.md",
                "**/*design*.md",
            ],
            "research_docs": [
                "**/research/**/*.md",
                "**/papers/**/*",
                "**/*research*.md",
            ],
        }

        # Scan for README files
        for readme in self.repo_root.rglob("README*"):
            if readme.is_file():
                docs_index["readme_files"].append(
                    {
                        "name": readme.name,
                        "path": str(readme.relative_to(self.repo_root)),
                        "full_path": str(readme),
                        "has_constitutional_hash": str(readme)
                        in self.constitutional_files,
                    }
                )

        # Scan docs directory
        docs_dir = self.repo_root / "docs"
        if docs_dir.exists():
            docs_index["main_docs"] = self._scan_docs_directory(docs_dir)

        self.docs_index = docs_index
        self.log_status(
            f"Indexed documentation with {len(docs_index['readme_files'])} README files"
        )
        return docs_index

    def _scan_docs_directory(self, docs_dir: Path) -> Dict[str, Any]:
        """Scan the main docs directory structure."""
        docs_structure = {}

        for item in docs_dir.iterdir():
            if item.is_dir():
                docs_structure[item.name] = {"path": str(item), "files": []}

                for doc_file in item.rglob("*.md"):
                    docs_structure[item.name]["files"].append(
                        {
                            "name": doc_file.name,
                            "path": str(doc_file.relative_to(item)),
                            "full_path": str(doc_file),
                            "has_constitutional_hash": str(doc_file)
                            in self.constitutional_files,
                        }
                    )
            elif item.suffix == ".md":
                if "root_files" not in docs_structure:
                    docs_structure["root_files"] = {"files": []}

                docs_structure["root_files"]["files"].append(
                    {
                        "name": item.name,
                        "path": str(item.relative_to(docs_dir)),
                        "full_path": str(item),
                        "has_constitutional_hash": str(item)
                        in self.constitutional_files,
                    }
                )

        return docs_structure

    def generate_dependency_graph(self) -> Dict[str, Any]:
        """Generate a basic dependency mapping using available tools."""
        self.log_status("Generating dependency mappings...")

        dependency_info = {
            "python_dependencies": {},
            "docker_dependencies": {},
            "service_dependencies": {},
            "infrastructure_dependencies": {},
        }

        # Python dependencies from requirements files
        for req_file in self.repo_root.rglob("requirements*.txt"):
            try:
                with open(req_file, "r") as f:
                    deps = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                    dependency_info["python_dependencies"][
                        str(req_file.relative_to(self.repo_root))
                    ] = deps
            except Exception as e:
                self.log_status(f"Error reading {req_file}: {e}", "WARNING")

        # Docker dependencies from docker-compose files
        for compose_file in self.repo_root.rglob("docker-compose*.yml"):
            dependency_info["docker_dependencies"][
                str(compose_file.relative_to(self.repo_root))
            ] = {
                "path": str(compose_file),
                "has_constitutional_hash": str(compose_file)
                in self.constitutional_files,
            }

        return dependency_info

    def create_review_cache(self) -> Dict[str, Any]:
        """Create a comprehensive cache file for review environment."""
        self.log_status("Creating review environment cache...")

        cache_data = {
            "metadata": {
                "constitutional_hash": self.constitutional_hash,
                "cache_created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "repo_root": str(self.repo_root),
                "indexing_duration_seconds": time.time() - self.start_time,
            },
            "constitutional_compliance": {
                "hash": self.constitutional_hash,
                "files_with_hash": len(self.constitutional_files),
                "sample_files": list(self.constitutional_files)[
                    :10
                ],  # First 10 as sample
            },
            "analysis_tools": self.analysis_tools,
            "services_index": self.services_index,
            "config_index": self.config_index,
            "docs_index": self.docs_index,
            "dependency_info": self.generate_dependency_graph(),
            "statistics": self._generate_statistics(),
        }

        # Save cache file
        cache_file = self.repo_root / "review_environment_cache.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2, default=str)
            self.log_status(f"Review cache saved to {cache_file}")
        except Exception as e:
            self.log_status(f"Error saving cache: {e}", "ERROR")

        return cache_data

    def _generate_statistics(self) -> Dict[str, Any]:
        """Generate repository statistics."""
        stats = {
            "total_services": 0,
            "services_with_constitutional_hash": 0,
            "total_config_files": 0,
            "configs_with_constitutional_hash": 0,
            "total_docs": 0,
            "docs_with_constitutional_hash": 0,
            "analysis_tools_available": sum(
                1 for v in self.analysis_tools.values() if v
            ),
            "analysis_tools_total": len(self.analysis_tools),
        }

        # Count services
        for category in self.services_index.values():
            for service_name, service_info in category.get("services", {}).items():
                stats["total_services"] += 1
                if service_info.get("has_constitutional_hash", False):
                    stats["services_with_constitutional_hash"] += 1

        # Count configs
        for category in self.config_index.values():
            for config_group in category.values():
                for config_file in config_group.get("files", []):
                    stats["total_config_files"] += 1
                    if config_file.get("has_constitutional_hash", False):
                        stats["configs_with_constitutional_hash"] += 1

        # Count docs
        stats["total_docs"] = len(self.docs_index.get("readme_files", []))
        stats["docs_with_constitutional_hash"] = sum(
            1
            for doc in self.docs_index.get("readme_files", [])
            if doc.get("has_constitutional_hash", False)
        )

        return stats

    def run_full_indexing(self) -> bool:
        """Run complete repository indexing and setup."""
        self.log_status(
            "Starting full repository indexing and review environment setup..."
        )

        try:
            # Step 1: Validate constitutional compliance
            if not self.validate_constitutional_hash():
                self.log_status("Constitutional hash validation failed!", "ERROR")
                return False

            # Step 2: Check analysis tools
            self.check_analysis_tools()

            # Step 3: Index repository components
            self.index_services()
            self.index_configuration()
            self.index_documentation()

            # Step 4: Create review cache
            cache_data = self.create_review_cache()

            # Step 5: Generate summary report
            self._generate_summary_report(cache_data)

            self.log_status("Repository indexing completed successfully!")
            return True

        except Exception as e:
            self.log_status(f"Indexing failed with error: {e}", "ERROR")
            return False

    def _generate_summary_report(self, cache_data: Dict[str, Any]):
        """Generate and display summary report."""
        stats = cache_data["statistics"]
        metadata = cache_data["metadata"]

        print("\n" + "=" * 80)
        print("ACGS-2 REPOSITORY REVIEW ENVIRONMENT SETUP COMPLETE")
        print("=" * 80)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Repository Root: {self.repo_root}")
        print(f"Indexing Duration: {metadata['indexing_duration_seconds']:.2f} seconds")
        print()

        print("CONSTITUTIONAL COMPLIANCE STATUS:")
        print(
            f"  ✓ Constitutional hash found in {len(self.constitutional_files)} files"
        )
        print(f"  ✓ Hash validation: PASSED")
        print()

        print("ANALYSIS TOOLS AVAILABILITY:")
        for tool, available in self.analysis_tools.items():
            status = "✓" if available else "✗"
            print(f"  {status} {tool}")
        print(
            f"  Summary: {stats['analysis_tools_available']}/{stats['analysis_tools_total']} tools available"
        )
        print()

        print("REPOSITORY INDEXING SUMMARY:")
        print(
            f"  Services: {stats['total_services']} total, {stats['services_with_constitutional_hash']} with constitutional hash"
        )
        print(
            f"  Config Files: {stats['total_config_files']} total, {stats['configs_with_constitutional_hash']} with constitutional hash"
        )
        print(
            f"  Documentation: {stats['total_docs']} files, {stats['docs_with_constitutional_hash']} with constitutional hash"
        )
        print()

        print("REVIEW ENVIRONMENT STATUS:")
        print("  ✓ Full repository loaded and indexed")
        print("  ✓ Service directories mapped")
        print("  ✓ Configuration files cataloged")
        print("  ✓ Documentation indexed")
        print("  ✓ Constitutional hash cached for automated checks")
        print("  ✓ Review cache created: review_environment_cache.json")
        print()

        # Missing tools recommendations
        missing_tools = [
            tool for tool, available in self.analysis_tools.items() if not available
        ]
        if missing_tools:
            print("RECOMMENDED TOOL INSTALLATIONS:")
            for tool in missing_tools:
                if tool == "ripgrep":
                    print("  • ripgrep: Fast text search tool")
                    print("    Install: apt install ripgrep  OR  cargo install ripgrep")
                elif tool == "pyright":
                    print("  • pyright: Static type checker")
                    print("    Install: npm install -g pyright")
                elif tool == "fd":
                    print("  • fd: Fast file finder")
                    print("    Install: apt install fd-find")
            print()

        print("=" * 80)


def main():
    """Main execution function."""
    print("ACGS-2 Repository Review Environment Setup")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("Initializing indexing process...\n")

    # Initialize indexer
    indexer = ACGSRepositoryIndexer()

    # Run full indexing
    success = indexer.run_full_indexing()

    if success:
        print("\n✓ Review environment setup completed successfully!")
        print("✓ Constitutional hash cdd01ef066bc6cf2 cached for automated checks")
        print("✓ Repository fully loaded and indexed for review")
        return 0
    else:
        print("\n✗ Review environment setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
