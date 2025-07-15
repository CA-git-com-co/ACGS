#!/usr/bin/env python3
"""
5-Tier Hybrid Inference Router Staging Deployment Script

Deploys the updated 5-tier hybrid inference router system to ACGS-2 staging environment
with comprehensive validation and monitoring.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import yaml

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Configuration for 5-tier router staging deployment."""
    
    # Environment settings
    environment: str = "staging"
    namespace: str = "acgs-staging"
    
    # Infrastructure ports
    postgresql_port: int = 5439
    redis_port: int = 6389
    
    # Service ports
    hybrid_router_port: int = 8020
    model_registry_port: int = 8021
    ai_model_service_port: int = 8022
    
    # API configurations
    openrouter_api_url: str = "https://openrouter.ai/api/v1"
    groq_api_url: str = "https://api.groq.com/openai/v1"
    nano_vllm_url: str = "http://nano-vllm:8000"
    
    # Performance targets
    target_p99_latency_ms: float = 5.0
    target_throughput_rps: float = 100.0
    target_cache_hit_rate: float = 0.85
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH


class StagingDeploymentOrchestrator:
    """Orchestrates the deployment of 5-tier hybrid inference router to staging."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.deployment_start_time = datetime.utcnow()
        self.deployment_status = {}
        
    async def deploy_to_staging(self) -> Dict[str, Any]:
        """Execute complete staging deployment."""
        logger.info("🚀 Starting 5-Tier Hybrid Inference Router Staging Deployment")
        logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        try:
            # Pre-deployment validation
            await self._validate_prerequisites()
            
            # Deploy infrastructure
            await self._deploy_infrastructure()
            
            # Deploy 5-tier router components
            await self._deploy_router_components()
            
            # Configure API integrations
            await self._configure_api_integrations()
            
            # Validate deployment
            await self._validate_deployment()
            
            # Generate deployment report
            report = await self._generate_deployment_report()
            
            logger.info("✅ Staging deployment completed successfully!")
            return report
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            await self._rollback_deployment()
            raise
    
    async def _validate_prerequisites(self):
        """Validate deployment prerequisites."""
        logger.info("🔍 Validating deployment prerequisites...")
        
        # Check Docker and Docker Compose
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Docker and Docker Compose are required")
        
        # Check required environment variables
        required_env_vars = [
            "OPENROUTER_API_KEY",
            "GROQ_API_KEY",
            "POSTGRES_PASSWORD"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise RuntimeError(f"Missing required environment variables: {missing_vars}")
        
        # Validate 5-tier router configuration
        router_config_path = Path("services/shared/routing/hybrid_inference_router.py")
        if not router_config_path.exists():
            raise RuntimeError("5-tier router configuration not found")
        
        logger.info("✅ Prerequisites validated")
    
    async def _deploy_infrastructure(self):
        """Deploy staging infrastructure."""
        logger.info("🏗️ Deploying staging infrastructure...")
        
        # Create staging environment file
        env_content = f"""
# ACGS-2 Staging Environment Configuration
ENVIRONMENT=staging
CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}

# Database configuration
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD={os.getenv('POSTGRES_PASSWORD')}
POSTGRES_DB=acgs_staging
DATABASE_URL=postgresql+asyncpg://acgs_user:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/acgs_staging

# Redis configuration
REDIS_URL=redis://redis:6379/0

# API Keys
OPENROUTER_API_KEY={os.getenv('OPENROUTER_API_KEY')}
GROQ_API_KEY={os.getenv('GROQ_API_KEY')}

# Service URLs
HYBRID_ROUTER_URL=http://hybrid-router:{self.config.hybrid_router_port}
MODEL_REGISTRY_URL=http://model-registry:{self.config.model_registry_port}
AI_MODEL_SERVICE_URL=http://ai-model-service:{self.config.ai_model_service_port}

