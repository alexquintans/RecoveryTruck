import React, { useEffect, useState, useRef } from 'react';

declare global {
  interface Window {
    MercadoPago: any;
  }
}

interface MercadoPagoPaymentProps {
  preferenceId: string;
  publicKey: string;
  amount: number;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

const MercadoPagoPayment: React.FC<MercadoPagoPaymentProps> = ({ 
  preferenceId, 
  publicKey, 
  amount,
  onSuccess, 
  onError, 
  onCancel 
}) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const mpInstanceRef = useRef<any>(null);

  // Debug: verificar props (reduzido)
  if (import.meta.env.DEV) {
    console.log('🔍 MercadoPagoPayment - Props:', { 
      hasPreferenceId: !!preferenceId, 
      hasPublicKey: !!publicKey, 
      amount 
    });
  }

  // Inicializar SDK do Mercado Pago
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('🔍 MercadoPagoPayment - Iniciando inicialização...');
    }
    
    // Verificar se as props necessárias estão presentes
    if (!preferenceId || !publicKey) {
      console.error('❌ MercadoPagoPayment - Props inválidas:', { preferenceId, publicKey });
      setError('Configuração de pagamento inválida');
      onError?.('Configuração de pagamento inválida');
      setIsLoading(false);
      return;
    }

    // Verificar se o SDK está disponível
    if (typeof window === 'undefined' || !window.MercadoPago) {
      console.error('❌ MercadoPagoPayment - SDK não disponível');
      setError('SDK do Mercado Pago não foi carregado. Recarregue a página.');
      onError?.('SDK do Mercado Pago não foi carregado');
      setIsLoading(false);
      return;
    }

    // Função para inicializar o SDK
    const initializeSDK = () => {
      try {
        console.log('🔍 MercadoPagoPayment - SDK encontrado, criando instância...');
        const mp = new window.MercadoPago(publicKey, {
          locale: 'pt-BR'
        });
        mpInstanceRef.current = mp;

        console.log('🔍 MercadoPagoPayment - Configurando checkout...');
        
        // Configurar checkout com preferência - versão corrigida
        mp.checkout({
          preference: {
            id: preferenceId
          },
          render: {
            container: '.cho-container',
            label: 'Pagar com Mercado Pago',
            type: 'button', // Usar button para renderizar o botão automaticamente
          },
          callbacks: {
            onSuccess: (data: any) => {
              console.log('✅ Pagamento aprovado:', data);
              setIsProcessing(true);
              onSuccess?.(data);
            },
            onError: (error: any) => {
              console.error('❌ Erro no pagamento:', error);
              setError('Erro ao processar pagamento. Tente novamente.');
              onError?.(error.message || 'Erro desconhecido');
            },
            onCancel: () => {
              console.log('🚫 Pagamento cancelado pelo usuário');
              onCancel?.();
            }
          }
        });

        setIsInitialized(true);
        setIsLoading(false);
        console.log('✅ SDK Mercado Pago inicializado com sucesso');
      } catch (err) {
        console.error('❌ Erro ao inicializar SDK:', err);
        setError('Erro ao carregar interface de pagamento');
        onError?.('Erro ao inicializar SDK');
        setIsLoading(false);
      }
    };

    // Aguardar um pouco para garantir que o DOM está pronto
    const timer = setTimeout(initializeSDK, 100);

    // Cleanup function
    return () => {
      clearTimeout(timer);
      if (mpInstanceRef.current) {
        mpInstanceRef.current = null;
      }
    };
  }, [publicKey, preferenceId, onSuccess, onError, onCancel]);

  // Adicionar estilos CSS customizados para o botão do Mercado Pago
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .cho-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
      }
      
      .cho-container button {
        background: linear-gradient(135deg, #009ee3 0%, #0077cc 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        color: white !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 16px 32px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(0, 158, 227, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
        min-width: 280px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 12px !important;
      }
      
      .cho-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(0, 158, 227, 0.4) !important;
        background: linear-gradient(135deg, #0077cc 0%, #005fa3 100%) !important;
      }
      
      .cho-container button:active {
        transform: translateY(0) !important;
        box-shadow: 0 4px 15px rgba(0, 158, 227, 0.3) !important;
      }
      
      .cho-container button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
        transition: left 0.5s !important;
      }
      
      .cho-container button:hover::before {
        left: 100% !important;
      }
      
      .cho-container button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 158, 227, 0.3) !important;
      }
      
      /* Animação de pulso para o botão */
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
      }
      
      .cho-container button {
        animation: pulse 2s infinite !important;
      }
      
      .cho-container button:hover {
        animation: none !important;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="relative">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">Erro no Pagamento</h3>
        <p className="text-sm text-red-600 text-center mb-6 max-w-sm">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl text-sm hover:from-red-600 hover:to-red-700 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (isLoading || !isInitialized) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="relative">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mb-4"></div>
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-400 animate-ping"></div>
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">Carregando Pagamento</h3>
        <p className="text-sm text-gray-600 text-center">Preparando interface de pagamento...</p>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="relative">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-200 border-t-green-600 mb-4"></div>
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-green-400 animate-ping"></div>
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">Processando Pagamento</h3>
        <p className="text-sm text-gray-600 text-center">Aguarde enquanto confirmamos seu pagamento...</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Card principal com gradiente */}
      <div className="relative overflow-hidden bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-3xl shadow-2xl border border-blue-100 p-8">
        {/* Efeito de brilho no fundo */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full opacity-10 blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full opacity-10 blur-3xl"></div>
        
        {/* Header com ícone animado */}
        <div className="text-center mb-8 relative z-10">
          <div className="relative inline-block mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            {/* Anel animado */}
            <div className="absolute inset-0 rounded-full border-2 border-blue-300 animate-ping"></div>
          </div>
          
          <h3 className="text-2xl font-bold text-gray-800 mb-3">
            Pagamento Seguro
          </h3>
          
          {/* Valor destacado */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-2xl inline-block mb-4 shadow-lg">
            <p className="text-3xl font-bold">
              R$ {amount.toFixed(2).replace('.', ',')}
            </p>
          </div>
          
          <p className="text-sm text-gray-600 leading-relaxed">
            Clique no botão abaixo para pagar com Mercado Pago
          </p>
        </div>
        
        {/* Container para o SDK do Mercado Pago */}
        <div className="mb-8 relative z-10">
          <div className="cho-container"></div>
        </div>
        
        {/* Footer com informações de segurança */}
        <div className="text-center relative z-10">
          {/* Badge de segurança */}
          <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-full text-xs font-medium mb-4 border border-green-200">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            <span>Pagamento processado com segurança pelo Mercado Pago</span>
          </div>
          
          {/* Informações da empresa */}
          <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
            <span className="font-medium">© 2025 RecoveryTruck</span>
            <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
            <span>Pagamento 100% seguro</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MercadoPagoPayment; 