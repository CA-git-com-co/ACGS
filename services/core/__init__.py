"""
Core Services Package for ACGS
Constitutional Hash: cdd01ef066bc6cf2
"""

# Import submodules to enable Python imports despite directory names with dashes
import sys
import os
from pathlib import Path

# Get the directory of this file
core_dir = Path(__file__).parent

# Add subdirectories with dashes as importable modules
for subdir in core_dir.iterdir():
    if subdir.is_dir() and "-" in subdir.name:
        # Create module name by replacing dashes with underscores
        module_name = subdir.name.replace("-", "_")
        # Add to sys.modules to make it importable
        sys.modules[f"services.core.{module_name}"] = __import__(
            "services.core", fromlist=[subdir.name]
        )
