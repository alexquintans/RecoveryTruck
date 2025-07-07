import React, { useState, useEffect } from 'react';
import { useTicketQueue } from '../hooks/useTicketQueue';
import { useDisplayWebSocket } from '../hooks/useDisplayWebSocket';
import { useAuth } from '../hooks/useAuth';

interface Ticket {
  id: string;
  number?: string;
  status: string;
  calledAt?: string;
  service?: { name: string };
  services?: { name: string }[];
  customer?: { name: string };
  equipmentId?: string;
  operator?: { name: string };
}

const DisplayPage: React.FC = () => {
  const { user } = useAuth();
  const { tickets, equipment, operationConfig } = useTicketQueue();
  const [lastCalled, setLastCalled] = useState<Ticket | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isOperating, setIsOperating] = useState(false);

  // Obter tenant ID do usuário ou usar default
  const tenantId = (user as any)?.tenant_id || 'default';

  // WebSocket para display público
  const { isConnected, isConnecting, lastMessage } = useDisplayWebSocket({
    tenantId,
    enabled: true,
    onTicketCalled: (ticketData) => {
      console.log('🎉 Novo ticket chamado via WebSocket:', ticketData);
      // Atualizar último chamado quando receber via WebSocket
      const calledTicket = tickets.find(t => t.id === ticketData.id);
      if (calledTicket) {
        setLastCalled(calledTicket);
      }
    },
    onQueueUpdate: (update) => {
      console.log('📋 Atualização da fila via WebSocket:', update);
    },
  });

  // Atualizar horário a cada segundo
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Verificar se a operação está ativa
  useEffect(() => {
    setIsOperating(operationConfig.isOperating);
  }, [operationConfig.isOperating]);

  // Atualizar último ticket chamado
  useEffect(() => {
    const called = tickets
      .filter((t: Ticket) => t.status === 'called' || t.status === 'in_progress')
      .sort((a: Ticket, b: Ticket) => (b.calledAt ?? '').localeCompare(a.calledAt ?? ''))[0];
    
    if (called && (!lastCalled || called.id !== lastCalled.id)) {
      setLastCalled(called);
    }
  }, [tickets, lastCalled]);

  // Filtrar próximos na fila
  const queue = tickets.filter((t: Ticket) => t.status === 'in_queue').slice(0, 8);

  // Obter nome do equipamento
  const equipmentName = (id?: string) => {
    if (!id) return '';
    const eq = equipment.find((e: any) => e.id === id);
    return eq?.name ?? '';
  };

  // Formatar número do ticket
  const formatTicketNumber = (ticket: Ticket) => {
    return ticket.number ?? 
           (ticket.id ? `#${ticket.id.substring(0, 6).toUpperCase()}` : '--');
  };

  // Formatar horário
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Formatar data
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-[#17405E] text-white overflow-hidden font-sans">
      {/* Header com informações do sistema */}
      <header className="bg-[#17405E] border-b-4 border-[#7ED321] p-4 shadow-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-3 h-3 rounded-full bg-[#7ED321] animate-pulse"></div>
            <h1 className="text-2xl font-bold tracking-wide text-white">RecoveryTruck</h1>
            <span className="text-sm bg-[#7ED321] text-[#17405E] px-2 py-1 rounded font-semibold">Display Público</span>
          </div>
          <div className="text-right">
            <div className="text-3xl font-mono font-bold text-white">{formatTime(currentTime)}</div>
            <div className="text-sm text-[#2E6B8C] font-medium">{formatDate(currentTime)}</div>
          </div>
        </div>
      </header>

      {/* Status da conexão */}
      <div className="absolute top-20 right-4 z-10">
        <div className={`px-3 py-1 rounded-full text-xs font-bold border-2 ${
          isConnected 
            ? 'bg-[#7ED321] text-[#17405E] border-[#7ED321]' 
            : isConnecting 
            ? 'bg-yellow-400 text-[#17405E] border-yellow-400' 
            : 'bg-red-500 text-white border-red-500'
        }`}>
          {isConnected ? '🟢 Conectado' : isConnecting ? '🟡 Conectando...' : '🔴 Desconectado'}
        </div>
      </div>

      {/* Conteúdo principal */}
      <main className="flex flex-col items-center justify-center min-h-screen p-8 space-y-10">
        {/* Título principal */}
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-extrabold text-[#7ED321] tracking-wider drop-shadow-lg">
            CHAMADA DE SENHAS
          </h2>
          <p className="text-xl text-white/80 font-medium">
            {isOperating ? 'Sistema em Operação' : 'Sistema Pausado'}
          </p>
        </div>

        {/* Último chamado - Destaque principal */}
        <section className="w-full max-w-3xl bg-white/90 rounded-2xl border-4 border-[#7ED321] shadow-xl p-10 text-center space-y-6">
          <h3 className="text-3xl font-bold text-[#17405E] mb-2 tracking-wide">SENHA CHAMADA</h3>
          {lastCalled ? (
            <div className="space-y-4">
              {/* Número do ticket em destaque */}
              <div className="text-8xl font-extrabold text-[#7ED321] tracking-widest animate-pulse drop-shadow-xl">
                {formatTicketNumber(lastCalled)}
              </div>
              {/* Informações do cliente */}
              <div className="space-y-2">
                <div className="text-2xl font-semibold text-[#17405E]">
                  {lastCalled.customer?.name ?? 'Cliente'}
                </div>
                <div className="text-xl text-[#2E6B8C] font-medium">
                  {/* Suporte para múltiplos serviços */}
                  {lastCalled.services && lastCalled.services.length > 0 ? (
                    <span>
                      {lastCalled.services.map((service, index) => (
                        <span key={index}>
                          {service.name}{index < lastCalled.services!.length - 1 ? ', ' : ''}
                        </span>
                      ))}
                    </span>
                  ) : (
                    <span>{lastCalled.service?.name ?? 'Serviço'}</span>
                  )}
                  {lastCalled.equipmentId && (
                    <span className="ml-2 text-[#7ED321] font-bold">
                      – {equipmentName(lastCalled.equipmentId)}
                    </span>
                  )}
                </div>
                {lastCalled.operator?.name && (
                  <div className="text-lg text-[#17405E] font-semibold">
                    Operador: {lastCalled.operator.name}
                  </div>
                )}
              </div>
              {/* Horário da chamada */}
              {lastCalled.calledAt && (
                <div className="text-sm text-[#2E6B8C] font-medium">
                  Chamado às {new Date(lastCalled.calledAt).toLocaleTimeString('pt-BR', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-6xl text-[#17405E]/30 font-bold">---</div>
              <p className="text-xl text-[#17405E]/40">Aguardando próxima chamada...</p>
            </div>
          )}
        </section>

        {/* Próximos na fila */}
        <section className="w-full max-w-3xl bg-white/80 rounded-2xl border-2 border-[#7ED321] shadow-lg p-6">
          <h3 className="text-2xl font-bold text-[#17405E] mb-4 text-center tracking-wide">
            PRÓXIMOS NA FILA
          </h3>
          {queue.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-xl text-[#17405E]/40">Fila vazia</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {queue.map((ticket: Ticket, idx) => (
                <div 
                  key={ticket.id} 
                  className="bg-[#17405E]/10 rounded-lg p-4 text-center border-2 border-[#7ED321] shadow"
                >
                  <div className="text-2xl font-bold text-[#17405E] mb-1">
                    {formatTicketNumber(ticket)}
                  </div>
                  <div className="text-sm text-[#2E6B8C] font-medium">
                    {ticket.service?.name ?? 'Serviço'}
                  </div>
                  <div className="text-xs text-[#17405E]/60 mt-1">
                    Posição {idx + 1}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Informações adicionais */}
        <div className="flex justify-center space-x-8 text-sm text-[#2E6B8C] font-medium">
          <div className="text-center">
            <div className="font-semibold text-[#17405E]">Total na Fila</div>
            <div className="text-2xl font-bold text-[#7ED321]">{tickets.filter(t => t.status === 'in_queue').length}</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-[#17405E]">Em Atendimento</div>
            <div className="text-2xl font-bold text-[#7ED321]">{tickets.filter(t => t.status === 'in_progress').length}</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-[#17405E]">Equipamentos Ativos</div>
            <div className="text-2xl font-bold text-[#7ED321]">{equipment.filter(e => e.status === 'in_use').length}</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="absolute bottom-4 left-4 right-4 text-center">
        <p className="text-sm text-white/70 font-medium">
          Sistema de Gerenciamento de Filas - RecoveryTruck
        </p>
      </footer>
    </div>
  );
};

export default DisplayPage; 