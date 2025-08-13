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
    onSuccess: (data) => {
      console.log('🔍 DEBUG - useEquipmentStatus - Query success:', {
        equipmentsCount: data?.equipments?.length || 0,
        equipments: data?.equipments?.map((e: any) => ({
          id: e.id,
          identifier: e.identifier,
          status: e.status,
          in_use: e.in_use
        })) || []
      });
    },
    onError: (error) => {
      console.error('❌ ERRO - useEquipmentStatus - Query error:', error);
    }
  });

  // ✅ Forçar limpeza dos equipamentos
  const forceCleanupMutation = useMutation({
    mutationFn: equipmentService.forceCleanup,
    onSuccess: (data) => {
      console.log('🔍 DEBUG - useEquipmentStatus - Force cleanup success:', data);
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['equipment', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
      queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
    },
    onError: (error) => {
      console.error('❌ ERRO - useEquipmentStatus - Force cleanup error:', error);
    }
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
