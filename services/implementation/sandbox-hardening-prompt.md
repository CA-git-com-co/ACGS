# Sandbox Security Hardening Implementation Prompt

## Context
You are hardening the ACGS-1 Lite Sandbox Controller to use gVisor or Firecracker for enhanced isolation. The current implementation uses Docker with security constraints but needs kernel-level isolation to prevent AI agent escape attempts.

## Requirements

### Core Implementation
1. **Runtime Class Configuration**:
   ```yaml
   # For gVisor
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: gvisor
   handler: runsc
   scheduling:
     nodeSelector:
       sandbox: gvisor
   
   # For Kata/Firecracker
   apiVersion: node.k8s.io/v1
   kind: RuntimeClass
   metadata:
     name: kata-firecracker
   handler: kata
   ```

2. **Sandbox Controller Updates**:
   ```python
   # sandbox-controller/sandbox_executor.py
   async def create_sandbox_pod(self, agent_code: str) -> str:
       pod_spec = {
           "metadata": {
               "name": f"sandbox-{uuid.uuid4()}",
               "labels": {"app": "ai-agent-sandbox"}
           },
           "spec": {
               "runtimeClassName": "gvisor",  # or kata-firecracker
               "securityContext": {
                   "runAsNonRoot": True,
                   "runAsUser": 1000,
                   "fsGroup": 1000,
                   "seccompProfile": {
                       "type": "RuntimeDefault"
                   }
               },
               "containers": [{
                   "name": "agent",
                   "image": "sandbox-runtime:latest",
                   "resources": {
                       "limits": {"cpu": "1", "memory": "512Mi"},
                       "requests": {"cpu": "0.5", "memory": "256Mi"}
                   },
                   "securityContext": {
                       "allowPrivilegeEscalation": False,
                       "readOnlyRootFilesystem": True,
                       "capabilities": {"drop": ["ALL"]}
                   }
               }]
           }
       }
   ```

3. **Enhanced Seccomp Profiles**:
   ```json
   {
     "defaultAction": "SCMP_ACT_ERRNO",
     "architectures": ["SCMP_ARCH_X86_64"],
     "syscalls": [
       {
         "names": ["read", "write", "close", "fstat", "mmap", "mprotect", "munmap", "brk", "rt_sigaction", "rt_sigprocmask", "ioctl", "nanosleep", "select", "poll", "exit_group"],
         "action": "SCMP_ACT_ALLOW"
       }
     ]
   }
   ```

4. **Syscall Monitoring**:
   ```python
   class SyscallMonitor:
       async def monitor_container(self, container_id: str):
           # Use gVisor's debug logs or Kata's trace
           async for event in self.trace_syscalls(container_id):
               if event.syscall in DANGEROUS_SYSCALLS:
                   await self.alert_violation(event)
                   await self.terminate_container(container_id)
   ```

### Performance Requirements
- Cold start latency <100ms for gVisor, <200ms for Firecracker
- Memory overhead <50MB per sandbox
- Support 100+ concurrent sandboxes

### Security Requirements
- No direct kernel access from sandbox
- No network access unless explicitly allowed
- No persistent storage access
- Syscall filtering at kernel level

## Implementation Steps

1. **Node Preparation**:
   ```bash
   # Install gVisor
   curl -fsSL https://gvisor.dev/archive.key | sudo apt-key add -
   echo "deb https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list
   sudo apt-get update && sudo apt-get install -y runsc
   
   # Configure containerd for gVisor
   cat <<EOF | sudo tee /etc/containerd/config.toml
   [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
     runtime_type = "io.containerd.runsc.v1"
   EOF
   ```

2. **Kubernetes Configuration**:
   - Label nodes for sandbox workloads
   - Deploy RuntimeClass resources
   - Update sandbox pods to use new runtime

3. **Monitoring Integration**:
   - Export syscall violation metrics to Prometheus
   - Create Grafana dashboard for sandbox security events
   - Set up AlertManager rules for escape attempts

## Testing Requirements

1. **Security Testing**:
   - Run container escape tools (e.g., CDK)
   - Attempt privilege escalation
   - Test resource exhaustion attacks
   - Verify syscall blocking

2. **Performance Testing**:
   ```python
   async def benchmark_sandbox_startup():
       times = []
       for i in range(100):
           start = time.time()
           pod_id = await create_sandbox_pod(test_code)
           await wait_for_ready(pod_id)
           times.append(time.time() - start)
       
       assert np.percentile(times, 95) < 0.1  # 100ms P95
   ```

3. **Compatibility Testing**:
   - Verify AI agent code runs correctly
   - Test with various workload types
   - Ensure monitoring still functions

## Success Criteria
- [ ] Zero successful escapes in penetration testing
- [ ] All dangerous syscalls blocked at kernel level
- [ ] Cold start P95 latency <100ms
- [ ] Resource usage within 10% of Docker baseline
- [ ] Monitoring detects 100% of violation attempts