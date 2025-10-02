import { useState, useEffect } from 'react'
import { 
  Settings, 
  Users, 
  Database, 
  Shield, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  Upload,
  Trash2,
  RefreshCw,
  Server,
  Mail,
  Globe,
  HardDrive,
  Cpu,
  BarChart3
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { StatsCard } from '../components/ui/stats-card'
import { Progress } from '../components/ui/progress'
import { Switch } from '../components/ui/switch'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { Alert, AlertDescription } from '../components/ui/alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const AdminPage = () => {
  const { user, isAdmin } = useAuth()
  const [loading, setLoading] = useState(true)
  const [systemData, setSystemData] = useState(null)
  const [systemSettings, setSystemSettings] = useState({
    maintenance_mode: false,
    user_registration: true,
    email_notifications: true,
    automatic_backups: true,
    holiday_sync: true,
    max_vacation_days: 25,
    max_hld_hours: 80,
    summer_hours: 7
  })

  useEffect(() => {
    if (!isAdmin()) {
      // Redirigir si no es admin
      return
    }
    loadSystemData()
  }, [])

  const loadSystemData = async () => {
    setLoading(true)
    try {
      // Simular carga de datos del sistema
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = generateMockSystemData()
      setSystemData(mockData)
    } catch (error) {
      console.error('Error cargando datos del sistema:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockSystemData = () => {
    return {
      system_stats: {
        total_users: 42,
        active_users: 35,
        total_teams: 5,
        pending_approvals: 3,
        system_uptime: '99.9%',
        database_size: '2.3 GB',
        last_backup: '2024-01-15T02:00:00Z',
        cpu_usage: 23.5,
        memory_usage: 67.2,
        disk_usage: 45.8
      },
      recent_activities: [
        {
          id: 1,
          type: 'user_registration',
          description: 'Nuevo usuario registrado: María González',
          timestamp: '2024-01-15T10:30:00Z',
          severity: 'info'
        },
        {
          id: 2,
          type: 'system_backup',
          description: 'Backup automático completado exitosamente',
          timestamp: '2024-01-15T02:00:00Z',
          severity: 'success'
        },
        {
          id: 3,
          type: 'holiday_sync',
          description: 'Sincronización de festivos actualizada para España',
          timestamp: '2024-01-14T18:45:00Z',
          severity: 'info'
        },
        {
          id: 4,
          type: 'security_alert',
          description: 'Intento de acceso fallido detectado',
          timestamp: '2024-01-14T15:20:00Z',
          severity: 'warning'
        },
        {
          id: 5,
          type: 'data_export',
          description: 'Reporte mensual exportado por Admin',
          timestamp: '2024-01-14T12:10:00Z',
          severity: 'info'
        }
      ],
      user_analytics: {
        daily_active_users: [
          { date: '2024-01-09', users: 28 },
          { date: '2024-01-10', users: 32 },
          { date: '2024-01-11', users: 29 },
          { date: '2024-01-12', users: 35 },
          { date: '2024-01-13', users: 31 },
          { date: '2024-01-14', users: 33 },
          { date: '2024-01-15', users: 35 }
        ],
        user_roles: {
          admin: 2,
          manager: 8,
          employee: 25,
          viewer: 7
        }
      },
      system_health: {
        api_response_time: 145,
        database_connections: 12,
        error_rate: 0.02,
        cache_hit_rate: 94.5
      }
    }
  }

  const handleSettingChange = async (setting, value) => {
    setSystemSettings(prev => ({
      ...prev,
      [setting]: value
    }))
    
    // Simular guardado de configuración
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      console.log(`Configuración ${setting} actualizada a:`, value)
    } catch (error) {
      console.error('Error actualizando configuración:', error)
    }
  }

  const handleSystemAction = async (action) => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      switch (action) {
        case 'backup':
          console.log('Backup manual iniciado')
          break
        case 'sync_holidays':
          console.log('Sincronización de festivos iniciada')
          break
        case 'clear_cache':
          console.log('Cache limpiado')
          break
        case 'export_data':
          console.log('Exportación de datos iniciada')
          break
        default:
          console.log('Acción desconocida:', action)
      }
    } catch (error) {
      console.error('Error ejecutando acción:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      success: 'text-green-600',
      info: 'text-blue-600',
      warning: 'text-yellow-600',
      error: 'text-red-600'
    }
    return colors[severity] || colors.info
  }

  const getSeverityIcon = (severity) => {
    const icons = {
      success: <CheckCircle className="w-4 h-4" />,
      info: <Activity className="w-4 h-4" />,
      warning: <AlertTriangle className="w-4 h-4" />,
      error: <AlertTriangle className="w-4 h-4" />
    }
    return icons[severity] || icons.info
  }

  if (!isAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Alert className="max-w-md">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            No tienes permisos para acceder a esta página. Solo los administradores pueden ver el panel de administración.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (loading && !systemData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Administración</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando panel de administración..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Panel de Administración</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestión del sistema y configuración global
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => handleSystemAction('backup')} disabled={loading}>
            {loading ? <LoadingSpinner size="sm" /> : <Download className="w-4 h-4 mr-2" />}
            Backup Manual
          </Button>
          <Button variant="outline" onClick={() => loadSystemData()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
        </div>
      </div>

      {/* Estadísticas del sistema */}
      {systemData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Usuarios Totales"
            value={systemData.system_stats.total_users}
            subtitle={`${systemData.system_stats.active_users} activos`}
            icon={Users}
            variant="info"
          />
          <StatsCard
            title="Uptime del Sistema"
            value={systemData.system_stats.system_uptime}
            subtitle="Disponibilidad"
            icon={Server}
            variant="success"
          />
          <StatsCard
            title="Uso de CPU"
            value={`${systemData.system_stats.cpu_usage}%`}
            subtitle="Rendimiento actual"
            icon={Cpu}
            variant={systemData.system_stats.cpu_usage > 80 ? "danger" : "warning"}
          />
          <StatsCard
            title="Uso de Memoria"
            value={`${systemData.system_stats.memory_usage}%`}
            subtitle="RAM utilizada"
            icon={HardDrive}
            variant={systemData.system_stats.memory_usage > 80 ? "danger" : "info"}
          />
        </div>
      )}

      {/* Contenido principal */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
          <TabsTrigger value="system">Sistema</TabsTrigger>
          <TabsTrigger value="settings">Configuración</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        {/* Pestaña de Resumen */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Estado del sistema */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Estado del Sistema
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">CPU</span>
                    <span className="text-sm font-medium">{systemData?.system_stats.cpu_usage}%</span>
                  </div>
                  <Progress value={systemData?.system_stats.cpu_usage} className="h-2" />
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Memoria</span>
                    <span className="text-sm font-medium">{systemData?.system_stats.memory_usage}%</span>
                  </div>
                  <Progress value={systemData?.system_stats.memory_usage} className="h-2" />
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Disco</span>
                    <span className="text-sm font-medium">{systemData?.system_stats.disk_usage}%</span>
                  </div>
                  <Progress value={systemData?.system_stats.disk_usage} className="h-2" />
                </div>
                
                <div className="pt-4 border-t">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Último Backup</p>
                      <p className="font-medium">
                        {new Date(systemData?.system_stats.last_backup).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Tamaño BD</p>
                      <p className="font-medium">{systemData?.system_stats.database_size}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actividad reciente */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Actividad Reciente
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {systemData?.recent_activities.slice(0, 5).map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className={`mt-1 ${getSeverityColor(activity.severity)}`}>
                        {getSeverityIcon(activity.severity)}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.description}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.timestamp).toLocaleString('es-ES')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Métricas de rendimiento */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Métricas de Rendimiento
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {systemData?.system_health.api_response_time}ms
                  </p>
                  <p className="text-sm text-gray-500">Tiempo de respuesta API</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {systemData?.system_health.cache_hit_rate}%
                  </p>
                  <p className="text-sm text-gray-500">Tasa de acierto cache</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {systemData?.system_health.database_connections}
                  </p>
                  <p className="text-sm text-gray-500">Conexiones BD activas</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">
                    {(systemData?.system_health.error_rate * 100).toFixed(2)}%
                  </p>
                  <p className="text-sm text-gray-500">Tasa de errores</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pestaña de Usuarios */}
        <TabsContent value="users" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Distribución de Roles</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(systemData?.user_analytics.user_roles || {}).map(([role, count]) => (
                    <div key={role} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm capitalize">{role}</span>
                        <span className="text-sm font-medium">{count} usuarios</span>
                      </div>
                      <Progress 
                        value={(count / systemData?.system_stats.total_users) * 100} 
                        className="h-2" 
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Usuarios Activos Diarios</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {systemData?.user_analytics.daily_active_users.slice(-5).map((day, index) => (
                    <div key={index} className="flex justify-between items-center p-2 border rounded">
                      <span className="text-sm">
                        {new Date(day.date).toLocaleDateString('es-ES')}
                      </span>
                      <Badge variant="outline">{day.users} usuarios</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña de Sistema */}
        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Acciones del Sistema</CardTitle>
                <CardDescription>
                  Operaciones de mantenimiento y administración
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('backup')}
                  disabled={loading}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Crear Backup Manual
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('sync_holidays')}
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sincronizar Festivos
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('clear_cache')}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Limpiar Cache
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleSystemAction('export_data')}
                  disabled={loading}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Exportar Datos
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Información del Sistema</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Versión</p>
                    <p className="font-medium">v2.1.0</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Entorno</p>
                    <p className="font-medium">Producción</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Base de Datos</p>
                    <p className="font-medium">PostgreSQL 15</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Servidor</p>
                    <p className="font-medium">Ubuntu 22.04</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña de Configuración */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuración del Sistema</CardTitle>
              <CardDescription>
                Ajustes globales de la aplicación
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Configuración General</h4>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="maintenance_mode">Modo Mantenimiento</Label>
                      <p className="text-sm text-gray-500">Deshabilitar acceso temporal</p>
                    </div>
                    <Switch
                      id="maintenance_mode"
                      checked={systemSettings.maintenance_mode}
                      onCheckedChange={(checked) => handleSettingChange('maintenance_mode', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="user_registration">Registro de Usuarios</Label>
                      <p className="text-sm text-gray-500">Permitir nuevos registros</p>
                    </div>
                    <Switch
                      id="user_registration"
                      checked={systemSettings.user_registration}
                      onCheckedChange={(checked) => handleSettingChange('user_registration', checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="email_notifications">Notificaciones Email</Label>
                      <p className="text-sm text-gray-500">Sistema de emails automático</p>
                    </div>
                    <Switch
                      id="email_notifications"
                      checked={systemSettings.email_notifications}
                      onCheckedChange={(checked) => handleSettingChange('email_notifications', checked)}
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Configuración de Negocio</h4>
                  
                  <div>
                    <Label htmlFor="max_vacation_days">Días de Vacaciones Máximos</Label>
                    <Input
                      id="max_vacation_days"
                      type="number"
                      value={systemSettings.max_vacation_days}
                      onChange={(e) => handleSettingChange('max_vacation_days', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="max_hld_hours">Horas HLD Máximas</Label>
                    <Input
                      id="max_hld_hours"
                      type="number"
                      value={systemSettings.max_hld_hours}
                      onChange={(e) => handleSettingChange('max_hld_hours', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="summer_hours">Horas de Verano (Julio-Agosto)</Label>
                    <Input
                      id="summer_hours"
                      type="number"
                      value={systemSettings.summer_hours}
                      onChange={(e) => handleSettingChange('summer_hours', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pestaña de Logs */}
        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Registro de Actividades</CardTitle>
              <CardDescription>
                Historial completo de eventos del sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Fecha/Hora</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Descripción</TableHead>
                      <TableHead>Severidad</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {systemData?.recent_activities.map((activity) => (
                      <TableRow key={activity.id}>
                        <TableCell className="text-sm">
                          {new Date(activity.timestamp).toLocaleString('es-ES')}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{activity.type}</Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          {activity.description}
                        </TableCell>
                        <TableCell>
                          <div className={`flex items-center ${getSeverityColor(activity.severity)}`}>
                            {getSeverityIcon(activity.severity)}
                            <span className="ml-1 capitalize">{activity.severity}</span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AdminPage
