#!/usr/bin/env python3
"""
Real-time ACGS Monitoring Dashboard

Create a monitoring interface showing agent activity, HITL decisions, and system health.
Display key metrics: decision latency, escalation rates, agent confidence scores, constitutional compliance rates.
Include alerts for performance degradation or security violations.
"""

import asyncio
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime, timedelta
import httpx
import redis
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "user": "acgs_user",
    "password": "acgs_secure_password",
    "database": "acgs_db",
}

REDIS_CONFIG = {"host": "localhost", "port": 6389, "db": 0}

SERVICES = {
    "ac_service": "http://localhost:8001",
    "hitl_service": "http://localhost:8008",
    "auth_service": "http://localhost:8016",
}

app = FastAPI(title="ACGS Real-time Monitoring Dashboard")


class ACGSMonitor:
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.metrics_cache = {}
        self.alerts = []

    async def initialize(self):
        """Initialize database and Redis connections."""
        try:
            # Initialize Redis
            self.redis_client = redis.Redis(
                host=REDIS_CONFIG["host"],
                port=REDIS_CONFIG["port"],
                db=REDIS_CONFIG["db"],
                decode_responses=True,
            )

            # Initialize database pool
            self.db_pool = await asyncpg.create_pool(
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                user=DATABASE_CONFIG["user"],
                password=DATABASE_CONFIG["password"],
                database=DATABASE_CONFIG["database"],
                min_size=2,
                max_size=10,
            )

            print("✅ ACGS Monitor initialized successfully")

        except Exception as e:
            print(f"❌ Failed to initialize ACGS Monitor: {e}")
            raise

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "overall_status": "healthy",
            "alerts": len(self.alerts),
        }

        # Check each service
        for service_name, service_url in SERVICES.items():
            try:
                start_time = time.perf_counter()
                response = await self.http_client.get(
                    f"{service_url}/health", timeout=5.0
                )
                response_time = (time.perf_counter() - start_time) * 1000

                health_data["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response_time,
                    "last_check": datetime.utcnow().isoformat(),
                }

                if response.status_code != 200:
                    health_data["overall_status"] = "degraded"

            except Exception as e:
                health_data["services"][service_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat(),
                }
                health_data["overall_status"] = "degraded"

        return health_data

    async def get_hitl_metrics(self) -> Dict[str, Any]:
        """Get HITL decision metrics."""
        try:
            async with self.db_pool.acquire() as conn:
                # Get recent HITL decisions
                recent_decisions = await conn.fetch(
                    """
                    SELECT 
                        escalation_level,
                        decision_latency_ms,
                        constitutional_compliance_score,
                        created_at
                    FROM agent_operation_reviews 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    ORDER BY created_at DESC
                    LIMIT 100
                """
                )

                if not recent_decisions:
                    return {
                        "total_decisions": 0,
                        "avg_latency_ms": 0,
                        "escalation_rate": 0,
                        "compliance_rate": 0,
                        "decisions_per_minute": 0,
                    }

                # Calculate metrics
                latencies = [
                    row["decision_latency_ms"]
                    for row in recent_decisions
                    if row["decision_latency_ms"]
                ]
                escalations = [
                    row for row in recent_decisions if row["escalation_level"] > 1
                ]
                compliance_scores = [
                    row["constitutional_compliance_score"]
                    for row in recent_decisions
                    if row["constitutional_compliance_score"]
                ]

                # Calculate decisions per minute
                if recent_decisions:
                    time_span = (
                        datetime.utcnow() - recent_decisions[-1]["created_at"]
                    ).total_seconds() / 60
                    decisions_per_minute = len(recent_decisions) / max(time_span, 1)
                else:
                    decisions_per_minute = 0

                return {
                    "total_decisions": len(recent_decisions),
                    "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
                    "p95_latency_ms": (
                        sorted(latencies)[int(0.95 * len(latencies))]
                        if latencies
                        else 0
                    ),
                    "p99_latency_ms": (
                        sorted(latencies)[int(0.99 * len(latencies))]
                        if latencies
                        else 0
                    ),
                    "escalation_rate": (
                        len(escalations) / len(recent_decisions)
                        if recent_decisions
                        else 0
                    ),
                    "compliance_rate": (
                        statistics.mean(compliance_scores) if compliance_scores else 0
                    ),
                    "decisions_per_minute": decisions_per_minute,
                    "last_updated": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            return {"error": str(e)}

    async def get_agent_metrics(self) -> Dict[str, Any]:
        """Get agent activity and confidence metrics."""
        try:
            async with self.db_pool.acquire() as conn:
                # Get agent confidence profiles
                agent_profiles = await conn.fetch(
                    """
                    SELECT 
                        agent_id,
                        operation_confidence_adjustments,
                        updated_at
                    FROM agent_confidence_profiles 
                    WHERE updated_at > NOW() - INTERVAL '24 hours'
                    ORDER BY updated_at DESC
                """
                )

                # Get recent agent operations
                recent_operations = await conn.fetch(
                    """
                    SELECT 
                        agent_id,
                        operation_type,
                        escalation_level,
                        created_at
                    FROM agent_operation_reviews 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """
                )

                # Calculate metrics
                active_agents = len(set(row["agent_id"] for row in recent_operations))

                # Agent activity by type
                operation_types = {}
                for row in recent_operations:
                    op_type = row["operation_type"]
                    operation_types[op_type] = operation_types.get(op_type, 0) + 1

                return {
                    "active_agents": active_agents,
                    "total_agent_profiles": len(agent_profiles),
                    "operations_last_hour": len(recent_operations),
                    "operation_types": operation_types,
                    "last_updated": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            return {"error": str(e)}

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            # Get Redis performance
            redis_info = self.redis_client.info()

            # Test Redis latency
            start_time = time.perf_counter()
            self.redis_client.ping()
            redis_latency = (time.perf_counter() - start_time) * 1000

            # Get database performance
            async with self.db_pool.acquire() as conn:
                start_time = time.perf_counter()
                await conn.fetchval("SELECT 1")
                db_latency = (time.perf_counter() - start_time) * 1000

            return {
                "redis": {
                    "latency_ms": redis_latency,
                    "used_memory_mb": redis_info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "commands_processed": redis_info.get("total_commands_processed", 0),
                },
                "database": {
                    "latency_ms": db_latency,
                    "active_connections": self.db_pool.get_size(),
                },
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance degradation or security violations."""
        new_alerts = []

        try:
            # Get current metrics
            hitl_metrics = await self.get_hitl_metrics()
            performance_metrics = await self.get_performance_metrics()

            # Check HITL latency alerts
            if hitl_metrics.get("p99_latency_ms", 0) > 5.0:
                new_alerts.append(
                    {
                        "type": "performance",
                        "severity": "warning",
                        "message": f"HITL P99 latency ({hitl_metrics['p99_latency_ms']:.2f}ms) exceeds 5ms target",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Check escalation rate alerts
            if hitl_metrics.get("escalation_rate", 0) > 0.2:
                new_alerts.append(
                    {
                        "type": "security",
                        "severity": "warning",
                        "message": f"High escalation rate ({hitl_metrics['escalation_rate']*100:.1f}%) detected",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Check compliance rate alerts
            if hitl_metrics.get("compliance_rate", 1.0) < 0.95:
                new_alerts.append(
                    {
                        "type": "security",
                        "severity": "critical",
                        "message": f"Low constitutional compliance rate ({hitl_metrics['compliance_rate']*100:.1f}%)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Check Redis latency
            if performance_metrics.get("redis", {}).get("latency_ms", 0) > 10.0:
                new_alerts.append(
                    {
                        "type": "performance",
                        "severity": "warning",
                        "message": f"High Redis latency ({performance_metrics['redis']['latency_ms']:.2f}ms)",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Add new alerts to the list (keep last 50)
            self.alerts.extend(new_alerts)
            self.alerts = self.alerts[-50:]

            return new_alerts

        except Exception as e:
            return [
                {
                    "type": "system",
                    "severity": "error",
                    "message": f"Alert check failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ]

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            "system_health": await self.get_system_health(),
            "hitl_metrics": await self.get_hitl_metrics(),
            "agent_metrics": await self.get_agent_metrics(),
            "performance_metrics": await self.get_performance_metrics(),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global monitor instance
monitor = ACGSMonitor()


@app.on_event("startup")
async def startup_event():
    """Initialize the monitor on startup."""
    await monitor.initialize()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the monitoring dashboard."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS Real-time Monitoring Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
            .metric-value { font-size: 24px; font-weight: bold; color: #27ae60; }
            .metric-unit { font-size: 14px; color: #7f8c8d; }
            .status-healthy { color: #27ae60; }
            .status-warning { color: #f39c12; }
            .status-error { color: #e74c3c; }
            .alerts { background: #fff; padding: 20px; border-radius: 8px; margin-top: 20px; }
            .alert { padding: 10px; margin: 5px 0; border-radius: 4px; }
            .alert-warning { background: #fff3cd; border-left: 4px solid #ffc107; }
            .alert-critical { background: #f8d7da; border-left: 4px solid #dc3545; }
            .alert-error { background: #f8d7da; border-left: 4px solid #dc3545; }
            #data { white-space: pre-wrap; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 ACGS Real-time Monitoring Dashboard</h1>
            <p>Autonomous Coding Governance System - Live Metrics</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">System Health</div>
                <div id="system-status" class="metric-value">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">HITL Decision Latency (P99)</div>
                <div id="hitl-latency" class="metric-value">Loading...</div>
                <span class="metric-unit">ms</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Escalation Rate</div>
                <div id="escalation-rate" class="metric-value">Loading...</div>
                <span class="metric-unit">%</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Constitutional Compliance</div>
                <div id="compliance-rate" class="metric-value">Loading...</div>
                <span class="metric-unit">%</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Active Agents</div>
                <div id="active-agents" class="metric-value">Loading...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Decisions/Minute</div>
                <div id="decisions-per-minute" class="metric-value">Loading...</div>
            </div>
        </div>
        
        <div class="alerts">
            <h2>🚨 Recent Alerts</h2>
            <div id="alerts-container">Loading alerts...</div>
        </div>
        
        <div class="alerts">
            <h2>📊 Raw Data</h2>
            <div id="data">Loading...</div>
        </div>

        <script>
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/dashboard');
                    const data = await response.json();
                    
                    // Update system health
                    const systemStatus = document.getElementById('system-status');
                    systemStatus.textContent = data.system_health.overall_status.toUpperCase();
                    systemStatus.className = 'metric-value status-' + (data.system_health.overall_status === 'healthy' ? 'healthy' : 'warning');
                    
                    // Update HITL metrics
                    document.getElementById('hitl-latency').textContent = data.hitl_metrics.p99_latency_ms?.toFixed(2) || '0.00';
                    document.getElementById('escalation-rate').textContent = ((data.hitl_metrics.escalation_rate || 0) * 100).toFixed(1);
                    document.getElementById('compliance-rate').textContent = ((data.hitl_metrics.compliance_rate || 0) * 100).toFixed(1);
                    document.getElementById('decisions-per-minute').textContent = (data.hitl_metrics.decisions_per_minute || 0).toFixed(1);
                    
                    // Update agent metrics
                    document.getElementById('active-agents').textContent = data.agent_metrics.active_agents || 0;
                    
                    // Update alerts
                    const alertsContainer = document.getElementById('alerts-container');
                    if (data.alerts && data.alerts.length > 0) {
                        alertsContainer.innerHTML = data.alerts.map(alert => 
                            `<div class="alert alert-${alert.severity}">
                                <strong>${alert.type.toUpperCase()}</strong>: ${alert.message}
                                <br><small>${alert.timestamp}</small>
                            </div>`
                        ).join('');
                    } else {
                        alertsContainer.innerHTML = '<div class="status-healthy">No active alerts</div>';
                    }
                    
                    // Update raw data
                    document.getElementById('data').textContent = JSON.stringify(data, null, 2);
                    
                } catch (error) {
                    console.error('Failed to update dashboard:', error);
                }
            }
            
            // Update every 5 seconds
            updateDashboard();
            setInterval(updateDashboard, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/dashboard")
async def get_dashboard_api():
    """API endpoint for dashboard data."""
    return await monitor.get_dashboard_data()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "acgs_monitoring_dashboard",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def main():
    """Run the monitoring dashboard."""
    print("🚀 Starting ACGS Real-time Monitoring Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    print("🔗 API endpoint: http://localhost:8080/api/dashboard")

    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
