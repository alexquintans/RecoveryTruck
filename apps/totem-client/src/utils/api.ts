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

export const api = {
  /** Listar serviços disponíveis */
  getServices(): Promise<Service[]> {
    return baseApi.get('/services', { withAuth: false });
  },

  /** Criar sessão de pagamento (para um serviço) */
  createPaymentSession(
    serviceId: string,
    customer: Customer,
    paymentMethod: PaymentMethod,
    consentVersion: string = 'v1'
  ): Promise<PaymentSession> {
    const isDev = import.meta.env.VITE_MOCK_PAYMENT === 'true' || window.location.hostname === 'localhost';
    let backendPaymentMethod = paymentMethod;
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
    return baseApi.post('/payment_sessions', payload, { withAuth: false });
  },

  /** Criar ticket diretamente com múltiplos serviços */
  createTicket(
    services: Array<{ id: string; price: number }>,
    customer: Customer,
    extras?: Array<{ id: string; quantity: number; price: number }>
  ): Promise<Ticket> {
    return baseApi.post('/tickets', {
      services: services.map(s => ({
        service_id: s.id,
        price: s.price
      })),
      customer_name: customer.name,
      customer_cpf: customer.cpf,
      customer_phone: customer.phone,
      consent_version: 'v1',
      extras: extras || []
    });
  },

  /** Buscar status da sessão de pagamento */
  getPaymentSession(sessionId: string): Promise<PaymentSession> {
    return baseApi.get(`/payment_sessions/${sessionId}`, { withAuth: false });
  },

  /** Obter ticket (após pagamento) */
  getTicket(ticketId: string): Promise<Ticket> {
    return baseApi.get(`/tickets/${ticketId}`);
  },

  /** Buscar configuração vigente da operação */
  getOperationConfig(tenantId: string) {
    return baseApi.get(`/operation/config`, { params: { tenant_id: tenantId } });
  },

  /** Buscar fila de tickets (para exibição pública) */
  getQueue(tenantId: string): Promise<QueueInfo> {
    return baseApi.get('/tickets/queue/public', { 
      params: { 
        tenant_id: tenantId,
        include_called: true,
        include_in_progress: true 
      }, 
      withAuth: false 
    });
  },

  /** Buscar ticket específico na fila */
  getTicketInQueue(ticketId: string, tenantId: string): Promise<QueueTicket | null> {
    return baseApi.get(`/tickets/${ticketId}`, { 
      params: { tenant_id: tenantId }
    });
  },

  /** Buscar cliente na base de dados */
  searchCustomer(searchTerm: string): Promise<Customer | null> {
    return baseApi.get('/customers/search', { 
      params: { 
        q: searchTerm,
        tenant_id: (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e'
      }, 
      withAuth: false 
    });
  },
}; 