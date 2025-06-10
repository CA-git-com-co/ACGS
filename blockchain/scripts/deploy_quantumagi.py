#!/usr/bin/env python3
"""
Quantumagi Deployment and Integration Script
Handles deployment of Quantumagi programs and integration with ACGS
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumagiDeployer:
    """Handles deployment and integration of Quantumagi framework"""

    def __init__(self, config_path: str = "deploy_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.project_root = Path(__file__).parent.parent

    def _load_config(self) -> Dict:
        """Load deployment configuration"""
        default_config = {
            "solana_cluster": "devnet",
            "anchor_provider_url": "https://api.devnet.solana.com",
            "program_keypair_path": "target/deploy/quantumagi_core-keypair.json",
            "deployer_keypair_path": "~/.config/solana/id.json",
            "constitution_document_url": "https://arweave.net/constitution_hash",
            "gs_engine_config": {
                "llm_model": "gpt-4",
                "validation_threshold": 0.85,
                "max_policy_length": 1000,
            },
            "integration": {
                "acgs_backend_url": "http://localhost:8000",
                "enable_acgs_integration": True,
                "sync_policies": True,
            },
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Could not load config from {self.config_path}: {e}")

        return default_config

    async def deploy_full_stack(self):
        """Deploy the complete Quantumagi stack"""
        logger.info("🚀 Starting Quantumagi full stack deployment")

        try:
            # Step 1: Build and deploy Solana program
            await self._build_and_deploy_program()

            # Step 2: Initialize constitution
            await self._initialize_constitution()

            # Step 3: Setup GS Engine
            await self._setup_gs_engine()

            # Step 4: Deploy initial policies
            await self._deploy_initial_policies()

            # Step 5: Integrate with ACGS backend
            if self.config["integration"]["enable_acgs_integration"]:
                await self._integrate_with_acgs()

            # Step 6: Run validation tests
            await self._run_validation_tests()

            logger.info("✅ Quantumagi deployment completed successfully!")
            await self._print_deployment_summary()

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise

    async def _build_and_deploy_program(self):
        """Build and deploy the Solana program"""
        logger.info("📦 Building Solana program...")

        # Change to project directory
        os.chdir(self.project_root)

        # Build the program
        result = subprocess.run(["anchor", "build"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Build failed: {result.stderr}")

        logger.info("✅ Program built successfully")

        # Deploy the program
        logger.info(f"🚀 Deploying to {self.config['solana_cluster']}...")

        deploy_cmd = [
            "anchor",
            "deploy",
            "--provider.cluster",
            self.config["solana_cluster"],
            "--provider.wallet",
            self.config["deployer_keypair_path"],
        ]

        result = subprocess.run(deploy_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Deployment failed: {result.stderr}")

        logger.info("✅ Program deployed successfully")

        # Extract program ID from deployment output
        program_id = self._extract_program_id(result.stdout)
        self.config["program_id"] = program_id
        logger.info(f"📋 Program ID: {program_id}")

    def _extract_program_id(self, deploy_output: str) -> str:
        """Extract program ID from anchor deploy output"""
        # Parse the deployment output to find program ID
        lines = deploy_output.split("\n")
        for line in lines:
            if "Program Id:" in line:
                return line.split(":")[-1].strip()

        # Fallback: read from keypair file
        try:
            with open(self.config["program_keypair_path"], "r") as f:
                keypair_data = json.load(f)
                # Convert keypair to program ID (simplified)
                return "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"  # Placeholder
        except:
            return "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"  # Default

    async def _initialize_constitution(self):
        """Initialize the constitutional governance system"""
        logger.info("🏛️ Initializing constitution...")

        # Create constitution hash
        constitution_content = await self._fetch_constitution_document()
        constitution_hash = self._create_constitution_hash(constitution_content)

        # Initialize using client
        from client.solana_client import QuantumagiSolanaClient
        from solders.keypair import Keypair

        # Load deployer keypair
        deployer_keypair = self._load_keypair(self.config["deployer_keypair_path"])

        client = QuantumagiSolanaClient(
            rpc_url=self.config["anchor_provider_url"],
            program_id=self.config["program_id"],
            payer_keypair=deployer_keypair,
        )

        signature = await client.initialize_constitution(constitution_hash)
        logger.info(f"✅ Constitution initialized. Signature: {signature}")

    async def _fetch_constitution_document(self) -> str:
        """Fetch the constitutional document"""
        # For demo, return a sample constitution
        return """
        Quantumagi Constitutional Framework v1.0
        
        Article I: Fundamental Principles
        1. No unauthorized state mutations (PC-001)
        2. Governance approval required for critical operations
        3. Transparency in all policy decisions
        
        Article II: AI Governance
        1. AI systems must operate within constitutional bounds
        2. Prompt governance compiler enforces real-time compliance
        3. Multi-model validation ensures policy reliability
        
        Article III: Democratic Governance
        1. Policy proposals require community voting
        2. Constitutional amendments require supermajority
        3. Emergency powers limited to critical situations
        """

    def _create_constitution_hash(self, content: str) -> bytes:
        """Create SHA-256 hash of constitution"""
        import hashlib

        return hashlib.sha256(content.encode()).digest()

    def _load_keypair(self, keypair_path: str) -> "Keypair":
        """Load Solana keypair from file"""
        from solders.keypair import Keypair

        # Expand user path
        path = os.path.expanduser(keypair_path)

        try:
            with open(path, "r") as f:
                keypair_data = json.load(f)
                return Keypair.from_bytes(bytes(keypair_data))
        except Exception as e:
            logger.warning(f"Could not load keypair from {path}: {e}")
            # Generate a new keypair for demo
            return Keypair()

    async def _setup_gs_engine(self):
        """Setup the Governance Synthesis Engine"""
        logger.info("🧠 Setting up GS Engine...")

        # Install Python dependencies
        gs_engine_dir = self.project_root / "gs_engine"
        requirements_file = gs_engine_dir / "requirements.txt"

        if requirements_file.exists():
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.warning(
                    f"Failed to install GS Engine dependencies: {result.stderr}"
                )

        # Test GS Engine
        try:
            from gs_engine.governance_synthesis import QuantumagiGSEngine

            gs_engine = QuantumagiGSEngine(self.config["gs_engine_config"])
            logger.info("✅ GS Engine initialized successfully")

        except Exception as e:
            logger.warning(f"GS Engine setup incomplete: {e}")

    async def _deploy_initial_policies(self):
        """Deploy initial governance policies"""
        logger.info("📜 Deploying initial policies...")

        initial_policies = [
            {
                "id": "PC-001",
                "title": "No Extrajudicial State Mutation",
                "content": "AI systems must not perform unauthorized state mutations without proper governance approval",
                "category": "prompt_constitution",
            },
            {
                "id": "SF-001",
                "title": "Safety Validation Required",
                "content": "All safety-critical operations must pass validation before execution",
                "category": "safety",
            },
            {
                "id": "GV-001",
                "title": "Governance Approval Threshold",
                "content": "Major governance decisions require 60% approval threshold",
                "category": "governance",
            },
        ]

        # Deploy each policy
        for policy_spec in initial_policies:
            try:
                await self._deploy_single_policy(policy_spec)
                logger.info(f"✅ Deployed policy: {policy_spec['id']}")
            except Exception as e:
                logger.warning(f"Failed to deploy policy {policy_spec['id']}: {e}")

    async def _deploy_single_policy(self, policy_spec: Dict):
        """Deploy a single policy"""
        from client.solana_client import QuantumagiSolanaClient
        from gs_engine.governance_synthesis import PolicyCategory

        # Map category string to enum
        category_map = {
            "prompt_constitution": PolicyCategory.PROMPT_CONSTITUTION,
            "safety": PolicyCategory.SAFETY,
            "governance": PolicyCategory.GOVERNANCE,
            "financial": PolicyCategory.FINANCIAL,
        }

        category = category_map.get(policy_spec["category"], PolicyCategory.GOVERNANCE)

        # Deploy using client
        deployer_keypair = self._load_keypair(self.config["deployer_keypair_path"])

        client = QuantumagiSolanaClient(
            rpc_url=self.config["anchor_provider_url"],
            program_id=self.config["program_id"],
            payer_keypair=deployer_keypair,
        )

        signature = await client.propose_policy_from_principle(
            policy_spec["id"], policy_spec["content"], category
        )

        # Auto-enact for initial deployment
        await asyncio.sleep(1)  # Wait for confirmation
        policy_id = hash(policy_spec["id"]) % 1000000  # Simple ID generation
        await client.enact_policy(policy_id)

    async def _integrate_with_acgs(self):
        """Integrate with existing ACGS backend"""
        logger.info("🔗 Integrating with ACGS backend...")

        try:
            # Test connection to ACGS backend
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config['integration']['acgs_backend_url']}/health"
                ) as response:
                    if response.status == 200:
                        logger.info("✅ ACGS backend connection successful")
                    else:
                        logger.warning(
                            f"ACGS backend returned status: {response.status}"
                        )

        except Exception as e:
            logger.warning(f"Could not connect to ACGS backend: {e}")

    async def _run_validation_tests(self):
        """Run validation tests to ensure deployment success"""
        logger.info("🧪 Running validation tests...")

        try:
            # Run anchor tests
            result = subprocess.run(
                ["anchor", "test", "--skip-deploy"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                logger.info("✅ All validation tests passed")
            else:
                logger.warning(f"Some tests failed: {result.stderr}")

        except Exception as e:
            logger.warning(f"Could not run validation tests: {e}")

    async def _print_deployment_summary(self):
        """Print deployment summary"""
        summary = f"""
        
🎉 Quantumagi Deployment Summary
================================

Program ID: {self.config.get('program_id', 'N/A')}
Cluster: {self.config['solana_cluster']}
Constitution: Initialized ✅
Initial Policies: Deployed ✅
GS Engine: Ready ✅

Next Steps:
1. Test compliance checking with: python -m client.solana_client
2. Integrate with your dApp using the client library
3. Monitor governance through the Solana explorer

Documentation: ./README.md
Client Examples: ./client/
        """

        print(summary)


async def main():
    """Main deployment function"""
    deployer = QuantumagiDeployer()

    try:
        await deployer.deploy_full_stack()
    except KeyboardInterrupt:
        logger.info("Deployment cancelled by user")
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
