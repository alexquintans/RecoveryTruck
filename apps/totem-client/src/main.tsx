import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

console.log('VITE_TENANT_ID:', import.meta.env.VITE_TENANT_ID);

// Cria o cliente de consulta para React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

// Função para registrar o service worker
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('Service Worker registrado com sucesso:', registration);
          
          // Verificar atualizações periodicamente
          setInterval(() => {
            registration.update();
          }, 60 * 60 * 1000); // Verificar a cada hora
          
          // Atualizar quando houver nova versão
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            
            newWorker?.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // Há uma nova versão disponível
                if (confirm('Nova versão disponível! Atualizar agora?')) {
                  newWorker.postMessage({ type: 'SKIP_WAITING' });
                  window.location.reload();
                }
              }
            });
          });
        })
        .catch(error => {
          console.error('Erro ao registrar Service Worker:', error);
        });
        
      // Detectar quando o service worker é atualizado
      let refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });
    });
  }
}

// Registrar o service worker
registerServiceWorker();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
); 