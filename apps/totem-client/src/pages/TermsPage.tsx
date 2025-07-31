import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from '../components/Button';
import { TermsOfService } from '../components/TermsOfService';
import { useTotemStore } from '../store/totemStore';
import { api } from '../utils/api';

const TermsPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setStep, setCustomer } = useTotemStore();
  const [signed, setSigned] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const signatureRef = useRef<any>(null);
  const [existingConsent, setExistingConsent] = useState<{ signature: string; created_at: string } | null>(null);
  const [loadingConsent, setLoadingConsent] = useState(true);
  
  // Redirecionar se não houver serviço selecionado ou dados do cliente
  if (!selectedService || !customerData) {
    navigate('/customer-info');
    return null;
  }

  // Buscar consentimento mais recente ao carregar
  useEffect(() => {
    const fetchConsent = async () => {
      setLoadingConsent(true);
      try {
        const tenantId = (import.meta as any).env?.VITE_TENANT_ID || '38534c9f-accb-4884-9c19-dd37f77d0594';
        const params: any = { tenant_id: tenantId };
        if (customerData.cpf) params.cpf = customerData.cpf.replace(/\D/g, '');
        else if (customerData.name && customerData.phone) {
          params.name = customerData.name;
          params.phone = customerData.phone;
        } else if (customerData.name) {
          params.name = customerData.name;
        }
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`/customers/consents/last?${query}`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.signature) {
            setExistingConsent(data);
          }
        }
      } catch (e) {
        // Ignorar erro
      } finally {
        setLoadingConsent(false);
      }
    };
    fetchConsent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Limpar assinatura
  const handleClearSignature = () => {
    if (signatureRef.current) {
      signatureRef.current.clear();
      setSigned(false);
    }
  };

  // Verificar se o usuário assinou
  const checkSignature = () => {
    if (signatureRef.current) {
      return !signatureRef.current.isEmpty();
    }
    return false;
  };

  // Salvar assinatura e continuar
  const handleContinue = () => {
    if (!existingConsent) {
      if (!checkSignature()) {
        setError('Por favor, assine o termo de responsabilidade para continuar.');
        return;
      }
    }
    let signatureData = existingConsent?.signature;
    if (!existingConsent && signatureRef.current) {
      signatureData = signatureRef.current.toDataURL();
    }
    setCustomer({
      ...customerData,
      signature: signatureData,
      termsAccepted: true,
      termsAcceptedAt: new Date().toISOString(),
    });
    setStep('payment');
    navigate('/payment');
  };

  // Voltar para a página anterior
  const handleBack = () => {
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
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-primary mb-2">
            Termo de Responsabilidade
          </h2>
          <p className="text-text-light">
            Por favor, leia atentamente e assine o termo abaixo para continuar
          </p>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 mb-6 max-h-[40vh] overflow-y-auto">
          <TermsOfService service={selectedService} />
        </div>

        {loadingConsent ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-4 border-primary"></div>
            <span className="ml-3 text-primary">Verificando consentimento anterior...</span>
          </div>
        ) : existingConsent ? (
          <div className="mb-6 text-center">
            <h3 className="text-lg font-semibold mb-2 text-green-700">Assinatura já registrada recentemente</h3>
            <img src={existingConsent.signature} alt="Assinatura salva" className="mx-auto border-2 border-green-400 rounded-lg bg-white max-h-32" />
            <p className="text-sm text-gray-600 mt-2">Assinatura coletada em {new Date(existingConsent.created_at).toLocaleDateString()}</p>
            <p className="text-green-700 font-semibold mt-2">Você não precisa assinar novamente.</p>
          </div>
        ) : (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Assinatura:</h3>
            <div className="border-2 border-gray-300 rounded-xl bg-white">
              <div className="w-full h-40">
                {/* @ts-ignore */}
                <SignatureCanvas
                  ref={signatureRef}
                  canvasProps={{
                    className: 'w-full h-40',
                  }}
                  onEnd={() => setSigned(true)}
                />
              </div>
            </div>
            {error && <p className="mt-2 text-red-500">{error}</p>}
            <button
              type="button"
              onClick={handleClearSignature}
              className="mt-2 text-primary hover:underline focus:outline-none text-sm"
            >
              Limpar assinatura
            </button>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              console.log('🔍 DEBUG - Botão voltar clicado (TermsPage)');
              console.log('🔍 DEBUG - Navegando para /customer-info');
              try {
                // Limpar o estado quando voltar para a página de customer-info
                setCustomer(null);
                setStep('customer');
                navigate('/customer-info');
                console.log('🔍 DEBUG - Navegação executada com sucesso');
              } catch (error) {
                console.error('🔍 DEBUG - Erro na navegação:', error);
                // Fallback: tentar usar window.location
                window.location.href = '/customer-info';
              }
            }}
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
            disabled={!signed && !existingConsent}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            }
            iconPosition="right"
          >
            Concordar e Continuar
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default TermsPage; 