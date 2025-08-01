import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
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
import MercadoPagoPayment from '../components/MercadoPagoPayment';
import MercadoPagoQRCode from '../components/MercadoPagoQRCode';
import WebSocketStatus from '../components/WebSocketStatus';

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setPayment, setTicket, setStep } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  
  // Estado de pagamento
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<'pending' | 'paid' | 'failed'>('pending');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [preferenceId, setPreferenceId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ticketCreated, setTicketCreated] = useState(false);
  const [loadingTicket, setLoadingTicket] = useState(false);
  const [operationConfig, setOperationConfig] = useState<any>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [isCreatingTicket, setIsCreatingTicket] = useState(false);
  const [isCreatingPayment, setIsCreatingPayment] = useState(false);
  const [paymentCreated, setPaymentCreated] = useState(false);
  
  // Construir URL do WebSocket
  let baseWs = (import.meta as any).env?.VITE_WS_URL || 'wss://recoverytruck-production.up.railway.app/ws';
  
  // Forçar uso de wss:// em produção (corrigir se a variável estiver com ws://)
  if (baseWs.startsWith('ws://') && window.location.protocol === 'https:') {
    baseWs = baseWs.replace('ws://', 'wss://');
  }
  
  const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
  const wsUrl = `${baseWs}?tenant_id=${tenantId}&client_type=totem`;

  // Buscar configuração da operação
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoadingConfig(true);
        const config = await api.getOperationConfig(tenantId);
        setOperationConfig(config);
        console.log('🔍 Configuração carregada:', config);
      } catch (err) {
        console.error('Erro ao buscar configuração:', err);
        setError('Erro ao carregar configuração. Tente novamente.');
      } finally {
        setLoadingConfig(false);
      }
    };

    fetchConfig();
  }, [tenantId]);

  // WebSocket hook - SEMPRE chamado no topo
  console.log('🔍 PaymentPage - Iniciando renderização...');
  
  // Callback para mensagens do WebSocket - memoizado para evitar re-renders
  const handleWebSocketMessage = useCallback((msg: any) => {
    console.log('🔍 WebSocket - Mensagem recebida:', msg);
    if (!msg || msg.type !== 'payment_update') return;
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
  }, [sessionId, soundNotifications, setTicket, setStep, navigate]);

  const { isConnected: wsConnected } = useWebSocket({
    url: wsUrl,
    onMessage: handleWebSocketMessage,
  });

  // Métodos de pagamento habilitados pela operação
  const paymentModes: PaymentMethod[] = (operationConfig?.payment_modes || []) as PaymentMethod[];
  
  // Debug: verificar configuração (reduzido)
  if (import.meta.env.DEV) {
    console.log('🔍 PaymentPage - Configuração carregada:', {
      hasConfig: !!operationConfig,
      paymentModes: paymentModes.length,
      hasPublicKey: !!operationConfig?.payment_config?.mercado_pago_public_key
    });
  }

  // Se não houver métodos de pagamento (ou está configurado como 'none'), criar ticket direto
  useEffect(() => {
    if (!ticketCreated && !isCreatingTicket && operationConfig && !loadingConfig && (paymentModes.length === 0 || paymentModes.includes('none' as PaymentMethod))) {
      const createTicketDirectly = async () => {
        try {
          setIsCreatingTicket(true);
          setLoadingTicket(true);
          const services = Array.isArray(selectedService) ? selectedService : [selectedService];
          const serviceIds = services.map(s => ({ id: s.id, price: s.price }));

          const extrasWithPrices = (customerData.extras || []).map(extra => {
            const extraConfig = operationConfig?.extras?.find((e: any) => e.id === extra.id || e.extra_id === extra.id);
            return {
              id: extra.id,
              quantity: extra.quantity,
              price: extraConfig?.price || 0,
            };
          });

          const ticket = await api.createTicket(serviceIds, customerData, extrasWithPrices);
          console.log('PaymentPage - Ticket criado:', ticket);
          console.log('PaymentPage - Tipo do ticket:', typeof ticket);
          console.log('PaymentPage - Estrutura do ticket:', JSON.stringify(ticket, null, 2));
          setTicket(ticket);
          setStep('ticket');
          navigate('/ticket');
          setTicketCreated(true);
        } catch (err) {
          console.error('Erro ao criar ticket sem pagamento:', err);
          setError('Erro ao criar ticket. Tente novamente.');
        } finally {
          setLoadingTicket(false);
          setIsCreatingTicket(false);
        }
      };

      createTicketDirectly();
    }
  }, [ticketCreated, isCreatingTicket, operationConfig, loadingConfig, paymentModes, selectedService, customerData, setTicket, setStep, navigate]);

  // Definir publicKey no topo - ANTES de qualquer return
  const publicKey = operationConfig?.payment_config?.mercado_pago_public_key;

  /** Timeout PIX / pagamento */
  const timeoutRef = useRef<number | null>(null);
  useEffect(() => {
    if (sessionId && sessionStatus === 'pending' && !timeoutRef.current) {
      timeoutRef.current = window.setTimeout(() => {
        setError('Pagamento não foi confirmado a tempo. Por favor, tente novamente.');
        soundNotifications.play('error');
      }, 10 * 60 * 1000); // 10 minutos
    }

    // limpar quando status muda ou componente unmount
    return () => {
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [sessionId, sessionStatus, soundNotifications]);

  // Garantir que o step está correto - MOVIDO PARA O TOPO
  useEffect(() => {
    setStep('payment');
  }, [setStep]);

  // Criar pagamento quando o método for selecionado - MOVIDO PARA O TOPO
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('🔍 DEBUG - useEffect createPayment executado:', {
        selectedService: !!selectedService,
        customerData: !!customerData,
        paymentMethod,
        sessionId,
        isCreatingPayment,
        operationConfig: !!operationConfig
      });
    }

    const createPayment = async () => {
      if (!paymentMethod) return;
      
      if (import.meta.env.DEV) {
        console.log('🔍 createPayment - Iniciando criação de pagamento:', { paymentMethod });
      }
      
      try {
        setIsCreatingPayment(true);
        setError(null);
        
        // Garantir que temos um array de serviços
        const services = Array.isArray(selectedService) ? selectedService : [selectedService];
        const serviceIds = services.map(s => ({ id: s.id, price: s.price }));
        
        // Preparar extras com preços da configuração
        const extrasWithPrices = (customerData.extras || []).map(extra => {
          const extraConfig = operationConfig?.extras?.find(e => e.id === extra.id || e.extra_id === extra.id);
          return {
            id: extra.id,
            quantity: extra.quantity,
            price: extraConfig?.price || 0,
          };
        });

        // 1. Criar o ticket primeiro para consolidar o pedido
        const ticket = await api.createTicket(serviceIds, customerData, extrasWithPrices);
        setTicket(ticket);

        // 2. Criar a sessão de pagamento para o ticket gerado
        const session = await api.createPaymentForTicket(ticket.id, paymentMethod);
        setSessionId(session.id);
        
        if (paymentMethod === 'pix') {
          setQrCodeUrl(session.qr_code || null);
        } else if (paymentMethod === 'mercadopago') {
          setPreferenceId(session.preference_id || null);
        }
        
        setPayment(session as any);
        
        // Marcar que o pagamento foi criado
        setPaymentCreated(true);
        
        // Tocar som de pagamento iniciado
        soundNotifications.play('payment');
      } catch (err) {
        console.error('❌ Erro ao criar pagamento:', err);
        setError('Não foi possível iniciar o pagamento. Tente novamente.');
      } finally {
        setIsCreatingPayment(false);
      }
    };
    
    if (selectedService && customerData && paymentMethod && !sessionId && !isCreatingPayment && !paymentCreated && operationConfig) {
      createPayment();
    }
  }, [selectedService, customerData, paymentMethod, isCreatingPayment, paymentCreated, operationConfig, setPayment, soundNotifications, setTicket, setStep, navigate]); // Adicionado paymentCreated

  // Verificar status do pagamento - MOVIDO PARA O TOPO
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('🔍 DEBUG - useEffect checkPaymentStatus executado:', {
        sessionId,
        sessionStatus,
        wsConnected
      });
    }

    const checkPaymentStatus = async () => {
      if (!sessionId || sessionStatus !== 'pending' || wsConnected) return;

      try {
        const data = await api.getPaymentSession(sessionId);
        const newStatus = data.status as 'pending' | 'paid' | 'failed';
        
        // Só atualizar se o status realmente mudou
        if (newStatus !== sessionStatus) {
          setSessionStatus(newStatus);
        }
      
        if (newStatus === 'paid' && data.ticket_id) {
          soundNotifications.play('success');
          const ticket = await api.getTicket(data.ticket_id);
          setTicket(ticket);
          setStep('ticket');
          navigate('/ticket');
        } else if (newStatus === 'failed') {
          soundNotifications.play('error');
          setError('O pagamento falhou. Por favor, tente novamente.');
        }
      } catch (err) {
        console.error('Erro ao verificar status do pagamento:', err);
      }
    };

    // Só criar o intervalo se temos um sessionId válido e não estamos conectados via WebSocket
    if (sessionId && !wsConnected) {
      const interval = setInterval(checkPaymentStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [sessionId, wsConnected, soundNotifications, setTicket, setStep, navigate]); // Removido sessionStatus da dependência

  // Debug logs
  console.log('PaymentPage - selectedService:', selectedService);
  console.log('PaymentPage - customerData:', customerData);
  console.log('PaymentPage - operationConfig:', operationConfig);

  // Se está carregando configuração, mostrar loading
  if (loadingConfig) {
    return (
      <div className="totem-card flex flex-col items-center justify-center gap-6">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
        <h2 className="text-2xl font-bold text-primary text-center">Carregando...</h2>
        <p className="text-sm text-text-light text-center">Aguarde um momento...</p>
      </div>
    );
  }

  // Se está carregando o ticket, mostrar loading
  if (loadingTicket) {
    return (
      <div className="totem-card flex flex-col items-center justify-center gap-6">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
        <h2 className="text-2xl font-bold text-primary text-center">Criando seu ticket...</h2>
        <p className="text-sm text-text-light text-center">Aguarde um momento...</p>
      </div>
    );
  }

  // Se já criou o ticket, não mostrar nada (já navegou)
  if (ticketCreated) {
    return null;
  }

  // Se não há métodos de pagamento configurados, não mostrar nada (já processou)
  if (paymentModes.length === 0 || paymentModes.includes('none' as PaymentMethod)) {
    return null;
  }
  
  // Redirecionar se não houver serviço selecionado ou dados do cliente
  if (!selectedService || !customerData) {
    console.warn('Redirecionando: selectedService ou customerData ausente');
    navigate('/terms');
    return null;
  }



  // Selecionar método de pagamento
  const handleSelectPaymentMethod = (method: PaymentMethod) => {
    // Resetar estado quando selecionar um novo método
    setPaymentCreated(false);
    setSessionId(null);
    setQrCodeUrl(null);
    setPreferenceId(null);
    setError(null);
    setSessionStatus('pending');
    setPaymentMethod(method);
  };

  // Cancelar pagamento ou voltar para seleção de método
  const handleCancel = () => {
    // Se já existe um método de pagamento selecionado, voltar para a seleção de métodos
    if (paymentMethod) {
      setPaymentMethod(null);
      setSessionId(null);
      setQrCodeUrl(null);
      setPreferenceId(null);
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
    setPreferenceId(null);
    setPaymentCreated(false);
    setSessionStatus('pending');
  };

  // Lógica de cálculo e resumo movida para ser mais clara
  const servicesArray = Array.isArray(selectedService) ? selectedService : selectedService ? [selectedService] : [];
  
  // Mapear extras com dados da configuração da operação
  const extrasArray = (customerData?.extras || []).map(extra => {
    const extraConfig = operationConfig?.extras?.find(e => e.id === extra.id);
    return {
      ...extra,
      name: extraConfig?.name || 'Extra',
      price: extraConfig?.price || 0,
    };
  }).filter(extra => extra.quantity > 0); // Filtrar apenas extras com quantidade > 0

  const subtotalServico = servicesArray.reduce((acc, s) => acc + (s?.price || 0), 0);
  const subtotalExtras = extrasArray.reduce((acc, e) => acc + (e.price * e.quantity), 0);
  const desconto = servicesArray.length > 1 ? (servicesArray.length - 1) * 10 : 0;
  const total = subtotalServico + subtotalExtras - desconto;

  return (
    <div className="totem-card">
      {/* Status do WebSocket */}
      <WebSocketStatus isConnected={wsConnected} status={wsConnected ? 'open' : 'closed'} />
      
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
            Confira seu pedido e escolha a forma de pagamento
          </p>
        </div>

        {/* Resumo estilo nota fiscal */}
        <div className="bg-white rounded-2xl border-2 border-primary/20 shadow-lg p-6 mb-8 max-w-lg mx-auto">
          <h3 className="text-xl font-bold text-primary mb-4 text-center">Resumo do Pedido</h3>
          
          {/* Serviços */}
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">Serviços:</h4>
            {servicesArray.map((service, idx) => (
              <div className="flex justify-between items-center py-1" key={`service-${idx}`}>
                <span className="text-gray-600">{service.name}</span>
                <span className="font-semibold text-primary">{formatCurrency(service.price)}</span>
              </div>
            ))}
          </div>
          
          {/* Extras */}
          {extrasArray.length > 0 && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Extras:</h4>
              {extrasArray.map((extra, idx) => (
                <div className="flex justify-between items-center py-1" key={`extra-${idx}`}>
                  <span className="text-gray-600">{extra.name} (x{extra.quantity})</span>
                  <span className="font-semibold text-primary">{formatCurrency(extra.price * extra.quantity)}</span>
                </div>
              ))}
            </div>
          )}

          {/* Cálculos */}
          <div className="border-t pt-4 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Subtotal Serviços:</span>
              <span className="font-semibold text-primary">{formatCurrency(subtotalServico)}</span>
            </div>

            {extrasArray.length > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Subtotal Extras:</span>
                <span className="font-semibold text-primary">{formatCurrency(subtotalExtras)}</span>
              </div>
            )}

            {desconto > 0 && (
              <div className="flex justify-between items-center text-green-600">
                <span className="font-semibold">Desconto:</span>
                <span className="font-bold">-{formatCurrency(desconto)}</span>
              </div>
            )}

            <div className="flex justify-between items-center pt-2 border-t-2 border-primary/30">
              <span className="text-lg font-bold text-primary">Total:</span>
              <span className="text-xl font-bold text-primary">{formatCurrency(total)}</span>
            </div>
          </div>
        </div>

        {/* Lógica de exibição de pagamento */}
        {!paymentMethod ? (
          <PaymentMethodSelector 
            selectedMethod={paymentMethod}
            onSelect={handleSelectPaymentMethod}
            availableMethods={paymentModes as PaymentMethod[]}
          />
        ) : (
          <>
            {/* Interface de pagamento com cartão */}
            {(paymentMethod === 'credit_card' || paymentMethod === 'debit_card') && !error && (
              <CardPaymentInterface 
                paymentMethod={paymentMethod}
                amount={total}
              />
            )}

            {/* Interface de pagamento com PIX */}
            {paymentMethod === 'pix' && !error && (
              <PixPaymentInterface
                qrCodeUrl={qrCodeUrl}
                amount={total}
              />
            )}

            {/* Interface de pagamento com Mercado Pago */}
            {paymentMethod === 'mercadopago' && (
              <>
                {console.log('🔍 Debug MercadoPago:', { 
                  paymentMethod, 
                  preferenceId, 
                  qrCodeUrl,
                  total, 
                  error,
                  hasRequiredProps: !!(qrCodeUrl && !error)
                })}
                {preferenceId && !error ? (
                  <MercadoPagoPayment
                    preferenceId={preferenceId}
                    publicKey={operationConfig?.payment_config?.mercado_pago_public_key || ''}
                    amount={total}
                    onSuccess={() => {
                      console.log('✅ Pagamento Mercado Pago aprovado');
                      soundNotifications.play('success');
                      // O webhook vai processar automaticamente
                    }}
                    onError={(errorMsg) => {
                      console.error('❌ Erro no pagamento Mercado Pago:', errorMsg);
                      setError(`Erro no pagamento: ${errorMsg}`);
                      soundNotifications.play('error');
                    }}
                    onCancel={() => {
                      console.log('🚫 Pagamento Mercado Pago cancelado');
                      setPaymentMethod(null);
                      setPreferenceId(null);
                      setError(null);
                    }}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center p-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mb-4"></div>
                    <p className="text-sm text-text-light">
                      {!preferenceId ? 'Carregando interface de pagamento...' :
                       error ? 'Erro na configuração' : 'Carregando interface de pagamento...'}
                    </p>
                    {error && (
                      <p className="text-sm text-red-600 mt-2">{error}</p>
                    )}
                  </div>
                )}
              </>
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
          </>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            <p>{error}</p>
            <Button variant="primary" size="md" onClick={handleRetry} className="mt-2">Tentar Novamente</Button>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            size="lg" onClick={handleCancel} disabled={sessionStatus === 'pending'} 
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" /></svg>}
          >{paymentMethod ? 'Voltar' : 'Cancelar'}</Button>

          {!paymentMethod && (
            <Button
              variant="primary"
              size="lg" disabled={true}
              icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" /></svg>}
              iconPosition="right">Continuar</Button>
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