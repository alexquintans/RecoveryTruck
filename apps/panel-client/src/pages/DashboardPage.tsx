import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useMockPanelStore } from '../store/mockPanelStore';
import { TicketDisplay } from '../components/TicketDisplay';
import { ExportReportButton } from '../components/ExportReportButton';

const DashboardPage: React.FC = () => {
  const { tickets, equipment, stats, operationConfig } = useMockPanelStore();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Atualizar o tempo atual a cada minuto
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(timer);
  }, []);
  
  // Filtrar tickets por status
  const queuedTickets = tickets.filter(ticket => ticket.status === 'in_queue');
  const calledTickets = tickets.filter(ticket => ticket.status === 'called');
  const inProgressTickets = tickets.filter(ticket => ticket.status === 'in_progress');
  const completedTickets = tickets.filter(ticket => ticket.status === 'completed').slice(0, 5);
  
  // Contar tickets por status
  const ticketCounts = {
    inQueue: tickets.filter(t => t.status === 'in_queue').length,
    called: tickets.filter(t => t.status === 'called').length,
    inProgress: tickets.filter(t => t.status === 'in_progress').length,
    completed: tickets.filter(t => t.status === 'completed').length,
    cancelled: tickets.filter(t => t.status === 'cancelled').length,
    total: tickets.length
  };
  
  // Contar equipamentos por status
  const equipmentCounts = {
    available: equipment.filter(e => e.status === 'available').length,
    inUse: equipment.filter(e => e.status === 'in_use').length,
    maintenance: equipment.filter(e => e.status === 'maintenance').length,
    total: equipment.length
  };
  
  // Calcular utilização de equipamentos
  const calculateUtilization = () => {
    if (equipmentCounts.total === 0) return 0;
    return Math.round((equipmentCounts.inUse / equipmentCounts.total) * 100);
  };
  
  const utilization = calculateUtilization();
  
  // Calcular tempo médio de atendimento
  const calculateAverageServiceTime = () => {
    const completedTickets = tickets.filter(ticket => 
      ticket.status === 'completed' && ticket.startedAt && ticket.completedAt
    );
    
    if (completedTickets.length === 0) return 0;
    
    const totalMinutes = completedTickets.reduce((sum, ticket) => {
      const startTime = new Date(ticket.startedAt!).getTime();
      const endTime = new Date(ticket.completedAt!).getTime();
      const diffMinutes = (endTime - startTime) / (1000 * 60);
      return sum + diffMinutes;
    }, 0);
    
    return Math.round(totalMinutes / completedTickets.length);
  };
  
  const averageServiceTime = calculateAverageServiceTime();
  
  // Calcular receita média por atendimento
  const calculateAverageRevenue = () => {
    const completedTickets = tickets.filter(ticket => 
      ticket.status === 'completed' && ticket.service?.price
    );
    
    if (completedTickets.length === 0) return 0;
    
    const totalRevenue = completedTickets.reduce((sum, ticket) => 
      sum + (ticket.service?.price || 0), 0
    );
    
    return Math.round((totalRevenue / completedTickets.length) * 100) / 100;
  };
  
  const averageRevenue = calculateAverageRevenue();
  
  // Calcular tempo médio de espera em formato legível
  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} min`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours}h ${remainingMinutes}min`;
    }
  };
  
  // Formatar valor monetário
  const formatCurrency = (value: number) => {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  };
  
  return (
    <div className="dashboard-container">
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-600">Visão geral do sistema de filas e equipamentos</p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-end sm:items-center mt-4 sm:mt-0 gap-4">
            <div className="text-xl">
              {currentTime.toLocaleDateString('pt-BR')} - {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
            </div>
            
            <ExportReportButton />
          </div>
        </div>
      </div>
      
      {/* Status da operação */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Status da Operação</h2>
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${operationConfig.isOperating ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium">
              {operationConfig.isOperating ? 'Em operação' : 'Operação não iniciada'}
            </span>
          </div>
          
          {operationConfig.isOperating && (
            <>
              <div>
                <span className="text-gray-600 mr-2">Tempo de serviço:</span>
                <span className="font-medium">{operationConfig.serviceDuration} minutos</span>
              </div>
              <div>
                <span className="text-gray-600 mr-2">Equipamentos configurados:</span>
                <span className="font-medium">{equipmentCounts.total}</span>
              </div>
            </>
          )}
        </div>
        
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to="/operator" className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80 transition-colors">
            Painel do Operador
          </Link>
          <Link to="/display" className="px-4 py-2 bg-secondary text-primary rounded-md hover:bg-secondary/80 transition-colors">
            Painel de Exibição
          </Link>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Estatísticas de tickets */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Estatísticas de Atendimento</h2>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-blue-600">{ticketCounts.inQueue}</div>
              <div className="text-sm text-gray-600">Na Fila</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-yellow-600">{ticketCounts.called + ticketCounts.inProgress}</div>
              <div className="text-sm text-gray-600">Em Atendimento</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-green-600">{ticketCounts.completed}</div>
              <div className="text-sm text-gray-600">Concluídos</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-purple-600">{stats?.averageWaitTime || 0}</div>
              <div className="text-sm text-gray-600">Tempo Médio (min)</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-red-600">{ticketCounts.cancelled}</div>
              <div className="text-sm text-gray-600">Cancelados</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-gray-600">{tickets.length}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
          
          {/* Métricas adicionais de negócio */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h3 className="text-lg font-medium mb-3">Métricas de Negócio</h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Tempo Médio de Atendimento:</span>
                  <span className="font-bold text-indigo-600">{formatTime(averageServiceTime)}</span>
                </div>
              </div>
              
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Ticket Médio:</span>
                  <span className="font-bold text-indigo-600">{formatCurrency(averageRevenue)}</span>
                </div>
              </div>
              
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Faturamento do Dia:</span>
                  <span className="font-bold text-indigo-600">{formatCurrency(stats?.dailyRevenue || 0)}</span>
                </div>
              </div>
              
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Taxa de Conclusão:</span>
                  <span className="font-bold text-indigo-600">
                    {ticketCounts.total > 0
                      ? `${Math.round((ticketCounts.completed / ticketCounts.total) * 100)}%`
                      : '0%'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Estatísticas de equipamentos */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Status dos Equipamentos</h2>
          
          <div className="mb-4">
            <div className="flex justify-between mb-1">
              <span>Utilização: {utilization}%</span>
              <span>{equipmentCounts.inUse} de {equipmentCounts.total}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="h-2.5 rounded-full bg-blue-600" 
                style={{ width: `${utilization}%` }}
              ></div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-green-600">{equipmentCounts.available}</div>
              <div className="text-sm text-gray-600">Disponíveis</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-yellow-600">{equipmentCounts.inUse}</div>
              <div className="text-sm text-gray-600">Em Uso</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg text-center">
              <div className="text-3xl font-bold text-red-600">{equipmentCounts.maintenance}</div>
              <div className="text-sm text-gray-600">Manutenção</div>
            </div>
          </div>
          
          {/* Detalhes por tipo de equipamento */}
          {operationConfig.isOperating && (
            <div className="mt-4 border-t pt-4">
              <h3 className="text-lg font-medium mb-3">Detalhes por Tipo</h3>
              
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium">Banheiras de Gelo</h4>
                  <div className="flex justify-between text-sm">
                    <span>Configuradas: {operationConfig.equipmentCounts['banheira_gelo']}</span>
                    <span>Em uso: {equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'in_use').length}</span>
                    <span>Disponíveis: {equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'available').length}</span>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium">Botas de Compressão</h4>
                  <div className="flex justify-between text-sm">
                    <span>Configuradas: {operationConfig.equipmentCounts['bota_compressao']}</span>
                    <span>Em uso: {equipment.filter(e => e.type === 'bota_compressao' && e.status === 'in_use').length}</span>
                    <span>Disponíveis: {equipment.filter(e => e.type === 'bota_compressao' && e.status === 'available').length}</span>
                  </div>
                </div>
              </div>
              
              {/* Taxa de utilização por tipo */}
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-medium mb-2">Taxa de Utilização por Tipo</h4>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between mb-1 text-sm">
                      <span>Banheiras de Gelo</span>
                      <span>
                        {operationConfig.equipmentCounts['banheira_gelo'] > 0 
                          ? `${Math.round((equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'in_use').length / operationConfig.equipmentCounts['banheira_gelo']) * 100)}%`
                          : '0%'
                        }
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-blue-500" 
                        style={{ 
                          width: operationConfig.equipmentCounts['banheira_gelo'] > 0 
                            ? `${Math.round((equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'in_use').length / operationConfig.equipmentCounts['banheira_gelo']) * 100)}%`
                            : '0%'
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1 text-sm">
                      <span>Botas de Compressão</span>
                      <span>
                        {operationConfig.equipmentCounts['bota_compressao'] > 0 
                          ? `${Math.round((equipment.filter(e => e.type === 'bota_compressao' && e.status === 'in_use').length / operationConfig.equipmentCounts['bota_compressao']) * 100)}%`
                          : '0%'
                        }
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-green-500" 
                        style={{ 
                          width: operationConfig.equipmentCounts['bota_compressao'] > 0 
                            ? `${Math.round((equipment.filter(e => e.type === 'bota_compressao' && e.status === 'in_use').length / operationConfig.equipmentCounts['bota_compressao']) * 100)}%`
                            : '0%'
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Tickets recentes */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Tickets Recentes</h2>
          
          <div className="flex items-center gap-2">
            <div className="text-sm text-gray-500">
              Mostrando {Math.min(tickets.length, 5)} de {tickets.length} tickets
            </div>
            
            <ExportReportButton variant="outline" size="sm" />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Senha</th>
                <th className="px-4 py-2 text-left">Serviço</th>
                <th className="px-4 py-2 text-left">Cliente</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Horário</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tickets.slice(0, 5).map(ticket => (
                <tr key={ticket.id}>
                  <td className="px-4 py-2 font-medium">{ticket.number}</td>
                  <td className="px-4 py-2">{ticket.service?.name}</td>
                  <td className="px-4 py-2">{ticket.customer?.name}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      ticket.status === 'in_queue' ? 'bg-blue-100 text-blue-800' :
                      ticket.status === 'called' ? 'bg-yellow-100 text-yellow-800' :
                      ticket.status === 'in_progress' ? 'bg-purple-100 text-purple-800' :
                      ticket.status === 'completed' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {ticket.status === 'in_queue' ? 'Na Fila' :
                       ticket.status === 'called' ? 'Chamado' :
                       ticket.status === 'in_progress' ? 'Em Atendimento' :
                       ticket.status === 'completed' ? 'Concluído' :
                       'Cancelado'}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    {ticket.status === 'in_queue' && ticket.createdAt ? new Date(ticket.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                    {ticket.status === 'called' && ticket.calledAt ? new Date(ticket.calledAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                    {ticket.status === 'in_progress' && ticket.startedAt ? new Date(ticket.startedAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                    {ticket.status === 'completed' && ticket.completedAt ? new Date(ticket.completedAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                    {ticket.status === 'cancelled' && ticket.cancelledAt ? new Date(ticket.cancelledAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Componente de card estatístico (não utilizado no momento)
interface StatCardProps {
  title: string;
  value: number;
  color: string;
  icon: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, color, icon }) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${color}`}>
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={`p-3 rounded-full bg-opacity-20 ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 