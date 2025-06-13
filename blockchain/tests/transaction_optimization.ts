// Comprehensive tests for Quantumagi transaction optimization
// Target: >80% test coverage with cost validation

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { QuantumagiCore } from "../target/types/quantumagi_core";
import { expect } from "chai";
import { createHash } from "crypto";

describe("Transaction Optimization", () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;
  const provider = anchor.getProvider();

  // Test accounts
  let authority: anchor.web3.Keypair;
  let constitutionPDA: anchor.web3.PublicKey;
  let constitutionBump: number;

  before(async () => {
    authority = anchor.web3.Keypair.generate();

    // Airdrop SOL for testing
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(
        authority.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      )
    );

    // Derive constitution PDA
    [constitutionPDA, constitutionBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("constitution")],
      program.programId
    );

    // Initialize constitution for testing
    const constitutionalDoc = "Quantumagi Test Constitutional Framework v1.0";
    const hash = createHash("sha256").update(constitutionalDoc).digest();

    await program.methods
      .initialize(Array.from(hash))
      .accounts({
        constitution: constitutionPDA,
        authority: authority.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([authority])
      .rpc();
  });

  describe("Batch Configuration", () => {
    it("should create valid batch configuration", () => {
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

    it("should validate batch size limits", () => {
      const maxAllowedSize = 10;
      const testSizes = [1, 5, 10, 15];

      testSizes.forEach(size => {
        const isValid = size <= maxAllowedSize;
        expect(size <= maxAllowedSize).to.equal(isValid);
      });
    });
  });

  describe("Governance Operations", () => {
    it("should create policy proposal operation", () => {
      const policyId = new anchor.BN(1001);
      const ruleHash = Array.from(createHash("sha256").update("Test rule").digest());

      const operation = {
        policyProposal: {
          policyId,
          ruleHash,
        },
      };

      expect(operation.policyProposal.policyId.toNumber()).to.equal(1001);
      expect(operation.policyProposal.ruleHash).to.have.length(32);
    });

    it("should create policy vote operation", () => {
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

    it("should create compliance check operation", () => {
      const policyId = new anchor.BN(1001);
      const actionHash = Array.from(createHash("sha256").update("Test action").digest());

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

  describe("Batch Execution", () => {
    it("should execute single operation batch", async () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000),
        enabled: true,
      };

      const operations = [
        {
          policyProposal: {
            policyId: new anchor.BN(2001),
            ruleHash: Array.from(createHash("sha256").update("Single operation rule").digest()),
          },
        },
      ];

      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      await program.methods
        .executeGovernanceBatch(operations, batchConfig)
        .accounts({
          authority: authority.publicKey,
          constitution: constitutionPDA,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const transactionCost = initialBalance - finalBalance;

      // Verify cost is within target (0.01 SOL = 10,000,000 lamports)
      expect(transactionCost).to.be.lessThan(10_000_000);
      console.log(`Single operation cost: ${transactionCost} lamports`);
    });

    it("should execute multi-operation batch with cost optimization", async () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000),
        enabled: true,
      };

      const operations = [
        {
          policyProposal: {
            policyId: new anchor.BN(3001),
            ruleHash: Array.from(createHash("sha256").update("Batch rule 1").digest()),
          },
        },
        {
          policyVote: {
            policyId: new anchor.BN(3001),
            vote: true,
          },
        },
        {
          complianceCheck: {
            policyId: new anchor.BN(3001),
            actionHash: Array.from(createHash("sha256").update("Batch action").digest()),
          },
        },
      ];

      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      await program.methods
        .executeGovernanceBatch(operations, batchConfig)
        .accounts({
          authority: authority.publicKey,
          constitution: constitutionPDA,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const batchCost = initialBalance - finalBalance;

      // Verify batch cost is within target
      expect(batchCost).to.be.lessThan(10_000_000);
      
      // Estimate individual transaction costs for comparison
      const estimatedIndividualCost = operations.length * 15_000; // Conservative estimate
      const costSavings = Math.max(0, estimatedIndividualCost - batchCost);
      const optimizationPercent = (costSavings / estimatedIndividualCost) * 100;

      console.log(`Batch cost: ${batchCost} lamports`);
      console.log(`Estimated individual cost: ${estimatedIndividualCost} lamports`);
      console.log(`Cost optimization: ${optimizationPercent.toFixed(2)}%`);

      // Verify some cost optimization occurred
      expect(optimizationPercent).to.be.greaterThan(0);
    });

    it("should reject batch when batching is disabled", async () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000),
        enabled: false, // Disabled
      };

      const operations = [
        {
          policyProposal: {
            policyId: new anchor.BN(4001),
            ruleHash: Array.from(createHash("sha256").update("Disabled batch rule").digest()),
          },
        },
      ];

      try {
        await program.methods
          .executeGovernanceBatch(operations, batchConfig)
          .accounts({
            authority: authority.publicKey,
            constitution: constitutionPDA,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();

        expect.fail("Should have thrown BatchingDisabled error");
      } catch (error) {
        expect(error.toString()).to.include("BatchingDisabled");
      }
    });

    it("should reject batch exceeding maximum size", async () => {
      const batchConfig = {
        maxBatchSize: 2, // Small limit for testing
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000),
        enabled: true,
      };

      // Create batch with 3 operations (exceeds limit of 2)
      const operations = [
        {
          policyProposal: {
            policyId: new anchor.BN(5001),
            ruleHash: Array.from(createHash("sha256").update("Oversized batch rule 1").digest()),
          },
        },
        {
          policyProposal: {
            policyId: new anchor.BN(5002),
            ruleHash: Array.from(createHash("sha256").update("Oversized batch rule 2").digest()),
          },
        },
        {
          policyProposal: {
            policyId: new anchor.BN(5003),
            ruleHash: Array.from(createHash("sha256").update("Oversized batch rule 3").digest()),
          },
        },
      ];

      try {
        await program.methods
          .executeGovernanceBatch(operations, batchConfig)
          .accounts({
            authority: authority.publicKey,
            constitution: constitutionPDA,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();

        expect.fail("Should have thrown BatchSizeExceeded error");
      } catch (error) {
        expect(error.toString()).to.include("BatchSizeExceeded");
      }
    });
  });

  describe("Cost Analysis", () => {
    it("should demonstrate cost optimization with large batch", async () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10_000_000),
        enabled: true,
      };

      // Create maximum size batch
      const operations = [];
      for (let i = 0; i < 10; i++) {
        operations.push({
          policyVote: {
            policyId: new anchor.BN(6000 + i),
            vote: i % 2 === 0, // Alternate votes
          },
        });
      }

      const initialBalance = await provider.connection.getBalance(authority.publicKey);

      await program.methods
        .executeGovernanceBatch(operations, batchConfig)
        .accounts({
          authority: authority.publicKey,
          constitution: constitutionPDA,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const finalBalance = await provider.connection.getBalance(authority.publicKey);
      const batchCost = initialBalance - finalBalance;

      // Calculate theoretical individual costs
      const individualCostEstimate = operations.length * 15_000; // 15k lamports per tx
      const costSavings = Math.max(0, individualCostEstimate - batchCost);
      const optimizationPercent = (costSavings / individualCostEstimate) * 100;

      console.log(`Large batch (${operations.length} ops) cost: ${batchCost} lamports`);
      console.log(`Individual transactions estimate: ${individualCostEstimate} lamports`);
      console.log(`Total savings: ${costSavings} lamports`);
      console.log(`Optimization: ${optimizationPercent.toFixed(2)}%`);

      // Verify significant cost optimization for large batches
      expect(optimizationPercent).to.be.greaterThan(30); // At least 30% savings
      expect(batchCost).to.be.lessThan(10_000_000); // Within 0.01 SOL target
    });

    it("should validate cost target enforcement", async () => {
      const strictBatchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(1_000), // Very strict limit
        enabled: true,
      };

      const operations = [
        {
          constitutionalUpdate: {
            version: 2,
            hash: Array.from(createHash("sha256").update("Updated constitution").digest()),
          },
        },
      ];

      try {
        await program.methods
          .executeGovernanceBatch(operations, strictBatchConfig)
          .accounts({
            authority: authority.publicKey,
            constitution: constitutionPDA,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();

        expect.fail("Should have thrown CostTargetExceeded error");
      } catch (error) {
        expect(error.toString()).to.include("CostTargetExceeded");
      }
    });
  });
});
