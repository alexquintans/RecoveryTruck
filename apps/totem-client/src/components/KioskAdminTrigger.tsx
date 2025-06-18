import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Componente que detecta uma sequência especial de toques ou combinação de teclas
 * para acessar a área administrativa
 */
const KioskAdminTrigger: React.FC = () => {
  const navigate = useNavigate();
  const [touchSequence, setTouchSequence] = useState<string[]>([]);
  const [lastTouchTime, setLastTouchTime] = useState<number>(0);
  const [keySequence, setKeySequence] = useState<string[]>([]);
  const [lastKeyTime, setLastKeyTime] = useState<number>(0);
  
  // Tempo limite para completar a sequência (em milissegundos)
  const SEQUENCE_TIMEOUT = 3000;
  
  // A sequência correta de toques nos cantos
  const ADMIN_TOUCH_SEQUENCE = ['tl', 'tr', 'br', 'bl', 'tl'];
  
  // A sequência correta de teclas (Ctrl + Alt + A)
  const ADMIN_KEY_SEQUENCE = ['Control', 'Alt', 'a'];
  
  // Função para identificar em qual canto da tela o toque ocorreu
  const identifyCorner = (x: number, y: number): string => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    const cornerSize = Math.min(width, height) * 0.15; // 15% da menor dimensão
    
    if (x < cornerSize && y < cornerSize) return 'tl'; // top-left
    if (x > width - cornerSize && y < cornerSize) return 'tr'; // top-right
    if (x > width - cornerSize && y > height - cornerSize) return 'br'; // bottom-right
    if (x < cornerSize && y > height - cornerSize) return 'bl'; // bottom-left
    
    return 'center'; // não é um canto
  };
  
  // Manipulador de eventos de toque
  const handleTouch = (e: TouchEvent) => {
    const touch = e.touches[0];
    const corner = identifyCorner(touch.clientX, touch.clientY);
    const currentTime = Date.now();
    
    // Se não for um toque em um canto, ignoramos
    if (corner === 'center') {
      return;
    }
    
    // Se passou muito tempo desde o último toque, reiniciamos a sequência
    if (currentTime - lastTouchTime > SEQUENCE_TIMEOUT && touchSequence.length > 0) {
      setTouchSequence([corner]);
    } else {
      // Adicionamos o novo canto à sequência
      setTouchSequence(prev => [...prev, corner]);
    }
    
    setLastTouchTime(currentTime);
  };
  
  // Manipulador de eventos de teclado
  const handleKeyDown = (e: KeyboardEvent) => {
    const currentTime = Date.now();
    const key = e.key;
    
    // Se passou muito tempo desde a última tecla, reiniciamos a sequência
    if (currentTime - lastKeyTime > SEQUENCE_TIMEOUT && keySequence.length > 0) {
      setKeySequence([key]);
    } else {
      // Se a tecla já está na sequência, não adicionamos novamente
      if (!keySequence.includes(key)) {
        setKeySequence(prev => [...prev, key]);
      }
    }
    
    setLastKeyTime(currentTime);
    
    // Verificamos se todas as teclas da sequência administrativa estão pressionadas
    const isCtrlPressed = e.ctrlKey || keySequence.includes('Control');
    const isAltPressed = e.altKey || keySequence.includes('Alt');
    const isAPressed = keySequence.includes('a');
    
    if (isCtrlPressed && isAltPressed && isAPressed) {
      // Redirecionamos para a página de administração
      navigate('/admin');
      // Limpamos a sequência
      setKeySequence([]);
      e.preventDefault();
    }
  };
  
  // Manipulador de eventos de tecla solta
  const handleKeyUp = (e: KeyboardEvent) => {
    const key = e.key;
    // Removemos a tecla da sequência quando ela é solta
    setKeySequence(prev => prev.filter(k => k !== key));
  };
  
  // Verificar se a sequência de toques está correta
  useEffect(() => {
    // Convertemos a sequência atual para uma string para comparação fácil
    const currentSequence = touchSequence.join('-');
    const targetSequence = ADMIN_TOUCH_SEQUENCE.join('-');
    
    // Se a sequência atual corresponder à sequência de administrador
    if (currentSequence === targetSequence) {
      // Redirecionamos para a página de administração
      navigate('/admin');
      // Limpamos a sequência
      setTouchSequence([]);
    }
    
    // Se a sequência ficar muito longa, cortamos para evitar uso excessivo de memória
    if (touchSequence.length > 10) {
      setTouchSequence(touchSequence.slice(-5));
    }
  }, [touchSequence, navigate]);
  
  // Adicionar os listeners de eventos
  useEffect(() => {
    document.addEventListener('touchstart', handleTouch);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    
    return () => {
      document.removeEventListener('touchstart', handleTouch);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [lastTouchTime, touchSequence, lastKeyTime, keySequence]);
  
  // Este componente não renderiza nada visível
  return null;
};

export default KioskAdminTrigger; 