import { useCallback, useEffect, useRef } from 'react';
import { useWebSocket } from './useWebSocket';
import { useSoundNotifications } from './useSoundNotifications';
import { useTotemStore } from '../store/totemStore';

interface QueueUpdate {
  type: 'ticket_update' | 'ticket_status_changed' | 'queue_update';
  data: {
    id?: string;
    ticket_number?: number;
    status?: string;
    customer_name?: string;
    service_id?: string;
    updated_at?: string;
    old_status?: string;
    new_status?: string;
    operator?: string;
  };
}

interface UseQueueWebSocketOptions {
  tenantId: string;
  enabled?: boolean;
  onQueueUpdate?: (update: QueueUpdate) => void;
  onTicketCalled?: (ticketId: string, ticketNumber: number) => void;
}

export function useQueueWebSocket({
  tenantId,
  enabled = true,
  onQueueUpdate,
  onTicketCalled,
}: UseQueueWebSocketOptions) {
  const { currentTicket } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  const lastUpdateRef = useRef<QueueUpdate | null>(null);

  // Construir URL do WebSocket
  const baseWs = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000/ws';
  const wsUrl = `${baseWs}/${tenantId}/totem`;

  // Handler para mensagens do WebSocket
  const handleMessage = useCallback((data: QueueUpdate) => {
    console.log('📡 WebSocket message received:', data);
    
    // Evitar processar a mesma mensagem múltiplas vezes
    if (lastUpdateRef.current?.data?.updated_at === data.data?.updated_at) {
      return;
    }
    lastUpdateRef.current = data;

    // Processar diferentes tipos de mensagem
    switch (data.type) {
      case 'ticket_update':
        handleTicketUpdate(data);
        break;
      
      case 'ticket_status_changed':
        handleStatusChange(data);
        break;
      
      case 'queue_update':
        handleQueueUpdate(data);
        break;
      
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }

    // Callback customizado
    if (onQueueUpdate) {
      onQueueUpdate(data);
    }
  }, [currentTicket, onQueueUpdate, onTicketCalled]);

  // Handler para atualizações de ticket
  const handleTicketUpdate = useCallback((data: QueueUpdate) => {
    const { id, status, ticket_number } = data.data;
    
    // Se é o ticket atual do usuário
    if (currentTicket && id === currentTicket.id) {
      console.log(`🎫 Seu ticket #${ticket_number} foi atualizado: ${status}`);
      
      // Tocar som se foi chamado
      if (status === 'called') {
        soundNotifications.play('ticket_called');
        
        // Callback para ticket chamado
        if (onTicketCalled && id && ticket_number) {
          onTicketCalled(id, ticket_number);
        }
      }
    }
  }, [currentTicket, soundNotifications, onTicketCalled]);

  // Handler para mudanças de status
  const handleStatusChange = useCallback((data: QueueUpdate) => {
    const { id, old_status, new_status, ticket_number, operator } = data.data;
    
    console.log(`🔄 Status change: Ticket #${ticket_number} ${old_status} → ${new_status} by ${operator}`);
    
    // Se é o ticket atual do usuário
    if (currentTicket && id === currentTicket.id) {
      // Tocar som para mudanças importantes
      if (new_status === 'called') {
        soundNotifications.play('ticket_called');
        
        // Callback para ticket chamado
        if (onTicketCalled && id && ticket_number) {
          onTicketCalled(id, ticket_number);
        }
      } else if (new_status === 'in_progress') {
        soundNotifications.play('beep');
      }
    }
  }, [currentTicket, soundNotifications, onTicketCalled]);

  // Handler para atualizações da fila
  const handleQueueUpdate = useCallback((data: QueueUpdate) => {
    console.log('📊 Queue update received:', data);
    // Aqui você pode implementar lógica específica para atualizações da fila
  }, []);

  // Configurar WebSocket
  const { status, data, sendMessage, disconnect, reconnect } = useWebSocket({
    url: wsUrl,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    onMessage: handleMessage,
    onOpen: () => {
      console.log('🔗 WebSocket connected for queue updates');
    },
    onClose: () => {
      console.log('🔌 WebSocket disconnected');
    },
    onError: (error) => {
      console.error('❌ WebSocket error:', error);
    },
  });

  // Conectar/desconectar baseado na prop enabled
  useEffect(() => {
    if (enabled) {
      // WebSocket será conectado automaticamente pelo hook useWebSocket
    } else {
      disconnect();
    }
  }, [enabled, disconnect]);

  // Função para solicitar atualização da fila
  const requestQueueUpdate = useCallback(() => {
    if (status === 'open') {
      sendMessage({ type: 'request_queue_update' });
    }
  }, [status, sendMessage]);

  return {
    // Status da conexão
    isConnected: status === 'open',
    isConnecting: status === 'connecting',
    isError: status === 'error',
    
    // Dados
    lastMessage: data,
    
    // Funções
    requestQueueUpdate,
    disconnect,
    reconnect,
    
    // Status detalhado
    status,
  };
} 