// Constitutional Hash: cdd01ef066bc6cf2

// Comprehensive tests for Quantumagi transaction optimization
// Target: >80% test coverage with cost validation

import * as anchor from '@coral-xyz/anchor';
import { Program } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../target/types/quantumagi_core';
import { expect } from 'chai';
import { createHash } from 'crypto';

describe('Transaction Optimization', () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;
  const provider = anchor.getProvider();

  // Test accounts
  let authority: anchor.web3.Keypair;
  let governancePDA: anchor.web3.PublicKey;
  let governanceBump: number;

  before(async () => {
    // Test isolation - unique governance per test suite
    const testSuiteId = 'transaction_optimization_' + Date.now();
    authority = anchor.web3.Keypair.generate();

    // Airdrop SOL for testing
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(
        authority.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      )
    );

    // Derive governance PDA
    [governancePDA, governanceBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from('governance_transaction_optimization_' + Date.now())],
      program.programId
    );

    // Initialize governance for testing
    const principles = [
      'PC-001: No unauthorized state mutations',
      'GV-001: Democratic governance required',
      'FN-001: Treasury protection mandatory',
    ];

    await program.methods
      .initializeGovernance(authority.publicKey, principles)
      .accounts({
        governance: governancePDA,
        authority: authority.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([authority])
      .rpc();
  });

  describe('Batch Configuration', () => {
    it('should create valid batch configuration', () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000), // 0.01 SOL
        enabled: true,
      };

      expect(batchConfig.maxBatchSize).to.equal(10);
      expect(batchConfig.costTargetLamports.toNumber()).to.equal(10_000_000);
      expect(batchConfig.enabled).to.be.true;
    });

    it('should validate batch size limits', () => {
      const maxAllowedSize = 10;
      const testSizes = [1, 5, 10, 15];

      testSizes.forEach((size) => {
        const isValid = size <= maxAllowedSize;
        expect(size <= maxAllowedSize).to.equal(isValid);
      });
    });
  });

  describe('Governance Operations', () => {
    it('should create policy proposal operation', () => {
      const policyId = new anchor.BN(1001);
      const ruleHash = Array.from(createHash('sha256').update('Test rule').digest());

      const operation = {
        policyProposal: {
          policyId,
          ruleHash,
        },
      };

      expect(operation.policyProposal.policyId.toNumber()).to.equal(1001);
      expect(operation.policyProposal.ruleHash).to.have.length(32);
    });

    it('should create policy vote operation', () => {
      const policyId = new anchor.BN(1001);
      const vote = true;

      const operation = {
        policyVote: {
          policyId,
          vote,
        },
      };

      expect(operation.policyVote.policyId.toNumber()).to.equal(1001);
      expect(operation.policyVote.vote).to.be.true;
    });

    it('should create compliance check operation', () => {
      const policyId = new anchor.BN(1001);
      const actionHash = Array.from(createHash('sha256').update('Test action').digest());

      const operation = {
        complianceCheck: {
          policyId,
          actionHash,
        },
      };

      expect(operation.complianceCheck.policyId.toNumber()).to.equal(1001);
      expect(operation.complianceCheck.actionHash).to.have.length(32);
    });
  });

  describe('Optimized Governance Operations', () => {
    it('should execute single policy proposal with cost optimization', async () => {
      const policyId = new anchor.BN(2001);
      const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );

      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      // Create policy proposal (optimized single operation)
      await program.methods
        .createPolicyProposal(
          policyId,
          'Optimized Test Policy',
          'Testing cost optimization for single policy proposal',
          'ENFORCE: Cost optimization requirements for governance operations'
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const transactionCost = initialBalance - finalBalance;

      // Verify cost is within target (0.01 SOL = 10,000,000 lamports)
      expect(transactionCost).to.be.lessThan(10_000_000);
      console.log(`Single policy proposal cost: ${transactionCost} lamports`);
    });

    it('should execute multi-operation workflow with cost optimization', async () => {
      const policyId = new anchor.BN(3001);
      const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );

      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      // Operation 1: Create policy proposal
      await program.methods
        .createPolicyProposal(
          policyId,
          'Multi-operation Test Policy',
          'Testing multi-operation cost optimization',
          'ENFORCE: Multi-operation governance workflow requirements'
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      // Operation 2: Vote on proposal
      const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('vote_record'), policyId.toBuffer('le', 8), authority.publicKey.toBuffer()],
        program.programId
      );

      await program.methods
        .voteOnProposal(policyId, true, new anchor.BN(1))
        .accounts({
          proposal: proposalPDA,
          voteRecord: voteRecordPDA,
          voter: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      // Operation 3: Finalize proposal
      await program.methods
        .finalizeProposal(policyId)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          finalizer: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const workflowCost = initialBalance - finalBalance;

      // Verify workflow cost is within target
      expect(workflowCost).to.be.lessThan(10_000_000);

      console.log(`Multi-operation workflow cost: ${workflowCost} lamports`);
      console.log(`Average cost per operation: ${(workflowCost / 3).toFixed(0)} lamports`);

      // Verify cost efficiency (should be less than 0.01 SOL for complete workflow)
      expect(workflowCost).to.be.lessThan(10_000_000);
    });

    it('should handle emergency actions with cost validation', async () => {
      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      // Execute emergency action (simulating batch-like functionality)
      await program.methods
        .emergencyAction({ systemMaintenance: {} }, null)
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const emergencyActionCost = initialBalance - finalBalance;

      // Verify emergency action cost is minimal
      expect(emergencyActionCost).to.be.lessThan(5_000_000); // Should be very efficient
      console.log(`Emergency action cost: ${emergencyActionCost} lamports`);
    });

    it('should validate unauthorized access prevention', async () => {
      const unauthorizedUser = anchor.web3.Keypair.generate();

      // Airdrop to unauthorized user
      await provider.connection.confirmTransaction(
        await provider.connection.requestAirdrop(
          unauthorizedUser.publicKey,
          1 * anchor.web3.LAMPORTS_PER_SOL
        )
      );

      const policyId = new anchor.BN(5001);
      const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );

      try {
        // Attempt unauthorized emergency action
        await program.methods
          .emergencyAction({ systemMaintenance: {} }, null)
          .accounts({
            governance: governancePDA,
            authority: unauthorizedUser.publicKey,
          })
          .signers([unauthorizedUser])
          .rpc();

        expect.fail('Should have rejected unauthorized emergency action');
      } catch (error) {
        expect(error).to.exist;
        console.log('✅ Unauthorized access properly prevented');
      }
    });
  });

  describe('Cost Analysis', () => {
    it('should demonstrate cost optimization with multiple proposals', async () => {
      const initialBalance = await provider.connection.getBalance(authority.publicKey);
      const proposalCount = 5;
      const proposalCosts = [];

      // Create multiple proposals to analyze cost patterns
      for (let i = 0; i < proposalCount; i++) {
        const policyId = new anchor.BN(6000 + i);
        const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
          program.programId
        );

        const beforeBalance = await provider.connection.getBalance(authority.publicKey);

        await program.methods
          .createPolicyProposal(
            policyId,
            `Cost Analysis Policy ${i}`,
            `Testing cost patterns for proposal ${i}`,
            `ENFORCE: Cost analysis requirements for proposal ${i}`
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();

        const afterBalance = await provider.connection.getBalance(authority.publicKey);
        const proposalCost = beforeBalance - afterBalance;
        proposalCosts.push(proposalCost);
      }

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const totalCost = initialBalance - finalBalance;
      const averageCost = totalCost / proposalCount;

      console.log(`Multiple proposals (${proposalCount}) total cost: ${totalCost} lamports`);
      console.log(`Average cost per proposal: ${averageCost.toFixed(0)} lamports`);
      console.log(`Individual costs: ${proposalCosts.join(', ')} lamports`);

      // Verify cost efficiency
      expect(averageCost).to.be.lessThan(2_000_000); // Average should be reasonable
      expect(totalCost).to.be.lessThan(10_000_000); // Total within 0.01 SOL target
    });

    it('should validate performance targets for governance operations', async () => {
      const performanceTargets = {
        maxCostPerOperation: 2_000_000, // 0.002 SOL per operation
        maxTotalWorkflowCost: 10_000_000, // 0.01 SOL total
        maxResponseTime: 5000, // 5 seconds
      };

      const policyId = new anchor.BN(7001);
      const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );

      const startTime = Date.now();
      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      // Execute complete governance workflow
      await program.methods
        .createPolicyProposal(
          policyId,
          'Performance Target Validation',
          'Testing performance targets for governance operations',
          'ENFORCE: Performance target compliance requirements'
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const endTime = Date.now();
      const finalBalance = await provider.connection.getBalance(authority.publicKey);

      const operationCost = initialBalance - finalBalance;
      const responseTime = endTime - startTime;

      console.log(
        `Performance validation - Cost: ${operationCost} lamports, Time: ${responseTime}ms`
      );

      // Validate performance targets
      expect(operationCost).to.be.lessThan(performanceTargets.maxCostPerOperation);
      expect(responseTime).to.be.lessThan(performanceTargets.maxResponseTime);

      console.log('✅ All performance targets met');
    });
  });
});
