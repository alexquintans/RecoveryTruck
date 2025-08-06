import axios from 'axios';

// Configuração da API para o totem-client
const API_URL = import.meta.env.VITE_API_URL || 'https://recoverytruck-production.up.railway.app';

// Instância do axios configurada especificamente para o totem-client
export const totemApi = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor para adicionar headers necessários
totemApi.interceptors.request.use(
  (config) => {
    // Adicionar header de tenant
    const tenantId = import.meta.env.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
    if (tenantId) {
      config.headers['X-Tenant-Id'] = tenantId;
    }
    
    // Adicionar headers para CORS
    config.headers['Origin'] = window.location.origin;
    
    return config;
  },
  (error) => {
    console.error('Erro na requisição:', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros
totemApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Erro na resposta:', error);
    
    // Tratamento específico para erros de CORS
    if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      console.error('Erro de CORS detectado:', {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers,
      });
      
      // Emitir evento para notificar sobre erro de CORS
      window.dispatchEvent(new CustomEvent('cors:error', {
        detail: {
          message: 'Erro de conexão com o servidor. Verifique sua conexão com a internet.',
          originalError: error,
          url: error.config?.url,
        }
      }));
    }
    
    // Tratamento para erro 500
    if (error.response?.status === 500) {
      console.error('Erro interno do servidor:', error.response.data);
      window.dispatchEvent(new CustomEvent('server:error', {
        detail: {
          message: 'Erro interno do servidor. Tente novamente em alguns instantes.',
          originalError: error,
        }
      }));
    }
    
    return Promise.reject(error);
  }
);

// Função para verificar se a API está acessível
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await totemApi.get('/health', { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.error('API não está acessível:', error);
    return false;
  }
};

// Função para obter informações de CORS
export const getCorsInfo = () => {
  return {
    origin: window.location.origin,
    apiUrl: API_URL,
    tenantId: import.meta.env.VITE_TENANT_ID,
    userAgent: navigator.userAgent,
  };
}; 