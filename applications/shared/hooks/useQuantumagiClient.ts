import { useMemo } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { QuantumagiClient } from '../services/QuantumagiClient';

/**
 * React hook for accessing the Quantumagi client
 * Provides easy access to blockchain governance operations
 */
export const useQuantumagiClient = () => {
  const { connection } = useConnection();
  const wallet = useWallet();

  const client = useMemo(() => {
    if (!wallet.publicKey || !connection) {
      return null;
    }
    
    return new QuantumagiClient(connection, wallet);
  }, [connection, wallet.publicKey, wallet.connected]);

  return {
    client,
    connected: wallet.connected,
    publicKey: wallet.publicKey,
    connecting: wallet.connecting,
    disconnecting: wallet.disconnecting
  };
};

export default useQuantumagiClient;
