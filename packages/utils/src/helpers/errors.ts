/**
 * Interface para erros da API
 */
export interface ApiError {
  status: number;
  message: string;
  data?: any;
}

/**
 * Verifica se um objeto é um erro da API
 */
export function isApiError(error: any): error is ApiError {
  return (
    error &&
    typeof error === 'object' &&
    'status' in error &&
    'message' in error
  );
}

/**
 * Obtém uma mensagem amigável para o usuário com base no erro
 */
export function getErrorMessage(error: unknown): string {
  // Se for um erro da API, usa a mensagem retornada
  if (isApiError(error)) {
    return error.message;
  }
  
  // Se for um erro do JavaScript
  if (error instanceof Error) {
    return error.message;
  }
  
  // Para outros tipos de erro
  return 'Ocorreu um erro inesperado';
}

/**
 * Obtém uma mensagem específica para erros de autenticação
 */
export function getAuthErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    if (error.status === 401) {
      return 'Sua sessão expirou. Por favor, faça login novamente.';
    }
    
    if (error.status === 403) {
      return 'Você não tem permissão para acessar este recurso.';
    }
    
    return error.message;
  }
  
  return getErrorMessage(error);
}

/**
 * Registra erros no console e/ou serviço de monitoramento
 */
export function logError(error: unknown, context?: string): void {
  // Adiciona contexto ao erro
  const contextPrefix = context ? `[${context}] ` : '';
  
  if (isApiError(error)) {
    console.error(`${contextPrefix}API Error (${error.status}):`, error.message, error.data);
  } else if (error instanceof Error) {
    console.error(`${contextPrefix}Error:`, error.message, error.stack);
  } else {
    console.error(`${contextPrefix}Unknown Error:`, error);
  }
  
  // Aqui poderia enviar para um serviço de monitoramento como Sentry
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   window.Sentry.captureException(error, { extra: { context } });
  // }
} 