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
  const [selected, setSelected] = useState<Service[]>(selectedService ? [selectedService] : []);

  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';
  const { data: operationConfig, isLoading, error } = useQuery({
    queryKey: ['operationConfig', tenantId],
    queryFn: () => api.getOperationConfig(tenantId),
  });
  const services = (operationConfig?.services || []).filter((s: any) => s.active);

  // Selecionar/deselecionar múltiplos serviços
  const handleSelectService = (service: Service) => {
    setSelected((prev) => {
      const alreadySelected = prev.some((s) => s.id === service.id);
      if (alreadySelected) {
        return prev.filter((s) => s.id !== service.id);
      } else {
        return [...prev, service];
      }
    });
  };

  // Continuar para a próxima etapa
  const handleContinue = () => {
    if (selected.length > 0) {
      setService(selected);
      setStep('extras');
      navigate('/extras');
    }
  };

  // Voltar para a página inicial
  const handleBack = () => {
    navigate('/');
  };

  const desconto = selected.length > 1 ? (selected.length - 1) * 10 : 0;

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
                  key={service.service_id}
                  service={{
                    id: service.service_id,
                    name: service.name,
                    description: service.description,
                    price: service.price,
                    duration: service.duration,
                    slug: service.name?.toLowerCase().replace(/\s+/g, '-') || '',
                    color: service.color || 'blue',
                  }}
                  onClick={handleSelectService}
                  isSelected={selected.some((s) => s.id === service.service_id)}
                />
              ))}
            </div>

            {/* Mensagem promocional melhorada */}
            <div className="flex justify-center mb-8 mt-2">
              <div
                className="flex items-center gap-2 px-8 py-3 rounded-full bg-gradient-to-r from-secondary to-primary/80 shadow-lg border-2 border-secondary text-white font-extrabold text-base md:text-lg uppercase tracking-wider animate-pulse-slow drop-shadow-lg"
                style={{ letterSpacing: 1.5 }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white drop-shadow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8V4m0 0a4 4 0 110 8m0-8a4 4 0 100 8m0 8v-4m0 4a4 4 0 110-8m0 8a4 4 0 100-8" />
                </svg>
                CONTRATE MAIS DE UMA TERAPIA E GANHE DESCONTO!
              </div>
            </div>

            {/* Notinha dinâmica com desconto progressivo */}
            <div className="max-w-xl mx-auto mb-8">
              <div className="rounded-2xl shadow-lg border-2 border-primary bg-white p-6 relative">
                <h3 className="text-lg font-bold text-primary mb-2 mt-2 text-center">Resumo do Pedido</h3>
                <ul className="mb-2 divide-y divide-gray-100">
                  {selected.map((s) => (
                    <li key={s.id} className="flex justify-between py-2 text-text">
                      <span>{s.name}</span>
                      <span>R$ {s.price.toFixed(2).replace('.', ',')}</span>
                    </li>
                  ))}
                </ul>
                <div className="flex justify-between font-semibold text-primary mt-2">
                  <span>Total</span>
                  <span>R$ {selected.reduce((acc, s) => acc + s.price, 0).toFixed(2).replace('.', ',')}</span>
                </div>
                {/* Cálculo do desconto progressivo */}
                {selected.length > 1 && (
                  <div className="flex justify-between font-semibold text-green-600 mt-2 text-base">
                    <span>Desconto</span>
                    <span>-R$ {((selected.length - 1) * 10).toFixed(2).replace('.', ',')}</span>
                  </div>
                )}
                <div className="flex justify-between font-bold text-lg mt-2 border-t pt-2 border-gray-200">
                  <span>Valor final</span>
                  <span>
                    R$ {(selected.reduce((acc, s) => acc + s.price, 0) - (selected.length > 1 ? (selected.length - 1) * 10 : 0)).toFixed(2).replace('.', ',')}
                  </span>
                </div>
              </div>
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
                disabled={selected.length === 0}
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