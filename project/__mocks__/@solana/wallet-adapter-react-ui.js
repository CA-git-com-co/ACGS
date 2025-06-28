/**
 * Mock implementation of @solana/wallet-adapter-react-ui for Jest tests
 */

import React from 'react';

// Mock wallet modal provider
export const WalletModalProvider = ({ children }) => {
  return React.createElement('div', { 'data-testid': 'wallet-modal-provider' }, children);
};

// Mock wallet modal context
export const useWalletModal = () => ({
  visible: false,
  setVisible: jest.fn(),
});

// Mock wallet multi button
export const WalletMultiButton = props => {
  return React.createElement(
    'button',
    {
      'data-testid': 'wallet-multi-button',
      onClick: props.onClick,
      disabled: props.disabled,
      className: props.className,
    },
    props.children || 'Connect Wallet'
  );
};

// Mock wallet disconnect button
export const WalletDisconnectButton = props => {
  return React.createElement(
    'button',
    {
      'data-testid': 'wallet-disconnect-button',
      onClick: props.onClick,
      disabled: props.disabled,
      className: props.className,
    },
    props.children || 'Disconnect'
  );
};

// Mock wallet modal
export const WalletModal = props => {
  return React.createElement(
    'div',
    {
      'data-testid': 'wallet-modal',
      style: { display: props.visible ? 'block' : 'none' },
    },
    'Mock Wallet Modal'
  );
};

// Mock wallet modal context
export const WalletModalContext = React.createContext({
  visible: false,
  setVisible: jest.fn(),
});
