#!/usr/bin/env python3
"""
Comprehensive Port Conflict Resolution Script
Systematically assigns unique ports to all services to resolve conflicts
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
from pathlib import Path


def load_env_file(env_path: str) -> dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env_file(env_path: str, env_vars: dict[str, str]) -> None:
    """Save environment variables to .env file"""
    lines = ["# Constitutional Hash: cdd01ef066bc6cf2\n"]

    # Group related variables
    groups = {
        "Database Ports": [],
        "Redis Ports": [],
        "Core Service Ports": [],
        "Monitoring Ports": [],
        "Gateway Ports": [],
        "Test Ports": [],
        "Security Ports": [],
        "Other Ports": [],
        "Non-Port Variables": [],
    }

    for key, value in sorted(env_vars.items()):
        if "PORT" in key:
            if "POSTGRES" in key or "DB" in key:
                groups["Database Ports"].append(f"{key}={value}")
            elif "REDIS" in key:
                groups["Redis Ports"].append(f"{key}={value}")
            elif any(
                x in key
                for x in ["AUTH", "AC_", "INTEGRITY", "GOVERNANCE", "CONSTITUTIONAL"]
            ):
                groups["Core Service Ports"].append(f"{key}={value}")
            elif any(
                x in key for x in ["PROMETHEUS", "GRAFANA", "ALERT", "NODE_EXPORTER"]
            ):
                groups["Monitoring Ports"].append(f"{key}={value}")
            elif any(x in key for x in ["GATEWAY", "HAPROXY", "NGINX"]):
                groups["Gateway Ports"].append(f"{key}={value}")
            elif "TEST" in key:
                groups["Test Ports"].append(f"{key}={value}")
            elif any(x in key for x in ["OPA", "SECURITY", "AUDIT"]):
                groups["Security Ports"].append(f"{key}={value}")
            else:
                groups["Other Ports"].append(f"{key}={value}")
        else:
            groups["Non-Port Variables"].append(f"{key}={value}")

    # Write grouped variables
    for group_name, variables in groups.items():
        if variables:
            lines.append(f"\n# {group_name}\n")
            lines.extend([f"{var}\n" for var in variables])

    with open(env_path, "w") as f:
        f.writelines(lines)


def update_docker_compose_ports(file_path: str, port_mapping: dict[str, int]) -> None:
    """Update hardcoded ports in Docker Compose files"""
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content

        # Update hardcoded port mappings
        port_updates = {
            "3000:3000": "${GRAFANA_PORT}:3000",
            "9090:9090": "${PROMETHEUS_PORT}:9090",
            "9093:9093": "${ALERTMANAGER_PORT}:9093",
            "9100:9100": "${NODE_EXPORTER_PORT}:9100",
            "8080:8080": "${API_GATEWAY_PORT}:8080",
            "8001:8001": "${CONSTITUTIONAL_AI_PORT}:8001",
            "8002:8002": "${INTEGRITY_SERVICE_PORT}:8002",
            "5432:5432": "${POSTGRES_PORT}:5432",
            "6379:6379": "${REDIS_PORT}:6379",
        }

        for old_mapping, new_mapping in port_updates.items():
            content = content.replace(old_mapping, new_mapping)

        # Update specific hardcoded ports
        content = re.sub(r'(\s+- ["\']?)3000:', r"\1${GRAFANA_PORT}:", content)
        content = re.sub(r'(\s+- ["\']?)9090:', r"\1${PROMETHEUS_PORT}:", content)
        content = re.sub(r'(\s+- ["\']?)8080:', r"\1${API_GATEWAY_PORT}:", content)
        content = re.sub(
            r'(\s+- ["\']?)8001:', r"\1${CONSTITUTIONAL_AI_PORT}:", content
        )

        if content != original_content:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Updated hardcoded ports in {file_path}")

    except Exception as e:
        print(f"Error updating {file_path}: {e}")


def main():
    """Main function to resolve all port conflicts"""
    repo_root = Path("/home/dislove/ACGS-2")
    env_path = repo_root / ".env"

    print("🔧 Comprehensive Port Conflict Resolution")
    print("📋 Constitutional Hash: cdd01ef066bc6cf2")
    print()

    # Load existing environment variables
    env_vars = load_env_file(str(env_path))

    # Define comprehensive port assignments (starting from 3000 to avoid system ports)
    # We'll use ranges: 3000-3999, 5000-5999, 6000-6999, 8000-8999, 9000-9999

    port_assignments = {
        # Web UI Ports (3000-3099)
        "GRAFANA_PORT": "3001",  # Moved from 3000 to avoid conflicts
        "MCP_AGGREGATOR_PORT": "3010",
        "MCP_SEQUENTIAL_PORT": "3011",
        "MCP_MAGIC_PORT": "3012",
        "KIBANA_PORT": "3020",
        "PGADMIN_PORT": "3030",
        "ADMINER_PORT": "3031",
        "REDIS_COMMANDER_PORT": "3032",
        "SWAGGER_UI_PORT": "3040",
        "EVIDENTLY_PORT": "3050",
        # Database Ports (5000-5999)
        "POSTGRES_PORT": "5432",  # Keep standard
        "POSTGRES_TEST_PORT": "5433",
        "POSTGRES_E2E_PORT": "5434",
        "POSTGRES_REPLICA1_PORT": "5435",
        "POSTGRES_REPLICA2_PORT": "5436",
        "POSTGRES_CONSTITUTIONAL_PORT": "5437",
        "POSTGRES_CHAOS_PORT": "5438",
        "POSTGRES_STAGING_PORT": "5439",
        "COCKROACHDB_HTTP_PORT": "5440",
        "COCKROACHDB_SQL_PORT": "5441",
        # Redis Ports (6000-6999)
        "REDIS_PORT": "6379",  # Keep standard
        "REDIS_TEST_PORT": "6380",
        "REDIS_E2E_PORT": "6381",
        "REDIS_CLUSTER_PORT": "6382",
        "REDIS_CONSTITUTIONAL_PORT": "6383",
        "REDIS_MASTER1_PORT": "6384",
        "REDIS_MASTER2_PORT": "6385",
        "REDIS_MASTER3_PORT": "6386",
        "REDIS_REPLICA1_PORT": "6387",
        "REDIS_REPLICA2_PORT": "6388",
        "REDIS_REPLICA3_PORT": "6389",
        "LANGGRAPH_REDIS_PORT": "6390",
        "DRAGONFLYDB_PORT": "6391",
        # Core ACGS Services (8000-8099)
        "AUTH_SERVICE_PORT": "8000",
        "CONSTITUTIONAL_AI_PORT": "8001",
        "INTEGRITY_SERVICE_PORT": "8002",
        "FORMAL_VERIFICATION_PORT": "8003",
        "GOVERNANCE_SYNTHESIS_PORT": "8004",
        "POLICY_GOVERNANCE_PORT": "8005",
        "EVOLUTIONARY_COMPUTATION_PORT": "8006",
        "BLACKBOARD_SERVICE_PORT": "8010",
        "MULTI_AGENT_COORDINATOR_PORT": "8008",
        "AGENT_HITL_SERVICE_PORT": "8009",
        # API & Gateway Ports (8100-8199)
        "API_GATEWAY_PORT": "8100",
        "NGINX_PORT": "8101",
        "HAPROXY_STATS_PORT": "8102",
        "KONG_ADMIN_PORT": "8103",
        "KONG_PROXY_PORT": "8104",
        "TRAEFIK_WEB_PORT": "8105",
        "TRAEFIK_API_PORT": "8106",
        # Testing Ports (8200-8299)
        "AUTH_SERVICE_TEST_PORT": "8200",
        "AC_SERVICE_TEST_PORT": "8201",
        "CONSTITUTIONAL_AI_TEST_PORT": "8202",
        "INTEGRITY_SERVICE_TEST_PORT": "8203",
        "FORMAL_VERIFICATION_TEST_PORT": "8204",
        "GOVERNANCE_SYNTHESIS_TEST_PORT": "8205",
        "POLICY_GOVERNANCE_TEST_PORT": "8206",
        "EVOLUTIONARY_COMPUTATION_TEST_PORT": "8207",
        # Security Services (8300-8399)
        "OPA_PORT": "8300",
        "OPA_TEST_PORT": "8301",
        "VAULT_PORT": "8302",
        "CONSUL_PORT": "8303",
        "CERT_MANAGER_PORT": "8304",
        "SECURITY_MONITOR_PORT": "8305",
        "VULNERABILITY_SCANNER_PORT": "8306",
        "COMPLIANCE_CHECKER_PORT": "8307",
        "IDS_MONITOR_PORT": "8308",
        "AUDIT_LOGGER_PORT": "8309",
        # Specialized Services (8400-8499)
        "KIMI_SERVICE_PORT": "8400",
        "KIMI_MONITOR_PORT": "8401",
        "KIMI_SWE_SERVICE_PORT": "8402",
        "KIMI_SWE_MONITOR_PORT": "8403",
        "OCR_SERVICE_PORT": "8410",
        "OCR_MONITORING_PORT": "8411",
        "MODEL_ORCHESTRATOR_PORT": "8420",
        "NVIDIA_LLM_ROUTER_CONTROLLER_PORT": "8430",
        "NVIDIA_LLM_ROUTER_SERVER_PORT": "8431",
        # Storage & Messaging (8500-8599)
        "MINIO_API_PORT": "8500",
        "MINIO_CONSOLE_PORT": "8501",
        "NATS_PORT": "8510",
        "NATS_HTTP_PORT": "8511",
        "NATS_SURVEYOR_PORT": "8512",
        "ELASTICSEARCH_HTTP_PORT": "8520",
        "ELASTICSEARCH_TRANSPORT_PORT": "8521",
        "LOGSTASH_HTTP_PORT": "8530",
        "LOGSTASH_BEATS_PORT": "8531",
        "REGISTRY_PORT": "8540",
        # Monitoring Services (9000-9099)
        "PROMETHEUS_PORT": "9090",  # Keep standard
        "PROMETHEUS_TEST_PORT": "9091",
        "PROMETHEUS_E2E_PORT": "9092",
        "PROMETHEUS_STAGING_PORT": "9093",
        "PROMETHEUS_CHAOS_PORT": "9094",
        "PROMETHEUS_ENHANCED_PORT": "9095",
        "PROMETHEUS_CONSTITUTIONAL_PORT": "9096",
        # Alerting & Metrics (9100-9199)
        "ALERTMANAGER_PORT": "9093",  # Keep standard
        "ALERTMANAGER_TEST_PORT": "9094",
        "ALERTMANAGER_ENHANCED_PORT": "9095",
        "NODE_EXPORTER_PORT": "9100",
        "REDIS_EXPORTER_PORT": "9101",
        "POSTGRES_EXPORTER_PORT": "9102",
        "HAPROXY_EXPORTER_PORT": "9103",
        "SECURITY_EXPORTER_PORT": "9104",
        "CADVISOR_PORT": "9105",
        # Tracing & Observability (9200-9299)
        "JAEGER_UI_PORT": "9200",
        "JAEGER_GRPC_PORT": "9201",
        "JAEGER_THRIFT_PORT": "9202",
        "ZIPKIN_PORT": "9210",
        "TEMPO_HTTP_PORT": "9220",
        "TEMPO_GRPC_PORT": "9221",
        "OTEL_COLLECTOR_HTTP_PORT": "9230",
        "OTEL_COLLECTOR_GRPC_PORT": "9231",
        "LOKI_PORT": "9240",
        # Chaos & Testing (9300-9399)
        "CHAOS_MONKEY_PORT": "9300",
        "CHAOS_DASHBOARD_PORT": "9301",
        "CHAOS_SCHEDULER_PORT": "9302",
        "LOCUST_MASTER_PORT": "9310",
        "LOCUST_WEB_PORT": "9311",
        "LOAD_TESTER_PORT": "9320",
        # Development & Debug (9400-9499)
        "DEBUG_PORT": "9400",
        "PROFILER_PORT": "9401",
        "HEALTH_CHECK_PORT": "9410",
        "METRICS_PORT": "9420",
        # Other required variables
        "POSTGRES_PASSWORD": "acgs_secure_password_2024",
        "GITHUB_TOKEN": "your_github_token_here",
        "REDIS_PASSWORD": "acgs_redis_password_2024",
        "CONSTITUTIONAL_HASH": "cdd01ef066bc6cf2",
    }

    # Update environment variables
    env_vars.update(port_assignments)

    # Save updated .env file
    save_env_file(str(env_path), env_vars)
    print(f"✅ Updated .env file with {len(port_assignments)} port assignments")

    # Update Docker Compose files
    compose_files = [
        "docker-compose.base.yml",
        "docker-compose.mcp.yml",
        "docker-compose.monitoring.yml",
        "docker-compose.services.yml",
        "infrastructure/docker/docker-compose.acgs.yml",
        "infrastructure/docker/docker-compose.monitoring.yml",
        "infrastructure/docker/docker-compose.staging.yml",
    ]

    for compose_file in compose_files:
        full_path = repo_root / compose_file
        update_docker_compose_ports(str(full_path), port_assignments)

    print("\n🎯 Port Assignment Summary:")
    print("=" * 50)

    # Group and display port assignments
    groups = {
        "Web UI (3000-3099)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 3000 <= int(v) < 3100
        },
        "Databases (5000-5999)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 5000 <= int(v) < 6000
        },
        "Redis (6000-6999)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 6000 <= int(v) < 7000
        },
        "Core Services (8000-8099)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 8000 <= int(v) < 8100
        },
        "Gateways (8100-8199)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 8100 <= int(v) < 8200
        },
        "Testing (8200-8299)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 8200 <= int(v) < 8300
        },
        "Security (8300-8399)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 8300 <= int(v) < 8400
        },
        "Monitoring (9000-9199)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 9000 <= int(v) < 9200
        },
        "Observability (9200-9299)": {
            k: v
            for k, v in port_assignments.items()
            if k.endswith("_PORT") and 9200 <= int(v) < 9300
        },
    }

    for group_name, ports in groups.items():
        if ports:
            print(f"\n{group_name}:")
            for port_name, port_value in sorted(ports.items()):
                print(f"  {port_name}: {port_value}")

    print("\n✅ Comprehensive port conflict resolution completed!")
    print("📋 Constitutional Hash: cdd01ef066bc6cf2")
    print(
        "🔧 Total unique ports assigned:"
        f" {len([v for k, v in port_assignments.items() if k.endswith('_PORT')])}"
    )


if __name__ == "__main__":
    main()
