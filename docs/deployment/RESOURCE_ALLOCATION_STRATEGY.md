# ACGS-1 Lite Resource Allocation Strategy

## Overview

This document outlines the comprehensive resource allocation strategy for the Constitutional Trainer Service and all supporting components in the ACGS-1 Lite stack. The strategy ensures optimal performance, security, and cost-effectiveness while maintaining production-grade reliability.

## Resource Allocation Principles

### 1. **Security-First Approach**

- All containers must have resource limits to prevent resource exhaustion attacks
- Resource requests ensure guaranteed allocation for critical services
- Limits prevent any single service from consuming excessive cluster resources

### 2. **Performance Optimization**

- Resource requests based on observed baseline performance requirements
- Limits set with 2-3x headroom for peak load scenarios
- HPA configuration for automatic scaling based on resource utilization

### 3. **Cost Efficiency**

- Right-sized allocations to minimize waste
- Proportional scaling based on service criticality
- Efficient resource sharing through proper scheduling

## Service Resource Allocations

### Constitutional Trainer Service (Primary - GPU-Accelerated)

| Resource   | Request | Limit | Justification                                          |
| ---------- | ------- | ----- | ------------------------------------------------------ |
| **CPU**    | 500m    | 2000m | GPU-accelerated training with CPU coordination         |
| **Memory** | 2Gi     | 8Gi   | Large model processing and GPU memory coordination     |
| **GPU**    | 1       | 1     | NVIDIA GPU for constitutional AI training acceleration |

**Rationale:**

- Primary GPU-accelerated service for constitutional AI training
- Higher CPU allocation to coordinate with GPU operations
- Substantial memory allocation for large language model processing
- Single GPU allocation for cost-effective training acceleration
- Memory limits accommodate model loading, training data, and GPU coordination

### Policy Engine (Critical)

| Resource   | Request | Limit | Justification                               |
| ---------- | ------- | ----- | ------------------------------------------- |
| **CPU**    | 150m    | 400m  | Fast policy evaluation with OPA integration |
| **Memory** | 384Mi   | 768Mi | Policy rule caching and evaluation context  |

**Rationale:**

- Critical for constitutional compliance validation
- Lower baseline but sufficient burst for complex policy evaluations
- Memory allocation supports policy rule caching for performance
- Dual-container deployment (main + OPA) resource sharing

### Audit Engine (Essential)

| Resource   | Request | Limit | Justification                         |
| ---------- | ------- | ----- | ------------------------------------- |
| **CPU**    | 150m    | 300m  | Audit log processing and storage      |
| **Memory** | 384Mi   | 768Mi | Log buffering and database operations |

**Rationale:**

- Essential for compliance and audit trail integrity
- Moderate resource requirements for log processing
- Memory allocation supports batch processing and buffering
- Persistent storage for long-term audit retention

### Redis Cache (Supporting)

| Resource   | Request | Limit | Justification                        |
| ---------- | ------- | ----- | ------------------------------------ |
| **CPU**    | 100m    | 200m  | In-memory caching operations         |
| **Memory** | 256Mi   | 512Mi | Cache storage with eviction policies |

**Rationale:**

- Supporting service with predictable resource patterns
- Memory-focused workload with minimal CPU requirements
- Configured with LRU eviction for memory management
- Persistent storage for cache durability

## Resource Allocation Matrix

### Total Cluster Requirements

| Service                | CPU Request | CPU Limit | Memory Request | Memory Limit | GPU Request |
| ---------------------- | ----------- | --------- | -------------- | ------------ | ----------- |
| Constitutional Trainer | 500m        | 2000m     | 2Gi            | 8Gi          | 1           |
| Policy Engine          | 150m        | 400m      | 384Mi          | 768Mi        | 0           |
| Audit Engine           | 150m        | 300m      | 384Mi          | 768Mi        | 0           |
| Redis                  | 100m        | 200m      | 256Mi          | 512Mi        | 0           |
| **TOTAL**              | **900m**    | **2900m** | **3Gi**        | **10Gi**     | **1**       |

