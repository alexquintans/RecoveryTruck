import React, { useState, useEffect } from 'react';
import { ServiceCountdown } from './ServiceCountdown';

// Definir tipos inline para evitar problemas de importação
interface Customer {
  name: string;
  phone?: string;
  email?: string;
}

interface Service {
  id: string;
  name: string;
  price: number;
}

interface Ticket {
  id: string;
  number: string;
  status: string;
  createdAt: string;
  startedAt?: string;
  endTime?: string;
  service?: Service;
  customer?: Customer;
  equipmentId?: string;
}

interface ServiceStatusProps {
  ticket: Ticket;
  serviceDuration: number;
  onComplete?: () => void;
}

export const ServiceStatus: React.FC<ServiceStatusProps> = ({ 
  ticket, 
  serviceDuration,
  onComplete 
}) => {
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  
  // Calcular tempo restante
  useEffect(() => {
    if (!ticket.startedAt || !ticket.endTime) return;
    
    const endTime = new Date(ticket.endTime).getTime();
    const now = new Date().getTime();
    const remaining = Math.max(0, endTime - now);
    
    setTimeRemaining(Math.floor(remaining / 1000));
    
    if (remaining <= 0 && !isCompleted) {
      setIsCompleted(true);
      if (onComplete) onComplete();
    }
  }, [ticket, isCompleted, onComplete]);
  
  // Formatar o status para exibição
  const formatStatus = (status: string): string => {
    switch (status) {
      case 'in_queue': return 'Na Fila';
      case 'called': return 'Chamado';
      case 'in_progress': return 'Em Atendimento';
      case 'completed': return 'Concluído';
      case 'cancelled': return 'Cancelado';
      default: return status;
    }
  };
  
  // Determinar cor do status
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'in_queue': return 'bg-[#F0F8FF] text-[#3B82F6]';
      case 'called': return 'bg-[#FFF8E1] text-[#F59E0B]';
      case 'in_progress': return 'bg-[#F3E8FF] text-[#8B5CF6]';
      case 'completed': return 'bg-[#F0FDF4] text-[#16A34A]';
      case 'cancelled': return 'bg-[#FEF2F2] text-[#EF4444]';
      default: return 'bg-[#F9FAFB] text-[#6B7280]';
    }
  };
  
  return (
    <div className="p-4 border border-gray-200 rounded-lg">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold">Senha: {ticket.number}</h3>
        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(ticket.status)}`}>
          {formatStatus(ticket.status)}
        </span>
      </div>
      
      <div className="space-y-2">
        <div>
          <span className="font-medium">Cliente:</span> {ticket.customer?.name || 'Não informado'}
        </div>
        
        <div>
          <span className="font-medium">Serviço:</span> {ticket.service?.name || 'Não informado'}
        </div>
        
        {ticket.status === 'in_progress' && ticket.startedAt && (
          <div className="mt-4">
            <div className="font-medium mb-1">Tempo restante:</div>
            <ServiceCountdown 
              startTime={ticket.startedAt}
              duration={serviceDuration}
            />
          </div>
        )}
      </div>
    </div>
  );
}; 