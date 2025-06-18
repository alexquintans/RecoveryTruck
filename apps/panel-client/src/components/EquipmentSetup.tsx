import React, { useState } from 'react';
import { useMockPanelStore } from '../store/mockPanelStore';

interface EquipmentSetupProps {
  onComplete?: () => void;
}

export const EquipmentSetup: React.FC<EquipmentSetupProps> = ({ onComplete }) => {
  const { operationConfig, setEquipmentCount, startOperation } = useMockPanelStore();
  
  const [banheiraCount, setBanheiraCount] = useState(operationConfig.equipmentCounts['banheira_gelo'] || 3);
  const [botaCount, setBotaCount] = useState(operationConfig.equipmentCounts['bota_compressao'] || 3);
  const [serviceDuration, setServiceDuration] = useState(operationConfig.serviceDuration);
  
  const handleStartOperation = () => {
    // Atualizar contagem de equipamentos
    setEquipmentCount('banheira_gelo', banheiraCount);
    setEquipmentCount('bota_compressao', botaCount);
    
    // Iniciar operação
    startOperation();
    
    // Chamar callback se fornecido
    if (onComplete) onComplete();
  };
  
  return (
    <div>
      <div className="space-y-6">
        <div>
          <label className="block text-lg font-medium mb-2">Banheiras de Gelo</label>
          <div className="flex items-center">
            <button
              type="button"
              onClick={() => setBanheiraCount(Math.max(0, banheiraCount - 1))}
              className="px-3 py-1 bg-gray-200 rounded-l-md hover:bg-gray-300"
            >
              -
            </button>
            <input
              type="number"
              value={banheiraCount}
              onChange={(e) => setBanheiraCount(Math.max(0, parseInt(e.target.value) || 0))}
              className="w-16 text-center border-y border-gray-300 py-1"
              min="0"
            />
            <button
              type="button"
              onClick={() => setBanheiraCount(banheiraCount + 1)}
              className="px-3 py-1 bg-gray-200 rounded-r-md hover:bg-gray-300"
            >
              +
            </button>
          </div>
        </div>
        
        <div>
          <label className="block text-lg font-medium mb-2">Botas de Compressão</label>
          <div className="flex items-center">
            <button
              type="button"
              onClick={() => setBotaCount(Math.max(0, botaCount - 1))}
              className="px-3 py-1 bg-gray-200 rounded-l-md hover:bg-gray-300"
            >
              -
            </button>
            <input
              type="number"
              value={botaCount}
              onChange={(e) => setBotaCount(Math.max(0, parseInt(e.target.value) || 0))}
              className="w-16 text-center border-y border-gray-300 py-1"
              min="0"
            />
            <button
              type="button"
              onClick={() => setBotaCount(botaCount + 1)}
              className="px-3 py-1 bg-gray-200 rounded-r-md hover:bg-gray-300"
            >
              +
            </button>
          </div>
        </div>
        
        <div>
          <label className="block text-lg font-medium mb-2">Tempo de Serviço (minutos)</label>
          <div className="flex items-center">
            <button
              type="button"
              onClick={() => setServiceDuration(Math.max(1, serviceDuration - 1))}
              className="px-3 py-1 bg-gray-200 rounded-l-md hover:bg-gray-300"
            >
              -
            </button>
            <input
              type="number"
              value={serviceDuration}
              onChange={(e) => setServiceDuration(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-16 text-center border-y border-gray-300 py-1"
              min="1"
            />
            <button
              type="button"
              onClick={() => setServiceDuration(serviceDuration + 1)}
              className="px-3 py-1 bg-gray-200 rounded-r-md hover:bg-gray-300"
            >
              +
            </button>
          </div>
        </div>
        
        <div className="pt-4">
          <button
            type="button"
            onClick={handleStartOperation}
            className="px-6 py-3 bg-primary text-white font-semibold rounded-md hover:bg-primary/80 transition-colors"
            disabled={banheiraCount === 0 && botaCount === 0}
          >
            Iniciar Operação
          </button>
        </div>
      </div>
    </div>
  );
}; 