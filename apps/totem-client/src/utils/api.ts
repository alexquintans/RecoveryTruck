import { api as baseApi } from '@totem/utils';
import type { Service, Customer, PaymentMethod, Ticket } from '../types';

/**
 * Tipos retornados pela API real
 */
export interface PaymentSession {
  id: string;
  amount: number;
  payment_method: PaymentMethod;
  status: string; // pending, processing, paid, completed, cancelled
  service_id: string;
  qr_code?: string;
  payment_link?: string;
  transaction_id?: string;
  ticket_id?: string;
  preference_id?: string; // Para Mercado Pago
  created_at: string;
  updated_at: string;
}

/**
 * Tipos para a fila
 */
export interface QueueTicket {
  id: string;
  ticket_number: number;
  status: string;
  customer_name: string;
  service: {
    id: string;
    name: string;
    duration_minutes: number;
  };
  queued_at: string;
  called_at?: string;
  started_at?: string;
  completed_at?: string;
  priority: 'high' | 'normal' | 'low';
  queue_position?: number;
  estimated_wait_minutes?: number;
  waiting_time_minutes: number;
}

export interface QueueInfo {
  items: QueueTicket[];
  total: number;
  by_service: Record<string, QueueTicket[]>;
  by_status: Record<string, QueueTicket[]>;
  by_priority: Record<string, QueueTicket[]>;
  queue_stats: {
    total_active: number;
    by_status: Record<string, number>;
    by_priority: Record<string, number>;
    waiting_times: {
      average_minutes: number;
      maximum_minutes: number;
      total_estimated_minutes: number;
    };
    queue_health: {
      status: 'healthy' | 'warning' | 'critical';
      message: string;
      recommendations: string[];
    };
  };
  estimated_total_time: number;
}

// Tipo para os métodos de pagamento aceitos pelo backend
type BackendPaymentMethod = 'credit' | 'debit' | 'pix' | 'tap' | 'cash';

export const api = {
  /** Listar serviços disponíveis */
  async getServices(tenantId: string): Promise<Service[]> {
    const response = await baseApi.get('/services/public', { params: { tenant_id: tenantId } });
    return response.data.services; // <-- A CORREÇÃO: extrair a lista de serviços do objeto de resposta.
  },

  /** Criar sessão de pagamento (para um serviço) */
  async createPaymentSession(
    serviceId: string,
    customer: Customer,
    paymentMethod: PaymentMethod,
    consentVersion: string = 'v1'
  ): Promise<PaymentSession> {
    const isDev = import.meta.env.VITE_MOCK_PAYMENT === 'true' || window.location.hostname === 'localhost';
    let backendPaymentMethod: BackendPaymentMethod = paymentMethod as BackendPaymentMethod;
    if (paymentMethod === 'credit_card') backendPaymentMethod = 'credit';
    if (paymentMethod === 'debit_card') backendPaymentMethod = 'debit';
    const payload: any = {
      service_id: serviceId,
      customer_name: customer.name,
      consent_version: consentVersion,
      payment_method: backendPaymentMethod,
      ...(customer.cpf ? { customer_cpf: customer.cpf } : {}),
      ...(customer.phone ? { customer_phone: customer.phone } : {}),
      ...(isDev ? { mock: true } : {})
    };
    const response = await baseApi.post('/payment_sessions', payload, { withAuth: false });
    return response.data;
  },

  /** Criar ticket diretamente com múltiplos serviços */
  async createTicket(
    services: Array<{ id: string; price: number }>,
    customer: Customer,
    extras?: Array<{ id: string; quantity: number; price: number }>
  ): Promise<Ticket> {
    const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
    const response = await baseApi.post('/tickets', {
      tenant_id: tenantId, // Adicionado
      services: services.map(s => ({
        service_id: s.id,
        price: s.price
      })),
      customer_name: customer.name,
      customer_cpf: customer.cpf,
      customer_phone: customer.phone,
      consent_version: 'v1',
      extras: extras ? extras.map(e => ({ 
        extra_id: e.id, 
        quantity: e.quantity, 
        price: e.price 
      })) : []
    });
    
    // Retornar apenas os dados do ticket, não o objeto Axios completo
    return response.data;
  },

  /** Criar sessão de pagamento para um ticket existente */
  async createPaymentForTicket(ticketId: string, paymentMethod: PaymentMethod): Promise<PaymentSession> {
    const response = await baseApi.post(`/tickets/${ticketId}/create-payment`, {
      payment_method: paymentMethod,
    });
    return response.data;
  },

  /** Buscar status da sessão de pagamento */
  async getPaymentSession(sessionId: string): Promise<PaymentSession> {
    const response = await baseApi.get(`/payment_sessions/${sessionId}`, { withAuth: false });
    return response.data;
  },

  /** Obter ticket (após pagamento) */
  async getTicket(ticketId: string): Promise<Ticket> {
    const response = await baseApi.get(`/tickets/${ticketId}`);
    return response.data;
  },

  /** Buscar configuração vigente da operação (serviços e extras públicos) */
  async getOperationConfig(tenantId: string) {
    const response = await baseApi.get(`/operation/config`, { params: { tenant_id: tenantId } });
    // Garante que a resposta sempre tenha arrays, mesmo que a API não os envie.
    return {
      ...response.data,
      services: response.data.services || [],
      extras: response.data.extras || [],
      payment_modes: response.data.payment_modes || [],
    };
  },

  /** Buscar fila de tickets (para exibição pública) */
  async getQueue(tenantId: string): Promise<QueueInfo> {
    const response = await baseApi.get('/tickets/queue/public', { 
      params: { 
        tenant_id: tenantId,
        include_called: true,
        include_in_progress: true 
      }, 
      withAuth: false 
    });
    return response.data;
  },

  /** Buscar ticket específico na fila */
  async getTicketInQueue(ticketId: string, tenantId: string): Promise<QueueTicket | null> {
    const response = await baseApi.get(`/tickets/${ticketId}`, { 
      params: { tenant_id: tenantId }
    });
    return response.data;
  },

  /** Buscar cliente na base de dados */
  async searchCustomer(searchTerm: string): Promise<Customer | null> {
    const response = await baseApi.get('/customers/search', { 
      params: { 
        q: searchTerm,
        tenant_id: (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d'
      }, 
      withAuth: false 
    });
    return response.data;
  },
}; 