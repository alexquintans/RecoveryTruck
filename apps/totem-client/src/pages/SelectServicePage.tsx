import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';

import { ServiceCard } from '../components/ServiceCard';
import { Button } from '../components/Button';
import { api } from '../utils/api';
import { useTotemStore } from '../store/totemStore';
import type { Service } from '../types';

// O tipo de retorno da API para um serviço
interface ApiService {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number; // Corrigido de duration_minutes para duration
  is_active: boolean;
  color?: string;
  // Adicione outros campos que a API retorna, se houver
}


const SelectServicePage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, setService, setStep } = useTotemStore();
  const [selected, setSelected] = useState<Service[]>([]);

  // Sincronizar o estado local com o estado global quando a página carrega
  useEffect(() => {
    if (selectedService) {
      // Se selectedService é um array, use-o diretamente
      if (Array.isArray(selectedService)) {
        setSelected(selectedService);
      } else {
        // Se selectedService é um único serviço, coloque-o em um array
        setSelected([selectedService]);
      }
    } else {
      // Se não há serviço selecionado, limpe o estado local
      setSelected([]);
    }
  }, [selectedService]);

  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
  
  const { data: services = [], isLoading, error } = useQuery<ApiService[]>({
    queryKey: ['services', tenantId],
    queryFn: () => api.getServices(tenantId),
  });
  
  const activeServices = services.filter((s: ApiService) => s.is_active);

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
    // Limpar o estado quando voltar para a página inicial
    setService(null);
    setSelected([]);
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
              {activeServices.map((service) => {
                // Mapeia o objeto da API para o tipo do frontend
                const serviceForCard: Service = {
                  id: service.id,
                    name: service.name,
                    description: service.description,
                    price: service.price,
                  duration: service.duration, // Corrigido para usar a propriedade correta
                    slug: service.name?.toLowerCase().replace(/\s+/g, '-') || '',
                    color: service.color || 'blue',
                };
                return (
                  <ServiceCard
                    service={serviceForCard}
                  onClick={handleSelectService}
                    isSelected={selected.some((s) => s.id === service.id)}
                />
                );
              })}
            </div>

            {/* Promoção atrativa e elegante */}
            <div className="flex justify-center mb-6">
              <div className="relative group cursor-pointer">
                {/* Efeito de brilho animado */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-primary/10 to-primary/20 rounded-2xl blur-sm group-hover:blur-md transition-all duration-500 animate-pulse"></div>
                
                {/* Card principal */}
                <div className="relative bg-gradient-to-r from-primary via-primary/90 to-primary rounded-2xl p-6 shadow-xl border border-primary/30 transform group-hover:scale-105 transition-all duration-300">
                  <div className="flex items-center justify-between">
                    {/* Lado esquerdo - Ícone e texto */}
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </div>
                        {/* Badge de desconto */}
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center">
                          <span className="text-primary text-xs font-bold">%</span>
                        </div>
                      </div>
                      
                      <div className="text-white">
                        <p className="text-xl font-bold mb-1">
                          Ganhe desconto progressivo!
                        </p>
                        <p className="text-white/90 text-sm">
                          Quanto mais terapias, maior o desconto
                        </p>
                      </div>
                    </div>
                    
                    {/* Lado direito - Call to action */}
                    <div className="text-right">
                      <div className="bg-white/20 backdrop-blur-sm rounded-xl px-4 py-2 border border-white/30">
                        <p className="text-white font-bold text-lg">
                          +{selected.length > 1 ? (selected.length - 1) * 10 : 0}%
                        </p>
                        <p className="text-white/80 text-xs">
                          desconto
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Indicador de progresso */}
                  {selected.length > 0 && (
                    <div className="mt-4">
                      <div className="flex justify-between text-white/80 text-sm mb-1">
                        <span>Progresso do desconto</span>
                        <span>{selected.length}/4 terapias</span>
                      </div>
                      <div className="w-full bg-white/20 rounded-full h-2">
                        <div 
                          className="bg-white h-2 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${Math.min((selected.length / 4) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
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
                      <span>R$ {(s.price || 0).toFixed(2).replace('.', ',')}</span>
                    </li>
                  ))}
                </ul>
                <div className="flex justify-between font-semibold text-primary mt-2">
                  <span>Total</span>
                  <span>R$ {selected.reduce((acc, s) => acc + (s.price || 0), 0).toFixed(2).replace('.', ',')}</span>
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
                    R$ {(selected.reduce((acc, s) => acc + (s.price || 0), 0) - (selected.length > 1 ? (selected.length - 1) * 10 : 0)).toFixed(2).replace('.', ',')}
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