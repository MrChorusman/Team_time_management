import { config } from '../config/environment'

class GoogleOAuthService {
  constructor() {
    this.clientId = config.GOOGLE_CLIENT_ID
    this.isConfigured = !!this.clientId && this.clientId !== 'your-google-client-id-here'
    this.isMockMode = !this.isConfigured
    this.isProduction = config.IS_PRODUCTION
  }

  /**
   * Inicializa Google OAuth
   */
  async initialize() {
    if (this.isMockMode && !this.isProduction) {
      console.log('🔧 Modo mock activado para Google OAuth (desarrollo)')
      return true
    }
    
    if (this.isMockMode && this.isProduction) {
      console.warn('⚠️ Google OAuth no configurado en producción')
      return false
    }

    if (!this.isConfigured) {
      console.warn('Google OAuth no está configurado')
      return false
    }

    try {
      // Cargar la biblioteca de Google OAuth dinámicamente
      await this.loadGoogleScript()
      return true
    } catch (error) {
      console.error('Error inicializando Google OAuth:', error)
      return false
    }
  }

  /**
   * Carga el script de Google Identity Services
   */
  loadGoogleScript() {
    return new Promise((resolve, reject) => {
      if (window.google && window.google.accounts) {
        resolve()
        return
      }

      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      
      script.onload = () => {
        console.log('✅ Google Identity Services cargado correctamente')
        resolve()
      }
      
      script.onerror = () => {
        reject(new Error('Error cargando Google Identity Services'))
      }
      
      document.head.appendChild(script)
    })
  }

  /**
   * Maneja la respuesta de credenciales de Google
   */
  handleCredentialResponse(response) {
    console.log('🚀 Google OAuth response recibida:', response)
    
    if (response.code) {
      // Flujo de autorización con código
      console.log('📝 Código de autorización recibido')
      this.exchangeCodeForToken(response.code)
    } else if (response.credential) {
      // Flujo de ID token
      console.log('🔑 ID Token recibido')
      this.verifyTokenWithBackend(response.credential)
    } else {
      console.error('❌ Respuesta de Google inválida:', response)
      window.dispatchEvent(new CustomEvent('googleLoginError', {
        detail: { message: 'Respuesta de Google inválida' }
      }))
    }
  }
  
  /**
   * Intercambia código de autorización por token
   */
  async exchangeCodeForToken(code) {
    try {
      console.log('🔄 Intercambiando código por token...')
      
      const response = await fetch(`${config.API_BASE_URL}/auth/google/exchange`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          redirect_uri: window.location.origin
        })
      })

      const result = await response.json()
      
      if (result.success) {
        console.log('✅ Token intercambiado exitosamente')
        window.dispatchEvent(new CustomEvent('googleLoginSuccess', {
          detail: result
        }))
      } else {
        console.error('❌ Error intercambiando token:', result)
        window.dispatchEvent(new CustomEvent('googleLoginError', {
          detail: result
        }))
      }
    } catch (error) {
      console.error('❌ Error intercambiando código:', error)
      window.dispatchEvent(new CustomEvent('googleLoginError', {
        detail: { message: 'Error de conexión' }
      }))
    }
  }

  /**
   * Verifica el token con el backend
   */
  async verifyTokenWithBackend(credential) {
    try {
      const response = await fetch(`${config.API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: credential
        })
      })

      const result = await response.json()
      
      if (result.success) {
        // Emitir evento personalizado para notificar el login exitoso
        window.dispatchEvent(new CustomEvent('googleLoginSuccess', {
          detail: result
        }))
      } else {
        // Emitir evento de error
        window.dispatchEvent(new CustomEvent('googleLoginError', {
          detail: result
        }))
      }
    } catch (error) {
      console.error('Error verificando token con backend:', error)
      window.dispatchEvent(new CustomEvent('googleLoginError', {
        detail: { message: 'Error de conexión' }
      }))
    }
  }

  /**
   * Simula login con Google para modo mock
   */
  async mockGoogleLogin() {
    console.log('🔧 Ejecutando login mock de Google')
    
    // Simular datos de usuario de Google
    const mockUserData = {
      success: true,
      message: "Inicio de sesión con Google exitoso (modo demo)",
      user: {
        id: 999,
        email: "demo@google.com",
        first_name: "Demo",
        last_name: "Usuario",
        active: true,
        confirmed_at: new Date().toISOString(),
        google_id: "mock_google_id_123",
        picture: "https://via.placeholder.com/150/4285F4/FFFFFF?text=G"
      },
      roles: ["viewer"],
      redirectUrl: "/dashboard",
      environment: "development"
    }

    // Simular delay de red
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Emitir evento de éxito
    window.dispatchEvent(new CustomEvent('googleLoginSuccess', {
      detail: mockUserData
    }))

    return { success: true }
  }

  /**
   * Renderiza el botón de Google
   */
  renderButton(elementId) {
    if (this.isMockMode) {
      console.log('🔧 Modo mock: No se renderiza botón real de Google')
      return
    }

    if (!this.isConfigured) {
      console.warn('Google OAuth no está configurado')
      return
    }

    try {
      window.google.accounts.id.renderButton(
        document.getElementById(elementId),
        {
          theme: 'outline',
          size: 'large',
          width: '100%',
          text: 'signin_with',
          shape: 'rectangular',
          logo_alignment: 'left'
        }
      )
    } catch (error) {
      console.error('Error renderizando botón de Google:', error)
    }
  }

  /**
   * Inicia el proceso de login con Google
   */
  async login() {
    if (this.isMockMode && !this.isProduction) {
      console.log('🔧 Iniciando login mock de Google (desarrollo)')
      return await this.mockGoogleLogin()
    }
    
    if (this.isMockMode && this.isProduction) {
      throw new Error('Google OAuth no está configurado en producción')
    }

    if (!this.isConfigured) {
      throw new Error('Google OAuth no está configurado')
    }

    try {
      await this.initialize()
      
      // Usar Google Identity Services para mostrar ventana de selección
      if (window.google && window.google.accounts) {
        console.log('🚀 Iniciando Google OAuth real con ventana de selección')
        
        // Configurar el flujo de autorización
        window.google.accounts.oauth2.initCodeClient({
          client_id: this.clientId,
          scope: 'openid email profile',
          ux_mode: 'popup',
          callback: this.handleCredentialResponse.bind(this)
        }).requestCode()
        
      } else {
        throw new Error('Google Identity Services no está disponible')
      }
      
    } catch (error) {
      console.error('Error iniciando login con Google:', error)
      throw error
    }
  }

  /**
   * Verifica si está en modo mock (solo en desarrollo)
   */
  isMockModeEnabled() {
    return this.isMockMode && !this.isProduction
  }
  
  /**
   * Verifica si Google OAuth está disponible
   */
  isGoogleOAuthAvailable() {
    return this.isConfigured || (this.isMockMode && !this.isProduction)
  }
}

export default new GoogleOAuthService()