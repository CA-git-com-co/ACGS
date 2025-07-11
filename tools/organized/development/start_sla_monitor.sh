#!/bin/bash
# ACGS-1 SLA Monitor Startup Script
# Enterprise-grade SLA monitoring for constitutional governance system

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SLA_MONITOR_SCRIPT="infrastructure/monitoring/sla_monitor.py"
CONFIG_FILE="config/sla_monitor_config.json"
LOG_DIR="logs/sla_monitor"
PID_FILE="pids/sla_monitor.pid"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if SLA monitor is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to stop SLA monitor
stop_sla_monitor() {
    print_status "Stopping ACGS-1 SLA Monitor..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid"
                print_warning "Force killed SLA monitor process"
            fi
            
            rm -f "$PID_FILE"
            print_success "SLA monitor stopped"
        else
            print_warning "SLA monitor was not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found, SLA monitor may not be running"
    fi
}

# Function to start SLA monitor
start_sla_monitor() {
    print_status "Starting ACGS-1 SLA Monitor..."
    
    # Check if already running
    if check_running; then
        print_warning "SLA monitor is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Create necessary directories
    mkdir -p "$(dirname "$PID_FILE")"
    mkdir -p "$LOG_DIR"
    mkdir -p "logs/sla_reports"
    
    # Validate configuration file
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Validate SLA monitor script
    if [ ! -f "$SLA_MONITOR_SCRIPT" ]; then
        print_error "SLA monitor script not found: $SLA_MONITOR_SCRIPT"
        return 1
    fi
    
    # Check Python dependencies
    print_status "Checking Python dependencies..."
    python3 -c "
import asyncio
import aiohttp
import statistics
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
print('✅ All required dependencies available')
" 2>/dev/null || {
        print_error "Missing required Python dependencies. Please install:"
        print_error "pip install asyncio aiohttp"
        return 1
    }
    
    # Validate configuration
    print_status "Validating SLA monitor configuration..."
    python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    
# Validate required sections
required_sections = ['sla_targets', 'warning_thresholds', 'monitoring_endpoints']
for section in required_sections:
    if section not in config:
        raise ValueError(f'Missing required section: {section}')

print('✅ Configuration validation passed')
" 2>/dev/null || {
        print_error "Configuration validation failed"
        return 1
    }
    
    # Start SLA monitor in background
    print_status "Launching SLA monitor service..."
    
    nohup python3 "$SLA_MONITOR_SCRIPT" > "$LOG_DIR/sla_monitor.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "SLA monitor started successfully (PID: $pid)"
        print_status "Log file: $LOG_DIR/sla_monitor.log"
        print_status "SLA reports: logs/sla_reports/"
        print_status "Configuration: $CONFIG_FILE"
        return 0
    else
        print_error "SLA monitor failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "ACGS-1 SLA Monitor Status"
    echo "=========================="
    
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_success "SLA monitor is running (PID: $pid)"
        
        # Show recent log entries
        if [ -f "$LOG_DIR/sla_monitor.log" ]; then
            echo ""
            print_status "Recent log entries:"
            tail -n 10 "$LOG_DIR/sla_monitor.log"
        fi
        
        # Show latest SLA report if available
        local latest_report="logs/sla_reports/latest_sla_report.json"
        if [ -f "$latest_report" ]; then
            echo ""
            print_status "Latest SLA Status:"
            python3 -c "
import json
with open('$latest_report') as f:
    report = json.load(f)
    
