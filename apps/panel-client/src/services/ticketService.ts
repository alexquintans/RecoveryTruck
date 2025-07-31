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
    const response = await api.post(`/tickets/${ticketId}/call`, { equipment_id: equipmentId }, { params: withTenant() });
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
    const response = await api.get('/tickets/status/pending-payment');
    return response.data;
  },
}; 