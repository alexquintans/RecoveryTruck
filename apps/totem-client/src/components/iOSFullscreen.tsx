import { useEffect } from 'react';

/**
 * Componente para lidar com o modo tela cheia em dispositivos iOS
 * iOS não suporta a API Fullscreen padrão, então usamos uma abordagem diferente
 */
const IOSFullscreen: React.FC = () => {
  useEffect(() => {
    // Detectar se é um dispositivo iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    
    if (isIOS) {
      console.log("Dispositivo iOS detectado, aplicando técnicas alternativas de tela cheia");
      
      // Adicionar meta tags específicas para iOS
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      if (viewportMeta) {
        viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no');
      } else {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no';
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
      
      // Adicionar estilos para simular tela cheia em iOS
      const style = document.createElement('style');
      style.innerHTML = `
        html, body {
          position: fixed;
          width: 100%;
          height: 100%;
          overflow: hidden;
          -webkit-overflow-scrolling: touch;
        }
        
        body {
          margin: 0;
          padding: 0;
          min-height: 100%;
          min-height: -webkit-fill-available;
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
        }
      `;
      document.head.appendChild(style);
      
      // Impedir o comportamento de rolagem e zoom
      const preventDefaultBehavior = (e: Event) => {
        e.preventDefault();
      };
      
      document.addEventListener('touchmove', preventDefaultBehavior, { passive: false });
      document.addEventListener('gesturestart', preventDefaultBehavior);
      document.addEventListener('gesturechange', preventDefaultBehavior);
      document.addEventListener('gestureend', preventDefaultBehavior);
      
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
      
      return () => {
        document.removeEventListener('touchmove', preventDefaultBehavior);
        document.removeEventListener('gesturestart', preventDefaultBehavior);
        document.removeEventListener('gesturechange', preventDefaultBehavior);
        document.removeEventListener('gestureend', preventDefaultBehavior);
      };
    }
    
    return undefined;
  }, []);
  
  return null;
};

export default IOSFullscreen; 