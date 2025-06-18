// Mock Socket.IO Server para testar o painel de chamadas
// Este script simula o comportamento da API enviando dados para o painel

// Importações
const http = require('http');
const { Server } = require('socket.io');

// Criar servidor HTTP
const server = http.createServer();
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Lista de tickets simulados
const mockTickets = [
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
      color: '#0891b2'
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
      color: '#7e22ce'
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
      color: '#0891b2'
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
const mockStats = {
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
const mockOperators = [
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

// Evento de conexão
io.on('connection', (socket) => {
  console.log('Cliente conectado:', socket.id);
  
  // Enviar dados iniciais
  sendInitialData(socket);
  
  // Evento de mensagem para chamar ticket
  socket.on('ticket:call', (data) => {
    console.log('Chamando ticket:', data);
    handleTicketCall(data.ticketId, data.operatorId);
  });
  
  // Evento para iniciar atendimento
  socket.on('ticket:start', (data) => {
    console.log('Iniciando atendimento:', data);
    handleTicketStart(data.ticketId);
  });
  
  // Evento para completar atendimento
  socket.on('ticket:complete', (data) => {
    console.log('Completando atendimento:', data);
    handleTicketComplete(data.ticketId);
  });
  
  // Evento para cancelar ticket
  socket.on('ticket:cancel', (data) => {
    console.log('Cancelando ticket:', data);
    handleTicketCancel(data.ticketId);
  });
  
  // Evento de desconexão
  socket.on('disconnect', () => {
    console.log('Cliente desconectado:', socket.id);
  });
});

// Enviar dados iniciais para o cliente
function sendInitialData(socket) {
  // Enviar tickets
  socket.emit('tickets:update', mockTickets);
  
  // Enviar estatísticas
  socket.emit('stats:update', mockStats);
  
  // Enviar operadores
  socket.emit('operators:update', mockOperators);
}

// Manipuladores de ações de tickets
function handleTicketCall(ticketId, operatorId) {
  const ticket = mockTickets.find(t => t.id === ticketId);
  if (ticket) {
    ticket.status = 'called';
    ticket.calledAt = new Date().toISOString();
    ticket.operatorId = operatorId;
    
    // Atualizar estatísticas
    mockStats.inQueueTickets--;
    mockStats.calledTickets++;
    
    // Enviar atualizações para todos os clientes
    broadcastUpdates();
  }
}

function handleTicketStart(ticketId) {
  const ticket = mockTickets.find(t => t.id === ticketId);
  if (ticket) {
    ticket.status = 'in_progress';
    ticket.startedAt = new Date().toISOString();
    
    // Atualizar estatísticas
    mockStats.calledTickets--;
    mockStats.inProgressTickets++;
    
    // Enviar atualizações para todos os clientes
    broadcastUpdates();
  }
}

function handleTicketComplete(ticketId) {
  const ticket = mockTickets.find(t => t.id === ticketId);
  if (ticket) {
    ticket.status = 'completed';
    ticket.completedAt = new Date().toISOString();
    
    // Atualizar estatísticas
    if (ticket.status === 'in_progress') {
      mockStats.inProgressTickets--;
    } else if (ticket.status === 'called') {
      mockStats.calledTickets--;
    }
    mockStats.completedTickets++;
    
    // Adicionar ao faturamento
    if (ticket.service && ticket.service.price) {
      mockStats.dailyRevenue += ticket.service.price;
    }
    
    // Enviar atualizações para todos os clientes
    broadcastUpdates();
  }
}

function handleTicketCancel(ticketId) {
  const ticket = mockTickets.find(t => t.id === ticketId);
  if (ticket) {
    ticket.status = 'cancelled';
    ticket.cancelledAt = new Date().toISOString();
    
    // Atualizar estatísticas
    if (ticket.status === 'in_queue') {
      mockStats.inQueueTickets--;
    } else if (ticket.status === 'called') {
      mockStats.calledTickets--;
    } else if (ticket.status === 'in_progress') {
      mockStats.inProgressTickets--;
    }
    mockStats.cancelledTickets++;
    
    // Enviar atualizações para todos os clientes
    broadcastUpdates();
  }
}

// Enviar atualizações para todos os clientes
function broadcastUpdates() {
  // Enviar tickets atualizados
  io.emit('tickets:update', mockTickets);
  
  // Enviar estatísticas atualizadas
  io.emit('stats:update', mockStats);
}

// Simulação de novos tickets a cada 30 segundos
setInterval(() => {
  if (mockTickets.filter(t => t.status === 'in_queue').length < 5) {
    const newTicket = {
      id: `${mockTickets.length + 1}`,
      number: `A00${mockTickets.length + 1}`,
      serviceId: Math.random() > 0.5 ? '1' : '2',
      service: Math.random() > 0.5 ? 
        {
          id: '1',
          name: 'Banheira de Gelo',
          description: 'Imersão em água gelada para recuperação muscular',
          price: 50.0,
          duration: 10,
          slug: 'banheira-gelo',
          color: '#0891b2'
        } : 
        {
          id: '2',
          name: 'Bota de Compressão',
          description: 'Compressão pneumática para recuperação muscular',
          price: 40.0,
          duration: 15,
          slug: 'bota-compressao',
          color: '#7e22ce'
        },
      status: 'in_queue',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      queuedAt: new Date().toISOString(),
      priority: 'normal',
      queuePosition: mockTickets.filter(t => t.status === 'in_queue').length + 1,
      estimatedWaitTime: (mockTickets.filter(t => t.status === 'in_queue').length + 1) * 5
    };
    
    mockTickets.push(newTicket);
    mockStats.totalTickets++;
    mockStats.inQueueTickets++;
    
    console.log('Novo ticket criado:', newTicket.number);
    broadcastUpdates();
  }
}, 30000);

// Iniciar servidor na porta 8000
server.listen(8000, () => {
  console.log('Servidor Socket.IO mock iniciado na porta 8000');
  console.log('Abra http://localhost:3001 para ver o painel de chamadas');
}); 