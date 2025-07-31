// @ts-ignore
import jsPDF from 'jspdf';
// @ts-ignore
import 'jspdf-autotable';
// @ts-ignore
import autoTable from 'jspdf-autotable';

// Definições de tipos
export interface PanelStats {
  inQueueTickets: number;
  calledTickets: number;
  inProgressTickets: number;
  completedTickets: number;
  cancelledTickets?: number;
  totalTickets?: number;
  averageWaitTime: number;
  averageServiceTime?: number;
  dailyRevenue: number;
  averageRevenue?: number;
  completionRate?: number;
  utilizationByEquipmentType?: {
    [key: string]: number; // tipo de equipamento -> porcentagem de utilização
  };
}

export interface Customer {
  name: string;
  phone?: string;
  email?: string;
  document?: string;
}

export interface Service {
  id: string;
  name: string;
  description?: string;
  price: number;
  duration: number;
  equipmentType?: string;
}

export interface Ticket {
  id: string;
  number: string;
  status: 'in_queue' | 'called' | 'in_progress' | 'completed' | 'cancelled';
  createdAt: string;
  calledAt?: string;
  startedAt?: string;
  completedAt?: string;
  cancelledAt?: string;
  service?: Service;
  customer?: Customer;
  service_name?: string;
  customer_name?: string;
  services?: Service[];
  operatorId?: string;
  equipmentId?: string;
}

export interface Equipment {
  id: string;
  name: string;
  type: string;
  status: 'available' | 'in_use' | 'maintenance';
}

// Função para formatar valores monetários
const formatCurrency = (value: number): string => {
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  });
};

// Função para formatar tempo
const formatTime = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} min`;
  } else {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}min`;
  }
};

// Função para formatar data e hora
const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('pt-BR');
};

// Função para calcular o tempo médio de atendimento
const calculateAverageServiceTime = (tickets: Ticket[]): number => {
  const completedTickets = tickets.filter(ticket => ticket.status === 'completed' && ticket.startedAt && ticket.completedAt);
  
  if (completedTickets.length === 0) return 0;
  
  const totalMinutes = completedTickets.reduce((sum, ticket) => {
    const startTime = new Date(ticket.startedAt!).getTime();
    const endTime = new Date(ticket.completedAt!).getTime();
    const diffMinutes = (endTime - startTime) / (1000 * 60);
    return sum + diffMinutes;
  }, 0);
  
  return Math.round(totalMinutes / completedTickets.length);
};

// Função para calcular a taxa de ocupação dos equipamentos
const calculateEquipmentUtilization = (equipment: Equipment[]): number => {
  const total = equipment.length;
  if (total === 0) return 0;
  
  const inUse = equipment.filter(eq => eq.status === 'in_use').length;
  return Math.round((inUse / total) * 100);
};

// Função para calcular a receita média por atendimento
const calculateAverageRevenue = (tickets: Ticket[]): number => {
  const completedTickets = tickets.filter(ticket => ticket.status === 'completed' && ticket.service?.price);
  
  if (completedTickets.length === 0) return 0;
  
  const totalRevenue = completedTickets.reduce((sum, ticket) => sum + (ticket.service?.price || 0), 0);
  return Math.round((totalRevenue / completedTickets.length) * 100) / 100;
};

// Função para calcular estatísticas por tipo de serviço
const calculateServiceStats = (tickets: Ticket[]) => {
  const serviceStats: Record<string, { count: number, revenue: number }> = {};
  
  tickets.filter(ticket => ticket.status === 'completed').forEach(ticket => {
    // Usar service_name se disponível, senão usar service.name
    const serviceName = ticket.service_name || ticket.service?.name || 'Desconhecido';
    
    if (!serviceStats[serviceName]) {
      serviceStats[serviceName] = { count: 0, revenue: 0 };
    }
    
    serviceStats[serviceName].count += 1;
    
    // Calcular preço total dos serviços
    if (ticket.services && ticket.services.length > 0) {
      serviceStats[serviceName].revenue += ticket.services.reduce((sum, service) => 
        sum + (service.price || 0), 0
      );
    } else {
      serviceStats[serviceName].revenue += ticket.service?.price || 0;
    }
  });
  
  return serviceStats;
};

