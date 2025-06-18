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
          DEFAULT: '#1A3A4A', // Azul escuro da imagem
          light: '#2A4A5A',
          dark: '#0A2A3A',
        },
        secondary: '#8AE65C', // Verde claro da imagem
        accent: '#FFFFFF', // Branco
        background: '#F8FAFC', // Fundo claro para melhor legibilidade
        text: {
          DEFAULT: '#1A3A4A', // Azul escuro para texto principal
          light: '#64748B', // Cinza para texto secundário
        },
        // Cores específicas para serviços
        service: {
          'banheira-gelo': '#1A3A4A', // Azul escuro para banheira de gelo
          'bota-compressao': '#8AE65C', // Verde para bota de compressão
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