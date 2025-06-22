# ACGS-1 日常运维手册

**版本:** 1.0  
**日期:** 2025-06-22  
**适用环境:** 生产环境

## 🌅 每日运维检查清单

### 早班检查 (09:00)

#### 1. 系统健康状态检查

```bash
#!/bin/bash
# 系统健康检查脚本
echo "🔍 ACGS-1 系统健康检查 - $(date)"
echo "=================================="

# 检查所有服务状态
echo "📊 服务状态检查:"
for port in 8000 8001 8002 8003 8004 8005 8006 8007; do
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
    if [ "$status" = "200" ]; then
        echo "✅ Port $port: 健康"
    else
        echo "❌ Port $port: 异常 (HTTP $status)"
    fi
done

# 检查Istio网格状态
echo "🕸️ Istio网格状态:"
kubectl get pods -n istio-system --no-headers | awk '{print $1 "\t" $3}' | while read name status; do
    if [ "$status" = "Running" ]; then
        echo "✅ $name: 运行中"
    else
        echo "❌ $name: $status"
    fi
done

# 检查数据库连接
echo "🗄️ 数据库连接检查:"
for db in auth_db constitutional_db integrity_db verification_db synthesis_db governance_db council_db dgm_db; do
    result=$(psql "postgresql://acgs_user:acgs_password@localhost:5432/$db" -c "SELECT 1;" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ $db: 连接正常"
    else
        echo "❌ $db: 连接失败"
    fi
done

# 检查Redis集群
echo "💾 Redis集群状态:"
redis-cli -h redis-cluster -p 6379 cluster info | grep cluster_state | if grep -q "ok"; then
    echo "✅ Redis Cluster: 正常"
else
    echo "❌ Redis Cluster: 异常"
fi

# 检查Kafka集群
echo "📨 Kafka集群状态:"
kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Kafka: 正常"
else
    echo "❌ Kafka: 异常"
fi
```

#### 2. 性能指标检查

```bash
#!/bin/bash
# 性能指标检查
echo "📈 性能指标检查:"

# API响应时间检查
echo "⏱️ API响应时间 (P95):"
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))" | \
jq -r '.data.result[] | "\(.metric.service): \(.value[1])s"'

# 错误率检查
echo "🚨 错误率:"
curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])/rate(http_requests_total[5m])" | \
jq -r '.data.result[] | "\(.metric.service): \((.value[1] | tonumber * 100) | round)%"'

# 数据库连接池使用率
echo "🏊 数据库连接池使用率:"
for service in auth ac integrity fv gs pgc ec dgm; do
    active=$(psql -h localhost -U acgs_user -d ${service}_db -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
    total=$(psql -h localhost -U acgs_user -d ${service}_db -t -c "SELECT setting FROM pg_settings WHERE name = 'max_connections';")
    usage=$(echo "scale=2; $active * 100 / $total" | bc)
    echo "📊 ${service}_db: ${active}/${total} (${usage}%)"
done
```

### 中班检查 (14:00)

#### 3. 安全状态检查

```bash
#!/bin/bash
# 安全检查脚本
echo "🔒 安全状态检查:"

# 检查mTLS状态
echo "🔐 mTLS状态检查:"
kubectl get peerauthentication -n acgs -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.mtls.mode}{"\n"}{end}'

# 检查证书过期时间
echo "📜 证书过期检查:"
kubectl get certificates -n acgs -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.notAfter}{"\n"}{end}'

# 检查Vault密钥轮换状态
echo "🔑 Vault密钥状态:"
vault auth -method=userpass username=acgs-operator password=$VAULT_PASSWORD > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Vault认证成功"
    vault kv get -field=last_rotation secret/acgs/database
else
    echo "❌ Vault认证失败"
fi

# 检查异常登录
echo "👤 异常登录检查:"
psql -h localhost -U acgs_user -d auth_db -c "
SELECT username, COUNT(*) as failed_attempts
FROM audit_logs
WHERE action = 'login_failed'
AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY username
HAVING COUNT(*) > 5;
"
```

