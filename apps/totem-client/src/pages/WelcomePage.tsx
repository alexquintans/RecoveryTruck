import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { useTotemStore } from '../store/totemStore';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const { setStep, reset } = useTotemStore();

  // Resetar o estado ao carregar a página inicial
  useEffect(() => {
    reset();
  }, [reset]);

  const handleStart = () => {
    // Atualizar o estado para a etapa de seleção de serviço
    setStep('service');
    
    // Navegar para a página de seleção de serviço
    navigate('/service');
  };

  // Animações
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        when: "beforeChildren",
        staggerChildren: 0.2,
        duration: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <div className="totem-card">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="text-center"
      >
        <motion.div variants={itemVariants}>
          <img 
            src="/logo.png?v=2" 
            alt="RecoveryTruck Logo" 
            className="w-64 h-auto mx-auto mb-8"
            onError={(e) => {
              e.currentTarget.src = 'https://via.placeholder.com/200?text=RecoveryTruck';
            }}
          />
        </motion.div>

        <motion.h1 
          variants={itemVariants}
          className="text-4xl font-bold text-primary mb-4"
        >
          Bem-vindo ao RecoveryTruck
        </motion.h1>
        
        <motion.p 
          variants={itemVariants}
          className="text-xl text-text-light mb-6"
        >
          Toque no botão abaixo para iniciar seu atendimento
        </motion.p>

        <motion.div 
          variants={itemVariants}
          className="flex flex-col gap-4 items-center mb-8"
        >
          <div className="flex items-center gap-2 text-text-light">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Serviços de recuperação física</span>
          </div>
          <div className="flex items-center gap-2 text-text-light">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Pagamento rápido e seguro</span>
          </div>
          <div className="flex items-center gap-2 text-text-light">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Atendimento profissional</span>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          className="flex justify-center"
        >
          <Button 
            variant="primary" 
            size="xl"
            onClick={handleStart}
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            }
            iconPosition="right"
            className="px-10 py-5 text-2xl"
          >
            INICIAR ATENDIMENTO
          </Button>
        </motion.div>
        
        <motion.p
          variants={itemVariants}
          className="mt-8 text-sm text-text-light"
        >
          Toque na tela para interagir • Versão 1.0.0
        </motion.p>
      </motion.div>
    </div>
  );
};

export default WelcomePage; 