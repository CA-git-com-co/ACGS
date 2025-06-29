# ACGS-1 Lite Hardened Sandbox Controller

Maximum security sandbox controller with kernel-level isolation using gVisor and Firecracker for AI agent execution.

## 🔒 Security Features

- **Kernel-Level Isolation**: gVisor user-space kernel and Firecracker microVMs
- **Enhanced Seccomp Profiles**: Blocks 30+ dangerous syscalls at kernel level
- **Real-time Violation Detection**: Monitors and blocks escape attempts
- **Network Isolation**: Zero external network access by default
- **Resource Limits**: Strict CPU, memory, and filesystem constraints
- **Constitutional Verification**: Built-in hash validation (`cdd01ef066bc6cf2`)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agents     │    │ Hardened        │    │   Runtimes      │
│                 │    │ Sandbox         │    │                 │
│ Policy Engine   │────┤ Controller      │────┤ gVisor (runsc)  │
│ Evolution Mgr   │    │ Port 8002       │    │ Firecracker     │
│ Other Services  │    │                 │    │ (Kata)          │
└─────────────────┘    │ - Security      │    └─────────────────┘
                       │   Monitoring    │    
┌─────────────────┐    │ - Syscall       │    ┌─────────────────┐
│   Storage       │    │   Filtering     │    │  Kubernetes     │
│                 │    │ - Violation     │    │                 │
│ Audit Engine    │────┤   Detection     │────┤ RuntimeClasses  │
│ Redis Cache     │    │ - Resource      │    │ NetworkPolicies │
│ Prometheus      │    │   Limits        │    │ SecurityPolicies│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster with admin access
- Docker for building images
- Nodes with KVM support (for Firecracker)
- kubectl configured for cluster access

### 1. Node Preparation

**For gVisor runtime:**
```bash
# Run on each node that will run gVisor sandboxes
sudo ./setup-gvisor.sh
```

**For Firecracker runtime:**
```bash
# Run on each node that will run Firecracker sandboxes  
sudo ./setup-firecracker.sh
```

### 2. Deploy Controller

```bash
# Deploy hardened sandbox controller
./deploy.sh
```

### 3. Verify Deployment

```bash
# Check deployment status
kubectl get pods -n acgs-hardened-sandbox

# Port forward for testing
kubectl port-forward -n acgs-hardened-sandbox service/hardened-sandbox-controller 8002:8002

# Test execution
curl -X POST http://localhost:8002/api/v1/sandbox/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": "test_agent",
    "code": "print(\"Hello from hardened sandbox!\")",
    "runtime": "gvisor"
  }'
```

## 🔧 Configuration

### Runtime Selection

**gVisor (User-space Kernel):**
- Cold start: <100ms target
- Security level: High
- Resource overhead: ~10-15%
- Best for: CPU-intensive workloads

**Firecracker (microVM):**
- Cold start: <200ms target  
- Security level: Maximum
- Resource overhead: ~20-30%
- Best for: Maximum isolation requirements

### Resource Limits

```json
{
  "memory_limit_mb": 512,     // Max 2048MB
  "cpu_limit": 0.5,          // Max 2.0 cores
  "timeout_seconds": 300,     // Max 600 seconds
  "network_policy": "none"    // none/restricted/full
}
```

### Security Policies

**Blocked Syscalls:**
- `ptrace`, `mount`, `umount`, `chroot`
- `setns`, `unshare`, `clone`, `fork`
- `kexec_load`, `reboot`, `init_module`
- `quotactl`, `syslog`, `swapon`
- And 20+ more dangerous calls

**Escape Detection Patterns:**
- Container runtime access
- Privileged file system access  
- Device file manipulation
- Network escape attempts
- Process spawning violations

## 📡 API Reference

### Execute in Hardened Sandbox

**POST** `/api/v1/sandbox/execute`

