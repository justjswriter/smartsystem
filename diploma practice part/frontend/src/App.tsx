import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import Login from './pages/Login';
import Plants from './pages/Plants';
import PlantDetail from './pages/PlantDetail';
import './index.css';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/plants" element={<Plants />} />
          <Route path="/plants/:id" element={<PlantDetail />} />
          <Route path="/" element={<Navigate to="/plants" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
