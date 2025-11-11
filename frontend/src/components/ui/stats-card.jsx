import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Badge } from './badge'
import { cn } from '@/lib/utils.js'

const StatsCard = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend, 
  trendValue, 
  className,
  variant = 'default',
  loading = false 
}) => {
  const getVariantStyles = () => {
    // Diseño profesional y limpio - sin colores de fondo
    return 'hover:shadow-md transition-shadow duration-200'
  }

  const getTrendColor = () => {
    if (!trend) return ''
    return trend === 'up' 
      ? 'text-green-600 dark:text-green-400' 
      : 'text-red-600 dark:text-red-400'
  }

  const getTrendIcon = () => {
    if (!trend) return null
    return trend === 'up' ? '↗' : '↘'
  }

  if (loading) {
    return (
      <Card className={cn('animate-pulse', getVariantStyles(), className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
          <div className="h-4 w-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </CardHeader>
        <CardContent>
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-2"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn(getVariantStyles(), className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {title}
        </CardTitle>
        {Icon && (
          <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
          {value}
        </div>
        <div className="flex items-center justify-between">
          {subtitle && (
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
              {subtitle}
            </p>
          )}
          {trend && trendValue && (
            <Badge 
              variant="outline" 
              className={cn('text-xs font-semibold', getTrendColor())}
            >
              {getTrendIcon()} {trendValue}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export { StatsCard }
