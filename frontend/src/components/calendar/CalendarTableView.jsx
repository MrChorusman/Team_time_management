import { useState, useEffect, useRef, useMemo, useCallback, memo } from 'react'
import { ChevronLeft, ChevronRight, CalendarDays, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'
import ContextMenu from './ContextMenu'
import ActivityModal from './ActivityModal'

// ===== FUNCIONES HELPER INLINEADAS =====
// Movidas directamente al componente para evitar problemas de evaluación durante el bundling

// Mapeo completo bidireccional de países (inglés/español/códigos ISO)
var _COUNTRY_MAPPING = null
function getCountryMapping() {
  if (!_COUNTRY_MAPPING) {
    _COUNTRY_MAPPING = {
      'ES': { en: 'Spain', es: 'España' },
      'ESP': { en: 'Spain', es: 'España' },
      'US': { en: 'United States', es: 'Estados Unidos' },
      'USA': { en: 'United States', es: 'Estados Unidos' },
      'GB': { en: 'United Kingdom', es: 'Reino Unido' },
      'GBR': { en: 'United Kingdom', es: 'Reino Unido' },
      'FR': { en: 'France', es: 'Francia' },
      'FRA': { en: 'France', es: 'Francia' },
      'DE': { en: 'Germany', es: 'Alemania' },
      'DEU': { en: 'Germany', es: 'Alemania' },
      'IT': { en: 'Italy', es: 'Italia' },
      'ITA': { en: 'Italy', es: 'Italia' },
      'PT': { en: 'Portugal', es: 'Portugal' },
      'PRT': { en: 'Portugal', es: 'Portugal' },
      'MX': { en: 'Mexico', es: 'México' },
      'AR': { en: 'Argentina', es: 'Argentina' },
      'CO': { en: 'Colombia', es: 'Colombia' },
      'CL': { en: 'Chile', es: 'Chile' },
      'PE': { en: 'Peru', es: 'Perú' },
      'VE': { en: 'Venezuela', es: 'Venezuela' },
      'EC': { en: 'Ecuador', es: 'Ecuador' },
      'BO': { en: 'Bolivia', es: 'Bolivia' },
      'PY': { en: 'Paraguay', es: 'Paraguay' },
      'UY': { en: 'Uruguay', es: 'Uruguay' },
      'CR': { en: 'Costa Rica', es: 'Costa Rica' },
      'PA': { en: 'Panama', es: 'Panamá' },
      'DO': { en: 'Dominican Republic', es: 'República Dominicana' },
      'CA': { en: 'Canada', es: 'Canadá' },
      'BR': { en: 'Brazil', es: 'Brasil' },
      'AU': { en: 'Australia', es: 'Australia' },
      'NZ': { en: 'New Zealand', es: 'Nueva Zelanda' },
      'NL': { en: 'Netherlands', es: 'Países Bajos' },
      'BE': { en: 'Belgium', es: 'Bélgica' },
      'CH': { en: 'Switzerland', es: 'Suiza' },
      'AT': { en: 'Austria', es: 'Austria' },
      'SE': { en: 'Sweden', es: 'Suecia' },
      'NO': { en: 'Norway', es: 'Noruega' },
      'DK': { en: 'Denmark', es: 'Dinamarca' },
      'FI': { en: 'Finland', es: 'Finlandia' },
      'PL': { en: 'Poland', es: 'Polonia' },
      'GR': { en: 'Greece', es: 'Grecia' },
      'IE': { en: 'Ireland', es: 'Irlanda' }
    }
  }
  return _COUNTRY_MAPPING
}

function normalizeCountryName(countryInput) {
  if (!countryInput) return null
  const COUNTRY_MAPPING = getCountryMapping()
  const input = String(countryInput).trim()
  if (input.length === 2 && input.toUpperCase() in COUNTRY_MAPPING) {
    return COUNTRY_MAPPING[input.toUpperCase()].en
  }
  if (input.length === 3) {
    const iso3ToIso2 = {
      'ESP': 'ES', 'USA': 'US', 'GBR': 'GB', 'FRA': 'FR',
      'DEU': 'DE', 'ITA': 'IT', 'PRT': 'PT'
    }
    if (input.toUpperCase() in iso3ToIso2) {
      const code = iso3ToIso2[input.toUpperCase()]
      return COUNTRY_MAPPING[code].en
    }
  }
  const inputLower = input.toLowerCase()
  const countryCodes = Object.keys(COUNTRY_MAPPING)
  for (let i = 0; i < countryCodes.length; i++) {
    const code = countryCodes[i]
    const names = COUNTRY_MAPPING[code]
    if (names.en.toLowerCase() === inputLower || names.es.toLowerCase() === inputLower) {
      return names.en
    }
  }
  for (let i = 0; i < countryCodes.length; i++) {
    const code = countryCodes[i]
    const names = COUNTRY_MAPPING[code]
    if (inputLower.includes(names.en.toLowerCase()) || names.en.toLowerCase().includes(inputLower) ||
        inputLower.includes(names.es.toLowerCase()) || names.es.toLowerCase().includes(inputLower)) {
      return names.en
    }
  }
  return input
}

function getCountryVariants(countryInput) {
  if (!countryInput) return null
  const normalized = normalizeCountryName(countryInput)
  if (!normalized) return null
  const COUNTRY_MAPPING = getCountryMapping()
  const countryCodes = Object.keys(COUNTRY_MAPPING)
  for (let i = 0; i < countryCodes.length; i++) {
    const code = countryCodes[i]
    if (COUNTRY_MAPPING[code].en === normalized || COUNTRY_MAPPING[code].es === normalized) {
      return {
        en: COUNTRY_MAPPING[code].en,
        es: COUNTRY_MAPPING[code].es,
        code: code
      }
    }
  }
  return { en: normalized, es: normalized, code: null }
}

function doesHolidayApplyToLocation(holiday, employeeLocation) {
  if (!holiday || !employeeLocation?.country) return false
  const employeeVariants = getCountryVariants(employeeLocation.country)
  const holidayVariants = getCountryVariants(holiday.country)
  const employeeCountries = employeeVariants
    ? [employeeVariants.en, employeeVariants.es, employeeLocation.country].filter(Boolean)
    : [employeeLocation.country].filter(Boolean)
  const holidayCountries = holidayVariants
    ? [holidayVariants.en, holidayVariants.es, holiday.country].filter(Boolean)
    : [holiday.country].filter(Boolean)
  const countriesMatch = employeeCountries.some(empCountry =>
    holidayCountries.some(holCountry =>
      normalizeCountryName(empCountry) === normalizeCountryName(holCountry) ||
      empCountry === holCountry
    )
  )
  if (!countriesMatch) return false
  const holidayType = holiday.holiday_type || holiday.type || holiday.hierarchy_level || ''
  const holidayRegion = holiday.region
  const holidayCity = holiday.city
  const employeeRegion = employeeLocation.region || employeeLocation.location?.region
  const employeeCity = employeeLocation.city || employeeLocation.location?.city
  if (holidayType === 'national' || !holidayRegion) {
    return true
  }
  if (holidayType === 'regional') {
    return holidayRegion === employeeRegion
  }
  if (holidayType === 'local') {
    return holidayRegion === employeeRegion && holidayCity === employeeCity
  }
  return true
}

function countriesMatch(country1, country2) {
  if (!country1 || !country2) return false
  const norm1 = normalizeCountryName(country1)
  const norm2 = normalizeCountryName(country2)
  if (norm1 && norm2) {
    return norm1.toLowerCase() === norm2.toLowerCase()
  }
  return String(country1).toLowerCase() === String(country2).toLowerCase()
}

var _ISO_TO_COUNTRY_NAME = null
function getIsoToCountryName() {
  if (!_ISO_TO_COUNTRY_NAME) {
    _ISO_TO_COUNTRY_NAME = {
      'ESP': 'España',
      'ES': 'España',
      'USA': 'United States',
      'US': 'United States',
      'GBR': 'United Kingdom',
      'GB': 'United Kingdom',
      'FRA': 'France',
      'FR': 'France',
      'DEU': 'Germany',
      'DE': 'Germany',
      'ITA': 'Italy',
      'IT': 'Italy',
      'PRT': 'Portugal',
      'PT': 'Portugal'
    }
  }
  return _ISO_TO_COUNTRY_NAME
}

function formatDateLocal(year, month, day) {
  const monthStr = String(month + 1).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  return `${year}-${monthStr}-${dayStr}`
}

function getDaysInMonth(date) {
  const year = date.getFullYear()
  const month = date.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days = []
  for (let day = 1; day <= daysInMonth; day++) {
    const currentDate = new Date(year, month, day)
    const dateString = formatDateLocal(year, month, day)
    days.push({
      day,
      date: currentDate,
      dayOfWeek: currentDate.getDay(),
      isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6,
      dateString: dateString
    })
  }
  return days
}

function getMonthsInYear(date) {
  const year = date.getFullYear()
  const months = []
  for (let month = 0; month < 12; month++) {
    const monthDate = new Date(year, month, 1)
    const days = getDaysInMonth(monthDate)
    months.push({
      date: monthDate,
      name: monthDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }),
      days: days
    })
  }
  return months
}

