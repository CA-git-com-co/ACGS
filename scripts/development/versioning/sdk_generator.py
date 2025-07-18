"""
ACGS-1 SDK Generator

Generates version-specific client SDKs from OpenAPI specifications with
automatic compatibility layers and validation.
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class SDKLanguage(str, Enum):
    """Supported SDK languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"


class SDKTemplate(str, Enum):
    """SDK template types."""

    STANDARD = "standard"
    ASYNC = "async"
    REACTIVE = "reactive"
    MINIMAL = "minimal"


@dataclass
class SDKConfig:
    """Configuration for SDK generation."""

    language: SDKLanguage
    template: SDKTemplate = SDKTemplate.STANDARD
    package_name: str = "acgs-sdk"
    package_version: str = "1.0.0"
    api_version: str = "v1.0.0"
    compatibility_versions: list[str] = field(default_factory=list)
    include_examples: bool = True
    include_tests: bool = True
    include_docs: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "language": self.language.value,
            "template": self.template.value,
            "package_name": self.package_name,
            "package_version": self.package_version,
            "api_version": self.api_version,
            "compatibility_versions": self.compatibility_versions,
            "include_examples": self.include_examples,
            "include_tests": self.include_tests,
            "include_docs": self.include_docs,
        }


@dataclass
class SDKGenerationResult:
    """Result of SDK generation process."""

    success: bool
    output_path: Path
    generated_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generation_time_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "output_path": str(self.output_path),
            "generated_files": self.generated_files,
            "errors": self.errors,
            "warnings": self.warnings,
            "generation_time_seconds": self.generation_time_seconds,
        }


