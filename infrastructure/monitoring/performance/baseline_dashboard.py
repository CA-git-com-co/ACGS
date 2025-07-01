#!/usr/bin/env python3
"""
ACGS Performance Baseline Dashboard
Web dashboard for viewing and managing performance baselines across all services.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from baseline_metrics_collector import PerformanceBaselineCollector, baseline_collector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# FastAPI app
app = FastAPI(
    title="ACGS Performance Baseline Dashboard",
    description="Dashboard for monitoring and managing ACGS performance baselines",
    version="1.0.0",
)

# Templates and static files
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page."""
    try:
        # Load current baseline
        current_baseline = await baseline_collector.load_baseline()
        baseline_summary = (
            baseline_collector.get_baseline_summary() if current_baseline else {}
        )

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "baseline_summary": baseline_summary,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return HTMLResponse(f"<h1>Dashboard Error</h1><p>{str(e)}</p>", status_code=500)


@app.get("/api/baseline/current")
async def get_current_baseline():
    """Get current performance baseline."""
    try:
        baseline = await baseline_collector.load_baseline()
        if not baseline:
            raise HTTPException(status_code=404, detail="No baseline found")

        return baseline_collector.get_baseline_summary()
    except Exception as e:
        logger.error(f"Error getting current baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/baseline/{baseline_id}")
async def get_baseline(baseline_id: str):
    """Get specific baseline by ID."""
    try:
        baseline = await baseline_collector.load_baseline(baseline_id)
        if not baseline:
            raise HTTPException(
                status_code=404, detail=f"Baseline {baseline_id} not found"
            )

        return baseline_collector.get_baseline_summary()
    except Exception as e:
        logger.error(f"Error getting baseline {baseline_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/baseline/establish")
