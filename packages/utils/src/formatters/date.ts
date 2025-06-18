import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

/**
 * Formata uma data para o formato brasileiro (DD/MM/YYYY)
 */
export function formatDate(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'dd/MM/yyyy', { locale: ptBR });
}

/**
 * Formata uma data com hora para o formato brasileiro (DD/MM/YYYY HH:mm)
 */
export function formatDateTime(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'dd/MM/yyyy HH:mm', { locale: ptBR });
}

/**
 * Formata uma data para exibir apenas a hora (HH:mm)
 */
export function formatTime(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'HH:mm', { locale: ptBR });
}

/**
 * Formata uma data para exibir o dia da semana e a data (segunda-feira, 01/01/2023)
 */
export function formatDateWithWeekday(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, "EEEE, dd/MM/yyyy", { locale: ptBR });
}

/**
 * Formata uma data para exibir o tempo relativo (há 5 minutos, há 2 horas)
 */
export function formatRelativeTime(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - parsedDate.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'agora mesmo';
  }
  
  if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `há ${minutes} ${minutes === 1 ? 'minuto' : 'minutos'}`;
  }
  
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `há ${hours} ${hours === 1 ? 'hora' : 'horas'}`;
  }
  
  const days = Math.floor(diffInSeconds / 86400);
  return `há ${days} ${days === 1 ? 'dia' : 'dias'}`;
} 