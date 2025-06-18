import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import type { Ticket, Equipment, Operator, TicketStatus, EquipmentStatus, EquipmentType, PanelStats, OperationConfig } from '../types';

// Mock data para configuração de operação
const mockOperationConfig: OperationConfig = {
  equipmentCounts: {
    'banheira_gelo': 3,
    'bota_compressao': 3
  },
  serviceDuration: 10,
  isOperating: false
};

// Mock data para operadores
const mockOperators: Operator[] = [
  { id: '1', name: 'Operador 1' },
  { id: '2', name: 'Operador 2' }
];

// Mock data para equipamentos
const generateMockEquipment = (config: OperationConfig): Equipment[] => {
  const equipment: Equipment[] = [];
  
  // Banheiras de gelo
  for (let i = 0; i < config.equipmentCounts['banheira_gelo']; i++) {
    equipment.push({
      id: `bg-${i + 1}`,
      name: `Banheira ${i + 1}`,
      type: 'banheira_gelo' as EquipmentType,
      status: 'available' as EquipmentStatus,
      serviceId: 'service_banheira'
    });
  }
  
  // Botas de compressão
  for (let i = 0; i < config.equipmentCounts['bota_compressao']; i++) {
    equipment.push({
      id: `bc-${i + 1}`,
      name: `Bota ${i + 1}`,
      type: 'bota_compressao' as EquipmentType,
      status: 'available' as EquipmentStatus,
      serviceId: 'service_bota'
    });
  }
  
  return equipment;
};

// Lista de nomes para gerar clientes aleatórios
const mockCustomerNames = [
  'João Silva', 'Maria Oliveira', 'Carlos Santos', 'Ana Pereira', 'Pedro Costa',
  'Juliana Lima', 'Roberto Almeida', 'Fernanda Souza', 'Ricardo Martins', 'Camila Ferreira',
  'Marcelo Rodrigues', 'Patrícia Gomes', 'André Ribeiro', 'Luciana Carvalho', 'Bruno Barbosa'
];

// Mock data para tickets
const mockTickets: Ticket[] = [
  {
    id: '1',
    number: 'A001',
    status: 'in_queue',
    createdAt: new Date().toISOString(),
    service: { 
      id: '1', 
      name: 'Banheira de Gelo', 
      price: 50.0,
      description: 'Sessão de banheira de gelo',
      duration: 10,
      slug: 'banheira-gelo',
      color: 'blue'
    },
    customer: { name: 'João Silva', phone: '11999998888' }
  },
  {
    id: '2',
    number: 'A002',
    status: 'in_queue',
    createdAt: new Date().toISOString(),
    service: { 
      id: '2', 
      name: 'Bota de Compressão', 
      price: 40.0,
      description: 'Sessão de bota de compressão',
      duration: 10,
      slug: 'bota-compressao',
      color: 'green'
    },
    customer: { name: 'Maria Oliveira', phone: '11988887777' }
  },
  {
    id: '3',
    number: 'A003',
    status: 'in_queue',
    createdAt: new Date().toISOString(),
    service: { 
      id: '1', 
      name: 'Banheira de Gelo', 
      price: 50.0,
      description: 'Sessão de banheira de gelo',
      duration: 10,
      slug: 'banheira-gelo',
      color: 'blue'
    },
    customer: { name: 'Carlos Santos', phone: '11977776666' }
  }
];

// Mock stats
const mockStats = {
  inQueueTickets: 3,
  calledTickets: 0,
  inProgressTickets: 0,
  completedTickets: 0,
  averageWaitTime: 5,
  dailyRevenue: 0
};

interface MockPanelStore {
  tickets: Ticket[];
  operators: Operator[];
  equipment: Equipment[];
  operationConfig: OperationConfig;
  stats: typeof mockStats;
  autoCallEnabled: boolean;
  
  // Ações para tickets
  callTicket: (ticketId: string, operatorId: string, equipmentId: string) => void;
  startService: (ticketId: string, equipmentId: string) => void;
  completeService: (ticketId: string) => void;
  cancelTicket: (ticketId: string) => void;
  
  // Ações para equipamentos
  setEquipmentStatus: (equipmentId: string, status: EquipmentStatus) => void;
  setEquipmentCount: (type: string, count: number) => void;
  
  // Ações para configuração
  setServiceDuration: (duration: number) => void;
  startOperation: () => void;
  endOperation: () => void;
  
  // Ações para simulação
  toggleAutoCall: () => void;
  addRandomTicket: () => void;
  
  // Ações para demo
  resetMockData: () => void;
}

