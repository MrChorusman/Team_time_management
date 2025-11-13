import axios from 'axios'
import config from '../config/environment.js'

// Configuración base del cliente API
const API_BASE_URL = config.API_BASE_URL

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Aumentado a 60 segundos para redes móviles/5G con mayor latencia
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

// Interceptor para responses con retry logic para redes móviles
apiClient.interceptors.response.use(
  (response) => {
    // Log de responses exitosas en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Log de errores
    if (import.meta.env.DEV) {
      console.error(`❌ ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, error.response?.data)
    }
    
    // Retry logic para errores de red (timeout, conexión perdida, etc.)
    // Solo para errores de red, no para errores HTTP (4xx, 5xx)
    if (!error.response && originalRequest && !originalRequest.__retryCount) {
      originalRequest.__retryCount = 0
    }
    
    // Reintentar hasta 3 veces para errores de red
    if (!error.response && originalRequest && originalRequest.__retryCount < 3) {
      originalRequest.__retryCount += 1
      
      // Backoff exponencial: 1s, 2s, 4s
      const delay = Math.pow(2, originalRequest.__retryCount - 1) * 1000
      
      if (import.meta.env.DEV) {
        console.log(`🔄 Reintentando request (intento ${originalRequest.__retryCount}/3) después de ${delay}ms...`)
      }
      
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return apiClient(originalRequest)
    }
    
    // Manejar errores específicos
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Sesión expirada o no válida
          // Evitar loop infinito: NO procesar 401 del endpoint /auth/me
          if (!originalRequest.url.includes('/auth/me') && !originalRequest.url.includes('/auth/login')) {
            console.error('❌ Sesión expirada o inválida')
            
            // Limpiar estado de autenticación
            localStorage.removeItem('user')
            localStorage.removeItem('employee')
            localStorage.removeItem('auth_token')
            
            // Emitir evento personalizado para que AuthContext reaccione
            window.dispatchEvent(new CustomEvent('session-expired'))
            
            // Redirigir a login
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login?reason=session_expired'
            }
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
