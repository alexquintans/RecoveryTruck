import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { api } from '../utils/api';
import { useQuery } from '@tanstack/react-query';
import { formatCurrency } from '../utils';

// Interface para a resposta da API de configuração da operação
interface OperationConfig {
  extras: ApiExtra[];
  // Adicione outros campos da configuração se necessário
}

// Interface para um item "extra" como vem da API
interface ApiExtra {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  is_active: boolean; // Campo retornado pelo backend
}

const SelectExtrasPage: React.FC = () => {
  const navigate = useNavigate();
  const { setStep, setCustomer, customerData, selectedService, setService } = useTotemStore();
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
  
  const { data: operationConfig, isLoading, error } = useQuery<OperationConfig>({
    queryKey: ['operationConfig', tenantId],
    queryFn: () => api.getOperationConfig(tenantId),
  });
  
  const extras = (operationConfig?.extras || []).filter((x) => x.is_active && x.stock > 0);

  // Estado local para seleção de extras
  const [selectedExtras, setSelectedExtras] = useState<{ [extraId: string]: number }>({});

  const handleChange = (extraId: string, value: number) => {
    setSelectedExtras((prev) => ({ ...prev, [extraId]: value }));
  };

  const handleContinue = () => {
    // Salvar extras escolhidos no customerData
    setCustomer({ ...customerData, extras: Object.entries(selectedExtras).filter(([_, qty]) => qty > 0).map(([id, qty]) => ({ id, quantity: qty })) });
    setStep('customer');
    navigate('/customer-info');
  };

  return (
    <div className="totem-card overflow-y-auto">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="text-center mb-8 mt-2">
          <h2 className="text-3xl font-extrabold text-primary mb-2 tracking-tight">Personalize sua Experiência</h2>
          <p className="text-text-light text-lg mb-2">Selecione itens para incrementar sua sessão</p>
          
          {/* Banner promocional atrativo */}
          {extras.length > 0 && (
            <div className="flex justify-center mt-6 mb-8">
              <div className="relative group cursor-pointer">
                {/* Efeito de brilho animado */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-primary/10 to-primary/20 rounded-2xl blur-sm group-hover:blur-md transition-all duration-500 animate-pulse"></div>
                
                {/* Card principal */}
                <div className="relative bg-gradient-to-r from-primary via-primary/90 to-primary rounded-2xl p-6 shadow-xl border border-primary/30 transform group-hover:scale-105 transition-all duration-300">
                  <div className="flex items-center justify-center gap-4">
                    <div className="relative">
                      <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                        </svg>
                      </div>
                      {/* Badge de personalização */}
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center">
                        <span className="text-primary text-xs font-bold">+</span>
                      </div>
                    </div>
                    
                    <div className="text-white text-center">
                      <p className="text-xl font-bold mb-1">
                        Torne sua experiência única!
                      </p>
                      <p className="text-white/90 text-sm">
                        Adicione extras e maximize seus resultados
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
          </div>
        )}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            <p>Ocorreu um erro ao carregar os extras. Tente novamente.</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {extras.map((extra: ApiExtra) => {
            const quantity = selectedExtras[extra.id] || 0;
            const isSelected = quantity > 0;
            
            return (
              <motion.div
                key={extra.id}
                className={`
                  relative group cursor-pointer rounded-2xl p-6 transition-all duration-300 transform hover:scale-105
                  ${isSelected 
                    ? 'bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary shadow-xl' 
                    : 'bg-white border-2 border-accent hover:border-primary/50 shadow-lg hover:shadow-xl'
                  }
                `}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {/* Badge de seleção */}
                {isSelected && (
                  <div className="absolute -top-3 -right-3 w-8 h-8 bg-primary rounded-full flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}

                {/* Header do card */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`
                      w-12 h-12 rounded-full flex items-center justify-center shadow-md
                      ${isSelected ? 'bg-primary text-white' : 'bg-primary/10 text-primary'}
                    `}>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                      </svg>
                    </div>
                    <div>
                      <h4 className={`font-bold text-lg ${isSelected ? 'text-primary' : 'text-text'}`}>
                        {extra.name}
                      </h4>
                      <p className="text-sm text-text-light">{extra.description}</p>
                    </div>
                  </div>
                </div>

                {/* Informações do produto */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-primary">
                      R$ {extra.price.toFixed(2).replace('.', ',')}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-text-light text-sm">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                    <span>Estoque: {extra.stock}</span>
                  </div>
                </div>

                {/* Controles de quantidade */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-text-light">Quantidade</span>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleChange(extra.id, Math.max(0, quantity - 1));
                      }}
                      className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-xl font-bold transition-all shadow-md
                        ${quantity === 0 
                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                          : 'bg-primary text-white hover:bg-primary-dark hover:scale-110'
                        }
                      `}
                      disabled={quantity === 0}
                    >
                      -
                    </button>
                    
                    <div className="w-16 text-center">
                      <span className={`text-xl font-bold ${isSelected ? 'text-primary' : 'text-text'}`}>
                        {quantity}
                      </span>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleChange(extra.id, Math.min(extra.stock, quantity + 1));
                      }}
                      className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-xl font-bold transition-all shadow-md
                        ${quantity >= extra.stock 
                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                          : 'bg-primary text-white hover:bg-primary-dark hover:scale-110'
                        }
                      `}
                      disabled={quantity >= extra.stock}
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Indicador de valor total */}
                {isSelected && (
                  <div className="mt-4 pt-3 border-t border-primary/20">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-text-light">Total:</span>
                      <span className="text-lg font-bold text-primary">
                        R$ {(extra.price * quantity).toFixed(2).replace('.', ',')}
                      </span>
                    </div>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Resumo do Pedido Atraente */}
        <div className="bg-gradient-to-br from-white to-primary/5 rounded-2xl border-2 border-primary/20 shadow-xl p-6 mb-8">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-primary mb-2">Resumo do Pedido</h3>
            <div className="w-16 h-1 bg-primary rounded-full mx-auto"></div>
          </div>
          
          {/* Serviços Selecionados */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-bold text-primary text-lg">Serviços Selecionados</h4>
            </div>
            
            <div className="space-y-2">
              {Array.isArray(selectedService) ? selectedService.map((service, index) => (
                <div key={index} className="flex justify-between items-center py-2 px-3 bg-white/50 rounded-lg border border-primary/10">
                  <span className="text-text font-medium">{service.name}</span>
                  <span className="font-bold text-primary">{formatCurrency(service.price)}</span>
                </div>
              )) : selectedService && (
                <div className="flex justify-between items-center py-2 px-3 bg-white/50 rounded-lg border border-primary/10">
                  <span className="text-text font-medium">{selectedService.name}</span>
                  <span className="font-bold text-primary">{formatCurrency(selectedService.price)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Extras Selecionados */}
          {Object.entries(selectedExtras).some(([_, qty]) => qty > 0) && (
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                </div>
                <h4 className="font-bold text-primary text-lg">Extras Adicionados</h4>
              </div>
              
              <div className="space-y-2">
                {Object.entries(selectedExtras).map(([extraId, quantity]) => {
                  if (quantity === 0) return null;
                  const extra = extras.find((e) => e.id === extraId);
                  if (!extra) return null;
                  
                  return (
                    <div key={extraId} className="flex justify-between items-center py-2 px-3 bg-white/50 rounded-lg border border-primary/10">
                      <span className="text-text font-medium">
                        {extra.name} <span className="text-primary/70">(x{quantity})</span>
                      </span>
                      <span className="font-bold text-primary">
                        {formatCurrency(extra.price * quantity)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Cálculos com design melhorado */}
          <div className="bg-white/70 rounded-xl p-4 border border-primary/10">
            <div className="space-y-3">
              {/* Subtotal dos serviços */}
              <div className="flex justify-between items-center">
                <span className="text-text-light font-medium">Subtotal Serviços:</span>
                <span className="font-bold text-primary">
                  {formatCurrency(Array.isArray(selectedService) 
                    ? selectedService.reduce((acc, service) => acc + service.price, 0)
                    : (selectedService?.price || 0)
                  )}
                </span>
              </div>

              {/* Subtotal dos extras */}
              {Object.entries(selectedExtras).some(([_, qty]) => qty > 0) && (
                <div className="flex justify-between items-center">
                  <span className="text-text-light font-medium">Subtotal Extras:</span>
                  <span className="font-bold text-primary">
                    {formatCurrency(
                      Object.entries(selectedExtras).reduce((acc, [extraId, quantity]) => {
                        const extra = extras.find((e) => e.id === extraId);
                        return acc + (extra ? extra.price * quantity : 0);
                      }, 0)
                    )}
                  </span>
                </div>
              )}

              {/* Desconto com destaque */}
              {Array.isArray(selectedService) && selectedService.length > 1 && (
                <div className="flex justify-between items-center py-2 px-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span className="font-bold text-green-700">Desconto (Múltiplos Serviços):</span>
                  </div>
                  <span className="font-bold text-green-700">
                    -{formatCurrency((selectedService.length - 1) * 10)}
                  </span>
                </div>
              )}

              {/* Total destacado */}
              <div className="flex justify-between items-center pt-3 border-t-2 border-primary/30">
                <span className="text-xl font-bold text-primary">Total Final:</span>
                <span className="text-2xl font-bold text-primary">
                  {formatCurrency(
                    (Array.isArray(selectedService) 
                      ? selectedService.reduce((acc, service) => acc + service.price, 0)
                      : (selectedService?.price || 0)
                    ) +
                    Object.entries(selectedExtras).reduce((acc, [extraId, quantity]) => {
                      const extra = extras.find((e) => e.id === extraId);
                      return acc + (extra ? extra.price * quantity : 0);
                    }, 0) -
                    (Array.isArray(selectedService) && selectedService.length > 1 
                      ? (selectedService.length - 1) * 10 
                      : 0
                    )
                  )}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t mt-8 gap-6">
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              console.log('🔍 DEBUG - Botão voltar clicado');
              console.log('🔍 DEBUG - Navegando para /service');
              try {
                // Limpar o estado quando voltar para a página de serviços
                setService(null);
                setStep('service');
                navigate('/service');
                console.log('🔍 DEBUG - Navegação executada com sucesso');
              } catch (error) {
                console.error('🔍 DEBUG - Erro na navegação:', error);
                // Fallback: tentar usar window.location
                window.location.href = '/service';
              }
            }}
            className="group hover:scale-105 transition-all duration-300"
          >
            <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Voltar
          </Button>
          
          <Button
            variant="primary"
            size="xl"
            className="px-12 py-4 text-lg font-bold shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 group"
            onClick={handleContinue}
          >
            Continuar
            <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default SelectExtrasPage; 