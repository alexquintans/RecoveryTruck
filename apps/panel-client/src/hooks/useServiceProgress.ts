import { useState, useCallback } from 'react';
import { useAuth } from './useAuth';

export interface ServiceProgress {
  id: string;
  ticket_service_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  duration_minutes: number;
  operator_notes?: string;
  equipment_id?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  service_name: string;
  service_price: number;
  equipment_name?: string;
}

export const useServiceProgress = () => {
  const { user } = useAuth();
  const [serviceProgress, setServiceProgress] = useState<Record<string, ServiceProgress[]>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const fetchServiceProgress = useCallback(async (ticketId: string) => {
    if (!user?.token) return [];

    setLoading(prev => ({ ...prev, [ticketId]: true }));
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/ticket-service-progress/ticket/${ticketId}`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'X-Tenant-Id': user.tenant_id || ''
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setServiceProgress(prev => ({
          ...prev,
          [ticketId]: data.items
        }));
        return data.items;
      }
    } catch (error) {
      console.error('Erro ao buscar progresso dos serviços:', error);
    } finally {
      setLoading(prev => ({ ...prev, [ticketId]: false }));
    }
    
    return [];
  }, [user]);

  const startServiceProgress = useCallback(async (progressId: string, equipmentId?: string) => {
    if (!user?.token) return null;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/ticket-service-progress/${progressId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'X-Tenant-Id': user.tenant_id || '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ equipment_id: equipmentId })
      });
      
      if (response.ok) {
        const updatedProgress = await response.json();
        setServiceProgress(prev => {
          const newState = { ...prev };
          Object.keys(newState).forEach(ticketId => {
            newState[ticketId] = newState[ticketId].map(progress => 
              progress.id === progressId ? { ...progress, ...updatedProgress } : progress
            );
          });
          return newState;
        });
        return updatedProgress;
      }
    } catch (error) {
      console.error('Erro ao iniciar serviço:', error);
    }
    
    return null;
  }, [user]);

  const completeServiceProgress = useCallback(async (progressId: string, notes?: string) => {
    if (!user?.token) return null;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/ticket-service-progress/${progressId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'X-Tenant-Id': user.tenant_id || '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ operator_notes: notes })
      });
      
      if (response.ok) {
        const updatedProgress = await response.json();
        setServiceProgress(prev => {
          const newState = { ...prev };
          Object.keys(newState).forEach(ticketId => {
            newState[ticketId] = newState[ticketId].map(progress => 
              progress.id === progressId ? { ...progress, ...updatedProgress } : progress
            );
          });
          return newState;
        });
        return updatedProgress;
      }
    } catch (error) {
      console.error('Erro ao completar serviço:', error);
    }
    
    return null;
  }, [user]);

  const cancelServiceProgress = useCallback(async (progressId: string, reason: string) => {
    if (!user?.token) return null;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/ticket-service-progress/${progressId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'X-Tenant-Id': user.tenant_id || '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        const updatedProgress = await response.json();
        setServiceProgress(prev => {
          const newState = { ...prev };
          Object.keys(newState).forEach(ticketId => {
            newState[ticketId] = newState[ticketId].map(progress => 
              progress.id === progressId ? { ...progress, ...updatedProgress } : progress
            );
          });
          return newState;
        });
        return updatedProgress;
      }
    } catch (error) {
      console.error('Erro ao cancelar serviço:', error);
    }
    
    return null;
  }, [user]);

  const getProgressStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'pending': return 'bg-gray-100 text-gray-700 border-gray-300';
      case 'in_progress': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'completed': return 'bg-green-100 text-green-700 border-green-300';
      case 'cancelled': return 'bg-red-100 text-red-700 border-red-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  }, []);

  const getProgressStatusText = useCallback((status: string) => {
    switch (status) {
      case 'pending': return 'Pendente';
      case 'in_progress': return 'Em Andamento';
      case 'completed': return 'Concluído';
      case 'cancelled': return 'Cancelado';
      default: return 'Pendente';
    }
  }, []);

  return {
    serviceProgress,
    loading,
    fetchServiceProgress,
    startServiceProgress,
    completeServiceProgress,
    cancelServiceProgress,
    getProgressStatusColor,
    getProgressStatusText
  };
}; 