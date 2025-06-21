import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: [
    '../components/**/*.stories.@(js|jsx|mjs|ts|tsx)',
    '../pages/**/*.stories.@(js|jsx|mjs|ts|tsx)',
    '../stories/**/*.stories.@(js|jsx|mjs|ts|tsx)'
  ],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y'
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {}
  },
  docs: {
    autodocs: 'tag'
  },
  typescript: {
    check: false,
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      propFilter: prop => (prop.parent ? !/node_modules/.test(prop.parent.fileName) : true)
    }
  },
  viteFinal: async config => {
    // Customize Vite config for Storybook
    if (config.resolve) {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': '/src'
      };
    }

    // Handle environment variables
    config.define = {
      ...config.define,
      'process.env.REACT_APP_AC_API_URL': JSON.stringify(
        process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1'
      ),
      'process.env.REACT_APP_GS_API_URL': JSON.stringify(
        process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1'
      ),
      'process.env.REACT_APP_PGC_API_URL': JSON.stringify(
        process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005/api/v1'
      ),
      'process.env.REACT_APP_AUTH_API_URL': JSON.stringify(
        process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002/auth'
      ),
      'process.env.REACT_APP_INTEGRITY_API_URL': JSON.stringify(
        process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1'
      ),
      'process.env.REACT_APP_FV_API_URL': JSON.stringify(
        process.env.REACT_APP_FV_API_URL || 'http://localhost:8004/api/v1'
      ),
      'process.env.REACT_APP_EC_API_URL': JSON.stringify(
        process.env.REACT_APP_EC_API_URL || 'http://localhost:8007/api/v1'
      )
    };

    return config;
  }
};

export default config;
