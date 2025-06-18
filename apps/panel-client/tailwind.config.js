/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1A3A4A', // Azul escuro da imagem
        secondary: '#8AE65C', // Verde claro da imagem
        accent: '#FFFFFF', // Branco
        background: '#F8FAFC', // Mantendo um fundo claro para melhor legibilidade
        text: {
          DEFAULT: '#1A3A4A', // Azul escuro para texto principal
          light: '#64748B', // Cinza para texto secundário
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