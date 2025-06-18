import React, { useState } from 'react';
import { useMockPanelStore } from '../store/mockPanelStore';
import { generateReport, PanelStats, Ticket, Equipment } from '../services/reportService';
import { ReportFilterModal, ReportFilters } from './ReportFilterModal';

interface ExportReportButtonProps {
  className?: string;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const ExportReportButton: React.FC<ExportReportButtonProps> = ({
  className = '',
  variant = 'primary',
  size = 'md',
}) => {
  const { tickets, equipment, stats } = useMockPanelStore();
  const [isExporting, setIsExporting] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Calcular dados adicionais para o relatório
  const calculateReportData = (filters?: ReportFilters): PanelStats => {
    // Filtrar tickets por data se os filtros estiverem presentes
    let filteredTickets = [...tickets];
    
    if (filters) {
      const startDate = new Date(filters.startDate);
      const endDate = new Date(filters.endDate);
      endDate.setHours(23, 59, 59, 999); // Fim do dia
      
      filteredTickets = tickets.filter(ticket => {
        const ticketDate = new Date(ticket.createdAt);
        return ticketDate >= startDate && ticketDate <= endDate;
      });
      
      // Filtrar por tipo de serviço
      if (filters.serviceTypes.length > 0) {
        filteredTickets = filteredTickets.filter(ticket => 
          ticket.service && filters.serviceTypes.includes(ticket.service.equipmentType || '')
        );
      }
    }
    
    // Contar tickets por status
    const ticketCounts = {
      inQueue: filteredTickets.filter(t => t.status === 'in_queue').length,
      called: filteredTickets.filter(t => t.status === 'called').length,
      inProgress: filteredTickets.filter(t => t.status === 'in_progress').length,
      completed: filteredTickets.filter(t => t.status === 'completed').length,
      cancelled: filteredTickets.filter(t => t.status === 'cancelled').length,
      total: filteredTickets.length
    };

    // Calcular tempo médio de atendimento
    const calculateAverageServiceTime = () => {
      const completedTickets = filteredTickets.filter(ticket => 
        ticket.status === 'completed' && ticket.startedAt && ticket.completedAt
      );
      
      if (completedTickets.length === 0) return 0;
      
      const totalMinutes = completedTickets.reduce((sum, ticket) => {
        const startTime = new Date(ticket.startedAt!).getTime();
        const endTime = new Date(ticket.completedAt!).getTime();
        const diffMinutes = (endTime - startTime) / (1000 * 60);
        return sum + diffMinutes;
      }, 0);
      
      return Math.round(totalMinutes / completedTickets.length);
    };

    // Calcular receita média por atendimento
    const calculateAverageRevenue = () => {
      const completedTickets = filteredTickets.filter(ticket => 
        ticket.status === 'completed' && ticket.service?.price
      );
      
      if (completedTickets.length === 0) return 0;
      
      const totalRevenue = completedTickets.reduce((sum, ticket) => 
        sum + (ticket.service?.price || 0), 0
      );
      
      return Math.round((totalRevenue / completedTickets.length) * 100) / 100;
    };

    // Calcular taxa de conclusão
    const calculateCompletionRate = () => {
      if (ticketCounts.total === 0) return 0;
      return Math.round((ticketCounts.completed / ticketCounts.total) * 100);
    };

    // Calcular faturamento diário
    const calculateDailyRevenue = () => {
      const completedTickets = filteredTickets.filter(ticket => 
        ticket.status === 'completed' && ticket.service?.price
      );
      
      return completedTickets.reduce((sum, ticket) => 
        sum + (ticket.service?.price || 0), 0
      );
    };

    return {
      inQueueTickets: ticketCounts.inQueue,
      calledTickets: ticketCounts.called,
      inProgressTickets: ticketCounts.inProgress,
      completedTickets: ticketCounts.completed,
      cancelledTickets: ticketCounts.cancelled,
      totalTickets: ticketCounts.total,
      averageWaitTime: stats?.averageWaitTime || 0,
      averageServiceTime: calculateAverageServiceTime(),
      averageRevenue: calculateAverageRevenue(),
      completionRate: calculateCompletionRate(),
      dailyRevenue: calculateDailyRevenue(),
    };
  };

  // Filtrar equipamentos com base nos filtros
  const filterEquipment = (filters?: ReportFilters): Equipment[] => {
    if (!filters || filters.equipmentTypes.length === 0) {
      return equipment;
    }
    
    return equipment.filter(eq => filters.equipmentTypes.includes(eq.type));
  };

  // Filtrar tickets com base nos filtros
  const filterTickets = (filters?: ReportFilters): Ticket[] => {
    if (!filters) {
      return tickets;
    }
    
    let filteredTickets = [...tickets];
    
    // Filtrar por data
    const startDate = new Date(filters.startDate);
    const endDate = new Date(filters.endDate);
    endDate.setHours(23, 59, 59, 999); // Fim do dia
    
    filteredTickets = filteredTickets.filter(ticket => {
      const ticketDate = new Date(ticket.createdAt);
      return ticketDate >= startDate && ticketDate <= endDate;
    });
    
    // Filtrar por tipo de serviço
    if (filters.serviceTypes.length > 0) {
      filteredTickets = filteredTickets.filter(ticket => 
        ticket.service && filters.serviceTypes.includes(ticket.service.equipmentType || '')
      );
    }
    
    return filteredTickets;
  };

  // Função para exportar o relatório
  const handleExportReport = (filters?: ReportFilters) => {
    setIsExporting(true);
    
    try {
      // Preparar dados adicionais para o relatório
      const reportStats = calculateReportData(filters);
      const filteredEquipment = filterEquipment(filters);
      const filteredTickets = filterTickets(filters);
      
      // Gerar o relatório
      generateReport(
        reportStats, 
        filteredTickets, 
        filteredEquipment, 
        filters?.includeDetails
      );
      
      // Mostrar mensagem de sucesso
      alert('Relatório exportado com sucesso!');
    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
      alert('Erro ao exportar relatório. Tente novamente.');
    } finally {
      setIsExporting(false);
    }
  };

  // Classes CSS baseadas nas props
  const getButtonClasses = () => {
    let baseClasses = 'flex items-center rounded-lg shadow-md transition-colors ';
    
    // Tamanho
    if (size === 'sm') baseClasses += 'px-3 py-1 text-sm ';
    else if (size === 'lg') baseClasses += 'px-5 py-3 text-lg ';
    else baseClasses += 'px-4 py-2 '; // md (default)
    
    // Variante
    if (isExporting) {
      baseClasses += 'bg-gray-300 text-gray-600 cursor-not-allowed ';
    } else {
      if (variant === 'primary') baseClasses += 'bg-primary text-white hover:bg-primary/80 ';
      else if (variant === 'secondary') baseClasses += 'bg-secondary text-primary hover:bg-secondary/80 ';
      else baseClasses += 'bg-white text-primary border border-primary hover:bg-gray-50 ';
    }
    
    return baseClasses + className;
  };

  // Abrir modal de filtros
  const handleOpenFilters = () => {
    setShowFilters(true);
  };

  // Fechar modal de filtros
  const handleCloseFilters = () => {
    setShowFilters(false);
  };

  // Aplicar filtros e exportar relatório
  const handleApplyFilters = (filters: ReportFilters) => {
    handleExportReport(filters);
  };

  return (
    <>
      <button
        onClick={handleOpenFilters}
        disabled={isExporting}
        className={getButtonClasses()}
      >
        {isExporting ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Exportando...
          </>
        ) : (
          <>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Exportar Relatório
          </>
        )}
      </button>

      <ReportFilterModal
        isOpen={showFilters}
        onClose={handleCloseFilters}
        onApplyFilters={handleApplyFilters}
      />
    </>
  );
}; 