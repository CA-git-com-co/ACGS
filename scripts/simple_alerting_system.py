#!/usr/bin/env python3
"""
Simple Alerting System for ACGS-1 Services
Monitors services and sends alerts when thresholds are breached
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("acgs_alerting")

# Alert thresholds
ALERT_THRESHOLDS = {
    "response_time_ms": 500,  # Alert if response time > 500ms
    "uptime_percentage": 99.0,  # Alert if uptime < 99%
    "consecutive_failures": 3,  # Alert after 3 consecutive failures
}

# Service configuration
SERVICES = {
    "auth": {
        "name": "Authentication Service",
        "port": 8000,
        "url": "http://localhost:8000",
    },
    "ac": {
        "name": "Constitutional AI Service",
        "port": 8001,
        "url": "http://localhost:8001",
    },
    "integrity": {
        "name": "Integrity Service",
        "port": 8002,
        "url": "http://localhost:8002",
    },
    "fv": {
        "name": "Formal Verification Service",
        "port": 8003,
        "url": "http://localhost:8003",
    },
    "gs": {
        "name": "Governance Synthesis Service",
        "port": 8004,
        "url": "http://localhost:8004",
    },
    "pgc": {
        "name": "Policy Governance Service",
        "port": 8005,
        "url": "http://localhost:8005",
    },
    "ec": {
        "name": "Evolutionary Computation Service",
        "port": 8006,
        "url": "http://localhost:8006",
    },
}

# Alert state tracking
alert_state = {
    "active_alerts": {},
    "alert_history": [],
    "service_stats": {
        service_id: {"total_checks": 0, "failures": 0, "consecutive_failures": 0}
        for service_id in SERVICES.keys()
    },
}


class Alert:
    def __init__(
        self, service_id: str, alert_type: str, message: str, severity: str = "warning"
    ):
        self.service_id = service_id
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()
        self.alert_id = f"{service_id}_{alert_type}_{int(time.time())}"

    def to_dict(self):
        return {
            "alert_id": self.alert_id,
            "service_id": self.service_id,
            "service_name": SERVICES[self.service_id]["name"],
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "port": SERVICES[self.service_id]["port"],
        }


async def check_service_health(service_id: str, service_config: Dict) -> Dict[str, Any]:
    """Check health of a single service"""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
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
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "http_status": response.status,
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.now().isoformat(),
                    }
    except Exception as e:
        return {
            "status": "error",
            "response_time_ms": None,
            "http_status": None,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def process_alerts(service_id: str, health_data: Dict[str, Any]):
    """Process health data and generate alerts if needed"""
    stats = alert_state["service_stats"][service_id]
    stats["total_checks"] += 1

    alerts_to_fire = []
    alerts_to_clear = []

    # Check if service is down
    if health_data["status"] in ["unhealthy", "error"]:
        stats["failures"] += 1
        stats["consecutive_failures"] += 1

        # Alert on consecutive failures
        if stats["consecutive_failures"] >= ALERT_THRESHOLDS["consecutive_failures"]:
            alert_key = f"{service_id}_service_down"
            if alert_key not in alert_state["active_alerts"]:
                alert = Alert(
                    service_id=service_id,
                    alert_type="service_down",
                    message=f"Service has been down for {stats['consecutive_failures']} consecutive checks. Error: {health_data.get('error', 'Unknown')}",
                    severity="critical",
                )
                alerts_to_fire.append(alert)
    else:
        # Service is healthy, reset consecutive failures
        if stats["consecutive_failures"] > 0:
            # Clear service down alert if it exists
            alert_key = f"{service_id}_service_down"
            if alert_key in alert_state["active_alerts"]:
                alerts_to_clear.append(alert_key)

        stats["consecutive_failures"] = 0

        # Check response time
        response_time = health_data.get("response_time_ms")
        if response_time and response_time > ALERT_THRESHOLDS["response_time_ms"]:
            alert_key = f"{service_id}_high_response_time"
            if alert_key not in alert_state["active_alerts"]:
                alert = Alert(
                    service_id=service_id,
                    alert_type="high_response_time",
                    message=f"Response time ({response_time:.2f}ms) exceeds threshold ({ALERT_THRESHOLDS['response_time_ms']}ms)",
                    severity="warning",
                )
                alerts_to_fire.append(alert)
        else:
            # Clear high response time alert if it exists
            alert_key = f"{service_id}_high_response_time"
            if alert_key in alert_state["active_alerts"]:
                alerts_to_clear.append(alert_key)

    # Fire new alerts
    for alert in alerts_to_fire:
        alert_state["active_alerts"][f"{alert.service_id}_{alert.alert_type}"] = alert
        alert_state["alert_history"].append(alert.to_dict())
        logger.warning(f"🚨 ALERT FIRED: {alert.message}")

    # Clear resolved alerts
    for alert_key in alerts_to_clear:
        if alert_key in alert_state["active_alerts"]:
            resolved_alert = alert_state["active_alerts"].pop(alert_key)
            logger.info(
                f"✅ ALERT CLEARED: {resolved_alert.service_id} - {resolved_alert.alert_type}"
            )


async def monitoring_loop():
    """Main monitoring loop"""
    logger.info("🚀 Starting ACGS-1 Alerting System")
    logger.info(f"📊 Monitoring {len(SERVICES)} services")
    logger.info(f"⚠️ Alert thresholds: {ALERT_THRESHOLDS}")

    while True:
        try:
            # Check all services
            tasks = []
            for service_id, service_config in SERVICES.items():
                tasks.append(check_service_health(service_id, service_config))

            results = await asyncio.gather(*tasks)

            # Process results and generate alerts
            for i, (service_id, service_config) in enumerate(SERVICES.items()):
                health_data = results[i]
                process_alerts(service_id, health_data)

            # Log summary
            healthy_services = sum(
                1 for result in results if result["status"] == "healthy"
            )
            total_services = len(results)
            active_alerts_count = len(alert_state["active_alerts"])

            logger.info(
                f"📈 Health Check Complete: {healthy_services}/{total_services} services healthy, {active_alerts_count} active alerts"
            )

            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"❌ Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait longer on error


def get_alert_summary():
    """Get current alert summary"""
    return {
        "active_alerts": [
            alert.to_dict() for alert in alert_state["active_alerts"].values()
        ],
        "total_active_alerts": len(alert_state["active_alerts"]),
        "alert_history_count": len(alert_state["alert_history"]),
        "service_stats": alert_state["service_stats"],
        "thresholds": ALERT_THRESHOLDS,
        "last_check": datetime.now().isoformat(),
    }


def save_alert_report():
    """Save alert report to file"""
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": get_alert_summary(),
        "recent_alerts": alert_state["alert_history"][-50:],  # Last 50 alerts
    }

    with open("alert_report.json", "w") as f:
        json.dump(report, f, indent=2)

    logger.info("📋 Alert report saved to alert_report.json")


async def main():
    """Main function"""
    try:
        # Start monitoring loop
        await monitoring_loop()
    except KeyboardInterrupt:
        logger.info("🔄 Shutting down alerting system...")
        save_alert_report()
        logger.info("✅ Alerting system shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
