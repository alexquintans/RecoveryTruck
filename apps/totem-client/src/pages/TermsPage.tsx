import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from '../components/Button';
import { TermsOfService } from '../components/TermsOfService';
import { useTotemStore } from '../store/totemStore';

const TermsPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setStep, setCustomer } = useTotemStore();
  const [signed, setSigned] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const signatureRef = useRef<any>(null);
  
  // Redirecionar se não houver serviço selecionado ou dados do cliente
  if (!selectedService || !customerData) {
    navigate('/customer-info');
    return null;
  }

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
    if (!checkSignature()) {
      setError('Por favor, assine o termo de responsabilidade para continuar.');
      return;
    }

    // Salvar assinatura como base64
    if (signatureRef.current) {
      const signatureData = signatureRef.current.toDataURL();
      
      // Atualizar os dados do cliente com a assinatura
      setCustomer({
        ...customerData,
        signature: signatureData,
        termsAccepted: true,
        termsAcceptedAt: new Date().toISOString(),
      });
      
      // Avançar para a página de pagamento
      setStep('payment');
      navigate('/payment');
    }
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
            disabled={!signed}
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