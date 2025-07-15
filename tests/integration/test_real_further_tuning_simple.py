#!/usr/bin/env python3
"""
Simple Integration Tests for Real Further Tuning Implementation

Constitutional Hash: cdd01ef066bc6cf2
ACGS-2 Constitutional Compliance Validation

This module provides simple integration tests to validate the real further tuning
implementations are working correctly.
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def test_constitutional_hash_validation():
    """Test that constitutional hash is properly defined."""
    assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
    assert len(CONSTITUTIONAL_HASH) == 16


def test_performance_optimizer_file_exists():
    """Test that performance optimizer file exists."""
    performance_file = Path(__file__).parent.parent.parent / "services" / "shared" / "performance" / "real_performance_optimizer.py"
    assert performance_file.exists(), f"Performance optimizer file not found: {performance_file}"
    
    # Check file contains constitutional hash
    content = performance_file.read_text()
    assert CONSTITUTIONAL_HASH in content, "Constitutional hash not found in performance optimizer"


def test_security_hardening_file_exists():
    """Test that security hardening file exists."""
    security_file = Path(__file__).parent.parent.parent / "services" / "shared" / "security" / "real_security_hardening.py"
    assert security_file.exists(), f"Security hardening file not found: {security_file}"
    
    # Check file contains constitutional hash
    content = security_file.read_text()
    assert CONSTITUTIONAL_HASH in content, "Constitutional hash not found in security hardening"


def test_performance_optimizer_imports():
    """Test that performance optimizer can be imported."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
    
    try:
        import real_performance_optimizer
        assert hasattr(real_performance_optimizer, 'CONSTITUTIONAL_HASH')
        assert real_performance_optimizer.CONSTITUTIONAL_HASH == CONSTITUTIONAL_HASH
        assert hasattr(real_performance_optimizer, 'RealPerformanceConfig')
        assert hasattr(real_performance_optimizer, 'RealPerformanceOrchestrator')
    except ImportError as e:
        assert False, f"Failed to import performance optimizer: {e}"


def test_security_hardening_imports():
    """Test that security hardening can be imported."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    try:
        import real_security_hardening
        assert hasattr(real_security_hardening, 'CONSTITUTIONAL_HASH')
        assert real_security_hardening.CONSTITUTIONAL_HASH == CONSTITUTIONAL_HASH
        assert hasattr(real_security_hardening, 'RealSecurityConfig')
        assert hasattr(real_security_hardening, 'RealSecurityOrchestrator')
    except ImportError as e:
        assert False, f"Failed to import security hardening: {e}"


def test_performance_config_creation():
    """Test performance configuration creation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
    
    from real_performance_optimizer import RealPerformanceConfig
    
    config = RealPerformanceConfig(
        database_url=os.environ.get("DATABASE_URL"),
        redis_url="redis://localhost:6379/1",
        target_query_time_ms=100.0
    )
    
    assert config.constitutional_hash == CONSTITUTIONAL_HASH
    assert config.database_url == "postgresql://test:test@localhost:5432/test_db"
    assert config.redis_url == "redis://localhost:6379/1"
    assert config.target_query_time_ms == 100.0