function isHolidayHelper(dateString, employeeLocation, holidays) {
  if (!holidays || !Array.isArray(holidays) || !employeeLocation) return false
  const employeeCountryInput = employeeLocation?.country || ''
  const employeeVariants = getCountryVariants(employeeCountryInput)
  const employeeCountries = employeeVariants 
    ? [employeeVariants.en, employeeVariants.es, employeeLocation?.country].filter(Boolean)
    : [employeeLocation?.country].filter(Boolean)
  return holidays.some(holiday => {
    if (holiday.date !== dateString) return false
    const holidayVariants = getCountryVariants(holiday.country)
    const holidayCountries = holidayVariants
      ? [holidayVariants.en, holidayVariants.es, holiday.country].filter(Boolean)
      : [holiday.country].filter(Boolean)
    const countriesMatch = employeeCountries.some(empCountry => 
      holidayCountries.some(holCountry => 
        normalizeCountryName(empCountry) === normalizeCountryName(holCountry) ||
        empCountry === holCountry
      )
    )
    if (!countriesMatch) return false
    const holidayType = holiday.holiday_type || holiday.type || ''
    if (holidayType === 'national') {
      return true
    }
    if (holidayType === 'regional') {
      return holiday.region === employeeLocation?.region
    }
    if (holidayType === 'local') {
      return holiday.region === employeeLocation?.region &&
             holiday.city === employeeLocation?.city
    }
    return true
  })
}

