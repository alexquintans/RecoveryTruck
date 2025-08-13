import { api } from '@totem/utils';
import { withTenant } from '../utils/withTenant';

export const equipmentService = {
  async list() {
    const response = await api.get('/operation/equipment', { params: withTenant() });
    return response.data;
  },
  async getOperation() {
    const response = await api.get('/operation', { params: withTenant() });
    return response.data;
  },
  async stopOperation() {
    const response = await api.post('/operation/stop', {}, { params: withTenant() });
    return response.data;
  },
  // ✅ NOVO: Buscar status real dos equipamentos
  async getEquipmentStatus() {
    console.log('🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...');
    console.log('🔍 DEBUG - equipmentService.getEquipmentStatus - URL:', '/tickets/equipment/status');
    console.log('🔍 DEBUG - equipmentService.getEquipmentStatus - Params:', withTenant());
    
    try {
      const response = await api.get('/tickets/equipment/status', { params: withTenant() });
      console.log('🔍 DEBUG - equipmentService.getEquipmentStatus - Response:', {
        status: response.status,
        data: response.data,
        equipmentsCount: response.data?.equipments?.length || 0
      });
      return response.data;
    } catch (error) {
      console.error('❌ ERRO - equipmentService.getEquipmentStatus:', error);
      throw error;
    }
  },
  // ✅ NOVO: Forçar limpeza dos equipamentos
  async forceCleanup() {
    console.log('🔍 DEBUG - equipmentService.forceCleanup - Iniciando requisição...');
    console.log('🔍 DEBUG - equipmentService.forceCleanup - URL:', '/tickets/equipment/cleanup');
    console.log('🔍 DEBUG - equipmentService.forceCleanup - Params:', withTenant());
    
    try {
      const response = await api.post('/tickets/equipment/cleanup', {}, { params: withTenant() });
      console.log('🔍 DEBUG - equipmentService.forceCleanup - Response:', {
        status: response.status,
        data: response.data
      });
      return response.data;
    } catch (error) {
      console.error('❌ ERRO - equipmentService.forceCleanup:', error);
      throw error;
    }
  },
}; 