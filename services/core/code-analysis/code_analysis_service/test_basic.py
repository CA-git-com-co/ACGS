#!/usr/bin/env python3
"""
Basic test script for ACGS Code Analysis Engine implementation.
Tests core functionality without full service startup.
"""

import os
import sys
import asyncio

# Set environment variables for testing
os.environ["POSTGRESQL_PASSWORD"] = "test_password"

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.utils.constitutional import CONSTITUTIONAL_HASH
        print(f"✅ Constitutional utilities imported. Hash: {CONSTITUTIONAL_HASH}")
    except Exception as e:
        print(f"❌ Constitutional utilities import failed: {e}")
        return False
    
    try:
        from app.utils.logging import get_logger
        logger = get_logger("test")
        print("✅ Logging utilities imported")
    except Exception as e:
        print(f"❌ Logging utilities import failed: {e}")
        return False
    
    try:
        from app.middleware.auth import AuthenticationMiddleware
        print("✅ Authentication middleware imported")
    except Exception as e:
        print(f"❌ Authentication middleware import failed: {e}")
        return False
    
    try:
        from app.middleware.performance import PerformanceMiddleware
        print("✅ Performance middleware imported")
    except Exception as e:
        print(f"❌ Performance middleware import failed: {e}")
        return False
    
    try:
        from app.middleware.constitutional import ConstitutionalComplianceMiddleware
        print("✅ Constitutional compliance middleware imported")
    except Exception as e:
        print(f"❌ Constitutional compliance middleware import failed: {e}")
        return False
    
    try:
        from app.api.v1 import api_router
        print("✅ API router imported")
    except Exception as e:
        print(f"❌ API router import failed: {e}")
        return False
    
    try:
        from app.core.file_watcher import FileWatcherService
        print("✅ File watcher service imported")
    except Exception as e:
        print(f"❌ File watcher service import failed: {e}")
        return False
    
    try:
        from app.core.indexer import IndexerService
        print("✅ Indexer service imported")
    except Exception as e:
        print(f"❌ Indexer service import failed: {e}")
        return False
    
    try:
        from app.services.registry_service import ServiceRegistryClient
        print("✅ Service registry client imported")
    except Exception as e:
        print(f"❌ Service registry client import failed: {e}")
        return False
    
    try:
        from app.services.cache_service import CacheService
        print("✅ Cache service imported")
    except Exception as e:
        print(f"❌ Cache service import failed: {e}")
        return False
    
    try:
        from config.database import DatabaseManager
        print("✅ Database manager imported")
    except Exception as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    return True


def test_fastapi_app():
    """Test FastAPI app creation."""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from app.api.v1 import api_router
        
        # Create minimal FastAPI app
        app = FastAPI(
            title="ACGS Code Analysis Engine",
            description="Test app creation",
            version="1.0.0"
        )
        
        # Include router
        app.include_router(api_router, prefix="/api/v1")
        
        print("✅ FastAPI app created successfully")
        print(f"✅ API routes: {len(app.routes)} routes registered")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False


async def test_constitutional_compliance():
    """Test constitutional compliance functionality."""
    print("\nTesting constitutional compliance...")
    
    try:
        from app.utils.constitutional import (
            ConstitutionalValidator,
            validate_constitutional_hash,
            ensure_constitutional_compliance
        )
        
        # Test hash validation
        validator = ConstitutionalValidator()
        
        # Test valid hash
        if validate_constitutional_hash("cdd01ef066bc6cf2"):
            print("✅ Constitutional hash validation works")
        else:
            print("❌ Constitutional hash validation failed")
            return False
        
        # Test compliance enhancement
        test_data = {"test": "data"}
        enhanced_data = ensure_constitutional_compliance(test_data)
        
        if "constitutional_hash" in enhanced_data:
            print("✅ Constitutional compliance enhancement works")
        else:
            print("❌ Constitutional compliance enhancement failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Constitutional compliance test failed: {e}")
        return False


async def test_services():
    """Test service initialization."""
    print("\nTesting service initialization...")
    
    try:
        from app.core.indexer import IndexerService
        from app.services.cache_service import CacheService
        
        # Test indexer service
        indexer = IndexerService()
        status = indexer.get_status()
        
        if "constitutional_hash" in status:
            print("✅ Indexer service initialization works")
        else:
            print("❌ Indexer service missing constitutional compliance")
            return False
        
        # Test cache service (without connecting to Redis)
        cache = CacheService()

        # Test that cache service has the right key prefix
        if "acgs:code_analysis:" in cache.key_prefix:
            print("✅ Cache service initialization works")
        else:
            print("❌ Cache service missing expected key prefix")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 ACGS Code Analysis Engine - Basic Implementation Test")
    print("=" * 60)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test FastAPI app
    if not test_fastapi_app():
        success = False
    
    # Test constitutional compliance
    if not asyncio.run(test_constitutional_compliance()):
        success = False
    
    # Test services
    if not asyncio.run(test_services()):
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Implementation is working correctly.")
        print("✅ Ready to proceed with deployment testing.")
    else:
        print("❌ SOME TESTS FAILED! Implementation needs fixes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
