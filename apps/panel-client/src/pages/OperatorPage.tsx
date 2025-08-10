import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTicketQueue } from '../hooks/useTicketQueue';
import { useOperatorActions } from '../hooks/useOperatorActions';
import { useAuth } from '../hooks/useAuth';
import { useServiceProgress } from '../hooks/useServiceProgress';
import { useOperatorConfig } from '../hooks/useOperatorConfig';
import { useOperatorPreferences } from '../hooks/useOperatorPreferences';
import { fetchServices, fetchEquipments, fetchExtras, createService, createExtra, updateService as apiUpdateService, deleteService as apiDeleteService, updateExtra as apiUpdateExtra, deleteExtra as apiDeleteExtra, saveOperationConfig } from '../services/operatorConfigService';
// ✅ PROTEÇÃO: Importar Error Boundary
import { WebSocketErrorBoundary } from '@totem/hooks';
import { ServiceModal } from '../components/ServiceModal';
import { ExtraModal } from '../components/ExtraModal';
import { equipmentService } from '../services/equipmentService';
import { FaCogs, FaTools, FaGift, FaTicketAlt } from 'react-icons/fa';
import { EquipmentCard } from '../components/EquipmentCard';
import { MdConfirmationNumber } from 'react-icons/md';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { ServiceCountdown } from '../components/ServiceCountdown';
import { useQueryClient } from '@tanstack/react-query';

// Ícones SVG
const EditIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const DeleteIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      strokeWidth={2} 
      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
    />
  </svg>
);

const ModernDeleteIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" fill="none"/>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 9l-6 6m0-6l6 6" />
  </svg>
);

// Ícones SVG utilitários
const ServiceIcon = () => (
  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#3B82F6" /><path d="M8 12h8" stroke="white" strokeWidth="2" strokeLinecap="round" /></svg>
);
const ExtraIcon = () => (
  <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><rect x="4" y="8" width="16" height="8" rx="4" fill="#3B82F6" /><rect x="7" y="11" width="10" height="2" rx="1" fill="white" /></svg>
);
const ClockIcon = () => (
  <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="#1F526B" strokeWidth="2" /><path d="M12 7v5l3 3" stroke="#1F526B" strokeWidth="2" strokeLinecap="round" /></svg>
);
const MoneyIcon = () => (
  <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="10" rx="2" stroke="#1F526B" strokeWidth="2" /><path d="M7 12h10" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" /></svg>
);

// Tipos para os dados
interface Service {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number;
  equipment_count: number;
  isActive: boolean;
  type: string;
  color: string;
}

interface Extra {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  stock: number;
  isActive: boolean;
}

interface Equipment {
  id: string;
  name: string;
  type: string;
  count: number;
  isActive: boolean;
  serviceId: string;
}

interface ServiceProgress {
  id: string;
  ticket_service_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  duration_minutes: number;
  operator_notes?: string;
  equipment_id?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  service_name: string;
  service_price: number;
  equipment_name?: string;
}

interface Ticket {
  id: string;
  status: string;
  number?: string;
  service?: { 
    id: string;
    name: string; 
    price?: number;
    duration?: number;
  };  // Formato antigo
  services?: { 
    id: string;
    name: string; 
    price?: number;
    duration?: number;
  }[];  // Formato novo
  equipmentId?: string;
  operatorId?: string;
  createdAt?: string;
  calledAt?: string;
  priority?: string;
  customer_name?: string;
  customer?: {
    name: string;
  };
  payment_confirmed?: boolean;
  extras?: { 
    id?: string;
    name: string; 
    quantity: number;
    price?: number;
    extra?: {
      name: string;
    };
  }[]; // Adicionado para extras
  // NOVO: Progresso individual dos serviços
  serviceProgress?: ServiceProgress[];
}

// NOVO: Interface para filas por serviço
interface ServiceQueue {
  serviceId: string;
  serviceName: string;
  tickets: Ticket[];
}

// NOVO: Interface para prioridade do ticket
interface TicketPriority {
  isFirstService: boolean;
  isLastService: boolean;
  serviceOrder: number;
  totalServices: number;
}

// Dicionário de correção para nomes especiais
const nameCorrections: Record<string, string> = {
  'ofur': 'Ofurô',
  'crioterapia': 'Crioterapia',
  'bota_de_compress_o': 'Bota de Compressão',
  // Adicione outros termos se necessário
};

function formatEquipmentName(identifier: string) {
  return identifier
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => nameCorrections[word.toLowerCase()] || (word.charAt(0).toUpperCase() + word.slice(1)))
    .join(' ');
}

// Função utilitária para calcular desconto baseado na quantidade de serviços
function calculateDiscount(servicesCount: number): number {
  if (servicesCount >= 2) {
    return (servicesCount - 1) * 10; // 10 reais por serviço adicional
  }
  return 0;
}

// Função utilitária para calcular valor total com desconto
function calculateTotalWithDiscount(services: any[], extras: any[]): { subtotal: number; discount: number; total: number } {
  const servicesTotal = services.reduce((sum, s) => sum + (s.price || 0), 0);
  const extrasTotal = extras.reduce((sum, e) => sum + ((e.price || 0) * (e.quantity || 1)), 0);
  
  const subtotal = servicesTotal + extrasTotal;
  const discount = calculateDiscount(services.length);
  const total = Math.max(0, subtotal - discount);
  
  return { subtotal, discount, total };
}

// Paleta de cores da marca RecoveryTruck
const BRAND_COLORS = {
  primary: '#1F526B', // Azul Profundo da marca
  secondary: '#FFFFFF', // Branco da marca
  accent: '#D9D9D9', // Cinza Claro da marca
  text: '#000000', // Preto da marca
  success: '#3B82F6', // Azul para status ativo
  warning: '#F59E0B', // Amarelo para status de espera
  danger: '#EF4444', // Vermelho para ações perigosas
};

// Componente de Resumo Visual com cores da marca
function ResumoVisual({ servicos, equipamentos, extras, tickets }: {
  servicos: number;
  equipamentos: number;
  extras: number;
  tickets: number;
}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="flex items-center p-4 bg-white rounded-xl shadow-lg border border-accent gap-3 hover:shadow-xl transition-all">
        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
          <FaCogs className="text-primary text-2xl" />
        </div>
        <div>
          <div className="text-2xl font-bold text-primary">{servicos}</div>
          <div className="text-sm text-text/70">Serviços Ativos</div>
        </div>
      </div>
      <div className="flex items-center p-4 bg-white rounded-xl shadow-lg border border-accent gap-3 hover:shadow-xl transition-all">
        <div className="w-12 h-12 bg-success/10 rounded-full flex items-center justify-center">
          <FaTools className="text-success text-2xl" />
        </div>
        <div>
          <div className="text-2xl font-bold text-success">{equipamentos}</div>
          <div className="text-sm text-text/70">Equipamentos Disponíveis</div>
        </div>
      </div>
      <div className="flex items-center p-4 bg-white rounded-xl shadow-lg border border-accent gap-3 hover:shadow-xl transition-all">
        <div className="w-12 h-12 bg-warning/10 rounded-full flex items-center justify-center">
          <FaGift className="text-warning text-2xl" />
        </div>
        <div>
          <div className="text-2xl font-bold text-warning">{extras}</div>
          <div className="text-sm text-text/70">Extras Ativos</div>
        </div>
      </div>
      <div className="flex items-center p-4 bg-white rounded-xl shadow-lg border border-accent gap-3 hover:shadow-xl transition-all">
        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
          <FaTicketAlt className="text-primary text-2xl" />
        </div>
        <div>
          <div className="text-2xl font-bold text-primary">{tickets}</div>
          <div className="text-sm text-text/70">Tickets em Atendimento</div>
        </div>
      </div>
    </div>
  );
}

// NOVA: Função para calcular prioridade do ticket
const getTicketPriority = (ticket: Ticket, currentServiceId: string): TicketPriority => {
  const services = ticket.services || [ticket.service];
  const currentServiceIndex = services.findIndex(s => s?.id === currentServiceId);
  
  return {
    isFirstService: currentServiceIndex === 0,
    isLastService: currentServiceIndex === services.length - 1,
    serviceOrder: currentServiceIndex + 1,
    totalServices: services.length
  };
};