function getActivityForDayHelper(employeeId, dateString, activities) {
  if (!activities || !Array.isArray(activities)) return null
  return activities.find(activity => {
    if (!activity || activity.employee_id !== employeeId) return false
    const activityDate = activity.date || activity.start_date || activity.end_date
    if (!activityDate) return false
    if (activity.date === dateString) return true
    if (activity.start_date && activity.end_date) {
      return activity.start_date <= dateString && activity.end_date >= dateString
    }
    return false
  })
}

function getActivityCodeHelper(activity) {
  if (!activity) return ''
  const activityType = activity.activity_type || activity.type || ''
  if (!activityType) return ''
  let code = ''
  const typeUpper = activityType.toUpperCase()
  const typeLower = activityType.toLowerCase()
  if (typeUpper === 'V' || typeLower === 'vacation') {
    code = 'V'
  } else if (typeUpper === 'A' || typeLower === 'absence' || typeLower === 'sick_leave') {
    code = 'A'
  } else if (typeUpper === 'HLD' || typeLower === 'hld') {
    code = 'HLD'
  } else if (typeUpper === 'G' || typeLower === 'guard') {
    code = 'G'
  } else if (typeUpper === 'F' || typeLower === 'training') {
    code = 'F'
  } else if (typeUpper === 'C' || typeLower === 'other') {
    code = 'C'
  } else {
    code = activityType.charAt(0).toUpperCase()
  }
  if (activity.hours) {
    const hasHours = typeUpper === 'HLD' || typeUpper === 'G' || typeUpper === 'F' || 
                     typeLower === 'hld' || typeLower === 'guard' || typeLower === 'training'
    if (hasHours) {
      const sign = (typeUpper === 'G' || typeLower === 'guard') ? '+' : '-'
      return `${code} ${sign}${activity.hours}h`
    }
  }
  return code
}

