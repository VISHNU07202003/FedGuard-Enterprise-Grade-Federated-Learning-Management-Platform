import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from '@/layouts/MainLayout';
import { Dashboard } from '@/pages/Dashboard';
import { TrainingRuns } from '@/pages/TrainingRuns';
import { TrainingRunDetail } from '@/pages/TrainingRunDetail';
import { Clients } from '@/pages/Clients';
import { Topology } from '@/pages/Topology';
import { ModelRegistry } from '@/pages/ModelRegistry';
import { Copilot } from '@/pages/Copilot';
import { PlaceholderPage } from '@/pages/PlaceholderPage';
import { Settings } from '@/pages/Settings';

import { AuthProvider } from '@/features/auth/AuthContext';
import { ProtectedRoute } from '@/features/auth/ProtectedRoute';
import Login from '@/pages/Login';

import { Observability } from '@/pages/Observability';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
              <Route index element={<Dashboard />} />
              <Route path="training" element={<TrainingRuns />} />
              <Route path="training/:id" element={<TrainingRunDetail />} />
              <Route path="clients" element={<Clients />} />
              <Route path="topology" element={<Topology />} />
              <Route 
                path="experiments" 
                element={<ProtectedRoute allowedRoles={['admin', 'researcher']}><PlaceholderPage title="Experiments" description="Hyperparameter search and A/B testing." /></ProtectedRoute>} 
              />
              <Route path="models" element={<ModelRegistry />} />
              <Route 
                path="security" 
                element={<PlaceholderPage title="Security" description="Threat detection, audit logs, and access control." />} 
              />
              <Route 
                path="observability" 
                element={<Observability />} 
              />
              <Route 
                path="copilot" 
                element={<Copilot />} 
              />
              <Route 
                path="settings" 
                element={<Settings />} 
              />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
