# ACGS-1 生产环境硬化清单

**版本:** 1.0  
**日期:** 2025-06-22  
**状态:** 生产就绪检查清单

## 🚨 架构硬伤修复指南

### 1. Istio+Envoy 强制注入与资源控制

#### 问题诊断

- Sidecar注入可能被跳过，导致安全策略失效
- Envoy代理资源无限制，可能抢占应用资源

#### 硬化方案

```yaml
# 强制Sidecar注入配置
apiVersion: v1
kind: Namespace
metadata:
  name: acgs
  labels:
    istio-injection: enabled
    istio.io/rev: default
  annotations:
    # 强制注入，不允许跳过
    sidecar.istio.io/inject: 'true'
    # 禁用自动注入跳过
    sidecar.istio.io/proxyCPU: '100m'
    sidecar.istio.io/proxyMemory: '128Mi'

---
# Envoy资源限制
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: acgs-control-plane
spec:
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        # 强制注入策略
        autoInject: enabled
        # 禁用注入跳过
        excludeInboundPorts: ''
        excludeOutboundPorts: ''
```

#### 验证脚本

```bash
#!/bin/bash
# 检查Sidecar注入状态
echo "🔍 检查Sidecar注入状态..."
kubectl get pods -n acgs -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}' | grep -v istio-proxy && echo "❌ 发现未注入Sidecar的Pod" || echo "✅ 所有Pod都已注入Sidecar"

# 检查资源限制
echo "🔍 检查Envoy资源限制..."
kubectl get pods -n acgs -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[?(@.name=="istio-proxy")].resources}{"\n"}{end}'
```

### 2. Database per Service 演进管理

#### Schema演进自治策略

```yaml
# 每个服务的数据库迁移配置
services:
  auth-service:
    database: auth_db
    migration_tool: alembic
    schema_version_table: auth_schema_versions
    migration_path: /migrations/auth

  ac-service:
    database: constitutional_db
    migration_tool: alembic
    schema_version_table: ac_schema_versions
    migration_path: /migrations/ac
```

#### 跨服务事务处理 - Saga模式

```python
# 跨服务事务协调器
class ConstitutionalGovernanceSaga:
    def __init__(self):
        self.steps = []
        self.compensations = []

    async def execute_policy_creation(self, policy_data):
        """创建策略的分布式事务"""
        try:
            # Step 1: 在AC Service创建原则
            principle_id = await self.ac_service.create_principle(policy_data.principle)
            self.add_compensation(lambda: self.ac_service.delete_principle(principle_id))

            # Step 2: 在FV Service验证策略
            verification_id = await self.fv_service.verify_policy(policy_data.policy, principle_id)
            self.add_compensation(lambda: self.fv_service.delete_verification(verification_id))

            # Step 3: 在PGC Service部署策略
            deployment_id = await self.pgc_service.deploy_policy(policy_data.policy, verification_id)
            self.add_compensation(lambda: self.pgc_service.undeploy_policy(deployment_id))

            # Step 4: 在Integrity Service记录审计
            audit_id = await self.integrity_service.log_policy_creation(deployment_id)

            return {"success": True, "deployment_id": deployment_id}

        except Exception as e:
            # 执行补偿操作
            await self.compensate()
            raise PolicyCreationSagaError(f"策略创建失败: {e}")
```

### 3. 缓存与会话优化策略

#### Session TTL动态调整

```python
class AdaptiveSessionManager:
    def __init__(self):
        self.redis_session = Redis(host='redis-session', port=6379, db=0)
        self.redis_cache = Redis(host='redis-cluster', port=6379, db=1)

    async def calculate_optimal_ttl(self, user_id: str) -> int:
        """根据用户活跃度动态计算Session TTL"""
        user_activity = await self.get_user_activity_score(user_id)

        if user_activity > 0.8:  # 高活跃用户
            return 3600 * 8  # 8小时
        elif user_activity > 0.5:  # 中等活跃用户
            return 3600 * 4  # 4小时
        else:  # 低活跃用户
            return 3600 * 1  # 1小时
```

#### 热Key限流策略

