import { useState } from 'react'
import { 
  Bell, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Clock,
  X,
  Eye
} from 'lucide-react'
import { Card, CardContent } from './card'
import { Badge } from './badge'
import { Button } from './button'
import { cn } from '@/lib/utils.js'
import { useNotifications } from '../../contexts/NotificationContext'

const NotificationItem = ({ 
  notification, 
  onMarkAsRead, 
  onRemove,
  compact = false 
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const { getPriorityColor, getPriorityText, getRelativeTime } = useNotifications()

  const getNotificationIcon = () => {
    switch (notification.notification_type) {
      case 'approval_request':
        return <CheckCircle className="w-4 h-4" />
      case 'vacation_conflict':
        return <AlertCircle className="w-4 h-4" />
      case 'calendar_change':
        return <Clock className="w-4 h-4" />
      case 'weekly_summary':
        return <Info className="w-4 h-4" />
      default:
        return <Bell className="w-4 h-4" />
    }
  }

  const getNotificationColor = () => {
    switch (notification.notification_type) {
      case 'approval_request':
        return 'text-blue-600 dark:text-blue-400'
      case 'vacation_conflict':
        return 'text-red-600 dark:text-red-400'
      case 'calendar_change':
        return 'text-yellow-600 dark:text-yellow-400'
      case 'weekly_summary':
        return 'text-green-600 dark:text-green-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  const handleMarkAsRead = async () => {
    if (notification.read || isLoading) return
    
    setIsLoading(true)
    try {
      await onMarkAsRead(notification.id)
    } catch (error) {
      console.error('Error marcando notificación como leída:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemove = () => {
    if (onRemove) {
      onRemove(notification.id)
    }
  }

  if (compact) {
    return (
      <div className={cn(
        'flex items-start space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors',
        !notification.read && 'bg-blue-50 dark:bg-blue-900/20'
      )}>
        <div className={cn('mt-0.5', getNotificationColor())}>
          {getNotificationIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {notification.title}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                {notification.message}
              </p>
            </div>
            <div className="flex items-center space-x-1 ml-2">
              <Badge 
                variant="outline" 
                className={cn('text-xs', getPriorityColor(notification.priority))}
              >
                {getPriorityText(notification.priority)}
              </Badge>
              {!notification.read && (
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
              )}
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {getRelativeTime(notification.created_at)}
          </p>
        </div>
      </div>
    )
  }

  return (
    <Card className={cn(
      'transition-all duration-200 hover:shadow-md',
      !notification.read && 'border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-900/10'
    )}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            <div className={cn('mt-0.5', getNotificationColor())}>
              {getNotificationIcon()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  {notification.title}
                </h4>
                <div className="flex items-center space-x-2 ml-2">
                  <Badge 
                    variant="outline" 
                    className={cn('text-xs', getPriorityColor(notification.priority))}
                  >
                    {getPriorityText(notification.priority)}
                  </Badge>
                  {!notification.read && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                {notification.message}
              </p>
              
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-400">
                  {getRelativeTime(notification.created_at)}
                </p>
                
                <div className="flex items-center space-x-2">
                  {!notification.read && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleMarkAsRead}
                      disabled={isLoading}
                      className="text-xs"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      Marcar como leída
                    </Button>
                  )}
                  
                  {onRemove && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleRemove}
                      className="text-xs text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export { NotificationItem }
