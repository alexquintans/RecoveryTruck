import React, { useEffect, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import FullscreenPrompt from './FullscreenPrompt';
import IOSFullscreen from './iOSFullscreen';

interface KioskModeProps {
  children: React.ReactNode;
  enabled?: boolean;
}

const KioskMode: React.FC<KioskModeProps> = ({ children, enabled = true }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [userInteracted, setUserInteracted] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [fullscreenError, setFullscreenError] = useState<string | null>(null);
  const [fullscreenSupported, setFullscreenSupported] = useState(true);
  const [initialPromptShown, setInitialPromptShown] = useState(false);
  const [fullscreenAttempts, setFullscreenAttempts] = useState(0);
  const [autoStartAttempted, setAutoStartAttempted] = useState(false);
  const [isPWA, setIsPWA] = useState(false);
  
  // Verificar se estamos em ambiente de desenvolvimento e se o modo quiosque deve ser desativado
  const isDevelopment = import.meta.env.DEV;
  const disableKioskInDev = import.meta.env.VITE_DISABLE_KIOSK_MODE === 'true';
  
  // O modo quiosque só é realmente ativado se:
  // 1. A prop 'enabled' for true
  // 2. NÃO estivermos em desenvolvimento OU não tivermos configurado para desativar em dev
  const kioskModeActive = enabled && (!isDevelopment || !disableKioskInDev);

  // Verificar se está rodando como PWA
  useEffect(() => {
    // Função para verificar se está em modo PWA
    const checkPWAMode = () => {
      // Verificar se está em modo standalone (PWA)
      const isStandalone = 
        window.matchMedia('(display-mode: standalone)').matches || 
        window.matchMedia('(display-mode: fullscreen)').matches ||
        (window.navigator as any).standalone === true ||
        (window as any).IS_PWA_MODE === true;
      
      console.log("Verificando modo PWA:", isStandalone ? "ATIVADO" : "DESATIVADO");
      
      setIsPWA(isStandalone);
      
      if (isStandalone) {
        console.log("Aplicação rodando como PWA instalada");
        setUserInteracted(true);  // Considerar como já tendo interagido
        setIsFullscreen(true);    // Considerar como já estando em tela cheia
        setShowPrompt(false);     // Nunca mostrar o prompt em modo PWA
        
        // Forçar modo tela cheia em PWAs
        document.addEventListener('click', function tryFullscreen(e) {
          // Verificar se o clique foi em um elemento interativo
          const target = e.target as HTMLElement;
          const isInteractive = target.tagName === 'BUTTON' || 
                               target.tagName === 'A' || 
                               target.tagName === 'INPUT' || 
                               target.tagName === 'SELECT' || 
                               target.tagName === 'TEXTAREA' ||
                               target.closest('button') ||
                               target.closest('a') ||
                               target.closest('input') ||
                               target.closest('select') ||
                               target.closest('textarea');
          
          // Se for um elemento interativo, não tentar entrar em tela cheia
          if (isInteractive) {
            return;
          }
          
          if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(err => console.error('Erro ao entrar em tela cheia:', err));
          } else if ((document.documentElement as any).webkitRequestFullscreen) {
            (document.documentElement as any).webkitRequestFullscreen();
          } else if ((document.documentElement as any).mozRequestFullScreen) {
            (document.documentElement as any).mozRequestFullScreen();
          } else if ((document.documentElement as any).msRequestFullscreen) {
            (document.documentElement as any).msRequestFullscreen();
          }
          document.removeEventListener('click', tryFullscreen);
        }, { once: true });
      } else {
        // Verificar se a aplicação foi instalada como PWA
        if ('BeforeInstallPromptEvent' in window) {
          console.log("BeforeInstallPromptEvent suportado - aplicação pode ser instalada como PWA");
        }
      }
    };
    
    // Verificar inicialmente
    checkPWAMode();
    
    // Verificar quando o modo de exibição mudar
    const standaloneHandler = (e: MediaQueryListEvent) => {
      if (e.matches) {
        console.log("Aplicação entrou em modo standalone");
        setIsPWA(true);
        setShowPrompt(false);
      }
    };
    
    const fullscreenHandler = (e: MediaQueryListEvent) => {
      if (e.matches) {
        console.log("Aplicação entrou em modo fullscreen");
        setIsPWA(true);
        setShowPrompt(false);
      }
    };
    
    window.matchMedia('(display-mode: standalone)').addEventListener('change', standaloneHandler);
    window.matchMedia('(display-mode: fullscreen)').addEventListener('change', fullscreenHandler);
    
    return () => {
      window.matchMedia('(display-mode: standalone)').removeEventListener('change', standaloneHandler);
      window.matchMedia('(display-mode: fullscreen)').removeEventListener('change', fullscreenHandler);
    };
  }, []);

  // Verificar se o navegador suporta a API Fullscreen
  useEffect(() => {
    const hasFullscreenSupport = document.documentElement.requestFullscreen || 
                                (document.documentElement as any).webkitRequestFullscreen || 
                                (document.documentElement as any).mozRequestFullScreen || 
                                (document.documentElement as any).msRequestFullscreen;
    
    setFullscreenSupported(!!hasFullscreenSupport);
    
    if (!hasFullscreenSupport && isDevelopment) {
      console.warn('AVISO: Este navegador não suporta a API Fullscreen. Usando modo alternativo.');
    }
  }, [isDevelopment]);

  // Função para ativar o modo tela cheia
  const enableFullscreen = () => {
    if (!isFullscreen && fullscreenSupported && !isPWA) {
      try {
        console.log("Tentando ativar modo tela cheia...");
        setFullscreenAttempts(prev => prev + 1);
        
        // Tentar diferentes métodos de fullscreen para compatibilidade entre navegadores
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen().catch(err => {
            console.error('Erro ao entrar em tela cheia:', err);
            setFullscreenError(err instanceof Error ? err.message : String(err));
          });
        } else if ((document.documentElement as any).webkitRequestFullscreen) {
          (document.documentElement as any).webkitRequestFullscreen();
        } else if ((document.documentElement as any).mozRequestFullScreen) {
          (document.documentElement as any).mozRequestFullScreen();
        } else if ((document.documentElement as any).msRequestFullscreen) {
          (document.documentElement as any).msRequestFullscreen();
        } else {
          throw new Error("Navegador não suporta API Fullscreen");
        }
        setFullscreenError(null);
      } catch (err) {
        console.error(`Erro ao tentar entrar em modo tela cheia:`, err);
        setFullscreenError(err instanceof Error ? err.message : String(err));
        
        // Marcar como não suportado se ocorrer um erro
        if (fullscreenAttempts > 3) {
          setFullscreenSupported(false);
        }
      }
    }
  };

  // Função para detectar saída do modo tela cheia
  const handleFullscreenChange = () => {
    // Se estamos em modo PWA, sempre considerar como tela cheia
    if (isPWA) {
      setIsFullscreen(true);
      return;
    }
    
    const isInFullscreen = !!document.fullscreenElement || 
                         !!(document as any).webkitFullscreenElement || 
                         !!(document as any).mozFullScreenElement || 
                         !!(document as any).msFullscreenElement;
                         
    console.log("Estado da tela cheia alterado:", isInFullscreen ? "ATIVO" : "INATIVO");
    setIsFullscreen(isInFullscreen);
    
    // Se saiu do modo tela cheia e o modo quiosque está ativado, tenta reativar
    // Mas apenas se não estivermos na rota de administração e não for PWA
    if (!isInFullscreen && kioskModeActive && fullscreenSupported && !isPWA) {
      // Verificar se não estamos na página de administração
      const isAdminPage = window.location.pathname.includes('/admin');
      
      if (!isAdminPage) {
        console.log("Tentando reativar modo tela cheia após saída...");
        // Mostrar o prompt novamente se sair da tela cheia
        setShowPrompt(true);
      }
    }
  };

  // Função para impedir teclas de sistema
  const handleKeyDown = (e: KeyboardEvent) => {
    // Se o modo quiosque não estiver ativo, não bloqueamos teclas
    if (!kioskModeActive) return true;
    
    // Verificar se estamos na página de administração
    const isAdminPage = window.location.pathname.includes('/admin');
    if (isAdminPage) return true;
    
    // Impedir Alt+F4, Alt+Tab, tecla Windows, etc.
    if (
      (e.key === 'F4' && e.altKey) ||
      (e.key === 'Tab' && e.altKey) ||
      e.key === 'Meta' ||
      e.key === 'F11' ||
      (e.ctrlKey && e.altKey && e.key === 'Delete') ||
      (e.key === 'Escape' && isFullscreen)
    ) {
      e.preventDefault();
      return false;
    }
  };

  // Função para impedir clique direito
  const handleContextMenu = (e: MouseEvent) => {
    // Se o modo quiosque não estiver ativo, não bloqueamos o menu de contexto
    if (!kioskModeActive) return true;
    
    // Verificar se estamos na página de administração
    const isAdminPage = window.location.pathname.includes('/admin');
    if (isAdminPage) return true;
    
    e.preventDefault();
    return false;
  };

  // Detectar interação do usuário para ativar o modo tela cheia
  const handleUserInteraction = (e?: Event) => {
    // Se o evento veio de um elemento interativo (botão, link, etc.), não processar
    if (e && e.target) {
      const target = e.target as HTMLElement;
      console.log('🔍 DEBUG - KioskMode: Evento detectado em:', target.tagName, target.className);
      
      const isInteractive = target.tagName === 'BUTTON' || 
                           target.tagName === 'A' || 
                           target.tagName === 'INPUT' || 
                           target.tagName === 'SELECT' || 
                           target.tagName === 'TEXTAREA' ||
                           target.closest('button') ||
                           target.closest('a') ||
                           target.closest('input') ||
                           target.closest('select') ||
                           target.closest('textarea') ||
                           target.closest('[role="button"]') ||
                           target.closest('[onclick]');
      
      if (isInteractive) {
        console.log('🔍 DEBUG - KioskMode: Elemento interativo detectado, permitindo evento');
        // Permitir que o evento continue normalmente para elementos interativos
        return;
      }
    }
    
    console.log("Interação do usuário detectada");
    
    // Se já estamos em modo PWA, não precisamos fazer nada
    if (isPWA) {
      return;
    }
    
    if (!userInteracted && kioskModeActive) {
      console.log("Marcando usuário como tendo interagido");
      setUserInteracted(true);
      setShowPrompt(false);
      
      // Se o navegador suporta tela cheia, tentamos ativar
      if (fullscreenSupported && !isPWA) {
        // Pequeno timeout para garantir que o navegador reconheça a interação do usuário
        setTimeout(() => {
          enableFullscreen();
        }, 100);
      }
    } else if (kioskModeActive && !isFullscreen && fullscreenSupported && !isPWA) {
      // Se o usuário já interagiu mas não estamos em tela cheia, tentar novamente
      setTimeout(() => {
        enableFullscreen();
      }, 100);
    }
  };

  // Tentativa de iniciar automaticamente o modo tela cheia
  useEffect(() => {
    // Se estamos em modo PWA, não precisamos tentar entrar em tela cheia
    if (isPWA) {
      return;
    }
    
    if (kioskModeActive && !autoStartAttempted && !isPWA) {
      setAutoStartAttempted(true);
      
      // Adicionar um evento de clique automático para simular interação do usuário
      const autoStartFullscreen = () => {
        // Criar um elemento invisível para receber o clique
        const clickTrigger = document.createElement('button');
        clickTrigger.style.position = 'fixed';
        clickTrigger.style.opacity = '0';
        clickTrigger.style.pointerEvents = 'none';
        document.body.appendChild(clickTrigger);
        
        // Simular clique no elemento
        clickTrigger.click();
        
        // Remover o elemento após o clique
        document.body.removeChild(clickTrigger);
        
        // Marcar como interagido
        setUserInteracted(true);
        
        // Tentar entrar em tela cheia após uma pequena espera
        setTimeout(() => {
          enableFullscreen();
        }, 500);
      };
      
      // Executar após um pequeno delay para garantir que a página foi carregada
      setTimeout(autoStartFullscreen, 1000);
    }
  }, [kioskModeActive, autoStartAttempted, isPWA]);

  // Aplicar estilos de fallback quando a API Fullscreen não é suportada
  useEffect(() => {
    if (kioskModeActive && userInteracted && (!fullscreenSupported || isPWA)) {
      // Adicionar classe ao body para simular tela cheia via CSS
      document.body.classList.add('kiosk-fallback-mode');
      
      // Adicionar estilos CSS para simular tela cheia
      const style = document.createElement('style');
      style.innerHTML = `
        .kiosk-fallback-mode {
          overflow: hidden !important;
          position: fixed !important;
          width: 100% !important;
          height: 100% !important;
          max-width: 100% !important;
          max-height: 100% !important;
        }
        
        .kiosk-fallback-mode #root {
          width: 100% !important;
          height: 100% !important;
          position: fixed !important;
          top: 0 !important;
          left: 0 !important;
          right: 0 !important;
          bottom: 0 !important;
          z-index: 9999 !important;
        }
      `;
      document.head.appendChild(style);
      
      return () => {
        document.body.classList.remove('kiosk-fallback-mode');
        document.head.removeChild(style);
      };
    }
    
    return undefined;
  }, [kioskModeActive, userInteracted, fullscreenSupported, isPWA]);

  // Monitorar mudanças na URL para verificar se estamos na página de admin
  useEffect(() => {
    const handleLocationChange = () => {
      const isAdminPage = window.location.pathname.includes('/admin');
      
      // Se não estamos na página de admin e o modo quiosque está ativo,
      // garantimos que estamos em tela cheia
      if (!isAdminPage && kioskModeActive && !isFullscreen && fullscreenSupported && !isPWA) {
        enableFullscreen();
      }
    };
    
    // Adicionar listener para o evento popstate (quando o usuário navega)
    window.addEventListener('popstate', handleLocationChange);
    
    return () => {
      window.removeEventListener('popstate', handleLocationChange);
    };
  }, [kioskModeActive, isFullscreen, fullscreenSupported, isPWA]);

  // Mostrar o prompt de tela cheia após um pequeno delay
  useEffect(() => {
    // Se estamos em modo PWA, nunca mostrar o prompt
    if (isPWA) {
      setShowPrompt(false);
      return;
    }
    
    if (kioskModeActive && !initialPromptShown && !isPWA) {
      const promptTimer = setTimeout(() => {
        if (!isFullscreen && !document.fullscreenElement) {
          console.log("Mostrando prompt de tela cheia");
          setShowPrompt(true);
          setInitialPromptShown(true);
        }
      }, 1500);
      
      return () => {
        clearTimeout(promptTimer);
      };
    }
    
    return undefined;
  }, [kioskModeActive, initialPromptShown, isFullscreen, isPWA]);

  // Tentar entrar em tela cheia periodicamente se não estamos em tela cheia
  useEffect(() => {
    // Se estamos em modo PWA, não precisamos verificar periodicamente
    if (isPWA) {
      return;
    }
    
    if (kioskModeActive && !isFullscreen && fullscreenSupported && !isPWA) {
      const retryTimer = setInterval(() => {
        // Verificar se já estamos em tela cheia
        const isInFullscreen = !!document.fullscreenElement || 
                             !!(document as any).webkitFullscreenElement || 
                             !!(document as any).mozFullScreenElement || 
                             !!(document as any).msFullscreenElement;
        
        // Se não estamos em tela cheia e não estamos na página de admin, mostrar o prompt
        if (!isInFullscreen && !window.location.pathname.includes('/admin')) {
          console.log("Verificação periódica: não estamos em tela cheia, mostrando prompt");
          setShowPrompt(true);
        } else {
          setShowPrompt(false);
        }
      }, 5000); // Verificar a cada 5 segundos
      
      return () => {
        clearInterval(retryTimer);
      };
    }
    
    return undefined;
  }, [kioskModeActive, isFullscreen, fullscreenSupported, isPWA]);

  useEffect(() => {
    if (kioskModeActive) {
      console.log("Modo quiosque ATIVADO");
      
      // Adicionar listeners para eventos de tela cheia
      document.addEventListener('fullscreenchange', handleFullscreenChange);
      document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.addEventListener('mozfullscreenchange', handleFullscreenChange);
      document.addEventListener('MSFullscreenChange', handleFullscreenChange);
      
      // Adicionar listeners para eventos de teclado e contexto
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('contextmenu', handleContextMenu);
      
      // Adicionar listeners para detectar interação do usuário
      document.addEventListener('click', handleUserInteraction);
      document.addEventListener('touchstart', handleUserInteraction);
      
      // Impedir que o usuário feche a janela
      window.addEventListener('beforeunload', (e) => {
        if (kioskModeActive) {
          // Verificar se estamos na página de administração
          const isAdminPage = window.location.pathname.includes('/admin');
          if (!isAdminPage) {
            e.preventDefault();
            e.returnValue = '';
            return '';
          }
        }
      });
      
      // Exibir mensagem no console para desenvolvimento
      if (isDevelopment) {
        console.info(`Modo quiosque ${kioskModeActive ? 'ATIVADO' : 'DESATIVADO'}`);
        console.info('Para desativar o modo quiosque em desenvolvimento, defina VITE_DISABLE_KIOSK_MODE=true no arquivo .env');
        
        if (isPWA) {
          console.info('Aplicação rodando como PWA, não é necessário ativar tela cheia manualmente');
        }
      }
      
      return () => {
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
        document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
        document.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('contextmenu', handleContextMenu);
        document.removeEventListener('click', handleUserInteraction);
        document.removeEventListener('touchstart', handleUserInteraction);
      };
    } else {
      console.log("Modo quiosque DESATIVADO");
    }
    
    return undefined;
  }, [kioskModeActive, isFullscreen, isPWA]);

  return (
    <>
      {kioskModeActive && !isPWA && <IOSFullscreen />}
      <AnimatePresence>
        {showPrompt && !isPWA && (
          <FullscreenPrompt 
            onInteraction={handleUserInteraction} 
            visible={showPrompt} 
          />
        )}
      </AnimatePresence>
      {fullscreenError && !isPWA && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-2 text-sm z-50">
          Erro ao ativar tela cheia: {fullscreenError}
        </div>
      )}
      {children}
    </>
  );
};

export default KioskMode; 