```json
{
  "agent_id": "string",           // Required: Agent identifier
  "code": "string",               // Required: Code to execute
  "runtime": "gvisor|firecracker", // Optional: Runtime (default: gvisor)
  "timeout_seconds": 300,         // Optional: Execution timeout
  "memory_limit_mb": 512,         // Optional: Memory limit
  "cpu_limit": 0.5,              // Optional: CPU limit
  "network_policy": "none",       // Optional: Network access
  "filesystem_access": [],        // Optional: Allowed paths
  "environment": {}               // Optional: Environment variables
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "success": true,
  "output": "string",
  "error": null,
  "security_violations": [
    {
      "violation_id": "uuid",
      "timestamp": "2025-01-01T00:00:00Z",
      "violation_type": "string",
      "severity": "HIGH",
      "description": "string",
      "detection_layer": "SECCOMP",
      "blocked": true,
      "indicators": {},
      "remediation": "string"
    }
  ],
  "execution_time_seconds": 1.234,
  "cold_start_time_ms": 56.78,
  "resource_usage": {
    "cpu_usage_cores": 0.1,
    "memory_usage_mb": 64,
    "network_rx_bytes": 0,
    "network_tx_bytes": 0
  },
  "termination_reason": "completed",
  "runtime_used": "gvisor",
  "constitutional_hash_verified": true
}
```

### Get Sandbox Status

**GET** `/api/v1/sandbox/status`

```json
{
  "active_sandboxes": [
    {
      "execution_id": "uuid",
      "agent_id": "string", 
      "runtime": "gvisor",
      "uptime_seconds": 45.67,
      "pod_name": "string"
    }
  ],
  "total_count": 1,
  "constitutional_hash_verified": true
}
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "hardened-sandbox-controller",
  "version": "1.0.0",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "runtimes_available": ["gvisor", "firecracker"],
  "active_sandboxes": 0
}
```

## 📊 Monitoring

### Prometheus Metrics

**Key Metrics:**
- `hardened_sandbox_executions_total`: Total executions by runtime/result
- `hardened_sandbox_violations_total`: Security violations by type/severity
- `hardened_sandbox_escape_attempts_total`: Escape attempts by pattern
- `hardened_sandbox_cold_start_duration_seconds`: Cold start performance
- `active_hardened_sandboxes_count`: Currently active sandboxes

**Example Queries:**
```promql
# P95 cold start latency by runtime
histogram_quantile(0.95, hardened_sandbox_cold_start_duration_seconds_bucket)

# Security violation rate
rate(hardened_sandbox_violations_total[5m])

# Runtime success rate
rate(hardened_sandbox_executions_total{result="success"}[5m]) / 
rate(hardened_sandbox_executions_total[5m])
```

### Grafana Dashboard

Import the provided Grafana dashboard for comprehensive monitoring:
- Cold start performance trends
- Security violation patterns
- Resource usage by runtime
- Success/failure rates
- Active sandbox tracking

## 🧪 Testing

### Security Tests

```bash
# Run comprehensive security test suite
cd tests/
python test_security_hardening.py

# Run penetration tests
pytest test_security_hardening.py::TestHardenedSandboxSecurity -v

# Test escape attempt detection
pytest test_security_hardening.py::test_escape_attempt_detection -v
```

### Performance Tests

```bash
# Test cold start performance
pytest test_security_hardening.py::test_cold_start_performance -v

# Test concurrent execution
pytest test_security_hardening.py::test_concurrent_execution -v

# Full performance suite
pytest test_security_hardening.py::TestHardenedSandboxPerformance -v
```

### Integration Tests

```bash
# Test policy engine integration
pytest test_security_hardening.py::test_policy_engine_integration -v

# Test audit logging
pytest test_security_hardening.py::test_audit_logging_integration -v
```

## 🔧 Troubleshooting

### Common Issues

