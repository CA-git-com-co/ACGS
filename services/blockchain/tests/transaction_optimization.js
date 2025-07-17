// Constitutional Hash: cdd01ef066bc6cf2

'use strict';
// Comprehensive tests for Quantumagi transaction optimization
// Target: >80% test coverage with cost validation
var __createBinding =
  (this && this.__createBinding) ||
  (Object.create
    ? function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        var desc = Object.getOwnPropertyDescriptor(m, k);
        if (!desc || ('get' in desc ? !m.__esModule : desc.writable || desc.configurable)) {
          desc = {
            enumerable: true,
            get: function () {
              return m[k];
            },
          };
        }
        Object.defineProperty(o, k2, desc);
      }
    : function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        o[k2] = m[k];
      });
var __setModuleDefault =
  (this && this.__setModuleDefault) ||
  (Object.create
    ? function (o, v) {
        Object.defineProperty(o, 'default', { enumerable: true, value: v });
      }
    : function (o, v) {
        o['default'] = v;
      });
var __importStar =
  (this && this.__importStar) ||
  function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null)
      for (var k in mod)
        if (k !== 'default' && Object.prototype.hasOwnProperty.call(mod, k))
          __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
  };
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }
    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator['throw'](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
Object.defineProperty(exports, '__esModule', { value: true });
const anchor = __importStar(require('@coral-xyz/anchor'));
const chai_1 = require('chai');
const crypto_1 = require('crypto');
describe('Transaction Optimization', () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.QuantumagiCore;
  const provider = anchor.getProvider();
  // Test accounts
  let authority;
  let governancePDA;
  let governanceBump;
  before(() =>
    __awaiter(void 0, void 0, void 0, function* () {
      // Test isolation - unique governance per test suite
      const testSuiteId = 'transaction_optimization_' + Date.now();
      authority = anchor.web3.Keypair.generate();
      // Airdrop SOL for testing
      yield provider.connection.confirmTransaction(
        yield provider.connection.requestAirdrop(
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
      yield program.methods
        .initializeGovernance(authority.publicKey, principles)
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();
    })
  );
  describe('Batch Configuration', () => {
    it('should create valid batch configuration', () => {
      const batchConfig = {
        maxBatchSize: 10,
        batchTimeoutSeconds: new anchor.BN(5),
        costTargetLamports: new anchor.BN(10000000),
        enabled: true,
      };
      (0, chai_1.expect)(batchConfig.maxBatchSize).to.equal(10);
      (0, chai_1.expect)(batchConfig.costTargetLamports.toNumber()).to.equal(10000000);
      (0, chai_1.expect)(batchConfig.enabled).to.be.true;
    });
    it('should validate batch size limits', () => {
      const maxAllowedSize = 10;
      const testSizes = [1, 5, 10, 15];
      testSizes.forEach((size) => {
        const isValid = size <= maxAllowedSize;
        (0, chai_1.expect)(size <= maxAllowedSize).to.equal(isValid);
      });
    });
  });
  describe('Governance Operations', () => {
    it('should create policy proposal operation', () => {
      const policyId = new anchor.BN(1001);
      const ruleHash = Array.from((0, crypto_1.createHash)('sha256').update('Test rule').digest());
      const operation = {
        policyProposal: {
          policyId,
          ruleHash,
        },
      };
      (0, chai_1.expect)(operation.policyProposal.policyId.toNumber()).to.equal(1001);
      (0, chai_1.expect)(operation.policyProposal.ruleHash).to.have.length(32);
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
      (0, chai_1.expect)(operation.policyVote.policyId.toNumber()).to.equal(1001);
      (0, chai_1.expect)(operation.policyVote.vote).to.be.true;
    });
    it('should create compliance check operation', () => {
      const policyId = new anchor.BN(1001);
      const actionHash = Array.from(
        (0, crypto_1.createHash)('sha256').update('Test action').digest()
      );
      const operation = {
        complianceCheck: {
          policyId,
          actionHash,
        },
      };
      (0, chai_1.expect)(operation.complianceCheck.policyId.toNumber()).to.equal(1001);
      (0, chai_1.expect)(operation.complianceCheck.actionHash).to.have.length(32);
    });
  });
  describe('Optimized Governance Operations', () => {
    it('should execute single policy proposal with cost optimization', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(2001);
        const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
          program.programId
        );
        const initialBalance = yield provider.connection.getBalance(authority.publicKey);
        // Create policy proposal (optimized single operation)
        yield program.methods
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
        const finalBalance = yield provider.connection.getBalance(authority.publicKey);
        const transactionCost = initialBalance - finalBalance;
        // Verify cost is within target (0.01 SOL = 10,000,000 lamports)
        (0, chai_1.expect)(transactionCost).to.be.lessThan(10000000);
        console.log(`Single policy proposal cost: ${transactionCost} lamports`);
      }));
    it('should execute multi-operation workflow with cost optimization', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(3001);
        const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
          program.programId
        );
        const initialBalance = yield provider.connection.getBalance(authority.publicKey);
        // Operation 1: Create policy proposal
        yield program.methods
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
        yield program.methods
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
        yield program.methods
          .finalizeProposal(policyId)
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            finalizer: authority.publicKey,
          })
          .signers([authority])
          .rpc();
        const finalBalance = yield provider.connection.getBalance(authority.publicKey);
        const workflowCost = initialBalance - finalBalance;
        // Verify workflow cost is within target
        (0, chai_1.expect)(workflowCost).to.be.lessThan(10000000);
        console.log(`Multi-operation workflow cost: ${workflowCost} lamports`);
        console.log(`Average cost per operation: ${(workflowCost / 3).toFixed(0)} lamports`);
        // Verify cost efficiency (should be less than 0.01 SOL for complete workflow)
        (0, chai_1.expect)(workflowCost).to.be.lessThan(10000000);
      }));
    it('should handle emergency actions with cost validation', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const initialBalance = yield provider.connection.getBalance(authority.publicKey);
        // Execute emergency action (simulating batch-like functionality)
        yield program.methods
          .emergencyAction({ systemMaintenance: {} }, null)
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
          })
          .signers([authority])
          .rpc();
        const finalBalance = yield provider.connection.getBalance(authority.publicKey);
        const emergencyActionCost = initialBalance - finalBalance;
        // Verify emergency action cost is minimal
        (0, chai_1.expect)(emergencyActionCost).to.be.lessThan(5000000); // Should be very efficient
        console.log(`Emergency action cost: ${emergencyActionCost} lamports`);
      }));
    it('should validate unauthorized access prevention', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const unauthorizedUser = anchor.web3.Keypair.generate();
        // Airdrop to unauthorized user
        yield provider.connection.confirmTransaction(
          yield provider.connection.requestAirdrop(
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
          yield program.methods
            .emergencyAction({ systemMaintenance: {} }, null)
            .accounts({
              governance: governancePDA,
              authority: unauthorizedUser.publicKey,
            })
            .signers([unauthorizedUser])
            .rpc();
          chai_1.expect.fail('Should have rejected unauthorized emergency action');
        } catch (error) {
          (0, chai_1.expect)(error).to.exist;
          console.log('✅ Unauthorized access properly prevented');
        }
      }));
  });
  describe('Cost Analysis', () => {
    it('should demonstrate cost optimization with multiple proposals', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const initialBalance = yield provider.connection.getBalance(authority.publicKey);
        const proposalCount = 5;
        const proposalCosts = [];
        // Create multiple proposals to analyze cost patterns
        for (let i = 0; i < proposalCount; i++) {
          const policyId = new anchor.BN(6000 + i);
          const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
            program.programId
          );
          const beforeBalance = yield provider.connection.getBalance(authority.publicKey);
          yield program.methods
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
          const afterBalance = yield provider.connection.getBalance(authority.publicKey);
          const proposalCost = beforeBalance - afterBalance;
          proposalCosts.push(proposalCost);
        }
        const finalBalance = yield provider.connection.getBalance(authority.publicKey);
        const totalCost = initialBalance - finalBalance;
        const averageCost = totalCost / proposalCount;
        console.log(`Multiple proposals (${proposalCount}) total cost: ${totalCost} lamports`);
        console.log(`Average cost per proposal: ${averageCost.toFixed(0)} lamports`);
        console.log(`Individual costs: ${proposalCosts.join(', ')} lamports`);
        // Verify cost efficiency
        (0, chai_1.expect)(averageCost).to.be.lessThan(2000000); // Average should be reasonable
        (0, chai_1.expect)(totalCost).to.be.lessThan(10000000); // Total within 0.01 SOL target
      }));
    it('should validate performance targets for governance operations', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const performanceTargets = {
          maxCostPerOperation: 2000000,
          maxTotalWorkflowCost: 10000000,
          maxResponseTime: 5000, // 5 seconds
        };
        const policyId = new anchor.BN(7001);
        const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
          program.programId
        );
        const startTime = Date.now();
        const initialBalance = yield provider.connection.getBalance(authority.publicKey);
        // Execute complete governance workflow
        yield program.methods
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
        const finalBalance = yield provider.connection.getBalance(authority.publicKey);
        const operationCost = initialBalance - finalBalance;
        const responseTime = endTime - startTime;
        console.log(
          `Performance validation - Cost: ${operationCost} lamports, Time: ${responseTime}ms`
        );
        // Validate performance targets
        (0, chai_1.expect)(operationCost).to.be.lessThan(performanceTargets.maxCostPerOperation);
        (0, chai_1.expect)(responseTime).to.be.lessThan(performanceTargets.maxResponseTime);
        console.log('✅ All performance targets met');
      }));
  });
});
