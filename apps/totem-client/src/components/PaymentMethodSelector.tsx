import React from 'react';
import { motion } from 'framer-motion';
import type { PaymentMethod } from '../types';

interface PaymentMethodSelectorProps {
  selectedMethod: PaymentMethod | null;
  onSelect: (method: PaymentMethod) => void;
  availableMethods?: PaymentMethod[]; // lista permitida segundo config
}

export const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  selectedMethod,
  onSelect,
  availableMethods,
}) => {
  const paymentMethods = [
    {
      id: 'credit_card',
      name: 'Cartão de Crédito',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
          <line x1="1" y1="10" x2="23" y2="10"></line>
        </svg>
      ),
      description: 'Pague com seu cartão de crédito',
    },
    {
      id: 'debit_card',
      name: 'Cartão de Débito',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
          <line x1="1" y1="10" x2="23" y2="10"></line>
          <path d="M4 16h2"></path>
          <path d="M8 16h4"></path>
        </svg>
      ),
      description: 'Pague com seu cartão de débito',
    },
    {
      id: 'pix',
      name: 'PIX',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19.5 3.75H4.5C4.08579 3.75 3.75 4.08579 3.75 4.5V19.5C3.75 19.9142 4.08579 20.25 4.5 20.25H19.5C19.9142 20.25 20.25 19.9142 20.25 19.5V4.5C20.25 4.08579 19.9142 3.75 19.5 3.75Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8.25 7.5L12 11.25L15.75 7.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M8.25 16.5L12 12.75L15.75 16.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      description: 'Pague instantaneamente com PIX',
    },
    {
      id: 'mercadopago',
      name: 'Mercado Pago',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <text x="12" y="16" textAnchor="middle" fontSize="8">MP</text>
        </svg>
      ),
      description: 'Checkout Pro do Mercado Pago',
    },
    {
      id: 'sicredi',
      name: 'Maquininha Sicredi',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M8 15h8" />
          <path d="M9 11h6" />
        </svg>
      ),
      description: 'Pague usando a maquininha física',
    },
  ];

  // Filtrar métodos pela configuração, se fornecida
  const methodsToShow = availableMethods && availableMethods.length > 0
    ? paymentMethods.filter((m) => availableMethods.includes(m.id as PaymentMethod))
    : paymentMethods;

  return (
    <div className="payment-method-selector">
      <h3 className="text-xl font-semibold mb-4">Escolha como deseja pagar:</h3>
      
      <div className="grid grid-cols-1 gap-4">
        {methodsToShow.map((method) => (
          <motion.div
            key={method.id}
            className={`p-4 border-2 rounded-xl cursor-pointer transition-colors ${
              selectedMethod === method.id
                ? 'border-primary bg-primary/10'
                : 'border-gray-200 hover:border-primary/50'
            }`}
            onClick={() => onSelect(method.id as PaymentMethod)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center">
              <div className={`mr-4 text-${selectedMethod === method.id ? 'primary' : 'gray-500'}`}>
                {method.icon}
              </div>
              <div>
                <h4 className="text-lg font-medium">{method.name}</h4>
                <p className="text-sm text-gray-500">{method.description}</p>
              </div>
              <div className="ml-auto">
                {selectedMethod === method.id && (
                  <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}; 