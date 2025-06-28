/**
 * Mock implementation of @solana/wallet-adapter-base for Jest tests
 */

// Mock wallet adapter network - this is the key export that was failing
export const WalletAdapterNetwork = {
  Mainnet: 'mainnet-beta',
  Testnet: 'testnet',
  Devnet: 'devnet',
};

// Mock wallet ready state
export const WalletReadyState = {
  Installed: 'Installed',
  NotDetected: 'NotDetected',
  Loadable: 'Loadable',
  Unsupported: 'Unsupported',
};

// Mock wallet error classes
export class WalletError extends Error {
  constructor(message) {
    super(message);
    this.name = 'WalletError';
  }
}

export class WalletNotConnectedError extends WalletError {
  constructor() {
    super('Wallet not connected');
    this.name = 'WalletNotConnectedError';
  }
}

export class WalletNotReadyError extends WalletError {
  constructor() {
    super('Wallet not ready');
    this.name = 'WalletNotReadyError';
  }
}

// Mock base wallet adapter
export class BaseWalletAdapter {
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
    return new Uint8Array([1, 2, 3, 4, 5]);
  }

  emit(event, ...args) {
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
