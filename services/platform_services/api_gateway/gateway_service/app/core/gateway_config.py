"""
ACGS API Gateway Configuration

Configuration management for the constitutional AI-enhanced API gateway
with security, rate limiting, and compliance settings.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    name: str
    url: str
    health_check_path: str
    timeout_seconds: int
    max_retries: int
    constitutional_compliance_required: bool = True


class GatewayConfig:
    """ACGS API Gateway configuration."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Constitutional compliance
    CONSTITUTIONAL_HASH = CONSTITUTIONAL_HASH
    CONSTITUTIONAL_COMPLIANCE_ENABLED = os.getenv("CONSTITUTIONAL_COMPLIANCE_ENABLED", "true").lower() == "true"
    FORMAL_VERIFICATION_ENABLED = os.getenv("FORMAL_VERIFICATION_ENABLED", "true").lower() == "true"
    
    # Network configuration
    HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
    PORT = int(os.getenv("GATEWAY_PORT", "8080"))
    
    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,*.acgs.local").split(",")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    
    # Multi-tenant configuration
    MULTI_TENANT_ENABLED = os.getenv("MULTI_TENANT_ENABLED", "true").lower() == "true"
    TENANT_ISOLATION_STRICT = os.getenv("TENANT_ISOLATION_STRICT", "true").lower() == "true"
    
    # Security headers
    SECURITY_HEADERS_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
    HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
    CSP_POLICY = os.getenv("CSP_POLICY", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
    
    # Request/Response configuration
    MAX_REQUEST_SIZE_MB = int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Backend service configuration
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
    CONSTITUTIONAL_AI_SERVICE_URL = os.getenv("CONSTITUTIONAL_AI_SERVICE_URL", "http://constitutional-ai-service:8001")
    INTEGRITY_SERVICE_URL = os.getenv("INTEGRITY_SERVICE_URL", "http://integrity-service:8002")
    GOVERNANCE_SYNTHESIS_SERVICE_URL = os.getenv("GOVERNANCE_SYNTHESIS_SERVICE_URL", "http://governance-synthesis-service:8004")
    POLICY_GOVERNANCE_SERVICE_URL = os.getenv("POLICY_GOVERNANCE_SERVICE_URL", "http://policy-governance-service:8005")
    FORMAL_VERIFICATION_SERVICE_URL = os.getenv("FORMAL_VERIFICATION_SERVICE_URL", "http://formal-verification-service:8006")
    
    # Monitoring and logging
    PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_LOGGING_ENABLED = os.getenv("REQUEST_LOGGING_ENABLED", "true").lower() == "true"
    
    # Cache configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    
    # Documentation
    ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"
    ENABLE_REDOC = os.getenv("ENABLE_REDOC", "false").lower() == "true"
    
    # Circuit breaker configuration
    CIRCUIT_BREAKER_ENABLED = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))
    
    # Load balancing
    LOAD_BALANCING_STRATEGY = os.getenv("LOAD_BALANCING_STRATEGY", "round_robin")  # round_robin, least_connections, weighted
    
    # Health check configuration
    HEALTH_CHECK_INTERVAL_SECONDS = int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "30"))
    HEALTH_CHECK_TIMEOUT_SECONDS = int(os.getenv("HEALTH_CHECK_TIMEOUT_SECONDS", "10"))
    
    @classmethod
    def get_service_endpoints(cls) -> List[ServiceEndpoint]:
        """Get configured service endpoints."""
        
        return [
            ServiceEndpoint(
                name="auth",
                url=cls.AUTH_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            ),
            ServiceEndpoint(
                name="constitutional-ai",
                url=cls.CONSTITUTIONAL_AI_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            ),
            ServiceEndpoint(
                name="integrity",
                url=cls.INTEGRITY_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            ),
            ServiceEndpoint(
                name="governance-synthesis",
                url=cls.GOVERNANCE_SYNTHESIS_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            ),
            ServiceEndpoint(
                name="policy-governance",
                url=cls.POLICY_GOVERNANCE_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            ),
            ServiceEndpoint(
                name="formal-verification",
                url=cls.FORMAL_VERIFICATION_SERVICE_URL,
                health_check_path="/health",
                timeout_seconds=cls.REQUEST_TIMEOUT_SECONDS,
                max_retries=3,
                constitutional_compliance_required=True
            )
        ]
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Get security configuration."""
        
        return {
            "constitutional_hash": cls.CONSTITUTIONAL_HASH,
            "constitutional_compliance_enabled": cls.CONSTITUTIONAL_COMPLIANCE_ENABLED,
            "formal_verification_enabled": cls.FORMAL_VERIFICATION_ENABLED,
            "multi_tenant_enabled": cls.MULTI_TENANT_ENABLED,
            "tenant_isolation_strict": cls.TENANT_ISOLATION_STRICT,
            "rate_limiting": {
                "enabled": cls.RATE_LIMIT_ENABLED,
                "requests_per_minute": cls.RATE_LIMIT_REQUESTS_PER_MINUTE,
                "burst_limit": cls.RATE_LIMIT_BURST
            },
            "security_headers": {
                "enabled": cls.SECURITY_HEADERS_ENABLED,
                "hsts_max_age": cls.HSTS_MAX_AGE,
                "csp_policy": cls.CSP_POLICY
            },
            "authentication": {
                "jwt_algorithm": cls.JWT_ALGORITHM,
                "access_token_expire_minutes": cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            }
        }
    
    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """Get monitoring configuration."""
        
        return {
            "prometheus_enabled": cls.PROMETHEUS_ENABLED,
            "metrics_port": cls.METRICS_PORT,
            "request_logging_enabled": cls.REQUEST_LOGGING_ENABLED,
            "log_level": cls.LOG_LEVEL,
            "health_check": {
                "interval_seconds": cls.HEALTH_CHECK_INTERVAL_SECONDS,
                "timeout_seconds": cls.HEALTH_CHECK_TIMEOUT_SECONDS
            }
        }
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate gateway configuration."""
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "constitutional_hash": cls.CONSTITUTIONAL_HASH
        }
        
        # Check required environment variables
        required_vars = [
            "JWT_SECRET_KEY",
            "AUTH_SERVICE_URL",
            "CONSTITUTIONAL_AI_SERVICE_URL"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                validation_results["errors"].append(f"Missing required environment variable: {var}")
                validation_results["valid"] = False
        
        # Check constitutional hash
        if cls.CONSTITUTIONAL_HASH != CONSTITUTIONAL_HASH:
            validation_results["errors"].append("Constitutional hash mismatch")
            validation_results["valid"] = False
        
        # Check JWT secret in production
        if cls.ENVIRONMENT == "production" and cls.JWT_SECRET_KEY == "your-secret-key-change-in-production":
            validation_results["errors"].append("Default JWT secret key detected in production")
            validation_results["valid"] = False
        
        # Check rate limiting configuration
        if cls.RATE_LIMIT_REQUESTS_PER_MINUTE <= 0:
            validation_results["warnings"].append("Rate limiting disabled (requests_per_minute <= 0)")
        
        # Check CORS configuration
        if "*" in cls.CORS_ORIGINS and cls.ENVIRONMENT == "production":
            validation_results["warnings"].append("Wildcard CORS origin detected in production")
        
        # Check documentation endpoints in production
        if cls.ENVIRONMENT == "production" and (cls.ENABLE_DOCS or cls.ENABLE_REDOC):
            validation_results["warnings"].append("API documentation enabled in production")
        
        return validation_results
    
    @classmethod
    def log_configuration(cls):
        """Log current configuration (filtered for security)."""
        
        logger.info("ACGS API Gateway Configuration:")
        logger.info(f"  Environment: {cls.ENVIRONMENT}")
        logger.info(f"  Constitutional Hash: {cls.CONSTITUTIONAL_HASH}")
        logger.info(f"  Constitutional Compliance: {cls.CONSTITUTIONAL_COMPLIANCE_ENABLED}")
        logger.info(f"  Multi-tenant: {cls.MULTI_TENANT_ENABLED}")
        logger.info(f"  Rate Limiting: {cls.RATE_LIMIT_ENABLED} ({cls.RATE_LIMIT_REQUESTS_PER_MINUTE}/min)")
        logger.info(f"  Security Headers: {cls.SECURITY_HEADERS_ENABLED}")
        logger.info(f"  Request Logging: {cls.REQUEST_LOGGING_ENABLED}")
        logger.info(f"  Prometheus: {cls.PROMETHEUS_ENABLED}")
        logger.info(f"  Circuit Breaker: {cls.CIRCUIT_BREAKER_ENABLED}")
        logger.info(f"  Load Balancing: {cls.LOAD_BALANCING_STRATEGY}")
        
        # Log service endpoints (without URLs for security)
        endpoints = cls.get_service_endpoints()
        logger.info(f"  Configured Services: {[ep.name for ep in endpoints]}")
        
        # Validate and log any issues
        validation = cls.validate_configuration()
        if validation["errors"]:
            logger.error(f"Configuration errors: {validation['errors']}")
        if validation["warnings"]:
            logger.warning(f"Configuration warnings: {validation['warnings']}")


# Global configuration instance
config = GatewayConfig()

# Log configuration on import
if __name__ != "__main__":
    config.log_configuration()