function getCellBackgroundColorHelper(activity, isWeekend, isHolidayDay) {
  if (isHolidayDay) return 'bg-red-50 border-red-200'
  if (isWeekend) return 'bg-gray-100 border-gray-200'
  if (!activity) return 'bg-white border-gray-200'
  const activityType = (activity.activity_type || activity.type || '').toLowerCase()
  if (activityType === 'vacation' || activityType === 'v') {
    return 'bg-green-100 border-green-300'
  } else if (activityType === 'sick_leave' || activityType === 'absence' || activityType === 'a') {
    return 'bg-yellow-100 border-yellow-300'
  } else if (activityType === 'hld') {
    return 'bg-green-200 border-green-400'
  } else if (activityType === 'guard' || activityType === 'g') {
    return 'bg-blue-100 border-blue-300'
  } else if (activityType === 'training' || activityType === 'f') {
    return 'bg-purple-100 border-purple-300'
  } else if (activityType === 'other' || activityType === 'c') {
    return 'bg-sky-100 border-sky-300'
  }
  return 'bg-gray-100 border-gray-300'
}

function getCellTextColorHelper(activity, isWeekend, isHolidayDay) {
  if (isHolidayDay) return 'text-red-700'
  if (isWeekend) return 'text-gray-500'
  if (!activity) return 'text-gray-900'
  const activityType = (activity.activity_type || activity.type || '').toLowerCase()
  if (activityType === 'vacation' || activityType === 'v') {
    return 'text-green-700'
  } else if (activityType === 'sick_leave' || activityType === 'absence' || activityType === 'a') {
    return 'text-yellow-700'
  } else if (activityType === 'hld') {
    return 'text-green-800'
  } else if (activityType === 'guard' || activityType === 'g') {
    return 'text-blue-700'
  } else if (activityType === 'training' || activityType === 'f') {
    return 'text-purple-700'
  } else if (activityType === 'other' || activityType === 'c') {
    return 'text-sky-700'
  }
  return 'text-gray-700'
}

function getMonthSummaryHelper(employeeId, monthDate, activities) {
  if (!activities || !Array.isArray(activities)) return { vacation: 0, absence: 0 }
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const monthStart = formatDateLocal(year, month, 1)
  const lastDay = new Date(year, month + 1, 0).getDate()
  const monthEnd = formatDateLocal(year, month, lastDay)
  const monthActivities = activities.filter(activity => {
    if (!activity || activity.employee_id !== employeeId) return false
    const activityDate = activity.date || activity.start_date || activity.end_date
    if (!activityDate) return false
    if (activity.date) {
      return activity.date >= monthStart && activity.date <= monthEnd
    } else if (activity.start_date && activity.end_date) {
      return (activity.start_date >= monthStart && activity.start_date <= monthEnd) ||
             (activity.end_date >= monthStart && activity.end_date <= monthEnd) ||
             (activity.start_date <= monthStart && activity.end_date >= monthEnd)
    }
    return false
  })
  let vacationDays = 0
  let absenceDays = 0
  monthActivities.forEach(activity => {
    const activityType = activity.activity_type || activity.type
    if (activity.date) {
      if (activityType === 'V' || activityType === 'vacation') vacationDays += 1
      if (activityType === 'A' || activityType === 'absence' || activityType === 'sick_leave') absenceDays += 1
    } else if (activity.start_date && activity.end_date) {
      const activityStart = new Date(activity.start_date)
      const activityEnd = new Date(activity.end_date)
      const rangeStart = new Date(Math.max(activityStart, new Date(monthStart)))
      const rangeEnd = new Date(Math.min(activityEnd, new Date(monthEnd)))
      const days = Math.ceil((rangeEnd - rangeStart) / (1000 * 60 * 60 * 24)) + 1
      if (activityType === 'V' || activityType === 'vacation') vacationDays += days
      if (activityType === 'A' || activityType === 'absence' || activityType === 'sick_leave') absenceDays += days
    }
  })
  return { vacation: vacationDays, absence: absenceDays }
}

