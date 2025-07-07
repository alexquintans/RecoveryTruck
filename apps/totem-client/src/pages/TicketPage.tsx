import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { useQueueWebSocket } from '../hooks/useQueueWebSocket';
import { formatDate } from '../utils';
import { useQuery } from '@tanstack/react-query';
import { api } from '../utils/api';

const TicketPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentTicket, selectedService, customerData, reset } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  const [countdown, setCountdown] = useState(15); // Reduzido para 15 segundos
  
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';
  const { data: operationConfig } = useQuery({
    queryKey: ['operationConfig', tenantId],
    queryFn: () => api.getOperationConfig(tenantId),
  });
  const extrasConfig = (operationConfig?.extras || []).filter((x: any) => x.active);
  const selectedExtras = customerData?.extras || [];
  const extrasResumo = selectedExtras.map((e: any) => {
    const config = extrasConfig.find((x: any) => x.extra_id === e.id);
    return config ? {
      name: config.name,
      price: config.price,
      quantity: e.quantity,
      subtotal: config.price * e.quantity,
    } : null;
  }).filter(Boolean);
  const subtotalServico = selectedService?.price || 0;
  const subtotalExtras = extrasResumo.reduce((acc, e) => acc + e.subtotal, 0);
  const total = subtotalServico + subtotalExtras;

  // Redirecionar se não houver ticket
  if (!currentTicket || !selectedService) {
    navigate('/');
    return null;
  }

  // WebSocket para receber atualizações em tempo real
  const { isConnected } = useQueueWebSocket({
    tenantId,
    enabled: true,
    onTicketCalled: (ticketId, ticketNumber) => {
      console.log(`🎉 Ticket #${ticketNumber} foi chamado! Redirecionando para fila...`);
      // Redirecionar imediatamente se o ticket foi chamado
      handleGoToQueue();
    },
  });

  // Número do ticket para exibição
  const displayNumber = currentTicket.number ??
    (currentTicket.ticket_number !== undefined ? `#${String(currentTicket.ticket_number).padStart(3, '0')}` : undefined) ??
    (currentTicket.ticketNumber !== undefined ? `#${String(currentTicket.ticketNumber).padStart(3, '0')}` : undefined) ?? '--';

  // Efeito para tocar o som de ticket e iniciar contagem regressiva
  useEffect(() => {
    // Tocar som de ticket
    soundNotifications.play('ticket');
    
    // Iniciar contagem regressiva
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // Redirecionar para a página da fila após o término da contagem
          setTimeout(() => {
            handleGoToQueue();
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

  // Ir para a página da fila
  const handleGoToQueue = () => {
    navigate('/queue');
  };

  // Finalizar e voltar para a página inicial (opção manual)
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
          {currentTicket.status === 'print_error' ? (
            <>
              <h2 className="text-3xl font-bold text-red-600 mb-2">Erro na Impressão</h2>
              <p className="text-text-light">Houve um problema ao imprimir seu ticket. Procure um atendente.</p>
            </>
          ) : (
            <>
              <h2 className="text-3xl font-bold text-primary mb-2">Ticket Gerado com Sucesso!</h2>
              <p className="text-text-light">Seu ticket foi impresso. Por favor, aguarde ser chamado.</p>
            </>
          )}
          
          {/* Status do WebSocket */}
          <div className="flex justify-center items-center gap-2 mt-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-xs text-gray-500">
              {isConnected ? 'Conectado para atualizações' : 'Aguardando conexão...'}
            </span>
          </div>
        </div>

        <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-6 mb-8 max-w-md mx-auto">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-primary">RecoveryTruck</h3>
            <p className="text-sm text-text-light">Serviços de Recuperação Física</p>
          </div>
          
          <div className="border-t border-b border-gray-200 py-4 my-4">
            <div className="flex justify-between mb-2">
              <span className="font-semibold">Número:</span>
              <span className="text-xl font-bold">{displayNumber}</span>
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
            {currentTicket.status === 'print_error' ? (
              <p className="text-sm text-red-600 font-semibold">Dirija-se ao balcão para assistência.</p>
            ) : (
              <p className="text-sm text-text-light">Acompanhe sua posição na fila pelo painel.</p>
            )}
            <p className="text-sm font-semibold mt-2">
              Tempo estimado de espera: 10 minutos
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-8 max-w-lg mx-auto">
          <h3 className="text-xl font-bold text-primary mb-4">Resumo do Pedido</h3>
          <div className="flex justify-between mb-2">
            <span className="font-semibold">Serviço:</span>
            <span>{selectedService.name}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span>Duração:</span>
            <span>{selectedService.duration} min</span>
          </div>
          <div className="flex justify-between mb-2">
            <span>Valor do Serviço:</span>
            <span>R$ {selectedService.price.toFixed(2)}</span>
          </div>
          {extrasResumo.length > 0 && <>
            <div className="border-t my-2"></div>
            <div className="font-semibold mb-2">Extras:</div>
            {extrasResumo.map((e, idx) => (
              <div className="flex justify-between mb-1 text-sm" key={idx}>
                <span>{e.name} x{e.quantity}</span>
                <span>R$ {e.subtotal.toFixed(2)}</span>
              </div>
            ))}
            <div className="flex justify-between mt-2">
              <span>Subtotal Extras:</span>
              <span>R$ {subtotalExtras.toFixed(2)}</span>
            </div>
          </>}
          <div className="border-t my-2"></div>
          <div className="flex justify-between text-lg font-bold">
            <span>Total:</span>
            <span>R$ {total.toFixed(2)}</span>
          </div>
        </div>

        <div className="mt-8 space-y-4">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={handleGoToQueue}
            className="w-full"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            }
            iconPosition="right"
          >
            Acompanhar Fila ({countdown}s)
          </Button>
          
          <Button 
            variant="secondary" 
            size="lg" 
            onClick={handleFinish}
            className="w-full"
          >
            Finalizar Agora
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default TicketPage; 