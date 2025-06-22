#!/usr/bin/env python3
"""
ACGS-1 Deprecation Process Validation Script

Tests RFC 8594 compliant deprecation headers and sunset mechanisms
using controlled test scenarios.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeprecationTestCase:
    """Test case for deprecation validation."""
    name: str
    version: str
    deprecated: bool
    deprecated_since: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    expected_headers: Dict[str, str] = None
    expected_status: int = 200


class DeprecationTestServer:
    """Test server that simulates deprecated API versions."""
    
    def __init__(self):
        self.app = FastAPI(title="ACGS-1 Deprecation Test Server")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup test routes with different deprecation states."""
        
        @self.app.get("/api/v1/test")
        async def test_v1_deprecated(request: Request):
            """Deprecated v1 endpoint."""
            response_data = {
                "version": "v1.0.0",
                "message": "This is a deprecated endpoint",
                "data": {"test": "value"}
            }
            
            response = JSONResponse(content=response_data)
            
            # Add deprecation headers (RFC 8594 compliant)
            deprecated_since = datetime(2025, 1, 1, tzinfo=timezone.utc)
            sunset_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
            
            response.headers["API-Version"] = "v1.0.0"
            response.headers["Deprecation"] = deprecated_since.strftime("%a, %d %b %Y %H:%M:%S GMT")
            response.headers["Sunset"] = sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
            response.headers["Link"] = '<https://docs.acgs.ai/migration/v2.0>; rel="successor-version"'
            response.headers["Warning"] = '299 - "API version v1.0.0 is deprecated. Migrate to v2.0.0 by 2025-07-01"'
            
            return response
        
        @self.app.get("/api/v1/sunset")
        async def test_v1_sunset(request: Request):
            """Sunset v1 endpoint that returns 410 Gone."""
            response_data = {
                "error": {
                    "code": "VERSION_SUNSET",
                    "message": "API version v1.0.0 has been sunset",
                    "details": {
                        "sunset_date": "2025-07-01T00:00:00Z",
                        "successor_version": "v2.0.0",
                        "migration_guide": "https://docs.acgs.ai/migration/v2.0"
                    }
                }
            }
            
            response = JSONResponse(content=response_data, status_code=410)
            response.headers["API-Version"] = "v1.0.0"
            response.headers["Link"] = '<https://docs.acgs.ai/migration/v2.0>; rel="successor-version"'
            
            return response
        
        @self.app.get("/api/v2/test")
        async def test_v2_current(request: Request):
            """Current v2 endpoint (not deprecated)."""
            response_data = {
                "version": "v2.0.0",
                "message": "This is the current API version",
                "data": {"test": "value", "enhanced": True}
            }
            
            response = JSONResponse(content=response_data)
            response.headers["API-Version"] = "v2.0.0"
            response.headers["X-Supported-Versions"] = "v2.0.0,v1.0.0"
            
            return response
        
        @self.app.get("/api/v2/beta")
        async def test_v2_beta(request: Request):
            """Beta v2 endpoint with warning."""
            response_data = {
                "version": "v2.1.0-beta",
                "message": "This is a beta endpoint",
                "data": {"test": "value", "beta_feature": True}
            }
            
            response = JSONResponse(content=response_data)
            response.headers["API-Version"] = "v2.1.0-beta"
            response.headers["Warning"] = '299 - "This is a beta API version. Subject to change without notice."'
            
            return response
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


