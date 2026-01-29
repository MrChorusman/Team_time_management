// Funciones helper para CalendarTableView
// Separadas en archivo independiente para evitar problemas de inicialización durante minificación
// Export único como objeto al final para asegurar que todas las funciones estén definidas antes de exportarse

// #region agent log
// Función de logging que funciona en desarrollo y producción
const logDebug = (location, message, data, hypothesisId) => {
  const logData = {location,message,data,timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId};
  // Usar console.log con prefijo para fácil identificación
  console.log('[DEBUG]', JSON.stringify(logData));
  // Almacenar en window para acceso desde consola del navegador
  if (typeof window !== 'undefined') {
    if (!window._debugLogs) window._debugLogs = [];
    window._debugLogs.push(logData);
    // Mantener solo los últimos 100 logs para evitar problemas de memoria
    if (window._debugLogs.length > 100) window._debugLogs.shift();
  }
};
logDebug('calendarHelpers.js:5','Module evaluation started',{timestamp:Date.now()},'A');
// #endregion

// Mapeo completo bidireccional de países (inglés/español/códigos ISO)
// Usar función getter para evitar problemas de hoisting durante la minificación
let _COUNTRY_MAPPING = null
function getCountryMapping() {
  // #region agent log
  logDebug('calendarHelpers.js:11','getCountryMapping called',{_COUNTRY_MAPPING:_COUNTRY_MAPPING===null?'null':'initialized'},'E');
  // #endregion
  if (!_COUNTRY_MAPPING) {
    // #region agent log
    logDebug('calendarHelpers.js:14','Initializing _COUNTRY_MAPPING',{},'E');
    // #endregion
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

// Función para normalizar nombre de país
function normalizeCountryName(countryInput) {
  // #region agent log
  logDebug('calendarHelpers.js:62','normalizeCountryName called',{countryInput},'C');
  // #endregion
  if (!countryInput) return null
  
  const COUNTRY_MAPPING = getCountryMapping()
  // #region agent log
  logDebug('calendarHelpers.js:66','getCountryMapping returned',{hasMapping:!!COUNTRY_MAPPING},'C');
  // #endregion
  const input = String(countryInput).trim()
  
  // Si es código ISO (2 o 3 letras), buscar directamente
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
  
  // Buscar por nombre (inglés o español)
  const inputLower = input.toLowerCase()
  for (const code in COUNTRY_MAPPING) {
    const names = COUNTRY_MAPPING[code]
    if (names.en.toLowerCase() === inputLower || names.es.toLowerCase() === inputLower) {
      return names.en
    }
  }
  
  // Búsqueda parcial
  for (const code in COUNTRY_MAPPING) {
    const names = COUNTRY_MAPPING[code]
    if (inputLower.includes(names.en.toLowerCase()) || names.en.toLowerCase().includes(inputLower) ||
        inputLower.includes(names.es.toLowerCase()) || names.es.toLowerCase().includes(inputLower)) {
      return names.en
    }
  }
  
  // Si no se encuentra, devolver el input original
  return input
}

// Función para obtener todas las variantes de un país
function getCountryVariants(countryInput) {
  if (!countryInput) return null
  
  const normalized = normalizeCountryName(countryInput)
  if (!normalized) return null
  
  // Buscar el código ISO correspondiente
  const COUNTRY_MAPPING = getCountryMapping()
  for (const code in COUNTRY_MAPPING) {
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

// Verificar si un festivo aplica a la ubicación de un empleado
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

// Función para verificar si dos países coinciden
function countriesMatch(country1, country2) {
  if (!country1 || !country2) return false
  
  const norm1 = normalizeCountryName(country1)
  const norm2 = normalizeCountryName(country2)
  
  if (norm1 && norm2) {
    return norm1.toLowerCase() === norm2.toLowerCase()
  }
  
  return String(country1).toLowerCase() === String(country2).toLowerCase()
}

// Mantener compatibilidad con código existente
// Usar función getter para evitar problemas de hoisting durante la minificación
let _ISO_TO_COUNTRY_NAME = null
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

// Función helper para formatear fecha como YYYY-MM-DD sin problemas de zona horaria
function formatDateLocal(year, month, day) {
  // Usar padStart para asegurar formato de 2 dígitos
  const monthStr = String(month + 1).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  return `${year}-${monthStr}-${dayStr}`
}

// Obtener días del mes
function getDaysInMonth(date) {
  // #region agent log
  logDebug('calendarHelpers.js:219','getDaysInMonth called',{date:date?.toString()},'C');
  // #endregion
  const year = date.getFullYear()
  const month = date.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days = []
  
  for (let day = 1; day <= daysInMonth; day++) {
    const currentDate = new Date(year, month, day)
    // Usar formato local en lugar de toISOString() para evitar problemas de zona horaria
    // #region agent log
    logDebug('calendarHelpers.js:228','About to call formatDateLocal',{year,month,day},'C');
    // #endregion
    const dateString = formatDateLocal(year, month, day)
    // #region agent log
    logDebug('calendarHelpers.js:230','formatDateLocal returned',{dateString},'C');
    // #endregion
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

// Obtener meses del año
function getMonthsInYear(date) {
  // #region agent log
  logDebug('calendarHelpers.js:242','getMonthsInYear called',{date:date?.toString()},'C');
  // #endregion
  const year = date.getFullYear()
  const months = []
  
  for (let month = 0; month < 12; month++) {
    const monthDate = new Date(year, month, 1)
    // #region agent log
    logDebug('calendarHelpers.js:248','About to call getDaysInMonth from getMonthsInYear',{monthDate:monthDate?.toString()},'C');
    // #endregion
    const days = getDaysInMonth(monthDate)
    // #region agent log
    logDebug('calendarHelpers.js:250','getDaysInMonth returned from getMonthsInYear',{daysCount:days?.length},'C');
    // #endregion
    months.push({
      date: monthDate,
      name: monthDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }),
      days: days
    })
  }
  
  return months
}

// Verificar si un día es festivo para un empleado específico según su ubicación
function isHolidayHelper(dateString, employeeLocation, holidays) {
  if (!holidays || !Array.isArray(holidays) || !employeeLocation) return false
  
  // Obtener variantes del país del empleado
  const employeeCountryInput = employeeLocation?.country || ''
  const employeeVariants = getCountryVariants(employeeCountryInput)
  const employeeCountries = employeeVariants 
    ? [employeeVariants.en, employeeVariants.es, employeeLocation?.country].filter(Boolean)
    : [employeeLocation?.country].filter(Boolean)
  
  return holidays.some(holiday => {
    // Verificar que la fecha coincida
    if (holiday.date !== dateString) return false
    
    // Obtener variantes del país del festivo
    const holidayVariants = getCountryVariants(holiday.country)
    const holidayCountries = holidayVariants
      ? [holidayVariants.en, holidayVariants.es, holiday.country].filter(Boolean)
      : [holiday.country].filter(Boolean)
    
    // Verificar si los países coinciden (en cualquier variante)
    const countriesMatch = employeeCountries.some(empCountry => 
      holidayCountries.some(holCountry => 
        normalizeCountryName(empCountry) === normalizeCountryName(holCountry) ||
        empCountry === holCountry
      )
    )
    
    if (!countriesMatch) return false
    
    // Usar holiday_type (la columna hierarchy_level no existe en BD)
    const holidayType = holiday.holiday_type || holiday.type || ''
    
    // Festivos nacionales se aplican a todos del mismo país
    if (holidayType === 'national') {
      return true
    }
    
    // Festivos regionales solo para la misma región
    if (holidayType === 'regional') {
      return holiday.region === employeeLocation?.region
    }
    
    // Festivos locales solo para la misma ciudad
    if (holidayType === 'local') {
      return holiday.region === employeeLocation?.region &&
             holiday.city === employeeLocation?.city
    }
    
    // Si no tiene tipo específico pero coincide el país, considerarlo festivo nacional
    return true
  })
}

// Obtener actividades para un empleado en un día específico
function getActivityForDayHelper(employeeId, dateString, activities) {
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
function getActivityCodeHelper(activity) {
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
function getCellBackgroundColorHelper(activity, isWeekend, isHolidayDay) {
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
function getCellTextColorHelper(activity, isWeekend, isHolidayDay) {
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
function getMonthSummaryHelper(employeeId, monthDate, activities) {
  if (!activities || !Array.isArray(activities)) return { vacation: 0, absence: 0 }
  
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  // Usar formatDateLocal para evitar problemas de zona horaria
  const monthStart = formatDateLocal(year, month, 1)
  const lastDay = new Date(year, month + 1, 0).getDate()
  const monthEnd = formatDateLocal(year, month, lastDay)
  
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

// Obtener festivos del mes (ordenados cronológicamente)
function getMonthHolidaysHelper(monthDate, holidays) {
  if (!holidays || !Array.isArray(holidays)) return []
  
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  // Usar formatDateLocal para evitar problemas de zona horaria
  const monthStart = formatDateLocal(year, month, 1)
  const lastDay = new Date(year, month + 1, 0).getDate()
  const monthEnd = formatDateLocal(year, month, lastDay)
  
  const monthHolidays = holidays.filter(holiday => 
    holiday && holiday.date >= monthStart && holiday.date <= monthEnd
  )
  
  // Ordenar cronológicamente por fecha (de menor a mayor)
  return monthHolidays.sort((a, b) => {
    if (a.date < b.date) return -1
    if (a.date > b.date) return 1
    return 0
  })
}

// Exportaciones nombradas individuales para evitar problemas de inicialización circular
// Esto permite que cada función se importe independientemente sin problemas de hoisting
export {
  getIsoToCountryName,
  getCountryMapping,
  normalizeCountryName,
  getCountryVariants,
  doesHolidayApplyToLocation,
  countriesMatch,
  getDaysInMonth,
  getMonthsInYear,
  isHolidayHelper,
  getActivityForDayHelper,
  getActivityCodeHelper,
  getCellBackgroundColorHelper,
  getCellTextColorHelper,
  getMonthSummaryHelper,
  getMonthHolidaysHelper
}

// También exportar como objeto default para compatibilidad con código existente
// NO crear el objeto durante la evaluación del módulo - crear solo cuando se invoca la función
// Esto evita completamente problemas de hoisting durante la minificación
// #region agent log
logDebug('calendarHelpers.js:537','Module evaluation completed, all functions defined',{functionsDefined:typeof getIsoToCountryName==='function'&&typeof getCountryMapping==='function'&&typeof normalizeCountryName==='function'&&typeof getDaysInMonth==='function'&&typeof getMonthsInYear==='function'},'A');
// #endregion

// Función que crea el objeto solo cuando se invoca (lazy initialization)
function createCalendarHelpersObject() {
  // #region agent log
  logDebug('calendarHelpers.js:543','createCalendarHelpersObject called',{},'A');
  // #endregion
  
  // Crear el objeto con todas las funciones ya definidas
  const helpersObj = {
    // Exponer las funciones getter directamente para inicialización lazy
    get ISO_TO_COUNTRY_NAME() {
      // #region agent log
      logDebug('calendarHelpers.js:549','ISO_TO_COUNTRY_NAME getter accessed',{getIsoToCountryNameDefined:typeof getIsoToCountryName==='function'},'B');
      // #endregion
      return getIsoToCountryName()
    },
    get COUNTRY_MAPPING() {
      // #region agent log
      logDebug('calendarHelpers.js:555','COUNTRY_MAPPING getter accessed',{getCountryMappingDefined:typeof getCountryMapping==='function'},'B');
      // #endregion
      return getCountryMapping()
    },
    normalizeCountryName: normalizeCountryName,
    getCountryVariants: getCountryVariants,
    doesHolidayApplyToLocation: doesHolidayApplyToLocation,
    countriesMatch: countriesMatch,
    getDaysInMonth: getDaysInMonth,
    getMonthsInYear: getMonthsInYear,
    isHolidayHelper: isHolidayHelper,
    getActivityForDayHelper: getActivityForDayHelper,
    getActivityCodeHelper: getActivityCodeHelper,
    getCellBackgroundColorHelper: getCellBackgroundColorHelper,
    getCellTextColorHelper: getCellTextColorHelper,
    getMonthSummaryHelper: getMonthSummaryHelper,
    getMonthHolidaysHelper: getMonthHolidaysHelper
  }
  
  // #region agent log
  logDebug('calendarHelpers.js:575','createCalendarHelpersObject completed',{hasAllFunctions:typeof helpersObj.getDaysInMonth==='function'&&typeof helpersObj.getMonthsInYear==='function'},'A');
  // #endregion
  return helpersObj
}

// Crear una función getter singleton que crea el objeto solo cuando se invoca
let _calendarHelpersInstance = null
function getCalendarHelpersSingleton() {
  // #region agent log
  logDebug('calendarHelpers.js:583','getCalendarHelpersSingleton called',{_calendarHelpersInstance:_calendarHelpersInstance===null?'null':'initialized'},'D');
  // #endregion
  if (!_calendarHelpersInstance) {
    _calendarHelpersInstance = createCalendarHelpersObject()
  }
  return _calendarHelpersInstance
}

// Exportar la función getter en lugar del objeto directamente
// #region agent log
logDebug('calendarHelpers.js:591','Module export completed',{exportType:typeof getCalendarHelpersSingleton},'A');
// #endregion
export default getCalendarHelpersSingleton
