import React, { useState, useEffect } from 'react';

interface ServiceCountdownProps {
  startTime: string;
  duration: number; // duração em minutos
  className?: string;
  onComplete?: () => void;
}

export const ServiceCountdown: React.FC<ServiceCountdownProps> = ({ 
  startTime, 
  duration,
  className = '',
  onComplete 
}) => {
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  
  // Calcular tempo restante em segundos
  useEffect(() => {
    const calculateTimeLeft = () => {
      const start = new Date(startTime).getTime();
      const end = start + (duration * 60 * 1000); // converter minutos para milissegundos
      const now = new Date().getTime();
      
      // Tempo restante em segundos
      return Math.max(0, Math.floor((end - now) / 1000));
    };
    
    // Inicializar
    setTimeLeft(calculateTimeLeft());
    
    // Atualizar a cada segundo
    const timer = setInterval(() => {
      const remaining = calculateTimeLeft();
      setTimeLeft(remaining);
      
      if (remaining <= 0 && !isCompleted) {
        setIsCompleted(true);
        if (onComplete) onComplete();
        clearInterval(timer);
      }
    }, 1000);
    
    return () => clearInterval(timer);
  }, [startTime, duration, onComplete, isCompleted]);
  
  // Formatar o tempo restante
  const formatTimeLeft = (): string => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  // Calcular porcentagem de progresso
  const calculateProgress = (): number => {
    const totalSeconds = duration * 60;
    const elapsedSeconds = totalSeconds - timeLeft;
    return Math.min(100, Math.round((elapsedSeconds / totalSeconds) * 100));
  };
  
  const progress = calculateProgress();
  
  // Determinar cor da barra de progresso
  const getProgressColor = (): string => {
    if (progress < 50) return 'bg-[#3B82F6]';
    if (progress < 80) return 'bg-[#F59E0B]';
    return 'bg-[#EF4444]';
  };
  
  return (
    <div className={`service-countdown ${className}`}>
      <div className="flex justify-between items-center mb-1">
        <span className="text-lg font-bold">{formatTimeLeft()}</span>
        <span className="text-sm text-gray-500">{progress}%</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className={`h-2.5 rounded-full ${getProgressColor()}`} 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
}; 