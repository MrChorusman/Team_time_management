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
  Calendar,
  Users,
  Sun,
  Coffee,
  Plane
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
import { Checkbox } from '../../components/ui/checkbox'
import { apiClient } from '../../services/apiClient'

const EmployeeRegisterPageComplete = () => {
  const navigate = useNavigate()
  const { user, updateEmployee, loading } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [teams, setTeams] = useState([])
  const [communities, setCommunities] = useState([])
  const [loadingData, setLoadingData] = useState(true)
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm()

  // Cargar datos desde la API
  useEffect(() => {
    const loadData = async () => {
      try {
        const [teamsResponse, communitiesResponse] = await Promise.all([
          apiClient.get('/auth-simple/teams'),
          apiClient.get('/auth-simple/autonomous-communities')
        ])
        
        if (teamsResponse.data.success) {
          setTeams(teamsResponse.data.teams)
        }
        
        if (communitiesResponse.data.success) {
          setCommunities(communitiesResponse.data.communities)
        }
      } catch (error) {
        console.error('Error cargando datos:', error)
        // Usar datos por defecto si falla la carga
        setTeams(['Desarrollo Frontend', 'Desarrollo Backend', 'Marketing Digital', 'Ventas'])
        setCommunities(['Madrid', 'Cataluña', 'Andalucía', 'Valencia', 'Galicia'])
      } finally {
        setLoadingData(false)
      }
    }

    loadData()
  }, [])

  // Watchers para campos condicionales
  const hasSummerSchedule = watch('hasSummerSchedule')
  const selectedCountry = watch('country')

  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]

  const onSubmit = async (data) => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      const employeeData = {
        // Información básica
        team_name: data.teamName,
        full_name: data.fullName,
        
        // Configuración horaria
        hours_monday_thursday: parseFloat(data.hoursMonThu),
        hours_friday: parseFloat(data.hoursFriday),
        has_summer_schedule: data.hasSummerSchedule || false,
        summer_hours: data.hasSummerSchedule ? parseFloat(data.summerHours) : null,
        summer_months: data.hasSummerSchedule ? (Array.isArray(data.summerMonths) ? data.summerMonths.join(', ') : data.summerMonths) : null,
        
        // Beneficios laborales
        annual_vacation_days: parseInt(data.annualVacationDays),
        annual_free_hours: parseInt(data.annualFreeHours),
        
        // Ubicación geográfica
        country: data.country,
        region: data.country === 'ES' ? data.autonomousCommunity : data.region,
        city: data.city,
        
        // Fecha de inicio
        start_date: data.startDate,
        notes: data.notes || null
      }

      // Llamada al API para registrar empleado
      const response = await apiClient.post('/auth-simple/employee/register', employeeData)
      
      if (response.data.success) {
        // Actualizar contexto
        updateEmployee(employeeData)
        setSuccess(true)
      } else {
        setError(response.data.message || 'Error al registrar empleado')
      }
      
      // Redirigir después de 2 segundos
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
      
    } catch (error) {
      setError('Error al registrar empleado. Por favor, inténtalo de nuevo.')
      console.error('Error registrando empleado:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loadingData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando formulario...</p>
        </div>
      </div>
    )
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
                  ¡Registro Enviado!
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Tu perfil de empleado ha sido enviado exitosamente. <strong>Está pendiente de aprobación</strong> por un administrador.
                </p>
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mb-4">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    ⏳ <strong>Estado:</strong> Pendiente de aprobación<br/>
                    📧 Recibirás una notificación cuando sea aprobado.
                  </p>
                </div>
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
      <div className="max-w-4xl mx-auto">
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
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
              {/* Error general */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* 1. INFORMACIÓN BÁSICA DEL EMPLEADO */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-2">
                  📋 Información Básica
                </h3>

                {/* Nombre del Equipo */}
                <div className="space-y-2">
                  <Label htmlFor="teamName">Nombre del Equipo *</Label>
                  <Select onValueChange={(value) => setValue('teamName', value)}>
                    <SelectTrigger>
                      <Users className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Selecciona tu equipo" />
                    </SelectTrigger>
                    <SelectContent>
                      {teams.map((team) => (
                        <SelectItem key={team} value={team}>
                          {team}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.teamName && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      El equipo es requerido
                    </p>
                  )}
                </div>

                {/* Nombre y Apellidos */}
                <div className="space-y-2">
                  <Label htmlFor="fullName">Nombre y Apellidos *</Label>
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
                          value: 2,
                          message: 'El nombre debe tener al menos 2 caracteres'
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
              </div>

              {/* 2. CONFIGURACIÓN HORARIA */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-2">
                  🕐 Configuración Horaria
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Horas Lunes a Jueves */}
                  <div className="space-y-2">
                    <Label htmlFor="hoursMonThu">Horas Lunes a Jueves *</Label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="hoursMonThu"
                        type="number"
                        step="0.5"
                        min="0"
                        max="12"
                        placeholder="8.0"
                        className="pl-10"
                        {...register('hoursMonThu', {
                          required: 'Las horas de lunes a jueves son requeridas',
                          min: {
                            value: 0,
                            message: 'Mínimo 0 horas'
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

                  {/* Horas Viernes */}
                  <div className="space-y-2">
                    <Label htmlFor="hoursFriday">Horas Viernes *</Label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="hoursFriday"
                        type="number"
                        step="0.5"
                        min="0"
                        max="12"
                        placeholder="7.0"
                        className="pl-10"
                        {...register('hoursFriday', {
                          required: 'Las horas del viernes son requeridas',
                          min: {
                            value: 0,
                            message: 'Mínimo 0 horas'
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

                {/* Horario de Verano */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="hasSummerSchedule"
                      onCheckedChange={(checked) => {
                        setValue('hasSummerSchedule', checked)
                        // Limpiar campos de verano si se desmarca
                        if (!checked) {
                          setValue('summerHours', '')
                          setValue('summerMonths', [])
                        }
                      }}
                    />
                    <Label htmlFor="hasSummerSchedule" className="text-sm font-medium">
                      ¿Tiene horario de verano?
                    </Label>
                  </div>
                  
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      💡 <strong>Nota:</strong> Si NO tienes horario de verano, se utilizará el horario normal 
                      (Lunes-Jueves y Viernes) durante todo el año.
                    </p>
                  </div>

                  {hasSummerSchedule && (
                    <div className="space-y-4 pl-6 border-l-2 border-blue-200 bg-blue-50/50 dark:bg-blue-900/10 p-4 rounded-r-lg">
                      <div className="flex items-center space-x-2 mb-3">
                        <Sun className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                          Configuración de Horario de Verano
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Horas de Verano */}
                        <div className="space-y-2">
                          <Label htmlFor="summerHours">Horas Horario de Verano *</Label>
                          <div className="relative">
                            <Sun className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                            <Input
                              id="summerHours"
                              type="number"
                              step="0.5"
                              min="0"
                              max="12"
                              placeholder="7.0"
                              className="pl-10"
                              {...register('summerHours', {
                                required: hasSummerSchedule ? 'Las horas de verano son requeridas cuando tienes horario de verano' : false,
                                min: {
                                  value: 0,
                                  message: 'Mínimo 0 horas'
                                },
                                max: {
                                  value: 12,
                                  message: 'Máximo 12 horas'
                                }
                              })}
                            />
                          </div>
                          {errors.summerHours && (
                            <p className="text-sm text-red-600 dark:text-red-400">
                              {errors.summerHours.message}
                            </p>
                          )}
                        </div>

                        {/* Meses de Verano */}
                        <div className="space-y-2">
                          <Label htmlFor="summerMonths">Meses Horario de Verano *</Label>
                          <Select onValueChange={(value) => setValue('summerMonths', [value])}>
                            <SelectTrigger>
                              <Calendar className="w-4 h-4 mr-2" />
                              <SelectValue placeholder="Selecciona meses" />
                            </SelectTrigger>
                            <SelectContent>
                              {months.map((month) => (
                                <SelectItem key={month} value={month}>
                                  {month}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          {errors.summerMonths && (
                            <p className="text-sm text-red-600 dark:text-red-400">
                              Los meses de verano son requeridos cuando tienes horario de verano
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-xs text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-800/30 p-2 rounded">
                        ℹ️ <strong>Ejemplo:</strong> Si seleccionas "Julio" y "Agosto" con 7 horas, 
                        durante esos meses trabajarás 7 horas diarias en lugar del horario normal.
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 3. BENEFICIOS LABORALES */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-2">
                  🎁 Beneficios Laborales
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Días de Vacaciones Anuales */}
                  <div className="space-y-2">
                    <Label htmlFor="annualVacationDays">Días de Vacaciones Anuales *</Label>
                    <div className="relative">
                      <Plane className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="annualVacationDays"
                        type="number"
                        min="1"
                        max="40"
                        placeholder="22"
                        className="pl-10"
                        {...register('annualVacationDays', {
                          required: 'Los días de vacaciones son requeridos',
                          min: {
                            value: 1,
                            message: 'Mínimo 1 día'
                          },
                          max: {
                            value: 40,
                            message: 'Máximo 40 días'
                          }
                        })}
                      />
                    </div>
                    {errors.annualVacationDays && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.annualVacationDays.message}
                      </p>
                    )}
                  </div>

                  {/* Horas de Libre Disposición Anuales */}
                  <div className="space-y-2">
                    <Label htmlFor="annualFreeHours">Horas de Libre Disposición Anuales *</Label>
                    <div className="relative">
                      <Coffee className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="annualFreeHours"
                        type="number"
                        min="0"
                        max="200"
                        placeholder="40"
                        className="pl-10"
                        {...register('annualFreeHours', {
                          required: 'Las horas de libre disposición son requeridas',
                          min: {
                            value: 0,
                            message: 'Mínimo 0 horas'
                          },
                          max: {
                            value: 200,
                            message: 'Máximo 200 horas'
                          }
                        })}
                      />
                    </div>
                    {errors.annualFreeHours && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.annualFreeHours.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* 4. UBICACIÓN GEOGRÁFICA */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-2">
                  🌍 Ubicación Geográfica
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* País */}
                  <div className="space-y-2">
                    <Label htmlFor="country">País *</Label>
                    <Select onValueChange={(value) => {
                      setValue('country', value)
                      // Limpiar comunidad autónoma si cambia el país
                      if (value !== 'ES') {
                        setValue('autonomousCommunity', '')
                      }
                    }}>
                      <SelectTrigger>
                        <Globe className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Selecciona país" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ES">🇪🇸 España</SelectItem>
                        <SelectItem value="MX">🇲🇽 México</SelectItem>
                        <SelectItem value="AR">🇦🇷 Argentina</SelectItem>
                        <SelectItem value="CO">🇨🇴 Colombia</SelectItem>
                        <SelectItem value="PE">🇵🇪 Perú</SelectItem>
                        <SelectItem value="CL">🇨🇱 Chile</SelectItem>
                        <SelectItem value="FR">🇫🇷 Francia</SelectItem>
                        <SelectItem value="BR">🇧🇷 Brasil</SelectItem>
                        <SelectItem value="US">🇺🇸 Estados Unidos</SelectItem>
                        <SelectItem value="GB">🇬🇧 Reino Unido</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.country && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        El país es requerido
                      </p>
                    )}
                  </div>

                  {/* Comunidad Autónoma (solo para España) */}
                  {selectedCountry === 'ES' && (
                    <div className="space-y-2">
                      <Label htmlFor="autonomousCommunity">Comunidad Autónoma *</Label>
                      <Select onValueChange={(value) => setValue('autonomousCommunity', value)}>
                        <SelectTrigger>
                          <MapPin className="w-4 h-4 mr-2" />
                          <SelectValue placeholder="Selecciona comunidad autónoma" />
                        </SelectTrigger>
                        <SelectContent>
                          {/* Filtrar solo las comunidades autónomas españolas */}
                          {communities.filter(community => 
                            ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'Canarias', 
                             'Cantabria', 'Castilla-La Mancha', 'Castilla y León',
                             'Cataluña', 'Comunidad Valenciana', 'Extremadura',
                             'Galicia', 'La Rioja', 'Madrid', 'Murcia', 'Navarra',
                             'País Vasco', 'Ceuta', 'Melilla'].includes(community)
                          ).map((community) => (
                            <SelectItem key={community} value={community}>
                              {community}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {errors.autonomousCommunity && (
                        <p className="text-sm text-red-600 dark:text-red-400">
                          La comunidad autónoma es requerida para España
                        </p>
                      )}
                    </div>
                  )}

                  {/* Región/Estado (para otros países) */}
                  {selectedCountry && selectedCountry !== 'ES' && (
                    <div className="space-y-2">
                      <Label htmlFor="region">
                        {selectedCountry === 'MX' ? 'Estado *' : 
                         selectedCountry === 'AR' ? 'Provincia *' :
                         selectedCountry === 'FR' ? 'Région *' :
                         selectedCountry === 'BR' ? 'Estado *' :
                         selectedCountry === 'US' ? 'Estado *' :
                         selectedCountry === 'GB' ? 'Condado *' :
                         'Región *'}
                      </Label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <Input
                          id="region"
                          type="text"
                          placeholder={
                            selectedCountry === 'MX' ? 'Ej: Ciudad de México' :
                            selectedCountry === 'AR' ? 'Ej: Buenos Aires' :
                            selectedCountry === 'FR' ? 'Ej: Île-de-France' :
                            selectedCountry === 'BR' ? 'Ej: São Paulo' :
                            selectedCountry === 'US' ? 'Ej: California' :
                            selectedCountry === 'GB' ? 'Ej: Greater London' :
                            'Ej: Región'
                          }
                          className="pl-10"
                          {...register('region', {
                            required: selectedCountry !== 'ES' ? 'La región es requerida' : false,
                            minLength: {
                              value: 2,
                              message: 'La región debe tener al menos 2 caracteres'
                            }
                          })}
                        />
                      </div>
                      {errors.region && (
                        <p className="text-sm text-red-600 dark:text-red-400">
                          {errors.region.message}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Ciudad */}
                  <div className="space-y-2">
                    <Label htmlFor="city">Ciudad *</Label>
                    <div className="relative">
                      <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        id="city"
                        type="text"
                        placeholder="Madrid"
                        className="pl-10"
                        {...register('city', {
                          required: 'La ciudad es requerida',
                          minLength: {
                            value: 2,
                            message: 'La ciudad debe tener al menos 2 caracteres'
                          }
                        })}
                      />
                    </div>
                    {errors.city && (
                      <p className="text-sm text-red-600 dark:text-red-400">
                        {errors.city.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* 5. INFORMACIÓN ADICIONAL */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white border-b pb-2">
                  📅 Información Adicional
                </h3>

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

export default EmployeeRegisterPageComplete
