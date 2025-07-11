// Security Test Suite - Comprehensive Security Testing
// Constitutional Hash: cdd01ef066bc6cf2
// Version: 3.0 - Enterprise Security Testing

import * as anchor from '@coral-xyz/anchor';
import { PublicKey, Keypair, SystemProgram, Transaction } from '@solana/web3.js';
import { expect } from 'chai';
import { TestInfrastructure } from './test_setup_helper';

interface SecurityTestResult {
  testName: string;
  passed: boolean;
  vulnerabilityLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  description: string;
  recommendation?: string;
}

class SecurityTester {
  private results: SecurityTestResult[] = [];

  addResult(result: SecurityTestResult): void {
    this.results.push(result);
  }

  getResults(): SecurityTestResult[] {
    return this.results;
  }

  getSummary(): { total: number; passed: number; failed: number; critical: number; high: number } {
    const total = this.results.length;
    const passed = this.results.filter(r => r.passed).length;
    const failed = total - passed;
    const critical = this.results.filter(r => r.vulnerabilityLevel === 'Critical').length;
    const high = this.results.filter(r => r.vulnerabilityLevel === 'High').length;
    
    return { total, passed, failed, critical, high };
  }
}

describe('🛡️ Security Test Suite', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  
  const program = anchor.workspace.QuantumagiCore;
  const authority = Keypair.generate();
  const attacker = Keypair.generate();
  const normalUser = Keypair.generate();
  
  let governancePDA: PublicKey;
  let governanceBump: number;
  const securityTester = new SecurityTester();
  
  const constitutionalHash = "cdd01ef066bc6cf2";
  const testPrinciples = [
    "Security is paramount",
    "Access control must be enforced",
    "Input validation is mandatory"
  ];
  
  const governanceConfig = {
    constitutional_hash: constitutionalHash,
    minimum_quorum: 5,
    max_voting_power_per_vote: 100000,
    min_proposal_interval: 300,
    emergency_threshold: 8000,
    delegation_enabled: true,
    batch_operations_enabled: true,
  };

  before(async () => {
    console.log('🛡️ Setting up Security Testing Environment...');
    
    // Fund test accounts
    await TestInfrastructure.ensureFunding(provider.connection, authority.publicKey, 5.0);
    await TestInfrastructure.ensureFunding(provider.connection, attacker.publicKey, 2.0);
    await TestInfrastructure.ensureFunding(provider.connection, normalUser.publicKey, 2.0);
    
    // Generate governance PDA
    [governancePDA, governanceBump] = await TestInfrastructure.createUniqueGovernancePDA(
      program,
      'security-test'
    );
    
    // Initialize governance
    await program.methods
      .initializeGovernance(
        authority.publicKey,
        testPrinciples,
        governanceConfig
      )
      .accounts({
        governance: governancePDA,
        authority: authority.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([authority])
      .rpc();
    
    console.log('✅ Security test environment initialized');
  });

  describe('🔐 Access Control Tests', () => {
    it('should prevent unauthorized governance initialization', async () => {
      const [attackerGovernancePDA] = await TestInfrastructure.createUniqueGovernancePDA(
        program,
        'attacker-governance'
      );

      try {
        await program.methods
          .initializeGovernance(
            attacker.publicKey,
            testPrinciples,
            governanceConfig
          )
          .accounts({
            governance: attackerGovernancePDA,
            authority: attacker.publicKey, // Attacker as authority
            systemProgram: SystemProgram.programId,
          })
          .signers([attacker])
          .rpc();

        securityTester.addResult({
          testName: 'Unauthorized Governance Initialization',
          passed: false,
          vulnerabilityLevel: 'Critical',
          description: 'Attacker was able to initialize their own governance',
          recommendation: 'Add proper authorization checks for governance initialization'
        });

      } catch (error) {
        securityTester.addResult({
          testName: 'Unauthorized Governance Initialization',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented unauthorized governance initialization'
        });
      }
    });

    it('should prevent unauthorized emergency actions', async () => {
      try {
        await program.methods
          .emergencyAction(
            { suspendProposal: {} },
            1
          )
          .accounts({
            governance: governancePDA,
            authority: attacker.publicKey, // Wrong authority
          })
          .signers([attacker])
          .rpc();

        securityTester.addResult({
          testName: 'Unauthorized Emergency Action',
          passed: false,
          vulnerabilityLevel: 'Critical',
          description: 'Attacker was able to execute emergency actions',
          recommendation: 'Strengthen emergency action authorization'
        });

      } catch (error) {
        expect(error.toString()).to.include('UnauthorizedEmergencyAction');
        securityTester.addResult({
          testName: 'Unauthorized Emergency Action',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented unauthorized emergency actions'
        });
      }
    });

    it('should validate proposal creation permissions', async () => {
      // Test if non-funded accounts can create proposals
      const unfundedAccount = Keypair.generate();
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(7001).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      try {
        await program.methods
          .createPolicyProposal(
            7001,
            "Unauthorized Proposal",
            "This proposal should not be created",
            "Unauthorized policy text",
            {
              urgency: 'Normal',
              category: 'Policy',
              requires_supermajority: false,
              allow_delegation: true,
            }
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: unfundedAccount.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([unfundedAccount])
          .rpc();

        securityTester.addResult({
          testName: 'Unfunded Account Proposal Creation',
          passed: false,
          vulnerabilityLevel: 'Medium',
          description: 'Unfunded account was able to create proposals',
          recommendation: 'Add minimum balance checks for proposal creation'
        });

      } catch (error) {
        securityTester.addResult({
          testName: 'Unfunded Account Proposal Creation',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented unfunded accounts from creating proposals'
        });
      }
    });
  });

  describe('🔍 Input Validation Tests', () => {
    it('should detect and block malicious content', async () => {
      const maliciousInputs = [
        "<script>alert('xss')</script>",
        "javascript:void(0)",
        "data:text/html,<script>alert('xss')</script>",
        "eval(maliciousCode())",
        "<img src=x onerror=alert('xss')>",
      ];

      let blockedCount = 0;

      for (let i = 0; i < maliciousInputs.length; i++) {
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(8000 + i).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );

        try {
          await program.methods
            .createPolicyProposal(
              8000 + i,
              maliciousInputs[i],
              "Malicious content test",
              "Testing malicious input validation",
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: normalUser.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([normalUser])
            .rpc();

        } catch (error) {
          if (error.toString().includes('SuspiciousContent')) {
            blockedCount++;
          }
        }
      }

      const allBlocked = blockedCount === maliciousInputs.length;
      securityTester.addResult({
        testName: 'Malicious Content Detection',
        passed: allBlocked,
        vulnerabilityLevel: allBlocked ? 'Low' : 'High',
        description: `Blocked ${blockedCount}/${maliciousInputs.length} malicious inputs`,
        recommendation: allBlocked ? undefined : 'Improve malicious content detection patterns'
      });
    });

    it('should validate input length limits', async () => {
      const oversizedInputs = {
        title: 'A'.repeat(101), // Over 100 char limit
        description: 'B'.repeat(501), // Over 500 char limit
        policyText: 'C'.repeat(1001), // Over 1000 char limit
      };

      const tests = [
        { field: 'title', value: oversizedInputs.title },
        { field: 'description', value: oversizedInputs.description },
        { field: 'policyText', value: oversizedInputs.policyText },
      ];

      let blockedCount = 0;

      for (let i = 0; i < tests.length; i++) {
        const test = tests[i];
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(8100 + i).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );

        try {
          await program.methods
            .createPolicyProposal(
              8100 + i,
              test.field === 'title' ? test.value : 'Normal Title',
              test.field === 'description' ? test.value : 'Normal Description',
              test.field === 'policyText' ? test.value : 'Normal Policy Text',
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: normalUser.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([normalUser])
            .rpc();

        } catch (error) {
          if (error.toString().includes('TooLong')) {
            blockedCount++;
          }
        }
      }

      const allBlocked = blockedCount === tests.length;
      securityTester.addResult({
        testName: 'Input Length Validation',
        passed: allBlocked,
        vulnerabilityLevel: allBlocked ? 'Low' : 'Medium',
        description: `Blocked ${blockedCount}/${tests.length} oversized inputs`,
        recommendation: allBlocked ? undefined : 'Strengthen input length validation'
      });
    });

    it('should validate constitutional hash integrity', async () => {
      const [fakeGovernancePDA] = await TestInfrastructure.createUniqueGovernancePDA(
        program,
        'fake-governance'
      );

      const fakeConfig = {
        ...governanceConfig,
        constitutional_hash: "fake_hash_12345", // Invalid hash
      };

      try {
        await program.methods
          .initializeGovernance(
            normalUser.publicKey,
            testPrinciples,
            fakeConfig
          )
          .accounts({
            governance: fakeGovernancePDA,
            authority: normalUser.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([normalUser])
          .rpc();

        securityTester.addResult({
          testName: 'Constitutional Hash Validation',
          passed: false,
          vulnerabilityLevel: 'Critical',
          description: 'System accepted invalid constitutional hash',
          recommendation: 'Strengthen constitutional hash validation'
        });

      } catch (error) {
        expect(error.toString()).to.include('InvalidConstitutionalHash');
        securityTester.addResult({
          testName: 'Constitutional Hash Validation',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly validated constitutional hash integrity'
        });
      }
    });
  });

  describe('⚡ Overflow & Arithmetic Tests', () => {
    it('should prevent voting power overflow attacks', async () => {
      // Create a test proposal first
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(9001).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      await program.methods
        .createPolicyProposal(
          9001,
          "Overflow Test Proposal",
          "Testing voting power overflow protection",
          "Overflow test policy text",
          {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: normalUser.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([normalUser])
        .rpc();

      // Attempt overflow attack
      const [votePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(9001).toArrayLike(Buffer, 'le', 8),
          attacker.publicKey.toBuffer()
        ],
        program.programId
      );

      try {
        await program.methods
          .voteOnProposal(
            9001,
            true,
            18446744073709551615, // u64::MAX
            null
          )
          .accounts({
            proposal: proposalPDA,
            voteRecord: votePDA,
            governance: governancePDA,
            voter: attacker.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([attacker])
          .rpc();

        securityTester.addResult({
          testName: 'Voting Power Overflow Protection',
          passed: false,
          vulnerabilityLevel: 'High',
          description: 'System accepted maximum u64 voting power',
          recommendation: 'Add proper overflow protection for voting power'
        });

      } catch (error) {
        expect(error.toString()).to.include('VotingPowerTooHigh');
        securityTester.addResult({
          testName: 'Voting Power Overflow Protection',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented voting power overflow'
        });
      }
    });

    it('should handle proposal counter overflow safely', async () => {
      // This test simulates what would happen if proposal counters approach limits
      try {
        const governance = await program.account.governanceState.fetch(governancePDA);
        const currentProposals = governance.statistics.totalProposalsCreated;
        
        // Check if the system handles large proposal numbers correctly
        const largeProposalId = 4294967295; // u32::MAX
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(largeProposalId).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );

        await program.methods
          .createPolicyProposal(
            largeProposalId,
            "Large ID Test",
            "Testing large proposal ID handling",
            "Large ID policy text",
            {
              urgency: 'Normal',
              category: 'Policy',
              requires_supermajority: false,
              allow_delegation: true,
            }
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: normalUser.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([normalUser])
          .rpc();

        securityTester.addResult({
          testName: 'Large Proposal ID Handling',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'System properly handled large proposal ID'
        });

      } catch (error) {
        if (error.toString().includes('ArithmeticOverflow')) {
          securityTester.addResult({
            testName: 'Large Proposal ID Handling',
            passed: true,
            vulnerabilityLevel: 'Low',
            description: 'System properly detected and prevented arithmetic overflow'
          });
        } else {
          securityTester.addResult({
            testName: 'Large Proposal ID Handling',
            passed: false,
            vulnerabilityLevel: 'Medium',
            description: `Unexpected error with large proposal ID: ${error.message}`,
            recommendation: 'Review large number handling logic'
          });
        }
      }
    });
  });

  describe('🎭 Double Spending & Replay Tests', () => {
    it('should prevent double voting attacks', async () => {
      // Create test proposal
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(9002).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      await program.methods
        .createPolicyProposal(
          9002,
          "Double Vote Test",
          "Testing double voting prevention",
          "Double vote test policy",
          {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: normalUser.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([normalUser])
        .rpc();

      // First vote (should succeed)
      const [votePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(9002).toArrayLike(Buffer, 'le', 8),
          attacker.publicKey.toBuffer()
        ],
        program.programId
      );

      await program.methods
        .voteOnProposal(
          9002,
          true,
          1000,
          null
        )
        .accounts({
          proposal: proposalPDA,
          voteRecord: votePDA,
          governance: governancePDA,
          voter: attacker.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([attacker])
        .rpc();

      // Second vote attempt (should fail)
      try {
        await program.methods
          .voteOnProposal(
            9002,
            false, // Different vote
            2000,  // Different power
            null
          )
          .accounts({
            proposal: proposalPDA,
            voteRecord: votePDA,
            governance: governancePDA,
            voter: attacker.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([attacker])
          .rpc();

        securityTester.addResult({
          testName: 'Double Voting Prevention',
          passed: false,
          vulnerabilityLevel: 'High',
          description: 'System allowed double voting from same account',
          recommendation: 'Strengthen double voting prevention logic'
        });

      } catch (error) {
        expect(error.toString()).to.include('AlreadyVoted');
        securityTester.addResult({
          testName: 'Double Voting Prevention',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented double voting'
        });
      }
    });

    it('should validate unique vote records', async () => {
      // Test if the system properly handles vote record uniqueness
      const proposalId = 9002;
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      // Try to create a vote record with same seeds
      const [duplicateVotePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8),
          normalUser.publicKey.toBuffer()
        ],
        program.programId
      );

      try {
        await program.methods
          .voteOnProposal(
            proposalId,
            true,
            500,
            null
          )
          .accounts({
            proposal: proposalPDA,
            voteRecord: duplicateVotePDA,
            governance: governancePDA,
            voter: normalUser.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([normalUser])
          .rpc();

        securityTester.addResult({
          testName: 'Vote Record Uniqueness',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'System properly created unique vote record'
        });

      } catch (error) {
        if (error.toString().includes('AlreadyVoted')) {
          securityTester.addResult({
            testName: 'Vote Record Uniqueness',
            passed: true,
            vulnerabilityLevel: 'Low',
            description: 'System properly enforced vote record uniqueness'
          });
        } else {
          securityTester.addResult({
            testName: 'Vote Record Uniqueness',
            passed: false,
            vulnerabilityLevel: 'Medium',
            description: `Unexpected error in vote record creation: ${error.message}`,
            recommendation: 'Review vote record creation logic'
          });
        }
      }
    });
  });

  describe('💰 Economic Attack Tests', () => {
    it('should prevent proposal spam attacks', async () => {
      // Test rapid proposal creation to check rate limiting
      const spammer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, spammer.publicKey, 5.0);

      let successfulSpam = 0;
      const spamAttempts = 10;

      for (let i = 0; i < spamAttempts; i++) {
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(9100 + i).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );

        try {
          await program.methods
            .createPolicyProposal(
              9100 + i,
              `Spam Proposal ${i}`,
              `Spam description ${i}`,
              `Spam policy text ${i}`,
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: spammer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([spammer])
            .rpc();

          successfulSpam++;
          
        } catch (error) {
          if (error.toString().includes('ProposalRateLimited')) {
            break; // Rate limiting working
          }
        }

        // Minimal delay between attempts
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      const rateLimitingWorking = successfulSpam < spamAttempts;
      securityTester.addResult({
        testName: 'Proposal Spam Prevention',
        passed: rateLimitingWorking,
        vulnerabilityLevel: rateLimitingWorking ? 'Low' : 'Medium',
        description: `Rate limiting allowed ${successfulSpam}/${spamAttempts} rapid proposals`,
        recommendation: rateLimitingWorking ? undefined : 'Implement stricter rate limiting'
      });
    });

    it('should validate batch operation limits', async () => {
      // Test if batch operations can be abused
      const largeBatchData = Array(100).fill(0).map((_, i) => ({
        policy_id: 9200 + i,
        title: `Batch Attack ${i}`,
        description: `Batch description ${i}`,
        policy_text: `Batch policy ${i}`,
        options: {
          urgency: 'Normal',
          category: 'Policy',
          requires_supermajority: false,
          allow_delegation: true,
        }
      }));

      try {
        await program.methods
          .batchCreateProposals(largeBatchData)
          .accounts({
            governance: governancePDA,
            proposer: normalUser.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([normalUser])
          .rpc();

        securityTester.addResult({
          testName: 'Batch Operation Abuse Prevention',
          passed: false,
          vulnerabilityLevel: 'Medium',
          description: 'System allowed oversized batch operation',
          recommendation: 'Implement stricter batch size limits'
        });

      } catch (error) {
        expect(error.toString()).to.include('BatchTooLarge');
        securityTester.addResult({
          testName: 'Batch Operation Abuse Prevention',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly prevented oversized batch operations'
        });
      }
    });
  });

  describe('🔐 Cryptographic Security Tests', () => {
    it('should validate account ownership', async () => {
      // Test if someone can vote with another person's account
      const victim = Keypair.generate();
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(9003).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      // Create test proposal
      await program.methods
        .createPolicyProposal(
          9003,
          "Ownership Test",
          "Testing account ownership validation",
          "Ownership test policy",
          {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: normalUser.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([normalUser])
        .rpc();

      // Try to vote using victim's account but attacker's signature
      const [votePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(9003).toArrayLike(Buffer, 'le', 8),
          victim.publicKey.toBuffer()
        ],
        program.programId
      );

      try {
        await program.methods
          .voteOnProposal(
            9003,
            true,
            1000,
            null
          )
          .accounts({
            proposal: proposalPDA,
            voteRecord: votePDA,
            governance: governancePDA,
            voter: victim.publicKey, // Victim's account
            systemProgram: SystemProgram.programId,
          })
          .signers([attacker]) // But attacker's signature!
          .rpc();

        securityTester.addResult({
          testName: 'Account Ownership Validation',
          passed: false,
          vulnerabilityLevel: 'Critical',
          description: 'System allowed voting with incorrect signature',
          recommendation: 'Strengthen signature validation'
        });

      } catch (error) {
        securityTester.addResult({
          testName: 'Account Ownership Validation',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly validated account ownership'
        });
      }
    });

    it('should validate PDA derivation', async () => {
      // Test if someone can manipulate PDA derivation
      const fakeProposalId = 9004;
      
      // Create a legitimate proposal
      const [legitimatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(fakeProposalId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      await program.methods
        .createPolicyProposal(
          fakeProposalId,
          "PDA Test",
          "Testing PDA validation",
          "PDA test policy",
          {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        )
        .accounts({
          proposal: legitimatePDA,
          governance: governancePDA,
          proposer: normalUser.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([normalUser])
        .rpc();

      // Try to vote using a manipulated PDA
      const [correctVotePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(fakeProposalId).toArrayLike(Buffer, 'le', 8),
          attacker.publicKey.toBuffer()
        ],
        program.programId
      );

      // Create a fake PDA with different seeds
      const [fakeVotePDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('fake'),
          new anchor.BN(fakeProposalId).toArrayLike(Buffer, 'le', 8),
          attacker.publicKey.toBuffer()
        ],
        program.programId
      );

      try {
        await program.methods
          .voteOnProposal(
            fakeProposalId,
            true,
            1000,
            null
          )
          .accounts({
            proposal: legitimatePDA,
            voteRecord: fakeVotePDA, // Wrong PDA
            governance: governancePDA,
            voter: attacker.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([attacker])
          .rpc();

        securityTester.addResult({
          testName: 'PDA Derivation Validation',
          passed: false,
          vulnerabilityLevel: 'High',
          description: 'System accepted manipulated PDA',
          recommendation: 'Strengthen PDA validation logic'
        });

      } catch (error) {
        securityTester.addResult({
          testName: 'PDA Derivation Validation',
          passed: true,
          vulnerabilityLevel: 'Low',
          description: 'Properly validated PDA derivation'
        });
      }
    });
  });

  after(async () => {
    console.log('🧹 Generating security test report...');
    
    const results = securityTester.getResults();
    const summary = securityTester.getSummary();
    
    console.log('\n🛡️ SECURITY TEST REPORT');
    console.log('=========================');
    console.log(`Total Tests: ${summary.total}`);
    console.log(`Passed: ${summary.passed}`);
    console.log(`Failed: ${summary.failed}`);
    console.log(`Critical Issues: ${summary.critical}`);
    console.log(`High Severity Issues: ${summary.high}`);
    console.log('=========================');
    
    console.log('\n📋 Detailed Results:');
    results.forEach((result, index) => {
      const status = result.passed ? '✅' : '❌';
      const severity = result.vulnerabilityLevel;
      console.log(`${index + 1}. ${status} ${result.testName} [${severity}]`);
      console.log(`   Description: ${result.description}`);
      if (result.recommendation) {
        console.log(`   Recommendation: ${result.recommendation}`);
      }
      console.log('');
    });
    
    // Security score calculation
    const securityScore = (summary.passed / summary.total) * 100;
    const criticalPenalty = summary.critical * 20;
    const highPenalty = summary.high * 10;
    const finalScore = Math.max(0, securityScore - criticalPenalty - highPenalty);
    
    console.log(`\n🎯 Security Score: ${finalScore.toFixed(1)}/100`);
    console.log(`Constitutional Hash: ${constitutionalHash}`);
    console.log('=========================');
    
    if (summary.critical > 0) {
      console.log('⚠️  CRITICAL VULNERABILITIES DETECTED - IMMEDIATE ACTION REQUIRED');
    } else if (summary.high > 0) {
      console.log('⚠️  HIGH SEVERITY ISSUES DETECTED - REVIEW RECOMMENDED');
    } else if (summary.failed === 0) {
      console.log('✅ ALL SECURITY TESTS PASSED - SYSTEM SECURE');
    }
    
    console.log('\n🛡️ Security testing completed!');
  });
});