import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Falha ao entrar');
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <main className="flex-1 flex flex-col items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl shadow-xl px-8 py-10 w-full max-w-md flex flex-col items-center animate-fade-in"
        >
          <div className="mb-4">
            <svg className="w-12 h-12 text-blue-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="8" rx="4" strokeWidth="2" /><path d="M7 11V7a5 5 0 0110 0v4" strokeWidth="2" /></svg>
          </div>
          <h1 className="text-2xl font-bold mb-2 text-gray-800">Login do Operador</h1>
          <div className="w-full mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all text-gray-800 bg-gray-50"
              required
              autoFocus
            />
          </div>
          <div className="w-full mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-1">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all text-gray-800 bg-gray-50"
              required
            />
          </div>
          {error && <p className="text-red-500 text-xs italic mb-3 w-full text-center">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold text-base shadow hover:bg-blue-700 active:scale-95 transition-all mt-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" /></svg>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </main>
      <footer className="text-center text-xs text-gray-400 py-4">© 2025 RecoveryTruck. Todos os direitos reservados.</footer>
    </div>
  );
} 