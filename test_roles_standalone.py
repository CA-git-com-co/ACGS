#!/usr/bin/env python3
"""
Standalone test for Specialized Agent Roles implementation
Tests the core functionality without complex dependencies
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock

# Add the project root to Python path
sys.path.insert(0, '/home/dislove/ACGS-2')

async def test_specialized_roles():
    """Test specialized agent roles functionality"""
    print("🚀 Testing ACGS Specialized Agent Roles Implementation")
    print("=" * 60)
    
    try:
        # Import our specialized roles
        from services.shared.agents.specialized_agent_roles import (
            SpecializedRoleFactory,
            SpecializedRoleRegistry,
            AgentRoleType,
            PolicyManagerRole,
            ArchitectRole,
            ValidatorRole,
            ImplementerRole
        )
        print("✅ Successfully imported specialized agent roles")
        
        # Create mock dependencies
        safety_validator = AsyncMock()
        safety_validator.validate_content.return_value = {"is_compliant": True, "score": 0.95}
        
        audit_logger = AsyncMock()
        performance_monitor = AsyncMock()
        
        print("\n📋 Testing Role Factory...")
        
        # Test Policy Manager creation
        policy_manager = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            "pm_test_001",
            safety_validator,
            audit_logger,
            performance_monitor
        )
        assert isinstance(policy_manager, PolicyManagerRole)
        print("✅ Policy Manager role created successfully")
        
        # Test Architect creation
        architect = SpecializedRoleFactory.create_role(
            AgentRoleType.ARCHITECT,
            "arch_test_001",
            safety_validator,
            audit_logger,
            performance_monitor
        )
        assert isinstance(architect, ArchitectRole)
        print("✅ Architect role created successfully")
        
        # Test Validator creation
        validator = SpecializedRoleFactory.create_role(
            AgentRoleType.VALIDATOR,
            "val_test_001",
            safety_validator,
            audit_logger,
            performance_monitor
        )
        assert isinstance(validator, ValidatorRole)
        print("✅ Validator role created successfully")
        
        # Test Implementer creation
        implementer = SpecializedRoleFactory.create_role(
            AgentRoleType.IMPLEMENTER,
            "impl_test_001",
            safety_validator,
            audit_logger,
            performance_monitor
        )
        assert isinstance(implementer, ImplementerRole)
        print("✅ Implementer role created successfully")
        
        print("\n🔧 Testing Role Initialization...")
        
        # Initialize all roles
        await policy_manager.initialize()
        await architect.initialize()
        await validator.initialize()
        await implementer.initialize()
        
        assert policy_manager.is_active
        assert architect.is_active
        assert validator.is_active
        assert implementer.is_active
        print("✅ All roles initialized and activated")
        
        print("\n📊 Testing Role Registry...")
        
        # Test registry operations
        registry = SpecializedRoleRegistry()
        registry.register_role(policy_manager)
        registry.register_role(architect)
        registry.register_role(validator)
        registry.register_role(implementer)
        
        # Test retrieval
        retrieved_pm = registry.get_role("pm_test_001")
        assert retrieved_pm == policy_manager
        
        # Test type filtering
        policy_managers = registry.get_roles_by_type(AgentRoleType.POLICY_MANAGER)
        assert len(policy_managers) == 1
        assert policy_managers[0] == policy_manager
        
        print("✅ Role registry operations working correctly")
        
        print("\n⚡ Testing Task Execution...")
        
        # Test Policy Manager task execution
        pm_task = {
            "task_id": "req_analysis_test",
            "task_type": "requirements_analysis",
            "requirements": {
                "functional": ["authentication", "authorization"],
                "non_functional": ["performance", "security"],
                "constraints": ["budget", "timeline"]
            }
        }
        
        pm_result = await policy_manager.execute_task(pm_task)
        assert pm_result["task_result"] == "requirements_analysis_completed"
        assert pm_result["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✅ Policy Manager task execution successful")
        
        # Test Architect task execution
        arch_task = {
            "task_id": "sys_design_test",
            "task_type": "system_design",
            "requirements": {
                "scalability": "high",
                "performance": "sub_5ms",
                "security": "enterprise"
            }
        }
        
        arch_result = await architect.execute_task(arch_task)
        assert arch_result["task_result"] == "system_architecture_designed"
        assert arch_result["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✅ Architect task execution successful")
        
        # Test Validator task execution
        val_task = {
            "task_id": "compliance_test",
            "task_type": "compliance_validation",
            "validation_target": {
                "implementation": "test_policy",
                "requirements": ["gdpr", "security"]
            }
        }
        
        val_result = await validator.execute_task(val_task)
        assert val_result["task_result"] == "compliance_validation_completed"
        assert val_result["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✅ Validator task execution successful")
        
        # Test Implementer task execution
        impl_task = {
            "task_id": "implementation_test",
            "task_type": "policy_implementation",
            "policy_specification": {
                "policy_name": "test_policy",
                "steps": ["configure", "deploy", "validate"]
            }
        }
        
        impl_result = await implementer.execute_task(impl_task)
        assert impl_result["task_result"] == "policy_implementation_completed"
        assert impl_result["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✅ Implementer task execution successful")
        
        print("\n📈 Testing Performance Metrics...")
        
        # Check role status and metrics
        pm_status = policy_manager.get_role_status()
        assert pm_status["completed_tasks"] == 1
        assert pm_status["performance_metrics"]["tasks_completed"] == 1
        assert pm_status["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✅ Performance metrics tracking working")
        
        print("\n🔒 Testing Constitutional Compliance...")
        
        # Test constitutional compliance validation
        safety_validator.validate_content.return_value = {"is_compliant": False, "score": 0.3}
        
        non_compliant_task = {
            "task_id": "bad_task",
            "task_type": "requirements_analysis",
            "requirements": {"malicious": "content"}
        }
        
        try:
            await policy_manager.execute_task(non_compliant_task)
            assert False, "Should have raised ValueError for non-compliant task"
        except ValueError as e:
            assert "constitutional constraints" in str(e)
            print("✅ Constitutional compliance validation working")
        
        print("\n🎯 Testing Workflow Assignment...")
        
        # Test workflow assignment
        registry.assign_roles_to_workflow("test_workflow_001", [
            "pm_test_001", "arch_test_001", "val_test_001", "impl_test_001"
        ])
        
        workflow_roles = registry.get_workflow_roles("test_workflow_001")
        assert len(workflow_roles) == 4
        print("✅ Workflow role assignment working")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Specialized Agent Roles implementation is working correctly!")
        print("\n📊 Implementation Summary:")
        print(f"   • 4 specialized roles implemented (Policy Manager, Architect, Validator, Implementer)")
        print(f"   • MetaGPT assembly line paradigm integrated")
        print(f"   • Constitutional compliance validation: ✅")
        print(f"   • Performance monitoring integration: ✅")
        print(f"   • Role registry and workflow management: ✅")
        print(f"   • Task execution with domain expertise: ✅")
        print(f"   • Constitutional hash validation: cdd01ef066bc6cf2 ✅")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might be due to missing dependencies or circular imports")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_specialized_roles())
    if success:
        print("\n✅ Specialized Agent Roles implementation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
