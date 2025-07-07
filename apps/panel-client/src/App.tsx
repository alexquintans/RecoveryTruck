import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Páginas
import DashboardPage from './pages/DashboardPage';
import DisplayPage from './pages/DisplayPage';
import OperatorPage from './pages/OperatorPage';
import LoginPage from './pages/LoginPage';

// Componentes de layout
import Layout from './components/Layout';
import RequireAuth from './components/RequireAuth';

function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/"
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="display" element={<DisplayPage />} />
          <Route path="operator" element={<OperatorPage />} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

export default App; 