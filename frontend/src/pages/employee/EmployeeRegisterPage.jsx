import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { 
  User, 
  MapPin, 
  Clock, 
  Building, 
  Save,
  ArrowLeft,
  Globe,
  Calendar
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import { Textarea } from '../../components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Alert, AlertDescription } from '../../components/ui/alert'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import employeeService from '../../services/employeeService'

const EmployeeRegisterPage = () => {
  const navigate = useNavigate()
  const { user, updateEmployee, loading } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm()

  // Datos de países, regiones y ciudades (simplificado)
  const countries = [
    { code: 'ES', name: 'España' },
    { code: 'MX', name: 'México' },
    { code: 'AR', name: 'Argentina' },
    { code: 'CO', name: 'Colombia' },
    { code: 'PE', name: 'Perú' },
    { code: 'CL', name: 'Chile' }
  ]

  const regions = {
    'ES': ['Madrid', 'Cataluña', 'Andalucía', 'Valencia', 'País Vasco'],
    'MX': ['Ciudad de México', 'Jalisco', 'Nuevo León', 'Puebla', 'Guanajuato'],
    'AR': ['Buenos Aires', 'Córdoba', 'Santa Fe', 'Mendoza', 'Tucumán'],
    'CO': ['Bogotá', 'Antioquia', 'Valle del Cauca', 'Atlántico', 'Santander'],
    'PE': ['Lima', 'Arequipa', 'La Libertad', 'Piura', 'Lambayeque'],
    'CL': ['Santiago', 'Valparaíso', 'Biobío', 'Araucanía', 'Los Lagos']
  }

  const cities = {
    'Madrid': ['Madrid', 'Alcalá de Henares', 'Móstoles', 'Fuenlabrada'],
    'Cataluña': ['Barcelona', 'Hospitalet de Llobregat', 'Terrassa', 'Badalona'],
    'Ciudad de México': ['Ciudad de México', 'Ecatepec', 'Guadalajara', 'Puebla'],
    'Buenos Aires': ['Buenos Aires', 'La Plata', 'Mar del Plata', 'Bahía Blanca'],
    'Bogotá': ['Bogotá', 'Soacha', 'Villavicencio', 'Facatativá']
  }

  const selectedCountry = watch('country')
  const selectedRegion = watch('region')

  const onSubmit = async (data) => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      // Preparar datos del empleado
      const employeeData = {
        full_name: data.fullName,
        country: data.country,
        region: data.region,
        city: data.city,
        hours_monday_thursday: parseFloat(data.hoursMonThu),
        hours_friday: parseFloat(data.hoursFriday),
        start_date: data.startDate,
        notes: data.notes || null
      }

      // Llamada real al API para crear el empleado
      const response = await employeeService.createEmployee(employeeData)
      
      if (response.success) {
        // Actualizar contexto con los datos del empleado creado
        updateEmployee(response.employee)
        setSuccess(true)
        
        // Redirigir después de 2 segundos
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      } else {
        setError(response.message || 'Error al registrar empleado. Por favor, inténtalo de nuevo.')
      }
      
    } catch (error) {
      console.error('Error registrando empleado:', error)
      
      // Manejar diferentes tipos de errores
      if (error.response) {
        // Error de respuesta del servidor
        const errorMessage = error.response.data?.message || 
                            error.response.data?.error ||
                            'Error al registrar empleado. Por favor, inténtalo de nuevo.'
        setError(errorMessage)
      } else if (error.request) {
        // Error de red
        setError('Error de conexión. Por favor, verifica tu conexión a internet.')
      } else {
        // Otro tipo de error
        setError('Error inesperado. Por favor, inténtalo de nuevo.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="mx-auto h-12 w-12 bg-green-600 rounded-full flex items-center justify-center mb-4">
                  <User className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  ¡Registro Completado!
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Tu perfil de empleado ha sido enviado para aprobación. Serás redirigido al dashboard.
                </p>
                <LoadingSpinner size="sm" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">TTM</span>
          </div>
          <h1 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Registro de Empleado
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Completa tu perfil para acceder a todas las funcionalidades
          </p>
        </div>

        {/* Información del usuario actual */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Usuario: {user?.email}
            </CardTitle>
            <CardDescription>
              Completa los siguientes datos para crear tu perfil de empleado
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Formulario */}
        <Card>
          <CardHeader>
            <CardTitle>Información del Empleado</CardTitle>
            <CardDescription>
              Todos los campos marcados con * son obligatorios
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Error general */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Nombre completo */}
              <div className="space-y-2">
                <Label htmlFor="fullName">Nombre Completo *</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    id="fullName"
                    type="text"
                    placeholder="Juan Pérez García"
                    className="pl-10"
                    {...register('fullName', {
                      required: 'El nombre completo es requerido',
                      minLength: {
                        value: 3,
                        message: 'El nombre debe tener al menos 3 caracteres'
                      }
                    })}
                  />
                </div>
                {errors.fullName && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errors.fullName.message}
                  </p>
                )}
              </div>

              {/* Ubicación */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* País */}
                <div className="space-y-2">
                  <Label htmlFor="country">País *</Label>
                  <Select onValueChange={(value) => setValue('country', value)}>
                    <SelectTrigger>
                      <Globe className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Selecciona país" />
                    </SelectTrigger>
                    <SelectContent>
                      {countries.map((country) => (
                        <SelectItem key={country.code} value={country.code}>
                          {country.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.country && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      El país es requerido
                    </p>
                  )}
                </div>

                {/* Región */}
                <div className="space-y-2">
                  <Label htmlFor="region">Región/Estado *</Label>
                  <Select 
                    onValueChange={(value) => setValue('region', value)}
                    disabled={!selectedCountry}
                  >
                    <SelectTrigger>
                      <MapPin className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Selecciona región" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedCountry && regions[selectedCountry]?.map((region) => (
                        <SelectItem key={region} value={region}>
                          {region}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.region && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      La región es requerida
                    </p>
                  )}
                </div>

                {/* Ciudad */}
                <div className="space-y-2">
                  <Label htmlFor="city">Ciudad *</Label>
                  <Select 
                    onValueChange={(value) => setValue('city', value)}
                    disabled={!selectedRegion}
                  >
                    <SelectTrigger>
                      <Building className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Selecciona ciudad" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedRegion && cities[selectedRegion]?.map((city) => (
                        <SelectItem key={city} value={city}>
                          {city}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.city && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      La ciudad es requerida
                    </p>
                  )}
                </div>
              </div>

              {/* Configuración horaria */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hoursMonThu">Horas Lunes-Jueves *</Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="hoursMonThu"
                      type="number"
                      step="0.5"
                      min="1"
                      max="12"
                      placeholder="8.0"
                      className="pl-10"
                      {...register('hoursMonThu', {
                        required: 'Las horas de lunes a jueves son requeridas',
                        min: {
                          value: 1,
                          message: 'Mínimo 1 hora'
                        },
                        max: {
                          value: 12,
                          message: 'Máximo 12 horas'
                        }
                      })}
                    />
                  </div>
                  {errors.hoursMonThu && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.hoursMonThu.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="hoursFriday">Horas Viernes *</Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="hoursFriday"
                      type="number"
                      step="0.5"
                      min="1"
                      max="12"
                      placeholder="6.0"
                      className="pl-10"
                      {...register('hoursFriday', {
                        required: 'Las horas del viernes son requeridas',
                        min: {
                          value: 1,
                          message: 'Mínimo 1 hora'
                        },
                        max: {
                          value: 12,
                          message: 'Máximo 12 horas'
                        }
                      })}
                    />
                  </div>
                  {errors.hoursFriday && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.hoursFriday.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Fecha de inicio */}
              <div className="space-y-2">
                <Label htmlFor="startDate">Fecha de Inicio *</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    id="startDate"
                    type="date"
                    className="pl-10"
                    {...register('startDate', {
                      required: 'La fecha de inicio es requerida'
                    })}
                  />
                </div>
                {errors.startDate && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errors.startDate.message}
                  </p>
                )}
              </div>

              {/* Notas adicionales */}
              <div className="space-y-2">
                <Label htmlFor="notes">Notas Adicionales</Label>
                <Textarea
                  id="notes"
                  placeholder="Información adicional relevante (opcional)"
                  rows={3}
                  {...register('notes')}
                />
              </div>

              {/* Botones */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver al Dashboard
                </Button>
                
                <Button
                  type="submit"
                  disabled={isSubmitting || loading}
                  className="flex-1"
                >
                  {isSubmitting ? (
                    <LoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  {isSubmitting ? 'Guardando...' : 'Guardar Perfil'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Tu información será revisada por un administrador antes de ser aprobada.
          </p>
        </div>
      </div>
    </div>
  )
}

export default EmployeeRegisterPage
