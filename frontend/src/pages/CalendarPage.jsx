import { useState, useEffect } from 'react'
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Filter, 
  Download,
  ChevronLeft,
  ChevronRight,
  Clock,
  MapPin,
  User,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Calendar } from '../components/ui/calendar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Textarea } from '../components/ui/textarea'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const CalendarPage = () => {
  const { user, employee, isManager, isEmployee } = useAuth()
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [calendarData, setCalendarData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedView, setSelectedView] = useState('month')
  const [selectedActivity, setSelectedActivity] = useState(null)
  const [showNewActivityDialog, setShowNewActivityDialog] = useState(false)
  const [activityFilter, setActivityFilter] = useState('all')

  useEffect(() => {
    loadCalendarData()
  }, [currentMonth, activityFilter])

  const loadCalendarData = async () => {
    setLoading(true)
    try {
      // Simular carga de datos del calendario
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = generateMockCalendarData()
      setCalendarData(mockData)
    } catch (error) {
      console.error('Error cargando datos del calendario:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockCalendarData = () => {
    const activities = [
      {
        id: 1,
        type: 'vacation',
        title: 'Vacaciones de Verano',
        start_date: '2024-01-20',
        end_date: '2024-01-25',
        status: 'approved',
        employee: { full_name: 'Juan Pérez', id: 1 },
        notes: 'Vacaciones familiares planificadas'
      },
      {
        id: 2,
        type: 'hld',
        title: 'Día de Libre Disposición',
        start_date: '2024-01-18',
        end_date: '2024-01-18',
        status: 'pending',
        employee: { full_name: 'María García', id: 2 },
        notes: 'Asuntos personales'
      },
      {
        id: 3,
        type: 'sick_leave',
        title: 'Baja Médica',
        start_date: '2024-01-15',
        end_date: '2024-01-17',
        status: 'approved',
        employee: { full_name: 'Carlos López', id: 3 },
        notes: 'Gripe estacional'
      },
      {
        id: 4,
        type: 'guard',
        title: 'Guardia de Fin de Semana',
        start_date: '2024-01-27',
        end_date: '2024-01-28',
        status: 'approved',
        employee: { full_name: 'Ana Martín', id: 4 },
        notes: 'Guardia programada'
      },
      {
        id: 5,
        type: 'training',
        title: 'Curso de Formación React',
        start_date: '2024-01-22',
        end_date: '2024-01-24',
        status: 'approved',
        employee: { full_name: 'Luis Rodríguez', id: 5 },
        notes: 'Formación técnica avanzada'
      }
    ]

    const holidays = [
      {
        id: 1,
        name: 'Día de Reyes',
        date: '2024-01-06',
        type: 'national',
        country: 'ES'
      },
      {
        id: 2,
        name: 'Día de Andalucía',
        date: '2024-02-28',
        type: 'regional',
        region: 'Andalucía'
      }
    ]

    return {
      activities: activities.filter(activity => {
        if (activityFilter === 'all') return true
        return activity.type === activityFilter
      }),
      holidays,
      summary: {
        total_activities: activities.length,
        pending_approvals: activities.filter(a => a.status === 'pending').length,
        approved_activities: activities.filter(a => a.status === 'approved').length,
        vacation_days: activities.filter(a => a.type === 'vacation').length
      }
    }
  }

  const getActivityTypeColor = (type) => {
    const colors = {
      vacation: 'bg-blue-100 text-blue-800 border-blue-200',
      hld: 'bg-green-100 text-green-800 border-green-200',
      sick_leave: 'bg-red-100 text-red-800 border-red-200',
      guard: 'bg-purple-100 text-purple-800 border-purple-200',
      training: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      other: 'bg-gray-100 text-gray-800 border-gray-200'
    }
    return colors[type] || colors.other
  }

  const getActivityTypeLabel = (type) => {
    const labels = {
      vacation: 'Vacaciones',
      hld: 'HLD',
      sick_leave: 'Baja Médica',
      guard: 'Guardia',
      training: 'Formación',
      other: 'Otro'
    }
    return labels[type] || 'Desconocido'
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    }
    return colors[status] || colors.pending
  }

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'Pendiente',
      approved: 'Aprobado',
      rejected: 'Rechazado'
    }
    return labels[status] || 'Desconocido'
  }

  const isDateInRange = (date, startDate, endDate) => {
    const checkDate = new Date(date)
    const start = new Date(startDate)
    const end = new Date(endDate)
    return checkDate >= start && checkDate <= end
  }

  const getActivitiesForDate = (date) => {
    if (!calendarData) return []
    
    const dateStr = date.toISOString().split('T')[0]
    return calendarData.activities.filter(activity => 
      isDateInRange(dateStr, activity.start_date, activity.end_date)
    )
  }

  const getHolidaysForDate = (date) => {
    if (!calendarData) return []
    
    const dateStr = date.toISOString().split('T')[0]
    return calendarData.holidays.filter(holiday => holiday.date === dateStr)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Calendario</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando calendario..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Calendario</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona actividades, vacaciones y eventos del equipo
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {isEmployee() && (
            <Dialog open={showNewActivityDialog} onOpenChange={setShowNewActivityDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Nueva Actividad
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Nueva Actividad</DialogTitle>
                  <DialogDescription>
                    Crea una nueva actividad en tu calendario
                  </DialogDescription>
                </DialogHeader>
                <NewActivityForm onClose={() => setShowNewActivityDialog(false)} />
              </DialogContent>
            </Dialog>
          )}
          
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Estadísticas rápidas */}
      {calendarData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Actividades</p>
                  <p className="text-2xl font-bold">{calendarData.summary.total_activities}</p>
                </div>
                <CalendarIcon className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Pendientes</p>
                  <p className="text-2xl font-bold text-yellow-600">{calendarData.summary.pending_approvals}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Aprobadas</p>
                  <p className="text-2xl font-bold text-green-600">{calendarData.summary.approved_activities}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Vacaciones</p>
                  <p className="text-2xl font-bold text-blue-600">{calendarData.summary.vacation_days}</p>
                </div>
                <User className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros */}
      <div className="flex flex-wrap items-center gap-4">
        <Select value={activityFilter} onValueChange={setActivityFilter}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filtrar por tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas las actividades</SelectItem>
            <SelectItem value="vacation">Vacaciones</SelectItem>
            <SelectItem value="hld">HLD</SelectItem>
            <SelectItem value="sick_leave">Bajas médicas</SelectItem>
            <SelectItem value="guard">Guardias</SelectItem>
            <SelectItem value="training">Formación</SelectItem>
          </SelectContent>
        </Select>
        
        <Select value={selectedView} onValueChange={setSelectedView}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="month">Mes</SelectItem>
            <SelectItem value="week">Semana</SelectItem>
            <SelectItem value="list">Lista</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendario */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {currentMonth.toLocaleDateString('es-ES', { 
                    month: 'long', 
                    year: 'numeric' 
                  })}
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentMonth(new Date())}
                  >
                    Hoy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                month={currentMonth}
                onMonthChange={setCurrentMonth}
                className="w-full"
                modifiers={{
                  hasActivities: (date) => getActivitiesForDate(date).length > 0,
                  hasHolidays: (date) => getHolidaysForDate(date).length > 0
                }}
                modifiersStyles={{
                  hasActivities: { 
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)'
                  },
                  hasHolidays: { 
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)'
                  }
                }}
              />
            </CardContent>
          </Card>
        </div>

        {/* Panel lateral */}
        <div className="space-y-6">
          {/* Actividades del día seleccionado */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {selectedDate?.toLocaleDateString('es-ES', { 
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long'
                })}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDate && (
                <div className="space-y-3">
                  {/* Festivos */}
                  {getHolidaysForDate(selectedDate).map((holiday) => (
                    <div key={holiday.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 text-red-600 mr-2" />
                        <span className="font-medium text-red-800">{holiday.name}</span>
                      </div>
                      <p className="text-sm text-red-600 mt-1">
                        Festivo {holiday.type === 'national' ? 'nacional' : 'regional'}
                      </p>
                    </div>
                  ))}

                  {/* Actividades */}
                  {getActivitiesForDate(selectedDate).map((activity) => (
                    <div 
                      key={activity.id} 
                      className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800"
                      onClick={() => setSelectedActivity(activity)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={getActivityTypeColor(activity.type)}>
                          {getActivityTypeLabel(activity.type)}
                        </Badge>
                        <Badge variant="outline" className={getStatusColor(activity.status)}>
                          {getStatusLabel(activity.status)}
                        </Badge>
                      </div>
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {activity.title}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {activity.employee.full_name}
                      </p>
                    </div>
                  ))}

                  {getActivitiesForDate(selectedDate).length === 0 && getHolidaysForDate(selectedDate).length === 0 && (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                      No hay actividades para este día
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Próximas actividades */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Próximas Actividades</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {calendarData?.activities.slice(0, 5).map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.title}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.start_date).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    <Badge variant="outline" className={getStatusColor(activity.status)}>
                      {getStatusLabel(activity.status)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Dialog de detalle de actividad */}
      {selectedActivity && (
        <Dialog open={!!selectedActivity} onOpenChange={() => setSelectedActivity(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{selectedActivity.title}</DialogTitle>
              <DialogDescription>
                Detalles de la actividad
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge className={getActivityTypeColor(selectedActivity.type)}>
                  {getActivityTypeLabel(selectedActivity.type)}
                </Badge>
                <Badge variant="outline" className={getStatusColor(selectedActivity.status)}>
                  {getStatusLabel(selectedActivity.status)}
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Empleado</Label>
                  <p className="text-sm">{selectedActivity.employee.full_name}</p>
                </div>
                <div>
                  <Label>Fechas</Label>
                  <p className="text-sm">
                    {new Date(selectedActivity.start_date).toLocaleDateString('es-ES')}
                    {selectedActivity.start_date !== selectedActivity.end_date && 
                      ` - ${new Date(selectedActivity.end_date).toLocaleDateString('es-ES')}`
                    }
                  </p>
                </div>
              </div>
              
              {selectedActivity.notes && (
                <div>
                  <Label>Notas</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedActivity.notes}
                  </p>
                </div>
              )}
              
              {isManager() && selectedActivity.status === 'pending' && (
                <div className="flex space-x-2 pt-4">
                  <Button size="sm" className="flex-1">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Aprobar
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    <X className="w-4 h-4 mr-2" />
                    Rechazar
                  </Button>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

// Componente para el formulario de nueva actividad
const NewActivityForm = ({ onClose }) => {
  const [formData, setFormData] = useState({
    type: '',
    title: '',
    start_date: '',
    end_date: '',
    notes: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    // Aquí iría la lógica para crear la nueva actividad
    console.log('Nueva actividad:', formData)
    onClose()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="type">Tipo de Actividad</Label>
        <Select value={formData.type} onValueChange={(value) => setFormData({...formData, type: value})}>
          <SelectTrigger>
            <SelectValue placeholder="Selecciona el tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="vacation">Vacaciones</SelectItem>
            <SelectItem value="hld">HLD</SelectItem>
            <SelectItem value="sick_leave">Baja Médica</SelectItem>
            <SelectItem value="training">Formación</SelectItem>
            <SelectItem value="other">Otro</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="title">Título</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          placeholder="Describe la actividad"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="start_date">Fecha Inicio</Label>
          <Input
            id="start_date"
            type="date"
            value={formData.start_date}
            onChange={(e) => setFormData({...formData, start_date: e.target.value})}
          />
        </div>
        <div>
          <Label htmlFor="end_date">Fecha Fin</Label>
          <Input
            id="end_date"
            type="date"
            value={formData.end_date}
            onChange={(e) => setFormData({...formData, end_date: e.target.value})}
          />
        </div>
      </div>

      <div>
        <Label htmlFor="notes">Notas</Label>
        <Textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({...formData, notes: e.target.value})}
          placeholder="Información adicional (opcional)"
          rows={3}
        />
      </div>

      <div className="flex space-x-2 pt-4">
        <Button type="submit" className="flex-1">Crear Actividad</Button>
        <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
      </div>
    </form>
  )
}

export default CalendarPage
