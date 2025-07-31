/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1F526B', // Azul Profundo da marca
        secondary: '#FFFFFF', // Branco da marca
        accent: '#D9D9D9', // Cinza Claro da marca
        background: '#FFFFFF', // Fundo branco para melhor legibilidade
        text: {
          DEFAULT: '#000000', // Preto para texto principal
          light: '#1F526B', // Azul profundo para texto secundário
        },
        gray: {
          light: '#D9D9D9', // Cinza claro da marca
          DEFAULT: '#64748B', // Cinza padrão para elementos neutros
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        flash: 'flash 0.5s ease-in-out',
        pulse: 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        flash: {
          '0%, 100%': { opacity: 0 },
          '50%': { opacity: 1 },
        },
        pulse: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
      },
      blur: {
        '3xl': '64px',
      }
    },
  },
  plugins: [],
} 