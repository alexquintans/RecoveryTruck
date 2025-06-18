import React, { useState, useEffect } from 'react';
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

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setPayment, setTicket, setStep } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  
  // Estado de pagamento
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'processing' | 'completed' | 'failed'>('pending');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Redirecionar se não houver serviço selecionado ou dados do cliente
  if (!selectedService || !customerData) {
    navigate('/terms');
    return null;
  }

  // Criar pagamento quando o método for selecionado
  useEffect(() => {
    const createPayment = async () => {
      if (!paymentMethod) return;
      
      try {
        setError(null);
        const payment = await api.createPayment(selectedService.id, customerData, paymentMethod);
        setPaymentId(payment.id);
        
        if (paymentMethod === 'pix') {
          setQrCodeUrl(payment.qrCodeUrl || null);
        }
        
        setPayment(payment);
        
        // Tocar som de pagamento iniciado
        soundNotifications.play('payment');
      } catch (err) {
        console.error('Erro ao criar pagamento:', err);
        setError('Não foi possível iniciar o pagamento. Tente novamente.');
      }
    };
    
    if (selectedService && customerData && paymentMethod && !paymentId) {
      createPayment();
    }
  }, [selectedService, customerData, paymentMethod, paymentId, setPayment, soundNotifications]);

  // Verificar status do pagamento
  const { data: paymentData } = useQuery({
    queryKey: ['payment', paymentId],
    queryFn: () => api.checkPaymentStatus(paymentId!),
    enabled: !!paymentId && paymentStatus !== 'completed',
    refetchInterval: 3000, // Verificar a cada 3 segundos
    onSuccess: (data) => {
      setPaymentStatus(data.status);
      
      // Se o pagamento foi concluído com sucesso
      if (data.status === 'completed' && data.ticketId) {
        // Tocar som de sucesso
        soundNotifications.play('success');
        
        // Buscar o ticket
        api.getTicket(data.ticketId).then((ticket) => {
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
      setPaymentId(null);
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
    setPaymentId(null);
    setPaymentMethod(null);
  };

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
            Serviço: <span className="font-semibold text-primary">{selectedService.name}</span> - 
            <span className="font-semibold text-primary ml-1">{formatCurrency(selectedService.price)}</span>
          </p>
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
            amount={selectedService.price}
          />
        )}

        {/* Interface de pagamento com PIX */}
        {paymentMethod === 'pix' && !error && (
          <PixPaymentInterface
            qrCodeUrl={qrCodeUrl}
            amount={selectedService.price}
          />
        )}

        {/* Pagamento em processamento */}
        {paymentStatus === 'processing' && !error && (
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
            disabled={paymentStatus === 'processing'}
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
      </motion.div>
    </div>
  );
};

export default PaymentPage; 