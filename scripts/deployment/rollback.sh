# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -euo pipefail

# ACGS-1 Lite Rollback Script
# Handles rollback procedures for deployments and configurations

# Configuration
NAMESPACE_GOVERNANCE="governance"
NAMESPACE_WORKLOAD="workload"
NAMESPACE_MONITORING="monitoring"
NAMESPACE_SHARED="shared"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# Create backup before rollback
create_backup() {
    local backup_name="$1"
    local backup_dir="backups/$backup_name"
    
    log_info "Creating backup: $backup_name"
    mkdir -p "$backup_dir"
    
    # Backup current deployments
    kubectl get deployments --all-namespaces -o yaml > "$backup_dir/deployments.yaml"
    kubectl get services --all-namespaces -o yaml > "$backup_dir/services.yaml"
    kubectl get configmaps --all-namespaces -o yaml > "$backup_dir/configmaps.yaml"
    kubectl get secrets --all-namespaces -o yaml > "$backup_dir/secrets.yaml"
    
    # Backup database schema
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- pg_dump -U postgres acgs_lite > "$backup_dir/database-schema.sql" 2>/dev/null || log_warning "Could not backup database schema"
    
    log_success "Backup created: $backup_dir"
}

# Rollback deployment
rollback_deployment() {
    local namespace="$1"
    local deployment="$2"
    local revision="${3:-}"
    
    log_info "Rolling back deployment $namespace/$deployment"
    
    if [[ -n "$revision" ]]; then
        kubectl rollout undo deployment/"$deployment" -n "$namespace" --to-revision="$revision" || {
            log_error "Failed to rollback $namespace/$deployment to revision $revision"
            return 1
        }
    else
        kubectl rollout undo deployment/"$deployment" -n "$namespace" || {
            log_error "Failed to rollback $namespace/$deployment"
            return 1
        }
    fi
    
    # Wait for rollback to complete
    log_info "Waiting for rollback to complete..."
    kubectl rollout status deployment/"$deployment" -n "$namespace" --timeout=300s || {
        log_error "Rollback timeout for $namespace/$deployment"
        return 1
    }
    
    log_success "Successfully rolled back $namespace/$deployment"
}

# Rollback all services
rollback_all_services() {
    local revision="${1:-}"
    local backup_name="rollback-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Starting rollback of all ACGS-1 Lite services"
    
    # Create backup before rollback
    create_backup "$backup_name"
    
    # Rollback core services
    local services=(
        "$NAMESPACE_GOVERNANCE:policy-engine"
        "$NAMESPACE_GOVERNANCE:opa"
        "$NAMESPACE_WORKLOAD:sandbox-controller"
        "$NAMESPACE_MONITORING:prometheus"
        "$NAMESPACE_MONITORING:grafana"
        "$NAMESPACE_MONITORING:alertmanager"
    )
    
    local failed_rollbacks=()
    
    for service in "${services[@]}"; do
        local ns=$(echo "$service" | cut -d: -f1)
        local name=$(echo "$service" | cut -d: -f2)
        
        if ! rollback_deployment "$ns" "$name" "$revision"; then
            failed_rollbacks+=("$ns/$name")
        fi
    done
    
    if [[ ${#failed_rollbacks[@]} -eq 0 ]]; then
        log_success "All services rolled back successfully"
    else
        log_error "Failed to rollback: ${failed_rollbacks[*]}"
        return 1
    fi
}

# Rollback specific service
rollback_service() {
    local service_name="$1"
    local revision="${2:-}"
    local backup_name="rollback-$service_name-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Rolling back service: $service_name"
    
    # Create backup
    create_backup "$backup_name"
    
    case "$service_name" in
        "policy-engine")
            rollback_deployment "$NAMESPACE_GOVERNANCE" "policy-engine" "$revision"
            rollback_deployment "$NAMESPACE_GOVERNANCE" "opa" "$revision"
            ;;
        "sandbox-controller")
            rollback_deployment "$NAMESPACE_WORKLOAD" "sandbox-controller" "$revision"
            ;;
        "monitoring")
            rollback_deployment "$NAMESPACE_MONITORING" "prometheus" "$revision"
            rollback_deployment "$NAMESPACE_MONITORING" "grafana" "$revision"
            rollback_deployment "$NAMESPACE_MONITORING" "alertmanager" "$revision"
            ;;
        *)
            log_error "Unknown service: $service_name"
            return 1
            ;;
    esac
}

