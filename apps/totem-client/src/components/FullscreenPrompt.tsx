import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface FullscreenPromptProps {
  onInteraction: () => void;
  visible: boolean;
}

const FullscreenPrompt: React.FC<FullscreenPromptProps> = ({ onInteraction, visible }) => {
  const [pulsing, setPulsing] = useState(false);
  
  // Efeito de pulsação para chamar atenção
  useEffect(() => {
    if (visible) {
      const interval = setInterval(() => {
        setPulsing(prev => !prev);
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [visible]);

  // Função para ativar o modo tela cheia diretamente
  const activateFullscreen = () => {
    try {
      console.log("Tentando ativar tela cheia diretamente");
      
      // Tentativa direta de entrar em modo tela cheia
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
      
      // Notificar o componente pai
      onInteraction();
    } catch (error) {
      console.error("Erro ao ativar tela cheia:", error);
    }
  };
  
  // Função para garantir que o evento de clique seja tratado
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    console.log("Botão de tela cheia clicado");
    activateFullscreen();
  };
  
  if (!visible) return null;
  
  return (
    <motion.div 
      className="fixed inset-0 bg-primary/95 z-50 flex flex-col items-center justify-center p-6 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={handleClick}
    >
      <motion.div 
        className="bg-white rounded-xl p-8 max-w-md shadow-lg"
        animate={{ scale: pulsing ? 1.05 : 1 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-2xl font-bold mb-4 text-primary">Modo Tela Cheia</h2>
        
        <div className="mb-6">
          <motion.div 
            className="w-24 h-24 mx-auto mb-4"
            animate={{ scale: pulsing ? 1.2 : 1 }}
            transition={{ duration: 0.5 }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#1A3A4A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
            </svg>
          </motion.div>
          
          <p className="text-gray-700 mb-4 text-lg">
            Para uma melhor experiência, toque em qualquer lugar da tela para ativar o modo de tela cheia.
          </p>
          
          <p className="text-base text-red-600 font-medium">
            O navegador requer sua interação para ativar o modo tela cheia.
          </p>
        </div>
        
        <motion.button 
          className="bg-secondary text-primary font-semibold py-4 px-8 rounded-lg text-xl hover:bg-secondary/90 transition-colors w-full"
          onClick={handleClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          autoFocus
        >
          TOQUE AQUI PARA ATIVAR TELA CHEIA
        </motion.button>
        
        <p className="mt-4 text-sm text-gray-500">
          Este aplicativo funciona melhor em modo tela cheia
        </p>
      </motion.div>
    </motion.div>
  );
};

export default FullscreenPrompt; 