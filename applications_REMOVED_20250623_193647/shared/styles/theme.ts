// ACGS-PGP Framework Theme Configuration
// Design tokens for consistent styling across applications

export const theme = {
  colors: {
    // Primary brand colors
    primary: '#3f51b5',
    primaryDark: '#303f9f',
    primaryLight: '#7986cb',

    // Secondary brand colors
    secondary: '#f50057',
    secondaryDark: '#c51162',
    secondaryLight: '#ff5983',

    // Background colors
    background: '#f5f5f5',
    backgroundDark: '#121212',
    backgroundLight: '#ffffff',
    surface: '#ffffff',
    surfaceDark: '#1e1e1e',

    // Text colors
    text: '#333333',
    textSecondary: '#666666',
    textLight: '#999999',
    textDark: '#000000',
    textOnPrimary: '#ffffff',
    textOnSecondary: '#ffffff',

    // Status colors
    error: '#f44336',
    errorDark: '#d32f2f',
    errorLight: '#e57373',
    success: '#4caf50',
    successDark: '#388e3c',
    successLight: '#81c784',
    warning: '#ff9800',
    warningDark: '#f57c00',
    warningLight: '#ffb74d',
    info: '#2196f3',
    infoDark: '#1976d2',
    infoLight: '#64b5f6',

    // Neutral colors
    gray: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121'
    },

    // Constitutional governance specific colors
    governance: {
      principle: '#6366f1',
      policy: '#8b5cf6',
      compliance: '#10b981',
      violation: '#ef4444',
      pending: '#f59e0b',
      approved: '#22c55e',
      rejected: '#ef4444'
    }
  },

  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
    '4xl': '96px',
    '5xl': '128px'
  },

  typography: {
    fontFamily: {
      sans: '"Inter", "Roboto", "Helvetica Neue", "Arial", sans-serif',
      serif: '"Merriweather", "Georgia", "Times New Roman", serif',
      mono: '"Fira Code", "Monaco", "Consolas", "Courier New", monospace'
    },
    fontSize: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      base: '1rem', // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem', // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem', // 48px
      '6xl': '3.75rem' // 60px
    },
    fontWeight: {
      thin: 100,
      extralight: 200,
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
      black: 900
    },
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2
    },
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0em',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em'
    }
  },

  breakpoints: {
    xs: '0px',
    sm: '600px',
    md: '960px',
    lg: '1280px',
    xl: '1920px'
  },

  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
  },

  borderRadius: {
    none: '0px',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px'
  },

  transitions: {
    duration: {
      fast: '150ms',
      base: '200ms',
      slow: '300ms',
      slower: '500ms'
    },
    timing: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
      linear: 'linear'
    }
  },

  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800
  }
};

// Type definitions for theme
export type Theme = typeof theme;
export type ThemeColors = typeof theme.colors;
export type ThemeSpacing = typeof theme.spacing;
export type ThemeTypography = typeof theme.typography;
export type ThemeBreakpoints = typeof theme.breakpoints;

// Helper functions for theme usage
export const getColor = (path: string): string => {
  const keys = path.split('.');
  let value: any = theme.colors;

  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      console.warn(`Color path "${path}" not found in theme`);
      return theme.colors.text;
    }
  }

  return typeof value === 'string' ? value : theme.colors.text;
};

export const getSpacing = (size: keyof typeof theme.spacing): string => {
  return theme.spacing[size] || theme.spacing.md;
};

export const getFontSize = (size: keyof typeof theme.typography.fontSize): string => {
  return theme.typography.fontSize[size] || theme.typography.fontSize.base;
};

export const getBreakpoint = (size: keyof typeof theme.breakpoints): string => {
  return theme.breakpoints[size] || theme.breakpoints.md;
};

// CSS-in-JS helper for media queries
export const mediaQuery = (breakpoint: keyof typeof theme.breakpoints) => {
  return `@media (min-width: ${theme.breakpoints[breakpoint]})`;
};

// Default export
export default theme;
