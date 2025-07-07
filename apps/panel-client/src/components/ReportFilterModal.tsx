import React, { useState, useEffect } from 'react';
import { useTicketQueue } from '../hooks/useTicketQueue';
import { useAuth } from '../hooks/useAuth';
import { serviceService } from '../services/serviceService';

interface ReportFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyFilters: (filters: ReportFilters) => void;
}

export interface ReportFilters {
  startDate: string;
  endDate: string;
  includeDetails: boolean;
  serviceIds: string[];
}

export const ReportFilterModal: React.FC<ReportFilterModalProps> = ({
  isOpen,
  onClose,
  onApplyFilters
}) => {
  const { user } = useAuth();
  const tenantId = user?.tenant_id;

  // Estado para lista de serviços reais
  const [realServices, setRealServices] = useState<any[]>([]);

  // Buscar lista de serviços reais ao abrir o modal
  useEffect(() => {
    if (!tenantId) return;
    serviceService.list({ tenant_id: tenantId })
      .then((res: any) => {
        setRealServices(res.items || res);
      })
      .catch(() => setRealServices([]));
  }, [tenantId, isOpen]);

  // Estado dos filtros
  const [filters, setFilters] = useState<ReportFilters>({
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    includeDetails: true,
    serviceIds: [],
  });

  // Atualizar filtros quando os serviços mudarem (selecionar todos por padrão)
  useEffect(() => {
    if (realServices.length > 0) {
      setFilters(prev => ({
        ...prev,
        serviceIds: realServices.map(s => s.id)
      }));
    }
  }, [realServices]);

  // Atualizar campos do filtro
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      setFilters(prev => ({ ...prev, [name]: checked }));
    } else {
      setFilters(prev => ({ ...prev, [name]: value }));
    }
  };

  // Atualizar seleção de serviços
  const handleServiceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    if (checked) {
      setFilters(prev => ({ ...prev, serviceIds: [...prev.serviceIds, value] }));
    } else {
      setFilters(prev => ({ ...prev, serviceIds: prev.serviceIds.filter(id => id !== value) }));
    }
  };

  // Selecionar todos os serviços
  const selectAllServices = () => {
    setFilters(prev => ({ ...prev, serviceIds: realServices.map(s => s.id) }));
  };
  // Limpar seleção de serviços
  const clearAllServices = () => {
    setFilters(prev => ({ ...prev, serviceIds: [] }));
  };

  // Aplicar filtros
  const handleApplyFilters = () => {
    onApplyFilters(filters);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Filtros do Relatório</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="space-y-4">
          {/* Período */}
          <div>
            <h3 className="font-medium mb-2">Período</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Data Inicial</label>
                <input
                  type="date"
                  name="startDate"
                  value={filters.startDate}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Data Final</label>
                <input
                  type="date"
                  name="endDate"
                  value={filters.endDate}
                  onChange={handleInputChange}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>
          {/* Serviços Disponíveis */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium">Serviços Disponíveis</h3>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={selectAllServices}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >Selecionar Todos</button>
                <button
                  type="button"
                  onClick={clearAllServices}
                  className="text-xs text-red-600 hover:text-red-800"
                >Limpar</button>
              </div>
            </div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {realServices.length > 0 ? (
                realServices.map(service => (
                  <div key={service.id} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`service-${service.id}`}
                      value={service.id}
                      checked={filters.serviceIds.includes(service.id)}
                      onChange={handleServiceChange}
                      className="mr-2"
                    />
                    <label htmlFor={`service-${service.id}`} className="text-sm">
                      {service.name}
                    </label>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">Nenhum serviço cadastrado</div>
              )}
            </div>
          </div>
          {/* Opções adicionais */}
          <div>
            <h3 className="font-medium mb-2">Opções</h3>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="include-details"
                name="includeDetails"
                checked={filters.includeDetails}
                onChange={handleInputChange}
                className="mr-2"
              />
              <label htmlFor="include-details" className="text-sm">
                Incluir detalhes de atendimentos
              </label>
            </div>
          </div>
        </div>
        <div className="flex justify-end mt-6 gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >Cancelar</button>
          <button
            onClick={handleApplyFilters}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80"
          >Aplicar Filtros</button>
        </div>
      </div>
    </div>
  );
}; 