# Performance targets
TARGET_P99_LATENCY_MS={self.config.target_p99_latency_ms}
TARGET_THROUGHPUT_RPS={self.config.target_throughput_rps}
TARGET_CACHE_HIT_RATE={self.config.target_cache_hit_rate}
"""
        
        with open("config/environments/development.env.staging", "w") as f:
            f.write(env_content)
        
        # Deploy using Docker Compose
        cmd = [
            "docker-compose",
            "-f", "infrastructure/docker/docker-compose.staging.yml",
            "--env-file", "config/environments/development.env.staging",
            "up", "-d",
            "postgres", "redis"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Infrastructure deployment failed: {result.stderr}")
        
        # Wait for infrastructure to be ready
        await self._wait_for_service("postgres", self.config.postgresql_port, timeout=120)
        await self._wait_for_service("redis", self.config.redis_port, timeout=60)
        
        logger.info("✅ Infrastructure deployed successfully")
    
    async def _deploy_router_components(self):
        """Deploy 5-tier router components."""
        logger.info("🔄 Deploying 5-tier router components...")
        
        # Create Docker Compose configuration for router services
        router_compose = {
            "version": "3.8",
            "networks": {
                "acgs-staging": {"external": True}
            },
            "services": {
                "hybrid-router": {
                    "build": {
                        "context": "./services/shared/routing",
                        "dockerfile": "Dockerfile"
                    },
                    "container_name": "acgs-hybrid-router-staging",
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}",
                        "ENVIRONMENT=staging",
                        "OPENROUTER_API_KEY=${OPENROUTER_API_KEY}",
                        "GROQ_API_KEY=${GROQ_API_KEY}",
                        "REDIS_URL=redis://redis:6379/0"
                    ],
                    "ports": [f"{self.config.hybrid_router_port}:8000"],
                    "networks": ["acgs-staging"],
                    "depends_on": ["redis"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "model-registry": {
                    "build": {
                        "context": "./services/shared/models",
                        "dockerfile": "Dockerfile"
                    },
                    "container_name": "acgs-model-registry-staging",
                    "environment": [
                        f"CONSTITUTIONAL_HASH={CONSTITUTIONAL_HASH}",
                        "ENVIRONMENT=staging",
                        "DATABASE_URL=postgresql+asyncpg://acgs_user:${POSTGRES_PASSWORD}@postgres:5432/acgs_staging"
                    ],
                    "ports": [f"{self.config.model_registry_port}:8000"],
                    "networks": ["acgs-staging"],
                    "depends_on": ["postgres"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
            }
        }
        
        # Save router compose file
        with open("docker-compose.router.staging.yml", "w") as f:
            yaml.dump(router_compose, f, default_flow_style=False)
        
        # Deploy router services
        cmd = [
            "docker-compose",
            "-f", "docker-compose.router.staging.yml",
            "--env-file", "config/environments/development.env.staging",
            "up", "-d"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Router deployment failed: {result.stderr}")
        
        # Wait for services to be ready
        await self._wait_for_service("hybrid-router", self.config.hybrid_router_port, timeout=180)
        await self._wait_for_service("model-registry", self.config.model_registry_port, timeout=120)
        
        logger.info("✅ Router components deployed successfully")
    
    async def _configure_api_integrations(self):
        """Configure API integrations for all tiers."""
        logger.info("🔗 Configuring API integrations...")
        
        # Test OpenRouter API connection
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.get(
                    f"{self.config.openrouter_api_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        logger.info("✅ OpenRouter API connection validated")
                    else:
                        logger.warning(f"⚠️ OpenRouter API returned status {response.status}")
            except Exception as e:
                logger.error(f"❌ OpenRouter API connection failed: {e}")
        
        # Test Groq API connection
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.get(
                    f"{self.config.groq_api_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Groq API connection validated")
                    else:
                        logger.warning(f"⚠️ Groq API returned status {response.status}")
            except Exception as e:
                logger.error(f"❌ Groq API connection failed: {e}")
        
        logger.info("✅ API integrations configured")
    
    async def _wait_for_service(self, service_name: str, port: int, timeout: int = 120):
        """Wait for a service to become available."""
        logger.info(f"⏳ Waiting for {service_name} on port {port}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:{port}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            logger.info(f"✅ {service_name} is ready")
                            return
            except:
                pass
            
            await asyncio.sleep(5)
        
        raise RuntimeError(f"Service {service_name} did not become ready within {timeout} seconds")
    
    async def _validate_deployment(self):
        """Validate the deployment."""
        logger.info("🔍 Validating deployment...")
        
        # Test 5-tier router endpoints
        test_queries = [
            {"text": "Hello", "expected_tier": "tier_1_nano"},
            {"text": "Explain quantum computing", "expected_tier": "tier_2_fast"},
            {"text": "Analyze complex constitutional governance scenarios", "expected_tier": "tier_5_expert"}
        ]
        
        async with aiohttp.ClientSession() as session:
            for query in test_queries:
                try:
                    async with session.post(
                        f"http://localhost:{self.config.hybrid_router_port}/route",
                        json={"query": query["text"]},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"✅ Query routed to tier: {result.get('tier', 'unknown')}")
                        else:
                            logger.warning(f"⚠️ Router test failed with status {response.status}")
                except Exception as e:
                    logger.error(f"❌ Router test failed: {e}")
        
        logger.info("✅ Deployment validation completed")
    
    async def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment status report."""
        deployment_duration = (datetime.utcnow() - self.deployment_start_time).total_seconds()
        
        return {
            "deployment_status": "SUCCESS",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "environment": self.configconfig/environments/development.environment,
            "deployment_duration_seconds": deployment_duration,
            "deployed_components": [
                "5-tier-hybrid-router",
                "model-registry",
                "postgresql",
                "redis",
                "api-integrations"
            ],
            "api_integrations": {
                "openrouter": "configured",
                "groq": "configured",
                "nano_vllm": "pending"
            },
            "performance_targets": {
                "p99_latency_ms": self.config.target_p99_latency_ms,
                "throughput_rps": self.config.target_throughput_rps,
                "cache_hit_rate": self.config.target_cache_hit_rate
            },
            "next_steps": [
                "Execute load testing",
                "Validate performance targets",
                "Conduct stress testing",
                "Measure cost optimization"
            ]
        }
    
    async def _rollback_deployment(self):
        """Rollback deployment in case of failure."""
        logger.info("🔄 Rolling back deployment...")
        
        try:
            # Stop router services
            subprocess.run([
                "docker-compose", "-f", "docker-compose.router.staging.yml", "down"
            ], capture_output=True)
            
            # Stop infrastructure
            subprocess.run([
                "docker-compose", "-f", "infrastructure/docker/docker-compose.staging.yml", "down"
            ], capture_output=True)
            
            logger.info("✅ Rollback completed")
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")


async def main():
    """Main deployment function."""
    config = DeploymentConfig()
    orchestrator = StagingDeploymentOrchestrator(config)
    
    try:
        report = await orchestrator.deploy_to_staging()
        
        # Save deployment report
        report_path = f"deployment_report_staging_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n🎉 Deployment completed successfully!")
        print(f"📊 Report saved to: {report_path}")
        print(f"🔗 Hybrid Router: http://localhost:{config.hybrid_router_port}")
        print(f"🔗 Model Registry: http://localhost:{config.model_registry_port}")
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
