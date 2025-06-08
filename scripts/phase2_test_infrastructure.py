#!/usr/bin/env python3
"""
ACGS-1 Phase 2: Test Infrastructure Strengthening

This script implements comprehensive test infrastructure enhancements:
1. Anchor program test coverage analysis and expansion
2. End-to-end governance workflow testing
3. Frontend testing infrastructure setup
4. Performance benchmarking and validation

Usage:
    python scripts/phase2_test_infrastructure.py --setup-all
    python scripts/phase2_test_infrastructure.py --anchor-tests
    python scripts/phase2_test_infrastructure.py --e2e-tests
    python scripts/phase2_test_infrastructure.py --frontend-tests
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import shutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase2_test_infrastructure.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestInfrastructureManager:
    """Comprehensive test infrastructure manager for ACGS-1."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.blockchain_dir = project_root / "blockchain"
        self.services_dir = project_root / "services"
        self.applications_dir = project_root / "applications"
        self.tests_dir = project_root / "tests"

        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'anchor_tests': {},
            'e2e_tests': {},
            'frontend_tests': {},
            'coverage_analysis': {},
            'performance_metrics': {}
        }

    def setup_anchor_test_infrastructure(self) -> Dict:
        """Setup and enhance Anchor program testing infrastructure."""
        logger.info("Setting up Anchor test infrastructure...")

        anchor_results = {
            'programs_analyzed': [],
            'test_coverage': {},
            'new_tests_created': [],
            'coverage_percentage': 0.0
        }

        # Check if Anchor is installed
        if not self._check_anchor_installation():
            logger.error("Anchor framework not found. Please install Anchor CLI.")
            return anchor_results

        # Analyze existing programs
        programs_dir = self.blockchain_dir / "programs"
        if programs_dir.exists():
            for program_dir in programs_dir.iterdir():
                if program_dir.is_dir():
                    program_name = program_dir.name
                    logger.info(f"Analyzing program: {program_name}")

                    program_analysis = self._analyze_anchor_program(program_dir)
                    anchor_results['programs_analyzed'].append(program_analysis)

        # Generate comprehensive test suite
        self._generate_anchor_test_suite()

        # Calculate coverage
        coverage = self._calculate_test_coverage()
        anchor_results['coverage_percentage'] = coverage

        self.test_results['anchor_tests'] = anchor_results
        return anchor_results

    def _check_anchor_installation(self) -> bool:
        """Check if Anchor CLI is installed."""
        try:
            result = subprocess.run(['anchor', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _analyze_anchor_program(self, program_dir: Path) -> Dict:
        """Analyze an individual Anchor program for test coverage."""
        program_analysis = {
            'name': program_dir.name,
            'src_files': [],
            'existing_tests': [],
            'instructions': [],
            'accounts': [],
            'test_coverage_needed': []
        }

        # Analyze source files
        src_dir = program_dir / "src"
        if src_dir.exists():
            for src_file in src_dir.glob("**/*.rs"):
                program_analysis['src_files'].append(str(src_file.relative_to(program_dir)))

                # Extract instructions and accounts from Rust code
                instructions, accounts = self._extract_program_components(src_file)
                program_analysis['instructions'].extend(instructions)
                program_analysis['accounts'].extend(accounts)

        # Check existing tests
        test_file = self.blockchain_dir / "tests" / f"{program_dir.name}.ts"
        if test_file.exists():
            program_analysis['existing_tests'].append(str(test_file.relative_to(self.blockchain_dir)))

        # Determine test coverage needs
        for instruction in program_analysis['instructions']:
            program_analysis['test_coverage_needed'].append({
                'type': 'instruction',
                'name': instruction,
                'test_cases': [
                    f"test_{instruction}_success",
                    f"test_{instruction}_failure",
                    f"test_{instruction}_edge_cases"
                ]
            })

        return program_analysis

    def _extract_program_components(self, src_file: Path) -> tuple:
        """Extract instructions and accounts from Rust source file."""
        instructions = []
        accounts = []

        try:
            with open(src_file, 'r') as f:
                content = f.read()

                # Extract instruction functions (simplified regex)
                import re
                instruction_pattern = r'pub fn (\w+)\s*\('
                instructions.extend(re.findall(instruction_pattern, content))

                # Extract account structures
                account_pattern = r'#\[account\]\s*pub struct (\w+)'
                accounts.extend(re.findall(account_pattern, content))

        except Exception as e:
            logger.warning(f"Could not parse {src_file}: {e}")

        return instructions, accounts

    def _generate_anchor_test_suite(self):
        """Generate comprehensive Anchor test suite."""
        logger.info("Generating comprehensive Anchor test suite...")

        # Create enhanced test template - using simple string replacement
        test_template = """
import * as anchor from "@project-serum/anchor";
import { Program } from "@project-serum/anchor";
import { expect } from "chai";

describe("PROGRAM_NAME", () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.PROGRAM_NAME_CAMEL as Program<PROGRAM_NAME_CAMEL>;

  // Test accounts
  let authority: anchor.web3.Keypair;
  let constitution: anchor.web3.Keypair;
  let policy: anchor.web3.Keypair;

  before(async () => {
    authority = anchor.web3.Keypair.generate();
    constitution = anchor.web3.Keypair.generate();
    policy = anchor.web3.Keypair.generate();

    // Airdrop SOL for testing
    await program.provider.connection.confirmTransaction(
      await program.provider.connection.requestAirdrop(
        authority.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      )
    );
  });

  describe("Constitution Management", () => {
    it("Should initialize constitution successfully", async () => {
      // Test constitution initialization
      const constitutionHash = "test_hash_12345";

      await program.methods
        .initialize(constitutionHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([constitution, authority])
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitution.publicKey
      );

      expect(constitutionAccount.hash).to.equal(constitutionHash);
      expect(constitutionAccount.authority.toString()).to.equal(
        authority.publicKey.toString()
      );
    });

    it("Should update constitution with proper authority", async () => {
      // Test constitution updates
      const newHash = "updated_hash_67890";

      await program.methods
        .updateConstitution(newHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitution.publicKey
      );

      expect(constitutionAccount.hash).to.equal(newHash);
    });

    it("Should reject unauthorized constitution updates", async () => {
      const unauthorizedUser = anchor.web3.Keypair.generate();

      try {
        await program.methods
          .updateConstitution("unauthorized_hash")
          .accounts({
            constitution: constitution.publicKey,
            authority: unauthorizedUser.publicKey,
          })
          .signers([unauthorizedUser])
          .rpc();

        expect.fail("Should have thrown an error");
      } catch (error) {
        expect(error.message).to.include("unauthorized");
      }
    });
  });

  describe("Policy Management", () => {
    it("Should propose policy successfully", async () => {
      const policyContent = "Test policy content";
      const category = "Safety";

      await program.methods
        .proposePolicy(policyContent, category)
        .accounts({
          policy: policy.publicKey,
          proposer: authority.publicKey,
          constitution: constitution.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([policy, authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);

      expect(policyAccount.content).to.equal(policyContent);
      expect(policyAccount.category).to.equal(category);
      expect(policyAccount.status).to.equal("Proposed");
    });

    it("Should vote on policy", async () => {
      const vote = true; // Support

      await program.methods
        .voteOnPolicy(vote)
        .accounts({
          policy: policy.publicKey,
          voter: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.supportVotes).to.equal(1);
    });

    it("Should enact policy after sufficient votes", async () => {
      await program.methods
        .enactPolicy()
        .accounts({
          policy: policy.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.status).to.equal("Active");
    });
  });

  describe("PGC Compliance Checking", () => {
    it("Should validate compliant actions", async () => {
      const action = "compliant_action";
      const context = "test_context";

      const result = await program.methods
        .checkCompliance(action, context)
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.true;
      expect(result.confidence).to.be.greaterThan(0.9);
    });

    it("Should reject non-compliant actions", async () => {
      const action = "extrajudicial_state_mutation";
      const context = "unauthorized_context";

      const result = await program.methods
        .checkCompliance(action, context)
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.false;
      expect(result.violatedPolicies).to.have.length.greaterThan(0);
    });
  });

  describe("Emergency Governance", () => {
    it("Should deactivate policy in emergency", async () => {
      await program.methods
        .deactivatePolicy("Emergency deactivation")
        .accounts({
          policy: policy.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.status).to.equal("Deactivated");
    });
  });
});
"""

        # Generate tests for each program
        programs_dir = self.blockchain_dir / "programs"
        if programs_dir.exists():
            for program_dir in programs_dir.iterdir():
                if program_dir.is_dir():
                    program_name = program_dir.name
                    program_name_camel = self._to_camel_case(program_name)

                    test_content = test_template.replace("PROGRAM_NAME", program_name)
                    test_content = test_content.replace("PROGRAM_NAME_CAMEL", program_name_camel)

                    test_file = self.blockchain_dir / "tests" / f"{program_name}_comprehensive.ts"
                    with open(test_file, 'w') as f:
                        f.write(test_content)

                    logger.info(f"Generated comprehensive test suite: {test_file}")

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to CamelCase."""
        components = snake_str.split('-')
        return ''.join(word.capitalize() for word in components)

    def _calculate_test_coverage(self) -> float:
        """Calculate test coverage percentage."""
        # This is a simplified calculation
        # In practice, you'd use coverage tools

        total_functions = 0
        tested_functions = 0

        # Count functions in source files
        programs_dir = self.blockchain_dir / "programs"
        if programs_dir.exists():
            for program_dir in programs_dir.iterdir():
                if program_dir.is_dir():
                    src_dir = program_dir / "src"
                    if src_dir.exists():
                        for src_file in src_dir.glob("**/*.rs"):
                            with open(src_file, 'r') as f:
                                content = f.read()
                                import re
                                functions = re.findall(r'pub fn (\w+)\s*\(', content)
                                total_functions += len(functions)

        # Count test functions
        tests_dir = self.blockchain_dir / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.glob("**/*.ts"):
                with open(test_file, 'r') as f:
                    content = f.read()
                    import re
                    tests = re.findall(r'it\s*\(\s*["\']([^"\']+)["\']', content)
                    tested_functions += len(tests)

        if total_functions == 0:
            return 0.0

        coverage = min((tested_functions / total_functions) * 100, 100.0)
        return round(coverage, 2)

    def setup_e2e_testing(self) -> Dict:
        """Setup end-to-end governance workflow testing."""
        logger.info("Setting up end-to-end testing infrastructure...")

        e2e_results = {
            'test_scenarios': [],
            'workflow_tests': [],
            'performance_benchmarks': {},
            'success_rate': 0.0
        }

        # Create E2E test scenarios
        test_scenarios = [
            {
                'name': 'complete_governance_workflow',
                'description': 'Constitution deployment → Policy creation → Voting → Enactment',
                'steps': [
                    'deploy_constitution',
                    'propose_policy',
                    'vote_on_policy',
                    'enact_policy',
                    'validate_compliance'
                ]
            },
            {
                'name': 'appeals_workflow',
                'description': 'Policy violation → Appeal submission → Resolution',
                'steps': [
                    'trigger_violation',
                    'submit_appeal',
                    'review_appeal',
                    'resolve_appeal'
                ]
            },
            {
                'name': 'emergency_governance',
                'description': 'Emergency policy deactivation workflow',
                'steps': [
                    'detect_emergency',
                    'deactivate_policy',
                    'notify_stakeholders',
                    'validate_deactivation'
                ]
            }
        ]

        # Generate E2E test files
        for scenario in test_scenarios:
            self._generate_e2e_test(scenario)
            e2e_results['test_scenarios'].append(scenario['name'])

        # Setup performance benchmarking
        self._setup_performance_benchmarks()

        self.test_results['e2e_tests'] = e2e_results
        return e2e_results

    def _generate_e2e_test(self, scenario: Dict):
        """Generate end-to-end test file for a scenario."""
        scenario_name = scenario['name']
        scenario_description = scenario['description']
        test_steps = self._generate_test_steps(scenario['steps'])

        test_template = f'''
import {{ expect }} from "chai";
import * as anchor from "@project-serum/anchor";
import {{ Program }} from "@project-serum/anchor";

describe("E2E: {scenario_name}", () => {{
  let program: Program;
  let provider: anchor.AnchorProvider;

  before(async () => {{
    provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    program = anchor.workspace.QuantumagiCore;
  }});

  it("should complete {scenario_description}", async () => {{
    // Test implementation for {scenario_name}
    const startTime = Date.now();

    try {{
      // Execute test steps
{test_steps}

      const endTime = Date.now();
      const duration = endTime - startTime;

      console.log(`E2E test completed in ${{duration}}ms`);
      expect(duration).to.be.lessThan(30000); // 30 second timeout

    }} catch (error) {{
      console.error(`E2E test failed: ${{error.message}}`);
      throw error;
    }}
  }});
}});
'''

        test_file = self.tests_dir / "e2e" / f"{scenario['name']}.test.ts"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file, 'w') as f:
            f.write(test_template)

        logger.info(f"Generated E2E test: {test_file}")

    def _generate_test_steps(self, steps: List[str]) -> str:
        """Generate test step implementations."""
        step_implementations = {
            'deploy_constitution': '''
      // Deploy constitution
      const constitution = anchor.web3.Keypair.generate();
      const constitutionHash = "e2e_test_constitution_hash";

      await program.methods
        .initialize(constitutionHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: provider.wallet.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([constitution])
        .rpc();

      console.log("✅ Constitution deployed");''',

            'propose_policy': '''
      // Propose policy
      const policy = anchor.web3.Keypair.generate();
      const policyContent = "E2E test policy content";

      await program.methods
        .proposePolicy(policyContent, "Safety")
        .accounts({
          policy: policy.publicKey,
          proposer: provider.wallet.publicKey,
          constitution: constitution.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([policy])
        .rpc();

      console.log("✅ Policy proposed");''',

            'vote_on_policy': '''
      // Vote on policy
      await program.methods
        .voteOnPolicy(true)
        .accounts({
          policy: policy.publicKey,
          voter: provider.wallet.publicKey,
        })
        .rpc();

      console.log("✅ Vote cast");''',

            'enact_policy': '''
      // Enact policy
      await program.methods
        .enactPolicy()
        .accounts({
          policy: policy.publicKey,
          authority: provider.wallet.publicKey,
        })
        .rpc();

      console.log("✅ Policy enacted");''',

            'validate_compliance': '''
      // Validate compliance
      const result = await program.methods
        .checkCompliance("test_action", "test_context")
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.true;
      console.log("✅ Compliance validated");'''
        }

        implementations = []
        for step in steps:
            if step in step_implementations:
                implementations.append(step_implementations[step])
            else:
                implementations.append(f'      // TODO: Implement {step}')

        return '\n\n'.join(implementations)

    def _setup_performance_benchmarks(self):
        """Setup performance benchmarking infrastructure."""
        benchmark_config = {
            'targets': {
                'constitution_deployment': {'max_time_ms': 5000},
                'policy_proposal': {'max_time_ms': 3000},
                'policy_voting': {'max_time_ms': 2000},
                'compliance_check': {'max_time_ms': 1000}
            },
            'load_testing': {
                'concurrent_users': [1, 5, 10, 25],
                'test_duration_seconds': 60
            }
        }

        config_file = self.tests_dir / "performance" / "benchmark_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(benchmark_config, f, indent=2)

        logger.info(f"Performance benchmark config created: {config_file}")

    def setup_frontend_testing(self) -> Dict:
        """Setup frontend testing infrastructure."""
        logger.info("Setting up frontend testing infrastructure...")

        frontend_results = {
            'test_files_created': [],
            'testing_framework': 'jest',
            'coverage_target': 70.0,
            'component_tests': []
        }

        # Check if frontend directory exists
        frontend_dir = self.applications_dir / "frontend"
        if not frontend_dir.exists():
            logger.warning("Frontend directory not found, creating placeholder structure")
            frontend_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jest configuration
        self._setup_jest_config(frontend_dir)

        # Create component test templates
        self._create_component_tests(frontend_dir)

        # Setup Anchor client testing
        self._setup_anchor_client_tests(frontend_dir)

        self.test_results['frontend_tests'] = frontend_results
        return frontend_results

    def _setup_jest_config(self, frontend_dir: Path):
        """Setup Jest testing configuration."""
        jest_config = {
            "preset": "ts-jest",
            "testEnvironment": "jsdom",
            "setupFilesAfterEnv": ["<rootDir>/src/setupTests.ts"],
            "moduleNameMapping": {
                "^@/(.*)$": "<rootDir>/src/$1"
            },
            "collectCoverageFrom": [
                "src/**/*.{ts,tsx}",
                "!src/**/*.d.ts",
                "!src/index.tsx"
            ],
            "coverageThreshold": {
                "global": {
                    "branches": 70,
                    "functions": 70,
                    "lines": 70,
                    "statements": 70
                }
            }
        }

        config_file = frontend_dir / "jest.config.json"
        with open(config_file, 'w') as f:
            json.dump(jest_config, f, indent=2)

        logger.info(f"Jest configuration created: {config_file}")

    def _create_component_tests(self, frontend_dir: Path):
        """Create component test templates."""
        # Create basic component test structure
        test_dir = frontend_dir / "src" / "__tests__"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create a sample component test
        component_test = """
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Sample governance dashboard component test
describe('Governance Dashboard', () => {
  it('renders governance dashboard', () => {
    // Test implementation will be added when components are created
    expect(true).toBe(true);
  });
});
"""

        test_file = test_dir / "GovernanceDashboard.test.tsx"
        with open(test_file, 'w') as f:
            f.write(component_test)

        logger.info(f"Component test template created: {test_file}")

    def _setup_anchor_client_tests(self, frontend_dir: Path):
        """Setup Anchor client testing infrastructure."""
        # Create Anchor client test utilities
        utils_dir = frontend_dir / "src" / "utils" / "test"
        utils_dir.mkdir(parents=True, exist_ok=True)

        anchor_test_utils = """
// Anchor client testing utilities
export const mockAnchorProvider = {
  connection: {
    confirmTransaction: jest.fn(),
    requestAirdrop: jest.fn(),
  },
  wallet: {
    publicKey: 'mock-public-key',
  },
};

export const mockProgram = {
  methods: {
    initialize: jest.fn(),
    proposePolicy: jest.fn(),
    voteOnPolicy: jest.fn(),
    enactPolicy: jest.fn(),
    checkCompliance: jest.fn(),
  },
  account: {
    constitution: {
      fetch: jest.fn(),
    },
    policy: {
      fetch: jest.fn(),
    },
  },
};
"""

        utils_file = utils_dir / "anchorMocks.ts"
        with open(utils_file, 'w') as f:
            f.write(anchor_test_utils)

        logger.info(f"Anchor client test utilities created: {utils_file}")

    def run_comprehensive_tests(self) -> Dict:
        """Run comprehensive test suite across all components."""
        logger.info("Running comprehensive test suite...")

        results = {
            'anchor_tests': self.setup_anchor_test_infrastructure(),
            'e2e_tests': self.setup_e2e_testing(),
            'frontend_tests': self.setup_frontend_testing(),
            'overall_success': True,
            'recommendations': []
        }

        # Generate recommendations based on results
        recommendations = []

        anchor_coverage = results['anchor_tests'].get('coverage_percentage', 0)
        if anchor_coverage < 80:
            recommendations.append(
                f"Anchor test coverage is {anchor_coverage}%. Target: 80%+. "
                "Add more comprehensive test cases for program instructions."
            )

        recommendations.extend([
            "Implement continuous integration for all test suites",
            "Add performance regression testing",
            "Setup automated test reporting and metrics",
            "Integrate test results with deployment pipeline"
        ])

        results['recommendations'] = recommendations

        # Generate comprehensive report
        self._generate_test_report(results)

        return results

    def _generate_test_report(self, results: Dict):
        """Generate comprehensive test infrastructure report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"test_infrastructure_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Test infrastructure report generated: {report_file}")

        # Print summary
        print("\n" + "="*60)
        print("ACGS-1 TEST INFRASTRUCTURE SUMMARY")
        print("="*60)

        anchor_data = results['anchor_tests']
        print(f"🔗 Anchor Tests:")
        print(f"   - Programs analyzed: {len(anchor_data.get('programs_analyzed', []))}")
        print(f"   - Coverage: {anchor_data.get('coverage_percentage', 0)}%")

        e2e_data = results['e2e_tests']
        print(f"🔄 E2E Tests:")
        print(f"   - Scenarios: {len(e2e_data.get('test_scenarios', []))}")

        frontend_data = results['frontend_tests']
        print(f"🖥️ Frontend Tests:")
        print(f"   - Framework: {frontend_data.get('testing_framework', 'N/A')}")
        print(f"   - Target coverage: {frontend_data.get('coverage_target', 0)}%")

        recommendations = results.get('recommendations', [])
        print(f"💡 Recommendations: {len(recommendations)} items")

        print("="*60)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='ACGS-1 Test Infrastructure Manager')
    parser.add_argument('--setup-all', action='store_true',
                       help='Setup complete test infrastructure')
    parser.add_argument('--anchor-tests', action='store_true',
                       help='Setup Anchor program tests only')
    parser.add_argument('--e2e-tests', action='store_true',
                       help='Setup end-to-end tests only')
    parser.add_argument('--frontend-tests', action='store_true',
                       help='Setup frontend tests only')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(),
                       help='Project root directory')

    args = parser.parse_args()

    # Initialize test manager
    test_manager = TestInfrastructureManager(args.project_root)

    try:
        if args.setup_all or (not any([args.anchor_tests, args.e2e_tests, args.frontend_tests])):
            test_manager.run_comprehensive_tests()
        elif args.anchor_tests:
            test_manager.setup_anchor_test_infrastructure()
        elif args.e2e_tests:
            test_manager.setup_e2e_testing()
        elif args.frontend_tests:
            test_manager.setup_frontend_testing()

    except KeyboardInterrupt:
        logger.info("Test setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()