import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle2, XCircle, Clock, Mail, AlertCircle } from 'lucide-react'
import { Button } from '../../components/ui/button'
import { Alert, AlertDescription } from '../../components/ui/alert'

const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const [status, setStatus] = useState('verifying') // verifying, pending, success, error
  const [token, setToken] = useState('')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')
  const [expired, setExpired] = useState(false)

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    
    if (!tokenParam) {
      setStatus('error')
      setMessage('Token de verificación no encontrado')
      return
    }
    
    setToken(tokenParam)
    // Solo verificar el estado del token (GET), NO verificarlo automáticamente
    checkTokenStatus(tokenParam)
  }, [searchParams])

  const checkTokenStatus = async (token) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/verify-email/${token}`,
        {
          method: 'GET',
          credentials: 'include'
        }
      )
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setEmail(data.email || '')
        
        // Si ya está verificado, mostrar éxito
        if (data.already_verified) {
          setStatus('success')
          setMessage(data.message || 'Este email ya está verificado')
          setTimeout(() => {
            navigate('/login')
          }, 3000)
        } else {
          // Token válido pero requiere confirmación del usuario
          setStatus('pending') // Nuevo estado: pendiente de confirmación
          setMessage(data.message || 'Token válido. Haz clic en el botón para verificar tu email.')
        }
      } else {
        setStatus('error')
        setMessage(data.message || 'Error al verificar el email')
        setExpired(data.expired || false)
      }
    } catch (error) {
      console.error('Error verificando estado del token:', error)
      setStatus('error')
      setMessage('Error de conexión. Inténtalo de nuevo.')
    }
  }

  const verifyEmail = async (token) => {
    try {
      setStatus('verifying') // Cambiar a estado de verificación
      
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/verify-email/${token}`,
        {
          method: 'POST',
          credentials: 'include'
        }
      )
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setStatus('success')
        setMessage(data.message || 'Email verificado exitosamente')
        setEmail(data.email || '')
        
        // Redirigir al login después de 3 segundos
        setTimeout(() => {
          navigate('/login')
        }, 3000)
      } else {
        setStatus('error')
        setMessage(data.message || 'Error al verificar el email')
        setExpired(data.expired || false)
      }
    } catch (error) {
      console.error('Error verificando email:', error)
      setStatus('error')
      setMessage('Error de conexión. Inténtalo de nuevo.')
    }
  }

  const handleResendVerification = async () => {
    if (!email) {
      alert('No se pudo obtener el email. Por favor, solicita un nuevo enlace desde el login.')
      return
    }
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/resend-verification`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email })
        }
      )
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        alert('Email de verificación reenviado. Revisa tu bandeja de entrada.')
      } else {
        alert(data.message || 'Error al reenviar el email')
      }
    } catch (error) {
      console.error('Error reenviando verificación:', error)
      alert('Error de conexión')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        
        {/* Icono y título */}
        <div className="text-center">
          {status === 'verifying' && (
            <>
              <div className="mx-auto h-16 w-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center animate-pulse">
                <Clock className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                Verificando tu email...
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Por favor espera un momento
              </p>
            </>
          )}
          
          {status === 'pending' && (
            <>
              <div className="mx-auto h-16 w-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <Mail className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                Verifica tu email
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Haz clic en el botón para confirmar tu dirección de email
              </p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="mx-auto h-16 w-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                ¡Email verificado!
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Tu cuenta ha sido activada exitosamente
              </p>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="mx-auto h-16 w-16 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                <XCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
              </div>
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                Error de verificación
              </h2>
            </>
          )}
        </div>

        {/* Mensaje */}
        {message && status !== 'verifying' && (
          <Alert className={
            status === 'success' ? 'border-green-200 bg-green-50' : 
            status === 'pending' ? 'border-blue-200 bg-blue-50' :
            'border-red-200 bg-red-50'
          }>
            <AlertCircle className={`h-4 w-4 ${
              status === 'success' ? 'text-green-600' : 
              status === 'pending' ? 'text-blue-600' :
              'text-red-600'
            }`} />
            <AlertDescription className={
              status === 'success' ? 'text-green-800' : 
              status === 'pending' ? 'text-blue-800' :
              'text-red-800'
            }>
              {message}
            </AlertDescription>
          </Alert>
        )}

        {/* Acciones */}
        <div className="space-y-4">
          {status === 'pending' && (
            <div className="text-center">
              <Button
                onClick={() => verifyEmail(token)}
                className="w-full"
                size="lg"
              >
                <CheckCircle2 className="w-5 h-5 mr-2" />
                Confirmar y verificar mi email
              </Button>
              <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                Al hacer clic, confirmarás que esta es tu dirección de email y podrás iniciar sesión.
              </p>
            </div>
          )}
          
          {status === 'success' && (
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Serás redirigido al login en unos segundos...
              </p>
              <Button
                onClick={() => navigate('/login')}
                className="mt-4"
              >
                Ir al login ahora
              </Button>
            </div>
          )}
          
          {status === 'error' && expired && (
            <div className="space-y-4">
              <Alert>
                <Clock className="h-4 w-4" />
                <AlertDescription>
                  El enlace de verificación ha expirado. Puedes solicitar uno nuevo.
                </AlertDescription>
              </Alert>
              
              <Button
                onClick={handleResendVerification}
                className="w-full"
                variant="outline"
              >
                <Mail className="w-4 h-4 mr-2" />
                Reenviar email de verificación
              </Button>
            </div>
          )}
          
          {status === 'error' && !expired && (
            <div className="text-center">
              <Button
                onClick={() => navigate('/login')}
                variant="outline"
              >
                Volver al login
              </Button>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

export default VerifyEmailPage

