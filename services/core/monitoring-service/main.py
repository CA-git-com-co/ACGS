"""
Monitoring and Observability Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for comprehensive system monitoring, metrics collection,
alerting, and observability across all ACGS-2 services.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import httpx
import os
import json
import time
from collections import defaultdict, deque
import statistics

from .models import (
    ServiceHealth, MetricPoint, Alert, AlertRule, ServiceMetrics,
    HealthStatus, AlertSeverity, AlertStatus, SystemOverview,
    PerformanceMetrics, ServiceDependency, CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service registry - all ACGS-2 services to monitor
SERVICE_REGISTRY = {
    "constitutional-core": "http://localhost:8001",
    "groqcloud-policy": "http://localhost:8023", 
    "multi-agent-coordination": "http://localhost:8008",
    "worker-agents": "http://localhost:8009",
    "blackboard-coordination": "http://localhost:8010",
    "mcp-aggregator": "http://localhost:3000",
    "a2a-policy": "http://localhost:8020",
    "security-validation": "http://localhost:8021",
    "consensus-engine": "http://localhost:8011",
    "human-in-the-loop": "http://localhost:8012",
    "auth-service": "http://localhost:8013",
    "audit-service": "http://localhost:8015",
    "api-gateway": "http://localhost:8080",
    "gdpr-compliance": "http://localhost:8016",
    "alerting-service": "http://localhost:8017"
}

# Global storage
monitoring_storage = {
    "service_health": {},
    "metrics": defaultdict(lambda: deque(maxlen=1000)),  # Rolling metrics
    "alerts": {},
    "alert_rules": {},
    "performance_history": defaultdict(lambda: deque(maxlen=100)),
    "system_events": deque(maxlen=500),
    "service_dependencies": {}
}

# HTTP client for service health checks
http_client = httpx.AsyncClient(timeout=10.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Monitoring Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize default alert rules
    await initialize_alert_rules()
    await initialize_service_dependencies()
    
    # Start background monitoring tasks
    asyncio.create_task(continuous_health_monitoring())
    asyncio.create_task(metrics_collection())
    asyncio.create_task(alert_evaluation())
    asyncio.create_task(performance_analysis())
    asyncio.create_task(system_health_aggregation())
    
    yield
    
    # Cleanup
    await http_client.aclose()
    logger.info("Shutting down Monitoring Service")

app = FastAPI(
    title="Monitoring Service",
    description="System monitoring and observability for ACGS-2",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_alert_rules():
    """Initialize default alerting rules"""
    default_rules = [
        AlertRule(
            name="Service Down",
            description="Alert when service becomes unavailable",
            condition="health_status == 'unhealthy'",
            severity=AlertSeverity.CRITICAL,
            threshold=1,
            evaluation_window_minutes=1,
            constitutional_impact=True
        ),
        AlertRule(
            name="High Response Time",
            description="Alert when response time exceeds threshold",
            condition="response_time_ms > 5000",
            severity=AlertSeverity.WARNING,
            threshold=5,
            evaluation_window_minutes=5,
            constitutional_impact=False
        ),
        AlertRule(
            name="Constitutional Hash Mismatch",
            description="Alert when constitutional hash validation fails",
            condition="constitutional_hash != 'cdd01ef066bc6cf2'",
            severity=AlertSeverity.CRITICAL,
            threshold=1,
            evaluation_window_minutes=1,
            constitutional_impact=True
        ),
        AlertRule(
            name="Memory Usage High",
            description="Alert when memory usage exceeds 85%",
            condition="memory_usage_percent > 85",
            severity=AlertSeverity.WARNING,
            threshold=3,
            evaluation_window_minutes=10,
            constitutional_impact=False
        ),
        AlertRule(
            name="CPU Usage High",
            description="Alert when CPU usage exceeds 90%",
            condition="cpu_usage_percent > 90",
            severity=AlertSeverity.WARNING,
            threshold=3,
            evaluation_window_minutes=10,
            constitutional_impact=False
        ),
        AlertRule(
            name="Error Rate High",
            description="Alert when error rate exceeds 5%",
            condition="error_rate_percent > 5",
            severity=AlertSeverity.WARNING,
            threshold=2,
            evaluation_window_minutes=5,
            constitutional_impact=False
        )
    ]
    
    for rule in default_rules:
        monitoring_storage["alert_rules"][rule.rule_id] = rule
    
    logger.info(f"Initialized {len(default_rules)} default alert rules")

async def initialize_service_dependencies():
    """Initialize service dependency graph"""
    dependencies = {
        "constitutional-core": ["auth-service"],
        "groqcloud-policy": ["constitutional-core", "auth-service"],
        "multi-agent-coordination": ["constitutional-core", "consensus-engine"],
        "worker-agents": ["multi-agent-coordination", "auth-service"],
        "blackboard-coordination": ["multi-agent-coordination"],
        "mcp-aggregator": ["auth-service"],
        "a2a-policy": ["auth-service", "consensus-engine"],
        "security-validation": ["auth-service"],
        "consensus-engine": ["auth-service"],
        "human-in-the-loop": ["auth-service", "consensus-engine"],
        "auth-service": []  # No dependencies
    }
    
    for service, deps in dependencies.items():
        monitoring_storage["service_dependencies"][service] = ServiceDependency(
            service_name=service,
            dependencies=deps,
            dependency_status="healthy" if all(
                monitoring_storage["service_health"].get(dep, {}).get("status") == "healthy" 
                for dep in deps
            ) else "degraded"
        )
    
    logger.info("Initialized service dependency graph")

async def continuous_health_monitoring():
    """Continuously monitor service health"""
    while True:
        try:
            tasks = []
            for service_name, base_url in SERVICE_REGISTRY.items():
                tasks.append(check_service_health(service_name, base_url))
            
            # Execute health checks in parallel
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
            await asyncio.sleep(30)

async def check_service_health(service_name: str, base_url: str):
    """Check health of individual service"""
    start_time = time.time()
    
    try:
        response = await http_client.get(f"{base_url}/health")
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            health_data = response.json()
            
            # Validate constitutional hash
            constitutional_valid = (
                health_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
            )
            
            health_status = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.HEALTHY if constitutional_valid else HealthStatus.DEGRADED,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details=health_data,
                constitutional_compliance=constitutional_valid,
                error_message=None if constitutional_valid else "Constitutional hash mismatch"
            )
            
        else:
            health_status = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                last_check=datetime.utcnow(),
                details={},
                constitutional_compliance=False,
                error_message=f"HTTP {response.status_code}"
            )
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        health_status = ServiceHealth(
            service_name=service_name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            last_check=datetime.utcnow(),
            details={},
            constitutional_compliance=False,
            error_message=str(e)
        )
    
    # Store health status
    monitoring_storage["service_health"][service_name] = health_status
    
    # Record metrics
    await record_metric(service_name, "response_time_ms", response_time)
    await record_metric(service_name, "health_status", 1 if health_status.status == HealthStatus.HEALTHY else 0)
    await record_metric(service_name, "constitutional_compliance", 1 if health_status.constitutional_compliance else 0)

async def record_metric(service_name: str, metric_name: str, value: float, labels: Dict[str, str] = None):
    """Record a metric point"""
    metric_point = MetricPoint(
        service_name=service_name,
        metric_name=metric_name,
        value=value,
        labels=labels or {},
        timestamp=datetime.utcnow()
    )
    
    metric_key = f"{service_name}.{metric_name}"
    monitoring_storage["metrics"][metric_key].append(metric_point)

async def metrics_collection():
    """Collect various system metrics"""
    while True:
        try:
            # Collect system-wide metrics
            await collect_system_metrics()
            await collect_performance_metrics()
            
            await asyncio.sleep(60)  # Collect every minute
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(60)

async def collect_system_metrics():
    """Collect system-wide metrics"""
    total_services = len(SERVICE_REGISTRY)
    healthy_services = sum(
        1 for health in monitoring_storage["service_health"].values()
        if health.status == HealthStatus.HEALTHY
    )
    
    # System availability
    availability = (healthy_services / total_services * 100) if total_services > 0 else 0
    await record_metric("system", "availability_percent", availability)
    
    # Constitutional compliance rate
    compliant_services = sum(
        1 for health in monitoring_storage["service_health"].values()
        if health.constitutional_compliance
    )
    compliance_rate = (compliant_services / total_services * 100) if total_services > 0 else 0
    await record_metric("system", "constitutional_compliance_percent", compliance_rate)
    
    # Active alerts
    active_alerts = sum(
        1 for alert in monitoring_storage["alerts"].values()
        if alert.status == AlertStatus.ACTIVE
    )
    await record_metric("system", "active_alerts", active_alerts)

async def collect_performance_metrics():
    """Collect performance metrics"""
    for service_name in SERVICE_REGISTRY.keys():
        if service_name in monitoring_storage["service_health"]:
            health = monitoring_storage["service_health"][service_name]
            
            # Response time statistics
            response_times = [
                point.value for point in monitoring_storage["metrics"][f"{service_name}.response_time_ms"]
                if point.timestamp > datetime.utcnow() - timedelta(minutes=5)
            ]
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                
                await record_metric(service_name, "avg_response_time_ms", avg_response_time)
                await record_metric(service_name, "p95_response_time_ms", p95_response_time)

async def alert_evaluation():
    """Evaluate alert rules and trigger alerts"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            for rule in monitoring_storage["alert_rules"].values():
                await evaluate_alert_rule(rule, current_time)
            
            await asyncio.sleep(60)  # Evaluate every minute
            
        except Exception as e:
            logger.error(f"Alert evaluation error: {e}")
            await asyncio.sleep(60)

