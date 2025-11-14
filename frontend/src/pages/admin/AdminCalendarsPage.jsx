import { useState, useEffect, useMemo, lazy, Suspense } from 'react'
import { 
  Calendar as CalendarIcon, 
  Users, 
  Filter, 
  Download,
  ChevronLeft,
  ChevronRight,
  Building
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

// Lazy load CalendarTableView para evitar problemas de inicialización
const CalendarTableView = lazy(() => import('../../components/calendar/CalendarTableView'))

const AdminCalendarsPage = () => {
  const { isAdmin } = useAuth()
  const [loading, setLoading] = useState(true)
  const [teams, setTeams] = useState([])
  const [employees, setEmployees] = useState([])
  const [selectedTeam, setSelectedTeam] = useState('all')
  const [selectedEmployee, setSelectedEmployee] = useState('all')
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1)
  const [view, setView] = useState('monthly') // 'monthly' o 'annual'
  const [calendarViewMode, setCalendarViewMode] = useState('monthly') // Modo de vista del calendario (monthly/annual)
  const [activities, setActivities] = useState([])
  const [holidays, setHolidays] = useState([])

  // Calcular filteredEmployees ANTES de los useEffect que lo usan
  const filteredEmployees = useMemo(() => {
    return employees.filter(emp => {
      if (selectedTeam === 'all') return true
      return emp.team?.id === parseInt(selectedTeam)
    })
  }, [employees, selectedTeam])

  // Calcular selectedEmployeeData ANTES de los useEffect que lo usan
  const selectedEmployeeData = useMemo(() => {
    if (selectedEmployee === 'all') {
      return selectedTeam === 'all' ? filteredEmployees[0] || null : null
    }
    return filteredEmployees.find(emp => emp.id === parseInt(selectedEmployee)) || null
  }, [selectedEmployee, selectedTeam, filteredEmployees])

  useEffect(() => {
    if (!isAdmin()) {
      return
    }
    loadData()
  }, [])

  useEffect(() => {
    if (selectedEmployeeData || (selectedEmployee === 'all' && selectedTeam === 'all' && filteredEmployees.length > 0)) {
      loadCalendarData()
    }
  }, [selectedEmployee, selectedTeam, currentYear, currentMonth, filteredEmployees.length, selectedEmployeeData, calendarViewMode])

  const loadData = async () => {
    setLoading(true)
    try {
      // Cargar equipos
      const teamsResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL}/teams`, {
        credentials: 'include'
      })
      if (teamsResponse.ok) {
        const teamsData = await teamsResponse.json()
        setTeams(teamsData.teams || [])
      }

      // Cargar empleados
      const employeesResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employees`, {
        credentials: 'include'
      })
      if (employeesResponse.ok) {
        const employeesData = await employeesResponse.json()
        setEmployees(employeesData.employees || [])
      }
    } catch (error) {
      console.error('Error cargando datos:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCalendarData = async () => {
    // Si ambos filtros están en "all", cargar todos los empleados
    if (selectedEmployee === 'all' && selectedTeam === 'all') {
      // Cargar datos para todos los empleados
      const allActivities = []
      const allHolidays = []
      
      // Para vista anual, cargar festivos de todo el año
      if (calendarViewMode === 'annual') {
        // Cargar festivos de todo el año (solo una vez, son los mismos para todos)
        try {
          const holidaysResponse = await fetch(
            `${import.meta.env.VITE_API_BASE_URL}/holidays?year=${currentYear}`,
            { credentials: 'include' }
          )
          if (holidaysResponse.ok) {
            const holidaysData = await holidaysResponse.json()
            if (holidaysData.success && holidaysData.holidays) {
              // Filtrar festivos por país de los empleados
              const employeeCountries = [...new Set(filteredEmployees.map(emp => emp.country).filter(Boolean))]
              const relevantHolidays = holidaysData.holidays.filter(h => 
                employeeCountries.some(country => {
                  // Mapear códigos ISO a nombres de países
                  const ISO_TO_COUNTRY_NAME = {
                    'ESP': 'España', 'ES': 'España',
                    'USA': 'United States', 'US': 'United States',
                    'GBR': 'United Kingdom', 'GB': 'United Kingdom',
                    'FRA': 'France', 'FR': 'France',
                    'DEU': 'Germany', 'DE': 'Germany',
                    'ITA': 'Italy', 'IT': 'Italy',
                    'PRT': 'Portugal', 'PT': 'Portugal'
                  }
                  const countryName = ISO_TO_COUNTRY_NAME[country] || country
                  return h.country === countryName || h.country === country
                })
              )
              allHolidays.push(...relevantHolidays)
            }
          }
        } catch (error) {
          console.error('Error cargando festivos del año:', error)
        }
      }
      
      // Cargar actividades y festivos por mes para cada empleado
      const monthsToLoad = calendarViewMode === 'annual' ? [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] : [currentMonth]
      
      for (const emp of filteredEmployees) {
        for (const month of monthsToLoad) {
          try {
            const response = await fetch(
              `${import.meta.env.VITE_API_BASE_URL}/calendar?employee_id=${emp.id}&year=${currentYear}&month=${month}`,
              { credentials: 'include' }
            )
            
            if (response.ok) {
              const data = await response.json()
              if (data.success && data.calendar) {
                const employeeData = data.calendar.employees?.[0]
                if (employeeData?.activities) {
                  const activitiesArray = Object.values(employeeData.activities).map(act => ({
                    ...act,
                    employee_id: emp.id,
                    start_date: act.date,
                    end_date: act.date
                  }))
                  allActivities.push(...activitiesArray)
                }
                // Recopilar festivos del mes (solo si no estamos en vista anual, ya que los cargamos antes)
                if (calendarViewMode === 'monthly' && data.calendar.holidays && allHolidays.length === 0) {
                  allHolidays.push(...data.calendar.holidays)
                }
              }
            }
          } catch (error) {
            console.error(`Error cargando calendario para empleado ${emp.id}, mes ${month}:`, error)
          }
        }
      }
      
      setActivities(allActivities)
      setHolidays(allHolidays)
      return
    }
    
    // Si hay un empleado específico seleccionado
    if (!selectedEmployeeData) return

    try {
      // Para vista anual, cargar festivos de todo el año
      if (calendarViewMode === 'annual') {
        try {
          const holidaysResponse = await fetch(
            `${import.meta.env.VITE_API_BASE_URL}/holidays?year=${currentYear}`,
            { credentials: 'include' }
          )
          if (holidaysResponse.ok) {
            const holidaysData = await holidaysResponse.json()
            if (holidaysData.success && holidaysData.holidays) {
              // Filtrar festivos por país del empleado
              const employeeCountry = selectedEmployeeData.country
              const ISO_TO_COUNTRY_NAME = {
                'ESP': 'España', 'ES': 'España',
                'USA': 'United States', 'US': 'United States',
                'GBR': 'United Kingdom', 'GB': 'United Kingdom',
                'FRA': 'France', 'FR': 'France',
                'DEU': 'Germany', 'DE': 'Germany',
                'ITA': 'Italy', 'IT': 'Italy',
                'PRT': 'Portugal', 'PT': 'Portugal'
              }
              const countryName = ISO_TO_COUNTRY_NAME[employeeCountry] || employeeCountry
              const relevantHolidays = holidaysData.holidays.filter(h => 
                h.country === countryName || h.country === employeeCountry
              )
              setHolidays(relevantHolidays)
            }
          }
        } catch (error) {
          console.error('Error cargando festivos del año:', error)
        }
        
        // Cargar actividades de todos los meses
        const allActivities = []
        for (let month = 1; month <= 12; month++) {
          try {
            const response = await fetch(
              `${import.meta.env.VITE_API_BASE_URL}/calendar?employee_id=${selectedEmployeeData.id}&year=${currentYear}&month=${month}`,
              { credentials: 'include' }
            )
            if (response.ok) {
              const data = await response.json()
              if (data.success && data.calendar) {
                const employeeData = data.calendar.employees?.[0]
                if (employeeData?.activities) {
                  const activitiesArray = Object.values(employeeData.activities).map(act => ({
                    ...act,
                    employee_id: selectedEmployeeData.id,
                    start_date: act.date,
                    end_date: act.date
                  }))
                  allActivities.push(...activitiesArray)
                }
              }
            }
          } catch (error) {
            console.error(`Error cargando actividades del mes ${month}:`, error)
          }
        }
        setActivities(allActivities)
      } else {
        // Vista mensual - cargar solo el mes actual
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/calendar?employee_id=${selectedEmployeeData.id}&year=${currentYear}&month=${currentMonth}`,
          { credentials: 'include' }
        )
        
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.calendar) {
            const employeeData = data.calendar.employees?.[0]
            const activitiesArray = employeeData?.activities 
              ? Object.values(employeeData.activities).map(act => ({
                  ...act,
                  employee_id: selectedEmployeeData.id,
                  start_date: act.date,
                  end_date: act.date
                }))
              : []
            setActivities(activitiesArray)
            setHolidays(data.calendar.holidays || [])
          }
        }
      }
    } catch (error) {
      console.error('Error cargando datos del calendario:', error)
    }
  }

  // Función para crear actividad - conectada al backend
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

  // Función para eliminar actividad - conectada al backend
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

  if (!isAdmin()) {
    return (
      <div className="space-y-6 px-6">
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-lg text-gray-600 dark:text-gray-400">
              No tienes permisos para acceder a esta página
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6 px-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Calendarios</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" text="Cargando calendarios..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 px-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Calendarios</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Vista global de calendarios de todos los equipos y empleados
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={selectedTeam} onValueChange={(value) => {
              setSelectedTeam(value)
              setSelectedEmployee('all') // Reset employee filter when team changes
            }}>
              <SelectTrigger className="w-48">
                <Building className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filtrar por equipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los equipos</SelectItem>
                {teams.map(team => (
                  <SelectItem key={team.id} value={team.id.toString()}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={selectedEmployee} onValueChange={setSelectedEmployee}>
              <SelectTrigger className="w-48">
                <Users className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filtrar por empleado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los empleados</SelectItem>
                {filteredEmployees.map(emp => (
                  <SelectItem key={emp.id} value={emp.id.toString()}>
                    {emp.full_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={view} onValueChange={setView}>
              <SelectTrigger className="w-48">
                <CalendarIcon className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Vista" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Vista Mensual</SelectItem>
                <SelectItem value="annual">Vista Anual</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Calendario */}
      {selectedEmployeeData ? (
        <Suspense fallback={
          <Card>
            <CardContent className="p-12 text-center">
              <LoadingSpinner size="lg" text="Cargando calendario..." />
            </CardContent>
          </Card>
        }>
          <CalendarTableView
            employees={selectedEmployee === 'all' && selectedTeam === 'all' ? filteredEmployees : [selectedEmployeeData]}
            activities={activities}
            holidays={holidays}
            currentMonth={new Date(currentYear, currentMonth - 1, 1)}
            onMonthChange={(date) => {
              setCurrentYear(date.getFullYear())
              setCurrentMonth(date.getMonth() + 1)
            }}
            onActivityCreate={handleCreateActivity}
            onActivityDelete={handleDeleteActivity}
            onViewModeChange={setCalendarViewMode}
          />
        </Suspense>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <CalendarIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Selecciona un empleado para ver su calendario
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              {selectedTeam === 'all' 
                ? 'Filtra por equipo o selecciona un empleado específico para ver su calendario'
                : 'Selecciona un empleado del equipo seleccionado para ver su calendario'
              }
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default AdminCalendarsPage

