import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTicketQueue } from '../hooks/useTicketQueue';
import { useOperatorActions } from '../hooks/useOperatorActions';
import { useAuth } from '../hooks/useAuth';
import { fetchServices, fetchEquipments, fetchExtras, createService, createExtra, updateService as apiUpdateService, deleteService as apiDeleteService, updateExtra as apiUpdateExtra, deleteExtra as apiDeleteExtra, saveOperationConfig } from '../services/operatorConfigService';
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

interface Ticket {
  id: string;
  status: string;
  number?: string;
  service?: { name: string };  // Formato antigo
  services?: { name: string }[];  // Formato novo
  equipmentId?: string;
  operatorId?: string;
  createdAt?: string;
  calledAt?: string;
  priority?: string;
  extras?: { name: string; quantity: number }[]; // Adicionado para extras
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
function ResumoVisual({ servicos, equipamentos, extras, tickets }) {
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

const OperatorPage: React.FC = () => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState<'name' | 'config' | 'operation'>('name');
  const [operatorName, setOperatorName] = useState<string>(user?.name || '');
  const operatorId = user?.id;
  const tenantId = user?.tenant_id;
  
  // Estados para modais
  const [activeModal, setActiveModal] = useState<'service'|'extra'|null>(null);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [editingExtra, setEditingExtra] = useState<Extra | null>(null);

  // Estados para configuração
  const [services, setServices] = useState<Service[]>([]);
  const [extras, setExtras] = useState<Extra[]>([]);
  const [equipments, setEquipments] = useState<Equipment[]>([]);

  // Métodos de pagamento disponíveis para a operação
  type PaymentMode = 'none' | 'mercadopago' | 'sicredi';
  const [paymentModes, setPaymentModes] = useState<PaymentMode[]>([]);

  const togglePaymentMode = (mode: PaymentMode) => {
    setPaymentModes(prev => {
      if (mode === 'none') {
        // "Nenhum" é exclusivo – seleciona / desseleciona e limpa os demais
        return prev.includes('none') ? [] : ['none'];
      }
      // Se algum modo específico for marcado, remova "none" se existir
      const filtered = prev.filter(m => m !== 'none');
      if (filtered.includes(mode)) {
        // Desmarca o modo
        return filtered.filter(m => m !== mode);
      }
      // Marca o modo
      return [...filtered, mode];
    });
  };

  const [selectedEquipment, setSelectedEquipment] = useState<string>('');

  // Estados para formulários
  const [serviceForm, setServiceForm] = useState<Omit<Service, 'id'>>({
    name: '',
    description: '',
    price: 0,
    duration: 10,
    equipment_count: 1,
    isActive: true,
    type: '',
    color: 'blue'
  });

  const [extraForm, setExtraForm] = useState<Omit<Extra, 'id'>>({
    name: '',
    description: '',
    price: 0,
    category: '',
    stock: 0,
    isActive: true
  });

  // Dados para operação
  const { tickets, myTickets, completedTickets, cancelledTickets, pendingPaymentTickets, equipment, operationConfig, refetch } = useTicketQueue();
  const { 
    callTicket, 
    startService, 
    completeService, 
    cancelTicket,
    confirmPayment,
    moveToQueue,
    callLoading,
    startLoading,
    completeLoading,
    cancelLoading,
    confirmLoading,
    moveToQueueLoading,
  } = useOperatorActions();
  
  const navigate = useNavigate();
  
  const queryClient = useQueryClient();

  // Obter configuração atual de pagamento
  const [currentPaymentModes, setCurrentPaymentModes] = useState<string[]>([]);
  
  useEffect(() => {
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
    
    if (tenantId) {
      fetchPaymentConfig();
    }
  }, [tenantId]);

  // Verificar se o modo de pagamento é "none"
  const isPaymentNone = currentPaymentModes.includes('none');
  
  // Buscar dados reais da API ao montar o componente
  useEffect(() => {
    if (tenantId) {
      fetchServices({ tenant_id: tenantId }).then(data => setServices(data.items || data)).catch(() => {});
      fetchEquipments({ tenant_id: tenantId }).then(data => {
        const list = (data.items || data).map((eq: any) => ({
          id: eq.id,
          name: eq.name || eq.identifier || 'Equipamento',
          type: eq.type,
          serviceId: eq.service_id,
          count: 1,
          isActive: true,
        }));
        setEquipments(list);
      }).catch(() => {});
      fetchExtras({ tenant_id: tenantId }).then(data => setExtras(data.items || data)).catch(() => {});
    }
  }, [tenantId]);

  // Fechar todos os modais ao trocar de etapa
  useEffect(() => {
    setActiveModal(null);
    setEditingService(null);
    setEditingExtra(null);
  }, [currentStep]);

  // Funções para manipular serviços
  const toggleService = async (serviceId: string, currentActive: boolean) => {
    try {
      await apiUpdateService(serviceId, { is_active: !currentActive });
    setServices(prevServices =>
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
    setServices(prevServices =>
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
    setServices(prev => [...prev, newService]);
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
      setServices(prev => prev.map(s => s.id === serviceId ? { ...data, id: s.id } : s));
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
      setServices(prev => prev.filter(s => s.id !== serviceId));
    } catch(err) {
      alert('Falha ao excluir serviço');
    }
  };

  // Funções para manipular extras
  const toggleExtra = (extraId: string) => {
    setExtras(prevExtras =>
      prevExtras.map(extra =>
        extra.id === extraId
          ? { ...extra, isActive: !extra.isActive }
          : extra
      )
    );
  };

  const updateExtraStock = (extraId: string, stock: number) => {
    setExtras(prevExtras =>
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
    setExtras(prev => [...prev, newExtra]);
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
      setExtras(prev => 
        prev.map(e => e.id === editingExtra.id ? { ...extraForm, id: editingExtra.id } : e)
      );
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
    setEquipments(prev =>
      prev.map(eq =>
        eq.id === equipmentId
          ? { ...eq, count: Math.max(0, count) }
          : eq
      )
    );
  };

  const toggleEquipment = (equipmentId: string) => {
    setEquipments(prev =>
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

  // Funções para atualizar campos dos serviços e extras
  function updateServiceField(id: string, field: string, value: any) {
    setServices(prev => prev.map(s => s.id === id ? { ...s, [field]: value } : s));
  }
  function updateExtraField(id: string, field: string, value: any) {
    setExtras(prev => prev.map(x => x.id === id ? { ...x, [field]: value } : x));
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
              setCurrentStep('config');
            }
          }} className="w-full space-y-4 mt-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Operador</label>
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all text-gray-800 bg-gray-50"
                value={operatorName}
                onChange={(e) => setOperatorName(e.target.value)}
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
                  if (confirm('Tem certeza que deseja encerrar a operação?')) {
                    try {
                      await equipmentService.stopOperation();
                    } catch (e) {
                      alert('Falha ao encerrar operação no backend!');
                    }
                    alert('Operação encerrada com sucesso!');
                    setCurrentStep('name');
                    localStorage.removeItem('operator_config');
                    navigate('/');
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg shadow-lg hover:bg-red-700 transition-all font-semibold hover:scale-105"
              >
                Encerrar Operação
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
            servicos={services.filter(s => s.isActive).length}
            equipamentos={equipments.filter(e => e.isActive).length}
            extras={extras.filter(e => e.isActive).length}
            tickets={myTickets.length}
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
                    <div>
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
                    <span className="text-sm text-[#1F526B] font-medium">Toggle</span>
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
                      <span className="text-sm text-[#1F526B] font-medium">Toggle</span>
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
                    <div>
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
                    <span className="text-sm text-[#1F526B] font-medium">Toggle</span>
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
              onClick={() => setCurrentStep('name')}
              className="px-6 py-2 border border-accent text-text rounded-lg bg-white hover:bg-accent/50 transition-all font-semibold hover:shadow-md"
            >
              Voltar
            </button>
            <button 
              onClick={async () => {
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
                try {
                  await saveOperationConfig(configPayload);
                  setCurrentStep('operation');
                  alert('Configuração salva e operação iniciada com sucesso!');
                } catch (err) {
                  alert('Erro ao salvar configuração da operação!');
                }
              }}
              className="px-6 py-2 bg-[#3B82F6] text-white rounded-lg font-semibold shadow-lg hover:bg-[#2563EB] active:scale-95 transition-all hover:shadow-xl"
            >
              Salvar e Continuar
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
    const availableEquipments = equipments
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

    // Badge de status
    const StatusBadge = ({ status }: { status: string }) => {
      const color = status === 'in_queue' ? 'bg-blue-100 text-blue-700' :
        status === 'called' ? 'bg-yellow-100 text-yellow-700' :
        status === 'in_progress' ? 'bg-green-100 text-green-700' :
        status === 'completed' ? 'bg-gray-100 text-gray-700' :
        status === 'cancelled' ? 'bg-red-100 text-red-700' :
        'bg-gray-100 text-gray-700';
      return <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>{status.replace('_', ' ')}</span>;
    };

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
              onClick={() => {
                if (confirm('Tem certeza que deseja encerrar a operação?')) {
                  alert('Operação encerrada com sucesso!');
                  setCurrentStep('name');
                  localStorage.removeItem('operator_config');
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg shadow hover:bg-red-700 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              Encerrar Operação
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
          servicos={services.filter(s => s.isActive).length}
          equipamentos={equipments.filter(e => e.isActive).length}
          extras={extras.filter(e => e.isActive).length}
          tickets={myTickets.length}
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
          {/* Fila */}
          <section className="bg-white p-6 rounded-xl shadow flex flex-col gap-4">
            <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold mb-2">Fila</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                    queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  🔄 Atualizar Fila
                </button>
                <button
                  onClick={async () => {
                    // Teste: chamar o primeiro ticket da fila
                    if (tickets.length > 0) {
                      const firstTicket = tickets[0];
                      console.log('🧪 TESTE - Chamando ticket:', firstTicket.id, 'Status:', firstTicket.status);
                      
                      // Verificar se o ticket já foi chamado
                      if (firstTicket.status === 'called') {
                        console.log('🧪 TESTE - Ticket já foi chamado, pulando...');
                        alert('Este ticket já foi chamado!');
                        return;
                      }
                      
                      // Verificar se o ticket está na fila
                      if (firstTicket.status !== 'in_queue') {
                        console.log('🧪 TESTE - Ticket não está na fila, pulando...');
                        alert('Este ticket não está na fila!');
                        return;
                      }
                      
                      try {
                        await callTicket(firstTicket.id, 'crioterapia-1');
                        console.log('🧪 TESTE - Ticket chamado com sucesso');
                        // Forçar refresh
                        queryClient.invalidateQueries({ queryKey: ['tickets', 'queue'] });
                        queryClient.invalidateQueries({ queryKey: ['tickets', 'my-tickets'] });
                      } catch (error) {
                        console.error('🧪 TESTE - Erro ao chamar ticket:', error);
                        alert('Erro ao chamar ticket: ' + (error as any)?.message || 'Erro desconhecido');
                      }
                    }
                  }}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  🧪 Teste Chamar
                </button>
              </div>
            </div>
            {/* Debug: Log dos tickets recebidos */}
            {console.log('🔍 DEBUG - Tickets recebidos:', tickets)}
            {console.log('🔍 DEBUG - Tickets com status in_queue:', tickets.filter(t => t.status === 'in_queue'))}
            {console.log('🔍 DEBUG - Outros status encontrados:', [...new Set(tickets.map(t => t.status))])}
            {console.log('🔍 DEBUG - Ticket #38:', tickets.find(t => t.number === '#038' || t.number === '38' || t.ticket_number === 38))}
            {console.log('🔍 DEBUG - Todos os tickets com pending_payment:', tickets.filter(t => t.status === 'pending_payment'))}
            {tickets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path d="M8 12h4l3 6" strokeWidth="2" /></svg>
                <span className="text-base">Nenhum ticket na fila</span>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {tickets.map((ticket) => {
                  // Calcular tempo de espera
                  const created = ticket.createdAt ? new Date(ticket.createdAt) : null;
                  const now = new Date();
                  const waitingMinutes = created ? Math.floor((now.getTime() - created.getTime()) / 60000) : null;
                  return (
                    <div
                      key={ticket.id}
                      className="flex items-center justify-between bg-white rounded-2xl border border-blue-200 p-5 shadow-md hover:shadow-xl transition-transform hover:-translate-y-1 group focus-within:ring-2 focus-within:ring-blue-400"
                      tabIndex={0}
                      aria-label={`Ticket ${ticket.number}`}
                    >
                      <div className="flex flex-col gap-1 w-full">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-50 text-blue-700 text-3xl font-extrabold border-2 border-blue-200 shadow-sm">
                            <svg className="w-6 h-6 mr-1 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="4" y="8" width="16" height="8" rx="4" strokeWidth="2" /><path d="M8 12h8" strokeWidth="2" /></svg>
                            {ticket.number}
                          </span>
                          <StatusBadge status={ticket.status} />
                          {/* Badge de prioridade se existir */}
                          {ticket.priority && (
                            <span className={`ml-2 px-2 py-0.5 rounded text-xs font-semibold ${ticket.priority === 'high' ? 'bg-red-100 text-red-700' : ticket.priority === 'low' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>{ticket.priority === 'high' ? 'Prioritário' : ticket.priority === 'low' ? 'Baixa' : 'Normal'}</span>
                          )}
                          {/* Tempo de espera */}
                          {waitingMinutes !== null && (
                            <span className="ml-4 flex items-center gap-1 text-xs text-gray-500">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" strokeWidth="2" /><path d="M12 7v5l3 3" strokeWidth="2" strokeLinecap="round" /></svg>
                              {waitingMinutes} min
                            </span>
                          )}
                        </div>
                        <div className="text-base font-semibold text-gray-800">{ticket.customer_name || ticket.customer?.name}</div>
                        {/* Chips de serviços */}
                        <div className="flex flex-wrap gap-2 mt-1">
                          {ticket.services && ticket.services.length > 0 ? (
                            ticket.services.map((service, idx) => (
                              <span key={service.id || idx} className="bg-blue-100 text-blue-700 rounded-full px-3 py-0.5 text-xs font-medium shadow-sm">
                                {service.name}
                              </span>
                            ))
                          ) : (
                            <span className="bg-blue-50 text-blue-400 rounded-full px-3 py-0.5 text-xs font-medium">{ticket.service?.name}</span>
                          )}
                        </div>
                        {/* Chips de extras */}
                        {ticket.extras && ticket.extras.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-1">
                            {ticket.extras.map((extra, idx) => (
                              <span key={extra.id || idx} className="bg-green-100 text-green-700 rounded-full px-3 py-0.5 text-xs font-medium shadow-sm">
                                {extra.name} {extra.quantity > 1 && `(${extra.quantity}x)`}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-1">{ticket.createdAt && new Date(ticket.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</div>
                      </div>
                      <button
                        disabled={callLoading || !selectedEquipment}
                        onClick={async () => {
                          console.log('🔍 DEBUG - Chamando ticket:', ticket.id, 'com equipamento:', selectedEquipment);
                          console.log('🔍 DEBUG - Status do ticket:', ticket.status);
                          
                          // Verificar se o ticket já foi chamado
                          if (ticket.status === 'called') {
                            console.log('🔍 DEBUG - Ticket já foi chamado, pulando...');
                            alert('Este ticket já foi chamado!');
                            return;
                          }
                          
                          // Verificar se o ticket está na fila
                          if (ticket.status !== 'in_queue') {
                            console.log('🔍 DEBUG - Ticket não está na fila, pulando...');
                            alert('Este ticket não está na fila!');
                            return;
                          }
                          
                          await callTicket({ ticketId: ticket.id, equipmentId: selectedEquipment });
                          console.log('🔍 DEBUG - Ticket chamado, refetching...');
                          await refetch();
                          console.log('🔍 DEBUG - Refetch concluído');
                        }}
                        className="ml-6 px-7 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-400 focus:outline-none transition-all scale-100 group-hover:scale-105 disabled:bg-gray-300 disabled:text-gray-500"
                        aria-label={`Chamar ticket ${ticket.number}`}
                      >
                        Chamar
                      </button>
                    </div>
                  );
                })}
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
            {myTickets.length === 0 ? (
              <div className="text-gray-400 text-center py-8">Nenhum ticket em atendimento</div>
            ) : (
              myTickets.map(ticket => {
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
                      {/* Cálculo do valor total */}
                      {ticket.services && ticket.extras && (
                        <div className="mt-2 p-2 bg-blue-50 rounded-lg">
                          <div className="text-sm font-semibold text-blue-800 mb-1">Valor Total:</div>
                          <div className="text-xs text-blue-600">
                            {(() => {
                              const servicesTotal = ticket.services.reduce((sum, s) => sum + (s.price || 0), 0);
                              const extrasTotal = ticket.extras.reduce((sum, e) => sum + ((e.price || 0) * (e.quantity || 1)), 0);
                              const total = servicesTotal + extrasTotal;
                              return `R$ ${total.toFixed(2).replace('.', ',')}`;
                            })()}
                          </div>
                        </div>
                      )}
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
                              disabled={completeLoading}
                              onClick={async () => {
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
                                if (window.confirm('Tem certeza que deseja cancelar este atendimento?')) {
                                  const reason = window.prompt('Informe o motivo do cancelamento:', 'Cancelado pelo operador') || 'Cancelado pelo operador';
                                  await cancelTicket({ ticketId: ticket.id, reason });
                                  await refetch();
                                }
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
                          await confirmPayment({ ticketId: ticket.id });
                          await refetch();
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
                        {/* Cálculo do valor total */}
                        {ticket.services && ticket.extras && (
                          <div className="mt-2 p-2 bg-blue-50 rounded-lg">
                            <div className="text-sm font-semibold text-blue-800 mb-1">Valor Total:</div>
                            <div className="text-xs text-blue-600">
                              {(() => {
                                const servicesTotal = ticket.services.reduce((sum, s) => sum + (s.price || 0), 0);
                                const extrasTotal = ticket.extras.reduce((sum, e) => sum + ((e.price || 0) * (e.quantity || 1)), 0);
                                const total = servicesTotal + extrasTotal;
                                return `R$ ${total.toFixed(2).replace('.', ',')}`;
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
                          <button
                            className="w-full sm:w-auto px-5 py-2 bg-green-500 text-white rounded-lg font-bold shadow hover:bg-green-600 focus:ring-2 focus:ring-green-400 focus:outline-none transition-all disabled:bg-gray-300 disabled:text-gray-500"
                            aria-label={`Confirmar pagamento do ticket ${ticket.number}`}
                            disabled={confirmLoading}
                            onClick={async () => {
                              await confirmPayment({ ticketId: ticket.id });
                              await refetch();
                            }}
                          >
                            {confirmLoading ? 'Confirmando...' : 'Confirmar Pagamento'}
                          </button>
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
            onClick={() => setCurrentStep('config')}
            className="px-6 py-2 border border-gray-400 text-gray-700 rounded-lg bg-white hover:bg-gray-100 transition-all"
          >
            Voltar às Configurações
          </button>
        </div>
    </div>
  );
  };

  // Renderizar componente baseado na etapa atual
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

export default OperatorPage; 