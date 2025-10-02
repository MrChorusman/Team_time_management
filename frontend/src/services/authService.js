import { apiClient } from './apiClient'

export const authService = {
  // Iniciar sesión
  async login(email, password) {
    const response = await apiClient.post('/auth/login', {
      email,
      password
    })
    return response.data
  },

  // Registrar nuevo usuario
  async register(userData) {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  },

  // Cerrar sesión
  async logout() {
    const response = await apiClient.post('/auth/logout')
    return response.data
  },

  // Verificar sesión actual
  async checkSession() {
    const response = await apiClient.get('/auth/check-session')
    return response.data
  },

  // Obtener usuario actual
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // Cambiar contraseña
  async changePassword(currentPassword, newPassword) {
    const response = await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
    return response.data
  },

  // Obtener roles disponibles (solo admins)
  async getRoles() {
    const response = await apiClient.get('/auth/roles')
    return response.data
  }
}
