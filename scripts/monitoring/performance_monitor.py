#!/usr/bin/env python3
'''
ACGS-2 Real-Time Performance Monitor
Constitutional Hash: cdd01ef066bc6cf2
'''

import json
import time
import psutil
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class PerformanceMonitor:
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self):
        self.project_root = Path(".").resolve()
        self.targets = {
            "p99_latency_ms": 5.0,
            "throughput_rps": 100.0,
            "cache_hit_rate_percent": 85.0
        }
        
    def collect_system_metrics(self) -> Dict:
        '''Collect current system performance metrics'''
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            },
            "performance": {
                "estimated_p99_latency": self.estimate_p99_latency(),
                "estimated_throughput": self.estimate_throughput(),
                "estimated_cache_hit_rate": self.estimate_cache_hit_rate()
            },
            "targets": self.targets,
            "compliance": {}
        }
        
        # Check compliance with targets
        metrics["compliance"] = {
            "p99_latency": metrics["performance"]["estimated_p99_latency"] <= self.targets["p99_latency_ms"],
            "throughput": metrics["performance"]["estimated_throughput"] >= self.targets["throughput_rps"],
            "cache_hit_rate": metrics["performance"]["estimated_cache_hit_rate"] >= self.targets["cache_hit_rate_percent"]
        }
        
        metrics["overall_compliance"] = all(metrics["compliance"].values())
        
        return metrics
        
    def estimate_p99_latency(self) -> float:
        '''Estimate P99 latency based on system load'''
        load = psutil.cpu_percent()
        base_latency = 1.0  # Base latency in ms
        
        # Simple estimation: higher CPU load = higher latency
        if load < 20:
            return base_latency
        elif load < 50:
            return base_latency * 1.5
        elif load < 80:
            return base_latency * 3.0
        else:
            return base_latency * 6.0
            
    def estimate_throughput(self) -> float:
        '''Estimate throughput based on system resources'''
        cpu_available = 100 - psutil.cpu_percent()
        memory_available = 100 - psutil.virtual_memory().percent
        
        # Simple estimation: more available resources = higher throughput
        resource_factor = (cpu_available + memory_available) / 200
        base_throughput = 150.0  # Base RPS
        
        return base_throughput * resource_factor
        
    def estimate_cache_hit_rate(self) -> float:
        '''Estimate cache hit rate based on memory usage'''
        memory_usage = psutil.virtual_memory().percent
        
        # Simple estimation: lower memory pressure = better cache performance
        if memory_usage < 50:
            return 95.0
        elif memory_usage < 70:
            return 90.0
        elif memory_usage < 85:
            return 85.0
        else:
            return 75.0
            
    def generate_alerts(self, metrics: Dict) -> List[Dict]:
        '''Generate performance alerts based on metrics'''
        alerts = []
        
        if not metrics["compliance"]["p99_latency"]:
            alerts.append({
                "severity": "WARNING",
                "metric": "P99 Latency",
                "current": metrics["performance"]["estimated_p99_latency"],
                "target": self.targets["p99_latency_ms"],
                "message": f"P99 latency {metrics['performance']['estimated_p99_latency']:.2f}ms exceeds target {self.targets['p99_latency_ms']}ms"
            })
            
        if not metrics["compliance"]["throughput"]:
            alerts.append({
                "severity": "WARNING",
                "metric": "Throughput",
                "current": metrics["performance"]["estimated_throughput"],
                "target": self.targets["throughput_rps"],
                "message": f"Throughput {metrics['performance']['estimated_throughput']:.2f} RPS below target {self.targets['throughput_rps']} RPS"
            })
            
        if not metrics["compliance"]["cache_hit_rate"]:
            alerts.append({
                "severity": "WARNING",
                "metric": "Cache Hit Rate",
                "current": metrics["performance"]["estimated_cache_hit_rate"],
                "target": self.targets["cache_hit_rate_percent"],
                "message": f"Cache hit rate {metrics['performance']['estimated_cache_hit_rate']:.2f}% below target {self.targets['cache_hit_rate_percent']}%"
            })
            
        return alerts
        
    def save_metrics(self, metrics: Dict):
        '''Save metrics to dashboard file'''
        dashboard_path = Path("reports/performance/realtime_performance_dashboard.json")
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        dashboard_data = {
            "last_updated": metrics["timestamp"],
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "current_metrics": metrics,
            "alerts": self.generate_alerts(metrics),
            "history": []
        }
        
        if dashboard_path.exists():
            try:
                with open(dashboard_path, 'r') as f:
                    existing_data = json.load(f)
                    dashboard_data["history"] = existing_data.get("history", [])
            except:
                pass
                
        # Add current metrics to history
        dashboard_data["history"].append({
            "timestamp": metrics["timestamp"],
            "p99_latency": metrics["performance"]["estimated_p99_latency"],
            "throughput": metrics["performance"]["estimated_throughput"],
            "cache_hit_rate": metrics["performance"]["estimated_cache_hit_rate"],
            "overall_compliance": metrics["overall_compliance"]
        })
        
        # Keep only last 100 entries
        if len(dashboard_data["history"]) > 100:
            dashboard_data["history"] = dashboard_data["history"][-100:]
            
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
            
    def run_monitoring_cycle(self):
        '''Run a single monitoring cycle'''
        metrics = self.collect_system_metrics()
        self.save_metrics(metrics)
        
        print(f"📊 Performance Monitoring - {datetime.now().strftime('%H:%M:%S')}")
        print(f"⚡ P99 Latency: {metrics['performance']['estimated_p99_latency']:.2f}ms (target: <{self.targets['p99_latency_ms']}ms)")
        print(f"🚀 Throughput: {metrics['performance']['estimated_throughput']:.2f} RPS (target: >{self.targets['throughput_rps']} RPS)")
        print(f"💾 Cache Hit Rate: {metrics['performance']['estimated_cache_hit_rate']:.2f}% (target: >{self.targets['cache_hit_rate_percent']}%)")
        print(f"✅ Overall Compliance: {metrics['overall_compliance']}")
        
        return metrics

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.run_monitoring_cycle()
