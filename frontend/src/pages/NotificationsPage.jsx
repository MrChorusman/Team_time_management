import { useState, useEffect } from 'react'
import { 
  Bell, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Clock,
  Filter,
  Check,
  Trash2,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useNotifications } from '../contexts/NotificationContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { NotificationItem } from '../components/ui/notification-item'
import { StatsCard } from '../components/ui/stats-card'
import { Switch } from '../components/ui/switch'
import { Label } from '../components/ui/label'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const NotificationsPage = () => {
  const { user } = useAuth()
  const { 
    notifications, 
    loading, 
    markAsRead, 
    markAllAsRead, 
    removeNotification,
    getUnreadCount,
    getPriorityColor,
    getPriorityText
  } = useNotifications()
  
  const [filter, setFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [showSettings, setShowSettings] = useState(false)
  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    approval_requests: true,
    vacation_conflicts: true,
    calendar_changes: true,
    weekly_summaries: true,
    system_updates: false
  })

  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || 
                         (filter === 'unread' && !notification.read) ||
                         (filter === 'read' && notification.read) ||
                         notification.notification_type === filter

    const matchesPriority = priorityFilter === 'all' || notification.priority === priorityFilter

    return matchesFilter && matchesPriority
  })

  const getNotificationStats = () => {
    const total = notifications.length
    const unread = getUnreadCount()
    const high_priority = notifications.filter(n => n.priority === 'high' && !n.read).length
    const today = notifications.filter(n => {
      const notificationDate = new Date(n.created_at).toDateString()
      const today = new Date().toDateString()
      return notificationDate === today
    }).length

    return { total, unread, high_priority, today }
  }

  const stats = getNotificationStats()

  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead()
    } catch (error) {
      console.error('Error marcando todas como leídas:', error)
    }
  }

  const handleSettingChange = (setting, value) => {
    setNotificationSettings(prev => ({
      ...prev,
      [setting]: value
    }))
    // Aquí iría la llamada al API para guardar la configuración
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Notificaciones</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando notificaciones..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 px-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Notificaciones</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Centro de notificaciones y configuración de alertas
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => setShowSettings(!showSettings)}>
            <Settings className="w-4 h-4 mr-2" />
            Configuración
          </Button>
          
          {stats.unread > 0 && (
            <Button onClick={handleMarkAllAsRead}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Marcar Todas como Leídas
            </Button>
          )}
        </div>
      </div>

      {/* Configuración de notificaciones */}
      {showSettings && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Configuración de Notificaciones
            </CardTitle>
            <CardDescription>
              Personaliza cómo y cuándo recibir notificaciones
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium">Canales de Notificación</h4>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="email-notifications">Notificaciones por Email</Label>
                  <Switch
                    id="email-notifications"
                    checked={notificationSettings.email_notifications}
                    onCheckedChange={(checked) => handleSettingChange('email_notifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="push-notifications">Notificaciones Push</Label>
                  <Switch
                    id="push-notifications"
                    checked={notificationSettings.push_notifications}
                    onCheckedChange={(checked) => handleSettingChange('push_notifications', checked)}
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Tipos de Notificación</h4>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="approval-requests">Solicitudes de Aprobación</Label>
                  <Switch
                    id="approval-requests"
                    checked={notificationSettings.approval_requests}
                    onCheckedChange={(checked) => handleSettingChange('approval_requests', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="vacation-conflicts">Conflictos de Vacaciones</Label>
                  <Switch
                    id="vacation-conflicts"
                    checked={notificationSettings.vacation_conflicts}
                    onCheckedChange={(checked) => handleSettingChange('vacation_conflicts', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="calendar-changes">Cambios de Calendario</Label>
                  <Switch
                    id="calendar-changes"
                    checked={notificationSettings.calendar_changes}
                    onCheckedChange={(checked) => handleSettingChange('calendar_changes', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="weekly-summaries">Resúmenes Semanales</Label>
                  <Switch
                    id="weekly-summaries"
                    checked={notificationSettings.weekly_summaries}
                    onCheckedChange={(checked) => handleSettingChange('weekly_summaries', checked)}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filtros y búsqueda - PRIMERO */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filtrar por estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las notificaciones</SelectItem>
                <SelectItem value="unread">Sin leer</SelectItem>
                <SelectItem value="read">Leídas</SelectItem>
                <SelectItem value="approval_request">Solicitudes de aprobación</SelectItem>
                <SelectItem value="vacation_conflict">Conflictos de vacaciones</SelectItem>
                <SelectItem value="calendar_change">Cambios de calendario</SelectItem>
                <SelectItem value="weekly_summary">Resúmenes semanales</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-48">
                <AlertCircle className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filtrar por prioridad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las prioridades</SelectItem>
                <SelectItem value="high">Alta prioridad</SelectItem>
                <SelectItem value="medium">Prioridad media</SelectItem>
                <SelectItem value="low">Baja prioridad</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Lista de notificaciones */}
      <Tabs defaultValue="list" className="space-y-6">
        <TabsList>
          <TabsTrigger value="list">Vista Lista</TabsTrigger>
          <TabsTrigger value="compact">Vista Compacta</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          {filteredNotifications.length > 0 ? (
            <div className="space-y-4">
              {filteredNotifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={markAsRead}
                  onRemove={removeNotification}
                  compact={false}
                />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <Bell className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No hay notificaciones
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    {filter === 'unread' 
                      ? 'No tienes notificaciones sin leer' 
                      : 'No hay notificaciones que coincidan con los filtros seleccionados'
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="compact" className="space-y-2">
          {filteredNotifications.length > 0 ? (
            <Card>
              <CardContent className="p-0">
                {filteredNotifications.map((notification, index) => (
                  <div key={notification.id}>
                    <NotificationItem
                      notification={notification}
                      onMarkAsRead={markAsRead}
                      onRemove={removeNotification}
                      compact={true}
                    />
                    {index < filteredNotifications.length - 1 && (
                      <div className="border-b border-gray-200 dark:border-gray-700" />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <Bell className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No hay notificaciones
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    {filter === 'unread' 
                      ? 'No tienes notificaciones sin leer' 
                      : 'No hay notificaciones que coincidan con los filtros seleccionados'
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

    </div>
  )
}

export default NotificationsPage
