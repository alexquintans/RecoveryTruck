import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface AdminAccessProps {
  children: React.ReactNode;
}

const AdminAccess: React.FC<AdminAccessProps> = ({ children }) => {
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  // Senha administrativa (em um sistema real, isso seria validado no backend)
  const ADMIN_PASSWORD = 'admin123';
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password === ADMIN_PASSWORD) {
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('Senha incorreta');
    }
  };
  
  if (isAuthenticated) {
    return <>{children}</>;
  }
  
  return (
    <div className="flex items-center justify-center h-screen bg-primary p-6">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6 text-center">Acesso Administrativo</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Senha
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Digite a senha de administrador"
              required
            />
          </div>
          
          {error && (
            <div className="mb-4 text-red-600 text-sm">
              {error}
            </div>
          )}
          
          <div className="flex space-x-4">
            <button
              type="submit"
              className="flex-1 bg-primary text-white py-2 px-4 rounded-md hover:bg-primary-dark"
            >
              Acessar
            </button>
            
            <button
              type="button"
              onClick={() => navigate('/')}
              className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminAccess; 