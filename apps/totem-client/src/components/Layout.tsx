import React from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import KioskAdminTrigger from './KioskAdminTrigger';

const Layout = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 py-4 flex-shrink-0">
        <div className="container mx-auto px-4 flex items-center justify-center">
          <img 
            src="/logo192.png?v=2" 
            alt="RecoveryTruck Logo" 
            className="h-16 w-auto"
          />
        </div>
      </header>
      
      {/* Main content */}
      <main className="flex-grow flex items-center justify-center p-4 overflow-y-auto">
        <motion.div 
          className="w-full max-w-4xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Outlet />
        </motion.div>
      </main>
      
      {/* Footer */}
      <footer className="bg-primary text-white py-4 text-center relative">
        <div className="container mx-auto px-4">
          <p>© {new Date().getFullYear()} RecoveryTruck - Todos os direitos reservados</p>
          
          {/* Versão e indicação para tocar na tela */}
          <p className="text-xs text-white/70 mt-1">
            Toque na tela para interagir • Versão 1.0.0
          </p>
        </div>
      </footer>

      {/* Componente invisível que detecta a sequência de toques para acesso administrativo */}
      <KioskAdminTrigger />
    </div>
  );
};

export default Layout; 