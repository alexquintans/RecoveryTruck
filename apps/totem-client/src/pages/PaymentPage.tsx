import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Button } from '../components/Button';
import { PaymentMethodSelector } from '../components/PaymentMethodSelector';
import { CardPaymentInterface } from '../components/CardPaymentInterface';
import { PixPaymentInterface } from '../components/PixPaymentInterface';
import { useTotemStore } from '../store/totemStore';
import { api } from '../utils/api';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { formatCurrency } from '../utils';
import type { PaymentMethod } from '../types';
import { useWebSocket } from '@totem/hooks';

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setPayment, setTicket, setStep } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  
  // Estado de pagamento
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<'pending' | 'paid' | 'failed'>('pending');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  /** WebSocket de pagamento */
  // Construir URL
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const baseWs = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000/ws';
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '52c6777f-ee24-433b-8e4b-7185950da52e';
  const wsUrl = `${baseWs}?tenant_id=${tenantId}&client_type=totem`;

  const { isConnected: wsConnected } = useWebSocket({
    url: wsUrl,
    onMessage: (msg: any) => {
      if (!msg || msg.type !== 'payment_update') return;
      // Se for a sessão atual
      if (msg.data.id !== sessionId) return;

      const status = msg.data.status;
      setSessionStatus(status);

      if (status === 'paid' && msg.data.ticket_id) {
        soundNotifications.play('success');
        api.getTicket(msg.data.ticket_id).then((ticket) => {
          setTicket(ticket);
          setStep('ticket');
          navigate('/ticket');
        });
      } else if (status === 'failed') {
        soundNotifications.play('error');
        setError('O pagamento falhou. Por favor, tente novamente.');
      }
    },
  });

  /** Timeout PIX / pagamento */
  const timeoutRef = useRef<number | null>(null);
  useEffect(() => {
    if (sessionId && sessionStatus === 'pending' && !timeoutRef.current) {
      timeoutRef.current = window.setTimeout(() => {
        setError('Pagamento não foi confirmado a tempo. Por favor, tente novamente.');
        soundNotifications.play('error');
      }, 3 * 60 * 1000); // 3 minutos
    }

    // limpar quando status muda ou componente unmount
    return () => {
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [sessionId, sessionStatus]);
  
  // Debug: logar dados críticos
  console.log('PaymentPage - selectedService:', selectedService);
  console.log('PaymentPage - customerData:', customerData);
  
  // Redirecionar se não houver serviço selecionado ou dados do cliente
  if (!selectedService || !customerData) {
    console.warn('Redirecionando: selectedService ou customerData ausente');
    navigate('/terms');
    return null;
  }

  // Garantir que o step está correto
  useEffect(() => {
    setStep('payment');
  }, [setStep]);

  // Criar pagamento quando o método for selecionado
  useEffect(() => {
    const createPayment = async () => {
      if (!paymentMethod) return;
      
      try {
        setError(null);
        
        // Se há múltiplos serviços, usar o endpoint de payment session simulado
        if (Array.isArray(selectedService) && selectedService.length > 1) {
          const services = selectedService.map(s => ({
            id: s.id,
            price: s.price
          }));
          
          const extras = customerData?.extras?.map(e => ({
            id: e.id,
            quantity: e.quantity,
            price: 0 // Será calculado pelo backend
          })) || [];
          
          // Chamar payment session simulada para múltiplos serviços
          const session = await api.createPaymentSession(services[0].id, customerData, paymentMethod);
          setSessionId(session.id);
          setPayment(session as any);
          soundNotifications.play('payment');
          return;
        }
        
        // Para um único serviço, usar o fluxo de payment session
        const singleService = Array.isArray(selectedService) ? selectedService[0] : selectedService;
        const session = await api.createPaymentSession(singleService.id, customerData, paymentMethod);
        setSessionId(session.id);
        
        if (paymentMethod === 'pix') {
          setQrCodeUrl(session.qr_code || null);
        }
        
        setPayment(session as any);
        
        // Tocar som de pagamento iniciado
        soundNotifications.play('payment');
      } catch (err) {
        console.error('Erro ao criar pagamento:', err);
        setError('Não foi possível iniciar o pagamento. Tente novamente.');
      }
    };
    
    if (selectedService && customerData && paymentMethod && !sessionId) {
      createPayment();
    }
  }, [selectedService, customerData, paymentMethod, sessionId, setPayment, soundNotifications, setTicket, setStep, navigate]);

  // Verificar status do pagamento
  useQuery({
    queryKey: ['payment_session', sessionId],
    queryFn: () => api.getPaymentSession(sessionId!),
    enabled: !!sessionId && sessionStatus === 'pending' && !wsConnected,
    refetchInterval: wsConnected ? false : 3000,
    onSuccess: (data) => {
      setSessionStatus(data.status);
      
      if (data.status === 'paid' && data.ticket_id) {
        // Tocar som de sucesso
        soundNotifications.play('success');
        
        // Buscar o ticket
        api.getTicket(data.ticket_id).then((ticket) => {
          setTicket(ticket);
          setStep('ticket');
          navigate('/ticket');
        });
      } else if (data.status === 'failed') {
        // Tocar som de erro
        soundNotifications.play('error');
        setError('O pagamento falhou. Por favor, tente novamente.');
      }
    },
  });

  // Selecionar método de pagamento
  const handleSelectPaymentMethod = (method: PaymentMethod) => {
    setPaymentMethod(method);
  };

  // Cancelar pagamento ou voltar para seleção de método
  const handleCancel = () => {
    // Se já existe um método de pagamento selecionado, voltar para a seleção de métodos
    if (paymentMethod) {
      setPaymentMethod(null);
      setSessionId(null);
      setQrCodeUrl(null);
      setError(null);
    } else {
      // Caso contrário, voltar para a página de termos
      navigate('/terms');
    }
  };

  // Tentar novamente
  const handleRetry = () => {
    setError(null);
    setSessionId(null);
    setPaymentMethod(null);
  };

  const { data: operationConfig } = useQuery({
    queryKey: ['operationConfig', tenantId],
    queryFn: () => api.getOperationConfig(tenantId),
  });
  const extrasConfig = (operationConfig?.extras || []).filter((x: any) => x.active);
  const selectedExtras = customerData?.extras || [];
  const extrasResumo = selectedExtras.map((e: any) => {
    const config = extrasConfig.find((x: any) => x.extra_id === e.id);
    return config ? {
      name: config.name,
      price: config.price,
      quantity: e.quantity,
      subtotal: config.price * e.quantity,
    } : null;
  }).filter(Boolean);

  // Lidar com selectedService sendo array ou objeto
  const servicesArray = Array.isArray(selectedService) ? selectedService : selectedService ? [selectedService] : [];
  const subtotalServico = servicesArray.reduce((acc, s) => acc + (s?.price || 0), 0);
  const subtotalExtras = extrasResumo.reduce((acc, e) => acc + (e?.subtotal || 0), 0);
  // Desconto progressivo: R$10 para 2 serviços, R$20 para 3, etc.
  const desconto = servicesArray.length > 1 ? (servicesArray.length - 1) * 10 : 0;
  const total = subtotalServico + subtotalExtras - desconto;

  return (
    <div className="totem-card">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-primary mb-2">
            Pagamento
          </h2>
          <p className="text-text-light">
            Serviço: <span className="font-semibold text-primary">{selectedService?.name || '-'}</span> - 
            <span className="font-semibold text-primary ml-1">{formatCurrency(selectedService?.price || 0)}</span>
          </p>
        </div>

        {/* Resumo estilo nota fiscal */}
        <div className="bg-white rounded-2xl border-2 border-primary/20 shadow-lg p-6 mb-8 max-w-lg mx-auto">
          <h3 className="text-xl font-bold text-primary mb-4 text-center">Resumo do Pedido</h3>
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">Serviços:</h4>
            {servicesArray.length === 0 && (
              <div className="flex justify-between items-center py-1">
                <span className="text-gray-600">-</span>
                <span className="font-semibold text-primary">R$ 0,00</span>
              </div>
            )}
            {servicesArray.map((service, idx) => (
              <div className="flex justify-between items-center py-1" key={idx}>
                <span className="text-gray-600">{service.name}</span>
                <span className="font-semibold text-primary">{formatCurrency(service.price)}</span>
              </div>
            ))}
          </div>
          {extrasResumo.length > 0 && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Extras:</h4>
              {extrasResumo.map((e, idx) => (
                <div className="flex justify-between items-center py-1 text-sm" key={idx}>
                  <span className="text-gray-600">{e.name} x{e.quantity}</span>
                  <span className="font-semibold text-primary">{formatCurrency(e.subtotal)}</span>
                </div>
              ))}
              <div className="flex justify-between items-center mt-2">
                <span className="text-gray-600">Subtotal Extras:</span>
                <span className="font-semibold text-primary">{formatCurrency(subtotalExtras)}</span>
              </div>
            </div>
          )}
          {desconto > 0 && (
            <div className="flex justify-between items-center text-green-600 mb-2">
              <span className="font-semibold">Desconto (Múltiplos Serviços):</span>
              <span className="font-bold">-{formatCurrency(desconto)}</span>
            </div>
          )}
          <div className="border-t pt-4 space-y-2">
            <div className="flex justify-between items-center text-lg font-bold">
              <span>Total:</span>
              <span>{formatCurrency(total)}</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            <p>{error}</p>
            <Button
              variant="primary"
              size="md"
              onClick={handleRetry}
              className="mt-2"
            >
              Tentar Novamente
            </Button>
          </div>
        )}

        {/* Seleção de método de pagamento */}
        {!paymentMethod && !error && (
          <PaymentMethodSelector 
            selectedMethod={paymentMethod}
            onSelect={handleSelectPaymentMethod}
          />
        )}

        {/* Interface de pagamento com cartão */}
        {(paymentMethod === 'credit_card' || paymentMethod === 'debit_card') && !error && (
          <CardPaymentInterface 
            paymentMethod={paymentMethod}
            amount={selectedService?.price || 0}
          />
        )}

        {/* Interface de pagamento com PIX */}
        {paymentMethod === 'pix' && !error && (
          <PixPaymentInterface
            qrCodeUrl={qrCodeUrl}
            amount={selectedService?.price || 0}
          />
        )}

        {/* Pagamento em processamento */}
        {sessionStatus === 'pending' && paymentMethod !== null && !error && (
          <div className="flex flex-col items-center my-8">
            <div className="mb-6">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary mx-auto"></div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Processando pagamento</h3>
            <p className="text-text-light">
              Estamos processando seu pagamento. Por favor, aguarde...
            </p>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            size="lg"
            onClick={handleCancel}
            disabled={sessionStatus === 'pending'}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
            }
          >
            {paymentMethod ? 'Voltar' : 'Cancelar'}
          </Button>

          {!paymentMethod && (
            <Button
              variant="primary"
              size="lg"
              disabled={true}
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              }
              iconPosition="right"
            >
              Continuar
            </Button>
          )}
        </div>

        {/* Indicador de conexão WebSocket */}
        {!wsConnected && (
          <p className="text-sm text-gray-500 mt-4">Reconectando para confirmar pagamento...</p>
        )}
      </motion.div>
    </div>
  );
};

export default PaymentPage; 