import { getAuthToken } from './auth';

/**
 * Configuração base para requisições API
 */
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Opções para requisições fetch
 */
interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
  withAuth?: boolean;
}

/**
 * Realiza uma requisição HTTP usando fetch com suporte a autenticação
 */
export async function fetchApi<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { params, withAuth = true, ...fetchOptions } = options;
  
  // Constrói a URL com query params
  let url = `${API_URL}${endpoint}`;
  
  if (params) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      queryParams.append(key, String(value));
    });
    url += `?${queryParams.toString()}`;
  }
  
  // Configura os headers
  const headers = new Headers(fetchOptions.headers);
  
  if (!headers.has('Content-Type') && !fetchOptions.body) {
    headers.set('Content-Type', 'application/json');
  }
  
  // Adiciona o token de autenticação se necessário
  if (withAuth) {
    const token = getAuthToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }
  
  // Realiza a requisição
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });
  
  // Verifica se a resposta foi bem-sucedida
  if (!response.ok) {
    let errorData;
    
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { message: response.statusText };
    }
    
    const error = new Error(errorData.message || 'Erro na requisição');
    (error as any).status = response.status;
    (error as any).data = errorData;
    
    throw error;
  }
  
  // Retorna os dados da resposta
  return response.json();
}

/**
 * Métodos HTTP para facilitar o uso
 */
export const api = {
  get: <T = any>(endpoint: string, options?: FetchOptions) => 
    fetchApi<T>(endpoint, { ...options, method: 'GET' }),
    
  post: <T = any>(endpoint: string, data?: any, options?: FetchOptions) => 
    fetchApi<T>(endpoint, { 
      ...options, 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined 
    }),
    
  put: <T = any>(endpoint: string, data?: any, options?: FetchOptions) => 
    fetchApi<T>(endpoint, { 
      ...options, 
      method: 'PUT', 
      body: data ? JSON.stringify(data) : undefined 
    }),
    
  patch: <T = any>(endpoint: string, data?: any, options?: FetchOptions) => 
    fetchApi<T>(endpoint, { 
      ...options, 
      method: 'PATCH', 
      body: data ? JSON.stringify(data) : undefined 
    }),
    
  delete: <T = any>(endpoint: string, options?: FetchOptions) => 
    fetchApi<T>(endpoint, { ...options, method: 'DELETE' }),
}; 