async def evaluate_alert_rule(rule: AlertRule, current_time: datetime):
    """Evaluate a single alert rule"""
    try:
        # Get metrics for evaluation window
        window_start = current_time - timedelta(minutes=rule.evaluation_window_minutes)
        
        violations = 0
        
        # Check each service against the rule
        for service_name in SERVICE_REGISTRY.keys():
            if await check_rule_condition(rule, service_name, window_start, current_time):
                violations += 1
        
        # Check if threshold is exceeded
        if violations >= rule.threshold:
            alert_id = f"{rule.rule_id}_{service_name}_{current_time.strftime('%Y%m%d_%H%M')}"
            
            if alert_id not in monitoring_storage["alerts"]:
                alert = Alert(
                    alert_id=alert_id,
                    rule_id=rule.rule_id,
                    service_name=service_name,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    message=f"{rule.name}: {rule.description}",
                    details={"violations": violations, "threshold": rule.threshold},
                    constitutional_impact=rule.constitutional_impact,
                    triggered_at=current_time
                )
                
                monitoring_storage["alerts"][alert_id] = alert
                logger.warning(f"Alert triggered: {alert.message}")
                
                # Record system event
                monitoring_storage["system_events"].append({
                    "timestamp": current_time,
                    "type": "alert_triggered",
                    "severity": rule.severity.value,
                    "message": alert.message,
                    "constitutional_impact": rule.constitutional_impact
                })
    
    except Exception as e:
        logger.error(f"Error evaluating alert rule {rule.name}: {e}")

