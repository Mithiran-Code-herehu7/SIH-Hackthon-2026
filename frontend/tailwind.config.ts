import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        parchment: {
          50: '#FAF9F6',
          100: '#F7F5F2',
          200: '#EFECE6',
          300: '#E2DDD5',
          400: '#C4C0B6',
        },
        nearBlack: '#111318',
        darkGrey: '#525663',
        brandIndigo: {
          900: '#1E1B4B',
          800: '#312E81',
          700: '#3730A3',
          600: '#4338CA',
          100: '#EEF2FF',
        },
      },
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        card: '1rem',
        pill: '9999px',
      },
      boxShadow: {
        editorial: '0 4px 20px -4px rgba(17, 19, 24, 0.04), 0 2px 6px -2px rgba(17, 19, 24, 0.02)',
        'editorial-hover': '0 12px 30px -6px rgba(17, 19, 24, 0.08), 0 4px 12px -2px rgba(17, 19, 24, 0.04)',
      },
    },
  },
  plugins: [],
};

export default config;
