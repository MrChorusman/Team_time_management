import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Users, 
  Clock, 
  Calendar, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  BarChart3,
  PieChart,
  Activity,
  Target,
  HelpCircle
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useNotifications } from '../contexts/NotificationContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { StatsCard } from '../components/ui/stats-card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Progress } from '../components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Tooltip } from '../components/ui/tooltip'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/ui/collapsible'
import { ChevronDown, ChevronUp } from 'lucide-react'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const DashboardPage = () => {
  const navigate = useNavigate()
  const { user, employee, isAdmin, isManager, isEmployee } = useAuth()
  const { summary: notificationSummary } = useNotifications()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('current_month')

  useEffect(() => {
    loadDashboardData()
  }, [selectedPeriod])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // Obtener datos reales del backend
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/reports/dashboard`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.report) {
          // Transformar datos del backend al formato esperado por el frontend
          const report = data.report
          console.log('📊 Dashboard data recibida:', report) // Debug
          const transformedData = {
            type: report.dashboard_type || report.type || (isAdmin() ? 'admin' : 'manager'),
            statistics: report.statistics || {},
            team_performance: report.team_performance || (report.team_summaries || []).map(ts => ({
              team_name: ts.team?.name || 'Sin nombre',
              team_id: ts.team?.id,
              members_count: ts.summary?.employee_count || ts.team?.employee_count || 0,
              efficiency: ts.summary?.efficiency || 0
            })),
            pending_requests: report.pending_requests || [],
            recent_activity: report.recent_activity || [],
            alerts: report.alerts || []
          }
          console.log('📊 Dashboard data transformada:', transformedData) // Debug
          setDashboardData(transformedData)
        } else {
          console.warn('⚠️ Dashboard: respuesta sin report o success=false', data)
          setDashboardData(getEmptyDashboardData())
        }
      } else {
        // Si el endpoint no existe o hay error, mostrar dashboard vacío
        const errorText = await response.text()
        console.error('❌ Dashboard: Error en respuesta', response.status, errorText)
        setDashboardData(getEmptyDashboardData())
      }
    } catch (error) {
      console.error('Error cargando datos del dashboard:', error)
      // Mostrar dashboard vacío con mensaje apropiado
      setDashboardData(getEmptyDashboardData())
    } finally {
      setLoading(false)
    }
  }

  const getEmptyDashboardData = () => {
    // Datos vacíos reales según el rol del usuario
    if (isAdmin()) {
      return {
        type: 'admin',
        statistics: {
          total_employees: 0,
          total_teams: 0,
          pending_approvals: 0,
          global_efficiency: 0
        },
        recent_activity: [],
        team_performance: [],
        alerts: []
      }
    }
    
    if (isManager()) {
      return {
        type: 'manager',
        statistics: {
          team_members: 0,
          pending_approvals: 0,
          team_efficiency: 0,
          projects: 0
        },
        team_stats: {
          members: 0,
          efficiency: 0
        },
        recent_activity: [],
        alerts: [],
        pending_requests: [] // Asegurar que siempre existe como array
      }
    }
    
    return {
      type: 'employee',
      statistics: {
        hours_this_month: 0,
        efficiency: 0,
        vacation_days_left: 0,
        hld_hours_left: 0
      },
      monthly_summary: {
        theoretical_hours: 0,
        actual_hours: 0,
        efficiency: 0,
        days_worked: 0
      },
      recent_activity: [],
      alerts: []
    }
  }

  const _generateMockDashboardData_REMOVED = () => {
    if (isAdmin()) {
      return {
        type: 'admin',
        statistics: {
          total_employees: 156,
          total_teams: 12,
          pending_approvals: 8,
          global_efficiency: 87.5
        },
        recent_activity: [
          { type: 'employee_registration', description: 'Nuevo empleado: María García', timestamp: '2024-01-15T10:30:00Z' },
          { type: 'team_creation', description: 'Nuevo equipo: Frontend Development', timestamp: '2024-01-15T09:15:00Z' },
          { type: 'approval_request', description: 'Solicitud de aprobación pendiente', timestamp: '2024-01-15T08:45:00Z' }
        ],
        team_summaries: [
          { team: { name: 'Frontend Development', id: 1 }, summary: { average_efficiency: 92.3, employee_count: 8 } },
          { team: { name: 'Backend Development', id: 2 }, summary: { average_efficiency: 89.1, employee_count: 12 } },
          { team: { name: 'QA Testing', id: 3 }, summary: { average_efficiency: 85.7, employee_count: 6 } }
        ]
      }
    } else if (isManager()) {
      return {
        type: 'manager',
        statistics: {
          managed_teams: 2,
          total_employees: 15,
          pending_approvals: 3,
          average_efficiency: 89.2
        },
        team_summaries: [
          { 
            team: { name: 'Frontend Development', id: 1 }, 
            summary: { 
              average_efficiency: 92.3, 
              employee_count: 8,
              theoretical_hours: 320,
              actual_hours: 295,
              vacation_days: 12
            } 
          },
          { 
            team: { name: 'UI/UX Design', id: 2 }, 
            summary: { 
              average_efficiency: 86.1, 
              employee_count: 7,
              theoretical_hours: 280,
              actual_hours: 241,
              vacation_days: 8
            } 
          }
        ],
        pending_requests: [
          { employee: 'Juan Pérez', type: 'vacation', dates: '2024-01-20 - 2024-01-25' },
          { employee: 'Ana López', type: 'approval', description: 'Registro de empleado' },
          { employee: 'Carlos Ruiz', type: 'calendar_change', description: 'Modificación de horario' }
        ]
      }
    } else if (isEmployee()) {
      return {
        type: 'employee',
        employee_data: {
          full_name: employee?.full_name || 'Usuario',
          team: employee?.team?.name || 'Sin equipo',
          approved: employee?.approved || false
        },
        monthly_summary: {
          theoretical_hours: 160,
          actual_hours: 148,
          efficiency: 92.5,
          vacation_days: 2,
          absence_days: 1,
          hld_hours: 8,
          guard_hours: 0
        },
        annual_summary: {
          total_theoretical_hours: 1920,
          total_actual_hours: 1756,
          total_efficiency: 91.4,
          total_vacation_days: 18,
          remaining_vacation_days: 7,
          total_hld_hours: 64,
          remaining_hld_hours: 16
        },
        team_summary: {
          team_name: 'Frontend Development',
          average_efficiency: 89.2,
          employee_count: 8,
          team_ranking: 2
        }
      }
    }
    
    // Usuario sin employee
    if (!employee) {
      // Admins pueden acceder al dashboard completo sin employee
      if (isAdmin()) {
        return {
          type: 'admin',
          message: 'Panel de administración - Gestiona el sistema sin necesidad de perfil de empleado'
        }
      }
      
      // Otros usuarios sin employee son viewers
      return {
        type: 'viewer',
        message: 'Completa tu registro de empleado para acceder al dashboard completo'
      }
    }
    
    // Employee registrado pero pendiente de aprobación
    return {
      type: 'pending',
      message: 'Tu registro está pendiente de aprobación. Podrás acceder a todas las funcionalidades una vez que tu manager lo apruebe.'
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Buenos días'
    if (hour < 18) return 'Buenas tardes'
    return 'Buenas noches'
  }

  const getUserDisplayName = () => {
    // Prioridad 1: Nombre completo del empleado
    if (employee?.full_name) {
      return employee.full_name.split(' ')[0]
    }
    // Prioridad 2: first_name del user
    if (user?.first_name) {
      return user.first_name
    }
    // Prioridad 3: Extraer nombre del email antes de @
    if (user?.email) {
      const emailName = user.email.split('@')[0]
      // Capitalizar primera letra
      return emailName.charAt(0).toUpperCase() + emailName.slice(1)
    }
    return 'Usuario'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">Cargando información...</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <StatsCard key={i} loading={true} />
          ))}
        </div>
        
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando dashboard..." />
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Error cargando los datos del dashboard. Por favor, recarga la página.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  // Dashboard para Administradores
  if (dashboardData.type === 'admin') {
    return (
      <div className="w-full space-y-8 px-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              {getGreeting()}, {getUserDisplayName()}
            </h1>
            <p className="text-lg text-gray-700 dark:text-gray-300">
              Vista general del sistema
            </p>
          </div>
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 px-4 py-2">
            Administrador
          </Badge>
        </div>

        {/* Quick Actions para sistema vacío - PRIMERO */}
        {dashboardData.statistics.total_employees === 0 && (
          <Alert className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
            <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <AlertDescription className="text-blue-900 dark:text-blue-100">
              <p className="font-bold text-lg mb-2">¡Comienza configurando tu sistema!</p>
              <p className="text-sm mb-4 text-blue-700 dark:text-blue-300">
                Añade empleados y crea equipos para empezar a gestionar el tiempo de tu organización
              </p>
              <div className="flex gap-3">
                <Button 
                  size="sm" 
                  onClick={() => navigate('/employees')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Añadir Primer Empleado
                </Button>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => navigate('/teams')}
                  className="border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30"
                >
                  <Target className="w-4 h-4 mr-2" />
                  Crear Equipo
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Métricas principales con botones de consulta - Diseño compacto */}
        <div className="flex flex-wrap gap-4">
          {/* Total Empleados */}
          <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Total Empleados
              </CardTitle>
              <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                {dashboardData.statistics.total_employees}
              </div>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => navigate('/employees')}
                className="w-full"
              >
                Consultar
              </Button>
            </CardContent>
          </Card>

          {/* Equipos Activos */}
          <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Equipos Activos
              </CardTitle>
              <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                {dashboardData.statistics.total_teams}
              </div>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => navigate('/teams')}
                className="w-full"
              >
                Consultar
              </Button>
            </CardContent>
          </Card>

          {/* Aprobaciones Pendientes */}
          <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Aprobaciones Pendientes
              </CardTitle>
              <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                {dashboardData.statistics.pending_approvals}
              </div>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => navigate('/employees')}
                className="w-full"
              >
                Consultar
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Actividad Reciente y Eficiencia Global */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Actividad reciente */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Actividad Reciente
              </CardTitle>
              <CardDescription>
                Últimas acciones en el sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData.recent_activity && dashboardData.recent_activity.length > 0 ? (
                  dashboardData.recent_activity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {activity.message || activity.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {activity.timestamp ? new Date(activity.timestamp).toLocaleString('es-ES') : ''}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <Activity className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <p className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Sin actividad reciente
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Las acciones del sistema aparecerán aquí
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Eficiencia Global */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Eficiencia Global
                <Tooltip content="Se calcula como: (Horas trabajadas / Horas esperadas) × 100. Incluye horas regulares, guardias y descuenta ausencias." className="left-auto right-0 translate-x-0">
                  <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-help" />
                </Tooltip>
              </CardTitle>
              <CardDescription>
                Promedio del mes actual
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <div className="text-5xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData.statistics.global_efficiency}%
                </div>
                <Badge 
                  variant="outline" 
                  className="text-sm font-semibold text-green-600 dark:text-green-400"
                >
                  ↗ +2.3%
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Dashboard para Managers
  if (dashboardData.type === 'manager') {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {getGreeting()}, {getUserDisplayName()}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Panel de gestión - Tus equipos y empleados
            </p>
          </div>
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            Manager
          </Badge>
        </div>

        {/* Estadísticas principales - Listas desplegables - Diseño compacto */}
        <div className="flex flex-wrap gap-4">
          {/* Equipos Gestionados */}
          <Collapsible>
            <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
              <CollapsibleTrigger className="w-full">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Equipos Gestionados
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <Target className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <ChevronDown className="h-3 w-3 text-gray-400" />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CardContent className="pt-2">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData.statistics?.managed_teams || 0}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                  Bajo tu supervisión
                </p>
                <CollapsibleContent>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {dashboardData.team_performance && dashboardData.team_performance.length > 0 ? (
                      dashboardData.team_performance.map((team, index) => (
                        <div key={index} className="flex items-center justify-between text-xs py-1">
                          <span className="text-gray-600 dark:text-gray-400 truncate flex-1 mr-2">{team.team_name}</span>
                          <Badge variant="outline" className="text-xs px-1.5 py-0">{team.members_count} miembros</Badge>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-gray-500 dark:text-gray-400">No hay equipos asignados</p>
                    )}
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => navigate('/teams')}
                      className="w-full mt-2 text-xs"
                    >
                      Ver todos los equipos
                    </Button>
                  </div>
                </CollapsibleContent>
              </CardContent>
            </Card>
          </Collapsible>

          {/* Total Empleados */}
          <Collapsible>
            <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
              <CollapsibleTrigger className="w-full">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Total Empleados
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <Users className="h-4 w-4 text-green-600 dark:text-green-400" />
                    </div>
                    <ChevronDown className="h-3 w-3 text-gray-400" />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CardContent className="pt-2">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData.statistics?.total_employees || 0}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                  En tus equipos
                </p>
                <CollapsibleContent>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {dashboardData.team_performance && dashboardData.team_performance.length > 0 ? (
                      dashboardData.team_performance.map((team, index) => (
                        <div key={index} className="flex items-center justify-between text-xs py-1">
                          <span className="text-gray-600 dark:text-gray-400 truncate flex-1 mr-2">{team.team_name}</span>
                          <span className="font-medium text-xs">{team.members_count} empleados</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-gray-500 dark:text-gray-400">No hay empleados asignados</p>
                    )}
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => navigate('/employees')}
                      className="w-full mt-2 text-xs"
                    >
                      Ver todos los empleados
                    </Button>
                  </div>
                </CollapsibleContent>
              </CardContent>
            </Card>
          </Collapsible>

          {/* Aprobaciones Pendientes */}
          <Collapsible>
            <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
              <CollapsibleTrigger className="w-full">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Aprobaciones Pendientes
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                      <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <ChevronDown className="h-3 w-3 text-gray-400" />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CardContent className="pt-2">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData.statistics?.pending_approvals || 0}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                  Requieren tu atención
                </p>
                <CollapsibleContent>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    {(dashboardData.pending_requests || []).length > 0 ? (
                      <div className="space-y-2">
                        {(dashboardData.pending_requests || []).slice(0, 5).map((request, index) => (
                          <div key={index} className="text-xs p-2 bg-yellow-50 dark:bg-yellow-900/10 rounded">
                            <p className="font-medium text-gray-900 dark:text-white text-xs">{request.employee}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {request.type === 'vacation' && `Vacaciones: ${request.dates}`}
                              {request.type === 'approval' && request.description}
                              {request.type === 'calendar_change' && request.description}
                            </p>
                          </div>
                        ))}
                        {(dashboardData.pending_requests || []).length > 5 && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                            +{(dashboardData.pending_requests || []).length - 5} más
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500 dark:text-gray-400">No hay aprobaciones pendientes</p>
                    )}
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => navigate('/employees')}
                      className="w-full mt-2 text-xs"
                    >
                      Revisar todas
                    </Button>
                  </div>
                </CollapsibleContent>
              </CardContent>
            </Card>
          </Collapsible>

          {/* Eficiencia Promedio */}
          <Collapsible>
            <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
              <CollapsibleTrigger className="w-full">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Eficiencia Promedio
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <TrendingUp className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                    </div>
                    <ChevronDown className="h-3 w-3 text-gray-400" />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CardContent className="pt-2">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData.statistics?.average_efficiency || 0}%
                </div>
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    De tus equipos
                  </p>
                  <Badge variant="outline" className="text-xs font-semibold text-green-600 px-1.5 py-0">
                    ↗ +1.8%
                  </Badge>
                </div>
                <CollapsibleContent>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {dashboardData.team_performance && dashboardData.team_performance.length > 0 ? (
                      dashboardData.team_performance.map((team, index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-600 dark:text-gray-400 truncate flex-1 mr-2">{team.team_name}</span>
                            <span className="font-medium text-xs">{team.efficiency || 0}%</span>
                          </div>
                          <Progress value={team.efficiency || 0} className="h-1.5" />
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-gray-500 dark:text-gray-400">No hay datos de eficiencia</p>
                    )}
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => navigate('/reports')}
                      className="w-full mt-2 text-xs"
                    >
                      Ver reportes
                    </Button>
                  </div>
                </CollapsibleContent>
              </CardContent>
            </Card>
          </Collapsible>
        </div>

        {/* Contenido principal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Equipos gestionados */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Mis Equipos
              </CardTitle>
              <CardDescription>
                Resumen de rendimiento de tus equipos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {dashboardData.team_performance && dashboardData.team_performance.length > 0 ? (
                  dashboardData.team_performance.map((teamData, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {teamData.team_name}
                        </h4>
                        <Badge variant="outline">
                          {teamData.members_count} empleados
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Eficiencia</p>
                          <p className="font-medium">{teamData.efficiency}%</p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Miembros</p>
                          <p className="font-medium">{teamData.members_count}</p>
                        </div>
                      </div>
                      
                      <Progress value={teamData.efficiency} className="h-2 mt-3" />
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <p className="text-sm">No hay equipos con datos</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Solicitudes pendientes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Solicitudes Pendientes
              </CardTitle>
              <CardDescription>
                Acciones que requieren tu aprobación
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(dashboardData.pending_requests || []).map((request, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {request.employee}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {request.type === 'vacation' && `Vacaciones: ${request.dates}`}
                        {request.type === 'approval' && request.description}
                        {request.type === 'calendar_change' && request.description}
                      </p>
                    </div>
                    <Button size="sm" variant="outline">
                      Revisar
                    </Button>
                  </div>
                ))}
                {(!dashboardData.pending_requests || dashboardData.pending_requests.length === 0) && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                    No hay solicitudes pendientes
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Dashboard para Empleados
  if (dashboardData.type === 'employee') {
    // Si el empleado está pendiente de aprobación, mostrar mensaje y no cargar datos
    if (dashboardData?.employee_data && dashboardData.employee_data.approved === false) {
      return (
        <div className="w-full space-y-8 px-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {getGreeting()}, {getUserDisplayName()}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Tu registro está pendiente de aprobación
              </p>
            </div>
          </div>

          {/* Mensaje de estado pendiente */}
          <Alert variant="warning" className="border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20">
            <AlertCircle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800 dark:text-yellow-200">
              <p className="font-semibold mb-2">Tu registro está pendiente de aprobación</p>
              <p className="text-sm">
                Tu manager revisará tu solicitud y recibirás un email cuando tu cuenta sea aprobada. 
                Una vez aprobado, podrás acceder a todas las funcionalidades de la aplicación.
              </p>
            </AlertDescription>
          </Alert>

          {/* Información básica */}
          <Card>
            <CardHeader>
              <CardTitle>Información de tu Registro</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Nombre:</span>
                <span className="font-medium">{dashboardData.employee_data?.full_name || 'N/A'}</span>
              </div>
              {dashboardData.employee_data?.team && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Equipo:</span>
                  <Badge variant="secondary">{dashboardData.employee_data.team}</Badge>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Estado:</span>
                <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
                  <Clock className="w-3 h-3 mr-1" />
                  Pendiente de Aprobación
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {getGreeting()}, {getUserDisplayName()}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Tu resumen personal de tiempo y actividades
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              Empleado
            </Badge>
            {dashboardData?.employee_data?.team && (
              <Badge variant="secondary">
                {dashboardData.employee_data.team}
              </Badge>
            )}
          </div>
        </div>

        {/* Pestañas de resumen */}
        <Tabs defaultValue="monthly" className="space-y-6">
          <TabsList>
            <TabsTrigger value="monthly">Resumen Mensual</TabsTrigger>
            <TabsTrigger value="annual">Resumen Anual</TabsTrigger>
          </TabsList>

          {/* Resumen mensual */}
          <TabsContent value="monthly" className="space-y-6">
            <div className="flex flex-wrap gap-4">
              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Horas Reales
                  </CardTitle>
                  <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Clock className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.monthly_summary?.actual_hours || 0}h
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    de {dashboardData.monthly_summary?.theoretical_hours || 0}h teóricas
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/calendar')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Eficiencia
                  </CardTitle>
                  <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.monthly_summary?.efficiency || 0}%
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Este mes
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/reports')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Días de Vacaciones
                  </CardTitle>
                  <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <Calendar className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.monthly_summary?.vacation_days || 0}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Utilizados este mes
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/calendar')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Horas HLD
                  </CardTitle>
                  <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.monthly_summary?.hld_hours || 0}h
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Horas de libre disposición
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/calendar')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Progreso mensual */}
            <Card>
              <CardHeader>
                <CardTitle>Progreso del Mes</CardTitle>
                <CardDescription>
                  Tu rendimiento comparado con el objetivo mensual
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Horas Completadas</span>
                      <span className="text-sm text-gray-500">
                        {dashboardData.monthly_summary?.actual_hours || 0} / {dashboardData.monthly_summary?.theoretical_hours || 0}h
                      </span>
                    </div>
                    <Progress 
                      value={dashboardData.monthly_summary?.theoretical_hours 
                        ? ((dashboardData.monthly_summary.actual_hours || 0) / dashboardData.monthly_summary.theoretical_hours) * 100 
                        : 0} 
                      className="h-3" 
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Resumen anual */}
          <TabsContent value="annual" className="space-y-6">
            <div className="flex flex-wrap gap-4">
              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Horas Totales
                  </CardTitle>
                  <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Clock className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.annual_summary?.total_actual_hours || 0}h
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    de {dashboardData.annual_summary?.total_theoretical_hours || 0}h anuales
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/reports')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Eficiencia Anual
                  </CardTitle>
                  <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.annual_summary?.total_efficiency || 0}%
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Promedio del año
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/reports')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Vacaciones Restantes
                  </CardTitle>
                  <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <Calendar className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.annual_summary?.remaining_vacation_days || 0}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    de {dashboardData.annual_summary?.total_vacation_days || 0} anuales
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/calendar')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow flex-shrink-0" style={{ minWidth: '200px', maxWidth: '280px' }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    HLD Restantes
                  </CardTitle>
                  <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-gray-900 dark:text-white mb-1">
                    {dashboardData.annual_summary?.remaining_hld_hours || 0}h
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    de {dashboardData.annual_summary?.total_hld_hours || 0}h anuales
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigate('/calendar')}
                    className="w-full"
                  >
                    Consultar
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Información del equipo */}
        {dashboardData.team_summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Mi Equipo: {dashboardData.team_summary?.team_name || 'Sin equipo'}
              </CardTitle>
              <CardDescription>
                Rendimiento de tu equipo comparado con otros
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {dashboardData.team_summary?.average_efficiency || 0}%
                  </p>
                  <p className="text-sm text-gray-500">Eficiencia del equipo</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    #{dashboardData.team_summary?.team_ranking || 0}
                  </p>
                  <p className="text-sm text-gray-500">Ranking general</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {dashboardData.team_summary?.employee_count || 0}
                  </p>
                  <p className="text-sm text-gray-500">Miembros del equipo</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  // Dashboard para Viewers (sin empleado registrado)
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 bg-gray-300 rounded-full flex items-center justify-center mb-4">
          <Users className="h-6 w-6 text-gray-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Bienvenido a Team Time Management
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          {dashboardData.message}
        </p>
        {/* Solo mostrar el botón si NO tiene employee (viewer) */}
        {dashboardData.type === 'viewer' && (
          <Button onClick={() => navigate('/employee/register')}>
            Completar Registro de Empleado
          </Button>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
