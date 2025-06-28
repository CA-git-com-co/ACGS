/**
 * Mock implementation of Solana wallet adapter packages for Jest tests
 */

// Mock wallet adapter network
const WalletAdapterNetwork = {
  Mainnet: 'mainnet-beta',
  Testnet: 'testnet',
  Devnet: 'devnet',
};

// Mock wallet ready state
const WalletReadyState = {
  Installed: 'Installed',
  NotDetected: 'NotDetected',
  Loadable: 'Loadable',
  Unsupported: 'Unsupported',
};

// Mock wallet error classes
class WalletError extends Error {
  constructor(message) {
    super(message);
    this.name = 'WalletError';
  }
}

class WalletNotConnectedError extends WalletError {
  constructor() {
    super('Wallet not connected');
    this.name = 'WalletNotConnectedError';
  }
}

class WalletNotReadyError extends WalletError {
  constructor() {
    super('Wallet not ready');
    this.name = 'WalletNotReadyError';
  }
}

// Mock base wallet adapter
class BaseWalletAdapter {
  constructor() {
    this.name = 'Mock Wallet';
    this.url = 'https://mock-wallet.com';
    this.icon = 'data:image/svg+xml;base64,mock-icon';
    this.readyState = WalletReadyState.Installed;
    this.publicKey = null;
    this.connected = false;
    this.connecting = false;
    this.supportedTransactionVersions = new Set(['legacy', 0]);
  }

  async connect() {
    this.connecting = true;
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 100));
    this.connected = true;
    this.connecting = false;
    this.publicKey = { toString: () => 'MockPublicKey123' };
    this.emit('connect', this.publicKey);
  }

  async disconnect() {
    this.connected = false;
    this.publicKey = null;
    this.emit('disconnect');
  }

  async signTransaction(transaction) {
    if (!this.connected) throw new WalletNotConnectedError();
    return { ...transaction, signature: 'mock-signature' };
  }

  async signAllTransactions(transactions) {
    if (!this.connected) throw new WalletNotConnectedError();
    return transactions.map(tx => ({ ...tx, signature: 'mock-signature' }));
  }

  async signMessage(message) {
    if (!this.connected) throw new WalletNotConnectedError();
    return new Uint8Array([1, 2, 3, 4, 5]); // Mock signature
  }

  emit(event, ...args) {
    // Mock event emitter
    if (this.listeners && this.listeners[event]) {
      this.listeners[event].forEach(listener => listener(...args));
    }
  }

  on(event, listener) {
    if (!this.listeners) this.listeners = {};
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(listener);
  }

  off(event, listener) {
    if (this.listeners && this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(l => l !== listener);
    }
  }
}

// Mock specific wallet adapters
class PhantomWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Phantom';
    this.url = 'https://phantom.app';
  }
}

class SolflareWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Solflare';
    this.url = 'https://solflare.com';
  }
}

// Mock wallet adapter context
const useWallet = () => ({
  wallet: null,
  publicKey: null,
  connected: false,
  connecting: false,
  disconnecting: false,
  select: jest.fn(),
  connect: jest.fn(),
  disconnect: jest.fn(),
  sendTransaction: jest.fn(),
  signTransaction: jest.fn(),
  signAllTransactions: jest.fn(),
  signMessage: jest.fn(),
});

const useConnection = () => ({
  connection: {
    getLatestBlockhash: jest.fn().mockResolvedValue({
      blockhash: 'mock-blockhash',
      lastValidBlockHeight: 123456,
    }),
    sendTransaction: jest.fn().mockResolvedValue('mock-signature'),
    confirmTransaction: jest.fn().mockResolvedValue({ value: { err: null } }),
    getBalance: jest.fn().mockResolvedValue(1000000000), // 1 SOL in lamports
  },
});

// Mock wallet modal provider
const WalletModalProvider = ({ children }) => children;

// Mock wallet provider
const WalletProvider = ({ children }) => children;
const ConnectionProvider = ({ children }) => children;

module.exports = {
  WalletAdapterNetwork,
  WalletReadyState,
  WalletError,
  WalletNotConnectedError,
  WalletNotReadyError,
  BaseWalletAdapter,
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  useWallet,
  useConnection,
  WalletProvider,
  ConnectionProvider,
  WalletModalProvider,
};