export const useMockPanelStore = create<MockPanelStore>((set, get) => ({
  tickets: [...mockTickets],
  operators: [...mockOperators],
  equipment: generateMockEquipment(mockOperationConfig),
  operationConfig: { ...mockOperationConfig },
  stats: { ...mockStats },
  autoCallEnabled: false,
  
  // Chamar próximo ticket
  callTicket: (ticketId, operatorId, equipmentId) => {
    set(state => {
      const updatedTickets = state.tickets.map(ticket => {
        if (ticket.id === ticketId) {
          return {
            ...ticket,
            status: 'called' as TicketStatus,
            operatorId,
            equipmentId,
            calledAt: new Date().toISOString()
          };
        }
        return ticket;
      });
      
      const updatedEquipment = state.equipment.map(eq => {
        if (eq.id === equipmentId) {
          return { ...eq, status: 'in_use' as EquipmentStatus };
        }
        return eq;
      });
      
      // Atualizar estatísticas
      const updatedStats = {
        ...state.stats,
        inQueueTickets: updatedTickets.filter(t => t.status === 'in_queue').length,
        calledTickets: updatedTickets.filter(t => t.status === 'called').length
      };
      
      return { 
        tickets: updatedTickets, 
        equipment: updatedEquipment,
        stats: updatedStats
      };
    });
  },
  
  // Iniciar atendimento
  startService: (ticketId, equipmentId) => {
    set(state => {
      const now = new Date();
      const endTime = new Date(now.getTime() + state.operationConfig.serviceDuration * 60000);
      
      const updatedTickets = state.tickets.map(ticket => {
        if (ticket.id === ticketId) {
          return {
            ...ticket,
            status: 'in_progress' as TicketStatus,
            startedAt: now.toISOString(),
            endTime: endTime.toISOString()
          };
        }
        return ticket;
      });
      
      // Atualizar estatísticas
      const updatedStats = {
        ...state.stats,
        calledTickets: updatedTickets.filter(t => t.status === 'called').length,
        inProgressTickets: updatedTickets.filter(t => t.status === 'in_progress').length
      };
      
      return { 
        tickets: updatedTickets,
        stats: updatedStats
      };
    });
  },
  
  // Completar atendimento
  completeService: (ticketId) => {
    set(state => {
      const updatedTickets = state.tickets.map(ticket => {
        if (ticket.id === ticketId) {
          // Liberar equipamento associado
          const equipmentId = ticket.equipmentId;
          
          return {
            ...ticket,
            status: 'completed' as TicketStatus,
            completedAt: new Date().toISOString(),
            equipmentId: undefined
          };
        }
        return ticket;
      });
      
      // Encontrar o ticket que foi concluído para liberar o equipamento
      const completedTicket = state.tickets.find(t => t.id === ticketId);
      let updatedEquipment = [...state.equipment];
      
      if (completedTicket?.equipmentId) {
        updatedEquipment = state.equipment.map(eq => {
          if (eq.id === completedTicket.equipmentId) {
            return { ...eq, status: 'available' as EquipmentStatus };
          }
          return eq;
        });
      }
      
      // Atualizar estatísticas
      const updatedStats = {
        ...state.stats,
        inProgressTickets: updatedTickets.filter(t => t.status === 'in_progress').length,
        completedTickets: updatedTickets.filter(t => t.status === 'completed').length,
        dailyRevenue: state.stats.dailyRevenue + (completedTicket?.service?.price || 0)
      };
      
      return { 
        tickets: updatedTickets,
        equipment: updatedEquipment,
        stats: updatedStats
      };
    });
  },
  
  // Cancelar ticket
  cancelTicket: (ticketId) => {
    set(state => {
      const updatedTickets = state.tickets.map(ticket => {
        if (ticket.id === ticketId) {
          // Liberar equipamento associado
          const equipmentId = ticket.equipmentId;
          
          return {
            ...ticket,
            status: 'cancelled' as TicketStatus,
            cancelledAt: new Date().toISOString(),
            equipmentId: undefined
          };
        }
        return ticket;
      });
      
      // Encontrar o ticket que foi cancelado para liberar o equipamento
      const cancelledTicket = state.tickets.find(t => t.id === ticketId);
      let updatedEquipment = [...state.equipment];
      
      if (cancelledTicket?.equipmentId) {
        updatedEquipment = state.equipment.map(eq => {
          if (eq.id === cancelledTicket.equipmentId) {
            return { ...eq, status: 'available' as EquipmentStatus };
          }
          return eq;
        });
      }
      
      // Atualizar estatísticas
      const updatedStats = {
        ...state.stats,
        inQueueTickets: updatedTickets.filter(t => t.status === 'in_queue').length,
        calledTickets: updatedTickets.filter(t => t.status === 'called').length,
        inProgressTickets: updatedTickets.filter(t => t.status === 'in_progress').length
      };
      
      return { 
        tickets: updatedTickets,
        equipment: updatedEquipment,
        stats: updatedStats
      };
    });
  },
  
  // Alterar status do equipamento
  setEquipmentStatus: (equipmentId, status) => {
    set(state => {
      const updatedEquipment = state.equipment.map(eq => {
        if (eq.id === equipmentId) {
          return { ...eq, status };
        }
        return eq;
      });
      
      return { equipment: updatedEquipment };
    });
  },
  
  // Alterar quantidade de equipamentos
  setEquipmentCount: (type, count) => {
    set(state => {
      const updatedConfig = {
        ...state.operationConfig,
        equipmentCounts: {
          ...state.operationConfig.equipmentCounts,
          [type]: count
        }
      };
      
      const updatedEquipment = generateMockEquipment(updatedConfig);
      
      return { 
        operationConfig: updatedConfig,
        equipment: updatedEquipment
      };
    });
  },
  
  // Alterar duração do serviço
  setServiceDuration: (duration) => {
    set(state => ({
      operationConfig: {
        ...state.operationConfig,
        serviceDuration: duration
      }
    }));
  },
  
  // Iniciar operação
  startOperation: () => {
    set(state => ({
      operationConfig: {
        ...state.operationConfig,
        isOperating: true
      }
    }));
  },
  
  // Finalizar operação
  endOperation: () => {
    set(state => ({
      operationConfig: {
        ...state.operationConfig,
        isOperating: false
      }
    }));
  },
  
  // Alternar chamada automática
  toggleAutoCall: () => {
    set(state => {
      const newAutoCallEnabled = !state.autoCallEnabled;
      
      if (newAutoCallEnabled) {
        // Iniciar simulação de chamadas automáticas
        const intervalId = setInterval(() => {
          // Verificar se ainda está habilitado
          const currentState = get();
          if (!currentState.autoCallEnabled) {
            clearInterval(intervalId);
            return;
          }
          
          // Encontrar um ticket na fila
          const ticketsInQueue = currentState.tickets.filter(t => t.status === 'in_queue');
          if (ticketsInQueue.length > 0) {
            // Encontrar um equipamento disponível
            const availableEquipment = currentState.equipment.filter(e => e.status === 'available');
            if (availableEquipment.length > 0) {
              // Chamar o ticket
              const ticketToCall = ticketsInQueue[0];
              const equipment = availableEquipment[0];
              const operator = currentState.operators[Math.floor(Math.random() * currentState.operators.length)];
              
              currentState.callTicket(ticketToCall.id, operator.id, equipment.id);
              
              // Após 3 segundos, iniciar o serviço
              setTimeout(() => {
                const updatedState = get();
                const calledTicket = updatedState.tickets.find(t => t.id === ticketToCall.id);
                if (calledTicket && calledTicket.status === 'called') {
                  updatedState.startService(calledTicket.id, calledTicket.equipmentId!);
                }
              }, 3000);
              
              // Adicionar um novo ticket aleatório após chamar um
              setTimeout(() => {
                get().addRandomTicket();
              }, 5000);
            }
          }
        }, 10000); // Chamar um ticket a cada 10 segundos
      }
      
      return { autoCallEnabled: newAutoCallEnabled };
    });
  },
  
  // Adicionar um ticket aleatório
  addRandomTicket: () => {
    set(state => {
      // Gerar número de ticket
      const lastTicket = state.tickets.reduce((max, ticket) => {
        const ticketNum = parseInt(ticket.number.replace(/\D/g, ''));
        return ticketNum > max ? ticketNum : max;
      }, 0);
      
      const newTicketNumber = `A${String(lastTicket + 1).padStart(3, '0')}`;
      
      // Selecionar serviço aleatório
      const services = [
        { 
          id: '1', 
          name: 'Banheira de Gelo', 
          price: 50.0,
          description: 'Sessão de banheira de gelo',
          duration: 10,
          slug: 'banheira-gelo',
          color: 'blue'
        },
        { 
          id: '2', 
          name: 'Bota de Compressão', 
          price: 40.0,
          description: 'Sessão de bota de compressão',
          duration: 10,
          slug: 'bota-compressao',
          color: 'green'
        }
      ];
      
      const randomService = services[Math.floor(Math.random() * services.length)];
      
      // Selecionar cliente aleatório
      const randomName = mockCustomerNames[Math.floor(Math.random() * mockCustomerNames.length)];
      const randomPhone = `11${Math.floor(Math.random() * 90000000) + 10000000}`;
      
      // Criar novo ticket
      const newTicket: Ticket = {
        id: uuidv4(),
        number: newTicketNumber,
        status: 'in_queue',
        createdAt: new Date().toISOString(),
        service: randomService,
        customer: { name: randomName, phone: randomPhone },
        queuePosition: state.tickets.filter(t => t.status === 'in_queue').length + 1
      };
      
      // Atualizar estatísticas
      const updatedStats = {
        ...state.stats,
        inQueueTickets: state.stats.inQueueTickets + 1
      };
      
      return { 
        tickets: [...state.tickets, newTicket],
        stats: updatedStats
      };
    });
  },
  
  // Resetar dados mockados
  resetMockData: () => {
    set({
      tickets: [...mockTickets],
      operators: [...mockOperators],
      equipment: generateMockEquipment(mockOperationConfig),
      operationConfig: { ...mockOperationConfig },
      stats: { ...mockStats },
      autoCallEnabled: false
    });
  }
})); 