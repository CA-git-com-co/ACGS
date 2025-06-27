'use client';

import React, { useMemo } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';
import { QuantumagiDashboard } from './QuantumagiDashboard';

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

/**
 * Quantumagi App Wrapper with Solana Wallet Integration
 *
 * Provides the necessary providers for Solana wallet connectivity
 * and blockchain interactions in the Next.js environment.
 */
export const QuantumagiApp: React.FC = () => {
  // Configure Solana network (devnet for development)
  const network = WalletAdapterNetwork.Devnet;
  const endpoint = useMemo(() => {
    // Use environment variable if available, otherwise default to devnet
    return process.env.NEXT_PUBLIC_SOLANA_RPC_URL || clusterApiUrl(network);
  }, [network]);

  // Configure supported wallets
  const wallets = useMemo(() => [new PhantomWalletAdapter(), new SolflareWalletAdapter()], []);

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <QuantumagiDashboard />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
};

export default QuantumagiApp;
