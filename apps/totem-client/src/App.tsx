import { Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

// Páginas
import WelcomePage from './pages/WelcomePage';
import SelectServicePage from './pages/SelectServicePage';
import CustomerInfoPage from './pages/CustomerInfoPage';
import TermsPage from './pages/TermsPage';
import PaymentPage from './pages/PaymentPage';
import TicketPage from './pages/TicketPage';
import QueuePage from './pages/QueuePage';
import SelectExtrasPage from './pages/SelectExtrasPage';

// Componentes de layout
import Layout from './components/Layout';
import KioskMode from './components/KioskMode';
import AdminAccess from './components/AdminAccess';
import FullscreenButton from './components/FullscreenButton';
import PWAInstallPrompt from './components/PWAInstallPrompt';
import { RequireStep } from './components/RequireStep';

function App() {
  // Estado para controlar o modo quiosque
  const [kioskEnabled, setKioskEnabled] = useState(true);
  const [showPWAPrompt, setShowPWAPrompt] = useState(false);
  
  // Verificar se já está instalado como PWA
  useEffect(() => {
    const isPWA = 
      window.matchMedia('(display-mode: standalone)').matches || 
      window.matchMedia('(display-mode: fullscreen)').matches ||
      (window.navigator as any).standalone === true ||
      (window as any).IS_PWA_MODE === true;
    
    // Se não estiver em modo PWA, mostrar o prompt após um delay
    if (!isPWA) {
      // Verificar se o navegador suporta instalação de PWA
      const isChrome = navigator.userAgent.includes('Chrome');
      const isEdge = navigator.userAgent.includes('Edg');
      
      // Apenas mostrar automaticamente em navegadores que suportam bem PWAs
      if (isChrome || isEdge) {
        // Mostrar o prompt após 30 segundos
        const timer = setTimeout(() => {
          setShowPWAPrompt(true);
        }, 30000);
        
        return () => clearTimeout(timer);
      }
    }
  }, []);
  
  return (
    <KioskMode enabled={kioskEnabled}>
      {showPWAPrompt && (
        <PWAInstallPrompt onClose={() => setShowPWAPrompt(false)} />
      )}
      
      <AnimatePresence mode="wait">
        <Routes>
          {/* Rotas públicas */}
          <Route path="/" element={<Layout />}>
            <Route index element={<WelcomePage />} />
            <Route path="service" element={
              <RequireStep step="service">
                <SelectServicePage />
              </RequireStep>
            } />
            <Route path="extras" element={
              <RequireStep step="extras">
                <SelectExtrasPage />
              </RequireStep>
            } />
            <Route path="customer-info" element={
              <RequireStep step="customer">
                <CustomerInfoPage />
              </RequireStep>
            } />
            <Route path="terms" element={
              <RequireStep step="terms">
                <TermsPage />
              </RequireStep>
            } />
            <Route path="payment" element={
              <RequireStep step="payment">
                <PaymentPage />
              </RequireStep>
            } />
            <Route path="ticket" element={
              <RequireStep step="ticket">
                <TicketPage />
              </RequireStep>
            } />
            <Route path="queue" element={<QueuePage />} />
            
            {/* Rota de fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
          
          {/* Rota administrativa para desativar o modo quiosque (protegida por senha) */}
          <Route path="/admin" element={
            <AdminAccess>
              <div className="flex items-center justify-center h-screen bg-primary p-6">
                <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-center flex-1">Administração</h2>
                    <FullscreenButton className="ml-2" />
                  </div>
                  
                  <div className="space-y-4">
                    <button 
                      className="w-full bg-red-600 text-white py-3 rounded-lg font-medium hover:bg-red-700"
                      onClick={() => setKioskEnabled(false)}
                    >
                      Desativar Modo Quiosque
                    </button>
                    
                    <button 
                      className="w-full bg-primary text-white py-3 rounded-lg font-medium hover:bg-primary-dark"
                      onClick={() => setKioskEnabled(true)}
                    >
                      Ativar Modo Quiosque
                    </button>
                    
                    <button 
                      className="w-full bg-secondary text-primary py-3 rounded-lg font-medium hover:bg-secondary/90"
                      onClick={() => setShowPWAPrompt(true)}
                    >
                      Instalar como PWA
                    </button>
                    
                    <button 
                      className="w-full bg-gray-200 text-gray-800 py-3 rounded-lg font-medium hover:bg-gray-300"
                      onClick={() => window.location.href = '/'}
                    >
                      Voltar para Aplicação
                    </button>
                  </div>
                </div>
              </div>
            </AdminAccess>
          } />
        </Routes>
      </AnimatePresence>
    </KioskMode>
  );
}

export default App; 