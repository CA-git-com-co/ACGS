/**
 * Mock implementation of @solana/wallet-adapter-react for Jest tests
 */

import React from 'react';

// Mock wallet context hooks
export const useWallet = () => ({
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

export const useConnection = () => ({
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

// Mock wallet provider components
export const WalletProvider = ({ children }) => {
  return React.createElement('div', { 'data-testid': 'wallet-provider' }, children);
};

export const ConnectionProvider = ({ children }) => {
  return React.createElement('div', { 'data-testid': 'connection-provider' }, children);
};

// Mock wallet context
export const WalletContext = React.createContext({
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

export const ConnectionContext = React.createContext({
  connection: {
    getLatestBlockhash: jest.fn().mockResolvedValue({
      blockhash: 'mock-blockhash',
      lastValidBlockHeight: 123456,
    }),
    sendTransaction: jest.fn().mockResolvedValue('mock-signature'),
    confirmTransaction: jest.fn().mockResolvedValue({ value: { err: null } }),
    getBalance: jest.fn().mockResolvedValue(1000000000),
  },
});
