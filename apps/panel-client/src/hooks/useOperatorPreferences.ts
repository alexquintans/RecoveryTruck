import { useState, useCallback } from 'react';

interface OperatorPreferences {
  selectedEquipment: string;
  activeTab: string;
  activeServiceTab: string;
  autoRefresh: boolean;
  showNotifications: boolean;
  soundEnabled: boolean;
  theme: 'light' | 'dark' | 'auto';
}

const DEFAULT_PREFERENCES: OperatorPreferences = {
  selectedEquipment: '',
  activeTab: 'operation',
  activeServiceTab: '',
  autoRefresh: true,
  showNotifications: true,
  soundEnabled: true,
  theme: 'auto'
};

export function useOperatorPreferences() {
  const [preferences, setPreferences] = useState<OperatorPreferences>(() => {
    try {
      const saved = localStorage.getItem('operator_preferences');
      return saved ? { ...DEFAULT_PREFERENCES, ...JSON.parse(saved) } : DEFAULT_PREFERENCES;
    } catch (error) {
      console.warn('❌ ERRO ao carregar preferências do operador:', error);
      return DEFAULT_PREFERENCES;
    }
  });

  const updatePreference = useCallback((key: keyof OperatorPreferences, value: any) => {
    try {
      const newPreferences = { ...preferences, [key]: value };
      setPreferences(newPreferences);
      localStorage.setItem('operator_preferences', JSON.stringify(newPreferences));
      console.log('🔍 DEBUG - Preferência atualizada:', key, value);
    } catch (error) {
      console.error('❌ ERRO ao salvar preferência do operador:', error);
    }
  }, [preferences]);

  const updateMultiplePreferences = useCallback((updates: Partial<OperatorPreferences>) => {
    try {
      const newPreferences = { ...preferences, ...updates };
      setPreferences(newPreferences);
      localStorage.setItem('operator_preferences', JSON.stringify(newPreferences));
      console.log('🔍 DEBUG - Múltiplas preferências atualizadas:', updates);
    } catch (error) {
      console.error('❌ ERRO ao salvar múltiplas preferências do operador:', error);
    }
  }, [preferences]);

  const resetPreferences = useCallback(() => {
    try {
      setPreferences(DEFAULT_PREFERENCES);
      localStorage.setItem('operator_preferences', JSON.stringify(DEFAULT_PREFERENCES));
      console.log('🔍 DEBUG - Preferências resetadas para padrão');
    } catch (error) {
      console.error('❌ ERRO ao resetar preferências do operador:', error);
    }
  }, []);

  const clearPreferences = useCallback(() => {
    try {
      setPreferences(DEFAULT_PREFERENCES);
      localStorage.removeItem('operator_preferences');
      console.log('🔍 DEBUG - Preferências limpas');
    } catch (error) {
      console.error('❌ ERRO ao limpar preferências do operador:', error);
    }
  }, []);

  return { 
    preferences, 
    updatePreference, 
    updateMultiplePreferences,
    resetPreferences,
    clearPreferences 
  };
}
