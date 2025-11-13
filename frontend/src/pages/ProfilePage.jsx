import { useState, useEffect } from 'react'
import { 
  User, 
  Mail, 
  MapPin, 
  Building, 
  Clock, 
  Calendar,
  Edit,
  Save,
  X,
  Camera,
  Shield,
  Key,
  Bell,
  Globe,
  Smartphone
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { Badge } from '../components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Switch } from '../components/ui/switch'
import { Progress } from '../components/ui/progress'
import { Alert, AlertDescription } from '../components/ui/alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'

// Componente para mostrar la lista de actividad
const ActivityList = ({ userId }) => {
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (userId) {
      loadActivities()
    }
  }, [userId])

  const loadActivities = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/notifications?per_page=10`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setActivities(data.notifications || [])
      }
    } catch (error) {
      console.error('Error cargando actividad:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityColor = (type) => {
    const colors = {
      'employee_registration': 'bg-blue-600',
      'employee_approved': 'bg-green-600',
      'approval_request': 'bg-yellow-600',
      'system': 'bg-purple-600',
      'calendar_change': 'bg-indigo-600'
    }
    return colors[type] || 'bg-gray-600'
  }

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Hace unos momentos'
    if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`
    if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`
    if (diffDays < 7) return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`
    
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
  }

  if (loading) {
    return <LoadingSpinner size="sm" text="Cargando actividad..." />
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No hay actividad reciente</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start space-x-3">
          <div className={`w-2 h-2 ${getActivityColor(activity.notification_type)} rounded-full mt-2`} />
          <div className="flex-1">
            <p className="text-sm font-medium">{activity.title}</p>
            <p className="text-xs text-gray-500">{activity.message}</p>
            <p className="text-xs text-gray-400 mt-1">{formatTimeAgo(activity.created_at)}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

const ProfilePage = () => {
  const { user, employee, updateProfile } = useAuth()
  const [loading, setLoading] = useState(false)
  const [editing, setEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    country: '',
    region: '',
    city: '',
    hours_monday_thursday: 8.0,
    hours_friday: 6.0,
    phone: '',
    timezone: 'Europe/Madrid'
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })
  const [preferences, setPreferences] = useState({
    language: 'es',
    theme: 'system',
    email_notifications: true,
    push_notifications: true,
    weekly_reports: true,
    vacation_reminders: true
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    if (employee) {
      setProfileData({
        full_name: employee.full_name || '',
        email: employee.email || '',
        country: employee.country || '',
        region: employee.region || '',
        city: employee.city || '',
        hours_monday_thursday: employee.hours_monday_thursday || 8.0,
        hours_friday: employee.hours_friday || 6.0,
        phone: employee.phone || '',
        timezone: employee.timezone || 'Europe/Madrid'
      })
    }
  }, [employee])

  const getInitials = (name) => {
    if (!name) return 'U'
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // Simular actualización del perfil
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Aquí iría la llamada real al API
      // await updateProfile(profileData)
      
      setMessage({ type: 'success', text: 'Perfil actualizado correctamente' })
      setEditing(false)
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al actualizar el perfil' })
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'Las contraseñas no coinciden' })
      return
    }
    
    if (passwordData.new_password.length < 8) {
      setMessage({ type: 'error', text: 'La contraseña debe tener al menos 8 caracteres' })
      return
    }
    
    setLoading(true)
    
    try {
      // Simular cambio de contraseña
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setMessage({ type: 'success', text: 'Contraseña cambiada correctamente' })
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al cambiar la contraseña' })
    } finally {
      setLoading(false)
    }
  }

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }))
    
    // Simular guardado automático
    setTimeout(() => {
      setMessage({ type: 'success', text: 'Preferencias guardadas' })
    }, 500)
  }

  const getEmployeeStats = () => {
    if (!employee) return null
    
    return {
      efficiency: 92.3,
      hours_this_month: 145,
      vacation_days_used: 8,
      vacation_days_remaining: 15,
      hld_hours_used: 24,
      hld_hours_remaining: 16
    }
  }

  const stats = getEmployeeStats()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mi Perfil</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona tu información personal y preferencias
          </p>
        </div>
      </div>

      {/* Mensaje de estado */}
      {message.text && (
        <Alert className={message.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <AlertDescription className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
            {message.text}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información básica */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Información Personal
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setEditing(!editing)}
                >
                  {editing ? <X className="w-4 h-4" /> : <Edit className="w-4 h-4" />}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar */}
              <div className="flex flex-col items-center space-y-4">
                <div className="relative">
                  <Avatar className="h-24 w-24">
                    <AvatarImage src={`/avatars/${user?.id}.jpg`} />
                    <AvatarFallback className="text-lg">
                      {getInitials(profileData.full_name)}
                    </AvatarFallback>
                  </Avatar>
                  <Button
                    variant="outline"
                    size="sm"
                    className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full p-0"
                  >
                    <Camera className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="text-center">
                  <h3 className="font-semibold text-lg">{profileData.full_name}</h3>
                  <p className="text-sm text-gray-500">{profileData.email}</p>
                  {employee?.team && (
                    <Badge variant="outline" className="mt-2">
                      {employee.team.name}
                    </Badge>
                  )}
                </div>
              </div>

              {/* Estado de aprobación */}
              {employee && (
                <div className="text-center">
                  <Badge 
                    className={
                      employee.approved === 'approved' 
                        ? 'bg-green-100 text-green-800 border-green-200'
                        : employee.approved === 'pending'
                        ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                        : 'bg-red-100 text-red-800 border-red-200'
                    }
                  >
                    {employee.approved === 'approved' ? 'Aprobado' : 
                     employee.approved === 'pending' ? 'Pendiente de Aprobación' : 'Rechazado'}
                  </Badge>
                </div>
              )}

              {/* Estadísticas rápidas */}
              {stats && (
                <div className="space-y-3">
                  <h4 className="font-medium">Estadísticas del Mes</h4>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Eficiencia</span>
                      <span className="font-medium">{stats.efficiency}%</span>
                    </div>
                    <Progress value={stats.efficiency} className="h-2" />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Horas trabajadas</p>
                      <p className="font-medium">{stats.hours_this_month}h</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Vacaciones restantes</p>
                      <p className="font-medium">{stats.vacation_days_remaining} días</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Contenido principal */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList>
              <TabsTrigger value="profile">Perfil</TabsTrigger>
              <TabsTrigger value="security">Seguridad</TabsTrigger>
              <TabsTrigger value="preferences">Preferencias</TabsTrigger>
              <TabsTrigger value="activity">Actividad</TabsTrigger>
            </TabsList>

            {/* Pestaña de Perfil */}
            <TabsContent value="profile">
              <Card>
                <CardHeader>
                  <CardTitle>Información del Perfil</CardTitle>
                  <CardDescription>
                    Actualiza tu información personal y configuración laboral
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleProfileUpdate} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label htmlFor="full_name">Nombre Completo</Label>
                        <Input
                          id="full_name"
                          value={profileData.full_name}
                          onChange={(e) => setProfileData({...profileData, full_name: e.target.value})}
                          disabled={!editing}
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={profileData.email}
                          onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                          disabled={!editing}
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="phone">Teléfono</Label>
                        <Input
                          id="phone"
                          value={profileData.phone}
                          onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                          disabled={!editing}
                          placeholder="+34 600 000 000"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="timezone">Zona Horaria</Label>
                        <Select 
                          value={profileData.timezone} 
                          onValueChange={(value) => setProfileData({...profileData, timezone: value})}
                          disabled={!editing}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Europe/Madrid">Europa/Madrid (CET)</SelectItem>
                            <SelectItem value="America/Mexico_City">América/Ciudad_de_México (CST)</SelectItem>
                            <SelectItem value="America/Argentina/Buenos_Aires">América/Buenos_Aires (ART)</SelectItem>
                            <SelectItem value="America/Bogota">América/Bogotá (COT)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium">Ubicación</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <Label htmlFor="country">País</Label>
                          <Select 
                            value={profileData.country} 
                            onValueChange={(value) => setProfileData({...profileData, country: value})}
                            disabled={!editing}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selecciona país" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="ES">España</SelectItem>
                              <SelectItem value="MX">México</SelectItem>
                              <SelectItem value="AR">Argentina</SelectItem>
                              <SelectItem value="CO">Colombia</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div>
                          <Label htmlFor="region">Región/Estado</Label>
                          <Input
                            id="region"
                            value={profileData.region}
                            onChange={(e) => setProfileData({...profileData, region: e.target.value})}
                            disabled={!editing}
                            placeholder="Madrid, CDMX, etc."
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="city">Ciudad</Label>
                          <Input
                            id="city"
                            value={profileData.city}
                            onChange={(e) => setProfileData({...profileData, city: e.target.value})}
                            disabled={!editing}
                            placeholder="Madrid, Ciudad de México, etc."
                          />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium">Configuración Horaria</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="hours_monday_thursday">Horas Lunes-Jueves</Label>
                          <Input
                            id="hours_monday_thursday"
                            type="number"
                            step="0.5"
                            min="1"
                            max="12"
                            value={profileData.hours_monday_thursday}
                            onChange={(e) => setProfileData({...profileData, hours_monday_thursday: parseFloat(e.target.value)})}
                            disabled={!editing}
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="hours_friday">Horas Viernes</Label>
                          <Input
                            id="hours_friday"
                            type="number"
                            step="0.5"
                            min="1"
                            max="12"
                            value={profileData.hours_friday}
                            onChange={(e) => setProfileData({...profileData, hours_friday: parseFloat(e.target.value)})}
                            disabled={!editing}
                          />
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-500">
                        Total semanal: {(profileData.hours_monday_thursday * 4 + profileData.hours_friday)} horas
                      </div>
                    </div>

                    {editing && (
                      <div className="flex space-x-2">
                        <Button type="submit" disabled={loading}>
                          {loading ? <LoadingSpinner size="sm" /> : <Save className="w-4 h-4 mr-2" />}
                          Guardar Cambios
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setEditing(false)}>
                          Cancelar
                        </Button>
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Pestaña de Seguridad */}
            <TabsContent value="security">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="w-5 h-5 mr-2" />
                    Seguridad de la Cuenta
                  </CardTitle>
                  <CardDescription>
                    Gestiona la seguridad de tu cuenta y cambia tu contraseña
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordChange} className="space-y-6">
                    <div>
                      <Label htmlFor="current_password">Contraseña Actual</Label>
                      <Input
                        id="current_password"
                        type="password"
                        value={passwordData.current_password}
                        onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                        placeholder="Introduce tu contraseña actual"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="new_password">Nueva Contraseña</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={passwordData.new_password}
                        onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                        placeholder="Mínimo 8 caracteres"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="confirm_password">Confirmar Nueva Contraseña</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={passwordData.confirm_password}
                        onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                        placeholder="Repite la nueva contraseña"
                      />
                    </div>
                    
                    <Button type="submit" disabled={loading}>
                      {loading ? <LoadingSpinner size="sm" /> : <Key className="w-4 h-4 mr-2" />}
                      Cambiar Contraseña
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Pestaña de Preferencias */}
            <TabsContent value="preferences">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Globe className="w-5 h-5 mr-2" />
                    Preferencias
                  </CardTitle>
                  <CardDescription>
                    Personaliza tu experiencia en la aplicación
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Idioma y Región</h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="language">Idioma</Label>
                        <Select 
                          value={preferences.language} 
                          onValueChange={(value) => handlePreferenceChange('language', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="es">Español</SelectItem>
                            <SelectItem value="en">English</SelectItem>
                            <SelectItem value="pt">Português</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="theme">Tema</Label>
                        <Select 
                          value={preferences.theme} 
                          onValueChange={(value) => handlePreferenceChange('theme', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="light">Claro</SelectItem>
                            <SelectItem value="dark">Oscuro</SelectItem>
                            <SelectItem value="system">Sistema</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Notificaciones</h4>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label htmlFor="email_notifications">Notificaciones por Email</Label>
                          <p className="text-sm text-gray-500">Recibir notificaciones importantes por correo</p>
                        </div>
                        <Switch
                          id="email_notifications"
                          checked={preferences.email_notifications}
                          onCheckedChange={(checked) => handlePreferenceChange('email_notifications', checked)}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label htmlFor="push_notifications">Notificaciones Push</Label>
                          <p className="text-sm text-gray-500">Notificaciones en tiempo real en el navegador</p>
                        </div>
                        <Switch
                          id="push_notifications"
                          checked={preferences.push_notifications}
                          onCheckedChange={(checked) => handlePreferenceChange('push_notifications', checked)}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label htmlFor="weekly_reports">Reportes Semanales</Label>
                          <p className="text-sm text-gray-500">Resumen semanal de tu actividad</p>
                        </div>
                        <Switch
                          id="weekly_reports"
                          checked={preferences.weekly_reports}
                          onCheckedChange={(checked) => handlePreferenceChange('weekly_reports', checked)}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label htmlFor="vacation_reminders">Recordatorios de Vacaciones</Label>
                          <p className="text-sm text-gray-500">Avisos sobre días de vacaciones disponibles</p>
                        </div>
                        <Switch
                          id="vacation_reminders"
                          checked={preferences.vacation_reminders}
                          onCheckedChange={(checked) => handlePreferenceChange('vacation_reminders', checked)}
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Pestaña de Actividad */}
            <TabsContent value="activity">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    Actividad Reciente
                  </CardTitle>
                  <CardDescription>
                    Historial de acciones en tu cuenta
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ActivityList userId={user?.id} />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
