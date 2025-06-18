// Dados mock para o painel de chamadas
import type { Ticket, Operator, PanelStats } from '../types';

// Lista de tickets simulados
export const mockTickets: Ticket[] = [
  {
    id: '1',
    number: 'A001',
    serviceId: '1',
    service: {
      id: '1',
      name: 'Banheira de Gelo',
      description: 'Imersão em água gelada para recuperação muscular',
      price: 50.0,
      duration: 10,
      slug: 'banheira-gelo',
      color: '#1A3A4A'
    },
    status: 'in_queue',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    queuedAt: new Date().toISOString(),
    priority: 'normal',
    queuePosition: 1,
    estimatedWaitTime: 5
  },
  {
    id: '2',
    number: 'A002',
    serviceId: '2',
    service: {
      id: '2',
      name: 'Bota de Compressão',
      description: 'Compressão pneumática para recuperação muscular',
      price: 40.0,
      duration: 15,
      slug: 'bota-compressao',
      color: '#8AE65C'
    },
    status: 'in_queue',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    queuedAt: new Date(Date.now() - 5 * 60000).toISOString(),
    priority: 'normal',
    queuePosition: 2,
    estimatedWaitTime: 10
  },
  {
    id: '3',
    number: 'A003',
    serviceId: '1',
    service: {
      id: '1',
      name: 'Banheira de Gelo',
      description: 'Imersão em água gelada para recuperação muscular',
      price: 50.0,
      duration: 10,
      slug: 'banheira-gelo',
      color: '#1A3A4A'
    },
    status: 'called',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    queuedAt: new Date(Date.now() - 15 * 60000).toISOString(),
    calledAt: new Date().toISOString(),
    priority: 'normal',
    operatorId: '1'
  }
];

// Estatísticas simuladas
export const mockStats: PanelStats = {
  totalTickets: 10,
  inQueueTickets: 2,
  calledTickets: 1,
  inProgressTickets: 1,
  completedTickets: 6,
  cancelledTickets: 0,
  averageWaitTime: 8,
  dailyRevenue: 450.0
};

// Operadores simulados
export const mockOperators: Operator[] = [
  {
    id: '1',
    name: 'João Silva',
    username: 'joao.silva',
    active: true,
    role: 'operator'
  },
  {
    id: '2',
    name: 'Maria Santos',
    username: 'maria.santos',
    active: true,
    role: 'admin'
  }
]; 