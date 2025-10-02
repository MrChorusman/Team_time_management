import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [employee, setEmployee] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Verificar sesión al cargar la aplicación
  useEffect(() => {
    checkSession()
  }, [])

  const checkSession = async () => {
    try {
      setLoading(true)
      const response = await authService.checkSession()
      
      if (response.authenticated) {
        setUser(response.user)
        setEmployee(response.employee)
      } else {
        setUser(null)
        setEmployee(null)
      }
    } catch (error) {
      console.error('Error verificando sesión:', error)
      setUser(null)
      setEmployee(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await authService.login(email, password)
      
      if (response.success) {
        setUser(response.user)
        setEmployee(response.employee)
        return { success: true, redirectUrl: response.redirect_url }
      } else {
        setError(response.message)
        return { success: false, message: response.message }
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error de conexión'
      setError(errorMessage)
      return { success: false, message: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await authService.register(userData)
      
      if (response.success) {
        return { success: true, message: response.message }
      } else {
        setError(response.message)
        return { success: false, message: response.message }
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Error de conexión'
      setError(errorMessage)
      return { success: false, message: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      setLoading(true)
      await authService.logout()
    } catch (error) {
      console.error('Error cerrando sesión:', error)
    } finally {
      setUser(null)
      setEmployee(null)
      setLoading(false)
    }
  }

  const updateEmployee = (employeeData) => {
    setEmployee(employeeData)
  }

  const refreshUserData = async () => {
    try {
      const response = await authService.getCurrentUser()
      if (response.success) {
        setUser(response.user)
        setEmployee(response.employee)
      }
    } catch (error) {
      console.error('Error actualizando datos del usuario:', error)
    }
  }

  // Funciones de utilidad para verificar roles
  const hasRole = (roleName) => {
    return user?.roles?.some(role => role.name === roleName) || false
  }

  const isAdmin = () => hasRole('admin')
  const isManager = () => hasRole('manager')
  const isEmployee = () => hasRole('employee')
  const isViewer = () => hasRole('viewer')

  const canManageEmployees = () => isAdmin() || isManager()
  const canManageTeams = () => isAdmin()
  const canViewReports = () => isAdmin() || isManager() || isEmployee()

  const value = {
    // Estado
    user,
    employee,
    loading,
    error,
    
    // Acciones
    login,
    register,
    logout,
    updateEmployee,
    refreshUserData,
    checkSession,
    
    // Utilidades de roles
    hasRole,
    isAdmin,
    isManager,
    isEmployee,
    isViewer,
    canManageEmployees,
    canManageTeams,
    canViewReports,
    
    // Limpiar error
    clearError: () => setError(null)
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
