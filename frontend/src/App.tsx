import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/Layout';
import { ProtectedRoute, PublicRoute, AdminRoute } from './components/ProtectedRoute';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { DashboardPage } from './pages/DashboardPage';
import { DepartmentsPage } from './pages/DepartmentsPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { GoogleCallbackPage } from './pages/GoogleCallbackPage';
import { LoginPage } from './pages/LoginPage';
import { OrgChartPage } from './pages/OrgChartPage';
import { ProfilePage } from './pages/ProfilePage';
import { RegisterPage } from './pages/RegisterPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { UsersPage } from './pages/UsersPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/departments" element={<DepartmentsPage />} />
              <Route path="/org-chart" element={<OrgChartPage />} />
              <Route element={<AdminRoute />}>
                <Route path="/admin/users" element={<UsersPage />} />
                <Route path="/admin/audit-logs" element={<AuditLogsPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