#### 4. DGM安全监控

```bash
#!/bin/bash
# DGM安全监控
echo "🤖 DGM安全状态检查:"

# 检查DGM改进请求
echo "🔬 DGM改进请求:"
psql -h localhost -U acgs_user -d dgm_db -c "
SELECT
    improvement_id,
    status,
    risk_score,
    created_at
FROM dgm_archive
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY risk_score DESC;
"

# 检查沙箱环境状态
echo "🏖️ 沙箱环境状态:"
kubectl get pods -n dgm-sandbox --no-headers | awk '{print $1 "\t" $3}'

# 检查人工审核队列
echo "👥 人工审核队列:"
psql -h localhost -U acgs_user -d dgm_db -c "
SELECT COUNT(*) as pending_reviews
FROM improvement_workspaces
WHERE status = 'pending_review';
"
```

### 晚班检查 (22:00)

#### 5. 备份与清理

```bash
#!/bin/bash
# 备份与清理脚本
echo "💾 备份与清理任务:"

# 数据库备份检查
echo "🗄️ 数据库备份状态:"
for db in auth_db constitutional_db integrity_db verification_db synthesis_db governance_db council_db dgm_db; do
    backup_file="/backups/${db}_$(date +%Y%m%d).sql"
    if [ -f "$backup_file" ]; then
        size=$(du -h "$backup_file" | cut -f1)
        echo "✅ $db: 备份完成 ($size)"
    else
        echo "❌ $db: 备份缺失"
    fi
done

# 日志清理
echo "🧹 日志清理:"
find /var/log/acgs -name "*.log" -mtime +7 -delete
echo "✅ 清理7天前的日志文件"

# Kafka消息清理检查
echo "📨 Kafka消息保留检查:"
kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe --json | \
jq -r '.brokers[].logDirs[].partitions[] | select(.size > 1000000000) | "\(.topic)-\(.partition): \(.size/1000000000 | round)GB"'

# Redis内存使用检查
echo "💾 Redis内存使用:"
redis-cli -h redis-cluster -p 6379 info memory | grep used_memory_human
redis-cli -h redis-session -p 6379 info memory | grep used_memory_human
```

## 🚨 故障应急处理

### 服务宕机处理

```bash
#!/bin/bash
# 服务故障恢复脚本
service_name=$1
if [ -z "$service_name" ]; then
    echo "用法: $0 <service_name>"
    exit 1
fi

echo "🚨 处理服务故障: $service_name"

# 1. 检查Pod状态
echo "1️⃣ 检查Pod状态:"
kubectl get pods -n acgs -l app=$service_name

# 2. 查看Pod日志
echo "2️⃣ 查看最近日志:"
kubectl logs -n acgs -l app=$service_name --tail=50

# 3. 检查资源使用
echo "3️⃣ 检查资源使用:"
kubectl top pods -n acgs -l app=$service_name

# 4. 重启服务
echo "4️⃣ 重启服务:"
kubectl rollout restart deployment/$service_name -n acgs

# 5. 等待服务恢复
echo "5️⃣ 等待服务恢复:"
kubectl rollout status deployment/$service_name -n acgs --timeout=300s

# 6. 验证服务健康
echo "6️⃣ 验证服务健康:"
sleep 30
service_port=$(kubectl get svc $service_name -n acgs -o jsonpath='{.spec.ports[0].port}')
curl -f http://localhost:$service_port/health && echo "✅ 服务恢复正常" || echo "❌ 服务仍然异常"
```

### 数据库故障处理

