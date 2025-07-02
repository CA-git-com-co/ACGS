#!/bin/bash
# ACGS-1 Automated Health Check Script

PROJECT_ROOT="/home/dislove/ACGS-1"
LOG_FILE="/home/dislove/ACGS-1/logs/automated_health.log"

echo "$(date): Starting automated health check..." >> "$LOG_FILE"

cd "$PROJECT_ROOT"

# Run health check
health_result=$(python3 scripts/emergency_rollback_procedures.py health 2>/dev/null)

if [ $? -eq 0 ]; then
    # Parse health status
    overall_status=$(echo "$health_result" | grep -o '"overall_status": "[^"]*"' | cut -d'"' -f4)
    health_percentage=$(echo "$health_result" | grep -o '"health_percentage": [0-9.]*' | cut -d':' -f2 | tr -d ' ')
    
    echo "$(date): Health check completed - Status: $overall_status, Health: $health_percentage%" >> "$LOG_FILE"
    
    # Alert if health is degraded
    if [ "$overall_status" != "healthy" ]; then
        echo "$(date): ALERT - System health is $overall_status" >> "$LOG_FILE"
        
        # Create incident report for critical status
        if [ "$overall_status" = "critical" ]; then
            python3 scripts/emergency_rollback_procedures.py incident \
                --type "system_health_critical" \
                --description "Automated health check detected critical system status" \
                --severity "critical" >> "$LOG_FILE" 2>&1
        fi
    fi
else
    echo "$(date): ERROR - Health check failed" >> "$LOG_FILE"
fi
