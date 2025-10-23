import axios from 'axios'
import config from '../config/environment.js'

// Configuración base del cliente API
const API_BASE_URL = config.API_BASE_URL

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Para mantener cookies de sesión
})

// Interceptor para requests
apiClient.interceptors.request.use(
  (config) => {
    // Agregar token de autenticación si existe
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Log de requests en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }
    
    return config
  },
  (error) => {
    console.error('Error en request:', error)
    return Promise.reject(error)
  }
)

// Interceptor para responses
apiClient.interceptors.response.use(
  (response) => {
    // Log de responses exitosas en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    
    return response
  },
  (error) => {
    // Log de errores
    if (import.meta.env.DEV) {
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data)
    }
    
    // Manejar errores específicos
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token expirado o no válido
          localStorage.removeItem('auth_token')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
          
        case 403:
          // Acceso denegado
          console.warn('Acceso denegado:', data.message)
          break
          
        case 404:
          // Recurso no encontrado
          console.warn('Recurso no encontrado:', data.message)
          break
          
        case 422:
          // Error de validación
          console.warn('Error de validación:', data.message)
          break
          
        case 500:
          // Error interno del servidor
          console.error('Error interno del servidor:', data.message)
          break
          
        default:
          console.error('Error HTTP:', status, data.message)
      }
    } else if (error.request) {
      // Error de red
      console.error('Error de conexión:', error.message)
    } else {
      // Error de configuración
      console.error('Error de configuración:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// Funciones de utilidad para el cliente API
export const apiUtils = {
  // Construir URL con parámetros de consulta
  buildUrl(endpoint, params = {}) {
    const url = new URL(endpoint, API_BASE_URL)
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined) {
        url.searchParams.append(key, params[key])
      }
    })
    return url.toString()
  },

  // Manejar respuesta con paginación
  handlePaginatedResponse(response) {
    return {
      data: response.data,
      pagination: response.pagination || null,
      success: response.success || true
    }
  },

  // Manejar errores de forma consistente
  handleError(error) {
    if (error.response?.data) {
      return {
        success: false,
        message: error.response.data.message || 'Error desconocido',
        errors: error.response.data.errors || [],
        status: error.response.status
      }
    }
    
    return {
      success: false,
      message: error.message || 'Error de conexión',
      errors: [],
      status: null
    }
  },

  // Formatear datos para envío
  formatRequestData(data) {
    // Remover campos vacíos o null
    const cleanData = {}
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
        cleanData[key] = data[key]
      }
    })
    return cleanData
  },

  // Descargar archivo
  async downloadFile(url, filename) {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      
      return { success: true }
    } catch (error) {
      console.error('Error descargando archivo:', error)
      return { success: false, message: 'Error descargando archivo' }
    }
  }
}

export default apiClient
