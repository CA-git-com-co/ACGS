#!/usr/bin/env python3
'''
ACGS-2 Real-Time Constitutional Compliance Monitor
Constitutional Hash: cdd01ef066bc6cf2
'''

import json
import time
from pathlib import Path
from datetime import datetime

class ConstitutionalComplianceMonitor:
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self):
        self.project_root = Path(".").resolve()
        self.monitoring_data = {
            "last_check": None,
            "compliance_rate": 0.0,
            "violations": [],
            "alerts": []
        }
        
    def check_compliance_rate(self):
        '''Check current compliance rate'''
        total_files = 0
        compliant_files = 0
        
        for file_path in self.project_root.rglob("*.py"):
            if self.should_monitor_file(file_path):
                total_files += 1
                if self.check_file_compliance(file_path):
                    compliant_files += 1
                    
        rate = (compliant_files / max(total_files, 1)) * 100
        return rate, total_files, compliant_files
        
    def should_monitor_file(self, file_path):
        '''Check if file should be monitored'''
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'target'}
        return not any(skip in str(file_path) for skip in skip_dirs)
        
    def check_file_compliance(self, file_path):
        '''Check if file is constitutionally compliant'''
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self.CONSTITUTIONAL_HASH in f.read()
        except:
            return False
            
    def generate_alert(self, message, severity="INFO"):
        '''Generate compliance alert'''
        alert = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "severity": severity,
            "constitutional_hash": self.CONSTITUTIONAL_HASH
        }
        
        self.monitoring_data["alerts"].append(alert)
        
        # Keep only last 100 alerts
        if len(self.monitoring_data["alerts"]) > 100:
            self.monitoring_data["alerts"] = self.monitoring_data["alerts"][-100:]
            
    def run_monitoring_cycle(self):
        '''Run a single monitoring cycle'''
        rate, total, compliant = self.check_compliance_rate()
        
        self.monitoring_data.update({
            "last_check": datetime.now().isoformat(),
            "compliance_rate": round(rate, 2),
            "total_files": total,
            "compliant_files": compliant
        })
        
        # Generate alerts based on compliance rate
        if rate < 50.0:
            self.generate_alert(f"Constitutional compliance below target: {rate:.2f}%", "WARNING")
        elif rate < 40.0:
            self.generate_alert(f"Critical constitutional compliance: {rate:.2f}%", "CRITICAL")
            
        # Save monitoring data
        report_path = Path("reports/compliance/realtime_compliance_monitoring.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.monitoring_data, f, indent=2)
            
        return rate
        
if __name__ == "__main__":
    monitor = ConstitutionalComplianceMonitor()
    rate = monitor.run_monitoring_cycle()
    print(f"Constitutional compliance rate: {rate:.2f}%")
