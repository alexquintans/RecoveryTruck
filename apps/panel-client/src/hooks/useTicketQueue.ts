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
    refetchInterval: 10000, // Refetch a cada 10 segundos
  });

  // Query específica para tickets ativos do operador
  const myTicketsQuery = useQuery({
    queryKey: ['tickets', 'my-tickets'],
    queryFn: () => ticketService.getMyTickets(),
    enabled: isAuthenticated && !!user?.id,
    refetchInterval: 5000, // Refetch a cada 5 segundos
  });

  const operationQuery = useQuery({
    queryKey: ['operation'],
    queryFn: () => equipmentService.getOperation(),
    enabled: isAuthenticated,
    staleTime: 60_000,
  });

  const equipmentQuery = useQuery({
    queryKey: ['equipment'],
    queryFn: () => equipmentService.list(),
    enabled: isAuthenticated,
    staleTime: 30_000,
  });

  const completedTicketsQuery = useQuery({
    queryKey: ['tickets', 'completed'],
    queryFn: () => ticketService.getCompletedTickets(),
    enabled: isAuthenticated,
    refetchInterval: 10000,
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
    refetchInterval: 10000,
    staleTime: 0, // Sempre considerar stale para forçar refetch
    cacheTime: 5 * 60 * 1000, // 5 minutos
  });

  // Construir URL de WebSocket
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const baseWs = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000/ws';
  const tenantId = user?.tenant_id || (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';
  const token = getAuthToken();
  const wsUrl = `${baseWs}?tenant_id=${tenantId}&client_type=operator${token ? `&token=${token}` : ''}`;

  useWebSocket({
    url: wsUrl,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onMessage: (msg: any) => {
      if (!msg || typeof msg !== 'object') return;
      const { type, data } = msg as any;
      
      if (type === 'queue_update') {
        queryClient.setQueryData(['tickets', 'queue'], data);
      }
      if (type === 'ticket_update') {
        // Atualizar ticket específico dentro do cache
        queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
          if (!old || !old.items) return old;
          const items = old.items.map((t: any) => (t.id === data.id ? { ...t, ...data } : t));
          return { ...old, items };
        });
        
        // Também invalidar a query de meus tickets
        queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      }
      if (type === 'ticket_called') {
        // Invalidar ambas as queries quando um ticket é chamado
        queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
        queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      }
    },
  });

  const normalizeTicket = (t: any) => ({
    ...t,
    operatorId: t.assigned_operator_id || t.operator_id || t.operatorId,
    equipmentId: t.equipment_id || t.equipmentId,
    number: t.ticket_number || t.number,
    createdAt: t.created_at || t.createdAt,
    calledAt: t.called_at || t.calledAt,
    status: t.status,
    // Suporte para múltiplos serviços
    services: t.services || [],
    service: t.service || (t.services && t.services.length > 0 ? t.services[0] : { name: '--' }),
    customer: t.customer || { name: '--' },
  });

  // Mapear tickets da fila
  const queueTickets = ((queueQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets do operador
  const myTickets = ((myTicketsQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets concluídos
  const completedTickets = ((completedTicketsQuery.data as any)?.items ?? []).map(normalizeTicket);

  // Mapear tickets cancelados
  const cancelledTickets = ((cancelledTicketsQuery.data as any)?.items ?? []).map(normalizeTicket);

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
    equipment,
    operationConfig: {
      isOperating: operationConfig.is_operating ?? false,
      serviceDuration: operationConfig.service_duration ?? 10,
      equipmentCounts: operationConfig.equipment_counts ?? {},
    },
    refetchOperation: () => queryClient.invalidateQueries({ queryKey: ['operation'] }),
  } as typeof queueQuery & {
    tickets: any[];
    myTickets: any[];
    completedTickets: any[];
    cancelledTickets: any[];
    equipment: any[];
    operationConfig: any;
    refetchOperation: () => void;
  };
} 