async def check_rule_condition(rule: AlertRule, service_name: str, window_start: datetime, window_end: datetime) -> bool:
    """Check if alert rule condition is met for a service"""
    # Simplified condition checking - in production this would be more sophisticated
    if "health_status == 'unhealthy'" in rule.condition:
        health = monitoring_storage["service_health"].get(service_name)
        return health and health.status == HealthStatus.UNHEALTHY
    
    elif "response_time_ms >" in rule.condition:
        threshold = float(rule.condition.split(">")[1].strip())
        health = monitoring_storage["service_health"].get(service_name)
        return health and health.response_time_ms > threshold
    
    elif "constitutional_hash !=" in rule.condition:
        health = monitoring_storage["service_health"].get(service_name)
        return health and not health.constitutional_compliance
    
    return False

async def performance_analysis():
    """Analyze performance trends"""
    while True:
        try:
            for service_name in SERVICE_REGISTRY.keys():
                await analyze_service_performance(service_name)
            
            await asyncio.sleep(300)  # Analyze every 5 minutes
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            await asyncio.sleep(300)

async def analyze_service_performance(service_name: str):
    """Analyze performance for a specific service"""
    current_time = datetime.utcnow()
    
    # Get metrics from last hour
    hour_ago = current_time - timedelta(hours=1)
    
    response_times = [
        point.value for point in monitoring_storage["metrics"][f"{service_name}.response_time_ms"]
        if point.timestamp > hour_ago
    ]
    
    if len(response_times) >= 10:  # Need sufficient data
        performance = PerformanceMetrics(
            service_name=service_name,
            avg_response_time_ms=statistics.mean(response_times),
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times),
            throughput_rps=len(response_times) / 3600,  # Approximate RPS
            error_rate_percent=0,  # Would calculate from error metrics
            uptime_percent=100,  # Would calculate from health checks
            measurement_window_minutes=60,
            timestamp=current_time
        )
        
        monitoring_storage["performance_history"][service_name].append(performance)

