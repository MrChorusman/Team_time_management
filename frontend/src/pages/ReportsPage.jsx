import { useState, useEffect } from 'react'
import { 
  BarChart3, 
  Download, 
  Filter,
  Calendar,
  TrendingUp,
  Users,
  Clock,
  Target,
  FileText,
  PieChart,
  Activity,
  Award
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { StatsCard } from '../components/ui/stats-card'
import { Progress } from '../components/ui/progress'
import { Badge } from '../components/ui/badge'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const ReportsPage = () => {
  const { user, isAdmin, isManager, isEmployee } = useAuth()
  const [loading, setLoading] = useState(true)
  const [reportData, setReportData] = useState(null)
  const [selectedPeriod, setSelectedPeriod] = useState('current_month')
  const [selectedTeam, setSelectedTeam] = useState('all')
  const [selectedReport, setSelectedReport] = useState('efficiency')

  useEffect(() => {
    loadReportData()
  }, [selectedPeriod, selectedTeam, selectedReport])

  const loadReportData = async () => {
    setLoading(true)
    try {
      // Simular carga de datos de reportes
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = generateMockReportData()
      setReportData(mockData)
    } catch (error) {
      console.error('Error cargando datos de reportes:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockReportData = () => {
    return {
      summary: {
        total_employees: 35,
        total_teams: 5,
        total_hours_theoretical: 5600,
        total_hours_actual: 5124,
        global_efficiency: 91.5,
        total_vacation_days: 48,
        total_hld_hours: 140
      },
      efficiency_report: {
        by_team: [
          { team: 'Frontend Development', efficiency: 92.3, employees: 8, hours: 1182 },
          { team: 'Backend Development', efficiency: 89.1, employees: 12, hours: 1711 },
          { team: 'DevOps', efficiency: 91.8, employees: 4, hours: 587 },
          { team: 'QA Testing', efficiency: 85.7, employees: 6, hours: 823 },
          { team: 'UI/UX Design', efficiency: 88.4, employees: 5, hours: 707 }
        ],
        by_month: [
          { month: 'Enero', efficiency: 89.2, hours: 5200 },
          { month: 'Febrero', efficiency: 90.1, hours: 4800 },
          { month: 'Marzo', efficiency: 91.5, hours: 5400 },
          { month: 'Abril', efficiency: 88.7, hours: 5100 },
          { month: 'Mayo', efficiency: 92.3, hours: 5600 },
          { month: 'Junio', efficiency: 90.8, hours: 5300 }
        ],
        trends: {
          efficiency_trend: '+2.3%',
          hours_trend: '+5.1%',
          productivity_trend: '+1.8%'
        }
      },
      time_report: {
        distribution: {
          work_hours: 85.2,
          vacation_hours: 8.6,
          hld_hours: 2.5,
          sick_leave: 2.1,
          training: 1.6
        },
        overtime: {
          total_overtime_hours: 124,
          employees_with_overtime: 12,
          average_overtime_per_employee: 10.3
        }
      },
      vacation_report: {
        by_team: [
          { team: 'Frontend Development', used: 12, remaining: 76, total: 88 },
          { team: 'Backend Development', used: 18, remaining: 102, total: 120 },
          { team: 'QA Testing', used: 8, remaining: 52, total: 60 },
          { team: 'UI/UX Design', used: 6, remaining: 44, total: 50 },
          { team: 'DevOps', used: 4, remaining: 36, total: 40 }
        ],
        upcoming: [
          { employee: 'Juan Pérez', team: 'Frontend', dates: '2024-02-15 - 2024-02-20', days: 5 },
          { employee: 'María García', team: 'Backend', dates: '2024-02-22 - 2024-02-26', days: 5 },
          { employee: 'Carlos López', team: 'QA', dates: '2024-03-01 - 2024-03-05', days: 5 }
        ]
      },
      productivity_report: {
        top_performers: [
          { employee: 'Ana Martín', team: 'Frontend', efficiency: 97.2, hours: 156 },
          { employee: 'Luis Rodríguez', team: 'Backend', efficiency: 96.8, hours: 158 },
          { employee: 'Carmen Sánchez', team: 'DevOps', efficiency: 95.4, hours: 152 },
          { employee: 'David González', team: 'QA', efficiency: 94.1, hours: 149 },
          { employee: 'Laura Fernández', team: 'UI/UX', efficiency: 93.7, hours: 147 }
        ],
        team_rankings: [
          { position: 1, team: 'Frontend Development', score: 92.3 },
          { position: 2, team: 'DevOps', score: 91.8 },
          { position: 3, team: 'Backend Development', score: 89.1 },
          { position: 4, team: 'UI/UX Design', score: 88.4 },
          { position: 5, team: 'QA Testing', score: 85.7 }
        ]
      }
    }
  }

  const exportReport = (format) => {
    // Simular exportación
    console.log(`Exportando reporte en formato ${format}`)
    // Aquí iría la lógica real de exportación
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Reportes</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Generando reportes..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Reportes y Análisis</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Análisis detallado del rendimiento y métricas del equipo
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => exportReport('pdf')}>
            <Download className="w-4 h-4 mr-2" />
            Exportar PDF
          </Button>
          <Button variant="outline" onClick={() => exportReport('csv')}>
            <Download className="w-4 h-4 mr-2" />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-48">
                <Calendar className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Período" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="current_month">Mes Actual</SelectItem>
                <SelectItem value="last_month">Mes Anterior</SelectItem>
                <SelectItem value="current_quarter">Trimestre Actual</SelectItem>
                <SelectItem value="current_year">Año Actual</SelectItem>
                <SelectItem value="custom">Personalizado</SelectItem>
              </SelectContent>
            </Select>
            
            {(isAdmin() || isManager()) && (
              <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                <SelectTrigger className="w-48">
                  <Users className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Equipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los Equipos</SelectItem>
                  <SelectItem value="frontend">Frontend Development</SelectItem>
                  <SelectItem value="backend">Backend Development</SelectItem>
                  <SelectItem value="qa">QA Testing</SelectItem>
                  <SelectItem value="design">UI/UX Design</SelectItem>
                  <SelectItem value="devops">DevOps</SelectItem>
                </SelectContent>
              </Select>
            )}
            
            <Select value={selectedReport} onValueChange={setSelectedReport}>
              <SelectTrigger className="w-48">
                <BarChart3 className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Tipo de Reporte" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="efficiency">Eficiencia</SelectItem>
                <SelectItem value="time">Tiempo</SelectItem>
                <SelectItem value="vacation">Vacaciones</SelectItem>
                <SelectItem value="productivity">Productividad</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Resumen general */}
      {reportData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Empleados Totales"
            value={reportData.summary.total_employees}
            subtitle="Activos en el período"
            icon={Users}
            variant="info"
          />
          <StatsCard
            title="Eficiencia Global"
            value={`${reportData.summary.global_efficiency}%`}
            subtitle="Promedio general"
            icon={TrendingUp}
            trend="up"
            trendValue="+2.3%"
            variant="success"
          />
          <StatsCard
            title="Horas Trabajadas"
            value={`${reportData.summary.total_hours_actual}h`}
            subtitle={`de ${reportData.summary.total_hours_theoretical}h teóricas`}
            icon={Clock}
            variant="warning"
          />
          <StatsCard
            title="Días de Vacaciones"
            value={reportData.summary.total_vacation_days}
            subtitle="Utilizados en el período"
            icon={Calendar}
          />
        </div>
      )}

      {/* Contenido de reportes */}
      <Tabs defaultValue="efficiency" className="space-y-6">
        <TabsList>
          <TabsTrigger value="efficiency">Eficiencia</TabsTrigger>
          <TabsTrigger value="time">Tiempo</TabsTrigger>
          <TabsTrigger value="vacation">Vacaciones</TabsTrigger>
          <TabsTrigger value="productivity">Productividad</TabsTrigger>
        </TabsList>

        {/* Reporte de Eficiencia */}
        <TabsContent value="efficiency" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Eficiencia por Equipo
                </CardTitle>
                <CardDescription>
                  Rendimiento comparativo de los equipos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reportData?.efficiency_report.by_team.map((team, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{team.team}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">{team.employees} empleados</span>
                          <span className="text-sm font-medium">{team.efficiency}%</span>
                        </div>
                      </div>
                      <Progress value={team.efficiency} className="h-2" />
                      <p className="text-xs text-gray-500">{team.hours}h trabajadas</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Tendencias Mensuales
                </CardTitle>
                <CardDescription>
                  Evolución de la eficiencia en el tiempo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reportData?.efficiency_report.by_month.slice(-3).map((month, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{month.month}</p>
                        <p className="text-sm text-gray-500">{month.hours}h</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{month.efficiency}%</p>
                        <Badge variant="outline" className="text-xs">
                          {index === 2 ? '+1.4%' : index === 1 ? '+0.8%' : '-0.6%'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Indicadores Clave</CardTitle>
              <CardDescription>
                Métricas principales de rendimiento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {reportData?.efficiency_report.trends.efficiency_trend}
                  </p>
                  <p className="text-sm text-gray-500">Mejora en eficiencia</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {reportData?.efficiency_report.trends.hours_trend}
                  </p>
                  <p className="text-sm text-gray-500">Incremento en horas</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">
                    {reportData?.efficiency_report.trends.productivity_trend}
                  </p>
                  <p className="text-sm text-gray-500">Mejora en productividad</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reporte de Tiempo */}
        <TabsContent value="time" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PieChart className="w-5 h-5 mr-2" />
                  Distribución de Tiempo
                </CardTitle>
                <CardDescription>
                  Cómo se distribuyen las horas trabajadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(reportData?.time_report.distribution || {}).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm capitalize">
                          {key.replace('_', ' ')}
                        </span>
                        <span className="text-sm font-medium">{value}%</span>
                      </div>
                      <Progress value={value} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Horas Extra
                </CardTitle>
                <CardDescription>
                  Análisis de tiempo adicional trabajado
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-orange-600">
                      {reportData?.time_report.overtime.total_overtime_hours}h
                    </p>
                    <p className="text-sm text-gray-500">Total horas extra</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <p className="text-xl font-bold">
                        {reportData?.time_report.overtime.employees_with_overtime}
                      </p>
                      <p className="text-xs text-gray-500">Empleados con horas extra</p>
                    </div>
                    <div>
                      <p className="text-xl font-bold">
                        {reportData?.time_report.overtime.average_overtime_per_employee}h
                      </p>
                      <p className="text-xs text-gray-500">Promedio por empleado</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Reporte de Vacaciones */}
        <TabsContent value="vacation" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Vacaciones por Equipo
                </CardTitle>
                <CardDescription>
                  Estado de vacaciones por equipo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reportData?.vacation_report.by_team.map((team, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-medium">{team.team}</h4>
                        <Badge variant="outline">{team.total} días totales</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Utilizados</p>
                          <p className="font-medium text-red-600">{team.used} días</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Restantes</p>
                          <p className="font-medium text-green-600">{team.remaining} días</p>
                        </div>
                      </div>
                      <Progress value={(team.used / team.total) * 100} className="h-2 mt-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Próximas Vacaciones
                </CardTitle>
                <CardDescription>
                  Vacaciones programadas próximamente
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {reportData?.vacation_report.upcoming.map((vacation, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{vacation.employee}</p>
                        <p className="text-sm text-gray-500">{vacation.team}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{vacation.dates}</p>
                        <Badge variant="outline">{vacation.days} días</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Reporte de Productividad */}
        <TabsContent value="productivity" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="w-5 h-5 mr-2" />
                  Top Performers
                </CardTitle>
                <CardDescription>
                  Empleados con mejor rendimiento
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {reportData?.productivity_report.top_performers.map((performer, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium">{performer.employee}</p>
                          <p className="text-sm text-gray-500">{performer.team}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{performer.efficiency}%</p>
                        <p className="text-sm text-gray-500">{performer.hours}h</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Ranking de Equipos
                </CardTitle>
                <CardDescription>
                  Posicionamiento por rendimiento
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {reportData?.productivity_report.team_rankings.map((team, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                          team.position === 1 ? 'bg-yellow-500' :
                          team.position === 2 ? 'bg-gray-400' :
                          team.position === 3 ? 'bg-orange-600' : 'bg-gray-600'
                        }`}>
                          {team.position}
                        </div>
                        <p className="font-medium">{team.team}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{team.score}%</p>
                        <Badge variant="outline">
                          {team.position === 1 ? '🥇' : team.position === 2 ? '🥈' : team.position === 3 ? '🥉' : ''}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ReportsPage
