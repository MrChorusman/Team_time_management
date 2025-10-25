// Configuración de entorno para Vercel
export const config = {
  // URLs de API según el entorno
  API_BASE_URL: import.meta.env.MODE === 'production'
    ? 'https://team-time-management.onrender.com/api'
    : 'http://localhost:5001/api', // Puerto unificado 5001
  
  // Configuración de la aplicación
  APP_NAME: 'Team Time Management',
  APP_VERSION: '1.0.0',
  
  // Configuración de Google OAuth
  GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID || '123456789-abcdefg.apps.googleusercontent.com',
  
  // Configuración de desarrollo
  IS_DEVELOPMENT: import.meta.env.MODE === 'development',
  IS_PRODUCTION: import.meta.env.MODE === 'production'
}

export default config
