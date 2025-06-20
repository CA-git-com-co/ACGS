#!/usr/bin/env python3
"""
Simple Monitoring Dashboard for ACGS-1 Services
Provides a web-based dashboard to monitor all 7 core services
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="ACGS-1 Monitoring Dashboard",
    description="Simple monitoring dashboard for ACGS-1 services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service configuration
SERVICES = {
    "auth": {"name": "Authentication Service", "port": 8000, "url": "http://localhost:8000"},
    "ac": {"name": "Constitutional AI Service", "port": 8001, "url": "http://localhost:8001"},
    "integrity": {"name": "Integrity Service", "port": 8002, "url": "http://localhost:8002"},
    "fv": {"name": "Formal Verification Service", "port": 8003, "url": "http://localhost:8003"},
    "gs": {"name": "Governance Synthesis Service", "port": 8004, "url": "http://localhost:8004"},
    "pgc": {"name": "Policy Governance Service", "port": 8005, "url": "http://localhost:8005"},
    "ec": {"name": "Evolutionary Computation Service", "port": 8006, "url": "http://localhost:8006"},
}

# Global metrics storage
metrics_data = {
    "services": {},
    "system": {
        "start_time": time.time(),
        "total_requests": 0,
        "last_update": None
    }
}

async def check_service_health(service_id: str, service_config: Dict) -> Dict[str, Any]:
    """Check health of a single service"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            start_time = time.time()
            async with session.get(f"{service_config['url']}/health") as response:
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                if response.status == 200:
                    health_data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "http_status": response.status,
                        "details": health_data,
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "http_status": response.status,
                        "error": f"HTTP {response.status}",
                        "last_check": datetime.now().isoformat()
                    }
    except Exception as e:
        return {
            "status": "error",
            "response_time_ms": None,
            "http_status": None,
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

async def collect_all_metrics():
    """Collect metrics from all services"""
    tasks = []
    for service_id, service_config in SERVICES.items():
        tasks.append(check_service_health(service_id, service_config))
    
    results = await asyncio.gather(*tasks)
    
    # Update metrics data
    for i, (service_id, service_config) in enumerate(SERVICES.items()):
        metrics_data["services"][service_id] = {
            "name": service_config["name"],
            "port": service_config["port"],
            "health": results[i]
        }
    
    metrics_data["system"]["last_update"] = datetime.now().isoformat()
    metrics_data["system"]["total_requests"] += 1

@app.get("/")
async def dashboard():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-1 Monitoring Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .service-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status-healthy { color: #28a745; font-weight: bold; }
            .status-unhealthy { color: #dc3545; font-weight: bold; }
            .status-error { color: #ffc107; font-weight: bold; }
            .metric { margin: 10px 0; }
            .metric-label { font-weight: bold; color: #666; }
            .metric-value { color: #333; }
            .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0; }
            .refresh-btn:hover { background: #0056b3; }
            .system-info { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        </style>
        <script>
            async function refreshMetrics() {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    updateDashboard(data);
                } catch (error) {
                    console.error('Failed to refresh metrics:', error);
                }
            }
            
            function updateDashboard(data) {
                // Update system info
                document.getElementById('last-update').textContent = data.system.last_update || 'Never';
                document.getElementById('total-requests').textContent = data.system.total_requests;
                
                // Update service cards
                Object.entries(data.services).forEach(([serviceId, serviceData]) => {
                    const card = document.getElementById(`service-${serviceId}`);
                    if (card) {
                        const health = serviceData.health;
                        const statusElement = card.querySelector('.service-status');
                        const responseTimeElement = card.querySelector('.response-time');
                        const lastCheckElement = card.querySelector('.last-check');
                        
                        statusElement.textContent = health.status.toUpperCase();
                        statusElement.className = `service-status status-${health.status}`;
                        
                        responseTimeElement.textContent = health.response_time_ms ? `${health.response_time_ms}ms` : 'N/A';
                        lastCheckElement.textContent = health.last_check || 'Never';
                    }
                });
            }
            
            // Auto-refresh every 30 seconds
            setInterval(refreshMetrics, 30000);
            
            // Initial load
            window.onload = refreshMetrics;
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🚀 ACGS-1 Monitoring Dashboard</h1>
            <p>Real-time monitoring of all 7 core services</p>
        </div>
        
        <div class="system-info">
            <h3>📊 System Overview</h3>
            <div class="metric">
                <span class="metric-label">Last Update:</span>
                <span class="metric-value" id="last-update">Loading...</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Health Checks:</span>
                <span class="metric-value" id="total-requests">Loading...</span>
            </div>
            <button class="refresh-btn" onclick="refreshMetrics()">🔄 Refresh Now</button>
        </div>
        
        <div class="metrics-grid">
            <div class="service-card" id="service-auth">
                <h3>🔐 Authentication Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8000</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-ac">
                <h3>⚖️ Constitutional AI Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8001</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-integrity">
                <h3>🔒 Integrity Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8002</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-fv">
                <h3>✅ Formal Verification Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8003</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-gs">
                <h3>🏛️ Governance Synthesis Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8004</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-pgc">
                <h3>📋 Policy Governance Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8005</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
            
            <div class="service-card" id="service-ec">
                <h3>🧬 Evolutionary Computation Service</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="service-status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value response-time">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Port:</span>
                    <span class="metric-value">8006</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Check:</span>
                    <span class="metric-value last-check">Loading...</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/metrics")
async def get_metrics():
    """API endpoint to get current metrics"""
    await collect_all_metrics()
    return metrics_data

@app.get("/health")
async def health_check():
    """Health check for the monitoring service itself"""
    return {
        "status": "healthy",
        "service": "monitoring_dashboard",
        "version": "1.0.0",
        "uptime_seconds": time.time() - metrics_data["system"]["start_time"]
    }

if __name__ == "__main__":
    print("🚀 Starting ACGS-1 Monitoring Dashboard on port 3000")
    print("📊 Dashboard: http://localhost:3000")
    print("📈 Metrics API: http://localhost:3000/api/metrics")
    uvicorn.run(app, host="0.0.0.0", port=3000)
