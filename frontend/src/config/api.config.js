/**
 * Configuración unificada de API para el frontend
 * Centraliza todas las configuraciones de API y entornos
 */

// Configuración base
const BASE_CONFIG = {
  // URLs de API por entorno
  apiUrls: {
    development: 'http://localhost:5001/api',
    production: 'https://team-time-management.onrender.com/api'
  },
  
  // Configuración de timeout
  timeout: {
    development: 10000,  // 10 segundos en desarrollo
    production: 30000   // 30 segundos en producción
  },
  
  // Configuración de reintentos
  retry: {
    maxAttempts: 3,
    delay: 1000,  // 1 segundo entre reintentos
    backoffMultiplier: 2
  },
  
  // Headers por defecto
  defaultHeaders: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  
  // Configuración de autenticación
  auth: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    tokenExpiryKey: 'token_expiry'
  },
  
  // Endpoints principales
  endpoints: {
    auth: {
      login: '/auth/login',
      logout: '/auth/logout',
      refresh: '/auth/refresh',
      google: '/auth/google',
      callback: '/auth/callback'
    },
    employees: {
      list: '/employees',
      create: '/employees',
      update: '/employees',
      delete: '/employees'
    },
    teams: {
      list: '/teams',
      create: '/teams',
      update: '/teams',
      delete: '/teams'
    },
    calendar: {
      activities: '/calendar/activities',
      holidays: '/calendar/holidays'
    },
    reports: {
      hours: '/reports/hours',
      teams: '/reports/teams',
      employees: '/reports/employees'
    }
  }
};

/**
 * Obtiene la configuración actual basada en el entorno
 */
function getCurrentConfig() {
  const environment = import.meta.env.MODE || 'development';
  
  return {
    environment,
    apiUrl: BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development,
    timeout: BASE_CONFIG.timeout[environment] || BASE_CONFIG.timeout.development,
    retry: BASE_CONFIG.retry,
    defaultHeaders: BASE_CONFIG.defaultHeaders,
    auth: BASE_CONFIG.auth,
    endpoints: BASE_CONFIG.endpoints,
    
    // Configuración específica del entorno
    isDevelopment: environment === 'development',
    isProduction: environment === 'production',
    
    // URLs completas para endpoints comunes
    urls: {
      login: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.auth.login}`,
      logout: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.auth.logout}`,
      googleAuth: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.auth.google}`,
      employees: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.employees.list}`,
      teams: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.teams.list}`,
      calendar: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.calendar.activities}`,
      reports: `${BASE_CONFIG.apiUrls[environment] || BASE_CONFIG.apiUrls.development}${BASE_CONFIG.endpoints.reports.hours}`
    }
  };
}

/**
 * Construye una URL completa para un endpoint
 */
function buildApiUrl(endpoint) {
  const config = getCurrentConfig();
  return `${config.apiUrl}${endpoint}`;
}

/**
 * Obtiene headers con autenticación si está disponible
 */
function getAuthHeaders() {
  const config = getCurrentConfig();
  const token = localStorage.getItem(config.auth.tokenKey);
  
  const headers = { ...config.defaultHeaders };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * Configuración de fetch con reintentos automáticos
 */
async function fetchWithRetry(url, options = {}, attempt = 1) {
  const config = getCurrentConfig();
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...config.defaultHeaders,
        ...options.headers
      },
      signal: AbortSignal.timeout(config.timeout)
    });
    
    // Si la respuesta es exitosa, la devolvemos
    if (response.ok) {
      return response;
    }
    
    // Si es un error del servidor y no hemos alcanzado el máximo de reintentos
    if (response.status >= 500 && attempt < config.retry.maxAttempts) {
      const delay = config.retry.delay * Math.pow(config.retry.backoffMultiplier, attempt - 1);
      
      console.warn(`Intento ${attempt} fallido para ${url}. Reintentando en ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, attempt + 1);
    }
    
    // Si no podemos reintentar, devolvemos la respuesta
    return response;
    
  } catch (error) {
    // Si es un error de red y no hemos alcanzado el máximo de reintentos
    if (attempt < config.retry.maxAttempts) {
      const delay = config.retry.delay * Math.pow(config.retry.backoffMultiplier, attempt - 1);
      
      console.warn(`Error de red en intento ${attempt} para ${url}. Reintentando en ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, attempt + 1);
    }
    
    throw error;
  }
}

/**
 * Cliente API simplificado
 */
class ApiClient {
  constructor() {
    this.config = getCurrentConfig();
  }
  
  /**
   * Realiza una petición GET
   */
  async get(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = getAuthHeaders();
    
    return fetchWithRetry(url, {
      method: 'GET',
      headers: { ...headers, ...options.headers },
      ...options
    });
  }
  
  /**
   * Realiza una petición POST
   */
  async post(endpoint, data, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = getAuthHeaders();
    
    return fetchWithRetry(url, {
      method: 'POST',
      headers: { ...headers, ...options.headers },
      body: JSON.stringify(data),
      ...options
    });
  }
  
  /**
   * Realiza una petición PUT
   */
  async put(endpoint, data, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = getAuthHeaders();
    
    return fetchWithRetry(url, {
      method: 'PUT',
      headers: { ...headers, ...options.headers },
      body: JSON.stringify(data),
      ...options
    });
  }
  
  /**
   * Realiza una petición DELETE
   */
  async delete(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = getAuthHeaders();
    
    return fetchWithRetry(url, {
      method: 'DELETE',
      headers: { ...headers, ...options.headers },
      ...options
    });
  }
  
  /**
   * Maneja respuestas JSON con manejo de errores
   */
  async handleJsonResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// Instancia singleton del cliente API
const apiClient = new ApiClient();

// Exportar configuración y cliente
export {
  getCurrentConfig,
  buildApiUrl,
  getAuthHeaders,
  fetchWithRetry,
  ApiClient,
  apiClient
};

// Exportar configuración por defecto
export default getCurrentConfig();