```python
class HotKeyProtection:
    def __init__(self):
        self.hot_key_detector = HotKeyDetector()
        self.rate_limiter = RateLimiter()

    async def get_with_protection(self, key: str):
        """带热Key保护的缓存获取"""
        # 检测热Key
        if await self.hot_key_detector.is_hot_key(key):
            # 应用限流
            if not await self.rate_limiter.allow(key):
                raise HotKeyRateLimitError(f"热Key {key} 访问频率过高")

            # 热Key分片
            shard_key = self.generate_shard_key(key)
            return await self.redis_cache.get(shard_key)

        return await self.redis_cache.get(key)
```

### 4. Kafka分区与保留策略

#### Topic分区规划

```yaml
# Kafka Topic配置
kafka_topics:
  constitutional.events:
    partitions: 12 # 根据预期QPS计算
    replication_factor: 3
    retention_ms: 604800000 # 7天
    cleanup_policy: delete

  policy.changes:
    partitions: 8
    replication_factor: 3
    retention_ms: 2592000000 # 30天
    cleanup_policy: delete

  audit.logs:
    partitions: 16 # 审计日志量大
    replication_factor: 3
    retention_ms: 31536000000 # 1年
    cleanup_policy: compact # 保留最新状态

  dgm.improvements:
    partitions: 4
    replication_factor: 3
    retention_ms: 7776000000 # 90天
    cleanup_policy: delete
```

#### 自动分区扩展

```python
class KafkaPartitionManager:
    async def monitor_and_scale(self):
        """监控并自动扩展分区"""
        for topic in self.topics:
            metrics = await self.get_topic_metrics(topic)

            # 检查消费延迟
            if metrics.consumer_lag > 10000:
                current_partitions = await self.get_partition_count(topic)
                new_partitions = min(current_partitions * 2, 32)  # 最多32分区

                await self.add_partitions(topic, new_partitions)
                logger.info(f"扩展Topic {topic} 分区数到 {new_partitions}")
```

### 5. Hyperledger Fabric运维SOP

#### 节点治理清单

```yaml
# Fabric网络治理配置
fabric_network:
  organizations:
    - name: ACGS-Org
      msp_id: ACGSMSP
      peers:
        - peer0.acgs.com
        - peer1.acgs.com
      ca: ca.acgs.com

  channels:
    constitutional-audit:
      endorsement_policy: "OR('ACGSMSP.peer')"
      lifecycle_endorsement: 'MAJORITY Endorsement'

  maintenance_schedule:
    peer_backup: '0 2 * * *' # 每天2点备份
    ca_cert_rotation: '0 0 1 */3 *' # 每季度轮换证书
    chaincode_upgrade: 'manual' # 手动升级
```

#### Fabric性能监控

```python
class FabricPerformanceMonitor:
    async def check_network_health(self):
        """检查Fabric网络健康状态"""
        health_report = {
            "peer_status": await self.check_peer_status(),
            "orderer_status": await self.check_orderer_status(),
            "channel_height": await self.check_channel_height(),
            "transaction_throughput": await self.measure_throughput(),
            "endorsement_latency": await self.measure_endorsement_latency()
        }

        # 性能阈值检查
        if health_report["transaction_throughput"] < 100:  # TPS < 100
            await self.alert_low_throughput()

        if health_report["endorsement_latency"] > 5000:  # 延迟 > 5s
            await self.alert_high_latency()

        return health_report
```

### 6. 安全配置动态轮换

#### 自动密钥轮换

```python
class VaultKeyRotationManager:
    def __init__(self):
        self.vault_client = hvac.Client(url='https://vault.acgs.com')
        self.rotation_schedule = {
            'database_passwords': timedelta(days=30),
            'api_keys': timedelta(days=7),
            'tls_certificates': timedelta(days=90),
            'jwt_signing_keys': timedelta(days=1)
        }

    async def rotate_keys(self):
        """自动轮换密钥"""
        for key_type, interval in self.rotation_schedule.items():
            last_rotation = await self.get_last_rotation_time(key_type)

            if datetime.now() - last_rotation > interval:
                await self.perform_key_rotation(key_type)
                await self.notify_services_of_rotation(key_type)
                logger.info(f"已轮换 {key_type} 密钥")
```

#### 访问审计追踪

