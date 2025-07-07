#!/usr/bin/env python3
"""
Batch Constitutional Hash Addition Script
Adds constitutional hash comments to all files missing them.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Files that need constitutional hash (from validation report)
MISSING_HASH_FILES = [
    # Test files (Priority 1)
    "services/blockchain/test_database_performance_simulation.py",
    "services/blockchain/test_database_performance_optimization.py",
    "services/core/policy-governance/pgc_service/tests/test_wina_enforcement_integration.py",
    "services/core/policy-governance/pgc_service/tests/test_wina_enforcement_optimizer.py",
    "services/core/code-analysis/code_analysis_service/test_server.py",
    "services/core/code-analysis/code_analysis_service/test_minimal.py",
    "services/core/constitutional-ai/ac_service/test_stakeholder_engagement.py",
    "services/core/constitutional-ai/ac_service/test_stakeholder_simple.py",
    "services/core/constitutional-ai/ac_service/tests/test_hitl_api_integration.py",
    "services/core/constitutional-ai/ac_service/tests/test_intelligent_conflict_resolution.py",
    "services/core/constitutional-ai/ac_service/tests/test_human_in_the_loop_sampling.py",
    "services/core/governance-synthesis/gs_service/tests/test_wina_rego_synthesis.py",
    "services/core/governance-synthesis/gs_service/tests/test_policy_synthesis_enhancement.py",
    "services/core/governance-synthesis/gs_service/tests/test_wina_rego_integration.py",
    "services/core/governance-synthesis/gs_service/tests/test_router_optimization.py",
    "services/core/governance-synthesis/gs_service/tests/integration/test_opa_integration.py",
    "services/core/governance-synthesis/gs_service/tests/performance/test_governance_synthesis_performance.py",
    "services/core/governance-synthesis/gs_service/tests/security/test_security_compliance.py",
    "services/core/governance-synthesis/gs_service/tests/unit/services/test_policy_validator.py",
    "services/shared/wina/test_wina_core.py",
    "services/platform_services/authentication/auth_service/test_agent_system.py",
    "services/platform_services/authentication/auth_service/app/tests/test_users.py",
    "services/platform_services/authentication/auth_service/app/tests/test_rate_limiting.py",
    "services/platform_services/authentication/auth_service/app/tests/test_main.py",
    "services/platform_services/authentication/auth_service/app/tests/test_auth.py",
    "services/platform_services/authentication/auth_service/app/tests/__init__.py",
    "services/platform_services/authentication/auth_service/app/tests/test_auth_flows.py",
    "services/platform_services/authentication/auth_service/app/tests/test_token.py",
    "tests/multi_agent_test_runner.py",
    "tests/unit/test_apgf_integration.py",
    "tests/unit/__init__.py",
    "tests/unit/test_blackboard_service.py",
    "tests/unit/test_openrouter_integration.py",
    "tests/unit/test_worker_agents.py",
    "tests/unit/test_consensus_engine.py",
    "tests/unit/test_performance_monitoring.py",
    "tests/fixtures/mock_services.py",
    "tests/fixtures/__init__.py",
    "tests/integration/test_agent_coordination.py",
    "tests/integration/__init__.py",
    "tests/performance/__init__.py",
    "tests/fixtures/multi_agent/mock_services.py",
    "tests/fixtures/multi_agent/__init__.py",
    "tests/e2e/tests/constitutional.py",
    "tests/e2e/tests/security.py",
    "tests/e2e/tests/health.py",
    "tests/e2e/tests/infrastructure.py",
    "tests/e2e/tests/performance.py",
    "tests/e2e/tests/__init__.py",
    "tests/e2e/tests/governance.py",
    "tests/e2e/tests/hitl.py",
    "tests/e2e/framework/core.py",
    "tests/e2e/framework/__init__.py",
    "tests/e2e/framework/reporter.py",
    "tests/e2e/framework/mocks.py",
    "tests/e2e/framework/runner.py",
    "tests/e2e/framework/base.py",
    # Docker files (Priority 2)
    # Note: Docker files will be handled separately
    # Script files (Priority 3)
    "services/blockchain/scripts/validate_devnet_deployment.py",
    "services/blockchain/scripts/demo_end_to_end.py",
    "services/blockchain/scripts/advanced_features_demo.py",
    "services/blockchain/scripts/deploy_quantumagi.py",
    "services/blockchain/scripts/generate_program_ids.py",
    "services/blockchain/scripts/transaction_optimizer.py",
    "services/blockchain/scripts/initialize_constitution.py",
    "scripts/cicd/setup_branch_protection.py",
    "scripts/cicd/deployment_gates.py",
    "scripts/monitoring/deploy_enterprise_dashboard.py",
    "scripts/ci/validate_pytest_config.py",
    # Service files (Priority 4)
    "services/core/formal-verification/fv_service/app/core/proof_verification_pipeline.py",
    "services/core/formal-verification/fv_service/app/api/v1/proof_pipeline.py",
    "services/core/constitutional-ai/ac_service/app/services/hybrid_rlhf_constitutional_ai.py",
    "services/blockchain/client/python/solana_client.py",
    "services/cli_backup_20250706_110222/gemini_cli/monitoring.py",
    "services/cli_backup_20250706_110222/gemini_cli/setup.py",
    "services/cli_backup_20250706_110222/gemini_cli/__init__.py",
    "services/cli_backup_20250706_110222/gemini_cli/acgs_client.py",
    "services/cli_backup_20250706_110222/gemini_cli/gemini_cli.py",
    "services/cli_backup_20250706_110222/gemini_cli/mcp_servers/filesystem.py",
    "services/cli_backup_20250706_110222/gemini_cli/mcp_servers/__init__.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/audit.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/execute.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/monitor.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/__init__.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/verify.py",
    "services/cli_backup_20250706_110222/gemini_cli/commands/agent.py",
    "services/cli_backup_20250706_110222/gemini_cli/tools/__init__.py",
    "services/cli_backup_20250706_110222/gemini_cli/formatters/__init__.py",
    "services/shared/streaming/kafka_config_manager.py",
    "services/shared/streaming/__init__.py",
    "services/shared/streaming/event_streaming_manager.py",
    "services/shared/streaming/kafka_integration.py",
    "services/shared/streaming/example_usage.py",
    "services/shared/monitoring/advanced_metrics_collector.py",
    "services/shared/monitoring/__init__.py",
    "services/shared/monitoring/human_intervention_tracker.py",
    "services/shared/monitoring/model_drift_detector.py",
    "services/shared/fairness/bias_drift_monitor.py",
    "services/shared/fairness/fairlearn_integration.py",
    "services/shared/fairness/whatif_tool_integration.py",
    "services/shared/fairness/__init__.py",
    "services/shared/fairness/enhanced_fairness_framework.py",
    "services/shared/fairness/bias_mitigation_engine.py",
    "services/shared/compliance/__init__.py",
    "services/shared/compliance/compliance_monitor.py",
    "services/shared/compliance/human_oversight.py",
    "services/shared/compliance/technical_documentation.py",
    "services/shared/compliance/eu_ai_act_compliance.py",
    "services/shared/security/__init__.py",
    "services/shared/cache/__init__.py",
    "services/shared/explainability/lime_integration.py",
    "services/shared/explainability/__init__.py",
    "services/shared/explainability/hybrid_explainability_engine.py",
    "services/shared/explainability/shap_integration.py",
    "services/shared/agents/__init__.py",
    "services/shared/agents/apgf_orchestrator.py",
    "services/shared/agents/tool_router.py",
    "services/shared/async_processing/__init__.py",
    "services/shared/resource_management/__init__.py",
    "services/platform_services/integrity/integrity_service/app/api/v1/persistent_audit.py",
]


class ConstitutionalHashAdder:
    """Adds constitutional hash comments to files."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.files_processed = 0
        self.files_updated = 0
        self.errors: List[str] = []

    def add_hash_to_python_file(self, file_path: Path) -> bool:
        """Add constitutional hash to a Python file."""
        try:
            if not file_path.exists():
                self.errors.append(f"File not found: {file_path}")
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if hash already exists
            if CONSTITUTIONAL_HASH in content:
                print(
                    f"  ✅ Hash already present: {file_path.relative_to(self.base_path)}"
                )
                return False

            lines = content.split("\n")
            insert_index = 0

            # Find the best place to insert the hash
            # Skip shebang, encoding, and initial docstring
            for i, line in enumerate(lines):
                if line.startswith("#!") or "coding:" in line or "encoding:" in line:
                    insert_index = i + 1
                    continue
                elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Skip docstring
                    quote_type = '"""' if '"""' in line else "'''"
                    if line.count(quote_type) == 2:
                        # Single line docstring
                        insert_index = i + 1
                    else:
                        # Multi-line docstring
                        for j in range(i + 1, len(lines)):
                            if quote_type in lines[j]:
                                insert_index = j + 1
                                break
                    break
                elif line.strip() and not line.startswith("#"):
                    # First non-comment, non-empty line
                    insert_index = i
                    break

            # Insert constitutional hash comment
            hash_comment = f"# Constitutional Hash: {CONSTITUTIONAL_HASH}"

            # Add some spacing if needed
            if insert_index < len(lines) and lines[insert_index].strip():
                lines.insert(insert_index, hash_comment)
                lines.insert(insert_index + 1, "")
            else:
                lines.insert(insert_index, hash_comment)

            # Write back to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            print(f"  ✅ Added hash to: {file_path.relative_to(self.base_path)}")
            return True

        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {str(e)}")
            return False

    def process_files(self, file_list: List[str]) -> Dict[str, int]:
        """Process a list of files to add constitutional hash."""
        results = {"processed": 0, "updated": 0, "errors": 0, "not_found": 0}

        print(f"🔍 Processing {len(file_list)} files...")

        for file_path_str in file_list:
            file_path = self.base_path / file_path_str
            results["processed"] += 1

            if not file_path.exists():
                results["not_found"] += 1
                print(f"  ⚠️  File not found: {file_path_str}")
                continue

            if self.add_hash_to_python_file(file_path):
                results["updated"] += 1
            else:
                if file_path_str not in [str(e) for e in self.errors]:
                    # File exists but hash already present or other non-error condition
                    pass
                else:
                    results["errors"] += 1

        return results


