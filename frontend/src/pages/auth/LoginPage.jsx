import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, LogIn, Mail, Lock } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Alert, AlertDescription } from '../../components/ui/alert'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import googleOAuthService from '../../services/googleOAuthService'
import loginImage from '../../assets/images/imagen-login-page.png'

const LoginPage = () => {
  const navigate = useNavigate()
  const { login, loginWithGoogle, loading, error, clearError } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [googleConfigured, setGoogleConfigured] = useState(false)
  const [isMockMode, setIsMockMode] = useState(false)
  const [googleLoginSuccess, setGoogleLoginSuccess] = useState(false)
  
  // Inicializar Google OAuth
  useEffect(() => {
    const initGoogle = async () => {
      try {
        const configured = await googleOAuthService.initialize()
        setGoogleConfigured(configured)
        setIsMockMode(googleOAuthService.isMockModeEnabled())
      } catch (error) {
        console.error('Error inicializando Google OAuth:', error)
        setGoogleConfigured(false)
        setIsMockMode(false)
      }
    }
    
    initGoogle()
  }, [])

  // Manejar redirección después del login con Google
  useEffect(() => {
    const handleGoogleLoginSuccess = (event) => {
      const { redirectUrl } = event.detail
      setGoogleLoginSuccess(true)
      
        // Redirigir usando window.location para forzar navegación completa
        setTimeout(() => {
          const finalRedirectUrl = redirectUrl || '/dashboard'
          window.location.href = finalRedirectUrl
        }, 1000)
    }
    
    window.addEventListener('googleLoginSuccess', handleGoogleLoginSuccess)
    
    return () => {
      window.removeEventListener('googleLoginSuccess', handleGoogleLoginSuccess)
    }
  }, [navigate])
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm({
    mode: 'onChange',
    defaultValues: {
      email: '',
      password: ''
    }
  })

  const onSubmit = async (data) => {
    clearError()
    
    try {
      const result = await login(data.email, data.password)
      
      if (result.success) {
        // Redirigir usando window.location para forzar navegación completa
        // Esto evita que el AuthContext interfiera con la redirección
        const redirectUrl = result.redirectUrl || '/dashboard'
        window.location.href = redirectUrl
      }
    } catch (error) {
      console.error('Error en login:', error)
    }
  }

  const handleGoogleLogin = async () => {
    clearError()
    
    try {
      const result = await loginWithGoogle()
      
      if (result.success) {
        // El resultado se manejará a través de los event listeners en AuthContext
        // y la redirección se hará automáticamente
      }
    } catch (error) {
      console.error('Error en login con Google:', error)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo - Formulario (35%) */}
      <div className="w-[35%] bg-white dark:bg-gray-900 flex flex-col justify-start px-8 py-12" style={{ paddingTop: '8%' }}>
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TTM</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Team Time Management</h1>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Iniciar Sesión</h2>
              <p className="text-gray-700 dark:text-gray-300">Accede a tu cuenta</p>
        </div>

        {/* Formulario */}
        <Card className="border-0 shadow-none bg-transparent">
          <CardContent className="px-0">
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Error general */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Mensaje de éxito de Google */}
              {googleLoginSuccess && (
                <Alert className="border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-900 dark:text-green-200">
                  <AlertDescription>
                    ✅ ¡Login con Google exitoso! Redirigiendo...
                  </AlertDescription>
                </Alert>
              )}

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">Correo Electrónico</Label>
                <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="tu@email.com"
                    className="pl-10"
                    {...register('email', {
                      required: 'El correo electrónico es requerido',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Correo electrónico inválido'
                      }
                    })}
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Contraseña */}
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Tu contraseña"
                    className="pl-10 pr-10"
                    {...register('password', {
                      required: 'La contraseña es requerida',
                      minLength: {
                        value: 6,
                        message: 'La contraseña debe tener al menos 6 caracteres'
                      }
                    })}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errors.password.message}
                  </p>
                )}
              </div>

              {/* Recordar sesión y recuperar contraseña */}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                    Recordar sesión
                  </label>
                </div>

                    <div className="text-base">
                      <Link
                        to="/forgot-password"
                        className="font-medium text-blue-700 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors duration-200"
                      >
                        ¿Olvidaste tu contraseña?
                      </Link>
                    </div>
              </div>

              {/* Botón de envío */}
              <Button
                type="submit"
                className="w-full transition-all duration-200 ease-in-out hover:shadow-lg hover:scale-[1.02] mb-6"
                disabled={isSubmitting || loading}
              >
                {isSubmitting || loading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <LogIn className="w-4 h-4 mr-2" />
                )}
                {isSubmitting || loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </Button>

              {/* Separador */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white dark:bg-gray-900 px-2 text-gray-500 dark:text-gray-400">
                    O continúa con
                  </span>
                </div>
              </div>

              {/* Botón de Google */}
              {googleConfigured ? (
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full transition-all duration-200 ease-in-out hover:shadow-md hover:border-blue-300 hover:bg-blue-50"
                      onClick={handleGoogleLogin}
                      disabled={loading}
                    >
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  {isMockMode ? 'Continuar con Google (Demo)' : 'Continuar con Google'}
                </Button>
              ) : (
                <div className="text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Google OAuth no configurado
                  </p>
                </div>
              )}

              {/* Enlace a registro */}
                  <div className="text-center">
                    <p className="text-base text-gray-700 dark:text-gray-300">
                      ¿No tienes una cuenta?{' '}
                      <Link
                        to="/register"
                        className="font-medium text-blue-700 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors duration-200"
                      >
                        Regístrate aquí
                      </Link>
                    </p>
                  </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
            <div className="mt-8 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                © 2024 Team Time Management. Todos los derechos reservados.
              </p>
            </div>
      </div>

      {/* Panel derecho - Imagen (65%) */}
      <div className="w-[65%] relative overflow-hidden">
        <img
          src={loginImage}
          alt="Team Time Management - Gestión de tiempo, equipos y finanzas"
          className="w-full h-full object-cover"
          style={{ objectPosition: 'center 6%' }} 
        />
      </div>
    </div>
  )
}

export default LoginPage
