import { create } from 'zustand';
import { io, Socket } from 'socket.io-client';
import type { Ticket, Operator, PanelStats, Equipment, OperationConfig } from '../types';

// URL do servidor de sockets
// @ts-ignore - Ignorando o erro de tipagem do Vite env
const SOCKET_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000';

interface PanelState {
  // Dados
  tickets: Ticket[];
  operators: Operator[];
  stats: PanelStats | null;
  equipment: Equipment[];
  operationConfig: OperationConfig;
  
  // Estado da conexão
  socket: Socket | null;
  isConnected: boolean;
  lastError: string | null;
  
  // Ações
  connectToSocket: () => void;
  disconnectSocket: () => void;
  callTicket: (ticketId: string, operatorId: string, equipmentId: string) => void;
  startService: (ticketId: string, equipmentId: string) => void;
  completeService: (ticketId: string) => void;
  cancelTicket: (ticketId: string) => void;
  
  // Ações de equipamento
  setEquipmentCount: (type: string, count: number) => void;
  startOperation: () => void;
  endOperation: () => void;
  setEquipmentStatus: (equipmentId: string, status: 'available' | 'in_use' | 'maintenance') => void;
  setServiceDuration: (duration: number) => void;
}

// Estado inicial para estatísticas
const initialStats: PanelStats = {
  totalTickets: 0,
  inQueueTickets: 0,
  calledTickets: 0,
  inProgressTickets: 0,
  completedTickets: 0,
  cancelledTickets: 0,
  averageWaitTime: 0,
  dailyRevenue: 0,
  equipmentUtilization: {},
};

// Estado inicial para configuração de operação
const initialOperationConfig: OperationConfig = {
  equipmentCounts: {
    'banheira_gelo': 3,
    'bota_compressao': 3
  },
  serviceDuration: 10, // 10 minutos por padrão
  isOperating: false,
};

