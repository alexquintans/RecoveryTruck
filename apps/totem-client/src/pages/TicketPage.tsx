import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { formatDate } from '../utils';

const TicketPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentTicket, selectedService, customerData, reset } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  const [countdown, setCountdown] = useState(30); // Contagem regressiva em segundos
  
  // Redirecionar se não houver ticket
  if (!currentTicket || !selectedService) {
    navigate('/');
    return null;
  }

  // Efeito para tocar o som de ticket e iniciar contagem regressiva
  useEffect(() => {
    // Tocar som de ticket
    soundNotifications.play('ticket');
    
    // Iniciar contagem regressiva
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // Redirecionar para a página inicial após o término da contagem
          setTimeout(() => {
            handleFinish();
          }, 1000);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => {
      clearInterval(timer);
    };
  }, []);

  // Finalizar e voltar para a página inicial
  const handleFinish = () => {
    reset(); // Limpar o estado
    navigate('/');
  };

  return (
    <div className="totem-card">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-primary mb-2">
            Ticket Gerado com Sucesso!
          </h2>
          <p className="text-text-light">
            Seu ticket foi impresso. Por favor, aguarde ser chamado.
          </p>
        </div>

        <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-6 mb-8 max-w-md mx-auto">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-primary">RecoveryTruck</h3>
            <p className="text-sm text-text-light">Serviços de Recuperação Física</p>
          </div>
          
          <div className="border-t border-b border-gray-200 py-4 my-4">
            <div className="flex justify-between mb-2">
              <span className="font-semibold">Número:</span>
              <span className="text-xl font-bold">{currentTicket.number}</span>
            </div>
            
            <div className="flex justify-between mb-2">
              <span className="font-semibold">Serviço:</span>
              <span>{selectedService.name}</span>
            </div>
            
            {customerData?.name && (
              <div className="flex justify-between mb-2">
                <span className="font-semibold">Cliente:</span>
                <span>{customerData.name}</span>
              </div>
            )}
            
            <div className="flex justify-between">
              <span className="font-semibold">Data/Hora:</span>
              <span>{formatDate(currentTicket.createdAt)}</span>
            </div>
          </div>
          
          <div className="text-center mt-4">
            <p className="text-sm text-text-light">
              Acompanhe sua posição na fila pelo painel.
            </p>
            <p className="text-sm font-semibold mt-2">
              Tempo estimado de espera: 10 minutos
            </p>
          </div>
        </div>

        <div className="mt-8">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={handleFinish}
            className="w-full"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            }
            iconPosition="right"
          >
            Finalizar ({countdown}s)
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default TicketPage; 