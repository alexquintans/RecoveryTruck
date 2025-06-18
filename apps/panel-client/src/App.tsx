import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Páginas
import DashboardPage from './pages/DashboardPage';
import DisplayPage from './pages/DisplayPage';
import OperatorPage from './pages/OperatorPage';

// Componentes de layout
import Layout from './components/Layout';

function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        {/* Rotas do painel */}
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="display" element={<DisplayPage />} />
          <Route path="operator" element={<OperatorPage />} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

export default App; 