// Criar a store
export const usePanelStore = create<PanelState>((set, get) => ({
  // Estado inicial
  tickets: [],
  operators: [],
  stats: initialStats,
  equipment: [],
  operationConfig: initialOperationConfig,
  socket: null,
  isConnected: false,
  lastError: null,
  
  // Conectar ao socket
  connectToSocket: () => {
    const { socket } = get();
    
    // Se já existe uma conexão, não fazer nada
    if (socket && socket.connected) return;
    
    try {
      // Criar nova conexão
      const newSocket = io(SOCKET_URL, {
        reconnectionAttempts: 5,
        timeout: 10000,
      });
      
      // Configurar eventos do socket
      newSocket.on('connect', () => {
        console.log('Conectado ao servidor de sockets');
        set({ isConnected: true, lastError: null });
      });
      
      newSocket.on('disconnect', () => {
        console.log('Desconectado do servidor de sockets');
        set({ isConnected: false });
      });
      
      newSocket.on('connect_error', (error) => {
        console.error('Erro de conexão:', error);
        set({ lastError: 'Falha ao conectar ao servidor' });
      });
      
      // Eventos de dados
      newSocket.on('tickets:update', (tickets: Ticket[]) => {
        console.log('Tickets atualizados:', tickets);
        set({ tickets });
      });
      
      newSocket.on('operators:update', (operators: Operator[]) => {
        console.log('Operadores atualizados:', operators);
        set({ operators });
      });
      
      newSocket.on('stats:update', (stats: PanelStats) => {
        console.log('Estatísticas atualizadas:', stats);
        set({ stats });
      });
      
      newSocket.on('equipment:update', (equipment: Equipment[]) => {
        console.log('Equipamentos atualizados:', equipment);
        set({ equipment });
      });
      
      // Salvar o socket no estado
      set({ socket: newSocket });
    } catch (error) {
      console.error('Erro ao conectar ao socket:', error);
      set({ lastError: 'Erro ao inicializar conexão' });
    }
  },
  
  // Desconectar do socket
  disconnectSocket: () => {
    const { socket } = get();
    
    if (socket) {
      socket.disconnect();
      set({ socket: null, isConnected: false });
    }
  },
  
  // Chamar um ticket
  callTicket: (ticketId: string, operatorId: string, equipmentId: string) => {
    const { socket } = get();
    
    if (socket && socket.connected) {
      socket.emit('ticket:call', { ticketId, operatorId, equipmentId });
    } else {
      set({ lastError: 'Não conectado ao servidor' });
    }
  },
  
  // Iniciar atendimento
  startService: (ticketId: string, equipmentId: string) => {
    const { socket } = get();
    
    if (socket && socket.connected) {
      socket.emit('ticket:start', { ticketId, equipmentId });
      
      // Atualizar status do equipamento localmente também
      const { equipment } = get();
      const updatedEquipment = equipment.map(eq => 
        eq.id === equipmentId ? { ...eq, status: 'in_use' as const } : eq
      );
      set({ equipment: updatedEquipment });
    } else {
      set({ lastError: 'Não conectado ao servidor' });
    }
  },
  
  // Completar atendimento
  completeService: (ticketId: string) => {
    const { socket, tickets, equipment } = get();
    
    // Encontrar o ticket para obter o equipamento associado
    const ticket = tickets.find(t => t.id === ticketId);
    
    if (socket && socket.connected) {
      socket.emit('ticket:complete', { ticketId });
      
      // Se o ticket tem equipamento associado, atualizar seu status
      if (ticket?.equipmentId) {
        const updatedEquipment = equipment.map(eq => 
          eq.id === ticket.equipmentId ? { ...eq, status: 'available' as const } : eq
        );
        set({ equipment: updatedEquipment });
      }
    } else {
      set({ lastError: 'Não conectado ao servidor' });
    }
  },
  
  // Cancelar ticket
  cancelTicket: (ticketId: string) => {
    const { socket, tickets, equipment } = get();
    
    // Encontrar o ticket para obter o equipamento associado
    const ticket = tickets.find(t => t.id === ticketId);
    
    if (socket && socket.connected) {
      socket.emit('ticket:cancel', { ticketId });
      
      // Se o ticket tem equipamento associado, atualizar seu status
      if (ticket?.equipmentId) {
        const updatedEquipment = equipment.map(eq => 
          eq.id === ticket.equipmentId ? { ...eq, status: 'available' as const } : eq
        );
        set({ equipment: updatedEquipment });
      }
    } else {
      set({ lastError: 'Não conectado ao servidor' });
    }
  },
  
  // Configurar quantidade de equipamentos
  setEquipmentCount: (type: string, count: number) => {
    const { operationConfig } = get();
    
    set({
      operationConfig: {
        ...operationConfig,
        equipmentCounts: {
          ...operationConfig.equipmentCounts,
          [type]: count
        }
      }
    });
  },
  
  // Iniciar operação
  startOperation: () => {
    const { socket, operationConfig } = get();
    
    // Gerar equipamentos com base na configuração
    const equipment: Equipment[] = [];
    
    Object.entries(operationConfig.equipmentCounts).forEach(([type, count]) => {
      for (let i = 1; i <= count; i++) {
        equipment.push({
          id: `${type}_${i}`,
          name: `${type === 'banheira_gelo' ? 'Banheira de Gelo' : 'Bota de Compressão'} ${i}`,
          type,
          status: 'available' as const,
          serviceId: type === 'banheira_gelo' ? 'service_banheira' : 'service_bota'
        });
      }
    });
    
    // Atualizar estado
    set({ 
      equipment,
      operationConfig: {
        ...operationConfig,
        isOperating: true
      }
    });
    
    // Notificar servidor
    if (socket && socket.connected) {
      socket.emit('operation:start', { equipment, config: operationConfig });
    }
  },
  
  // Encerrar operação
  endOperation: () => {
    const { socket, operationConfig } = get();
    
    set({
      equipment: [],
      operationConfig: {
        ...operationConfig,
        isOperating: false
      }
    });
    
    // Notificar servidor
    if (socket && socket.connected) {
      socket.emit('operation:end');
    }
  },
  
  // Atualizar status de um equipamento
  setEquipmentStatus: (equipmentId: string, status: 'available' | 'in_use' | 'maintenance') => {
    const { equipment, socket } = get();
    
    const updatedEquipment = equipment.map(eq => 
      eq.id === equipmentId ? { ...eq, status } : eq
    );
    
    set({ equipment: updatedEquipment });
    
    // Notificar servidor
    if (socket && socket.connected) {
      socket.emit('equipment:update', { equipmentId, status });
    }
  },
  
  // Atualizar duração do serviço
  setServiceDuration: (duration: number) => {
    const { operationConfig, socket } = get();
    
    const updatedConfig = {
      ...operationConfig,
      serviceDuration: duration
    };
    
    set({ operationConfig: updatedConfig });
    
    // Notificar servidor
    if (socket && socket.connected) {
      socket.emit('config:update', { serviceDuration: duration });
    }
  },
})); 