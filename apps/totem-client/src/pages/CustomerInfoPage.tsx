import * as React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { PrivacyPolicy } from '../components/PrivacyPolicy';
import { useTotemStore } from '../store/totemStore';
import { validateCPF, validatePhone, validateName, formatCPF, formatPhone } from '../utils';
import type { Customer } from '../types';

const CustomerInfoPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedService, customerData, setCustomer, setStep } = useTotemStore();
  
  // Estado do formulário
  const [formData, setFormData] = useState<Partial<Customer>>(
    customerData || {
      name: '',
      cpf: '',
      phone: '',
      consentTerms: false,
    }
  );
  
  // Estado de erros
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // Estado do modal de política de privacidade
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false);
  
  // Redirecionar se não houver serviço selecionado
  if (!selectedService) {
    navigate('/service');
    return null;
  }

  // Lidar com mudanças nos campos
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    // Formatar CPF e telefone
    let formattedValue: string | boolean = value;
    if (name === 'cpf') {
      formattedValue = formatCPF(value);
    } else if (name === 'phone') {
      formattedValue = formatPhone(value);
    } else if (type === 'checkbox') {
      formattedValue = checked;
    }
    
    setFormData((prev) => ({
      ...prev,
      [name]: formattedValue,
    }));
    
    // Limpar erro ao editar campo
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  // Validar formulário
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!validateName(formData.name || '')) {
      newErrors.name = 'Nome completo é obrigatório (mínimo 3 caracteres)';
    }
    
    if (formData.cpf && !validateCPF(formData.cpf)) {
      newErrors.cpf = 'CPF inválido';
    }
    
    if (formData.phone && !validatePhone(formData.phone)) {
      newErrors.phone = 'Telefone inválido';
    }
    
    if (!formData.consentTerms) {
      newErrors.consentTerms = 'Você precisa concordar com os termos';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Enviar formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      setCustomer(formData as Customer);
      setStep('terms');
      navigate('/terms');
    }
  };

  // Voltar para a página anterior
  const handleBack = () => {
    navigate('/service');
  };

  // Abrir modal de política de privacidade
  const handleOpenPrivacyPolicy = () => {
    setShowPrivacyPolicy(true);
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
            Suas Informações
          </h2>
          <p className="text-text-light">
            Preencha seus dados para continuar com o serviço: 
            <span className="font-semibold text-primary ml-1">
              {selectedService.name}
            </span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nome */}
          <div>
            <label htmlFor="name" className="block text-lg font-medium mb-2">
              Nome Completo <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={`w-full p-4 text-lg rounded-xl border ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              } focus:ring-2 focus:ring-primary focus:border-transparent`}
              placeholder="Digite seu nome completo"
              autoComplete="name"
            />
            {errors.name && (
              <p className="mt-1 text-red-500">{errors.name}</p>
            )}
          </div>

          {/* CPF */}
          <div>
            <label htmlFor="cpf" className="block text-lg font-medium mb-2">
              CPF
            </label>
            <input
              type="text"
              id="cpf"
              name="cpf"
              value={formData.cpf}
              onChange={handleChange}
              className={`w-full p-4 text-lg rounded-xl border ${
                errors.cpf ? 'border-red-500' : 'border-gray-300'
              } focus:ring-2 focus:ring-primary focus:border-transparent`}
              placeholder="000.000.000-00"
              maxLength={14}
              autoComplete="off"
            />
            {errors.cpf && (
              <p className="mt-1 text-red-500">{errors.cpf}</p>
            )}
          </div>

          {/* Telefone */}
          <div>
            <label htmlFor="phone" className="block text-lg font-medium mb-2">
              Telefone
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className={`w-full p-4 text-lg rounded-xl border ${
                errors.phone ? 'border-red-500' : 'border-gray-300'
              } focus:ring-2 focus:ring-primary focus:border-transparent`}
              placeholder="(00) 00000-0000"
              maxLength={15}
              autoComplete="tel"
            />
            {errors.phone && (
              <p className="mt-1 text-red-500">{errors.phone}</p>
            )}
          </div>

          {/* Termos de consentimento */}
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                id="consentTerms"
                name="consentTerms"
                type="checkbox"
                checked={formData.consentTerms}
                onChange={handleChange}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
            </div>
            <div className="ml-3">
              <label htmlFor="consentTerms" className="text-base">
                <span className="text-red-500 mr-1">*</span>
                Concordo com o tratamento dos meus dados pessoais conforme a{' '}
                <button
                  type="button"
                  onClick={handleOpenPrivacyPolicy}
                  className="text-primary hover:underline focus:outline-none"
                >
                  Política de Privacidade
                </button>
              </label>
              {errors.consentTerms && (
                <p className="mt-1 text-red-500">{errors.consentTerms}</p>
              )}
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
              type="submit"
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
        </form>

        {/* Modal de Política de Privacidade */}
        <Modal
          isOpen={showPrivacyPolicy}
          onClose={() => setShowPrivacyPolicy(false)}
          title="Política de Privacidade"
          size="lg"
        >
          <PrivacyPolicy />
        </Modal>
      </motion.div>
    </div>
  );
};

export default CustomerInfoPage; 