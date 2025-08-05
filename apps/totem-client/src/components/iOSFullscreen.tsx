import { useEffect } from 'react';

/**
 * Componente para lidar com o modo tela cheia em dispositivos iOS e tablets
 * iOS não suporta a API Fullscreen padrão, então usamos uma abordagem diferente
 */
const IOSFullscreen: React.FC = () => {
  useEffect(() => {
    // Detectar se é um dispositivo iOS ou tablet
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    const isTablet = /iPad|Android(?=.*\bMobile\b)(?=.*\bSafari\b)/i.test(navigator.userAgent) || 
                    (window.innerWidth >= 768 && window.innerWidth <= 1024);
    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent);
    
    if (isIOS || isTablet || isMobile) {
      console.log(`Dispositivo detectado: ${isIOS ? 'iOS' : ''} ${isTablet ? 'Tablet' : ''} ${isMobile ? 'Mobile' : ''}`);
      console.log("Aplicando técnicas alternativas de tela cheia para dispositivo móvel/tablet");
      
      // Adicionar meta tags específicas para dispositivos móveis
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      if (viewportMeta) {
        viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no, viewport-fit=cover');
      } else {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no, viewport-fit=cover';
        document.head.appendChild(meta);
      }
      
      // Adicionar meta tag para modo standalone
      const appleMeta = document.createElement('meta');
      appleMeta.name = 'apple-mobile-web-app-capable';
      appleMeta.content = 'yes';
      document.head.appendChild(appleMeta);
      
      // Adicionar meta tag para barra de status
      const statusBarMeta = document.createElement('meta');
      statusBarMeta.name = 'apple-mobile-web-app-status-bar-style';
      statusBarMeta.content = 'black-translucent';
      document.head.appendChild(statusBarMeta);
      
      // Adicionar meta tag para orientação
      const orientationMeta = document.createElement('meta');
      orientationMeta.name = 'screen-orientation';
      orientationMeta.content = 'portrait';
      document.head.appendChild(orientationMeta);
      
      // Adicionar estilos para simular tela cheia em dispositivos móveis
      const style = document.createElement('style');
      style.innerHTML = `
        html, body {
          position: fixed;
          width: 100%;
          height: 100%;
          overflow: hidden;
          -webkit-overflow-scrolling: touch;
          margin: 0;
          padding: 0;
        }
        
        body {
          min-height: 100%;
          min-height: -webkit-fill-available;
          min-height: -moz-available;
          min-height: stretch;
        }
        
        #root {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          overflow: hidden;
          height: 100%;
          width: 100%;
          display: flex;
          flex-direction: column;
        }
        
        /* Estilos específicos para tablets */
        @media (min-width: 768px) and (max-width: 1024px) {
          html, body {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: hidden !important;
          }
          
          #root {
            width: 100vw !important;
            height: 100vh !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            overflow: hidden !important;
          }
        }
        
        /* Estilos para dispositivos iOS */
        @supports (-webkit-touch-callout: none) {
          html, body {
            height: -webkit-fill-available;
          }
          
          #root {
            height: -webkit-fill-available;
          }
        }
        
        /* Impedir seleção de texto */
        * {
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
          -webkit-touch-callout: none;
        }
        
        /* Permitir seleção em campos de input */
        input, textarea, [contenteditable] {
          -webkit-user-select: text;
          -moz-user-select: text;
          -ms-user-select: text;
          user-select: text;
        }
      `;
      document.head.appendChild(style);
      
      // Impedir o comportamento de rolagem e zoom
      const preventDefaultBehavior = (e: Event) => {
        e.preventDefault();
      };
      
      // Impedir gestos de zoom e rolagem
      document.addEventListener('touchmove', preventDefaultBehavior, { passive: false });
      document.addEventListener('gesturestart', preventDefaultBehavior);
      document.addEventListener('gesturechange', preventDefaultBehavior);
      document.addEventListener('gestureend', preventDefaultBehavior);
      
      // Impedir double-tap para zoom
      let lastTouchEnd = 0;
      document.addEventListener('touchend', (e) => {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
          e.preventDefault();
        }
        lastTouchEnd = now;
      }, false);
      
      // Impedir que a tela entre em modo de espera
      const keepAwake = () => {
        if (navigator.wakeLock) {
          navigator.wakeLock.request('screen')
            .then(() => console.log('Tela mantida ativa'))
            .catch(err => console.error('Erro ao manter tela ativa:', err));
        }
      };
      
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          keepAwake();
        }
      });
      
      keepAwake();
      
      // Impedir saída da aplicação
      const preventExit = (e: BeforeUnloadEvent) => {
        e.preventDefault();
        e.returnValue = '';
        return '';
      };
      
      window.addEventListener('beforeunload', preventExit);
      
      // Impedir teclas de sistema
      const preventSystemKeys = (e: KeyboardEvent) => {
        // Impedir Alt+Tab, F11, Escape, etc.
        if (
          (e.key === 'Tab' && e.altKey) ||
          e.key === 'F11' ||
          (e.key === 'Escape' && !document.querySelector('input:focus, textarea:focus')) ||
          (e.key === 'Meta' || e.key === 'Windows')
        ) {
          e.preventDefault();
          return false;
        }
      };
      
      document.addEventListener('keydown', preventSystemKeys);
      
      // Impedir menu de contexto
      document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
      });
      
      return () => {
        document.removeEventListener('touchmove', preventDefaultBehavior);
        document.removeEventListener('gesturestart', preventDefaultBehavior);
        document.removeEventListener('gesturechange', preventDefaultBehavior);
        document.removeEventListener('gestureend', preventDefaultBehavior);
        document.removeEventListener('keydown', preventSystemKeys);
        window.removeEventListener('beforeunload', preventExit);
        
        if (document.head.contains(style)) {
          document.head.removeChild(style);
        }
      };
    }
    
    return undefined;
  }, []);
  
  return null;
};

export default IOSFullscreen; 