// Função para gerar o relatório em PDF
export const generateReport = (stats: PanelStats, tickets: Ticket[], equipment?: Equipment[], includeDetails: boolean = true): void => {
  // Criar documento PDF
  const doc = new jsPDF();
  
  // Adicionar logo (representação simples)
  doc.setFillColor(31, 82, 107); // Cor primária #1F526B
  doc.rect(14, 10, 30, 8, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(12);
  doc.text('RecoveryTruck', 16, 16);
  doc.setTextColor(0, 0, 0);
  
  // Adicionar título
  doc.setFontSize(20);
  doc.text('Relatório de Atendimento', 14, 30);
  
  // Adicionar data do relatório
  doc.setFontSize(10);
  doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, 14, 38);
  
  // Calcular métricas adicionais
  const averageServiceTime = calculateAverageServiceTime(tickets);
  const equipmentUtilization = equipment ? calculateEquipmentUtilization(equipment) : 0;
  const averageRevenue = calculateAverageRevenue(tickets);
  const serviceStats = calculateServiceStats(tickets);
  
  // Adicionar resumo das estatísticas
  doc.setFontSize(14);
  doc.text('Resumo de Atendimentos', 14, 48);
  
  // Tabela de estatísticas
  autoTable(doc, {
    startY: 52,
    head: [['Métrica', 'Valor']],
    body: [
      ['Total de Tickets', stats.totalTickets?.toString() || '0'],
      ['Na Fila', stats.inQueueTickets.toString()],
      ['Em Atendimento', stats.inProgressTickets.toString()],
      ['Concluídos Hoje', stats.completedTickets.toString()],
      ['Cancelados', stats.cancelledTickets?.toString() || '0'],
      ['Tempo Médio de Espera', formatTime(stats.averageWaitTime)],
      ['Tempo Médio de Atendimento', formatTime(averageServiceTime)],
      ['Taxa de Ocupação de Equipamentos', `${equipmentUtilization}%`],
      ['Faturamento Diário', formatCurrency(stats.dailyRevenue)],
      ['Ticket Médio', formatCurrency(averageRevenue)]
    ],
    theme: 'striped',
    headStyles: { fillColor: [31, 82, 107] }, // Cor primária #1F526B
    styles: { fontSize: 10 }
  });
  
  // Obter a posição Y final da última tabela
  // @ts-ignore - Ignorando erro de tipagem do lastAutoTable
  const finalY1 = doc.lastAutoTable?.finalY || 100;
  
  // Adicionar estatísticas por tipo de serviço
  if (Object.keys(serviceStats).length > 0) {
    doc.setFontSize(14);
    doc.text('Desempenho por Tipo de Serviço', 14, finalY1 + 15);
    
    // Dados para a tabela de serviços
    const serviceData = Object.entries(serviceStats).map(([name, data]) => [
      name,
      data.count.toString(),
      formatCurrency(data.revenue),
      formatCurrency(data.revenue / data.count)
    ]);
    
    // Tabela de serviços
    autoTable(doc, {
      startY: finalY1 + 20,
      head: [['Serviço', 'Quantidade', 'Receita Total', 'Valor Médio']],
      body: serviceData,
      theme: 'striped',
      headStyles: { fillColor: [255, 255, 255] }, // Cor secundária #FFFFFF
      styles: { fontSize: 10 }
    });
  }
  
  // Obter a posição Y final da última tabela
  // @ts-ignore - Ignorando erro de tipagem do lastAutoTable
  const finalY2 = doc.lastAutoTable?.finalY || 200;
  
  // Adicionar lista de tickets recentes
  const completedTickets = tickets.filter(ticket => ticket.status === 'completed');
  
  if (completedTickets.length > 0 && includeDetails) {
    doc.setFontSize(14);
    doc.text('Atendimentos Concluídos', 14, finalY2 + 15);
    
    // Dados para a tabela de tickets com campos mais relevantes
    const ticketData = completedTickets.slice(0, 15).map(ticket => {
      // Usar service_name se disponível, senão usar service.name
      const serviceName = ticket.service_name || ticket.service?.name || 'Serviço';
      
      // Usar customer_name se disponível, senão usar customer.name
      const customerName = ticket.customer_name || ticket.customer?.name || 'Cliente';
      
      // Calcular preço total dos serviços
      let totalPrice = 0;
      if (ticket.services && ticket.services.length > 0) {
        totalPrice = ticket.services.reduce((sum, service) => sum + (service.price || 0), 0);
      } else {
        totalPrice = ticket.service?.price || 0;
      }
      
      return [
        ticket.number,
        serviceName,
        customerName,
        formatDateTime(ticket.completedAt || ''),
        formatCurrency(totalPrice)
      ];
    });
    
    // Tabela de tickets
    autoTable(doc, {
      startY: finalY2 + 20,
      head: [['Senha', 'Serviço', 'Cliente', 'Concluído em', 'Valor']],
      body: ticketData,
      theme: 'striped',
      headStyles: { fillColor: [31, 82, 107] }, // Cor primária #1F526B
      styles: { fontSize: 9 }
    });
  }
  
  // Adicionar nova página para gráficos e análises adicionais
  doc.addPage();
  
  // Título da segunda página
  doc.setFontSize(16);
  doc.text('Análise de Desempenho', 14, 20);
  
  // Distribuição de status
  doc.setFontSize(14);
  doc.text('Distribuição de Status', 14, 30);
  
  // Calcular porcentagens para o gráfico
  const total = stats.totalTickets && stats.totalTickets > 0 ? stats.totalTickets : 1;
  const inQueuePercent = Math.round((stats.inQueueTickets / total) * 100);
  const inProgressPercent = Math.round((stats.inProgressTickets / total) * 100);
  const completedPercent = Math.round((stats.completedTickets / total) * 100);
  const cancelledPercent = Math.round(((stats.cancelledTickets || 0) / total) * 100);
  
  // Desenhar barras simples para representar a distribuição
  const barHeight = 15;
  const maxBarWidth = 150;
  
  // Na fila
  doc.setFillColor(70, 130, 180); // SteelBlue
  doc.rect(40, 40, (maxBarWidth * inQueuePercent) / 100, barHeight, 'F');
  doc.text('Na Fila', 14, 50);
  doc.text(`${inQueuePercent}%`, 200, 50, { align: 'right' });
  
  // Em atendimento
  doc.setFillColor(255, 165, 0); // Orange
  doc.rect(40, 60, (maxBarWidth * inProgressPercent) / 100, barHeight, 'F');
  doc.text('Em Atendimento', 14, 70);
  doc.text(`${inProgressPercent}%`, 200, 70, { align: 'right' });
  
  // Concluídos
  doc.setFillColor(46, 139, 87); // SeaGreen
  doc.rect(40, 80, (maxBarWidth * completedPercent) / 100, barHeight, 'F');
  doc.text('Concluídos', 14, 90);
  doc.text(`${completedPercent}%`, 200, 90, { align: 'right' });
  
  // Cancelados
  doc.setFillColor(178, 34, 34); // FireBrick
  doc.rect(40, 100, (maxBarWidth * cancelledPercent) / 100, barHeight, 'F');
  doc.text('Cancelados', 14, 110);
  doc.text(`${cancelledPercent}%`, 200, 110, { align: 'right' });
  
  // Adicionar ocupação de equipamentos
  if (equipment && equipment.length > 0) {
    doc.setFontSize(14);
    doc.text('Ocupação de Equipamentos', 14, 130);
    
    // Agrupar equipamentos por tipo
    const equipmentByType: Record<string, { total: number, available: number, inUse: number, maintenance: number }> = {};
    
    equipment.forEach(eq => {
      const type = eq.type === 'banheira_gelo' ? 'Banheiras de Gelo' : 'Botas de Compressão';
      
      if (!equipmentByType[type]) {
        equipmentByType[type] = { total: 0, available: 0, inUse: 0, maintenance: 0 };
      }
      
      equipmentByType[type].total += 1;
      
      if (eq.status === 'available') equipmentByType[type].available += 1;
      if (eq.status === 'in_use') equipmentByType[type].inUse += 1;
      if (eq.status === 'maintenance') equipmentByType[type].maintenance += 1;
    });
    
    // Dados para a tabela de equipamentos
    const equipmentData = Object.entries(equipmentByType).map(([type, data]) => [
      type,
      data.total.toString(),
      data.available.toString(),
      data.inUse.toString(),
      data.maintenance.toString(),
      `${Math.round((data.inUse / data.total) * 100)}%`
    ]);
    
    // Tabela de equipamentos
    autoTable(doc, {
      startY: 135,
      head: [['Tipo', 'Total', 'Disponíveis', 'Em Uso', 'Manutenção', 'Taxa de Uso']],
      body: equipmentData,
      theme: 'grid',
      headStyles: { fillColor: [26, 58, 74] }, // Cor primária #1A3A4A
      styles: { fontSize: 10 }
    });
  }
  
  // Rodapé
  // @ts-ignore - Ignorando erro de tipagem do internal.getNumberOfPages
  const pageCount = doc.internal.getNumberOfPages();
  doc.setFontSize(8);
  
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    
    doc.text(
      'RecoveryTruck - Sistema de Gerenciamento de Atendimentos',
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );
    
    doc.text(
      `Página ${i} de ${pageCount}`,
      pageWidth - 20,
      pageHeight - 10
    );
  }
  
  // Salvar o PDF
  doc.save('relatorio-atendimentos.pdf');
}; 