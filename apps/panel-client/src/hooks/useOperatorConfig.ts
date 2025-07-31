import { useState, useEffect, useCallback } from 'react';
import {
  fetchServices,
  fetchExtras,
  fetchEquipments,
  toggleService as apiToggleService,
  toggleExtra as apiToggleExtra,
  assignEquipment as apiAssignEq,
  releaseEquipment as apiReleaseEq,
  getActiveSession,
} from '../services/operatorConfigService';
import { useAuth } from './useAuth';
import { API_URL } from '@totem/utils';

interface Service {
  id: string;
  name: string;
  duration_minutes: number;
  is_active: boolean;
  price: number;
}
interface Extra {
  id: string;
  name: string;
  stock: number;
  is_active: boolean;
  price: number;
}
interface Equipment {
  id: string;
  identifier: string;
  status: string;
  assigned_operator_id?: string;
}

export function useOperatorConfig() {
  const { user } = useAuth();
  const tenantId = (user as any)?.tenant_id; // JWT pode ter tenant_id
  const operatorId = user?.id;

  

  const [services, setServices] = useState<Service[]>([]);
  const [extras, setExtras] = useState<Extra[]>([]);
  const [equipments, setEquipments] = useState<Equipment[]>([]);

  // --- Fetch inicial ---
  useEffect(() => {
    if (!tenantId) return;
    (async () => {
      try {
        setServices(await fetchServices(tenantId));
        setExtras(await fetchExtras(tenantId));
        setEquipments(await fetchEquipments(tenantId));
      } catch (e) {
        console.error(e);
      }
    })();
  }, [tenantId]);

  // --- WebSocket ---
  useEffect(() => {
    if (!tenantId) {
      return;
    }
    
    const token = localStorage.getItem('token');
    
    const wsUrl = `${API_URL.replace('http', 'ws')}/ws/${tenantId}/operator${token ? `?token=${token}` : ''}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      // WebSocket conectado
    };
    
    ws.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
    };
    
    ws.onclose = () => {
      // WebSocket desconectado
    };
    
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        
        if (msg.type === 'service_update') {
          setServices((prev) => {
            const idx = prev.findIndex((s) => s.id === msg.data.service_id);
            if (idx === -1) return prev;
            const updated = [...prev];
            updated[idx] = { ...updated[idx], ...msg.data } as any;
            return updated;
          });
        }
        if (msg.type === 'extra_update') {
          setExtras((prev) => {
            const idx = prev.findIndex((e) => e.id === msg.data.extra_id);
            if (idx === -1) return prev;
            const updated = [...prev];
            updated[idx] = { ...updated[idx], ...msg.data } as any;
            return updated;
          });
        }
        if (msg.type === 'queue_update' && msg.data.equipment_id) {
          setEquipments((prev) => {
            const idx = prev.findIndex((e) => e.id === msg.data.equipment_id);
            if (idx === -1) return prev;
            const updated = [...prev];
            updated[idx] = { ...updated[idx], status: msg.data.status } as any;
            return updated;
          });
        }
        if (msg.type === 'equipment_update') {
          setEquipments((prev) => {
            const idx = prev.findIndex((e) => e.id === msg.data.id);
            if (idx === -1) {
              return prev;
            }
            const updated = [...prev];
            updated[idx] = { 
              ...updated[idx], 
              status: msg.data.status,
              assigned_operator_id: msg.data.assigned_operator_id 
            } as any;
            return updated;
          });
        }
      } catch (err) {
        console.error('Erro ao processar mensagem WebSocket:', err);
      }
    };
    return () => ws.close();
  }, [tenantId]);

  // --- Restaurar sessão ativa ---
  useEffect(() => {
    if (!operatorId) return;
    (async () => {
      try {
        const session = await getActiveSession(operatorId);
        if (session && session.config_json) {
          // Restaurar seleção de serviços/extras/equipamento
          if (session.config_json.services) setServices(session.config_json.services);
          if (session.config_json.extras) setExtras(session.config_json.extras);
          if (session.equipment_id) setEquipments((prev) => prev.map(e => e.id === session.equipment_id ? { ...e, status: 'in_use', assigned_operator_id: operatorId } : e));
        }
      } catch (e) {
        // Se não houver sessão ativa, ignora
      }
    })();
  }, [operatorId]);

  // --- Actions ---
  const toggleService = useCallback(async (id: string, enable: boolean, duration?: number) => {
    await apiToggleService(id, enable, duration);
    setServices((prev) => prev.map((s) => (s.id === id ? { ...s, is_active: enable, duration_minutes: duration ?? s.duration_minutes } : s)));
  }, []);

  const toggleExtra = useCallback(async (id: string, enable: boolean, stock?: number) => {
    await apiToggleExtra(id, enable, stock);
    setExtras((prev) => prev.map((e) => (e.id === id ? { ...e, is_active: enable, stock: stock ?? e.stock } : e)));
  }, []);

  const assignEquipment = useCallback(async (equipmentId: string) => {
    if (!operatorId) return;
    await apiAssignEq(operatorId, equipmentId);
    setEquipments((prev) => prev.map((e) => (e.id === equipmentId ? { ...e, status: 'in_use', assigned_operator_id: operatorId } : e)));
  }, [operatorId]);

  const releaseEquipment = useCallback(async (equipmentId: string) => {
    if (!operatorId) return;
    await apiReleaseEq(operatorId, equipmentId);
    setEquipments((prev) => prev.map((e) => (e.id === equipmentId ? { ...e, status: 'online', assigned_operator_id: undefined } : e)));
  }, [operatorId]);

  // --- Snapshot para persistência ---
  const getSnapshot = useCallback(() => ({
    services,
    extras,
    equipments,
  }), [services, extras, equipments]);

  return {
    services,
    extras,
    equipments,
    toggleService,
    toggleExtra,
    assignEquipment,
    releaseEquipment,
    getSnapshot,
  };
} 