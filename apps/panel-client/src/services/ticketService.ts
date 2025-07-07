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
  getQueue(params: QueueParams = {}) {
    return api.get('/tickets/queue', { params: withTenant(params) });
  },

  getMyTickets() {
    return api.get('/tickets', { 
      params: withTenant({ 
        category: 'active'
      }) 
    });
  },

  call(ticketId: string, equipmentId: string) {
    return api.post(`/tickets/${ticketId}/call`, { equipment_id: equipmentId }, { params: withTenant() });
  },

  start(ticketId: string) {
    return api.post(`/tickets/${ticketId}/start`, undefined, { params: withTenant() });
  },

  complete(ticketId: string, operatorNotes?: string) {
    return api.post(`/tickets/${ticketId}/complete`, {
      operator_notes: operatorNotes,
    }, { params: withTenant() });
  },

  cancel(ticketId: string, reason: string) {
    return api.post(
      `/tickets/${ticketId}/cancel`,
      undefined,
      { params: { ...withTenant(), cancellation_reason: reason } }
    );
  },

  reprint(ticketId: string) {
    return api.post(`/tickets/${ticketId}/reprint`, undefined, { params: withTenant() });
  },

  get(ticketId: string) {
    return api.get(`/tickets/${ticketId}`, { params: withTenant() });
  },

  getCompletedTickets() {
    return api.get('/tickets', {
      params: withTenant({ status: 'completed' })
    });
  },

  async getTickets(params: any) {
    return api.get('/tickets', { params: withTenant(params) });
  },
}; 