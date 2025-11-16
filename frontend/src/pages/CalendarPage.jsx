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
import CalendarTableView from '../components/calendar/CalendarTableView'
import CalendarSummary from '../components/calendar/CalendarSummary'

const CalendarPage = () => {
  const { user, employee, isAdmin, isManager, isEmployee } = useAuth()
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [calendarData, setCalendarData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedView, setSelectedView] = useState('table') // 'table' o 'calendar'
  const [selectedActivity, setSelectedActivity] = useState(null)
  const [showNewActivityDialog, setShowNewActivityDialog] = useState(false)
  const [activityFilter, setActivityFilter] = useState('all')
  const [calendarViewMode, setCalendarViewMode] = useState('monthly') // Modo de vista del calendario (monthly/annual)

  useEffect(() => {
    loadCalendarData()
  }, [currentMonth, activityFilter, calendarViewMode, employee])

  const loadCalendarData = async () => {
    setLoading(true)
    try {
      const year = currentMonth.getFullYear()
      const month = currentMonth.getMonth() + 1
      
      // Para vista anual, cargar festivos de todo el año
      if (calendarViewMode === 'annual') {
        console.log('📅 Cargando vista anual para año:', year)
        let relevantHolidays = []
        
        // Intentar cargar festivos (pero no bloquear si falla)
        try {
          const holidaysResponse = await fetch(
            `${import.meta.env.VITE_API_BASE_URL}/holidays?year=${year}`,
            { credentials: 'include' }
          )
          if (holidaysResponse.ok) {
            const holidaysData = await holidaysResponse.json()
            if (holidaysData.success && holidaysData.holidays) {
              // Filtrar festivos por país del empleado si existe
              relevantHolidays = holidaysData.holidays
              if (employee?.country) {
                const ISO_TO_COUNTRY_NAME = {
                  'ESP': 'España', 'ES': 'España',
                  'USA': 'United States', 'US': 'United States',
                  'GBR': 'United Kingdom', 'GB': 'United Kingdom',
                  'FRA': 'France', 'FR': 'France',
                  'DEU': 'Germany', 'DE': 'Germany',
                  'ITA': 'Italy', 'IT': 'Italy',
                  'PRT': 'Portugal', 'PT': 'Portugal'
                }
                const countryName = ISO_TO_COUNTRY_NAME[employee.country] || employee.country
                relevantHolidays = holidaysData.holidays.filter(h => 
                  h.country === countryName || h.country === employee.country
                )
              }
              console.log('✅ Festivos cargados:', relevantHolidays.length)
            }
          } else {
            console.warn('⚠️ Error en respuesta de festivos:', holidaysResponse.status)
          }
        } catch (error) {
          console.error('❌ Error cargando festivos del año:', error)
          // Continuar sin festivos si hay error
        }
        
        // Cargar actividades de todos los meses y empleados
        const allActivities = []
        let allEmployees = []
        
        // Cargar datos de todos los meses en paralelo para mejor rendimiento
        const monthPromises = []
        for (let m = 1; m <= 12; m++) {
          let url = `${import.meta.env.VITE_API_BASE_URL}/calendar?year=${year}&month=${m}`
          // Solo agregar filtros si no es admin (admin ve todos los empleados sin filtros)
          if (!isAdmin()) {
            if (employee) {
              url += `&employee_id=${employee.id}`
            } else if (isManager() && employee?.team_id) {
              url += `&team_id=${employee.team_id}`
            }
          }
          
          monthPromises.push(
            fetch(url, { credentials: 'include' })
              .then(response => {
                if (response.ok) {
                  return response.json()
                } else {
                  console.warn(`⚠️ Error HTTP cargando mes ${m}:`, response.status, response.statusText)
                  return null
                }
              })
              .catch(error => {
                console.error(`❌ Error cargando mes ${m}:`, error)
                return null
              })
          )
        }
        
        // Esperar todas las peticiones
        const monthResults = await Promise.all(monthPromises)
        console.log('📊 Resultados de meses cargados:', monthResults.filter(r => r !== null).length, 'de 12')
        
        // Procesar resultados
        monthResults.forEach((data, index) => {
          if (data && data.success && data.calendar?.employees) {
            // Recopilar empleados (evitar duplicados)
            data.calendar.employees.forEach(emp => {
              const empData = emp.employee || emp
              if (empData && !allEmployees.find(e => e.id === empData.id)) {
                allEmployees.push({
                  id: empData.id,
                  full_name: empData.full_name || empData.name,
                  team_name: empData.team_name || empData.team?.name || 'Sin equipo',
                  country: empData.country,
                  region: empData.region,
                  city: empData.city,
                  location: {
                    country: empData.country,
                    region: empData.region,
                    city: empData.city
                  }
                })
              }
              
              // Recopilar actividades
              if (emp.activities) {
                Object.values(emp.activities).forEach(activity => {
                  allActivities.push({
                    ...activity,
                    employee_id: empData.id
                  })
                })
              }
            })
          } else if (data && !data.success) {
            console.warn(`⚠️ Mes ${index + 1} devolvió success=false:`, data.message || 'Sin mensaje')
          }
        })
        
        // Si no hay empleados pero hay un empleado logueado, usar ese
        if (allEmployees.length === 0 && employee) {
          console.log('ℹ️ No se encontraron empleados, usando empleado logueado')
          allEmployees = [{
            id: employee.id,
            full_name: employee.full_name || employee.name,
            team_name: employee.team_name || employee.team?.name || 'Sin equipo',
            country: employee.country,
            region: employee.region,
            city: employee.city,
            location: {
              country: employee.country,
              region: employee.region,
              city: employee.city
            }
          }]
        }
        
        console.log('✅ Vista anual cargada:', {
          empleados: allEmployees.length,
          actividades: allActivities.length,
          festivos: relevantHolidays.length
        })
        
        setCalendarData({
          employees: allEmployees,
          activities: allActivities,
          holidays: relevantHolidays
        })
        setLoading(false)
        return
      }
      
      // Vista mensual - cargar datos del mes actual
      let url = `${import.meta.env.VITE_API_BASE_URL}/calendar?year=${year}&month=${month}`
      
      // Solo agregar filtros si no es admin (admin ve todos los empleados sin filtros)
      if (!isAdmin()) {
        if (employee) {
          url += `&employee_id=${employee.id}`
        } else if (isManager() && employee?.team_id) {
          url += `&team_id=${employee.team_id}`
        }
      }
      
      const response = await fetch(url, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.calendar) {
          // El backend devuelve calendar.employees[], calendar.holidays[], etc.
          // Necesitamos aplanar las actividades de todos los empleados
          // El backend devuelve activities como un diccionario por fecha, necesitamos convertirlo a array
          const allActivities = []
          const processedEmployees = []
          
          if (data.calendar.employees) {
            data.calendar.employees.forEach(emp => {
              const empData = emp.employee || emp
              
              // Asegurar que el empleado tenga team_name y full_name
              if (empData && !processedEmployees.find(e => e.id === empData.id)) {
                processedEmployees.push({
                  id: empData.id,
                  full_name: empData.full_name || empData.name || 'Sin nombre',
                  team_name: empData.team_name || empData.team?.name || 'Sin equipo',
                  country: empData.country,
                  region: empData.region,
                  city: empData.city,
                  location: {
                    country: empData.country,
                    region: empData.region,
                    city: empData.city
                  }
                })
              }
              
              if (emp.activities) {
                // activities es un diccionario {fecha: actividad}, convertir a array
                Object.values(emp.activities).forEach(activity => {
                  allActivities.push({
                    ...activity,
                    employee_id: empData.id
                  })
                })
              }
            })
          }
          
          // Si no hay empleados pero hay un empleado logueado, usar ese
          if (processedEmployees.length === 0 && employee) {
            processedEmployees.push({
              id: employee.id,
              full_name: employee.full_name || employee.name || 'Sin nombre',
              team_name: employee.team_name || employee.team?.name || 'Sin equipo',
              country: employee.country,
              region: employee.region,
              city: employee.city,
              location: {
                country: employee.country,
                region: employee.region,
                city: employee.city
              }
            })
          }
          
          setCalendarData({
            ...data.calendar,
            activities: allActivities, // Actividades aplanadas para compatibilidad
            employees: processedEmployees,
            holidays: data.calendar.holidays || []
          })
        } else {
          console.error('Error en respuesta del calendario:', data)
        }
      } else {
        console.error('Error cargando calendario:', response.statusText)
      }
    } catch (error) {
      console.error('Error cargando datos del calendario:', error)
    } finally {
      setLoading(false)
    }
  }

  // Crear actividad - conectada al backend
  const handleCreateActivity = async (activityData) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/calendar/activities`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(activityData)
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Error al crear la actividad')
      }

      const result = await response.json()
      
      // Recargar datos del calendario después de crear
      await loadCalendarData()
      
      return result
    } catch (error) {
      console.error('Error creando actividad:', error)
      throw error
    }
  }

  // Eliminar actividad - conectada al backend
  const handleDeleteActivity = async (activityId) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/calendar/activities/${activityId}`,
        {
          method: 'DELETE',
          credentials: 'include'
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Error al eliminar la actividad')
      }

      // Recargar datos del calendario después de eliminar
      await loadCalendarData()
    } catch (error) {
      console.error('Error eliminando actividad:', error)
      throw error
    }
  }

  const generateMockCalendarData = () => {
    // Generar fechas del mes actual
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    
    const employees = [
      {
        id: 1,
        full_name: 'Juan Pérez',
        team_name: 'Frontend',
        location: { country: 'ES', region: 'Madrid' }
      },
      {
        id: 2,
        full_name: 'María García',
        team_name: 'Frontend',
        location: { country: 'ES', region: 'Madrid' }
      },
      {
        id: 3,
        full_name: 'Carlos López',
        team_name: 'Backend',
        location: { country: 'ES', region: 'Cataluña' }
      },
      {
        id: 4,
        full_name: 'Ana Martín',
        team_name: 'Backend',
        location: { country: 'ES', region: 'Madrid' }
      },
      {
        id: 5,
        full_name: 'Luis Rodríguez',
        team_name: 'Marketing',
        location: { country: 'ES', region: 'Andalucía' }
      }
    ]
    
    const activities = [
      {
        id: 1,
        employee_id: 1,
        type: 'vacation',
        title: 'Vacaciones de Verano',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-20`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-25`,
        status: 'approved',
        employee: { full_name: 'Juan Pérez', id: 1 },
        notes: 'Vacaciones familiares planificadas'
      },
      {
        id: 2,
        employee_id: 2,
        type: 'hld',
        title: 'Horas Libre Disposición',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-18`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-18`,
        status: 'approved',
        hours: 2,
        employee: { full_name: 'María García', id: 2 },
        notes: 'Asuntos personales'
      },
      {
        id: 3,
        employee_id: 3,
        type: 'sick_leave',
        title: 'Baja Médica',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-15`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-17`,
        status: 'approved',
        employee: { full_name: 'Carlos López', id: 3 },
        notes: 'Gripe estacional'
      },
      {
        id: 4,
        employee_id: 4,
        type: 'guard',
        title: 'Guardia de Fin de Semana',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-27`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-28`,
        status: 'approved',
        hours: 4,
        employee: { full_name: 'Ana Martín', id: 4 },
        notes: 'Guardia programada'
      },
      {
        id: 5,
        employee_id: 5,
        type: 'training',
        title: 'Curso de Formación React',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-22`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-24`,
        status: 'approved',
        hours: 3,
        employee: { full_name: 'Luis Rodríguez', id: 5 },
        notes: 'Formación técnica avanzada'
      },
      {
        id: 6,
        employee_id: 1,
        type: 'hld',
        title: 'HLD Tarde',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-10`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-10`,
        status: 'approved',
        hours: 2,
        employee: { full_name: 'Juan Pérez', id: 1 },
        notes: 'Salir antes'
      }
    ]

    const holidays = [
      {
        id: 1,
        name: 'Día de Reyes',
        date: `${year}-${String(month + 1).padStart(2, '0')}-06`,
        type: 'national',
        country: 'ES'
      },
      {
        id: 2,
        name: 'Año Nuevo',
        date: `${year}-${String(month + 1).padStart(2, '0')}-01`,
        type: 'national',
        country: 'ES'
      }
    ]

    return {
      employees,
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

      {/* Filtros, Toggle de Vista y Leyenda */}
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
        
        {/* Toggle entre vista Tabla y Calendario */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <Button
            variant={selectedView === 'table' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setSelectedView('table')}
          >
            Vista Tabla
          </Button>
          <Button
            variant={selectedView === 'calendar' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setSelectedView('calendar')}
          >
            Vista Calendario
          </Button>
        </div>

        {/* Leyenda de códigos - Compacta en 1-2 líneas */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs ml-auto">
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-green-100 border border-green-300 rounded flex items-center justify-center text-[10px] font-bold text-green-700">V</div>
            <span className="text-gray-700 dark:text-gray-300">Vacaciones</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-yellow-100 border border-yellow-300 rounded flex items-center justify-center text-[10px] font-bold text-yellow-700">A</div>
            <span className="text-gray-700 dark:text-gray-300">Ausencias</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-green-200 border border-green-400 rounded flex items-center justify-center text-[10px] font-bold text-green-800">HLD</div>
            <span className="text-gray-700 dark:text-gray-300">HLD</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-blue-100 border border-blue-300 rounded flex items-center justify-center text-[10px] font-bold text-blue-700">G</div>
            <span className="text-gray-700 dark:text-gray-300">Guardia</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-purple-100 border border-purple-300 rounded flex items-center justify-center text-[10px] font-bold text-purple-700">F</div>
            <span className="text-gray-700 dark:text-gray-300">Formación</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-sky-100 border border-sky-300 rounded flex items-center justify-center text-[10px] font-bold text-sky-700">C</div>
            <span className="text-gray-700 dark:text-gray-300">Otro</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-red-50 border border-red-200 rounded flex items-center justify-center text-[10px] font-bold text-red-700">🔴</div>
            <span className="text-gray-700 dark:text-gray-300">Festivo</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-5 h-5 bg-gray-100 border border-gray-200 rounded flex items-center justify-center text-[10px] font-bold text-gray-500">□</div>
            <span className="text-gray-700 dark:text-gray-300">Fin Semana</span>
          </div>
        </div>
      </div>

      {/* Contenido principal - Vista Tabla (primera vista por defecto) */}
      {selectedView === 'table' && (
        <>
          <CalendarTableView
            employees={calendarData?.employees || []}
            activities={calendarData?.activities || []}
            holidays={calendarData?.holidays || []}
            currentMonth={currentMonth}
            onMonthChange={setCurrentMonth}
            onActivityCreate={handleCreateActivity}
            onActivityDelete={handleDeleteActivity}
            onViewModeChange={setCalendarViewMode}
            viewMode={calendarViewMode}
            employee={employee}
          />
          {/* Información compacta bajo el calendario */}
          {employee && calendarData && (
            <CalendarSummary 
              employee={employee}
              activities={calendarData?.activities || []}
              currentMonth={currentMonth}
            />
          )}
        </>
      )}

      {/* Contenido principal - Vista Calendario Tradicional */}
      {selectedView === 'calendar' && (
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
      )}

      {/* Dialog de detalle de actividad */}
      {selectedActivity && selectedView === 'calendar' && (
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
