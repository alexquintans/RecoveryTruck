import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const Layout: React.FC = () => {
  const location = useLocation();
  
  // Verificar se estamos na página de exibição para esconder a navegação
  const isDisplayPage = location.pathname === '/display';

  return (
    <div className="min-h-screen bg-background">
      {/* Cabeçalho */}
      {!isDisplayPage && (
        <header className="bg-primary text-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <img 
                  src="/logo.png" 
                  alt="RecoveryTruck Logo" 
                  className="h-10 w-10 mr-2"
                />
                <span className="font-bold text-xl">RecoveryTruck</span>
              </div>
              
              <nav className="flex space-x-4">
                <NavLink to="/" exact>Dashboard</NavLink>
                <NavLink to="/display">Tela de Chamada</NavLink>
                <NavLink to="/operator">Operador</NavLink>
              </nav>
            </div>
          </div>
        </header>
      )}
      
      {/* Conteúdo principal */}
      <main className={isDisplayPage ? '' : 'panel-container'}>
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Outlet />
        </motion.div>
      </main>
      
      {/* Rodapé */}
      {!isDisplayPage && (
        <footer className="bg-gray-100 border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              &copy; {new Date().getFullYear()} RecoveryTruck. Todos os direitos reservados.
            </p>
          </div>
        </footer>
      )}
    </div>
  );
};

// Componente de link de navegação com estado ativo
interface NavLinkProps {
  to: string;
  exact?: boolean;
  children: React.ReactNode;
}

const NavLink: React.FC<NavLinkProps> = ({ to, exact, children }) => {
  const location = useLocation();
  const isActive = exact ? location.pathname === to : location.pathname.startsWith(to);
  
  return (
    <Link
      to={to}
      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        isActive
          ? 'bg-secondary text-primary font-bold'
          : 'text-white/80 hover:bg-secondary/50 hover:text-primary'
      }`}
    >
      {children}
    </Link>
  );
};

export default Layout; 