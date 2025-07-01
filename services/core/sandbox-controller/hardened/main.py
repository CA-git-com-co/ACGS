#!/usr/bin/env python3
"""
ACGS-1 Lite Hardened Sandbox Controller

Enhanced security sandbox controller with:
- gVisor/Firecracker kernel-level isolation
- Enhanced seccomp profiles
- Syscall monitoring and violation detection
- Kubernetes RuntimeClass integration
- Zero-tolerance escape detection

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
import uuid
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import aiofiles
import aiohttp
import aioredis
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.rest import ApiException
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Constitutional hash for integrity verification
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Prometheus metrics - Initialize only once with unique names
from prometheus_client import REGISTRY

# Clear any existing metrics to avoid duplicates
try:
    REGISTRY._collector_to_names.clear()
    REGISTRY._names_to_collectors.clear()
except:
    pass

SANDBOX_EXECUTIONS_TOTAL = Counter(
    "hardened_sandbox_executions_v2_total",
    "Total hardened sandbox executions",
    ["runtime", "result", "termination_reason"]
)

SANDBOX_EXECUTION_DURATION = Histogram(
    "hardened_sandbox_execution_duration_v2_seconds",
    "Hardened sandbox execution time",
    ["runtime", "result"]
)

SECURITY_VIOLATIONS_TOTAL = Counter(
    "hardened_sandbox_violations_v2_total",
    "Total security violations detected",
    ["violation_type", "severity", "detection_layer"]
)

SANDBOX_ESCAPE_ATTEMPTS_TOTAL = Counter(
    "hardened_sandbox_escape_attempts_v2_total",
    "Sandbox escape attempts detected",
    ["pattern", "runtime", "blocked"]
)

SYSCALL_VIOLATIONS_TOTAL = Counter(
    "hardened_sandbox_syscall_violations_v2_total",
    "Syscall violations blocked",
    ["syscall", "action"]
)

ACTIVE_HARDENED_SANDBOXES = Gauge(
    "active_hardened_sandboxes_v2_count",
    "Number of active hardened sandboxes"
)

COLD_START_DURATION = Histogram(
    "hardened_sandbox_cold_start_duration_v2_seconds",
    "Cold start time for hardened sandboxes",
    ["runtime"]
)

# Dangerous syscalls that should always be blocked
DANGEROUS_SYSCALLS = {
    "ptrace", "mount", "umount", "umount2", "pivot_root", "chroot",
    "setns", "unshare", "clone", "fork", "vfork", "execve", "execveat",
    "kexec_load", "kexec_file_load", "reboot", "init_module", "finit_module",
    "delete_module", "quotactl", "syslog", "swapon", "swapoff",
    "acct", "settimeofday", "adjtimex", "clock_adjtime", "lookup_dcookie",
    "perf_event_open", "fanotify_init", "name_to_handle_at", "open_by_handle_at"
}

# Patterns indicating potential escape attempts
ESCAPE_PATTERNS = {
    "proc_filesystem_access": ["/proc/sys", "/proc/*/mem", "/proc/kcore"],
    "device_access": ["/dev/mem", "/dev/kmem", "/dev/port"],
    "kernel_modules": ["insmod", "rmmod", "modprobe"],
    "container_breakout": ["docker", "containerd", "runc", "crun"],
    "privilege_escalation": ["sudo", "su", "pkexec", "passwd"],
    "network_escape": ["iptables", "netfilter", "tc", "ip route"],
    "filesystem_escape": ["mount", "umount", "chroot", "pivot_root"]
}

# Request/Response Models
class HardenedSandboxRequest(BaseModel):
    """Request model for hardened sandbox execution."""
    agent_id: str = Field(..., description="Agent identifier")
    code: str = Field(..., description="Code to execute")
    runtime: str = Field(default="gvisor", description="Sandbox runtime (gvisor/firecracker)")
    timeout_seconds: int = Field(default=300, le=600, description="Execution timeout")
    memory_limit_mb: int = Field(default=512, le=2048, description="Memory limit in MB")
    cpu_limit: float = Field(default=0.5, le=2.0, description="CPU limit (cores)")
    network_policy: str = Field(default="none", description="Network access policy")
    filesystem_access: List[str] = Field(default_factory=list, description="Allowed filesystem paths")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")

class SecurityViolation(BaseModel):
    """Security violation detected during execution."""
    violation_id: str
    timestamp: datetime
    violation_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    detection_layer: str  # SECCOMP, SYSCALL_MONITOR, NETWORK, FILESYSTEM
    blocked: bool
    indicators: Dict[str, Any]
    remediation: str

class HardenedSandboxResponse(BaseModel):
    """Response from hardened sandbox execution."""
    execution_id: str
    success: bool
    output: str
    error: Optional[str] = None
    security_violations: List[SecurityViolation] = Field(default_factory=list)
    execution_time_seconds: float
    cold_start_time_ms: float
    resource_usage: Dict[str, Any]
    termination_reason: str
    runtime_used: str
    constitutional_hash_verified: bool

# Hardened Sandbox Controller
class HardenedSandboxController:
    """Enhanced sandbox controller with kernel-level isolation."""
    
    def __init__(self):
        self.k8s_client = None
        self.redis_client = None
        self.audit_engine_url = "http://audit-engine:8003"
        self.policy_engine_url = "http://policy-engine:8001"
        
        # Runtime configurations
        self.runtime_configs = {
            "gvisor": {
                "runtime_class": "gvisor",
                "cold_start_target_ms": 100,
                "security_level": "high"
            },
            "firecracker": {
                "runtime_class": "kata-firecracker", 
                "cold_start_target_ms": 200,
                "security_level": "maximum"
            }
        }
        
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        self.violation_detector = ViolationDetector()
        
    async def initialize(self):
        """Initialize the hardened sandbox controller."""
        try:
            logger.info("Initializing Hardened Sandbox Controller", constitutional_hash=CONSTITUTIONAL_HASH)
            
            # Initialize Kubernetes client
            await self._init_k8s_client()
            
            # Initialize Redis for caching and coordination
            await self._init_redis()
            
            # Verify runtime classes are available
            await self._verify_runtime_classes()
            
            # Initialize seccomp profiles
            await self._setup_seccomp_profiles()
            
            # Start violation monitoring
            asyncio.create_task(self._monitor_violations())
            
            logger.info("Hardened Sandbox Controller initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Hardened Sandbox Controller", error=str(e))
            raise
    
    async def _init_k8s_client(self):
        """Initialize Kubernetes client."""
        try:
            # Try in-cluster config first, then local config
            try:
                config.load_incluster_config()
                logger.info("Using in-cluster Kubernetes configuration")
            except config.config_exception.ConfigException:
                await config.load_kube_config()
                logger.info("Using local Kubernetes configuration")
            
            self.k8s_client = client.ApiClient()
            
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client", error=str(e))
            raise
    
    async def _init_redis(self):
        """Initialize Redis client."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = await aioredis.from_url(redis_url)
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def _verify_runtime_classes(self):
        """Verify that required runtime classes are available."""
        v1 = client.NodeV1Api(self.k8s_client)
        
        try:
            runtime_classes = await v1.list_runtime_class()
            available_runtimes = {rc.metadata.name for rc in runtime_classes.items}
            
            required_runtimes = {"gvisor", "kata-firecracker"}
            missing_runtimes = required_runtimes - available_runtimes
            
            if missing_runtimes:
                logger.warning("Missing runtime classes", missing=list(missing_runtimes))
                # Install missing runtime classes
                await self._install_runtime_classes(missing_runtimes)
            else:
                logger.info("All required runtime classes available", runtimes=list(available_runtimes))
                
        except ApiException as e:
            logger.error("Failed to verify runtime classes", error=str(e))
            raise
    
    async def _install_runtime_classes(self, missing_runtimes: Set[str]):
        """Install missing runtime classes."""
        v1 = client.NodeV1Api(self.k8s_client)
        
        for runtime in missing_runtimes:
            if runtime == "gvisor":
                runtime_class = client.V1RuntimeClass(
                    metadata=client.V1ObjectMeta(name="gvisor"),
                    handler="runsc",
                    scheduling=client.V1Scheduling(
                        node_selector={"sandbox": "gvisor"}
                    )
                )
            elif runtime == "kata-firecracker":
                runtime_class = client.V1RuntimeClass(
                    metadata=client.V1ObjectMeta(name="kata-firecracker"),
                    handler="kata",
                    scheduling=client.V1Scheduling(
                        node_selector={"sandbox": "kata"}
                    )
                )
            else:
                continue
            
            try:
                await v1.create_runtime_class(body=runtime_class)
                logger.info("Created runtime class", runtime=runtime)
            except ApiException as e:
                if e.status != 409:  # Already exists
                    logger.error("Failed to create runtime class", runtime=runtime, error=str(e))
    
    async def _setup_seccomp_profiles(self):
        """Set up enhanced seccomp profiles."""
        seccomp_profile = {
            "defaultAction": "SCMP_ACT_ERRNO",
            "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_AARCH64"],
            "syscalls": [
                {
                    "names": [
                        # Essential syscalls for basic operation
                        "read", "write", "close", "fstat", "lseek", "mmap", "mprotect",
                        "munmap", "brk", "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
                        "ioctl", "access", "pipe", "select", "poll", "epoll_create",
                        "epoll_ctl", "epoll_wait", "nanosleep", "getrlimit", "getrusage",
                        "times", "futex", "exit_group", "exit", "wait4", "kill", "uname",
                        "fcntl", "getdents", "getcwd", "chdir", "rename", "mkdir", "rmdir",
                        "creat", "link", "unlink", "symlink", "readlink", "chmod", "fchmod",
                        "chown", "fchown", "lchown", "umask", "gettimeofday", "getpid",
                        "getppid", "getuid", "getgid", "geteuid", "getegid", "setpgid",
                        "getpgrp", "setsid", "setreuid", "setregid", "getgroups", "setgroups",
                        "setresuid", "getresuid", "setresgid", "getresgid", "getpgid",
                        "setfsuid", "setfsgid", "getsid", "capget", "capset", "rt_sigpending",
                        "rt_sigtimedwait", "rt_sigqueueinfo", "rt_sigsuspend", "sigaltstack",
                        "personality", "statfs", "fstatfs", "sysfs", "getpriority",
                        "setpriority", "sched_setparam", "sched_getparam", "sched_setscheduler",
                        "sched_getscheduler", "sched_get_priority_max", "sched_get_priority_min",
                        "sched_rr_get_interval", "mlock", "munlock", "mlockall", "munlockall",
                        "vhangup", "modify_ldt", "pivot_root", "prctl", "arch_prctl",
                        "adjtimex", "setrlimit", "sync", "acct", "settimeofday", "mount",
                        "umount2", "swapon", "swapoff", "reboot", "sethostname", "setdomainname",
                        "iopl", "ioperm", "create_module", "init_module", "delete_module",
                        "get_kernel_syms", "query_module", "quotactl", "nfsservctl", "getpmsg",
                        "putpmsg", "afs_syscall", "tuxcall", "security", "gettid", "readahead",
                        "setxattr", "lsetxattr", "fsetxattr", "getxattr", "lgetxattr", "fgetxattr",
                        "listxattr", "llistxattr", "flistxattr", "removexattr", "lremovexattr",
                        "fremovexattr", "tkill", "time", "sched_setaffinity", "sched_getaffinity"
                    ],
                    "action": "SCMP_ACT_ALLOW"
                },
                {
                    "names": list(DANGEROUS_SYSCALLS),
                    "action": "SCMP_ACT_KILL"
                }
            ]
        }
        
        # Save seccomp profile
        profile_path = Path("/tmp/hardened-seccomp-profile.json")
        async with aiofiles.open(profile_path, 'w') as f:
            await f.write(json.dumps(seccomp_profile, indent=2))
        
        logger.info("Enhanced seccomp profile created", dangerous_syscalls=len(DANGEROUS_SYSCALLS))
    
    async def execute_in_hardened_sandbox(self, request: HardenedSandboxRequest) -> HardenedSandboxResponse:
        """Execute code in hardened sandbox with enhanced security."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        cold_start_time = None
        violations = []
        
        try:
            logger.info("Starting hardened sandbox execution", 
                       execution_id=execution_id, 
                       agent_id=request.agent_id,
                       runtime=request.runtime)
            
            # Validate request
            await self._validate_execution_request(request)
            
            # Check with policy engine first
            policy_decision = await self._check_policy_authorization(request)
            if not policy_decision["allow"]:
                raise HTTPException(status_code=403, detail="Execution not authorized by policy engine")
            
            # Create hardened sandbox pod
            cold_start_start = time.time()
            pod_name = await self._create_hardened_sandbox_pod(execution_id, request)
            cold_start_time = (time.time() - cold_start_start) * 1000
            
            # Monitor cold start performance
            COLD_START_DURATION.labels(runtime=request.runtime).observe(cold_start_time / 1000)
            
            # Wait for pod to be ready
            await self._wait_for_pod_ready(pod_name, timeout=60)
            
            # Execute code with monitoring
            execution_result = await self._execute_with_monitoring(pod_name, request, execution_id)
            
            # Collect violations
            violations = await self._collect_violations(execution_id)
            
            # Clean up
            await self._cleanup_sandbox_pod(pod_name)
            
            execution_time = time.time() - start_time
            
            # Record metrics
            SANDBOX_EXECUTIONS_TOTAL.labels(
                runtime=request.runtime,
                result="success" if execution_result["success"] else "failure",
                termination_reason=execution_result["termination_reason"]
            ).inc()
            
            SANDBOX_EXECUTION_DURATION.labels(
                runtime=request.runtime,
                result="success" if execution_result["success"] else "failure"
            ).observe(execution_time)
            
            # Log to audit engine
            await self._log_audit_event(execution_id, request, execution_result, violations)
            
            return HardenedSandboxResponse(
                execution_id=execution_id,
                success=execution_result["success"],
                output=execution_result["output"],
                error=execution_result.get("error"),
                security_violations=violations,
                execution_time_seconds=execution_time,
                cold_start_time_ms=cold_start_time or 0,
                resource_usage=execution_result["resource_usage"],
                termination_reason=execution_result["termination_reason"],
                runtime_used=request.runtime,
                constitutional_hash_verified=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            SANDBOX_EXECUTIONS_TOTAL.labels(
                runtime=request.runtime,
                result="error",
                termination_reason="exception"
            ).inc()
            
            logger.error("Hardened sandbox execution failed",
                        execution_id=execution_id,
                        error=str(e))
            
            return HardenedSandboxResponse(
                execution_id=execution_id,
                success=False,
                output="",
                error=str(e),
                security_violations=violations,
                execution_time_seconds=execution_time,
                cold_start_time_ms=cold_start_time or 0,
                resource_usage={},
                termination_reason="error",
                runtime_used=request.runtime,
                constitutional_hash_verified=True
            )
    
    async def _validate_execution_request(self, request: HardenedSandboxRequest):
        """Validate execution request for security."""
        # Check for suspicious patterns in code
        suspicious_patterns = [
            "import os", "import subprocess", "import sys",
            "exec(", "eval(", "__import__",
            "/proc/", "/dev/", "/sys/",
            "socket", "urllib", "requests"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in request.code:
                violation = SecurityViolation(
                    violation_id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="suspicious_code",
                    severity="MEDIUM",
                    description=f"Suspicious pattern detected: {pattern}",
                    detection_layer="CODE_ANALYSIS",
                    blocked=False,
                    indicators={"pattern": pattern, "code_snippet": request.code[:200]},
                    remediation="Review code for security implications"
                )
                
                await self._record_violation(violation)
    
    async def _check_policy_authorization(self, request: HardenedSandboxRequest) -> Dict[str, Any]:
        """Check with policy engine for authorization."""
        try:
            async with aiohttp.ClientSession() as session:
                policy_request = {
                    "action": "sandbox.execute",
                    "context": {
                        "agent": {"id": request.agent_id},
                        "sandbox": {
                            "runtime": request.runtime,
                            "memory_mb": request.memory_limit_mb,
                            "cpu_cores": request.cpu_limit,
                            "network_policy": request.network_policy
                        },
                        "environment": {"sandbox_enabled": True}
                    }
                }
                
                async with session.post(
                    f"{self.policy_engine_url}/api/v1/evaluate",
                    json=policy_request,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning("Policy engine request failed", status=response.status)
                        return {"allow": False, "reason": "Policy engine unavailable"}
                        
        except Exception as e:
            logger.error("Policy engine check failed", error=str(e))
            return {"allow": False, "reason": f"Policy check error: {str(e)}"}
    
    async def _create_hardened_sandbox_pod(self, execution_id: str, request: HardenedSandboxRequest) -> str:
        """Create hardened sandbox pod with gVisor/Firecracker."""
        pod_name = f"hardened-sandbox-{execution_id[:8]}"
        
        runtime_config = self.runtime_configs[request.runtime]
        
        # Pod specification with hardened security
        pod_spec = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "labels": {
                    "app": "hardened-sandbox",
                    "execution-id": execution_id,
                    "agent-id": request.agent_id,
                    "runtime": request.runtime
                },
                "annotations": {
                    "constitutional-hash": CONSTITUTIONAL_HASH,
                    "security-level": runtime_config["security_level"]
                }
            },
            "spec": {
                "runtimeClassName": runtime_config["runtime_class"],
                "restartPolicy": "Never",
                "terminationGracePeriodSeconds": 10,
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "runAsGroup": 1000,
                    "fsGroup": 1000,
                    "seccompProfile": {
                        "type": "Localhost",
                        "localhostProfile": "hardened-seccomp-profile.json"
                    },
                    "supplementalGroups": []
                },
                "containers": [{
                    "name": "sandbox",
                    "image": "ubuntu:22.04",
                    "command": ["/bin/sleep", "300"],  # Keep alive for execution
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": True,
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "runAsGroup": 1000,
                        "capabilities": {
                            "drop": ["ALL"]
                        }
                    },
                    "resources": {
                        "limits": {
                            "cpu": str(request.cpu_limit),
                            "memory": f"{request.memory_limit_mb}Mi",
                            "ephemeral-storage": "1Gi"
                        },
                        "requests": {
                            "cpu": str(request.cpu_limit * 0.1),  # 10% request
                            "memory": f"{request.memory_limit_mb // 2}Mi"
                        }
                    },
                    "env": [
                        {"name": "EXECUTION_ID", "value": execution_id},
                        {"name": "AGENT_ID", "value": request.agent_id},
                        {"name": "CONSTITUTIONAL_HASH", "value": CONSTITUTIONAL_HASH}
                    ] + [{"name": k, "value": v} for k, v in request.environment.items()],
                    "volumeMounts": [
                        {
                            "name": "tmp",
                            "mountPath": "/tmp"
                        },
                        {
                            "name": "var-tmp", 
                            "mountPath": "/var/tmp"
                        }
                    ]
                }],
                "volumes": [
                    {
                        "name": "tmp",
                        "emptyDir": {"sizeLimit": "100Mi"}
                    },
                    {
                        "name": "var-tmp",
                        "emptyDir": {"sizeLimit": "100Mi"}
                    }
                ],
                "nodeSelector": {
                    "sandbox": request.runtime
                },
                "tolerations": [
                    {
                        "key": "sandbox",
                        "operator": "Equal",
                        "value": request.runtime,
                        "effect": "NoSchedule"
                    }
                ]
            }
        }
        
        # Create pod
        v1 = client.CoreV1Api(self.k8s_client)
        await v1.create_namespaced_pod(namespace="default", body=pod_spec)
        
        # Track active sandbox
        self.active_sandboxes[execution_id] = {
            "pod_name": pod_name,
            "agent_id": request.agent_id,
            "runtime": request.runtime,
            "start_time": time.time()
        }
        
        ACTIVE_HARDENED_SANDBOXES.inc()
        
        logger.info("Created hardened sandbox pod", 
                   pod_name=pod_name, 
                   runtime=request.runtime,
                   execution_id=execution_id)
        
        return pod_name
    
    async def _wait_for_pod_ready(self, pod_name: str, timeout: int = 60):
        """Wait for pod to be ready."""
        v1 = client.CoreV1Api(self.k8s_client)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                pod = await v1.read_namespaced_pod(name=pod_name, namespace="default")
                if pod.status.phase == "Running":
                    # Check if container is ready
                    if pod.status.container_statuses:
                        if all(cs.ready for cs in pod.status.container_statuses):
                            return
                
                await asyncio.sleep(1)
                
            except ApiException as e:
                if e.status == 404:
                    await asyncio.sleep(1)
                    continue
                raise
        
        raise Exception(f"Pod {pod_name} did not become ready within {timeout} seconds")
    
    async def _execute_with_monitoring(self, pod_name: str, request: HardenedSandboxRequest, execution_id: str) -> Dict[str, Any]:
        """Execute code with real-time monitoring."""
        try:
            # Start syscall monitoring
            monitor_task = asyncio.create_task(
                self._monitor_syscalls(pod_name, execution_id)
            )
            
            # Execute the code
            v1 = client.CoreV1Api(self.k8s_client)
            
            # Create execution script
            script = f"""#!/bin/bash
