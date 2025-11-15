import { useMemo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

/**
 * Componente para mostrar resumen compacto de vacaciones, HLD, guardias y formación
 */
const CalendarSummary = ({ employee, activities, currentMonth }) => {
  const summary = useMemo(() => {
    if (!employee || !activities || !Array.isArray(activities)) {
      return {
        vacationTotal: employee?.vacation_days || 0,
        vacationPlanned: 0,
        vacationConsumed: 0,
        hldTotal: employee?.hld_hours || 0,
        hldConsumed: 0,
        guardMonthly: 0,
        trainingMonthly: 0
      }
    }

    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    const today = new Date()
    const todayString = today.toISOString().split('T')[0]

    // Filtrar actividades del mes actual y del empleado
    const monthActivities = activities.filter(activity => {
      if (!activity || activity.employee_id !== employee.id) return false
      
      const activityDate = activity.date || activity.start_date || activity.end_date
      if (!activityDate) return false
      
      const activityDateObj = new Date(activityDate)
      return activityDateObj.getFullYear() === year && activityDateObj.getMonth() === month
    })

    let vacationPlanned = 0
    let vacationConsumed = 0
    let hldConsumed = 0
    let guardMonthly = 0
    let trainingMonthly = 0

    monthActivities.forEach(activity => {
      const activityType = (activity.activity_type || activity.type || '').toUpperCase()
      const activityDate = activity.date || activity.start_date
      
      if (!activityDate) return

      if (activityType === 'V' || activityType === 'VACATION') {
        vacationPlanned += 1
        // Si la fecha ya pasó, es consumida
        if (activityDate <= todayString) {
          vacationConsumed += 1
        }
      } else if (activityType === 'HLD') {
        hldConsumed += activity.hours || 0
      } else if (activityType === 'G' || activityType === 'GUARD') {
        guardMonthly += activity.hours || 0
      } else if (activityType === 'F' || activityType === 'TRAINING') {
        trainingMonthly += activity.hours || 0
      }
    })

    return {
      vacationTotal: employee?.vacation_days || 0,
      vacationPlanned,
      vacationConsumed,
      hldTotal: employee?.hld_hours || 0,
      hldConsumed,
      guardMonthly,
      trainingMonthly
    }
  }, [employee, activities, currentMonth])

  return (
    <Card className="mt-4">
      <CardContent className="p-4">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          {/* Vacaciones */}
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">Vacaciones:</span>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              Total: {summary.vacationTotal}d
            </Badge>
            <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
              Planificadas: {summary.vacationPlanned}d
            </Badge>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              Consumidas: {summary.vacationConsumed}d
            </Badge>
          </div>

          {/* HLD */}
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">HLD:</span>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              Total: {summary.hldTotal}h
            </Badge>
            <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
              Consumidas: {summary.hldConsumed}h
            </Badge>
          </div>

          {/* Guardias */}
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">Guardias mensuales:</span>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              {summary.guardMonthly}h
            </Badge>
          </div>

          {/* Formación */}
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">Formación mensual:</span>
            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
              {summary.trainingMonthly}h
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default CalendarSummary

