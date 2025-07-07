import { API_URL } from '@totem/utils';
import { getAuthToken } from '@totem/utils';
import { withTenant } from '../utils/withTenant';

function authHeaders() {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
}

// ---------- Services ----------
export async function fetchServices(params: any = {}) {
  const url = new URL(`${API_URL}/operator/services`);
  const allParams = withTenant(params);
  Object.entries(allParams).forEach(([k, v]) => url.searchParams.append(k, String(v)));
  const res = await fetch(url.toString(), {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao buscar serviços');
  return res.json();
}

export async function toggleService(id: string, enable: boolean, durationMinutes?: number) {
  const body: any = { is_active: enable };
  if (durationMinutes) body.duration_minutes = durationMinutes;
  const res = await fetch(`${API_URL}/operator/services/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Falha ao atualizar serviço');
  return res.json();
}

export async function updateService(id: string, data: any) {
  const payload = {
    name: data.name,
    description: data.description,
    price: data.price,
    duration_minutes: data.duration ?? data.duration_minutes,
    equipment_count: data.equipment_count,
    is_active: data.isActive ?? data.is_active,
  } as any;
  const res = await fetch(`${API_URL}/operator/services/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Falha ao atualizar serviço');
  return res.json();
}

export async function deleteService(id: string) {
  const res = await fetch(`${API_URL}/operator/services/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao excluir serviço');
  return res.json();
}

// ---------- Create Service ----------
export async function createService(data: any, params: any = {}) {
  const url = new URL(`${API_URL}/operator/services`);
  const allParams = withTenant(params);
  Object.entries(allParams).forEach(([k, v]) => url.searchParams.append(k, String(v)));
  const payload = {
    name: data.name,
    description: data.description || '',
    price: Number(data.price),
    duration_minutes: Number(data.duration_minutes || data.duration || 10),
    equipment_count: Number(data.equipment_count || 1),
    is_active: data.is_active ?? true,
  };
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Falha ao criar serviço: ${res.status} - ${errorText}`);
  }
  return res.json();
}

// ---------- Extras ----------
export async function fetchExtras(params: any = {}) {
  const url = new URL(`${API_URL}/operator/extras`);
  const allParams = withTenant(params);
  Object.entries(allParams).forEach(([k, v]) => url.searchParams.append(k, String(v)));
  const res = await fetch(url.toString(), {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao buscar extras');
  return res.json();
}

export async function toggleExtra(id: string, enable: boolean, stock?: number) {
  const body: any = { is_active: enable };
  if (stock !== undefined) body.stock = stock;
  const res = await fetch(`${API_URL}/operator/extras/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Falha ao atualizar extra');
  return res.json();
}

export async function updateExtra(id: string, data: any) {
  const payload = {
    name: data.name,
    description: data.description,
    price: data.price,
    category: data.category,
    stock: data.stock,
    is_active: data.isActive ?? data.is_active,
  } as any;
  const res = await fetch(`${API_URL}/operator/extras/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Falha ao atualizar extra');
  return res.json();
}

export async function deleteExtra(id: string) {
  const res = await fetch(`${API_URL}/operator/extras/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao excluir item extra');
  return res.json();
}

// ---------- Create Extra ----------
export async function createExtra(data: any, params: any = {}) {
  const url = new URL(`${API_URL}/operator/extras`);
  const allParams = withTenant(params);
  Object.entries(allParams).forEach(([k, v]) => url.searchParams.append(k, String(v)));
  const payload = {
    name: data.name,
    description: data.description || '',
    price: Number(data.price),
    category: data.category || '',
    stock: Number(data.stock || 0),
    is_active: data.is_active ?? true,
  };
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Falha ao criar item extra: ${res.status} - ${errorText}`);
  }
  return res.json();
}

// ---------- Equipments ----------
export async function fetchEquipments(params: any = {}) {
  const url = new URL(`${API_URL}/operator/equipments`);
  const allParams = withTenant(params);
  Object.entries(allParams).forEach(([k, v]) => url.searchParams.append(k, String(v)));
  const res = await fetch(url.toString(), {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao buscar equipamentos');
  return res.json();
}

export async function assignEquipment(operatorId: string, equipmentId: string) {
  const res = await fetch(`${API_URL}/operator/equipments/assign`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ operator_id: operatorId, equipment_id: equipmentId }),
  });
  if (!res.ok) throw new Error('Falha ao atribuir equipamento');
  return res.json();
}

export async function releaseEquipment(operatorId: string, equipmentId: string) {
  const res = await fetch(`${API_URL}/equipments/release`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ operator_id: operatorId, equipment_id: equipmentId }),
  });
  if (!res.ok) throw new Error('Falha ao liberar equipamento');
  return res.json();
}

// ---------- Sessions ----------
export async function startSession(operatorId: string, equipmentId: string, configJson: any) {
  const res = await fetch(`${API_URL}/sessions/start`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ operator_id: operatorId, equipment_id: equipmentId, config_json: configJson }),
  });
  if (!res.ok) throw new Error('Falha ao iniciar sessão');
  return res.json();
}

export async function finishSession(sessionId: string) {
  const res = await fetch(`${API_URL}/sessions/finish?session_id=${sessionId}`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao finalizar sessão');
  return res.json();
}

export async function getActiveSession(operatorId: string) {
  const res = await fetch(`${API_URL}/sessions/active?operator_id=${operatorId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Falha ao buscar sessão ativa');
  return res.json();
}

export async function saveOperationConfig(payload: any) {
  const url = new URL(`${API_URL}/operation/config`);
  if (payload.tenant_id) {
    url.searchParams.append('tenant_id', payload.tenant_id);
  }
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Falha ao salvar configuração da operação');
  return res.json();
} 