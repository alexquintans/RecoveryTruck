import { useEffect, useState } from 'react';
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
  const tenantId = user?.tenant_id
    || tickets[0]?.tenant_id
    || myTickets[0]?.tenant_id
    || completedTickets[0]?.tenant_id
    || cancelledTickets[0]?.tenant_id
    || '';

  // Debug logs
  console.log('🔍 Dashboard - tickets:', tickets.length);
  console.log('🔍 Dashboard - myTickets:', myTickets.length);
  console.log('🔍 Dashboard - completedTickets:', completedTickets.length);
  console.log('🔍 Dashboard - cancelledTickets:', cancelledTickets.length);
  console.log('🔍 Dashboard - cancelledTickets data:', cancelledTickets);

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

  /** Cálculos de estatísticas rápidas */
  const allTickets = [
    ...tickets,
    ...myTickets,
    ...completedTickets,
    ...cancelledTickets,
  ];
  const ticketCounts = {
    inQueue: tickets.filter((t: any) => t.status === 'in_queue').length,
    inProgress: myTickets.filter((t: any) => t.status === 'in_progress').length,
    called: myTickets.filter((t: any) => t.status === 'called').length,
    completed: completedTickets.length,
    cancelled: cancelledTickets.length,
    total: allTickets.length,
  };

  const equipmentCounts = {
    available: equipment.filter((e: any) => e.status === 'available').length,
    inUse: equipment.filter((e: any) => e.status === 'in_use').length,
    maintenance: equipment.filter((e: any) => e.status === 'maintenance').length,
    total: equipment.length,
  };

  const utilization = equipmentCounts.total
    ? Math.round((equipmentCounts.inUse / equipmentCounts.total) * 100)
    : 0;

  // Tickets recentes (últimos 5, incluindo todos os status, ordenados pelo evento mais recente)
  const recentTickets = allTickets
    .sort((a: any, b: any) => {
      const aDate = new Date(a.completedAt || a.cancelledAt || a.createdAt || 0);
      const bDate = new Date(b.completedAt || b.cancelledAt || b.createdAt || 0);
      return bDate.getTime() - aDate.getTime();
    })
    .slice(0, 5);

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
            <button
              onClick={async () => {
                if (confirm('Tem certeza que deseja encerrar a operação?')) {
                  await equipmentService.stopOperation();
                  refetchOperation();
                }
              }}
              className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Encerrar Operação
            </button>
          )}
        </div>
      </section>

      {/* Estatísticas rápidas */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tickets */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-semibold">Tickets</h2>
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <Stat label="Fila" value={ticketCounts.inQueue} color="blue" />
            <Stat
              label="Em Atendimento"
              value={ticketCounts.called + ticketCounts.inProgress}
              color="yellow"
            />
            <Stat label="Concluídos" value={ticketCounts.completed} color="green" />
            <Stat label="Cancelados" value={ticketCounts.cancelled} color="red" />
            <Stat label="Total" value={ticketCounts.total} color="gray" />
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
                className="h-2 bg-blue-600 rounded-full"
                style={{ width: `${utilization}%` }}
              />
            </div>
            <div className="grid grid-cols-3 gap-2 text-center mt-2">
              <Stat label="Disponíveis" value={equipmentCounts.available} color="green" />
              <Stat label="Em Uso" value={equipmentCounts.inUse} color="yellow" />
              <Stat label="Manutenção" value={equipmentCounts.maintenance} color="red" />
            </div>
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
                <th className="px-4 py-2 text-left">Serviço</th>
                <th className="px-4 py-2 text-left">Cliente</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Horário</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentTickets.map((t) => (
                <tr key={t.id} className="whitespace-nowrap">
                  <td className="px-4 py-2 font-medium">{t.number ?? '--'}</td>
                  <td className="px-4 py-2">
                    {t.service_name
                      || (services.find(s => String(s.id) === String(t.service_id || t.serviceId))?.name)
                      || t.service?.name
                      || t.service_id
                      || '--'}
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

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    yellow: 'text-yellow-600 bg-yellow-50',
    red: 'text-red-600 bg-red-50',
    gray: 'text-gray-600 bg-gray-50',
  };
  return (
    <div className={`p-4 rounded-lg ${colorMap[color]} flex flex-col items-center gap-1`}>
      <span className="text-2xl font-bold">{value}</span>
      <span className="text-xs text-gray-700">{label}</span>
    </div>
  );
} 