import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';

import { ServiceCard } from '../components/ServiceCard';
import { Button } from '../components/Button';
import { api } from '../utils/api';
import { useTotemStore } from '../store/totemStore';
import type { Service } from '../types';

const SelectServicePage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, setService, setStep } = useTotemStore();
  const [selected, setSelected] = useState<Service | null>(selectedService);

  // Buscar serviços da API
  const { data: services = [], isLoading, error } = useQuery({
    queryKey: ['services'],
    queryFn: api.getServices,
  });

  // Selecionar um serviço
  const handleSelectService = (service: Service) => {
    setSelected(service);
  };

  // Continuar para a próxima etapa
  const handleContinue = () => {
    if (selected) {
      setService(selected);
      setStep('customer');
      navigate('/customer-info');
    }
  };

  // Voltar para a página inicial
  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="totem-card">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-primary mb-2">
            Selecione o Serviço
          </h2>
          <p className="text-text-light">
            Escolha o serviço de recuperação que você deseja utilizar
          </p>
          <p className="text-sm text-primary mt-2">
            Todos os serviços têm duração de 10 minutos
          </p>
        </div>

        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            <p>Ocorreu um erro ao carregar os serviços. Tente novamente.</p>
          </div>
        )}

        {!isLoading && !error && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {services.map((service) => (
                <ServiceCard
                  key={service.id}
                  service={service}
                  onClick={handleSelectService}
                  isSelected={selected?.id === service.id}
                />
              ))}
            </div>

            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                size="lg"
                onClick={handleBack}
                icon={
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                }
              >
                Voltar
              </Button>

              <Button
                variant="primary"
                size="lg"
                onClick={handleContinue}
                disabled={!selected}
                icon={
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                }
                iconPosition="right"
              >
                Continuar
              </Button>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default SelectServicePage; 