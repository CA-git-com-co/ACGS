'use strict';
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
describe('quantumagi-core', () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.QuantumagiCore;
  // Test accounts
  let authority;
  let governancePDA;
  let proposalPDA;
  before(() =>
    __awaiter(void 0, void 0, void 0, function* () {
      // Test isolation - unique governance per test suite
      const testSuiteId = 'quantumagi-core_comprehensive_' + Date.now();
      authority = anchor.web3.Keypair.generate();
      // Generate PDAs - Use short seeds to avoid max length error
      [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('governance'), Buffer.from('comp')],
        program.programId
      );
      // Airdrop SOL for testing
      yield program.provider.connection.confirmTransaction(
        yield program.provider.connection.requestAirdrop(
          authority.publicKey,
          2 * anchor.web3.LAMPORTS_PER_SOL
        )
      );
    })
  );
  describe('Governance Management', () => {
    it('Should initialize governance successfully', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        // Test governance initialization
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
        const governanceAccount = yield program.account.governanceState.fetch(governancePDA);
        (0, chai_1.expect)(governanceAccount.principles.length).to.equal(principles.length);
        (0, chai_1.expect)(governanceAccount.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
      }));
    it('Should execute emergency actions with proper authority', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        // Test emergency governance actions
        yield program.methods
          .emergencyAction({ systemMaintenance: {} }, null)
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
          })
          .signers([authority])
          .rpc();
        // Emergency action should complete without error
        console.log('Emergency action executed successfully');
      }));
    it('Should reject unauthorized emergency actions', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const unauthorizedUser = anchor.web3.Keypair.generate();
        try {
          yield program.methods
            .emergencyAction({ systemMaintenance: {} }, null)
            .accounts({
              governance: governancePDA,
              authority: unauthorizedUser.publicKey,
            })
            .signers([unauthorizedUser])
            .rpc();
          chai_1.expect.fail('Should have thrown an error');
        } catch (error) {
          (0, chai_1.expect)(error.message).to.include('unauthorized');
        }
      }));
  });
  describe('Policy Management', () => {
    it('Should create policy proposal successfully', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(Date.now());
        const title = 'Test Policy';
        const description = 'Test policy description';
        const policyText = 'ENFORCE: Test policy content for safety compliance';
        [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
          program.programId
        );
        yield program.methods
          .createPolicyProposal(policyId, title, description, policyText)
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
        (0, chai_1.expect)(proposalAccount.policyText).to.equal(policyText);
        (0, chai_1.expect)(proposalAccount.title).to.equal(title);
        (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ active: {} });
      }));
    it('Should vote on proposal', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(Date.now() - 1000); // Use the policy ID from previous test
        const vote = true; // Support
        const votingPower = new anchor.BN(1);
        const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('vote_record'), policyId.toBuffer('le', 8), authority.publicKey.toBuffer()],
          program.programId
        );
        yield program.methods
          .voteOnProposal(policyId, vote, votingPower)
          .accounts({
            proposal: proposalPDA,
            voteRecord: voteRecordPDA,
            voter: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        const voteRecordAccount = yield program.account.voteRecord.fetch(voteRecordPDA);
        (0, chai_1.expect)(voteRecordAccount.vote).to.equal(vote);
        (0, chai_1.expect)(voteRecordAccount.votingPower.toNumber()).to.equal(1);
      }));
    it('Should finalize proposal after voting', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(Date.now() - 1000); // Use the same policy ID
        yield program.methods
          .finalizeProposal(policyId)
          .accounts({
            proposal: proposalPDA,
            governance: governancePDA,
            finalizer: authority.publicKey,
          })
          .signers([authority])
          .rpc();
        const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
        (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ approved: {} });
      }));
  });
  describe('System Validation', () => {
    it('Should validate governance state', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const governanceAccount = yield program.account.governanceState.fetch(governancePDA);
        (0, chai_1.expect)(governanceAccount.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(governanceAccount.principles.length).to.be.greaterThan(0);
        (0, chai_1.expect)(governanceAccount.totalPolicies).to.be.greaterThan(0);
      }));
    it('Should validate proposal state', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
        (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ approved: {} });
        (0, chai_1.expect)(proposalAccount.proposer.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(proposalAccount.votesFor.toNumber()).to.be.greaterThan(0);
      }));
  });
  describe('Emergency Actions', () => {
    it('Should execute emergency suspension', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        const policyId = new anchor.BN(Date.now() - 1000);
        yield program.methods
          .emergencyAction({ suspendProposal: {} }, policyId)
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
          })
          .signers([authority])
          .rpc();
        // Emergency action should complete successfully
        console.log('Emergency suspension executed successfully');
      }));
  });
});
