import React from 'react';
import { motion } from 'framer-motion';
import type { Service } from '../types';

interface ServiceCardProps {
  service: Service;
  onClick: (service: Service) => void;
  isSelected?: boolean;
}

// Componente para renderizar o ícone do serviço
const ServiceIcon: React.FC<{ slug: string }> = ({ slug }) => {
  switch (slug) {
    case 'banheira-gelo':
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-6 w-6 text-white" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" 
          />
        </svg>
      );
    case 'bota-compressao':
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-6 w-6 text-white" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" 
          />
        </svg>
      );
    case 'massagem-terapeutica':
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-6 w-6 text-white" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" 
          />
        </svg>
      );
    default:
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-6 w-6 text-white" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M13 10V3L4 14h7v7l9-11h-7z" 
          />
        </svg>
      );
  }
};

export const ServiceCard: React.FC<ServiceCardProps> = ({ 
  service, 
  onClick, 
  isSelected = false 
}) => {
  // Usar as cores da nova paleta com base no slug do serviço
  let serviceColor = '#1A3A4A'; // Cor padrão (primary)
  
  if (service.slug === 'bota-compressao') {
    serviceColor = '#8AE65C'; // Cor secundária
  }

  const handleClick = () => {
    onClick(service);
  };

  return (
    <motion.div
      className={`
        p-6 rounded-2xl shadow-md cursor-pointer transition-all
        ${isSelected 
          ? 'border-4 shadow-lg scale-[1.02]' 
          : 'border border-gray-200 hover:shadow-lg hover:scale-[1.01]'
        }
      `}
      style={{
        backgroundColor: `${serviceColor}10`, // Cor com 10% de opacidade
        borderColor: isSelected ? serviceColor : undefined,
      }}
      onClick={handleClick}
      whileHover={{ scale: isSelected ? 1.02 : 1.01 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex flex-col h-full">
        <div className="mb-4">
          <div 
            className="w-12 h-12 rounded-full mb-3 flex items-center justify-center"
            style={{ backgroundColor: serviceColor }}
          >
            <ServiceIcon slug={service.slug} />
          </div>
          <h3 className="text-xl font-bold mb-2">{service.name}</h3>
          <p className="text-text-light mb-4">{service.description}</p>
        </div>
        
        <div className="mt-auto flex justify-between items-center">
          <div className="flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-5 w-5 text-text-light mr-1" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
            <span className="text-text-light">{service.duration} min</span>
          </div>
          
          <span className="text-xl font-bold">
            R$ {service.price.toFixed(2).replace('.', ',')}
          </span>
        </div>
      </div>
    </motion.div>
  );
}; 