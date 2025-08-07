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
}; 