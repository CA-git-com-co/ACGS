"""
ACGS-1 Constitutional Compliance Validator for Data Flywheel Integration

This module provides constitutional compliance validation for AI models
optimized through the Data Flywheel process, ensuring all governance
models maintain adherence to constitutional principles.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import httpx
import yaml
from pydantic import BaseModel


class ComplianceLevel(Enum):
    """Constitutional compliance levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles for governance"""

    DEMOCRATIC_PARTICIPATION = "democratic_participation"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    RULE_OF_LAW = "rule_of_law"
    HUMAN_RIGHTS = "human_rights"
    SUSTAINABILITY = "sustainability"
    PUBLIC_WELFARE = "public_welfare"
    EQUITY = "equity"
    PRIVACY_PROTECTION = "privacy_protection"
    DUE_PROCESS = "due_process"


@dataclass
class ComplianceResult:
    """Result of constitutional compliance validation"""

    principle: ConstitutionalPrinciple
    score: float
    level: ComplianceLevel
    explanation: str
    recommendations: List[str]
    timestamp: str


class GovernanceWorkflow(BaseModel):
    """Governance workflow definition"""

    name: str
    steps: List[str]
    compliance_required: bool
    validation_threshold: float


class ConstitutionalComplianceValidator:
    """
    Validates AI model outputs against constitutional principles
    and governance requirements for the ACGS-1 system.
    """

    def __init__(self, config_path: str = "config/acgs_config.yaml"):
        """Initialize the constitutional compliance validator"""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.acgs_base_url = self.config.get("acgs_config", {}).get(
            "base_url", "http://localhost"
        )
        self.constitutional_config = self.config.get("constitutional_config", {})
        self.compliance_threshold = self.constitutional_config.get(
            "compliance_threshold", 0.95
        )

        # Initialize ACGS-1 service clients
        self.ac_service_url = f"{self.acgs_base_url}:8001"
        self.fv_service_url = f"{self.acgs_base_url}:8003"
        self.gs_service_url = f"{self.acgs_base_url}:8004"
        self.pgc_service_url = f"{self.acgs_base_url}:8005"

    def _load_config(self, config_path: str) -> Dict:
        """Load ACGS-1 configuration"""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config from {config_path}: {e}")
            return {}

    async def validate_model_output(
        self,
        model_output: str,
        expected_output: str,
        governance_context: Dict,
        workload_id: str,
    ) -> List[ComplianceResult]:
        """
        Validate model output against constitutional principles

        Args:
            model_output: The output from the optimized model
            expected_output: The expected output from the original model
            governance_context: Context about the governance task
            workload_id: Identifier for the governance workload

        Returns:
            List of compliance results for each constitutional principle
        """
        self.logger.info(
            f"Validating constitutional compliance for workload: {workload_id}"
        )

        compliance_results = []
        principles = self.constitutional_config.get("principles", [])

        for principle_name in principles:
            try:
                principle = ConstitutionalPrinciple(principle_name)
                result = await self._validate_principle(
                    principle, model_output, expected_output, governance_context
                )
                compliance_results.append(result)
            except ValueError:
                self.logger.warning(
                    f"Unknown constitutional principle: {principle_name}"
                )
                continue

        # Overall compliance assessment
        overall_score = sum(r.score for r in compliance_results) / len(
            compliance_results
        )
        self.logger.info(
            f"Overall constitutional compliance score: {overall_score:.3f}"
        )

        if overall_score < self.compliance_threshold:
            self.logger.warning(
                f"Constitutional compliance below threshold: {overall_score:.3f} < {self.compliance_threshold}"
            )

        return compliance_results

    async def _validate_principle(
        self,
        principle: ConstitutionalPrinciple,
        model_output: str,
        expected_output: str,
        governance_context: Dict,
    ) -> ComplianceResult:
        """Validate a specific constitutional principle"""

        # Use AC Service for constitutional analysis
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ac_service_url}/api/v1/constitutional/validate",
                    json={
                        "principle": principle.value,
                        "model_output": model_output,
                        "expected_output": expected_output,
                        "governance_context": governance_context,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result_data = response.json()
                    return ComplianceResult(
                        principle=principle,
                        score=result_data.get("compliance_score", 0.0),
                        level=ComplianceLevel(
                            result_data.get("compliance_level", "low")
                        ),
                        explanation=result_data.get("explanation", ""),
                        recommendations=result_data.get("recommendations", []),
                        timestamp=result_data.get("timestamp", ""),
                    )
                else:
                    self.logger.error(
                        f"AC Service validation failed: {response.status_code}"
                    )

        except Exception as e:
            self.logger.error(f"Error validating principle {principle.value}: {e}")

        # Fallback to local validation
        return await self._local_principle_validation(
            principle, model_output, expected_output, governance_context
        )

    async def _local_principle_validation(
        self,
        principle: ConstitutionalPrinciple,
        model_output: str,
        expected_output: str,
        governance_context: Dict,
    ) -> ComplianceResult:
        """Local fallback validation for constitutional principles"""

        # Simple heuristic-based validation
        score = 0.8  # Default moderate compliance
        level = ComplianceLevel.MEDIUM
        explanation = f"Local validation for {principle.value}"
        recommendations = []

        # Principle-specific validation logic
        if principle == ConstitutionalPrinciple.TRANSPARENCY:
            # Check for transparency indicators
            transparency_keywords = [
                "explain",
                "because",
                "reason",
                "transparent",
                "clear",
            ]
            if any(
                keyword in model_output.lower() for keyword in transparency_keywords
            ):
                score += 0.1

        elif principle == ConstitutionalPrinciple.ACCOUNTABILITY:
            # Check for accountability indicators
            accountability_keywords = [
                "responsible",
                "accountable",
                "oversight",
                "review",
            ]
            if any(
                keyword in model_output.lower() for keyword in accountability_keywords
            ):
                score += 0.1

        elif principle == ConstitutionalPrinciple.HUMAN_RIGHTS:
            # Check for human rights considerations
            rights_keywords = ["rights", "dignity", "equality", "fairness", "justice"]
            if any(keyword in model_output.lower() for keyword in rights_keywords):
                score += 0.1

        # Determine compliance level
        if score >= 0.95:
            level = ComplianceLevel.CRITICAL
        elif score >= 0.85:
            level = ComplianceLevel.HIGH
        elif score >= 0.70:
            level = ComplianceLevel.MEDIUM
        else:
            level = ComplianceLevel.LOW
            recommendations.append(
                f"Improve {principle.value} compliance in model output"
            )

        return ComplianceResult(
            principle=principle,
            score=min(score, 1.0),
            level=level,
            explanation=explanation,
            recommendations=recommendations,
            timestamp="",
        )

    async def validate_governance_workflow(
        self, workflow_name: str, model_outputs: List[str], workflow_context: Dict
    ) -> Dict[str, float]:
        """
        Validate model outputs against governance workflow requirements

        Args:
            workflow_name: Name of the governance workflow
            model_outputs: List of model outputs for each workflow step
            workflow_context: Context about the workflow execution

        Returns:
            Dictionary of validation scores for each workflow step
        """
        self.logger.info(f"Validating governance workflow: {workflow_name}")

        workflows = self.constitutional_config.get("workflows", {})
        workflow_config = workflows.get(workflow_name, {})

        if not workflow_config.get("enabled", False):
            self.logger.warning(
                f"Workflow {workflow_name} is not enabled for validation"
            )
            return {}

        validation_scores = {}
        workflow_steps = workflow_config.get("validation_steps", [])

        for i, (step, output) in enumerate(zip(workflow_steps, model_outputs)):
            try:
                # Use PGC Service for workflow validation
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.pgc_service_url}/api/v1/workflow/validate",
                        json={
                            "workflow_name": workflow_name,
                            "step_name": step,
                            "model_output": output,
                            "workflow_context": workflow_context,
                        },
                        timeout=30.0,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        validation_scores[step] = result.get("validation_score", 0.0)
                    else:
                        self.logger.error(
                            f"PGC Service validation failed for step {step}"
                        )
                        validation_scores[step] = 0.5  # Default moderate score

            except Exception as e:
                self.logger.error(f"Error validating workflow step {step}: {e}")
                validation_scores[step] = 0.5

        return validation_scores

    async def check_acgs_service_health(self) -> Dict[str, bool]:
        """Check health of ACGS-1 services required for validation"""
        services = self.config.get("acgs_config", {}).get("services", {})
        health_status = {}

        for service_name, service_config in services.items():
            if not service_config.get("required", False):
                continue

            port = service_config.get("port")
            endpoint = service_config.get("endpoint", "/health")
            url = f"{self.acgs_base_url}:{port}{endpoint}"

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    health_status[service_name] = response.status_code == 200
            except Exception as e:
                self.logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False

        return health_status

    def get_compliance_summary(
        self, compliance_results: List[ComplianceResult]
    ) -> Dict:
        """Generate a summary of constitutional compliance results"""
        if not compliance_results:
            return {"overall_score": 0.0, "compliant": False, "summary": "No results"}

        overall_score = sum(r.score for r in compliance_results) / len(
            compliance_results
        )
        compliant = overall_score >= self.compliance_threshold

        principle_scores = {r.principle.value: r.score for r in compliance_results}
        low_compliance = [
            r.principle.value for r in compliance_results if r.score < 0.7
        ]

        return {
            "overall_score": overall_score,
            "compliant": compliant,
            "threshold": self.compliance_threshold,
            "principle_scores": principle_scores,
            "low_compliance_principles": low_compliance,
            "total_principles_evaluated": len(compliance_results),
            "summary": f"Constitutional compliance: {overall_score:.1%}",
        }