# Rollback database
rollback_database() {
    local backup_file="$1"
    local backup_name="db-rollback-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Rolling back database from backup: $backup_file"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Create current backup
    create_backup "$backup_name"
    
    # Stop services that use the database
    log_info "Scaling down services..."
    kubectl scale deployment/policy-engine --replicas=0 -n $NAMESPACE_GOVERNANCE
    kubectl scale deployment/sandbox-controller --replicas=0 -n $NAMESPACE_WORKLOAD
    kubectl scale deployment/audit-trail-archiver --replicas=0 -n $NAMESPACE_SHARED
    
    # Wait for pods to terminate
    sleep 30
    
    # Restore database
    log_info "Restoring database..."
    kubectl exec -i constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite < "$backup_file" || {
        log_error "Database restore failed"
        return 1
    }
    
    # Restart services
    log_info "Restarting services..."
    kubectl scale deployment/policy-engine --replicas=3 -n $NAMESPACE_GOVERNANCE
    kubectl scale deployment/sandbox-controller --replicas=2 -n $NAMESPACE_WORKLOAD
    kubectl scale deployment/audit-trail-archiver --replicas=2 -n $NAMESPACE_SHARED
    
    # Wait for services to be ready
    kubectl wait --for=condition=Available deployment/policy-engine -n $NAMESPACE_GOVERNANCE --timeout=300s
    kubectl wait --for=condition=Available deployment/sandbox-controller -n $NAMESPACE_WORKLOAD --timeout=300s
    
    log_success "Database rollback completed"
}

# Rollback configuration
rollback_configuration() {
    local config_type="$1"
    local backup_name="config-rollback-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Rolling back configuration: $config_type"
    
    # Create backup
    create_backup "$backup_name"
    
    case "$config_type" in
        "policies")
            log_info "Rolling back OPA policies..."
            kubectl rollout restart deployment/opa -n $NAMESPACE_GOVERNANCE
            ;;
        "network")
            log_info "Rolling back network policies..."
            kubectl delete networkpolicy --all -n $NAMESPACE_GOVERNANCE
            kubectl delete networkpolicy --all -n $NAMESPACE_WORKLOAD
            kubectl delete networkpolicy --all -n $NAMESPACE_SHARED
            kubectl apply -f infrastructure/kubernetes/acgs-lite/network-policies.yaml
            ;;
        "rbac")
            log_info "Rolling back RBAC configuration..."
            kubectl apply -f infrastructure/kubernetes/acgs-lite/rbac.yaml
            ;;
        "monitoring")
            log_info "Rolling back monitoring configuration..."
            kubectl delete configmap prometheus-config -n $NAMESPACE_MONITORING
            kubectl delete configmap grafana-config -n $NAMESPACE_MONITORING
            kubectl delete configmap alertmanager-config -n $NAMESPACE_MONITORING
            kubectl apply -f infrastructure/kubernetes/acgs-lite/monitoring.yaml
            kubectl apply -f infrastructure/kubernetes/acgs-lite/grafana.yaml
            kubectl apply -f infrastructure/kubernetes/acgs-lite/alertmanager.yaml
            ;;
        *)
            log_error "Unknown configuration type: $config_type"
            return 1
            ;;
    esac
    
    log_success "Configuration rollback completed: $config_type"
}

# Emergency rollback
emergency_rollback() {
    local backup_name="emergency-rollback-$(date +%Y%m%d-%H%M%S)"
    
    log_info "INITIATING EMERGENCY ROLLBACK"
    
    # Create backup
    create_backup "$backup_name"
    
    # Scale down all services immediately
    log_info "Scaling down all services..."
    kubectl scale deployment --all --replicas=0 -n $NAMESPACE_GOVERNANCE
    kubectl scale deployment --all --replicas=0 -n $NAMESPACE_WORKLOAD
    
    # Wait for pods to terminate
    sleep 30
    
    # Restore from last known good configuration
    log_info "Restoring from last known good configuration..."
    
    # Find the most recent backup
    local latest_backup=$(ls -1t backups/ | head -n 1 2>/dev/null || echo "")
    
    if [[ -n "$latest_backup" ]] && [[ -d "backups/$latest_backup" ]]; then
        log_info "Restoring from backup: $latest_backup"
        
        # Restore configurations
        kubectl apply -f "backups/$latest_backup/deployments.yaml" || log_warning "Could not restore deployments"
        kubectl apply -f "backups/$latest_backup/configmaps.yaml" || log_warning "Could not restore configmaps"
        
        # Wait for services to be ready
        kubectl wait --for=condition=Available deployment/policy-engine -n $NAMESPACE_GOVERNANCE --timeout=300s || log_warning "Policy Engine not ready"
        kubectl wait --for=condition=Available deployment/sandbox-controller -n $NAMESPACE_WORKLOAD --timeout=300s || log_warning "Sandbox Controller not ready"
    else
        log_warning "No backup found, deploying from source..."
        kubectl apply -f infrastructure/kubernetes/acgs-lite/
    fi
    
    log_success "Emergency rollback completed"
}

