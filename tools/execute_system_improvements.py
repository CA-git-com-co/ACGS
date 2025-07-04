#!/usr/bin/env python3
"""
ACGS-1 System Improvements Execution Script
Executes all system improvements in the correct order to achieve target metrics
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemImprovementExecutor:
    """Executes all ACGS-1 system improvements"""
    
    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.scripts_dir = self.project_root / "scripts"
        self.execution_log = []
        
    async def execute_all_improvements(self):
        """Execute all system improvements in order"""
        logger.info("🚀 Starting ACGS-1 System Improvements Execution")
        
        start_time = datetime.now()
        
        execution_plan = [
            {
                "name": "OPA DNS Resolution Fix",
                "script": "fix_opa_dns_resolution.py",
                "description": "Fix PGC service OPA dependency issues",
                "priority": "critical"
            },
            {
                "name": "Secondary Service Instances Fix",
                "script": "fix_secondary_service_instances.py", 
                "description": "Fix health check failures for backup instances",
                "priority": "high"
            },
            {
                "name": "Cache Performance Enhancement",
                "script": "enhance_cache_performance.py",
                "description": "Improve cache hit rate from 1.0% to 85%+",
                "priority": "high"
            },
            {
                "name": "Concurrent Capacity Enhancement",
                "script": "enhance_concurrent_capacity.py",
                "description": "Increase capacity from 966 to 1000+ users",
                "priority": "high"
            },
            {
                "name": "Throughput Enhancement",
                "script": "enhance_throughput_performance.py",
                "description": "Increase throughput from 1505 to 2000+ RPS",
                "priority": "high"
            },
            {
                "name": "Access Control Enhancement",
                "script": "enhance_access_control.py",
                "description": "Improve Access Control score from 5.4 to 8.0+",
                "priority": "medium"
            },
            {
                "name": "Frontend Integration Enhancement",
                "script": "enhance_frontend_integration.py",
                "description": "Complete blockchain-frontend integration",
                "priority": "medium"
            },
            {
                "name": "Comprehensive System Validation",
                "script": "comprehensive_system_validation.py",
                "description": "Validate all improvements and measure targets",
                "priority": "validation"
            }
        ]
        
        results = {
            "execution_start": start_time.isoformat(),
            "execution_plan": execution_plan,
            "execution_results": [],
            "overall_success": False,
            "targets_achieved": {},
            "execution_duration": 0
        }
        
        # Execute each improvement
        for step in execution_plan:
<<<<<<< HEAD
            logger.info(f"\\n{'='*60}")
=======
            logger.info(f"\n{'='*60}")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
            logger.info(f"🔧 Executing: {step['name']}")
            logger.info(f"📝 Description: {step['description']}")
            logger.info(f"⚡ Priority: {step['priority'].upper()}")
            logger.info(f"{'='*60}")
            
            step_result = await self.execute_improvement_step(step)
            results["execution_results"].append(step_result)
            
            # Log step completion
            status = "✅ SUCCESS" if step_result["success"] else "❌ FAILED"
            logger.info(f"{status}: {step['name']} completed in {step_result['duration']:.1f}s")
            
            if not step_result["success"] and step["priority"] == "critical":
                logger.error(f"❌ Critical step failed: {step['name']}")
                logger.error("🛑 Stopping execution due to critical failure")
                break
            
            # Brief pause between steps
            await asyncio.sleep(2)
        
        # Calculate overall results
        end_time = datetime.now()
        results["execution_end"] = end_time.isoformat()
        results["execution_duration"] = (end_time - start_time).total_seconds()
        
        successful_steps = sum(1 for result in results["execution_results"] if result["success"])
        total_steps = len(results["execution_results"])
        results["overall_success"] = successful_steps == total_steps
        
        # Extract target achievements from validation step
        validation_result = next(
            (result for result in results["execution_results"] 
             if result["step_name"] == "Comprehensive System Validation"),
            None
        )
        
        if validation_result and validation_result["success"]:
            try:
                validation_data = json.loads(validation_result.get("output", "{}"))
                results["targets_achieved"] = validation_data.get("targets_achieved", {})
            except Exception as e:
                logger.warning(f"⚠️ Could not parse validation results: {e}")
        
        # Save execution results
        with open("system_improvements_execution_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Print final summary
        self.print_execution_summary(results)
        
        return results
    
    async def execute_improvement_step(self, step):
        """Execute a single improvement step"""
        step_start = time.time()
        
        step_result = {
            "step_name": step["name"],
            "script": step["script"],
            "priority": step["priority"],
            "success": False,
            "duration": 0,
            "output": "",
            "error": ""
        }
        
        try:
            script_path = self.scripts_dir / step["script"]
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Make script executable
            subprocess.run(["chmod", "+x", str(script_path)], check=True)
            
            # Execute the script
            logger.info(f"▶️ Running: python {script_path}")
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            step_result["output"] = stdout.decode() if stdout else ""
            step_result["error"] = stderr.decode() if stderr else ""
            step_result["success"] = process.returncode == 0
            
            if step_result["success"]:
                logger.info(f"✅ {step['name']} completed successfully")
            else:
                logger.error(f"❌ {step['name']} failed with return code {process.returncode}")
                if step_result["error"]:
                    logger.error(f"Error output: {step_result['error']}")
            
        except Exception as e:
            step_result["error"] = str(e)
            logger.error(f"❌ {step['name']} failed with exception: {e}")
        
        step_result["duration"] = time.time() - step_start
        return step_result
    
    def print_execution_summary(self, results):
        """Print execution summary"""
<<<<<<< HEAD
        print("\\n" + "="*80)
=======
        print("\n" + "="*80)
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        print("🎯 ACGS-1 SYSTEM IMPROVEMENTS EXECUTION SUMMARY")
        print("="*80)
        
        print(f"Execution Duration: {results['execution_duration']:.1f} seconds")
        print(f"Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}")
        
        # Step results
<<<<<<< HEAD
        print(f"\\nStep Results ({len(results['execution_results'])}):") 
=======
        print(f"\nStep Results ({len(results['execution_results'])}):")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        for result in results["execution_results"]:
            status = "✅" if result["success"] else "❌"
            duration = f"{result['duration']:.1f}s"
            print(f"  {status} {result['step_name']} ({duration})")
        
        # Target achievements
        if results.get("targets_achieved"):
<<<<<<< HEAD
            print(f"\\nTarget Achievements:")
=======
            print(f"\nTarget Achievements:")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
            for target, achieved in results["targets_achieved"].items():
                status = "✅" if achieved else "❌"
                print(f"  {status} {target.replace('_', ' ').title()}")
        
        # Success metrics
        successful_steps = sum(1 for result in results["execution_results"] if result["success"])
        total_steps = len(results["execution_results"])
        success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
        
<<<<<<< HEAD
        print(f"\\nExecution Metrics:")
=======
        print(f"\nExecution Metrics:")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        print(f"  Success Rate: {success_rate:.1f}% ({successful_steps}/{total_steps})")
        print(f"  Critical Steps: {'✅ PASSED' if successful_steps >= total_steps - 1 else '❌ FAILED'}")
        
        # Next steps
        if not results["overall_success"]:
<<<<<<< HEAD
            print(f"\\n⚠️ Next Steps:")
=======
            print(f"\n⚠️ Next Steps:")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
            print(f"  1. Review failed steps in execution log")
            print(f"  2. Address any critical issues")
            print(f"  3. Re-run specific improvement scripts as needed")
            print(f"  4. Run comprehensive validation again")
        else:
<<<<<<< HEAD
            print(f"\\n🎉 All improvements completed successfully!")
=======
            print(f"\n🎉 All improvements completed successfully!")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
            print(f"  System is ready for production deployment")
        
        print("="*80)

async def main():
    """Main execution function"""
    executor = SystemImprovementExecutor()
    
    print("🚀 ACGS-1 System Improvements Execution")
    print("This will execute all system improvements to achieve target metrics:")
    print("  - >99.9% availability")
    print("  - <500ms response times") 
    print("  - >85% cache hit rate")
    print("  - >1000 concurrent users")
    print("  - >2000 RPS throughput")
    print("  - <1% error rate")
    print("  - >8.0/10 access control score")
    print("  - >90% E2E validation score")
    
    # Confirm execution
    try:
<<<<<<< HEAD
        confirm = input("\\nProceed with execution? (y/N): ").strip().lower()
=======
        confirm = input("\nProceed with execution? (y/N): ").strip().lower()
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        if confirm != 'y':
            print("Execution cancelled.")
            return
    except KeyboardInterrupt:
<<<<<<< HEAD
        print("\\nExecution cancelled.")
=======
        print("\nExecution cancelled.")
>>>>>>> 7e8c70b4dbb97f17773bac3ac6b95fa8f0905aa4
        return
    
    # Execute improvements
    results = await executor.execute_all_improvements()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
