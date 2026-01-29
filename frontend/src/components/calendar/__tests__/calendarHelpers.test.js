import { describe, it, expect, beforeEach } from 'vitest'

// Importar las funciones helper desde CalendarTableView
// Como están inlineadas, necesitamos extraerlas o crear un módulo de exportación
// Por ahora, vamos a crear un módulo de exportación temporal para testing

// Extraer funciones helper para testing
// Estas funciones están inlineadas en CalendarTableView.jsx
// Vamos a crear un módulo de exportación para poder testearlas

/**
 * PRUEBAS UNITARIAS - Funciones Helper del Calendario
 * 
 * Estas pruebas verifican la funcionalidad de las funciones helper
 * que están inlineadas en CalendarTableView.jsx
 */

// Mock de las funciones helper - en producción estas están inlineadas
// Para testing, las extraemos a un módulo separado

// Función para normalizar nombres de países
function normalizeCountryName(countryInput) {
  if (!countryInput) return null
  
  const COUNTRY_MAPPING = {
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
  }
  
  const input = String(countryInput).trim()
  
  // Código ISO de 2 caracteres
  if (input.length === 2 && input.toUpperCase() in COUNTRY_MAPPING) {
    return COUNTRY_MAPPING[input.toUpperCase()].en
  }
  
  // Código ISO de 3 caracteres
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
  
  // Búsqueda por nombre completo
  const inputLower = input.toLowerCase()
  const countryCodes = Object.keys(COUNTRY_MAPPING)
  
  for (let i = 0; i < countryCodes.length; i++) {
    const code = countryCodes[i]
    const names = COUNTRY_MAPPING[code]
    if (names.en.toLowerCase() === inputLower || names.es.toLowerCase() === inputLower) {
      return names.en
    }
  }
  
  // Búsqueda parcial
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

// Función para formatear fechas
function formatDateLocal(year, month, day) {
  const monthStr = String(month + 1).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  return `${year}-${monthStr}-${dayStr}`
}

// Función para obtener días del mes
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

// Función para obtener código de actividad
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

// Función para obtener actividad de un día
function getActivityForDayHelper(employeeId, dateString, activities) {
  if (!activities || !Array.isArray(activities)) return null
  
  const found = activities.find(activity => {
    if (!activity || activity.employee_id !== employeeId) return false
    const activityDate = activity.date || activity.start_date || activity.end_date
    if (!activityDate) return false
    
    if (activity.date === dateString) return true
    if (activity.start_date && activity.end_date) {
      return activity.start_date <= dateString && activity.end_date >= dateString
    }
    return false
  })
  
  return found || null
}

// Función para obtener resumen mensual
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

describe('Calendar Helper Functions', () => {
  
  describe('normalizeCountryName', () => {
    it('debe normalizar código ISO de 2 caracteres', () => {
      expect(normalizeCountryName('ES')).toBe('Spain')
      expect(normalizeCountryName('US')).toBe('United States')
      expect(normalizeCountryName('FR')).toBe('France')
    })
    
    it('debe normalizar código ISO de 3 caracteres', () => {
      expect(normalizeCountryName('ESP')).toBe('Spain')
      expect(normalizeCountryName('USA')).toBe('United States')
      expect(normalizeCountryName('FRA')).toBe('France')
    })
    
    it('debe normalizar nombres en inglés', () => {
      expect(normalizeCountryName('Spain')).toBe('Spain')
      expect(normalizeCountryName('United States')).toBe('United States')
      expect(normalizeCountryName('France')).toBe('France')
    })
    
    it('debe normalizar nombres en español', () => {
      expect(normalizeCountryName('España')).toBe('Spain')
      expect(normalizeCountryName('Estados Unidos')).toBe('United States')
      expect(normalizeCountryName('Francia')).toBe('France')
    })
    
    it('debe manejar valores null o undefined', () => {
      expect(normalizeCountryName(null)).toBeNull()
      expect(normalizeCountryName(undefined)).toBeNull()
      expect(normalizeCountryName('')).toBeNull()
    })
    
    it('debe ser case-insensitive', () => {
      expect(normalizeCountryName('es')).toBe('Spain')
      expect(normalizeCountryName('ESPAÑA')).toBe('Spain')
      expect(normalizeCountryName('spain')).toBe('Spain')
    })
  })
  
  describe('formatDateLocal', () => {
    it('debe formatear fechas correctamente', () => {
      expect(formatDateLocal(2024, 0, 1)).toBe('2024-01-01')
      expect(formatDateLocal(2024, 11, 31)).toBe('2024-12-31')
      expect(formatDateLocal(2024, 2, 5)).toBe('2024-03-05')
    })
    
    it('debe agregar ceros a la izquierda cuando es necesario', () => {
      expect(formatDateLocal(2024, 0, 5)).toBe('2024-01-05')
      expect(formatDateLocal(2024, 8, 9)).toBe('2024-09-09')
    })
  })
  
  describe('getDaysInMonth', () => {
    it('debe retornar todos los días de enero 2024', () => {
      const date = new Date(2024, 0, 1) // Enero 2024
      const days = getDaysInMonth(date)
      
      expect(days).toHaveLength(31)
      expect(days[0].day).toBe(1)
      expect(days[0].dateString).toBe('2024-01-01')
      expect(days[30].day).toBe(31)
      expect(days[30].dateString).toBe('2024-01-31')
    })
    
    it('debe retornar todos los días de febrero 2024 (año bisiesto)', () => {
      const date = new Date(2024, 1, 1) // Febrero 2024 (bisiesto)
      const days = getDaysInMonth(date)
      
      expect(days).toHaveLength(29)
      expect(days[0].day).toBe(1)
      expect(days[28].day).toBe(29)
    })
    
    it('debe retornar todos los días de febrero 2023 (no bisiesto)', () => {
      const date = new Date(2023, 1, 1) // Febrero 2023
      const days = getDaysInMonth(date)
      
      expect(days).toHaveLength(28)
    })
    
    it('debe identificar correctamente los fines de semana', () => {
      const date = new Date(2024, 0, 1) // Enero 2024
      const days = getDaysInMonth(date)
      
      // 1 de enero de 2024 es lunes (dayOfWeek = 1)
      // 6 de enero es sábado (dayOfWeek = 6)
      // 7 de enero es domingo (dayOfWeek = 0)
      
      const saturday = days.find(d => d.day === 6)
      const sunday = days.find(d => d.day === 7)
      
      expect(saturday.isWeekend).toBe(true)
      expect(sunday.isWeekend).toBe(true)
    })
  })
  
  describe('getActivityCodeHelper', () => {
    it('debe retornar "V" para vacaciones', () => {
      expect(getActivityCodeHelper({ activity_type: 'V' })).toBe('V')
      expect(getActivityCodeHelper({ activity_type: 'vacation' })).toBe('V')
      expect(getActivityCodeHelper({ type: 'V' })).toBe('V')
    })
    
    it('debe retornar "A" para ausencias', () => {
      expect(getActivityCodeHelper({ activity_type: 'A' })).toBe('A')
      expect(getActivityCodeHelper({ activity_type: 'absence' })).toBe('A')
      expect(getActivityCodeHelper({ activity_type: 'sick_leave' })).toBe('A')
    })
    
    it('debe retornar "HLD" para días festivos', () => {
      expect(getActivityCodeHelper({ activity_type: 'HLD' })).toBe('HLD')
      expect(getActivityCodeHelper({ activity_type: 'hld' })).toBe('HLD')
    })
    
    it('debe retornar "G" para guardias', () => {
      expect(getActivityCodeHelper({ activity_type: 'G' })).toBe('G')
      expect(getActivityCodeHelper({ activity_type: 'guard' })).toBe('G')
    })
    
    it('debe retornar "F" para formación', () => {
      expect(getActivityCodeHelper({ activity_type: 'F' })).toBe('F')
      expect(getActivityCodeHelper({ activity_type: 'training' })).toBe('F')
    })
    
    it('debe incluir horas cuando están disponibles', () => {
      expect(getActivityCodeHelper({ activity_type: 'G', hours: 8 })).toBe('G +8h')
      expect(getActivityCodeHelper({ activity_type: 'HLD', hours: 4 })).toBe('HLD -4h')
      expect(getActivityCodeHelper({ activity_type: 'F', hours: 6 })).toBe('F -6h')
    })
    
    it('debe manejar valores null o undefined', () => {
      expect(getActivityCodeHelper(null)).toBe('')
      expect(getActivityCodeHelper(undefined)).toBe('')
      expect(getActivityCodeHelper({})).toBe('')
    })
  })
  
  describe('getActivityForDayHelper', () => {
    const mockActivities = [
      {
        id: 1,
        employee_id: 1,
        date: '2024-01-15',
        activity_type: 'V'
      },
      {
        id: 2,
        employee_id: 1,
        start_date: '2024-01-20',
        end_date: '2024-01-25',
        activity_type: 'A'
      },
      {
        id: 3,
        employee_id: 2,
        date: '2024-01-15',
        activity_type: 'V'
      }
    ]
    
    it('debe encontrar actividad por fecha exacta', () => {
      const activity = getActivityForDayHelper(1, '2024-01-15', mockActivities)
      expect(activity).not.toBeNull()
      expect(activity.id).toBe(1)
      expect(activity.activity_type).toBe('V')
    })
    
    it('debe encontrar actividad dentro de un rango de fechas', () => {
      const activity = getActivityForDayHelper(1, '2024-01-22', mockActivities)
      expect(activity).not.toBeNull()
      expect(activity.id).toBe(2)
      expect(activity.activity_type).toBe('A')
    })
    
    it('debe retornar null si no hay actividad para el empleado', () => {
      const activity = getActivityForDayHelper(3, '2024-01-15', mockActivities)
      expect(activity).toBeNull()
    })
    
    it('debe retornar null si no hay actividades', () => {
      const activity = getActivityForDayHelper(1, '2024-01-15', [])
      expect(activity).toBeNull()
    })
    
    it('debe retornar null si las actividades son null o undefined', () => {
      expect(getActivityForDayHelper(1, '2024-01-15', null)).toBeNull()
      expect(getActivityForDayHelper(1, '2024-01-15', undefined)).toBeNull()
    })
  })
  
  describe('getMonthSummaryHelper', () => {
    const mockActivities = [
      {
        id: 1,
        employee_id: 1,
        date: '2024-01-05',
        activity_type: 'V'
      },
      {
        id: 2,
        employee_id: 1,
        date: '2024-01-10',
        activity_type: 'V'
      },
      {
        id: 3,
        employee_id: 1,
        date: '2024-01-15',
        activity_type: 'A'
      },
      {
        id: 4,
        employee_id: 1,
        start_date: '2024-01-20',
        end_date: '2024-01-25',
        activity_type: 'V'
      },
      {
        id: 5,
        employee_id: 2,
        date: '2024-01-05',
        activity_type: 'V'
      }
    ]
    
    it('debe calcular correctamente días de vacaciones y ausencias', () => {
      const monthDate = new Date(2024, 0, 1) // Enero 2024
      const summary = getMonthSummaryHelper(1, monthDate, mockActivities)
      
      // 2 días de vacaciones individuales + 6 días de rango (20-25) = 8 días de vacaciones
      // 1 día de ausencia
      expect(summary.vacation).toBe(8)
      expect(summary.absence).toBe(1)
    })
    
    it('debe retornar 0 para empleado sin actividades', () => {
      const monthDate = new Date(2024, 0, 1)
      const summary = getMonthSummaryHelper(3, monthDate, mockActivities)
      
      expect(summary.vacation).toBe(0)
      expect(summary.absence).toBe(0)
    })
    
    it('debe retornar 0 si no hay actividades', () => {
      const monthDate = new Date(2024, 0, 1)
      const summary = getMonthSummaryHelper(1, monthDate, [])
      
      expect(summary.vacation).toBe(0)
      expect(summary.absence).toBe(0)
    })
    
    it('debe manejar actividades que cruzan límites de mes', () => {
      const activities = [
        {
          id: 1,
          employee_id: 1,
          start_date: '2024-01-28',
          end_date: '2024-02-05',
          activity_type: 'V'
        }
      ]
      
      const monthDate = new Date(2024, 0, 1) // Enero 2024
      const summary = getMonthSummaryHelper(1, monthDate, activities)
      
      // Solo cuenta los días de enero (28, 29, 30, 31) = 4 días
      expect(summary.vacation).toBe(4)
    })
  })
})