# List available rollback points
list_rollback_points() {
    log_info "Available rollback points:"
    
    # List deployment revisions
    echo ""
    echo "Deployment Revisions:"
    echo "===================="
    
    local deployments=(
        "$NAMESPACE_GOVERNANCE:policy-engine"
        "$NAMESPACE_GOVERNANCE:opa"
        "$NAMESPACE_WORKLOAD:sandbox-controller"
    )
    
    for deployment in "${deployments[@]}"; do
        local ns=$(echo "$deployment" | cut -d: -f1)
        local name=$(echo "$deployment" | cut -d: -f2)
        
        echo ""
        echo "$ns/$name:"
        kubectl rollout history deployment/"$name" -n "$ns" 2>/dev/null || echo "  No history available"
    done
    
    # List backups
    echo ""
    echo "Available Backups:"
    echo "=================="
    if [[ -d "backups" ]]; then
        ls -la backups/ | grep "^d" | awk '{print $9, $6, $7, $8}' | grep -v "^\.$\|^\.\.$"
    else
        echo "No backups directory found"
    fi
}

# Verify rollback
verify_rollback() {
    log_info "Verifying rollback..."
    
    # Check deployment status
    local failed_deployments=()
    
    local deployments=(
        "$NAMESPACE_GOVERNANCE:policy-engine"
        "$NAMESPACE_GOVERNANCE:opa"
        "$NAMESPACE_WORKLOAD:sandbox-controller"
    )
    
    for deployment in "${deployments[@]}"; do
        local ns=$(echo "$deployment" | cut -d: -f1)
        local name=$(echo "$deployment" | cut -d: -f2)
        
        local ready=$(kubectl get deployment "$name" -n "$ns" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired=$(kubectl get deployment "$name" -n "$ns" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [[ "$ready" != "$desired" ]] || [[ "$ready" -eq 0 ]]; then
            failed_deployments+=("$ns/$name")
        fi
    done
    
    if [[ ${#failed_deployments[@]} -eq 0 ]]; then
        log_success "All deployments are healthy after rollback"
    else
        log_error "Failed deployments after rollback: ${failed_deployments[*]}"
        return 1
    fi
    
    # Test Policy Engine
    log_info "Testing Policy Engine..."
    kubectl port-forward svc/policy-engine 8001:8001 -n $NAMESPACE_GOVERNANCE >/dev/null 2>&1 &
    local port_forward_pid=$!
    sleep 5
    
    if curl -f -s http://localhost:8001/health >/dev/null 2>&1; then
        log_success "Policy Engine health check passed"
    else
        log_error "Policy Engine health check failed"
    fi
    
    kill $port_forward_pid 2>/dev/null || true
    
    log_success "Rollback verification completed"
}

# Main rollback function
main() {
    local action="$1"
    shift
    
    case "$action" in
        "all")
            local revision="${1:-}"
            rollback_all_services "$revision"
            verify_rollback
            ;;
        "service")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 service <service_name> [revision]"
                exit 1
            fi
            local service_name="$1"
            local revision="${2:-}"
            rollback_service "$service_name" "$revision"
            verify_rollback
            ;;
        "database")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 database <backup_file>"
                exit 1
            fi
            rollback_database "$1"
            ;;
        "config")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 config <config_type>"
                exit 1
            fi
            rollback_configuration "$1"
            ;;
        "emergency")
            emergency_rollback
            verify_rollback
            ;;
        "list")
            list_rollback_points
            ;;
        "verify")
            verify_rollback
            ;;
        *)
            echo "ACGS-1 Lite Rollback Script"
            echo "Usage: $0 <action> [arguments]"
            echo ""
            echo "Actions:"
            echo "  all [revision]              - Rollback all services to previous or specific revision"
            echo "  service <name> [revision]   - Rollback specific service (policy-engine, sandbox-controller, monitoring)"
            echo "  database <backup_file>      - Rollback database from backup file"
            echo "  config <type>               - Rollback configuration (policies, network, rbac, monitoring)"
            echo "  emergency                   - Emergency rollback to last known good state"
            echo "  list                        - List available rollback points"
            echo "  verify                      - Verify system health after rollback"
            echo ""
            echo "Examples:"
            echo "  $0 all                      # Rollback all services to previous version"
            echo "  $0 service policy-engine 3 # Rollback policy engine to revision 3"
            echo "  $0 database backup.sql      # Restore database from backup"
            echo "  $0 config network           # Rollback network policies"
            echo "  $0 emergency                # Emergency rollback"
            exit 1
            ;;
    esac
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
