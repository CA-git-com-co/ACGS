#!/bin/bash
# ACGS-1 Health Metrics Exporter Startup Script
# Prometheus metrics exporter for health monitoring data

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EXPORTER_SCRIPT="infrastructure/monitoring/health_metrics_exporter.py"
LOG_DIR="logs/health_metrics"
PID_FILE="pids/health_metrics_exporter.pid"
PORT=9115

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

# Function to check if exporter is already running
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

# Function to stop metrics exporter
stop_exporter() {
    print_status "Stopping ACGS-1 Health Metrics Exporter..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid"
                print_warning "Force killed metrics exporter process"
            fi
            
            rm -f "$PID_FILE"
            print_success "Health metrics exporter stopped"
        else
            print_warning "Health metrics exporter was not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found, metrics exporter may not be running"
    fi
}

# Function to start metrics exporter
start_exporter() {
    print_status "Starting ACGS-1 Health Metrics Exporter..."
    
    # Check if already running
    if check_running; then
        print_warning "Health metrics exporter is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Create necessary directories
    mkdir -p "$(dirname "$PID_FILE")"
    mkdir -p "$LOG_DIR"
    
    # Validate exporter script
    if [ ! -f "$EXPORTER_SCRIPT" ]; then
        print_error "Metrics exporter script not found: $EXPORTER_SCRIPT"
        return 1
    fi
    
    # Check Python dependencies
    print_status "Checking Python dependencies..."
    python3 -c "
import prometheus_client
import asyncio
import json
print('✅ All required dependencies available')
" 2>/dev/null || {
        print_error "Missing required Python dependencies. Please install:"
        print_error "pip install prometheus-client"
        return 1
    }
    
    # Check if port is available
    if netstat -tuln | grep -q ":$PORT "; then
        print_error "Port $PORT is already in use"
        return 1
    fi
    
    # Start metrics exporter in background
    print_status "Launching health metrics exporter on port $PORT..."
    
    nohup python3 "$EXPORTER_SCRIPT" > "$LOG_DIR/health_metrics_exporter.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "Health metrics exporter started successfully (PID: $pid)"
        print_status "Metrics endpoint: http://localhost:$PORT/metrics"
        print_status "Log file: $LOG_DIR/health_metrics_exporter.log"
        
        # Test metrics endpoint
        sleep 2
        if curl -s "http://localhost:$PORT/metrics" > /dev/null; then
            print_success "Metrics endpoint is responding"
        else
            print_warning "Metrics endpoint not yet responding (may need more time)"
        fi
        
        return 0
    else
        print_error "Health metrics exporter failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "ACGS-1 Health Metrics Exporter Status"
    echo "======================================"
    
    if check_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Health metrics exporter is running (PID: $pid)"
        print_status "Metrics endpoint: http://localhost:$PORT/metrics"
        
        # Test endpoint
        if curl -s "http://localhost:$PORT/metrics" > /dev/null; then
            print_success "Metrics endpoint is responding"
            
            # Show some sample metrics
            echo ""
            print_status "Sample metrics:"
            curl -s "http://localhost:$PORT/metrics" | grep "acgs_" | head -5
        else
            print_warning "Metrics endpoint is not responding"
        fi
        
        # Show recent log entries
        if [ -f "$LOG_DIR/health_metrics_exporter.log" ]; then
            echo ""
            print_status "Recent log entries:"
            tail -n 5 "$LOG_DIR/health_metrics_exporter.log"
        fi
    else
        print_warning "Health metrics exporter is not running"
    fi
}

# Function to restart exporter
restart_exporter() {
    print_status "Restarting ACGS-1 Health Metrics Exporter..."
    stop_exporter
    sleep 2
    start_exporter
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/health_metrics_exporter.log" ]; then
        print_status "Showing health metrics exporter logs (press Ctrl+C to exit):"
        tail -f "$LOG_DIR/health_metrics_exporter.log"
    else
        print_warning "Log file not found: $LOG_DIR/health_metrics_exporter.log"
    fi
}

# Function to test metrics
test_metrics() {
    print_status "Testing health metrics endpoint..."
    
    if ! check_running; then
        print_error "Health metrics exporter is not running"
        return 1
    fi
    
    local endpoint="http://localhost:$PORT/metrics"
    
    if curl -s "$endpoint" > /dev/null; then
        print_success "Metrics endpoint is accessible"
        
        echo ""
        print_status "Available ACGS metrics:"
        curl -s "$endpoint" | grep "^# HELP acgs_" | head -10
        
        echo ""
        print_status "Current metric values:"
        curl -s "$endpoint" | grep "^acgs_" | head -10
        
    else
        print_error "Metrics endpoint is not accessible"
        return 1
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        start_exporter
        ;;
    stop)
        stop_exporter
        ;;
    restart)
        restart_exporter
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        test_metrics
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the health metrics exporter"
        echo "  stop      - Stop the health metrics exporter"
        echo "  restart   - Restart the health metrics exporter"
        echo "  status    - Show current status and endpoint info"
        echo "  logs      - Show live logs (tail -f)"
        echo "  test      - Test metrics endpoint and show sample data"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start metrics exporter"
        echo "  $0 status         # Check if running"
        echo "  $0 test           # Test metrics endpoint"
        echo "  $0 logs           # View live logs"
        exit 1
        ;;
esac
