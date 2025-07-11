// Enhanced Governance Test Suite - Comprehensive Testing Framework
// Constitutional Hash: cdd01ef066bc6cf2
// Version: 3.0 - Enterprise Testing

import * as anchor from '@coral-xyz/anchor';
import { PublicKey, Keypair, SystemProgram } from '@solana/web3.js';
import { expect } from 'chai';
import { TestInfrastructure } from './test_setup_helper';

interface GovernanceConfig {
  constitutional_hash: string;
  minimum_quorum: number;
  max_voting_power_per_vote: number;
  min_proposal_interval: number;
  emergency_threshold: number;
  delegation_enabled: boolean;
  batch_operations_enabled: boolean;
}

interface ProposalOptions {
  urgency: 'Emergency' | 'High' | 'Normal' | 'Low';
  category: 'Constitutional' | 'Policy' | 'Technical' | 'Economic' | 'Administrative';
  requires_supermajority: boolean;
  allow_delegation: boolean;
}

describe('Enhanced Governance System', () => {
  // Test configuration
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  
  const program = anchor.workspace.QuantumagiCore;
  const authority = Keypair.generate();
  const proposer = Keypair.generate();
  const voter1 = Keypair.generate();
  const voter2 = Keypair.generate();
  const delegateVoter = Keypair.generate();
  
  let governancePDA: PublicKey;
  let governanceBump: number;
  
  // Test data
  const constitutionalHash = "cdd01ef066bc6cf2";
  const testPrinciples = [
    "Transparency in all governance decisions",
    "Democratic participation for all stakeholders", 
    "Constitutional compliance is mandatory",
    "Efficiency and cost-effectiveness",
    "Security and data protection"
  ];
  
  const governanceConfig: GovernanceConfig = {
    constitutional_hash: constitutionalHash,
    minimum_quorum: 10,
    max_voting_power_per_vote: 1000000,
    min_proposal_interval: 300, // 5 minutes
    emergency_threshold: 8000, // 80%
    delegation_enabled: true,
    batch_operations_enabled: true,
  };

  before(async () => {
    // Setup test environment
    console.log('🚀 Setting up Enhanced Governance Test Environment...');
    
    // Fund test accounts
    await TestInfrastructure.ensureFunding(provider.connection, authority.publicKey, 5.0);
    await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 2.0);
    await TestInfrastructure.ensureFunding(provider.connection, voter1.publicKey, 1.0);
    await TestInfrastructure.ensureFunding(provider.connection, voter2.publicKey, 1.0);
    await TestInfrastructure.ensureFunding(provider.connection, delegateVoter.publicKey, 1.0);
    
    // Generate unique governance PDA
    [governancePDA, governanceBump] = await TestInfrastructure.createUniqueGovernancePDA(
      program,
      'enhanced-governance'
    );
    
    console.log(`✅ Test accounts funded and governance PDA created: ${governancePDA.toString()}`);
  });

  describe('🏛️ Governance Initialization', () => {
    it('should initialize enhanced governance with constitutional compliance', async () => {
      const tx = await program.methods
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

      console.log(`📋 Governance initialized: ${tx}`);

      // Verify governance state
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      
      expect(governanceAccount.authority.toString()).to.equal(authority.publicKey.toString());
      expect(governanceAccount.principles).to.have.length(testPrinciples.length);
      expect(governanceAccount.totalPolicies).to.equal(0);
      expect(governanceAccount.activeProposals).to.equal(0);
      expect(governanceAccount.emergencyMode).to.be.false;
      expect(governanceAccount.configuration.constitutionalHash).to.equal(constitutionalHash);
      expect(governanceAccount.version).to.equal(3);
      
      console.log('✅ Governance initialization verified');
    });

    it('should reject initialization with invalid constitutional hash', async () => {
      const invalidConfig = { ...governanceConfig, constitutional_hash: "invalid_hash" };
      
      try {
        await program.methods
          .initializeGovernance(
            authority.publicKey,
            testPrinciples,
            invalidConfig
          )
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        
        expect.fail('Should have rejected invalid constitutional hash');
      } catch (error) {
        expect(error.toString()).to.include('InvalidConstitutionalHash');
        console.log('✅ Invalid constitutional hash properly rejected');
      }
    });

    it('should reject too many principles', async () => {
      const tooManyPrinciples = Array(101).fill("Test principle");
      
      try {
        await program.methods
          .initializeGovernance(
            authority.publicKey,
            tooManyPrinciples,
            governanceConfig
          )
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        
        expect.fail('Should have rejected too many principles');
      } catch (error) {
        expect(error.toString()).to.include('TooManyPrinciples');
        console.log('✅ Too many principles properly rejected');
      }
    });
  });

  describe('📝 Enhanced Proposal Creation', () => {
    let proposalPDA: PublicKey;
    let proposalBump: number;
    const policyId = 1;

    before(async () => {
      [proposalPDA, proposalBump] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );
    });

    it('should create enhanced proposal with constitutional compliance', async () => {
      const proposalOptions: ProposalOptions = {
        urgency: 'Normal',
        category: 'Policy',
        requires_supermajority: false,
        allow_delegation: true,
      };

      const tx = await program.methods
        .createPolicyProposal(
          policyId,
          "Test Enhanced Proposal",
          "This is a test proposal for the enhanced governance system",
          "Detailed policy text with constitutional compliance requirements",
          proposalOptions
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: proposer.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([proposer])
        .rpc();

      console.log(`📄 Enhanced proposal created: ${tx}`);

      // Verify proposal state
      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);
      
      expect(proposalAccount.policyId.value).to.equal(policyId);
      expect(proposalAccount.title.title).to.equal("Test Enhanced Proposal");
      expect(proposalAccount.proposer.toString()).to.equal(proposer.publicKey.toString());
      expect(proposalAccount.status).to.deep.equal({ active: {} });
      expect(proposalAccount.constitutionalCompliance).to.be.greaterThan(0);
      expect(proposalAccount.options.category).to.deep.equal({ policy: {} });
      expect(proposalAccount.options.allowDelegation).to.be.true;
      
      console.log(`✅ Enhanced proposal verified with compliance score: ${proposalAccount.constitutionalCompliance}`);
    });

    it('should reject proposal with suspicious content', async () => {
      const maliciousOptions: ProposalOptions = {
        urgency: 'Normal',
        category: 'Policy',
        requires_supermajority: false,
        allow_delegation: true,
      };

      try {
        await program.methods
          .createPolicyProposal(
            policyId + 1,
            "<script>alert('xss')</script>",
            "This proposal contains suspicious content",
            "javascript:void(0)",
            maliciousOptions
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: proposer.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([proposer])
          .rpc();
        
        expect.fail('Should have rejected suspicious content');
      } catch (error) {
        expect(error.toString()).to.include('SuspiciousContent');
        console.log('✅ Suspicious content properly rejected');
      }
    });

    it('should respect proposal rate limiting', async () => {
      // First proposal should succeed
      const options: ProposalOptions = {
        urgency: 'Normal',
        category: 'Policy',
        requires_supermajority: false,
        allow_delegation: true,
      };

      // Create first proposal
      const [firstProposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(policyId + 2).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      await program.methods
        .createPolicyProposal(
          policyId + 2,
          "First Rate Limit Test",
          "Testing rate limiting functionality",
          "Rate limit test policy text",
          options
        )
        .accounts({
          proposal: firstProposalPDA,
          governance: governancePDA,
          proposer: proposer.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([proposer])
        .rpc();

      // Immediate second proposal should be rate limited
      const [secondProposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(policyId + 3).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      try {
        await program.methods
          .createPolicyProposal(
            policyId + 3,
            "Second Rate Limit Test",
            "This should be rate limited",
            "Rate limit test policy text 2",
            options
          )
          .accounts({
            proposal: secondProposalPDA,
            governance: governancePDA,
            proposer: proposer.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([proposer])
          .rpc();
        
        expect.fail('Should have been rate limited');
      } catch (error) {
        expect(error.toString()).to.include('ProposalRateLimited');
        console.log('✅ Proposal rate limiting working correctly');
      }
    });
  });

  describe('🗳️ Enhanced Voting System', () => {
    let votePDA: PublicKey;
    let voteBump: number;
    const policyId = 1;

    before(async () => {
      [votePDA, voteBump] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8),
          voter1.publicKey.toBuffer()
        ],
        program.programId
      );
    });

    it('should cast enhanced vote with constitutional weighting', async () => {
      const votingPower = 1000;

      const tx = await program.methods
        .voteOnProposal(
          policyId,
          true, // vote for
          votingPower,
          null // no delegation
        )
        .accounts({
          proposal: PublicKey.findProgramAddressSync(
            [Buffer.from('proposal'), new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8)],
            program.programId
          )[0],
          voteRecord: votePDA,
          governance: governancePDA,
          voter: voter1.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([voter1])
        .rpc();

      console.log(`🗳️ Enhanced vote cast: ${tx}`);

      // Verify vote record
      const voteRecord = await program.account.voteRecord.fetch(votePDA);
      
      expect(voteRecord.voter.toString()).to.equal(voter1.publicKey.toString());
      expect(voteRecord.policyId.value).to.equal(policyId);
      expect(voteRecord.vote).to.be.true;
      expect(voteRecord.votingPower.value).to.equal(votingPower);
      expect(voteRecord.constitutionalWeight).to.be.greaterThan(100);
      expect(voteRecord.delegationProof).to.be.null;
      
      console.log(`✅ Enhanced vote verified with constitutional weight: ${voteRecord.constitutionalWeight}`);
    });

    it('should prevent double voting', async () => {
      try {
        await program.methods
          .voteOnProposal(
            policyId,
            false, // vote against
            500,
            null
          )
          .accounts({
            proposal: PublicKey.findProgramAddressSync(
              [Buffer.from('proposal'), new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8)],
              program.programId
            )[0],
            voteRecord: votePDA,
            governance: governancePDA,
            voter: voter1.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([voter1])
          .rpc();
        
        expect.fail('Should have prevented double voting');
      } catch (error) {
        expect(error.toString()).to.include('AlreadyVoted');
        console.log('✅ Double voting properly prevented');
      }
    });

    it('should validate voting power limits', async () => {
      const [vote2PDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vote'),
          new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8),
          voter2.publicKey.toBuffer()
        ],
        program.programId
      );

      try {
        await program.methods
          .voteOnProposal(
            policyId,
            true,
            2000000, // Exceeds max voting power
            null
          )
          .accounts({
            proposal: PublicKey.findProgramAddressSync(
              [Buffer.from('proposal'), new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8)],
              program.programId
            )[0],
            voteRecord: vote2PDA,
            governance: governancePDA,
            voter: voter2.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([voter2])
          .rpc();
        
        expect.fail('Should have rejected excessive voting power');
      } catch (error) {
        expect(error.toString()).to.include('VotingPowerExceedsLimit');
        console.log('✅ Voting power limits properly enforced');
      }
    });
  });

  describe('⚡ Batch Operations', () => {
    it('should process batch proposal creation', async () => {
      const batchData = [
        {
          policy_id: 10,
          title: "Batch Proposal 1",
          description: "First proposal in batch",
          policy_text: "Batch policy text 1",
          options: {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        },
        {
          policy_id: 11,
          title: "Batch Proposal 2", 
          description: "Second proposal in batch",
          policy_text: "Batch policy text 2",
          options: {
            urgency: 'High',
            category: 'Technical',
            requires_supermajority: true,
            allow_delegation: false,
          }
        }
      ];

      const tx = await program.methods
        .batchCreateProposals(batchData)
        .accounts({
          governance: governancePDA,
          proposer: proposer.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([proposer])
        .rpc();

      console.log(`📦 Batch proposals created: ${tx}`);

      // Verify governance state updated
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      expect(governanceAccount.statistics.batchOperationsCount).to.be.greaterThan(0);
      
      console.log('✅ Batch operations completed successfully');
    });

    it('should respect batch size limits', async () => {
      const largeBatch = Array(51).fill(0).map((_, i) => ({
        policy_id: 100 + i,
        title: `Large Batch Proposal ${i}`,
        description: `Description ${i}`,
        policy_text: `Policy text ${i}`,
        options: {
          urgency: 'Normal',
          category: 'Policy',
          requires_supermajority: false,
          allow_delegation: true,
        }
      }));

      try {
        await program.methods
          .batchCreateProposals(largeBatch)
          .accounts({
            governance: governancePDA,
            proposer: proposer.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([proposer])
          .rpc();
        
        expect.fail('Should have rejected large batch');
      } catch (error) {
        expect(error.toString()).to.include('BatchTooLarge');
        console.log('✅ Batch size limits properly enforced');
      }
    });
  });

  describe('🏁 Proposal Finalization', () => {
    const policyId = 1;

    it('should finalize proposal with enhanced outcome calculation', async () => {
      // Wait for voting period to end (simplified for testing)
      await new Promise(resolve => setTimeout(resolve, 1000));

      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(policyId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      const tx = await program.methods
        .finalizeProposal(policyId)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          finalizer: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      console.log(`🏁 Proposal finalized: ${tx}`);

      // Verify finalization
      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      
      expect(proposalAccount.status).to.not.deep.equal({ active: {} });
      expect(proposalAccount.finalResult).to.not.be.null;
      expect(governanceAccount.activeProposals).to.be.lessThan(governanceAccount.statistics.totalProposalsCreated);
      
      console.log(`✅ Proposal finalized with result: ${JSON.stringify(proposalAccount.finalResult)}`);
    });
  });

  describe('📊 Performance Metrics', () => {
    it('should track governance statistics', async () => {
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      const stats = governanceAccount.statistics;
      
      expect(stats.totalProposalsCreated).to.be.greaterThan(0);
      expect(stats.batchOperationsCount).to.be.greaterThan(0);
      expect(governanceAccount.auditTrail).to.have.length.greaterThan(0);
      
      console.log('📈 Governance Statistics:');
      console.log(`  - Total Proposals: ${stats.totalProposalsCreated}`);
      console.log(`  - Approved Proposals: ${stats.approvedProposals}`);
      console.log(`  - Rejected Proposals: ${stats.rejectedProposals}`);
      console.log(`  - Total Votes Cast: ${stats.totalVotesCast}`);
      console.log(`  - Batch Operations: ${stats.batchOperationsCount}`);
      console.log(`  - Audit Trail Entries: ${governanceAccount.auditTrail.length}`);
      
      console.log('✅ Performance metrics validation completed');
    });

    it('should maintain constitutional compliance audit trail', async () => {
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      const auditTrail = governanceAccount.auditTrail;
      
      // Verify audit trail contains initialization
      const initEntry = auditTrail.find(entry => 
        entry.action.hasOwnProperty('systemInitialized')
      );
      expect(initEntry).to.not.be.undefined;
      expect(initEntry.actor.toString()).to.equal(authority.publicKey.toString());
      
      // Verify audit trail contains proposal creation
      const proposalEntry = auditTrail.find(entry => 
        entry.action.hasOwnProperty('proposalCreated')
      );
      expect(proposalEntry).to.not.be.undefined;
      
      console.log('✅ Constitutional compliance audit trail verified');
    });
  });

  describe('🔧 Error Handling & Edge Cases', () => {
    it('should handle arithmetic overflow gracefully', async () => {
      // Test with maximum values to trigger overflow protection
      try {
        await program.methods
          .voteOnProposal(
            1,
            true,
            18446744073709551615, // u64::MAX
            null
          )
          .accounts({
            proposal: PublicKey.findProgramAddressSync(
              [Buffer.from('proposal'), new anchor.BN(1).toArrayLike(Buffer, 'le', 8)],
              program.programId
            )[0],
            voteRecord: PublicKey.findProgramAddressSync(
              [
                Buffer.from('vote'),
                new anchor.BN(1).toArrayLike(Buffer, 'le', 8),
                voter2.publicKey.toBuffer()
              ],
              program.programId
            )[0],
            governance: governancePDA,
            voter: voter2.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([voter2])
          .rpc();
        
        expect.fail('Should have prevented overflow');
      } catch (error) {
        expect(error.toString()).to.include('VotingPowerTooHigh');
        console.log('✅ Arithmetic overflow protection working');
      }
    });

    it('should validate empty inputs', async () => {
      const [emptyProposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(999).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );

      try {
        await program.methods
          .createPolicyProposal(
            999,
            "", // Empty title
            "Description",
            "Policy text",
            {
              urgency: 'Normal',
              category: 'Policy',
              requires_supermajority: false,
              allow_delegation: true,
            }
          )
          .accounts({
            proposal: emptyProposalPDA,
            governance: governancePDA,
            proposer: proposer.publicKey,
            systemProgram: SystemProgram.programId,
          })
          .signers([proposer])
          .rpc();
        
        expect.fail('Should have rejected empty title');
      } catch (error) {
        expect(error.toString()).to.include('InvalidTitle');
        console.log('✅ Empty input validation working');
      }
    });
  });

  after(async () => {
    console.log('🧹 Cleaning up test environment...');
    
    // Generate test summary
    const governanceAccount = await program.account.governanceState.fetch(governancePDA);
    const stats = governanceAccount.statistics;
    
    console.log('\n📊 ENHANCED GOVERNANCE TEST SUMMARY');
    console.log('=====================================');
    console.log(`Constitutional Hash: ${constitutionalHash}`);
    console.log(`Total Proposals Created: ${stats.totalProposalsCreated}`);
    console.log(`Approved Proposals: ${stats.approvedProposals}`);
    console.log(`Rejected Proposals: ${stats.rejectedProposals}`);
    console.log(`Total Votes Cast: ${stats.totalVotesCast}`);
    console.log(`Batch Operations: ${stats.batchOperationsCount}`);
    console.log(`Audit Trail Entries: ${governanceAccount.auditTrail.length}`);
    console.log(`Test Coverage: Enhanced governance features`);
    console.log('=====================================');
    console.log('✅ All enhanced governance tests completed successfully!');
  });
});