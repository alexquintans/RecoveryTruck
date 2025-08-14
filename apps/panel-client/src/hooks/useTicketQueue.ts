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
        
        // ✅ CORREÇÃO CRÍTICA: Backend já filtra tickets em atendimento
        // Não aplicar filtro adicional no frontend para evitar duplicação
        console.log('🔍 DEBUG - getMyTickets - RESULTADO DO BACKEND (sem filtro adicional):', {
          total: result?.length || 0,
          tickets: result?.map((t: any) => ({
            id: t.id,
            ticket_number: t.ticket_number,
            status: t.status,
            assigned_operator_id: t.assigned_operator_id
          })) || [],
          statuses: result?.map((t: any) => t.status) || []
        });
        
        return result; // ✅ CORREÇÃO: Retornar resultado direto do backend
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

  // ✅ CORREÇÃO CRÍTICA: Callbacks do WebSocket com tratamento robusto de erros
  const wsCallbacks = useMemo(() => ({
    onOpen: () => {
      console.log('🔌 WebSocket conectado com sucesso!');
    },
    onError: (error: any) => {
      console.error('🔌 WebSocket error:', error);
      // ✅ CORREÇÃO CRÍTICA: Não deixar erro quebrar a aplicação
      // Log do erro mas continuar funcionamento
    },
    onClose: () => {
      console.log('🔌 WebSocket fechado');
      // ✅ CORREÇÃO CRÍTICA: Implementar reconexão automática
      // O hook useWebSocket já gerencia reconexão automaticamente
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
          // ✅ NOVO: Invalidar progresso por serviço quando um ticket é atualizado
          queryClient.invalidateQueries({ queryKey: ['service-progress'] });
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
          // ✅ NOVO: Recarregar o progresso por serviço para refletir chamada por serviço
          queryClient.invalidateQueries({ queryKey: ['service-progress'] });
        } catch (error) {
          console.error('Erro ao invalidar tickets via WebSocket:', error);
        }
      }
      // ✅ NOVO: Quando serviço for iniciado, recarregar progresso imediatamente
      if (type === 'service_started') {
        console.log('🔄 Serviço iniciado via WebSocket');
        try {
          queryClient.invalidateQueries({ queryKey: ['service-progress'] });
          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
        } catch (error) {
          console.error('Erro ao invalidar queries de progresso de serviço:', error);
        }
      }
      if (type === 'payment_update') {
        console.log('🔄 Atualização de pagamento via WebSocket:', data);
        try {
          // ✅ CORREÇÃO CRÍTICA: Processar dados específicos do pagamento
          if (data && data.payment_confirmed && data.ticket_id) {
            console.log(`🎯 Pagamento confirmado para ticket ${data.ticket_id}, movendo para fila...`);
            
            // ✅ CORREÇÃO CRÍTICA: Atualizar o ticket específico no cache
            queryClient.setQueryData<any>(['tickets', 'queue'], (old: any) => {
              if (!old || !old.items) return old;
              const items = old.items.map((t: any) => 
                t.id === data.ticket_id 
                  ? { ...t, status: 'in_queue', payment_confirmed: true, queued_at: data.updated_at }
                  : t
              );
              return { ...old, items };
            });
            
            // ✅ CORREÇÃO CRÍTICA: Atualizar tickets de pagamento pendente
            queryClient.setQueryData<any>(['tickets', 'pending-payment'], (old: any) => {
              if (!old || !Array.isArray(old)) return old;
              return old.filter((t: any) => t.id !== data.ticket_id);
            });
            
            // ✅ CORREÇÃO CRÍTICA: Invalidar todas as queries relacionadas
            Promise.all([
              queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] }),
              queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] }),
              queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] })
            ]).catch(error => {
              console.error('Erro ao invalidar queries de pagamento:', error);
            });
          }
        } catch (error) {
          console.error('Erro ao processar atualização de pagamento via WebSocket:', error);
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

  // ✅ CORREÇÃO CRÍTICA: Normalização padronizada e consistente
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
    
    // ✅ CORREÇÃO CRÍTICA: Verificação de segurança antes da normalização
    if (!t || !t.id) {
      console.error('❌ ERRO: Ticket inválido para normalização:', t);
      return null;
    }
    
    const normalized = {
      ...t,
      // ✅ CORREÇÃO CRÍTICA: Garantir que o ID seja preservado
      id: t.id,
      operatorId: t.assigned_operator_id || t.operator_id || t.operatorId,
      equipmentId: t.equipment_id || t.equipmentId,
      number: t.ticket_number || t.number,
      createdAt: t.created_at || t.createdAt,
      calledAt: t.called_at || t.calledAt,
      status: t.status,
      payment_confirmed: t.payment_confirmed,
      // ✅ CORREÇÃO CRÍTICA: Padronizar estrutura de serviços com proteção
      services: (t.services || []).map((ts: any) => {
        // ✅ PADRONIZAÇÃO: Sempre usar a estrutura service.id
        const serviceId = ts.service?.id || ts.id;
        const serviceName = ts.service?.name || ts.name;
        const servicePrice = ts.price || ts.service?.price;
        const serviceDuration = ts.service?.duration_minutes || ts.duration;
        
        return {
          id: serviceId, // ✅ SEMPRE usar service.id como padrão
          name: serviceName,
          price: servicePrice,
          duration: serviceDuration,
          // Preservar estrutura original para compatibilidade
          service: ts.service,
          ticketService: ts,
          // ✅ NOVO: Adicionar campos padronizados
          service_id: serviceId, // Para compatibilidade com backend
          service_name: serviceName
        };
      }),
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
      customer_name: t.customer_name || t.customer?.name || '--',
    };
    
    // ✅ ADICIONADO: Verificação de segurança
    if (!normalized.id) {
      console.error('❌ ERRO: Ticket sem ID após normalização:', { original: t, normalized });
      return null; // ✅ CORREÇÃO: Retornar null em vez de objeto inválido
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
    ((queueQuery.data as any)?.items ?? []).map(normalizeTicket).filter(Boolean), 
    [queueQuery.data, normalizeTicket]
  );

  const myTickets = useMemo(() => {
    // ✅ DEBUG CRÍTICO: Verificar se os dados estão chegando
    console.log('🔍 DEBUG CRÍTICO - myTickets useMemo - VERIFICAÇÃO INICIAL:', {
      myTicketsQueryData: myTicketsQuery.data,
      myTicketsQueryDataLength: myTicketsQuery.data?.length || 0,
      myTicketsQueryDataType: typeof myTicketsQuery.data,
      isArray: Array.isArray(myTicketsQuery.data),
      // ✅ NOVO: Log detalhado da estrutura dos dados
      firstItem: myTicketsQuery.data?.[0],
      firstItemKeys: myTicketsQuery.data?.[0] ? Object.keys(myTicketsQuery.data[0]) : [],
      // ✅ NOVO: Log detalhado de cada ticket
      allTickets: myTicketsQuery.data?.map((t: any) => ({
        id: t.id,
        ticket_number: t.ticket_number,
        status: t.status,
        hasServices: !!t.services,
        servicesCount: t.services?.length || 0,
        hasCustomer: !!t.customer,
        customerName: t.customer?.name || t.customer_name,
        hasCustomerName: !!t.customer_name,
        allKeys: Object.keys(t)
      })) || []
    });
    
    const rawData = (myTicketsQuery.data as any[]) ?? [];
    console.log('🔍 DEBUG - myTickets useMemo - DADOS APÓS FALLBACK:', {
      rawData,
      rawDataLength: rawData.length,
      rawDataType: typeof rawData,
      // ✅ NOVO: Verificar se há dados válidos
      hasValidData: rawData.length > 0,
      firstRawItem: rawData[0],
      firstRawItemStructure: rawData[0] ? {
        id: rawData[0].id,
        ticket_number: rawData[0].ticket_number,
        status: rawData[0].status,
        hasServices: !!rawData[0].services,
        servicesCount: rawData[0].services?.length || 0
      } : null
    });
    
    // ✅ CORREÇÃO CRÍTICA: Verificar se há dados antes de processar
    if (!rawData || rawData.length === 0) {
      console.warn('🔍 DEBUG - myTickets: Nenhum dado para processar');
      return [];
    }
    
    try {
      // ✅ CORREÇÃO CRÍTICA: Usar dados diretamente sem normalização complexa
      const validTickets = rawData.filter(t => t && t.id);
      console.log('🔍 DEBUG - myTickets - Tickets válidos encontrados:', validTickets.length);
      
      // ✅ CORREÇÃO CRÍTICA: Aplicar apenas normalização mínima necessária
      const processedTickets = validTickets.map((t: any) => ({
        ...t,
        // ✅ CORREÇÃO: Garantir campos essenciais
        id: t.id,
        number: t.ticket_number || t.number,
        status: t.status,
        customer_name: t.customer_name || t.customer?.name,
        services: t.services || [],
        extras: t.extras || [],
        // ✅ CORREÇÃO: Manter estrutura original para compatibilidade
        ticket_number: t.ticket_number,
        assigned_operator_id: t.assigned_operator_id,
        called_at: t.called_at,
        created_at: t.created_at,
        payment_confirmed: t.payment_confirmed,
        // Novo: normalizar progresso por serviço vindo do backend
        serviceProgress: Array.isArray(t.services_progress)
          ? t.services_progress.map((p: any) => ({
              service_id: p.service_id,
              status: p.status,
              started_at: p.started_at,
              duration_minutes: p.duration_minutes,
              equipment_id: p.equipment_id,
            }))
          : (t.serviceProgress || [])
      }));
      
      console.log('🔍 DEBUG - myTickets useMemo - DADOS PROCESSADOS:', {
        processedTickets,
        processedLength: processedTickets.length,
        processedIds: processedTickets.map((t: any) => t.id),
        // ✅ NOVO: Verificar se processamento foi bem-sucedido
        hasProcessedData: processedTickets.length > 0,
        firstProcessedItem: processedTickets[0],
        firstProcessedItemStructure: processedTickets[0] ? {
          id: processedTickets[0].id,
          number: processedTickets[0].number,
          status: processedTickets[0].status,
          hasServices: !!processedTickets[0].services,
          servicesCount: processedTickets[0].services?.length || 0
        } : null
      });
      
      // ✅ DEBUG CRÍTICO: Verificar o que está sendo retornado
      console.log('🔍 DEBUG CRÍTICO - myTickets FINAL:', {
        returnValue: processedTickets,
        returnValueLength: processedTickets.length,
        returnValueType: typeof processedTickets,
        isArray: Array.isArray(processedTickets),
        willBeReturned: processedTickets.length > 0 ? 'SIM - Dados serão retornados' : 'NÃO - Array vazio'
      });
      
      return processedTickets;
    } catch (error) {
      console.error('❌ ERRO no processamento de myTickets:', error);
      console.error('❌ Dados que causaram erro:', rawData);
      return [];
    }
  }, [myTicketsQuery.data]); // ✅ CORREÇÃO: Remover normalizeTicket das dependências

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