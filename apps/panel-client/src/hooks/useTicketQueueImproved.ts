import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from './useAuth';
import { useProtectedWebSocket } from '@totem/hooks';
import { useMemo, useCallback, useState, useEffect } from 'react';

export function useTicketQueueImproved() {
  const { user, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [loadingState, setLoadingState] = useState<'initial' | 'loading' | 'ready' | 'error'>('initial');

  // Obter tenant ID do usuário
  const tenantId = user?.tenant_id;

  // Construir URL do WebSocket com proteções
  const wsUrl = useMemo(() => {
    try {
      if (!user?.tenant_id) {
        console.warn('WebSocket: tenant_id não disponível');
        return null;
      }
      
      let baseWs = (import.meta as any).env?.VITE_WS_URL || 'wss://recoverytruck-production.up.railway.app/ws';
      
      if (baseWs.startsWith('ws://') && window.location.protocol === 'https:') {
        baseWs = baseWs.replace('ws://', 'wss://');
      }
      
      const token = localStorage.getItem('auth_token');
      const url = `${baseWs}?tenant_id=${tenantId}&client_type=operator${token ? `&token=${token}` : ''}`;
      
      console.log('WebSocket URL construída:', url);
      return url;
    } catch (error) {
      console.error('Erro ao construir URL do WebSocket:', error);
      return null;
    }
  }, [user?.tenant_id]);

  // Callbacks protegidos para WebSocket
  const wsCallbacks = useMemo(() => ({
    onOpen: () => {
      console.log('🔌 WebSocket conectado com sucesso!');
    },
    onError: (error: any) => {
      console.log('❌ WebSocket error:', error);
      // Não deixar o erro do WebSocket quebrar a aplicação
    },
    onClose: () => {
      console.log('🔌 WebSocket fechado');
      // Não deixar o fechamento do WebSocket quebrar a aplicação
    },
    onMessage: (msg: any) => {
      try {
        if (!msg || typeof msg !== 'object') {
          console.warn('WebSocket: mensagem inválida recebida:', msg);
          return;
        }
        
        const { type, data } = msg as any;
        
        if (!type || !data) {
          console.warn('WebSocket: mensagem sem type ou data:', msg);
          return;
        }
        
        console.log('🔌 WebSocket message received:', { type, data });
        
        // Validar dados antes de usar
        if (type === 'queue_update') {
          if (!Array.isArray(data) && !data.items) {
            console.warn('WebSocket: dados de fila inválidos:', data);
            return;
          }
          
          try {
            queryClient.setQueryData(['tickets', 'queue'], data);
          } catch (error) {
            console.error('Erro ao atualizar fila via WebSocket:', error);
          }
        }
        
        if (type === 'equipment_update') {
          try {
            queryClient.invalidateQueries({ queryKey: ['equipment'] });
          } catch (error) {
            console.error('Erro ao invalidar equipamentos via WebSocket:', error);
          }
        }
        
        if (type === 'ticket_update') {
          if (!data.id) {
            console.warn('WebSocket: ticket_update sem ID:', data);
            return;
          }
          
          try {
            queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
              if (!old || !old.items) return old;
              const items = old.items.map((t: any) => (t.id === data.id ? { ...t, ...data } : t));
              return { ...old, items };
            });
            queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
          } catch (error) {
            console.error('Erro ao atualizar ticket via WebSocket:', error);
          }
        }
        
        if (type === 'payment_update') {
          try {
            queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
            queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
            queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
          } catch (error) {
            console.error('Erro ao invalidar pagamentos via WebSocket:', error);
          }
        }
      } catch (error) {
        console.error('Erro geral no WebSocket callback:', error);
      }
    },
  }), [queryClient]);

  // WebSocket condicional baseado no estado
  const shouldConnectWebSocket = isAuthenticated && 
                                wsUrl && 
                                wsUrl.startsWith('ws');

  // WebSocket com proteções robustas
  const webSocket = useProtectedWebSocket({
    url: wsUrl,
    enabled: shouldConnectWebSocket,
    ...wsCallbacks,
  });

  // Queries com proteções
  const { data: tickets, isLoading: ticketsLoading, refetch: refetchTickets } = useQuery({
    queryKey: ['tickets', 'queue'],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/tickets/queue?tenant_id=${tenantId}`);
        if (!response.ok) throw new Error('Falha ao carregar tickets');
        return response.json();
      } catch (error) {
        console.error('Erro ao carregar tickets:', error);
        throw error;
      }
    },
    enabled: !!tenantId,
    retry: 3,
    retryDelay: 1000,
  });

  const { data: myTickets, isLoading: myTicketsLoading, refetch: refetchMyTickets } = useQuery({
    queryKey: ['tickets', 'my-tickets'],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/tickets/my-tickets?tenant_id=${tenantId}`);
        if (!response.ok) throw new Error('Falha ao carregar meus tickets');
        return response.json();
      } catch (error) {
        console.error('Erro ao carregar meus tickets:', error);
        throw error;
      }
    },
    enabled: !!tenantId,
    retry: 3,
    retryDelay: 1000,
  });

  const { data: equipment, isLoading: equipmentLoading, refetch: refetchEquipment } = useQuery({
    queryKey: ['equipment'],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/equipment?tenant_id=${tenantId}`);
        if (!response.ok) throw new Error('Falha ao carregar equipamentos');
        return response.json();
      } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
        throw error;
      }
    },
    enabled: !!tenantId,
    retry: 3,
    retryDelay: 1000,
  });

  const { data: operationConfig, isLoading: operationLoading, refetch: refetchOperation } = useQuery({
    queryKey: ['operation-config'],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/operation-config?tenant_id=${tenantId}`);
        if (!response.ok) throw new Error('Falha ao carregar configuração de operação');
        return response.json();
      } catch (error) {
        console.error('Erro ao carregar configuração de operação:', error);
        throw error;
      }
    },
    enabled: !!tenantId,
    retry: 3,
    retryDelay: 1000,
  });

  // useEffect com debounce e proteções
  const debouncedRefetch = useCallback(
    () => {
      try {
        refetchTickets();
        refetchMyTickets();
        refetchEquipment();
        refetchOperation();
      } catch (error) {
        console.error('Erro ao refetch dados:', error);
      }
    },
    [refetchTickets, refetchMyTickets, refetchEquipment, refetchOperation]
  );

  useEffect(() => {
    try {
      if (operationConfig?.isOperating && tenantId) {
        console.log('🔄 Operação ativa detectada, carregando dados...');
        debouncedRefetch();
      }
    } catch (error) {
      console.error('Erro no useEffect de carregar dados:', error);
    }
  }, [operationConfig?.isOperating, tenantId, debouncedRefetch]);

  // Loading state com estados intermediários
  useEffect(() => {
    const checkDataReady = () => {
      const isReady = user && 
                     tenantId && 
                     operationConfig && 
                     Array.isArray(tickets?.items) && 
                     Array.isArray(equipment?.items) &&
                     myTickets &&
                     !ticketsLoading &&
                     !equipmentLoading &&
                     !operationLoading;
      
      if (isReady) {
        setLoadingState('ready');
      } else if (loadingState === 'initial') {
        setLoadingState('loading');
      }
    };
    
    checkDataReady();
  }, [user, tenantId, operationConfig, tickets, equipment, myTickets, ticketsLoading, equipmentLoading, operationLoading, loadingState]);

  return {
    // Estados de loading
    loadingState,
    isLoading: loadingState !== 'ready',
    
    // Dados
    tickets: tickets?.items || [],
    myTickets: myTickets?.items || [],
    equipment: equipment?.items || [],
    operationConfig: operationConfig || { isOperating: false },
    
    // WebSocket
    webSocket,
    
    // Funções
    refetch: debouncedRefetch,
  };
}
