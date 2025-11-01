import { useAuth } from '../contexts/AuthContext'

/**
 * Hook para verificar roles del usuario actual
 * 
 * @returns {Object} - Funciones de verificación de roles y permisos
 * 
 * @example
 * const { isAdmin, canManageEmployees } = useRoles()
 * 
 * if (isAdmin()) {
 *   // Renderizar interfaz de admin
 * }
 */
export const useRoles = () => {
  const { user } = useAuth()
  
  /**
   * Verifica si el usuario tiene un rol específico
   * @param {string} roleName - Nombre del rol a verificar
   * @returns {boolean}
   */
  const hasRole = (roleName) => {
    if (!user || !user.roles) return false
    return user.roles.includes(roleName)
  }
  
  /**
   * Verifica si el usuario tiene al menos uno de los roles especificados
   * @param {...string} roleNames - Nombres de los roles a verificar
   * @returns {boolean}
   */
  const hasAnyRole = (...roleNames) => {
    if (!user || !user.roles) return false
    return roleNames.some(role => user.roles.includes(role))
  }
  
  /**
   * Verifica si el usuario tiene todos los roles especificados
   * @param {...string} roleNames - Nombres de los roles a verificar
   * @returns {boolean}
   */
  const hasAllRoles = (...roleNames) => {
    if (!user || !user.roles) return false
    return roleNames.every(role => user.roles.includes(role))
  }
  
  // Roles específicos
  const isAdmin = () => hasRole('admin')
  const isManager = () => hasRole('manager')
  const isEmployee = () => hasRole('employee')
  const isViewer = () => hasRole('viewer')
  
  // Permisos compuestos basados en roles
  const canManageEmployees = () => hasAnyRole('admin', 'manager')
  const canManageTeams = () => isAdmin()
  const canViewReports = () => hasAnyRole('admin', 'manager', 'employee')
  const canManageSettings = () => isAdmin()
  const canApproveEmployees = () => hasAnyRole('admin', 'manager')
  const canEditOwnProfile = () => hasAnyRole('admin', 'manager', 'employee')
  
  return {
    // Verificaciones básicas
    hasRole,
    hasAnyRole,
    hasAllRoles,
    
    // Roles específicos
    isAdmin,
    isManager,
    isEmployee,
    isViewer,
    
    // Permisos compuestos
    canManageEmployees,
    canManageTeams,
    canViewReports,
    canManageSettings,
    canApproveEmployees,
    canEditOwnProfile,
    
    // Datos raw
    roles: user?.roles || [],
    hasUser: !!user
  }
}

export default useRoles

