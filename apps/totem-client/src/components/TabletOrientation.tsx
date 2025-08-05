import { useEffect, useState } from 'react';

interface TabletOrientationProps {
  children: React.ReactNode;
}

/**
 * Componente para gerenciar orientação e comportamento específico em tablets
 */
const TabletOrientation: React.FC<TabletOrientationProps> = ({ children }) => {
  const [isTablet, setIsTablet] = useState(false);
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');
  const [showOrientationWarning, setShowOrientationWarning] = useState(false);

  useEffect(() => {
    const detectTablet = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      const isTabletDevice = /ipad|android(?=.*\bMobile\b)(?=.*\bSafari\b)/i.test(userAgent) || 
                            (window.innerWidth >= 768 && window.innerWidth <= 1024);
      
      setIsTablet(isTabletDevice);
      
      if (isTabletDevice) {
        console.log('Tablet detectado, aplicando configurações específicas');
        
        // Forçar orientação portrait
        const lockOrientation = async () => {
          try {
            if (screen.orientation && (screen.orientation as any).lock) {
              await (screen.orientation as any).lock('portrait');
              console.log('Orientação travada em portrait');
            }
          } catch (error) {
            console.warn('Não foi possível travar a orientação:', error);
          }
        };
        
        lockOrientation();
        
        // Detectar mudanças de orientação
        const handleOrientationChange = () => {
          const currentOrientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
          setOrientation(currentOrientation);
          
          if (currentOrientation === 'landscape') {
            setShowOrientationWarning(true);
          } else {
            setShowOrientationWarning(false);
          }
        };
        
        // Verificar orientação inicial
        handleOrientationChange();
        
        // Adicionar listener para mudanças de orientação
        window.addEventListener('orientationchange', handleOrientationChange);
        window.addEventListener('resize', handleOrientationChange);
        
        // Adicionar meta tags para orientação
        const orientationMeta = document.createElement('meta');
        orientationMeta.name = 'screen-orientation';
        orientationMeta.content = 'portrait';
        document.head.appendChild(orientationMeta);
        
        const orientationMeta2 = document.createElement('meta');
        orientationMeta2.name = 'x5-orientation';
        orientationMeta2.content = 'portrait';
        document.head.appendChild(orientationMeta2);
        
        return () => {
          window.removeEventListener('orientationchange', handleOrientationChange);
          window.removeEventListener('resize', handleOrientationChange);
        };
      }
    };
    
    detectTablet();
  }, []);

  if (!isTablet) {
    return <>{children}</>;
  }

  return (
    <>
      {showOrientationWarning && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm mx-4 text-center">
            <div className="text-6xl mb-4">📱</div>
            <h2 className="text-xl font-bold mb-2">Gire o Tablet</h2>
            <p className="text-gray-600">
              Para melhor experiência, use o tablet na orientação vertical (portrait).
            </p>
            <button
              onClick={() => setShowOrientationWarning(false)}
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Entendi
            </button>
          </div>
        </div>
      )}
      
      <div className={`tablet-container ${orientation === 'landscape' ? 'landscape' : 'portrait'}`}>
        {children}
      </div>
      
      <style dangerouslySetInnerHTML={{
        __html: `
          .tablet-container {
            width: 100%;
            height: 100%;
            overflow: hidden;
          }
          
          .tablet-container.landscape {
            transform: rotate(90deg);
            transform-origin: center center;
            width: 100vh;
            height: 100vw;
          }
          
          @media (orientation: landscape) and (max-height: 600px) {
            .tablet-container {
              transform: scale(0.8);
            }
          }
        `
      }} />
    </>
  );
};

export default TabletOrientation; 