import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, UserPlus, Mail, Lock, User } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Alert, AlertDescription } from '../../components/ui/alert'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

const RegisterPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, register: registerUser, loading, error, clearError } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [registrationSuccess, setRegistrationSuccess] = useState(() => {
    // Leer del localStorage al inicializar
    return localStorage.getItem('registrationSuccess') === 'true'
  })
  const [invitationToken, setInvitationToken] = useState(null)
  const [registrationDetails, setRegistrationDetails] = useState({
    hasInvitation: false,
    requiresVerification: null
  })
  const registrationSuccessRef = useRef(false)
  
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting }
  } = useForm({
    mode: 'onChange'
  })

  const password = watch('password')

  // Detectar token de invitación en la URL
  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      setInvitationToken(token)
      setRegistrationDetails((prev) => ({
        ...prev,
        hasInvitation: true
      }))
    }
  }, [searchParams])

  // Limpiar localStorage cuando el componente se desmonte o cuando se navegue
  useEffect(() => {
    return () => {
      // No limpiar aquí - queremos que persista hasta que el usuario navegue
    }
  }, [])

  // Limpiar localStorage cuando se navegue a login
  useEffect(() => {
    const handleBeforeUnload = () => {
      // No limpiar en beforeunload - queremos que persista
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [])

  const onSubmit = async (data, e) => {
    e?.preventDefault() // Prevenir comportamiento por defecto del formulario
    clearError()
    
    try {
      const registerData = {
        email: data.email,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName
      }
      
      // Si hay token de invitación, incluirlo en el registro
      if (invitationToken) {
        registerData.invitation_token = invitationToken
      }
      
      const result = await registerUser(registerData)
      console.log('Resultado del registro:', result)
      
      if (result && result.success) {
        console.log('Registro exitoso, estableciendo estado de éxito')
        // NO resetear el formulario - queremos mantener el estado
        // Establecer el estado ANTES de cualquier otra operación
        registrationSuccessRef.current = true
        localStorage.setItem('registrationSuccess', 'true')
        setRegistrationSuccess(true)
        console.log('Estado registrationSuccess establecido a true')
        
        const backendHasInvitation = Boolean(result?.has_invitation)
        const backendRequiresVerification = result?.requires_verification ?? null
        const backendInvitationToken = result?.invitation_token || null
        const effectiveInvitationToken = invitationToken || backendInvitationToken || null
        const finalHasInvitation = backendHasInvitation || Boolean(effectiveInvitationToken)
        
        if (!invitationToken && backendInvitationToken) {
          setInvitationToken(backendInvitationToken)
        }
        
        setRegistrationDetails({
          hasInvitation: finalHasInvitation,
          requiresVerification: backendRequiresVerification
        })
        
        // Si hay invitación, redirigir a completar perfil de empleado después de mostrar mensaje
        // Si NO hay invitación, NO redirigir automáticamente - dejar que el usuario vea el mensaje
        if (finalHasInvitation && effectiveInvitationToken) {
          setTimeout(() => {
            navigate(`/employee/register?token=${effectiveInvitationToken}`)
          }, 3000)
        }
        // Si no hay invitación, el usuario debe ver el mensaje y hacer clic en "Ir a Login"
        // NO llamar a reset() aquí - queremos mantener el estado de éxito
      } else {
        // Si result.success es false, el error ya fue manejado por AuthContext
        console.error('Error en registro:', result?.message || 'Error desconocido', result)
      }
    } catch (error) {
      console.error('Error capturado en registro:', error)
      console.error('Error details:', error.response?.data || error.message)
      // El error ya fue manejado por AuthContext, pero podemos mostrar un mensaje adicional si es necesario
    }
  }

  if (registrationSuccess || registrationSuccessRef.current) {
    return (
      <div className="flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8" style={{ minHeight: 'calc(100vh - 2rem)' }}>
        <div className="max-w-md w-full">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="mx-auto h-12 w-12 bg-green-600 rounded-full flex items-center justify-center mb-4">
                  <UserPlus className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  ¡Registro Exitoso!
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {registrationDetails.hasInvitation || invitationToken ? (
                    'Tu cuenta ha sido creada exitosamente. Tu email ha sido confirmado automáticamente. Ahora completa tu perfil de empleado.'
                  ) : registrationDetails.requiresVerification === false ? (
                    'Tu cuenta ha sido creada exitosamente y ya está activa. Puedes iniciar sesión con tus credenciales.'
                  ) : (
                    <>
                      Tu cuenta ha sido creada exitosamente.{' '}
                      <strong>Por favor, verifica tu email</strong> para activar tu cuenta antes de iniciar sesión.
                    </>
                  )}
                </p>
                {!(registrationDetails.hasInvitation || invitationToken) && registrationDetails.requiresVerification !== false && (
                  <>
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4">
                      <p className="text-sm text-blue-800 dark:text-blue-200">
                        📧 Revisa tu bandeja de entrada y busca el email de verificación. 
                        Si no lo encuentras, revisa la carpeta de spam.
                      </p>
                    </div>
                    <Button 
                      onClick={() => {
                        localStorage.removeItem('registrationSuccess')
                        navigate('/login')
                      }} 
                      className="w-full mt-4"
                    >
                      Ir a Iniciar Sesión
                    </Button>
                  </>
                )}
                {(registrationDetails.hasInvitation || invitationToken) && <LoadingSpinner size="sm" />}
                {!(registrationDetails.hasInvitation || invitationToken) && registrationDetails.requiresVerification === false && (
                  <Button 
                    onClick={() => {
                      localStorage.removeItem('registrationSuccess')
                      navigate('/login')
                    }} 
                    className="w-full mt-4"
                  >
                    Ir a Iniciar Sesión
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8" style={{ minHeight: 'calc(100vh - 2rem)' }}>
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">TTM</span>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Crear Cuenta
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Únete a Team Time Management
          </p>
          {user && (
            <div className="mt-4">
              <Alert variant="destructive">
                <AlertDescription>
                  Ya has iniciado sesión como <strong>{user.email}</strong>. 
                  Si estás aceptando una invitación para otro usuario, cierra sesión antes de continuar para evitar conflictos.
                </AlertDescription>
              </Alert>
            </div>
          )}
        </div>

        {/* Formulario */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">
              {invitationToken ? 'Aceptar Invitación' : 'Registro'}
            </CardTitle>
            <CardDescription className="text-center">
              {invitationToken 
                ? 'Has sido invitado a unirte al equipo. Completa tu registro para continuar.'
                : 'Completa los datos para crear tu cuenta'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Mensaje informativo si hay token de invitación */}
              {invitationToken && (
                <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                  <AlertDescription className="text-blue-800 dark:text-blue-200">
                    📧 Estás aceptando una invitación. Tu email será verificado automáticamente al completar el registro.
                  </AlertDescription>
                </Alert>
              )}
              
              {/* Error general */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Nombre */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">Nombre</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="firstName"
                      type="text"
                      placeholder="Juan"
                      className="pl-10"
                      {...register('firstName', {
                        required: 'El nombre es requerido',
                        minLength: {
                          value: 2,
                          message: 'El nombre debe tener al menos 2 caracteres'
                        }
                      })}
                    />
                  </div>
                  {errors.firstName && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.firstName.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName">Apellido</Label>
                  <Input
                    id="lastName"
                    type="text"
                    placeholder="Pérez"
                    {...register('lastName', {
                      required: 'El apellido es requerido',
                      minLength: {
                        value: 2,
                        message: 'El apellido debe tener al menos 2 caracteres'
                      }
                    })}
                  />
                  {errors.lastName && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.lastName.message}
                    </p>
                  )}
                </div>
              </div>

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

              {/* Contraseña */}
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Mínimo 6 caracteres"
                    className="pl-10 pr-10"
                    {...register('password', {
                      required: 'La contraseña es requerida',
                      minLength: {
                        value: 6,
                        message: 'La contraseña debe tener al menos 6 caracteres'
                      },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                        message: 'La contraseña debe contener al menos una mayúscula, una minúscula y un número'
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

              {/* Confirmar contraseña */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirmar Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Repite tu contraseña"
                    className="pl-10 pr-10"
                    {...register('confirmPassword', {
                      required: 'Debes confirmar tu contraseña',
                      validate: value =>
                        value === password || 'Las contraseñas no coinciden'
                    })}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errors.confirmPassword.message}
                  </p>
                )}
              </div>

              {/* Términos y condiciones */}
              <div className="flex items-center">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  {...register('terms', {
                    required: 'Debes aceptar los términos y condiciones'
                  })}
                />
                <label htmlFor="terms" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                  Acepto los{' '}
                  <Link
                    to="/terms"
                    className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    términos y condiciones
                  </Link>
                </label>
              </div>
              {errors.terms && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {errors.terms.message}
                </p>
              )}

              {/* Botón de envío */}
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting || loading}
              >
                {isSubmitting || loading ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <UserPlus className="w-4 h-4 mr-2" />
                )}
                {isSubmitting || loading ? 'Creando cuenta...' : 'Crear Cuenta'}
              </Button>

              {/* Enlace a login */}
              <div className="text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  ¿Ya tienes una cuenta?{' '}
                  <Link
                    to="/login"
                    className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    Inicia sesión aquí
                  </Link>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            © 2024 Team Time Management. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
