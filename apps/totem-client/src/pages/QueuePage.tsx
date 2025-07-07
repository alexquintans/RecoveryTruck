import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { useQueueWebSocket } from '../hooks/useQueueWebSocket';
import { api, type QueueTicket, type QueueInfo } from '../utils/api';
import { formatDate } from '../utils';

const QueuePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentTicket, selectedService, customerData, reset } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  
  const [queueInfo, setQueueInfo] = useState<QueueInfo | null>(null);
  const [userTicket, setUserTicket] = useState<QueueTicket | null>(null);
  const [userPosition, setUserPosition] = useState<number | null>(null);
  const [estimatedWaitTime, setEstimatedWaitTime] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';

  // Redirecionar se não houver ticket
  if (!currentTicket || !selectedService) {
    navigate('/');
    return null;
  }

  // WebSocket para atualizações em tempo real
  const { isConnected, isConnecting, isError, lastMessage } = useQueueWebSocket({
    tenantId,
    enabled: true,
    onQueueUpdate: (update) => {
      console.log('🔄 Queue update received via WebSocket:', update);
      setLastUpdate(new Date().toLocaleTimeString());
      
      // Se recebeu atualização de ticket, buscar dados atualizados da fila
      if (update.type === 'ticket_update' || update.type === 'ticket_status_changed') {
        fetchQueueInfo();
      }
    },
    onTicketCalled: (ticketId, ticketNumber) => {
      console.log(`🎉 Ticket #${ticketNumber} foi chamado!`);
      // O som já é tocado automaticamente pelo hook
      // Aqui você pode adicionar lógica adicional (ex: mostrar notificação visual)
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
        
        // Calcular tempo estimado de espera
        if (position >= 0) {
          const avgServiceTime = selectedService.duration || 10; // minutos
          const estimatedTime = (position + 1) * avgServiceTime;
          setEstimatedWaitTime(estimatedTime);
        }
      }
      
    } catch (err) {
      console.error('Erro ao buscar fila:', err);
      setError('Erro ao carregar informações da fila');
    } finally {
      setIsLoading(false);
    }
  }, [currentTicket.id, selectedService, tenantId]);

  // Buscar dados iniciais
  useEffect(() => {
    fetchQueueInfo();
  }, [fetchQueueInfo]);

  // Atualizar a cada 30 segundos (fallback caso WebSocket falhe)
  useEffect(() => {
    const interval = setInterval(fetchQueueInfo, 30000);
    return () => clearInterval(interval);
  }, [fetchQueueInfo]);

  // Tocar som quando ticket for chamado (fallback)
  useEffect(() => {
    if (userTicket && userTicket.status === 'called') {
      soundNotifications.play('ticket_called');
    }
  }, [userTicket?.status, soundNotifications]);

  // Finalizar e voltar para a página inicial
  const handleFinish = () => {
    reset();
    navigate('/');
  };

  // Formatar tempo de espera
  const formatWaitTime = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}min`;
  };

  // Obter cor do status
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'in_queue': return 'text-blue-600';
      case 'called': return 'text-yellow-600';
      case 'in_progress': return 'text-purple-600';
      case 'completed': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  // Obter texto do status
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'in_queue': return 'Na Fila';
      case 'called': return 'Chamado';
      case 'in_progress': return 'Em Atendimento';
      case 'completed': return 'Concluído';
      default: return status;
    }
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
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-primary mb-2">Acompanhe sua Fila</h2>
          <p className="text-text-light">Seu ticket está sendo processado</p>
          
          {/* Status do WebSocket */}
          <div className="flex justify-center items-center gap-2 mt-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 
              isConnecting ? 'bg-yellow-500' : 
              'bg-red-500'
            }`}></div>
            <span className="text-xs text-gray-500">
              {isConnected ? 'Conectado' : 
               isConnecting ? 'Conectando...' : 
               'Desconectado'}
            </span>
            {lastUpdate && (
              <span className="text-xs text-gray-400">
                • Última atualização: {lastUpdate}
              </span>
            )}
          </div>
        </div>

        {/* Informações do Ticket */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-primary">RecoveryTruck</h3>
            <p className="text-sm text-text-light">Serviços de Recuperação Física</p>
          </div>
          
          <div className="border-t border-b border-gray-200 py-4 my-4">
            <div className="flex justify-between mb-2">
              <span className="font-semibold">Número:</span>
              <span className="text-xl font-bold">#{currentTicket.ticket_number?.toString().padStart(3, '0') || '---'}</span>
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
              <span className="font-semibold">Status:</span>
              <span className={`font-medium ${getStatusColor(userTicket?.status || 'in_queue')}`}>
                {getStatusText(userTicket?.status || 'in_queue')}
              </span>
            </div>
          </div>
        </div>

        {/* Status da Fila */}
        {userTicket && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-xl font-bold text-primary mb-4">Status da Fila</h3>
            
            {userTicket.status === 'in_queue' && userPosition && (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600 mb-2">{userPosition}</div>
                  <p className="text-lg text-gray-700">Sua posição na fila</p>
                </div>
                
                {estimatedWaitTime && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-2">
                      {formatWaitTime(estimatedWaitTime)}
                    </div>
                    <p className="text-gray-700">Tempo estimado de espera</p>
                  </div>
                )}
                
                {queueInfo && (
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-700 mb-1">
                      {queueInfo.queue_stats.total_active} pessoas na fila
                    </div>
                    <p className="text-sm text-gray-500">
                      Média de espera: {formatWaitTime(queueInfo.queue_stats.waiting_times.average_minutes)}
                    </p>
                  </div>
                )}
              </div>
            )}
            
            {userTicket.status === 'called' && (
              <div className="text-center">
                <div className="text-4xl font-bold text-yellow-600 mb-2">🎉</div>
                <div className="text-2xl font-bold text-yellow-600 mb-2">Seu ticket foi chamado!</div>
                <p className="text-lg text-gray-700">Dirija-se ao balcão para atendimento</p>
              </div>
            )}
            
            {userTicket.status === 'in_progress' && (
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">⚡</div>
                <div className="text-2xl font-bold text-purple-600 mb-2">Em Atendimento</div>
                <p className="text-lg text-gray-700">Seu atendimento está em andamento</p>
              </div>
            )}
            
            {userTicket.status === 'completed' && (
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">✅</div>
                <div className="text-2xl font-bold text-green-600 mb-2">Atendimento Concluído</div>
                <p className="text-lg text-gray-700">Obrigado por escolher nossos serviços!</p>
              </div>
            )}
          </div>
        )}

        {/* Próximos na Fila (apenas se estiver na fila) */}
        {userTicket?.status === 'in_queue' && queueInfo && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-xl font-bold text-primary mb-4">Próximos na Fila</h3>
            
            {queueInfo.items.filter(t => t.status === 'in_queue').slice(0, 5).map((ticket, index) => (
              <div 
                key={ticket.id} 
                className={`flex justify-between items-center py-2 ${
                  ticket.id === currentTicket.id ? 'bg-blue-50 border-l-4 border-blue-500 px-3' : ''
                }`}
              >
                <div className="flex items-center">
                  <span className="font-medium mr-3">{index + 1}.</span>
                  <span className="font-bold">#{ticket.ticket_number.toString().padStart(3, '0')}</span>
                  {ticket.id === currentTicket.id && (
                    <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Você
                    </span>
                  )}
                </div>
                <span className="text-gray-600">{ticket.service.name}</span>
              </div>
            ))}
            
            {queueInfo.items.filter(t => t.status === 'in_queue').length === 0 && (
              <p className="text-gray-500 text-center">Fila vazia</p>
            )}
          </div>
        )}

        {/* Botão para voltar */}
        <div className="mt-6">
          <Button onClick={handleFinish} variant="secondary" className="w-full">
            Voltar ao Início
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default QueuePage; 