```bash
#!/bin/bash
# 数据库故障处理
db_name=$1
echo "🗄️ 处理数据库故障: $db_name"

# 1. 检查数据库连接
echo "1️⃣ 检查数据库连接:"
pg_isready -h localhost -p 5432 -d $db_name

# 2. 检查数据库大小和连接数
echo "2️⃣ 检查数据库状态:"
psql -h localhost -U acgs_user -d $db_name -c "
SELECT
    pg_database_size('$db_name')/1024/1024 as size_mb,
    (SELECT count(*) FROM pg_stat_activity WHERE datname = '$db_name') as connections;
"

# 3. 检查慢查询
echo "3️⃣ 检查慢查询:"
psql -h localhost -U acgs_user -d $db_name -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 5;
"

# 4. 强制断开空闲连接
echo "4️⃣ 清理空闲连接:"
psql -h localhost -U acgs_user -d $db_name -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$db_name'
AND state = 'idle'
AND state_change < now() - interval '1 hour';
"

# 5. 执行VACUUM ANALYZE
echo "5️⃣ 执行数据库维护:"
psql -h localhost -U acgs_user -d $db_name -c "VACUUM ANALYZE;"
```

## 📊 性能调优脚本

### 数据库性能优化

```bash
#!/bin/bash
# 数据库性能优化脚本
echo "⚡ 数据库性能优化:"

for db in auth_db constitutional_db integrity_db verification_db synthesis_db governance_db council_db dgm_db; do
    echo "🔧 优化数据库: $db"

    # 更新统计信息
    psql -h localhost -U acgs_user -d $db -c "ANALYZE;"

    # 检查缺失的索引
    psql -h localhost -U acgs_user -d $db -c "
    SELECT schemaname, tablename, attname, n_distinct, correlation
    FROM pg_stats
    WHERE schemaname = 'public'
    AND n_distinct > 100
    AND correlation < 0.1;
    "

    # 检查未使用的索引
    psql -h localhost -U acgs_user -d $db -c "
    SELECT schemaname, tablename, indexname, idx_scan
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0;
    "
done
```

### 缓存预热

```bash
#!/bin/bash
# 缓存预热脚本
echo "🔥 缓存预热:"

# 预热用户会话缓存
echo "👤 预热用户会话缓存:"
curl -s "http://localhost:8000/api/v1/cache/warmup/sessions"

# 预热宪法原则缓存
echo "📜 预热宪法原则缓存:"
curl -s "http://localhost:8001/api/v1/cache/warmup/principles"

# 预热策略缓存
echo "📋 预热策略缓存:"
curl -s "http://localhost:8005/api/v1/cache/warmup/policies"

echo "✅ 缓存预热完成"
```

## 🎯 监控告警处理

### 告警响应流程

```bash
#!/bin/bash
# 告警响应脚本
alert_name=$1
service_name=$2

echo "🚨 处理告警: $alert_name (服务: $service_name)"

case $alert_name in
    "HighErrorRate")
        echo "🔍 分析高错误率..."
        kubectl logs -n acgs -l app=$service_name --tail=100 | grep -i error
        ;;
    "HighLatency")
        echo "🐌 分析高延迟..."
        curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket{service=\"$service_name\"}[5m]))"
        ;;
    "DatabaseConnectionHigh")
        echo "🗄️ 分析数据库连接..."
        psql -h localhost -U acgs_user -d ${service_name}_db -c "SELECT count(*) FROM pg_stat_activity;"
        ;;
    "DGMSecurityAlert")
        echo "🤖 DGM安全告警..."
        kubectl logs -n acgs -l app=dgm-service --tail=50 | grep -i security
        ;;
esac

echo "📧 发送告警通知到运维群..."
# 这里可以集成钉钉、企业微信等通知
```

---

**使用说明**:

1. 将这些脚本放在 `/opt/acgs/scripts/` 目录下
2. 设置定时任务执行日常检查
3. 配置告警系统调用应急脚本
4. 定期更新脚本和阈值

**记住**: 这些脚本是你半夜被叫醒时的"救命稻草"，平时多测试，关键时刻不掉链子！
