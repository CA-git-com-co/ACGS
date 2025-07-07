"""
ACGS Constitutional Compliance Testing Validator
Constitutional Hash: cdd01ef066bc6cf2

This module provides automated constitutional compliance validation
across all ACGS services and API endpoints.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


@dataclass
class ComplianceViolation:
    """Represents a constitutional compliance violation."""
    service_name: str
    endpoint: str
    violation_type: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    timestamp: datetime
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class ComplianceReport:
    """Constitutional compliance validation report."""
    total_endpoints_tested: int
    compliant_endpoints: int
    violations: List[ComplianceViolation]
    compliance_rate: float
    constitutional_hash: str
    test_timestamp: datetime
    
    @property
    def is_fully_compliant(self) -> bool:
        """Check if all endpoints are constitutionally compliant."""
        return len(self.violations) == 0 and self.compliance_rate == 1.0


class ConstitutionalComplianceValidator:
    """Automated constitutional compliance validator for ACGS services."""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    REQUIRED_HEADERS = [
        "X-Constitutional-Hash",
        "X-Constitutional-Compliance"
    ]
    
    def __init__(self):
        self.violations: List[ComplianceViolation] = []
        self.tested_endpoints = 0
        self.compliant_endpoints = 0
    
    async def validate_service_compliance(
        self,
        service_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        auth_headers: Optional[Dict[str, str]] = None
    ) -> ComplianceReport:
        """Validate constitutional compliance for all endpoints of a service."""
        logger.info(f"Starting constitutional compliance validation for {service_name}")
        
        self.violations.clear()
        self.tested_endpoints = 0
        self.compliant_endpoints = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint_config in endpoints:
                await self._validate_endpoint(
                    client, service_name, base_url, endpoint_config, auth_headers
                )
        
        compliance_rate = (
            self.compliant_endpoints / self.tested_endpoints 
            if self.tested_endpoints > 0 else 0.0
        )
        
        report = ComplianceReport(
            total_endpoints_tested=self.tested_endpoints,
            compliant_endpoints=self.compliant_endpoints,
            violations=self.violations.copy(),
            compliance_rate=compliance_rate,
            constitutional_hash=self.CONSTITUTIONAL_HASH,
            test_timestamp=datetime.utcnow()
        )
        
        logger.info(
            f"Constitutional compliance validation completed for {service_name}: "
            f"{compliance_rate:.2%} compliant ({self.compliant_endpoints}/{self.tested_endpoints})"
        )
        
        return report
    
    async def _validate_endpoint(
        self,
        client: httpx.AsyncClient,
        service_name: str,
        base_url: str,
        endpoint_config: Dict[str, Any],
        auth_headers: Optional[Dict[str, str]]
    ):
        """Validate constitutional compliance for a single endpoint."""
        endpoint = endpoint_config["path"]
        method = endpoint_config.get("method", "GET")
        test_data = endpoint_config.get("test_data", {})
        
        self.tested_endpoints += 1
        
        try:
            url = urljoin(base_url, endpoint)
            headers = {
                "X-Constitutional-Hash": self.CONSTITUTIONAL_HASH,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if auth_headers:
                headers.update(auth_headers)
            
            # Add tenant context for multi-tenant endpoints
            if endpoint_config.get("requires_tenant", True):
                headers["X-Tenant-ID"] = "test-tenant-compliance"
                headers["X-User-ID"] = "test-user-compliance"
            
            # Make request
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=test_data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(url, json=test_data, headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                self._add_violation(
                    service_name, endpoint, "unsupported_method",
                    f"Unsupported HTTP method: {method}", "medium"
                )
                return
            
            # Validate response
            await self._validate_response_compliance(
                service_name, endpoint, response, test_data
            )
            
        except httpx.TimeoutException:
            self._add_violation(
                service_name, endpoint, "timeout",
                "Request timed out during compliance validation", "high"
            )
        except httpx.RequestError as e:
            self._add_violation(
                service_name, endpoint, "request_error",
                f"Request error during compliance validation: {str(e)}", "high"
            )
        except Exception as e:
            self._add_violation(
                service_name, endpoint, "unexpected_error",
                f"Unexpected error during compliance validation: {str(e)}", "critical"
            )
    
    async def _validate_response_compliance(
        self,
        service_name: str,
        endpoint: str,
        response: httpx.Response,
        request_data: Dict[str, Any]
    ):
        """Validate constitutional compliance in HTTP response."""
        violations_found = False
        
        # Check response status
        if response.status_code >= 500:
            self._add_violation(
                service_name, endpoint, "server_error",
                f"Server error response: {response.status_code}", "high",
                request_data, self._safe_json_parse(response)
            )
            violations_found = True
        
        # Check required headers
        for header in self.REQUIRED_HEADERS:
            if header not in response.headers:
                self._add_violation(
                    service_name, endpoint, "missing_header",
                    f"Missing required header: {header}", "critical",
                    request_data, self._safe_json_parse(response)
                )
                violations_found = True
        
        # Validate constitutional hash in headers
        hash_header = response.headers.get("X-Constitutional-Hash")
        if hash_header != self.CONSTITUTIONAL_HASH:
            self._add_violation(
                service_name, endpoint, "invalid_constitutional_hash_header",
                f"Invalid constitutional hash in header: expected {self.CONSTITUTIONAL_HASH}, got {hash_header}",
                "critical", request_data, self._safe_json_parse(response)
            )
            violations_found = True
        
        # Validate constitutional compliance header
        compliance_header = response.headers.get("X-Constitutional-Compliance")
        if compliance_header != "verified":
            self._add_violation(
                service_name, endpoint, "invalid_compliance_header",
                f"Invalid constitutional compliance header: expected 'verified', got {compliance_header}",
                "critical", request_data, self._safe_json_parse(response)
            )
            violations_found = True
        
        # Validate JSON response body if applicable
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                response_data = response.json()
                await self._validate_json_compliance(
                    service_name, endpoint, response_data, request_data
                )
            except json.JSONDecodeError:
                self._add_violation(
                    service_name, endpoint, "invalid_json",
                    "Response is not valid JSON despite content-type", "medium",
                    request_data
                )
                violations_found = True
        
        if not violations_found:
            self.compliant_endpoints += 1
    
    async def _validate_json_compliance(
        self,
        service_name: str,
        endpoint: str,
        response_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ):
        """Validate constitutional compliance in JSON response data."""
        violations_found = False
        
        # Check for constitutional hash in response body
        if isinstance(response_data, dict):
            body_hash = response_data.get("constitutional_hash")
            if body_hash != self.CONSTITUTIONAL_HASH:
                self._add_violation(
                    service_name, endpoint, "invalid_constitutional_hash_body",
                    f"Invalid constitutional hash in response body: expected {self.CONSTITUTIONAL_HASH}, got {body_hash}",
                    "critical", request_data, response_data
                )
                violations_found = True
            
            # Validate nested data structures
            if "data" in response_data:
                await self._validate_nested_compliance(
                    service_name, endpoint, response_data["data"], request_data, "data"
                )
        
        if violations_found:
            # Don't increment compliant_endpoints if violations found
            pass
    
    async def _validate_nested_compliance(
        self,
        service_name: str,
        endpoint: str,
        data: Any,
        request_data: Dict[str, Any],
        path: str
    ):
        """Validate constitutional compliance in nested data structures."""
        if isinstance(data, dict):
            # Check for constitutional hash in nested objects
            if "constitutional_hash" in data:
                nested_hash = data["constitutional_hash"]
                if nested_hash != self.CONSTITUTIONAL_HASH:
                    self._add_violation(
                        service_name, endpoint, "invalid_nested_constitutional_hash",
                        f"Invalid constitutional hash in nested data at {path}: expected {self.CONSTITUTIONAL_HASH}, got {nested_hash}",
                        "high", request_data, data
                    )
            
            # Recursively check nested objects
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    await self._validate_nested_compliance(
                        service_name, endpoint, value, request_data, f"{path}.{key}"
                    )
        
        elif isinstance(data, list):
            # Check each item in list
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    await self._validate_nested_compliance(
                        service_name, endpoint, item, request_data, f"{path}[{i}]"
                    )
    
    def _add_violation(
        self,
        service_name: str,
        endpoint: str,
        violation_type: str,
        description: str,
        severity: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        """Add a constitutional compliance violation."""
        violation = ComplianceViolation(
            service_name=service_name,
            endpoint=endpoint,
            violation_type=violation_type,
            description=description,
            severity=severity,
            timestamp=datetime.utcnow(),
            request_data=request_data,
            response_data=response_data
        )
        
        self.violations.append(violation)
        logger.warning(
            f"Constitutional compliance violation in {service_name}{endpoint}: "
            f"{violation_type} - {description}"
        )
    
    def _safe_json_parse(self, response: httpx.Response) -> Optional[Dict[str, Any]]:
        """Safely parse JSON response."""
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return None
    
    async def validate_all_acgs_services(
        self,
        service_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, ComplianceReport]:
        """Validate constitutional compliance across all ACGS services."""
        logger.info("Starting comprehensive ACGS constitutional compliance validation")
        
        reports = {}
        
        for service_name, config in service_configs.items():
            try:
                report = await self.validate_service_compliance(
                    service_name=service_name,
                    base_url=config["base_url"],
                    endpoints=config["endpoints"],
                    auth_headers=config.get("auth_headers")
                )
                reports[service_name] = report
                
            except Exception as e:
                logger.error(f"Failed to validate {service_name}: {str(e)}")
                # Create error report
                reports[service_name] = ComplianceReport(
                    total_endpoints_tested=0,
                    compliant_endpoints=0,
                    violations=[ComplianceViolation(
                        service_name=service_name,
                        endpoint="*",
                        violation_type="validation_failure",
                        description=f"Failed to validate service: {str(e)}",
                        severity="critical",
                        timestamp=datetime.utcnow()
                    )],
                    compliance_rate=0.0,
                    constitutional_hash=self.CONSTITUTIONAL_HASH,
                    test_timestamp=datetime.utcnow()
                )
        
        # Generate summary report
        total_endpoints = sum(r.total_endpoints_tested for r in reports.values())
        total_compliant = sum(r.compliant_endpoints for r in reports.values())
        overall_compliance = total_compliant / total_endpoints if total_endpoints > 0 else 0.0
        
        logger.info(
            f"ACGS constitutional compliance validation completed: "
            f"{overall_compliance:.2%} overall compliance "
            f"({total_compliant}/{total_endpoints} endpoints)"
        )
        
        return reports
    
    def generate_compliance_report_json(
        self, 
        reports: Dict[str, ComplianceReport]
    ) -> Dict[str, Any]:
        """Generate JSON compliance report."""
        return {
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "overall_compliance": {
                "total_services": len(reports),
                "total_endpoints": sum(r.total_endpoints_tested for r in reports.values()),
                "compliant_endpoints": sum(r.compliant_endpoints for r in reports.values()),
                "compliance_rate": sum(r.compliance_rate for r in reports.values()) / len(reports) if reports else 0.0,
                "fully_compliant_services": sum(1 for r in reports.values() if r.is_fully_compliant)
            },
            "service_reports": {
                service_name: {
                    "compliance_rate": report.compliance_rate,
                    "total_endpoints": report.total_endpoints_tested,
                    "compliant_endpoints": report.compliant_endpoints,
                    "violations_count": len(report.violations),
                    "is_fully_compliant": report.is_fully_compliant,
                    "violations": [
                        {
                            "endpoint": v.endpoint,
                            "type": v.violation_type,
                            "description": v.description,
                            "severity": v.severity,
                            "timestamp": v.timestamp.isoformat()
                        }
                        for v in report.violations
                    ]
                }
                for service_name, report in reports.items()
            }
        }
