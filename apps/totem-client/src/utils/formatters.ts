/**
 * Formata um CPF (000.000.000-00)
 * @param value Valor a ser formatado
 * @returns CPF formatado
 */
export const formatCPF = (value: string): string => {
  const digits = value.replace(/\D/g, '');
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9, 11)}`;
};

/**
 * Formata um telefone brasileiro ((00) 00000-0000)
 * @param value Valor a ser formatado
 * @returns Telefone formatado
 */
export const formatPhone = (value: string): string => {
  const digits = value.replace(/\D/g, '');
  if (digits.length <= 2) return digits;
  if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7, 11)}`;
};

/**
 * Formata um valor monetário (R$ 0,00)
 * @param value Valor a ser formatado
 * @param currency Símbolo da moeda (padrão: R$)
 * @returns Valor formatado
 */
export const formatCurrency = (value: number, currency = 'R$'): string => {
  return `${currency} ${value.toFixed(2).replace('.', ',')}`;
};

/**
 * Formata uma data (DD/MM/YYYY HH:MM)
 * @param dateString Data a ser formatada
 * @returns Data formatada
 */
export const formatDate = (dateString: string): string => {
  try {
  const date = new Date(dateString);
    
    // Verificar se a data é válida
    if (isNaN(date.getTime())) {
      console.warn('formatDate: Data inválida recebida:', dateString);
      return 'Data não disponível';
    }
    
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
  } catch (error) {
    console.error('formatDate: Erro ao formatar data:', dateString, error);
    return 'Data não disponível';
  }
};

/**
 * Formata uma data curta (DD/MM/YYYY)
 * @param dateString Data a ser formatada
 * @returns Data formatada
 */
export const formatShortDate = (dateString: string): string => {
  try {
  const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn('formatShortDate: Data inválida recebida:', dateString);
      return 'Data não disponível';
    }
    
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
  } catch (error) {
    console.error('formatShortDate: Erro ao formatar data:', dateString, error);
    return 'Data não disponível';
  }
};

/**
 * Formata um horário (HH:MM)
 * @param dateString Data a ser formatada
 * @returns Horário formatado
 */
export const formatTime = (dateString: string): string => {
  try {
  const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      console.warn('formatTime: Data inválida recebida:', dateString);
      return 'Horário não disponível';
    }
    
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
  } catch (error) {
    console.error('formatTime: Erro ao formatar horário:', dateString, error);
    return 'Horário não disponível';
  }
}; 