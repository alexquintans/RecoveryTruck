import React, { useState, useEffect } from 'react';

interface FullscreenButtonProps {
  className?: string;
}

const FullscreenButton: React.FC<FullscreenButtonProps> = ({ className = '' }) => {
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
  
  // Alternar o modo tela cheia
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      // Entrar no modo tela cheia
      try {
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
        console.error("Erro ao entrar no modo tela cheia:", error);
      }
    } else {
      // Sair do modo tela cheia
      try {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if ((document as any).webkitExitFullscreen) {
          (document as any).webkitExitFullscreen();
        } else if ((document as any).mozCancelFullScreen) {
          (document as any).mozCancelFullScreen();
        } else if ((document as any).msExitFullscreen) {
          (document as any).msExitFullscreen();
        }
      } catch (error) {
        console.error("Erro ao sair do modo tela cheia:", error);
      }
    }
  };
  
  // Monitorar mudanças no estado da tela cheia
  useEffect(() => {
    document.addEventListener('fullscreenchange', checkFullscreenState);
    document.addEventListener('webkitfullscreenchange', checkFullscreenState);
    document.addEventListener('mozfullscreenchange', checkFullscreenState);
    document.addEventListener('MSFullscreenChange', checkFullscreenState);
    
    // Verificar o estado inicial
    checkFullscreenState();
    
    return () => {
      document.removeEventListener('fullscreenchange', checkFullscreenState);
      document.removeEventListener('webkitfullscreenchange', checkFullscreenState);
      document.removeEventListener('mozfullscreenchange', checkFullscreenState);
      document.removeEventListener('MSFullscreenChange', checkFullscreenState);
    };
  }, []);
  
  return (
    <button
      className={`p-2 rounded-md hover:bg-gray-200 transition-colors ${className}`}
      onClick={toggleFullscreen}
      title={isFullscreen ? "Sair da tela cheia" : "Entrar em tela cheia"}
    >
      {isFullscreen ? (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
        </svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
        </svg>
      )}
    </button>
  );
};

export default FullscreenButton; 