print(f\"  Overall Status: {report.get('overall_status', 'unknown').upper()}\")
print(f\"  Uptime: {report.get('uptime_percentage', 0):.2f}%\")
print(f\"  Avg Response Time: {report.get('avg_response_time_ms', 0):.1f}ms\")
print(f\"  Concurrent Capacity: {report.get('concurrent_actions_capacity', 0)}\")
print(f\"  SOL Cost: {report.get('sol_transaction_cost', 0):.4f}\")
print(f\"  Compliance: {report.get('compliance_accuracy', 0):.2f}%\")
print(f\"  24h Breaches: {report.get('breach_count_24h', 0)}\")
print(f\"  24h Warnings: {report.get('warning_count_24h', 0)}\")
" 2>/dev/null || echo "  Unable to parse latest report"
        else
            print_warning "No SLA reports found yet"
        fi
    else
        print_warning "SLA monitor is not running"
    fi
}

# Function to restart SLA monitor
restart_sla_monitor() {
    print_status "Restarting ACGS-1 SLA Monitor..."
    stop_sla_monitor
    sleep 2
    start_sla_monitor
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/sla_monitor.log" ]; then
        print_status "Showing SLA monitor logs (press Ctrl+C to exit):"
        tail -f "$LOG_DIR/sla_monitor.log"
    else
        print_warning "Log file not found: $LOG_DIR/sla_monitor.log"
    fi
}

# Function to validate configuration
validate_config() {
    print_status "Validating SLA monitor configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Validate JSON syntax and structure
    python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)

print('✅ Configuration file syntax is valid')
print()
print('SLA Targets:')
targets = config.get('sla_targets', {})
for key, value in targets.items():
    print(f'  {key}: {value}')

print()
print('Warning Thresholds:')
warnings = config.get('warning_thresholds', {})
for key, value in warnings.items():
    print(f'  {key}: {value}')

print()
print('Monitoring Configuration:')
print(f'  Check interval: {config.get(\"check_interval\", \"N/A\")} seconds')
print(f'  Report interval: {config.get(\"report_interval\", \"N/A\")} seconds')
print(f'  Retention: {config.get(\"retention_days\", \"N/A\")} days')
print(f'  Services monitored: {len(config.get(\"monitoring_endpoints\", {}))}')
print(f'  Alerting enabled: {config.get(\"alert_enabled\", False)}')
" 2>/dev/null || {
        print_error "Configuration validation failed"
        return 1
    }
}

# Function to show SLA trends
show_trends() {
    print_status "Showing SLA trends (last 24 hours)..."
    
    if ! check_running; then
        print_error "SLA monitor is not running"
        return 1
    fi
    
    # This would integrate with the actual SLA monitor to get trends
    local latest_report="logs/sla_reports/latest_sla_report.json"
    if [ -f "$latest_report" ]; then
        python3 -c "
import json
import glob
from datetime import datetime, timedelta

# Load recent reports
report_files = sorted(glob.glob('logs/sla_reports/sla_report_*.json'))
if len(report_files) < 2:
    print('Not enough data for trend analysis')
    exit(0)

# Analyze last few reports
recent_files = report_files[-10:]  # Last 10 reports
uptime_values = []
response_times = []

for file in recent_files:
    try:
        with open(file) as f:
            report = json.load(f)
            uptime_values.append(report.get('uptime_percentage', 0))
            response_times.append(report.get('avg_response_time_ms', 0))
    except:
        continue

if uptime_values and response_times:
    print(f'Uptime Trend (last {len(uptime_values)} reports):')
    print(f'  Current: {uptime_values[-1]:.2f}%')
    print(f'  Average: {sum(uptime_values)/len(uptime_values):.2f}%')
    print(f'  Min: {min(uptime_values):.2f}%')
    print(f'  Max: {max(uptime_values):.2f}%')
    print()
    print(f'Response Time Trend (last {len(response_times)} reports):')
    print(f'  Current: {response_times[-1]:.1f}ms')
    print(f'  Average: {sum(response_times)/len(response_times):.1f}ms')
    print(f'  Min: {min(response_times):.1f}ms')
    print(f'  Max: {max(response_times):.1f}ms')
else:
    print('No trend data available')
" 2>/dev/null || print_warning "Unable to analyze trends"
    else
        print_warning "No SLA reports found"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        start_sla_monitor
        ;;
    stop)
        stop_sla_monitor
        ;;
    restart)
        restart_sla_monitor
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    validate)
        validate_config
        ;;
    trends)
        show_trends
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|validate|trends}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the SLA monitor service"
        echo "  stop      - Stop the SLA monitor service"
        echo "  restart   - Restart the SLA monitor service"
        echo "  status    - Show current status and latest SLA metrics"
        echo "  logs      - Show live logs (tail -f)"
        echo "  validate  - Validate configuration file"
        echo "  trends    - Show SLA trends over time"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start SLA monitoring"
        echo "  $0 status         # Check current SLA status"
        echo "  $0 trends         # View SLA trends"
        echo "  $0 validate       # Check configuration"
        exit 1
        ;;
esac