function getMonthHolidaysHelper(monthDate, holidays) {
  if (!holidays || !Array.isArray(holidays)) return []
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const monthStart = formatDateLocal(year, month, 1)
  const lastDay = new Date(year, month + 1, 0).getDate()
  const monthEnd = formatDateLocal(year, month, lastDay)
  const monthHolidays = holidays.filter(holiday => 
    holiday && holiday.date >= monthStart && holiday.date <= monthEnd
  )
  return monthHolidays.sort((a, b) => {
    if (a.date < b.date) return -1
    if (a.date > b.date) return 1
    return 0
  })
}
// ===== FIN FUNCIONES HELPER =====

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
// Las funciones helper están inlineadas directamente en este archivo para evitar problemas de bundling
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
  const longPressTimer = useRef(null)
  const { toast } = useToast()

  // Función helper para calcular días del mes (fallback cuando calendarHelpers no está disponible)
  const calculateDaysInMonthFallback = (date) => {
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
        dateString: `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      })
    }
    return days
  }

  // Calcular meses usando useMemo - funciones helper están inlineadas
  const calculatedMonths = useMemo(() => {
    try {
      if (viewMode === 'annual') {
        return getMonthsInYear(currentMonth) || []
      } else {
        const monthDays = getDaysInMonth(currentMonth)
        const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
        return [{ date: currentMonth, name: monthName, days: monthDays }]
      }
    } catch (error) {
      console.error('Error calculando meses:', error)
      const monthName = currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
      const days = calculateDaysInMonthFallback(currentMonth)
      return viewMode === 'annual' ? [] : [{ date: currentMonth, name: monthName, days }]
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
    
    // Verificar si es festivo
    const isHolidayDay = isHolidayHelper(dateString, employeeLocation, holidays)
    
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
    const existingActivity = getActivityForDayHelper(employeeId, dateString, activities)

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

  // Eliminar actividad - memoizado (MOVIDO ANTES de handleMenuSelect para evitar referencia antes de inicialización)
  const handleDeleteActivity = useCallback(async () => {
    if (!contextMenu.activity) return

    // Obtener el código de actividad
    const activityCode = getActivityCodeHelper(contextMenu.activity) || 'ACT'

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
                          
                          const summary = getMonthSummaryHelper(employee.id, month.date, activities)
                          const monthDays = month.days || []
                          
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
                                const activity = getActivityForDayHelper(employee.id, dayInfo.dateString, activities)
                                const employeeLocation = employee.location || { country: employee.country, region: employee.region, city: employee.city }
                                const isHolidayDay = isHolidayHelper(dayInfo.dateString, employeeLocation, holidays)
                                const bgColor = getCellBackgroundColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                const textColor = getCellTextColorHelper(activity, dayInfo.isWeekend, isHolidayDay)
                                const code = getActivityCodeHelper(activity)
                                
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
                        // Obtener festivos del mes
                        const monthHolidays = getMonthHolidaysHelper(month.date, holidays)
                        
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
                        const relevantHolidays = employeeLocations.length > 0
                          ? monthHolidays.filter(holiday =>
                              employeeLocations.some(location =>
                                doesHolidayApplyToLocation(holiday, location)
                              )
                            )
                          : monthHolidays
                        
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

