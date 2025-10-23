// Configuración de entorno para Vercel
export const config = {
  // URLs de API según el entorno
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://team-time-management.onrender.com/api'
    : 'http://localhost:5001/api',
  
  // Configuración de la aplicación
  APP_NAME: 'Team Time Management',
  APP_VERSION: '1.0.0',
  
  // Configuración de Google OAuth
  GOOGLE_CLIENT_ID: process.env.VITE_GOOGLE_CLIENT_ID || '',
  
  // Configuración de desarrollo
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  IS_PRODUCTION: process.env.NODE_ENV === 'production'
}

export default config
