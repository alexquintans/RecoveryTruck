import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ticketService } from '../services/ticketService';
import { useAuth } from './useAuth';
// @ts-ignore monorepo path
import { useWebSocket } from '@totem/hooks';
import { getAuthToken } from '@totem/utils';
import { equipmentService } from '../services/equipmentService';
import { useMemo, useCallback } from 'react';

export function useTicketQueue() {
  const { isAuthenticated, user } = useAuth();
  const queryClient = useQueryClient();

  const queueQuery = useQuery({
    queryKey: ['tickets', 'queue'],
    queryFn: async () => {
      const result = await ticketService.getQueue();
      console.log('🔍 DEBUG - Queue query result:', {
        total: result?.total || 0,
        itemsCount: result?.items?.length || 0,
        byService: result?.by_service || {},
        itemsDetails: result?.items?.map((t: any) => ({
          id: t.id,
          ticket_number: t.ticket_number,
          status: t.status,
          services: t.services?.length || 0,
          service_names: t.services?.map((s: any) => s.service?.name) || [],
          service_details: t.services?.map((s: any) => ({
            id: s.service?.id,
            name: s.service?.name,
            price: s.price
          })) || [],
          // ✅ CORREÇÃO: Log detalhado da estrutura dos serviços
          services_structure: t.services?.map((s: any) => ({
            service_id: s.service_id,
            service_object: s.service,
            price: s.price,
            has_service: !!s.service,
            service_id_type: typeof s.service_id,
            service_object_type: typeof s.service
          })) || []
        }))
      });
      return result;
    },
    enabled: isAuthenticated,
    staleTime: 30_000, // 30 segundos
    cacheTime: 60_000, // 1 minuto
    refetchInterval: 30_000, // Refetch a cada 30 segundos
  });

  // Query específica para tickets ativos do operador
  const myTicketsQuery = useQuery({
    queryKey: ['tickets', 'my-tickets'],
    queryFn: async () => {
      console.log('🔍 DEBUG - myTicketsQuery - Iniciando query...');
      console.log('🔍 DEBUG - myTicketsQuery - enabled:', isAuthenticated && !!user?.id);
      console.log('🔍 DEBUG - myTicketsQuery - user:', user);
      console.log('🔍 DEBUG - myTicketsQuery - isAuthenticated:', isAuthenticated);
      console.log('🔍 DEBUG - myTicketsQuery - user?.id:', user?.id);
      try {
        console.log('🔍 DEBUG - Chamando getMyTickets...');
        const result = await ticketService.getMyTickets();
        console.log('🔍 DEBUG - getMyTickets result:', {
          total: result?.length || 0,
          tickets: result?.map((t: any) => ({
            id: t.id,
            ticket_number: t.ticket_number,
            status: t.status,
            assigned_operator_id: t.assigned_operator_id,
            called_at: t.called_at,
            services_count: t.services?.length || 0
          })) || []
        });
        
        // ✅ CORREÇÃO: Verificar filtro
        console.log('🔍 DEBUG - getMyTickets - ANTES DO FILTRO:', {
          total: result?.length || 0,
          tickets: result?.map((t: any) => ({
            id: t.id,
            ticket_number: t.ticket_number,
            status: t.status,
            assigned_operator_id: t.assigned_operator_id
          })) || []
        });
        
        // ✅ CORREÇÃO: Filtrar apenas tickets em atendimento (called ou in_progress)
        const filtered = result.filter((ticket: any) => 
          ticket.status === 'called' || ticket.status === 'in_progress'
        );
        console.log('🔍 DEBUG - getMyTickets - APÓS FILTRO CORRIGIDO:', {
          total: filtered?.length || 0,
          tickets: filtered?.map((t: any) => ({
            id: t.id,
            ticket_number: t.ticket_number,
            status: t.status,
            assigned_operator_id: t.assigned_operator_id
          })) || []
        });
        
        return filtered; // ✅ CORREÇÃO: Retornar apenas tickets em atendimento
      } catch (error) {
        console.error('❌ ERRO em getMyTickets:', error);
        throw error;
      }
    },
    enabled: isAuthenticated && !!user?.id,
    onSuccess: (data) => {
      console.log('🔍 DEBUG - myTicketsQuery - onSuccess:', {
        dataLength: data?.length || 0,
        data: data
      });
    },
    onError: (error) => {
      console.error('🔍 DEBUG - myTicketsQuery - onError:', error);
    },
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
    queryFn: async () => {
      console.log('🔍 DEBUG - pendingPaymentQuery - Iniciando...');
      const result = await ticketService.getPendingPayment();
      console.log('🔍 DEBUG - pendingPaymentQuery - Resultado:', {
        total: result?.length || 0,
        tickets: result?.map((t: any) => ({
          id: t.id,
          ticket_number: t.ticket_number,
          status: t.status,
          payment_confirmed: t.payment_confirmed
        })) || []
      });
      return result;
    },
    enabled: !!user,
    staleTime: 30_000, // 30 segundos
    cacheTime: 60_000, // 1 minuto
    refetchInterval: 30_000, // Refetch a cada 30 segundos
  });

  // ✅ SOLUÇÃO: Memoizar a URL do WebSocket com proteções
  const wsUrl = useMemo(() => {
    try {
      // ✅ PROTEÇÃO: Verificar se user existe
      if (!user?.tenant_id) {
        console.warn('🔍 DEBUG - user ou tenant_id não disponível ainda');
        return null;
      }
      
      // Construir URL de WebSocket
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
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
      
      const tenantId = user.tenant_id; // ✅ Agora sabemos que existe
      const token = getAuthToken();
      
      // Corrigir URL do WebSocket para usar query parameters
      const finalUrl = `${baseWs}?tenant_id=${tenantId}&client_type=operator${token ? `&token=${token}` : ''}`;
      console.log('🔍 DEBUG - WebSocket URL final construída:', finalUrl);
      return finalUrl;
    } catch (error) {
      console.error('Erro ao construir URL do WebSocket:', error);
      // ✅ PROTEÇÃO: Retornar null em caso de erro
      return null;
    }
  }, [user?.tenant_id]); // ✅ Dependência correta

  // Memoizar as callbacks do WebSocket para evitar recriações
  const wsCallbacks = useMemo(() => ({
    onOpen: () => {
      console.log('🔌 WebSocket conectado com sucesso!');
    },
    onError: (error: any) => {
      console.log('🔌 WebSocket error:', error);
      // Não deixar o erro do WebSocket quebrar a aplicação
    },
    onClose: () => {
      console.log('🔌 WebSocket fechado');
      // Não deixar o fechamento do WebSocket quebrar a aplicação
    },
    onMessage: (msg: any) => {
      try {
        // ✅ PROTEÇÃO: Validações robustas
        if (!msg || typeof msg !== 'object') {
          console.warn('WebSocket: mensagem inválida recebida:', msg);
          return;
        }
        
        const { type, data } = msg as any;
        
        if (!type) {
          console.warn('WebSocket: mensagem sem type:', msg);
          return;
        }
        
        console.log('🔌 WebSocket message received:', { type, data });
        
        // ✅ CORREÇÃO: Log detalhado para debug de pagamento
        if (type === 'payment_update') {
          console.log('🔍 DEBUG - Estrutura da mensagem de pagamento:', {
            type,
            data,
            hasData: !!data,
            hasPaymentConfirmed: data?.payment_confirmed,
            hasTicketId: data?.ticket_id,
            dataKeys: data ? Object.keys(data) : []
          });
        }
        
        // ✅ CORREÇÃO: Log detalhado para debug de tickets com múltiplos serviços
        if (type === 'ticket_update') {
          console.log('🔍 DEBUG - Ticket update com múltiplos serviços:', {
            ticketId: data?.id,
            services: data?.services?.length || 0,
            serviceNames: data?.services?.map((s: any) => s.service?.name) || []
          });
        }
        
        if (type === 'queue_update') {
          console.log('🔄 Atualizando fila via WebSocket');
          try {
            if (data && queryClient) {
              queryClient.setQueryData(['tickets', 'queue'], data);
            }
          } catch (error) {
            console.error('Erro ao atualizar fila via WebSocket:', error);
          }
        }
        if (type === 'equipment_update') {
          console.log('🔄 Atualizando equipamentos via WebSocket');
          try {
            if (queryClient) {
              queryClient.invalidateQueries({ queryKey: ['equipment'] });
            }
          } catch (error) {
            console.error('Erro ao invalidar equipamentos via WebSocket:', error);
          }
        }
      if (type === 'ticket_update') {
        console.log('🔄 Atualizando ticket específico via WebSocket');
        try {
          // Atualizar ticket-specifico dentro do cache
          queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
            if (!old || !old.items) return old;
            const items = old.items.map((t: any) => (t.id === data.id ? { ...t, ...data } : t));
            return { ...old, items };
          });
          
          // Também invalidar a query de meus tickets
          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
        } catch (error) {
          console.error('Erro ao atualizar ticket via WebSocket:', error);
        }
      }
      if (type === 'ticket_called') {
        console.log('🔄 Ticket chamado via WebSocket');
        try {
          // Invalidar ambas as queries quando um ticket é chamado
          queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
        } catch (error) {
          console.error('Erro ao invalidar tickets via WebSocket:', error);
        }
      }
      if (type === 'payment_update') {
        console.log('🔄 Atualização de pagamento via WebSocket:', data);
        try {
          // ✅ CORREÇÃO: Processar dados específicos do pagamento
          if (data && data.payment_confirmed && data.ticket_id) {
            console.log(`🎯 Pagamento confirmado para ticket ${data.ticket_id}, movendo para fila...`);
            
            // Atualizar o ticket específico no cache
            queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
              if (!old || !old.items) return old;
              const items = old.items.map((t: any) => 
                t.id === data.ticket_id 
                  ? { ...t, status: 'in_queue', payment_confirmed: true, queued_at: data.updated_at }
                  : t
              );
              return { ...old, items };
            });
            
            // Atualizar tickets de pagamento pendente
            queryClient.setQueryData<any>(['tickets', 'pending-payment'], (old: any) => {
              if (!old || !Array.isArray(old)) return old;
              return old.filter((t: any) => t.id !== data.ticket_id);
            });
          }
          
          // Invalidar queries relacionadas a pagamento quando um pagamento for confirmado
          queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
          queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
        } catch (error) {
          console.error('Erro ao invalidar pagamentos via WebSocket:', error);
        }
      }
      } catch (error) {
        console.error('Erro crítico no onMessage do WebSocket:', error);
        // ✅ PROTEÇÃO: Não deixar erros quebrar a aplicação
      }
    },
  }), [queryClient]);

  // ✅ SOLUÇÃO: WebSocket com proteções robustas
  const shouldConnectWebSocket = isAuthenticated && wsUrl && typeof wsUrl === 'string' && wsUrl.startsWith('ws');
  
  // ✅ CORREÇÃO: Sempre chamar useWebSocket para evitar React Error #310
  // O hook deve ser sempre executado, mas com URL null quando não deve conectar
  const webSocket = useWebSocket({
    url: shouldConnectWebSocket ? wsUrl : null, // ✅ Passar null se não deve conectar
    enabled: shouldConnectWebSocket, // ✅ Usar propriedade enabled
    reconnectInterval: 5000,
    reconnectAttempts: 5,
    ...wsCallbacks,
  });

  // ✅ CORREÇÃO: Memoizar função para evitar React Error #310
  const normalizeTicket = useCallback((t: any) => {
    // ✅ ADICIONADO: Log para debug da normalização
    console.log('🔍 DEBUG - Normalizando ticket:', {
      originalId: t.id,
      ticketNumber: t.ticket_number || t.number,
      status: t.status,
      hasServices: !!t.services,
      servicesCount: t.services?.length || 0,
      // ✅ NOVO: Log detalhado da estrutura dos serviços
      servicesStructure: t.services?.map((s: any) => ({
        hasService: !!s.service,
        serviceId: s.service?.id,
        serviceName: s.service?.name,
        price: s.price,
        originalStructure: s
      })) || [],
      // ✅ NOVO: Log completo do ticket original
      originalTicket: t
    });
    
    const normalized = {
      ...t,
      // ✅ CORREÇÃO: Garantir que o ID seja preservado
      id: t.id,
      operatorId: t.assigned_operator_id || t.operator_id || t.operatorId,
      equipmentId: t.equipment_id || t.equipmentId,
      number: t.ticket_number || t.number,
      createdAt: t.created_at || t.createdAt,
      calledAt: t.called_at || t.calledAt,
      status: t.status,
      payment_confirmed: t.payment_confirmed,
      // ✅ CORREÇÃO: Mapear corretamente a estrutura de serviços do backend
      services: (t.services || []).map((ts: any) => ({
        id: ts.service?.id || ts.id,
        name: ts.service?.name || ts.name,
        price: ts.price || ts.service?.price,
        duration: ts.service?.duration_minutes || ts.duration,
        // Preservar a estrutura original para compatibilidade
        service: ts.service,
        ticketService: ts
      })),
      extras: (t.extras || []).map((te: any) => ({
        id: te.extra?.id || te.id,
        name: te.extra?.name || te.name,
        quantity: te.quantity,
        price: te.price || te.extra?.price,
        // Preservar a estrutura original para compatibilidade
        extra: te.extra,
        ticketExtra: te
      })),
      service: t.service || (t.services && t.services.length > 0 ? {
        id: t.services[0].service?.id || t.services[0].id,
        name: t.services[0].service?.name || t.services[0].name,
        price: t.services[0].price || t.services[0].service?.price
      } : { name: '--' }),
      customer: t.customer || { name: '--' },
    };
    
    // ✅ ADICIONADO: Verificação de segurança
    if (!normalized.id) {
      console.error('❌ ERRO: Ticket sem ID após normalização:', { original: t, normalized });
    } else {
      console.log('✅ DEBUG - Ticket normalizado com sucesso:', {
        originalId: t.id,
        normalizedId: normalized.id,
        ticketNumber: normalized.number,
        status: normalized.status,
        // ✅ NOVO: Log dos serviços normalizados
        normalizedServices: normalized.services?.map((s: any) => ({
          id: s.id,
          name: s.name,
          price: s.price,
          hasOriginalService: !!s.service
        })) || []
      });
    }
    
    return normalized;
  }, []); // Sem dependências pois é uma função pura

  // ✅ CORREÇÃO: Memoizar arrays de tickets para evitar React Error #310
  const queueTickets = useMemo(() => 
    ((queueQuery.data as any)?.items ?? []).map(normalizeTicket), 
    [queueQuery.data, normalizeTicket]
  );

  const myTickets = useMemo(() => {
    console.log('🔍 DEBUG - myTickets useMemo - DADOS BRUTOS:', {
      myTicketsQueryData: myTicketsQuery.data,
      myTicketsQueryDataLength: myTicketsQuery.data?.length || 0,
      myTicketsQueryDataType: typeof myTicketsQuery.data,
      isArray: Array.isArray(myTicketsQuery.data)
    });
    
    const rawData = (myTicketsQuery.data as any[]) ?? [];
    console.log('🔍 DEBUG - myTickets useMemo - DADOS APÓS FALLBACK:', {
      rawData,
      rawDataLength: rawData.length,
      rawDataType: typeof rawData
    });
    
    const normalized = rawData.map(normalizeTicket);
    console.log('🔍 DEBUG - myTickets useMemo - DADOS NORMALIZADOS:', {
      normalized,
      normalizedLength: normalized.length,
      normalizedIds: normalized.map((t: any) => t.id)
    });
    
    return normalized;
  }, [myTicketsQuery.data, normalizeTicket]);

  const completedTickets = useMemo(() => 
    ((completedTicketsQuery.data as any)?.items ?? []).map(normalizeTicket), 
    [completedTicketsQuery.data, normalizeTicket]
  );

  const cancelledTickets = useMemo(() => 
    ((cancelledTicketsQuery.data as any)?.items ?? []).map(normalizeTicket), 
    [cancelledTicketsQuery.data, normalizeTicket]
  );

  const pendingPaymentTickets = useMemo(() => 
    ((pendingPaymentQuery.data as any[]) ?? []).map(normalizeTicket), 
    [pendingPaymentQuery.data, normalizeTicket]
  );

  // Mapear equipamentos para status amigável do dashboard
  const operationConfig = (operationQuery.data as any) ?? { 
    is_operating: false, 
    service_duration: 10, 
    equipment_counts: {} 
  };
  
  const { myTickets: _, ...queueQueryWithoutMyTickets } = queueQuery;
  
  // ✅ CORREÇÃO: Memoizar objetos para evitar React Error #310
  const normalizedOperationConfig = useMemo(() => ({
    isOperating: operationConfig.is_operating ?? false,
    serviceDuration: operationConfig.service_duration ?? 10,
    equipmentCounts: operationConfig.equipment_counts ?? {},
  }), [operationConfig.is_operating, operationConfig.service_duration, operationConfig.equipment_counts]);
  
  const equipment = useMemo(() => 
    ((equipmentQuery.data as any[]) ?? []).map((e) => ({
      ...e,
      status:
        e.status === 'online'
          ? 'available'
          : e.status === 'maintenance'
          ? 'maintenance'
          : 'in_use',
    })).filter((e) => {
      // Filtrar apenas equipamentos da operação ativa
      return e.operation_id === operationConfig.operation_id || !e.operation_id;
    }), [equipmentQuery.data, operationConfig.operation_id]);

  // ✅ CORREÇÃO: Memoizar funções de refetch para evitar React Error #310
  const refetchOperation = useCallback(() => 
    queryClient.invalidateQueries({ queryKey: ['operation'] }), 
    [queryClient]
  );

  const refetch = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
    queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
    queryClient.invalidateQueries({ queryKey: ['equipment'] });
  }, [queryClient]);

  return {
    ...queueQueryWithoutMyTickets,
    tickets: queueTickets,
    myTickets,
    completedTickets,
    cancelledTickets,
    pendingPaymentTickets,
    equipment,
    operationConfig: normalizedOperationConfig,
    refetchOperation,
    refetch,
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