def main() -> None:
    """Main function to add constitutional hash to all missing files."""
    print("⚖️  ACGS Constitutional Hash Batch Addition")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)

    base_path = Path(__file__).parent.parent
    adder = ConstitutionalHashAdder(base_path)

    # Process test files first (Priority 1)
    print("\n🧪 Processing Test Files (Priority 1)...")
    test_files = [
        f for f in MISSING_HASH_FILES if "test" in f.lower() or "/tests/" in f
    ]
    test_results = adder.process_files(test_files)

    print(f"\n📊 Test Files Results:")
    print(f"  Processed: {test_results['processed']}")
    print(f"  Updated: {test_results['updated']}")
    print(f"  Not Found: {test_results['not_found']}")
    print(f"  Errors: {test_results['errors']}")

    # Process script files (Priority 3)
    print("\n📜 Processing Script Files (Priority 3)...")
    script_files = [
        f for f in MISSING_HASH_FILES if "/scripts/" in f or f.startswith("scripts/")
    ]
    script_results = adder.process_files(script_files)

    print(f"\n📊 Script Files Results:")
    print(f"  Processed: {script_results['processed']}")
    print(f"  Updated: {script_results['updated']}")
    print(f"  Not Found: {script_results['not_found']}")
    print(f"  Errors: {script_results['errors']}")

    # Process remaining service files (Priority 4)
    print("\n⚙️  Processing Service Files (Priority 4)...")
    service_files = [
        f
        for f in MISSING_HASH_FILES
        if not (
            "test" in f.lower()
            or "/tests/" in f
            or "/scripts/" in f
            or f.startswith("scripts/")
        )
    ]
    service_results = adder.process_files(service_files)

    print(f"\n📊 Service Files Results:")
    print(f"  Processed: {service_results['processed']}")
    print(f"  Updated: {service_results['updated']}")
    print(f"  Not Found: {service_results['not_found']}")
    print(f"  Errors: {service_results['errors']}")

    # Summary
    total_processed = (
        test_results["processed"]
        + script_results["processed"]
        + service_results["processed"]
    )
    total_updated = (
        test_results["updated"] + script_results["updated"] + service_results["updated"]
    )
    total_not_found = (
        test_results["not_found"]
        + script_results["not_found"]
        + service_results["not_found"]
    )
    total_errors = (
        test_results["errors"] + script_results["errors"] + service_results["errors"]
    )

    print(f"\n📊 Overall Summary:")
    print(f"  Total Processed: {total_processed}")
    print(f"  Total Updated: {total_updated}")
    print(f"  Total Not Found: {total_not_found}")
    print(f"  Total Errors: {total_errors}")

    if adder.errors:
        print(f"\n❌ Errors encountered:")
        for error in adder.errors:
            print(f"  - {error}")

    print(f"\n✅ Constitutional hash addition completed!")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    main()