### Scaling Characteristics

| Service                | Min Replicas | Max Replicas | HPA Trigger           |
| ---------------------- | ------------ | ------------ | --------------------- |
| Constitutional Trainer | 2            | 8            | CPU: 70%, Memory: 80% |
| Policy Engine          | 2            | 6            | CPU: 70%, Memory: 80% |
| Audit Engine           | 2            | 6            | CPU: 70%, Memory: 80% |
| Redis                  | 1            | 3            | Memory: 85%           |

## Environment-Specific Allocations

### Development Environment

- **Resource Multiplier**: 0.5x (CPU/Memory), 1x (GPU)
- **Rationale**: Lower load, single-user testing, but full GPU for development
- **Total Requirements**: 450m CPU, 1.5Gi Memory, 1 GPU

### Staging Environment

- **Resource Multiplier**: 1.0x (baseline)
- **Rationale**: Production-like testing with realistic load
- **Total Requirements**: 900m CPU, 3Gi Memory, 1 GPU

### Production Environment

- **Resource Multiplier**: 1.5x (CPU/Memory), 1-2x (GPU)
- **Rationale**: Production load with safety margins and optional GPU scaling
- **Total Requirements**: 1350m CPU, 4.5Gi Memory, 1-2 GPUs

## Quality of Service (QoS) Classes

### Guaranteed QoS

- **Services**: Constitutional Trainer, Policy Engine
- **Configuration**: requests = limits
- **Benefit**: Highest priority, never evicted

### Burstable QoS

- **Services**: Audit Engine, Redis
- **Configuration**: requests < limits
- **Benefit**: Guaranteed baseline with burst capacity

## Node Sizing Recommendations

### GPU Node Requirements (Constitutional Trainer)

- **CPU**: 8 cores (8000m)
- **Memory**: 16Gi
- **GPU**: 1x NVIDIA GPU (T4, V100, A100, or equivalent)
- **Storage**: 100Gi SSD
- **Rationale**: Dedicated GPU node for constitutional AI training

### CPU Node Requirements (Supporting Services)

- **CPU**: 4 cores (4000m)
- **Memory**: 8Gi
- **Storage**: 50Gi SSD
- **Rationale**: Supports Policy Engine, Audit Engine, Redis, and monitoring

### High-Availability Configuration

- **GPU Nodes**: 1-2 nodes (for Constitutional Trainer scaling)
- **CPU Nodes**: 2-3 nodes (for supporting services)
- **Total Resources**: 12-20 cores, 32-48Gi Memory, 1-2 GPUs
- **Rationale**: Fault tolerance, load distribution, and GPU cost optimization

## Monitoring and Alerting

### Resource Utilization Alerts

| Metric             | Warning Threshold | Critical Threshold | Action                 |
| ------------------ | ----------------- | ------------------ | ---------------------- |
| CPU Utilization    | 70%               | 85%                | Scale up / Investigate |
| Memory Utilization | 75%               | 90%                | Scale up / Investigate |
| Disk Usage         | 80%               | 95%                | Cleanup / Expand       |
| Pod Restart Rate   | 5/hour            | 10/hour            | Investigate / Debug    |

### Performance Metrics

| Service                | SLA Target  | Monitoring Metric          |
| ---------------------- | ----------- | -------------------------- |
| Constitutional Trainer | P99 < 2s    | training_request_duration  |
| Policy Engine          | P99 < 25ms  | policy_evaluation_duration |
| Audit Engine           | P99 < 100ms | audit_log_write_duration   |
| Redis                  | P99 < 1ms   | cache_operation_duration   |

## Security Considerations

### Resource-Based Security

1. **Resource Limits**: Prevent DoS attacks through resource exhaustion
2. **Resource Requests**: Ensure service availability under load
3. **QoS Classes**: Protect critical services from resource starvation
4. **Node Affinity**: Isolate sensitive workloads on dedicated nodes

