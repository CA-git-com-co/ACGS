#!/usr/bin/env python3
"""
Integration Tests for Real Further Tuning Implementation

Constitutional Hash: cdd01ef066bc6cf2
ACGS-2 Constitutional Compliance Validation

This module provides comprehensive integration tests for the real further tuning
implementations including performance optimization and security hardening.
"""

import asyncio
import os
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import the real implementations
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "performance"))
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "security"))

try:
    from real_performance_optimizer import (
        RealPerformanceConfig,
        RealDatabaseOptimizer,
        RealRedisOptimizer,
        RealMemoryOptimizer,
        RealPerformanceOrchestrator
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from real_security_hardening import (
        RealSecurityConfig,
        RealVulnerabilityScanner,
        RealAuthenticationSystem,
        RealSecurityOrchestrator
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@pytest.mark.skipif(not PERFORMANCE_AVAILABLE, reason="Performance modules not available")
class TestRealPerformanceOptimization:
    """Test suite for real performance optimization implementation."""

    @pytest.fixture
    def performance_config(self):
        """Create test performance configuration."""
        return RealPerformanceConfig(
            database_url=os.environ.get("DATABASE_URL"),
            redis_url="redis://localhost:6379/1",
            db_pool_min_size=2,
            db_pool_max_size=5,
            redis_pool_size=3,
            target_query_time_ms=100.0,
            target_cache_hit_rate=0.75
        )
    
    @pytest.fixture
    def temp_db_file(self):
        """Create temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    def test_performance_config_creation(self, performance_config):
        """Test performance configuration creation."""
        assert performance_config.constitutional_hash == CONSTITUTIONAL_HASH
        assert performance_config.db_pool_min_size == 2
        assert performance_config.db_pool_max_size == 5
        assert performance_config.target_query_time_ms == 100.0
        assert performance_config.target_cache_hit_rate == 0.75
    
    def test_database_optimizer_initialization(self, performance_config):
        """Test database optimizer initialization."""
        optimizer = RealDatabaseOptimizer(performance_config)
        
        assert optimizer.config == performance_config
        assert optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        assert optimizer.pool is None
        assert len(optimizer.query_cache) == 0
        assert len(optimizer.query_stats) == 0
    
    def test_redis_optimizer_initialization(self, performance_config):
        """Test Redis optimizer initialization."""
        optimizer = RealRedisOptimizer(performance_config)
        
        assert optimizer.config == performance_config
        assert optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        assert optimizer.redis is None
        assert optimizer.cache_stats["hits"] == 0
        assert optimizer.cache_stats["misses"] == 0
    
    def test_memory_optimizer_initialization(self, performance_config):
        """Test memory optimizer initialization."""
        optimizer = RealMemoryOptimizer(performance_config)
        
        assert optimizer.config == performance_config
        assert optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(optimizer.object_pools) == 0
        assert len(optimizer.memory_history) == 0
        assert optimizer.gc_stats["collections"] == 0
    
    def test_memory_optimizer_real_usage(self, performance_config):
        """Test memory optimizer with real system data."""
        optimizer = RealMemoryOptimizer(performance_config)
        
        # Get real memory usage
        memory_usage = optimizer.get_real_memory_usage()
        
        assert "process_rss_mb" in memory_usage
        assert "system_used_percent" in memory_usage
        assert "constitutional_hash" in memory_usage
        assert memory_usage["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert memory_usage["process_rss_mb"] > 0
        assert 0 <= memory_usage["system_used_percent"] <= 100
    
    @pytest.mark.asyncio
    async def test_memory_optimization(self, performance_config):
        """Test memory optimization functionality."""
        optimizer = RealMemoryOptimizer(performance_config)
        
        # Perform memory optimization
        result = await optimizer.optimize_memory()
        
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "memory_before" in result
        assert "memory_after" in result
        assert "optimization_time_seconds" in result
        assert result["optimization_time_seconds"] >= 0
    
    @pytest.mark.asyncio
    async def test_memory_performance_metrics(self, performance_config):
        """Test memory performance metrics collection."""
        optimizer = RealMemoryOptimizer(performance_config)
        
        # Get performance metrics
        metrics = await optimizer.get_performance_metrics()
        
        assert "constitutional_hash" in metrics
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "current_memory" in metrics
        assert "memory_trend" in metrics
        assert "gc_stats" in metrics
        assert "object_pools" in metrics
    
    def test_object_pool_management(self, performance_config):
        """Test object pool management."""
        optimizer = RealMemoryOptimizer(performance_config)
        
        # Test object pool creation
        def test_factory():
            return {"test": "object"}
        
        pool = optimizer.get_object_pool("test_pool", test_factory)
        assert len(pool) > 0
        
        # Test returning object to pool
        test_obj = {"returned": "object"}
        success = optimizer.return_to_pool("test_pool", test_obj)
        assert success
        
        # Verify object is in pool
        pool = optimizer.get_object_pool("test_pool")
        assert test_obj in pool
    
    def test_performance_orchestrator_initialization(self, performance_config):
        """Test performance orchestrator initialization."""
        orchestrator = RealPerformanceOrchestrator(performance_config)
        
        assert orchestrator.config == performance_config
        assert orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
        assert isinstance(orchestrator.db_optimizer, RealDatabaseOptimizer)
        assert isinstance(orchestrator.redis_optimizer, RealRedisOptimizer)
        assert isinstance(orchestrator.memory_optimizer, RealMemoryOptimizer)
        assert len(orchestrator.performance_history) == 0
        assert not orchestrator.optimization_running


class TestRealSecurityHardening:
    """Test suite for real security hardening implementation."""
    
    @pytest.fixture
    def security_config(self, temp_db_file):
        """Create test security configuration."""
        return RealSecurityConfig(
            security_db_path=temp_db_file,
            password_min_length=8,
            max_login_attempts=3,
            lockout_duration_minutes=5
        )
    
    @pytest.fixture
    def temp_db_file(self):
        """Create temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def temp_scan_dir(self):
        """Create temporary directory with test files for scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files with vulnerabilities
            (temp_path / "test.py").write_text("""
# Test file with vulnerabilities
password = os.environ.get("PASSWORD")
api_key = os.environ.get("API_KEY")  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
database_url = os.environ.get("DATABASE_URL")
""")
            
            (temp_path / "safe.py").write_text("""
# Safe file using environment variables
import os
password = os.environ.get("PASSWORD")
api_key = os.environ.get("API_KEY")
database_url = os.environ.get("DATABASE_URL")
""")
            
            yield temp_path
    
    def test_security_config_creation(self, security_config):
        """Test security configuration creation."""
        assert security_config.constitutional_hash == CONSTITUTIONAL_HASH
        assert security_config.password_min_length == 8
        assert security_config.max_login_attempts == 3
        assert security_config.lockout_duration_minutes == 5
        assert "password" in security_config.secret_patterns
        assert "api_key" in security_config.secret_patterns
    
    def test_vulnerability_scanner_initialization(self, security_config):
        """Test vulnerability scanner initialization."""
        scanner = RealVulnerabilityScanner(security_config)
        
        assert scanner.config == security_config
        assert scanner.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(scanner.vulnerabilities) == 0
    
    @pytest.mark.asyncio
    async def test_vulnerability_scanning(self, security_config, temp_scan_dir):
        """Test real vulnerability scanning."""
        scanner = RealVulnerabilityScanner(security_config)
        
        # Scan the temporary directory
        vulnerabilities = await scanner.scan_directory(temp_scan_dir)
        
        # Should find vulnerabilities in test.py but not safe.py
        assert len(vulnerabilities) > 0
        
        # Check that vulnerabilities have required fields
        for vuln in vulnerabilities:
            assert hasattr(vuln, 'file_path')
            assert hasattr(vuln, 'line_number')
            assert hasattr(vuln, 'vulnerability_type')
            assert hasattr(vuln, 'severity')
            assert hasattr(vuln, 'constitutional_hash')
            assert vuln.constitutional_hash == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_vulnerability_remediation(self, security_config, temp_scan_dir):
        """Test vulnerability remediation."""
        scanner = RealVulnerabilityScanner(security_config)
        
        # Scan for vulnerabilities
        vulnerabilities = await scanner.scan_directory(temp_scan_dir)
        initial_count = len(vulnerabilities)
        
        # Attempt remediation
        remediated_count = await scanner.remediate_vulnerabilities(vulnerabilities)
        
        # Should have attempted to remediate some vulnerabilities
        assert remediated_count >= 0
        assert remediated_count <= initial_count
    
    def test_authentication_system_initialization(self, security_config):
        """Test authentication system initialization."""
        auth_system = RealAuthenticationSystem(security_config)
        
        assert auth_system.config == security_config
        assert auth_system.constitutional_hash == CONSTITUTIONAL_HASH
        assert auth_system.db_path == security_config.security_db_path
    
    def test_password_hashing(self, security_config):
        """Test password hashing functionality."""
        auth_system = RealAuthenticationSystem(security_config)
        
        password = os.environ.get("PASSWORD")
        password_hash, salt = auth_system.hash_password(password)
        
        # Verify hash and salt are generated
        assert password_hash
        assert salt
        assert password_hash != password
        
        # Verify password verification works
        assert auth_system.verify_password(password, password_hash)
        assert not auth_system.verify_password("wrong_password", password_hash)
    
    @pytest.mark.asyncio
    async def test_user_creation(self, security_config):
        """Test user creation functionality."""
        auth_system = RealAuthenticationSystem(security_config)
        
        # Test successful user creation
        result = await auth_system.create_user("test_user", "secure_password_123")
        
        assert result["success"]
        assert "user_id" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Test duplicate user creation
        duplicate_result = await auth_system.create_user("test_user", "another_password")
        assert not duplicate_result["success"]
        assert "already exists" in duplicate_result["error"]
    
    @pytest.mark.asyncio
    async def test_user_authentication(self, security_config):
        """Test user authentication functionality."""
        auth_system = RealAuthenticationSystem(security_config)
        
        # Create a test user
        await auth_system.create_user("auth_test_user", "secure_password_123")
        
        # Test successful authentication
        auth_result = await auth_system.authenticate_user("auth_test_user", "secure_password_123")
        
        assert auth_result["success"]
        assert "session_token" in auth_result
        assert auth_result["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Test failed authentication
        failed_result = await auth_system.authenticate_user("auth_test_user", "wrong_password")
        assert not failed_result["success"]
    
    @pytest.mark.asyncio
    async def test_session_management(self, security_config):
        """Test session management functionality."""
        auth_system = RealAuthenticationSystem(security_config)
        
        # Create user and authenticate
        await auth_system.create_user("session_test_user", "secure_password_123")
        auth_result = await auth_system.authenticate_user("session_test_user", "secure_password_123")
        
        session_token = auth_result["session_token"]
        
        # Test session validation
        validation_result = await auth_system.validate_session(session_token)
        assert validation_result["valid"]
        assert validation_result["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Test session logout
        logout_result = await auth_system.logout_user(session_token)
        assert logout_result
        
        # Test session validation after logout
        post_logout_validation = await auth_system.validate_session(session_token)
        assert not post_logout_validation["valid"]
    
    @pytest.mark.asyncio
    async def test_security_metrics(self, security_config):
        """Test security metrics collection."""
        auth_system = RealAuthenticationSystem(security_config)
        
        # Get security metrics
        metrics = await auth_system.get_security_metrics()
        
        assert "constitutional_hash" in metrics
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "total_users" in metrics
        assert "locked_users" in metrics
        assert "active_sessions" in metrics
        assert "login_success_rate" in metrics
    
    def test_security_orchestrator_initialization(self, security_config):
        """Test security orchestrator initialization."""
        orchestrator = RealSecurityOrchestrator(security_config)
        
        assert orchestrator.config == security_config
        assert orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
        assert isinstance(orchestrator.vulnerability_scanner, RealVulnerabilityScanner)
        assert isinstance(orchestrator.auth_system, RealAuthenticationSystem)
    
    @pytest.mark.asyncio
    async def test_comprehensive_security_scan(self, security_config, temp_scan_dir):
        """Test comprehensive security scan."""
        orchestrator = RealSecurityOrchestrator(security_config)
        
        # Perform comprehensive scan
        report = await orchestrator.perform_comprehensive_security_scan(temp_scan_dir)
        
        assert "constitutional_hash" in report
        assert report["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "scan_timestamp" in report
        assert "scan_duration_seconds" in report
        assert "vulnerabilities_found" in report
        assert "vulnerabilities_remediated" in report
        assert "security_score" in report
        assert "authentication_metrics" in report
        assert "recommendations" in report
        
        # Verify scan found vulnerabilities
        assert report["vulnerabilities_found"] > 0
        assert 0 <= report["security_score"] <= 100


class TestIntegrationScenarios:
    """Test suite for integration scenarios combining performance and security."""
    
    @pytest.fixture
    def integrated_configs(self, temp_db_file):
        """Create integrated test configurations."""
        performance_config = RealPerformanceConfig(
            database_url=os.environ.get("DATABASE_URL"),
            redis_url="redis://localhost:6379/1"
        )
        
        security_config = RealSecurityConfig(
            security_db_path=temp_db_file
        )
        
        return performance_config, security_config
    
    @pytest.fixture
    def temp_db_file(self):
        """Create temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    def test_constitutional_compliance_validation(self, integrated_configs):
        """Test constitutional compliance across all components."""
        performance_config, security_config = integrated_configs
        
        # Test performance components
        db_optimizer = RealDatabaseOptimizer(performance_config)
        redis_optimizer = RealRedisOptimizer(performance_config)
        memory_optimizer = RealMemoryOptimizer(performance_config)
        
        assert db_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        assert redis_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        assert memory_optimizer.constitutional_hash == CONSTITUTIONAL_HASH
        
        # Test security components
        vulnerability_scanner = RealVulnerabilityScanner(security_config)
        auth_system = RealAuthenticationSystem(security_config)
        
        assert vulnerability_scanner.constitutional_hash == CONSTITUTIONAL_HASH
        assert auth_system.constitutional_hash == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_performance_and_security_integration(self, integrated_configs, temp_scan_dir):
        """Test integration between performance optimization and security hardening."""
        performance_config, security_config = integrated_configs
        
        # Initialize orchestrators
        performance_orchestrator = RealPerformanceOrchestrator(performance_config)
        security_orchestrator = RealSecurityOrchestrator(security_config)
        
        # Collect baseline performance metrics
        performance_metrics = await performance_orchestrator.collect_real_performance_metrics()
        
        # Perform security scan
        security_report = await security_orchestrator.perform_comprehensive_security_scan(temp_scan_dir)
        
        # Verify both systems maintain constitutional compliance
        assert performance_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert security_report["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Verify integration points
        assert "memory" in performance_metrics
        assert "vulnerabilities_found" in security_report
        assert performance_metrics["timestamp"] > 0
        assert security_report["scan_duration_seconds"] > 0
    
    def test_error_handling_and_resilience(self, integrated_configs):
        """Test error handling and system resilience."""
        performance_config, security_config = integrated_configs
        
        # Test with invalid configurations
        invalid_performance_config = RealPerformanceConfig(
            database_url=os.environ.get("DATABASE_URL"),
            redis_url="invalid://connection"
        )
        
        # Should not crash on initialization
        orchestrator = RealPerformanceOrchestrator(invalid_performance_config)
        assert orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
        
        # Test security with non-existent directory
        security_orchestrator = RealSecurityOrchestrator(security_config)
        scanner = security_orchestrator.vulnerability_scanner
        
        # Should handle non-existent paths gracefully
        non_existent_path = Path("/non/existent/path")
        scannable_files = scanner._get_scannable_files(non_existent_path)
        assert len(scannable_files) == 0


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])
