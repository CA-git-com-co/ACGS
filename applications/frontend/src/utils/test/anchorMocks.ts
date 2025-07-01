
// Anchor client testing utilities
export const mockAnchorProvider = {
  connection: {
    confirmTransaction: jest.fn(),
    requestAirdrop: jest.fn(),
  },
  wallet: {
    publicKey: 'mock-public-key',
  },
};

export const mockProgram = {
  methods: {
    initialize: jest.fn(),
    proposePolicy: jest.fn(),
    voteOnPolicy: jest.fn(),
    enactPolicy: jest.fn(),
    checkCompliance: jest.fn(),
  },
  account: {
    constitution: {
      fetch: jest.fn(),
    },
    policy: {
      fetch: jest.fn(),
    },
  },
};
