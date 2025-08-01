import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ticketService } from '../services/ticketService';
import { useAuth } from './useAuth';
// @ts-ignore monorepo path
import { useWebSocket } from '@totem/hooks';
import { getAuthToken } from '@totem/utils';
import { equipmentService } from '../services/equipmentService';

export function useTicketQueue() {
  const { isAuthenticated, user } = useAuth();
  const queryClient = useQueryClient();

  const queueQuery = useQuery({
    queryKey: ['tickets', 'queue'],
    queryFn: () => ticketService.getQueue(),
    enabled: isAuthenticated,
    staleTime: 30_000, // 30 segundos
    cacheTime: 60_000, // 1 minuto
    refetchInterval: 30_000, // Refetch a cada 30 segundos
  });

  // Query específica para tickets ativos do operador
  const myTicketsQuery = useQuery({
    queryKey: ['tickets', 'my-tickets'],
    queryFn: async () => {
      try {
        const result = await ticketService.getMyTickets();
        return result;
      } catch (error) {
        console.error('❌ ERRO em getMyTickets:', error);
        throw error;
      }
    },
    enabled: isAuthenticated && !!user?.id,
    staleTime: 30_000, // 30 segundos
    cacheTime: 60_000, // 1 minuto
    refetchInterval: 30_000, // Refetch a cada 30 segundos
  });

  const operationQuery = useQuery({
    queryKey: ['operation'],
    queryFn: () => equipmentService.getOperation(),
    enabled: isAuthenticated,
    staleTime: 60_000, // 1 minuto
    cacheTime: 120_000, // 2 minutos
    refetchInterval: 60_000, // Refetch a cada 1 minuto
  });

  const equipmentQuery = useQuery({
    queryKey: ['equipment'],
    queryFn: () => equipmentService.list(),
    enabled: isAuthenticated,
    staleTime: 60_000, // 1 minuto
    cacheTime: 120_000, // 2 minutos
    refetchInterval: 60_000, // Refetch a cada 1 minuto
  });

  const completedTicketsQuery = useQuery({
    queryKey: ['tickets', 'completed'],
    queryFn: () => ticketService.getCompletedTickets(),
    enabled: isAuthenticated,
    staleTime: 60_000, // 1 minuto
    cacheTime: 120_000, // 2 minutos
    refetchInterval: 60_000, // Refetch a cada 1 minuto
  });

  const cancelledTicketsQuery = useQuery({
    queryKey: ['tickets', 'cancelled'],
    queryFn: async () => {
      console.log('🔍 Buscando tickets cancelados...');
      const result = await ticketService.getTickets({ status: 'cancelled' });
      console.log('🔍 Resultado tickets cancelados:', result);
      return result;
    },
    enabled: isAuthenticated,
    staleTime: 60_000, // 1 minuto
    cacheTime: 120_000, // 2 minutos
    refetchInterval: 60_000, // Refetch a cada 1 minuto
  });

  // Query para tickets aguardando confirmação de pagamento
  const pendingPaymentQuery = useQuery({
    queryKey: ['tickets', 'pending-payment'],
    queryFn: () => ticketService.getPendingPayment(),
    enabled: !!user,
    staleTime: 30_000, // 30 segundos
    cacheTime: 60_000, // 1 minuto
    refetchInterval: 30_000, // Refetch a cada 30 segundos
  });

  // Construir URL de WebSocket
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const baseWs = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000/ws';
  const tenantId = user?.tenant_id || (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
  const token = getAuthToken();
  
  // Corrigir URL do WebSocket para usar a nova estrutura com path parameters
  const wsUrl = `ws://localhost:8000/ws/${tenantId}/operator${token ? `?token=${token}` : ''}`;



  // Reativando WebSocket
  useWebSocket({
    url: wsUrl,
    onOpen: () => {
      console.log('🔌 WebSocket conectado com sucesso!');
    },
    onError: (error) => {
      console.log('🔌 WebSocket error:', error);
    },
    onClose: () => {
      console.log('🔌 WebSocket fechado');
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onMessage: (msg: any) => {
      console.log('🔍 DEBUG - WebSocket message received:', msg);
      if (!msg || typeof msg !== 'object') return;
      const { type, data } = msg as any;
      
      if (type === 'queue_update') {
        console.log('🔍 DEBUG - Queue update received:', data);
        queryClient.setQueryData(['tickets', 'queue'], data);
      }
      if (type === 'equipment_update') {
        console.log('🔍 DEBUG - Equipment update received:', data);
        queryClient.invalidateQueries({ queryKey: ['equipment'] });
      }
      if (type === 'ticket_update') {
        console.log('🔍 DEBUG - Ticket update received:', data);
        // Atualizar ticket-specifico dentro do cache
        queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
          if (!old || !old.items) return old;
          const items = old.items.map((t: any) => (t.id === data.id ? { ...t, ...data } : t));
          return { ...old, items };
        });
        
        // Também invalidar a query de meus tickets
        queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      }
      if (type === 'ticket_called') {
        console.log('🔍 DEBUG - Ticket called received:', data);
        // Invalidar ambas as queries quando um ticket é chamado
        queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
        queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      }
    },
  });

  const normalizeTicket = (t: any) => {
    const normalized = {
      ...t,
      operatorId: t.assigned_operator_id || t.operator_id || t.operatorId,
      equipmentId: t.equipment_id || t.equipmentId,
      number: t.ticket_number || t.number,
      createdAt: t.created_at || t.createdAt,
      calledAt: t.called_at || t.calledAt,
      status: t.status,
      payment_confirmed: t.payment_confirmed,
      // Suporte para múltiplos serviços e extras
      services: t.services || [],
      extras: t.extras || [],
      service: t.service || (t.services && t.services.length > 0 ? t.services[0] : { name: '--' }),
      customer: t.customer || { name: '--' },
    };
    
    return normalized;
  };

  // Mapear tickets da fila
  const queueTickets = ((queueQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets do operador
  const myTickets = ((myTicketsQuery.data as any[]) ?? []).map(normalizeTicket);
  


  // Mapear tickets concluídos
  const completedTickets = ((completedTicketsQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets cancelados
  const cancelledTickets = ((cancelledTicketsQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets aguardando confirmação de pagamento
  const pendingPaymentTickets = ((pendingPaymentQuery.data as any[]) ?? []).map(normalizeTicket);

  // Mapear equipamentos para status amigável do dashboard
  const equipment = ((equipmentQuery.data as any[]) ?? []).map((e) => ({
    ...e,
    status:
      e.status === 'online'
        ? 'available'
        : e.status === 'maintenance'
        ? 'maintenance'
        : 'in_use',
  }));

  const operationConfig = (operationQuery.data as any) ?? { is_operating: false, service_duration: 10, equipment_counts: {} };
  
  return {
    ...queueQuery,
    tickets: queueTickets,
    myTickets,
    completedTickets,
    cancelledTickets,
    pendingPaymentTickets,
    equipment,
    operationConfig: {
      isOperating: operationConfig.is_operating ?? false,
      serviceDuration: operationConfig.service_duration ?? 10,
      equipmentCounts: operationConfig.equipment_counts ?? {},
    },
    refetchOperation: () => queryClient.invalidateQueries({ queryKey: ['operation'] }),
    refetch: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
    },
  } as typeof queueQuery & {
    tickets: any[];
    myTickets: any[];
    completedTickets: any[];
    cancelledTickets: any[];
    pendingPaymentTickets: any[];
    equipment: any[];
    operationConfig: any;
    refetchOperation: () => void;
    refetch: () => void;
  };
} 