import React, { useEffect, useState } from 'react';

interface MercadoPagoQRCodeProps {
  qrCodeUrl: string;
  amount: number;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

const MercadoPagoQRCode: React.FC<MercadoPagoQRCodeProps> = ({ 
  qrCodeUrl, 
  amount,
  onSuccess, 
  onError, 
  onCancel 
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (qrCodeUrl) {
      setIsLoading(false);
    }
  }, [qrCodeUrl]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="text-red-500 mb-4">
          <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Erro no Pagamento</h3>
        <p className="text-sm text-red-600 text-center mb-6">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors font-medium"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mb-4"></div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Carregando QR Code</h3>
        <p className="text-sm text-gray-600 text-center">Preparando pagamento PIX...</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="bg-white rounded-xl shadow-xl p-8 border border-gray-100">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">
            Pagamento PIX
          </h3>
          <p className="text-3xl font-bold text-blue-600 mb-2">
            R$ {amount.toFixed(2)}
          </p>
          <p className="text-sm text-gray-600">
            Escaneie o QR Code com seu app bancário
          </p>
        </div>
        
        {/* QR Code */}
        <div className="flex justify-center mb-6">
          <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
            <img 
              src={qrCodeUrl} 
              alt="QR Code PIX" 
              className="w-64 h-64 object-contain"
              onError={() => setError('Erro ao carregar QR Code')}
            />
          </div>
        </div>
        
        {/* Instruções */}
        <div className="text-center mb-6">
          <div className="bg-blue-50 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-blue-800 mb-2">Como pagar:</h4>
            <ol className="text-sm text-blue-700 text-left space-y-1">
              <li>1. Abra seu app bancário</li>
              <li>2. Escolha a opção "PIX"</li>
              <li>3. Escaneie o QR Code acima</li>
              <li>4. Confirme o pagamento</li>
            </ol>
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500 mb-2">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>Pagamento processado com segurança pelo Mercado Pago</span>
          </div>
          <div className="flex items-center justify-center gap-1 text-xs text-gray-400">
            <span>© 2025 RecoveryTruck</span>
            <span>•</span>
            <span>Pagamento 100% seguro</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MercadoPagoQRCode; 