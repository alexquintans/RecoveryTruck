import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ticketService } from '../services/ticketService';

export function useOperatorActions() {
  const queryClient = useQueryClient();

  const callMutation = useMutation({
    mutationFn: ({ ticketId, equipmentId }: { ticketId: string; equipmentId: string }) => ticketService.call(ticketId, equipmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
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
    onSuccess: (data) => {
      console.log('🔍 DEBUG - confirmPayment onSuccess:', data);
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
      console.log('🔍 DEBUG - Cache invalidado para confirmPayment');
    },
    onError: (error) => {
      console.error('❌ ERRO em confirmPayment:', error);
    },
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
    startService: startMutation.mutateAsync,
    completeService: completeMutation.mutateAsync,
    cancelTicket: cancelMutation.mutateAsync,
    callLoading: callMutation.status === 'pending',
    startLoading: startMutation.status === 'pending',
    completeLoading: completeMutation.status === 'pending',
    cancelLoading: cancelMutation.status === 'pending',
    confirmPayment: confirmPaymentMutation.mutateAsync,
    confirmLoading: confirmPaymentMutation.status === 'pending',
    moveToQueue: moveToQueueMutation.mutateAsync,
    moveToQueueLoading: moveToQueueMutation.status === 'pending',
  };
} 