"""
Sandbox Manager Service

Core service for managing secure execution environments using Docker containers.
"""

import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import docker
from docker.errors import DockerException

from ..core.config import settings
from ..models.execution import (
    ExecutionAuditLog,
    ExecutionEnvironment,
    ExecutionPolicy,
    ExecutionStatus,
    SandboxExecution,
)

logger = logging.getLogger(__name__)


class SandboxManager:
    """
    Manager for secure sandbox execution environments.

    Features:
    - Docker-based isolation
    - Resource limiting
    - Security policy enforcement
    - Network isolation
    - File system restrictions
    """

    def __init__(self):
        self.docker_client = docker.from_env()
        self.active_containers: dict[str, docker.models.containers.Container] = {}
        self.execution_policies: dict[str, dict] = settings.EXECUTION_POLICIES

    async def create_execution(
        self,
        db: AsyncSession,
        agent_id: str,
        agent_type: str,
        environment: str,
        code: str,
        language: str,
        execution_context: dict[str, Any] | None = None,
        input_files: list[dict[str, Any]] | None = None,
        environment_variables: dict[str, str] | None = None,
        request_metadata: dict[str, Any] | None = None,
    ) -> SandboxExecution:
        """
        Create a new sandbox execution session.

        Args:
            agent_id: ID of the requesting agent
            environment: Execution environment (python, bash, node, etc.)
            code: Code to execute
            language: Programming language
            execution_context: Additional execution context
            input_files: Files to make available in sandbox
            environment_variables: Environment variables for execution
            request_metadata: Request metadata (session_id, etc.)

        Returns:
            SandboxExecution object
        """
        execution_id = f"exec_{agent_id}_{datetime.utcnow().timestamp()}"

        # Get execution policy for this agent/environment
        policy = await self._get_execution_policy(db, agent_id, agent_type, environment)

        # Create execution record
        execution = SandboxExecution(
            execution_id=execution_id,
            agent_id=agent_id,
            agent_type=agent_type,
            environment=environment,
            code=code,
            language=language,
            execution_context=execution_context or {},
            environment_variables=environment_variables or {},
            input_files=input_files or [],
            memory_limit_mb=policy.get("max_memory_mb", 512),
            timeout_seconds=policy.get("max_execution_time", 300),
            constitutional_hash=settings.CONSTITUTIONAL_HASH,
            request_id=request_metadata.get("request_id") if request_metadata else None,
            session_id=request_metadata.get("session_id") if request_metadata else None,
            metadata=request_metadata or {},
        )

        # Validate code against policy
        violations = await self._validate_code_policy(code, language, policy)
        if violations:
            execution.status = ExecutionStatus.FAILED.value
            execution.policy_violations = violations
            execution.error_message = f"Policy violations: {', '.join(violations)}"

        db.add(execution)
        await db.commit()

        # Create audit log
        await self._create_audit_log(
            db=db,
            execution_id=execution.id,
            event_type="execution_created",
            event_description=f"Sandbox execution created for agent {agent_id}",
            event_data={
                "environment": environment,
                "language": language,
                "policy_violations": violations,
            },
        )

        return execution

    async def execute_code(
        self,
        db: AsyncSession,
        execution: SandboxExecution,
    ) -> SandboxExecution:
        """
        Execute code in a secure sandbox environment.

        Args:
            execution: SandboxExecution object to execute

        Returns:
            Updated SandboxExecution with results
        """
        if execution.status != ExecutionStatus.PENDING.value:
            raise ValueError(
                f"Execution {execution.execution_id} is not in pending state"
            )

        if execution.policy_violations:
            raise ValueError(
                f"Execution has policy violations: {execution.policy_violations}"
            )

        try:
            # Update status to running
            execution.status = ExecutionStatus.RUNNING.value
            execution.started_at = datetime.utcnow()
            await db.commit()

            # Create audit log
            await self._create_audit_log(
                db=db,
                execution_id=execution.id,
                event_type="execution_started",
                event_description=f"Starting execution in {execution.environment} environment",
            )

            # Execute based on environment
            if execution.environment == ExecutionEnvironment.PYTHON.value:
                result = await self._execute_python(execution)
            elif execution.environment == ExecutionEnvironment.BASH.value:
                result = await self._execute_bash(execution)
            elif execution.environment == ExecutionEnvironment.NODE.value:
                result = await self._execute_node(execution)
            else:
                raise ValueError(
                    f"Unsupported execution environment: {execution.environment}"
                )

            # Update execution with results
            execution.status = result["status"]
            execution.exit_code = result["exit_code"]
            execution.stdout = result["stdout"]
            execution.stderr = result["stderr"]
            execution.execution_time_ms = result["execution_time_ms"]
            execution.memory_usage_mb = result.get("memory_usage_mb")
            execution.cpu_usage_percent = result.get("cpu_usage_percent")
            execution.container_id = result.get("container_id")
            execution.completed_at = datetime.utcnow()

            # Check for security violations in output
            security_violations = await self._check_security_violations(
                execution.stdout, execution.stderr, execution.environment
            )
            execution.security_violations = security_violations

            await db.commit()

            # Create completion audit log
            await self._create_audit_log(
                db=db,
                execution_id=execution.id,
                event_type="execution_completed",
                event_description=f"Execution completed with status {execution.status}",
                event_data={
                    "exit_code": execution.exit_code,
                    "execution_time_ms": execution.execution_time_ms,
                    "security_violations": security_violations,
                },
            )

        except Exception as e:
            logger.error(f"Execution failed for {execution.execution_id}: {e}")
            execution.status = ExecutionStatus.ERROR.value
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await db.commit()

            # Create error audit log
            await self._create_audit_log(
                db=db,
                execution_id=execution.id,
                event_type="execution_failed",
                event_description=f"Execution failed: {e!s}",
                event_data={"error": str(e)},
            )

        return execution

    async def _execute_python(self, execution: SandboxExecution) -> dict[str, Any]:
        """Execute Python code in a secure container."""
        return await self._execute_in_container(
            image=settings.PYTHON_BASE_IMAGE,
            execution=execution,
            command=["python", "-c", execution.code],
        )

    async def _execute_bash(self, execution: SandboxExecution) -> dict[str, Any]:
        """Execute Bash code in a secure container."""
        return await self._execute_in_container(
            image=settings.BASH_BASE_IMAGE,
            execution=execution,
            command=["bash", "-c", execution.code],
        )

    async def _execute_node(self, execution: SandboxExecution) -> dict[str, Any]:
        """Execute Node.js code in a secure container."""
        return await self._execute_in_container(
            image=settings.NODE_BASE_IMAGE,
            execution=execution,
            command=["node", "-e", execution.code],
        )

    async def _execute_in_container(
        self,
        image: str,
        execution: SandboxExecution,
        command: list[str],
    ) -> dict[str, Any]:
        """
        Execute code in a Docker container with security restrictions.

        Args:
            image: Docker image to use
            execution: Execution object with parameters
            command: Command to run in container

        Returns:
            Execution results dictionary
        """
        start_time = datetime.utcnow()
        container = None

        try:
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                work_dir = Path(temp_dir)

                # Write input files if any
                if execution.input_files:
                    await self._write_input_files(work_dir, execution.input_files)

                # Container configuration
                container_config = {
                    "image": image,
                    "command": command,
                    "working_dir": "/workspace",
                    "volumes": {str(work_dir): {"bind": "/workspace", "mode": "rw"}},
                    "mem_limit": f"{execution.memory_limit_mb}m",
                    "memswap_limit": f"{execution.memory_limit_mb}m",
                    "cpu_period": 100000,
                    "cpu_quota": int(settings.SANDBOX_CPU_LIMIT * 100000),
                    "network_mode": (
                        "none" if not execution.network_enabled else "bridge"
                    ),
                    "user": f"{settings.SANDBOX_USER_ID}:{settings.SANDBOX_USER_ID}",
                    "read_only": True,
                    "tmpfs": {
                        "/tmp": "noexec,nosuid,size=100m",
                        "/var/tmp": "noexec,nosuid,size=100m",
                    },
                    "security_opt": [
                        "no-new-privileges:true",
                        "seccomp=default",
                    ],
                    "cap_drop": ["ALL"],
                    "cap_add": ["CHOWN", "DAC_OVERRIDE", "SETUID", "SETGID"],
                    "environment": execution.environment_variables,
                    "remove": True,  # Auto-remove container when done
                }

                # Run container with timeout
                container = self.docker_client.containers.run(
                    detach=True, **container_config
                )

                # Store container reference
                self.active_containers[execution.execution_id] = container

                # Wait for completion with timeout
                try:
                    result = container.wait(timeout=execution.timeout_seconds)
                    exit_code = result["StatusCode"]

                    # Get output
                    stdout = container.logs(stdout=True, stderr=False).decode(
                        "utf-8", errors="replace"
                    )
                    stderr = container.logs(stdout=False, stderr=True).decode(
                        "utf-8", errors="replace"
                    )

                    # Calculate execution time
                    end_time = datetime.utcnow()
                    execution_time_ms = int(
                        (end_time - start_time).total_seconds() * 1000
                    )

                    # Get container stats (if available)
                    memory_usage_mb = None
                    cpu_usage_percent = None
                    try:
                        stats = container.stats(stream=False)
                        if stats:
                            memory_usage_mb = stats.get("memory", {}).get(
                                "usage", 0
                            ) / (1024 * 1024)
                            cpu_stats = stats.get("cpu_stats", {})
                            if cpu_stats:
                                cpu_usage_percent = self._calculate_cpu_usage(cpu_stats)
                    except Exception as e:
                        logger.warning(f"Failed to get container stats: {e}")

                    # Determine status based on exit code
                    if exit_code == 0:
                        status = ExecutionStatus.COMPLETED.value
                    else:
                        status = ExecutionStatus.FAILED.value

                    return {
                        "status": status,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "execution_time_ms": execution_time_ms,
                        "memory_usage_mb": memory_usage_mb,
                        "cpu_usage_percent": cpu_usage_percent,
                        "container_id": container.id,
                    }

                except Exception as timeout_error:
                    # Container timed out or other error
                    logger.warning(
                        f"Container execution timed out or failed: {timeout_error}"
                    )

                    # Kill container if still running
                    try:
                        container.kill()
                    except Exception:
                        pass

                    # Get partial output if available
                    stdout = stderr = ""
                    try:
                        stdout = container.logs(stdout=True, stderr=False).decode(
                            "utf-8", errors="replace"
                        )
                        stderr = container.logs(stdout=False, stderr=True).decode(
                            "utf-8", errors="replace"
                        )
                    except Exception:
                        pass

                    end_time = datetime.utcnow()
                    execution_time_ms = int(
                        (end_time - start_time).total_seconds() * 1000
                    )

                    return {
                        "status": ExecutionStatus.TIMEOUT.value,
                        "exit_code": -1,
                        "stdout": stdout,
                        "stderr": stderr
                        + f"\nExecution timed out after {execution.timeout_seconds} seconds",
                        "execution_time_ms": execution_time_ms,
                        "container_id": container.id if container else None,
                    }

        except DockerException as e:
            logger.error(f"Docker execution failed: {e}")
            return {
                "status": ExecutionStatus.ERROR.value,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Docker execution failed: {e!s}",
                "execution_time_ms": 0,
            }
        finally:
            # Clean up container reference
            if execution.execution_id in self.active_containers:
                del self.active_containers[execution.execution_id]

    async def _get_execution_policy(
        self,
        db: AsyncSession,
        agent_id: str,
        agent_type: str,
        environment: str,
    ) -> dict[str, Any]:
        """Get execution policy for agent and environment."""
        # First check for agent-specific policy
        result = await db.execute(
            select(ExecutionPolicy)
            .where(
                ExecutionPolicy.agent_id == agent_id,
                ExecutionPolicy.environment == environment,
                ExecutionPolicy.is_active == True,
            )
            .order_by(ExecutionPolicy.priority.desc())
        )
        policy = result.scalar_one_or_none()

        if policy:
            return policy.policy_rules

        # Check for agent type policy
        result = await db.execute(
            select(ExecutionPolicy)
            .where(
                ExecutionPolicy.agent_type == agent_type,
                ExecutionPolicy.environment == environment,
                ExecutionPolicy.is_active == True,
            )
            .order_by(ExecutionPolicy.priority.desc())
        )
        policy = result.scalar_one_or_none()

        if policy:
            return policy.policy_rules

        # Fall back to default policy from settings
        return self.execution_policies.get(environment, {})

    async def _validate_code_policy(
        self, code: str, language: str, policy: dict[str, Any]
    ) -> list[str]:
        """Validate code against execution policy."""
        violations = []

        if language == "python":
            # Check for blocked imports
            blocked_imports = policy.get("blocked_imports", [])
            for blocked in blocked_imports:
                if f"import {blocked}" in code or f"from {blocked}" in code:
                    violations.append(f"Blocked import: {blocked}")

            # Check for dangerous functions
            dangerous_patterns = [
                "exec(",
                "eval(",
                "compile(",
                "__import__(",
                "getattr(",
                "setattr(",
                "delattr(",
                "open(",
                "file(",
                "input(",
                "raw_input(",
            ]
            for pattern in dangerous_patterns:
                if pattern in code:
                    violations.append(f"Dangerous pattern: {pattern}")

        elif language == "bash":
            # Check for blocked commands
            blocked_commands = policy.get("blocked_commands", [])
            for blocked in blocked_commands:
                if blocked in code:
                    violations.append(f"Blocked command: {blocked}")

        return violations

    async def _check_security_violations(
        self, stdout: str, stderr: str, environment: str
    ) -> list[str]:
        """Check execution output for security violations."""
        violations = []

        # Check for suspicious output patterns
        suspicious_patterns = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "/etc/passwd",
            "/etc/shadow",
            "id_rsa",
            "private",
        ]

        combined_output = (stdout + stderr).lower()
        for pattern in suspicious_patterns:
            if pattern in combined_output:
                violations.append(f"Suspicious output pattern: {pattern}")

        return violations

    async def _write_input_files(
        self, work_dir: Path, input_files: list[dict[str, Any]]
    ) -> None:
        """Write input files to the working directory."""
        for file_data in input_files:
            file_path = work_dir / file_data["name"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if "content" in file_data:
                file_path.write_text(file_data["content"])
            elif "base64_content" in file_data:
                import base64

                content = base64.b64decode(file_data["base64_content"])
                file_path.write_bytes(content)

    def _calculate_cpu_usage(self, cpu_stats: dict[str, Any]) -> float | None:
        """Calculate CPU usage percentage from container stats."""
        try:
            cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - cpu_stats.get(
                "precpu_stats", {}
            ).get("cpu_usage", {}).get("total_usage", 0)
            system_delta = cpu_stats["system_cpu_usage"] - cpu_stats.get(
                "precpu_stats", {}
            ).get("system_cpu_usage", 0)

            if system_delta > 0:
                cpu_percent = (
                    (cpu_delta / system_delta)
                    * len(cpu_stats["cpu_usage"]["percpu_usage"])
                    * 100
                )
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass

        return None

    async def _create_audit_log(
        self,
        db: AsyncSession,
        execution_id: str,
        event_type: str,
        event_description: str,
        event_data: dict[str, Any] | None = None,
    ) -> None:
        """Create an audit log entry."""
        audit_log = ExecutionAuditLog(
            execution_id=execution_id,
            event_type=event_type,
            event_description=event_description,
            event_data=event_data or {},
            constitutional_hash=settings.CONSTITUTIONAL_HASH,
        )

        db.add(audit_log)
        await db.commit()

    async def kill_execution(self, execution_id: str) -> bool:
        """Kill a running execution."""
        if execution_id in self.active_containers:
            try:
                container = self.active_containers[execution_id]
                container.kill()
                del self.active_containers[execution_id]
                return True
            except Exception as e:
                logger.error(
                    f"Failed to kill container for execution {execution_id}: {e}"
                )

        return False

    async def cleanup_old_executions(self, db: AsyncSession) -> int:
        """Clean up old execution records and containers."""
        cutoff_date = datetime.utcnow() - timedelta(
            days=settings.MAX_EXECUTION_LOG_AGE_DAYS
        )

        # Delete old execution records
        result = await db.execute(
            select(SandboxExecution).where(
                SandboxExecution.created_at < cutoff_date,
                SandboxExecution.cleaned_up == False,
            )
        )
        old_executions = result.scalars().all()

        cleaned_count = 0
        for execution in old_executions:
            execution.cleaned_up = True
            execution.cleanup_at = datetime.utcnow()
            cleaned_count += 1

        await db.commit()

        # Clean up any orphaned containers
        try:
            containers = self.docker_client.containers.list(
                all=True, filters={"label": "acgs.service=sandbox-execution"}
            )
            for container in containers:
                if container.status in ["exited", "dead"]:
                    container.remove()
        except Exception as e:
            logger.error(f"Failed to clean up orphaned containers: {e}")

        return cleaned_count

    def close(self):
        """Clean up resources."""
        # Kill any remaining active containers
        for execution_id, container in self.active_containers.items():
            try:
                container.kill()
            except Exception as e:
                logger.error(f"Failed to kill container {execution_id}: {e}")

        self.active_containers.clear()

        if hasattr(self.docker_client, "close"):
            self.docker_client.close()
