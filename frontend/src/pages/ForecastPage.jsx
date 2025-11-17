import { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Clock, 
  DollarSign,
  Users,
  Building,
  Calendar,
  BarChart3,
  Target,
  AlertCircle,
  CheckCircle,
  XCircle,
  Download,
  Filter
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Progress } from '../components/ui/progress'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Alert, AlertDescription } from '../components/ui/alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { toast } from 'sonner'

const ForecastPage = () => {
  const { user, employee, isAdmin, isManager, isEmployee } = useAuth()
  const [loading, setLoading] = useState(true)
  const [companiesLoading, setCompaniesLoading] = useState(true)
  const [companies, setCompanies] = useState([])
  const [selectedCompanyId, setSelectedCompanyId] = useState(null)
  const [selectedView, setSelectedView] = useState('employee') // 'employee', 'team', 'global'
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null)
  const [selectedTeamId, setSelectedTeamId] = useState(null)
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)
  const [forecastData, setForecastData] = useState(null)
  const [employees, setEmployees] = useState([])
  const [teams, setTeams] = useState([])

  useEffect(() => {
    const initializeData = async () => {
      setLoading(true)
      setCompaniesLoading(true)
      
      await Promise.all([
        loadCompanies(),
        loadEmployees(),
        loadTeams()
      ])
      
      setCompaniesLoading(false)
      setLoading(false)
    }
    
    initializeData()
  }, [])

  // Establecer vista por defecto después de cargar empleados
  useEffect(() => {
    if (companiesLoading) return
    
    // Establecer vista por defecto según el rol
    if (isEmployee() && employee) {
      setSelectedView('employee')
      setSelectedEmployeeId(employee.id)
    } else if (isManager() && employee?.team_id) {
      setSelectedView('team')
      setSelectedTeamId(employee.team_id)
    } else if (isAdmin() && employees.length > 0 && !selectedEmployeeId) {
      setSelectedView('employee')
      // Seleccionar el primer empleado por defecto
      setSelectedEmployeeId(employees[0].id)
    }
  }, [companiesLoading, employees, employee])

  useEffect(() => {
    if (companiesLoading) return // Esperar a que se carguen las empresas
    
    if (selectedCompanyId && selectedView) {
      // Validar que se haya seleccionado empleado/equipo según la vista
      if (selectedView === 'employee') {
        if (!selectedEmployeeId && !isEmployee()) {
          setLoading(false)
          return // Esperar a que se seleccione un empleado
        }
      }
      if (selectedView === 'team' && !selectedTeamId) {
        setLoading(false)
        return // Esperar a que se seleccione un equipo
      }
      loadForecast()
    } else {
      setLoading(false)
    }
  }, [selectedCompanyId, selectedView, selectedEmployeeId, selectedTeamId, currentYear, currentMonth, companiesLoading])

  const loadCompanies = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/companies?active_only=true`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setCompanies(data.companies || [])
          // Seleccionar la primera empresa por defecto si hay empresas
          if (data.companies && data.companies.length > 0 && !selectedCompanyId) {
            setSelectedCompanyId(data.companies[0].id)
          }
        }
      }
    } catch (error) {
      console.error('Error cargando empresas:', error)
      toast.error('Error cargando empresas')
    }
  }

  const loadEmployees = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          const employeesList = data.employees || []
          setEmployees(employeesList)
        }
      }
    } catch (error) {
      console.error('Error cargando empleados:', error)
    }
  }

  const loadTeams = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/teams`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setTeams(data.teams || [])
          // Si es manager, seleccionar su equipo por defecto
          if (isManager() && employee?.team_id && !selectedTeamId) {
            setSelectedTeamId(employee.team_id)
          }
        }
      }
    } catch (error) {
      console.error('Error cargando equipos:', error)
    }
  }

  const loadForecast = async () => {
    if (!selectedCompanyId) return

    setLoading(true)
    try {
      let url = `${import.meta.env.VITE_API_BASE_URL}/forecast?company_id=${selectedCompanyId}&year=${currentYear}&month=${currentMonth}&view=${selectedView}`
      
      if (selectedView === 'employee' && selectedEmployeeId) {
        url += `&employee_id=${selectedEmployeeId}`
      } else if (selectedView === 'team' && selectedTeamId) {
        url += `&team_id=${selectedTeamId}`
      }

      const response = await fetch(url, {
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setForecastData(data.forecast)
        } else {
          toast.error(data.message || 'Error obteniendo forecast')
        }
      } else {
        const errorData = await response.json().catch(() => ({}))
        toast.error(errorData.message || 'Error obteniendo forecast')
      }
    } catch (error) {
      console.error('Error cargando forecast:', error)
      toast.error('Error de conexión al cargar forecast')
    } finally {
      setLoading(false)
    }
  }

  const getPerformanceBadge = (status) => {
    switch (status) {
      case 'excellent':
        return <Badge className="bg-green-100 text-green-800 border-green-300"><CheckCircle className="w-3 h-3 mr-1" />Excelente</Badge>
      case 'good':
        return <Badge className="bg-blue-100 text-blue-800 border-blue-300"><Target className="w-3 h-3 mr-1" />Bueno</Badge>
      case 'needs_improvement':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300"><AlertCircle className="w-3 h-3 mr-1" />Mejorable</Badge>
      default:
        return <Badge variant="outline">Sin datos</Badge>
    }
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A'
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
  }


  const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

  if (loading && !forecastData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Forecast</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Análisis de horas y eficiencia por períodos de facturación
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Layout: Información a la izquierda, Filtros a la derecha */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna izquierda: Información en lista */}
        <div className="lg:col-span-2 space-y-4">
          {forecastData ? (
            <Card>
              <CardHeader>
                <CardTitle>Información del Forecast</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Horas Teóricas */}
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Clock className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Horas Teóricas</p>
                        <p className="text-sm text-gray-500">
                          Período: {forecastData.period_start ? new Date(forecastData.period_start).toLocaleDateString('es-ES') : 'N/A'} - {forecastData.period_end ? new Date(forecastData.period_end).toLocaleDateString('es-ES') : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {forecastData.theoretical_hours || 0}h
                    </div>
                  </div>

                  {/* Horas Reales */}
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Clock className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Horas Reales</p>
                        <p className="text-sm text-gray-500">Sin incluir guardias</p>
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {forecastData.actual_hours || 0}h
                    </div>
                  </div>

                  {/* Eficiencia */}
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <TrendingUp className="w-5 h-5 text-gray-500" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">Eficiencia</p>
                        <div className="mt-2">
                          <Progress value={forecastData.efficiency || 0} className="h-2" />
                        </div>
                        <div className="mt-2">
                          {getPerformanceBadge(forecastData.performance_status)}
                        </div>
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {forecastData.efficiency || 0}%
                    </div>
                  </div>

                  {/* Valor Económico */}
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <DollarSign className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Valor Económico</p>
                        <p className="text-sm text-gray-500">
                          {forecastData.hourly_rate ? `Tarifa: ${formatCurrency(forecastData.hourly_rate)}/h` : 'Sin tarifa configurada'}
                        </p>
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {forecastData.economic_value ? formatCurrency(forecastData.economic_value) : 'N/A'}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-gray-500">
                  {loading ? 'Calculando forecast...' : 'Selecciona los filtros para ver el forecast'}
                </div>
              </CardContent>
            </Card>
              ) : (
                <Card>
                  <CardContent className="py-12">
                    <div className="text-center text-gray-500">
                      Selecciona los filtros para ver el forecast
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Columna derecha: Filtros */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Filter className="w-5 h-5 mr-2" />
                    Filtros
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Selector de Empresa */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Empresa</label>
                      <Select 
                        value={selectedCompanyId?.toString() || ''} 
                        onValueChange={(value) => setSelectedCompanyId(parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar empresa" />
                        </SelectTrigger>
                        <SelectContent>
                          {companies.map(company => (
                            <SelectItem key={company.id} value={company.id.toString()}>
                              {company.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Selector de Vista */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Vista</label>
                      <Select value={selectedView} onValueChange={setSelectedView}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {isEmployee() && (
                            <SelectItem value="employee">Por Empleado</SelectItem>
                          )}
                          {(isManager() || isAdmin()) && (
                            <>
                              <SelectItem value="team">Por Equipo</SelectItem>
                              {isAdmin() && <SelectItem value="global">Vista Global</SelectItem>}
                            </>
                          )}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Selector de Empleado (si vista es employee) */}
                    {selectedView === 'employee' && (isAdmin() || isManager()) && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Empleado</label>
                        <Select 
                          value={selectedEmployeeId?.toString() || ''} 
                          onValueChange={(value) => setSelectedEmployeeId(parseInt(value))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccionar empleado" />
                          </SelectTrigger>
                          <SelectContent>
                            {employees.map(emp => (
                              <SelectItem key={emp.id} value={emp.id.toString()}>
                                {emp.full_name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Selector de Equipo (si vista es team) */}
                    {selectedView === 'team' && (isAdmin() || isManager()) && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Equipo</label>
                        <Select 
                          value={selectedTeamId?.toString() || ''} 
                          onValueChange={(value) => setSelectedTeamId(parseInt(value))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccionar equipo" />
                          </SelectTrigger>
                          <SelectContent>
                            {teams.map(team => (
                              <SelectItem key={team.id} value={team.id.toString()}>
                                {team.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Selector de Período (lista desplegable) */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Período</label>
                      <Select 
                        value={`${currentYear}-${currentMonth.toString().padStart(2, '0')}`}
                        onValueChange={(value) => {
                          const [year, month] = value.split('-')
                          setCurrentYear(parseInt(year))
                          setCurrentMonth(parseInt(month))
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {/* Generar opciones para los últimos 12 meses */}
                          {Array.from({ length: 12 }, (_, i) => {
                            const date = new Date()
                            date.setMonth(date.getMonth() - i)
                            const year = date.getFullYear()
                            const month = date.getMonth() + 1
                            const monthName = monthNames[month - 1]
                            return (
                              <SelectItem key={`${year}-${month.toString().padStart(2, '0')}`} value={`${year}-${month.toString().padStart(2, '0')}`}>
                                {monthName} {year}
                              </SelectItem>
                            )
                          })}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </>
      )}

      {/* Contenido adicional del Forecast (desglose, tablas) */}
      {forecastData && (
        <div className="space-y-6">
          {/* Desglose de actividades */}

      {/* Contenido adicional del Forecast (desglose, tablas) */}
      {forecastData && (
        <div className="space-y-6">
          {/* Desglose de actividades */}
          {forecastData.breakdown && (
            <Card>
              <CardHeader>
                <CardTitle>Desglose de Actividades</CardTitle>
                <CardDescription>
                  Detalle de horas por tipo de actividad en el período seleccionado
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                      {forecastData.breakdown.vacation_days || 0}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Vacaciones</div>
                  </div>
                  <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">
                      {forecastData.breakdown.absence_days || 0}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Ausencias</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-green-700 dark:text-green-400">
                      {forecastData.breakdown.hld_hours || 0}h
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">HLD</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-purple-700 dark:text-purple-400">
                      {forecastData.breakdown.guard_hours || 0}h
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Guardias*</div>
                    <div className="text-xs text-gray-500 mt-1 italic">*Solo informativo</div>
                  </div>
                  <div className="text-center p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-700 dark:text-indigo-400">
                      {forecastData.breakdown.training_hours || 0}h
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Formación</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-gray-700 dark:text-gray-400">
                      {forecastData.breakdown.other_days || 0}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Otros</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tabla de empleados (si vista es team o global) */}
          {(selectedView === 'team' || selectedView === 'global') && forecastData.employees && (
            <Card>
              <CardHeader>
                <CardTitle>Empleados</CardTitle>
                <CardDescription>
                  {selectedView === 'team' ? 'Forecast por empleado del equipo' : 'Forecast de todos los empleados'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Empleado</TableHead>
                      <TableHead className="text-right">Horas Teóricas</TableHead>
                      <TableHead className="text-right">Horas Reales</TableHead>
                      <TableHead className="text-right">Eficiencia</TableHead>
                      <TableHead className="text-right">Valor Económico</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {forecastData.employees.map((emp) => (
                      <TableRow key={emp.employee_id}>
                        <TableCell className="font-medium">{emp.employee_name}</TableCell>
                        <TableCell className="text-right">{emp.theoretical_hours}h</TableCell>
                        <TableCell className="text-right">{emp.actual_hours}h</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <span>{emp.efficiency}%</span>
                            <Progress value={emp.efficiency} className="w-16 h-2" />
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          {emp.economic_value ? formatCurrency(emp.economic_value) : 'N/A'}
                        </TableCell>
                        <TableCell>{getPerformanceBadge(emp.performance_status)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Tabla de equipos (si vista es global) */}
          {selectedView === 'global' && forecastData.teams && (
            <Card>
              <CardHeader>
                <CardTitle>Equipos</CardTitle>
                <CardDescription>
                  Forecast consolidado por equipo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Equipo</TableHead>
                      <TableHead className="text-right">Empleados</TableHead>
                      <TableHead className="text-right">Horas Teóricas</TableHead>
                      <TableHead className="text-right">Horas Reales</TableHead>
                      <TableHead className="text-right">Eficiencia</TableHead>
                      <TableHead className="text-right">Valor Económico</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {forecastData.teams.map((team) => (
                      <TableRow key={team.team_id}>
                        <TableCell className="font-medium">{team.team_name}</TableCell>
                        <TableCell className="text-right">{team.employee_count}</TableCell>
                        <TableCell className="text-right">{team.total_theoretical_hours}h</TableCell>
                        <TableCell className="text-right">{team.total_actual_hours}h</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <span>{team.efficiency}%</span>
                            <Progress value={team.efficiency} className="w-16 h-2" />
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          {team.total_economic_value ? formatCurrency(team.total_economic_value) : 'N/A'}
                        </TableCell>
                        <TableCell>{getPerformanceBadge(team.performance_status)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        <Alert>
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>
            No se pudo cargar el forecast. Por favor, intenta de nuevo.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

export default ForecastPage

