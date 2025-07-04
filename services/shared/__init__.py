
# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS/shared/__init__.py
# This file makes 'shared' a Python package.

# Import legacy components for backward compatibility
try:
    from . import models, schemas, utils
    from .utils import ACGSConfig, get_config, reset_config
except ImportError:
    # Handle missing legacy modules gracefully
    pass

# Import new Phase 2 components
# Temporarily commented out service_mesh due to tenacity import issues
# from . import common, di, events

# from . import service_mesh

# You can optionally define __all__ to control what `from shared import *` imports
__all__ = [
    "ACGSConfig",
    # "common",
    # "di",
    # "events",
    "get_config",
    # "models",
    "reset_config",
    # "schemas",
    # "service_mesh",
    # "utils",
]
