import React, { useCallback, useEffect, useRef } from 'react';
import { useWebSocket } from '@totem/hooks';
import { useSoundNotifications } from '@totem/hooks';

interface DisplayUpdate {
  type: 'ticket_called' | 'ticket_update' | 'queue_update' | 'equipment_update';
  data: {
    id?: string;
    ticket_number?: number;
    status?: string;
    customer_name?: string;
    service_name?: string;
    equipment_name?: string;
    called_at?: string;
    operator_name?: string;
  };
}

interface UseDisplayWebSocketOptions {
  tenantId: string;
  enabled?: boolean;
  onTicketCalled?: (ticketData: any) => void;
  onQueueUpdate?: (update: DisplayUpdate) => void;
}

export function useDisplayWebSocket({
  tenantId,
  enabled = true,
  onTicketCalled,
  onQueueUpdate,
}: UseDisplayWebSocketOptions) {
  const soundNotifications = useSoundNotifications({
    sounds: {
      ticket_called: { src: '/sounds/call.mp3' },
    },
    enabled: true,
    defaultVolume: 0.7,
  });

  const lastCalledRef = useRef<string | null>(null);

  // Construir URL do WebSocket
  let baseWs = (import.meta as any).env?.VITE_WS_URL || 'wss://recoverytruck-production.up.railway.app/ws';
  
  // Debug: mostrar a URL base
  console.log('🔍 DEBUG - VITE_WS_URL:', (import.meta as any).env?.VITE_WS_URL);
  console.log('🔍 DEBUG - baseWs inicial:', baseWs);
  
  // Garantir que termina com /ws
  if (!baseWs.endsWith('/ws')) {
    if (baseWs.endsWith('/')) {
      baseWs = baseWs + 'ws';
    } else {
      baseWs = baseWs + '/ws';
    }
  }
  
  console.log('🔍 DEBUG - baseWs após correção:', baseWs);
  
  // Forçar uso de wss:// em produção (corrigir se a variável estiver com ws://)
  if (baseWs.startsWith('ws://') && window.location.protocol === 'https:') {
    baseWs = baseWs.replace('ws://', 'wss://');
    console.log('🔍 DEBUG - baseWs após forçar wss:', baseWs);
  }
  
  const wsUrl = `${baseWs}?tenant_id=${tenantId}&client_type=display`;
  console.log('🔍 DEBUG - Display WebSocket URL final:', wsUrl);

  // Handler para mensagens do WebSocket
  const handleMessage = useCallback((data: DisplayUpdate) => {
    console.log('📺 Display WebSocket message received:', data);
    
    // Processar diferentes tipos de mensagem
    switch (data.type) {
      case 'ticket_called':
        handleTicketCalled(data);
        break;
      
      case 'ticket_update':
        handleTicketUpdate(data);
        break;
      
      case 'queue_update':
        handleQueueUpdate(data);
        break;
      
      case 'equipment_update':
        handleEquipmentUpdate(data);
        break;
      
      default:
        console.log('Unknown display WebSocket message type:', data.type);
    }

    // Callback customizado
    if (onQueueUpdate) {
      onQueueUpdate(data);
    }
  }, [onQueueUpdate]);

  // Handler para ticket chamado
  const handleTicketCalled = useCallback((data: DisplayUpdate) => {
    const ticketId = data.data.id;
    
    // Evitar tocar som para o mesmo ticket múltiplas vezes
    if (ticketId && ticketId !== lastCalledRef.current) {
      lastCalledRef.current = ticketId;
      
      console.log(`🎉 Ticket #${data.data.ticket_number} foi chamado no display!`);
      
      // Tocar som de chamada
      soundNotifications.play('ticket_called');
      
      // Callback customizado
      if (onTicketCalled) {
        onTicketCalled(data.data);
      }
    }
  }, [soundNotifications, onTicketCalled]);

  // Handler para atualização de ticket
  const handleTicketUpdate = useCallback((data: DisplayUpdate) => {
    console.log('🔄 Ticket update received:', data);
  }, []);

  // Handler para atualização da fila
  const handleQueueUpdate = useCallback((data: DisplayUpdate) => {
    console.log('📋 Queue update received:', data);
  }, []);

  // Handler para atualização de equipamento
  const handleEquipmentUpdate = useCallback((data: DisplayUpdate) => {
    console.log('🔧 Equipment update received:', data);
  }, []);

  // Configurar WebSocket
  const { isConnected, lastMessage, sendMessage, connect, disconnect } = useWebSocket({
    url: wsUrl,
    reconnectInterval: 5000,
    reconnectAttempts: 10,
    onMessage: handleMessage,
    onOpen: () => {
      console.log('📺 Display WebSocket connected');
    },
    onClose: () => {
      console.log('📺 Display WebSocket disconnected');
    },
    onError: (error) => {
      console.error('❌ Display WebSocket error:', error);
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
    if (isConnected) {
      sendMessage({ type: 'request_queue_update' });
    }
  }, [isConnected, sendMessage]);

  return {
    // Status da conexão
    isConnected,
    isConnecting: !isConnected,
    isError: false, // O hook base não expõe status de erro diretamente
    
    // Dados
    lastMessage,
    
    // Funções
    requestQueueUpdate,
    disconnect,
    reconnect: connect,
  };
} 