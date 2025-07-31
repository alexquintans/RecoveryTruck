import React, { useEffect, useState, useCallback } from 'react';
import { initMercadoPago, Payment } from '@mercadopago/sdk-react';

interface MercadoPagoPaymentReactProps {
  preferenceId: string;
  publicKey: string;
  amount: number;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

const MercadoPagoPaymentReact: React.FC<MercadoPagoPaymentReactProps> = ({ 
  preferenceId, 
  publicKey, 
  amount,
  onSuccess, 
  onError, 
  onCancel 
}) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Inicializar SDK do Mercado Pago React
  useEffect(() => {
    try {
      initMercadoPago(publicKey);
      setIsInitialized(true);
      console.log('✅ SDK React Mercado Pago inicializado');
    } catch (err) {
      console.error('❌ Erro ao inicializar SDK React:', err);
      setError('Erro ao carregar interface de pagamento');
      onError?.('Erro ao inicializar SDK React');
    }
  }, [publicKey, onError]);

  // Callbacks do Payment Brick
  const initialization = useCallback(() => {
    return {
      amount: amount,
      preferenceId: preferenceId,
    };
  }, [amount, preferenceId]);

  const onReady = useCallback(() => {
    console.log('✅ Payment Brick pronto');
  }, []);

  const onSubmit = useCallback(({ formData }: any) => {
    console.log('📤 Formulário enviado:', formData);
    // O SDK vai processar automaticamente
  }, []);

  const onErrorCallback = useCallback((error: any) => {
    console.error('❌ Erro no Payment Brick:', error);
    setError('Erro ao processar pagamento. Tente novamente.');
    onError?.(error.message || 'Erro desconhecido');
  }, [onError]);

  const onBinChange = useCallback(({ bin }: any) => {
    console.log('💳 BIN alterado:', bin);
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="text-red-500 mb-4">
          <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <p className="text-sm text-red-600 text-center mb-4">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary-dark transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (!isInitialized) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mb-4"></div>
        <p className="text-sm text-text-light">Carregando Payment Brick...</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Pagamento Seguro - R$ {amount.toFixed(2)}
          </h3>
          <p className="text-sm text-gray-600">
            Escolha sua forma de pagamento preferida
          </p>
        </div>
        
        <Payment
          initialization={initialization}
          onReady={onReady}
          onSubmit={onSubmit}
          onError={onErrorCallback}
          onBinChange={onBinChange}
          locale="pt-BR"
          customization={{
            visual: {
              style: {
                theme: 'default'
              }
            },
            paymentMethods: {
              creditCard: 'all',
              debitCard: 'all',
              bankTransfer: 'all',
              ticket: 'all'
            }
          }}
        />
        
        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>Pagamento processado com segurança pelo Mercado Pago</p>
        </div>
      </div>
    </div>
  );
};

export default MercadoPagoPaymentReact; 