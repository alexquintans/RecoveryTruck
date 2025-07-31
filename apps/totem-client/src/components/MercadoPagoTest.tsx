import React, { useEffect, useState } from 'react';

interface MercadoPagoTestProps {
  preferenceId: string;
  publicKey: string;
}

const MercadoPagoTest: React.FC<MercadoPagoTestProps> = ({ preferenceId, publicKey }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔍 MercadoPagoTest - Iniciando teste...');
    console.log('🔍 MercadoPagoTest - Props:', { preferenceId, publicKey });

    // Verificar se o SDK está disponível
    if (typeof window === 'undefined' || !window.MercadoPago) {
      console.error('❌ MercadoPagoTest - SDK não disponível');
      setError('SDK do Mercado Pago não foi carregado');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🔍 MercadoPagoTest - SDK encontrado, criando instância...');
      const mp = new window.MercadoPago(publicKey, {
        locale: 'pt-BR'
      });

      console.log('🔍 MercadoPagoTest - Configurando checkout...');
      
      // Configuração mais simples possível
      mp.checkout({
        preference: {
          id: preferenceId
        },
        render: {
          container: '.cho-container',
          label: 'Pagar com Mercado Pago',
        },
        callbacks: {
          onSuccess: (data: any) => {
            console.log('✅ Pagamento aprovado:', data);
          },
          onError: (error: any) => {
            console.error('❌ Erro no pagamento:', error);
          },
          onCancel: () => {
            console.log('🚫 Pagamento cancelado');
          }
        }
      });

      setIsLoading(false);
      console.log('✅ MercadoPagoTest - Checkout configurado com sucesso');
    } catch (err) {
      console.error('❌ MercadoPagoTest - Erro ao configurar checkout:', err);
      setError('Erro ao configurar checkout');
      setIsLoading(false);
    }
  }, [preferenceId, publicKey]);

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-red-800 font-semibold mb-2">Erro no Teste</h3>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-600 mr-2"></div>
          <span className="text-blue-800 text-sm">Carregando interface de pagamento...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
      <h3 className="text-green-800 font-semibold mb-2">Teste do Mercado Pago</h3>
      <p className="text-green-600 text-sm mb-4">
        Interface de pagamento configurada. Verifique o console para logs.
      </p>
      
      {/* Container onde o iframe será renderizado */}
      <div className="cho-container min-h-[400px] border-2 border-dashed border-gray-300 rounded-lg p-4">
        <p className="text-gray-500 text-center">
          O iframe do Mercado Pago deve aparecer aqui...
        </p>
      </div>
      
      <div className="mt-4 text-xs text-gray-600">
        <p><strong>Preference ID:</strong> {preferenceId}</p>
        <p><strong>Public Key:</strong> {publicKey.substring(0, 20)}...</p>
      </div>
    </div>
  );
};

export default MercadoPagoTest; 