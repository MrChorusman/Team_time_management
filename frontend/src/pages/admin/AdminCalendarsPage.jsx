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
  }, [selectedEmployee, selectedTeam, currentYear, currentMonth, filteredEmployees.length, selectedEmployeeData])

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
      
      for (const emp of filteredEmployees) {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_BASE_URL}/calendar?employee_id=${emp.id}&year=${currentYear}&month=${currentMonth}`,
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
              // Recopilar festivos (solo una vez, son los mismos para todos)
              if (data.calendar.holidays && allHolidays.length === 0) {
                allHolidays.push(...data.calendar.holidays)
              }
            }
          }
        } catch (error) {
          console.error(`Error cargando calendario para empleado ${emp.id}:`, error)
        }
      }
      
      setActivities(allActivities)
      setHolidays(allHolidays)
      return
    }
    
    // Si hay un empleado específico seleccionado
    if (!selectedEmployeeData) return

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/calendar?employee_id=${selectedEmployeeData.id}&year=${currentYear}&month=${currentMonth}`,
        { credentials: 'include' }
      )
      
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.calendar) {
          // El backend devuelve los datos en calendar.employees[0].activities y calendar.holidays
          const employeeData = data.calendar.employees?.[0]
          // activities viene como diccionario {fecha: actividad}, convertir a array
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
    } catch (error) {
      console.error('Error cargando datos del calendario:', error)
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
            onActivityCreate={loadCalendarData}
            onActivityDelete={loadCalendarData}
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

