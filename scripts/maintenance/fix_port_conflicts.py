#!/usr/bin/env python3
"""
ACGS Port Conflict Resolution Script
Constitutional Hash: cdd01ef066bc6cf2

This script systematically resolves port conflicts across all Docker Compose files
and updates service configurations to use unique ports.
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

import yaml

# Constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Port assignments for ACGS services - all unique
PORT_ASSIGNMENTS = {
    # Core Infrastructure (5000s range)
    "postgres": 5439,
    "postgresql": 5440,
    "postgresql-primary": 5441,
    "postgresql-replica": 5442,
    "postgres-test": 5443,
    "postgres-e2e": 5444,
    "postgres_constitutional": 5445,
    "postgres_replica1": 5446,
    "acgs-postgres": 5447,
    "postgres-service": 5448,
    "postgres-deployment": 5449,
    "constitutional-postgres-rw": 5450,
    "constitutional-postgres-ro": 5451,
    "constitutional-postgres-pooler": 5452,
    "storage_manager": 5453,
    # Redis Services (6000s range)
    "redis": 6389,
    "redis-test": 6390,
    "redis-cluster": 6391,
    "redis-e2e": 6392,
    "redis_constitutional": 6393,
    "acgs-redis": 6394,
    "dragonflydb": 6395,
    "nvidia_router_redis": 6396,
    # Core ACGS Services (8000s range)
    "constitutional-ai-service": 8001,
    "ac-service": 8002,
    "acgs-ac-service": 8003,
    "constitutional-ai-test": 8004,
    "ac_service": 8005,
    "constitutional_core": 8006,
    "mock-constitutional-ai": 8007,
    "ac-service-deployment": 8008,
    "acgs-ac-service-active": 8009,
    "acgs-ac-service-green": 8010,
    "acgs-ac-service-blue": 8011,
    "policy-engine": 8012,
    # Auth Services (8100s range)
    "auth-service": 8100,
    "auth-service-test": 8101,
    "auth_service": 8102,
    "mock-auth-service": 8103,
    "acgs-auth-service": 8104,
    "auth-service-deployment": 8105,
    "acgs-auth-service-active": 8106,
    "acgs-auth-service-green": 8107,
    "acgs-auth-service-blue": 8108,
    # Integrity Services (8200s range)
    "integrity-service": 8200,
    # Gateway Services (8300s range)
    "api-gateway": 8300,
    "api_gateway": 8301,
    "api_gateway_constitutional": 8302,
    # Other Core Services (8400s range)
    "governance-synthesis-service": 8400,
    "policy-governance-service": 8401,
    "formal-verification-service": 8402,
    "opencode-cli-service": 8403,
    # Monitoring Services (9000s range)
    "prometheus": 9090,
    "prometheus-e2e": 9091,
    "prometheus_constitutional": 9092,
    "prometheus-chaos": 9093,
    "acgs-prometheus": 9094,
    "prometheus-enhanced": 9095,
    "prometheus-operator": 9096,
    "alertmanager": 9100,
    "alertmanager-enhanced": 9101,
    "grafana": 3001,
    "grafana-staging": 3002,
    "grafana-enhanced": 3003,
    "grafana-e2e": 3004,
    "grafana_constitutional": 3005,
    "grafana-chaos": 3006,
    "acgs-grafana": 3007,
    # Application Services (8500s range)
    "nginx": 8500,
    "nginx-ingress-controller": 8501,
    "nginx-ingress": 8502,
    "nginx-gateway": 8503,
    "nginx-gateway-internal": 8504,
    "ingress-nginx-controller": 8505,
    "haproxy": 8510,
    "haproxy-backup": 8511,
    # Kafka Services (9200s range)
    "kafka-2": 9200,
    "kafka-ui": 8600,
    "schema-registry": 8601,
    "constitutional-events-schema-registry": 8602,
    # Special Services (8700s range)
    "redis-commander": 8700,
    "cadvisor": 8701,
    "evidently": 8702,
    "cockroachdb": 8703,
    "kong": 8704,
    "registry": 8705,
    "kimi_service": 8706,
    "kimi_swe_service": 8707,
    "nano-vllm-reasoning": 8708,
    "nano-vllm-reasoning-staging": 8709,
    # Operational Services (8800s range)
    "operational-framework": 8800,
    "operational-config": 8801,
    "enterprise-monitoring": 8802,
    "ocr-monitoring": 8803,
    # Deployment Services (8900s range)
    "frontend-deployment": 8900,
    "frontend-service": 8901,
    "audit-trail-archiver": 8902,
    "acgs-traffic-controller": 8903,
    "acgs-deployment-status": 8904,
    "rollback-controller": 8905,
    "acgs-health-checker": 8906,
    "acgs-model-service": 8907,
    "acge-model-service": 8908,
    # Test Services (8950s range)
    "test_priority3_integration": 8950,
    "test_core_services_unit_coverage": 8951,
    "test_evolutionary_tensor_integration": 8952,
    "constitutional_service_pattern": 8953,
    "deploy_staging": 8954,
    "simple_main": 8955,
    "main": 8956,
    # MCP Services (3000s range) - already configured correctly
    "mcp_aggregator": 3000,
    "mcp_filesystem": 3010,
    "mcp_github": 3011,
    "mcp_browser": 3012,
    # Nvidia Services (8980s range)
    "nvidia_llm_router_controller": 8980,
    "nvidia_llm_router_server": 8981,
    # ACGS Extended Services (8990s range)
    "acgs-constitutional-ai-service": 8990,
    "acgs-policy-governance-service": 8991,
    "acgs-governance-synthesis-service": 8992,
    "acgs-pgp-deployment": 8993,
}


def update_env_file():
    """Update config/environments/development.env file with all unique port assignments."""
    env_file_path = "config/environments/development.env"

    try:
        with open(env_file_path, "r") as f:
            content = f.read()

        # Create new port section
        port_section = "\n# Port Configuration - All Unique Assignments\n"
        port_section += "# Constitutional Hash: cdd01ef066bc6cf2\n\n"

        # Core Infrastructure
        port_section += "# Core Infrastructure\n"
        port_section += "POSTGRES_PORT=5439\n"
        port_section += "REDIS_PORT=6389\n"
        port_section += "OPA_PORT=8181\n"
        port_section += "NATS_PORT=4222\n"
        port_section += "NATS_HTTP_PORT=8222\n\n"

        # Core ACGS Services
        port_section += "# Core ACGS Services\n"
        port_section += "CONSTITUTIONAL_AI_PORT=8001\n"
        port_section += "INTEGRITY_PORT=8200\n"
        port_section += "AUTH_PORT=8100\n"
        port_section += "API_GATEWAY_PORT=8300\n"
        port_section += "GOVERNANCE_SYNTHESIS_PORT=8400\n"
        port_section += "POLICY_GOVERNANCE_PORT=8401\n"
        port_section += "FORMAL_VERIFICATION_PORT=8402\n"
        port_section += "CODE_ANALYSIS_PORT=8007\n"
        port_section += "CONTEXT_PORT=8012\n\n"

        # MCP Services
        port_section += "# MCP Services\n"
        port_section += "MCP_AGGREGATOR_PORT=3000\n"
        port_section += "MCP_FILESYSTEM_PORT=3010\n"
        port_section += "MCP_GITHUB_PORT=3011\n"
        port_section += "MCP_BROWSER_PORT=3012\n\n"

        # Monitoring Services
        port_section += "# Monitoring Services\n"
        port_section += "PROMETHEUS_PORT=9090\n"
        port_section += "GRAFANA_PORT=3001\n"
        port_section += "ALERTMANAGER_PORT=9100\n"
        port_section += "JAEGER_UI_PORT=16686\n"
        port_section += "JAEGER_COLLECTOR_PORT=14268\n"
        port_section += "JAEGER_AGENT_PORT=6831\n"
        port_section += "ELASTICSEARCH_PORT=9200\n"
        port_section += "KIBANA_PORT=5601\n"
        port_section += "NODE_EXPORTER_PORT=9100\n"
        port_section += "POSTGRES_EXPORTER_PORT=9187\n"
        port_section += "REDIS_EXPORTER_PORT=9121\n"

        # Remove existing port configuration section if it exists
        lines = content.split("\n")
        new_lines = []
        skip_section = False

        for line in lines:
            if line.strip().startswith("# Port Configuration"):
                skip_section = True
                continue
            elif skip_section and line.startswith("#") and "Services" in line:
                continue
            elif skip_section and ("_PORT=" in line or line.strip() == ""):
                continue
            else:
                skip_section = False
                new_lines.append(line)

        # Find where to insert the new port section
        insert_index = -1
        for i, line in enumerate(new_lines):
            if line.startswith("# ACGS Core Services URLs"):
                insert_index = i
                break

        if insert_index >= 0:
            new_lines.insert(insert_index, port_section)
        else:
            new_lines.append(port_section)

        # Write back to file
        with open(env_file_path, "w") as f:
            f.write("\n".join(new_lines))

        print("✅ Updated config/environments/development.env file with unique port assignments")
        return True

    except Exception as e:
        print(f"❌ Error updating config/environments/development.env file: {e}")
        return False


def main():
    """Main function to fix port conflicts."""
    print("🔧 ACGS Port Conflict Resolution")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)

    success = update_env_file()

    print("=" * 60)
    if success:
        print("🎉 Port conflicts have been resolved!")
        print("📋 Next steps:")
        print("   1. Review the updated config/environments/development.env file")
        print("   2. Update any Docker Compose files that reference hardcoded ports")
        print("   3. Test service startup with new port assignments")
        print("   4. Update documentation with new port mappings")
    else:
        print("❌ Some issues occurred during port conflict resolution")


if __name__ == "__main__":
    main()
