import { useState, useEffect } from 'react'
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
import CalendarTableView from '../../components/calendar/CalendarTableView'

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

  useEffect(() => {
    if (!isAdmin()) {
      return
    }
    loadData()
  }, [])

  useEffect(() => {
    if (selectedEmployeeData) {
      loadCalendarData()
    }
  }, [selectedEmployee, currentYear, currentMonth])

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
          setActivities(employeeData?.activities || [])
          setHolidays(data.calendar.holidays || [])
        }
      }
    } catch (error) {
      console.error('Error cargando datos del calendario:', error)
    }
  }

  const filteredEmployees = employees.filter(emp => {
    if (selectedTeam === 'all') return true
    return emp.team?.id === parseInt(selectedTeam)
  })

  const selectedEmployeeData = selectedEmployee === 'all' 
    ? null 
    : filteredEmployees.find(emp => emp.id === parseInt(selectedEmployee))

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
        <CalendarTableView
          employees={[selectedEmployeeData]}
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

