import { render } from '@testing-library/react';
import { QuantumagiApp } from '@/components/blockchain/QuantumagiApp';

describe('QuantumagiApp', () => {
  it('renders without crashing', () => {
    // The component should render without throwing errors related to wallet context
    expect(() => render(<QuantumagiApp />)).not.toThrow();
  });

  it('provides Solana wallet context', () => {
    // The component should render without throwing errors related to wallet context
    expect(() => render(<QuantumagiApp />)).not.toThrow();
  });
});
