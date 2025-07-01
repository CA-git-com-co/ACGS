#!/usr/bin/env python3
"""
Mock ACGS Services for End-to-End Testing

This script creates mock HTTP services that simulate the ACGS-1 system
for testing purposes when the actual services are not available.

Features:
- Mock all 8 core services
- Realistic response times and data
- Health endpoints
- Authentication simulation
- Policy creation simulation

Usage:
    python tests/e2e/mock_acgs_services.py
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from aiohttp import web, ClientSession
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockACGSServices:
    """Mock ACGS services for testing."""

    def __init__(self):
        self.start_time = time.time()
        self.users = {}  # Simple in-memory user store
        self.principles = [
            {
                "id": "principle_001",
                "name": "Transparency",
                "description": "All governance decisions must be transparent and auditable",
                "category": "governance",
                "priority": "high",
            },
            {
                "id": "principle_002",
                "name": "Fairness",
                "description": "Policies must treat all stakeholders fairly and equitably",
                "category": "ethics",
                "priority": "high",
            },
        ]
        self.policies = []

    async def health_handler(self, request):
        """Health check endpoint for all services."""
        service_name = request.match_info.get("service", "unknown")

        # Simulate some processing time
        await asyncio.sleep(0.01)

        return web.json_response(
            {
                "status": "healthy",
                "service": f"{service_name}_service",
                "version": "3.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": time.time() - self.start_time,
            }
        )

    async def auth_register(self, request):
        """Mock user registration."""
        try:
            data = await request.json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "citizen")

            if not username or not email or not password:
                return web.json_response(
                    {"error": "Missing required fields"}, status=400
                )

            if username in self.users:
                return web.json_response({"error": "User already exists"}, status=409)

            # Simulate processing time
            await asyncio.sleep(0.05)

            self.users[username] = {
                "username": username,
                "email": email,
                "role": role,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            return web.json_response(
                {
                    "message": "User registered successfully",
                    "user_id": f"user_{len(self.users)}",
                },
                status=201,
            )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def auth_login(self, request):
        """Mock user login."""
        try:
            data = await request.post()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return web.json_response({"error": "Missing credentials"}, status=400)

            if username not in self.users:
                return web.json_response({"error": "Invalid credentials"}, status=401)

            # Simulate processing time
            await asyncio.sleep(0.08)

            # Generate mock JWT token
            mock_token = f"mock_jwt_token_{username}_{int(time.time())}"

            return web.json_response(
                {
                    "access_token": mock_token,
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": self.users[username],
                }
            )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def auth_profile(self, request):
        """Mock user profile endpoint."""
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return web.json_response(
                    {"error": "Missing or invalid token"}, status=401
                )

            token = auth_header.replace("Bearer ", "")

            # Extract username from mock token
            if "mock_jwt_token_" in token:
                username = token.split("_")[3]
                if username in self.users:
                    return web.json_response(self.users[username])

            return web.json_response({"error": "Invalid token"}, status=401)

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def ac_principles(self, request):
        """Mock constitutional principles endpoint."""
        try:
            if request.method == "GET":
                # Simulate processing time
                await asyncio.sleep(0.03)

                return web.json_response(
                    {
                        "status": "success",
                        "data": {
                            "principles": self.principles,
                            "total": len(self.principles),
                            "constitutional_hash": "cdd01ef066bc6cf2",
                        },
                    }
                )

            elif request.method == "POST":
                data = await request.json()

                # Simulate processing time
                await asyncio.sleep(0.1)

                new_principles = data.get("principles", [])
                for principle in new_principles:
                    principle["id"] = f"principle_{len(self.principles) + 1:03d}"
                    self.principles.append(principle)

                return web.json_response(
                    {
                        "status": "success",
                        "message": f"Created {len(new_principles)} principles",
                        "principles": new_principles,
                    },
                    status=201,
                )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def ac_validate(self, request):
        """Mock constitutional validation endpoint."""
        try:
            data = await request.json()
            content = data.get("content", "")

            # Simulate multi-model validation processing
            await asyncio.sleep(0.2)

            # Mock validation score based on content
            compliance_score = 0.85 if "privacy" in content.lower() else 0.75

            return web.json_response(
                {
                    "status": "success",
                    "validation_result": {
                        "compliance_score": compliance_score,
                        "constitutional_hash": "cdd01ef066bc6cf2",
                        "validation_models": ["gpt-4", "claude-3", "gemini-pro"],
                        "consensus_score": 0.88,
                        "recommendations": [
                            "Consider adding transparency requirements",
                            "Ensure stakeholder consultation process",
                        ],
                    },
                }
            )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def gs_synthesize(self, request):
        """Mock policy synthesis endpoint."""
        try:
            data = await request.json()
            policy_title = data.get("policy_title", "Untitled Policy")
            domain = data.get("domain", "general")

            # Simulate synthesis processing time
            await asyncio.sleep(0.15)

            synthesized_policy = {
                "id": f"policy_{len(self.policies) + 1:03d}",
                "title": policy_title,
                "domain": domain,
                "content": f"This is a synthesized {domain} policy for {policy_title}. "
                f"It incorporates constitutional principles and stakeholder requirements.",
                "hash": f"policy_hash_{int(time.time())}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "synthesis_metadata": {
                    "models_used": ["gpt-4", "claude-3"],
                    "processing_time_ms": 150,
                    "confidence_score": 0.92,
                },
            }

            self.policies.append(synthesized_policy)

            return web.json_response(
                {
                    "status": "success",
                    "generated_rules": [synthesized_policy],
                    "message": "Policy synthesis completed successfully",
                    "overall_synthesis_status": "completed",
                },
                status=202,
            )

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def create_app(self):
        """Create aiohttp application with all mock endpoints."""
        app = web.Application()

        # Health endpoints for all services
        app.router.add_get("/health", self.health_handler)

        # Auth service endpoints (port 8000)
        app.router.add_post("/auth/register", self.auth_register)
        app.router.add_post("/auth/login", self.auth_login)
        app.router.add_get("/auth/profile", self.auth_profile)

        # AC service endpoints (port 8001)
        app.router.add_get("/api/v1/principles", self.ac_principles)
        app.router.add_post("/api/v1/principles", self.ac_principles)
        app.router.add_post("/api/v1/validate/multi-model", self.ac_validate)
        app.router.add_post("/api/v1/compliance/validate", self.ac_validate)

        # GS service endpoints (port 8004)
        app.router.add_post("/api/v1/synthesize", self.gs_synthesize)
        app.router.add_get(
            "/api/v1/policies", lambda r: web.json_response({"policies": self.policies})
        )

        return app

    async def start_mock_services(self):
        """Start mock services on different ports."""
        services = [
            {"name": "auth", "port": 8000},
            {"name": "ac", "port": 8001},
            {"name": "integrity", "port": 8002},
            {"name": "fv", "port": 8003},
            {"name": "gs", "port": 8004},
            {"name": "pgc", "port": 8005},
            {"name": "ec", "port": 8006},
            {"name": "dgm", "port": 8007},
        ]

        runners = []

        for service in services:
            app = await self.create_app()
            runner = web.AppRunner(app)
            await runner.setup()

            site = web.TCPSite(runner, "localhost", service["port"])
            await site.start()

            runners.append(runner)
            logger.info(
                f"✅ Mock {service['name']} service started on port {service['port']}"
            )

        logger.info("🎉 All mock ACGS services are running!")
        logger.info("Press Ctrl+C to stop the services")

        try:
            # Keep services running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping mock services...")
            for runner in runners:
                await runner.cleanup()
            logger.info("✅ All mock services stopped")


async def main():
    """Main function to start mock services."""
    mock_services = MockACGSServices()
    await mock_services.start_mock_services()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Mock services stopped by user")