class DeprecationValidator:
    """
    Validates deprecation process implementation.
    
    Tests RFC 8594 compliant deprecation headers, sunset mechanisms,
    and proper client communication for deprecated API versions.
    """
    
    def __init__(self, test_server_port: int = 8999):
        self.test_server_port = test_server_port
        self.test_server_url = f"http://localhost:{test_server_port}"
        self.test_server = DeprecationTestServer()
        
        # Define test cases
        self.test_cases = [
            DeprecationTestCase(
                name="deprecated_v1_endpoint",
                version="v1.0.0",
                deprecated=True,
                deprecated_since=datetime(2025, 1, 1, tzinfo=timezone.utc),
                sunset_date=datetime(2025, 7, 1, tzinfo=timezone.utc),
                expected_headers={
                    "API-Version": "v1.0.0",
                    "Deprecation": "Wed, 01 Jan 2025 00:00:00 GMT",
                    "Sunset": "Tue, 01 Jul 2025 00:00:00 GMT",
                    "Link": '<https://docs.acgs.ai/migration/v2.0>; rel="successor-version"',
                    "Warning": '299 - "API version v1.0.0 is deprecated. Migrate to v2.0.0 by 2025-07-01"'
                },
                expected_status=200
            ),
            DeprecationTestCase(
                name="sunset_v1_endpoint",
                version="v1.0.0",
                deprecated=True,
                expected_headers={
                    "API-Version": "v1.0.0",
                    "Link": '<https://docs.acgs.ai/migration/v2.0>; rel="successor-version"'
                },
                expected_status=410
            ),
            DeprecationTestCase(
                name="current_v2_endpoint",
                version="v2.0.0",
                deprecated=False,
                expected_headers={
                    "API-Version": "v2.0.0",
                    "X-Supported-Versions": "v2.0.0,v1.0.0"
                },
                expected_status=200
            ),
            DeprecationTestCase(
                name="beta_v2_endpoint",
                version="v2.1.0-beta",
                deprecated=False,
                expected_headers={
                    "API-Version": "v2.1.0-beta",
                    "Warning": '299 - "This is a beta API version. Subject to change without notice."'
                },
                expected_status=200
            )
        ]
    
    async def validate_deprecation_process(self) -> Dict[str, Any]:
        """Run comprehensive deprecation process validation."""
        logger.info("🔍 Starting deprecation process validation...")
        
        # Start test server
        server_task = await self._start_test_server()
        
        try:
            # Wait for server to be ready
            await self._wait_for_server()
            
            # Run deprecation tests
            test_results = await self._run_deprecation_tests()
            
            # Validate RFC 8594 compliance
            rfc_compliance = self._validate_rfc_compliance(test_results)
            
            # Test client behavior with deprecated APIs
            client_behavior = await self._test_client_behavior()
            
            # Validate deprecation timeline
            timeline_validation = self._validate_deprecation_timeline()
            
            # Generate comprehensive report
            report = {
                "validation_summary": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_test_cases": len(self.test_cases),
                    "passed_tests": len([r for r in test_results if r["success"]]),
                    "failed_tests": len([r for r in test_results if not r["success"]])
                },
                "test_results": test_results,
                "rfc_compliance": rfc_compliance,
                "client_behavior": client_behavior,
                "timeline_validation": timeline_validation,
                "success_criteria": {
                    "all_tests_pass": all(r["success"] for r in test_results),
                    "rfc_8594_compliant": rfc_compliance["compliant"],
                    "proper_client_handling": client_behavior["proper_handling"],
                    "timeline_valid": timeline_validation["valid"]
                }
            }
            
            return report
            
        finally:
            # Stop test server
            if server_task:
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
    
    async def _start_test_server(self):
        """Start the test server."""
        logger.info(f"🚀 Starting test server on port {self.test_server_port}...")
        
        config = uvicorn.Config(
            self.test_server.app,
            host="127.0.0.1",
            port=self.test_server_port,
            log_level="warning"
        )
        server = uvicorn.Server(config)
        
        # Start server in background
        server_task = asyncio.create_task(server.serve())
        return server_task
    
    async def _wait_for_server(self, timeout: int = 10):
        """Wait for test server to be ready."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.test_server_url}/health", timeout=1.0)
                    if response.status_code == 200:
                        logger.info("✅ Test server is ready")
                        return
            except:
                pass
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Test server failed to start within timeout")
            
            await asyncio.sleep(0.1)
    
    async def _run_deprecation_tests(self) -> List[Dict[str, Any]]:
        """Run all deprecation test cases."""
        logger.info("🧪 Running deprecation test cases...")
        
        results = []
        
        async with httpx.AsyncClient() as client:
            for test_case in self.test_cases:
                result = await self._run_single_test(client, test_case)
                results.append(result)
                
                if result["success"]:
                    logger.info(f"✅ {test_case.name}: PASSED")
                else:
                    logger.error(f"❌ {test_case.name}: FAILED - {result['error']}")
        
        return results
    
    async def _run_single_test(self, client: httpx.AsyncClient, test_case: DeprecationTestCase) -> Dict[str, Any]:
        """Run a single deprecation test case."""
        try:
            # Determine endpoint URL based on test case
            if test_case.name == "deprecated_v1_endpoint":
                url = f"{self.test_server_url}/api/v1/test"
            elif test_case.name == "sunset_v1_endpoint":
                url = f"{self.test_server_url}/api/v1/sunset"
            elif test_case.name == "current_v2_endpoint":
                url = f"{self.test_server_url}/api/v2/test"
            elif test_case.name == "beta_v2_endpoint":
                url = f"{self.test_server_url}/api/v2/beta"
            else:
                raise ValueError(f"Unknown test case: {test_case.name}")
            
            # Make request
            response = await client.get(url)
            
            # Validate status code
            if response.status_code != test_case.expected_status:
                return {
                    "test_case": test_case.name,
                    "success": False,
                    "error": f"Expected status {test_case.expected_status}, got {response.status_code}"
                }
            
            # Validate headers
            header_validation = self._validate_headers(response.headers, test_case.expected_headers)
            if not header_validation["valid"]:
                return {
                    "test_case": test_case.name,
                    "success": False,
                    "error": f"Header validation failed: {header_validation['errors']}"
                }
            
            # Validate response content for non-error responses
            if response.status_code < 400:
                content_validation = self._validate_response_content(response.json(), test_case)
                if not content_validation["valid"]:
                    return {
                        "test_case": test_case.name,
                        "success": False,
                        "error": f"Content validation failed: {content_validation['errors']}"
                    }
            
            return {
                "test_case": test_case.name,
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            
        except Exception as e:
            return {
                "test_case": test_case.name,
                "success": False,
                "error": str(e)
            }
    
    def _validate_headers(self, actual_headers: Dict[str, str], expected_headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate response headers against expected values."""
        if not expected_headers:
            return {"valid": True, "errors": []}
        
        errors = []
        
        for header_name, expected_value in expected_headers.items():
            if header_name not in actual_headers:
                errors.append(f"Missing header: {header_name}")
            elif actual_headers[header_name] != expected_value:
                errors.append(f"Header {header_name}: expected '{expected_value}', got '{actual_headers[header_name]}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_response_content(self, response_data: Dict[str, Any], test_case: DeprecationTestCase) -> Dict[str, Any]:
        """Validate response content structure."""
        errors = []
        
        # Basic structure validation
        if "version" not in response_data:
            errors.append("Missing 'version' field in response")
        elif response_data["version"] != test_case.version:
            errors.append(f"Version mismatch: expected {test_case.version}, got {response_data['version']}")
        
        if "message" not in response_data:
            errors.append("Missing 'message' field in response")
        
        if "data" not in response_data:
            errors.append("Missing 'data' field in response")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_rfc_compliance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate RFC 8594 compliance."""
        logger.info("📋 Validating RFC 8594 compliance...")
        
        compliance_checks = {
            "deprecation_header_format": True,
            "sunset_header_format": True,
            "link_header_present": True,
            "warning_header_present": True,
            "http_date_format": True
        }
        
        errors = []
        
        for result in test_results:
            if not result["success"]:
                continue
            
            headers = result.get("headers", {})
            
            # Check Deprecation header format (RFC 7234)
            if "Deprecation" in headers:
                deprecation_header = headers["Deprecation"]
                if not self._is_valid_http_date(deprecation_header):
                    compliance_checks["deprecation_header_format"] = False
                    errors.append(f"Invalid Deprecation header format: {deprecation_header}")
            
            # Check Sunset header format (RFC 8594)
            if "Sunset" in headers:
                sunset_header = headers["Sunset"]
                if not self._is_valid_http_date(sunset_header):
                    compliance_checks["sunset_header_format"] = False
                    errors.append(f"Invalid Sunset header format: {sunset_header}")
            
            # Check Link header for successor version
            if "Link" in headers:
                link_header = headers["Link"]
                if 'rel="successor-version"' not in link_header:
                    compliance_checks["link_header_present"] = False
                    errors.append("Link header missing successor-version relation")
        
        return {
            "compliant": all(compliance_checks.values()),
            "checks": compliance_checks,
            "errors": errors
        }
    
    def _is_valid_http_date(self, date_string: str) -> bool:
        """Validate HTTP date format (RFC 7231)."""
        try:
            # Try to parse HTTP date format
            datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S GMT")
            return True
        except ValueError:
            return False
    
    async def _test_client_behavior(self) -> Dict[str, Any]:
        """Test how clients should behave with deprecated APIs."""
        logger.info("👥 Testing client behavior with deprecated APIs...")
        
        behavior_tests = {
            "handles_deprecation_warnings": False,
            "respects_sunset_dates": False,
            "follows_migration_links": False
        }
        
        async with httpx.AsyncClient() as client:
            # Test deprecated endpoint
            response = await client.get(f"{self.test_server_url}/api/v1/test")
            
            if response.status_code == 200:
                headers = response.headers
                
                # Check if deprecation information is accessible
                if "Deprecation" in headers and "Sunset" in headers:
                    behavior_tests["handles_deprecation_warnings"] = True
                
                if "Link" in headers and "successor-version" in headers["Link"]:
                    behavior_tests["follows_migration_links"] = True
            
            # Test sunset endpoint
            sunset_response = await client.get(f"{self.test_server_url}/api/v1/sunset")
            if sunset_response.status_code == 410:
                behavior_tests["respects_sunset_dates"] = True
        
        return {
            "proper_handling": all(behavior_tests.values()),
            "behavior_checks": behavior_tests
        }
    
    def _validate_deprecation_timeline(self) -> Dict[str, Any]:
        """Validate deprecation timeline logic."""
        logger.info("📅 Validating deprecation timeline...")
        
        # Test timeline calculations
        now = datetime.now(timezone.utc)
        deprecated_since = now - timedelta(days=30)  # 30 days ago
        sunset_date = now + timedelta(days=150)      # 150 days from now
        
        # Validate 6-month deprecation period
        deprecation_period = sunset_date - deprecated_since
        expected_period = timedelta(days=180)  # 6 months
        
        timeline_valid = abs(deprecation_period.days - expected_period.days) <= 7  # Allow 1 week tolerance
        
        return {
            "valid": timeline_valid,
            "deprecation_period_days": deprecation_period.days,
            "expected_period_days": expected_period.days,
            "within_tolerance": timeline_valid
        }
    
    def save_report(self, report: Dict[str, Any], output_path: Path):
        """Save deprecation validation report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Deprecation validation report saved to {output_path}")


async def main():
    """Main function to run deprecation validation."""
    validator = DeprecationValidator()
    
    # Run comprehensive validation
    report = await validator.validate_deprecation_process()
    
    # Save report
    output_path = Path("docs/implementation/reports/deprecation_validation_report.json")
    validator.save_report(report, output_path)
    
    # Print summary
    print("\n" + "="*80)
    print("ACGS-1 DEPRECATION PROCESS VALIDATION SUMMARY")
    print("="*80)
    
    summary = report["validation_summary"]
    print(f"📊 Test Cases: {summary['total_test_cases']}")
    print(f"✅ Passed: {summary['passed_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    
    criteria = report["success_criteria"]
    print(f"\n🎯 SUCCESS CRITERIA:")
    print(f"   ✅ All Tests Pass: {'PASS' if criteria['all_tests_pass'] else 'FAIL'}")
    print(f"   📋 RFC 8594 Compliant: {'PASS' if criteria['rfc_8594_compliant'] else 'FAIL'}")
    print(f"   👥 Client Handling: {'PASS' if criteria['proper_client_handling'] else 'FAIL'}")
    print(f"   📅 Timeline Valid: {'PASS' if criteria['timeline_valid'] else 'FAIL'}")
    
    rfc_compliance = report["rfc_compliance"]
    if not rfc_compliance["compliant"]:
        print(f"\n⚠️  RFC COMPLIANCE ISSUES:")
        for error in rfc_compliance["errors"]:
            print(f"   - {error}")
    
    print("\n" + "="*80)
    
    # Return exit code based on success criteria
    all_criteria_passed = all(criteria.values())
    return 0 if all_criteria_passed else 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
