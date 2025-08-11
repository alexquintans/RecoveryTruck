import { api, getAuthToken } from '@totem/utils';
import { withTenant } from '../utils/withTenant';

export interface QueueParams {
  sort_order?: 'fifo' | 'priority' | 'service' | 'waiting_time';
  service_id?: string;
  priority_filter?: 'high' | 'normal' | 'low';
  include_called?: boolean;
  include_in_progress?: boolean;
}

const token = getAuthToken();

export const ticketService = {
  async getQueue(params: QueueParams = {}) {
    const response = await api.get('/tickets/queue', { params: withTenant(params) });
    return response.data;
  },

  async getMyTickets() {
    try {
      const response = await api.get('/tickets/my-tickets', { params: withTenant() });
      return response.data;
    } catch (error) {
      console.error('❌ ERRO em getMyTickets:', error);
      throw error;
    }
  },

  async call(ticketId: string, equipmentId: string) {
    // ✅ ADICIONADO: Log para debug da chamada da API
    console.log('🔍 DEBUG - ticketService.call:', {
      ticketId,
      equipmentId,
      ticketIdType: typeof ticketId,
      equipmentIdType: typeof equipmentId,
      url: `/tickets/${ticketId}/call`,
      body: { equipment_id: equipmentId }
    });
    
    const response = await api.post(`/tickets/${ticketId}/call`, { equipment_id: equipmentId }, { params: withTenant() });
    return response.data;
  },

  async callService(ticketId: string, serviceId: string, equipmentId: string) {
    // ✅ ADICIONADO: Log para debug da chamada da API
    console.log('🔍 DEBUG - ticketService.callService:', {
      ticketId,
      serviceId,
      equipmentId,
      ticketIdType: typeof ticketId,
      url: `/tickets/${ticketId}/call-service`,
      body: { service_id: serviceId, equipment_id: equipmentId }
    });
    
    const response = await api.post(`/tickets/${ticketId}/call-service`, { 
      service_id: serviceId, 
      equipment_id: equipmentId 
    }, { params: withTenant() });
    return response.data;
  },

  async start(ticketId: string) {
    const response = await api.post(`/tickets/${ticketId}/start`, undefined, { params: withTenant() });
    return response.data;
  },

  async complete(ticketId: string, operatorNotes?: string) {
    const response = await api.post(`/tickets/${ticketId}/complete`, {
      operator_notes: operatorNotes,
    }, { params: withTenant() });
    return response.data;
  },

  async cancel(ticketId: string, reason: string) {
    const response = await api.post(
      `/tickets/${ticketId}/cancel`,
      undefined,
      { params: { ...withTenant(), cancellation_reason: reason } }
    );
    return response.data;
  },

  async reprint(ticketId: string) {
    const response = await api.post(`/tickets/${ticketId}/reprint`, undefined, { params: withTenant() });
    return response.data;
  },

  async get(ticketId: string) {
    const response = await api.get(`/tickets/${ticketId}`, { params: withTenant() });
    return response.data;
  },

  async getCompletedTickets() {
    const response = await api.get('/tickets', {
      params: withTenant({ status: 'completed' })
    });
    return response.data;
  },

  async getTickets(params: any) {
    const response = await api.get('/tickets', { params: withTenant(params) });
    return response.data;
  },

  async confirmPayment(ticketId: string) {
    const response = await api.post(`/tickets/${ticketId}/confirm-payment`, undefined, { params: withTenant() });
    return response.data;
  },

  async moveToQueue(ticketId: string) {
    const response = await api.post(`/tickets/${ticketId}/move-to-queue`, undefined, { params: withTenant() });
    return response.data;
  },

  getPendingPayment: async () => {
    const response = await api.get('/tickets/status/pending-payment', { params: withTenant() });
    return response.data;
  },
}; 