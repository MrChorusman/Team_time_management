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
  Sun
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
import teamService from '../../services/teamService'
import locationService from '../../services/locationService'

const EmployeeRegisterPage = () => {
  const navigate = useNavigate()
  const { user, updateEmployee, loading } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [teams, setTeams] = useState([])
  const [loadingTeams, setLoadingTeams] = useState(true)
  const [hasSummerSchedule, setHasSummerSchedule] = useState(false)
  const [selectedSummerMonths, setSelectedSummerMonths] = useState([])
  
  // Estados para ubicaciones geográficas
  const [countries, setCountries] = useState([])
  const [autonomousCommunities, setAutonomousCommunities] = useState([])
  const [cities, setCities] = useState([])
  const [loadingLocations, setLoadingLocations] = useState({
    countries: false,
    communities: false,
    cities: false
  })
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm({
    defaultValues: {
      vacationDays: 22, // Valor estándar en España
      hldHours: 40 // Valor estándar
    }
  })

  // Meses disponibles para horario de verano
  const months = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' }
  ]

  const selectedCountry = watch('country')
  const selectedCommunity = watch('region')

  // Cargar países al montar el componente
  useEffect(() => {
    const loadCountries = async () => {
      setLoadingLocations(prev => ({ ...prev, countries: true }))
      try {
        const response = await locationService.getAllCountries()
        if (response.success) {
          setCountries(response.countries)
        }
      } catch (error) {
        console.error('Error cargando países:', error)
        setError('Error cargando lista de países')
      } finally {
        setLoadingLocations(prev => ({ ...prev, countries: false }))
      }
    }
    loadCountries()
  }, [])

  // Cargar comunidades autónomas al seleccionar país
  useEffect(() => {
    if (!selectedCountry) {
      setAutonomousCommunities([])
      setCities([])
      setValue('region', '')
      setValue('city', '')
      return
    }

    const loadCommunities = async () => {
      setLoadingLocations(prev => ({ ...prev, communities: true }))
      try {
        const response = await locationService.getAutonomousCommunities(selectedCountry)
        if (response.success) {
          setAutonomousCommunities(response.autonomous_communities)
        }
      } catch (error) {
        console.error('Error cargando comunidades:', error)
        setError('Error cargando comunidades autónomas')
      } finally {
        setLoadingLocations(prev => ({ ...prev, communities: false }))
      }
    }
    loadCommunities()
  }, [selectedCountry, setValue])

  // Cargar ciudades al seleccionar comunidad autónoma
  useEffect(() => {
    if (!selectedCommunity) {
      setCities([])
      setValue('city', '')
      return
    }

    const loadCities = async () => {
      setLoadingLocations(prev => ({ ...prev, cities: true }))
      try {
        const response = await locationService.getCities(selectedCommunity)
        if (response.success) {
          setCities(response.cities)
        }
      } catch (error) {
        console.error('Error cargando ciudades:', error)
        setError('Error cargando ciudades')
      } finally {
        setLoadingLocations(prev => ({ ...prev, cities: false }))
      }
    }
    loadCities()
  }, [selectedCommunity, setValue])

  // Cargar equipos disponibles
  useEffect(() => {
    const loadTeams = async () => {
      try {
        setLoadingTeams(true)
        const response = await teamService.getAllTeams()
        if (response.success && response.teams) {
          setTeams(response.teams)
        }
      } catch (error) {
        console.error('Error cargando equipos:', error)
        setError('Error cargando equipos. Por favor, recarga la página.')
      } finally {
        setLoadingTeams(false)
      }
    }
    
    loadTeams()
  }, [])

  const onSubmit = async (data) => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      // Validar que se haya seleccionado un equipo
      if (!data.team) {
        setError('Por favor, selecciona un equipo')
        setIsSubmitting(false)
        return
      }

      // Validar horario de verano si está activado
      if (hasSummerSchedule) {
        if (!data.hoursSummer) {
          setError('Por favor, indica las horas de trabajo en verano')
          setIsSubmitting(false)
          return
        }
        if (selectedSummerMonths.length === 0) {
          setError('Por favor, selecciona al menos un mes de verano')
          setIsSubmitting(false)
          return
        }
      }

      // Obtener nombres de país y comunidad autónoma para enviar al backend
      const selectedCountryObj = countries.find(c => c.code === data.country)
      const selectedCommunityObj = autonomousCommunities.find(c => c.id.toString() === data.region)
      
      // Preparar datos del empleado
      const employeeData = {
        full_name: data.fullName,
        team_id: parseInt(data.team), // CRÍTICO: Equipo es obligatorio
        country: selectedCountryObj?.name || data.country,
        region: selectedCommunityObj?.name || data.region,
        city: data.city,
        hours_monday_thursday: parseFloat(data.hoursMonThu),
        hours_friday: parseFloat(data.hoursFriday),
        annual_vacation_days: parseInt(data.vacationDays), // Del formulario
        annual_hld_hours: parseInt(data.hldHours), // Del formulario
        has_summer_schedule: hasSummerSchedule,
        hours_summer: hasSummerSchedule ? parseFloat(data.hoursSummer) : null,
        summer_months: hasSummerSchedule ? selectedSummerMonths : []
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

              {/* Equipo */}
              <div className="space-y-2">
                <Label htmlFor="team">Equipo *</Label>
                <Select 
                  onValueChange={(value) => setValue('team', value)}
                  disabled={loadingTeams}
                >
                  <SelectTrigger>
                    <Users className="w-4 h-4 mr-2" />
                    <SelectValue placeholder={loadingTeams ? "Cargando equipos..." : "Selecciona equipo"} />
                  </SelectTrigger>
                  <SelectContent>
                    {teams.map((team) => (
                      <SelectItem key={team.id} value={team.id.toString()}>
                        {team.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.team && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    El equipo es requerido
                  </p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Selecciona el equipo al que perteneces
                </p>
              </div>

              {/* Ubicación */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* País */}
                <div className="space-y-2">
                  <Label htmlFor="country">País *</Label>
                  <Select 
                    onValueChange={(value) => setValue('country', value)}
                    disabled={loadingLocations.countries}
                  >
                    <SelectTrigger>
                      <Globe className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={loadingLocations.countries ? "Cargando..." : "Selecciona país"} />
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
                  {loadingLocations.countries && (
                    <p className="text-xs text-gray-500">Cargando países...</p>
                  )}
                </div>

                {/* Comunidad Autónoma / Región */}
                <div className="space-y-2">
                  <Label htmlFor="region">Comunidad Autónoma / Región *</Label>
                  <Select 
                    onValueChange={(value) => setValue('region', value)}
                    disabled={!selectedCountry || loadingLocations.communities || autonomousCommunities.length === 0}
                  >
                    <SelectTrigger>
                      <MapPin className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={
                        loadingLocations.communities ? "Cargando..." :
                        !selectedCountry ? "Selecciona país primero" :
                        autonomousCommunities.length === 0 ? "No hay comunidades disponibles" :
                        "Selecciona comunidad"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {autonomousCommunities.map((community) => (
                        <SelectItem key={community.id} value={community.id.toString()}>
                          {community.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.region && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      La comunidad autónoma es requerida
                    </p>
                  )}
                  {loadingLocations.communities && (
                    <p className="text-xs text-gray-500">Cargando comunidades...</p>
                  )}
                </div>

                {/* Ciudad */}
                <div className="space-y-2">
                  <Label htmlFor="city">Ciudad *</Label>
                  <Select 
                    onValueChange={(value) => setValue('city', value)}
                    disabled={!selectedCommunity || loadingLocations.cities || cities.length === 0}
                  >
                    <SelectTrigger>
                      <Building className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={
                        loadingLocations.cities ? "Cargando..." :
                        !selectedCommunity ? "Selecciona comunidad primero" :
                        cities.length === 0 ? "No hay ciudades disponibles" :
                        "Selecciona ciudad"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.map((city) => (
                        <SelectItem key={city.id} value={city.name}>
                          {city.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.city && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      La ciudad es requerida
                    </p>
                  )}
                  {loadingLocations.cities && (
                    <p className="text-xs text-gray-500">Cargando ciudades...</p>
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

              {/* Beneficios laborales */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vacationDays">Días de Vacaciones Anuales *</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="vacationDays"
                      type="number"
                      min="1"
                      max="40"
                      placeholder="22"
                      className="pl-10"
                      {...register('vacationDays', {
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
                  {errors.vacationDays && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.vacationDays.message}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Estándar en España: 22 días laborables
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="hldHours">Horas Libre Disposición Anuales *</Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="hldHours"
                      type="number"
                      min="0"
                      max="200"
                      placeholder="40"
                      className="pl-10"
                      {...register('hldHours', {
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
                  {errors.hldHours && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {errors.hldHours.message}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Típicamente entre 40-80 horas anuales
                  </p>
                </div>
              </div>

              {/* Horario de verano */}
              <div className="space-y-4 border-t pt-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="hasSummer"
                    checked={hasSummerSchedule}
                    onChange={(e) => setHasSummerSchedule(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <Label htmlFor="hasSummer" className="flex items-center cursor-pointer">
                    <Sun className="w-4 h-4 mr-2" />
                    ¿Tiene horario de verano? (jornada intensiva)
                  </Label>
                </div>

                {hasSummerSchedule && (
                  <div className="space-y-4 pl-6 border-l-2 border-yellow-400">
                    <div className="space-y-2">
                      <Label htmlFor="hoursSummer">Horas Verano *</Label>
                      <div className="relative">
                        <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <Input
                          id="hoursSummer"
                          type="number"
                          step="0.5"
                          min="1"
                          max="12"
                          placeholder="7.0"
                          className="pl-10"
                          {...register('hoursSummer', {
                            required: hasSummerSchedule ? 'Las horas de verano son requeridas' : false
                          })}
                        />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Horas de trabajo diarias durante el verano
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label>Meses con horario de verano *</Label>
                      <div className="grid grid-cols-3 gap-2">
                        {months.map((month) => (
                          <div key={month.value} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={`month-${month.value}`}
                              value={month.value}
                              checked={selectedSummerMonths.includes(month.value)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedSummerMonths([...selectedSummerMonths, month.value])
                                } else {
                                  setSelectedSummerMonths(selectedSummerMonths.filter(m => m !== month.value))
                                }
                              }}
                              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <Label htmlFor={`month-${month.value}`} className="text-sm cursor-pointer">
                              {month.label}
                            </Label>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Selecciona los meses en los que aplica el horario de verano
                      </p>
                    </div>
                  </div>
                )}
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
