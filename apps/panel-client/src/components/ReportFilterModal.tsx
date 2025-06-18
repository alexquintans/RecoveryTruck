import React, { useState } from 'react';

interface ReportFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyFilters: (filters: ReportFilters) => void;
}

export interface ReportFilters {
  startDate: string;
  endDate: string;
  includeDetails: boolean;
  serviceTypes: string[];
  equipmentTypes: string[];
}

export const ReportFilterModal: React.FC<ReportFilterModalProps> = ({
  isOpen,
  onClose,
  onApplyFilters
}) => {
  const [filters, setFilters] = useState<ReportFilters>({
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    includeDetails: true,
    serviceTypes: ['banheira_gelo', 'bota_compressao'],
    equipmentTypes: ['banheira_gelo', 'bota_compressao']
  });

  // Atualizar filtros
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFilters(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFilters(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // Atualizar seleção de tipos de serviço
  const handleServiceTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    
    if (checked) {
      setFilters(prev => ({
        ...prev,
        serviceTypes: [...prev.serviceTypes, value]
      }));
    } else {
      setFilters(prev => ({
        ...prev,
        serviceTypes: prev.serviceTypes.filter(type => type !== value)
      }));
    }
  };

  // Atualizar seleção de tipos de equipamento
  const handleEquipmentTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    
    if (checked) {
      setFilters(prev => ({
        ...prev,
        equipmentTypes: [...prev.equipmentTypes, value]
      }));
    } else {
      setFilters(prev => ({
        ...prev,
        equipmentTypes: prev.equipmentTypes.filter(type => type !== value)
      }));
    }
  };

  // Aplicar filtros
  const handleApplyFilters = () => {
    onApplyFilters(filters);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
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
          
          {/* Tipos de Serviço */}
          <div>
            <h3 className="font-medium mb-2">Tipos de Serviço</h3>
            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="service-banheira"
                  value="banheira_gelo"
                  checked={filters.serviceTypes.includes('banheira_gelo')}
                  onChange={handleServiceTypeChange}
                  className="mr-2"
                />
                <label htmlFor="service-banheira">Banheira de Gelo</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="service-bota"
                  value="bota_compressao"
                  checked={filters.serviceTypes.includes('bota_compressao')}
                  onChange={handleEquipmentTypeChange}
                  className="mr-2"
                />
                <label htmlFor="service-bota">Bota de Compressão</label>
              </div>
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
              <label htmlFor="include-details">Incluir detalhes de atendimentos</label>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end mt-6 gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleApplyFilters}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/80"
          >
            Aplicar Filtros
          </button>
        </div>
      </div>
    </div>
  );
}; 