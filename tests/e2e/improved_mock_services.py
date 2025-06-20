#!/usr/bin/env python3
"""
Improved ACGS Mock Services with Dynamic Port Allocation

This module provides enhanced mock services that address the port conflict
issues found in the audit. Features dynamic port allocation, better error
handling, and improved service simulation.

Features:
- Dynamic port allocation to avoid conflicts
- Improved constitutional compliance logic
- Better service health simulation
- Enhanced error handling and logging
- Realistic response times and data

Usage:
    python tests/e2e/improved_mock_services.py
    
Formal Verification Comments:
# requires: Available ports, Python asyncio
# ensures: Mock services running without conflicts
# sha256: improved_mock_services_v1.0
"""

import asyncio
import json
import logging
import random
import socket
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from aiohttp import web
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedMockACGSServices:
    """
    Enhanced mock ACGS services with improved reliability and features.
    
    Addresses issues found in audit:
    - Dynamic port allocation to avoid conflicts
    - Improved constitutional compliance scoring
    - Better service simulation
    - Enhanced error handling
    """

    def __init__(self):
        self.start_time = time.time()
        self.users = {}
        self.principles = self._initialize_constitutional_principles()
        self.policies = []
        self.service_ports = {}
        self.runners = []

    def _initialize_constitutional_principles(self) -> List[Dict[str, Any]]:
        """Initialize comprehensive constitutional principles."""
        return [
            {
                "id": "principle_001",
                "name": "Transparency",
                "description": "All governance decisions must be transparent and auditable",
                "category": "governance",
                "priority": "high",
                "compliance_keywords": ["transparent", "open", "auditable", "visible"],
                "weight": 0.25
            },
            {
                "id": "principle_002",
                "name": "Fairness",
                "description": "Policies must treat all stakeholders fairly and equitably",
                "category": "ethics",
                "priority": "high",
                "compliance_keywords": ["fair", "equitable", "just", "equal"],
                "weight": 0.25
            },
            {
                "id": "principle_003",
                "name": "Privacy",
                "description": "User privacy and data rights must be protected",
                "category": "privacy",
                "priority": "high",
                "compliance_keywords": ["privacy", "protect", "consent", "rights"],
                "weight": 0.25
            },
            {
                "id": "principle_004",
                "name": "Accountability",
                "description": "Decision makers must be accountable for their actions",
                "category": "governance",
                "priority": "high",
                "compliance_keywords": ["accountable", "responsible", "oversight"],
                "weight": 0.25
            }
        ]

    def _find_free_port(self, start_port: int = 8000) -> int:
        """Find a free port starting from the given port number."""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports available")

    async def health_handler(self, request):
        """Enhanced health check endpoint."""
        service_name = request.match_info.get('service', 'unknown')
        
        # Simulate realistic processing time
        await asyncio.sleep(random.uniform(0.01, 0.03))
        
        # Simulate occasional service degradation
        is_healthy = random.random() > 0.05  # 95% healthy rate
        
        uptime = time.time() - self.start_time
        
        response_data = {
            "status": "healthy" if is_healthy else "degraded",
            "service": f"{service_name}_service",
            "version": "3.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": uptime,
            "port": self.service_ports.get(service_name, 0),
            "metrics": {
                "requests_processed": random.randint(100, 1000),
                "avg_response_time_ms": random.uniform(10, 50),
                "memory_usage_mb": random.uniform(50, 200),
                "cpu_usage_percent": random.uniform(5, 25)
            }
        }
        
        status_code = 200 if is_healthy else 503
        return web.json_response(response_data, status=status_code)

    async def auth_register(self, request):
        """Enhanced user registration with validation."""
        try:
            data = await request.json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "citizen")
            
            # Enhanced validation
            if not username or len(username) < 3:
                return web.json_response(
                    {"error": "Username must be at least 3 characters"}, 
                    status=400
                )
            
            if not email or "@" not in email:
                return web.json_response(
                    {"error": "Valid email required"}, 
                    status=400
                )
            
            if not password or len(password) < 8:
                return web.json_response(
                    {"error": "Password must be at least 8 characters"}, 
                    status=400
                )
            
            if username in self.users:
                return web.json_response(
                    {"error": "User already exists"}, 
                    status=409
                )
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.03, 0.08))
            
            user_id = f"user_{len(self.users) + 1:04d}"
            self.users[username] = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": None,
                "login_count": 0
            }
            
            return web.json_response({
                "message": "User registered successfully",
                "user_id": user_id,
                "username": username,
                "role": role
            }, status=201)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return web.json_response(
                {"error": "Internal server error"}, 
                status=500
            )

    async def auth_login(self, request):
        """Enhanced user login with realistic token generation."""
        try:
            data = await request.post()
            username = data.get("username")
            password = data.get("password")
            
            if not username or not password:
                return web.json_response(
                    {"error": "Username and password required"}, 
                    status=400
                )
            
            if username not in self.users:
                # Simulate processing time even for failed attempts
                await asyncio.sleep(random.uniform(0.05, 0.1))
                return web.json_response(
                    {"error": "Invalid credentials"}, 
                    status=401
                )
            
            # Simulate authentication processing
            await asyncio.sleep(random.uniform(0.06, 0.12))
            
            # Update user login info
            user = self.users[username]
            user["last_login"] = datetime.now(timezone.utc).isoformat()
            user["login_count"] += 1
            
            # Generate realistic JWT token
            token_payload = {
                "user_id": user["user_id"],
                "username": username,
                "role": user["role"],
                "exp": int(time.time()) + 3600  # 1 hour expiry
            }
            
            mock_token = f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.{username}_{int(time.time())}.mock_signature"
            
            return web.json_response({
                "access_token": mock_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": f"refresh_{username}_{int(time.time())}",
                "user": {
                    "user_id": user["user_id"],
                    "username": username,
                    "role": user["role"],
                    "email": user["email"]
                }
            })
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return web.json_response(
                {"error": "Internal server error"}, 
                status=500
            )

    def _calculate_constitutional_compliance(self, content: str) -> float:
        """
        Enhanced constitutional compliance calculation.
        
        Addresses the compliance scoring issues found in audit.
        """
        content_lower = content.lower()
        total_score = 0.0
        total_weight = 0.0
        
        for principle in self.principles:
            principle_score = 0.0
            keyword_matches = 0
            
            # Check for positive compliance keywords
            for keyword in principle["compliance_keywords"]:
                if keyword in content_lower:
                    keyword_matches += 1
            
            # Calculate principle score based on keyword matches
            if keyword_matches > 0:
                principle_score = min(1.0, keyword_matches / len(principle["compliance_keywords"]))
            
            # Apply contextual scoring
            if principle["name"] == "Privacy":
                if "unrestricted" in content_lower and "without consent" in content_lower:
                    principle_score = 0.1  # Major violation
                elif "protect" in content_lower and ("privacy" in content_lower or "data" in content_lower):
                    principle_score = max(principle_score, 0.9)
            
            elif principle["name"] == "Transparency":
                if "transparent" in content_lower or "open" in content_lower:
                    principle_score = max(principle_score, 0.85)
                elif "secret" in content_lower or "hidden" in content_lower:
                    principle_score = 0.2
            
            elif principle["name"] == "Fairness":
                if "fair" in content_lower or "equitable" in content_lower:
                    principle_score = max(principle_score, 0.8)
                elif "discriminat" in content_lower or "bias" in content_lower:
                    principle_score = 0.3
            
            # Weight the principle score
            weighted_score = principle_score * principle["weight"]
            total_score += weighted_score
            total_weight += principle["weight"]
        
        # Normalize score
        final_score = total_score / total_weight if total_weight > 0 else 0.5
        
        # Add some realistic variance
        variance = random.uniform(-0.05, 0.05)
        final_score = max(0.0, min(1.0, final_score + variance))
        
        return final_score

    async def ac_compliance_validate(self, request):
        """Enhanced constitutional compliance validation."""
        try:
            data = await request.json()
            content = data.get("content", "")
            
            if not content:
                return web.json_response(
                    {"error": "Content required for validation"}, 
                    status=400
                )
            
            # Simulate processing time for compliance checking
            await asyncio.sleep(random.uniform(0.08, 0.15))
            
            # Calculate compliance score using improved algorithm
            compliance_score = self._calculate_constitutional_compliance(content)
            
            # Generate detailed validation result
            validation_result = {
                "compliance_score": compliance_score,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "content_length": len(content),
                "principle_scores": {},
                "recommendations": [],
                "risk_level": "low" if compliance_score >= 0.8 else "medium" if compliance_score >= 0.6 else "high"
            }
            
            # Calculate individual principle scores
            for principle in self.principles:
                principle_score = 0.0
                content_lower = content.lower()
                
                for keyword in principle["compliance_keywords"]:
                    if keyword in content_lower:
                        principle_score += 0.25
                
                validation_result["principle_scores"][principle["name"]] = min(1.0, principle_score)
            
            # Generate recommendations based on score
            if compliance_score < 0.8:
                validation_result["recommendations"].append("Consider adding transparency requirements")
                validation_result["recommendations"].append("Ensure stakeholder consultation process")
                
                if compliance_score < 0.6:
                    validation_result["recommendations"].append("Major constitutional compliance issues detected")
                    validation_result["recommendations"].append("Review policy against core principles")
            
            return web.json_response({
                "status": "success",
                "validation_result": validation_result
            })
            
        except Exception as e:
            logger.error(f"Compliance validation error: {str(e)}")
            return web.json_response(
                {"error": "Validation failed"}, 
                status=500
            )

    async def gs_synthesize(self, request):
        """Enhanced policy synthesis with better simulation."""
        try:
            data = await request.json()
            policy_title = data.get("policy_title", "Untitled Policy")
            domain = data.get("domain", "general")
            principles = data.get("principles", [])
            complexity = data.get("complexity", "medium")
            
            # Simulate synthesis processing time based on complexity
            processing_times = {"low": 0.1, "medium": 0.15, "high": 0.25}
            processing_time = processing_times.get(complexity, 0.15)
            await asyncio.sleep(processing_time)
            
            # Generate more realistic policy content
            policy_content = self._generate_policy_content(policy_title, domain, principles)
            
            synthesized_policy = {
                "id": f"policy_{len(self.policies) + 1:03d}",
                "title": policy_title,
                "domain": domain,
                "content": policy_content,
                "hash": f"policy_hash_{int(time.time())}_{random.randint(1000, 9999)}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "principles_applied": principles,
                "complexity": complexity,
                "synthesis_metadata": {
                    "models_used": ["gpt-4", "claude-3", "gemini-pro"],
                    "processing_time_ms": processing_time * 1000,
                    "confidence_score": random.uniform(0.85, 0.98),
                    "consensus_score": random.uniform(0.8, 0.95),
                    "validation_status": "pending"
                }
            }
            
            self.policies.append(synthesized_policy)
            
            return web.json_response({
                "status": "success",
                "generated_rules": [synthesized_policy],
                "message": "Policy synthesis completed successfully",
                "overall_synthesis_status": "completed",
                "processing_time_ms": processing_time * 1000
            }, status=202)
            
        except Exception as e:
            logger.error(f"Policy synthesis error: {str(e)}")
            return web.json_response(
                {"error": "Synthesis failed"}, 
                status=500
            )

    def _generate_policy_content(self, title: str, domain: str, principles: List[str]) -> str:
        """Generate realistic policy content based on inputs."""
        templates = {
            "privacy": "This privacy policy ensures user data protection through {principles}. "
                      "All data collection requires explicit consent and follows transparency guidelines.",
            "security": "This security policy establishes {principles} for system protection. "
                       "Access controls and monitoring ensure accountability and fairness.",
            "governance": "This governance policy implements {principles} for decision-making processes. "
                         "Transparent procedures ensure fair and accountable outcomes.",
            "general": "This policy addresses {domain} concerns through {principles}. "
                      "Implementation follows constitutional guidelines for transparency and accountability."
        }
        
        template = templates.get(domain, templates["general"])
        principles_text = ", ".join(principles) if principles else "core constitutional principles"
        
        content = template.format(principles=principles_text, domain=domain)
        content += f"\n\nPolicy Title: {title}\nDomain: {domain}\nGenerated: {datetime.now().isoformat()}"
        
        return content

    async def create_service_app(self, service_name: str) -> web.Application:
        """Create application for a specific service."""
        app = web.Application()
        
        # Common endpoints for all services
        app.router.add_get('/health', self.health_handler)
        
        # Service-specific endpoints
        if service_name == "auth":
            app.router.add_post('/auth/register', self.auth_register)
            app.router.add_post('/auth/login', self.auth_login)
            app.router.add_get('/auth/profile', self.auth_profile)
        
        elif service_name == "ac":
            app.router.add_get('/api/v1/principles', self.ac_principles)
            app.router.add_post('/api/v1/principles', self.ac_principles)
            app.router.add_post('/api/v1/compliance/validate', self.ac_compliance_validate)
            app.router.add_post('/api/v1/validate/multi-model', self.ac_compliance_validate)
        
        elif service_name == "gs":
            app.router.add_post('/api/v1/synthesize', self.gs_synthesize)
            app.router.add_get('/api/v1/policies', self.gs_policies)
        
        # Add generic endpoints for other services
        else:
            app.router.add_get('/api/v1/status', self.generic_status)
            app.router.add_post('/api/v1/process', self.generic_process)
        
        return app

    async def auth_profile(self, request):
        """Get user profile from token."""
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return web.json_response(
                    {"error": "Missing or invalid authorization header"}, 
                    status=401
                )
            
            token = auth_header.replace("Bearer ", "")
            
            # Extract username from mock token
            if "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9." in token:
                username = token.split(".")[1].split("_")[0]
                if username in self.users:
                    return web.json_response(self.users[username])
            
            return web.json_response(
                {"error": "Invalid or expired token"}, 
                status=401
            )
            
        except Exception as e:
            logger.error(f"Profile error: {str(e)}")
            return web.json_response(
                {"error": "Internal server error"}, 
                status=500
            )

    async def ac_principles(self, request):
        """Handle constitutional principles requests."""
        try:
            if request.method == "GET":
                await asyncio.sleep(random.uniform(0.02, 0.05))
                
                return web.json_response({
                    "status": "success",
                    "data": {
                        "principles": self.principles,
                        "total": len(self.principles),
                        "constitutional_hash": "cdd01ef066bc6cf2",
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                })
            
            elif request.method == "POST":
                data = await request.json()
                new_principles = data.get("principles", [])
                
                await asyncio.sleep(random.uniform(0.08, 0.15))
                
                for principle in new_principles:
                    principle["id"] = f"principle_{len(self.principles) + 1:03d}"
                    principle["created_at"] = datetime.now(timezone.utc).isoformat()
                    self.principles.append(principle)
                
                return web.json_response({
                    "status": "success",
                    "message": f"Created {len(new_principles)} principles",
                    "principles": new_principles
                }, status=201)
                
        except Exception as e:
            logger.error(f"Principles error: {str(e)}")
            return web.json_response(
                {"error": "Internal server error"}, 
                status=500
            )

    async def gs_policies(self, request):
        """Get synthesized policies."""
        try:
            await asyncio.sleep(random.uniform(0.01, 0.03))
            
            return web.json_response({
                "status": "success",
                "policies": self.policies,
                "total": len(self.policies),
                "last_updated": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Policies error: {str(e)}")
            return web.json_response(
                {"error": "Internal server error"}, 
                status=500
            )

    async def generic_status(self, request):
        """Generic status endpoint for other services."""
        await asyncio.sleep(random.uniform(0.01, 0.03))
        
        return web.json_response({
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "3.0.0"
        })

    async def generic_process(self, request):
        """Generic processing endpoint for other services."""
        try:
            data = await request.json()
            await asyncio.sleep(random.uniform(0.05, 0.1))
            
            return web.json_response({
                "status": "processed",
                "result": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_received": bool(data)
            })
            
        except Exception as e:
            return web.json_response(
                {"error": "Processing failed"}, 
                status=500
            )

    async def start_improved_mock_services(self):
        """Start all mock services with dynamic port allocation."""
        services = [
            {"name": "auth", "preferred_port": 8000},
            {"name": "ac", "preferred_port": 8001},
            {"name": "integrity", "preferred_port": 8002},
            {"name": "fv", "preferred_port": 8003},
            {"name": "gs", "preferred_port": 8004},
            {"name": "pgc", "preferred_port": 8005},
            {"name": "ec", "preferred_port": 8006},
            {"name": "dgm", "preferred_port": 8007}
        ]
        
        logger.info("🚀 Starting improved ACGS mock services...")
        
        for service in services:
            try:
                # Find free port
                port = self._find_free_port(service["preferred_port"])
                self.service_ports[service["name"]] = port
                
                # Create service app
                app = await self.create_service_app(service["name"])
                runner = web.AppRunner(app)
                await runner.setup()
                
                site = web.TCPSite(runner, 'localhost', port)
                await site.start()
                
                self.runners.append(runner)
                logger.info(f"✅ Mock {service['name']} service started on port {port}")
                
            except Exception as e:
                logger.error(f"❌ Failed to start {service['name']} service: {str(e)}")
        
        logger.info("🎉 All improved mock ACGS services are running!")
        logger.info("📊 Service ports:")
        for service_name, port in self.service_ports.items():
            logger.info(f"  {service_name}: http://localhost:{port}")
        
        logger.info("Press Ctrl+C to stop the services")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping improved mock services...")
            for runner in self.runners:
                await runner.cleanup()
            logger.info("✅ All improved mock services stopped")

async def main():
    """Main function to start improved mock services."""
    mock_services = ImprovedMockACGSServices()
    await mock_services.start_improved_mock_services()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Improved mock services stopped by user")
