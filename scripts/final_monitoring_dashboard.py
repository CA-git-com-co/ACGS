#!/usr/bin/env python3
"""
Final ACGS Monitoring Dashboard

A simple monitoring interface using only standard library and available modules.
"""

import asyncio
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Configuration
SERVICES = {
    "ac_service": "http://localhost:8001",
    "hitl_service": "http://localhost:8008",
    "auth_service": "http://localhost:8016"
}

app = FastAPI(title="ACGS Final Monitoring Dashboard")

class FinalACGSMonitor:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.alerts = []
        
    async def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all services."""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "overall_status": "healthy",
            "healthy_services": 0,
            "total_services": len(SERVICES)
        }
        
        for service_name, service_url in SERVICES.items():
            try:
                start_time = time.perf_counter()
                response = await self.http_client.get(f"{service_url}/health", timeout=5.0)
                response_time = (time.perf_counter() - start_time) * 1000
                
                service_data = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "last_check": datetime.utcnow().isoformat()
                }
                
                if response.status_code == 200:
                    health_data["healthy_services"] += 1
                    try:
                        service_data["data"] = response.json()
                    except:
                        pass
                else:
                    health_data["overall_status"] = "degraded"
                    
                health_data["services"][service_name] = service_data
                
            except Exception as e:
                health_data["services"][service_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                health_data["overall_status"] = "degraded"
        
        return health_data
    
    async def test_hitl_performance(self) -> Dict[str, Any]:
        """Test HITL service performance."""
        try:
            test_request = {
                "agent_id": "dashboard-monitor",
                "agent_type": "monitoring_test",
                "operation_type": "dashboard_check",
                "operation_description": "Dashboard monitoring test",
                "operation_context": {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "test_id": "dashboard-monitor"
                }
            }
            
            start_time = time.perf_counter()
            response = await self.http_client.post(
                f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                json=test_request,
                timeout=5.0
            )
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "latency_ms": latency_ms,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_data": response.json() if response.status_code == 200 else None,
                "last_updated": datetime.utcnow().isoformat()
            }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        service_health = await self.get_service_health()
        hitl_performance = await self.test_hitl_performance()
        
        # Check for alerts
        new_alerts = []
        if hitl_performance.get("latency_ms", 0) > 5.0:
            new_alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": f"HITL latency ({hitl_performance['latency_ms']:.2f}ms) exceeds 5ms target",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if not hitl_performance.get("success", False):
            new_alerts.append({
                "type": "reliability",
                "severity": "error",
                "message": "HITL service not responding correctly",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if service_health["overall_status"] != "healthy":
            new_alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"System status degraded: {service_health['healthy_services']}/{service_health['total_services']} services healthy",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Add to alerts list (keep last 10)
        self.alerts.extend(new_alerts)
        self.alerts = self.alerts[-10:]
        
        return {
            "system_health": service_health,
            "hitl_performance": hitl_performance,
            "alerts": self.alerts,
            "summary": {
                "overall_status": service_health["overall_status"],
                "healthy_services": f"{service_health['healthy_services']}/{service_health['total_services']}",
                "hitl_latency": hitl_performance.get("latency_ms", 0),
                "hitl_success": hitl_performance.get("success", False),
                "active_alerts": len([a for a in self.alerts if a.get("severity") in ["warning", "error"]])
            },
            "timestamp": datetime.utcnow().isoformat()
        }

# Global monitor instance
monitor = FinalACGSMonitor()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the monitoring dashboard."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS Final Monitoring Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }
            .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
            .metric-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
            .metric-card:hover { transform: translateY(-2px); }
            .metric-title { font-size: 0.9rem; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
            .metric-value { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
            .metric-unit { font-size: 0.9rem; color: #6c757d; }
            .status-healthy { color: #28a745; }
            .status-warning { color: #ffc107; }
            .status-error { color: #dc3545; }
            .status-degraded { color: #fd7e14; }
            .alerts-section { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem; }
            .alerts-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #495057; }
            .alert { padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid; }
            .alert-warning { background: #fff3cd; border-color: #ffc107; }
            .alert-error { background: #f8d7da; border-color: #dc3545; }
            .no-alerts { text-align: center; color: #28a745; font-weight: 500; padding: 2rem; }
            .last-updated { text-align: center; color: #6c757d; font-size: 0.9rem; margin-top: 2rem; }
            .loading { opacity: 0.6; }
            .services-detail { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem; }
            .service-item { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid #e9ecef; }
            .service-item:last-child { border-bottom: none; }
            .service-name { font-weight: 600; }
            .service-status { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
            .service-status.healthy { background: #d4edda; color: #155724; }
            .service-status.error { background: #f8d7da; color: #721c24; }
            .service-status.unhealthy { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 ACGS Final Monitoring Dashboard</h1>
            <p>Autonomous Coding Governance System - Live Infrastructure Status</p>
        </div>
        
        <div class="container">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">System Health</div>
                    <div id="system-status" class="metric-value">Loading...</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Services Online</div>
                    <div id="services-online" class="metric-value">Loading...</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">HITL Latency</div>
                    <div id="hitl-latency" class="metric-value">Loading...</div>
                    <span class="metric-unit">ms</span>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">HITL Status</div>
                    <div id="hitl-status" class="metric-value">Loading...</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Active Alerts</div>
                    <div id="active-alerts" class="metric-value">Loading...</div>
                </div>
            </div>
            
            <div class="services-detail">
                <div class="alerts-title">🔧 Service Details</div>
                <div id="services-container">Loading services...</div>
            </div>
            
            <div class="alerts-section">
                <div class="alerts-title">🚨 Recent Alerts</div>
                <div id="alerts-container">
                    <div class="no-alerts">Loading alerts...</div>
                </div>
            </div>
            
            <div class="last-updated" id="last-updated">Last updated: Loading...</div>
        </div>

        <script>
            async function updateDashboard() {
                try {
                    document.body.classList.add('loading');
                    
                    const response = await fetch('/api/dashboard');
                    const data = await response.json();
                    
                    // Update system health
                    const systemStatus = document.getElementById('system-status');
                    const status = data.summary.overall_status.toUpperCase();
                    systemStatus.textContent = status;
                    systemStatus.className = 'metric-value status-' + data.summary.overall_status;
                    
                    // Update services online
                    document.getElementById('services-online').textContent = data.summary.healthy_services;
                    
                    // Update HITL metrics
                    const hitlLatency = data.summary.hitl_latency;
                    const latencyElement = document.getElementById('hitl-latency');
                    latencyElement.textContent = hitlLatency ? hitlLatency.toFixed(2) : '0.00';
                    latencyElement.className = 'metric-value ' + (hitlLatency > 5 ? 'status-warning' : 'status-healthy');
                    
                    const hitlStatus = document.getElementById('hitl-status');
                    hitlStatus.textContent = data.summary.hitl_success ? 'ONLINE' : 'OFFLINE';
                    hitlStatus.className = 'metric-value ' + (data.summary.hitl_success ? 'status-healthy' : 'status-error');
                    
                    // Update active alerts
                    const alertsCount = data.summary.active_alerts;
                    const alertsElement = document.getElementById('active-alerts');
                    alertsElement.textContent = alertsCount;
                    alertsElement.className = 'metric-value ' + (alertsCount > 0 ? 'status-warning' : 'status-healthy');
                    
                    // Update services detail
                    const servicesContainer = document.getElementById('services-container');
                    if (data.system_health && data.system_health.services) {
                        servicesContainer.innerHTML = Object.entries(data.system_health.services).map(([name, service]) => 
                            `<div class="service-item">
                                <div>
                                    <div class="service-name">${name.replace('_', ' ').toUpperCase()}</div>
                                    <small>${service.response_time_ms ? service.response_time_ms.toFixed(2) + 'ms' : 'N/A'}</small>
                                </div>
                                <div class="service-status ${service.status}">${service.status.toUpperCase()}</div>
                            </div>`
                        ).join('');
                    }
                    
                    // Update alerts
                    const alertsContainer = document.getElementById('alerts-container');
                    if (data.alerts && data.alerts.length > 0) {
                        alertsContainer.innerHTML = data.alerts.map(alert => 
                            `<div class="alert alert-${alert.severity}">
                                <strong>${alert.type.toUpperCase()}</strong>: ${alert.message}
                                <br><small>${new Date(alert.timestamp).toLocaleString()}</small>
                            </div>`
                        ).join('');
                    } else {
                        alertsContainer.innerHTML = '<div class="no-alerts">✅ No active alerts - All systems operating normally</div>';
                    }
                    
                    // Update timestamp
                    document.getElementById('last-updated').textContent = 
                        'Last updated: ' + new Date(data.timestamp).toLocaleString();
                    
                    document.body.classList.remove('loading');
                    
                } catch (error) {
                    console.error('Failed to update dashboard:', error);
                    document.body.classList.remove('loading');
                }
            }
            
            // Update immediately and then every 15 seconds
            updateDashboard();
            setInterval(updateDashboard, 15000);
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
        "service": "acgs_final_monitoring_dashboard", 
        "timestamp": datetime.utcnow().isoformat()
    }

async def main():
    """Run the monitoring dashboard."""
    print("🚀 Starting ACGS Final Monitoring Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    print("🔗 API endpoint: http://localhost:8080/api/dashboard")
    print("💡 Press Ctrl+C to stop")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
