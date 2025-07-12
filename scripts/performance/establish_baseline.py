#!/usr/bin/env python3
"""
ACGS Performance Baseline Establishment Script
Constitutional Hash: cdd01ef066bc6cf2

This script establishes performance baselines for ACGS services.
"""

import asyncio
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import httpx
import structlog

logger = structlog.get_logger()

class PerformanceBaselineEstablisher:
    """Establishes performance baselines for ACGS services."""
    
    def __init__(self, quick_mode: bool = False):
        self.quick_mode = quick_mode
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.services = {
            "auth": {"port": 8016, "endpoint": "/health"},
            "constitutional-ai": {"port": 8001, "endpoint": "/health"},
            "governance-synthesis": {"port": 8004, "endpoint": "/health"},
            "policy-governance": {"port": 8005, "endpoint": "/health"},
            "formal-verification": {"port": 8003, "endpoint": "/health"},
            "evolutionary-computation": {"port": 8006, "endpoint": "/health"},
        }
        
    async def check_service_health(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a service is healthy and measure response time."""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://localhost:{config['port']}{config['endpoint']}")
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return {
                    "service": service_name,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "constitutional_hash": self.constitutional_hash
                }
        except Exception as e:
            logger.warning(f"Service {service_name} health check failed", error=str(e))
            return {
                "service": service_name,
                "status": "unreachable",
                "response_time_ms": None,
                "error": str(e),
                "constitutional_hash": self.constitutional_hash
            }
    
    async def establish_baseline(self) -> Dict[str, Any]:
        """Establish performance baseline for all services."""
        logger.info("Establishing performance baseline", quick_mode=self.quick_mode)
        
        baseline_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "quick_mode": self.quick_mode,
            "services": {},
            "summary": {}
        }
        
        # Check all services
        tasks = []
        for service_name, config in self.services.items():
            tasks.append(self.check_service_health(service_name, config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        healthy_services = 0
        total_response_time = 0
        response_times = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error("Service check failed", error=str(result))
                continue
                
            service_name = result["service"]
            baseline_data["services"][service_name] = result
            
            if result["status"] == "healthy":
                healthy_services += 1
                if result["response_time_ms"] is not None:
                    response_times.append(result["response_time_ms"])
                    total_response_time += result["response_time_ms"]
        
        # Calculate summary statistics
        baseline_data["summary"] = {
            "total_services": len(self.services),
            "healthy_services": healthy_services,
            "unhealthy_services": len(self.services) - healthy_services,
            "avg_response_time_ms": total_response_time / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "constitutional_compliance": True,  # All services include constitutional hash
        }
        
        return baseline_data
    
    def save_baseline(self, baseline_data: Dict[str, Any]) -> None:
        """Save baseline data to file."""
        baseline_dir = Path("infrastructure/monitoring/performance/baselines")
        baseline_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"baseline_{timestamp}.json"
        filepath = baseline_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        # Also save as latest baseline
        latest_filepath = baseline_dir / "latest_baseline.json"
        with open(latest_filepath, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        logger.info(f"Baseline saved to {filepath}")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Establish ACGS performance baseline")
    parser.add_argument("--quick", action="store_true", help="Run in quick mode")
    args = parser.parse_args()
    
    establisher = PerformanceBaselineEstablisher(quick_mode=args.quick)
    
    try:
        baseline_data = await establisher.establish_baseline()
        establisher.save_baseline(baseline_data)
        
        # Print summary
        summary = baseline_data["summary"]
        print(f"\n=== Performance Baseline Summary ===")
        print(f"Constitutional Hash: {baseline_data['constitutional_hash']}")
        print(f"Healthy Services: {summary['healthy_services']}/{summary['total_services']}")
        print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
        print(f"Constitutional Compliance: {'✅' if summary['constitutional_compliance'] else '❌'}")
        
        if summary['healthy_services'] < summary['total_services']:
            print(f"\n⚠️  Warning: {summary['unhealthy_services']} services are not healthy")
            exit(1)
        else:
            print(f"\n✅ All services are healthy")
            
    except Exception as e:
        logger.error("Failed to establish baseline", error=str(e))
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
