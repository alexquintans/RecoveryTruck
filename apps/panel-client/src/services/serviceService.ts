import { api } from '@totem/utils';

export const serviceService = {
  list(params?: any) {
    return api.get('/services', { params }); // agora autenticado por padrão
  },
  get(serviceId: string) {
    return api.get(`/services/${serviceId}`);
  },
}; 