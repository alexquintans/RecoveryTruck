import { api, API_URL } from '@totem/utils';
import { setAuthToken, setAuthUser } from '@totem/utils';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface Operator {
  id: string;
  name: string;
  email: string;
  tenant_id: string;
}

export async function login(email: string, password: string): Promise<void> {
  // FastAPI espera form-urlencoded
  const body = new URLSearchParams();
  body.append('username', email);
  body.append('password', password);
  
  const response = await fetch(`${API_URL}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Falha no login');
  }
  const data: LoginResponse & { operator?: Operator } = await response.json();
  
  setAuthToken(data.access_token);
  if (data.operator) {
    setAuthUser({
      id: data.operator.id,
      name: data.operator.name,
      email: data.operator.email,
      role: 'operator',
      tenant_id: data.operator.tenant_id,
    });
  }
}

export function logout() {
  localStorage.clear();
  // Emite evento global (capturado em useAuth)
  window.dispatchEvent(new CustomEvent('auth:logout'));
} 