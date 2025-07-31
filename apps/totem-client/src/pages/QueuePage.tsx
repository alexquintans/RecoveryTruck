import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { useQueueWebSocket } from '../hooks/useQueueWebSocket';
import { api, type QueueTicket, type QueueInfo } from '../utils/api';

const QueuePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentTicket, selectedService, customerData, reset } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [userTicket, setUserTicket] = useState<QueueTicket | null>(null);
  const [userPosition, setUserPosition] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRedirectCountdown, setAutoRedirectCountdown] = useState(8); // 8 segundos
  
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '38534c9f-accb-4884-9c19-dd37f77d0594';

  // Redirecionar se não houver ticket
  if (!currentTicket || !selectedService) {
    navigate('/');
    return null;
  }

  // Auto-redirecionamento para página inicial
  useEffect(() => {
    const timer = setInterval(() => {
      setAutoRedirectCountdown((prev) => {
        if (prev <= 1) {
          reset();
          navigate('/');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate, reset]);

  // WebSocket para atualizações em tempo real
  const { isConnected, isConnecting, isError, lastMessage } = useQueueWebSocket({
    tenantId,
    enabled: true,
    onQueueUpdate: (update) => {
      console.log('🔄 Queue update received via WebSocket:', update);
      
      // Se recebeu atualização de ticket, buscar dados atualizados da fila
      if (update.type === 'ticket_update' || update.type === 'ticket_status_changed') {
        fetchQueueInfo();
      }
    },
    onTicketCalled: (ticketId, ticketNumber) => {
      console.log(`🎉 Ticket #${ticketNumber} foi chamado!`);
    },
  });

  // Buscar informações da fila
  const fetchQueueInfo = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Buscar fila completa
      const queueData = await api.getQueue(tenantId);
      setQueueInfo(queueData);
      
      // Encontrar o ticket do usuário na fila
      const userTicketInQueue = queueData.items.find(
        (ticket: QueueTicket) => ticket.id === currentTicket.id
      );
      
      if (userTicketInQueue) {
        setUserTicket(userTicketInQueue);
        
        // Calcular posição na fila (apenas tickets IN_QUEUE)
        const inQueueTickets = queueData.items.filter(
          (ticket: QueueTicket) => ticket.status === 'in_queue'
        );
        
        const position = inQueueTickets.findIndex(
          (ticket: QueueTicket) => ticket.id === currentTicket.id
        );
        
        setUserPosition(position >= 0 ? position + 1 : null);
      } else {
        // Ticket não encontrado na fila (pode ter sido chamado ou concluído)
        setUserTicket(null);
        setUserPosition(null);
      }
    } catch (err) {
      console.error('❌ Erro ao buscar informações da fila:', err);
      setError('Erro ao carregar informações da fila');
    } finally {
      setIsLoading(false);
    }
  }, [tenantId, currentTicket.id]);

  // Buscar dados iniciais
  useEffect(() => {
    fetchQueueInfo();
  }, [fetchQueueInfo]);

  const handleFinish = () => {
    reset();
    navigate('/');
  };

  if (isLoading) {
    return (
      <div className="totem-card">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-primary mb-2">Carregando...</h2>
          <p className="text-text-light">Buscando informações da fila</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="totem-card">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Erro</h2>
          <p className="text-text-light mb-4">{error}</p>
          <Button onClick={handleFinish} variant="primary">
            Voltar ao Início
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="totem-card">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-primary mb-2">Sua Posição na Fila</h2>
          <p className="text-text-light">Aguarde ser chamado</p>
        </div>

        {/* Posição na Fila - Foco Principal */}
        {userPosition && userTicket?.status === 'in_queue' ? (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <div className="text-center">
              <div className="text-6xl font-bold text-blue-600 mb-4">{userPosition}</div>
              <p className="text-2xl text-gray-700 mb-2">Sua posição na fila</p>
              <p className="text-sm text-gray-500">Ticket #{currentTicket.ticket_number?.toString().padStart(3, '0')}</p>
            </div>
          </div>
        ) : userTicket?.status === 'called' ? (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <div className="text-center">
              <div className="text-6xl mb-4">🎉</div>
              <div className="text-2xl font-bold text-yellow-600 mb-2">Seu ticket foi chamado!</div>
              <p className="text-lg text-gray-700">Dirija-se ao balcão para atendimento</p>
            </div>
          </div>
        ) : userTicket?.status === 'in_progress' ? (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <div className="text-center">
              <div className="text-6xl mb-4">⚡</div>
              <div className="text-2xl font-bold text-purple-600 mb-2">Em Atendimento</div>
              <p className="text-lg text-gray-700">Seu atendimento está em andamento</p>
            </div>
          </div>
        ) : userTicket?.status === 'completed' ? (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <div className="text-center">
              <div className="text-6xl mb-4">✅</div>
              <div className="text-2xl font-bold text-green-600 mb-2">Atendimento Concluído</div>
              <p className="text-lg text-gray-700">Obrigado por escolher nossos serviços!</p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600 mb-2">Ticket não encontrado na fila</div>
              <p className="text-gray-500">Seu ticket pode ter sido processado</p>
            </div>
          </div>
        )}

        {/* Auto-redirecionamento */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="text-center">
            <p className="text-sm text-blue-800 mb-2">
              ⏰ Retornando automaticamente para a página inicial em {autoRedirectCountdown} segundos
            </p>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-1000"
                style={{ width: `${((8 - autoRedirectCountdown) / 8) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Botões */}
        <div className="space-y-4">
          <Button onClick={handleFinish} variant="primary" className="w-full">
            Voltar ao Início Agora
          </Button>
          
          <Button onClick={handleFinish} variant="secondary" className="w-full">
            Finalizar
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default QueuePage; 