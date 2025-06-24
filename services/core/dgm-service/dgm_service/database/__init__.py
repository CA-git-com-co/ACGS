"""
Database package for DGM service.
"""

from .migrations import DGMMigrationManager

__all__ = ["DGMMigrationManager"]
