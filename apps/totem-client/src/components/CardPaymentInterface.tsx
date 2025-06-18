import React from 'react';
import { motion } from 'framer-motion';
import type { PaymentMethod } from '../types';

interface CardPaymentInterfaceProps {
  paymentMethod: PaymentMethod;
  amount: number;
}

export const CardPaymentInterface: React.FC<CardPaymentInterfaceProps> = ({
  paymentMethod,
  amount,
}) => {
  return (
    <div className="card-payment-interface">
      <div className="mb-6 p-6 bg-white rounded-lg shadow-md flex flex-col items-center">
        <div className="w-full flex justify-center mb-4">
          {paymentMethod === 'credit_card' ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
              <line x1="1" y1="10" x2="23" y2="10"></line>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
              <line x1="1" y1="10" x2="23" y2="10"></line>
              <path d="M4 16h2"></path>
              <path d="M8 16h4"></path>
            </svg>
          )}
        </div>
        
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">
            {paymentMethod === 'credit_card' ? 'Cartão de Crédito' : 'Cartão de Débito'}
          </h3>
          <p className="text-gray-500 mb-4">
            Valor a pagar: <span className="font-bold">R$ {amount.toFixed(2).replace('.', ',')}</span>
          </p>
        </div>
        
        <div className="w-full bg-gray-100 p-4 rounded-lg">
          <div className="flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500 mr-3" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            <span className="text-lg font-medium">Conexão segura</span>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">Instruções:</h3>
        <ol className="text-left list-decimal list-inside space-y-2">
          <li>Insira ou aproxime seu cartão na máquina</li>
          <li>Confirme o valor de R$ {amount.toFixed(2).replace('.', ',')}</li>
          <li>Digite sua senha se solicitado</li>
          <li>Aguarde a aprovação do pagamento</li>
          <li>Retire seu cartão da máquina</li>
        </ol>
      </div>

      <div className="animate-pulse">
        <p className="text-primary font-semibold">
          Aguardando inserção do cartão...
        </p>
      </div>
    </div>
  );
}; 