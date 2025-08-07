import { useState, useCallback } from 'react';

interface OperatorConfig {
  operatorName: string;
  services: any[];
  extras: any[];
  equipments: any[];
  paymentModes: string[];
  selectedEquipment: string;
  activeTab: string;
  activeServiceTab: string;
}

export function useOperatorConfig() {
  const [config, setConfig] = useState<OperatorConfig | null>(() => {
    try {
      const saved = localStorage.getItem('operator_config');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.warn('❌ ERRO ao carregar configuração do operador:', error);
      return null;
    }
  });

  const saveConfig = useCallback((newConfig: Partial<OperatorConfig>) => {
    try {
      const updatedConfig = { ...config, ...newConfig };
      setConfig(updatedConfig);
      localStorage.setItem('operator_config', JSON.stringify(updatedConfig));
      console.log('🔍 DEBUG - Configuração do operador salva:', updatedConfig);
    } catch (error) {
      console.error('❌ ERRO ao salvar configuração do operador:', error);
    }
  }, [config]);

  const clearConfig = useCallback(() => {
    try {
      setConfig(null);
      localStorage.removeItem('operator_config');
      console.log('🔍 DEBUG - Configuração do operador limpa');
    } catch (error) {
      console.error('❌ ERRO ao limpar configuração do operador:', error);
    }
  }, []);

  const updateConfigField = useCallback((field: keyof OperatorConfig, value: any) => {
    saveConfig({ [field]: value });
  }, [saveConfig]);

  return { 
    config, 
    saveConfig, 
    clearConfig, 
    updateConfigField 
  };
} 