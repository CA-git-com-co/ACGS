#!/usr/bin/env python3
"""
ACGS-1 Security Headers Middleware Application Script

This script applies essential security headers middleware to all running ACGS services
to address the missing security headers identified in the security audit.

This is a focused implementation to quickly improve the compliance score by adding
the critical OWASP-recommended security headers.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Service paths
SERVICES = {
    "ac_service": "services/core/constitutional-ai/ac_service/app/main.py",
    "integrity_service": "services/platform/integrity/integrity_service/app/main.py",
    "fv_service": "services/core/formal-verification/fv_service/main.py",
    "gs_service": "services/core/governance-synthesis/gs_service/app/main.py",
    "pgc_service": "services/core/policy-governance/pgc_service/app/main.py",
    "ec_service": "services/core/self-evolving-ai/app/main.py",
}

SECURITY_HEADERS_MIDDLEWARE = '''
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add comprehensive OWASP-recommended security headers."""
    response = await call_next(request)
    
    # Core security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # HSTS (HTTP Strict Transport Security)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy (CSP) - Enhanced for XSS protection
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    
    # Permissions Policy
    permissions_policy = (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=(), gyroscope=()"
    )
    response.headers["Permissions-Policy"] = permissions_policy
    
    # Additional security headers
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    
    # ACGS-1 specific headers
    response.headers["X-ACGS-Security"] = "enabled"
    response.headers["X-Constitutional-Hash"] = "cdd01ef066bc6cf2"
    
    return response
'''


def apply_security_headers_to_service(service_name: str, service_path: str) -> bool:
    """Apply security headers middleware to a specific service."""
    full_path = project_root / service_path

    if not full_path.exists():
        logger.warning(f"⚠️ Service file not found: {full_path}")
        return False

    try:
        # Read current content
        with open(full_path, "r") as f:
            content = f.read()

        # Check if security headers middleware is already present
        if "add_security_headers" in content and "X-Content-Type-Options" in content:
            logger.info(f"✅ {service_name}: Security headers middleware already present")
            return True

        # Find the right place to add the middleware (after app creation)
        lines = content.split("\n")

        # Look for app creation or existing middleware
        insert_index = -1
        for i, line in enumerate(lines):
            if "app = FastAPI(" in line:
                # Find the end of the FastAPI constructor
                j = i
                paren_count = 0
                while j < len(lines):
                    paren_count += lines[j].count("(") - lines[j].count(")")
                    if paren_count == 0 and ")" in lines[j]:
                        insert_index = j + 1
                        break
                    j += 1
                break
            elif "@app.middleware" in line:
                # Insert before existing middleware
                insert_index = i
                break

        if insert_index == -1:
            # Fallback: insert before the first @app route
            for i, line in enumerate(lines):
                if line.strip().startswith("@app."):
                    insert_index = i
                    break

        if insert_index == -1:
            logger.error(f"❌ Could not find insertion point in {service_name}")
            return False

        # Insert the security headers middleware
        lines.insert(insert_index, "")
        lines.insert(insert_index + 1, SECURITY_HEADERS_MIDDLEWARE)
        lines.insert(insert_index + 2, "")

        # Write back to file
        updated_content = "\n".join(lines)
        with open(full_path, "w") as f:
            f.write(updated_content)

        logger.info(f"✅ {service_name}: Security headers middleware applied")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to apply security headers to {service_name}: {e}")
        return False


def main():
    """Apply security headers middleware to all services."""
    logger.info("🔒 Applying Security Headers Middleware to ACGS Services")
    logger.info("🎯 Target: Add OWASP-recommended security headers to improve compliance")

    success_count = 0
    total_services = len(SERVICES)

    for service_name, service_path in SERVICES.items():
        logger.info(f"🔧 Processing {service_name}")
        if apply_security_headers_to_service(service_name, service_path):
            success_count += 1

    # Summary
    logger.info("=" * 60)
    logger.info("🔒 SECURITY HEADERS MIDDLEWARE APPLICATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Services updated: {success_count}/{total_services}")
    logger.info(f"🎯 Success rate: {(success_count/total_services)*100:.1f}%")

    if success_count == total_services:
        logger.info("🎉 All services updated successfully!")
        logger.info("🔄 Please restart services to apply security headers")
        return 0
    else:
        logger.warning("⚠️ Some services could not be updated")
        return 1


if __name__ == "__main__":
    exit(main())
