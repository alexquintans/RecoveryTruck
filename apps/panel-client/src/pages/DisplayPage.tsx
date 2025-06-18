import React, { useState, useEffect } from 'react';
import { useMockPanelStore } from '../store/mockPanelStore';

// Definir tipos inline para evitar problemas de importação
interface Customer {
  name: string;
}

interface Service {
  id: string;
  name: string;
  color?: string;
}

interface Ticket {
  id: string;
  number: string;
  status: string;
  createdAt: string;
  calledAt?: string;
  service?: Service;
  customer?: Customer;
  equipmentId?: string;
}

const DisplayPage: React.FC = () => {
  const { tickets, equipment, toggleAutoCall, autoCallEnabled, addRandomTicket } = useMockPanelStore();
  const [lastCalledTicket, setLastCalledTicket] = useState<Ticket | null>(null);
  const [animateCall, setAnimateCall] = useState(false);
  const [showFlash, setShowFlash] = useState(false);
  
  // Tickets chamados recentemente (últimos 5)
  const recentlyCalled = tickets
    .filter(ticket => ticket.status === 'called' || ticket.status === 'in_progress')
    .sort((a, b) => {
      const dateA = a.calledAt ? new Date(a.calledAt).getTime() : 0;
      const dateB = b.calledAt ? new Date(b.calledAt).getTime() : 0;
      return dateB - dateA;
    })
    .slice(0, 5);
  
  // Tickets na fila de espera
  const queuedTickets = tickets
    .filter(ticket => ticket.status === 'in_queue')
    .slice(0, 10);
  
  // Detectar novo ticket chamado
  useEffect(() => {
    const latestCalled = recentlyCalled[0];
    
    if (latestCalled && (!lastCalledTicket || latestCalled.id !== lastCalledTicket.id)) {
      setLastCalledTicket(latestCalled);
      setAnimateCall(true);
      
      // Efeito de flash na tela
      setShowFlash(true);
      setTimeout(() => setShowFlash(false), 500);
      
      // Tocar som de notificação usando Web Audio API
      try {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime); // Nota A5
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.5, audioContext.currentTime + 0.1);
        gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 1);
      } catch (err) {
        console.error('Erro ao tocar som:', err);
      }
      
      // Remover animação após 5 segundos
      setTimeout(() => {
        setAnimateCall(false);
      }, 5000);
    }
  }, [recentlyCalled, lastCalledTicket]);
  
  // Encontrar equipamento associado ao ticket
  const getEquipmentName = (equipmentId?: string) => {
    if (!equipmentId) return '';
    const eq = equipment.find(e => e.id === equipmentId);
    return eq ? eq.name : '';
  };
  
  // Adicionar ticket manualmente para demonstração
  const handleAddTicket = () => {
    addRandomTicket();
  };
  
  return (
    <div className="display-container bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen p-6 relative overflow-hidden">
      {/* Flash de notificação */}
      {showFlash && (
        <div className="absolute inset-0 bg-primary opacity-30 z-50 animate-flash"></div>
      )}
      
      {/* Círculos decorativos */}
      <div className="absolute top-20 right-20 w-64 h-64 rounded-full bg-blue-200 opacity-20 blur-3xl"></div>
      <div className="absolute bottom-20 left-20 w-80 h-80 rounded-full bg-indigo-200 opacity-20 blur-3xl"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <header className="mb-8 flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0 text-center md:text-left">
            <h1 className="text-4xl font-bold text-primary mb-2">Painel de Chamadas</h1>
            <p className="text-xl text-text-light">
              {new Date().toLocaleDateString('pt-BR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={handleAddTicket}
              className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg shadow-lg transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-opacity-50"
            >
              <span className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Novo Ticket
              </span>
            </button>
            
            <button
              onClick={toggleAutoCall}
              className={`${
                autoCallEnabled ? 'bg-red-500 hover:bg-red-600' : 'bg-secondary hover:bg-secondary/90'
              } ${autoCallEnabled ? 'text-white' : 'text-primary'} px-4 py-2 rounded-lg shadow-lg transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${
                autoCallEnabled ? 'focus:ring-red-400' : 'focus:ring-secondary'
              }`}
            >
              <span className="flex items-center">
                {autoCallEnabled ? (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                    </svg>
                    Parar Simulação
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                    </svg>
                    Iniciar Simulação
                  </>
                )}
              </span>
            </button>
          </div>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Última chamada */}
          <div className="col-span-1 lg:col-span-2">
            <div 
              className={`bg-white rounded-2xl shadow-xl p-8 border-l-8 border-primary transition-all duration-500
                ${animateCall ? 'animate-pulse border-red-500 transform scale-105' : ''}`}
            >
              <h2 className="text-2xl font-bold mb-6 text-center flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                </svg>
                Chamada Atual
              </h2>
              
              {lastCalledTicket ? (
                <div className="text-center">
                  <div className="flex justify-center items-center mb-6">
                    <div className={`bg-primary text-white text-6xl font-bold py-6 px-10 rounded-xl shadow-lg transform ${animateCall ? 'scale-110' : ''} transition-transform duration-500`}>
                      {lastCalledTicket.number}
                    </div>
                  </div>
                  
                  <div className="text-3xl font-medium mb-3">
                    {lastCalledTicket.customer?.name || 'Cliente'}
                  </div>
                  
                  <div className="text-xl text-gray-600 mb-5">
                    {lastCalledTicket.service?.name || 'Serviço'}
                  </div>
                  
                  <div className="inline-block bg-secondary text-primary text-xl font-semibold py-3 px-6 rounded-lg shadow">
                    {getEquipmentName(lastCalledTicket.equipmentId)}
                  </div>
                </div>
              ) : (
                <div className="text-center text-text-light text-xl py-12">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Nenhum ticket sendo chamado no momento
                </div>
              )}
            </div>
          </div>
          
          {/* Chamados recentes */}
          <div>
            <div className="bg-white rounded-xl shadow-lg p-6 h-full border-t-4 border-primary">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-primary">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                Chamados Recentes
              </h2>
              
              {recentlyCalled.length > 0 ? (
                <div className="space-y-4">
                  {recentlyCalled.map((ticket, index) => (
                    index > 0 && (
                      <div 
                        key={ticket.id} 
                        className="border border-gray-200 rounded-lg p-4 transition-all hover:shadow-md hover:border-primary"
                      >
                        <div className="flex justify-between items-center">
                          <div className="flex items-center">
                            <span className="text-xl font-bold mr-3 bg-primary/10 text-primary py-1 px-3 rounded-lg">{ticket.number}</span>
                            <div>
                              <p className="font-medium text-text">{ticket.customer?.name || 'Cliente'}</p>
                              <p className="text-sm text-text-light">{ticket.service?.name || 'Serviço'}</p>
                            </div>
                          </div>
                          <div className="bg-secondary text-primary text-xs font-semibold px-2 py-1 rounded-full">
                            Em Atendimento
                          </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-500 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                          </svg>
                          Equipamento: {getEquipmentName(ticket.equipmentId)}
                        </div>
                      </div>
                    )
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Nenhum ticket sendo chamado no momento
                </div>
              )}
            </div>
          </div>
          
          {/* Fila de espera */}
          <div>
            <div className="bg-white rounded-xl shadow-lg p-6 h-full border-t-4 border-secondary">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-primary">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
                Fila de Espera
              </h2>
              
              {queuedTickets.length > 0 ? (
                <div className="space-y-2">
                  {queuedTickets.map((ticket, index) => (
                    <div 
                      key={ticket.id} 
                      className="border border-gray-200 rounded-lg p-3 transition-all hover:shadow-md hover:border-secondary"
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center">
                          <span className="text-lg font-bold mr-3 bg-secondary/20 text-primary py-1 px-2 rounded-lg">{ticket.number}</span>
                          <p className="text-sm text-text-light">{ticket.service?.name || 'Serviço'}</p>
                        </div>
                        <div className="bg-primary/10 text-primary text-xs font-semibold px-2 py-1 rounded-full">
                          Na Fila
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Não há tickets na fila de espera
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Status dos equipamentos */}
        <div className="mt-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-primary/70">
            <h2 className="text-xl font-semibold mb-4 flex items-center text-primary">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              Status dos Equipamentos
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Banheiras de Gelo */}
              <div className="border border-gray-200 rounded-lg p-4 transition-all hover:shadow-md hover:border-primary/30">
                <h3 className="font-semibold text-lg mb-3 flex items-center text-primary">
                  <span className="w-3 h-3 rounded-full bg-primary mr-2"></span>
                  Banheiras de Gelo
                </h3>
                
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-green-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-green-700">
                      {equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'available').length}
                    </div>
                    <div className="text-xs text-green-600">Disponíveis</div>
                  </div>
                  
                  <div className="bg-yellow-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-yellow-700">
                      {equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'in_use').length}
                    </div>
                    <div className="text-xs text-yellow-600">Em Uso</div>
                  </div>
                  
                  <div className="bg-red-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-red-700">
                      {equipment.filter(e => e.type === 'banheira_gelo' && e.status === 'maintenance').length}
                    </div>
                    <div className="text-xs text-red-600">Manutenção</div>
                  </div>
                </div>
              </div>
              
              {/* Botas de Compressão */}
              <div className="border border-gray-200 rounded-lg p-4 transition-all hover:shadow-md hover:border-primary/30">
                <h3 className="font-semibold text-lg mb-3 flex items-center text-primary">
                  <span className="w-3 h-3 rounded-full bg-secondary mr-2"></span>
                  Botas de Compressão
                </h3>
                
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-green-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-green-700">
                      {equipment.filter(e => e.type === 'bota_compressao' && e.status === 'available').length}
                    </div>
                    <div className="text-xs text-green-600">Disponíveis</div>
                  </div>
                  
                  <div className="bg-yellow-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-yellow-700">
                      {equipment.filter(e => e.type === 'bota_compressao' && e.status === 'in_use').length}
                    </div>
                    <div className="text-xs text-yellow-600">Em Uso</div>
                  </div>
                  
                  <div className="bg-red-100 p-3 rounded-lg transition-transform hover:scale-105">
                    <div className="text-2xl font-bold text-red-700">
                      {equipment.filter(e => e.type === 'bota_compressao' && e.status === 'maintenance').length}
                    </div>
                    <div className="text-xs text-red-600">Manutenção</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <footer className="mt-8 text-center text-text-light text-sm py-4">
          © {new Date().getFullYear()} RecoveryTruck. Todos os direitos reservados.
        </footer>
      </div>
    </div>
  );
};

export default DisplayPage; 