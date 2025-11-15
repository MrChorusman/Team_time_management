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
      // TODO: Implementar carga real de datos de reportes desde el backend
      // Por ahora, mostrar estado vacío
      setReportData(null)
    } catch (error) {
      console.error('Error cargando datos de reportes:', error)
      setReportData(null)
    } finally {
      setLoading(false)
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

      {/* Estado vacío - sin datos mock */}
      {!reportData && !loading && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Reportes no disponibles
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                La funcionalidad de reportes estará disponible próximamente
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ReportsPage