### Compliance Requirements

- **Resource Governance**: All containers must have defined limits
- **Audit Trail**: Resource allocation changes must be logged
- **Access Control**: Resource modifications require elevated privileges
- **Monitoring**: Continuous monitoring of resource utilization

## Implementation Guidelines

### Deployment Checklist

- [ ] Verify resource requests and limits in all manifests
- [ ] Configure HPA for scalable services
- [ ] Set up resource monitoring and alerting
- [ ] Test resource allocation under load
- [ ] Document any environment-specific adjustments

### Validation Commands

```bash
# Check resource configuration
kubectl describe deployment constitutional-trainer -n governance

# Monitor resource usage
kubectl top pods -n governance

# Verify HPA status
kubectl get hpa -n governance

# Check resource quotas
kubectl describe resourcequota -n governance
```

### Troubleshooting

#### Common Issues

1. **Pod Eviction**: Increase memory limits or requests
2. **Slow Performance**: Increase CPU limits or optimize code
3. **OOMKilled**: Increase memory limits and investigate memory leaks
4. **Pending Pods**: Check node capacity and resource quotas

#### Performance Tuning

1. **CPU Optimization**: Profile CPU usage and adjust limits
2. **Memory Optimization**: Analyze memory patterns and tune GC
3. **I/O Optimization**: Use faster storage classes for data-intensive services
4. **Network Optimization**: Configure appropriate bandwidth limits

## GPU-Specific Considerations

### GPU Resource Management

1. **GPU Allocation**: Constitutional Trainer requires dedicated GPU access
2. **GPU Sharing**: Single GPU per pod to avoid resource conflicts
3. **GPU Scheduling**: Use node selectors and tolerations for GPU nodes
4. **GPU Monitoring**: Track GPU utilization, memory, and temperature

### GPU Node Configuration

```yaml
nodeSelector:
  acgs-lite.io/node-type: governance
  nvidia.com/gpu.present: 'true'

tolerations:
  - key: 'nvidia.com/gpu'
    operator: 'Exists'
    effect: 'NoSchedule'
```

### GPU Cost Optimization

- **Spot Instances**: Use GPU spot instances for development/testing
- **Scheduling**: Optimize GPU utilization through intelligent scheduling
- **Scaling**: Scale GPU nodes based on training workload demand
- **Monitoring**: Track GPU cost per training session

## Cost Optimization

### Resource Efficiency Metrics

| Metric              | Target  | Measurement                     |
| ------------------- | ------- | ------------------------------- |
| CPU Utilization     | 60-80%  | Average over 24h                |
| Memory Utilization  | 70-85%  | Average over 24h                |
| GPU Utilization     | 70-90%  | Average during training         |
| Storage Utilization | 70-90%  | Current usage                   |
| Cost per Request    | < $0.01 | Monthly average (GPU-inclusive) |

### Optimization Strategies

1. **Right-sizing**: Regular review and adjustment of resource allocations
2. **Vertical Scaling**: Use VPA for automatic resource optimization
3. **Horizontal Scaling**: Optimize HPA settings for cost-effective scaling
4. **Spot Instances**: Use spot instances for non-critical workloads

## Maintenance and Updates

### Regular Reviews

- **Weekly**: Resource utilization analysis
- **Monthly**: Cost optimization review
- **Quarterly**: Capacity planning and forecasting
- **Annually**: Complete resource strategy review

### Update Procedures

1. **Baseline Measurement**: Capture current performance metrics
2. **Gradual Rollout**: Update resources in staging first
3. **Performance Validation**: Verify SLA compliance
4. **Rollback Plan**: Maintain previous configuration for quick rollback

## Conclusion

This resource allocation strategy provides a comprehensive framework for managing resources in the ACGS-1 Lite stack. Regular monitoring, optimization, and adherence to these guidelines will ensure optimal performance, security, and cost-effectiveness.

For questions or updates to this strategy, please consult the ACGS-1 Lite operations team.
