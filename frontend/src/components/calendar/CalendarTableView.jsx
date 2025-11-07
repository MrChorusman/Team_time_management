import React, { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, CalendarDays, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

/**
 * CalendarTableView - Calendario tipo tabla/spreadsheet
 * 
 * Estructura:
 * - Filas: Empleados
 * - Columnas: Equipo | Empleado | Vac | Aus | 1 | 2 | 3 | ... | 31
 * - Vista mensual o anual
 */
const CalendarTableView = ({ employees, activities, holidays, currentMonth, onMonthChange }) => {
  const [viewMode, setViewMode] = useState('monthly') // 'monthly' o 'annual'
  const [hoveredDay, setHoveredDay] = useState(null)

  // Obtener días del mes
  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    const days = []
    
    for (let day = 1; day <= daysInMonth; day++) {
      const currentDate = new Date(year, month, day)
      days.push({
        day,
        date: currentDate,
        dayOfWeek: currentDate.getDay(),
        isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6,
        dateString: currentDate.toISOString().split('T')[0]
      })
    }
    
    return days
  }

  // Obtener todos los meses del año para vista anual
  const getMonthsInYear = (date) => {
    const year = date.getFullYear()
    const months = []
    
    for (let month = 0; month < 12; month++) {
      const monthDate = new Date(year, month, 1)
      months.push({
        date: monthDate,
        name: monthDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }),
        days: getDaysInMonth(monthDate)
      })
    }
    
    return months
  }

  const days = getDaysInMonth(currentMonth)
  const months = viewMode === 'annual' ? getMonthsInYear(currentMonth) : [{ date: currentMonth, name: currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }), days }]

  // Verificar si un día es festivo para un empleado específico según su ubicación
  const isHoliday = (dateString, employeeLocation) => {
    if (!holidays || !employeeLocation) return false
    
    return holidays.some(holiday => {
      // Verificar que la fecha coincida
      if (holiday.date !== dateString) return false
      
      // Festivos nacionales se aplican a todos del mismo país
      if (holiday.type === 'national') {
        return holiday.country === employeeLocation.country
      }
      
      // Festivos regionales solo para la misma región
      if (holiday.type === 'regional') {
        return holiday.country === employeeLocation.country && 
               holiday.region === employeeLocation.region
      }
      
      // Festivos locales solo para la misma ciudad
      if (holiday.type === 'local') {
        return holiday.country === employeeLocation.country && 
               holiday.region === employeeLocation.region &&
               holiday.city === employeeLocation.city
      }
      
      return false
    })
  }

  // Obtener actividades para un empleado en un día específico
  const getActivityForDay = (employeeId, dateString) => {
    if (!activities) return null
    return activities.find(activity => 
      activity.employee_id === employeeId && 
      activity.start_date <= dateString && 
      activity.end_date >= dateString &&
      activity.status === 'approved'
    )
  }

  // Obtener código de actividad para mostrar en la celda
  const getActivityCode = (activity) => {
    if (!activity) return ''
    
    const codes = {
      vacation: 'V',
      sick_leave: 'A',
      hld: 'HLD',
      guard: 'G',
      training: 'F',
      other: 'C'
    }
    
    const code = codes[activity.type] || activity.type.charAt(0).toUpperCase()
    
    // Para actividades con horas, mostrar el número
    if (activity.hours && (activity.type === 'hld' || activity.type === 'guard' || activity.type === 'training')) {
      const sign = activity.type === 'guard' ? '+' : '-'
      return `${code} ${sign}${activity.hours}h`
    }
    
    return code
  }

  // Obtener color de fondo según el tipo de actividad
  const getCellBackgroundColor = (activity, isWeekend, isHolidayDay) => {
    if (isHolidayDay) return 'bg-red-50 border-red-200'
    if (isWeekend) return 'bg-gray-100 border-gray-200'
    
    if (!activity) return 'bg-white border-gray-200'
    
    const colors = {
      vacation: 'bg-green-100 border-green-300',
      sick_leave: 'bg-yellow-100 border-yellow-300',
      hld: 'bg-green-200 border-green-400',
      guard: 'bg-blue-100 border-blue-300',
      training: 'bg-purple-100 border-purple-300',
      other: 'bg-sky-100 border-sky-300'
    }
    
    return colors[activity.type] || 'bg-gray-100 border-gray-300'
  }

  // Obtener color de texto según el tipo de actividad
  const getCellTextColor = (activity, isWeekend, isHolidayDay) => {
    if (isHolidayDay) return 'text-red-700'
    if (isWeekend) return 'text-gray-500'
    
    if (!activity) return 'text-gray-900'
    
    const colors = {
      vacation: 'text-green-700',
      sick_leave: 'text-yellow-700',
      hld: 'text-green-800',
      guard: 'text-blue-700',
      training: 'text-purple-700',
      other: 'text-sky-700'
    }
    
    return colors[activity.type] || 'text-gray-700'
  }

  // Calcular días de vacaciones y ausencias del mes para un empleado
  const getMonthSummary = (employeeId, monthDate) => {
    if (!activities) return { vacation: 0, absence: 0 }
    
    const year = monthDate.getFullYear()
    const month = monthDate.getMonth()
    const monthStart = new Date(year, month, 1).toISOString().split('T')[0]
    const monthEnd = new Date(year, month + 1, 0).toISOString().split('T')[0]
    
    const monthActivities = activities.filter(activity => 
      activity.employee_id === employeeId &&
      activity.status === 'approved' &&
      ((activity.start_date >= monthStart && activity.start_date <= monthEnd) ||
       (activity.end_date >= monthStart && activity.end_date <= monthEnd) ||
       (activity.start_date <= monthStart && activity.end_date >= monthEnd))
    )
    
    let vacationDays = 0
    let absenceDays = 0
    
    monthActivities.forEach(activity => {
      const activityStart = new Date(activity.start_date)
      const activityEnd = new Date(activity.end_date)
      const rangeStart = new Date(Math.max(activityStart, new Date(monthStart)))
      const rangeEnd = new Date(Math.min(activityEnd, new Date(monthEnd)))
      
      const days = Math.ceil((rangeEnd - rangeStart) / (1000 * 60 * 60 * 24)) + 1
      
      if (activity.type === 'vacation') vacationDays += days
      if (activity.type === 'sick_leave') absenceDays += days
    })
    
    return { vacation: vacationDays, absence: absenceDays }
  }

  // Obtener festivos del mes
  const getMonthHolidays = (monthDate) => {
    if (!holidays) return []
    
    const year = monthDate.getFullYear()
    const month = monthDate.getMonth()
    const monthStart = new Date(year, month, 1).toISOString().split('T')[0]
    const monthEnd = new Date(year, month + 1, 0).toISOString().split('T')[0]
    
    return holidays.filter(holiday => 
      holiday.date >= monthStart && holiday.date <= monthEnd
    )
  }

  // Renderizar una fila de empleado
  const renderEmployeeRow = (employee, monthDate) => {
    const summary = getMonthSummary(employee.id, monthDate)
    const monthDays = getDaysInMonth(monthDate)
    
    return (
      <tr key={`${employee.id}-${monthDate.toISOString()}`} className="hover:bg-gray-50">
        {/* Equipo */}
        <td className="sticky left-0 z-10 px-4 py-3 bg-white border-r border-b border-gray-300 font-medium text-sm whitespace-nowrap">
          {employee.team_name || 'Sin equipo'}
        </td>
        
        {/* Empleado */}
        <td className="sticky left-[140px] z-10 px-4 py-3 bg-white border-r border-b border-gray-300 font-medium text-sm whitespace-nowrap">
          {employee.full_name}
        </td>
        
        {/* Vac (Vacaciones) */}
        <td className="sticky left-[280px] z-10 px-3 py-3 bg-blue-50 border-r border-b border-gray-300 text-center font-semibold text-sm">
          {summary.vacation}
        </td>
        
        {/* Aus (Ausencias) */}
        <td className="sticky left-[330px] z-10 px-3 py-3 bg-yellow-50 border-r border-b border-gray-300 text-center font-semibold text-sm">
          {summary.absence}
        </td>
        
        {/* Días del mes (1-31) */}
        {monthDays.map((dayInfo) => {
          const activity = getActivityForDay(employee.id, dayInfo.dateString)
          const isHolidayDay = isHoliday(dayInfo.dateString, employee.location)
          const bgColor = getCellBackgroundColor(activity, dayInfo.isWeekend, isHolidayDay)
          const textColor = getCellTextColor(activity, dayInfo.isWeekend, isHolidayDay)
          const code = getActivityCode(activity)
          
          return (
            <td
              key={dayInfo.day}
              className={`px-2 py-3 border-r border-b border-gray-200 text-center text-xs font-medium ${bgColor} ${textColor} cursor-pointer hover:opacity-80 transition-opacity`}
              onMouseEnter={() => setHoveredDay(dayInfo.dateString)}
              onMouseLeave={() => setHoveredDay(null)}
              title={activity ? `${activity.type}: ${activity.notes || ''}` : (isHolidayDay ? 'Festivo' : (dayInfo.isWeekend ? 'Fin de semana' : 'Día laborable'))}
            >
              {code}
            </td>
          )
        })}
      </tr>
    )
  }

  // Renderizar cabecera de la tabla
  const renderTableHeader = (monthDays) => {
    return (
      <thead className="bg-gray-100 sticky top-0 z-20">
        <tr>
          {/* Columnas fijas */}
          <th className="sticky left-0 z-30 px-4 py-3 bg-gray-100 border-r border-gray-300 text-left text-xs font-semibold text-gray-700 uppercase">
            Equipo
          </th>
          <th className="sticky left-[140px] z-30 px-4 py-3 bg-gray-100 border-r border-gray-300 text-left text-xs font-semibold text-gray-700 uppercase">
            Empleado
          </th>
          <th className="sticky left-[280px] z-30 px-3 py-3 bg-blue-100 border-r border-gray-300 text-center text-xs font-semibold text-blue-700 uppercase">
            Vac
          </th>
          <th className="sticky left-[330px] z-30 px-3 py-3 bg-yellow-100 border-r border-gray-300 text-center text-xs font-semibold text-yellow-700 uppercase">
            Aus
          </th>
          
          {/* Días del mes */}
          {monthDays.map((dayInfo) => (
            <th
              key={dayInfo.day}
              className={`px-2 py-3 border-r border-gray-200 text-center text-xs font-semibold ${
                dayInfo.isWeekend ? 'bg-gray-200 text-gray-600' : 'bg-gray-100 text-gray-700'
              }`}
            >
              {dayInfo.day}
            </th>
          ))}
        </tr>
        
        {/* Fila de días de la semana */}
        <tr className="bg-gray-50">
          <th colSpan="4" className="sticky left-0 z-30 border-r border-gray-300"></th>
          {monthDays.map((dayInfo) => {
            const dayName = ['D', 'L', 'M', 'X', 'J', 'V', 'S'][dayInfo.dayOfWeek]
            return (
              <th
                key={`day-${dayInfo.day}`}
                className={`px-2 py-1 border-r border-gray-200 text-center text-xs ${
                  dayInfo.isWeekend ? 'bg-gray-200 text-gray-600 font-semibold' : 'text-gray-600'
                }`}
              >
                {dayName}
              </th>
            )
          })}
        </tr>
      </thead>
    )
  }

  return (
    <div className="space-y-4">
      {/* Controles superiores */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Toggle vista */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <Button
              variant={viewMode === 'monthly' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('monthly')}
              className="flex items-center space-x-1"
            >
              <CalendarDays className="w-4 h-4" />
              <span>Mensual</span>
            </Button>
            <Button
              variant={viewMode === 'annual' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('annual')}
              className="flex items-center space-x-1"
            >
              <List className="w-4 h-4" />
              <span>Anual</span>
            </Button>
          </div>
          
          {/* Navegación mensual (solo en vista mensual) */}
          {viewMode === 'monthly' && (
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onMonthChange(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm font-semibold capitalize min-w-[180px] text-center">
                {currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onMonthChange(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
          
          {/* Navegación anual (solo en vista anual) */}
          {viewMode === 'annual' && (
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onMonthChange(new Date(currentMonth.getFullYear() - 1, 0, 1))}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm font-semibold min-w-[120px] text-center">
                Año {currentMonth.getFullYear()}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onMonthChange(new Date(currentMonth.getFullYear() + 1, 0, 1))}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Tabla de calendario */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto overflow-y-auto max-h-[600px] relative">
            {months.map((month) => (
              <div key={month.date.toISOString()} className="mb-8">
                {viewMode === 'annual' && (
                  <div className="sticky left-0 z-10 px-4 py-2 bg-gray-50 border-b border-gray-300">
                    <h3 className="text-lg font-semibold capitalize">{month.name}</h3>
                  </div>
                )}
                
                <table className="w-full border-collapse text-sm">
                  {renderTableHeader(month.days)}
                  <tbody>
                    {employees && employees.length > 0 ? (
                      employees.map(employee => renderEmployeeRow(employee, month.date))
                    ) : (
                      <tr>
                        <td colSpan={month.days.length + 4} className="px-4 py-8 text-center text-gray-500">
                          No hay empleados para mostrar
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                
                {/* Leyenda de festivos del mes (en ambas vistas) */}
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-300">
                  <h4 className="text-xs font-semibold text-gray-700 uppercase mb-2">Festivos del mes</h4>
                  <div className="flex flex-wrap gap-2">
                    {getMonthHolidays(month.date).length > 0 ? (
                      getMonthHolidays(month.date).map((holiday) => {
                        const day = new Date(holiday.date).getDate()
                        return (
                          <Badge key={holiday.id} variant="outline" className="bg-red-50 text-red-700 border-red-300">
                            Día {day}: {holiday.name} ({holiday.type === 'national' ? 'Nacional' : holiday.type === 'regional' ? 'Regional' : 'Local'})
                          </Badge>
                        )
                      })
                    ) : (
                      <span className="text-xs text-gray-500">No hay festivos este mes</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Leyenda de códigos */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Leyenda de Actividades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-100 border-2 border-green-300 rounded flex items-center justify-center text-xs font-bold text-green-700">
                V
              </div>
              <span className="text-xs text-gray-700">Vacaciones</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-yellow-100 border-2 border-yellow-300 rounded flex items-center justify-center text-xs font-bold text-yellow-700">
                A
              </div>
              <span className="text-xs text-gray-700">Ausencias</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-200 border-2 border-green-400 rounded flex items-center justify-center text-xs font-bold text-green-800">
                HLD
              </div>
              <span className="text-xs text-gray-700">Horas Libre Disposición</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-100 border-2 border-blue-300 rounded flex items-center justify-center text-xs font-bold text-blue-700">
                G
              </div>
              <span className="text-xs text-gray-700">Guardia</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-purple-100 border-2 border-purple-300 rounded flex items-center justify-center text-xs font-bold text-purple-700">
                F
              </div>
              <span className="text-xs text-gray-700">Formación/Evento</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-sky-100 border-2 border-sky-300 rounded flex items-center justify-center text-xs font-bold text-sky-700">
                C
              </div>
              <span className="text-xs text-gray-700">Permiso/Otro</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-red-50 border-2 border-red-200 rounded flex items-center justify-center text-xs font-bold text-red-700">
                🔴
              </div>
              <span className="text-xs text-gray-700">Festivo</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gray-100 border-2 border-gray-200 rounded flex items-center justify-center text-xs font-bold text-gray-500">
                □
              </div>
              <span className="text-xs text-gray-700">Fin de Semana</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default CalendarTableView

