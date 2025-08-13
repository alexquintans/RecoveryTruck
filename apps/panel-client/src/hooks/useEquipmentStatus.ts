import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { equipmentService } from '../services/equipmentService';

export const useEquipmentStatus = () => {
  const queryClient = useQueryClient();

  // ✅ Buscar status real dos equipamentos
  const equipmentStatusQuery = useQuery({
    queryKey: ['equipment', 'status'],
    queryFn: equipmentService.getEquipmentStatus,
    refetchInterval: 5000, // Atualizar a cada 5 segundos
    staleTime: 2000, // Considerar dados frescos por 2 segundos
  });

  // ✅ Forçar limpeza dos equipamentos
  const forceCleanupMutation = useMutation({
    mutationFn: equipmentService.forceCleanup,
    onSuccess: () => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['equipment', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
  });

  return {
    equipmentStatus: equipmentStatusQuery.data?.equipments || [],
    isLoading: equipmentStatusQuery.isLoading,
    isError: equipmentStatusQuery.isError,
    error: equipmentStatusQuery.error,
    refetch: equipmentStatusQuery.refetch,
    forceCleanup: forceCleanupMutation.mutate,
    isCleaningUp: forceCleanupMutation.isPending,
  };
};
