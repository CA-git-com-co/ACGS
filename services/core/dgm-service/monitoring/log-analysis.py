#!/usr/bin/env python3
"""
DGM Service Log Analysis Tool

Provides real-time log analysis, pattern detection,
and automated alerting for DGM service operations.
"""

import json
import re
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import asyncio
import aiofiles
import requests


class LogAnalyzer:
    """
    Real-time log analyzer for DGM Service.
    
    Monitors log files, detects patterns, and generates alerts
    for anomalies, errors, and performance issues.
    """
    
    def __init__(self, log_dir: str = "/var/log/dgm-service"):
        self.log_dir = Path(log_dir)
        self.patterns = self._load_patterns()
        self.metrics = defaultdict(int)
        self.recent_events = deque(maxlen=1000)
        self.alert_thresholds = self._load_alert_thresholds()
        self.running = False
    
    def _load_patterns(self) -> Dict[str, re.Pattern]:
        """Load log analysis patterns."""
        return {
            'error': re.compile(r'"level":\s*"ERROR"'),
            'warning': re.compile(r'"level":\s*"WARNING"'),
            'constitutional_violation': re.compile(r'"event_type":\s*"constitutional_compliance".*"compliant":\s*false'),
            'performance_degradation': re.compile(r'"threshold_exceeded":\s*true'),
            'auth_failure': re.compile(r'"event_type":\s*"authentication".*"success":\s*false'),
            'high_response_time': re.compile(r'"duration_ms":\s*([0-9]+)'),
            'improvement_failure': re.compile(r'"improvement_event_type":\s*"failed"'),
            'database_error': re.compile(r'"event_type":\s*"database_operation".*"error":\s*"[^"]+"'),
            'model_request_failure': re.compile(r'"provider":\s*"[^"]+".*"status":\s*"failed"'),
            'cache_miss': re.compile(r'"cache_hit_rate":\s*([0-9.]+)')
        }
    
    def _load_alert_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Load alerting thresholds."""
        return {
            'error_rate': {
                'threshold': 10,  # errors per minute
                'window': 60,     # seconds
                'severity': 'critical'
            },
            'constitutional_violations': {
                'threshold': 1,   # any violation is critical
                'window': 300,    # 5 minutes
                'severity': 'critical'
            },
            'auth_failures': {
                'threshold': 5,   # failures per minute
                'window': 60,
                'severity': 'warning'
            },
            'high_response_time': {
                'threshold': 2000,  # milliseconds
                'count': 10,        # consecutive occurrences
                'severity': 'warning'
            },
            'improvement_failures': {
                'threshold': 3,   # failures per hour
                'window': 3600,
                'severity': 'warning'
            },
            'low_cache_hit_rate': {
                'threshold': 0.7,  # 70%
                'severity': 'warning'
            }
        }
    
    async def analyze_log_file(self, file_path: Path) -> None:
        """Analyze a single log file."""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                async for line in f:
                    await self.analyze_log_line(line.strip(), file_path.name)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    async def analyze_log_line(self, line: str, source: str) -> None:
        """Analyze a single log line."""
        if not line:
            return
        
        try:
            # Try to parse as JSON
            log_data = json.loads(line)
            await self.process_structured_log(log_data, source)
        except json.JSONDecodeError:
            # Handle non-JSON logs
            await self.process_unstructured_log(line, source)
    
    async def process_structured_log(self, log_data: Dict[str, Any], source: str) -> None:
        """Process structured JSON log entry."""
        timestamp = datetime.fromisoformat(log_data.get('timestamp', datetime.now().isoformat()))
        level = log_data.get('level', 'INFO')
        event_type = log_data.get('event_type', 'general')
        
        # Update metrics
        self.metrics[f'{source}_total'] += 1
        self.metrics[f'{source}_{level.lower()}'] += 1
        self.metrics[f'event_{event_type}'] += 1
        
        # Store recent event
        event = {
            'timestamp': timestamp,
            'source': source,
            'level': level,
            'event_type': event_type,
            'data': log_data
        }
        self.recent_events.append(event)
        
        # Check for specific patterns
        await self.check_patterns(log_data, event)
    
    async def process_unstructured_log(self, line: str, source: str) -> None:
        """Process unstructured log line."""
        # Basic pattern matching for unstructured logs
        if 'ERROR' in line:
            self.metrics[f'{source}_error'] += 1
        elif 'WARNING' in line:
            self.metrics[f'{source}_warning'] += 1
        
        self.metrics[f'{source}_total'] += 1
    
    async def check_patterns(self, log_data: Dict[str, Any], event: Dict[str, Any]) -> None:
        """Check log data against known patterns."""
        # Constitutional violations
        if (log_data.get('event_type') == 'constitutional_compliance' and 
            not log_data.get('constitutional', {}).get('compliant', True)):
            await self.trigger_alert('constitutional_violation', event, 'critical')
        
        # Performance issues
        if log_data.get('threshold_exceeded'):
            await self.trigger_alert('performance_degradation', event, 'warning')
        
        # Authentication failures
        if (log_data.get('event_type') == 'authentication' and 
            not log_data.get('success', True)):
            await self.trigger_alert('auth_failure', event, 'warning')
        
        # High response times
        duration = log_data.get('duration_ms', 0)
        if duration > self.alert_thresholds['high_response_time']['threshold']:
            await self.trigger_alert('high_response_time', event, 'warning')
        
        # Improvement failures
        if (log_data.get('improvement_event_type') == 'failed'):
            await self.trigger_alert('improvement_failure', event, 'warning')
        
        # Database errors
        if (log_data.get('event_type') == 'database_operation' and 
            log_data.get('error')):
            await self.trigger_alert('database_error', event, 'error')
        
        # Low cache hit rate
        cache_hit_rate = log_data.get('cache_hit_rate')
        if (cache_hit_rate is not None and 
            cache_hit_rate < self.alert_thresholds['low_cache_hit_rate']['threshold']):
            await self.trigger_alert('low_cache_hit_rate', event, 'warning')
    
    async def trigger_alert(self, alert_type: str, event: Dict[str, Any], severity: str) -> None:
        """Trigger an alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity,
            'source': event['source'],
            'event': event,
            'message': f"DGM Service Alert: {alert_type} detected"
        }
        
        print(f"🚨 ALERT [{severity.upper()}]: {alert_type}")
        print(f"   Source: {event['source']}")
        print(f"   Time: {event['timestamp']}")
        print(f"   Details: {json.dumps(event['data'], indent=2)}")
        print("-" * 50)
        
        # Send to alertmanager if configured
        await self.send_to_alertmanager(alert)
    
    async def send_to_alertmanager(self, alert: Dict[str, Any]) -> None:
        """Send alert to Alertmanager."""
        try:
            alertmanager_url = "http://dgm-alertmanager:9093/api/v1/alerts"
            
            alert_payload = [{
                "labels": {
                    "alertname": f"DGM_{alert['alert_type']}",
                    "service": "dgm-service",
                    "severity": alert['severity'],
                    "source": alert['source']
                },
                "annotations": {
                    "summary": alert['message'],
                    "description": f"Alert triggered by log analysis: {alert['alert_type']}",
                    "timestamp": alert['timestamp']
                },
                "startsAt": alert['timestamp']
            }]
            
            response = requests.post(alertmanager_url, json=alert_payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Alert sent to Alertmanager: {alert['alert_type']}")
            else:
                print(f"❌ Failed to send alert to Alertmanager: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending alert to Alertmanager: {e}")
    
    async def monitor_logs(self, interval: int = 5) -> None:
        """Monitor log files continuously."""
        self.running = True
        print(f"🔍 Starting DGM log monitoring (interval: {interval}s)")
        print(f"📁 Log directory: {self.log_dir}")
        
        while self.running:
            try:
                # Find all log files
                log_files = list(self.log_dir.glob("*.log"))
                
                for log_file in log_files:
                    if log_file.exists():
                        await self.analyze_log_file(log_file)
                
                # Print periodic summary
                await self.print_summary()
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping log monitoring...")
                self.running = False
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def print_summary(self) -> None:
        """Print monitoring summary."""
        now = datetime.now()
        print(f"\n📊 DGM Log Analysis Summary - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Recent events summary
        recent_count = len([e for e in self.recent_events 
                           if (now - e['timestamp']).seconds < 300])
        print(f"Recent events (5min): {recent_count}")
        
        # Error rates
        error_count = sum(v for k, v in self.metrics.items() if 'error' in k)
        warning_count = sum(v for k, v in self.metrics.items() if 'warning' in k)
        print(f"Errors: {error_count}, Warnings: {warning_count}")
        
        # Top event types
        event_metrics = {k: v for k, v in self.metrics.items() if k.startswith('event_')}
        if event_metrics:
            top_events = sorted(event_metrics.items(), key=lambda x: x[1], reverse=True)[:5]
            print("Top event types:")
            for event_type, count in top_events:
                print(f"  {event_type}: {count}")
        
        print("=" * 60)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="DGM Service Log Analysis Tool")
    parser.add_argument("--log-dir", default="/var/log/dgm-service",
                       help="Log directory path")
    parser.add_argument("--interval", type=int, default=5,
                       help="Monitoring interval in seconds")
    parser.add_argument("--analyze-file", 
                       help="Analyze a specific log file")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_dir)
    
    if args.analyze_file:
        # Analyze single file
        file_path = Path(args.analyze_file)
        if file_path.exists():
            print(f"🔍 Analyzing log file: {file_path}")
            await analyzer.analyze_log_file(file_path)
            await analyzer.print_summary()
        else:
            print(f"❌ Log file not found: {file_path}")
            sys.exit(1)
    else:
        # Continuous monitoring
        await analyzer.monitor_logs(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
