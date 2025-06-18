import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TicketDisplay } from '../components/TicketDisplay';
import { EquipmentSetup } from '../components/EquipmentSetup';
import { EquipmentManager } from '../components/EquipmentManager';
import { ServiceStatus } from '../components/ServiceStatus';
import { ServiceCountdown } from '../components/ServiceCountdown';
import { ExportReportButton } from '../components/ExportReportButton';
import { useMockPanelStore } from '../store/mockPanelStore';

// Definir tipos inline para evitar problemas de importação
interface Equipment {
  id: string;
  name: string;
  type: 'banheira_gelo' | 'bota_compressao';
  status: 'available' | 'in_use' | 'maintenance';
  serviceId: string;
}

const OperatorPage: React.FC = () => {
  const [selectedTicket, setSelectedTicket] = useState<string | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [operatorId, setOperatorId] = useState<string>('');
  const [operatorName, setOperatorName] = useState<string>('');
  const [operatorSaved, setOperatorSaved] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'queue' | 'equipment'>('queue');
  
  const { 
    tickets, 
    operators, 
    equipment,
    operationConfig,
    callTicket, 
    startService, 
    completeService, 
    cancelTicket,
    resetMockData,
    startOperation,
    endOperation
  } = useMockPanelStore();
  
  // Filtrar tickets na fila
  const queuedTickets = tickets.filter(ticket => ticket.status === 'in_queue');
  
  // Tickets chamados ou em atendimento pelo operador atual
  const activeTickets = tickets.filter(ticket => 
    (ticket.status === 'called' || ticket.status === 'in_progress') && 
    ticket.operatorId === operatorId
  );
  
  // Tickets em atendimento por todos os operadores
  const inProgressTickets = tickets.filter(ticket => 
    ticket.status === 'in_progress'
  );
  
  // Chamar próximo ticket
  const handleCallNext = () => {
    if (queuedTickets.length === 0 || !operatorId || !selectedEquipment) return;
    
    const nextTicket = queuedTickets[0];
    callTicket(nextTicket.id, operatorId, selectedEquipment.id);
    setSelectedTicket(nextTicket.id);
  };
  
  // Iniciar atendimento
  const handleStartService = (ticketId: string) => {
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket || !ticket.equipmentId) return;
    
    startService(ticket.id, ticket.equipmentId);
  };
  
  // Completar atendimento
  const handleCompleteService = (ticketId: string) => {
    completeService(ticketId);
  };
  
  // Cancelar atendimento
  const handleCancelService = (ticketId: string) => {
    cancelTicket(ticketId);
  };
  
  // Selecionar um equipamento
  const handleSelectEquipment = (eq: Equipment) => {
    if (eq.status === 'available') {
      setSelectedEquipment(eq);
    }
  };
  
  // Salvar informações do operador
  const handleSaveOperator = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Aqui você pode adicionar lógica para salvar o operador no backend
    // Por enquanto, apenas salvamos localmente
    localStorage.setItem('operatorId', operatorId);
    localStorage.setItem('operatorName', operatorName);
    setOperatorSaved(true);
  };

  // Iniciar operação com configuração
  const handleStartOperation = () => {
    startOperation();
  };
  
  // Encerrar operação
  const handleEndOperation = () => {
    endOperation();
    setSelectedEquipment(null);
  };
  
  // Carregar informações do operador do localStorage
  useEffect(() => {
    const savedOperatorId = localStorage.getItem('operatorId');
    const savedOperatorName = localStorage.getItem('operatorName');
    
    if (savedOperatorId) {
      setOperatorId(savedOperatorId);
      setOperatorSaved(true);
    }
    if (savedOperatorName) setOperatorName(savedOperatorName);
  }, []);
  
  return (
    <div className="panel-container">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h1 className="text-3xl font-bold">Painel do Operador</h1>
        <div className="flex flex-wrap gap-3">
          {operationConfig.isOperating && (
            <>
              <button
                onClick={() => setActiveTab(activeTab === 'queue' ? 'equipment' : 'queue')}
                className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                {activeTab === 'queue' ? 'Ver Equipamentos' : 'Ver Fila'}
              </button>
              
              <ExportReportButton variant="secondary" />
            </>
          )}
          <button
            onClick={resetMockData}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Resetar Dados (Demo)
          </button>
        </div>
      </div>
      
      {/* Configuração do operador */}
      {!operatorSaved && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Identificação do Operador</h2>
          
          <form onSubmit={handleSaveOperator} className="space-y-4">
            <div>
              <label htmlFor="operatorId" className="block text-sm font-medium mb-1">
                ID do Operador
              </label>
              <input
                type="text"
                id="operatorId"
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <div>
              <label htmlFor="operatorName" className="block text-sm font-medium mb-1">
                Nome do Operador
              </label>
              <input
                type="text"
                id="operatorName"
                value={operatorName}
                onChange={(e) => setOperatorName(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            
            <div>
              <button
                type="submit"
                className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80 transition-colors"
              >
                Salvar
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Configuração de equipamentos ou gerenciamento de equipamentos */}
      {operatorSaved && (
        <>
          {!operationConfig.isOperating ? (
            <div className="mb-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Configuração Inicial</h2>
                <p className="text-gray-600 mb-6">
                  Configure a quantidade de equipamentos disponíveis antes de iniciar a operação.
                </p>
                <EquipmentSetup onComplete={handleStartOperation} />
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'equipment' && (
                <div className="mb-6">
                  <EquipmentManager 
                    onSelectEquipment={handleSelectEquipment}
                    onEndOperation={handleEndOperation} 
                  />
                </div>
              )}
            </>
          )}
        </>
      )}
      
      {/* Área de atendimento e fila - mostrar apenas se operador estiver identificado e operação iniciada */}
      {operatorSaved && operationConfig.isOperating && activeTab === 'queue' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Coluna da esquerda - Atendimentos ativos */}
          <div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Atendimentos Ativos</h2>
              
              {activeTickets.length > 0 ? (
                <div className="space-y-6">
                  {activeTickets.map(ticket => {
                    const ticketEquipment = equipment.find(e => e.id === ticket.equipmentId);
                    
                    return (
                      <div key={ticket.id} className="border border-gray-200 rounded-lg p-4">
                        <ServiceStatus 
                          ticket={ticket} 
                          serviceDuration={operationConfig.serviceDuration}
                          onComplete={() => handleCompleteService(ticket.id)}
                        />
                        
                        <div className="p-3 mt-3 bg-blue-50 rounded-md">
                          <h3 className="font-medium">Equipamento</h3>
                          <p>{ticketEquipment?.name || 'Nenhum equipamento selecionado'}</p>
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mt-3">
                          {ticket.status === 'called' && (
                            <button
                              onClick={() => handleStartService(ticket.id)}
                              disabled={!ticket.equipmentId}
                              className="px-4 py-2 bg-secondary text-primary font-semibold rounded-md hover:bg-secondary/80 transition-colors disabled:opacity-50"
                            >
                              Iniciar Atendimento
                            </button>
                          )}
                          
                          {ticket.status === 'in_progress' && (
                            <button
                              onClick={() => handleCompleteService(ticket.id)}
                              className="px-4 py-2 bg-secondary text-primary font-semibold rounded-md hover:bg-secondary/80 transition-colors"
                            >
                              Concluir Atendimento
                            </button>
                          )}
                          
                          <button
                            onClick={() => handleCancelService(ticket.id)}
                            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Nenhum ticket em atendimento</p>
                  
                  {queuedTickets.length > 0 && (
                    <>
                      <div className="my-4">
                        <h3 className="text-lg font-medium mb-2">Selecione um equipamento disponível:</h3>
                        <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto p-2">
                          {equipment
                            .filter(eq => eq.status === 'available')
                            .map(eq => (
                              <div
                                key={eq.id}
                                onClick={() => setSelectedEquipment(eq)}
                                className={`p-2 border rounded cursor-pointer ${
                                  selectedEquipment?.id === eq.id
                                    ? 'border-primary bg-primary/10'
                                    : 'border-gray-200 hover:bg-gray-50'
                                }`}
                              >
                                <p className="font-medium">{eq.name}</p>
                                <p className="text-xs text-gray-500">
                                  {eq.type === 'banheira_gelo' ? 'Banheira de Gelo' : 'Bota de Compressão'}
                                </p>
                              </div>
                            ))}
                        </div>
                      </div>
                      
                      <button
                        onClick={handleCallNext}
                        disabled={!selectedEquipment}
                        className="mt-4 px-6 py-3 bg-secondary text-primary font-semibold rounded-md hover:bg-secondary/80 transition-colors disabled:opacity-50"
                      >
                        {selectedEquipment ? 'Chamar Próximo' : 'Selecione um equipamento disponível'}
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
            
            {/* Todos os atendimentos em andamento */}
            {inProgressTickets.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mt-6">
                <h2 className="text-xl font-semibold mb-4">Todos os Atendimentos em Andamento</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {inProgressTickets.map(ticket => {
                    const ticketEquipment = equipment.find(e => e.id === ticket.equipmentId);
                    const isMyTicket = ticket.operatorId === operatorId;
                    
                    return (
                      <div 
                        key={ticket.id} 
                        className={`border rounded-lg p-3 ${isMyTicket ? 'border-primary' : 'border-gray-200'}`}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">Senha: {ticket.number}</p>
                            <p className="text-sm">{ticket.service?.name}</p>
                            <p className="text-xs text-gray-500">
                              Equipamento: {ticketEquipment?.name || 'N/A'}
                            </p>
                          </div>
                          
                          {ticket.startedAt && (
                            <div className="text-right">
                              <ServiceCountdown 
                                startTime={ticket.startedAt}
                                duration={operationConfig.serviceDuration}
                                className="w-24"
                              />
                            </div>
                          )}
                        </div>
                        
                        {isMyTicket && (
                          <div className="mt-2 flex justify-end">
                            <button
                              onClick={() => handleCompleteService(ticket.id)}
                              className="px-2 py-1 text-xs bg-secondary text-primary rounded hover:bg-secondary/80"
                            >
                              Concluir
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
          
          {/* Coluna da direita - Fila de espera */}
          <div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Fila de Espera</h2>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {queuedTickets.length} tickets
                </span>
              </div>
              
              {queuedTickets.length > 0 ? (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                  {queuedTickets.map(ticket => (
                    <div 
                      key={ticket.id}
                      className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                    >
                      <TicketDisplay 
                        ticket={ticket} 
                        size="small"
                        showPosition
                      />
                      {selectedEquipment && (
                        <div className="mt-2 flex justify-end">
                          <button
                            onClick={() => callTicket(ticket.id, operatorId, selectedEquipment.id)}
                            className="px-3 py-1 text-sm bg-primary text-white rounded hover:bg-primary/80"
                          >
                            Chamar este ticket
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Não há tickets na fila de espera</p>
                </div>
              )}
            </div>
            
            {/* Equipamentos disponíveis */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-6">
              <h2 className="text-xl font-semibold mb-4">Equipamentos Disponíveis</h2>
              
              <div className="grid grid-cols-2 gap-3">
                {equipment
                  .filter(eq => eq.status === 'available')
                  .map(eq => (
                    <div
                      key={eq.id}
                      onClick={() => setSelectedEquipment(eq)}
                      className={`p-3 border rounded-lg cursor-pointer ${
                        selectedEquipment?.id === eq.id
                          ? 'border-primary bg-primary/10'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <p className="font-medium">{eq.name}</p>
                      <p className="text-xs text-gray-500">
                        {eq.type === 'banheira_gelo' ? 'Banheira de Gelo' : 'Bota de Compressão'}
                      </p>
                    </div>
                  ))}
                
                {equipment.filter(eq => eq.status === 'available').length === 0 && (
                  <div className="col-span-2 text-center py-4 text-gray-500">
                    Não há equipamentos disponíveis no momento
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OperatorPage; 