**1. Cold Start Timeout**
```bash
# Check node resources
kubectl describe node <node-name>

# Check runtime installation
kubectl get runtimeclass

# Verify seccomp profiles
kubectl get configmap hardened-seccomp-profile -n acgs-hardened-sandbox
```

**2. Security Violations**
```bash
# Check violation logs
kubectl logs -n acgs-hardened-sandbox -l app=hardened-sandbox-controller | grep violation

# Review seccomp denials
dmesg | grep SECCOMP

# Check syscall blocking
journalctl -u containerd | grep runsc
```

**3. Runtime Failures**
```bash
# gVisor troubleshooting
runsc list
runsc --debug logs <container-id>

# Firecracker troubleshooting  
kata-runtime kata-check
journalctl -u kata-containers
```

### Performance Optimization

**gVisor Tuning:**
```toml
# /etc/containerd/runsc.toml
[runsc_config]
  platform = "kvm"        # Use KVM for better performance
  file-access = "shared"   # Shared file access mode
  network = "host"         # Host networking if allowed
```

**Firecracker Tuning:**
```toml
# /etc/kata-containers/configuration-fc.toml
[hypervisor.firecracker]
  default_vcpus = 2
  default_memory = 1024
  enable_iommu = true
```

### Debugging

**Enable Debug Logging:**
```yaml
# In deployment
env:
- name: LOG_LEVEL
  value: "DEBUG"
- name: ENABLE_SECURITY_DEBUG
  value: "true"
```

**Collect Debug Information:**
```bash
# Service logs
kubectl logs -n acgs-hardened-sandbox -l app=hardened-sandbox-controller --tail=1000

# System information
kata-runtime kata-env
runsc --version

# Node diagnostics
kubectl describe nodes -l sandbox=gvisor
kubectl describe nodes -l sandbox=kata
```

## 🔐 Security Considerations

### Production Deployment

1. **Node Isolation**: Dedicate specific nodes for sandbox workloads
2. **Network Segmentation**: Use NetworkPolicies to isolate sandbox traffic
3. **Resource Quotas**: Set cluster-level resource limits
4. **Monitoring**: Enable real-time security monitoring and alerting
5. **Updates**: Regularly update gVisor and Firecracker components

### Compliance

- **SOC 2**: Comprehensive audit logging and access controls
- **PCI DSS**: Network isolation and encryption in transit
- **GDPR**: Data minimization and secure processing
- **Constitutional**: Built-in constitutional hash verification

### Known Limitations

1. **Performance Overhead**: 10-30% resource overhead depending on runtime
2. **Cold Start Latency**: Initial startup time for isolation setup
3. **Syscall Compatibility**: Some legitimate syscalls may be blocked
4. **Resource Scaling**: Limited by node capacity for isolation

## 🏗️ Development

### Building from Source

```bash
# Clone repository
git clone <repository-url>
cd services/core/sandbox-controller/hardened

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t acgs-hardened-sandbox-controller .
```

### Contributing

1. Add security tests for new features
2. Update seccomp profiles when adding syscall support
3. Document security implications
4. Test with both gVisor and Firecracker runtimes

### Architecture Decisions

**Why gVisor + Firecracker?**
- Defense in depth: Multiple isolation layers
- Runtime flexibility: Choose based on workload requirements
- Performance options: Trade-off between speed and security

**Why Kubernetes?**
- Orchestration: Automatic scaling and recovery
- Resource management: Fine-grained resource controls
- Monitoring: Built-in metrics and logging integration

## 📚 References

- [gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker Security](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md#security-model)
- [Kata Containers](https://katacontainers.io/)
- [Kubernetes RuntimeClass](https://kubernetes.io/docs/concepts/containers/runtime-class/)
- [Seccomp Profiles](https://kubernetes.io/docs/tutorials/security/seccomp/)

## 📄 License

Constitutional AI Governance System (ACGS-1 Lite)
Constitutional Hash: `cdd01ef066bc6cf2`