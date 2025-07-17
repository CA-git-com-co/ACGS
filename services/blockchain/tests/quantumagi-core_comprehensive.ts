// Constitutional Hash: cdd01ef066bc6cf2

import * as anchor from '@coral-xyz/anchor';
import { Program } from '@coral-xyz/anchor';
import { QuantumagiCore } from '../target/types/quantumagi_core';
import { expect } from 'chai';

describe('quantumagi-core', () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;

  // Test accounts
  let authority: anchor.web3.Keypair;
  let governancePDA: anchor.web3.PublicKey;
  let proposalPDA: anchor.web3.PublicKey;

  before(async () => {
    // Test isolation - unique governance per test suite
    const testSuiteId = 'quantumagi-core_comprehensive_' + Date.now();
    authority = anchor.web3.Keypair.generate();

    // Generate PDAs - Use short seeds to avoid max length error
    [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from('governance'), Buffer.from('comp')],
      program.programId
    );

    // Airdrop SOL for testing
    await program.provider.connection.confirmTransaction(
      await program.provider.connection.requestAirdrop(
        authority.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      )
    );
  });

  describe('Governance Management', () => {
    it('Should initialize governance successfully', async () => {
      // Test governance initialization
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

      const governanceAccount = await program.account.governanceState.fetch(governancePDA);

      expect(governanceAccount.principles.length).to.equal(principles.length);
      expect(governanceAccount.authority.toString()).to.equal(authority.publicKey.toString());
    });

    it('Should execute emergency actions with proper authority', async () => {
      // Test emergency governance actions
      await program.methods
        .emergencyAction({ systemMaintenance: {} }, null)
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      // Emergency action should complete without error
      console.log('Emergency action executed successfully');
    });

    it('Should reject unauthorized emergency actions', async () => {
      const unauthorizedUser = anchor.web3.Keypair.generate();

      try {
        await program.methods
          .emergencyAction({ systemMaintenance: {} }, null)
          .accounts({
            governance: governancePDA,
            authority: unauthorizedUser.publicKey,
          })
          .signers([unauthorizedUser])
          .rpc();

        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('unauthorized');
      }
    });
  });

  describe('Policy Management', () => {
    it('Should create policy proposal successfully', async () => {
      const policyId = new anchor.BN(Date.now());
      const title = 'Test Policy';
      const description = 'Test policy description';
      const policyText = 'ENFORCE: Test policy content for safety compliance';

      [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
        program.programId
      );

      await program.methods
        .createPolicyProposal(policyId, title, description, policyText)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);

      expect(proposalAccount.policyText).to.equal(policyText);
      expect(proposalAccount.title).to.equal(title);
      expect(proposalAccount.status).to.deep.equal({ active: {} });
    });

    it('Should vote on proposal', async () => {
      const policyId = new anchor.BN(Date.now() - 1000); // Use the policy ID from previous test
      const vote = true; // Support
      const votingPower = new anchor.BN(1);

      const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from('vote_record'), policyId.toBuffer('le', 8), authority.publicKey.toBuffer()],
        program.programId
      );

      await program.methods
        .voteOnProposal(policyId, vote, votingPower)
        .accounts({
          proposal: proposalPDA,
          voteRecord: voteRecordPDA,
          voter: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const voteRecordAccount = await program.account.voteRecord.fetch(voteRecordPDA);
      expect(voteRecordAccount.vote).to.equal(vote);
      expect(voteRecordAccount.votingPower.toNumber()).to.equal(1);
    });

    it('Should finalize proposal after voting', async () => {
      const policyId = new anchor.BN(Date.now() - 1000); // Use the same policy ID

      await program.methods
        .finalizeProposal(policyId)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          finalizer: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);
      expect(proposalAccount.status).to.deep.equal({ approved: {} });
    });
  });

  describe('System Validation', () => {
    it('Should validate governance state', async () => {
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);

      expect(governanceAccount.authority.toString()).to.equal(authority.publicKey.toString());
      expect(governanceAccount.principles.length).to.be.greaterThan(0);
      expect(governanceAccount.totalPolicies).to.be.greaterThan(0);
    });

    it('Should validate proposal state', async () => {
      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);

      expect(proposalAccount.status).to.deep.equal({ approved: {} });
      expect(proposalAccount.proposer.toString()).to.equal(authority.publicKey.toString());
      expect(proposalAccount.votesFor.toNumber()).to.be.greaterThan(0);
    });
  });

  describe('Emergency Actions', () => {
    it('Should execute emergency suspension', async () => {
      const policyId = new anchor.BN(Date.now() - 1000);

      await program.methods
        .emergencyAction({ suspendProposal: {} }, policyId)
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      // Emergency action should complete successfully
      console.log('Emergency suspension executed successfully');
    });
  });
});
