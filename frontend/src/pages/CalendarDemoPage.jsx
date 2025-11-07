import { useState } from 'react'
import CalendarTableView from '../components/calendar/CalendarTableView'

/**
 * CalendarDemoPage - Página de demostración del calendario sin autenticación
 * Solo para propósitos de testing y demostración
 */
const CalendarDemoPage = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [activities, setActivities] = useState([])

  // Generar empleados mock
  const mockEmployees = [
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
    },
    {
      id: 6,
      full_name: 'Laura Fernández',
      team_name: 'Marketing',
      location: { country: 'ES', region: 'Madrid' }
    }
  ]

  // Crear actividad (demo con actualización en tiempo real)
  const handleCreateActivity = async (activityData) => {
    const newActivity = {
      id: Date.now(),
      employee_id: activityData.employee_id,
      type: activityData.activity_type,
      start_date: activityData.date,
      end_date: activityData.date,
      hours: activityData.hours,
      start_time: activityData.start_time,
      end_time: activityData.end_time,
      notes: activityData.description,
      status: 'approved'
    }
    
    setActivities(prev => [...(prev || []), newActivity])
  }

  // Eliminar actividad (demo con actualización en tiempo real)
  const handleDeleteActivity = async (activityId) => {
    setActivities(prev => (prev || []).filter(a => a.id !== activityId))
  }

  // Generar actividades mock para el mes actual
  const generateMockActivities = () => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    
    return [
      {
        id: 1,
        employee_id: 1,
        type: 'vacation',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-20`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-25`,
        status: 'approved',
        notes: 'Vacaciones de verano'
      },
      {
        id: 2,
        employee_id: 2,
        type: 'hld',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-18`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-18`,
        status: 'approved',
        hours: 2,
        notes: 'Asuntos personales'
      },
      {
        id: 3,
        employee_id: 3,
        type: 'sick_leave',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-15`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-17`,
        status: 'approved',
        notes: 'Gripe'
      },
      {
        id: 4,
        employee_id: 4,
        type: 'guard',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-27`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-28`,
        status: 'approved',
        hours: 4,
        notes: 'Guardia fin de semana'
      },
      {
        id: 5,
        employee_id: 5,
        type: 'training',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-22`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-24`,
        status: 'approved',
        hours: 3,
        notes: 'Curso de formación React'
      },
      {
        id: 6,
        employee_id: 1,
        type: 'hld',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-10`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-10`,
        status: 'approved',
        hours: 2,
        notes: 'Salir antes'
      },
      {
        id: 7,
        employee_id: 6,
        type: 'vacation',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-05`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-09`,
        status: 'approved',
        notes: 'Vacaciones'
      },
      {
        id: 8,
        employee_id: 2,
        type: 'training',
        start_date: `${year}-${String(month + 1).padStart(2, '0')}-12`,
        end_date: `${year}-${String(month + 1).padStart(2, '0')}-12`,
        status: 'approved',
        hours: 4,
        notes: 'Workshop'
      }
    ]
  }

  // Generar festivos mock
  const generateMockHolidays = () => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    
    return [
      {
        id: 1,
        name: 'Año Nuevo',
        date: `${year}-${String(month + 1).padStart(2, '0')}-01`,
        type: 'national',
        country: 'ES'
      },
      {
        id: 2,
        name: 'Día de Reyes',
        date: `${year}-${String(month + 1).padStart(2, '0')}-06`,
        type: 'national',
        country: 'ES'
      },
      {
        id: 3,
        name: 'Día de la Comunidad de Madrid',
        date: `${year}-${String(month + 1).padStart(2, '0')}-02`,
        type: 'regional',
        country: 'ES'
      }
    ]
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-[1800px] mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📊 Calendario - Vista Demo</h1>
              <p className="text-gray-600 mt-2">
                Demostración del nuevo calendario tipo tabla spreadsheet según requisitos originales
              </p>
            </div>
            <div className="text-sm text-gray-500">
              <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
                <p className="font-semibold text-blue-900">Modo Demo</p>
                <p className="text-blue-700">Datos de ejemplo</p>
              </div>
            </div>
          </div>
        </div>


        {/* Calendario */}
        <CalendarTableView
          employees={mockEmployees}
          activities={activities.length > 0 ? activities : generateMockActivities()}
          holidays={generateMockHolidays()}
          currentMonth={currentMonth}
          onMonthChange={setCurrentMonth}
          onActivityCreate={handleCreateActivity}
          onActivityDelete={handleDeleteActivity}
        />
      </div>
    </div>
  )
}

export default CalendarDemoPage