class SDKGenerator:
    """
    Generates client SDKs from OpenAPI specifications with version compatibility.

    Features:
    - Multi-language SDK generation
    - Version compatibility layers
    - Automatic testing and validation
    - Documentation generation
    - Package publishing preparation
    """

    def __init__(self, base_output_dir: Path = Path("generated_sdks")):
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

        # Language-specific configurations
        self.language_configs = {
            SDKLanguage.PYTHON: {
                "generator": "python",
                "package_manager": "pip",
                "test_framework": "pytest",
                "doc_generator": "sphinx",
            },
            SDKLanguage.JAVASCRIPT: {
                "generator": "javascript",
                "package_manager": "npm",
                "test_framework": "jest",
                "doc_generator": "jsdoc",
            },
            SDKLanguage.TYPESCRIPT: {
                "generator": "typescript-node",
                "package_manager": "npm",
                "test_framework": "jest",
                "doc_generator": "typedoc",
            },
            SDKLanguage.JAVA: {
                "generator": "java",
                "package_manager": "maven",
                "test_framework": "junit",
                "doc_generator": "javadoc",
            },
            SDKLanguage.CSHARP: {
                "generator": "csharp",
                "package_manager": "nuget",
                "test_framework": "nunit",
                "doc_generator": "docfx",
            },
        }

    def generate_sdk(
        self, openapi_spec_path: Path, config: SDKConfig
    ) -> SDKGenerationResult:
        """
        Generate SDK from OpenAPI specification.

        Args:
            openapi_spec_path: Path to OpenAPI specification file
            config: SDK generation configuration

        Returns:
            Generation result with success status and details
        """
        start_time = datetime.now()

        result = SDKGenerationResult(
            success=False,
            output_path=self.base_output_dir
            / config.language.value
            / config.api_version,
        )

        try:
            # Create output directory
            result.output_path.mkdir(parents=True, exist_ok=True)

            # Load and validate OpenAPI spec
            openapi_spec = self._load_openapi_spec(openapi_spec_path)
            if not openapi_spec:
                result.errors.append("Failed to load OpenAPI specification")
                return result

            # Generate base SDK using OpenAPI Generator
            base_generation_result = self._generate_base_sdk(
                openapi_spec_path, config, result.output_path
            )

            if not base_generation_result:
                result.errors.append("Base SDK generation failed")
                return result

            # Add ACGS-specific enhancements
            self._add_acgs_enhancements(config, result.output_path, result)

            # Add compatibility layer if needed
            if config.compatibility_versions:
                self._add_compatibility_layer(config, result.output_path, result)

            # Generate tests if requested
            if config.include_tests:
                self._generate_tests(config, result.output_path, result)

            # Generate documentation if requested
            if config.include_docs:
                self._generate_documentation(config, result.output_path, result)

            # Generate examples if requested
            if config.include_examples:
                self._generate_examples(config, result.output_path, result)

            # Validate generated SDK
            validation_result = self._validate_sdk(config, result.output_path)
            if not validation_result:
                result.warnings.append("SDK validation failed")

            result.success = True
            logger.info(
                f"SDK generation completed successfully for {config.language.value}"
            )

        except Exception as e:
            result.errors.append(f"SDK generation failed: {e!s}")
            logger.error(f"SDK generation failed: {e}")

        finally:
            end_time = datetime.now()
            result.generation_time_seconds = (end_time - start_time).total_seconds()

        return result

    def _load_openapi_spec(self, spec_path: Path) -> dict[str, Any] | None:
        """Load and validate OpenAPI specification."""
        try:
            with open(spec_path) as f:
                if spec_path.suffix.lower() in [".yaml", ".yml"]:
                    import yaml

                    return yaml.safe_load(f)
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            return None

    def _generate_base_sdk(
        self, spec_path: Path, config: SDKConfig, output_path: Path
    ) -> bool:
        """Generate base SDK using OpenAPI Generator."""
        try:
            lang_config = self.language_configs.get(config.language)
            if not lang_config:
                logger.error(f"Unsupported language: {config.language}")
                return False

            # Prepare OpenAPI Generator command
            cmd = [
                "openapi-generator-cli",
                "generate",
                "-i",
                str(spec_path),
                "-g",
                lang_config["generator"],
                "-o",
                str(output_path),
                "--package-name",
                config.package_name,
                "--additional-properties",
                f"packageVersion={config.package_version}",
                "--skip-validate-spec",
            ]

            # Add language-specific properties
            if config.language == SDKLanguage.PYTHON:
                cmd.extend(
                    [
                        "--additional-properties",
                        f"projectName={config.package_name},packageName={config.package_name.replace('-', '_')}",
                    ]
                )
            elif config.language == SDKLanguage.JAVASCRIPT:
                cmd.extend(
                    [
                        "--additional-properties",
                        f"npmName={config.package_name},npmVersion={config.package_version}",
                    ]
                )

            # Execute OpenAPI Generator
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"OpenAPI Generator failed: {result.stderr}")
                return False

            logger.info(f"Base SDK generated successfully for {config.language.value}")
            return True

        except Exception as e:
            logger.error(f"Base SDK generation failed: {e}")
            return False

    def _add_acgs_enhancements(
        self, config: SDKConfig, output_path: Path, result: SDKGenerationResult
    ):
        """Add ACGS-specific enhancements to generated SDK."""
        enhancements_dir = output_path / "acgs_enhancements"
        enhancements_dir.mkdir(exist_ok=True)

        # Add retry logic
        self._add_retry_logic(config, enhancements_dir, result)

        # Add rate limiting
        self._add_rate_limiting(config, enhancements_dir, result)

        # Add error handling
        self._add_error_handling(config, enhancements_dir, result)

        # Add logging integration
        self._add_logging_integration(config, enhancements_dir, result)

        # Add metrics collection
        self._add_metrics_collection(config, enhancements_dir, result)

    def _add_retry_logic(
        self, config: SDKConfig, enhancements_dir: Path, result: SDKGenerationResult
    ):
        """Add retry logic with exponential backoff."""
        if config.language == SDKLanguage.PYTHON:
            retry_code = '''
"""ACGS SDK Retry Logic with Exponential Backoff."""

import time
import random
from typing import Callable, Any
from functools import wraps

class RetryConfig:
    def __init__(self, max_attempts=3, backoff_factor=2.0, max_delay=60.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

def with_retry(retry_config: RetryConfig = None):
    """Decorator to add retry logic to API calls."""
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        break
                    
                    # Calculate delay with jitter
                    delay = min(
                        retry_config.backoff_factor ** attempt,
                        retry_config.max_delay
                    )
                    jitter = random.uniform(0.1, 0.3) * delay
                    time.sleep(delay + jitter)
            
            raise last_exception
        
        return wrapper
    return decorator
'''

            retry_file = enhancements_dir / "retry_logic.py"
            with open(retry_file, "w") as f:
                f.write(retry_code)

            result.generated_files.append(str(retry_file))

    def _add_rate_limiting(
        self, config: SDKConfig, enhancements_dir: Path, result: SDKGenerationResult
    ):
        """Add rate limiting functionality."""
        # Implementation would add rate limiting code for each language
        pass

    def _add_error_handling(
        self, config: SDKConfig, enhancements_dir: Path, result: SDKGenerationResult
    ):
        """Add enhanced error handling."""
        # Implementation would add error handling code for each language
        pass

    def _add_logging_integration(
        self, config: SDKConfig, enhancements_dir: Path, result: SDKGenerationResult
    ):
        """Add logging integration."""
        # Implementation would add logging code for each language
        pass

    def _add_metrics_collection(
        self, config: SDKConfig, enhancements_dir: Path, result: SDKGenerationResult
    ):
        """Add metrics collection."""
        # Implementation would add metrics code for each language
        pass

    def _add_compatibility_layer(
        self, config: SDKConfig, output_path: Path, result: SDKGenerationResult
    ):
        """Add compatibility layer for older API versions."""
        compatibility_dir = output_path / "compatibility"
        compatibility_dir.mkdir(exist_ok=True)

        for version in config.compatibility_versions:
            version_dir = compatibility_dir / version.replace(".", "_")
            version_dir.mkdir(exist_ok=True)

            # Generate compatibility transformers
            self._generate_compatibility_transformers(
                config, version, version_dir, result
            )

    def _generate_compatibility_transformers(
        self,
        config: SDKConfig,
        target_version: str,
        version_dir: Path,
        result: SDKGenerationResult,
    ):
        """Generate compatibility transformers for specific version."""
        if config.language == SDKLanguage.PYTHON:
            transformer_code = f'''
"""Compatibility transformer for API {target_version}."""

class V{target_version.replace(".", "_")}Transformer:
    """Transform responses between {config.api_version} and {target_version}."""
    
    @staticmethod
    def transform_response(response_data):
        """Transform response from {config.api_version} to {target_version} format."""
        if not isinstance(response_data, dict):
            return response_data
        
        # Example transformations (customize based on actual API changes)
        transformed = response_data.copy()
        
        # Convert camelCase to snake_case for v1.x compatibility
        if target_version.startswith("v1"):
            transformed = {{
                snake_case_key(k): v for k, v in transformed.items()
            }}
        
        return transformed

def snake_case_key(key):
    """Convert camelCase to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', key)
    return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()
'''

            transformer_file = version_dir / "transformer.py"
            with open(transformer_file, "w") as f:
                f.write(transformer_code)

            result.generated_files.append(str(transformer_file))

    def _generate_tests(
        self, config: SDKConfig, output_path: Path, result: SDKGenerationResult
    ):
        """Generate test suite for SDK."""
        tests_dir = output_path / "tests"
        tests_dir.mkdir(exist_ok=True)

        # Generate unit tests
        self._generate_unit_tests(config, tests_dir, result)

        # Generate integration tests
        self._generate_integration_tests(config, tests_dir, result)

        # Generate compatibility tests
        if config.compatibility_versions:
            self._generate_compatibility_tests(config, tests_dir, result)

    def _generate_unit_tests(
        self, config: SDKConfig, tests_dir: Path, result: SDKGenerationResult
    ):
        """Generate unit tests."""
        # Implementation would generate unit tests for each language
        pass

    def _generate_integration_tests(
        self, config: SDKConfig, tests_dir: Path, result: SDKGenerationResult
    ):
        """Generate integration tests."""
        # Implementation would generate integration tests for each language
        pass

    def _generate_compatibility_tests(
        self, config: SDKConfig, tests_dir: Path, result: SDKGenerationResult
    ):
        """Generate compatibility tests."""
        # Implementation would generate compatibility tests for each language
        pass

    def _generate_documentation(
        self, config: SDKConfig, output_path: Path, result: SDKGenerationResult
    ):
        """Generate SDK documentation."""
        docs_dir = output_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Generate README
        self._generate_readme(config, docs_dir, result)

        # Generate API documentation
        self._generate_api_docs(config, docs_dir, result)

        # Generate migration guides
        if config.compatibility_versions:
            self._generate_migration_guides(config, docs_dir, result)

    def _generate_readme(
        self, config: SDKConfig, docs_dir: Path, result: SDKGenerationResult
    ):
        """Generate README file."""
        readme_content = f"""# ACGS SDK for {config.language.value.title()}

Official {config.language.value.title()} SDK for ACGS-1 APIs.

## Installation

```bash
# Installation command for {config.language.value}
```

## Quick Start

```{config.language.value}
# Quick start example for {config.language.value}
```

## API Version Support

- Current API Version: {config.api_version}
- Compatible Versions: {", ".join(config.compatibility_versions)}

## Documentation

- [API Reference](./api_reference.md)
- [Examples](./examples/)
- [Migration Guides](./migration/)

## Support

For support, please visit [ACGS Documentation](https://docs.acgs.ai).
"""

        readme_file = docs_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

        result.generated_files.append(str(readme_file))

    def _generate_api_docs(
        self, config: SDKConfig, docs_dir: Path, result: SDKGenerationResult
    ):
        """Generate API documentation."""
        # Implementation would generate API docs for each language
        pass

    def _generate_migration_guides(
        self, config: SDKConfig, docs_dir: Path, result: SDKGenerationResult
    ):
        """Generate migration guides."""
        # Implementation would generate migration guides
        pass

    def _generate_examples(
        self, config: SDKConfig, output_path: Path, result: SDKGenerationResult
    ):
        """Generate usage examples."""
        examples_dir = output_path / "examples"
        examples_dir.mkdir(exist_ok=True)

        # Generate basic examples
        self._generate_basic_examples(config, examples_dir, result)

        # Generate advanced examples
        self._generate_advanced_examples(config, examples_dir, result)

    def _generate_basic_examples(
        self, config: SDKConfig, examples_dir: Path, result: SDKGenerationResult
    ):
        """Generate basic usage examples."""
        # Implementation would generate basic examples for each language
        pass

    def _generate_advanced_examples(
        self, config: SDKConfig, examples_dir: Path, result: SDKGenerationResult
    ):
        """Generate advanced usage examples."""
        # Implementation would generate advanced examples for each language
        pass

    def _validate_sdk(self, config: SDKConfig, output_path: Path) -> bool:
        """Validate generated SDK."""
        try:
            # Check if required files exist
            required_files = self._get_required_files(config)
            for file_path in required_files:
                if not (output_path / file_path).exists():
                    logger.warning(f"Required file missing: {file_path}")
                    return False

            # Run language-specific validation
            return self._run_language_validation(config, output_path)

        except Exception as e:
            logger.error(f"SDK validation failed: {e}")
            return False

    def _get_required_files(self, config: SDKConfig) -> list[str]:
        """Get list of required files for the SDK."""
        if config.language == SDKLanguage.PYTHON:
            return ["setup.py", "config/environments/requirements.txt", "README.md"]
        if config.language == SDKLanguage.JAVASCRIPT:
            return ["package.json", "README.md"]
        if config.language == SDKLanguage.JAVA:
            return ["pom.xml", "README.md"]
        return ["README.md"]

    def _run_language_validation(self, config: SDKConfig, output_path: Path) -> bool:
        """Run language-specific validation."""
        # Implementation would run language-specific validation
        return True

    def generate_all_sdks(
        self,
        openapi_spec_path: Path,
        api_version: str,
        languages: list[SDKLanguage] = None,
    ) -> dict[SDKLanguage, SDKGenerationResult]:
        """Generate SDKs for all specified languages."""
        if languages is None:
            languages = list(SDKLanguage)

        results = {}

        for language in languages:
            config = SDKConfig(
                language=language,
                api_version=api_version,
                package_version=api_version.lstrip("v"),
                compatibility_versions=(
                    ["v1.5.0"] if api_version.startswith("v2") else []
                ),
            )

            result = self.generate_sdk(openapi_spec_path, config)
            results[language] = result

            if result.success:
                logger.info(f"Successfully generated {language.value} SDK")
            else:
                logger.error(
                    f"Failed to generate {language.value} SDK: {result.errors}"
                )

        return results
