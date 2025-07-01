#!/usr/bin/env python3
"""
ACGS-1 Lite Sandbox Controller
Manages isolated execution environments for AI agents with escape detection
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import aioredis
import docker
import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
SANDBOX_EXECUTIONS_TOTAL = Counter(
    "sandbox_executions_total",
    "Total number of sandbox executions",
    ["result", "termination_reason"],
)

SANDBOX_EXECUTION_DURATION = Histogram(
    "sandbox_execution_duration_seconds", "Time spent executing in sandbox", ["result"]
)

SANDBOX_VIOLATIONS_TOTAL = Counter(
    "sandbox_violations_total",
    "Total number of sandbox violations detected",
    ["violation_type", "severity"],
)

SANDBOX_ESCAPE_ATTEMPTS_TOTAL = Counter(
    "sandbox_escape_attempts_total",
    "Total number of sandbox escape attempts",
    ["pattern"],
)

ACTIVE_SANDBOXES = Gauge(
    "active_sandboxes_count", "Number of currently active sandboxes"
)


# Request/Response Models
class SandboxExecutionRequest(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    code: str = Field(..., description="Code to execute")
    timeout_seconds: int = Field(default=300, description="Execution timeout")
    memory_limit_mb: int = Field(default=2048, description="Memory limit in MB")
    cpu_limit: float = Field(default=0.5, description="CPU limit (cores)")
    environment: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )


class SandboxExecutionResponse(BaseModel):
    execution_id: str = Field(..., description="Execution identifier")
    success: bool = Field(..., description="Whether execution completed successfully")
    output: str = Field(..., description="Execution output")
    error: Optional[str] = Field(None, description="Error message if failed")
    violations: List[Dict[str, Any]] = Field(
        default_factory=list, description="Security violations detected"
    )
    execution_time_seconds: float = Field(..., description="Actual execution time")
    resource_usage: Dict[str, Any] = Field(..., description="Resource usage statistics")
    termination_reason: str = Field(..., description="Reason for termination")


class ViolationEvent(BaseModel):
    violation_id: str
    sandbox_id: str
    agent_id: str
    violation_type: str
    severity: str
    description: str
    detection_layer: str
    indicators: Dict[str, Any]
    timestamp: str


# Sandbox Controller Service
class SandboxController:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client: Optional[aioredis.Redis] = None
        self.policy_engine_url = "http://policy-engine:8001"
        self.redpanda_url = "http://constitutional-events-kafka:9092"
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        self.violation_patterns = self._load_violation_patterns()

    async def initialize(self):
        """Initialize connections"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(
                "redis://redis:6379/0", encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis")

            # Start monitoring task
            asyncio.create_task(self._monitor_sandboxes())
            logger.info("Sandbox Controller initialized")

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def _load_violation_patterns(self) -> Dict[str, Any]:
        """Load violation detection patterns"""
        return {
            "process_injection": {
                "syscalls": ["ptrace", "process_vm_writev", "process_vm_readv"],
                "severity": "critical",
            },
            "privilege_escalation": {
                "syscalls": ["setuid", "setgid", "setresuid", "setresgid"],
                "severity": "critical",
            },
            "network_access": {
                "syscalls": ["socket", "bind", "connect", "listen"],
                "severity": "high",
            },
            "file_traversal": {
                "paths": ["/etc/", "/root/", "/proc/", "/sys/"],
                "severity": "high",
            },
            "shell_execution": {
                "processes": ["/bin/sh", "/bin/bash", "/bin/zsh"],
                "severity": "medium",
            },
        }

    async def execute_in_sandbox(
        self, request: SandboxExecutionRequest
    ) -> SandboxExecutionResponse:
        """Execute code in an isolated sandbox"""
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Validate request with policy engine
            await self._validate_execution_request(request)

            # Create sandbox
            sandbox_info = await self._create_sandbox(execution_id, request)

            # Execute code
            result = await self._execute_code(sandbox_info, request)

            # Clean up
            await self._cleanup_sandbox(sandbox_info)

            execution_time = time.time() - start_time

            # Update metrics
            SANDBOX_EXECUTIONS_TOTAL.labels(
                result="success" if result.success else "failure",
                termination_reason=result.termination_reason,
            ).inc()

            SANDBOX_EXECUTION_DURATION.labels(
                result="success" if result.success else "failure"
            ).observe(execution_time)

            return result

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            execution_time = time.time() - start_time

            SANDBOX_EXECUTIONS_TOTAL.labels(
                result="error", termination_reason="system_error"
            ).inc()

            return SandboxExecutionResponse(
                execution_id=execution_id,
                success=False,
                output="",
                error=str(e),
                violations=[],
                execution_time_seconds=execution_time,
                resource_usage={},
                termination_reason="system_error",
            )

    async def _validate_execution_request(self, request: SandboxExecutionRequest):
        """Validate execution request with policy engine"""
        try:
            async with aiohttp.ClientSession() as session:
                policy_request = {
                    "action": "execute_in_sandbox",
                    "agent_id": request.agent_id,
                    "input_data": {
                        "memory_mb": request.memory_limit_mb,
                        "cpu_cores": request.cpu_limit,
                        "execution_time_seconds": request.timeout_seconds,
                        "network_access": False,
                    },
                }

                async with session.post(
                    f"{self.policy_engine_url}/v1/evaluate", json=policy_request
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Policy validation failed: {response.status}")

                    result = await response.json()
                    if not result.get("allow", False):
                        violations = result.get("violations", [])
                        raise Exception(f"Policy violation: {', '.join(violations)}")

        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            raise

    async def _create_sandbox(
        self, execution_id: str, request: SandboxExecutionRequest
    ) -> Dict[str, Any]:
        """Create isolated sandbox container"""
        try:
            # Prepare container configuration
            container_config = {
                "image": "python:3.11-slim",
                "name": f"sandbox-{execution_id}",
                "detach": True,
                "remove": False,  # We'll remove manually after forensics
                "network_mode": "none",  # No network access
                "read_only": True,  # Read-only root filesystem
                "mem_limit": f"{request.memory_limit_mb}m",
                "cpu_quota": int(
                    request.cpu_limit * 100000
                ),  # CPU quota in microseconds
                "cpu_period": 100000,
                "pids_limit": 100,  # Limit number of processes
                "security_opt": [
                    "no-new-privileges:true",
                    "seccomp:unconfined",  # We'll implement custom seccomp
                ],
                "cap_drop": ["ALL"],  # Drop all capabilities
                "user": "1000:1000",  # Non-root user
                "working_dir": "/workspace",
                "volumes": {
                    "/tmp": {"bind": "/workspace", "mode": "rw"}
                },  # Temporary workspace
                "environment": {
                    **request.environment,
                    "PYTHONPATH": "/workspace",
                    "HOME": "/workspace",
                },
                "command": ["python", "-c", request.code],
            }

            # Create container
            container = self.docker_client.containers.create(**container_config)

            sandbox_info = {
                "execution_id": execution_id,
                "container_id": container.id,
                "container": container,
                "agent_id": request.agent_id,
                "start_time": time.time(),
                "timeout": request.timeout_seconds,
                "violations": [],
            }

            self.active_sandboxes[execution_id] = sandbox_info
            ACTIVE_SANDBOXES.set(len(self.active_sandboxes))

            return sandbox_info

        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise

    async def _execute_code(
        self, sandbox_info: Dict[str, Any], request: SandboxExecutionRequest
    ) -> SandboxExecutionResponse:
        """Execute code in sandbox with monitoring"""
        container = sandbox_info["container"]
        execution_id = sandbox_info["execution_id"]

        try:
            # Start container
            container.start()

            # Start monitoring
            monitor_task = asyncio.create_task(
                self._monitor_sandbox_execution(sandbox_info)
            )

            # Wait for completion or timeout
            try:
                await asyncio.wait_for(
                    self._wait_for_container(container), timeout=request.timeout_seconds
                )
            except asyncio.TimeoutError:
                # Timeout - kill container
                container.kill()
                sandbox_info["violations"].append(
                    {
                        "type": "execution_timeout",
                        "severity": "medium",
                        "description": f"Execution exceeded {request.timeout_seconds} seconds",
                    }
                )

            # Stop monitoring
            monitor_task.cancel()

            # Get execution results
            exit_code = container.attrs["State"]["ExitCode"]
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")

            # Get resource usage
            stats = container.stats(stream=False)
            resource_usage = self._extract_resource_usage(stats)

            # Determine termination reason
            termination_reason = self._determine_termination_reason(
                exit_code, sandbox_info["violations"]
            )

            execution_time = time.time() - sandbox_info["start_time"]

            return SandboxExecutionResponse(
                execution_id=execution_id,
                success=exit_code == 0 and len(sandbox_info["violations"]) == 0,
                output=logs,
                error=None if exit_code == 0 else f"Exit code: {exit_code}",
                violations=sandbox_info["violations"],
                execution_time_seconds=execution_time,
                resource_usage=resource_usage,
                termination_reason=termination_reason,
            )

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            raise

    async def _monitor_sandbox_execution(self, sandbox_info: Dict[str, Any]):
        """Monitor sandbox for violations during execution"""
        container = sandbox_info["container"]

        try:
            while container.status == "running":
                # Check for process violations
                await self._check_process_violations(sandbox_info)

                # Check for resource violations
                await self._check_resource_violations(sandbox_info)

                # Check for file access violations
                await self._check_file_violations(sandbox_info)

                await asyncio.sleep(0.1)  # 100ms monitoring interval

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")

    async def _check_process_violations(self, sandbox_info: Dict[str, Any]):
        """Check for process-based violations"""
        try:
            container = sandbox_info["container"]

            # Get container processes
            processes = container.top()

            for process in processes.get("Processes", []):
                process_name = process[-1] if process else ""

                # Check for shell execution
                for shell in self.violation_patterns["shell_execution"]["processes"]:
                    if shell in process_name:
                        violation = {
                            "type": "shell_execution",
                            "severity": "medium",
                            "description": f"Shell execution detected: {process_name}",
                            "process": process_name,
                        }
                        sandbox_info["violations"].append(violation)
                        await self._report_violation(sandbox_info, violation)

        except Exception as e:
            logger.warning(f"Process violation check failed: {e}")

    async def _check_resource_violations(self, sandbox_info: Dict[str, Any]):
        """Check for resource limit violations"""
        try:
            container = sandbox_info["container"]
            stats = container.stats(stream=False)

            # Check memory usage
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            memory_percent = (memory_usage / memory_limit) * 100

            if memory_percent > 95:  # 95% of limit
                violation = {
                    "type": "memory_limit_breach",
                    "severity": "high",
                    "description": f"Memory usage at {memory_percent:.1f}%",
                    "memory_usage": memory_usage,
                    "memory_limit": memory_limit,
                }
                sandbox_info["violations"].append(violation)
                await self._report_violation(sandbox_info, violation)

        except Exception as e:
            logger.warning(f"Resource violation check failed: {e}")

    async def _check_file_violations(self, sandbox_info: Dict[str, Any]):
        """Check for unauthorized file access"""
        # This would require more sophisticated monitoring
        # For now, we'll implement basic checks
        pass

    async def _report_violation(
        self, sandbox_info: Dict[str, Any], violation: Dict[str, Any]
    ):
        """Report violation to monitoring systems"""
        try:
            # Update metrics
            SANDBOX_VIOLATIONS_TOTAL.labels(
                violation_type=violation["type"], severity=violation["severity"]
            ).inc()

            # Check if this constitutes an escape attempt
            if violation["severity"] in ["critical", "high"]:
                SANDBOX_ESCAPE_ATTEMPTS_TOTAL.labels(pattern=violation["type"]).inc()

                # Trigger emergency containment
                await self._emergency_containment(sandbox_info, violation)

            # Send to audit trail
            await self._send_to_audit_trail(sandbox_info, violation)

        except Exception as e:
            logger.error(f"Failed to report violation: {e}")

    async def _emergency_containment(
        self, sandbox_info: Dict[str, Any], violation: Dict[str, Any]
    ):
        """Emergency containment for critical violations"""
        try:
            container = sandbox_info["container"]

            # Pause container to preserve state
            container.pause()

            # Take forensic snapshot
            await self._take_forensic_snapshot(sandbox_info)

            # Kill container
            container.kill()

            logger.critical(
                f"Emergency containment triggered for {sandbox_info['execution_id']}: {violation}"
            )

        except Exception as e:
            logger.error(f"Emergency containment failed: {e}")

    async def _take_forensic_snapshot(self, sandbox_info: Dict[str, Any]):
        """Take forensic snapshot of container"""
        try:
            container = sandbox_info["container"]
            execution_id = sandbox_info["execution_id"]

            # Export container filesystem
            snapshot_path = f"/tmp/forensics/sandbox-{execution_id}.tar"
            Path("/tmp/forensics").mkdir(exist_ok=True)

            with open(snapshot_path, "wb") as f:
                for chunk in container.export():
                    f.write(chunk)

            logger.info(f"Forensic snapshot saved: {snapshot_path}")

        except Exception as e:
            logger.error(f"Forensic snapshot failed: {e}")

    async def _send_to_audit_trail(
        self, sandbox_info: Dict[str, Any], violation: Dict[str, Any]
    ):
        """Send violation to audit trail"""
        try:
            event = ViolationEvent(
                violation_id=str(uuid.uuid4()),
                sandbox_id=sandbox_info["execution_id"],
                agent_id=sandbox_info["agent_id"],
                violation_type=violation["type"],
                severity=violation["severity"],
                description=violation["description"],
                detection_layer="sandbox_controller",
                indicators=violation,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Send to RedPanda (simplified - would use proper Kafka client)
            logger.info(f"Audit event: {event.dict()}")

        except Exception as e:
            logger.error(f"Failed to send audit event: {e}")

    def _extract_resource_usage(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource usage from container stats"""
        try:
            return {
                "memory_usage_bytes": stats["memory_stats"]["usage"],
                "memory_limit_bytes": stats["memory_stats"]["limit"],
                "cpu_usage_percent": self._calculate_cpu_percent(stats),
                "network_rx_bytes": (
                    stats["networks"]["eth0"]["rx_bytes"] if "networks" in stats else 0
                ),
                "network_tx_bytes": (
                    stats["networks"]["eth0"]["tx_bytes"] if "networks" in stats else 0
                ),
            }
        except Exception:
            return {}

    def _calculate_cpu_percent(self, stats: Dict[str, Any]) -> float:
        """Calculate CPU usage percentage"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            if system_delta > 0:
                return (cpu_delta / system_delta) * 100.0
            return 0.0
        except Exception:
            return 0.0

    def _determine_termination_reason(
        self, exit_code: int, violations: List[Dict[str, Any]]
    ) -> str:
        """Determine reason for sandbox termination"""
        if violations:
            critical_violations = [v for v in violations if v["severity"] == "critical"]
            if critical_violations:
                return "security_violation"
            return "policy_violation"

        if exit_code == 0:
            return "normal_completion"
        elif exit_code == 137:  # SIGKILL
            return "timeout_or_killed"
        else:
            return "execution_error"

    async def _wait_for_container(self, container):
        """Wait for container to complete"""
        while True:
            container.reload()
            if container.status != "running":
                break
            await asyncio.sleep(0.1)

    async def _cleanup_sandbox(self, sandbox_info: Dict[str, Any]):
        """Clean up sandbox resources"""
        try:
            container = sandbox_info["container"]
            execution_id = sandbox_info["execution_id"]

            # Remove container
            container.remove(force=True)

            # Remove from active sandboxes
            if execution_id in self.active_sandboxes:
                del self.active_sandboxes[execution_id]

            ACTIVE_SANDBOXES.set(len(self.active_sandboxes))

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def _monitor_sandboxes(self):
        """Background task to monitor all active sandboxes"""
        while True:
            try:
                # Clean up any orphaned containers
                for execution_id, sandbox_info in list(self.active_sandboxes.items()):
                    if (
                        time.time() - sandbox_info["start_time"]
                        > sandbox_info["timeout"] + 60
                    ):
                        logger.warning(f"Cleaning up orphaned sandbox: {execution_id}")
                        await self._cleanup_sandbox(sandbox_info)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Sandbox monitoring failed: {e}")
                await asyncio.sleep(30)


# FastAPI Application
app = FastAPI(
    title="ACGS-1 Lite Sandbox Controller",
    description="AI agent sandbox execution and monitoring service",
    version="1.0.0",
)

# Global service instance
sandbox_controller = SandboxController()


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    await sandbox_controller.initialize()
    logger.info("Sandbox Controller started")


@app.post("/v1/execute", response_model=SandboxExecutionResponse)
async def execute_in_sandbox(request: SandboxExecutionRequest):
    """Execute code in an isolated sandbox"""
    return await sandbox_controller.execute_in_sandbox(request)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_sandboxes": len(sandbox_controller.active_sandboxes),
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, log_level="info")
