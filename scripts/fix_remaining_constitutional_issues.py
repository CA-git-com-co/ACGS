#!/usr/bin/env python3
"""
Comprehensive Constitutional Compliance Fixer
Systematically addresses all remaining constitutional hash issues.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
from pathlib import Path

import yaml

# Constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConstitutionalComplianceFixer:
    def __init__(self, root_dir: str = "/home/dislove/ACGS-2"):
        self.root_dir = Path(root_dir)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.stats = {"processed": 0, "updated": 0, "skipped": 0, "errors": 0}

        # File patterns to exclude from processing
        self.exclude_patterns = {
            ".git",
            ".mypy_cache",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".idea",
            ".vscode",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
        }

        # Virtual environment paths to skip (they're dependencies)
        self.venv_paths = {
            ".venv/lib/python3.12/site-packages",
            "venv/lib/python3.12/site-packages",
        }

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped based on exclusion patterns."""
        str_path = str(file_path)

        # Skip virtual environment dependencies
        for venv_path in self.venv_paths:
            if venv_path in str_path:
                return True

        # Skip certain patterns
        for pattern in self.exclude_patterns:
            if pattern in str_path:
                return True

        return False

    def has_constitutional_hash(self, content: str, file_type: str) -> bool:
        """Check if content already has constitutional hash."""
        if file_type == "json":
            try:
                data = json.loads(content)
                return self._check_json_hash(data)
            except json.JSONDecodeError:
                return False
        elif file_type in ["yaml", "yml"]:
            try:
                data = yaml.safe_load(content)
                return self._check_yaml_hash(data)
            except yaml.YAMLError:
                return False
        elif file_type == "py":
            return self.constitutional_hash in content
        elif file_type in ["dockerfile", "docker"]:
            return f"# Constitutional Hash: {self.constitutional_hash}" in content
        else:
            return self.constitutional_hash in content

    def _check_json_hash(self, data: any) -> bool:
        """Recursively check JSON data for constitutional hash."""
        if isinstance(data, dict):
            if (
                "constitutional_hash" in data
                and data["constitutional_hash"] == self.constitutional_hash
            ):
                return True
            return any(self._check_json_hash(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._check_json_hash(item) for item in data)
        return False

    def _check_yaml_hash(self, data: any) -> bool:
        """Recursively check YAML data for constitutional hash."""
        if isinstance(data, dict):
            if (
                "constitutional_hash" in data
                and data["constitutional_hash"] == self.constitutional_hash
            ):
                return True
            return any(self._check_yaml_hash(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._check_yaml_hash(item) for item in data)
        return False

    def add_constitutional_hash_json(self, content: str) -> str:
        """Add constitutional hash to JSON content."""
        try:
            data = json.loads(content)

            if isinstance(data, dict):
                data["constitutional_hash"] = self.constitutional_hash
            elif isinstance(data, list):
                # For JSON arrays, wrap in object with hash
                data = {"constitutional_hash": self.constitutional_hash, "data": data}
            else:
                # For primitive values, wrap in object
                data = {"constitutional_hash": self.constitutional_hash, "value": data}

            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If JSON is malformed, add hash as comment at the top
            return f"// Constitutional Hash: {self.constitutional_hash}\n{content}"

    def add_constitutional_hash_yaml(self, content: str) -> str:
        """Add constitutional hash to YAML content."""
        try:
            data = yaml.safe_load(content)

            if isinstance(data, dict):
                data["constitutional_hash"] = self.constitutional_hash
            elif isinstance(data, list):
                # For YAML arrays, create new structure
                data = {"constitutional_hash": self.constitutional_hash, "items": data}
            else:
                # For primitive values, wrap in object
                data = {"constitutional_hash": self.constitutional_hash, "value": data}

            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError:
            # If YAML is malformed, add hash as comment at the top
            return f"# Constitutional Hash: {self.constitutional_hash}\n{content}"

    def add_constitutional_hash_python(self, content: str) -> str:
        """Add constitutional hash to Python file."""
        lines = content.split("\n")

        # Find the best place to insert the hash
        insert_index = 0

        # Skip shebang and encoding declarations
        for i, line in enumerate(lines[:5]):
            if line.startswith("#!") or "coding:" in line or "encoding:" in line:
                insert_index = i + 1
            else:
                break

        # Insert constitutional hash comment
        hash_comment = f"# Constitutional Hash: {self.constitutional_hash}"
        lines.insert(insert_index, hash_comment)

        return "\n".join(lines)

    def add_constitutional_hash_dockerfile(self, content: str) -> str:
        """Add constitutional hash to Dockerfile."""
        lines = content.split("\n")

        # Add hash at the beginning after any existing comments
        insert_index = 0
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith("#"):
                insert_index = i + 1
            else:
                break

        hash_comment = f"# Constitutional Hash: {self.constitutional_hash}"
        lines.insert(insert_index, hash_comment)

        return "\n".join(lines)

    def add_constitutional_hash_generic(self, content: str, file_extension: str) -> str:
        """Add constitutional hash to generic file types."""
        comment_styles = {
            ".sh": "#",
            ".bash": "#",
            ".zsh": "#",
            ".fish": "#",
            ".ini": "#",
            ".conf": "#",
            ".cfg": "#",
            ".properties": "#",
            ".env": "#",
            ".toml": "#",
            ".gitignore": "#",
            ".gitattributes": "#",
            ".editorconfig": "#",
        }

        comment_char = comment_styles.get(file_extension, "#")
        hash_comment = f"{comment_char} Constitutional Hash: {self.constitutional_hash}"

        return f"{hash_comment}\n{content}"

    def process_file(self, file_path: Path) -> bool:
        """Process a single file to add constitutional hash if needed."""
        if self.should_skip_file(file_path):
            self.stats["skipped"] += 1
            return False

        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Determine file type
            file_extension = file_path.suffix.lower()
            file_name = file_path.name.lower()

            # Determine file type
            if file_extension == ".json":
                file_type = "json"
            elif file_extension in [".yml", ".yaml"]:
                file_type = "yaml"
            elif file_extension == ".py":
                file_type = "py"
            elif "dockerfile" in file_name or file_name == "dockerfile":
                file_type = "dockerfile"
            else:
                file_type = "generic"

            # Check if hash already exists
            if self.has_constitutional_hash(content, file_type):
                self.stats["skipped"] += 1
                return False

            # Add constitutional hash based on file type
            if file_type == "json":
                new_content = self.add_constitutional_hash_json(content)
            elif file_type == "yaml":
                new_content = self.add_constitutional_hash_yaml(content)
            elif file_type == "py":
                new_content = self.add_constitutional_hash_python(content)
            elif file_type == "dockerfile":
                new_content = self.add_constitutional_hash_dockerfile(content)
            else:
                new_content = self.add_constitutional_hash_generic(
                    content, file_extension
                )

            # Write updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"✅ Updated: {file_path}")
            self.stats["updated"] += 1
            return True

        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            self.stats["errors"] += 1
            return False
        finally:
            self.stats["processed"] += 1

    def fix_specific_missing_files(self):
        """Fix specific files identified in the validation report."""
        specific_files = [
            # Python __init__.py files
            "services/core/constitutional-ai/ac_service/app/validation/__init__.py",
            "services/core/constitutional-ai/ac_service/app/config/__init__.py",
            "services/core/constitutional-ai/ac_service/app/framework/__init__.py",
            "services/core/constitutional-ai/ac_service/app/compliance/__init__.py",
            # Blockchain configuration
            "services/blockchain/initial_policies.json",
            # Infrastructure configs
            "infrastructure/docker/acgs_pgp_rules.yml",
            "infrastructure/docker/monitoring/config/alertmanager.yml",
            "infrastructure/docker/monitoring/config/prometheus.yml",
            "infrastructure/docker/infrastructure/docker/opa-config.yaml",
        ]

        logger.info("🔧 Fixing specific missing files...")
        for file_path in specific_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                self.process_file(full_path)
            else:
                logger.warning(f"⚠️ File not found: {full_path}")

    def fix_docker_files(self):
        """Fix all Docker-related files."""
        logger.info("🐳 Processing Docker files...")

        docker_patterns = [
            "**/Dockerfile*",
            "**/docker-compose*.yml",
            "**/docker-compose*.yaml",
            "**/*.dockerfile",
            "**/docker/**/*.yml",
            "**/docker/**/*.yaml",
        ]

        for pattern in docker_patterns:
            for file_path in self.root_dir.rglob(pattern):
                if file_path.is_file() and not self.should_skip_file(file_path):
                    self.process_file(file_path)

    def fix_configuration_files(self):
        """Fix remaining configuration files."""
        logger.info("⚙️ Processing configuration files...")

        config_patterns = [
            "**/*.json",
            "**/*.yml",
            "**/*.yaml",
            "**/*.toml",
            "**/*.ini",
            "**/*.cfg",
            "**/*.conf",
        ]

        for pattern in config_patterns:
            for file_path in self.root_dir.rglob(pattern):
                if file_path.is_file() and not self.should_skip_file(file_path):
                    self.process_file(file_path)

    def fix_python_files(self):
        """Fix remaining Python files missing constitutional hash."""
        logger.info("🐍 Processing Python files...")

        for file_path in self.root_dir.rglob("**/*.py"):
            if file_path.is_file() and not self.should_skip_file(file_path):
                self.process_file(file_path)

    def run_comprehensive_fix(self):
        """Run comprehensive constitutional compliance fix."""
        print("🔧 ACGS Constitutional Compliance Comprehensive Fixer")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        print("=" * 60)

        # Fix specific files first
        self.fix_specific_missing_files()

        # Fix Docker files
        self.fix_docker_files()

        # Fix configuration files
        self.fix_configuration_files()

        # Fix Python files
        self.fix_python_files()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 Constitutional Compliance Fix Summary")
        print("=" * 60)
        print(f"📁 Files processed: {self.stats['processed']}")
        print(f"✅ Files updated: {self.stats['updated']}")
        print(f"⏭️ Files skipped: {self.stats['skipped']}")
        print(f"❌ Errors: {self.stats['errors']}")

        if self.stats["updated"] > 0:
            print(
                "\n🎉 Successfully added constitutional hash to"
                f" {self.stats['updated']} files!"
            )
        else:
            print("\n✅ All files already have constitutional hash compliance!")


def main():
    """Main execution function."""
    fixer = ConstitutionalComplianceFixer()
    fixer.run_comprehensive_fix()


if __name__ == "__main__":
    main()
