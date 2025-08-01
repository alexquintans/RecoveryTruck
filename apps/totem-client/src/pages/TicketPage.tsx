import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';
import { useSoundNotifications } from '../hooks/useSoundNotifications';
import { formatDate, formatCurrency } from '../utils';
import type { Service } from '../types';

// Versão corrigida do TicketPage - todos os hooks no topo
const TicketPage: React.FC = () => {
  // TODOS OS HOOKS DEVEM SER CHAMADOS INCONDICIONALMENTE NO TOPO
  const navigate = useNavigate();
  const { currentTicket, selectedService, customerData, reset } = useTotemStore();
  const soundNotifications = useSoundNotifications();
  const [countdown, setCountdown] = useState(10); // 10 segundos
  const [operationConfig, setOperationConfig] = useState<any>(null);
  
  // Debug: logar dados críticos
  console.log('TicketPage - currentTicket:', currentTicket);
  console.log('TicketPage - Tipo do currentTicket:', typeof currentTicket);
  console.log('TicketPage - Estrutura do currentTicket:', JSON.stringify(currentTicket, null, 2));
  console.log('TicketPage - selectedService:', selectedService);
  console.log('TicketPage - customerData:', customerData);
  
  // Função para obter o serviço principal (primeiro do array ou o único)
  const getMainService = (): Service | null => {
    console.log('getMainService - selectedService:', selectedService);
    
    if (!selectedService) {
      console.log('getMainService - selectedService é null/undefined');
    return null;
  }

    if (Array.isArray(selectedService)) {
      if (selectedService.length === 0) {
        console.log('getMainService - Array de serviços está vazio');
        return null;
      }
      console.log('getMainService - Retornando primeiro serviço do array:', selectedService[0]);
      return selectedService[0];
    }
    
    console.log('getMainService - Retornando serviço único:', selectedService);
    return selectedService;
  };
  
  const mainService = getMainService();
  
  // Buscar configuração da operação para verificar método de pagamento
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '7f02a566-2406-436d-b10d-90ecddd3fe2d';
        const { api } = await import('../utils/api');
        const config = await api.getOperationConfig(tenantId);
        setOperationConfig(config);
      } catch (err) {
        console.error('Erro ao buscar configuração da operação:', err);
      }
    };

    fetchConfig();
  }, []);
  
  // Verificar se o método de pagamento é "none"
  const paymentModes = operationConfig?.payment_modes || [];
  const isPaymentNone = paymentModes.includes('none') || paymentModes.length === 0;
  
  // Função para verificar se o ticket é válido
  const isTicketValid = (ticket: any): boolean => {
    console.log('isTicketValid - Verificando ticket:', ticket);
    
    if (!ticket) {
      console.log('isTicketValid - Ticket é null/undefined');
      return false;
    }
    
    if (typeof ticket !== 'object') {
      console.log('isTicketValid - Ticket não é um objeto:', typeof ticket);
      return false;
    }
    
    // Verificar se tem pelo menos um identificador
    const hasId = ticket.id || ticket.number || ticket.ticket_number;
    if (!hasId) {
      console.log('isTicketValid - Ticket não tem ID válido:', { id: ticket.id, number: ticket.number, ticket_number: ticket.ticket_number });
      return false;
    }
    
    // Verificar se tem data de criação (aceitar ambos os formatos)
    const hasCreatedAt = ticket.createdAt || ticket.created_at;
    if (!hasCreatedAt) {
      console.log('isTicketValid - Ticket não tem data de criação:', { createdAt: ticket.createdAt, created_at: ticket.created_at });
      return false;
    }
    
    console.log('isTicketValid - Ticket é válido');
    return true;
  };

  // Efeito para tocar som e iniciar contagem - APENAS SE TIVER DADOS VÁLIDOS
  useEffect(() => {
    // Só executar se tiver dados válidos
    if (isTicketValid(currentTicket) && mainService) {
    // Tocar som de ticket
    soundNotifications.play('ticket');
    
    // Iniciar contagem regressiva
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // Redirecionar para a página inicial após o término da contagem
          setTimeout(() => {
              reset(); // Limpar o estado
              navigate('/');
          }, 1000);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => {
      clearInterval(timer);
    };
    }
  }, [soundNotifications, navigate, currentTicket, mainService, isTicketValid, reset]);

  // Verificação de segurança - se não tiver dados, mostra loading
  if (!isTicketValid(currentTicket) || !mainService) {
    console.log('TicketPage - Renderizando loading:', { 
      currentTicket, 
      mainService, 
      isTicketValid: isTicketValid(currentTicket) 
    });
    return (
      <div className="totem-card flex flex-col items-center justify-center gap-6 overflow-y-auto">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
        <h2 className="text-2xl font-bold text-primary text-center">Carregando seu ticket...</h2>
        <p className="text-sm text-text-light text-center">
          {!isTicketValid(currentTicket) && 'Ticket não encontrado'}
          {!mainService && 'Serviço não encontrado'}
        </p>
        <div className="text-xs text-gray-500 mt-2">
          <p>Debug: Ticket válido: {isTicketValid(currentTicket) ? 'Sim' : 'Não'}</p>
          <p>Debug: Serviço válido: {mainService ? 'Sim' : 'Não'}</p>
        </div>
      </div>
    );
  }

  // Finalizar e voltar para a página inicial (opção manual)
  const handleFinish = () => {
    reset(); // Limpar o estado
    navigate('/');
  };

  // Número do ticket para exibição
  const displayNumber = currentTicket.number || 
    (currentTicket.ticket_number ? `#${String(currentTicket.ticket_number).padStart(3, '0')}` : '--');

  console.log('TicketPage - Renderizando ticket:', { displayNumber, currentTicket, mainService });
  console.log('TicketPage - Extras do ticket:', currentTicket.extras);
  console.log('TicketPage - CustomerData extras:', customerData?.extras);
  console.log('TicketPage - OperationConfig:', operationConfig);
  console.log('TicketPage - PaymentModes:', paymentModes);
  console.log('TicketPage - IsPaymentNone:', isPaymentNone);

  return (
    <div className="totem-card overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="mb-6">
              <h2 className="text-3xl font-bold text-primary mb-2">Ticket Gerado com Sucesso!</h2>
              <p className="text-text-light">Seu ticket foi impresso. Por favor, aguarde ser chamado.</p>
        </div>

        <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-6 mb-8 max-w-md mx-auto">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-primary">RecoveryTruck</h3>
            <p className="text-sm text-text-light">Serviços de Recuperação Física</p>
          </div>
          
          <div className="border-t border-b border-gray-200 py-4 my-4">
            <div className="flex justify-between mb-2">
              <span className="font-semibold">Número:</span>
              <span className="text-xl font-bold">{displayNumber}</span>
            </div>
            
            {currentTicket.services && currentTicket.services.length > 0 ? (
              <div className="mb-2">
                <div className="font-semibold">Serviços:</div>
                {currentTicket.services.map((service: any, idx: number) => (
                  <div key={service.service_id || idx} className="mb-1">
                    <div className="flex justify-between">
                      <span className="font-medium">{service.name}</span>
                      <span className="font-bold">{formatCurrency(service.price || 0)}</span>
                    </div>
                    <div className="flex justify-between text-sm text-gray-600 ml-2">
                      <span>Duração: {service.duration || 10} min</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex justify-between mb-2">
                <span className="font-semibold">Serviço:</span>
                <span>{mainService?.name || 'Não informado'}</span>
              </div>
            )}
            
            {/* Extras escolhidos pelo cliente */}
            {currentTicket.extras && currentTicket.extras.length > 0 && (
              <div className="mb-2">
                <div className="font-semibold mb-1">Extras:</div>
                {currentTicket.extras.map((extra: any, index: number) => {
                  // Usar o nome que vem da API
                  const extraName = extra.name || `Extra ${index + 1}`;
                  
                  return (
                    <div key={index} className="flex justify-between text-sm ml-2">
                      <span>{extra.quantity}x {extraName}</span>
                      <span>{formatCurrency(extra.price * extra.quantity)}</span>
                    </div>
                  );
                })}
              </div>
            )}
            
            {customerData?.name && (
              <div className="flex justify-between mb-2">
                <span className="font-semibold">Cliente:</span>
                <span>{customerData.name}</span>
              </div>
            )}
            
            <div className="flex justify-between">
              <span className="font-semibold">Data/Hora:</span>
              <span>{formatDate(currentTicket.created_at || currentTicket.createdAt || new Date().toISOString())}</span>
            </div>
          </div>
          
          <div className="text-center mt-4">
              <p className="text-sm text-text-light">Acompanhe sua posição na fila pelo painel.</p>
            <p className="text-sm font-semibold mt-2">
              Tempo estimado de espera: 10 minutos
            </p>
            
            {/* Mensagem para pagamento manual quando método é "none" */}
            {isPaymentNone && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 font-medium">
                  💳 Dirija-se ao atendente para efetuar o pagamento do seu ticket.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 space-y-4">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={handleFinish}
            className="w-full"
          >
            Voltar ao Início
          </Button>
          
          <Button 
            variant="secondary" 
            size="lg" 
            onClick={handleFinish}
            className="w-full"
          >
            Finalizar Agora
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default TicketPage; 