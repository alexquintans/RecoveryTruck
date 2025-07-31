/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1F526B', // Azul Profundo da marca
          light: '#2A6B8A',
          dark: '#0A3A4A',
        },
        secondary: '#FFFFFF', // Branco da marca
        accent: '#D9D9D9', // Cinza Claro da marca
        background: '#FFFFFF', // Fundo branco para melhor legibilidade
        text: {
          DEFAULT: '#000000', // Preto para texto principal
          light: '#1F526B', // Azul profundo para texto secundário
        },
        // Cores específicas para serviços
        service: {
          'banheira-gelo': '#1F526B', // Azul profundo para banheira de gelo
          'bota-compressao': '#FFFFFF', // Branco para bota de compressão
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
      },
    },
  },
  plugins: [],
} 