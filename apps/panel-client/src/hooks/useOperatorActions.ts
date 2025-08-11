import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ticketService } from '../services/ticketService';

export function useOperatorActions() {
  const queryClient = useQueryClient();

  const callMutation = useMutation({
    mutationFn: ({ ticketId, equipmentId }: { ticketId: string; equipmentId: string }) => {
      // ✅ ADICIONADO: Log para debug da mutation
      console.log('🔍 DEBUG - callMutation.mutationFn:', {
        ticketId,
        equipmentId,
        ticketIdType: typeof ticketId,
        equipmentIdType: typeof equipmentId
      });
      
      return ticketService.call(ticketId, equipmentId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  const callServiceMutation = useMutation({
    mutationFn: ({ ticketId, serviceId, equipmentId }: { ticketId: string; serviceId: string; equipmentId: string }) => {
      // ✅ ADICIONADO: Log para debug da mutation
      console.log('🔍 DEBUG - callServiceMutation.mutationFn:', {
        ticketId,
        serviceId,
        equipmentId,
        ticketIdType: typeof ticketId,
        ticketIdValue: ticketId
      });
      
      return ticketService.callService(ticketId, serviceId, equipmentId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      queryClient.invalidateQueries({ queryKey: ['service-progress'] });
    },
  });

  const startMutation = useMutation({
    mutationFn: ({ ticketId }: { ticketId: string }) => ticketService.start(ticketId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: ({ ticketId, notes }: { ticketId: string; notes?: string }) =>
      ticketService.complete(ticketId, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: ({ ticketId, reason }: { ticketId: string; reason: string }) =>
      ticketService.cancel(ticketId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  const confirmPaymentMutation = useMutation({
    mutationFn: ({ ticketId }: { ticketId: string }) => ticketService.confirmPayment(ticketId),
    onSuccess: async (data, variables) => {
      console.log('✅ Pagamento confirmado, invalidando queries...');
      
      try {
        // ✅ CORREÇÃO CRÍTICA: Invalidar todas as queries relacionadas a tickets
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] }),
          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] }),
          queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] }),
          queryClient.invalidateQueries({ queryKey: ['tickets', 'completed'] }),
          queryClient.invalidateQueries({ queryKey: ['tickets', 'cancelled'] })
        ]);
        
        // ✅ CORREÇÃO CRÍTICA: Invalidar queries específicas por ticket
        await queryClient.invalidateQueries({ 
          queryKey: ['tickets'], 
          predicate: (query) => query.queryKey.includes(variables.ticketId)
        });
        
        // ✅ CORREÇÃO CRÍTICA: Forçar refetch das queries principais
        await Promise.all([
          queryClient.refetchQueries({ queryKey: ['tickets', 'queue'] }),
          queryClient.refetchQueries({ queryKey: ['tickets', 'pending-payment'] }),
          queryClient.refetchQueries({ queryKey: ['tickets', 'my-tickets'] })
        ]);
        
        console.log('✅ Queries invalidadas e refetchadas com sucesso');
      } catch (error) {
        console.error('❌ Erro ao invalidar queries:', error);
      }
    },
    onError: (error) => {
      console.error('❌ Erro ao confirmar pagamento:', error);
    }
  });

  const moveToQueueMutation = useMutation({
    mutationFn: ({ ticketId }: { ticketId: string }) => ticketService.moveToQueue(ticketId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  return {
    callTicket: callMutation.mutateAsync,
    callService: callServiceMutation.mutateAsync,
    startService: startMutation.mutateAsync,
    completeService: completeMutation.mutateAsync,
    cancelTicket: cancelMutation.mutateAsync,
    callLoading: callMutation.status === 'pending',
    callServiceLoading: callServiceMutation.status === 'pending',
    startLoading: startMutation.status === 'pending',
    completeLoading: completeMutation.status === 'pending',
    cancelLoading: cancelMutation.status === 'pending',
    confirmPayment: confirmPaymentMutation.mutateAsync,
    confirmLoading: confirmPaymentMutation.status === 'pending',
    moveToQueue: moveToQueueMutation.mutateAsync,
    moveToQueueLoading: moveToQueueMutation.status === 'pending',
  };
} 