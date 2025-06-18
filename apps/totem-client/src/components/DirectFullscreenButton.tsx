import React, { useState, useEffect } from 'react';

interface DirectFullscreenButtonProps {
  className?: string;
  children?: React.ReactNode;
}

/**
 * Botão dedicado para ativar o modo tela cheia diretamente na interface
 * Isso é necessário para navegadores que exigem interação direta do usuário
 */
const DirectFullscreenButton: React.FC<DirectFullscreenButtonProps> = ({ 
  className = '', 
  children 
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Verificar o estado atual da tela cheia
  const checkFullscreenState = () => {
    const fullscreenElement = 
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement;
    
    setIsFullscreen(!!fullscreenElement);
  };
  
  // Ativar o modo tela cheia
  const enableFullscreen = () => {
    try {
      console.log("Ativando modo tela cheia via botão direto");
      const docEl = document.documentElement;
      
      if (docEl.requestFullscreen) {
        docEl.requestFullscreen();
      } else if ((docEl as any).webkitRequestFullscreen) {
        (docEl as any).webkitRequestFullscreen();
      } else if ((docEl as any).mozRequestFullScreen) {
        (docEl as any).mozRequestFullScreen();
      } else if ((docEl as any).msRequestFullscreen) {
        (docEl as any).msRequestFullscreen();
      }
    } catch (error) {
      console.error("Erro ao ativar tela cheia:", error);
    }
  };
  
  // Monitorar mudanças no estado da tela cheia
  useEffect(() => {
    document.addEventListener('fullscreenchange', checkFullscreenState);
    document.addEventListener('webkitfullscreenchange', checkFullscreenState);
    document.addEventListener('mozfullscreenchange', checkFullscreenState);
    document.addEventListener('MSFullscreenChange', checkFullscreenState);
    
    return () => {
      document.removeEventListener('fullscreenchange', checkFullscreenState);
      document.removeEventListener('webkitfullscreenchange', checkFullscreenState);
      document.removeEventListener('mozfullscreenchange', checkFullscreenState);
      document.removeEventListener('MSFullscreenChange', checkFullscreenState);
    };
  }, []);
  
  return (
    <button
      className={`bg-secondary text-primary font-bold py-4 px-8 rounded-lg text-xl shadow-lg hover:bg-secondary/90 active:scale-95 transition-all flex items-center justify-center ${className}`}
      onClick={enableFullscreen}
    >
      {children || (
        <>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-6 w-6 mr-2" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
          </svg>
          ATIVAR TELA CHEIA
        </>
      )}
    </button>
  );
};

export default DirectFullscreenButton; 