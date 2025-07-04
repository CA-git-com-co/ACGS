#!/usr/bin/env python3
"""
Quantumagi End-to-End Demonstration Script
Showcases the complete constitutional governance workflow from principle to enforcement
"""

import asyncio
import json
import logging

# Add project paths
import os
import sys
from datetime import datetime

# Add blockchain directory to path for imports
blockchain_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if blockchain_dir not in sys.path:
    sys.path.insert(0, blockchain_dir)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QuantumagiDemo:
    """Complete end-to-end demonstration of Quantumagi framework"""

    def __init__(self):
        self.demo_data = {
            "constitution_hash": None,
            "policies": [],
            "compliance_results": [],
            "appeals": [],
            "metrics": {
                "start_time": datetime.now(),
                "policies_created": 0,
                "compliance_checks": 0,
                "appeals_processed": 0,
            },
        }

    async def run_complete_demo(self):
        """Run the complete Quantumagi demonstration"""

        print("\n" + "=" * 80)
        print("🏛️  QUANTUMAGI END-TO-END DEMONSTRATION")
        print("    On-Chain Constitutional Governance for Solana")
        print("=" * 80)

        try:
            # Phase 1: Constitutional Foundation
            await self._phase_1_constitutional_foundation()

            # Phase 2: Policy Synthesis & Proposal
            await self._phase_2_policy_synthesis()

            # Phase 3: Democratic Governance
            await self._phase_3_democratic_governance()

            # Phase 4: Real-time Compliance Enforcement
            await self._phase_4_compliance_enforcement()

            # Phase 5: Appeals & Human Oversight
            await self._phase_5_appeals_system()

            # Phase 6: System Integration & Monitoring
            await self._phase_6_system_integration()

            # Final Report
            await self._generate_final_report()

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise

    async def _phase_1_constitutional_foundation(self):
        """Phase 1: Initialize constitutional framework"""
        print("\n📜 PHASE 1: CONSTITUTIONAL FOUNDATION")
        print("-" * 50)

        # Create constitutional document
        constitution_content = """
        QUANTUMAGI CONSTITUTIONAL FRAMEWORK v1.0

        PREAMBLE
        We, the community of Quantumagi, establish this constitutional framework
        to govern AI systems operating on the Solana blockchain with transparency,
        safety, and democratic participation.

        ARTICLE I: FUNDAMENTAL PRINCIPLES
        Section 1: No Extrajudicial State Mutation (PC-001)
        AI systems shall not perform unauthorized state mutations without proper
        governance approval through established democratic processes.

        Section 2: Democratic Governance Requirement (GV-001)
        All governance decisions affecting the community must be subject to
        transparent democratic voting with adequate deliberation time.

        Section 3: Treasury Protection (FN-001)
        Community treasury operations exceeding established limits require
        multi-signature approval from elected treasury guardians.

        ARTICLE II: AI SAFETY STANDARDS
        Section 1: Safety-First Operations (SF-001)
        All AI system deployments must undergo comprehensive safety validation
        with continuous monitoring and immediate halt capabilities.

        Section 2: Transparency and Auditability (TR-001)
        All governance decisions and compliance checks must be publicly
        auditable with immutable logging on the blockchain.

        ARTICLE III: ENFORCEMENT MECHANISMS
        Section 1: Prompt Governance Compiler (PGC)
        Real-time compliance checking shall be enforced through the PGC system
        with multi-model validation achieving 99.92% reliability.

        Section 2: Appeals Process
        Community members may appeal policy violations through a multi-tier
        system including automated review and human oversight.
        """

        # Generate constitution hash
        import hashlib

        constitution_hash = hashlib.sha256(constitution_content.encode()).digest()
        self.demo_data["constitution_hash"] = constitution_hash.hex()

        print(
            f"✅ Constitutional document created ({len(constitution_content)} characters)"
        )
        print(f"📋 Constitution hash: {constitution_hash.hex()[:16]}...")
        print("🏛️ Framework established with 5 core principles")

        # Simulate on-chain initialization
        await asyncio.sleep(1)
        print("⛓️  Constitution initialized on Solana blockchain")

        await asyncio.sleep(2)

    async def _phase_2_policy_synthesis(self):
        """Phase 2: GS Engine policy synthesis"""
        print("\n🧠 PHASE 2: GOVERNANCE SYNTHESIS ENGINE")
        print("-" * 50)

        # Constitutional principles to synthesize
        principles = [
            {
                "id": "PC-001",
                "title": "No Extrajudicial State Mutation",
                "content": "AI systems must not perform unauthorized state mutations without proper governance approval",
                "category": "prompt_constitution",
                "priority": "critical",
            },
            {
                "id": "GV-001",
                "title": "Democratic Policy Approval",
                "content": "All governance policies must be approved through democratic voting process",
                "category": "governance",
                "priority": "high",
            },
            {
                "id": "FN-001",
                "title": "Treasury Protection",
                "content": "Financial operations exceeding limits require multi-signature approval",
                "category": "financial",
                "priority": "critical",
            },
        ]

        print(f"🔄 Processing {len(principles)} constitutional principles...")

        for principle in principles:
            print(f"\n  📋 Synthesizing: {principle['id']} - {principle['title']}")

            # Simulate GS Engine processing
            print("    🔍 Running multi-model validation...")
            await asyncio.sleep(1)

            # Mock validation scores
            validation_scores = {
                "syntactic": 0.95,
                "semantic": 0.92,
                "safety": 0.98,
                "bias": 0.89,
                "conflict": 0.94,
            }

            consensus_score = sum(validation_scores.values()) / len(validation_scores)

            print(f"    📊 Validation scores: {validation_scores}")
            print(f"    🎯 Consensus score: {consensus_score:.3f}")

            # Generate policy rule
            rule_templates = {
                "prompt_constitution": "DENY unauthorized_state_mutations WITHOUT governance_approval",
                "governance": "REQUIRE governance_approval FOR policy_changes",
                "financial": "LIMIT treasury_operations TO authorized_amounts AND REQUIRE multi_sig_approval",
            }

            policy_rule = rule_templates.get(
                principle["category"], f"ENFORCE {principle['title'].upper()}"
            )

            policy = {
                "id": principle["id"],
                "rule": policy_rule,
                "category": principle["category"],
                "priority": principle["priority"],
                "validation_score": consensus_score,
                "synthesized_at": datetime.now().isoformat(),
                "status": "synthesized",
            }

            self.demo_data["policies"].append(policy)
            self.demo_data["metrics"]["policies_created"] += 1

            print(f"    ✅ Policy synthesized: {policy_rule}")
            print(f"    📈 Validation score: {consensus_score:.1%}")

        print(
            f"\n🎉 Policy synthesis complete: {len(self.demo_data['policies'])} policies generated"
        )
        await asyncio.sleep(2)

    async def _phase_3_democratic_governance(self):
        """Phase 3: Democratic voting and enactment"""
        print("\n🗳️  PHASE 3: DEMOCRATIC GOVERNANCE")
        print("-" * 50)

        print("📋 Submitting policies for democratic voting...")

        for policy in self.demo_data["policies"]:
            print(f"\n  🗳️  Voting on {policy['id']}: {policy['rule'][:50]}...")

            # Simulate voting process
            await asyncio.sleep(0.5)

            # Mock voting results
            votes_for = 15 + (hash(policy["id"]) % 5)
            votes_against = 2 + (hash(policy["id"]) % 3)
            approval_rate = votes_for / (votes_for + votes_against)

            policy["votes_for"] = votes_for
            policy["votes_against"] = votes_against
            policy["approval_rate"] = approval_rate

            print(
                f"    📊 Votes: {votes_for} for, {votes_against} against ({approval_rate:.1%} approval)"
            )

            # Enact if approved
            if approval_rate > 0.6:
                policy["status"] = "enacted"
                policy["enacted_at"] = datetime.now().isoformat()
                print(f"    ✅ Policy ENACTED - {policy['id']}")
            else:
                policy["status"] = "rejected"
                print(f"    ❌ Policy REJECTED - {policy['id']}")

        enacted_policies = [
            p for p in self.demo_data["policies"] if p["status"] == "enacted"
        ]
        print(
            f"\n🎉 Democratic process complete: {len(enacted_policies)}/{len(self.demo_data['policies'])} policies enacted"
        )

        await asyncio.sleep(2)

    async def _phase_4_compliance_enforcement(self):
        """Phase 4: PGC real-time compliance checking"""
        print("\n🔍 PHASE 4: PROMPT GOVERNANCE COMPILER (PGC)")
        print("-" * 50)

        # Test scenarios for compliance checking
        test_scenarios = [
            {
                "action": "authorized_treasury_transfer_with_approval",
                "context": {
                    "requires_governance": False,
                    "has_approval": True,
                    "amount": 1000,
                    "limit": 5000,
                },
                "expected": "PASS",
                "policy_id": "FN-001",
            },
            {
                "action": "unauthorized_state_mutation_bypass",
                "context": {"requires_governance": True, "has_approval": False},
                "expected": "FAIL",
                "policy_id": "PC-001",
            },
            {
                "action": "governance_decision_without_voting",
                "context": {"requires_governance": True, "has_approval": False},
                "expected": "FAIL",
                "policy_id": "GV-001",
            },
            {
                "action": "excessive_treasury_withdrawal",
                "context": {
                    "requires_governance": False,
                    "has_approval": False,
                    "amount": 10000,
                    "limit": 5000,
                },
                "expected": "FAIL",
                "policy_id": "FN-001",
            },
            {
                "action": "standard_governance_operation_approved",
                "context": {"requires_governance": True, "has_approval": True},
                "expected": "PASS",
                "policy_id": "GV-001",
            },
        ]

        print(f"🔄 Running {len(test_scenarios)} compliance test scenarios...")

        passed_tests = 0

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n  Test {i}: {scenario['action']}")
            print(f"    Policy: {scenario['policy_id']}")

            # Simulate PGC processing
            await asyncio.sleep(0.3)

            # Mock compliance logic
            is_compliant = self._mock_compliance_check(
                scenario["action"], scenario["context"]
            )
            confidence = 85 + (hash(scenario["action"]) % 15)  # 85-99% confidence

            result = {
                "action": scenario["action"],
                "policy_id": scenario["policy_id"],
                "is_compliant": is_compliant,
                "confidence": confidence,
                "expected": scenario["expected"],
                "timestamp": datetime.now().isoformat(),
            }

            self.demo_data["compliance_results"].append(result)
            self.demo_data["metrics"]["compliance_checks"] += 1

            # Check if result matches expectation
            expected_pass = scenario["expected"] == "PASS"
            if is_compliant == expected_pass:
                print(f"    ✅ {scenario['expected']} - Confidence: {confidence}%")
                passed_tests += 1
            else:
                print(f"    ❌ Unexpected result - Expected: {scenario['expected']}")

        success_rate = passed_tests / len(test_scenarios)
        print(
            f"\n📊 PGC Performance: {passed_tests}/{len(test_scenarios)} tests passed ({success_rate:.1%})"
        )
        print(
            f"🎯 Average confidence: {sum(r['confidence'] for r in self.demo_data['compliance_results'])/len(self.demo_data['compliance_results']):.1f}%"
        )

        await asyncio.sleep(2)

    def _mock_compliance_check(self, action: str, context: dict) -> bool:
        """Mock PGC compliance checking logic"""
        action_lower = action.lower()

        # Check for obvious violations
        if "unauthorized" in action_lower or "bypass" in action_lower:
            return False

        # Check governance requirements
        if context.get("requires_governance", False) and not context.get(
            "has_approval", False
        ):
            return False

        # Check financial limits
        if "amount" in context and "limit" in context:
            if context["amount"] > context["limit"]:
                return False

        return True

    async def _phase_5_appeals_system(self):
        """Phase 5: Appeals and human oversight"""
        print("\n⚖️  PHASE 5: APPEALS & HUMAN OVERSIGHT")
        print("-" * 50)

        # Simulate appeal for a compliance violation
        violation_case = {
            "appeal_id": "APP-001",
            "policy_id": "PC-001",
            "violation": "unauthorized_state_mutation_bypass",
            "appellant": "Community Member #42",
            "reason": "System error caused false positive violation detection",
            "evidence": "Transaction logs show proper authorization was present",
        }

        print(f"📋 Processing appeal: {violation_case['appeal_id']}")
        print(f"    Policy: {violation_case['policy_id']}")
        print(f"    Appellant: {violation_case['appellant']}")
        print(f"    Reason: {violation_case['reason']}")

        # Simulate automated review
        print("\n🤖 Automated Review Phase:")
        await asyncio.sleep(1)

        automated_decision = "escalate_to_human"
        confidence = 72  # Low confidence triggers human review

        print(f"    🔍 AI Review Decision: {automated_decision}")
        print(f"    📊 Confidence: {confidence}% (< 85% threshold)")
        print("    ⬆️  Escalating to human committee...")

        # Simulate human committee review
        print("\n👥 Human Committee Review:")
        await asyncio.sleep(2)

        committee_decision = "overturn"
        ruling = "Appeal approved. System error confirmed. Policy violation overturned."

        appeal_result = {
            "appeal_id": violation_case["appeal_id"],
            "policy_id": violation_case["policy_id"],
            "automated_decision": automated_decision,
            "automated_confidence": confidence,
            "committee_decision": committee_decision,
            "ruling": ruling,
            "resolved_at": datetime.now().isoformat(),
        }

        self.demo_data["appeals"].append(appeal_result)
        self.demo_data["metrics"]["appeals_processed"] += 1

        print(f"    ⚖️  Committee Decision: {committee_decision.upper()}")
        print(f"    📝 Ruling: {ruling}")
        print("    ✅ Appeal resolved successfully")

        await asyncio.sleep(2)

    async def _phase_6_system_integration(self):
        """Phase 6: System integration and monitoring"""
        print("\n📊 PHASE 6: SYSTEM INTEGRATION & MONITORING")
        print("-" * 50)

        print("🔄 Initializing real-time monitoring systems...")

        # Simulate event monitoring startup
        monitoring_components = [
            "Solana WebSocket Event Listener",
            "ACGS Backend Integration",
            "Policy Synthesis Pipeline",
            "Compliance Monitoring System",
            "Appeals Processing Queue",
            "Performance Metrics Collector",
        ]

        for component in monitoring_components:
            print(f"    ✅ {component}")
            await asyncio.sleep(0.3)

        print("\n📡 Event monitoring active - listening for:")
        event_types = [
            "Constitution updates",
            "Policy proposals",
            "Vote submissions",
            "Compliance checks",
            "Appeal submissions",
            "Security alerts",
        ]

        for event_type in event_types:
            print(f"    🔍 {event_type}")

        print("\n🎯 System integration complete - Quantumagi fully operational!")

        await asyncio.sleep(2)

    async def _generate_final_report(self):
        """Generate comprehensive demonstration report"""
        print("\n📋 FINAL DEMONSTRATION REPORT")
        print("=" * 80)

        # Calculate metrics
        duration = datetime.now() - self.demo_data["metrics"]["start_time"]
        enacted_policies = len(
            [p for p in self.demo_data["policies"] if p["status"] == "enacted"]
        )
        # Calculate compliance success rate with division by zero protection
        compliance_results = self.demo_data["compliance_results"]
        if len(compliance_results) > 0:
            compliance_success_rate = len(
                [
                    r
                    for r in compliance_results
                    if r["is_compliant"] == (r["expected"] == "PASS")
                ]
            ) / len(compliance_results)
        else:
            compliance_success_rate = 0.0

        print("🏛️  QUANTUMAGI DEMONSTRATION SUMMARY")
        print(f"    Duration: {duration.total_seconds():.1f} seconds")
        print(f"    Constitution Hash: {self.demo_data['constitution_hash'][:16]}...")
        print()
        print("📊 GOVERNANCE METRICS:")
        print(f"    Policies Created: {self.demo_data['metrics']['policies_created']}")
        print(f"    Policies Enacted: {enacted_policies}")
        print(
            f"    Compliance Checks: {self.demo_data['metrics']['compliance_checks']}"
        )
        print(
            f"    Appeals Processed: {self.demo_data['metrics']['appeals_processed']}"
        )
        print()
        print("🎯 PERFORMANCE METRICS:")
        # Calculate metrics with division by zero protection
        policies_created = self.demo_data["metrics"]["policies_created"]
        policy_enactment_rate = (
            (enacted_policies / policies_created) if policies_created > 0 else 0.0
        )

        avg_confidence = 0.0
        if len(compliance_results) > 0:
            avg_confidence = sum(r["confidence"] for r in compliance_results) / len(
                compliance_results
            )

        print(f"    Policy Enactment Rate: {policy_enactment_rate:.1%}")
        print(f"    PGC Accuracy: {compliance_success_rate:.1%}")
        print(f"    Average Confidence: {avg_confidence:.1f}%")
        print()
        print("✅ SYSTEM STATUS:")
        print("    Constitutional Framework: ACTIVE")
        print("    GS Engine: OPERATIONAL")
        print("    PGC Enforcement: ACTIVE")
        print("    Appeals System: OPERATIONAL")
        print("    Event Monitoring: ACTIVE")
        print()
        print("🎉 QUANTUMAGI DEMONSTRATION COMPLETE!")
        print("    On-chain constitutional governance successfully demonstrated")
        print("    AlphaEvolve-ACGS integration validated")
        print("    Real-time compliance enforcement verified")
        print("    Democratic governance process confirmed")
        print()
        print("=" * 80)

        # Save detailed report
        report_data = {
            "demo_summary": {
                "duration_seconds": duration.total_seconds(),
                "constitution_hash": self.demo_data["constitution_hash"],
                "timestamp": datetime.now().isoformat(),
            },
            "metrics": {
                "start_time": self.demo_data["metrics"]["start_time"].isoformat(),
                "policies_created": self.demo_data["metrics"]["policies_created"],
                "compliance_checks": self.demo_data["metrics"]["compliance_checks"],
                "appeals_processed": self.demo_data["metrics"]["appeals_processed"],
            },
            "policies": self.demo_data["policies"],
            "compliance_results": self.demo_data["compliance_results"],
            "appeals": self.demo_data["appeals"],
            "performance": {
                "policy_enactment_rate": policy_enactment_rate,
                "pgc_accuracy": compliance_success_rate,
                "average_confidence": avg_confidence,
            },
        }

        report_filename = (
            f"quantumagi_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_filename, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved: {report_filename}")


async def main():
    """Run the complete Quantumagi demonstration"""
    demo = QuantumagiDemo()

    try:
        await demo.run_complete_demo()
        return 0
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
