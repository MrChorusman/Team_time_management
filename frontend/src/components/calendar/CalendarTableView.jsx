import { useState, useEffect, useRef, useMemo } from 'react'
import { ChevronLeft, ChevronRight, CalendarDays, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'
import ContextMenu from './ContextMenu'
import ActivityModal from './ActivityModal'
import calendarHelpers from './calendarHelpers'

// NO destructurar al inicio - usar directamente desde el objeto para evitar problemas de inicialización

/**
 * CalendarTableView - Calendario tipo tabla/spreadsheet
 * 
 * Estructura:
 * - Filas: Empleados
 * - Columnas: Equipo | Empleado | Vac | Aus | 1 | 2 | 3 | ... | 31
 * - Vista mensual o anual
 */
// Las funciones helper están ahora en calendarHelpers.js para evitar problemas de inicialización
const CalendarTableView = ({ employees, activities, holidays, currentMonth, onMonthChange, onActivityCreate, onActivityDelete, onViewModeChange }) => {
  const [viewMode, setViewMode] = useState('monthly') // 'monthly' o 'annual'
  
  // Notificar al padre cuando cambia el modo de vista
  useEffect(() => {
    if (onViewModeChange) {
      onViewModeChange(viewMode)
    }
  }, [viewMode, onViewModeChange])
  const [hoveredDay, setHoveredDay] = useState(null)
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, employeeId: null, date: null, activity: null })
  const [activityModal, setActivityModal] = useState({ visible: false, type: null, date: null, employeeId: null, employeeName: null })
  const longPressTimer = useRef(null)
  const { toast } = useToast()

  // Calcular meses usando useMemo en lugar de IIFE para mejor compatibilidad con minificación
  // Usar funciones directamente desde calendarHelpers sin destructurar
  const calculatedMonths = useMemo(() => {
    try {
      if (viewMode === 'annual') {
        return calendarHelpers.getMonthsInYear(currentMonth) || []
      } else {
        const monthDays = calendarHelpers.getDaysInMonth(currentMonth)
        const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
        return [{ date: currentMonth, name: monthName, days: monthDays }]
      }
    } catch (error) {
      console.error('Error calculando meses:', error)
      return []
    }
  }, [viewMode, currentMonth])

  // Renderizar encabezado de la tabla
  const renderTableHeader = (daysInMonth) => {
    const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    
    return (
      <thead>
        <tr>
          <th className="sticky left-0 z-20 px-4 py-2 bg-gray-100 border-r border-b border-gray-300 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-[140px]">
            Equipo
          </th>
          <th className="sticky left-[140px] z-20 px-4 py-2 bg-gray-100 border-r border-b border-gray-300 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider w-[140px]">
            Empleado
          </th>
          <th className="sticky left-[280px] z-20 px-3 py-2 bg-blue-100 border-r border-b border-gray-300 text-center text-xs font-semibold text-blue-800 uppercase tracking-wider w-[50px]">
            Vac
          </th>
          <th className="sticky left-[330px] z-20 px-3 py-2 bg-yellow-100 border-r border-b border-gray-300 text-center text-xs font-semibold text-yellow-800 uppercase tracking-wider w-[50px]">
            Aus
          </th>
          {daysInMonth.map((dayInfo) => (
            <th 
              key={dayInfo.day} 
              className={`px-2 py-2 border-r border-b border-gray-300 text-center text-xs font-semibold uppercase tracking-wider ${dayInfo.isWeekend ? 'bg-gray-200 text-gray-600' : 'bg-gray-100 text-gray-700'}`}
            >
              {dayInfo.day} <br /> {dayNames[dayInfo.dayOfWeek]}
            </th>
          ))}
        </tr>
      </thead>
    )
  }

  // ===== HANDLERS (definidos después de las funciones helper) =====

  // Manejo de menú contextual (click derecho)
  const handleContextMenu = (e, employeeId, employeeName, dateString, dayInfo) => {
    e.preventDefault()
    e.stopPropagation()

    // Validar que tenemos los datos necesarios
    if (!employeeId || !dateString) {
      console.warn('handleContextMenu: Faltan datos necesarios', { employeeId, dateString })
      return
    }

    const employee = employees.find(emp => emp.id === employeeId)
    if (!employee) {
      console.warn('handleContextMenu: Empleado no encontrado', { employeeId, employees })
      return
    }

    const employeeLocation = employee?.location || { country: employee?.country, region: employee?.region, city: employee?.city }
    const isHolidayDay = calendarHelpers.isHolidayHelper(dateString, employeeLocation, holidays)
    
    // Asegurar que isWeekend se calcula correctamente desde dayInfo
    // Si dayInfo no tiene isWeekend, calcularlo desde la fecha
    let isWeekendDay = dayInfo?.isWeekend
    if (isWeekendDay === undefined && dayInfo?.date) {
      const dayOfWeek = dayInfo.date.getDay()
      isWeekendDay = dayOfWeek === 0 || dayOfWeek === 6
    } else if (isWeekendDay === undefined && dateString) {
      // Si no tenemos dayInfo.date, calcular desde dateString
      const date = new Date(dateString + 'T00:00:00')
      const dayOfWeek = date.getDay()
      isWeekendDay = dayOfWeek === 0 || dayOfWeek === 6
    }

    // Buscar si ya hay actividad en este día
    const existingActivity = calendarHelpers.getActivityForDayHelper(employeeId, dateString, activities)

    // Calcular posición del menú (asegurar que esté dentro de la ventana)
    const menuX = Math.min(e.clientX, window.innerWidth - 250)
    const menuY = Math.min(e.clientY, window.innerHeight - 300)

    // Abrir menú contextual con información del día
    setContextMenu({
      visible: true,
      x: menuX,
      y: menuY,
      employeeId,
      employeeName,
      date: dateString,
      activity: existingActivity,
      isHoliday: isHolidayDay,
      isWeekend: isWeekendDay || false // Asegurar que siempre sea boolean
    })
  }

  // Manejo de long press para móvil
  const handleTouchStart = (e, employeeId, employeeName, dateString, dayInfo) => {
    longPressTimer.current = setTimeout(() => {
      // Simular click derecho después de 500ms
      const touch = e.touches[0]
      const fakeEvent = {
        preventDefault: () => {},
        clientX: touch.clientX,
        clientY: touch.clientY
      }
      // Asegurar que dayInfo se pasa correctamente
      handleContextMenu(fakeEvent, employeeId, employeeName, dateString, dayInfo || {})
      
      // Feedback háptico si está disponible
      if (navigator.vibrate) {
        navigator.vibrate(50)
      }
    }, 500)
  }

  const handleTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
    }
  }

  // Manejo de selección en menú contextual
  const handleMenuSelect = (option) => {
    if (option === 'delete') {
      handleDeleteActivity()
      return
    }

    // Mapear códigos del menú contextual a tipos de actividad del modal
    const codeToTypeMap = {
      'v': 'vacation',
      'a': 'sick_leave',
      'hld': 'hld',
      'g': 'guard',
      'f': 'training',
      'c': 'other'
    }
    
    const activityType = codeToTypeMap[option] || 'other'
    const isGuard = activityType === 'guard'
    
    // Solo guardias se permiten en festivos/fines de semana
    if ((contextMenu.isHoliday || contextMenu.isWeekend) && !isGuard) {
      toast({
        title: "⚠️ Día no laborable",
        description: "Solo puedes marcar Guardias en festivos o fines de semana",
        variant: "destructive"
      })
      return
    }

    // Abrir modal para crear actividad
    setActivityModal({
      visible: true,
      type: activityType,
      date: contextMenu.date,
      employeeId: contextMenu.employeeId,
      employeeName: contextMenu.employeeName
    })
  }

  // Guardar actividad desde el modal
  const handleSaveActivity = async (activityData) => {
    try {
      // Mapear tipos del modal a códigos del backend
      const typeToCodeMap = {
        'vacation': 'V',
        'sick_leave': 'A',
        'hld': 'HLD',
        'guard': 'G',
        'training': 'F',
        'other': 'C'
      }
      
      const activityCode = typeToCodeMap[activityData.activityType] || 'C'
      
      // Callback al componente padre para guardar en backend
      if (onActivityCreate) {
        await onActivityCreate({
          employee_id: activityModal.employeeId,
          date: activityModal.date,
          activity_type: activityCode, // Enviar código al backend (V, A, G, etc.)
          hours: activityData.hours || null,
          start_time: activityData.startTime || null,
          end_time: activityData.endTime || null,
          description: activityData.notes || ''
        })
      }

      toast({
        title: "✅ Actividad guardada",
        description: `${activityCode} marcado correctamente`,
      })

      setActivityModal({ visible: false, type: null, date: null, employeeId: null, employeeName: null })
    } catch (error) {
      toast({
        title: "❌ Error",
        description: error.message || "No se pudo guardar la actividad",
        variant: "destructive"
      })
    }
  }

  // Eliminar actividad
  const handleDeleteActivity = async () => {
    if (!contextMenu.activity) return

    // Confirmación
    if (!window.confirm(`¿Eliminar ${contextMenu.activity.type.toUpperCase()} del ${new Date(contextMenu.date).toLocaleDateString('es-ES')}?`)) {
      return
    }

    try {
      // Callback al componente padre para eliminar en backend
      if (onActivityDelete) {
        await onActivityDelete(contextMenu.activity.id)
      }

      toast({
        title: "🗑️ Actividad eliminada",
        description: "La actividad ha sido eliminada correctamente",
      })
    } catch (error) {
      toast({
        title: "❌ Error",
        description: error.message || "No se pudo eliminar la actividad",
        variant: "destructive"
      })
    }
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
            {calculatedMonths && Array.isArray(calculatedMonths) && calculatedMonths.length > 0 ? (
              calculatedMonths.map((month) => (
                <div key={month.date.toISOString()} className="mb-8">
                  {viewMode === 'annual' && (
                    <div className="sticky left-0 z-10 px-4 py-2 bg-gray-50 border-b border-gray-300">
                      <h3 className="text-lg font-semibold capitalize text-gray-900">{month.name}</h3>
                    </div>
                  )}
                  
                  <table className="w-full border-collapse text-sm">
                    {renderTableHeader(month.days)}
                    <tbody>
                      {employees && employees.length > 0 ? (
                        employees.map(employee => {
                          if (!employee || !month.date) return null
                          const summary = calendarHelpers.getMonthSummaryHelper(employee.id, month.date, activities)
                          const monthDays = calendarHelpers.getDaysInMonth(month.date)
                          
                          return (
                            <tr key={`${employee.id}-${month.date.toISOString()}`} className="hover:bg-gray-50">
                              {/* Equipo */}
                              <td className="sticky left-0 z-10 px-4 py-3 bg-white border-r border-b border-gray-300 font-medium text-sm text-gray-900 whitespace-nowrap">
                                {employee.team_name || 'Sin equipo'}
                              </td>
                              
                              {/* Empleado */}
                              <td className="sticky left-[140px] z-10 px-4 py-3 bg-white border-r border-b border-gray-300 font-medium text-sm text-gray-900 whitespace-nowrap">
                                {employee.full_name}
                              </td>
                              
                              {/* Vac (Vacaciones) */}
                              <td className="sticky left-[280px] z-10 px-3 py-3 bg-blue-50 border-r border-b border-gray-300 text-center font-semibold text-sm text-gray-900">
                                {summary.vacation}
                              </td>
                              
                              {/* Aus (Ausencias) */}
                              <td className="sticky left-[330px] z-10 px-3 py-3 bg-yellow-50 border-r border-b border-gray-300 text-center font-semibold text-sm text-gray-900">
                                {summary.absence}
                              </td>
                              
                              {/* Días del mes (1-31) */}
                              {monthDays.map((dayInfo) => {
                                const activity = calendarHelpers.getActivityForDayHelper(employee.id, dayInfo.dateString, activities)
                                const employeeLocation = employee.location || { country: employee.country, region: employee.region, city: employee.city }
                                const isHolidayDay = calendarHelpers.isHolidayHelper(dayInfo.dateString, employeeLocation, holidays)
                                const bgColor = calendarHelpers.getCellBackgroundColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                const textColor = calendarHelpers.getCellTextColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                const code = calendarHelpers.getActivityCodeHelper(activity)
                                
                                return (
                                  <td
                                    key={dayInfo.day}
                                    className={`px-2 py-3 border-r border-b border-gray-200 text-center text-xs font-medium ${bgColor} ${textColor} cursor-pointer hover:opacity-80 transition-opacity select-none`}
                                    onMouseEnter={() => setHoveredDay(dayInfo.dateString)}
                                    onMouseLeave={() => setHoveredDay(null)}
                                    onContextMenu={(e) => handleContextMenu(e, employee.id, employee.full_name, dayInfo.dateString, dayInfo)}
                                    onTouchStart={(e) => handleTouchStart(e, employee.id, employee.full_name, dayInfo.dateString, dayInfo)}
                                    onTouchEnd={handleTouchEnd}
                                    title={activity ? `${activity.type}: ${activity.notes || ''}` : (isHolidayDay ? 'Festivo' : (dayInfo.isWeekend ? 'Fin de semana' : 'Click derecho para marcar'))}
                                  >
                                    {code}
                                  </td>
                                )
                              })}
                            </tr>
                          )
                        })
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
                      {calendarHelpers.getMonthHolidaysHelper(month.date, holidays).length > 0 ? (
                        calendarHelpers.getMonthHolidaysHelper(month.date, holidays).map((holiday) => {
                          const day = new Date(holiday.date).getDate()
                          return (
                            <Badge key={holiday.id} variant="outline" className="bg-red-50 text-red-700 border-red-300">
                              Día {day}: {holiday.name} ({holiday.holiday_type === 'national' ? 'Nacional' : holiday.holiday_type === 'regional' ? 'Regional' : 'Local'})
                            </Badge>
                          )
                        })
                      ) : (
                        <span className="text-xs text-gray-500">No hay festivos este mes</span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-4 py-8 text-center text-gray-500">
                No hay datos de calendario para mostrar.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Leyenda de códigos - Compacta en 1-2 líneas */}
      <Card>
        <CardContent className="p-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-green-100 border border-green-300 rounded flex items-center justify-center text-[10px] font-bold text-green-700">V</div>
              <span className="text-gray-700">Vacaciones</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-yellow-100 border border-yellow-300 rounded flex items-center justify-center text-[10px] font-bold text-yellow-700">A</div>
              <span className="text-gray-700">Ausencias</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-green-200 border border-green-400 rounded flex items-center justify-center text-[10px] font-bold text-green-800">HLD</div>
              <span className="text-gray-700">HLD</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-blue-100 border border-blue-300 rounded flex items-center justify-center text-[10px] font-bold text-blue-700">G</div>
              <span className="text-gray-700">Guardia</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-purple-100 border border-purple-300 rounded flex items-center justify-center text-[10px] font-bold text-purple-700">F</div>
              <span className="text-gray-700">Formación</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-sky-100 border border-sky-300 rounded flex items-center justify-center text-[10px] font-bold text-sky-700">C</div>
              <span className="text-gray-700">Otro</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-red-50 border border-red-200 rounded flex items-center justify-center text-[10px] font-bold text-red-700">🔴</div>
              <span className="text-gray-700">Festivo</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-5 h-5 bg-gray-100 border border-gray-200 rounded flex items-center justify-center text-[10px] font-bold text-gray-500">□</div>
              <span className="text-gray-700">Fin Semana</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Menú contextual */}
      <ContextMenu
        visible={contextMenu.visible}
        x={contextMenu.x}
        y={contextMenu.y}
        hasActivity={!!contextMenu.activity}
        onSelect={handleMenuSelect}
        onClose={() => setContextMenu({ ...contextMenu, visible: false })}
      />

      {/* Modal de actividad */}
      <ActivityModal
        visible={activityModal.visible}
        activityType={activityModal.type}
        date={activityModal.date}
        employeeName={activityModal.employeeName}
        onSave={handleSaveActivity}
        onCancel={() => setActivityModal({ visible: false, type: null, date: null, employeeId: null, employeeName: null })}
      />
    </div>
  )
}

export default CalendarTableView