async def system_health_aggregation():
    """Aggregate system health data"""
    while True:
        try:
            await update_service_dependencies()
            await calculate_system_overview()
            
            await asyncio.sleep(120)  # Update every 2 minutes
            
        except Exception as e:
            logger.error(f"System health aggregation error: {e}")
            await asyncio.sleep(120)

async def update_service_dependencies():
    """Update service dependency status"""
    for service_name, dependency in monitoring_storage["service_dependencies"].items():
        healthy_deps = sum(
            1 for dep in dependency.dependencies
            if monitoring_storage["service_health"].get(dep, {}).status == HealthStatus.HEALTHY
        )
        
        total_deps = len(dependency.dependencies)
        
        if total_deps == 0:
            dependency.dependency_status = "healthy"
        elif healthy_deps == total_deps:
            dependency.dependency_status = "healthy"
        elif healthy_deps > 0:
            dependency.dependency_status = "degraded"
        else:
            dependency.dependency_status = "unhealthy"

async def calculate_system_overview():
    """Calculate overall system overview"""
    total_services = len(SERVICE_REGISTRY)
    healthy_services = sum(
        1 for health in monitoring_storage["service_health"].values()
        if health.status == HealthStatus.HEALTHY
    )
    
    active_alerts = len([
        alert for alert in monitoring_storage["alerts"].values()
        if alert.status == AlertStatus.ACTIVE
    ])
    
    critical_alerts = len([
        alert for alert in monitoring_storage["alerts"].values()
        if alert.status == AlertStatus.ACTIVE and alert.severity == AlertSeverity.CRITICAL
    ])
    
    overview = SystemOverview(
        total_services=total_services,
        healthy_services=healthy_services,
        degraded_services=sum(
            1 for health in monitoring_storage["service_health"].values()
            if health.status == HealthStatus.DEGRADED
        ),
        unhealthy_services=sum(
            1 for health in monitoring_storage["service_health"].values()
            if health.status == HealthStatus.UNHEALTHY
        ),
        overall_availability_percent=(healthy_services / total_services * 100) if total_services > 0 else 0,
        constitutional_compliance_percent=sum(
            1 for health in monitoring_storage["service_health"].values()
            if health.constitutional_compliance
        ) / total_services * 100 if total_services > 0 else 0,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        last_updated=datetime.utcnow()
    )
    
    monitoring_storage["system_overview"] = overview

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "monitoring-service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "monitoring": {
            "tracked_services": len(SERVICE_REGISTRY),
            "active_alerts": len([
                a for a in monitoring_storage["alerts"].values()
                if a.status == AlertStatus.ACTIVE
            ]),
            "alert_rules": len(monitoring_storage["alert_rules"])
        }
    }

