"""
Constitutional Validators for ACGS-1 Lite Integration
Provides constitutional compliance validation through Policy Engine integration.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import aioredis

logger = logging.getLogger(__name__)


class ACGSConstitutionalValidator:
    """Constitutional compliance validator integrated with ACGS-1 Policy Engine."""

    def __init__(self, config):
        self.config = config
        self.policy_engine_url = config.policy_engine_url
        self.audit_engine_url = config.audit_engine_url
        self.constitutional_hash = config.constitutional_hash

        # Cache for policy evaluations
        self.redis_client = None
        self.cache_ttl = 300  # 5 minutes

        # Validation metrics
        self.validation_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

        # Constitutional principles for local validation
        self.constitutional_principles = {
            "harmlessness": {
                "weight": 0.3,
                "keywords": ["harmful", "dangerous", "illegal", "unethical", "violence"],
                "threshold": 0.1,
            },
            "helpfulness": {
                "weight": 0.25,
                "keywords": ["helpful", "informative", "accurate", "useful"],
                "threshold": 0.7,
            },
            "honesty": {
                "weight": 0.25,
                "keywords": ["truthful", "accurate", "factual", "honest"],
                "threshold": 0.7,
            },
            "privacy": {
                "weight": 0.2,
                "keywords": ["private", "confidential", "personal", "sensitive"],
                "threshold": 0.8,
            },
        }

    async def initialize(self):
        """Initialize async components."""
        try:
            # Initialize Redis connection for caching
            redis_url = getattr(self.config, "redis_url", "redis://redis:6379/0")
            self.redis_client = await aioredis.from_url(redis_url)
            logger.info("Constitutional validator initialized with Redis caching")
        except Exception as e:
            logger.warning(f"Redis initialization failed, proceeding without cache: {e}")
            self.redis_client = None

    async def validate_response(
        self, response: str, context: Dict[str, Any]
    ) -> Tuple[bool, float, List[str]]:
        """
        Validate response against constitutional principles.

        Returns:
            Tuple of (is_compliant, confidence_score, violations)
        """
        start_time = time.time()
        evaluation_id = self._generate_evaluation_id(response, context)

        try:
            # Check cache first
            cached_result = await self._get_cached_result(evaluation_id)
            if cached_result:
                self.cache_hits += 1
                return cached_result

            # Cache miss - perform validation
            self.cache_misses += 1

            # Multi-layer validation approach
            policy_result = await self._validate_with_policy_engine(
                response, context, evaluation_id
            )
            local_result = await self._validate_locally(response, context)

            # Combine results with weighted scoring
            combined_score = (
                policy_result["confidence_score"] * 0.7 + local_result["confidence_score"] * 0.3
            )

            # Determine compliance based on threshold
            is_compliant = (
                policy_result["allow"] and combined_score >= self.config.compliance_threshold
            )

            # Combine violations
            violations = list(
                set(policy_result.get("violations", []) + local_result.get("violations", []))
            )

            result = (is_compliant, combined_score, violations)

            # Cache the result
            await self._cache_result(evaluation_id, result)

            # Update metrics
            self.validation_count += 1

            # Log validation to Audit Engine
            await self._log_validation(response, context, combined_score, violations, evaluation_id)

            validation_time = time.time() - start_time
            logger.debug(
                f"Constitutional validation completed in {validation_time:.3f}s: "
                f"compliant={is_compliant}, score={combined_score:.3f}"
            )

            return result

        except Exception as e:
            logger.error(f"Constitutional validation failed: {e}")
            # Return safe default (non-compliant)
            return False, 0.0, ["validation_error"]

    async def _validate_with_policy_engine(
        self, response: str, context: Dict[str, Any], evaluation_id: str
    ) -> Dict[str, Any]:
        """Validate response using ACGS-1 Policy Engine."""

        policy_request = {
            "action": "constitutional_evaluation",
            "content": response,
            "context": context,
            "constitutional_hash": self.constitutional_hash,
            "evaluation_id": evaluation_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            timeout = aiohttp.ClientTimeout(total=5.0)  # 5 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.policy_engine_url}/api/v1/evaluate",
                    json=policy_request,
                    headers={
                        "Content-Type": "application/json",
                        "X-Constitutional-Hash": self.constitutional_hash,
                    },
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"Policy Engine request failed: {resp.status}")
                        return self._get_default_policy_result()

                    result = await resp.json()

                    # Validate response structure
                    if not self._validate_policy_response(result):
                        logger.error("Invalid Policy Engine response structure")
                        return self._get_default_policy_result()

                    return result

        except asyncio.TimeoutError:
            logger.error("Policy Engine request timed out")
            return self._get_default_policy_result()
        except Exception as e:
            logger.error(f"Policy Engine validation failed: {e}")
            return self._get_default_policy_result()

    async def _validate_locally(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform local constitutional validation as backup."""

        violations = []
        principle_scores = {}

        response_lower = response.lower()

        for principle, config in self.constitutional_principles.items():
            score = await self._evaluate_principle(response_lower, principle, config)
            principle_scores[principle] = score

            if score < config["threshold"]:
                violations.append(f"{principle}_violation")

        # Calculate weighted overall score
        overall_score = sum(
            score * self.constitutional_principles[principle]["weight"]
            for principle, score in principle_scores.items()
        )

        return {
            "allow": overall_score >= self.config.compliance_threshold,
            "confidence_score": overall_score,
            "violations": violations,
            "principle_scores": principle_scores,
            "validation_method": "local",
        }

    async def _evaluate_principle(self, response: str, principle: str, config: Dict) -> float:
        """Evaluate a specific constitutional principle."""

        keywords = config["keywords"]

        if principle == "harmlessness":
            # For harmlessness, presence of harmful keywords reduces score
            harmful_count = sum(1 for keyword in keywords if keyword in response)
            return max(0.0, 1.0 - (harmful_count * 0.2))

        elif principle in ["helpfulness", "honesty"]:
            # For helpfulness and honesty, presence of positive keywords increases score
            positive_count = sum(1 for keyword in keywords if keyword in response)
            return min(1.0, positive_count * 0.25)

        elif principle == "privacy":
            # For privacy, check for potential privacy violations
            privacy_keywords = ["personal", "private", "confidential", "ssn", "credit card"]
            privacy_violations = sum(1 for keyword in privacy_keywords if keyword in response)
            return max(0.0, 1.0 - (privacy_violations * 0.3))

        return 0.5  # Default neutral score

    def _validate_policy_response(self, response: Dict[str, Any]) -> bool:
        """Validate Policy Engine response structure."""
        required_fields = ["allow", "confidence_score"]
        return all(field in response for field in required_fields)

    def _get_default_policy_result(self) -> Dict[str, Any]:
        """Get default policy result for fallback scenarios."""
        return {
            "allow": False,
            "confidence_score": 0.0,
            "violations": ["policy_engine_unavailable"],
            "reason": "Policy Engine validation failed",
            "validation_method": "fallback",
        }

    def _generate_evaluation_id(self, response: str, context: Dict[str, Any]) -> str:
        """Generate unique evaluation ID for caching."""
        content = f"{response}:{json.dumps(context, sort_keys=True)}:{self.constitutional_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def _get_cached_result(
        self, evaluation_id: str
    ) -> Optional[Tuple[bool, float, List[str]]]:
        """Get cached validation result."""
        if not self.redis_client:
            return None

        try:
            cached_data = await self.redis_client.get(f"constitutional_validation:{evaluation_id}")
            if cached_data:
                result = json.loads(cached_data)
                return (result["is_compliant"], result["confidence_score"], result["violations"])
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")

        return None

    async def _cache_result(self, evaluation_id: str, result: Tuple[bool, float, List[str]]):
        """Cache validation result."""
        if not self.redis_client:
            return

        try:
            cache_data = {
                "is_compliant": result[0],
                "confidence_score": result[1],
                "violations": result[2],
                "cached_at": datetime.utcnow().isoformat(),
            }

            await self.redis_client.setex(
                f"constitutional_validation:{evaluation_id}", self.cache_ttl, json.dumps(cache_data)
            )
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")

    async def _log_validation(
        self,
        response: str,
        context: Dict[str, Any],
        score: float,
        violations: List[str],
        evaluation_id: str,
    ):
        """Log validation results to Audit Engine."""

        audit_event = {
            "event_type": "constitutional_validation",
            "constitutional_hash": self.constitutional_hash,
            "evaluation_id": evaluation_id,
            "compliance_score": score,
            "violations": violations,
            "context": context,
            "response_length": len(response),
            "validation_timestamp": datetime.utcnow().isoformat(),
            "validator_version": "1.0.0",
        }

        try:
            timeout = aiohttp.ClientTimeout(total=3.0)  # 3 second timeout for audit
            async with aiohttp.ClientSession(timeout=timeout) as session:
                await session.post(
                    f"{self.audit_engine_url}/api/v1/log",
                    json=audit_event,
                    headers={
                        "Content-Type": "application/json",
                        "X-Constitutional-Hash": self.constitutional_hash,
                    },
                )
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

    async def batch_validate(
        self, responses: List[str], contexts: List[Dict[str, Any]]
    ) -> List[Tuple[bool, float, List[str]]]:
        """Batch validate multiple responses for efficiency."""

        if len(responses) != len(contexts):
            raise ValueError("Responses and contexts must have the same length")

        # Create validation tasks
        tasks = [
            self.validate_response(response, context)
            for response, context in zip(responses, contexts)
        ]

        # Execute validations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch validation failed for item {i}: {result}")
                processed_results.append((False, 0.0, ["batch_validation_error"]))
            else:
                processed_results.append(result)

        return processed_results

    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation performance metrics."""
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            "total_validations": self.validation_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "constitutional_hash": self.constitutional_hash,
            "compliance_threshold": self.config.compliance_threshold,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of validation components."""
        health_status = {
            "validator_status": "healthy",
            "policy_engine_status": "unknown",
            "audit_engine_status": "unknown",
            "redis_status": "unknown",
            "constitutional_hash": self.constitutional_hash,
        }

        # Check Policy Engine
        try:
            timeout = aiohttp.ClientTimeout(total=2.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.policy_engine_url}/health") as resp:
                    health_status["policy_engine_status"] = (
                        "healthy" if resp.status == 200 else "unhealthy"
                    )
        except Exception:
            health_status["policy_engine_status"] = "unhealthy"

        # Check Audit Engine
        try:
            timeout = aiohttp.ClientTimeout(total=2.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.audit_engine_url}/health") as resp:
                    health_status["audit_engine_status"] = (
                        "healthy" if resp.status == 200 else "unhealthy"
                    )
        except Exception:
            health_status["audit_engine_status"] = "unhealthy"

        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["redis_status"] = "healthy"
            except Exception:
                health_status["redis_status"] = "unhealthy"
        else:
            health_status["redis_status"] = "disabled"

        return health_status

    async def cleanup(self):
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Constitutional validator cleanup completed")