```python
class VaultAccessAuditor:
    async def log_access(self, user: str, path: str, operation: str):
        """记录Vault访问日志"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "path": path,
            "operation": operation,
            "source_ip": self.get_client_ip(),
            "user_agent": self.get_user_agent(),
            "session_id": self.get_session_id()
        }

        # 发送到审计日志系统
        await self.send_to_audit_system(audit_entry)

        # 检查异常访问模式
        if await self.detect_anomalous_access(user, path):
            await self.trigger_security_alert(audit_entry)
```

### 7. 监控告警优化

#### SLO Dashboard模板

```yaml
# Grafana Dashboard配置
dashboards:
  service_slo:
    panels:
      - title: 'Request Rate'
        query: 'rate(http_requests_total[5m])'
        thresholds: [100, 1000, 5000]

      - title: 'Error Rate'
        query: 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])'
        thresholds: [0.01, 0.05, 0.1] # 1%, 5%, 10%

      - title: 'Response Latency P95'
        query: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'
        thresholds: [0.1, 0.5, 1.0] # 100ms, 500ms, 1s
```

#### 告警抖动控制

```yaml
# Alertmanager配置
alerting_rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 2m # 持续2分钟才告警
    annotations:
      summary: '服务 {{ $labels.service }} 错误率过高'

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m # 持续5分钟才告警
    annotations:
      summary: '服务 {{ $labels.service }} 延迟过高'

# 告警抑制规则
inhibit_rules:
  - source_match:
      alertname: ServiceDown
    target_match:
      service: '{{ $labels.service }}'
    equal: ['service'] # 服务下线时抑制其他告警
```

### 8. DGM安全沙箱强化

#### 灰度发布控制

```python
class DGMGradualRollout:
    def __init__(self):
        self.rollout_stages = [
            {"name": "canary", "traffic_percent": 1, "duration": "1h"},
            {"name": "small", "traffic_percent": 10, "duration": "4h"},
            {"name": "medium", "traffic_percent": 50, "duration": "12h"},
            {"name": "full", "traffic_percent": 100, "duration": "∞"}
        ]

    async def deploy_improvement(self, improvement_id: str):
        """DGM改进的灰度发布"""
        for stage in self.rollout_stages:
            # 部署到指定流量比例
            await self.update_traffic_split(improvement_id, stage["traffic_percent"])

            # 监控关键指标
            metrics = await self.monitor_stage(stage["duration"])

            # 检查是否需要回滚
            if not self.validate_metrics(metrics):
                await self.rollback_improvement(improvement_id)
                raise DGMRolloutFailure(f"Stage {stage['name']} 指标异常，已回滚")

            logger.info(f"DGM改进 {improvement_id} 在 {stage['name']} 阶段成功")
```

#### 人工审核界面

```python
class DGMReviewDashboard:
    async def generate_improvement_report(self, improvement_id: str):
        """生成改进报告供人工审核"""
        improvement = await self.get_improvement_details(improvement_id)

        report = {
            "improvement_id": improvement_id,
            "proposed_changes": improvement.changes,
            "impact_analysis": {
                "affected_services": improvement.affected_services,
                "performance_impact": improvement.performance_delta,
                "risk_score": improvement.risk_assessment.score,
                "rollback_complexity": improvement.rollback_plan.complexity
            },
            "test_results": {
                "unit_tests": improvement.test_results.unit,
                "integration_tests": improvement.test_results.integration,
                "performance_tests": improvement.test_results.performance
            },
            "recommendation": self.generate_recommendation(improvement)
        }

        return report
```

## 🎯 生产就绪检查清单

### 部署前检查

- [ ] 所有Pod都已强制注入Sidecar
- [ ] Envoy资源限制已配置
- [ ] 数据库迁移脚本已测试
- [ ] Kafka分区已合理规划
- [ ] Vault密钥轮换已配置
- [ ] 监控Dashboard已部署
- [ ] 告警规则已配置并测试
- [ ] DGM安全控制已启用

### 运行时监控

- [ ] SLO指标正常 (延迟、错误率、吞吐量)
- [ ] 资源使用率在安全范围内
- [ ] 告警系统响应正常
- [ ] 日志收集完整
- [ ] 安全扫描通过
- [ ] 备份恢复测试成功

---

**总结**: 这份硬化清单把你提到的每个"硬伤"都给了具体的修复方案。虽然看起来工作量不小，但这些都是生产环境的"必修课"。毕竟，架构图画得再漂亮，半夜被告警吵醒的还是我们这些"码农"。
