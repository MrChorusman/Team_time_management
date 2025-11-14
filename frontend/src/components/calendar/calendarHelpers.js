// Funciones helper para CalendarTableView
// Separadas en archivo independiente para evitar problemas de inicialización durante minificación

// Mapeo de códigos ISO a nombres de países
export const ISO_TO_COUNTRY_NAME = {
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

// Obtener días del mes
export function getDaysInMonth(date) {
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

// Obtener meses del año
export function getMonthsInYear(date) {
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

// Verificar si un día es festivo para un empleado específico según su ubicación
export function isHolidayHelper(dateString, employeeLocation, holidays) {
  if (!holidays || !Array.isArray(holidays) || !employeeLocation) return false
  
  // Convertir código ISO a nombre de país si es necesario
  const employeeCountryCode = employeeLocation?.country || ''
  const employeeCountry = ISO_TO_COUNTRY_NAME[employeeCountryCode] || employeeCountryCode
  
  return holidays.some(holiday => {
    // Verificar que la fecha coincida
    if (holiday.date !== dateString) return false
    
    // Usar holiday_type (la columna hierarchy_level no existe en BD)
    const holidayType = holiday.holiday_type || holiday.type || ''
    
    // Festivos nacionales se aplican a todos del mismo país
    if (holidayType === 'national') {
      return holiday.country === employeeCountry || 
             holiday.country === employeeLocation?.country
    }
    
    // Festivos regionales solo para la misma región
    if (holidayType === 'regional') {
      return (holiday.country === employeeCountry || holiday.country === employeeLocation?.country) && 
             holiday.region === employeeLocation?.region
    }
    
    // Festivos locales solo para la misma ciudad
    if (holidayType === 'local') {
      return (holiday.country === employeeCountry || holiday.country === employeeLocation?.country) && 
             holiday.region === employeeLocation?.region &&
             holiday.city === employeeLocation?.city
    }
    
    // Si no tiene tipo específico pero coincide el país, considerarlo festivo nacional
    if (holiday.country === employeeCountry || holiday.country === employeeLocation?.country) {
      return true
    }
    
    return false
  })
}

// Obtener actividades para un empleado en un día específico
export function getActivityForDayHelper(employeeId, dateString, activities) {
  if (!activities || !Array.isArray(activities)) return null
    
  return activities.find(activity => {
    if (!activity || activity.employee_id !== employeeId) return false
    
    // Usar date, start_date o end_date según lo que esté disponible
    const activityDate = activity.date || activity.start_date || activity.end_date
    if (!activityDate) return false
    
    // Si tiene date exacto, comparar directamente
    if (activity.date === dateString) return true
    
    // Si tiene rango de fechas, verificar si la fecha está en el rango
    if (activity.start_date && activity.end_date) {
      return activity.start_date <= dateString && activity.end_date >= dateString
    }
    
    return false
  })
}

// Obtener código de actividad para mostrar en la celda
export function getActivityCodeHelper(activity) {
  if (!activity) return ''
  
  // Usar activity_type o type según lo que esté disponible
  const activityType = activity.activity_type || activity.type || ''
  if (!activityType) return ''
  
  // Mapeo de tipos de actividad a códigos
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
  
  // Para actividades con horas, mostrar el número
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

// Obtener color de fondo según el tipo de actividad
export function getCellBackgroundColorHelper(activity, isWeekend, isHolidayDay) {
  if (isHolidayDay) return 'bg-red-50 border-red-200'
  if (isWeekend) return 'bg-gray-100 border-gray-200'
  
  if (!activity) return 'bg-white border-gray-200'
  
  // Usar activity_type o type según disponibilidad
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

// Obtener color de texto según el tipo de actividad
export function getCellTextColorHelper(activity, isWeekend, isHolidayDay) {
  if (isHolidayDay) return 'text-red-700'
  if (isWeekend) return 'text-gray-500'
  
  if (!activity) return 'text-gray-900'
  
  // Usar activity_type o type según disponibilidad
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

// Calcular días de vacaciones y ausencias del mes para un empleado
export function getMonthSummaryHelper(employeeId, monthDate, activities) {
  if (!activities || !Array.isArray(activities)) return { vacation: 0, absence: 0 }
  
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const monthStart = new Date(year, month, 1).toISOString().split('T')[0]
  const monthEnd = new Date(year, month + 1, 0).toISOString().split('T')[0]
  
  const monthActivities = activities.filter(activity => {
    if (!activity || activity.employee_id !== employeeId) return false
    
    // Usar date, start_date o end_date según disponibilidad
    const activityDate = activity.date || activity.start_date || activity.end_date
    if (!activityDate) return false
    
    // Verificar si la actividad está en el rango del mes
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
    // Usar activity_type o type según lo que esté disponible
    const activityType = activity.activity_type || activity.type
    
    // Para actividades de un solo día, usar date
    if (activity.date) {
      if (activityType === 'V' || activityType === 'vacation') vacationDays += 1
      if (activityType === 'A' || activityType === 'absence' || activityType === 'sick_leave') absenceDays += 1
    } else if (activity.start_date && activity.end_date) {
      // Para rangos de fechas
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

// Obtener festivos del mes
export function getMonthHolidaysHelper(monthDate, holidays) {
  if (!holidays || !Array.isArray(holidays)) return []
  
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const monthStart = new Date(year, month, 1).toISOString().split('T')[0]
  const monthEnd = new Date(year, month + 1, 0).toISOString().split('T')[0]
  
  return holidays.filter(holiday => 
    holiday && holiday.date >= monthStart && holiday.date <= monthEnd
  )
}

