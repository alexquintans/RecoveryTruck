import React from 'react';

// Definir tipos inline para evitar problemas de importação
interface Customer {
  name: string;
  phone?: string;
  email?: string;
  document?: string;
}

interface Service {
  id: string;
  name: string;
  description?: string;
  price: number;
}

interface Ticket {
  id: string;
  number: string;
  status: string;
  createdAt: string;
  service?: Service;
  services?: Service[];
  customer?: Customer;
  queuePosition?: number;
}

interface TicketDisplayProps {
  ticket: Ticket;
  size?: 'small' | 'medium' | 'large';
  showPosition?: boolean;
}

export const TicketDisplay: React.FC<TicketDisplayProps> = ({ 
  ticket, 
  size = 'medium',
  showPosition = false
}) => {
  // Determinar classes com base no tamanho
  const containerClasses = {
    small: 'p-3',
    medium: 'p-4',
    large: 'p-5'
  };
  
  // Determinar classes para o título
  const titleClasses = {
    small: 'text-base font-medium',
    medium: 'text-lg font-semibold',
    large: 'text-xl font-bold'
  };
  
  // Formatar status para exibição
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
      case 'in_queue': return 'bg-blue-100 text-blue-800';
      case 'called': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-purple-100 text-purple-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className={`${containerClasses[size]} flex justify-between items-center`}>
      <div>
        <div className="flex items-center gap-2">
          <span className={titleClasses[size]}>{ticket.number}</span>
          {ticket.services && ticket.services.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {ticket.services.map((service, index) => (
                <span key={service.id} className="text-sm text-gray-600">
                  {service.name}{index < ticket.services!.length - 1 ? ', ' : ''}
                </span>
              ))}
            </div>
          ) : ticket.service ? (
            <span className="text-sm text-gray-600">{ticket.service.name}</span>
          ) : null}
        </div>
        
        {ticket.customer && (
          <p className="text-sm text-gray-500 mt-1">{ticket.customer.name}</p>
        )}
      </div>
      
      <div className="flex flex-col items-end">
        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(ticket.status)}`}>
          {formatStatus(ticket.status)}
        </span>
        
        {showPosition && ticket.status === 'in_queue' && (
          <span className="text-xs text-gray-500 mt-1">Posição: {ticket.queuePosition || '-'}</span>
        )}
      </div>
    </div>
  );
}; 