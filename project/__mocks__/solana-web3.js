/**
 * Mock implementation of @solana/web3.js for Jest tests
 */

// Mock cluster API URL function
const clusterApiUrl = cluster => {
  const urls = {
    'mainnet-beta': 'https://api.mainnet-beta.solana.com',
    testnet: 'https://api.testnet.solana.com',
    devnet: 'https://api.devnet.solana.com',
  };
  return urls[cluster] || urls['devnet'];
};

// Mock PublicKey class
class PublicKey {
  constructor(value) {
    this.value = value || 'MockPublicKey123';
  }

  toString() {
    return this.value;
  }

  toBase58() {
    return this.value;
  }

  equals(other) {
    return this.value === other.value;
  }

  static isOnCurve(pubkey) {
    return true;
  }
}

// Mock Connection class
class Connection {
  constructor(endpoint, commitment) {
    this.endpoint = endpoint;
    this.commitment = commitment || 'confirmed';
  }

  async getLatestBlockhash() {
    return {
      blockhash: 'mock-blockhash-' + Date.now(),
      lastValidBlockHeight: 123456,
    };
  }

  async getBalance(publicKey) {
    return 1000000000; // 1 SOL in lamports
  }

  async sendTransaction(transaction, signers, options) {
    return 'mock-transaction-signature-' + Date.now();
  }

  async confirmTransaction(signature, commitment) {
    return {
      value: { err: null },
    };
  }

  async getAccountInfo(publicKey) {
    return {
      executable: false,
      owner: new PublicKey('11111111111111111111111111111111'),
      lamports: 1000000000,
      data: Buffer.alloc(0),
    };
  }
}

// Mock Transaction class
class Transaction {
  constructor() {
    this.instructions = [];
    this.signatures = [];
    this.feePayer = null;
    this.recentBlockhash = null;
  }

  add(instruction) {
    this.instructions.push(instruction);
    return this;
  }

  sign(...signers) {
    this.signatures = signers.map(signer => ({
      publicKey: signer.publicKey,
      signature: 'mock-signature',
    }));
  }

  serialize() {
    return Buffer.from('mock-serialized-transaction');
  }
}

// Mock TransactionInstruction class
class TransactionInstruction {
  constructor({ keys, programId, data }) {
    this.keys = keys || [];
    this.programId = programId;
    this.data = data || Buffer.alloc(0);
  }
}

// Mock Keypair class
class Keypair {
  constructor() {
    this.publicKey = new PublicKey('MockKeypair' + Math.random());
    this.secretKey = new Uint8Array(64);
  }

  static generate() {
    return new Keypair();
  }

  static fromSecretKey(secretKey) {
    const keypair = new Keypair();
    keypair.secretKey = secretKey;
    return keypair;
  }
}

// Mock SystemProgram
const SystemProgram = {
  programId: new PublicKey('11111111111111111111111111111111'),

  transfer: ({ fromPubkey, toPubkey, lamports }) => {
    return new TransactionInstruction({
      keys: [
        { pubkey: fromPubkey, isSigner: true, isWritable: true },
        { pubkey: toPubkey, isSigner: false, isWritable: true },
      ],
      programId: SystemProgram.programId,
      data: Buffer.from([2, 0, 0, 0, ...new Uint8Array(8)]), // Mock transfer instruction
    });
  },

  createAccount: ({ fromPubkey, newAccountPubkey, lamports, space, programId }) => {
    return new TransactionInstruction({
      keys: [
        { pubkey: fromPubkey, isSigner: true, isWritable: true },
        { pubkey: newAccountPubkey, isSigner: true, isWritable: true },
      ],
      programId: SystemProgram.programId,
      data: Buffer.from([0, 0, 0, 0, ...new Uint8Array(8)]), // Mock create account instruction
    });
  },
};

// Mock LAMPORTS_PER_SOL constant
const LAMPORTS_PER_SOL = 1000000000;

module.exports = {
  clusterApiUrl,
  PublicKey,
  Connection,
  Transaction,
  TransactionInstruction,
  Keypair,
  SystemProgram,
  LAMPORTS_PER_SOL,
};
