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
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/dashboard/stats`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        // Si el endpoint no existe o hay error, mostrar dashboard vacío
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
        alerts: []
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

        {/* Métricas principales con botones de consulta */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Empleados */}
          <Card className="hover:shadow-md transition-shadow">
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
          <Card className="hover:shadow-md transition-shadow">
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
          <Card className="hover:shadow-md transition-shadow">
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

        {/* Estadísticas principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Equipos Gestionados"
            value={dashboardData.statistics.managed_teams}
            subtitle="Bajo tu supervisión"
            icon={Target}
            variant="info"
          />
          <StatsCard
            title="Total Empleados"
            value={dashboardData.statistics.total_employees}
            subtitle="En tus equipos"
            icon={Users}
            variant="success"
          />
          <StatsCard
            title="Aprobaciones Pendientes"
            value={dashboardData.statistics.pending_approvals}
            subtitle="Requieren tu atención"
            icon={AlertCircle}
            variant="warning"
          />
          <StatsCard
            title="Eficiencia Promedio"
            value={`${dashboardData.statistics.average_efficiency}%`}
            subtitle="De tus equipos"
            icon={TrendingUp}
            trend="up"
            trendValue="+1.8%"
          />
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
                {dashboardData.pending_requests.map((request, index) => (
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
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Dashboard para Empleados
  if (dashboardData.type === 'employee') {
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
            {dashboardData.employee_data.team && (
              <Badge variant="secondary">
                {dashboardData.employee_data.team}
              </Badge>
            )}
          </div>
        </div>

        {/* Estado de aprobación */}
        {!dashboardData.employee_data.approved && (
          <Alert variant="warning">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Tu registro está pendiente de aprobación por tu manager. Algunas funcionalidades pueden estar limitadas.
            </AlertDescription>
          </Alert>
        )}

        {/* Pestañas de resumen */}
        <Tabs defaultValue="monthly" className="space-y-6">
          <TabsList>
            <TabsTrigger value="monthly">Resumen Mensual</TabsTrigger>
            <TabsTrigger value="annual">Resumen Anual</TabsTrigger>
          </TabsList>

          {/* Resumen mensual */}
          <TabsContent value="monthly" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="Horas Reales"
                value={`${dashboardData.monthly_summary.actual_hours}h`}
                subtitle={`de ${dashboardData.monthly_summary.theoretical_hours}h teóricas`}
                icon={Clock}
                variant="info"
              />
              <StatsCard
                title="Eficiencia"
                value={`${dashboardData.monthly_summary.efficiency}%`}
                subtitle="Este mes"
                icon={TrendingUp}
                trend="up"
                trendValue="+3.2%"
                variant="success"
              />
              <StatsCard
                title="Días de Vacaciones"
                value={dashboardData.monthly_summary.vacation_days}
                subtitle="Utilizados este mes"
                icon={Calendar}
                variant="warning"
              />
              <StatsCard
                title="Horas HLD"
                value={`${dashboardData.monthly_summary.hld_hours}h`}
                subtitle="Horas de libre disposición"
                icon={Activity}
              />
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
                        {dashboardData.monthly_summary.actual_hours} / {dashboardData.monthly_summary.theoretical_hours}h
                      </span>
                    </div>
                    <Progress 
                      value={(dashboardData.monthly_summary.actual_hours / dashboardData.monthly_summary.theoretical_hours) * 100} 
                      className="h-3" 
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Resumen anual */}
          <TabsContent value="annual" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="Horas Totales"
                value={`${dashboardData.annual_summary.total_actual_hours}h`}
                subtitle={`de ${dashboardData.annual_summary.total_theoretical_hours}h anuales`}
                icon={Clock}
                variant="info"
              />
              <StatsCard
                title="Eficiencia Anual"
                value={`${dashboardData.annual_summary.total_efficiency}%`}
                subtitle="Promedio del año"
                icon={TrendingUp}
                variant="success"
              />
              <StatsCard
                title="Vacaciones Restantes"
                value={dashboardData.annual_summary.remaining_vacation_days}
                subtitle={`de ${dashboardData.annual_summary.total_vacation_days} anuales`}
                icon={Calendar}
                variant="warning"
              />
              <StatsCard
                title="HLD Restantes"
                value={`${dashboardData.annual_summary.remaining_hld_hours}h`}
                subtitle={`de ${dashboardData.annual_summary.total_hld_hours}h anuales`}
                icon={Activity}
              />
            </div>
          </TabsContent>
        </Tabs>

        {/* Información del equipo */}
        {dashboardData.team_summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Mi Equipo: {dashboardData.team_summary.team_name}
              </CardTitle>
              <CardDescription>
                Rendimiento de tu equipo comparado con otros
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {dashboardData.team_summary.average_efficiency}%
                  </p>
                  <p className="text-sm text-gray-500">Eficiencia del equipo</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    #{dashboardData.team_summary.team_ranking}
                  </p>
                  <p className="text-sm text-gray-500">Ranking general</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {dashboardData.team_summary.employee_count}
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
