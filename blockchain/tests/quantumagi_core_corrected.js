'use strict';
// Corrected Test Suite for Quantumagi Core Program
// Demonstrates proper method signatures and account structures
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
describe('Quantumagi Core - Corrected Test Suite', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.QuantumagiCore;
  const authority = provider.wallet;
  // Correct PDAs - Use exact seeds that match the program
  const [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from('governance')],
    program.programId
  );
  describe('✅ Governance Initialization', () => {
    it('should initialize governance with constitutional principles', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const principles = [
          'PC-001: No unauthorized state mutations',
          'GV-001: Democratic governance required',
          'FN-001: Treasury protection mandatory',
        ];
        // ✅ CORRECT: Use initializeGovernance method
        yield program.methods
          .initializeGovernance(authority.publicKey, principles)
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        // ✅ CORRECT: Fetch governanceState account
        const governanceAccount = yield program.account.governanceState.fetch(governancePDA);
        (0, chai_1.expect)(governanceAccount.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(governanceAccount.principles.length).to.equal(principles.length);
        (0, chai_1.expect)(governanceAccount.totalPolicies).to.equal(0);
        (0, chai_1.expect)(governanceAccount.activeProposals).to.equal(0);
        console.log('✅ Governance initialized successfully');
      }));
  });
  describe('✅ Policy Proposal Management', () => {
    let policyId;
    let proposalPDA;
    beforeEach(() => {
      policyId = new anchor.BN(Date.now());
      // ✅ CORRECT: Use "proposal" seed
      [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );
    });
    it('should create policy proposal', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const title = 'Test Governance Policy';
        const description = 'A test policy for governance validation';
        const policyText = 'ENFORCE: All governance actions require proper authorization';
        // ✅ CORRECT: Use createPolicyProposal method
        yield program.methods
          .createPolicyProposal(policyId, title, description, policyText)
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        // ✅ CORRECT: Fetch policyProposal account
        const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
        (0, chai_1.expect)(proposalAccount.policyId.toString()).to.equal(policyId.toString());
        (0, chai_1.expect)(proposalAccount.title).to.equal(title);
        (0, chai_1.expect)(proposalAccount.policyText).to.equal(policyText);
        (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ active: {} });
        console.log('✅ Policy proposal created successfully');
      }));
    it('should vote on proposal', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        // Create proposal first
        yield program.methods
          .createPolicyProposal(
            policyId,
            'Voting Test Policy',
            'Policy for testing voting mechanism',
            'ENFORCE: Voting validation requirements'
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        // ✅ CORRECT: Use "vote" seed (matches program)
        const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('vote'), policyId.toBuffer('le', 8), authority.publicKey.toBuffer()],
          program.programId
        );
        // ✅ CORRECT: Use voteOnProposal method with proper parameters
        yield program.methods
          .voteOnProposal(policyId, true, new anchor.BN(1)) // policyId, vote, votingPower
          .accounts({
            proposal: proposalPDA,
            voteRecord: voteRecordPDA,
            voter: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        // ✅ CORRECT: Fetch voteRecord account
        const voteRecordAccount = yield program.account.voteRecord.fetch(voteRecordPDA);
        (0, chai_1.expect)(voteRecordAccount.vote).to.equal(true);
        (0, chai_1.expect)(voteRecordAccount.votingPower.toNumber()).to.equal(1);
        (0, chai_1.expect)(voteRecordAccount.voter.toString()).to.equal(
          authority.publicKey.toString()
        );
        console.log('✅ Vote cast successfully');
      }));
    it('should finalize proposal', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        // Create proposal first
        yield program.methods
          .createPolicyProposal(
            policyId,
            'Finalize Test Policy',
            'Policy for testing finalization',
            'ENFORCE: Finalization validation requirements'
          )
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        // ✅ CORRECT: Use finalizeProposal method
        yield program.methods
          .finalizeProposal(policyId)
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            finalizer: authority.publicKey,
          })
          .rpc();
        const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
        (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ approved: {} });
        console.log('✅ Proposal finalized successfully');
      }));
  });
  describe('✅ Emergency Actions', () => {
    it('should execute emergency action', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        // ✅ CORRECT: Use emergencyAction method
        yield program.methods
          .emergencyAction(
            { systemMaintenance: {} }, // EmergencyActionType
            null // No specific policy target
          )
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
          })
          .rpc();
        console.log('✅ Emergency action executed successfully');
      }));
  });
  describe('✅ System Validation', () => {
    it('should validate governance state', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const governanceAccount = yield program.account.governanceState.fetch(governancePDA);
        (0, chai_1.expect)(governanceAccount.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(governanceAccount.principles.length).to.be.greaterThan(0);
        // Note: totalPolicies starts at 0 and increments when policies are finalized
        (0, chai_1.expect)(governanceAccount.totalPolicies).to.be.greaterThanOrEqual(0);
        console.log('✅ Governance state validation successful');
        console.log(`   Authority: ${governanceAccount.authority.toString().substring(0, 8)}...`);
        console.log(`   Principles: ${governanceAccount.principles.length}`);
        console.log(`   Total Policies: ${governanceAccount.totalPolicies}`);
      }));
  });
});
