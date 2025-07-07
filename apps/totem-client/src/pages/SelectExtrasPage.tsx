import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { api } from '../utils/api';
import { useQuery } from '@tanstack/react-query';
import { formatCurrency } from '../utils';

const SelectExtrasPage: React.FC = () => {
  const navigate = useNavigate();
  const { setStep, setCustomer, customerData, selectedService } = useTotemStore();
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';
  const { data: operationConfig, isLoading, error } = useQuery({
    queryKey: ['operationConfig', tenantId],
    queryFn: () => api.getOperationConfig(tenantId),
  });
  const extras = (operationConfig?.extras || []).filter((x: any) => x.active && x.stock > 0);

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
    <div className="totem-card">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="text-center mb-8 mt-2">
          <h2 className="text-3xl font-extrabold text-primary mb-2 tracking-tight">Personalize sua Experiência</h2>
          <p className="text-text-light text-lg mb-2">Selecione itens para incrementar sua sessão</p>
          {extras.length > 0 && (
            <div className="flex justify-center mt-2 mb-4">
              <div className="px-6 py-2 rounded-full bg-gradient-to-r from-secondary to-primary/80 shadow-md border-2 border-secondary text-white font-bold text-sm uppercase tracking-wider animate-pulse-slow drop-shadow" style={{ letterSpacing: 1.2 }}>
                Adicione extras e torne sua experiência ainda melhor!
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
          {extras.map((extra: any) => (
            <div key={extra.extra_id} className="border-2 rounded-2xl p-6 flex flex-col gap-3 shadow-md bg-gradient-to-br from-white to-green-50 hover:shadow-xl transition-all duration-200 border-green-300">
              <div className="flex items-center gap-3 mb-2">
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-green-100 shadow">
                  <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="3" strokeWidth="2" /></svg>
                </span>
                <div>
                  <h4 className="font-bold text-primary text-lg">{extra.name}</h4>
                  <span className="text-xs text-gray-500">{extra.description}</span>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1 text-primary font-semibold text-base">
                  <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3" strokeWidth="2" /></svg>
                  R$ {extra.price.toFixed(2)}
                </span>
                <span className="flex items-center gap-1 text-gray-500 text-xs">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 12h16" strokeWidth="2" /></svg>
                  Estoque: {extra.stock}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-3">
                <span className="text-sm text-gray-700 font-medium">Quantidade</span>
                <button
                  onClick={() => handleChange(extra.extra_id, Math.max(0, (selectedExtras[extra.extra_id] || 0) - 1))}
                  className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center text-xl font-bold hover:bg-gray-300 transition-all shadow"
                  title="Diminuir quantidade"
                  disabled={selectedExtras[extra.extra_id] === 0}
                >
                  -
                </button>
                <input
                  type="number"
                  value={selectedExtras[extra.extra_id] || 0}
                  min={0}
                  max={extra.stock}
                  onChange={e => handleChange(extra.extra_id, Math.max(0, Math.min(extra.stock, parseInt(e.target.value) || 0)))}
                  className="w-16 text-center border border-gray-300 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all bg-white text-lg font-semibold"
                />
                <button
                  onClick={() => handleChange(extra.extra_id, Math.min(extra.stock, (selectedExtras[extra.extra_id] || 0) + 1))}
                  className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center text-xl font-bold hover:bg-gray-300 transition-all shadow"
                  title="Aumentar quantidade"
                  disabled={selectedExtras[extra.extra_id] >= extra.stock}
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Notinha - Resumo do Pedido */}
        <div className="bg-white rounded-2xl border-2 border-primary/20 shadow-lg p-6 mb-8">
          <h3 className="text-xl font-bold text-primary mb-4 text-center">Resumo do Pedido</h3>
          
          {/* Serviços Selecionados */}
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">Serviços:</h4>
            {Array.isArray(selectedService) ? selectedService.map((service, index) => (
              <div key={index} className="flex justify-between items-center py-1">
                <span className="text-gray-600">{service.name}</span>
                <span className="font-semibold text-primary">{formatCurrency(service.price)}</span>
              </div>
            )) : selectedService && (
              <div className="flex justify-between items-center py-1">
                <span className="text-gray-600">{selectedService.name}</span>
                <span className="font-semibold text-primary">{formatCurrency(selectedService.price)}</span>
              </div>
            )}
          </div>

          {/* Extras Selecionados */}
          {Object.entries(selectedExtras).some(([_, qty]) => qty > 0) && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Extras:</h4>
              {Object.entries(selectedExtras).map(([extraId, quantity]) => {
                if (quantity === 0) return null;
                const extra = extras.find((e: any) => e.extra_id === extraId);
                if (!extra) return null;
                
                return (
                  <div key={extraId} className="flex justify-between items-center py-1">
                    <span className="text-gray-600">
                      {extra.name} (x{quantity})
                    </span>
                    <span className="font-semibold text-primary">
                      {formatCurrency(extra.price * quantity)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Cálculos */}
          <div className="border-t pt-4 space-y-2">
            {/* Subtotal dos serviços */}
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Subtotal Serviços:</span>
              <span className="font-semibold text-primary">
                {formatCurrency(Array.isArray(selectedService) 
                  ? selectedService.reduce((acc, service) => acc + service.price, 0)
                  : (selectedService?.price || 0)
                )}
              </span>
            </div>

            {/* Subtotal dos extras */}
            {Object.entries(selectedExtras).some(([_, qty]) => qty > 0) && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Subtotal Extras:</span>
                <span className="font-semibold text-primary">
                  {formatCurrency(
                    Object.entries(selectedExtras).reduce((acc, [extraId, quantity]) => {
                      const extra = extras.find((e: any) => e.extra_id === extraId);
                      return acc + (extra ? extra.price * quantity : 0);
                    }, 0)
                  )}
                </span>
              </div>
            )}

            {/* Desconto */}
            {Array.isArray(selectedService) && selectedService.length > 1 && (
              <div className="flex justify-between items-center text-green-600">
                <span className="font-semibold">Desconto (Múltiplos Serviços):</span>
                <span className="font-bold">
                  -{formatCurrency((selectedService.length - 1) * 10)}
                </span>
              </div>
            )}

            {/* Total */}
            <div className="flex justify-between items-center pt-2 border-t-2 border-primary/30">
              <span className="text-lg font-bold text-primary">Total:</span>
              <span className="text-xl font-bold text-primary">
                {formatCurrency(
                  (Array.isArray(selectedService) 
                    ? selectedService.reduce((acc, service) => acc + service.price, 0)
                    : (selectedService?.price || 0)
                  ) +
                  Object.entries(selectedExtras).reduce((acc, [extraId, quantity]) => {
                    const extra = extras.find((e: any) => e.extra_id === extraId);
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

        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t mt-8 gap-4">
          <Button
            variant="outline"
            size="lg"
            onClick={() => navigate('/service')}
          >
            Voltar
          </Button>
          <Button
            variant="primary"
            size="xl"
            className="px-10 py-4 text-lg font-bold shadow-lg"
            onClick={handleContinue}
          >
            Continuar
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default SelectExtrasPage; 