# Monitoring endpoints
@app.get("/api/v1/services/health", response_model=List[ServiceHealth])
async def get_services_health():
    """Get health status of all services"""
    return list(monitoring_storage["service_health"].values())

@app.get("/api/v1/services/{service_name}/health", response_model=ServiceHealth)
async def get_service_health(service_name: str):
    """Get health status of specific service"""
    if service_name not in monitoring_storage["service_health"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return monitoring_storage["service_health"][service_name]

@app.get("/api/v1/metrics/{service_name}")
async def get_service_metrics(
    service_name: str,
    metric_name: Optional[str] = None,
    hours: int = 1
):
    """Get metrics for a service"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    if metric_name:
        metric_key = f"{service_name}.{metric_name}"
        if metric_key not in monitoring_storage["metrics"]:
            raise HTTPException(status_code=404, detail="Metric not found")
        
        metrics = [
            point for point in monitoring_storage["metrics"][metric_key]
            if point.timestamp > cutoff_time
        ]
    else:
        metrics = []
        for metric_key, points in monitoring_storage["metrics"].items():
            if metric_key.startswith(f"{service_name}."):
                metrics.extend([
                    point for point in points
                    if point.timestamp > cutoff_time
                ])
    
    return {
        "service_name": service_name,
        "metric_name": metric_name,
        "time_range_hours": hours,
        "data_points": len(metrics),
        "metrics": metrics
    }

@app.get("/api/v1/alerts", response_model=List[Alert])
async def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24
):
    """Get alerts"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    alerts = [
        alert for alert in monitoring_storage["alerts"].values()
        if alert.triggered_at > cutoff_time
    ]
    
    if status:
        alerts = [a for a in alerts if a.status.value == status]
    
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity]
    
    return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

@app.get("/api/v1/overview", response_model=SystemOverview)
async def get_system_overview():
    """Get system overview"""
    if "system_overview" not in monitoring_storage:
        await calculate_system_overview()
    
    return monitoring_storage["system_overview"]

