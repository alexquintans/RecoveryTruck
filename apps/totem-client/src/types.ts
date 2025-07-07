/**
 * Tipos para os serviços oferecidos
 */
export interface Service {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number; // em minutos
  slug: string;
  color?: string;
}

/**
 * Tipos para os clientes
 */
export interface Customer {
  name: string;
  cpf?: string;
  phone?: string;
  email?: string;
  consentTerms: boolean;
  signature?: string; // Assinatura em formato base64
  termsAccepted?: boolean; // Indicador de aceitação dos termos
  termsAcceptedAt?: string; // Data de aceitação dos termos
}

/**
 * Tipos para os tickets
 */
export type TicketStatus = 
  | 'paid'
  | 'printing'
  | 'in_queue'
  | 'called'
  | 'in_progress'
  | 'completed'
  | 'print_error'
  | 'cancelled'
  | 'expired';

export interface Ticket {
  id: string;
  number: string;
  ticket_number?: number;
  ticketNumber?: number; // compatibilidade camelCase
  serviceId: string;
  service?: Service;
  customerId?: string;
  customer?: Customer;
  status: TicketStatus;
  createdAt: string;
  updatedAt: string;
  printedAt?: string;
  queuedAt?: string;
  calledAt?: string;
  startedAt?: string;
  completedAt?: string;
  cancelledAt?: string;
  expiredAt?: string;
  operatorNotes?: string;
  priority?: 'high' | 'normal' | 'low';
  queuePosition?: number;
  estimatedWaitTime?: number; // em minutos
}

/**
 * Tipos para os pagamentos
 */
export type PaymentMethod = 
  | 'credit_card'
  | 'debit_card'
  | 'pix'
  | 'cash';

export type PaymentStatus = 
  | 'pending'
  | 'processing'
  | 'completed'
  | 'cancelled'
  | 'failed';

export interface Payment {
  id: string;
  amount: number;
  method: PaymentMethod;
  status: PaymentStatus;
  serviceId: string;
  service?: Service;
  customerId?: string;
  customer?: Customer;
  ticketId?: string;
  ticket?: Ticket;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  cancelledAt?: string;
  failedAt?: string;
  transactionId?: string;
  qrCodeUrl?: string;
  qrCodeText?: string;
} 