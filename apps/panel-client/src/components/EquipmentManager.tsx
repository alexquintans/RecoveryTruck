// @jsxImportSource react
import React, { useState } from 'react';
import { usePanelStore } from '../store/panelStore';
import { ServiceCountdown } from './ServiceCountdown';
import { EquipmentCard } from './EquipmentCard';
import type { Equipment, Ticket } from '../types';

interface EquipmentManagerProps {
  onSelectEquipment?: (equipment: Equipment) => void;
  onEndOperation?: () => void;
}

export const EquipmentManager: React.FC<EquipmentManagerProps> = ({ 
  onSelectEquipment,
  onEndOperation
}: EquipmentManagerProps) => {
  const { equipment, tickets, setEquipmentStatus, endOperation, operationConfig, setServiceDuration } = usePanelStore();
  const [editingServiceTime, setEditingServiceTime] = useState<boolean>(false);
  const [serviceDurationInput, setServiceDurationInput] = useState<number>(operationConfig.serviceDuration);
  const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);
  
  // Agrupar equipamentos por tipo
  const equipmentByType: Record<string, Equipment[]> = {};
  equipment.forEach((eq: Equipment) => {
    if (!equipmentByType[eq.type]) {
      equipmentByType[eq.type] = [];
    }
    equipmentByType[eq.type].push(eq);
  });
  
  // Encontrar ticket associado a um equipamento
  const findTicketForEquipment = (equipmentId: string): Ticket | undefined => {
    return tickets.find((t: Ticket) => 
      t.equipmentId === equipmentId && 
      (t.status === 'in_progress' || t.status === 'called')
    );
  };
  
  // Calcular tempo restante para um ticket
  const calculateRemainingTime = (ticket?: Ticket): string => {
    if (!ticket || !ticket.startedAt || !ticket.endTime) return '--:--';
    
    const endTime = new Date(ticket.endTime).getTime();
    const now = new Date().getTime();
    const remaining = Math.max(0, endTime - now);
    
    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  // Atualizar duração do serviço
  const handleUpdateServiceDuration = (): void => {
    setServiceDuration(serviceDurationInput);
    setEditingServiceTime(false);
  };

  // Encerrar operação
  const handleEndOperation = (): void => {
    endOperation();
    if (onEndOperation) onEndOperation();
  };
  
  // Selecionar equipamento
  const handleSelectEquipment = (eq: Equipment): void => {
    if (eq.status === 'available') {
      setSelectedEquipment(eq.id);
      if (onSelectEquipment) onSelectEquipment(eq);
    }
  };
  
  // Renderizar um equipamento com o novo card
  const renderEquipment = (eq: Equipment) => {
    const ticket = findTicketForEquipment(eq.id);
    
    return (
      <div key={eq.id} className="relative">
        <EquipmentCard
          equipamento={eq}
          selecionado={selectedEquipment === eq.id}
          onClick={() => handleSelectEquipment(eq)}
        />
        
        {/* Informações do ticket em uso */}
        {ticket && ticket.status === 'in_progress' && ticket.startedAt && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm mb-1">
              <span className="font-medium">Cliente:</span> {ticket.customer?.name}
            </p>
            <p className="text-sm mb-2">
              <span className="font-medium">Senha:</span> {ticket.number}
            </p>
            <ServiceCountdown 
              startTime={ticket.startedAt}
              duration={operationConfig.serviceDuration}
              className="mt-2"
            />
          </div>
        )}
        
        {/* Botões de controle de status */}
        <div className="mt-3 flex justify-end gap-2">
          {eq.status === 'available' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setEquipmentStatus(eq.id, 'maintenance' as const);
              }}
              className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
            >
              Manutenção
            </button>
          )}
          
          {eq.status === 'maintenance' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setEquipmentStatus(eq.id, 'available' as const);
              }}
              className="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
            >
              Disponibilizar
            </button>
          )}
        </div>
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-semibold">Equipamentos</h2>
          <div className="mt-2 flex items-center">
            <span className="text-sm mr-3">Tempo de serviço:</span>
            {editingServiceTime ? (
              <div className="flex items-center">
                <input
                  type="number"
                  value={serviceDurationInput}
                  onChange={(e) => setServiceDurationInput(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-16 p-1 border border-gray-300 rounded mr-2"
                  min="1"
                />
                <span className="text-sm mr-2">minutos</span>
                <button
                  onClick={handleUpdateServiceDuration}
                  className="px-2 py-1 text-xs bg-primary text-white rounded hover:bg-primary/80"
                >
                  Salvar
                </button>
              </div>
            ) : (
              <div className="flex items-center">
                <span className="font-medium">{operationConfig.serviceDuration} minutos</span>
                <button
                  onClick={() => {
                    setServiceDurationInput(operationConfig.serviceDuration);
                    setEditingServiceTime(true);
                  }}
                  className="ml-2 text-xs text-blue-600 hover:underline"
                >
                  Editar
                </button>
              </div>
            )}
          </div>
        </div>
        <button
          onClick={handleEndOperation}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
        >
          Encerrar Operação
        </button>
      </div>
      
      {Object.entries(equipmentByType).map(([type, eqs]) => (
        <div key={type} className="mb-6">
          <h3 className="text-xl font-medium mb-3">
            {type === 'banheira_gelo' ? 'Banheiras de Gelo' : 'Botas de Compressão'}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {eqs.map(renderEquipment)}
          </div>
        </div>
      ))}
    </div>
  );
}; 