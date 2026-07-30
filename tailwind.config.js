/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable toggling dark mode using class='dark'
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f3ff',
          100: '#e1e8ff',
          200: '#c8d4ff',
          300: '#a1b6ff',
          400: '#728fff',
          500: '#4361ee', // Primary brand indigo/blue
          600: '#2c43db',
          700: '#2030c6',
          800: '#1b26a0',
          900: '#1a247f',
        },
        dark: {
          50: '#f6f6f7',
          100: '#eef0f2',
          200: '#dadfe5',
          300: '#b8c3d0',
          400: '#8e9fb2',
          500: '#6c8096',
          600: '#54667a',
          700: '#3d4b5c',
          800: '#1e2530', // Slate Card Surface
          900: '#0f1319', // Main Dark Background
        },
        cyber: {
          neon: '#00f5ff',
          purple: '#bd00ff',
          pink: '#ff007a',
          green: '#39ff14',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-glow': '0 8px 32px 0 rgba(67, 97, 238, 0.15)',
        'neon-glow': '0 0 15px rgba(0, 245, 255, 0.4)',
      }
    },
  },
  plugins: [],
}
