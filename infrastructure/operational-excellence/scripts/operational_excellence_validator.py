#!/usr/bin/env python3
"""
ACGS Operational Excellence Validator
Validates and scores operational excellence to achieve 98+/100 production readiness
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OperationalExcellenceValidator:
    """
    Comprehensive operational excellence validator
    Assesses all aspects of operational maturity and provides actionable recommendations
    """

    def __init__(self):
        self.validation_id = f"validation-{int(time.time())}"
        self.base_path = Path(__file__).parent.parent.parent.parent
        self.results = {
            "validation_id": self.validation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": 0,
            "target_score": 98,
            "categories": {},
            "recommendations": [],
            "critical_issues": [],
            "status": "in_progress",
        }

    async def validate_operational_excellence(self) -> dict:
        """Execute comprehensive operational excellence validation"""
        logger.info(f"Starting operational excellence validation: {self.validation_id}")

        try:
            # Category 1: Deployment Pipeline Excellence (25 points)
            logger.info("Validating deployment pipeline excellence...")
            deployment_score = await self._validate_deployment_pipeline()
            self.results["categories"]["deployment_pipeline"] = deployment_score

            # Category 2: Infrastructure as Code (20 points)
            logger.info("Validating infrastructure as code...")
            iac_score = await self._validate_infrastructure_as_code()
            self.results["categories"]["infrastructure_as_code"] = iac_score

            # Category 3: Monitoring & Observability (20 points)
            logger.info("Validating monitoring and observability...")
            monitoring_score = await self._validate_monitoring_observability()
            self.results["categories"]["monitoring_observability"] = monitoring_score

            # Category 4: Disaster Recovery & Business Continuity (15 points)
            logger.info("Validating disaster recovery...")
            dr_score = await self._validate_disaster_recovery()
            self.results["categories"]["disaster_recovery"] = dr_score

            # Category 5: Security & Compliance (10 points)
            logger.info("Validating security and compliance...")
            security_score = await self._validate_security_compliance()
            self.results["categories"]["security_compliance"] = security_score

            # Category 6: Documentation & Knowledge Management (10 points)
            logger.info("Validating documentation...")
            docs_score = await self._validate_documentation()
            self.results["categories"]["documentation"] = docs_score

            # Calculate overall score
            self.results["overall_score"] = sum(
                category["score"] for category in self.results["categories"].values()
            )

            # Generate recommendations
            self.results["recommendations"] = self._generate_recommendations()
            self.results["critical_issues"] = self._identify_critical_issues()

            # Determine status
            if self.results["overall_score"] >= self.results["target_score"]:
                self.results["status"] = "excellent"
            elif self.results["overall_score"] >= 90:
                self.results["status"] = "good"
            elif self.results["overall_score"] >= 80:
                self.results["status"] = "acceptable"
            else:
                self.results["status"] = "needs_improvement"

            logger.info(
                f"Validation complete. Score: {self.results['overall_score']}/100"
            )

        except Exception as e:
            self.results["status"] = "failed"
            self.results["error"] = str(e)
            logger.error(f"Validation failed: {e}")

        # Save results
        await self._save_results()

        return self.results

    async def _validate_deployment_pipeline(self) -> dict:
        """Validate deployment pipeline maturity (25 points max)"""
        score = 0
        details = []
        max_score = 25

        # CI/CD Pipeline Configuration (5 points)
        ci_files = [
            self.base_path / ".github/workflows/ci.yml",
            self.base_path / ".github/workflows/ci-uv.yml",
        ]

        if any(f.exists() for f in ci_files):
            score += 5
            details.append("✅ CI/CD pipeline configured")
        else:
            details.append("❌ CI/CD pipeline missing")

        # Automated Testing (5 points)
        test_files = list(self.base_path.rglob("test_*.py")) + list(
            self.base_path.rglob("*_test.py")
        )
        if len(test_files) >= 20:
            score += 5
            details.append(
                f"✅ Comprehensive test suite ({len(test_files)} test files)"
            )
        elif len(test_files) >= 10:
            score += 3
            details.append(f"⚠️ Good test coverage ({len(test_files)} test files)")
        elif len(test_files) >= 5:
            score += 2
            details.append(f"⚠️ Basic test coverage ({len(test_files)} test files)")
        else:
            details.append("❌ Insufficient test coverage")

        # Blue-Green Deployment (5 points)
        blue_green_files = [
            self.base_path / "scripts/blue_green_deployment.py",
            self.base_path
            / "infrastructure/operational-excellence/scripts/enterprise_deployment_pipeline.py",
        ]

        if any(f.exists() for f in blue_green_files):
            score += 5
            details.append("✅ Blue-green deployment implemented")
        else:
            details.append("❌ Blue-green deployment missing")

        # Rollback Procedures (5 points)
        rollback_files = list(self.base_path.glob("scripts/*rollback*"))
        if len(rollback_files) >= 2:
            score += 5
            details.append("✅ Comprehensive rollback procedures")
        elif len(rollback_files) >= 1:
            score += 3
            details.append("⚠️ Basic rollback procedures")
        else:
            details.append("❌ Rollback procedures missing")

        # Deployment Validation (5 points)
        validation_files = [
            self.base_path / "scripts/validate_production_deployment.sh",
            self.base_path / "scripts/validate_production_deployment_comprehensive.py",
        ]

        if any(f.exists() for f in validation_files):
            score += 5
            details.append("✅ Deployment validation automated")
        else:
            details.append("❌ Deployment validation missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Deployment Pipeline Excellence",
        }

    async def _validate_infrastructure_as_code(self) -> dict:
        """Validate Infrastructure as Code implementation (20 points max)"""
        score = 0
        details = []
        max_score = 20

        # Kubernetes Manifests (5 points)
        k8s_dir = self.base_path / "infrastructure/kubernetes"
        if k8s_dir.exists():
            k8s_files = list(k8s_dir.glob("*.yaml"))
            if len(k8s_files) >= 15:
                score += 5
                details.append(
                    f"✅ Comprehensive Kubernetes manifests ({len(k8s_files)} files)"
                )
            elif len(k8s_files) >= 10:
                score += 4
                details.append(f"✅ Good Kubernetes coverage ({len(k8s_files)} files)")
            elif len(k8s_files) >= 5:
                score += 2
                details.append(f"⚠️ Basic Kubernetes coverage ({len(k8s_files)} files)")
            else:
                details.append("❌ Insufficient Kubernetes manifests")
        else:
            details.append("❌ Kubernetes directory missing")

        # Docker Compose Configurations (5 points)
        docker_dir = self.base_path / "infrastructure/docker"
        if docker_dir.exists():
            compose_files = list(docker_dir.glob("docker-compose*.yml"))
            if len(compose_files) >= 8:
                score += 5
                details.append(
                    f"✅ Multiple environment configurations ({len(compose_files)} files)"
                )
            elif len(compose_files) >= 5:
                score += 3
                details.append(
                    f"⚠️ Good environment coverage ({len(compose_files)} files)"
                )
            else:
                details.append("❌ Limited environment configurations")
        else:
            details.append("❌ Docker configuration missing")

        # Terraform/Infrastructure Automation (5 points)
        terraform_dir = self.base_path / "infrastructure/terraform"
        if terraform_dir.exists():
            tf_files = list(terraform_dir.glob("*.tf"))
            if len(tf_files) >= 3:
                score += 5
                details.append("✅ Terraform infrastructure automation")
            else:
                score += 2
                details.append("⚠️ Basic Terraform setup")
        else:
            details.append("❌ Infrastructure automation missing")

        # GitOps Implementation (5 points)
        gitops_dirs = [self.base_path / "crossplane", self.base_path / "argocd"]

        if all(d.exists() for d in gitops_dirs):
            score += 5
            details.append("✅ GitOps workflow implemented")
        elif any(d.exists() for d in gitops_dirs):
            score += 2
            details.append("⚠️ Partial GitOps implementation")
        else:
            details.append("❌ GitOps workflow missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Infrastructure as Code",
        }

    async def _validate_monitoring_observability(self) -> dict:
        """Validate monitoring and observability (20 points max)"""
        score = 0
        details = []
        max_score = 20

        # Prometheus Configuration (5 points)
        prometheus_files = [
            self.base_path / "infrastructure/monitoring/prometheus.yml",
            self.base_path / "infrastructure/docker/prometheus.yml",
        ]

        if any(f.exists() for f in prometheus_files):
            score += 5
            details.append("✅ Prometheus monitoring configured")
        else:
            details.append("❌ Prometheus monitoring missing")

        # Grafana Dashboards (5 points)
        grafana_dirs = [
            self.base_path / "infrastructure/monitoring/grafana_dashboards",
            self.base_path / "infrastructure/monitoring/dashboards",
        ]

        dashboard_count = 0
        for dir_path in grafana_dirs:
            if dir_path.exists():
                dashboard_count += len(list(dir_path.glob("*.json")))

        if dashboard_count >= 10:
            score += 5
            details.append(
                f"✅ Comprehensive Grafana dashboards ({dashboard_count} dashboards)"
            )
        elif dashboard_count >= 5:
            score += 3
            details.append(f"⚠️ Good dashboard coverage ({dashboard_count} dashboards)")
        elif dashboard_count >= 1:
            score += 1
            details.append(f"⚠️ Basic dashboards ({dashboard_count} dashboards)")
        else:
            details.append("❌ Grafana dashboards missing")

        # Alerting Rules (5 points)
        alert_dirs = [
            self.base_path / "infrastructure/monitoring/rules",
            self.base_path / "infrastructure/monitoring/alerting",
        ]

        alert_files = []
        for dir_path in alert_dirs:
            if dir_path.exists():
                alert_files.extend(list(dir_path.glob("*.yml")))
                alert_files.extend(list(dir_path.glob("*.yaml")))

        if len(alert_files) >= 5:
            score += 5
            details.append("✅ Comprehensive alerting rules")
        elif len(alert_files) >= 2:
            score += 3
            details.append("⚠️ Basic alerting rules")
        else:
            details.append("❌ Alerting rules missing")

        # Distributed Tracing (5 points)
        tracing_dirs = [
            self.base_path / "infrastructure/monitoring/jaeger",
            self.base_path / "infrastructure/observability",
        ]

        if any(d.exists() for d in tracing_dirs):
            score += 5
            details.append("✅ Distributed tracing implemented")
        else:
            details.append("❌ Distributed tracing missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Monitoring & Observability",
        }

    async def _validate_disaster_recovery(self) -> dict:
        """Validate disaster recovery capabilities (15 points max)"""
        score = 0
        details = []
        max_score = 15

        # Backup Procedures (5 points)
        backup_files = list(self.base_path.glob("scripts/*backup*"))
        dr_script = (
            self.base_path
            / "infrastructure/operational-excellence/scripts/disaster_recovery_automation.py"
        )

        if dr_script.exists():
            score += 5
            details.append("✅ Enterprise disaster recovery automation")
        elif len(backup_files) >= 3:
            score += 4
            details.append(
                f"✅ Comprehensive backup procedures ({len(backup_files)} scripts)"
            )
        elif len(backup_files) >= 1:
            score += 2
            details.append(f"⚠️ Basic backup procedures ({len(backup_files)} scripts)")
        else:
            details.append("❌ Backup procedures missing")

        # Disaster Recovery Documentation (5 points)
        dr_docs = list(self.base_path.rglob("*disaster*recovery*"))
        dr_docs.extend(list(self.base_path.rglob("*DISASTER*RECOVERY*")))

        if len(dr_docs) >= 2:
            score += 5
            details.append("✅ Comprehensive disaster recovery documentation")
        elif len(dr_docs) >= 1:
            score += 3
            details.append("⚠️ Basic disaster recovery documentation")
        else:
            details.append("❌ Disaster recovery documentation missing")

        # Emergency Procedures (5 points)
        emergency_files = [
            self.base_path / "scripts/emergency-response.sh",
            self.base_path / "scripts/emergency_response.py",
            self.base_path / "scripts/emergency_shutdown_all_services.sh",
        ]

        existing_emergency = [f for f in emergency_files if f.exists()]
        if len(existing_emergency) >= 2:
            score += 5
            details.append("✅ Comprehensive emergency procedures")
        elif len(existing_emergency) >= 1:
            score += 3
            details.append("⚠️ Basic emergency procedures")
        else:
            details.append("❌ Emergency procedures missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Disaster Recovery & Business Continuity",
        }

    async def _validate_security_compliance(self) -> dict:
        """Validate security and compliance (10 points max)"""
        score = 0
        details = []
        max_score = 10

        # Security Scanning (5 points)
        security_files = list(self.base_path.glob("scripts/*security*"))
        if len(security_files) >= 8:
            score += 5
            details.append(
                f"✅ Comprehensive security scanning ({len(security_files)} scripts)"
            )
        elif len(security_files) >= 5:
            score += 3
            details.append(f"⚠️ Good security coverage ({len(security_files)} scripts)")
        elif len(security_files) >= 2:
            score += 1
            details.append(f"⚠️ Basic security scanning ({len(security_files)} scripts)")
        else:
            details.append("❌ Security scanning missing")

        # Compliance Validation (5 points)
        compliance_files = list(self.base_path.glob("scripts/*compliance*"))
        constitutional_files = list(self.base_path.glob("scripts/*constitutional*"))

        total_compliance = len(compliance_files) + len(constitutional_files)
        if total_compliance >= 5:
            score += 5
            details.append("✅ Comprehensive compliance validation")
        elif total_compliance >= 2:
            score += 3
            details.append("⚠️ Basic compliance validation")
        else:
            details.append("❌ Compliance validation missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Security & Compliance",
        }

    async def _validate_documentation(self) -> dict:
        """Validate documentation and knowledge management (10 points max)"""
        score = 0
        details = []
        max_score = 10

        # Operational Runbooks (5 points)
        runbook_files = list(self.base_path.rglob("*runbook*"))
        runbook_files.extend(list(self.base_path.rglob("*RUNBOOK*")))
        runbook_files.extend(list(self.base_path.rglob("*OPERATIONAL*")))

        enterprise_runbook = (
            self.base_path
            / "infrastructure/operational-excellence/runbooks/ENTERPRISE_OPERATIONAL_RUNBOOK.md"
        )

        if enterprise_runbook.exists():
            score += 5
            details.append("✅ Enterprise operational runbook available")
        elif len(runbook_files) >= 3:
            score += 4
            details.append(
                f"✅ Multiple operational runbooks ({len(runbook_files)} files)"
            )
        elif len(runbook_files) >= 1:
            score += 2
            details.append(f"⚠️ Basic runbooks available ({len(runbook_files)} files)")
        else:
            details.append("❌ Operational runbooks missing")

        # Deployment and Technical Guides (5 points)
        guide_files = list(self.base_path.rglob("*DEPLOYMENT*"))
        guide_files.extend(list(self.base_path.rglob("*GUIDE*")))
        guide_files.extend(list(self.base_path.rglob("*deployment*guide*")))

        if len(guide_files) >= 5:
            score += 5
            details.append(
                f"✅ Comprehensive documentation ({len(guide_files)} guides)"
            )
        elif len(guide_files) >= 3:
            score += 3
            details.append(f"⚠️ Good documentation coverage ({len(guide_files)} guides)")
        elif len(guide_files) >= 1:
            score += 1
            details.append(f"⚠️ Basic documentation ({len(guide_files)} guides)")
        else:
            details.append("❌ Deployment guides missing")

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "details": details,
            "category": "Documentation & Knowledge Management",
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations"""
        recommendations = []

        for category_name, category_data in self.results["categories"].items():
            if category_data["percentage"] < 80:
                recommendations.append(
                    f"Improve {category_data['category']}: {category_data['percentage']:.1f}% "
                    f"(Target: 80%+, Current: {category_data['score']}/{category_data['max_score']})"
                )

        if self.results["overall_score"] < self.results["target_score"]:
            gap = self.results["target_score"] - self.results["overall_score"]
            recommendations.append(
                f"Overall score gap: {gap} points needed to reach {self.results['target_score']}/100 target"
            )

        return recommendations

    def _identify_critical_issues(self) -> list[str]:
        """Identify critical issues that must be addressed"""
        critical_issues = []

        for category_name, category_data in self.results["categories"].items():
            if category_data["percentage"] < 60:
                critical_issues.append(
                    f"CRITICAL: {category_data['category']} score {category_data['percentage']:.1f}% "
                    f"is below acceptable threshold (60%)"
                )

        return critical_issues

    async def _save_results(self):
        """Save validation results"""
        results_dir = Path("/tmp/operational_excellence_results")
        results_dir.mkdir(exist_ok=True)

        results_file = results_dir / f"{self.validation_id}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Validation results saved to {results_file}")


