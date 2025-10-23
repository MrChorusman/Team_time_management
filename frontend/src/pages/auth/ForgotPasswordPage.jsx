import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Mail, ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Alert, AlertDescription } from '../../components/ui/alert'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import { authService } from '../../services/authService'

const ForgotPasswordPage = () => {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm()

  const onSubmit = async (data) => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await authService.forgotPassword(data.email)
      
      if (result.success) {
        setSuccess(true)
      } else {
        setError(result.message || 'Error al enviar el email de recuperación')
      }
    } catch (error) {
      console.error('Error en forgot password:', error)
      setError('Error al enviar el email de recuperación')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl text-center">Email Enviado</CardTitle>
              <CardDescription className="text-center">
                Revisa tu bandeja de entrada
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center space-y-4">
                <div className="mx-auto h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Mail className="h-6 w-6 text-green-600" />
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Te hemos enviado un enlace para restablecer tu contraseña. 
                  Revisa tu bandeja de entrada y sigue las instrucciones.
                </p>
                <Link to="/login">
                  <Button variant="outline" className="w-full">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Volver al Login
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">TTM</span>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Recuperar Contraseña
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Ingresa tu email para recibir un enlace de recuperación
          </p>
        </div>

        {/* Formulario */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">¿Olvidaste tu contraseña?</CardTitle>
            <CardDescription className="text-center">
              No te preocupes, te ayudaremos a recuperarla
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Error general */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">Correo Electrónico</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
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

              {/* Botón de envío */}
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting || loading}
              >
                {isSubmitting || loading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <Mail className="w-4 h-4 mr-2" />
                )}
                {isSubmitting || loading ? 'Enviando...' : 'Enviar Enlace'}
              </Button>

              {/* Enlace de vuelta */}
              <div className="text-center">
                <Link
                  to="/login"
                  className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <ArrowLeft className="w-4 h-4 inline mr-1" />
                  Volver al Login
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default ForgotPasswordPage
