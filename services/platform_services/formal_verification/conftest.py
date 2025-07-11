"""
Pytest configuration for ACGS Formal Verification Service
Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)