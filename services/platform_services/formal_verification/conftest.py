"""
Pytest configuration for ACGS Formal Verification Service
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import pathlib
import sys

# Add the current directory to Python path for imports
current_dir = pathlib.Path(pathlib.Path(__file__).resolve()).parent
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
