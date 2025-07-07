# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS/shared/__init__.py
# This file makes 'shared' a Python package.

# Import legacy components for backward compatibility
try:
    from . import utils
except ImportError:
    # Handle missing legacy modules gracefully
    pass

# Import new Phase 2 components
# Temporarily commented out service_mesh due to tenacity import issues
# from . import common, di, events

# from . import service_mesh

# You can optionally define __all__ to control what `from shared import *` imports
__all__ = [
    "CONSTITUTIONAL_HASH",
    # "common",
    # "di",
    # "events",
    # "models",
    # "schemas",
    # "service_mesh",
    # "utils",
]
