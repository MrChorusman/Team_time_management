import { useState } from 'react'
import CalendarTableView from '../components/calendar/CalendarTableView'

/**
 * CalendarDemoPage - Página de demostración del calendario sin autenticación
 * Solo para propósitos de testing y demostración
 */
const CalendarDemoPage = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date())

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

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">✅ Implementado</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Vista tabla tipo Excel</li>
              <li>• Empleados en filas</li>
              <li>• Días (1-31) en columnas</li>
              <li>• Códigos: V, A, HLD, G, F, C</li>
            </ul>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">🎨 Características</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Colores por tipo</li>
              <li>• Resumen Vac y Aus</li>
              <li>• Leyenda de festivos</li>
              <li>• Toggle mensual/anual</li>
            </ul>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">📱 UX</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Columnas sticky</li>
              <li>• Scroll horizontal</li>
              <li>• Tooltips informativos</li>
              <li>• Responsive design</li>
            </ul>
          </div>
        </div>

        {/* Calendario */}
        <CalendarTableView
          employees={mockEmployees}
          activities={generateMockActivities()}
          holidays={generateMockHolidays()}
          currentMonth={currentMonth}
          onMonthChange={setCurrentMonth}
        />
      </div>
    </div>
  )
}

export default CalendarDemoPage