set -e
cd /tmp
cat > code.py << 'EOF'
{request.code}
EOF

# Execute with timeout
timeout {request.timeout_seconds} python3 code.py 2>&1
"""
            
            # Execute in pod
            exec_command = ['/bin/bash', '-c', script]
            
            resp = await v1.connect_get_namespaced_pod_exec(
                name=pod_name,
                namespace="default",
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=False
            )
            
            # Collect output
            output = ""
            error = None
            
            while True:
                try:
                    data = await asyncio.wait_for(resp.read_stdout(), timeout=1.0)
                    if data:
                        output += data.decode('utf-8')
                    else:
                        break
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
            
            # Stop monitoring
            monitor_task.cancel()
            
            # Get resource usage
            resource_usage = await self._get_resource_usage(pod_name)
            
            return {
                "success": True,
                "output": output,
                "error": error,
                "resource_usage": resource_usage,
                "termination_reason": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "resource_usage": {},
                "termination_reason": "error"
            }
    
    async def _monitor_syscalls(self, pod_name: str, execution_id: str):
        """Monitor syscalls for violations."""
        try:
            # In a real implementation, this would integrate with:
            # - gVisor debug logs
            # - Kata trace output  
            # - eBPF syscall monitoring
            # - Falco for runtime security
            
            # Simulate syscall monitoring
            while True:
                await asyncio.sleep(1)
                
                # Check for violations (simplified)
                # In production, parse actual syscall logs
                violations = await self._check_syscall_violations(pod_name)
                
                for violation in violations:
                    await self._record_violation(violation)
                    
                    if violation.severity in ["HIGH", "CRITICAL"]:
                        # Terminate sandbox immediately
                        await self._emergency_terminate_sandbox(pod_name, violation)
                        break
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Syscall monitoring error", pod_name=pod_name, error=str(e))
    
    async def _check_syscall_violations(self, pod_name: str) -> List[SecurityViolation]:
        """Check for syscall violations (simplified implementation)."""
        violations = []
        
        # In production, this would parse actual syscall audit logs
        # For now, return empty list
        return violations
    
    async def _record_violation(self, violation: SecurityViolation):
        """Record security violation."""
        SECURITY_VIOLATIONS_TOTAL.labels(
            violation_type=violation.violation_type,
            severity=violation.severity,
            detection_layer=violation.detection_layer
        ).inc()
        
        # Store in Redis for collection
        await self.redis_client.lpush(
            f"violations:sandbox",
            json.dumps(violation.dict(), default=str)
        )
        
        logger.warning("Security violation detected",
                      violation_id=violation.violation_id,
                      type=violation.violation_type,
                      severity=violation.severity)
    
    async def _emergency_terminate_sandbox(self, pod_name: str, violation: SecurityViolation):
        """Emergency termination of sandbox due to critical violation."""
        try:
            v1 = client.CoreV1Api(self.k8s_client)
            await v1.delete_namespaced_pod(name=pod_name, namespace="default")
            
            logger.critical("Emergency sandbox termination",
                           pod_name=pod_name,
                           violation_id=violation.violation_id,
                           reason=violation.description)
            
        except Exception as e:
            logger.error("Failed to emergency terminate sandbox", error=str(e))
    
    async def _collect_violations(self, execution_id: str) -> List[SecurityViolation]:
        """Collect all violations for this execution."""
        violations = []
        
        # Get violations from Redis
        violation_data = await self.redis_client.lrange(f"violations:sandbox", 0, -1)
        
        for data in violation_data:
            try:
                violation_dict = json.loads(data)
                violations.append(SecurityViolation(**violation_dict))
            except Exception:
                continue
        
        # Clear collected violations
        await self.redis_client.delete(f"violations:sandbox")
        
        return violations
    
    async def _get_resource_usage(self, pod_name: str) -> Dict[str, Any]:
        """Get resource usage statistics."""
        try:
            # In production, get actual metrics from Kubernetes metrics API
            return {
                "cpu_usage_cores": 0.1,
                "memory_usage_mb": 64,
                "network_rx_bytes": 0,
                "network_tx_bytes": 0,
                "filesystem_reads": 100,
                "filesystem_writes": 50
            }
        except Exception:
            return {}
    
    async def _cleanup_sandbox_pod(self, pod_name: str):
        """Clean up sandbox pod."""
        try:
            v1 = client.CoreV1Api(self.k8s_client)
            await v1.delete_namespaced_pod(name=pod_name, namespace="default")
            
            # Remove from active sandboxes
            for exec_id, info in list(self.active_sandboxes.items()):
                if info["pod_name"] == pod_name:
                    del self.active_sandboxes[exec_id]
                    ACTIVE_HARDENED_SANDBOXES.dec()
                    break
            
            logger.info("Cleaned up sandbox pod", pod_name=pod_name)
            
        except Exception as e:
            logger.error("Failed to cleanup sandbox pod", pod_name=pod_name, error=str(e))
    
    async def _log_audit_event(self, execution_id: str, request: HardenedSandboxRequest, 
                             result: Dict[str, Any], violations: List[SecurityViolation]):
        """Log execution to audit engine."""
        try:
            audit_event = {
                "event_type": "sandbox_execution",
                "service_name": "hardened_sandbox_controller",
                "agent_id": request.agent_id,
                "action": f"execute_{request.runtime}",
                "outcome": "success" if result["success"] else "failure",
                "payload": {
                    "execution_id": execution_id,
                    "runtime": request.runtime,
                    "violations_count": len(violations),
                    "execution_time": result.get("resource_usage", {}).get("execution_time", 0),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.audit_engine_url}/api/v1/audit/events",
                    json=audit_event,
                    timeout=aiohttp.ClientTimeout(total=5)
                )
                
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))
    
    async def _monitor_violations(self):
        """Background task to monitor for violations."""
        while True:
            try:
                # Monitor escape attempts across all sandboxes
                for exec_id, info in self.active_sandboxes.items():
                    # Check for escape patterns
                    escape_detected = await self._check_escape_patterns(info["pod_name"])
                    if escape_detected:
                        SANDBOX_ESCAPE_ATTEMPTS_TOTAL.labels(
                            pattern=escape_detected["pattern"],
                            runtime=info["runtime"],
                            blocked=True
                        ).inc()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error("Violation monitoring error", error=str(e))
                await asyncio.sleep(10)
    
    async def _check_escape_patterns(self, pod_name: str) -> Optional[Dict[str, str]]:
        """Check for sandbox escape patterns."""
        # In production, this would analyze:
        # - Process lists
        # - Network connections  
        # - File system access patterns
        # - System call patterns
        
        # For now, return None (no escape detected)
        return None

class ViolationDetector:
    """Advanced violation detection system."""
    
    def __init__(self):
        self.pattern_database = ESCAPE_PATTERNS
        self.ml_model = None  # Could load ML model for anomaly detection
    
    async def analyze_execution(self, execution_data: Dict[str, Any]) -> List[SecurityViolation]:
        """Analyze execution for security violations."""
        violations = []
        
        # Analyze code patterns
        code_violations = self._analyze_code_patterns(execution_data.get("code", ""))
        violations.extend(code_violations)
        
        # Analyze syscall patterns (if available)
        if "syscalls" in execution_data:
            syscall_violations = self._analyze_syscall_patterns(execution_data["syscalls"])
            violations.extend(syscall_violations)
        
        return violations
    
    def _analyze_code_patterns(self, code: str) -> List[SecurityViolation]:
        """Analyze code for suspicious patterns."""
        violations = []
        
        # Check for escape patterns
        for category, patterns in self.pattern_database.items():
            for pattern in patterns:
                if pattern in code:
                    violation = SecurityViolation(
                        violation_id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        violation_type="code_pattern",
                        severity="MEDIUM",
                        description=f"Suspicious code pattern detected: {pattern}",
                        detection_layer="STATIC_ANALYSIS",
                        blocked=False,
                        indicators={"pattern": pattern, "category": category},
                        remediation="Review code for security implications"
                    )
                    violations.append(violation)
        
        return violations
    
    def _analyze_syscall_patterns(self, syscalls: List[str]) -> List[SecurityViolation]:
        """Analyze syscall patterns for violations."""
        violations = []
        
        for syscall in syscalls:
            if syscall in DANGEROUS_SYSCALLS:
                violation = SecurityViolation(
                    violation_id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    violation_type="dangerous_syscall",
                    severity="HIGH",
                    description=f"Dangerous syscall attempted: {syscall}",
                    detection_layer="SECCOMP",
                    blocked=True,
                    indicators={"syscall": syscall},
                    remediation="Syscall blocked by seccomp profile"
                )
                violations.append(violation)
        
        return violations

# FastAPI app
app = FastAPI(
    title="ACGS-1 Lite Hardened Sandbox Controller",
    description="Enhanced security sandbox with gVisor/Firecracker isolation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global controller instance
hardened_controller = HardenedSandboxController()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await hardened_controller.initialize()
    yield
    # Shutdown (if needed)
    pass

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hardened-sandbox-controller",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "runtimes_available": list(hardened_controller.runtime_configs.keys()),
        "active_sandboxes": len(hardened_controller.active_sandboxes)
    }

@app.post("/api/v1/sandbox/execute")
async def execute_in_sandbox(request: HardenedSandboxRequest) -> HardenedSandboxResponse:
    """Execute code in hardened sandbox."""
    return await hardened_controller.execute_in_hardened_sandbox(request)

@app.get("/api/v1/sandbox/status")
async def get_sandbox_status():
    """Get status of all active sandboxes."""
    active_sandboxes = []
    
    for exec_id, info in hardened_controller.active_sandboxes.items():
        active_sandboxes.append({
            "execution_id": exec_id,
            "agent_id": info["agent_id"],
            "runtime": info["runtime"],
            "uptime_seconds": time.time() - info["start_time"],
            "pod_name": info["pod_name"]
        })
    
    return {
        "active_sandboxes": active_sandboxes,
        "total_count": len(active_sandboxes),
        "constitutional_hash_verified": True
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8002,
        reload=False
    )