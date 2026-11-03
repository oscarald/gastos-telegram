import { BrowserRouter, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import GastosPage from './pages/GastosPage';
import CategoriasPage from './pages/CategoriasPage';
import ReglasPage from './pages/ReglasPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/gastos" element={<GastosPage />} />
          <Route path="/categorias" element={<CategoriasPage />} />
          <Route path="/reglas" element={<ReglasPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
