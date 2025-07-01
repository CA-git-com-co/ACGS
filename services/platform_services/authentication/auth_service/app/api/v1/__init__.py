# backend/auth_service/app/api/v1/__init__.py
from . import api_router, deps, endpoints

__all__ = ["endpoints", "deps", "api_router"]
