#!/usr/bin/env python3
"""
Comprehensive ACGS-1 CI/CD Pipeline Analysis
Validates all GitHub Actions workflows for constitutional governance system
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CICDPipelineAnalyzer:
    """Comprehensive CI/CD pipeline analysis for ACGS-1."""

    def __init__(self):
        self.root_dir = Path("/home/dislove/ACGS-1")
        self.workflows_dir = self.root_dir / ".github" / "workflows"
        self.analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "Comprehensive CI/CD Pipeline Analysis",
            "workflow_files": {},
            "technology_coverage": {},
            "security_analysis": {},
            "performance_metrics": {},
            "integration_validation": {},
            "issues_found": [],
            "recommendations": [],
            "overall_health": "unknown",
        }

    def analyze_workflow_files(self):
        """Analyze all workflow files for syntax and configuration."""
        logger.info("🔍 Analyzing workflow files...")

        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        for workflow_file in workflow_files:
            logger.info(f"  📄 Analyzing {workflow_file.name}")

            try:
                # Parse YAML syntax
                with open(workflow_file) as f:
                    workflow_content = yaml.safe_load(f)

                # Analyze workflow structure
                analysis = {
                    "file_path": str(workflow_file.relative_to(self.root_dir)),
                    "syntax_valid": True,
                    "triggers": workflow_content.get("on", {}),
                    "jobs": list(workflow_content.get("jobs", {}).keys()),
                    "job_count": len(workflow_content.get("jobs", {})),
                    "permissions": workflow_content.get("permissions", {}),
                    "environment_vars": workflow_content.get("env", {}),
                    "issues": [],
                }

                # Check for required elements
                if not workflow_content.get("name"):
                    analysis["issues"].append("Missing workflow name")

                if not workflow_content.get("on"):
                    analysis["issues"].append("Missing trigger configuration")

                if not workflow_content.get("jobs"):
                    analysis["issues"].append("No jobs defined")

                # Analyze job dependencies
                jobs = workflow_content.get("jobs", {})
                for job_name, job_config in jobs.items():
                    if "needs" in job_config:
                        analysis[f"{job_name}_dependencies"] = job_config["needs"]

                self.analysis_report["workflow_files"][workflow_file.name] = analysis
                logger.info(
                    f"    ✅ {workflow_file.name}: Valid ({analysis['job_count']} jobs)"
                )

            except yaml.YAMLError as e:
                logger.error(f"    ❌ {workflow_file.name}: YAML syntax error - {e}")
                self.analysis_report["workflow_files"][workflow_file.name] = {
                    "file_path": str(workflow_file.relative_to(self.root_dir)),
                    "syntax_valid": False,
                    "error": str(e),
                    "issues": ["YAML syntax error"],
                }
                self.analysis_report["issues_found"].append(
                    f"YAML syntax error in {workflow_file.name}"
                )

            except Exception as e:
                logger.error(f"    ❌ {workflow_file.name}: Analysis error - {e}")
                self.analysis_report["issues_found"].append(
                    f"Analysis error in {workflow_file.name}: {e!s}"
                )

    def analyze_technology_coverage(self):
        """Analyze technology stack coverage across workflows."""
        logger.info("🏗️ Analyzing technology stack coverage...")

        technology_matrix = {
            "rust_anchor": {"workflows": [], "coverage": "none"},
            "python_services": {"workflows": [], "coverage": "none"},
            "typescript_javascript": {"workflows": [], "coverage": "none"},
            "docker_containers": {"workflows": [], "coverage": "none"},
            "solana_blockchain": {"workflows": [], "coverage": "none"},
        }

        # Check each workflow for technology support
        for workflow_name, workflow_data in self.analysis_report[
            "workflow_files"
        ].items():
            if not workflow_data.get("syntax_valid", False):
                continue

            workflow_path = Path(workflow_data["file_path"])
            try:
                with open(self.root_dir / workflow_path) as f:
                    content = f.read().lower()

                # Check for Rust/Anchor support
                if any(
                    keyword in content
                    for keyword in ["rust", "anchor", "cargo", "solana"]
                ):
                    technology_matrix["rust_anchor"]["workflows"].append(workflow_name)

                # Check for Python support
                if any(
                    keyword in content
                    for keyword in ["python", "pip", "pytest", "bandit", "black"]
                ):
                    technology_matrix["python_services"]["workflows"].append(
                        workflow_name
                    )

                # Check for TypeScript/JavaScript support
                if any(
                    keyword in content
                    for keyword in ["node", "npm", "typescript", "javascript", "yarn"]
                ):
                    technology_matrix["typescript_javascript"]["workflows"].append(
                        workflow_name
                    )

                # Check for Docker support
                if any(
                    keyword in content
                    for keyword in ["docker", "dockerfile", "container", "buildx"]
                ):
                    technology_matrix["docker_containers"]["workflows"].append(
                        workflow_name
                    )

                # Check for Solana blockchain support
                if any(
                    keyword in content
                    for keyword in ["solana", "anchor", "devnet", "blockchain"]
                ):
                    technology_matrix["solana_blockchain"]["workflows"].append(
                        workflow_name
                    )

            except Exception as e:
                logger.warning(f"    ⚠️ Could not analyze {workflow_name}: {e}")

        # Determine coverage levels
        for tech, data in technology_matrix.items():
            workflow_count = len(data["workflows"])
            if workflow_count >= 2:
                data["coverage"] = "comprehensive"
            elif workflow_count == 1:
                data["coverage"] = "basic"
            else:
                data["coverage"] = "none"

        self.analysis_report["technology_coverage"] = technology_matrix

        # Log results
        for tech, data in technology_matrix.items():
            coverage_icon = "✅" if data["coverage"] != "none" else "❌"
            logger.info(
                f"  {coverage_icon} {tech.replace('_', ' ').title()}: {data['coverage']} ({len(data['workflows'])} workflows)"
            )

    def analyze_security_configuration(self):
        """Analyze security scanning and configuration."""
        logger.info("🔒 Analyzing security configuration...")

        security_features = {
            "codeql_scanning": False,
            "dependency_scanning": False,
            "container_scanning": False,
            "secret_scanning": False,
            "security_permissions": False,
            "msdo_scanning": False,
        }

        security_workflows = []

        for workflow_name, workflow_data in self.analysis_report[
            "workflow_files"
        ].items():
            if not workflow_data.get("syntax_valid", False):
                continue

            # Check permissions
            permissions = workflow_data.get("permissions", {})
            if "security-events" in permissions:
                security_features["security_permissions"] = True

            # Check for security-related workflows
            if any(
                keyword in workflow_name.lower()
                for keyword in ["security", "codeql", "defender"]
            ):
                security_workflows.append(workflow_name)

            # Check workflow content for security features
            workflow_path = Path(workflow_data["file_path"])
            try:
                with open(self.root_dir / workflow_path) as f:
                    content = f.read().lower()

                if "codeql" in content:
                    security_features["codeql_scanning"] = True
                if any(
                    keyword in content
                    for keyword in ["bandit", "safety", "trivy", "dependency"]
                ):
                    security_features["dependency_scanning"] = True
                if "trivy" in content or "container" in content:
                    security_features["container_scanning"] = True
                if "microsoft/security-devops" in content:
                    security_features["msdo_scanning"] = True

            except Exception as e:
                logger.warning(
                    f"    ⚠️ Could not analyze security in {workflow_name}: {e}"
                )

        self.analysis_report["security_analysis"] = {
            "features": security_features,
            "security_workflows": security_workflows,
            "security_score": sum(security_features.values())
            / len(security_features)
            * 100,
        }

        security_score = self.analysis_report["security_analysis"]["security_score"]
        logger.info(f"  📊 Security Score: {security_score:.1f}%")

        for feature, enabled in security_features.items():
            status_icon = "✅" if enabled else "❌"
            logger.info(f"    {status_icon} {feature.replace('_', ' ').title()}")

    def analyze_performance_optimization(self):
        """Analyze workflow performance and optimization."""
        logger.info("⚡ Analyzing performance optimization...")

        performance_features = {
            "caching_enabled": False,
            "parallel_jobs": False,
            "conditional_execution": False,
            "artifact_management": False,
            "matrix_strategies": False,
        }

        total_jobs = 0
        workflows_with_caching = []

        for workflow_name, workflow_data in self.analysis_report[
            "workflow_files"
        ].items():
            if not workflow_data.get("syntax_valid", False):
                continue

            total_jobs += workflow_data.get("job_count", 0)

            workflow_path = Path(workflow_data["file_path"])
            try:
                with open(self.root_dir / workflow_path) as f:
                    content = f.read().lower()

                # Check for performance optimizations
                if "cache" in content:
                    performance_features["caching_enabled"] = True
                    workflows_with_caching.append(workflow_name)

                if "strategy:" in content and "matrix:" in content:
                    performance_features["matrix_strategies"] = True

                if "needs:" in content:
                    performance_features["parallel_jobs"] = True

                if "if:" in content:
                    performance_features["conditional_execution"] = True

                if "upload-artifact" in content or "download-artifact" in content:
                    performance_features["artifact_management"] = True

            except Exception as e:
                logger.warning(
                    f"    ⚠️ Could not analyze performance in {workflow_name}: {e}"
                )

        self.analysis_report["performance_metrics"] = {
            "features": performance_features,
            "total_jobs": total_jobs,
            "workflows_with_caching": workflows_with_caching,
            "performance_score": sum(performance_features.values())
            / len(performance_features)
            * 100,
        }

        performance_score = self.analysis_report["performance_metrics"][
            "performance_score"
        ]
        logger.info(f"  📊 Performance Score: {performance_score:.1f}%")
        logger.info(f"  📈 Total Jobs Across Workflows: {total_jobs}")

    def validate_constitutional_governance_integration(self):
        """Validate integration with constitutional governance system."""
        logger.info("🏛️ Validating constitutional governance integration...")

        governance_features = {
            "quantumagi_deployment": False,
            "service_health_checks": False,
            "governance_workflow_testing": False,
            "constitutional_compliance": False,
            "solana_devnet_integration": False,
        }

        # Check for governance-specific configurations
        for workflow_name, workflow_data in self.analysis_report[
            "workflow_files"
        ].items():
            if not workflow_data.get("syntax_valid", False):
                continue

            workflow_path = Path(workflow_data["file_path"])
            try:
                with open(self.root_dir / workflow_path) as f:
                    content = f.read().lower()

                if "quantumagi" in content:
                    governance_features["quantumagi_deployment"] = True

                if "health" in content or "service" in content:
                    governance_features["service_health_checks"] = True

                if any(
                    keyword in content
                    for keyword in ["governance", "constitutional", "compliance"]
                ):
                    governance_features["governance_workflow_testing"] = True
                    governance_features["constitutional_compliance"] = True

                if "devnet" in content or "solana" in content:
                    governance_features["solana_devnet_integration"] = True

            except Exception as e:
                logger.warning(
                    f"    ⚠️ Could not analyze governance integration in {workflow_name}: {e}"
                )

        self.analysis_report["integration_validation"] = {
            "governance_features": governance_features,
            "integration_score": sum(governance_features.values())
            / len(governance_features)
            * 100,
        }

        integration_score = self.analysis_report["integration_validation"][
            "integration_score"
        ]
        logger.info(f"  📊 Governance Integration Score: {integration_score:.1f}%")

    def generate_recommendations(self):
        """Generate recommendations for pipeline improvements."""
        logger.info("💡 Generating recommendations...")

        recommendations = []

        # Technology coverage recommendations
        tech_coverage = self.analysis_report["technology_coverage"]
        for tech, data in tech_coverage.items():
            if data["coverage"] == "none":
                recommendations.append(
                    f"Add {tech.replace('_', ' ')} support to CI/CD pipeline"
                )

        # Security recommendations
        security_score = self.analysis_report["security_analysis"]["security_score"]
        if security_score < 80:
            recommendations.append("Enhance security scanning coverage (target: >80%)")

        # Performance recommendations
        performance_score = self.analysis_report["performance_metrics"][
            "performance_score"
        ]
        if performance_score < 70:
            recommendations.append(
                "Optimize workflow performance with caching and parallelization"
            )

        # Integration recommendations
        integration_score = self.analysis_report["integration_validation"][
            "integration_score"
        ]
        if integration_score < 80:
            recommendations.append(
                "Improve constitutional governance system integration"
            )

        # Workflow-specific recommendations
        for workflow_name, workflow_data in self.analysis_report[
            "workflow_files"
        ].items():
            if workflow_data.get("issues"):
                recommendations.append(
                    f"Fix issues in {workflow_name}: {', '.join(workflow_data['issues'])}"
                )

        self.analysis_report["recommendations"] = recommendations

        if recommendations:
            logger.info("  📋 Recommendations generated:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"    {i}. {rec}")
        else:
            logger.info(
                "  ✅ No critical recommendations - pipeline is well-configured"
            )

    def calculate_overall_health(self):
        """Calculate overall pipeline health score."""
        logger.info("📊 Calculating overall pipeline health...")

        # Weight different aspects
        weights = {
            "syntax_validity": 0.25,
            "technology_coverage": 0.25,
            "security_score": 0.25,
            "performance_score": 0.15,
            "integration_score": 0.10,
        }

        # Calculate syntax validity score
        valid_workflows = sum(
            1
            for w in self.analysis_report["workflow_files"].values()
            if w.get("syntax_valid", False)
        )
        total_workflows = len(self.analysis_report["workflow_files"])
        syntax_score = (
            (valid_workflows / total_workflows * 100) if total_workflows > 0 else 0
        )

        # Get other scores
        tech_score = (
            sum(
                1
                for t in self.analysis_report["technology_coverage"].values()
                if t["coverage"] != "none"
            )
            / len(self.analysis_report["technology_coverage"])
            * 100
        )
        security_score = self.analysis_report["security_analysis"]["security_score"]
        performance_score = self.analysis_report["performance_metrics"][
            "performance_score"
        ]
        integration_score = self.analysis_report["integration_validation"][
            "integration_score"
        ]

        # Calculate weighted overall score
        overall_score = (
            syntax_score * weights["syntax_validity"]
            + tech_score * weights["technology_coverage"]
            + security_score * weights["security_score"]
            + performance_score * weights["performance_score"]
            + integration_score * weights["integration_score"]
        )

        # Determine health status
        if overall_score >= 90:
            health_status = "excellent"
        elif overall_score >= 80:
            health_status = "good"
        elif overall_score >= 70:
            health_status = "fair"
        else:
            health_status = "needs_improvement"

        self.analysis_report["overall_health"] = {
            "score": round(overall_score, 1),
            "status": health_status,
            "component_scores": {
                "syntax_validity": round(syntax_score, 1),
                "technology_coverage": round(tech_score, 1),
                "security_score": round(security_score, 1),
                "performance_score": round(performance_score, 1),
                "integration_score": round(integration_score, 1),
            },
        }

        logger.info(
            f"  🎯 Overall Health Score: {overall_score:.1f}% ({health_status.replace('_', ' ').title()})"
        )

    def save_report(self):
        """Save the comprehensive analysis report."""
        report_file = (
            self.root_dir
            / f"cicd_pipeline_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(self.analysis_report, f, indent=2)

        logger.info(f"📄 Analysis report saved: {report_file}")
        return report_file

    def run_analysis(self):
        """Execute the complete CI/CD pipeline analysis."""
        logger.info("🚀 Starting Comprehensive CI/CD Pipeline Analysis")
        logger.info("=" * 60)

        start_time = time.time()

        # Execute analysis phases
        self.analyze_workflow_files()
        self.analyze_technology_coverage()
        self.analyze_security_configuration()
        self.analyze_performance_optimization()
        self.validate_constitutional_governance_integration()
        self.generate_recommendations()
        self.calculate_overall_health()

        # Save report
        self.save_report()

        duration = time.time() - start_time

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 CI/CD PIPELINE ANALYSIS SUMMARY")
        logger.info("=" * 60)

        overall_health = self.analysis_report["overall_health"]
        logger.info(
            f"🎯 Overall Health: {overall_health['score']}% ({overall_health['status'].replace('_', ' ').title()})"
        )
        logger.info(
            f"📄 Workflows Analyzed: {len(self.analysis_report['workflow_files'])}"
        )
        logger.info(f"🔍 Issues Found: {len(self.analysis_report['issues_found'])}")
        logger.info(
            f"💡 Recommendations: {len(self.analysis_report['recommendations'])}"
        )
        logger.info(f"⏱️ Analysis Duration: {duration:.2f} seconds")

        if overall_health["score"] >= 80:
            logger.info("🎉 CI/CD Pipeline: PRODUCTION READY!")
        else:
            logger.info("⚠️ CI/CD Pipeline: Needs Improvement")

        return self.analysis_report


def main():
    """Main execution function."""
    analyzer = CICDPipelineAnalyzer()
    report = analyzer.run_analysis()

    # Return success if overall health is good
    return 0 if report["overall_health"]["score"] >= 70 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
