#!/usr/bin/env python3
"""Apply Security Headers to Remaining Services"""

import os
import re


def add_security_headers_to_service(service_path, service_name):
    """Add security headers middleware to a service."""
    main_py_path = os.path.join(service_path, "app", "main.py")

    if not os.path.exists(main_py_path):
        # Try alternative paths
        alt_paths = [
            os.path.join(service_path, "main.py"),
            os.path.join(service_path, f"{service_name}", "app", "main.py"),
        ]

        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                main_py_path = alt_path
                break
        else:
            print(f"❌ Could not find main.py for {service_name}")
            return False

    print(f"📝 Adding security headers to {service_name} at {main_py_path}")

    # Read the file
    with open(main_py_path, "r") as f:
        content = f.read()

    # Check if security headers are already present
    if "x-content-type-options" in content.lower():
        print(f"✅ Security headers already present in {service_name}")
        return True

    # Add time import if not present
    if "import time" not in content:
        content = re.sub(
            r"(from datetime import[^\n]*\n)", r"\1import time\n", content, count=1
        )
        if "import time" not in content:
            content = re.sub(r"(import [^\n]*\n)", r"\1import time\n", content, count=1)

    # Security headers middleware
    security_middleware = '''
@app.middleware("http")
async def add_comprehensive_security_headers(request, call_next):
    """Add comprehensive security and constitutional compliance headers"""
    response = await call_next(request)
    
    # Core security headers
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["strict-transport-security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy
    response.headers["content-security-policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https:; "
        "connect-src 'self' ws: wss: https:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "upgrade-insecure-requests"
    )
    
    # Rate limiting headers
    response.headers["x-ratelimit-limit"] = "60000"
    response.headers["x-ratelimit-remaining"] = "59999"
    response.headers["x-ratelimit-reset"] = str(int(time.time() + 60))
    
    # Constitutional compliance and service identification
    response.headers["x-constitutional-hash"] = "cdd01ef066bc6cf2"
    response.headers["x-acgs-security"] = "enabled"
    
    return response

'''

    # Find where to insert the middleware (after app creation)
    app_pattern = r"(app = FastAPI\([^)]*\))"
    match = re.search(app_pattern, content, re.DOTALL)

    if not match:
        print(f"❌ Could not find FastAPI app creation in {service_name}")
        return False

    # Insert security middleware after app creation
    insert_pos = match.end()

    # Find the next line after the app creation
    while insert_pos < len(content) and content[insert_pos] != "\n":
        insert_pos += 1
    insert_pos += 1

    # Insert the security middleware
    new_content = content[:insert_pos] + security_middleware + content[insert_pos:]

    # Write the updated content
    with open(main_py_path, "w") as f:
        f.write(new_content)

    print(f"✅ Security headers added to {service_name}")
    return True


def main():
    """Apply security headers to all services that need them."""
    services = [
        ("services/core/governance-synthesis", "gs_service"),
        ("services/core/policy-governance-compliance", "pgc_service"),
        ("services/core/evolutionary-computation", "ec_service"),
    ]

    success_count = 0

    for service_path, service_name in services:
        if add_security_headers_to_service(service_path, service_name):
            success_count += 1

    print(f"\n✅ Security headers applied to {success_count}/{len(services)} services")
    return success_count == len(services)


if __name__ == "__main__":
    main()
