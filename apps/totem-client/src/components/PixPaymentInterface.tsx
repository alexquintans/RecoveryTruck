import React from 'react';

interface PixPaymentInterfaceProps {
  qrCodeUrl: string | null;
  amount: number;
}

export const PixPaymentInterface: React.FC<PixPaymentInterfaceProps> = ({
  qrCodeUrl,
  amount,
}) => {
  return (
    <div className="pix-payment-interface">
      {qrCodeUrl ? (
        <div className="mb-6 p-4 bg-white rounded-lg shadow-md">
          <img 
            src={qrCodeUrl} 
            alt="QR Code de Pagamento PIX" 
            className="w-64 h-64 mx-auto"
            onError={(e) => {
              // Fallback para QR code genérico
              const target = e.target as HTMLImageElement;
              target.src = 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=PIXFallback';
            }}
          />
        </div>
      ) : (
        <div className="mb-6 p-4 bg-white rounded-lg shadow-md flex items-center justify-center w-64 h-64 mx-auto">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
        </div>
      )}

      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold mb-2">
          Pagamento via PIX
        </h3>
        <p className="text-gray-500 mb-4">
          Valor a pagar: <span className="font-bold">R$ {amount.toFixed(2).replace('.', ',')}</span>
        </p>
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">Instruções:</h3>
        <ol className="text-left list-decimal list-inside space-y-2">
          <li>Abra o aplicativo do seu banco</li>
          <li>Selecione a opção "Pagar com PIX"</li>
          <li>Escaneie o QR Code acima</li>
          <li>Confirme o valor de R$ {amount.toFixed(2).replace('.', ',')}</li>
          <li>Confirme o pagamento</li>
        </ol>
      </div>

      <div className="animate-pulse">
        <p className="text-primary font-semibold">
          Aguardando pagamento...
        </p>
      </div>
    </div>
  );
}; 