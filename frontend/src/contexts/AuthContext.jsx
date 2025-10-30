import { createContext, useContext, useState, useEffect, useRef } from 'react'
import { authService } from '../services/authService'
import googleOAuthService from '../services/googleOAuthService'

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
  const [hasLoggedIn, setHasLoggedIn] = useState(false) // Flag para evitar verificar sesión después del login
  const hasInitialized = useRef(false) // Flag para evitar múltiples inicializaciones

  // Verificar sesión al cargar la aplicación
  useEffect(() => {
    // Evitar múltiples inicializaciones
    if (hasInitialized.current) {
      return
    }
    
    hasInitialized.current = true
    
    // Solo verificar sesión si no tenemos usuario logueado y no hemos hecho login recientemente
    // Esto evita que se resetee el estado después de un login exitoso
    if (!user && !hasLoggedIn) {
      checkSession()
    } else if (hasLoggedIn) {
      // Si hemos hecho login, no verificar sesión y marcar loading como false
      setLoading(false)
    }
    
    // Configurar listeners para Google OAuth
    const handleGoogleLoginSuccess = (event) => {
      const { user, redirectUrl } = event.detail
      setUser(user)
      setEmployee(null) // Los usuarios de Google no tienen employee por defecto
      setError(null)
      setLoading(false)
      
      // La redirección se manejará en el componente LoginPage
      // No redirigir aquí para evitar problemas con React Router
    }
    
    const handleGoogleLoginError = (event) => {
      setError(event.detail.message || 'Error en login con Google')
      setLoading(false)
    }
    
    window.addEventListener('googleLoginSuccess', handleGoogleLoginSuccess)
    window.addEventListener('googleLoginError', handleGoogleLoginError)
    
    return () => {
      window.removeEventListener('googleLoginSuccess', handleGoogleLoginSuccess)
      window.removeEventListener('googleLoginError', handleGoogleLoginError)
    }
  }, [])

  const checkSession = async () => {
    try {
      setLoading(true)
      
      // SIEMPRE verificar con el backend, incluso si hay localStorage
      // Esto evita usar sesiones expiradas del localStorage
      try {
        const response = await authService.checkSession()
        
        // El endpoint /auth/me devuelve { success: true, user: {...}, employee: {...} }
        if (response.success && response.user) {
          setUser(response.user)
          setEmployee(response.employee || null)
          // Guardar en localStorage
          localStorage.setItem('user', JSON.stringify(response.user))
          if (response.employee) {
            localStorage.setItem('employee', JSON.stringify(response.employee))
          }
        } else {
          // No hay sesión válida, limpiar localStorage
          setUser(null)
          setEmployee(null)
          localStorage.removeItem('user')
          localStorage.removeItem('employee')
        }
      } catch (error) {
        // Si el backend falla (401, 404, etc), limpiar localStorage
        console.error('Error verificando sesión:', error)
        setUser(null)
        setEmployee(null)
        localStorage.removeItem('user')
        localStorage.removeItem('employee')
      }
    } catch (error) {
      console.error('Error general en checkSession:', error)
      setUser(null)
      setEmployee(null)
      localStorage.removeItem('user')
      localStorage.removeItem('employee')
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
        setHasLoggedIn(true) // Marcar que hemos hecho login exitoso
        
        // Guardar en localStorage para persistir la sesión
        localStorage.setItem('user', JSON.stringify(response.user))
        if (response.employee) {
          localStorage.setItem('employee', JSON.stringify(response.employee))
        }
        
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

  const loginWithGoogle = async () => {
    try {
      setLoading(true)
      setError(null)
      
      await googleOAuthService.login()
      
      // El resultado se manejará a través de los event listeners
      return { success: true }
    } catch (error) {
      const errorMessage = error.message || 'Error iniciando login con Google'
      setError(errorMessage)
      setLoading(false)
      return { success: false, message: errorMessage }
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
      setHasLoggedIn(false) // Resetear flag de login
      setLoading(false)
      
      // Limpiar localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('employee')
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
    loginWithGoogle,
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
