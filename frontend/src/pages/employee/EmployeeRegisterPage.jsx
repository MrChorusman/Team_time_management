import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
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
import { MultiSelect } from '../../components/ui/multi-select'
import employeeService from '../../services/employeeService'
import teamService from '../../services/teamService'

const EmployeeRegisterPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, updateEmployee, loading, logout } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [teams, setTeams] = useState([])
  const [loadingTeams, setLoadingTeams] = useState(true)
  const [hasSummerSchedule, setHasSummerSchedule] = useState(false)
  const [selectedSummerMonths, setSelectedSummerMonths] = useState([])
  const [selectedTeamIds, setSelectedTeamIds] = useState([])
  const [primaryTeamId, setPrimaryTeamId] = useState(null)
  const [invitationToken, setInvitationToken] = useState(null)
  const [invitationEmail, setInvitationEmail] = useState(null)
  const [tokenValidating, setTokenValidating] = useState(false)
  const [tokenError, setTokenError] = useState(null)

  // Función para manejar cambios en la selección de equipos desde MultiSelect
  const handleTeamSelectionChange = (selectedIds) => {
    setSelectedTeamIds(selectedIds)
    // Si el equipo principal ya no está seleccionado, cambiarlo al primero disponible
    if (primaryTeamId && !selectedIds.includes(primaryTeamId)) {
      setPrimaryTeamId(selectedIds[0] || null)
    }
    // Si no hay equipo principal y hay equipos seleccionados, establecer el primero como principal
    if (!primaryTeamId && selectedIds.length > 0) {
      setPrimaryTeamId(selectedIds[0])
    }
  }
  
  // Estados para países, regiones y ciudades desde BD
  const [countries, setCountries] = useState([])
  const [regions, setRegions] = useState([])
  const [cities, setCities] = useState([])
  const [loadingCountries, setLoadingCountries] = useState(true)
  const [loadingRegions, setLoadingRegions] = useState(false)
  const [loadingCities, setLoadingCities] = useState(false)
  
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

  // Definir selectedCountry y selectedRegion ANTES de usarlos en useEffect
  const selectedCountry = watch('country')
  const selectedRegion = watch('region')

  // Cargar países desde BD
  useEffect(() => {
    const loadCountries = async () => {
      try {
        setLoadingCountries(true)
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/locations/public/countries`, {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setCountries(data.countries || [])
          }
        }
      } catch (error) {
        console.error('Error cargando países:', error)
      } finally {
        setLoadingCountries(false)
      }
    }
    loadCountries()
  }, [])

  // Cargar regiones cuando se selecciona un país
  useEffect(() => {
    const loadRegions = async () => {
      if (!selectedCountry) {
        setRegions([])
        setCities([])
        return
      }
      
      try {
        setLoadingRegions(true)
        const country = countries.find(c => c.code === selectedCountry || c.name === selectedCountry)
        if (!country) return
        
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/locations/public/autonomous-communities?country_code=${country.code}`,
          { credentials: 'include' }
        )
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setRegions(data.autonomous_communities || [])
          }
        }
      } catch (error) {
        console.error('Error cargando regiones:', error)
      } finally {
        setLoadingRegions(false)
      }
    }
    loadRegions()
  }, [selectedCountry, countries])

  // Cargar ciudades cuando se selecciona una región
  useEffect(() => {
    const loadCities = async () => {
      if (!selectedRegion) {
        setCities([])
        return
      }
      
      try {
        setLoadingCities(true)
        const region = regions.find(r => r.name === selectedRegion || r.id === selectedRegion)
        if (!region) return
        
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/locations/public/cities?autonomous_community_id=${region.id}`,
          { credentials: 'include' }
        )
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setCities(data.cities || [])
          }
        }
      } catch (error) {
        console.error('Error cargando ciudades:', error)
      } finally {
        setLoadingCities(false)
      }
    }
    loadCities()
  }, [selectedRegion, regions])

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

  // Verificar token de invitación
  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      verifyInvitationToken(token)
    }
  }, [searchParams])

  // Función para verificar token
  const verifyInvitationToken = async (token) => {
    setTokenValidating(true)
    setTokenError(null)
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/invite/${token}`, {
        method: 'GET',
        credentials: 'include'
      })
      
      const data = await response.json()
      
      if (response.ok && data.valid) {
        setInvitationToken(token)
        setInvitationEmail(data.email)
        
        // Pre-llenar el email si el usuario no está logueado
        if (!user || !user.email) {
          setValue('email', data.email)
        }
      } else {
        setTokenError(data.error || 'Token de invitación inválido o expirado')
      }
    } catch (error) {
      console.error('Error verificando token:', error)
      setTokenError('Error al verificar la invitación')
    } finally {
      setTokenValidating(false)
    }
  }

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
      const normalizedTeamIds = selectedTeamIds.length > 0
        ? selectedTeamIds
        : (primaryTeamId ? [primaryTeamId] : [])

      if (normalizedTeamIds.length === 0) {
        setError('Por favor, selecciona al menos un equipo')
        setIsSubmitting(false)
        return
      }

      const effectivePrimaryTeamId = primaryTeamId || normalizedTeamIds[0]

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

      // Preparar datos del empleado
      const employeeData = {
        full_name: data.fullName,
        team_id: parseInt(effectivePrimaryTeamId, 10),
        country: data.country,
        region: data.region,
        city: data.city,
        hours_monday_thursday: parseFloat(data.hoursMonThu),
        hours_friday: parseFloat(data.hoursFriday),
        annual_vacation_days: parseInt(data.vacationDays), // Del formulario
        annual_hld_hours: parseInt(data.hldHours), // Del formulario
        has_summer_schedule: hasSummerSchedule,
        hours_summer: hasSummerSchedule ? parseFloat(data.hoursSummer) : null,
        summer_months: hasSummerSchedule ? selectedSummerMonths : []
      }

      employeeData.team_ids = normalizedTeamIds.map((id) => parseInt(id, 10))

      // Llamada real al API para crear el empleado
      const response = await employeeService.createEmployee(employeeData)
      
      if (response.success) {
        // Actualizar contexto con los datos del empleado creado
        updateEmployee(response.employee)
        setSuccess(true)
        
        // Si hay token de invitación, marcarlo como usado
        if (invitationToken) {
          try {
            await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees/invite/${invitationToken}/use`, {
              method: 'POST',
              credentials: 'include'
            })
          } catch (error) {
            console.error('Error marcando invitación como usada:', error)
            // No bloquear el flujo si falla
          }
        }
        
        // NO redirigir automáticamente - mostrar mensaje de éxito persistente
        // El usuario debe esperar aprobación del manager
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
                  Tu perfil de empleado ha sido enviado para aprobación. 
                  <strong> Debes esperar a que el manager de tu equipo apruebe tu registro</strong> antes de poder acceder a todas las funcionalidades.
                </p>
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mb-4">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    Estado: <strong>Pendiente de aprobación</strong>
                  </p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">
                    Recibirás un email cuando tu registro sea aprobado por el manager de tu equipo.
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button 
                    onClick={() => navigate('/dashboard')} 
                    variant="outline"
                    className="flex-1"
                  >
                    Ir a Dashboard
                  </Button>
                  <Button 
                    onClick={async () => {
                      await logout()
                      navigate('/login')
                    }}
                    variant="outline"
                    className="flex-1"
                  >
                    Cerrar Sesión
                  </Button>
                </div>
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
          <div className="flex justify-between items-start mb-4">
            <Button
              variant="ghost"
              onClick={async () => {
                await logout()
                navigate('/login')
              }}
              className="text-gray-600 dark:text-gray-400"
            >
              Cerrar Sesión
            </Button>
            <div className="flex-1"></div>
          </div>
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

        {/* Alert de validación de token */}
        {tokenValidating && (
          <Alert className="mb-6">
            <AlertDescription className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent mr-2" />
              Verificando invitación...
            </AlertDescription>
          </Alert>
        )}

        {/* Alert de error de token */}
        {tokenError && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>
              <strong>Invitación inválida:</strong> {tokenError}
              <p className="mt-2 text-sm">
                Por favor, solicita una nueva invitación a tu administrador.
              </p>
            </AlertDescription>
          </Alert>
        )}

        {/* Alert de invitación válida */}
        {invitationToken && !tokenError && (
          <Alert className="mb-6 bg-green-50 border-green-200">
            <AlertDescription className="text-green-800">
              <strong>✓ Invitación válida</strong>
              <p className="mt-1">
                Completa tu registro para unirte al equipo: <strong>{invitationEmail}</strong>
              </p>
            </AlertDescription>
          </Alert>
        )}

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

              {/* Equipos */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Equipos *</Label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Selecciona uno o varios equipos a los que perteneces
                    </p>
                  </div>
                  {selectedTeamIds.length > 0 && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {selectedTeamIds.length} seleccionado{selectedTeamIds.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
                <MultiSelect
                  options={teams.map(team => ({ id: team.id, name: team.name }))}
                  selected={selectedTeamIds}
                  onSelect={handleTeamSelectionChange}
                  placeholder="Selecciona equipos..."
                  searchPlaceholder="Buscar equipos..."
                  emptyText="No se encontraron equipos."
                  disabled={loadingTeams}
                />
                {selectedTeamIds.length === 0 && (
                  <p className="text-xs text-red-600 dark:text-red-400">
                    Debes seleccionar al menos un equipo
                  </p>
                )}
                {selectedTeamIds.length > 0 && (
                  <div className="pt-2 space-y-2">
                    <Label>Equipo principal</Label>
                    <Select
                      value={primaryTeamId?.toString() || ''}
                      onValueChange={(value) => setPrimaryTeamId(parseInt(value, 10))}
                    >
                      <SelectTrigger>
                        <Users className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Selecciona equipo principal" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedTeamIds.map((teamId) => {
                          const team = teams.find((t) => t.id === teamId)
                          if (!team) return null
                          return (
                            <SelectItem key={team.id} value={team.id.toString()}>
                              {team.name}
                            </SelectItem>
                          )
                        })}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      El equipo principal se utilizará como referencia por defecto hasta que un manager configure los porcentajes.
                    </p>
                  </div>
                )}
              </div>

              {/* Ubicación */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* País */}
                <div className="space-y-2">
                  <Label htmlFor="country">País *</Label>
                  <Select 
                    onValueChange={(value) => {
                      setValue('country', value)
                      setValue('region', '') // Limpiar región al cambiar país
                      setValue('city', '') // Limpiar ciudad al cambiar país
                    }}
                    disabled={loadingCountries}
                  >
                    <SelectTrigger>
                      <Globe className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={loadingCountries ? "Cargando países..." : "Selecciona país"} />
                    </SelectTrigger>
                    <SelectContent>
                      {countries.map((country) => (
                        <SelectItem key={country.code || country.id} value={country.code || country.name}>
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
                    onValueChange={(value) => {
                      setValue('region', value)
                      setValue('city', '') // Limpiar ciudad al cambiar región
                    }}
                    disabled={!selectedCountry || loadingRegions}
                  >
                    <SelectTrigger>
                      <MapPin className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={
                        !selectedCountry 
                          ? "Selecciona primero un país" 
                          : loadingRegions 
                            ? "Cargando regiones..." 
                            : "Selecciona región"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {regions.map((region) => (
                        <SelectItem key={region.id || region.name} value={region.name}>
                          {region.name}
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
                    disabled={!selectedRegion || loadingCities}
                  >
                    <SelectTrigger>
                      <Building className="w-4 h-4 mr-2" />
                      <SelectValue placeholder={
                        !selectedRegion 
                          ? "Selecciona primero una región" 
                          : loadingCities 
                            ? "Cargando ciudades..." 
                            : "Selecciona ciudad"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.map((city) => (
                        <SelectItem key={city.id || city.name} value={city.name}>
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
                      max="50"
                      placeholder="22"
                      className="pl-10"
                      {...register('vacationDays', {
                        required: 'Los días de vacaciones son requeridos',
                        min: {
                          value: 1,
                          message: 'Mínimo 1 día'
                        },
                        max: {
                          value: 50,
                          message: 'Máximo 50 días'
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
                      max="300"
                      placeholder="40"
                      className="pl-10"
                      {...register('hldHours', {
                        required: 'Las horas de libre disposición son requeridas',
                        min: {
                          value: 0,
                          message: 'Mínimo 0 horas'
                        },
                        max: {
                          value: 300,
                          message: 'Máximo 300 horas'
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
                  Ir a Dashboard
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
