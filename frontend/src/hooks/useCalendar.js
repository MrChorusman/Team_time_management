import { useQuery } from '@tanstack/react-query'

/**
 * Hook personalizado para obtener datos del calendario con React Query
 * Proporciona caché automático y refetch inteligente
 */
export const useCalendar = (options = {}) => {
  const {
    employeeId = null,
    teamId = null,
    year = new Date().getFullYear(),
    month = new Date().getMonth() + 1,
    view = 'monthly', // 'monthly' o 'annual'
    enabled = true
  } = options

  // Determinar endpoint según la vista
  const endpoint = view === 'annual' 
    ? `/calendar/annual?year=${year}${employeeId ? `&employee_id=${employeeId}` : ''}${teamId ? `&team_id=${teamId}` : ''}`
    : `/calendar?year=${year}&month=${month}${employeeId ? `&employee_id=${employeeId}` : ''}${teamId ? `&team_id=${teamId}` : ''}`

  return useQuery({
    queryKey: ['calendar', employeeId, teamId, year, month, view],
    queryFn: async () => {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}${endpoint}`,
        { credentials: 'include' }
      )
      
      if (!response.ok) {
        throw new Error('Error cargando calendario')
      }
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.message || 'Error cargando calendario')
      }
      
      return data.calendar
    },
    enabled,
    staleTime: 2 * 60 * 1000, // 2 minutos - datos frescos
    gcTime: 10 * 60 * 1000, // 10 minutos - tiempo de caché
  })
}

/**
 * Hook para obtener actividades del año completo (optimizado)
 */
export const useYearActivities = (options = {}) => {
  const {
    employeeId = null,
    teamId = null,
    year = new Date().getFullYear(),
    enabled = true
  } = options

  return useQuery({
    queryKey: ['year-activities', employeeId, teamId, year],
    queryFn: async () => {
      const endpoint = `/calendar/annual?year=${year}${employeeId ? `&employee_id=${employeeId}` : ''}${teamId ? `&team_id=${teamId}` : ''}`
      
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}${endpoint}`,
        { credentials: 'include' }
      )
      
      if (!response.ok) {
        throw new Error('Error cargando actividades del año')
      }
      
      const data = await response.json()
      
      if (!data.success) {
        throw new Error(data.message || 'Error cargando actividades')
      }
      
      // Aplanar actividades de todos los meses
      const allActivities = []
      if (data.calendar?.months) {
        data.calendar.months.forEach(monthData => {
          if (monthData.employees) {
            monthData.employees.forEach(emp => {
              const empData = emp.employee || emp
              if (emp.activities) {
                Object.values(emp.activities).forEach(activity => {
                  allActivities.push({
                    ...activity,
                    employee_id: empData.id
                  })
                })
              }
            })
          }
        })
      }
      
      return allActivities
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 15 * 60 * 1000, // 15 minutos
  })
}
