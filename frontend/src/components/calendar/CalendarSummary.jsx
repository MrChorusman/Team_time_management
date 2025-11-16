import { useMemo } from 'react'
import { Card, CardContent } from '@/components/ui/card'

/**
 * Componente para mostrar resumen compacto de vacaciones, HLD, guardias y formación
 * Formato: 4 columnas (Vacaciones, HLD, Guardias, Formación)
 */
const CalendarSummary = ({ employee, activities, currentMonth }) => {
  const summary = useMemo(() => {
    if (!employee || !activities || !Array.isArray(activities)) {
      return {
        vacationTotal: employee?.vacation_days || 0,
        vacationPlanned: 0,
        vacationConsumed: 0,
        vacationRemaining: employee?.vacation_days || 0,
        hldTotal: employee?.hld_hours || 0,
        hldPlanned: 0,
        hldConsumed: 0,
        hldRemaining: employee?.hld_hours || 0,
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

    activities.forEach(activity => {
      if (activity.employee_id !== employee.id) return

      const activityDate = activity.date || activity.start_date
      if (!activityDate) return

      const activityDateObj = new Date(activityDate + 'T00:00:00')
      const activityYear = activityDateObj.getFullYear()
      const activityMonth = activityDateObj.getMonth() + 1
      const activityType = (activity.activity_type || activity.type || '').toUpperCase()

      // Vacaciones
      if (activityType === 'V' || activityType === 'VACATION') {
        vacationPlanned++
        if (activityDate <= todayString) {
          vacationConsumed++
        }
      }

      // HLD
      if (activityType === 'HLD') {
        const hours = activity.hours || 0
        hldPlanned += hours
        if (activityDate <= todayString) {
          hldConsumed += hours
        }
      }

      // Guardias
      if (activityType === 'G' || activityType === 'GUARD') {
        const hours = activity.hours || 0
        if (activityYear === currentYear && activityMonth === currentMonthNum) {
          guardMonthly += hours
        }
        if (activityYear === currentYear) {
          guardAnnual += hours
        }
      }

      // Formación
      if (activityType === 'F' || activityType === 'TRAINING') {
        const hours = activity.hours || 0
        if (activityYear === currentYear && activityMonth === currentMonthNum) {
          trainingMonthly += hours
        }
        if (activityYear === currentYear) {
          trainingAnnual += hours
        }
      }
    })

    const vacationTotal = employee.vacation_days || 0
    // Restan = Total - Planificadas (las consumidas están incluidas en planificadas)
    // Si el usuario quiere restar ambas por separado: Total - Consumidas - (Planificadas - Consumidas) = Total - Planificadas
    const vacationRemaining = Math.max(0, vacationTotal - vacationPlanned)
    
    const hldTotal = employee.hld_hours || 0
    // Restan = Total - Planificadas (las consumidas están incluidas en planificadas)
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
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Vacaciones</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Total:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationTotal} días</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Planificadas:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationPlanned} días</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Consumidas:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationConsumed} días</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Restan:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.vacationRemaining} días</span>
              </div>
            </div>
          </div>

          {/* Columna 2: Horas de Libre Disposición */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Horas de Libre Disposición</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Total:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldTotal}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Planificadas:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldPlanned}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Consumidas:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldConsumed}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Restan:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.hldRemaining}h</span>
              </div>
            </div>
          </div>

          {/* Columna 3: Guardias */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Guardias</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Guardias mensuales:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.guardMonthly}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Guardias anuales:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.guardAnnual}h</span>
              </div>
            </div>
          </div>

          {/* Columna 4: Formación */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Formación</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Formación mensual:</span>
                <span className="font-medium text-gray-900 dark:text-white">{summary.trainingMonthly}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Formación anual:</span>
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
