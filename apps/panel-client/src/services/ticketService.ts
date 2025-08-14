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
      console.log('🔍 DEBUG - ticketService.getMyTickets - Iniciando chamada...');
      const response = await api.get('/tickets/my-tickets', { params: withTenant() });
      console.log('🔍 DEBUG - ticketService.getMyTickets - Response:', {
        status: response.status,
        dataLength: response.data?.length || 0,
        data: response.data,
        // ✅ NOVO: Log detalhado da estrutura de cada ticket
        ticketsStructure: response.data?.map((t: any) => ({
          id: t.id,
          ticket_number: t.ticket_number,
          status: t.status,
          hasServices: !!t.services,
          servicesCount: t.services?.length || 0,
          hasCustomer: !!t.customer,
          customerName: t.customer?.name || t.customer_name,
          hasCustomerName: !!t.customer_name,
          allKeys: Object.keys(t),
          // ✅ NOVO: Log completo do primeiro ticket para debug
          fullTicket: response.data?.[0] === t ? t : null
        })) || []
      });
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

  // ✅ NOVO: Verificar conflitos antes de chamar ticket
  async checkConflicts(ticketId: string, serviceId: string) {
    console.log('🔍 DEBUG - ticketService.checkConflicts:', {
      ticketId,
      serviceId,
      url: `/tickets/${ticketId}/check-conflicts`
    });
    
    const response = await api.get(`/tickets/${ticketId}/check-conflicts`, { 
      params: { ...withTenant(), service_id: serviceId }
    });
    return response.data;
  },

  // ✅ NOVO: Chamada inteligente com verificação de conflitos
  async callIntelligent(ticketId: string, serviceId: string, equipmentId: string, checkConflicts: boolean = true) {
    console.log('🔍 DEBUG - ticketService.callIntelligent:', {
      ticketId,
      serviceId,
      equipmentId,
      checkConflicts,
      url: `/tickets/${ticketId}/call-intelligent`,
      body: { 
        service_id: serviceId, 
        equipment_id: equipmentId,
        check_customer_conflicts: checkConflicts
      }
    });
    
    const response = await api.post(`/tickets/${ticketId}/call-intelligent`, { 
      service_id: serviceId, 
      equipment_id: equipmentId,
      check_customer_conflicts: checkConflicts
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