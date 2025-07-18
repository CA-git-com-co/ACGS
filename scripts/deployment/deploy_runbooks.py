#!/usr/bin/env python3
"""
ACGS-1 Runbook Deployment and Validation Script
Deploys operational runbooks and validates their completeness and accessibility
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RunbookDeployer:
    """Deployer for ACGS-1 Operational Runbooks"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.runbooks_dir = (
            self.project_root / "infrastructure" / "monitoring" / "runbooks"
        )
        self.scripts_dir = self.project_root / "scripts"

        # Core runbooks that should exist
        self.core_runbooks = [
            "service_down_runbook.md",
            "high_response_time_runbook.md",
            "database_issues_runbook.md",
            "constitutional_compliance_runbook.md",
            "incident_response_playbook.md",
            "change_management_runbook.md",
            "README.md",
        ]

        # Ensure directories exist
        self.runbooks_dir.mkdir(parents=True, exist_ok=True)

    async def deploy_runbooks(self) -> dict[str, Any]:
        """Deploy and validate all operational runbooks"""
        logger.info("🚀 Starting ACGS-1 Runbook Deployment and Validation")
        logger.info("=" * 80)

        start_time = time.time()
        results = {}

        try:
            # Step 1: Validate runbook directory structure
            results["directory_structure"] = await self.validate_directory_structure()

            # Step 2: Validate core runbooks exist
            results["core_runbooks"] = await self.validate_core_runbooks()

            # Step 3: Validate runbook content and format
            results["content_validation"] = await self.validate_runbook_content()

            # Step 4: Create runbook index and navigation
            results["index_creation"] = await self.create_runbook_index()

            # Step 5: Validate emergency procedures
            results["emergency_procedures"] = await self.validate_emergency_procedures()

            # Step 6: Create runbook access tools
            results["access_tools"] = await self.create_access_tools()

            # Step 7: Validate escalation procedures
            results["escalation_validation"] = (
                await self.validate_escalation_procedures()
            )

            # Step 8: Create runbook training materials
            results["training_materials"] = await self.create_training_materials()

            # Step 9: Setup runbook maintenance procedures
            results["maintenance_setup"] = await self.setup_maintenance_procedures()

            # Step 10: Final validation and testing
            results["final_validation"] = await self.final_validation()

            total_time = time.time() - start_time

            logger.info("✅ Runbook deployment completed successfully!")
            logger.info(f"⏱️  Total deployment time: {total_time:.2f} seconds")

            return {
                "status": "success",
                "deployment_time": total_time,
                "results": results,
                "summary": self.generate_deployment_summary(results),
            }

        except Exception as e:
            logger.error(f"❌ Runbook deployment failed: {e}")
            return {"status": "failed", "error": str(e), "results": results}

    async def validate_directory_structure(self) -> dict[str, Any]:
        """Validate runbook directory structure"""
        logger.info("📁 Validating runbook directory structure...")

        validation = {}

        # Check main runbooks directory
        validation["runbooks_dir"] = {
            "exists": self.runbooks_dir.exists(),
            "path": str(self.runbooks_dir),
            "writable": (
                os.access(self.runbooks_dir, os.W_OK)
                if self.runbooks_dir.exists()
                else False
            ),
        }

        # Check for subdirectories
        subdirs = ["templates", "assets", "scripts"]
        for subdir in subdirs:
            subdir_path = self.runbooks_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            validation[f"subdir_{subdir}"] = {
                "exists": subdir_path.exists(),
                "path": str(subdir_path),
            }

        return validation

    async def validate_core_runbooks(self) -> dict[str, Any]:
        """Validate that all core runbooks exist"""
        logger.info("📚 Validating core runbooks...")

        validation = {}

        for runbook in self.core_runbooks:
            runbook_path = self.runbooks_dir / runbook
            validation[runbook] = {
                "exists": runbook_path.exists(),
                "path": str(runbook_path),
                "size": runbook_path.stat().st_size if runbook_path.exists() else 0,
                "readable": runbook_path.is_file() if runbook_path.exists() else False,
            }

        # Count total runbooks
        all_runbooks = list(self.runbooks_dir.glob("*.md"))
        validation["summary"] = {
            "total_runbooks": len(all_runbooks),
            "core_runbooks_present": sum(
                1 for rb in self.core_runbooks if (self.runbooks_dir / rb).exists()
            ),
            "core_runbooks_required": len(self.core_runbooks),
        }

        return validation

    async def validate_runbook_content(self) -> dict[str, Any]:
        """Validate runbook content and format"""
        logger.info("🔍 Validating runbook content...")

        validation = {}

        for runbook in self.core_runbooks:
            if runbook == "README.md":
                continue

            runbook_path = self.runbooks_dir / runbook
            if not runbook_path.exists():
                validation[runbook] = {"status": "missing"}
                continue

            try:
                with open(runbook_path) as f:
                    content = f.read()

                # Check for required sections
                required_sections = [
                    "## Overview",
                    "## Immediate Response",
                    "## Investigation",
                    "## Escalation Procedures",
                    "## Post-Incident Actions",
                ]

                section_checks = {}
                for section in required_sections:
                    section_checks[section] = section in content

                # Check for emergency commands
                has_emergency_commands = "```bash" in content and "curl" in content

                # Check for contact information
                has_contacts = (
                    "Emergency Contacts" in content or "Escalation" in content
                )

                validation[runbook] = {
                    "status": "valid",
                    "size": len(content),
                    "sections": section_checks,
                    "has_emergency_commands": has_emergency_commands,
                    "has_contacts": has_contacts,
                    "completeness_score": sum(section_checks.values())
                    / len(section_checks)
                    * 100,
                }

            except Exception as e:
                validation[runbook] = {"status": "error", "error": str(e)}

        return validation

    async def create_runbook_index(self) -> dict[str, Any]:
        """Create comprehensive runbook index"""
        logger.info("📖 Creating runbook index...")

        try:
            # Create quick reference card
            quick_ref_content = """# ACGS-1 Quick Reference Card

## Emergency Commands
```bash
# System health check
python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py health

# Emergency service restart
python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py restart

# Constitutional compliance check
curl -f http://localhost:8005/api/v1/governance/compliance/status  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

# Database connectivity test
psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;"

# Service status check
for port in {8000..8006}; do echo -n "Port $port: "; curl -f http://localhost:$port/health >/dev/null 2>&1 && echo "UP" || echo "DOWN"; done
```

## Critical Thresholds
- **Service Availability:** >99.5%
- **Response Time:** <500ms (95th percentile)
- **Constitutional Compliance:** >95%
- **Database Query Time:** <100ms

## Emergency Contacts
- **Operations Team:** #acgs-operations
- **Constitutional Team:** #acgs-governance
- **Security Team:** #acgs-security
- **On-Call:** Emergency rotation

## Escalation Levels
- **P0 Critical:** <5 minutes (Complete outage)
- **P1 High:** <15 minutes (Major impact)
- **P2 Medium:** <1 hour (Moderate impact)
- **P3 Low:** <4 hours (Minor impact)
"""

            quick_ref_path = self.runbooks_dir / "quick_reference.md"
            with open(quick_ref_path, "w") as f:
                f.write(quick_ref_content)

            # Create runbook checklist
            checklist_content = """# Incident Response Checklist

## Initial Response (0-5 minutes)
- [ ] Acknowledge alert within target time
- [ ] Assess severity and impact
- [ ] Check system health status
- [ ] Identify affected services
- [ ] Notify team if escalation needed

## Investigation (5-30 minutes)
- [ ] Review recent changes/deployments
- [ ] Check service logs for errors
- [ ] Analyze system metrics
- [ ] Identify root cause
- [ ] Document findings

## Resolution (30 minutes - 4 hours)
- [ ] Implement immediate mitigation
- [ ] Apply permanent fix
- [ ] Verify resolution
- [ ] Test affected functionality
- [ ] Monitor for recurrence

## Communication
- [ ] Update stakeholders on status
- [ ] Document actions taken
- [ ] Schedule post-incident review
- [ ] Update runbooks if needed

## Constitutional Governance Specific
- [ ] Verify constitutional hash: cdd01ef066bc6cf2
- [ ] Check compliance rate >95%
- [ ] Validate governance workflows
- [ ] Ensure blockchain connectivity
"""

            checklist_path = self.runbooks_dir / "incident_checklist.md"
            with open(checklist_path, "w") as f:
                f.write(checklist_content)

            return {
                "status": "created",
                "quick_reference": str(quick_ref_path),
                "checklist": str(checklist_path),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def validate_emergency_procedures(self) -> dict[str, Any]:
        """Validate emergency procedures are accessible"""
        logger.info("🚨 Validating emergency procedures...")

        validation = {}

        # Check emergency scripts exist
        emergency_scripts = [
            "emergency_rollback_procedures.py",
            "comprehensive_health_check.py",
            "simple_backup_recovery.py",
        ]

        for script in emergency_scripts:
            script_path = self.scripts_dir / script
            validation[script] = {
                "exists": script_path.exists(),
                "executable": (
                    os.access(script_path, os.X_OK) if script_path.exists() else False
                ),
                "path": str(script_path),
            }

        # Test emergency commands
        try:
            # Test health check
            result = subprocess.run(
                [
                    "python3",
                    str(self.scripts_dir / "emergency_rollback_procedures.py"),
                    "health",
                ],
                check=False,
                capture_output=True,
                timeout=30,
                text=True,
            )
            validation["health_check_test"] = {
                "status": "success" if result.returncode == 0 else "failed",
                "output": (
                    result.stdout[:200]
                    if result.returncode == 0
                    else result.stderr[:200]
                ),
            }
        except Exception as e:
            validation["health_check_test"] = {"status": "error", "error": str(e)}

        return validation

    async def create_access_tools(self) -> dict[str, Any]:
        """Create tools for easy runbook access"""
        logger.info("🔧 Creating runbook access tools...")

        try:
            # Create runbook search script
            search_script = self.scripts_dir / "search_runbooks.py"
            search_content = f"""#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

def search_runbooks(query):
    runbooks_dir = Path("{self.runbooks_dir}")
    results = []
    
    for runbook in runbooks_dir.glob("*.md"):
        try:
            with open(runbook, 'r') as f:
                content = f.read()
            
            if re.search(query, content, re.IGNORECASE):
                results.append({{
                    "file": runbook.name,
                    "path": str(runbook),
                    "matches": len(re.findall(query, content, re.IGNORECASE))
                }})
        except Exception:
            continue
    
    return sorted(results, key=lambda x: x["matches"], reverse=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search_runbooks.py <search_term>")
        sys.exit(1)
    
    query = sys.argv[1]
    results = search_runbooks(query)
    
    if results:
        print(f"Found {{len(results)}} runbooks matching '{{query}}':")
        for result in results:
            print(f"  {{result['file']}} ({{result['matches']}} matches)")
            print(f"    Path: {{result['path']}}")
    else:
        print(f"No runbooks found matching '{{query}}'")
"""

            with open(search_script, "w") as f:
                f.write(search_content)
            search_script.chmod(0o755)

            # Create runbook launcher script
            launcher_script = self.scripts_dir / "open_runbook.py"
            launcher_content = f"""#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def open_runbook(runbook_name):
    runbooks_dir = Path("{self.runbooks_dir}")
    
    # Try exact match first
    runbook_path = runbooks_dir / runbook_name
    if not runbook_path.exists():
        # Try with .md extension
        runbook_path = runbooks_dir / f"{{runbook_name}}.md"
    
    if not runbook_path.exists():
        # Search for partial matches
        matches = list(runbooks_dir.glob(f"*{{runbook_name}}*.md"))
        if matches:
            runbook_path = matches[0]
        else:
            print(f"Runbook '{{runbook_name}}' not found")
            return False
    
    # Open with default editor or viewer
    try:
        subprocess.run(["less", str(runbook_path)])
        return True
    except Exception as e:
        print(f"Error opening runbook: {{e}}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 open_runbook.py <runbook_name>")
        print("Available runbooks:")
        runbooks_dir = Path("{self.runbooks_dir}")
        for runbook in sorted(runbooks_dir.glob("*.md")):
            print(f"  {{runbook.stem}}")
        sys.exit(1)
    
    runbook_name = sys.argv[1]
    open_runbook(runbook_name)
"""

            with open(launcher_script, "w") as f:
                f.write(launcher_content)
            launcher_script.chmod(0o755)

            return {
                "status": "created",
                "search_script": str(search_script),
                "launcher_script": str(launcher_script),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def validate_escalation_procedures(self) -> dict[str, Any]:
        """Validate escalation procedures are defined"""
        logger.info("📞 Validating escalation procedures...")

        validation = {}

        # Check each runbook has escalation procedures
        for runbook in self.core_runbooks:
            if runbook == "README.md":
                continue

            runbook_path = self.runbooks_dir / runbook
            if not runbook_path.exists():
                validation[runbook] = {"status": "missing"}
                continue

            try:
                with open(runbook_path) as f:
                    content = f.read()

                has_escalation = "Escalation" in content
                has_contacts = "Contact" in content or "Team" in content
                has_timeframes = any(
                    time in content for time in ["minutes", "hours", "immediate"]
                )

                validation[runbook] = {
                    "has_escalation_section": has_escalation,
                    "has_contact_info": has_contacts,
                    "has_timeframes": has_timeframes,
                    "escalation_complete": has_escalation
                    and has_contacts
                    and has_timeframes,
                }

            except Exception as e:
                validation[runbook] = {"status": "error", "error": str(e)}

        return validation

    async def create_training_materials(self) -> dict[str, Any]:
        """Create runbook training materials"""
        logger.info("🎓 Creating training materials...")

        try:
            training_dir = self.runbooks_dir / "training"
            training_dir.mkdir(exist_ok=True)

            # Create training checklist
            training_content = """# ACGS-1 Runbook Training Program

## Training Requirements

### New Team Member Onboarding
- [ ] Complete runbook overview session
- [ ] Review all core runbooks
- [ ] Practice emergency procedures
- [ ] Shadow experienced team member during incident
- [ ] Complete runbook quiz

### Quarterly Training Requirements
- [ ] Review updated runbooks
- [ ] Practice incident response drill
- [ ] Update emergency contact information
- [ ] Test escalation procedures

### Annual Certification
- [ ] Complete comprehensive runbook review
- [ ] Pass incident response simulation
- [ ] Demonstrate emergency procedure execution
- [ ] Update training documentation

## Training Modules

### Module 1: Runbook Overview
- Purpose and structure of runbooks
- When and how to use runbooks
- Emergency response principles
- Constitutional governance framework

### Module 2: Service-Specific Procedures
- Understanding each service's role
- Common failure patterns
- Service-specific troubleshooting
- Dependencies and interactions

### Module 3: Emergency Response
- Incident classification and severity
- Emergency command execution
- Escalation procedures and timing
- Communication protocols

### Module 4: Constitutional Governance
- Constitutional compliance requirements
- Governance workflow understanding
- Blockchain integration basics
- Stakeholder communication

## Practical Exercises

### Exercise 1: Service Down Response
- Simulate service outage
- Practice diagnostic procedures
- Execute recovery steps
- Document lessons learned

### Exercise 2: Constitutional Compliance Failure
- Simulate compliance violation
- Practice emergency halt procedures
- Execute compliance restoration
- Validate constitutional framework

### Exercise 3: Performance Degradation
- Simulate high response times
- Practice performance analysis
- Execute optimization procedures
- Monitor improvement

## Assessment Criteria

### Knowledge Assessment
- Understanding of runbook structure
- Familiarity with emergency procedures
- Knowledge of escalation paths
- Constitutional governance awareness

### Practical Assessment
- Ability to execute emergency procedures
- Proper use of diagnostic tools
- Effective communication during incidents
- Documentation and follow-up skills
"""

            training_path = training_dir / "training_program.md"
            with open(training_path, "w") as f:
                f.write(training_content)

            return {
                "status": "created",
                "training_dir": str(training_dir),
                "training_program": str(training_path),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def setup_maintenance_procedures(self) -> dict[str, Any]:
        """Setup runbook maintenance procedures"""
        logger.info("🔧 Setting up maintenance procedures...")

        try:
            # Create maintenance script
            maintenance_script = self.scripts_dir / "maintain_runbooks.py"
            maintenance_content = f"""#!/usr/bin/env python3
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

def check_runbook_freshness():
    runbooks_dir = Path("{self.runbooks_dir}")
    stale_runbooks = []
    
    for runbook in runbooks_dir.glob("*.md"):
        stat = runbook.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        age_days = (datetime.now() - modified_time).days
        
        if age_days > 90:  # Consider stale after 90 days
            stale_runbooks.append({{
                "file": runbook.name,
                "age_days": age_days,
                "last_modified": modified_time.strftime("%Y-%m-%d")
            }})
    
    return stale_runbooks

def validate_runbook_links():
    runbooks_dir = Path("{self.runbooks_dir}")
    broken_links = []
    
    for runbook in runbooks_dir.glob("*.md"):
        try:
            with open(runbook, 'r') as f:
                content = f.read()
            
            # Check for internal links
            import re
            links = re.findall(r'\\[.*?\\]\\((.*?\\.md)\\)', content)
            
            for link in links:
                link_path = runbooks_dir / link
                if not link_path.exists():
                    broken_links.append({{
                        "runbook": runbook.name,
                        "broken_link": link
                    }})
        except Exception:
            continue
    
    return broken_links

if __name__ == "__main__":
    print("ACGS-1 Runbook Maintenance Report")
    print("=" * 40)
    
    # Check for stale runbooks
    stale = check_runbook_freshness()
    if stale:
        print(f"\\nStale runbooks (>90 days old): {{len(stale)}}")
        for item in stale:
            print(f"  {{item['file']}} - {{item['age_days']}} days old")
    else:
        print("\\n✅ All runbooks are up to date")
    
    # Check for broken links
    broken = validate_runbook_links()
    if broken:
        print(f"\\nBroken links found: {{len(broken)}}")
        for item in broken:
            print(f"  {{item['runbook']}} -> {{item['broken_link']}}")
    else:
        print("\\n✅ All runbook links are valid")
"""

            with open(maintenance_script, "w") as f:
                f.write(maintenance_content)
            maintenance_script.chmod(0o755)

            return {"status": "created", "maintenance_script": str(maintenance_script)}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def final_validation(self) -> dict[str, Any]:
        """Perform final validation of runbook deployment"""
        logger.info("✅ Performing final validation...")

        validation = {}

        # Count total runbooks
        all_runbooks = list(self.runbooks_dir.glob("*.md"))
        validation["total_runbooks"] = len(all_runbooks)

        # Check core runbooks completeness
        core_present = sum(
            1 for rb in self.core_runbooks if (self.runbooks_dir / rb).exists()
        )
        validation["core_completeness"] = {
            "present": core_present,
            "required": len(self.core_runbooks),
            "percentage": (core_present / len(self.core_runbooks)) * 100,
        }

        # Check access tools
        access_tools = ["search_runbooks.py", "open_runbook.py", "maintain_runbooks.py"]
        tools_present = sum(
            1 for tool in access_tools if (self.scripts_dir / tool).exists()
        )
        validation["access_tools"] = {
            "present": tools_present,
            "required": len(access_tools),
            "percentage": (tools_present / len(access_tools)) * 100,
        }

        # Overall deployment score
        validation["deployment_score"] = (
            validation["core_completeness"]["percentage"] * 0.6
            + validation["access_tools"]["percentage"] * 0.4
        )

        return validation

    def generate_deployment_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            "runbooks_deployed": 0,
            "tools_created": 0,
            "validations_passed": 0,
            "issues_found": 0,
        }

        # Analyze results
        for component, result in results.items():
            if isinstance(result, dict):
                if result.get("status") == "created":
                    summary["tools_created"] += 1

                if "total_runbooks" in result:
                    summary["runbooks_deployed"] = result["total_runbooks"]

                if "percentage" in result and result["percentage"] > 80:
                    summary["validations_passed"] += 1
                elif "error" in result:
                    summary["issues_found"] += 1

        return summary


async def main():
    """Main deployment function"""
    deployer = RunbookDeployer()
    result = await deployer.deploy_runbooks()

    print("\\n" + "=" * 80)
    print("RUNBOOK DEPLOYMENT SUMMARY")
    print("=" * 80)
    print(json.dumps(result, indent=2))

    if result["status"] == "success":
        print("\\n✅ Runbook deployment completed successfully!")
        print("\\nNext steps:")
        print("1. Review runbooks: ls -la infrastructure/monitoring/runbooks/")
        print("2. Search runbooks: python3 scripts/search_runbooks.py <term>")
        print("3. Open runbook: python3 scripts/open_runbook.py <name>")
        print("4. Maintain runbooks: python3 scripts/maintain_runbooks.py")
    else:
        print("\\n❌ Runbook deployment failed. Check the error details above.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
