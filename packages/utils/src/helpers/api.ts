import { getAuthToken, logout } from './auth';
import axios from 'axios';

/**
 * Configuração base para requisições API
 */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore - import.meta.env disponível em projetos Vite
const isDev = (import.meta as any).env?.DEV === true;
export const API_URL = isDev 
  ? '/api' // Usar proxy em desenvolvimento
  : ((import.meta as any).env?.VITE_API_URL || 'http://localhost:8000');

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
  
  // Sempre setar Content-Type: application/json quando houver body
  if (!headers.has('Content-Type') && fetchOptions.body) {
    headers.set('Content-Type', 'application/json');
  }
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
  
  // Header de Tenant (se existir)
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore - Tipagem ImportMeta fora do contexto Vite
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID as string | "7f02a566-2406-436d-b10d-90ecddd3fe2d";
  if (tenantId && !headers.has('X-Tenant-Id')) {
    headers.set('X-Tenant-Id', tenantId);
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
    
    // Logout automático se token inválido/expirado
    if (response.status === 401) {
      logout();
      // Opcional: emitir evento para redirecionar
      window.dispatchEvent(new CustomEvent('auth:logout'));
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
 * Instância do axios configurada com interceptors para autenticação
 */
export const api = axios.create({
  baseURL: API_URL,
});

// Interceptor para adicionar headers de autenticação e tenant
api.interceptors.request.use(
  (config) => {
    // Adicionar token de autenticação
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Adicionar header de tenant
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore - Tipagem ImportMeta fora do contexto Vite
    const tenantId = (import.meta as any).env?.VITE_TENANT_ID as string | "7f02a566-2406-436d-b10d-90ecddd3fe2d";
    if (tenantId && !config.headers['X-Tenant-Id']) {
      config.headers['X-Tenant-Id'] = tenantId;
    }
    
    // Sempre incluir Content-Type se não estiver definido
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    // ✅ NOVO: Logs detalhados para debug
    console.log('🔍 DEBUG - Axios Request Interceptor:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      params: config.params,
      data: config.data
    });
    
    return config;
  },
  (error) => {
    console.error('❌ ERRO - Axios Request Interceptor Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros de autenticação
api.interceptors.response.use(
  (response) => {
    // ✅ NOVO: Logs detalhados para debug
    console.log('🔍 DEBUG - Axios Response Interceptor:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    
    return response;
  },
  (error) => {
    // ✅ NOVO: Logs detalhados para debug
    console.error('❌ ERRO - Axios Response Interceptor Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    
    // Logout automático se token inválido/expirado
    if (error.response?.status === 401) {
      logout();
      // Emitir evento para redirecionar
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    
    // Tratamento específico para erros de CORS
    if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      console.error('Erro de CORS detectado. Verifique se o servidor está configurado corretamente.');
      // Emitir evento para notificar sobre erro de CORS
      window.dispatchEvent(new CustomEvent('cors:error', { 
        detail: { 
          message: 'Erro de conexão com o servidor. Verifique sua conexão com a internet.',
          originalError: error 
        } 
      }));
    }
    
    return Promise.reject(error);
  }
); 