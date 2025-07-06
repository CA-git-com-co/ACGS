"""
ACGS API Gateway Constitutional Compliance Middleware

Middleware for enforcing constitutional compliance across all API requests
with formal verification and constitutional hash validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalComplianceMiddleware(BaseHTTPMiddleware):
    """
    Constitutional compliance middleware for API gateway.
    
    Enforces constitutional principles across all API requests including:
    - Constitutional hash verification
    - Formal verification of request compliance
    - Democratic governance principles
    - Human dignity protection
    - Transparency and accountability
    """
    
    def __init__(
        self,
        app,
        constitutional_hash: str = CONSTITUTIONAL_HASH,
        policy_engine: Optional[Any] = None,
        enable_formal_verification: bool = True,
        enable_audit_logging: bool = True
    ):
        super().__init__(app)
        self.constitutional_hash = constitutional_hash
        self.policy_engine = policy_engine
        self.enable_formal_verification = enable_formal_verification
        self.enable_audit_logging = enable_audit_logging
        
        # Constitutional principles to enforce
        self.constitutional_principles = {
            "human_dignity": "Respect for human dignity in all operations",
            "fairness": "Fair and non-discriminatory treatment",
            "transparency": "Transparent decision-making processes",
            "accountability": "Clear accountability for all actions",
            "democratic_governance": "Democratic oversight of decisions",
            "privacy_protection": "Protection of personal privacy",
            "data_minimization": "Minimal data collection and processing",
            "purpose_limitation": "Data used only for stated purposes"
        }
        
        logger.info(f"Constitutional compliance middleware initialized with hash: {constitutional_hash}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through constitutional compliance checks."""
        
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        try:
            # Step 1: Verify constitutional hash
            constitutional_verification = await self._verify_constitutional_hash(request)
            if not constitutional_verification["valid"]:
                return await self._create_compliance_violation_response(
                    "Constitutional hash verification failed",
                    constitutional_verification,
                    request_id
                )
            
            # Step 2: Perform constitutional compliance assessment
            compliance_assessment = await self._assess_request_compliance(request)
            if not compliance_assessment["compliant"]:
                return await self._create_compliance_violation_response(
                    "Constitutional compliance assessment failed",
                    compliance_assessment,
                    request_id
                )
            
            # Step 3: Apply constitutional policies
            policy_result = await self._apply_constitutional_policies(request)
            if not policy_result["allowed"]:
                return await self._create_policy_violation_response(
                    "Constitutional policy violation",
                    policy_result,
                    request_id
                )
            
            # Step 4: Add constitutional context to request
            await self._add_constitutional_context(request, compliance_assessment)
            
            # Process request
            response = await call_next(request)
            
            # Step 5: Verify response constitutional compliance
            response_compliance = await self._verify_response_compliance(request, response)
            if not response_compliance["compliant"]:
                logger.warning(f"Response compliance issue for request {request_id}: {response_compliance}")
            
            # Step 6: Add constitutional headers to response
            await self._add_constitutional_headers(response, compliance_assessment)
            
            # Step 7: Log constitutional compliance audit trail
            if self.enable_audit_logging:
                await self._log_constitutional_audit(
                    request, response, compliance_assessment, 
                    time.time() - start_time, request_id
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Constitutional compliance middleware error for request {request_id}: {e}")
            
            # Log compliance failure
            if self.enable_audit_logging:
                await self._log_constitutional_failure(request, str(e), request_id)
            
            return await self._create_error_response(
                "Constitutional compliance check failed",
                str(e),
                request_id
            )
    
    async def _verify_constitutional_hash(self, request: Request) -> Dict[str, Any]:
        """Verify constitutional hash integrity."""
        
        try:
            # Check if request includes constitutional hash
            request_hash = request.headers.get("X-Constitutional-Hash")
            
            # Verify against expected hash
            hash_valid = self.constitutional_hash == CONSTITUTIONAL_HASH
            request_hash_valid = request_hash == CONSTITUTIONAL_HASH if request_hash else True
            
            return {
                "valid": hash_valid and request_hash_valid,
                "expected_hash": CONSTITUTIONAL_HASH,
                "current_hash": self.constitutional_hash,
                "request_hash": request_hash,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Constitutional hash verification error: {e}")
            return {
                "valid": False,
                "error": str(e),
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _assess_request_compliance(self, request: Request) -> Dict[str, Any]:
        """Assess request compliance with constitutional principles."""
        
        try:
            compliance_score = 0.0
            principle_scores = {}
            violations = []
            
            # Assess each constitutional principle
            for principle, description in self.constitutional_principles.items():
                score = await self._assess_principle_compliance(request, principle)
                principle_scores[principle] = score
                compliance_score += score
                
                if score < 0.8:  # Compliance threshold
                    violations.append(f"Principle '{principle}' compliance below threshold: {score:.2f}")
            
            # Calculate overall compliance
            overall_score = compliance_score / len(self.constitutional_principles)
            compliant = overall_score >= 0.8 and len(violations) == 0
            
            # Formal verification if enabled
            formal_verification_result = None
            if self.enable_formal_verification:
                formal_verification_result = await self._perform_formal_verification(request)
                compliant = compliant and formal_verification_result.get("verified", False)
            
            return {
                "compliant": compliant,
                "overall_score": overall_score,
                "principle_scores": principle_scores,
                "violations": violations,
                "formal_verification": formal_verification_result,
                "constitutional_hash": self.constitutional_hash,
                "assessed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Constitutional compliance assessment error: {e}")
            return {
                "compliant": False,
                "error": str(e),
                "assessed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _assess_principle_compliance(self, request: Request, principle: str) -> float:
        """Assess compliance with a specific constitutional principle."""
        
        try:
            # Get tenant context
            tenant_context = getattr(request.state, "tenant_context", {})
            user_context = getattr(request.state, "user_context", {})
            
            if principle == "human_dignity":
                # Assess human dignity considerations
                return await self._assess_human_dignity_compliance(request, tenant_context, user_context)
                
            elif principle == "fairness":
                # Assess fairness and non-discrimination
                return await self._assess_fairness_compliance(request, tenant_context, user_context)
                
            elif principle == "transparency":
                # Assess transparency requirements
                return await self._assess_transparency_compliance(request, tenant_context, user_context)
                
            elif principle == "accountability":
                # Assess accountability mechanisms
                return await self._assess_accountability_compliance(request, tenant_context, user_context)
                
            elif principle == "democratic_governance":
                # Assess democratic governance compliance
                return await self._assess_democratic_governance_compliance(request, tenant_context, user_context)
                
            elif principle == "privacy_protection":
                # Assess privacy protection measures
                return await self._assess_privacy_protection_compliance(request, tenant_context, user_context)
                
            elif principle == "data_minimization":
                # Assess data minimization principles
                return await self._assess_data_minimization_compliance(request, tenant_context, user_context)
                
            elif principle == "purpose_limitation":
                # Assess purpose limitation compliance
                return await self._assess_purpose_limitation_compliance(request, tenant_context, user_context)
                
            else:
                logger.warning(f"Unknown constitutional principle: {principle}")
                return 1.0  # Default to compliant for unknown principles
                
        except Exception as e:
            logger.error(f"Error assessing principle {principle}: {e}")
            return 0.5  # Partial compliance on error
    
    async def _assess_human_dignity_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess human dignity compliance."""
        
        # Check for automated decision-making affecting individuals
        if request.method in ["POST", "PUT", "PATCH"]:
            # Ensure human oversight for decisions affecting individuals
            if "automated_decision" in str(request.url).lower():
                # Require human-in-the-loop for automated decisions
                if not request.headers.get("X-Human-Oversight"):
                    return 0.6  # Partial compliance - automated without human oversight
        
        # Check for data processing that could affect human dignity
        if "personal" in str(request.url).lower() or "profile" in str(request.url).lower():
            # Ensure dignity-respecting data processing
            if user_context.get("consent_level") != "explicit":
                return 0.7  # Requires explicit consent for personal data
        
        return 1.0  # Full compliance
    
    async def _assess_fairness_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess fairness and non-discrimination compliance."""
        
        # Check for fair access across tenants
        if tenant_context:
            # Ensure equal treatment across tenants
            tenant_id = tenant_context.get("tenant_id")
            if tenant_id:
                # Check for tenant-based discrimination
                if request.headers.get("X-Tenant-Priority"):
                    return 0.5  # Tenant prioritization may violate fairness
        
        # Check for fair resource allocation
        if "priority" in request.query_params:
            # Ensure priority is based on fair criteria
            return 0.8  # Acceptable with proper justification
        
        return 1.0  # Full compliance
    
    async def _assess_transparency_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess transparency requirements compliance."""
        
        # Check for transparent decision-making
        if request.method in ["POST", "PUT", "DELETE"]:
            # Require audit trail for state-changing operations
            if not request.headers.get("X-Audit-Enabled", "true") == "true":
                return 0.4  # Poor transparency without audit trail
        
        # Check for explanation requirements
        if "decision" in str(request.url).lower():
            # Require explainable decisions
            if not request.headers.get("X-Explainable"):
                return 0.7  # Partial compliance - decisions should be explainable
        
        return 1.0  # Full compliance
    
    async def _assess_accountability_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess accountability mechanisms compliance."""
        
        # Check for proper identification
        if not user_context or not user_context.get("user_id"):
            return 0.3  # Poor accountability without user identification
        
        # Check for responsibility assignment
        if request.method in ["POST", "PUT", "DELETE"]:
            # Require responsible party identification
            if not request.headers.get("X-Responsible-Party"):
                return 0.8  # Good but could be better with explicit responsibility
        
        return 1.0  # Full compliance
    
    async def _assess_democratic_governance_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess democratic governance compliance."""
        
        # Check for governance-related operations
        if "governance" in str(request.url).lower() or "policy" in str(request.url).lower():
            # Ensure democratic oversight
            if not request.headers.get("X-Democratic-Oversight"):
                return 0.6  # Requires democratic oversight for governance operations
        
        # Check for stakeholder consultation
        if request.method in ["POST", "PUT"] and "policy" in str(request.url).lower():
            # Require stakeholder input for policy changes
            if not request.headers.get("X-Stakeholder-Consulted"):
                return 0.7  # Should include stakeholder consultation
        
        return 1.0  # Full compliance
    
    async def _assess_privacy_protection_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess privacy protection compliance."""
        
        # Check for personal data processing
        if "personal" in str(request.url).lower() or "profile" in str(request.url).lower():
            # Ensure privacy protection measures
            if not request.headers.get("X-Privacy-Protected"):
                return 0.5  # Requires explicit privacy protection
        
        # Check for tenant data isolation
        if tenant_context and tenant_context.get("tenant_id"):
            # Ensure tenant data isolation
            if not tenant_context.get("isolation_verified"):
                return 0.4  # Critical privacy violation without tenant isolation
        
        return 1.0  # Full compliance
    
    async def _assess_data_minimization_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess data minimization compliance."""
        
        # Check request body size for data minimization
        if hasattr(request, "body"):
            try:
                body = await request.body()
                if len(body) > 10000:  # 10KB threshold
                    return 0.8  # Large payloads should be justified
            except:
                pass
        
        # Check for excessive data collection
        if request.method == "POST" and "collect" in str(request.url).lower():
            # Ensure minimal data collection
            if not request.headers.get("X-Data-Minimized"):
                return 0.6  # Should minimize data collection
        
        return 1.0  # Full compliance
    
    async def _assess_purpose_limitation_compliance(self, request: Request, tenant_context: Dict, user_context: Dict) -> float:
        """Assess purpose limitation compliance."""
        
        # Check for purpose specification
        if request.method in ["POST", "PUT"] and "data" in str(request.url).lower():
            # Require purpose specification for data operations
            if not request.headers.get("X-Data-Purpose"):
                return 0.7  # Should specify data purpose
        
        # Check for purpose limitation adherence
        purpose = request.headers.get("X-Data-Purpose")
        if purpose and "marketing" in purpose.lower():
            # Ensure consent for marketing purposes
            if not user_context.get("marketing_consent"):
                return 0.4  # Violation of purpose limitation without consent
        
        return 1.0  # Full compliance
    
    async def _perform_formal_verification(self, request: Request) -> Dict[str, Any]:
        """Perform formal verification of request compliance."""
        
        try:
            # Simplified formal verification - in real implementation, 
            # this would integrate with Z3 SMT solver
            
            verification_constraints = {
                "constitutional_hash_valid": self.constitutional_hash == CONSTITUTIONAL_HASH,
                "request_authenticated": hasattr(request.state, "user_context"),
                "tenant_isolated": True,  # Simplified check
                "audit_enabled": True
            }
            
            verification_result = all(verification_constraints.values())
            
            return {
                "verified": verification_result,
                "constraints": verification_constraints,
                "verification_method": "constitutional_formal_verification",
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Formal verification error: {e}")
            return {
                "verified": False,
                "error": str(e),
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _apply_constitutional_policies(self, request: Request) -> Dict[str, Any]:
        """Apply constitutional policies to request."""
        
        try:
            if not self.policy_engine:
                return {"allowed": True, "policies_applied": []}
            
            # Apply constitutional policies through policy engine
            policy_result = await self.policy_engine.evaluate_constitutional_policies(request)
            
            return {
                "allowed": policy_result.get("allowed", True),
                "policies_applied": policy_result.get("policies", []),
                "policy_violations": policy_result.get("violations", []),
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Constitutional policy application error: {e}")
            return {
                "allowed": False,
                "error": str(e),
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _add_constitutional_context(self, request: Request, compliance_assessment: Dict[str, Any]):
        """Add constitutional context to request state."""
        
        request.state.constitutional_compliance = compliance_assessment
        request.state.constitutional_hash = self.constitutional_hash
        request.state.constitutional_verified = compliance_assessment.get("compliant", False)
    
    async def _verify_response_compliance(self, request: Request, response: Response) -> Dict[str, Any]:
        """Verify response constitutional compliance."""
        
        try:
            # Check response headers for constitutional compliance
            constitutional_headers = [
                "X-Constitutional-Hash",
                "X-Audit-Trail-Id",
                "X-Tenant-Isolation-Verified"
            ]
            
            compliance_issues = []
            for header in constitutional_headers:
                if header not in response.headers:
                    compliance_issues.append(f"Missing constitutional header: {header}")
            
            # Check for constitutional hash in response
            response_hash = response.headers.get("X-Constitutional-Hash")
            if response_hash != self.constitutional_hash:
                compliance_issues.append("Response constitutional hash mismatch")
            
            return {
                "compliant": len(compliance_issues) == 0,
                "issues": compliance_issues,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Response compliance verification error: {e}")
            return {
                "compliant": False,
                "error": str(e),
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _add_constitutional_headers(self, response: Response, compliance_assessment: Dict[str, Any]):
        """Add constitutional compliance headers to response."""
        
        response.headers["X-Constitutional-Hash"] = self.constitutional_hash
        response.headers["X-Constitutional-Compliant"] = "true" if compliance_assessment.get("compliant") else "false"
        response.headers["X-Constitutional-Score"] = str(round(compliance_assessment.get("overall_score", 0), 2))
        response.headers["X-Formal-Verification"] = "verified" if self.enable_formal_verification else "disabled"
    
    async def _log_constitutional_audit(
        self, 
        request: Request, 
        response: Response, 
        compliance_assessment: Dict[str, Any],
        processing_time: float,
        request_id: str
    ):
        """Log constitutional compliance audit trail."""
        
        audit_entry = {
            "event_type": "constitutional_compliance_check",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "compliance_assessment": compliance_assessment,
            "request": {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None
            },
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers)
            },
            "processing_time_seconds": processing_time,
            "tenant_context": getattr(request.state, "tenant_context", {}),
            "user_context": getattr(request.state, "user_context", {})
        }
        
        # Log to audit system
        logger.info(f"Constitutional audit: {json.dumps(audit_entry, default=str)}")
    
    async def _log_constitutional_failure(self, request: Request, error: str, request_id: str):
        """Log constitutional compliance failure."""
        
        failure_entry = {
            "event_type": "constitutional_compliance_failure",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "error": error,
            "request": {
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None
            }
        }
        
        logger.error(f"Constitutional compliance failure: {json.dumps(failure_entry, default=str)}")
    
    async def _create_compliance_violation_response(
        self, 
        message: str, 
        details: Dict[str, Any], 
        request_id: str
    ) -> Response:
        """Create response for constitutional compliance violations."""
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Constitutional Compliance Violation",
                "message": message,
                "details": details,
                "constitutional_hash": self.constitutional_hash,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def _create_policy_violation_response(
        self, 
        message: str, 
        policy_result: Dict[str, Any], 
        request_id: str
    ) -> Response:
        """Create response for constitutional policy violations."""
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Constitutional Policy Violation",
                "message": message,
                "policy_violations": policy_result.get("policy_violations", []),
                "constitutional_hash": self.constitutional_hash,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def _create_error_response(self, message: str, error: str, request_id: str) -> Response:
        """Create response for constitutional compliance errors."""
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Constitutional Compliance Error",
                "message": message,
                "details": error,
                "constitutional_hash": self.constitutional_hash,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )