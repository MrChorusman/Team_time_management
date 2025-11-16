import { useMemo } from 'react'
import { Card, CardContent } from '@/components/ui/card'

/**
 * Componente para mostrar resumen compacto de vacaciones, HLD, guardias y formación
 * Formato: 4 columnas (Vacaciones, HLD, Guardias, Formación)
 */
const CalendarSummary = ({ employee, activities, currentMonth }) => {
  const summary = useMemo(() => {
    // Obtener totales del empleado (usar annual_vacation_days y annual_hld_hours del backend)
    const vacationTotal = employee?.annual_vacation_days || employee?.vacation_days || 0
    const hldTotal = employee?.annual_hld_hours || employee?.hld_hours || 0

    if (!employee || !activities || !Array.isArray(activities)) {
      return {
        vacationTotal,
        vacationPlanned: 0,
        vacationConsumed: 0,
        vacationRemaining: vacationTotal,
        hldTotal,
        hldPlanned: 0,
        hldConsumed: 0,
        hldRemaining: hldTotal,
        guardMonthly: 0,
        guardAnnual: 0,
        trainingMonthly: 0,
        trainingAnnual: 0
      }
    }

    const currentYear = currentMonth.getFullYear()
    const currentMonthNum = currentMonth.getMonth() + 1
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayString = today.toISOString().split('T')[0]

    let vacationPlanned = 0
    let vacationConsumed = 0
    let hldPlanned = 0
    let hldConsumed = 0
    let guardMonthly = 0
    let guardAnnual = 0
    let trainingMonthly = 0
    let trainingAnnual = 0

    // Filtrar actividades del empleado actual
    const employeeActivities = activities.filter(activity => {
      if (!activity) return false
      // Comparar employee_id (puede ser número o string)
      const activityEmployeeId = activity.employee_id || activity.employee?.id
      const employeeId = employee.id
      return String(activityEmployeeId) === String(employeeId)
    })

    employeeActivities.forEach(activity => {
      // Obtener fecha de la actividad (puede venir en diferentes formatos)
      const activityDate = activity.date || activity.start_date || activity.end_date
      if (!activityDate) {
        console.warn('Actividad sin fecha:', activity)
        return
      }

      // Normalizar fecha a formato YYYY-MM-DD
      let dateString = activityDate
      if (activityDate instanceof Date) {
        const year = activityDate.getFullYear()
        const month = String(activityDate.getMonth() + 1).padStart(2, '0')
        const day = String(activityDate.getDate()).padStart(2, '0')
        dateString = `${year}-${month}-${day}`
      } else if (typeof activityDate === 'string') {
        // Si ya es string, asegurar formato YYYY-MM-DD
        dateString = activityDate.split('T')[0]
      }

      const activityDateObj = new Date(dateString + 'T00:00:00')
      if (isNaN(activityDateObj.getTime())) {
        console.warn('Fecha inválida en actividad:', activityDate, activity)
        return
      }

      const activityYear = activityDateObj.getFullYear()
      const activityMonth = activityDateObj.getMonth() + 1
      const activityType = (activity.activity_type || activity.type || '').toUpperCase()

      // Vacaciones (tipo 'V')
      if (activityType === 'V' || activityType === 'VACATION') {
        vacationPlanned++
        // Si la fecha ya pasó, es consumida
        if (dateString <= todayString) {
          vacationConsumed++
        }
      }

      // HLD (tipo 'HLD')
      if (activityType === 'HLD') {
        const hours = parseFloat(activity.hours) || 0
        hldPlanned += hours
        // Si la fecha ya pasó, es consumida
        if (dateString <= todayString) {
          hldConsumed += hours
        }
      }

      // Guardias (tipo 'G')
      if (activityType === 'G' || activityType === 'GUARD') {
        const hours = parseFloat(activity.hours) || 0
        // Guardias mensuales: del mes actual
        if (activityYear === currentYear && activityMonth === currentMonthNum) {
          guardMonthly += hours
        }
        // Guardias anuales: del año actual
        if (activityYear === currentYear) {
          guardAnnual += hours
        }
      }

      // Formación (tipo 'F')
      if (activityType === 'F' || activityType === 'TRAINING') {
        const hours = parseFloat(activity.hours) || 0
        // Formación mensual: del mes actual
        if (activityYear === currentYear && activityMonth === currentMonthNum) {
          trainingMonthly += hours
        }
        // Formación anual: del año actual
        if (activityYear === currentYear) {
          trainingAnnual += hours
        }
      }
    })

    // Restan = Total - Planificadas (las consumidas están incluidas en planificadas)
    const vacationRemaining = Math.max(0, vacationTotal - vacationPlanned)
    const hldRemaining = Math.max(0, hldTotal - hldPlanned)

    return {
      vacationTotal,
      vacationPlanned,
      vacationConsumed,
      vacationRemaining: Math.max(0, vacationRemaining),
      hldTotal,
      hldPlanned,
      hldConsumed,
      hldRemaining: Math.max(0, hldRemaining),
      guardMonthly,
      guardAnnual,
      trainingMonthly,
      trainingAnnual
    }
  }, [employee, activities, currentMonth])

  return (
    <Card className="mt-4">
      <CardContent className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Columna 1: Vacaciones */}
          <div className="border-r border-gray-200 dark:border-gray-700 pr-6 last:border-r-0">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Vacaciones</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Total</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationTotal} días</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Planificadas</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationPlanned} días</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Consumidas</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationConsumed} días</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Restan</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationRemaining} días</span>
              </div>
            </div>
          </div>

          {/* Columna 2: Horas de Libre Disposición */}
          <div className="border-r border-gray-200 dark:border-gray-700 pr-6 last:border-r-0">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Horas de Libre Disposición</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Total</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldTotal}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Planificadas</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldPlanned}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Consumidas</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldConsumed}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Restan</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldRemaining}h</span>
              </div>
            </div>
          </div>

          {/* Columna 3: Guardias */}
          <div className="border-r border-gray-200 dark:border-gray-700 pr-6 last:border-r-0">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Guardias</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Guardias mensuales</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.guardMonthly}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Guardias anuales</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.guardAnnual}h</span>
              </div>
            </div>
          </div>

          {/* Columna 4: Formación */}
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Formación</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Formación mensual</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.trainingMonthly}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">- Formación anual</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.trainingAnnual}h</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default CalendarSummary
