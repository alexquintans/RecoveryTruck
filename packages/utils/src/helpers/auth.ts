import { getStorageItem, setStorageItem, removeStorageItem } from './storage';

// Constantes
const TOKEN_KEY = 'totem_auth_token';
const USER_KEY = 'totem_user';

/**
 * Interface para o usuário autenticado
 */
export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: string;
  tenant_id?: string;
}

/**
 * Salva o token JWT no localStorage
 */
export function setAuthToken(token: string): void {
  setStorageItem(TOKEN_KEY, token);
}

/**
 * Obtém o token JWT do localStorage
 */
export function getAuthToken(): string | null {
  return getStorageItem<string>(TOKEN_KEY);
}

/**
 * Salva os dados do usuário no localStorage
 */
export function setAuthUser(user: AuthUser): void {
  setStorageItem(USER_KEY, user);
}

/**
 * Obtém os dados do usuário do localStorage
 */
export function getAuthUser(): AuthUser | null {
  return getStorageItem<AuthUser>(USER_KEY);
}

/**
 * Verifica se o usuário está autenticado
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  if (!token) return false;
  
  // Verifica se o token está expirado
  try {
    const payload = parseJwt(token);
    const expiry = payload.exp * 1000; // Converte para milissegundos
    
    return new Date().getTime() < expiry;
  } catch (error) {
    return false;
  }
}

/**
 * Realiza o logout do usuário
 */
export function logout(): void {
  removeStorageItem(TOKEN_KEY);
  removeStorageItem(USER_KEY);
}

/**
 * Decodifica um token JWT sem verificação de assinatura
 * (apenas para leitura do payload)
 */
export function parseJwt(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    return JSON.parse(jsonPayload);
  } catch (error) {
    throw new Error('Token inválido');
  }
} 