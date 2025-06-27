"""
Formal Verification Completion Tests

Comprehensive tests to validate Z3 SMT solver integration completion
and formal verification capabilities for safety-critical applications.
"""

import asyncio
import pytest
import tempfile
import yaml
from pathlib import Path

# Test configuration for 99.92% reliability target
TEST_CONFIG = {
    "reliability_target": 0.9992,
    "verification_timeout": 30,
    "constitutional_compliance_threshold": 0.95,
    "safety_critical_requirements": [
        "consistency",
        "completeness", 
        "constitutional_compliance",
        "formal_correctness"
    ]
}

class TestFormalVerificationCompletion:
    """Test suite for formal verification completion validation."""
    
    @pytest.fixture
    def sample_policy(self):
        """Provide sample policy for testing."""
        return """
        package acgs.access_control
        
        default allow = false
        
        allow {
            input.role == "admin"
            input.action == "read"
        }
        
        allow {
            input.role == "user"
            input.action == "read"
            input.resource != "sensitive"
        }
        """
    
    @pytest.fixture
    def constitutional_principles(self):
        """Provide constitutional principles for testing."""
        return {
            "constitutional_principles": {
                "transparency": {
                    "description": "All decisions must be transparent and auditable",
                    "requirements": [
                        "audit_trail_enabled",
                        "decision_logging"
                    ],
                    "enforcement": "strict"
                },
                "fairness": {
                    "description": "Fair treatment of all stakeholders",
                    "requirements": [
                        {
                            "condition": {
                                "type": "threshold",
                                "metric": "fairness_score",
                                "value": 0.85
                            }
                        }
                    ],
                    "enforcement": "moderate"
                },
                "security": {
                    "description": "Security properties must be preserved",
                    "requirements": [
                        "access_control_enabled",
                        "encryption_required"
                    ],
                    "enforcement": "strict"
                }
            },
            "governance_requirements": {
                "democratic_oversight": {
                    "description": "Democratic oversight mechanisms",
                    "threshold": 0.8
                }
            }
        }
    
    async def test_z3_solver_integration(self):
        """Test Z3 SMT solver integration and basic functionality."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

            try:
                from fv_service.app.core.smt_solver_integration import Z3SMTSolverClient
            except ImportError:
                # Fallback for direct execution
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
                from services.core.formal_verification.fv_service.app.core.smt_solver_integration import Z3SMTSolverClient

            solver_client = Z3SMTSolverClient()

            # Validate solver initialization
            assert solver_client.solver is not None
            assert solver_client.policy_compiler is not None
            assert hasattr(solver_client, 'constitutional_constraints')
            assert hasattr(solver_client, 'formal_properties')

        except ImportError as e:
            pytest.fail(f"Z3 SMT solver integration import failed: {e}")
        except Exception as e:
            pytest.fail(f"Z3 solver initialization failed: {e}")
    
    async def test_policy_smt_compiler(self, sample_policy):
        """Test policy-to-SMT compiler functionality."""
        try:
            from ..fv_service.app.core.policy_smt_compiler import PolicySMTCompiler
            
            compiler = PolicySMTCompiler()
            
            # Test policy compilation
            constraints = compiler.compile_governance_policy(sample_policy, "test_policy")
            
            assert len(constraints) > 0, "Policy compilation should generate constraints"
            
            # Test constraint properties
            for constraint in constraints:
                assert hasattr(constraint, 'constraint')
                assert hasattr(constraint, 'source_policy')
                assert hasattr(constraint, 'policy_type')
                assert constraint.source_policy == "test_policy"
            
            # Test compilation summary
            summary = compiler.get_compilation_summary()
            assert "total_variables" in summary
            assert "total_constraints" in summary
            assert summary["constitutional_hash"] == "cdd01ef066bc6cf2"
            
        except Exception as e:
            pytest.fail(f"Policy-to-SMT compiler test failed: {e}")
    
    async def test_constitutional_principles_compilation(self, constitutional_principles):
        """Test constitutional principles compilation to SMT."""
        try:
            from ..fv_service.app.core.policy_smt_compiler import PolicySMTCompiler
            
            compiler = PolicySMTCompiler()
            
            # Create temporary principles file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(constitutional_principles, f)
                principles_file = f.name
            
            try:
                # Test constitutional principles compilation
                constraints = compiler.compile_constitutional_principles(principles_file)
                
                assert len(constraints) > 0, "Constitutional principles should generate constraints"
                
                # Verify constitutional principle constraints
                constitutional_constraints = [
                    c for c in constraints 
                    if c.policy_type.value == "constitutional_principle"
                ]
                assert len(constitutional_constraints) > 0, "Should have constitutional constraints"
                
                # Check for high-priority constraints (strict enforcement)
                strict_constraints = [c for c in constraints if c.priority >= 5]
                assert len(strict_constraints) > 0, "Should have strict enforcement constraints"
                
            finally:
                Path(principles_file).unlink()  # Clean up temp file
                
        except Exception as e:
            pytest.fail(f"Constitutional principles compilation test failed: {e}")
    
    async def test_enhanced_policy_verification(self, sample_policy, constitutional_principles):
        """Test enhanced policy verification with constitutional compliance."""
        try:
            from ..fv_service.app.core.smt_solver_integration import Z3SMTSolverClient
            
            solver_client = Z3SMTSolverClient()
            
            # Create temporary principles file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(constitutional_principles, f)
                principles_file = f.name
            
            try:
                # Test enhanced verification
                result = await solver_client.verify_policy_compliance(
                    sample_policy, "test_policy", principles_file
                )
                
                # Validate verification result structure
                assert "policy_id" in result
                assert "verification_status" in result
                assert "constitutional_compliance" in result
                assert "formal_properties_verified" in result
                assert "constraint_summary" in result
                assert "recommendations" in result
                
                # Check constitutional compliance
                compliance = result["constitutional_compliance"]
                assert "overall_compliant" in compliance
                assert "compliance_score" in compliance
                
                # Check formal properties verification
                properties = result["formal_properties_verified"]
                assert "verification_score" in properties
                
                # Validate constraint summary
                summary = result["constraint_summary"]
                assert "total_variables" in summary
                assert "total_constraints" in summary
                
            finally:
                Path(principles_file).unlink()
                
        except Exception as e:
            pytest.fail(f"Enhanced policy verification test failed: {e}")
    
    async def test_formal_properties_generation(self):
        """Test formal properties generation for correctness and completeness."""
        try:
            from ..fv_service.app.core.policy_smt_compiler import PolicySMTCompiler, PolicyType
            
            compiler = PolicySMTCompiler()
            
            # Add some test constraints
            test_policy = "allow { input.role == 'admin' }"
            compiler.compile_governance_policy(test_policy, "test_policy")
            
            # Generate formal properties
            properties = compiler.generate_formal_properties()
            
            assert len(properties) > 0, "Should generate formal properties"
            
            # Check for consistency and completeness properties
            property_types = [p.source_policy for p in properties]
            assert any("consistency" in pt for pt in property_types), "Should have consistency property"
            assert any("completeness" in pt for pt in property_types), "Should have completeness property"
            
        except Exception as e:
            pytest.fail(f"Formal properties generation test failed: {e}")
    
    async def test_reliability_target_achievement(self, sample_policy, constitutional_principles):
        """Test that formal verification achieves 99.92% reliability target."""
        try:
            from ..fv_service.app.core.smt_solver_integration import Z3SMTSolverClient
            
            solver_client = Z3SMTSolverClient()
            
            # Create temporary principles file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(constitutional_principles, f)
                principles_file = f.name
            
            try:
                # Run multiple verification tests to measure reliability
                verification_count = 100  # Sample size for reliability testing
                successful_verifications = 0
                
                for i in range(verification_count):
                    try:
                        result = await solver_client.verify_policy_compliance(
                            sample_policy, f"test_policy_{i}", principles_file
                        )
                        
                        # Count as successful if verification completed without error
                        if "error_message" not in result:
                            successful_verifications += 1
                            
                    except Exception:
                        # Verification failure
                        pass
                
                # Calculate reliability
                reliability = successful_verifications / verification_count
                
                assert reliability >= TEST_CONFIG["reliability_target"], \
                    f"Reliability {reliability:.4f} below target {TEST_CONFIG['reliability_target']:.4f}"
                
                print(f"Formal verification reliability: {reliability:.4f} (target: {TEST_CONFIG['reliability_target']:.4f})")
                
            finally:
                Path(principles_file).unlink()
                
        except Exception as e:
            pytest.fail(f"Reliability target test failed: {e}")
    
    async def test_safety_critical_requirements(self, constitutional_principles):
        """Test safety-critical application requirements."""
        try:
            from ..fv_service.app.core.policy_smt_compiler import PolicySMTCompiler
            
            compiler = PolicySMTCompiler()
            
            # Create temporary principles file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(constitutional_principles, f)
                principles_file = f.name
            
            try:
                # Compile constitutional principles
                constraints = compiler.compile_constitutional_principles(principles_file)
                
                # Check safety-critical requirements
                safety_requirements_met = {
                    "consistency": False,
                    "completeness": False,
                    "constitutional_compliance": False,
                    "formal_correctness": False
                }
                
                # Check for consistency constraints
                consistency_constraints = [
                    c for c in constraints 
                    if "consistency" in c.source_policy.lower()
                ]
                if consistency_constraints:
                    safety_requirements_met["consistency"] = True
                
                # Check for constitutional compliance
                constitutional_constraints = [
                    c for c in constraints 
                    if c.policy_type.value == "constitutional_principle"
                ]
                if constitutional_constraints:
                    safety_requirements_met["constitutional_compliance"] = True
                
                # Check for completeness (all principles covered)
                principles_covered = set()
                for constraint in constitutional_constraints:
                    if "transparency" in constraint.source_policy:
                        principles_covered.add("transparency")
                    elif "fairness" in constraint.source_policy:
                        principles_covered.add("fairness")
                    elif "security" in constraint.source_policy:
                        principles_covered.add("security")
                
                if len(principles_covered) >= 3:  # All main principles covered
                    safety_requirements_met["completeness"] = True
                
                # Check for formal correctness (high-priority constraints)
                high_priority_constraints = [c for c in constraints if c.priority >= 4]
                if high_priority_constraints:
                    safety_requirements_met["formal_correctness"] = True
                
                # Validate all safety requirements are met
                for requirement, met in safety_requirements_met.items():
                    assert met, f"Safety-critical requirement '{requirement}' not met"
                
                print(f"All safety-critical requirements met: {safety_requirements_met}")
                
            finally:
                Path(principles_file).unlink()
                
        except Exception as e:
            pytest.fail(f"Safety-critical requirements test failed: {e}")


async def run_formal_verification_tests():
    """Run all formal verification completion tests."""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    test_suite = TestFormalVerificationCompletion()
    
    tests = [
        ("Z3 Solver Integration", test_suite.test_z3_solver_integration()),
        ("Policy SMT Compiler", test_suite.test_policy_smt_compiler({})),
        ("Constitutional Principles Compilation", test_suite.test_constitutional_principles_compilation({})),
        ("Enhanced Policy Verification", test_suite.test_enhanced_policy_verification({}, {})),
        ("Formal Properties Generation", test_suite.test_formal_properties_generation()),
        ("Reliability Target Achievement", test_suite.test_reliability_target_achievement({}, {})),
        ("Safety Critical Requirements", test_suite.test_safety_critical_requirements({}))
    ]
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    for test_name, test_coro in tests:
        try:
            logger.info(f"Running test: {test_name}")
            await test_coro
            results["passed"] += 1
            logger.info(f"✅ {test_name} PASSED")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{test_name}: {str(e)}")
            logger.error(f"❌ {test_name} FAILED: {e}")
    
    # Print summary
    total_tests = results["passed"] + results["failed"]
    success_rate = results["passed"] / total_tests if total_tests > 0 else 0
    reliability_achieved = success_rate >= TEST_CONFIG["reliability_target"]
    
    print(f"\n{'='*70}")
    print(f"FORMAL VERIFICATION COMPLETION TEST RESULTS")
    print(f"{'='*70}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {success_rate:.4f}")
    print(f"Reliability Target: {TEST_CONFIG['reliability_target']:.4f}")
    print(f"Target Achieved: {'✅ YES' if reliability_achieved else '❌ NO'}")
    
    if results["errors"]:
        print(f"\nErrors:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    print(f"{'='*70}")
    
    return reliability_achieved


if __name__ == "__main__":
    success = asyncio.run(run_formal_verification_tests())
    exit(0 if success else 1)