def test_security_config_creation():
    """Test security configuration creation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_security_hardening import RealSecurityConfig
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        config = RealSecurityConfig(
            security_db_path=temp_db,
            password_min_length=12,
            max_login_attempts=5
        )
        
        assert config.constitutional_hash == CONSTITUTIONAL_HASH
        assert config.security_db_path == temp_db
        assert config.password_min_length == 12
        assert config.max_login_attempts == 5
        assert "password" in config.secret_patterns
        assert "api_key" in config.secret_patterns
        
    finally:
        os.unlink(temp_db)


def test_memory_optimizer_functionality():
    """Test memory optimizer basic functionality."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
    
    from real_performance_optimizer import RealPerformanceConfig, RealMemoryOptimizer
    
    config = RealPerformanceConfig()
    optimizer = RealMemoryOptimizer(config)
    
    # Test memory usage collection
    memory_usage = optimizer.get_real_memory_usage()
    
    assert "constitutional_hash" in memory_usage
    assert memory_usage["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert "process_rss_mb" in memory_usage
    assert "system_used_percent" in memory_usage
    assert memory_usage["process_rss_mb"] > 0
    assert 0 <= memory_usage["system_used_percent"] <= 100


def test_vulnerability_scanner_functionality():
    """Test vulnerability scanner basic functionality."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_security_hardening import RealSecurityConfig, RealVulnerabilityScanner
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        config = RealSecurityConfig(security_db_path=temp_db)
        scanner = RealVulnerabilityScanner(config)
        
        assert scanner.constitutional_hash == CONSTITUTIONAL_HASH
        assert scanner.config == config
        
        # Test pattern matching
        test_line = 'password = os.environ.get("PASSWORD")'
        assert not scanner._is_safe_usage(test_line)
        
        safe_line = 'password = os.environ.get("PASSWORD")'
        assert scanner._is_safe_usage(safe_line)
        
    finally:
        os.unlink(temp_db)


def test_authentication_system_functionality():
    """Test authentication system basic functionality."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_security_hardening import RealSecurityConfig, RealAuthenticationSystem
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        config = RealSecurityConfig(security_db_path=temp_db)
        auth_system = RealAuthenticationSystem(config)
        
        assert auth_system.constitutional_hash == CONSTITUTIONAL_HASH
        assert auth_system.config == config
        
        # Test password hashing
        password = os.environ.get("PASSWORD")
        password_hash, salt = auth_system.hash_password(password)
        
        assert password_hash
        assert salt
        assert password_hash != password
        assert auth_system.verify_password(password, password_hash)
        assert not auth_system.verify_password("wrong_password", password_hash)
        
    finally:
        os.unlink(temp_db)


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_performance_optimizer import RealPerformanceConfig, RealPerformanceOrchestrator
    from real_security_hardening import RealSecurityConfig, RealSecurityOrchestrator
    
    # Test performance orchestrator
    perf_config = RealPerformanceConfig()
    perf_orchestrator = RealPerformanceOrchestrator(perf_config)
    
    assert perf_orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
    assert perf_orchestrator.config == perf_config
    assert not perf_orchestrator.optimization_running
    
    # Test security orchestrator
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        sec_config = RealSecurityConfig(security_db_path=temp_db)
        sec_orchestrator = RealSecurityOrchestrator(sec_config)
        
        assert sec_orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
        assert sec_orchestrator.config == sec_config
        
    finally:
        os.unlink(temp_db)


def test_file_scanning_capability():
    """Test file scanning capability with real files."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_security_hardening import RealSecurityConfig, RealVulnerabilityScanner
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            config = RealSecurityConfig(security_db_path=temp_db)
            scanner = RealVulnerabilityScanner(config)
            
            # Create test file with vulnerability
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("""
# Test file with vulnerability
password = os.environ.get("PASSWORD")
api_key = os.environ.get("API_KEY")  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
""")
            
            # Test file scanning
            scannable_files = scanner._get_scannable_files(Path(temp_dir))
            assert len(scannable_files) == 1
            assert test_file in scannable_files
            
        finally:
            os.unlink(temp_db)


def test_constitutional_compliance_integration():
    """Test constitutional compliance across all components."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))
    
    from real_performance_optimizer import (
        RealPerformanceConfig, RealDatabaseOptimizer, 
        RealRedisOptimizer, RealMemoryOptimizer
    )
    from real_security_hardening import (
        RealSecurityConfig, RealVulnerabilityScanner, 
        RealAuthenticationSystem
    )
    
    # Test all components have constitutional hash
    perf_config = RealPerformanceConfig()
    
    db_optimizer = RealDatabaseOptimizer(perf_config)
    redis_optimizer = RealRedisOptimizer(perf_config)
    memory_optimizer = RealMemoryOptimizer(perf_config)
    
    assert db_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
    assert redis_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
    assert memory_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        sec_config = RealSecurityConfig(security_db_path=temp_db)
        
        vulnerability_scanner = RealVulnerabilityScanner(sec_config)
        auth_system = RealAuthenticationSystem(sec_config)
        
        assert vulnerability_scanner.constitutional_hash == CONSTITUTIONAL_HASH
        assert auth_system.constitutional_hash == CONSTITUTIONAL_HASH
        
    finally:
        os.unlink(temp_db)


if __name__ == "__main__":
    # Run simple tests
    print("🔒 Running ACGS-2 Real Further Tuning Integration Tests")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    tests = [
        test_constitutional_hash_validation,
        test_performance_optimizer_file_exists,
        test_security_hardening_file_exists,
        test_performance_optimizer_imports,
        test_security_hardening_imports,
        test_performance_config_creation,
        test_security_config_creation,
        test_memory_optimizer_functionality,
        test_vulnerability_scanner_functionality,
        test_authentication_system_functionality,
        test_orchestrator_initialization,
        test_file_scanning_capability,
        test_constitutional_compliance_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
    else:
        print(f"⚠️ {failed} tests failed")
