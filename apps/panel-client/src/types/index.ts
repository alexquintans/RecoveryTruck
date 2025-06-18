/**
 * Tipos para o sistema de filas
 */

// Status possíveis para um ticket
export type TicketStatus = 'in_queue' | 'called' | 'in_progress' | 'completed' | 'cancelled';

// Status possíveis para um equipamento
export type EquipmentStatus = 'available' | 'in_use' | 'maintenance';

// Tipos de equipamentos
export type EquipmentType = 'banheira_gelo' | 'bota_compressao';

// Informações do cliente
export interface Customer {
  name: string;
  phone?: string;
  email?: string;
  document?: string;
  termsAccepted?: boolean;
  termsAcceptedAt?: string;
}

// Serviço oferecido
export interface Service {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number;
  equipmentType?: EquipmentType;
  slug: string;
  color?: string;
}

// Ticket/senha para atendimento
export interface Ticket {
  id: string;
  number: string;
  status: TicketStatus;
  createdAt: string;
  calledAt?: string;
  startedAt?: string;
  endTime?: string;
  completedAt?: string;
  cancelledAt?: string;
  service?: Service;
  customer?: Customer;
  operatorId?: string;
  equipmentId?: string;
  queuePosition?: number;
}

// Equipamento para uso
export interface Equipment {
  id: string;
  name: string;
  type: EquipmentType;
  status: EquipmentStatus;
  serviceId: string;
}

// Operador
export interface Operator {
  id: string;
  name: string;
}

// Configuração de operação
export interface OperationConfig {
  equipmentCounts: Record<string, number>;
  serviceDuration: number;
  isOperating: boolean;
}

// Estatísticas do painel
export interface PanelStats {
  inQueueTickets: number;
  calledTickets: number;
  inProgressTickets: number;
  completedTickets: number;
  cancelledTickets?: number;
  totalTickets?: number;
  averageWaitTime: number;
  averageServiceTime?: number;
  dailyRevenue: number;
  averageRevenue?: number;
  completionRate?: number;
  utilizationByEquipmentType?: {
    [key: string]: number; // tipo de equipamento -> porcentagem de utilização
  };
} 