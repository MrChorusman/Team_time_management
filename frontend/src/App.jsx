import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { NotificationProvider } from './contexts/NotificationContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from 'sonner'

// Componentes de layout
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import LoadingSpinner from './components/ui/LoadingSpinner'

// Páginas principales
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import VerifyEmailPage from './pages/auth/VerifyEmailPage'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage'
import DashboardPage from './pages/DashboardPage'
import CalendarPage from './pages/CalendarPage'
import ForecastPage from './pages/ForecastPage'
import EmployeesPage from './pages/EmployeesPage'
import TeamsPage from './pages/TeamsPage'
import ReportsPage from './pages/ReportsPage'
import NotificationsPage from './pages/NotificationsPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'
import AdminCalendarsPage from './pages/admin/AdminCalendarsPage'
import EmployeeRegisterPage from './pages/employee/EmployeeRegisterPage'
import CalendarDemoPage from './pages/CalendarDemoPage'
import ProjectsPage from './pages/ProjectsPage'

import './App.css'

// Componente de rutas protegidas
function ProtectedRoute({ children, requiredRole = null }) {
  const { user, employee, loading } = useAuth()
  
  if (loading) {
    return <LoadingSpinner />
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  // Si el usuario no tiene empleado registrado, redirigir al registro
  // EXCEPTO para administradores y managers que pueden acceder directamente
  if (user && !employee && window.location.pathname !== '/employee/register') {
    // Verificar si es admin o manager (roles son strings)
    const userRoles = user.roles || []
    const isAdminOrManager = userRoles.includes('admin') || userRoles.includes('manager')
    
    if (!isAdminOrManager) {
      return <Navigate to="/employee/register" replace />
    }
  }
  
  // Verificar rol requerido (roles son strings, no objetos)
  if (requiredRole && user.roles) {
    if (!user.roles.includes(requiredRole)) {
      return <Navigate to="/dashboard" replace />
    }
  }
  
  return children
}

// Layout principal de la aplicación
function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  
  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div 
        className="flex-1 flex flex-col overflow-hidden transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? '256px' : '0' }}
      >
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 pt-8 pb-8 px-6 scrollbar-custom">
          {children}
        </main>
      </div>
    </div>
  )
}

// Componente principal de la aplicación
function AppContent() {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route 
        path="/login" 
        element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
      />
      <Route 
        path="/register" 
        element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />} 
      />
      
      {/* Verificación de email (público) */}
      <Route 
        path="/verify-email" 
        element={<VerifyEmailPage />} 
      />
      <Route 
        path="/forgot-password" 
        element={user ? <Navigate to="/dashboard" replace /> : <ForgotPasswordPage />} 
      />
      
      {/* Ruta de demostración del calendario (sin autenticación) */}
      <Route path="/calendar-demo" element={<CalendarDemoPage />} />
      
      {/* Rutas protegidas */}
      <Route path="/" element={
        <ProtectedRoute>
          <AppLayout>
            <Navigate to="/dashboard" replace />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <AppLayout>
            <DashboardPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/calendar" element={
        <ProtectedRoute>
          <AppLayout>
            <CalendarPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/forecast" element={
        <ProtectedRoute>
          <AppLayout>
            <ForecastPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/employees" element={
        <ProtectedRoute>
          <AppLayout>
            <EmployeesPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/teams" element={
        <ProtectedRoute>
          <AppLayout>
            <TeamsPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/projects" element={
        <ProtectedRoute>
          <AppLayout>
            <ProjectsPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/reports" element={
        <ProtectedRoute>
          <AppLayout>
            <ReportsPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/notifications" element={
        <ProtectedRoute>
          <AppLayout>
            <NotificationsPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/profile" element={
        <ProtectedRoute>
          <AppLayout>
            <ProfilePage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin" element={
        <ProtectedRoute requiredRole="admin">
          <AppLayout>
            <AdminPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/calendars" element={
        <ProtectedRoute requiredRole="admin">
          <AppLayout>
            <AdminCalendarsPage />
          </AppLayout>
        </ProtectedRoute>
      } />
      
      {/* Registro de empleado (sin layout completo) */}
      <Route path="/employee/register" element={
        <ProtectedRoute>
          <EmployeeRegisterPage />
        </ProtectedRoute>
      } />
      
      {/* Ruta 404 */}
      <Route path="*" element={
        <ProtectedRoute>
          <AppLayout>
            <div className="text-center py-12">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
              <p className="text-gray-600 dark:text-gray-400">Página no encontrada</p>
            </div>
          </AppLayout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

// Componente raíz de la aplicación
function App() {
  return (
    <ThemeProvider>
      <Router 
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <AuthProvider>
          <NotificationProvider>
            <AppContent />
            <Toaster position="top-right" richColors />
          </NotificationProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  )
}

export default App
