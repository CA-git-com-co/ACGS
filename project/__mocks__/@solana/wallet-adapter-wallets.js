/**
 * Mock implementation of @solana/wallet-adapter-wallets for Jest tests
 */

// Mock wallet ready state
const WalletReadyState = {
  Installed: 'Installed',
  NotDetected: 'NotDetected',
  Loadable: 'Loadable',
  Unsupported: 'Unsupported',
};

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
}

// Mock specific wallet adapters
export class PhantomWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Phantom';
    this.url = 'https://phantom.app';
    this.icon = 'data:image/svg+xml;base64,phantom-icon';
    this.readyState = WalletReadyState.Installed;
  }
}

export class SolflareWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Solflare';
    this.url = 'https://solflare.com';
    this.icon = 'data:image/svg+xml;base64,solflare-icon';
    this.readyState = WalletReadyState.Installed;
  }
}

export class TorusWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Torus';
    this.url = 'https://tor.us';
    this.icon = 'data:image/svg+xml;base64,torus-icon';
    this.readyState = WalletReadyState.Loadable;
  }
}

export class LedgerWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Ledger';
    this.url = 'https://www.ledger.com';
    this.icon = 'data:image/svg+xml;base64,ledger-icon';
    this.readyState = WalletReadyState.Loadable;
  }
}

export class SolletWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'Sollet';
    this.url = 'https://www.sollet.io';
    this.icon = 'data:image/svg+xml;base64,sollet-icon';
    this.readyState = WalletReadyState.Loadable;
  }
}

export class MathWalletAdapter extends BaseWalletAdapter {
  constructor() {
    super();
    this.name = 'MathWallet';
    this.url = 'https://mathwallet.org';
    this.icon = 'data:image/svg+xml;base64,math-icon';
    this.readyState = WalletReadyState.NotDetected;
  }
}
