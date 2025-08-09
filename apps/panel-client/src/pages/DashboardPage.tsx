import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTicketQueue } from '../hooks/useTicketQueue';
import { ExportReportButton } from '../components/ExportReportButton';
import { equipmentService } from '../services/equipmentService';
import { useAuth } from '../hooks/useAuth';

interface Ticket {
  id: string;
  status: string;
  number?: string;
  service?: { name: string; price?: number };
  customer?: { name: string };
  createdAt?: string;
  calledAt?: string;
  startedAt?: string;
  completedAt?: string;
  cancelledAt?: string;
}

export default function DashboardPage() {
  const { tickets, myTickets, completedTickets, cancelledTickets, equipment, operationConfig, refetchOperation } = useTicketQueue();
  const { user } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [services, setServices] = useState<any[]>([]);
  const [isStoppingOperation, setIsStoppingOperation] = useState(false);
  const tenantId = user?.tenant_id
    || tickets[0]?.tenant_id
    || myTickets[0]?.tenant_id
    || completedTickets[0]?.tenant_id
    || cancelledTickets[0]?.tenant_id
    || '';

  // Debug logs (reduzido)
  // console.log('🔍 Dashboard - Resumo:', {
  //   tickets: tickets.length,
  //   myTickets: myTickets.length,
  //   completed: completedTickets.length,
  //   cancelled: cancelledTickets.length
  // });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60_000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!tenantId) return;
    let cancelled = false;
    fetch('/api/operator/services?tenant_id=' + tenantId)
      .then(res => res.json())
      .then(data => { if (!cancelled) setServices(data); })
      .catch(() => { if (!cancelled) setServices([]); });
    return () => { cancelled = true; };
  }, [tenantId]);

  // Refetch automático ao focar a aba/página
  useEffect(() => {
    const onFocus = () => refetchOperation();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [refetchOperation]);

  /** Helpers utilitários */
  const formatTime = (minutes: number) =>
    minutes < 60
      ? `${minutes} min`
      : `${Math.floor(minutes / 60)}h ${minutes % 60}min`;

  const formatCurrency = (value: number) =>
    value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  /** ✅ CORREÇÃO: Cálculos de estatísticas memoizados para evitar React Error #300 */
  const allTickets = useMemo(() => [
    ...tickets,
    ...myTickets,
    ...completedTickets,
    ...cancelledTickets,
  ], [tickets, myTickets, completedTickets, cancelledTickets]);
  
  // Remover duplicatas baseado no ID do ticket
  const uniqueTickets = useMemo(() => 
    allTickets.filter((ticket, index, self) => 
      index === self.findIndex(t => t.id === ticket.id)
    ), [allTickets]
  );
  
  const ticketCounts = useMemo(() => ({
    inQueue: tickets.filter((t: any) => t.status === 'in_queue').length,
    inProgress: myTickets.filter((t: any) => t.status === 'in_progress').length,
    called: myTickets.filter((t: any) => t.status === 'called').length,
    completed: completedTickets.length,
    cancelled: cancelledTickets.length,
    total: uniqueTickets.length,
    // Contagem corrigida para "Em Atendimento" - apenas tickets em progresso (não chamados)
    inService: myTickets.filter((t: any) => t.status === 'in_progress').length,
  }), [tickets, myTickets, completedTickets, cancelledTickets, uniqueTickets]);

  const equipmentCounts = useMemo(() => ({
    available: equipment.filter((e: any) => e.status === 'available').length,
    inUse: equipment.filter((e: any) => e.status === 'in_use').length,
    maintenance: equipment.filter((e: any) => e.status === 'maintenance').length,
    total: equipment.length,
  }), [equipment]);

  const utilization = useMemo(() => 
    equipmentCounts.total
      ? Math.round((equipmentCounts.inUse / equipmentCounts.total) * 100)
      : 0, [equipmentCounts.total, equipmentCounts.inUse]
  );

  // Tickets recentes (últimos 5, incluindo todos os status, ordenados pelo evento mais recente)
  const recentTickets = useMemo(() => 
    allTickets
      .sort((a: any, b: any) => {
        const aDate = new Date(a.completedAt || a.cancelledAt || a.createdAt || 0);
        const bDate = new Date(b.completedAt || b.cancelledAt || b.createdAt || 0);
        return bDate.getTime() - aDate.getTime();
      })
      .slice(0, 5), [allTickets]
  );

  // ✅ CORREÇÃO: Debug logs memoizados para evitar loops infinitos
  const debugData = useMemo(() => ({
    tickets: {
      queue: tickets.length,
      myTickets: myTickets.length,
      completed: completedTickets.length,
      cancelled: cancelledTickets.length,
      total: allTickets.length,
      unique: uniqueTickets.length
    },
    equipment: {
      total: equipment.length,
      available: equipmentCounts.available,
      inUse: equipmentCounts.inUse,
      maintenance: equipmentCounts.maintenance,
      utilization: utilization
    },
    operation: {
      isOperating: operationConfig.isOperating,
      serviceDuration: operationConfig.serviceDuration,
      tenantId
    }
  }), [
    tickets.length, 
    myTickets.length, 
    completedTickets.length, 
    cancelledTickets.length, 
    allTickets.length, 
    uniqueTickets.length,
    equipment.length,
    equipmentCounts.available,
    equipmentCounts.inUse,
    equipmentCounts.maintenance,
    utilization,
    operationConfig.isOperating,
    operationConfig.serviceDuration,
    tenantId
  ]);

  // Debug logs executam apenas quando dados realmente mudam
  useEffect(() => {
    console.log('🔍 DEBUG - Dashboard Data Integrity:', debugData);
  }, [debugData]);

  return (
    <div className="dashboard-container p-4 space-y-6">
      {/* Cabeçalho */}
      <header className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-600">Totem – visão geral</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-lg">
            {currentTime.toLocaleDateString('pt-BR')} –{' '}
            {currentTime.toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          <ExportReportButton />
        </div>
      </header>

      {/* Status da operação */}
      <section className="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 className="text-xl font-semibold">Operação</h2>
        <div className="flex flex-wrap gap-6 items-center">
          <div className="flex items-center gap-2">
            <span
              className={`inline-block w-3 h-3 rounded-full ${operationConfig.isOperating ? 'bg-green-500' : 'bg-red-500'}`}
            />
            <span>{operationConfig.isOperating ? 'Em operação' : 'Parado'}</span>
          </div>
          {operationConfig.isOperating && (
            <>
              <span>
                Tempo de serviço: {operationConfig.serviceDuration} min
              </span>
              <span>Equipamentos: {equipmentCounts.total}</span>
            </>
          )}
        </div>
        <div className="flex gap-3">
          <Link
            to="/operator"
            className="px-3 py-2 bg-blue-600 text-white rounded-md"
          >
            Painel do Operador
          </Link>
          <Link
            to="/display"
            className="px-3 py-2 bg-gray-200 text-gray-800 rounded-md"
          >
            Painel de Exibição
          </Link>
          {operationConfig.isOperating && (
            <div className="flex items-center gap-2">
              <button
                onClick={async () => {
                  // Verificar se há tickets em andamento
                  const ticketsInProgress = myTickets.filter((t: any) => 
                    t.status === 'in_progress' || t.status === 'called'
                  );
                  
                  if (ticketsInProgress.length > 0) {
                    const confirmMessage = `Existem ${ticketsInProgress.length} ticket(s) em andamento. Encerrar a operação irá cancelar todos os atendimentos ativos. Deseja continuar?`;
                    if (!confirm(confirmMessage)) {
                      return;
                    }
                  } else {
                    if (!confirm('Tem certeza que deseja encerrar a operação?')) {
                      return;
                    }
                  }
                  
                  setIsStoppingOperation(true);
                  try {
                    await equipmentService.stopOperation();
                    await refetchOperation();
                    alert('Operação encerrada com sucesso!');
                  } catch (error) {
                    console.error('Erro ao encerrar operação:', error);
                    alert('Erro ao encerrar operação. Tente novamente.');
                  } finally {
                    setIsStoppingOperation(false);
                  }
                }}
                className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                disabled={isStoppingOperation}
              >
                {isStoppingOperation ? 'Encerrando...' : 'Encerrar Operação'}
              </button>
              
              {/* Indicador de tickets em andamento */}
              {myTickets.filter((t: any) => t.status === 'in_progress' || t.status === 'called').length > 0 && (
                <div className="flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-md text-xs">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>
                    {myTickets.filter((t: any) => t.status === 'in_progress' || t.status === 'called').length} ticket(s) em andamento
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Estatísticas rápidas */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tickets */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-semibold">Tickets</h2>
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <Stat 
              label="Fila" 
              value={ticketCounts.inQueue} 
              color="blue" 
              tooltip={`${ticketCounts.inQueue} tickets aguardando atendimento`}
            />
            <Stat
              label="Em Atendimento"
              value={ticketCounts.inService}
              color="yellow"
              tooltip={`${ticketCounts.inService} tickets sendo atendidos ativamente`}
            />
            <Stat 
              label="Concluídos" 
              value={ticketCounts.completed} 
              color="green" 
              tooltip={`${ticketCounts.completed} tickets finalizados hoje`}
            />
            <Stat 
              label="Cancelados" 
              value={ticketCounts.cancelled} 
              color="red" 
              tooltip={`${ticketCounts.cancelled} tickets cancelados hoje`}
            />
            <Stat 
              label="Total" 
              value={ticketCounts.total} 
              color="gray" 
              tooltip={`${ticketCounts.total} tickets processados hoje`}
            />
          </div>
        </div>

        {/* Equipamentos */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-semibold">Equipamentos</h2>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>Utilização:</span>
              <span>{utilization}%</span>
            </div>
            <div className="w-full bg-gray-200 h-2 rounded-full">
              <div
                className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${utilization}%` }}
              />
            </div>
            <div className="grid grid-cols-3 gap-2 text-center mt-2">
              <Stat 
                label="Disponíveis" 
                value={equipmentCounts.available} 
                color="green" 
                tooltip={`${equipmentCounts.available} de ${equipmentCounts.total} equipamentos disponíveis`}
              />
              <Stat 
                label="Em Uso" 
                value={equipmentCounts.inUse} 
                color="yellow" 
                tooltip={`${equipmentCounts.inUse} equipamentos em uso ativo`}
              />
              <Stat 
                label="Manutenção" 
                value={equipmentCounts.maintenance} 
                color="red" 
                tooltip={`${equipmentCounts.maintenance} equipamentos em manutenção`}
              />
            </div>
            {equipmentCounts.total === 0 && (
              <div className="text-center text-gray-500 text-xs mt-2">
                Nenhum equipamento configurado
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Tickets Recentes */}
      <section className="bg-white rounded-lg shadow p-6">
        <header className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Últimos Tickets</h2>
          <span className="text-sm text-gray-500">
            {recentTickets.length} de {allTickets.length}
          </span>
        </header>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Senha</th>
                <th className="px-4 py-2 text-left">Serviços</th>
                <th className="px-4 py-2 text-left">Extras</th>
                <th className="px-4 py-2 text-left">Cliente</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Horário</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentTickets.map((t: any) => (
                <tr key={t.id} className="whitespace-nowrap">
                  <td className="px-4 py-2 font-medium">{t.number ?? '--'}</td>
                  <td className="px-4 py-2">
                    {t.services?.map((s: any) => s.service.name).join(', ') || '--'}
                  </td>
                  <td className="px-4 py-2">
                    {t.extras && t.extras.length > 0 ? (
                      <div className="relative group flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
                        </svg>
                        <span className="absolute left-1/2 -translate-x-1/2 -top-10 z-10 w-auto p-2 text-xs text-white bg-gray-800 rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                          {t.extras.map((e: any) => `${e.extra.name} (x${e.quantity})`).join(', ')}
                        </span>
                      </div>
                    ) : (
                      '--'
                    )}
                  </td>
                  <td className="px-4 py-2">{t.customer_name ?? '--'}</td>
                  <td className="px-4 py-2 capitalize">{t.status.replace('_', ' ')}</td>
                  <td className="px-4 py-2">
                    {t.completedAt || t.cancelledAt || t.createdAt
                      ? new Date(t.completedAt || t.cancelledAt || t.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
                      : '--'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, color, tooltip }: { label: string; value: number; color: string; tooltip?: string }) {
  const colorMap: Record<string, string> = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    red: 'text-red-600 bg-red-50',
    gray: 'text-gray-600 bg-gray-50',
  };
  
  const content = (
    <div className={`p-4 rounded-lg ${colorMap[color]} flex flex-col items-center gap-1`}>
      <span className="text-2xl font-bold">{value}</span>
      <span className="text-xs text-gray-700">{label}</span>
    </div>
  );

  if (tooltip) {
    return (
      <div className="relative group">
        {content}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
          {tooltip}
        </div>
      </div>
    );
  }

  return content;
} 