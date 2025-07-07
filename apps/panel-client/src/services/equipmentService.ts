import { api } from '@totem/utils';
import { withTenant } from '../utils/withTenant';

export const equipmentService = {
  list() {
    return api.get('/operation/equipment');
  },
  getOperation() {
    return api.get('/operation', { params: withTenant() });
  },
  stopOperation() {
    return api.post('/operation/stop', {}, { params: withTenant() });
  },
}; 