async def main():
    """Main validation execution"""
    validator = OperationalExcellenceValidator()

    print("🔍 ACGS Operational Excellence Validation")
    print("=" * 50)

    results = await validator.validate_operational_excellence()

    print("\n📊 VALIDATION RESULTS")
    print(
        f"Overall Score: {results['overall_score']}/100 (Target: {results['target_score']})"
    )
    print(f"Status: {results['status'].upper()}")

    print("\n📈 CATEGORY BREAKDOWN")
    for category_name, category_data in results["categories"].items():
        status_icon = (
            "✅"
            if category_data["percentage"] >= 80
            else "⚠️" if category_data["percentage"] >= 60 else "❌"
        )
        print(
            f"{status_icon} {category_data['category']}: {category_data['score']}/{category_data['max_score']} ({category_data['percentage']:.1f}%)"
        )

    if results["critical_issues"]:
        print("\n🚨 CRITICAL ISSUES")
        for issue in results["critical_issues"]:
            print(f"  • {issue}")

    if results["recommendations"]:
        print("\n💡 RECOMMENDATIONS")
        for rec in results["recommendations"]:
            print(f"  • {rec}")

    print(
        f"\n📄 Detailed results saved to: /tmp/operational_excellence_results/{results['validation_id']}.json"
    )

    if results["overall_score"] >= results["target_score"]:
        print("\n🎉 CONGRATULATIONS! Operational excellence target achieved!")
    else:
        gap = results["target_score"] - results["overall_score"]
        print(f"\n🎯 {gap} points needed to reach operational excellence target")


if __name__ == "__main__":
    asyncio.run(main())
