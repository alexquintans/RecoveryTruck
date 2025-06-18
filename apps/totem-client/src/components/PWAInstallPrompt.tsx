import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface PWAInstallPromptProps {
  onClose: () => void;
}

const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({ onClose }) => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [installable, setInstallable] = useState(false);
  
  useEffect(() => {
    // Verificar se já está instalado como PWA
    const isPWA = 
      window.matchMedia('(display-mode: standalone)').matches || 
      window.matchMedia('(display-mode: fullscreen)').matches ||
      (window.navigator as any).standalone === true ||
      (window as any).IS_PWA_MODE === true;
    
    if (isPWA) {
      // Já está instalado como PWA, não mostrar o prompt
      console.log("Aplicação já está instalada como PWA");
      onClose();
      return;
    }
    
    // Verificar se o navegador suporta instalação de PWA
    const isChrome = navigator.userAgent.includes('Chrome');
    const isFirefox = navigator.userAgent.includes('Firefox');
    const isEdge = navigator.userAgent.includes('Edg');
    const isSafari = navigator.userAgent.includes('Safari') && !navigator.userAgent.includes('Chrome');
    
    // Navegadores que suportam PWA
    const supportsPWA = isChrome || isEdge || isFirefox || isSafari;
    setInstallable(supportsPWA);
    
    if (!supportsPWA) {
      console.log("Navegador não suporta instalação de PWA");
      onClose();
      return;
    }
    
    // Capturar o evento beforeinstallprompt
    const handleBeforeInstallPrompt = (e: Event) => {
      // Prevenir que o navegador mostre o prompt automaticamente
      e.preventDefault();
      
      // Armazenar o evento para usar mais tarde
      setDeferredPrompt(e);
      
      // Mostrar nosso prompt personalizado
      setIsVisible(true);
      console.log("Prompt de instalação disponível");
    };
    
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    
    // Verificar se o evento já foi disparado antes de registrarmos o listener
    if ((window as any).deferredPrompt) {
      setDeferredPrompt((window as any).deferredPrompt);
      setIsVisible(true);
      console.log("Usando prompt de instalação armazenado anteriormente");
    }
    
    // Verificar se a aplicação já foi instalada
    window.addEventListener('appinstalled', () => {
      console.log('PWA foi instalada com sucesso!');
      setIsVisible(false);
      onClose();
    });
    
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, [onClose]);
  
  const handleInstall = async () => {
    if (!deferredPrompt) {
      console.log('Nenhum prompt de instalação disponível');
      
      // Instruções alternativas para navegadores que não suportam o evento beforeinstallprompt
      alert('Para instalar o aplicativo:\n\n' +
            '1. Toque no menu do navegador (três pontos)\n' +
            '2. Selecione "Instalar aplicativo" ou "Adicionar à tela inicial"');
      
      setIsVisible(false);
      onClose();
      return;
    }
    
    // Mostrar o prompt de instalação
    deferredPrompt.prompt();
    
    // Esperar pela escolha do usuário
    const choiceResult = await deferredPrompt.userChoice;
    
    // Resetar o deferredPrompt após o uso
    setDeferredPrompt(null);
    (window as any).deferredPrompt = null;
    
    // Esconder nosso prompt
    setIsVisible(false);
    
    // Fechar o componente
    onClose();
    
    if (choiceResult.outcome === 'accepted') {
      console.log('Usuário aceitou a instalação da PWA');
    } else {
      console.log('Usuário recusou a instalação da PWA');
    }
  };
  
  const handleClose = () => {
    setIsVisible(false);
    onClose();
  };
  
  if (!isVisible || !installable) {
    return null;
  }
  
  return (
    <motion.div 
      className="fixed inset-0 bg-primary/80 z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center mb-4">
          <div className="bg-primary p-3 rounded-full mr-4">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-8 w-8 text-white" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" 
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-primary">Instalar Aplicativo</h2>
        </div>
        
        <p className="text-gray-700 mb-6">
          Instale o RecoveryTruck como um aplicativo para uma experiência completa em tela cheia e acesso rápido.
        </p>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={handleInstall}
            className="bg-secondary text-primary font-bold py-3 px-4 rounded-lg hover:bg-secondary/90 transition-colors"
          >
            Instalar Agora
          </button>
          
          <button
            onClick={handleClose}
            className="text-gray-600 py-2 hover:text-gray-800 transition-colors"
          >
            Talvez mais tarde
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default PWAInstallPrompt; 