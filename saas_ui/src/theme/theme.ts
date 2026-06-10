/**
 * Nova Trader - Clean Trading Interface Theme
 * Modern financial dashboard with light/dark mode support
 */
import { extendTheme } from '@mui/joy/styles';

// Base 8px grid system for spatial orientation
const spacing = 8;

const theme = extendTheme({
  spacing: (factor: number) => `${spacing * factor}px`,

  colorSchemes: {
    light: {
      palette: {
        // Clean light mode - high contrast, calm
        background: {
          body: '#fafafa',
          surface: '#ffffff',
          level1: '#f5f5f5',
          level2: '#eeeeee',
          level3: '#e0e0e0',
        },
        text: {
          primary: '#1a1a1a',
          secondary: '#616161',
          tertiary: '#9e9e9e',
        },
        primary: {
          50: '#e3f2fd',
          100: '#bbdefb',
          200: '#90caf9',
          300: '#64b5f6',
          400: '#42a5f5',
          500: '#2196f3', // Main brand blue
          600: '#1e88e5',
          700: '#1976d2',
          800: '#1565c0',
          900: '#0d47a1',
        },
        success: {
          500: '#4caf50', // Profit green
        },
        danger: {
          500: '#f44336', // Loss red
        },
        warning: {
          500: '#ff9800', // Alert orange
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#eeeeee',
          300: '#e0e0e0',
          400: '#bdbdbd',
          500: '#9e9e9e',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
        },
      },
    },
    dark: {
      palette: {
        // Professional dark mode - reduced eye strain
        background: {
          body: '#0a0a0a',
          surface: '#121212',
          level1: '#1e1e1e',
          level2: '#2a2a2a',
          level3: '#333333',
        },
        text: {
          primary: '#ffffff',
          secondary: '#b3b3b3',
          tertiary: '#666666',
        },
        primary: {
          50: '#e3f2fd',
          100: '#bbdefb',
          200: '#90caf9',
          300: '#64b5f6',
          400: '#42a5f5',
          500: '#2196f3',
          600: '#1e88e5',
          700: '#1976d2',
          800: '#1565c0',
          900: '#0d47a1',
        },
        success: {
          500: '#00e676', // Bright profit green for dark mode
        },
        danger: {
          500: '#ff5252', // Bright loss red for dark mode
        },
        warning: {
          500: '#ffc107',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#eeeeee',
          300: '#e0e0e0',
          400: '#bdbdbd',
          500: '#9e9e9e',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
        },
      },
    },
  },

  typography: {
    // Clean, professional typography
    fontFamily: {
      body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      display: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      code: 'JetBrains Mono, "Fira Code", Consolas, "Liberation Mono", Menlo, Monaco, monospace',
    },
    fontSize: {
      xs: '0.75rem',   // 12px - micro data labels
      sm: '0.875rem',  // 14px - secondary text
      md: '1rem',      // 16px - body text
      lg: '1.125rem',  // 18px - section headers
      xl: '1.25rem',   // 20px - card titles
      xl2: '1.5rem',   // 24px - page titles
      xl3: '1.875rem', // 30px - hero numbers
      xl4: '2.25rem',  // 36px - key metrics
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semiBold: 600,
      bold: 700,
    },
    lineHeight: {
      xs: 1.2,
      sm: 1.25,
      md: 1.5,
      lg: 1.55,
      xl: 1.6,
    },
  },

  radius: {
    none: '0px',
    xs: '2px',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    xl2: '20px',
    xl3: '24px',
  },

  shadow: {
    // Subtle depth for Flat Design 2.0
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  },

  components: {
    JoyCard: {
      styleOverrides: {
        root: ({ theme }) => ({
          // Hard connectors and visible grid structure
          border: `1px solid ${theme.palette.divider}`,
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            borderColor: theme.palette.primary[300],
            boxShadow: theme.shadow.md,
          },
        }),
      },
    },
    JoyButton: {
      styleOverrides: {
        root: ({ theme }) => ({
          // Clean, purposeful buttons
          textTransform: 'none',
          fontWeight: 500,
          letterSpacing: '0.025em',
        }),
      },
    },
    JoyTypography: {
      styleOverrides: {
        root: {
          // Baseline grid alignment
          lineHeight: 1.5,
        },
      },
    },
  },
});

export default theme;