@app.get("/api/v1/performance/{service_name}")
async def get_service_performance(service_name: str, hours: int = 24):
    """Get performance metrics for service"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    performance_data = [
        perf for perf in monitoring_storage["performance_history"][service_name]
        if perf.timestamp > cutoff_time
    ]
    
    return {
        "service_name": service_name,
        "time_range_hours": hours,
        "data_points": len(performance_data),
        "performance": performance_data
    }

@app.get("/api/v1/dependencies")
async def get_service_dependencies():
    """Get service dependency graph"""
    return {
        "dependencies": monitoring_storage["service_dependencies"],
        "graph": {
            service: {
                "depends_on": dep.dependencies,
                "status": dep.dependency_status
            }
            for service, dep in monitoring_storage["service_dependencies"].items()
        }
    }

@app.get("/")
async def monitoring_dashboard():
    """Monitoring dashboard UI"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-2 Monitoring Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .healthy { color: #27ae60; }
            .warning { color: #f39c12; }
            .critical { color: #e74c3c; }
            .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
            .service-list { list-style: none; padding: 0; }
            .service-item { padding: 8px; margin: 4px 0; border-left: 4px solid #ccc; background: #f8f9fa; }
            .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="header">
            <h1>🔧 ACGS-2 Monitoring Dashboard</h1>
            <p>Constitutional Hash: cdd01ef066bc6cf2</p>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>System Overview</h3>
                <div id="system-overview">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Service Health</h3>
                <div id="service-health">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Active Alerts</h3>
                <div id="alerts">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Performance Metrics</h3>
                <canvas id="performance-chart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <script>
            let performanceChart = null;
            
            async function refreshData() {
                await Promise.all([
                    loadSystemOverview(),
                    loadServiceHealth(),
                    loadAlerts(),
                    loadPerformanceChart()
                ]);
            }
            
            async function loadSystemOverview() {
                try {
                    const response = await fetch('/api/v1/overview');
                    const data = await response.json();
                    
                    document.getElementById('system-overview').innerHTML = `
                        <div class="metric healthy">${data.healthy_services}/${data.total_services}</div>
                        <p>Services Online</p>
                        <div>Availability: ${data.overall_availability_percent.toFixed(1)}%</div>
                        <div>Constitutional Compliance: ${data.constitutional_compliance_percent.toFixed(1)}%</div>
                        <div>Active Alerts: <span class="${data.critical_alerts > 0 ? 'critical' : 'healthy'}">${data.active_alerts}</span></div>
                    `;
                } catch (error) {
                    document.getElementById('system-overview').innerHTML = 'Error loading data';
                }
            }
            
            async function loadServiceHealth() {
                try {
                    const response = await fetch('/api/v1/services/health');
                    const services = await response.json();
                    
                    const html = services.map(service => {
                        const statusClass = service.status === 'healthy' ? 'healthy' : 
                                          service.status === 'degraded' ? 'warning' : 'critical';
                        const statusColor = service.status === 'healthy' ? '#27ae60' : 
                                          service.status === 'degraded' ? '#f39c12' : '#e74c3c';
                        
                        return `
                            <div class="service-item" style="border-left-color: ${statusColor}">
                                <span class="status-indicator" style="background: ${statusColor}"></span>
                                <strong>${service.service_name}</strong>
                                <div style="font-size: 0.9em; color: #666;">
                                    Response: ${service.response_time_ms.toFixed(0)}ms | 
                                    Constitutional: ${service.constitutional_compliance ? '✅' : '❌'}
                                </div>
                            </div>
                        `;
                    }).join('');
                    
                    document.getElementById('service-health').innerHTML = `<ul class="service-list">${html}</ul>`;
                } catch (error) {
                    document.getElementById('service-health').innerHTML = 'Error loading service health';
                }
            }
            
            async function loadAlerts() {
                try {
                    const response = await fetch('/api/v1/alerts?hours=24');
                    const alerts = await response.json();
                    
                    if (alerts.length === 0) {
                        document.getElementById('alerts').innerHTML = '<div class="healthy">No active alerts</div>';
                        return;
                    }
                    
                    const html = alerts.slice(0, 5).map(alert => {
                        const severityClass = alert.severity === 'critical' ? 'critical' : 
                                            alert.severity === 'warning' ? 'warning' : 'healthy';
                        
                        return `
                            <div class="service-item">
                                <span class="${severityClass}">⚠️ ${alert.severity.toUpperCase()}</span>
                                <div><strong>${alert.message}</strong></div>
                                <div style="font-size: 0.8em; color: #666;">
                                    ${alert.service_name} | ${new Date(alert.triggered_at).toLocaleString()}
                                </div>
                            </div>
                        `;
                    }).join('');
                    
                    document.getElementById('alerts').innerHTML = html;
                } catch (error) {
                    document.getElementById('alerts').innerHTML = 'Error loading alerts';
                }
            }
            
            async function loadPerformanceChart() {
                try {
                    // For demo, create a sample chart
                    const ctx = document.getElementById('performance-chart').getContext('2d');
                    
                    if (performanceChart) {
                        performanceChart.destroy();
                    }
                    
                    performanceChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
                            datasets: [{
                                label: 'Avg Response Time (ms)',
                                data: [120, 135, 125, 140, 130],
                                borderColor: '#3498db',
                                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Response Time (ms)'
                                    }
                                }
                            }
                        }
                    });
                } catch (error) {
                    console.error('Error loading performance chart:', error);
                }
            }
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8014))
    uvicorn.run(app, host="0.0.0.0", port=port)