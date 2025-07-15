"""
Dash Import Helper for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Helper module to enable imports from directories with dashes in their names.
"""

import importlib.util
import sys
from pathlib import Path


def import_from_dash_path(module_path: str, attribute: str = None):
    """
    Import a module or attribute from a path containing dashes.
    
    Args:
        module_path: The module path with dashes (e.g., 'services.core.policy-governance.pgc_service.main')
        attribute: Optional specific attribute to import (e.g., 'app')
    
    Returns:
        The imported module or attribute
    """
    # Convert the path to a file system path
    path_parts = module_path.split('.')
    
    # Find the base directory (services)
    base_path = Path(__file__).parent.parent
    
    # Build the file path
    current_path = base_path
    for part in path_parts[1:]:  # Skip 'services'
        current_path = current_path / part
    
    # If it's a package, look for __init__.py, otherwise add .py
    if (current_path / '__init__.py').exists():
        spec_file = current_path / '__init__.py'
        module_name = module_path
    else:
        spec_file = current_path.with_suffix('.py')
        module_name = module_path
    
    if not spec_file.exists():
        raise ImportError(f"Cannot find module at {spec_file}")
    
    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, spec_file)
    module = importlib.util.module_from_spec(spec)
    
    # Add to sys.modules to prevent re-loading
    sys.modules[module_name] = module
    
    # Execute the module
    spec.loader.exec_module(module)
    
    # Return the module or specific attribute
    if attribute:
        return getattr(module, attribute)
    return module


def import_policy_governance_main():
    """Import the policy governance main app."""
    try:
        return import_from_dash_path('services.core.policy-governance.pgc_service.main', 'app')
    except Exception:
        return None


def import_constitutional_ai_main():
    """Import the constitutional AI main app."""
    try:
        return import_from_dash_path('services.core.constitutional-ai.ac_service.main', 'app')
    except Exception:
        return None


def import_governance_synthesis_main():
    """Import the governance synthesis main app."""
    try:
        return import_from_dash_path('services.core.governance-synthesis.gs_service.main', 'app')
    except Exception:
        return None


def import_formal_verification_main():
    """Import the formal verification main app."""
    try:
        return import_from_dash_path('services.core.formal-verification.fv_service.main', 'app')
    except Exception:
        return None