// NOVO: Componente TicketCard melhorado para filas por serviço
const TicketCard = ({ 
  ticket, 
  currentService, 
  onCall, 
  selectedEquipment, 
  callLoading 
}: { 
  ticket: Ticket; 
  currentService: string; 
  onCall: (ticket: Ticket, serviceId: string) => void;
  selectedEquipment: string;
  callLoading: boolean;
}) => {
  const priority = getTicketPriority(ticket, currentService);
  const services = ticket.services || [ticket.service].filter(Boolean);
  const currentServiceData = services.find(s => s?.id === currentService);
  
  // Calcular tempo de espera
  const created = ticket.createdAt ? new Date(ticket.createdAt) : null;
  const now = new Date();
  const waitingMinutes = created ? Math.floor((now.getTime() - created.getTime()) / 60000) : null;
  
  return (
    <div className={`flex items-center justify-between bg-white rounded-2xl border p-5 shadow-md hover:shadow-xl transition-transform hover:-translate-y-1 group focus-within:ring-2 focus-within:ring-blue-400 ${
      priority.isFirstService ? 'border-blue-300 bg-blue-50 ring-2 ring-blue-200' : 'border-blue-200'
    }`}>
      <div className="flex flex-col gap-1 w-full">
        <div className="flex items-center gap-3 mb-1">
          {/* Número do ticket */}
          <span className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-50 text-blue-700 text-3xl font-extrabold border-2 border-blue-200 shadow-sm">
            {ticket.number}
          </span>
          
          {/* Indicadores de múltiplos serviços - MELHORADO */}
          {services.length > 1 && (
            <div className="flex items-center gap-2">
              {/* Badge de ordem do serviço */}
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium border border-blue-200">
                {priority.serviceOrder}/{priority.totalServices}
              </span>
              {/* Badge de primeiro serviço */}
              {priority.isFirstService && (
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium border border-green-200">
                  🥇 Primeiro
                </span>
              )}
              {/* Badge de último serviço */}
              {priority.isLastService && !priority.isFirstService && (
                <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded-full text-xs font-medium border border-orange-200">
                  🏁 Último
                </span>
              )}
            </div>
          )}
          
          {/* Tempo de espera */}
          {waitingMinutes !== null && (
            <span className="ml-4 flex items-center gap-1 text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded-full">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" strokeWidth="2" />
                <path d="M12 7v5l3 3" strokeWidth="2" strokeLinecap="round" />
              </svg>
              {waitingMinutes} min
            </span>
          )}
        </div>
        
        {/* Nome do cliente */}
        <div className="text-base font-semibold text-gray-800">{ticket.customer_name || ticket.customer?.name}</div>
        
        {/* Serviço atual - MELHORADO */}
        <div className="mt-2">
          <div className="flex items-center gap-2 mb-1">
            <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" fill="#3B82F6" />
              <path d="M8 12h8" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
            <span className="text-xs font-semibold text-gray-600">SERVIÇO ATUAL:</span>
          </div>
          <span className="bg-blue-100 text-blue-700 rounded-full px-3 py-1 text-xs font-medium shadow-sm border border-blue-200">
            {currentServiceData?.name}
            {currentServiceData?.duration && (
              <span className="ml-1 text-blue-600">({currentServiceData.duration}min)</span>
            )}
            {currentServiceData?.price && (
              <span className="ml-1 text-blue-600">R$ {currentServiceData.price.toFixed(2).replace('.', ',')}</span>
            )}
          </span>
        </div>
        
        {/* Outros serviços (se houver múltiplos) - MELHORADO */}
        {services.length > 1 && (
          <div className="mt-2">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span className="text-xs font-semibold text-gray-600">TAMBÉM AGUARDA:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {services.filter(s => s?.id !== currentService).map((service, idx) => (
                <span key={service?.id || idx} className="bg-gray-100 text-gray-700 rounded-full px-3 py-1 text-xs font-medium shadow-sm border border-gray-200">
                  {service?.name}
                  {service?.duration && (
                    <span className="ml-1 text-gray-600">({service.duration}min)</span>
                  )}
                  {service?.price && (
                    <span className="ml-1 text-gray-600">R$ {service.price.toFixed(2).replace('.', ',')}</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Extras */}
        {ticket.extras && ticket.extras.length > 0 && (
          <div className="mt-2">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="4" y="8" width="16" height="8" rx="4" fill="#10B981" />
                <rect x="7" y="11" width="10" height="2" rx="1" fill="white" />
              </svg>
              <span className="text-xs font-semibold text-gray-600">EXTRAS:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {ticket.extras.map((extra, idx) => (
                <span key={extra.id || idx} className="bg-green-100 text-green-700 rounded-full px-3 py-1 text-xs font-medium shadow-sm border border-green-200">
                  {extra.name} {extra.quantity > 1 && `(${extra.quantity}x)`}
                  {extra.price && (
                    <span className="ml-1 text-green-600">R$ {extra.price.toFixed(2).replace('.', ',')}</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Horário de criação */}
        <div className="text-xs text-gray-400 mt-1">
          {ticket.createdAt && new Date(ticket.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      
      {/* Botão de chamada - MELHORADO */}
      <div className="flex gap-2 ml-6">
        <button
          disabled={callLoading || !selectedEquipment}
          onClick={() => onCall(ticket, currentService)}
          className={`px-4 py-2 rounded-lg font-semibold transition-all ${
            priority.isFirstService 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          } disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg`}
        >
          {callLoading ? 'Chamando...' : priority.isFirstService ? '🥇 Chamar Primeiro' : 'Chamar'}
        </button>
      </div>
    </div>
  );
};

// Componente para exibir progresso individual dos serviços - MOVIDO PARA FORA
const ServiceProgressCard = ({ 
  progress, 
  ticketId, 
  selectedEquipment,
  setSelectedEquipment,
  equipments,
  startServiceProgress,
  completeServiceProgress,
  cancelServiceProgress,
  fetchServiceProgress,
  getProgressStatusColor,
  getProgressStatusText
}: { 
  progress: ServiceProgress; 
  ticketId: string;
  selectedEquipment: string;
  setSelectedEquipment: (equipment: string) => void;
  equipments: Equipment[];
  startServiceProgress: (progressId: string, equipmentId?: string) => Promise<void>;
  completeServiceProgress: (progressId: string, notes?: string) => Promise<void>;
  cancelServiceProgress: (progressId: string, reason: string) => Promise<void>;
  fetchServiceProgress: (ticketId: string) => Promise<void>;
  getProgressStatusColor: (status: string) => string;
  getProgressStatusText: (status: string) => string;
}) => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [showNotesModal, setShowNotesModal] = React.useState(false);
  const [notes, setNotes] = React.useState(progress.operator_notes || '');

  const handleStartService = async () => {
    setIsLoading(true);
    try {
      await startServiceProgress(progress.id, selectedEquipment || undefined);
      // Recarregar progresso do ticket
      await fetchServiceProgress(ticketId);
    } catch (error) {
      console.error('Erro ao iniciar serviço:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteService = async () => {
    setIsLoading(true);
    try {
      await completeServiceProgress(progress.id, notes);
      // Recarregar progresso do ticket
      await fetchServiceProgress(ticketId);
      setShowNotesModal(false);
    } catch (error) {
      console.error('Erro ao completar serviço:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelService = async () => {
    const reason = prompt('Motivo do cancelamento:');
    if (reason) {
      setIsLoading(true);
      try {
        await cancelServiceProgress(progress.id, reason);
        // Recarregar progresso do ticket
        await fetchServiceProgress(ticketId);
      } catch (error) {
        console.error('Erro ao cancelar serviço:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${getProgressStatusColor(progress.status)}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-current"></div>
          <span className="font-medium text-sm">{progress.service_name}</span>
        </div>
        <span className="text-xs font-semibold">
          {getProgressStatusText(progress.status)}
        </span>
      </div>
      
      <div className="text-xs text-gray-600 mb-2">
        <div>Duração: {progress.duration_minutes} min</div>
        <div>Preço: R$ {progress.service_price.toFixed(2).replace('.', ',')}</div>
        {progress.equipment_name && (
          <div>Equipamento: {progress.equipment_name}</div>
        )}
      </div>

      {progress.operator_notes && (
        <div className="text-xs text-gray-500 mb-2">
          <strong>Observações:</strong> {progress.operator_notes}
        </div>
      )}

      <div className="flex gap-2 mt-3">
        {progress.status === 'pending' && (
          <>
            <select
              value={selectedEquipment}
              onChange={(e) => setSelectedEquipment(e.target.value)}
              className="px-2 py-1 text-xs border rounded"
            >
              <option value="">Selecionar equipamento</option>
              {equipments.filter(e => e.isActive).map(equipment => (
                <option key={equipment.id} value={equipment.id}>
                  {equipment.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleStartService}
              disabled={isLoading}
              className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {isLoading ? 'Iniciando...' : 'Iniciar'}
            </button>
          </>
        )}

        {progress.status === 'in_progress' && (
          <>
            <button
              onClick={() => setShowNotesModal(true)}
              className="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600"
            >
              Completar
            </button>
            <button
              onClick={handleCancelService}
              className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
            >
              Cancelar
            </button>
          </>
        )}

        {progress.status === 'completed' && (
          <span className="text-xs text-green-600 font-medium">
            ✅ Concluído
          </span>
        )}

        {progress.status === 'cancelled' && (
          <span className="text-xs text-red-600 font-medium">
            ❌ Cancelado
          </span>
        )}
      </div>

      {/* Modal para notas */}
      {showNotesModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Observações do Serviço</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full p-2 border rounded mb-4"
              rows={3}
              placeholder="Digite observações sobre o serviço..."
            />
            <div className="flex gap-2">
              <button
                onClick={handleCompleteService}
                disabled={isLoading}
                className="flex-1 px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                {isLoading ? 'Completando...' : 'Completar'}
              </button>
              <button
                onClick={() => setShowNotesModal(false)}
                className="flex-1 px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Componente para badge de status - MOVIDO PARA FORA
const StatusBadge = ({ status }: { status: string }) => {
  const color = status === 'in_queue' ? 'bg-blue-100 text-blue-700' :
    status === 'called' ? 'bg-yellow-100 text-yellow-700' :
    status === 'in_progress' ? 'bg-green-100 text-green-700' :
    status === 'completed' ? 'bg-gray-100 text-gray-700' :
    status === 'cancelled' ? 'bg-red-100 text-red-700' :
    'bg-gray-100 text-gray-700';
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>{status.replace('_', ' ')}</span>;
};

const OperatorPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  
  // Proteção adicional para evitar erros quando dados estão carregando
  const {
    operationConfig,
    myTickets,
    tickets,
    equipment,
    pendingPaymentTickets,
    refetch,
    refetchOperation,
    ...ticketQueueRest
  } = useTicketQueue();

  // ✅ CORREÇÃO: Memoizar arrays para evitar loops infinitos
  const safeMyTickets = useMemo(() => myTickets || [], [myTickets]);
  const safeTickets = useMemo(() => tickets || [], [tickets]);
  const safeEquipment = useMemo(() => equipment || [], [equipment]);
  const safePendingPaymentTickets = useMemo(() => pendingPaymentTickets || [], [pendingPaymentTickets]);
  const safeOperationConfig = useMemo(() => 
    operationConfig || { isOperating: false, serviceDuration: 10 }, 
    [operationConfig]
  );

  // Obter tenantId do usuário
  const tenantId = user?.tenant_id || '';

  // Obter operatorId do usuário
  const operatorId = user?.id || '';

  // TODOS OS HOOKS DEVEM SER CHAMADOS NO TOPO
  const [currentStep, setCurrentStep] = useState<string | null>(() => {
    // Tentar recuperar do localStorage
    const saved = localStorage.getItem('operator_current_step');
    return saved || null;
  });
  
  // NOVO: Hooks para persistência de configuração e preferências
  const { config: operatorConfig, saveConfig, clearConfig, updateConfigField } = useOperatorConfig();
  const { preferences, updatePreference, updateMultiplePreferences, clearPreferences } = useOperatorPreferences();
  
  // Estados com persistência melhorada
  const [operatorName, setOperatorName] = useState(() => {
    return operatorConfig?.operatorName || '';
  });
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [activeTab, setActiveTab] = useState(() => {
    return preferences.activeTab;
  });
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [services, setServices] = useState<Service[]>(() => {
    return operatorConfig?.services || [];
  });
  const [extras, setExtras] = useState<Extra[]>(() => {
    return operatorConfig?.extras || [];
  });
  const [equipments, setEquipments] = useState<Equipment[]>(() => {
    return operatorConfig?.equipments || [];
  });
  const [paymentModes, setPaymentModes] = useState<string[]>(() => {
    return operatorConfig?.paymentModes || ['none'];
  });
  const [currentPaymentModes, setCurrentPaymentModes] = useState<string[]>([]);
  const [serviceForm, setServiceForm] = useState({
    name: '',
    description: '',
    price: 0,
    duration: 10,
    equipment_count: 1,
    type: 'default',
    color: '#3B82F6'
  });
  const [extraForm, setExtraForm] = useState({
    name: '',
    description: '',
    price: 0,
    category: 'default',
    stock: 0
  });
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [editingExtra, setEditingExtra] = useState<Extra | null>(null);
  const [showServiceModal, setShowServiceModal] = useState(false);
  const [showExtraModal, setShowExtraModal] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<string>(() => {
    return preferences.selectedEquipment;
  });

  // NOVO: Estado para controle das filas por serviço com persistência
  const [activeServiceTab, setActiveServiceTab] = useState<string>(() => {
    return preferences.activeServiceTab;
  });
  const [serviceQueues, setServiceQueues] = useState<ServiceQueue[]>([]);

  // NOVO: Usar o hook para progresso dos serviços
  const {
    serviceProgress,
    loading: progressLoading,
    fetchServiceProgress,
    startServiceProgress,
    completeServiceProgress,
    cancelServiceProgress,
    getProgressStatusColor,
    getProgressStatusText
  } = useServiceProgress();

  // Usar o hook para ações do operador
  const {
    callTicket,
    callLoading,
    startService,
    startLoading,
    completeService,
    completeLoading,
    cancelTicket,
    cancelLoading,
    confirmPayment,
    confirmLoading,
    moveToQueue,
    moveToQueueLoading,
    callService
  } = useOperatorActions();

  // CORRIGIDO: Funções para persistir mudanças de estado - agora usando useCallback
  const setCurrentStepWithPersistence = useCallback((step: string | null) => {
    setCurrentStep(step);
    if (step) {
      localStorage.setItem('operator_current_step', step);
    } else {
      localStorage.removeItem('operator_current_step');
    }
  }, []);

  const setOperatorNameWithPersistence = useCallback((name: string) => {
    setOperatorName(name);
    updateConfigField('operatorName', name);
  }, [updateConfigField]);

  const setActiveTabWithPersistence = useCallback((tab: string) => {
    setActiveTab(tab);
    updatePreference('activeTab', tab);
  }, [updatePreference]);

  const setSelectedEquipmentWithPersistence = useCallback((equipmentId: string) => {
    setSelectedEquipment(equipmentId);
    updatePreference('selectedEquipment', equipmentId);
  }, [updatePreference]);

  const setActiveServiceTabWithPersistence = useCallback((serviceTab: string) => {
    setActiveServiceTab(serviceTab);
    updatePreference('activeServiceTab', serviceTab);
  }, [updatePreference]);

  const setServicesWithPersistence = useCallback((newServices: Service[]) => {
    setServices(newServices);
    updateConfigField('services', newServices);
  }, [updateConfigField]);

  const setExtrasWithPersistence = useCallback((newExtras: Extra[]) => {
    setExtras(newExtras);
    updateConfigField('extras', newExtras);
  }, [updateConfigField]);

  const setEquipmentsWithPersistence = useCallback((newEquipments: Equipment[]) => {
    setEquipments(newEquipments);
    updateConfigField('equipments', newEquipments);
  }, [updateConfigField]);

  const setPaymentModesWithPersistence = useCallback((newPaymentModes: string[]) => {
    setPaymentModes(newPaymentModes);
    updateConfigField('paymentModes', newPaymentModes);
  }, [updateConfigField]);

  // CORRIGIDO: Função para limpar o estado quando a operação for encerrada - agora usando useCallback
  const clearOperatorState = useCallback(() => {
    console.log('🔍 DEBUG - Limpando estado do operador');
    
    // Limpar localStorage
    localStorage.removeItem('operator_current_step');
    localStorage.removeItem('operator_config');
    localStorage.removeItem('operator_name');
    localStorage.removeItem('operator_selected_equipment');
    localStorage.removeItem('operator_active_tab');
    localStorage.removeItem('operator_active_service_tab');
    localStorage.removeItem('operator_preferences');
    
    // Limpar estado React diretamente para evitar dependências circulares
    setCurrentStep(null);
    setOperatorName('');
    setSelectedEquipment('');
    setActiveTab('operation');
    setActiveServiceTab('');
    
    // Limpar configuração e preferências
    if (clearConfig) clearConfig();
    if (clearPreferences) clearPreferences();
    
    // Limpar cache do React Query
    if (queryClient) queryClient.clear();
    
    console.log('🔍 DEBUG - Estado do operador limpo completamente');
  }, [clearConfig, clearPreferences, queryClient]);

  // CORRIGIDO: useEffect para carregar progresso dos serviços automaticamente
  // Problema: fetchServiceProgress estava sendo recriada a cada render
  // Solução: fetchServiceProgress já é memoizado pelo hook useServiceProgress
  useEffect(() => {
    if (currentStep === 'operation' && safeMyTickets.length > 0) {
      const loadServiceProgress = async () => {
        for (const ticket of safeMyTickets) {
          try {
            await fetchServiceProgress(ticket.id);
          } catch (error) {
            console.error('Erro ao carregar progresso do ticket:', ticket.id, error);
          }
        }
      };
      
      loadServiceProgress();
    }
  }, [safeMyTickets.length, currentStep, fetchServiceProgress]); // ✅ Usar length para evitar loop

  // CORRIGIDO: Funções utilitárias agora usam useCallback para evitar recriações
  // ✅ CORREÇÃO: Memoizar serviceProgress keys para evitar loop
  const serviceProgressKeys = useMemo(() => {
    try {
      if (!serviceProgress || typeof serviceProgress !== 'object') {
        return [];
      }
      return Object.keys(serviceProgress);
    } catch (error) {
      console.error('Erro ao memoizar serviceProgressKeys:', error);
      return [];
    }
  }, [serviceProgress]);
  
  const getTicketOverallStatus = useCallback((ticketId: string) => {
    const progress = serviceProgress[ticketId];
    if (!progress || progress.length === 0) return 'pending';
    
    const completed = progress.filter(p => p.status === 'completed').length;
    const total = progress.length;
    
    if (completed === 0) return 'pending';
    if (completed === total) return 'completed';
    return 'in_progress';
  }, [serviceProgress]); // serviceProgress vem do hook e é memoizado

  const getTicketProgressSummary = useCallback((ticketId: string) => {
    const progress = serviceProgress[ticketId];
    if (!progress || progress.length === 0) return { completed: 0, total: 0, inProgress: 0, pending: 0 };
    
    const completed = progress.filter(p => p.status === 'completed').length;
    const inProgress = progress.filter(p => p.status === 'in_progress').length;
    const pending = progress.filter(p => p.status === 'pending').length;
    const total = progress.length;
    
    return { completed, total, inProgress, pending };
  }, [serviceProgress]);

  const canCompleteTicket = useCallback((ticketId: string) => {
    const progress = serviceProgress[ticketId];
    if (!progress || progress.length === 0) return false;
    
    return progress.every(p => p.status === 'completed');
  }, [serviceProgress]);

  // CORRIGIDO: useEffect para buscar configuração de pagamento
  // Problema: Não tinha dependências corretas
  // Solução: Adicionadas dependências tenantId e currentStep
  useEffect(() => {
    if (tenantId && currentStep === 'config') {
      const fetchPaymentConfig = async () => {
        try {
          const response = await fetch(`/api/operation/config?tenant_id=${tenantId}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'X-Tenant-Id': tenantId,
            }
          });
          if (response.ok) {
            const config = await response.json();
            setCurrentPaymentModes(config.payment_modes || []);
          }
        } catch (error) {
          console.error('Erro ao buscar configuração de pagamento:', error);
        }
      };
      
      fetchPaymentConfig();
    }
  }, [tenantId, currentStep]);

  // Verificar se o modo de pagamento é "none"
  const isPaymentNone = currentPaymentModes.includes('none');
  
  // CORRIGIDO: useEffect para buscar dados da API
  useEffect(() => {
    if (tenantId) {
      const loadData = async () => {
        try {
          console.log('🔄 Carregando dados para tenant:', tenantId);
          const [servicesData, equipmentsData, extrasData] = await Promise.all([
            fetchServices({ tenant_id: tenantId }).catch(() => ({ items: [] })),
            fetchEquipments({ tenant_id: tenantId }).catch(() => ({ items: [] })),
            fetchExtras({ tenant_id: tenantId }).catch(() => ({ items: [] }))
          ]);
          
          console.log('✅ Dados carregados:', { 
            services: servicesData.items || servicesData,
            equipments: equipmentsData.items || equipmentsData,
            extras: extrasData.items || extrasData
          });
          
          setServices(servicesData.items || servicesData);
          setEquipments((equipmentsData.items || equipmentsData).map((eq: any) => ({
            id: eq.id,
            name: eq.name || eq.identifier || 'Equipamento',
            type: eq.type,
            serviceId: eq.service_id,
            count: 1,
            isActive: true,
          })));
          setExtras(extrasData.items || extrasData);
        } catch (error) {
          console.error('❌ Erro ao carregar dados:', error);
        }
      };
      
      loadData();
    }
  }, [tenantId]);

  // ✅ CORREÇÃO: Carregar dados quando operação estiver ativa
  useEffect(() => {
    if (tenantId && safeOperationConfig?.isOperating) {
      const loadOperationData = async () => {
        try {
          console.log('🔄 Carregando dados da operação ativa para tenant:', tenantId);
          const [servicesData, equipmentsData, extrasData] = await Promise.all([
            fetchServices({ tenant_id: tenantId }).catch(() => ({ items: [] })),
            fetchEquipments({ tenant_id: tenantId }).catch(() => ({ items: [] })),
            fetchExtras({ tenant_id: tenantId }).catch(() => ({ items: [] }))
          ]);
          
          console.log('✅ Dados da operação carregados:', { 
            services: servicesData.items || servicesData,
            equipments: equipmentsData.items || equipmentsData,
            extras: extrasData.items || extrasData
          });
          
          // ✅ Atualizar estados com dados da operação
          setServices(servicesData.items || servicesData);
          setEquipments((equipmentsData.items || equipmentsData).map((eq: any) => ({
            id: eq.id,
            name: eq.name || eq.identifier || 'Equipamento',
            type: eq.type,
            serviceId: eq.service_id,
            count: 1,
            isActive: true,
          })));
          setExtras(extrasData.items || extrasData);
        } catch (error) {
          console.error('❌ Erro ao carregar dados da operação:', error);
        }
      };
      
      loadOperationData();
    }
  }, [tenantId, safeOperationConfig?.isOperating]); // ← Executar quando operação ficar ativa

  // CORRIGIDO: useEffect para fechar modais
  useEffect(() => {
    if (currentStep) {
      setActiveModal(null);
      setEditingService(null);
      setEditingExtra(null);
    }
  }, [currentStep]);

  // Funções para manipular serviços
  const toggleService = async (serviceId: string, currentActive: boolean) => {
    try {
      await apiUpdateService(serviceId, { is_active: !currentActive });
      setServicesWithPersistence(prevServices =>
      prevServices.map(service =>
        service.id === serviceId
            ? { ...service, isActive: !currentActive }
          : service
      )
    );
    } catch (e) {
      alert('Erro ao atualizar serviço!');
    }
  };

  const updateServiceDuration = (serviceId: string, duration: number) => {
    setServicesWithPersistence(prevServices =>
      prevServices.map(service =>
        service.id === serviceId
          ? { ...service, duration }
          : service
      )
    );
  };

  const addService = () => {
    const newService: Service = {
      ...serviceForm,
      id: Date.now().toString()
    };
    setServicesWithPersistence(prev => [...prev, newService]);
    setServiceForm({
      name: '',
      description: '',
      price: 0,
      duration: 10,
      equipment_count: 1,
      isActive: true,
      type: '',
      color: 'blue'
    });
    setActiveModal(null);
  };

  const editService = (service: Service) => {
    setEditingService(service);
    setServiceForm(service);
    setActiveModal('service');
  };

  const updateService = async (serviceId: string, data: Partial<Service>) => {
    try {
      const updated = await apiUpdateService(serviceId, data);
      setServicesWithPersistence(prev => prev.map(s => s.id === serviceId ? { ...data, id: s.id } : s));
      setEditingService(null);
      setServiceForm({
        name: '',
        description: '',
        price: 0,
        duration: 10,
        equipment_count: 1,
        isActive: true,
        type: '',
        color: 'blue'
      });
      setActiveModal(null);
    } catch(err) {
      alert('Falha ao atualizar serviço');
    }
  };

  const deleteService = async (serviceId: string) => {
    try {
      await apiDeleteService(serviceId);
      setServicesWithPersistence(prev => prev.filter(s => s.id !== serviceId));
    } catch(err) {
      alert('Falha ao excluir serviço');
    }
  };

  // Funções para manipular extras
  const toggleExtra = (extraId: string) => {
    setExtrasWithPersistence(prevExtras =>
      prevExtras.map(extra =>
        extra.id === extraId
          ? { ...extra, isActive: !extra.isActive }
          : extra
      )
    );
  };

  const updateExtraStock = (extraId: string, stock: number) => {
    setExtrasWithPersistence(prevExtras =>
      prevExtras.map(extra =>
        extra.id === extraId
          ? { ...extra, stock }
          : extra
      )
    );
  };

  const addExtra = () => {
    const newExtra: Extra = {
      ...extraForm,
      id: Date.now().toString()
    };
    setExtrasWithPersistence(prev => [...prev, newExtra]);
    setExtraForm({
      name: '',
      description: '',
      price: 0,
      category: '',
      stock: 0,
      isActive: true
    });
    setActiveModal(null);
  };

  const editExtra = (extra: Extra) => {
    setEditingExtra(extra);
    setExtraForm(extra);
    setActiveModal('extra');
  };

  const updateExtra = async () => {
    if (!editingExtra) return;
    try {
      await apiUpdateExtra(editingExtra.id, extraForm);
      setExtras(prev => prev.map(e => e.id === editingExtra.id ? { ...extraForm, id: editingExtra.id } : e));
      setEditingExtra(null);
      setExtraForm({
        name: '',
        description: '',
        price: 0,
        category: '',
        stock: 0,
        isActive: true
      });
      setActiveModal(null);
    } catch(err) {
      alert('Falha ao atualizar item extra');
    }
  };

  const deleteExtra = async (extraId: string) => {
    try {
      await apiDeleteExtra(extraId);
      setExtras(prev => prev.filter(e => e.id !== extraId));
    } catch(err) {
      alert('Falha ao excluir item extra');
    }
  };

  // Funções para equipamentos
  const updateEquipmentCount = (equipmentId: string, count: number) => {
    setEquipmentsWithPersistence(prev =>
      prev.map(eq =>
        eq.id === equipmentId
          ? { ...eq, count: Math.max(0, count) }
          : eq
      )
    );
  };

  const toggleEquipment = (equipmentId: string) => {
    setEquipmentsWithPersistence(prev =>
      prev.map(eq =>
        eq.id === equipmentId
          ? { ...eq, isActive: !eq.isActive }
          : eq
      )
    );
  };

  // Funções para abrir modais (garantem que só um modal fica aberto)
  function openServiceModal() {
    setActiveModal('service');
  }
  function openExtraModal() {
    setActiveModal('extra');
  }
  function closeModal(){
    setActiveModal(null);
  }

  // Função para alternar modos de pagamento
  const togglePaymentMode = (mode: string) => {
    setPaymentModesWithPersistence(prev => {
      if (prev.includes(mode)) {
        return prev.filter(m => m !== mode);
      } else {
        return [...prev, mode];
      }
    });
  };

  // Funções para atualizar campos dos serviços e extras
  function updateServiceField(id: string, field: string, value: any) {
    setServicesWithPersistence(prev => prev.map(s => s.id === id ? { ...s, [field]: value } : s));
  }
  function updateExtraField(id: string, field: string, value: any) {
    setExtrasWithPersistence(prev => prev.map(x => x.id === id ? { ...x, [field]: value } : x));
  }

  // Renderizar etapa do nome
  const renderNameStep = () => (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="flex justify-between items-center p-6">
        <h1 className="text-3xl font-bold text-gray-800">Painel do Operador</h1>
        <Link to="/" className="text-blue-600 underline text-base">← Dashboard</Link>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md flex flex-col items-center animate-fade-in">
          <div className="mb-4">
            <svg className="w-12 h-12 text-blue-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" strokeWidth="2" /><path d="M6 20v-2a4 4 0 014-4h4a4 4 0 014 4v2" strokeWidth="2" /></svg>
          </div>
          <h2 className="text-xl font-semibold mb-2 text-gray-800">Identificação</h2>
          <form onSubmit={(e) => {
            e.preventDefault();
            if (operatorName.trim()) {
                              setCurrentStepWithPersistence('config');
            }
          }} className="w-full space-y-4 mt-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Operador</label>
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all text-gray-800 bg-gray-50"
                value={operatorName}
              onChange={(e) => setOperatorNameWithPersistence(e.target.value)}
                placeholder="Digite seu nome"
                required
                autoFocus
              />
            </div>
            <button 
              type="submit"
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold text-base shadow hover:bg-blue-700 active:scale-95 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" /></svg>
              Continuar
            </button>
          </form>
        </div>
      </main>
      <footer className="text-center text-xs text-gray-400 py-4">© 2025 RecoveryTruck. Todos os direitos reservados.</footer>
    </div>
  );

  // Renderizar etapa de configuração
  const renderConfigStep = () => {
    return (
      <div className="p-4 space-y-6 bg-gray-50 min-h-screen">
        <header className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Painel do Operador</h1>
          <div className="flex items-center gap-4">
                          <button
                onClick={async () => {
                  console.log('🔍 DEBUG - Iniciando processo de salvamento...');
                  console.log('🔍 DEBUG - Estado atual:', {
                    isSavingConfig,
                    currentStep,
                    operatorName,
                    tenantId,
                    operatorId
                  });
                  
                  setIsSavingConfig(true);
                  console.log('🔍 DEBUG - Iniciando salvamento da configuração...');
                  
                  // Montar o payload conforme esperado pelo backend
                  const configPayload = {
                    tenant_id: tenantId,
                    operator_id: operatorId,
                    services: services.map(s => ({
                      service_id: s.id,
                      active: !!s.isActive,
                      duration: s.duration,
                      price: s.price,
                      equipment_count: s.equipment_count,
                    })),
                    equipments: equipments.map(e => ({
                      equipment_id: e.id,
                      active: !!e.isActive,
                      quantity: e.count,
                    })),
                    extras: extras.map(x => ({
                      extra_id: x.id,
                      active: !!x.isActive,
                      stock: x.stock,
                      price: x.price,
                    })),
                    payment_modes: paymentModes,
                  };
                  
                  console.log('🔍 DEBUG - Payload da configuração:', configPayload);
                  console.log('🔍 DEBUG - Chamando saveOperationConfig...');
                  
                  try {
                    const result = await saveOperationConfig(configPayload);
                    console.log('🔍 DEBUG - Resultado do salvamento:', result);
                    
                    // Aguardar um pouco para garantir que o backend processou
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Forçar atualização do cache da operação
                    await refetchOperation();
                    
                    console.log('🔍 DEBUG - Operação atualizada, verificando status...');
                    
                    setCurrentStepWithPersistence('operation');
                    alert('Configuração salva e operação iniciada com sucesso!');
                    
                    // Aguardar um pouco antes de resetar o estado para evitar conflitos
                    setTimeout(() => {
                      setIsSavingConfig(false);
                      console.log('🔍 DEBUG - Estado isSavingConfig resetado');
                    }, 2000);
                  } catch (err) {
                    console.error('❌ ERRO ao salvar configuração:', err);
                    console.error('❌ ERRO - Stack trace:', err.stack);
                    alert('Erro ao salvar configuração da operação!');
                    setIsSavingConfig(false);
                  }
                }}
                className="px-6 py-2 bg-[#3B82F6] text-white rounded-lg font-semibold shadow-lg hover:bg-[#2563EB] active:scale-95 transition-all hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isSavingConfig}
              >
                {isSavingConfig ? 'Salvando...' : 'Salvar Configurações e Iniciar Atendimento'}
              </button>
              <Link to="/" className="text-primary underline text-base hover:text-primary/80 transition-colors">← Dashboard</Link>
          </div>
        </header>

        <div className="bg-white rounded-2xl shadow-xl max-w-5xl mx-auto p-8 animate-fade-in space-y-10">
          {/* Progress Bar */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2 text-gray-800">Configuração de Serviços e Extras</h2>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: '50%' }}></div>
            </div>
          </div>

          {/* Resumo visual no topo */}
          <ResumoVisual
            servicos={(services || []).filter(s => s.isActive).length}
            equipamentos={(equipments || []).filter(e => e.isActive).length}
            extras={(extras || []).filter(e => e.isActive).length}
            tickets={safeMyTickets.length}
          />

          {/* Serviços Disponíveis */}
          <section>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Serviços Disponíveis</h3>
              <button 
                onClick={openServiceModal}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-semibold shadow-lg hover:bg-primary/90 active:scale-95 transition-all hover:shadow-xl"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                Adicionar Serviço
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.map((service) => (
                <div 
                  key={service.id}
                  className={`transition-all duration-200 border-2 rounded-2xl p-5 flex flex-col gap-3 shadow-lg bg-white hover:shadow-xl
                    ${service.isActive ? 'border-2 border-[#3B82F6] bg-[#F0F8FF]' : 'border-[#D9D9D9] bg-[#FAFAFA]'}
                  `}
                  style={{ boxShadow: service.isActive ? '0 4px 20px 0 rgba(59, 130, 246, 0.25)' : '0 2px 12px 0 rgba(0, 0, 0, 0.08)' }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <ServiceIcon />
                    <div className="flex-1">
                      <input
                        type="text"
                        value={service.name}
                        onChange={e => updateServiceField(service.id, 'name', e.target.value)}
                        className="text-xl font-bold text-[#1F526B] bg-transparent border-b border-[#3B82F6] focus:outline-none focus:border-[#1F526B] transition-all w-full"
                      />
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${service.isActive ? 'bg-[#3B82F6] text-white' : 'bg-[#D9D9D9] text-[#666666]'}`}>{service.isActive ? 'Ativo' : 'Inativo'}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteService(service.id)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-full transition-all duration-200 group"
                      title="Excluir serviço"
                    >
                      <ModernDeleteIcon />
                    </button>
                  </div>
                  <div className="flex gap-4 mt-2">
                    <span className="flex items-center gap-1 text-sm text-[#1F526B]">
                      <ClockIcon />
                      <input
                        type="number"
                        min={1}
                        value={service.duration}
                        onChange={e => updateServiceField(service.id, 'duration', Number(e.target.value))}
                        className="w-14 text-center border border-[#D9D9D9] rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-[#3B82F6] transition-all bg-white"
                      /> min
                    </span>
                    <span className="flex items-center gap-1 text-sm text-[#1F526B]">
                      <MoneyIcon />
                      <input
                        type="number"
                        min={0}
                        step={0.01}
                        value={service.price}
                        onChange={e => updateServiceField(service.id, 'price', Number(e.target.value))}
                        className="w-16 text-center border border-[#D9D9D9] rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-[#3B82F6] transition-all bg-white"
                      />
                    </span>
                    </div>
                  <label className="flex items-center gap-2 mt-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={service.isActive}
                      onChange={() => toggleService(service.id, service.isActive)}
                      className="sr-only"
                      />
                    <div className={`w-11 h-6 rounded-full transition-colors duration-200 ${service.isActive ? 'bg-[#3B82F6]' : 'bg-[#D9D9D9]'}`}></div>
                    <div className={`absolute ml-1 mt-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${service.isActive ? 'translate-x-5' : ''}`}></div>
                    <span className="text-sm text-[#1F526B] font-medium">Ativar/Desativar</span>
                    </label>
                </div>
              ))}
            </div>
          </section>

          {/* Equipamentos Disponíveis */}
          <section>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Equipamentos Disponíveis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {equipments
                .filter(equipment =>
                  services.filter(s => s.isActive).map(s => String(s.id)).includes(String(equipment.serviceId))
                )
                .map((equipment) => (
                <div 
                  key={equipment.id}
                    className={`transition-all duration-200 border-2 rounded-2xl p-5 flex flex-col gap-3 shadow-lg bg-white hover:shadow-xl
                      ${equipment.isActive ? 'border-2 border-[#3B82F6] bg-[#F0F8FF]' : 'border-[#D9D9D9] bg-[#FAFAFA]'}
                    `}
                    style={{ boxShadow: equipment.isActive ? '0 4px 20px 0 rgba(59, 130, 246, 0.25)' : '0 2px 12px 0 rgba(0, 0, 0, 0.08)' }}
                >
                  <div className="flex items-center gap-3 mb-2">
                      {/* Ícone estilizado */}
                      <div className="w-10 h-10 flex items-center justify-center rounded-full bg-[#1F526B]">
                        <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
                          <rect x="4" y="8" width="16" height="8" rx="4" fill="#3B82F6" />
                          <rect x="7" y="11" width="10" height="2" rx="1" fill="white" />
                        </svg>
                      </div>
                    <div>
                        <span className="text-xl font-bold text-[#1F526B]">{formatEquipmentName(equipment.name)}</span>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs font-semibold px-3 py-1 rounded-full ${equipment.isActive ? 'bg-[#3B82F6] text-white' : 'bg-[#D9D9D9] text-[#666666]'}`}>{equipment.isActive ? 'Disponível' : 'Indisponível'}</span>
                    </div>
                  </div>
                    </div>
                    <label className="flex items-center gap-2 mt-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={equipment.isActive}
                        onChange={() => {
                          setEquipments(prev => prev.map(eq => eq.id === equipment.id ? { ...eq, isActive: !eq.isActive } : eq));
                        }}
                        className="sr-only"
                      />
                      <div className={`w-11 h-6 rounded-full transition-colors duration-200 ${equipment.isActive ? 'bg-[#3B82F6]' : 'bg-[#D9D9D9]'}`}></div>
                      <div className={`absolute ml-1 mt-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${equipment.isActive ? 'translate-x-5' : ''}`}></div>
                      <span className="text-sm text-[#1F526B] font-medium">Ativar/Desativar</span>
                    </label>
                </div>
              ))}
            </div>
          </section>

          {/* Itens Extras Disponíveis */}
          <section>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Itens Extras Disponíveis</h3>
              <button 
                onClick={openExtraModal}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-semibold shadow-lg hover:bg-primary/90 active:scale-95 transition-all hover:shadow-xl"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                Adicionar Item Extra
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {extras.map((extra) => (
                <div 
                  key={extra.id}
                  className={`transition-all duration-200 border-2 rounded-2xl p-5 flex flex-col gap-3 shadow-lg bg-white hover:shadow-xl
                    ${extra.isActive ? 'border-2 border-[#3B82F6] bg-[#F0F8FF]' : 'border-[#D9D9D9] bg-[#FAFAFA]'}
                  `}
                  style={{ boxShadow: extra.isActive ? '0 4px 20px 0 rgba(59, 130, 246, 0.25)' : '0 2px 12px 0 rgba(0, 0, 0, 0.08)' }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <ExtraIcon />
                    <div className="flex-1">
                      <input
                        type="text"
                        value={extra.name}
                        onChange={e => updateExtraField(extra.id, 'name', e.target.value)}
                        className="text-xl font-bold text-[#1F526B] bg-transparent border-b border-[#3B82F6] focus:outline-none focus:border-[#1F526B] transition-all w-full"
                      />
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${extra.isActive ? 'bg-[#3B82F6] text-white' : 'bg-[#D9D9D9] text-[#666666]'}`}>{extra.isActive ? 'Ativo' : 'Inativo'}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteExtra(extra.id)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-full transition-all duration-200 group"
                      title="Excluir item extra"
                    >
                      <ModernDeleteIcon />
                    </button>
                  </div>
                  <div className="flex gap-4 mt-2">
                    <span className="flex items-center gap-1 text-sm text-[#1F526B]">
                      <MoneyIcon />
                      <input
                        type="number"
                        min={0}
                        step={0.01}
                        value={extra.price}
                        onChange={e => updateExtraField(extra.id, 'price', Number(e.target.value))}
                        className="w-16 text-center border border-[#D9D9D9] rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-[#3B82F6] transition-all bg-white"
                      />
                    </span>
                    <span className="flex items-center gap-1 text-sm text-[#1F526B]">
                      Estoque:
                      <input
                        type="number"
                        min={0}
                        value={extra.stock}
                        onChange={e => updateExtraField(extra.id, 'stock', Number(e.target.value))}
                        className="w-14 text-center border border-[#D9D9D9] rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:border-[#3B82F6] transition-all bg-white"
                      />
                    </span>
                  </div>
                  <label className="flex items-center gap-2 mt-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={extra.isActive}
                        onChange={() => toggleExtra(extra.id)}
                      className="sr-only"
                      />
                    <div className={`w-11 h-6 rounded-full transition-colors duration-200 ${extra.isActive ? 'bg-[#3B82F6]' : 'bg-[#D9D9D9]'}`}></div>
                    <div className={`absolute ml-1 mt-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${extra.isActive ? 'translate-x-5' : ''}`}></div>
                    <span className="text-sm text-[#1F526B] font-medium">Ativar/Desativar</span>
                    </label>
                </div>
              ))}
            </div>
          </section>

          {/* Métodos de Pagamento */}
          <section>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Métodos de Pagamento</h3>
            <div className="flex flex-col md:flex-row gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={paymentModes.includes('none')}
                  onChange={() => togglePaymentMode('none')}
                  className="w-5 h-5 text-primary bg-gray-100 border-gray-300 rounded"
                />
                Nenhum (Gerenciamento de Tickets)
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={paymentModes.includes('mercadopago')}
                  onChange={() => togglePaymentMode('mercadopago')}
                  disabled={paymentModes.includes('none')}
                  className="w-5 h-5 text-primary bg-gray-100 border-gray-300 rounded"
                />
                Mercado&nbsp;Pago
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={paymentModes.includes('sicredi')}
                  onChange={() => togglePaymentMode('sicredi')}
                  disabled={paymentModes.includes('none')}
                  className="w-5 h-5 text-primary bg-gray-100 border-gray-300 rounded"
                />
                Sicredi (Maquininha)
              </label>
            </div>
          </section>

          {/* Botões de ação */}
          <div className="flex justify-between pt-8 border-t mt-8">
            <button 
              onClick={() => setCurrentStepWithPersistence('name')}
              className="px-6 py-2 border border-accent text-text rounded-lg bg-white hover:bg-accent/50 transition-all font-semibold hover:shadow-md"
            >
              Voltar
            </button>
            <button 
              onClick={async () => {
                console.log('🔍 DEBUG - Iniciando processo de salvamento...');
                console.log('🔍 DEBUG - Estado atual:', {
                  isSavingConfig,
                  currentStep,
                  operatorName,
                  tenantId,
                  operatorId
                });
                
                setIsSavingConfig(true);
                console.log('🔍 DEBUG - Iniciando salvamento da configuração...');
                
                // Montar o payload conforme esperado pelo backend
                const configPayload = {
                  tenant_id: tenantId,
                  operator_id: operatorId,
                  services: services.map(s => ({
                    service_id: s.id,
                    active: !!s.isActive,
                    duration: s.duration,
                    price: s.price,
                    equipment_count: s.equipment_count,
                  })),
                  equipments: equipments.map(e => ({
                    equipment_id: e.id,
                    active: !!e.isActive,
                    quantity: e.count,
                  })),
                  extras: extras.map(x => ({
                    extra_id: x.id,
                    active: !!x.isActive,
                    stock: x.stock,
                    price: x.price,
                  })),
                  payment_modes: paymentModes,
                };
                
                console.log('🔍 DEBUG - Payload da configuração:', configPayload);
                console.log('🔍 DEBUG - Chamando saveOperationConfig...');
                
                try {
                  const result = await saveOperationConfig(configPayload);
                  console.log('🔍 DEBUG - Resultado do salvamento:', result);
                  
                  // Aguardar um pouco para garantir que o backend processou
                  await new Promise(resolve => setTimeout(resolve, 1000));
                  
                  // Forçar atualização do cache da operação
                  await refetchOperation();
                  
                  console.log('🔍 DEBUG - Operação atualizada, verificando status...');
                  
                  setCurrentStepWithPersistence('operation');
                  alert('Configuração salva e operação iniciada com sucesso!');
                  
                  // Aguardar um pouco antes de resetar o estado para evitar conflitos
                  setTimeout(() => {
                    setIsSavingConfig(false);
                    console.log('🔍 DEBUG - Estado isSavingConfig resetado');
                  }, 2000);
                } catch (err) {
                  console.error('❌ ERRO ao salvar configuração:', err);
                  console.error('❌ ERRO - Stack trace:', err.stack);
                  alert('Erro ao salvar configuração da operação!');
                  setIsSavingConfig(false);
                }
              }}
              className="px-6 py-2 bg-[#3B82F6] text-white rounded-lg font-semibold shadow-lg hover:bg-[#2563EB] active:scale-95 transition-all hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSavingConfig}
            >
              {isSavingConfig ? 'Salvando...' : 'Salvar Configurações e Iniciar Atendimento'}
            </button>
          </div>

          <ServiceModal
            isOpen={activeModal==='service'}
            onClose={closeModal}
            initialData={editingService || undefined}
            onSubmit={async (data)=>{
              
              
              if(editingService){
                try {
                  await updateService(editingService.id, { ...data, equipment_count: data.equipment_count });
                  setServices(prev=>prev.map(s=>s.id===editingService.id?{...data,id:editingService.id}:s));
                  setEditingService(null);
                } catch(err){
                  console.error('Erro ao atualizar serviço:', err);
                  alert('Falha ao atualizar serviço');
                }
              }else{
                try {
                  if (!tenantId) {
                    throw new Error('tenantId não encontrado');
                  }
                  const created = await createService(data, { tenant_id: tenantId });
                  setServices(prev=>[...prev, created]);
                  // Recarregar equipamentos, pois podem ter sido criados automaticamente
                  try {
                    const eqData = await fetchEquipments({ tenant_id: tenantId });
                    setEquipments((eqData.items || eqData).map((eq: any)=>({
                                              id: eq.id,
                        name: eq.name || eq.identifier,
                      type: eq.type,
                      serviceId: eq.service_id,
                      count: 1,
                      isActive: true,
                    })));
                  }catch{}
                } catch(err){
                  console.error('Erro ao criar serviço:', err);
                  alert('Falha ao criar serviço');
                }
              }
            }}
          />
          <ExtraModal
            isOpen={activeModal==='extra'}
            onClose={closeModal}
            initialData={editingExtra || undefined}
            onSubmit={async (data)=>{

              
              if(editingExtra){
                try {
                  await updateExtra();
                  setExtras(prev=>prev.map(e=>e.id===editingExtra.id?{...data,id:editingExtra.id}:e));
                  setEditingExtra(null);
                } catch(err){
                  console.error('Erro ao atualizar extra:', err);
                  alert('Falha ao atualizar item extra');
                }
              }else{
                try {
                  if (!tenantId) {
                    throw new Error('tenantId não encontrado');
                  }
                  const created = await createExtra(data, { tenant_id: tenantId });
                  setExtras(prev=>[...prev, created]);
                } catch(err){
                  console.error('Erro ao criar extra:', err);
                  alert('Falha ao criar item extra');
                }
              }
            }}
          />
        </div>
      </div>
    );
  };

  // Renderizar etapa de operação
  const renderOperationStep = () => {


    const queuedTickets = tickets.filter(ticket => ticket.status === 'in_queue');
    // Usar myTickets diretamente do hook ao invés de filtrar manualmente
    // const myTickets = tickets.filter(ticket => 
    //   (ticket.status === 'called' || ticket.status === 'in_progress') && 
    //   ticket.operatorId === operatorId
    // );

    // Gerar equipamentos baseado na configuração
    const availableEquipments = (equipments || [])
      .filter(eq => eq.isActive && eq.count > 0)
      .map(eq => ({
        id: eq.id,
        name: eq.name,
        type: eq.type,
        status: 'available',
      }));

    // Ícones de equipamentos
    const equipmentIcons: Record<string, JSX.Element> = {
      banheira_gelo: (
        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="10" width="18" height="7" rx="3" strokeWidth="2" /><path d="M5 17v1a2 2 0 002 2h10a2 2 0 002-2v-1" strokeWidth="2" /></svg>
      ),
      bota_compressao: (
        <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="12" height="16" rx="6" strokeWidth="2" /><path d="M12 20v-4" strokeWidth="2" /></svg>
      ),
      massagem: (
        <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" strokeWidth="2" /><rect x="6" y="14" width="12" height="6" rx="3" strokeWidth="2" /></svg>
      ),
      ufuro: (
        <svg className="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="8" ry="5" strokeWidth="2" /><path d="M4 12c0 2.5 3.6 5 8 5s8-2.5 8-5" strokeWidth="2" /></svg>
      ),
    };

    // CORRIGIDO: Função para organizar tickets por serviço - definida como função normal
    const organizeTicketsByService = (tickets: Ticket[], activeServices: Service[]) => {
      // Proteção contra dados undefined/null
      if (!tickets || !Array.isArray(tickets)) {
        console.warn('organizeTicketsByService: tickets não é um array válido:', tickets);
        return [];
      }
      
      if (!activeServices || !Array.isArray(activeServices)) {
        console.warn('organizeTicketsByService: activeServices não é um array válido:', activeServices);
        return [];
      }
      
      // Filtrar apenas tickets que estão na fila (in_queue), excluindo pending_payment
      const queueTickets = tickets.filter(ticket => {
        if (!ticket || typeof ticket !== 'object') return false;
        return ticket.status === 'in_queue';
      });
      
      return activeServices.map(service => {
        if (!service || !service.id) {
          console.warn('organizeTicketsByService: serviço inválido:', service);
          return { serviceId: '', serviceName: '', tickets: [] };
        }
        
        return {
          serviceId: service.id,
          serviceName: service.name || '',
          tickets: queueTickets.filter(ticket => {
            if (!ticket) return false;
            
            // Verificar se o ticket tem serviços
            const ticketServices = ticket.services || (ticket.service ? [ticket.service] : []);
            
            return ticketServices.some(s => s && s.id === service.id);
          })
        };
      });
    };

    // Função getTicketPriority já definida no escopo global, removendo duplicata

    // CORRIGIDO: Função para obter tickets de um serviço específico - definida como função normal
    const getTicketsForService = (serviceId: string) => {
      const queue = serviceQueues.find(q => q.serviceId === serviceId);
      return queue?.tickets || [];
    };

    // CORRIGIDO: Função de chamada inteligente - MELHORADA conforme NewTickets.md
    const handleCallTicket = async (ticket: Ticket, serviceId: string) => {
      console.log('🔍 DEBUG - Chamando ticket:', ticket.id, 'com equipamento:', selectedEquipment);
      console.log('🔍 DEBUG - Status do ticket:', ticket.status);
      
      // Verificar se o ticket já foi chamado
      if (ticket.status === 'called') {
        console.log('🔍 DEBUG - Ticket já foi chamado, pulando...');
        alert('Este ticket já foi chamado!');
        return;
      }
      
      // Verificar se o ticket está na fila (apenas in_queue, não pending_payment)
      if (ticket.status !== 'in_queue') {
        console.log('🔍 DEBUG - Ticket não está na fila, pulando...');
        alert('Este ticket não está na fila!');
        return;
      }
      
      // Verificar se é o primeiro serviço do ticket
      const services = ticket.services || [ticket.service];
      const isFirstService = services[0]?.id === serviceId;
      
      try {
        if (isFirstService) {
          // Chamar o ticket completo (primeiro serviço)
          console.log('🔍 DEBUG - Chamando ticket completo (primeiro serviço)');
          await callTicket(ticket.id, selectedEquipment);
        } else {
          // Chamar apenas o serviço específico (não é o primeiro)
          console.log('🔍 DEBUG - Chamando serviço específico:', serviceId);
          await callService(ticket.id, serviceId, selectedEquipment);
        }
        
        // Mostrar feedback visual
        const serviceName = services.find(s => s.id === serviceId)?.name || 'Serviço';
        const message = isFirstService 
          ? `Ticket #${ticket.number} chamado para ${serviceName} (primeiro serviço)`
          : `Ticket #${ticket.number} chamado para ${serviceName}`;
        
        // TODO: Implementar notificação toast
        console.log('✅', message);
        
      } catch (error) {
        console.error('❌ ERRO ao chamar ticket:', error);
        alert('Erro ao chamar ticket! Verifique se o equipamento está selecionado.');
      }
    };

    // CORRIGIDO: Efeito para organizar filas quando tickets ou serviços mudam
    // Problema: Dependências estavam causando loops infinitos
    // Solução: Memoizar as dependências e usar useCallback
    const activeServices = useMemo(() => {
      try {
        if (!services || !Array.isArray(services)) {
          console.warn('activeServices useMemo: services não é um array válido:', services);
          return [];
        }
        return services.filter(s => s && s.isActive);
      } catch (error) {
        console.error('Erro no activeServices useMemo:', error);
        return [];
      }
    }, [services]);
    
    const organizedQueues = useMemo(() => {
      try {
        if (!safeTickets || !Array.isArray(safeTickets) || !activeServices || !Array.isArray(activeServices)) {
          console.warn('organizedQueues useMemo: dados inválidos:', { safeTickets, activeServices });
          return [];
        }
        return organizeTicketsByService(safeTickets, activeServices);
      } catch (error) {
        console.error('organizedQueues useMemo: erro ao organizar filas:', error);
        return [];
      }
    }, [safeTickets, activeServices]);
    
    useEffect(() => {
      if (currentStep === 'operation') {
        try {
          // Verificar se organizedQueues é válido
          if (!organizedQueues || !Array.isArray(organizedQueues)) {
            console.warn('useEffect: organizedQueues não é válido:', organizedQueues);
            setServiceQueues([]);
            return;
          }
          
          setServiceQueues(organizedQueues);
          
          // Definir primeira fila como ativa se não houver uma ativa
          if (organizedQueues.length > 0 && !activeServiceTab) {
            const firstQueue = organizedQueues[0];
            if (firstQueue && firstQueue.serviceId) {
              setActiveServiceTab(firstQueue.serviceId);
              // Usar try-catch para evitar erros
              try {
                if (typeof updatePreference === 'function') {
                  updatePreference('activeServiceTab', firstQueue.serviceId);
                }
              } catch (error) {
                console.error('Erro ao atualizar preferência:', error);
              }
            }
          }
        } catch (error) {
          console.error('Erro no useEffect de organizar filas:', error);
          setServiceQueues([]);
        }
      }
    }, [organizedQueues, currentStep, activeServiceTab, updatePreference]);

    return (
      <div className="p-4 space-y-8 max-w-6xl mx-auto">
        {/* Cabeçalho moderno */}
        <header className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-2">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold">Painel do Operador</h1>
            <span className="text-gray-500 text-base hidden md:inline">|</span>
            <span className="text-base text-gray-700 font-medium">Operador: <span className="font-semibold text-blue-700">{operatorName}</span></span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={async () => {
                if (confirm('Tem certeza que deseja encerrar a operação?')) {
                  try {
                    await equipmentService.stopOperation();
                    alert('Operação encerrada com sucesso!');
                    
                    // ✅ CORREÇÃO: Usar timeout para evitar conflitos de renderização
                    setTimeout(() => {
                      try {
                        clearOperatorState();
                        navigate('/');
                      } catch (error) {
                        console.error('Erro ao limpar estado:', error);
                        // Fallback: apenas navegar
                        navigate('/');
                      }
                    }, 100);
                  } catch (e) {
                    console.error('Erro ao encerrar operação:', e);
                    alert('Falha ao encerrar operação no backend!');
                  }
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg shadow hover:bg-red-700 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              Finalizar e Sair
            </button>
            <Link to="/" className="text-blue-600 underline text-base">← Dashboard</Link>
          </div>
        </header>
        {/* Resumo visual */}
        <div className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold mb-2">Resumo Visual</h2>
            <button
              onClick={refetch}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              🔄 Atualizar
            </button>
          </div>
        <ResumoVisual
          servicos={(services || []).filter(s => s.isActive).length}
          equipamentos={(equipments || []).filter(e => e.isActive).length}
          extras={(extras || []).filter(e => e.isActive).length}
          tickets={safeMyTickets.length}
        />
        </div>
        {/* Seleção de Equipamentos */}
        <section className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
          <h2 className="text-xl font-semibold mb-2">Selecione um Equipamento</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {availableEquipments.map((equipment) => (
              <EquipmentCard
                key={equipment.id}
                equipamento={equipment}
                selecionado={selectedEquipment === equipment.id}
                onClick={() => setSelectedEquipment(equipment.id)}
              />
            ))}
          </div>
        </section>

        {/* Fila e Meus Tickets */}
        <div className="grid gap-6">
          {/* NOVO: Filas por Serviço */}
          <section className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold mb-2">Filas por Serviço</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                    queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                  }}
                  className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all duration-200 group"
                  title="Atualizar fila"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Tabs dos Serviços - MELHORADO */}
            {serviceQueues.length > 0 ? (
              <div className="service-queues">
                <div className="queue-tabs flex flex-wrap gap-2 mb-6 bg-gray-50 p-4 rounded-xl">
                  {serviceQueues.map(service => (
                    <button 
                      key={service.serviceId}
                      className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 ${
                        activeServiceTab === service.serviceId 
                          ? 'bg-blue-600 text-white shadow-lg transform scale-105' 
                          : 'bg-white text-gray-700 hover:bg-gray-100 shadow-md hover:shadow-lg'
                      }`}
                      onClick={() => {
                        setActiveServiceTab(service.serviceId);
                        try {
                          updatePreference('activeServiceTab', service.serviceId);
                        } catch (error) {
                          console.error('Erro ao atualizar preferência:', error);
                        }
                      }}
                    >
                      <span className="font-semibold">{service.serviceName}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                        activeServiceTab === service.serviceId 
                          ? 'bg-white bg-opacity-20 text-white' 
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {service.tickets.length}
                      </span>
                    </button>
                  ))}
                </div>
                
                {/* Conteúdo da fila ativa - MELHORADO */}
                <div className="queue-content">
                  {(() => {
                    const activeQueue = serviceQueues.find(q => q.serviceId === activeServiceTab);
                    const activeTickets = activeQueue?.tickets || [];
                    
                    return activeTickets.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-12 text-gray-400 bg-gray-50 rounded-xl">
                        <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <circle cx="12" cy="12" r="10" strokeWidth="2" />
                          <path d="M8 12h4l3 6" strokeWidth="2" />
                        </svg>
                        <span className="text-lg font-medium">Nenhum ticket na fila de {activeQueue?.serviceName}</span>
                        <span className="text-sm text-gray-400 mt-1">Os tickets aparecerão aqui quando chegarem</span>
                      </div>
                    ) : (
                      <div className="flex flex-col gap-4">
                        {/* Header da fila */}
                        <div className="flex items-center justify-between bg-blue-50 p-4 rounded-xl border border-blue-200">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-white font-bold text-sm">{activeTickets.length}</span>
                            </div>
                            <div>
                              <h3 className="font-semibold text-blue-900">{activeQueue?.serviceName}</h3>
                              <p className="text-sm text-blue-600">
                                {activeTickets.length === 1 ? '1 ticket na fila' : `${activeTickets.length} tickets na fila`}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-blue-600">Tempo estimado</div>
                            <div className="font-semibold text-blue-900">
                              {activeTickets.reduce((total, ticket) => {
                                const service = ticket.services?.find(s => s.id === activeServiceTab) || ticket.service;
                                return total + (service?.duration || 0);
                              }, 0)} min
                            </div>
                          </div>
                        </div>
                        
                        {/* Lista de tickets */}
                        <div className="space-y-4">
                          {activeTickets.map((ticket) => (
                            <TicketCard 
                              key={ticket.id}
                              ticket={ticket}
                              currentService={activeServiceTab}
                              onCall={handleCallTicket}
                              selectedEquipment={selectedEquipment}
                              callLoading={callLoading}
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400 bg-gray-50 rounded-xl">
                <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" strokeWidth="2" />
                  <path d="M8 12h4l3 6" strokeWidth="2" />
                </svg>
                <span className="text-lg font-medium">Nenhum serviço ativo</span>
                <span className="text-sm text-gray-400 mt-1">Ative pelo menos um serviço para ver as filas</span>
              </div>
            )}
          </section>

          {/* Meus Tickets */}
          <section className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
            <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold mb-2">Meus Tickets</h2>
              <button
                onClick={() => {
                  queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                }}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
              >
                🔄
              </button>
            </div>
            {safeMyTickets.length === 0 ? (
              <div className="text-gray-400 text-center py-8">Nenhum ticket em atendimento</div>
            ) : (
              safeMyTickets.map(ticket => {
                console.log('Ticket em andamento:', ticket);
                return (
                  <div
                    key={ticket.id}
                    className={`flex flex-col md:flex-row md:items-center justify-between rounded-2xl p-4 md:p-5 shadow-md hover:shadow-xl transition-transform hover:-translate-y-1 group focus-within:ring-2 focus-within:ring-yellow-400
                      ${ticket.status === 'called'
                        ? 'bg-white border border-yellow-200'
                        : ticket.status === 'in_progress'
                          ? 'bg-green-50 border-2 border-green-400'
                          : 'bg-white border border-gray-200 opacity-60'
                      }
                    `}
                    tabIndex={0}
                    aria-label={`Ticket ${ticket.number}`}
                  >
                    <div className="flex flex-row md:flex-col items-center gap-4 md:gap-2 w-full md:w-auto mb-2 md:mb-0">
                      <div className="flex flex-col items-center">
                        <span className={`text-xl md:text-2xl font-bold flex items-center gap-1
                          ${ticket.status === 'in_progress' ? 'text-green-700' : 'text-yellow-600'}`}
                        >
                          <MdConfirmationNumber className="inline text-2xl md:text-3xl" />
                          {ticket.number}
                        </span>
                        <span className={`text-xs font-bold px-2 py-1 rounded-full mt-1
                          ${ticket.status === 'in_progress' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'}`}
                        >
                          {ticket.status === 'in_progress' ? 'Em andamento' : 'Aguardando'}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 flex flex-col gap-1 md:gap-2 w-full">
                      <div className="font-semibold text-base md:text-lg text-gray-800 break-words">{ticket.customer_name}</div>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {ticket.services?.map((s, idx) => (
                          <span key={s.id || idx} className="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full text-xs font-medium">
                            {s.service?.name || s.name || 'Serviço'}
                          </span>
                        ))}
                      </div>
                      {/* Chips de extras */}
                      {ticket.extras && ticket.extras.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {ticket.extras.map((extra, idx) => (
                            <span key={extra.id || idx} className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-medium">
                              {extra.extra?.name || extra.name || 'Extra'} {extra.quantity > 1 && `(${extra.quantity}x)`}
                            </span>
                          ))}
                        </div>
                      )}
                      {/* Cálculo do valor total com desconto */}
                      {ticket.services && ticket.extras && (
                        <div className="mt-2 p-2 bg-blue-50 rounded-lg">
                          <div className="text-sm font-semibold text-blue-800 mb-1">Valor Total:</div>
                                                      <div className="text-xs text-blue-600">
                              {(() => {
                                const { subtotal, discount, total } = calculateTotalWithDiscount(ticket.services, ticket.extras);
                                
                                return (
                                  <div>
                                    <div>Subtotal: R$ {subtotal.toFixed(2).replace('.', ',')}</div>
                                    {discount > 0 && (
                                      <div className="text-green-600">Desconto: -R$ {discount.toFixed(2).replace('.', ',')}</div>
                                    )}
                                    <div className="font-semibold">Total: R$ {total.toFixed(2).replace('.', ',')}</div>
                                  </div>
                                );
                              })()}
                          </div>
                        </div>
                      )}

                      {/* NOVO: Seção de Progresso Individual dos Serviços */}
                      <div className="w-full mt-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-sm font-semibold text-gray-700">Progresso dos Serviços</h4>
                          <button
                            onClick={() => fetchServiceProgress(ticket.id)}
                            className="text-xs text-blue-600 hover:text-blue-800 underline"
                          >
                            Atualizar
                          </button>
                        </div>
                        
                        {/* Resumo do progresso */}
                        {(() => {
                          const summary = getTicketProgressSummary(ticket.id);
                          const overallStatus = getTicketOverallStatus(ticket.id);
                          
                          return (
                            <div className="mb-3 p-2 bg-gray-50 rounded-lg">
                              <div className="flex items-center justify-between text-xs">
                                <span className="font-medium">Progresso Geral:</span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  overallStatus === 'completed' ? 'bg-green-100 text-green-700' :
                                  overallStatus === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                                  overallStatus === 'cancelled' ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {overallStatus === 'completed' ? 'Concluído' :
                                   overallStatus === 'in_progress' ? 'Em Andamento' :
                                   overallStatus === 'cancelled' ? 'Cancelado' :
                                   'Pendente'}
                                </span>
                              </div>
                              <div className="flex gap-2 mt-1 text-xs text-gray-600">
                                <span>Total: {summary.total}</span>
                                <span className="text-green-600">✓ {summary.completed}</span>
                                <span className="text-blue-600">⟳ {summary.inProgress}</span>
                                <span className="text-gray-600">⏳ {summary.pending}</span>
                              </div>
                            </div>
                          );
                        })()}
                        
                        {/* Resumo visual do progresso */}
                        {(() => {
                          const summary = getTicketProgressSummary(ticket.id);
                          const overallStatus = getTicketOverallStatus(ticket.id);
                          
                          return (
                            <div className="mb-3 p-2 bg-gray-50 rounded-lg">
                              <div className="flex items-center justify-between text-xs">
                                <span className="font-medium">Progresso Geral:</span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  overallStatus === 'completed' ? 'bg-green-100 text-green-700' :
                                  overallStatus === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                                  overallStatus === 'cancelled' ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {overallStatus === 'completed' ? 'Concluído' :
                                   overallStatus === 'in_progress' ? 'Em Andamento' :
                                   overallStatus === 'cancelled' ? 'Cancelado' :
                                   'Pendente'}
                                </span>
                              </div>
                              <div className="flex gap-2 mt-1 text-xs text-gray-600">
                                <span>Total: {summary.total}</span>
                                <span className="text-green-600">✓ {summary.completed}</span>
                                <span className="text-blue-600">⟳ {summary.inProgress}</span>
                                <span className="text-gray-600">⏳ {summary.pending}</span>
                              </div>
                            </div>
                          );
                        })()}
                        
                        {/* Carregar progresso dos serviços */}
                        {(() => {
                          const progress = serviceProgress[ticket.id] || [];
                          if (progress.length === 0) {
                            return (
                              <div className="text-xs text-gray-500 italic">
                                Carregando progresso dos serviços...
                              </div>
                            );
                          }
                          
                          return (
                            <div className="space-y-2">
                              {progress.map((serviceProgress) => (
                                <ServiceProgressCard
                                  key={serviceProgress.id}
                                  progress={serviceProgress}
                                  ticketId={ticket.id}
                                  selectedEquipment={selectedEquipment}
                                  setSelectedEquipment={setSelectedEquipment}
                                  equipments={equipments}
                                  startServiceProgress={startServiceProgress}
                                  completeServiceProgress={completeServiceProgress}
                                  cancelServiceProgress={cancelServiceProgress}
                                  fetchServiceProgress={fetchServiceProgress}
                                  getProgressStatusColor={getProgressStatusColor}
                                  getProgressStatusText={getProgressStatusText}
                                />
                              ))}
                            </div>
                          );
                        })()}
                      </div>

                      <div className="text-xs text-gray-400 mt-1">
                        {ticket.calledAt ? `Chamado há ${formatDistanceToNow(new Date(ticket.calledAt), { addSuffix: true, locale: ptBR })}` : ""}
                      </div>
                      {ticket.status === 'in_progress' && (
                        <div className="mt-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 w-full">
                          {(ticket.startedAt || ticket.started_at) && (
                            <div className="flex-1 flex flex-col items-center sm:items-start">
                              <ServiceCountdown
                                startTime={ticket.startedAt || ticket.started_at}
                                duration={
                                  ticket.services?.[0]?.duration_minutes ??
                                  ticket.services?.[0]?.duration ??
                                  ticket.services?.[0]?.durationMinutes ??
                                  10
                                }
                              />
                            </div>
                          )}
                          {!(ticket.startedAt || ticket.started_at) && (
                            <span className="text-red-500 font-bold">Início não informado</span>
                          )}
                          <div className="flex flex-col sm:flex-row gap-2 mt-2 sm:mt-0 w-full sm:w-auto justify-center items-center">
                            <button
                              className="w-full sm:w-auto px-5 py-2 bg-green-600 text-white rounded-lg font-bold shadow hover:bg-green-700 focus:ring-2 focus:ring-green-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                              aria-label={`Concluir atendimento do ticket ${ticket.number}`}
                              disabled={completeLoading || !canCompleteTicket(ticket.id)}
                              onClick={async () => {
                                // Verificar se todos os serviços estão completos
                                if (!canCompleteTicket(ticket.id)) {
                                  alert('Todos os serviços devem estar completos para finalizar o ticket!');
                                  return;
                                }
                                
                                await completeService({ ticketId: ticket.id });
                                await refetch();
                              }}
                            >
                              {completeLoading ? 'Concluindo...' : 'Concluir'}
                            </button>
                            <button
                              className="w-full sm:w-auto px-5 py-2 bg-red-500 text-white rounded-lg font-bold shadow hover:bg-red-600 focus:ring-2 focus:ring-red-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                              aria-label={`Cancelar atendimento do ticket ${ticket.number}`}
                              disabled={cancelLoading}
                              onClick={async () => {
                                await cancelTicket({ ticketId: ticket.id });
                                await refetch();
                              }}
                            >
                              {cancelLoading ? 'Cancelando...' : 'Cancelar'}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                    {ticket.status === 'called' && (
                      <button
                        className="mt-4 md:mt-0 w-full md:w-auto px-7 py-3 bg-yellow-500 text-white rounded-xl font-bold shadow-lg hover:bg-yellow-600 focus:ring-2 focus:ring-yellow-400 focus:outline-none transition-all scale-100 group-hover:scale-105 disabled:bg-gray-300 disabled:text-gray-500"
                        aria-label={`Iniciar atendimento do ticket ${ticket.number}`}
                        onClick={async () => {
                          await startService({ ticketId: ticket.id });
                          await refetch();
                          queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                          queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                        }}
                      >
                        Iniciar
                      </button>
                    )}
                    {ticket.status === 'pending_payment' && ticket.payment_confirmed !== true && (
                      <button
                        className="w-full sm:w-auto px-5 py-2 bg-green-500 text-white rounded-lg font-bold shadow hover:bg-green-600 focus:ring-2 focus:ring-green-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                        aria-label={`Confirmar pagamento do ticket ${ticket.number}`}
                        disabled={confirmLoading}
                        onClick={async () => {
                          try {
                            console.log('🔄 Confirmando pagamento do ticket:', ticket.id);
                            await confirmPayment({ ticketId: ticket.id });
                            
                            // Forçar refetch de todas as queries relacionadas
                            console.log('🔄 Atualizando queries após confirmação...');
                            await refetch();
                            
                            // Invalidar queries específicas
                            queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                            queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
                            queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                            
                            console.log('✅ Pagamento confirmado e queries atualizadas');
                          } catch (error) {
                            console.error('❌ Erro ao confirmar pagamento:', error);
                            alert('Erro ao confirmar pagamento. Tente novamente.');
                          }
                        }}
                      >
                        {confirmLoading ? 'Confirmando...' : 'Confirmar Pagamento'}
                      </button>
                    )}
                    {ticket.status === 'paid' && (
                      <button
                        className="mt-4 md:mt-0 w-full md:w-auto px-7 py-3 bg-green-500 text-white rounded-xl font-bold shadow-lg hover:bg-green-600 focus:ring-2 focus:ring-green-400 focus:outline-none transition-all scale-100 group-hover:scale-105 disabled:bg-gray-300 disabled:text-gray-500"
                        aria-label={`Mover ticket ${ticket.number} para fila`}
                        disabled={moveToQueueLoading}
                        onClick={async () => {
                          await moveToQueue({ ticketId: ticket.id });
                          await refetch();
                        }}
                      >
                        {moveToQueueLoading ? 'Movendo...' : 'Mover para Fila'}
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </section>

          {/* Tickets Aguardando Confirmação de Pagamento */}
          <section className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
            <h2 className="text-xl font-semibold mb-2">Aguardando Confirmação de Pagamento</h2>
            {pendingPaymentTickets.length === 0 ? (
              <div className="text-gray-400 text-center py-8">Nenhum ticket aguardando confirmação</div>
            ) : (
              <div className="grid gap-4">
                {pendingPaymentTickets.map(ticket => {
                  return (
                    <div
                      key={ticket.id}
                      className="flex flex-col md:flex-row md:items-center justify-between rounded-2xl p-4 md:p-5 shadow-md hover:shadow-xl transition-transform hover:-translate-y-1 group focus-within:ring-2 focus-within:ring-orange-400 bg-orange-50 border-2 border-orange-200"
                      tabIndex={0}
                      aria-label={`Ticket ${ticket.number}`}
                    >
                      <div className="flex flex-row md:flex-col items-center gap-4 md:gap-2 w-full md:w-auto mb-2 md:mb-0">
                        <div className="flex flex-col items-center">
                          <span className="text-xl md:text-2xl font-bold flex items-center gap-1 text-orange-700">
                            <MdConfirmationNumber className="inline text-2xl md:text-3xl" />
                            {ticket.number}
                          </span>
                          <span className="text-xs font-bold px-2 py-1 rounded-full mt-1 bg-orange-200 text-orange-800">
                            Aguardando Pagamento
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 flex flex-col gap-1 md:gap-2 w-full">
                        <div className="font-semibold text-base md:text-lg text-gray-800 break-words">{ticket.customer_name}</div>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {ticket.services?.map((s, idx) => (
                            <span key={s.id || idx} className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs font-medium">
                              {s.service?.name || s.name || 'Serviço'}
                            </span>
                          ))}
                        </div>
                        {/* Chips de extras */}
                        {ticket.extras && ticket.extras.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {ticket.extras.map((extra, idx) => (
                              <span key={extra.id || idx} className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-medium">
                                {extra.extra?.name || extra.name || 'Extra'} {extra.quantity > 1 && `(${extra.quantity}x)`}
                              </span>
                            ))}
                          </div>
                        )}
                        {/* Cálculo do valor total com desconto */}
                        {ticket.services && ticket.extras && (
                          <div className="mt-2 p-2 bg-blue-50 rounded-lg">
                            <div className="text-sm font-semibold text-blue-800 mb-1">Valor Total:</div>
                                                      <div className="text-xs text-blue-600">
                            {(() => {
                              const { subtotal, discount, total } = calculateTotalWithDiscount(ticket.services, ticket.extras);
                              
                              return (
                                <div>
                                  <div>Subtotal: R$ {subtotal.toFixed(2).replace('.', ',')}</div>
                                  {discount > 0 && (
                                    <div className="text-green-600">Desconto: -R$ {discount.toFixed(2).replace('.', ',')}</div>
                                  )}
                                  <div className="font-semibold">Total: R$ {total.toFixed(2).replace('.', ',')}</div>
                                </div>
                              );
                            })()}
                            </div>
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-1">
                          {ticket.createdAt && new Date(ticket.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                      <div className="flex flex-col gap-2 mt-4 md:mt-0">
                        {ticket.status === 'pending_payment' && ticket.payment_confirmed !== true && (
                          <div className="flex gap-2">
                            <button
                              className="flex-1 px-5 py-2 bg-green-500 text-white rounded-lg font-bold shadow hover:bg-green-600 focus:ring-2 focus:ring-green-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                              aria-label={`Confirmar pagamento do ticket ${ticket.number}`}
                              disabled={confirmLoading}
                              onClick={async () => {
                                try {
                                  console.log('🔄 Confirmando pagamento do ticket:', ticket.id);
                                  await confirmPayment({ ticketId: ticket.id });
                                  
                                  // Forçar refetch de todas as queries relacionadas
                                  console.log('🔄 Atualizando queries após confirmação...');
                                  await refetch();
                                  
                                  // Invalidar queries específicas
                                  queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                                  queryClient.invalidateQueries({ queryKey: ['tickets', 'pending-payment'] });
                                  queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                                  
                                  console.log('✅ Pagamento confirmado e queries atualizadas');
                                } catch (error) {
                                  console.error('❌ Erro ao confirmar pagamento:', error);
                                  alert('Erro ao confirmar pagamento. Tente novamente.');
                                }
                              }}
                            >
                              {confirmLoading ? 'Confirmando...' : 'Confirmar Pagamento'}
                            </button>
                            <button
                              className="px-5 py-2 bg-red-500 text-white rounded-lg font-bold shadow hover:bg-red-600 focus:ring-2 focus:ring-red-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                              aria-label={`Cancelar ticket ${ticket.number}`}
                              disabled={cancelLoading}
                              onClick={async () => {
                                const reason = prompt('Motivo do cancelamento:');
                                if (reason && reason.trim()) {
                                  if (confirm(`Confirmar cancelamento do ticket ${ticket.number}?\nMotivo: ${reason}`)) {
                                    await cancelTicket({ ticketId: ticket.id, reason: reason.trim() });
                                    await refetch();
                                  }
                                } else if (reason !== null) {
                                  alert('Por favor, informe o motivo do cancelamento.');
                                }
                              }}
                            >
                              {cancelLoading ? 'Cancelando...' : 'Cancelar'}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </div>

        {/* Botão para voltar à configuração */}
        <div className="flex justify-center mt-6">
          <button 
                            onClick={() => setCurrentStepWithPersistence('config')}
            className="px-6 py-2 border border-gray-400 text-gray-700 rounded-lg bg-white hover:bg-gray-100 transition-all"
          >
            Voltar para Configurar Serviços e Equipamentos
          </button>
        </div>
    </div>
  );
  };

  // ✅ CORREÇÃO: useEffect unificado para gerenciar a etapa inicial e mudanças de status da operação
  // Problema: Dependências estavam causando loops infinitos e React Errors #300/#310
  // Solução: Memoizar valores e usar useRef para evitar recriações
  const isOperating = safeOperationConfig?.isOperating;
  
  // ✅ CORREÇÃO: Usar useRef para rastrear mudanças de estado
  const previousOperatingState = useRef<boolean | null>(null);
  const isInitialized = useRef<boolean>(false);
  
  useEffect(() => {
    try {
      // ✅ CORREÇÃO: Evitar execução desnecessária no primeiro render
      if (!isInitialized.current) {
        isInitialized.current = true;
        
        // Definir etapa inicial baseado no status da operação
        if (currentStep === null) {
          if (isOperating) {
            console.log('🔍 Operação ativa, indo para operação');
            setCurrentStep('operation');
            localStorage.setItem('operator_current_step', 'operation');
          } else {
            console.log('🔍 Operação não ativa, indo para configuração');
            setCurrentStep('name');
            localStorage.setItem('operator_current_step', 'name');
          }
        }
        return;
      }
      
      // ✅ CORREÇÃO: Não fazer nada se estiver salvando configuração
      if (isSavingConfig) {
        console.log('🔍 Salvando configuração, ignorando mudanças');
        return;
      }
      
      // ✅ CORREÇÃO: Verificar mudanças reais de estado da operação
      const hasOperatingStateChanged = previousOperatingState.current !== null && 
                                      previousOperatingState.current !== isOperating;
      
      if (hasOperatingStateChanged) {
        console.log('🔍 Mudança de estado da operação detectada:', {
          anterior: previousOperatingState.current,
          atual: isOperating
        });
        
        if (isOperating) {
          // Operação ficou ativa
          console.log('🔍 Operação ativa detectada, redirecionando para operação');
          setCurrentStep('operation');
          localStorage.setItem('operator_current_step', 'operation');
        } else {
          // Operação foi encerrada
          console.log('🔍 Operação encerrada, redirecionando para configuração');
          
          // ✅ CORREÇÃO: Usar timeout para evitar conflitos de renderização
          setTimeout(() => {
            try {
              // Limpar localStorage de forma segura
              localStorage.removeItem('operator_current_step');
              localStorage.removeItem('operator_config');
              localStorage.removeItem('operator_name');
              localStorage.removeItem('operator_selected_equipment');
              localStorage.removeItem('operator_active_tab');
              localStorage.removeItem('operator_active_service_tab');
              localStorage.removeItem('operator_preferences');
              
              // Atualizar estado React de forma segura
              setCurrentStep('name');
              setOperatorName('');
              setSelectedEquipment('');
              setActiveTab('operation');
              setActiveServiceTab('');
              
              // Limpar configuração e preferências de forma segura
              if (typeof clearConfig === 'function') {
                try {
                  clearConfig();
                } catch (error) {
                  console.warn('Erro ao limpar config:', error);
                }
              }
              
              if (typeof clearPreferences === 'function') {
                try {
                  clearPreferences();
                } catch (error) {
                  console.warn('Erro ao limpar preferences:', error);
                }
              }
              
              // ✅ CORREÇÃO: NÃO limpar cache aqui para evitar React Error #310
              // O cache será limpo pelo useEffect específico
              
              localStorage.setItem('operator_current_step', 'name');
            } catch (error) {
              console.error('Erro ao limpar estado da operação:', error);
              // Fallback: apenas definir a etapa
              setCurrentStep('name');
              localStorage.setItem('operator_current_step', 'name');
            }
          }, 100); // ✅ Aumentar delay para evitar conflitos
        }
      }
      
      // Atualizar referência
      previousOperatingState.current = isOperating;
      
    } catch (error) {
      console.error('Erro no useEffect unificado:', error);
      // Fallback: ir para configuração em caso de erro
      setCurrentStep('name');
      localStorage.setItem('operator_current_step', 'name');
    }
  }, [isOperating, currentStep, isSavingConfig, clearConfig, clearPreferences]); // ✅ Remover queryClient das dependências

  // ✅ CORREÇÃO: useEffect para carregar dados quando operação estiver ativa
  useEffect(() => {
    try {
      if (safeOperationConfig?.isOperating && tenantId) {
        console.log('🔄 Operação ativa detectada, carregando dados...');
        // ✅ CORREÇÃO: Adicionar delay para evitar problemas de timing
        setTimeout(() => {
          try {
            // ✅ CORREÇÃO: Usar queryClient diretamente ao invés de funções que podem ser recriadas
            if (queryClient) {
              queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
              queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
              queryClient.invalidateQueries({ queryKey: ['equipment'] });
              queryClient.invalidateQueries({ queryKey: ['operation'] });
            }
          } catch (error) {
            console.error('Erro ao refetch dados:', error);
          }
        }, 150); // ✅ Aumentar delay para evitar conflitos
      }
    } catch (error) {
      console.error('Erro no useEffect de carregar dados:', error);
    }
  }, [safeOperationConfig?.isOperating, tenantId, queryClient]); // ✅ Usar safeOperationConfig

  // ✅ CORREÇÃO: Limpar cache apenas quando necessário para evitar React Error #310/#300
  // Usar o mesmo useRef do useEffect anterior para evitar conflitos
  useEffect(() => {
    const isCurrentlyOperating = safeOperationConfig?.isOperating;
    
    // ✅ CORREÇÃO: Apenas executar quando há uma mudança REAL de estado (não na inicialização)
    if (previousOperatingState.current !== null && 
        previousOperatingState.current !== isCurrentlyOperating) {
      
      // ✅ CORREÇÃO: Só limpar cache quando operação para de estar ativa (false)
      // NÃO limpar quando operação fica ativa (true) para evitar React Error #310
      if (previousOperatingState.current === true && isCurrentlyOperating === false) {
        console.log('🧹 Operação encerrada, limpando cache...');
        
        // ✅ CORREÇÃO: Usar timeout para evitar conflitos com outros useEffects
        setTimeout(() => {
          try {
            if (queryClient) {
              queryClient.invalidateQueries({ queryKey: ['tickets'] });
              queryClient.invalidateQueries({ queryKey: ['equipment'] });
              queryClient.invalidateQueries({ queryKey: ['operation'] });
            }
          } catch (error) {
            console.error('Erro ao limpar cache:', error);
          }
        }, 200); // ✅ Aumentar delay para evitar conflitos
      } else if (previousOperatingState.current === false && isCurrentlyOperating === true) {
        console.log('🧹 Operação iniciada, NÃO limpando cache para evitar React Error #310');
      }
    }
    
    // ✅ CORREÇÃO: NÃO atualizar referência aqui, pois já é atualizada no useEffect anterior
    // previousOperatingState.current = isCurrentlyOperating;
  }, [safeOperationConfig?.isOperating, queryClient]); // ✅ Usar safeOperationConfig

  // NOVO: Verificar se os dados estão carregando - MELHORADO
  const isLoading = !user || !tenantId || !safeOperationConfig || !services || !equipments || !extras || 
                   !Array.isArray(services) || !Array.isArray(equipments) || !Array.isArray(extras) ||
                   !safeMyTickets || !safeTickets || !safeEquipment;

  // ✅ CORREÇÃO: Logs para debug dos dados do ResumoVisual
  useEffect(() => {
    console.log('🔍 DEBUG - ResumoVisual dados:', {
      services: services?.length || 0,
      servicesAtivos: services?.filter(s => s && s.isActive).length || 0,
      equipments: equipments?.length || 0,
      equipmentsAtivos: equipments?.filter(e => e && e.isActive).length || 0,
      extras: extras?.length || 0,
      extrasAtivos: extras?.filter(e => e && e.isActive).length || 0,
      tickets: safeMyTickets?.length || 0,
      operationConfig: safeOperationConfig?.isOperating,
      currentStep,
      tenantId
    });
  }, [services, equipments, extras, safeMyTickets, safeOperationConfig?.isOperating, currentStep, tenantId]);

  // Se ainda está carregando, mostrar loading
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando painel do operador...</p>
          <p className="text-sm text-gray-500 mt-2">
            {!user && 'Aguardando autenticação...'}
            {!tenantId && 'Carregando tenant...'}
            {!safeOperationConfig && 'Carregando configuração...'}
            {!services && 'Carregando serviços...'}
            {!equipments && 'Carregando equipamentos...'}
            {!extras && 'Carregando extras...'}
            {!safeMyTickets && 'Carregando tickets...'}
            {!safeTickets && 'Carregando fila...'}
            {!safeEquipment && 'Carregando equipamentos...'}
          </p>
        </div>
      </div>
    );
  }

  // Renderizar componente baseado na etapa atual
  if (!currentStep) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <span className="text-gray-500 text-lg">Carregando...</span>
      </div>
    );
  }

  switch (currentStep) {
    case 'name':
      return renderNameStep();
    case 'config':
      return renderConfigStep();
    case 'operation':
      return renderOperationStep();
    default:
      return renderNameStep();
  }
};

// ✅ SOLUÇÃO: Wrapper com Error Boundary para capturar React Error #310
const OperatorPageWithErrorBoundary: React.FC = () => {
  return (
    <WebSocketErrorBoundary>
      <OperatorPage />
    </WebSocketErrorBoundary>
  );
};

export default OperatorPageWithErrorBoundary; 