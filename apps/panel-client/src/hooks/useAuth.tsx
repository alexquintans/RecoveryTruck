import { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { isAuthenticated as checkAuth, getAuthUser } from '@totem/utils';
import { login as loginService, logout as logoutService } from '../services/authService';

interface AuthContextProps {
  user: ReturnType<typeof getAuthUser>;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState(getAuthUser());
  const [loading, setLoading] = useState(false);
  const [isAuth, setIsAuth] = useState(checkAuth());

  const handleLogoutEvent = useCallback(() => {
    setUser(null);
    setIsAuth(false);
  }, []);

  useEffect(() => {
    window.addEventListener('auth:logout', handleLogoutEvent);
    return () => window.removeEventListener('auth:logout', handleLogoutEvent);
  }, [handleLogoutEvent]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      await loginService(email, password);
      setUser(getAuthUser());
      setIsAuth(true);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    logoutService();
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: isAuth, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
} 