#!/bin/bash
# ACGS-1 Health Monitor Startup Script
# Enterprise-grade health monitoring for constitutional governance system

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HEALTH_MONITOR_DIR="infrastructure/monitoring"
CONFIG_FILE="config/health_monitor_config.json"
LOG_DIR="logs/health_monitor"
PID_FILE="pids/health_monitor.pid"

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

# Function to check if health monitor is already running
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

# Function to stop health monitor
stop_health_monitor() {
    print_status "Stopping ACGS-1 Health Monitor..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid"
                print_warning "Force killed health monitor process"
            fi
            
            rm -f "$PID_FILE"
            print_success "Health monitor stopped"
        else
            print_warning "Health monitor was not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found, health monitor may not be running"
    fi
}

# Function to start health monitor
start_health_monitor() {
    print_status "Starting ACGS-1 Health Monitor..."
    
    # Check if already running
    if check_running; then
        print_warning "Health monitor is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Create necessary directories
    mkdir -p "$(dirname "$PID_FILE")"
    mkdir -p "$LOG_DIR"
    mkdir -p "logs/health_reports"
    
    # Validate configuration file
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Validate health monitor script
    if [ ! -f "$HEALTH_MONITOR_DIR/health_check_service.py" ]; then
        print_error "Health monitor script not found: $HEALTH_MONITOR_DIR/health_check_service.py"
        return 1
    fi
    
    # Check Python dependencies
    print_status "Checking Python dependencies..."
    python3 -c "
import asyncio
import aiohttp
import redis
import psycopg2
print('✅ All required dependencies available')
" 2>/dev/null || {
        print_error "Missing required Python dependencies. Please install:"
        print_error "pip install asyncio aiohttp redis psycopg2-binary"
        return 1
    }
    
    # Start health monitor in background
    print_status "Launching health monitor service..."
    
    cd "$HEALTH_MONITOR_DIR"
    nohup python3 health_check_service.py > "../../$LOG_DIR/health_monitor.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "../../$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "Health monitor started successfully (PID: $pid)"
        print_status "Log file: $LOG_DIR/health_monitor.log"
        print_status "Health reports: logs/health_reports/"
        return 0
    else
        print_error "Health monitor failed to start"
        rm -f "../../$PID_FILE"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "ACGS-1 Health Monitor Status"
    echo "================================"
    
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Health monitor is running (PID: $pid)"
        
        # Show recent log entries
        if [ -f "$LOG_DIR/health_monitor.log" ]; then
            echo ""
            print_status "Recent log entries:"
            tail -n 10 "$LOG_DIR/health_monitor.log"
        fi
        
        # Show latest health report if available
        local latest_report=$(ls -t logs/health_reports/health_report_*.json 2>/dev/null | head -n 1)
        if [ -n "$latest_report" ]; then
            echo ""
            print_status "Latest health report: $latest_report"
            echo "Generated: $(stat -c %y "$latest_report")"
        fi
    else
        print_warning "Health monitor is not running"
    fi
}

# Function to restart health monitor
restart_health_monitor() {
    print_status "Restarting ACGS-1 Health Monitor..."
    stop_health_monitor
    sleep 2
    start_health_monitor
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/health_monitor.log" ]; then
        print_status "Showing health monitor logs (press Ctrl+C to exit):"
        tail -f "$LOG_DIR/health_monitor.log"
    else
        print_warning "Log file not found: $LOG_DIR/health_monitor.log"
    fi
}

# Function to validate configuration
validate_config() {
    print_status "Validating health monitor configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Validate JSON syntax
    if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        print_success "Configuration file syntax is valid"
    else
        print_error "Configuration file has invalid JSON syntax"
        return 1
    fi
    
    # Show configuration summary
    python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    
print('Configuration Summary:')
print(f'  Check interval: {config.get(\"check_interval\", \"N/A\")} seconds')
print(f'  Alert cooldown: {config.get(\"alert_cooldown\", \"N/A\")} seconds')
print(f'  Timeout: {config.get(\"timeout\", \"N/A\")} seconds')
print(f'  Services monitored: {len(config.get(\"services\", {}))}')
print(f'  Infrastructure components: {len(config.get(\"infrastructure\", {}))}')
print(f'  Blockchain monitoring: {\"enabled\" if config.get(\"blockchain\") else \"disabled\"}')
print(f'  Reporting: {\"enabled\" if config.get(\"reporting\", {}).get(\"enabled\") else \"disabled\"}')
"
}

# Main script logic
case "${1:-start}" in
    start)
        start_health_monitor
        ;;
    stop)
        stop_health_monitor
        ;;
    restart)
        restart_health_monitor
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
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|validate}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the health monitor service"
        echo "  stop      - Stop the health monitor service"
        echo "  restart   - Restart the health monitor service"
        echo "  status    - Show current status and recent activity"
        echo "  logs      - Show live logs (tail -f)"
        echo "  validate  - Validate configuration file"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start monitoring"
        echo "  $0 status         # Check if running"
        echo "  $0 logs           # View live logs"
        echo "  $0 validate       # Check configuration"
        exit 1
        ;;
esac