async def establish_new_baseline(duration_hours: int = 1):
    """Establish a new performance baseline."""
    try:
        if duration_hours < 1 or duration_hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400, detail="Duration must be between 1 and 168 hours"
            )

        # Start baseline collection in background
        asyncio.create_task(
            baseline_collector.establish_performance_baseline(duration_hours)
        )

        return {
            "message": f"Baseline collection started for {duration_hours} hours",
            "duration_hours": duration_hours,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    except Exception as e:
        logger.error(f"Error establishing baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services/status")
async def get_services_status():
    """Get current status of all services."""
    try:
        services_status = {}

        for service_name, port in baseline_collector.services.items():
            try:
                # Quick health check
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:{port}/health", timeout=5
                    ) as response:
                        services_status[service_name] = {
                            "port": port,
                            "status": (
                                "healthy" if response.status == 200 else "unhealthy"
                            ),
                            "response_code": response.status,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
            except Exception as e:
                services_status[service_name] = {
                    "port": port,
                    "status": "unreachable",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        return {
            "services": services_status,
            "total_services": len(services_status),
            "healthy_services": sum(
                1 for s in services_status.values() if s["status"] == "healthy"
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/live")
async def get_live_metrics():
    """Get live performance metrics."""
    try:
        live_metrics = {}

        for service_name, port in baseline_collector.services.items():
            metrics = await baseline_collector.measure_service_performance(
                service_name, port
            )
            live_metrics[service_name] = {
                "response_time_ms": metrics.get("response_time_ms", 0),
                "available": metrics.get("available", False),
                "constitutional_compliance": metrics.get(
                    "constitutional_compliance", 1.0
                ),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "metrics": live_metrics,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting live metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/baselines/list")
async def list_baselines():
    """List all available baselines."""
    try:
        baselines_dir = Path("infrastructure/monitoring/performance/baselines")
        baselines = []

        if baselines_dir.exists():
            for baseline_file in baselines_dir.glob("baseline_*.json"):
                try:
                    with open(baseline_file) as f:
                        baseline_data = json.load(f)

                    baselines.append(
                        {
                            "baseline_id": baseline_data["baseline_id"],
                            "version": baseline_data["version"],
                            "created_at": baseline_data["metadata"]["created_at"],
                            "duration_hours": baseline_data["metadata"][
                                "measurement_duration_hours"
                            ],
                            "sample_count": baseline_data["metadata"]["sample_count"],
                            "services_count": len(baseline_data["services"]),
                            "avg_response_time": baseline_data["system_wide"][
                                "overall_avg_response_time"
                            ],
                            "error_rate": baseline_data["system_wide"][
                                "overall_error_rate"
                            ],
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error reading baseline file {baseline_file}: {e}")

        return {
            "baselines": sorted(baselines, key=lambda x: x["created_at"], reverse=True),
            "total_count": len(baselines),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }
    except Exception as e:
        logger.error(f"Error listing baselines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/comparison/{baseline1_id}/{baseline2_id}")
async def compare_baselines(baseline1_id: str, baseline2_id: str):
    """Compare two baselines."""
    try:
        baseline1 = await baseline_collector.load_baseline(baseline1_id)
        baseline2 = await baseline_collector.load_baseline(baseline2_id)

        if not baseline1 or not baseline2:
            raise HTTPException(
                status_code=404, detail="One or both baselines not found"
            )

        comparison = {
            "baseline1": {
                "id": baseline1.baseline_id,
                "created_at": baseline1.created_at.isoformat(),
                "avg_response_time": baseline1.overall_avg_response_time,
                "error_rate": baseline1.overall_error_rate,
                "constitutional_compliance": baseline1.overall_constitutional_compliance,
            },
            "baseline2": {
                "id": baseline2.baseline_id,
                "created_at": baseline2.created_at.isoformat(),
                "avg_response_time": baseline2.overall_avg_response_time,
                "error_rate": baseline2.overall_error_rate,
                "constitutional_compliance": baseline2.overall_constitutional_compliance,
            },
            "differences": {
                "response_time_change_ms": baseline2.overall_avg_response_time
                - baseline1.overall_avg_response_time,
                "error_rate_change": baseline2.overall_error_rate
                - baseline1.overall_error_rate,
                "compliance_change": baseline2.overall_constitutional_compliance
                - baseline1.overall_constitutional_compliance,
            },
            "service_comparisons": {},
        }

        # Compare individual services
        for service_name in baseline1.services.keys():
            if service_name in baseline2.services:
                service1 = baseline1.services[service_name]
                service2 = baseline2.services[service_name]

                comparison["service_comparisons"][service_name] = {
                    "response_time_change_ms": service2.avg_response_time
                    - service1.avg_response_time,
                    "error_rate_change": service2.error_rate_percent
                    - service1.error_rate_percent,
                    "uptime_change": service2.uptime_percent - service1.uptime_percent,
                    "compliance_change": service2.constitutional_compliance_rate
                    - service1.constitutional_compliance_rate,
                }

        return comparison
    except Exception as e:
        logger.error(f"Error comparing baselines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "acgs-baseline-dashboard",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Create dashboard template
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS Performance Baseline Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #ecf0f1; border-radius: 5px; min-width: 150px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 14px; color: #7f8c8d; }
        .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .service-card { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .status-healthy { color: #27ae60; }
        .status-unhealthy { color: #e74c3c; }
        .constitutional-hash { font-family: monospace; background-color: #f8f9fa; padding: 5px; border-radius: 3px; }
        button { background-color: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background-color: #2980b9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ACGS Performance Baseline Dashboard</h1>
        <p>Constitutional Hash: <span class="constitutional-hash">{{ constitutional_hash }}</span></p>
        <p>Last Updated: {{ timestamp }}</p>
    </div>

    <div class="card">
        <h2>System Overview</h2>
        {% if baseline_summary %}
        <div class="metric">
            <div class="metric-value">{{ "%.2f"|format(baseline_summary.system_metrics.avg_response_time_ms) }}ms</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ "%.2f"|format(baseline_summary.system_metrics.error_rate_percent) }}%</div>
            <div class="metric-label">Error Rate</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ "%.1f"|format(baseline_summary.system_metrics.constitutional_compliance_percent) }}%</div>
            <div class="metric-label">Constitutional Compliance</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ baseline_summary.services_count }}</div>
            <div class="metric-label">Services Monitored</div>
        </div>
        {% else %}
        <p>No baseline data available. <button onclick="establishBaseline()">Establish Baseline</button></p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Service Performance</h2>
        <div class="service-grid" id="services-grid">
            <!-- Services will be loaded here -->
        </div>
    </div>

    <div class="card">
        <h2>Actions</h2>
        <button onclick="establishBaseline()">Establish New Baseline</button>
        <button onclick="refreshData()">Refresh Data</button>
        <button onclick="viewLiveMetrics()">View Live Metrics</button>
        <button onclick="compareBaselines()">Compare Baselines</button>
    </div>

    <script>
        async function loadServicesStatus() {
            try {
                const response = await fetch('/api/services/status');
                const data = await response.json();
                
                const grid = document.getElementById('services-grid');
                grid.innerHTML = '';
                
                for (const [serviceName, status] of Object.entries(data.services)) {
                    const card = document.createElement('div');
                    card.className = 'service-card';
                    card.innerHTML = `
                        <h3>${serviceName}</h3>
                        <p>Port: ${status.port}</p>
                        <p>Status: <span class="status-${status.status}">${status.status}</span></p>
                        <p>Last Check: ${new Date(status.timestamp).toLocaleString()}</p>
                    `;
                    grid.appendChild(card);
                }
            } catch (error) {
                console.error('Error loading services status:', error);
            }
        }

        async function establishBaseline() {
            const hours = prompt('Enter baseline duration in hours (1-168):', '1');
            if (hours && hours >= 1 && hours <= 168) {
                try {
                    const response = await fetch(`/api/baseline/establish?duration_hours=${hours}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    alert(`Baseline collection started for ${hours} hours`);
                } catch (error) {
                    alert('Error establishing baseline: ' + error.message);
                }
            }
        }

        function refreshData() {
            location.reload();
        }

        async function viewLiveMetrics() {
            try {
                const response = await fetch('/api/metrics/live');
                const data = await response.json();
                
                let metricsText = 'Live Metrics:\\n\\n';
                for (const [service, metrics] of Object.entries(data.metrics)) {
                    metricsText += `${service}:\\n`;
                    metricsText += `  Response Time: ${metrics.response_time_ms.toFixed(2)}ms\\n`;
                    metricsText += `  Available: ${metrics.available}\\n`;
                    metricsText += `  Constitutional Compliance: ${(metrics.constitutional_compliance * 100).toFixed(1)}%\\n\\n`;
                }
                
                alert(metricsText);
            } catch (error) {
                alert('Error getting live metrics: ' + error.message);
            }
        }

        async function compareBaselines() {
            try {
                const response = await fetch('/api/baselines/list');
                const data = await response.json();
                
                if (data.baselines.length < 2) {
                    alert('Need at least 2 baselines to compare');
                    return;
                }
                
                let baselinesList = 'Available Baselines:\\n\\n';
                data.baselines.forEach((baseline, index) => {
                    baselinesList += `${index + 1}. ${baseline.baseline_id} (${new Date(baseline.created_at).toLocaleDateString()})\\n`;
                });
                
                alert(baselinesList);
            } catch (error) {
                alert('Error listing baselines: ' + error.message);
            }
        }

        // Load services status on page load
        loadServicesStatus();
        
        // Refresh services status every 30 seconds
        setInterval(loadServicesStatus, 30000);
    </script>
</body>
</html>
"""


# Create templates directory and save template
def create_dashboard_template():
    """Create dashboard template file."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    template_file = templates_dir / "dashboard.html"
    with open(template_file, "w") as f:
        f.write(dashboard_template)


if __name__ == "__main__":
    # Create template
    create_dashboard_template()

    # Start dashboard server
    uvicorn.run(app, host="0.0.0.0", port=8094, log_level="info")
