import React, { useEffect, useState } from 'react';
import { checkApiHealth, getCorsInfo } from '../utils/api-config';

interface ErrorHandlerProps {
  children: React.ReactNode;
}

export const ErrorHandler: React.FC<ErrorHandlerProps> = ({ children }) => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Verificar status da API ao carregar
    const checkApi = async () => {
      try {
        const isHealthy = await checkApiHealth();
        setApiStatus(isHealthy ? 'online' : 'offline');
        if (!isHealthy) {
          setError('Servidor não está respondendo. Verifique sua conexão.');
        }
      } catch (err) {
        setApiStatus('offline');
        setError('Erro ao conectar com o servidor.');
      }
    };

    checkApi();

    // Listener para erros de CORS
    const handleCorsError = (event: CustomEvent) => {
      console.error('Erro de CORS detectado:', event.detail);
      setError(event.detail.message || 'Erro de conexão com o servidor.');
    };

    // Listener para erros do servidor
    const handleServerError = (event: CustomEvent) => {
      console.error('Erro do servidor detectado:', event.detail);
      setError(event.detail.message || 'Erro interno do servidor.');
    };

    window.addEventListener('cors:error', handleCorsError as EventListener);
    window.addEventListener('server:error', handleServerError as EventListener);

    return () => {
      window.removeEventListener('cors:error', handleCorsError as EventListener);
      window.removeEventListener('server:error', handleServerError as EventListener);
    };
  }, []);

  const handleRetry = () => {
    setApiStatus('checking');
    setError(null);
    window.location.reload();
  };

  const handleDebug = () => {
    const corsInfo = getCorsInfo();
    console.log('Informações de CORS:', corsInfo);
    alert(`Informações de CORS:\n${JSON.stringify(corsInfo, null, 2)}`);
  };

  if (apiStatus === 'offline' || error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-800 mb-4">
              Erro de Conexão
            </h1>
            <p className="text-gray-600 mb-6">
              {error || 'Não foi possível conectar com o servidor. Verifique sua conexão com a internet.'}
            </p>
            
            <div className="space-y-3">
              <button
                onClick={handleRetry}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Tentar Novamente
              </button>
              
              <button
                onClick={handleDebug}
                className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg text-sm hover:bg-gray-300 transition-colors"
              >
                Informações de Debug
              </button>
            </div>
            
            <div className="mt-6 text-xs text-gray-500">
              <p>Status da API: {apiStatus}</p>
              <p>URL: {import.meta.env.VITE_API_URL}</p>
              <p>Tenant: {import.meta.env.VITE_TENANT_ID}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (apiStatus === 'checking') {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando conexão...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}; 