import { useState, useEffect, useRef, useMemo, useCallback, memo } from 'react'
import { ChevronLeft, ChevronRight, CalendarDays, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'
import ContextMenu from './ContextMenu'
import ActivityModal from './ActivityModal'
// Importar usando importación dinámica para evitar problemas de inicialización durante el bundling
// Esto asegura que el módulo se carga solo cuando se necesita, no durante la evaluación del módulo
let calendarHelpersModule = null
let calendarHelpersPromise = null

// Función helper para obtener calendarHelpers de forma segura usando importación dinámica
const getCalendarHelpers = async () => {
  try {
    // Si ya tenemos el módulo cargado, retornarlo directamente
    if (calendarHelpersModule) {
      return calendarHelpersModule
    }
    
    // Si hay una promesa de carga en curso, esperarla
    if (calendarHelpersPromise) {
      return await calendarHelpersPromise
    }
    
    // Cargar el módulo de forma dinámica
    calendarHelpersPromise = import('./calendarHelpers').then(module => {
      // El módulo ahora exporta el objeto directamente, no una función
      const helpers = module.default
      if (!helpers || typeof helpers.getMonthsInYear !== 'function') {
        console.warn('calendarHelpers no tiene las funciones necesarias')
        return null
      }
      calendarHelpersModule = helpers
      return helpers
    }).catch(error => {
      console.warn('Error cargando calendarHelpers:', error)
      return null
    })
    
    return await calendarHelpersPromise
  } catch (error) {
    console.warn('Error obteniendo calendarHelpers:', error)
    return null
  }
}

// Versión síncrona para uso inmediato (retorna null si no está cargado)
const getCalendarHelpersSync = () => {
  return calendarHelpersModule
}

// NO destructurar al inicio - usar directamente desde el objeto para evitar problemas de inicialización
// Usar una función que siempre obtenga la referencia más reciente

/**
 * CalendarTableView - Calendario tipo tabla/spreadsheet
 * 
 * Estructura:
 * - Filas: Empleados
 * - Columnas: Equipo | Empleado | Vac | Aus | 1 | 2 | 3 | ... | 31
 * - Vista mensual o anual
 */
// Las funciones helper están ahora en calendarHelpers.js para evitar problemas de inicialización
const CalendarTableView = ({ employees, activities, holidays, currentMonth, onMonthChange, onActivityCreate, onActivityDelete, onViewModeChange, viewMode: externalViewMode }) => {
  // Usar viewMode externo si se proporciona, sino usar estado local
  const [internalViewMode, setInternalViewMode] = useState('monthly')
  const viewMode = externalViewMode !== undefined ? externalViewMode : internalViewMode
  
  // Notificar al padre cuando cambia el modo de vista (solo si usamos estado interno)
  useEffect(() => {
    if (externalViewMode === undefined && onViewModeChange) {
      onViewModeChange(internalViewMode)
    }
  }, [internalViewMode, onViewModeChange, externalViewMode])
  
  // Handler para cambiar el modo de vista
  const handleViewModeChange = (newMode) => {
    if (externalViewMode !== undefined) {
      // Si el modo viene del padre, notificar el cambio
      if (onViewModeChange) {
        onViewModeChange(newMode)
      }
    } else {
      // Si usamos estado interno, actualizarlo
      setInternalViewMode(newMode)
    }
  }
  const [hoveredDay, setHoveredDay] = useState(null)
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, employeeId: null, date: null, activity: null })
  const [activityModal, setActivityModal] = useState({ visible: false, type: null, date: null, employeeId: null, employeeName: null })
  const [loadedHelpers, setLoadedHelpers] = useState(null)
  const longPressTimer = useRef(null)
  const { toast } = useToast()

  // Cargar calendarHelpers cuando el componente se monta
  useEffect(() => {
    getCalendarHelpers().then(helpers => {
      if (helpers) {
        setLoadedHelpers(helpers)
      }
    }).catch(error => {
      console.error('Error cargando calendarHelpers:', error)
    })
  }, [])

  // Calcular meses usando useMemo en lugar de IIFE para mejor compatibilidad con minificación
  // Usar funciones directamente desde calendarHelpers sin destructurar
  // Validar que calendarHelpers esté completamente inicializado antes de usarlo
  const calculatedMonths = useMemo(() => {
    try {
      // Obtener calendarHelpers de forma segura (versión síncrona)
      const helpers = loadedHelpers || getCalendarHelpersSync()
      
      // Validar que calendarHelpers y sus funciones estén disponibles
      if (!helpers || typeof helpers.getMonthsInYear !== 'function' || typeof helpers.getDaysInMonth !== 'function') {
        console.warn('calendarHelpers no está completamente inicializado, usando valores por defecto')
        // Retornar estructura básica para evitar errores
        const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
        const year = currentMonth.getFullYear()
        const month = currentMonth.getMonth()
        const daysInMonth = new Date(year, month + 1, 0).getDate()
        const days = []
        for (let day = 1; day <= daysInMonth; day++) {
          const currentDate = new Date(year, month, day)
          days.push({
            day,
            date: currentDate,
            dayOfWeek: currentDate.getDay(),
            isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6,
            dateString: `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
          })
        }
        return viewMode === 'annual' ? [] : [{ date: currentMonth, name: monthName, days }]
      }
      
      if (viewMode === 'annual') {
        return helpers.getMonthsInYear(currentMonth) || []
      } else {
        const monthDays = helpers.getDaysInMonth(currentMonth)
        const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
        return [{ date: currentMonth, name: monthName, days: monthDays }]
      }
    } catch (error) {
      console.error('Error calculando meses:', error)
      return []
    }
  }, [viewMode, currentMonth, loadedHelpers])

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

  // ===== HANDLERS OPTIMIZADOS CON useCallback =====

  // Manejo de menú contextual (click derecho) - memoizado
  const handleContextMenu = useCallback((e, employeeId, employeeName, dateString, dayInfo) => {
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
    const helpers = loadedHelpers || getCalendarHelpersSync()
    
    // Verificar si es festivo
    let isHolidayDay = false
    if (helpers && typeof helpers.isHolidayHelper === 'function') {
      isHolidayDay = helpers.isHolidayHelper(dateString, employeeLocation, holidays)
    }
    
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
    let existingActivity = null
    if (helpers && typeof helpers.getActivityForDayHelper === 'function') {
      existingActivity = helpers.getActivityForDayHelper(employeeId, dateString, activities)
    }

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
  }, [employees, activities, holidays])

  // Manejo de long press para móvil - memoizado
  const handleTouchStart = useCallback((e, employeeId, employeeName, dateString, dayInfo) => {
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
  }, [handleContextMenu])

  const handleTouchEnd = useCallback(() => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
    }
  }, [])

  // Manejo de selección en menú contextual - memoizado
  const handleMenuSelect = useCallback((option) => {
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
  }, [contextMenu, toast, handleDeleteActivity])

  // Guardar actividad desde el modal - memoizado
  const handleSaveActivity = useCallback(async (activityData) => {
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
  }, [activityModal, toast, onActivityCreate])

  // Eliminar actividad - memoizado
  const handleDeleteActivity = useCallback(async () => {
    if (!contextMenu.activity) return

    // Obtener el tipo de actividad (puede ser activity_type o type)
    const activityType = contextMenu.activity.activity_type || contextMenu.activity.type || 'actividad'
    let activityCode = activityType.toUpperCase()
    const helpers = loadedHelpers || getCalendarHelpersSync()
    if (helpers && typeof helpers.getActivityCodeHelper === 'function') {
      activityCode = helpers.getActivityCodeHelper(contextMenu.activity) || activityCode
    }

    // Confirmación
    if (!window.confirm(`¿Eliminar ${activityCode} del ${new Date(contextMenu.date).toLocaleDateString('es-ES')}?`)) {
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
  }, [contextMenu, toast, onActivityDelete])

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
              onClick={() => handleViewModeChange('monthly')}
              className="flex items-center space-x-1"
            >
              <CalendarDays className="w-4 h-4" />
              <span>Mensual</span>
            </Button>
            <Button
              variant={viewMode === 'annual' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleViewModeChange('annual')}
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
                          
                          // Validar calendarHelpers antes de usarlo
                          const helpers = loadedHelpers || getCalendarHelpersSync()
                          let summary = { vacation: 0, absence: 0 }
                          let monthDays = month.days || []
                          
                          if (helpers && typeof helpers.getMonthSummaryHelper === 'function') {
                            summary = helpers.getMonthSummaryHelper(employee.id, month.date, activities)
                          }
                          if (helpers && typeof helpers.getDaysInMonth === 'function') {
                            monthDays = helpers.getDaysInMonth(month.date)
                          }
                          
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
                                // Validar calendarHelpers antes de usarlo
                                const helpers = loadedHelpers || getCalendarHelpersSync()
                                let activity = null
                                let isHolidayDay = false
                                let bgColor = 'bg-white border-gray-200'
                                let textColor = 'text-gray-900'
                                let code = ''
                                
                                if (helpers && typeof helpers.getActivityForDayHelper === 'function') {
                                  activity = helpers.getActivityForDayHelper(employee.id, dayInfo.dateString, activities)
                                }
                                
                                const employeeLocation = employee.location || { country: employee.country, region: employee.region, city: employee.city }
                                
                                if (helpers && typeof helpers.isHolidayHelper === 'function') {
                                  isHolidayDay = helpers.isHolidayHelper(dayInfo.dateString, employeeLocation, holidays)
                                }
                                
                                if (helpers && typeof helpers.getCellBackgroundColorHelper === 'function') {
                                  bgColor = helpers.getCellBackgroundColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                }
                                
                                if (helpers && typeof helpers.getCellTextColorHelper === 'function') {
                                  textColor = helpers.getCellTextColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                }
                                
                                if (helpers && typeof helpers.getActivityCodeHelper === 'function') {
                                  code = helpers.getActivityCodeHelper(activity)
                                }
                                
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
                      {(() => {
                        // Obtener festivos del mes - validar calendarHelpers
                        const helpers = loadedHelpers || getCalendarHelpersSync()
                        let monthHolidays = []
                        if (helpers && typeof helpers.getMonthHolidaysHelper === 'function') {
                          monthHolidays = helpers.getMonthHolidaysHelper(month.date, holidays)
                        }
                        
                        // Construir ubicaciones de los empleados visibles (país, región, ciudad)
                        const employeeLocations = (employees || [])
                          .map(emp => ({
                            country: emp?.country || emp?.location?.country,
                            region: emp?.region || emp?.location?.region,
                            city: emp?.city || emp?.location?.city,
                            location: emp?.location
                          }))
                          .filter(location => !!location.country)
                        
                        // Filtrar festivos relevantes solo para las ubicaciones mostradas
                        let relevantHolidays = []
                        if (employeeLocations.length > 0 && helpers && typeof helpers.doesHolidayApplyToLocation === 'function') {
                          relevantHolidays = monthHolidays.filter(holiday =>
                            employeeLocations.some(location =>
                              helpers.doesHolidayApplyToLocation(holiday, location)
                            )
                          )
                        } else {
                          // Si calendarHelpers no está disponible, mostrar todos los festivos del mes
                          relevantHolidays = monthHolidays
                        }
                        
                        // Deduplicar festivos por fecha y nombre (evitar duplicados)
                        const uniqueHolidays = []
                        const seenHolidays = new Set()
                        
                        relevantHolidays.forEach(holiday => {
                          const key = `${holiday.date}-${holiday.name}`
                          if (!seenHolidays.has(key)) {
                            seenHolidays.add(key)
                            uniqueHolidays.push(holiday)
                          }
                        })
                        
                        return uniqueHolidays.length > 0 ? (
                          uniqueHolidays.map((holiday) => {
                            const day = new Date(holiday.date).getDate()
                            return (
                              <Badge key={`${holiday.id}-${holiday.date}`} variant="outline" className="bg-red-50 text-red-700 border-red-300">
                                Día {day}: {holiday.name} ({holiday.holiday_type === 'national' ? 'Nacional' : holiday.holiday_type === 'regional' ? 'Regional' : 'Local'})
                              </Badge>
                            )
                          })
                        ) : (
                          <span className="text-xs text-gray-500">No hay festivos este mes</span>
                        )
                      })()}
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

// Memoizar el componente completo para evitar re-renders innecesarios
export default memo(CalendarTableView)

