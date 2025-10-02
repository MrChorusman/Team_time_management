import { createContext, useContext, useState, useEffect } from 'react'
import { notificationService } from '../services/notificationService'
import { useAuth } from './AuthContext'

const NotificationContext = createContext({})

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications debe ser usado dentro de un NotificationProvider')
  }
  return context
}

export const NotificationProvider = ({ children }) => {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [summary, setSummary] = useState({
    unread_count: 0,
    priority_counts: { urgent: 0, high: 0, medium: 0, low: 0 },
    recent_notifications: [],
    has_urgent: false,
    has_high: false
  })
  const [loading, setLoading] = useState(false)

  // Cargar notificaciones cuando el usuario esté autenticado
  useEffect(() => {
    if (user) {
      loadNotifications()
      loadSummary()
      
      // Configurar polling para actualizaciones en tiempo real
      const interval = setInterval(() => {
        loadSummary()
      }, 30000) // Cada 30 segundos
      
      return () => clearInterval(interval)
    }
  }, [user])

  const loadNotifications = async (page = 1, unreadOnly = false) => {
    if (!user) return
    
    try {
      setLoading(true)
      const response = await notificationService.getNotifications(page, 20, unreadOnly)
      
      if (response.success) {
        if (page === 1) {
          setNotifications(response.notifications)
        } else {
          setNotifications(prev => [...prev, ...response.notifications])
        }
      }
    } catch (error) {
      console.error('Error cargando notificaciones:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSummary = async () => {
    if (!user) return
    
    try {
      const response = await notificationService.getSummary()
      
      if (response.success) {
        setSummary(response.summary)
      }
    } catch (error) {
      console.error('Error cargando resumen de notificaciones:', error)
    }
  }

  const markAsRead = async (notificationIds) => {
    try {
      const response = await notificationService.markAsRead(notificationIds)
      
      if (response.success) {
        // Actualizar estado local
        setNotifications(prev => 
          prev.map(notif => 
            notificationIds.includes(notif.id) 
              ? { ...notif, read: true, read_at: new Date().toISOString() }
              : notif
          )
        )
        
        // Actualizar resumen
        loadSummary()
      }
      
      return response
    } catch (error) {
      console.error('Error marcando notificaciones como leídas:', error)
      return { success: false, message: 'Error de conexión' }
    }
  }

  const markAllAsRead = async () => {
    try {
      const response = await notificationService.markAllAsRead()
      
      if (response.success) {
        // Marcar todas las notificaciones locales como leídas
        setNotifications(prev => 
          prev.map(notif => ({ 
            ...notif, 
            read: true, 
            read_at: new Date().toISOString() 
          }))
        )
        
        // Actualizar resumen
        setSummary(prev => ({
          ...prev,
          unread_count: 0,
          priority_counts: { urgent: 0, high: 0, medium: 0, low: 0 },
          has_urgent: false,
          has_high: false
        }))
      }
      
      return response
    } catch (error) {
      console.error('Error marcando todas las notificaciones:', error)
      return { success: false, message: 'Error de conexión' }
    }
  }

  const getNotificationById = async (notificationId) => {
    try {
      const response = await notificationService.getNotification(notificationId)
      
      if (response.success) {
        // Actualizar la notificación en el estado local si existe
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? response.notification
              : notif
          )
        )
        
        // Si se marcó como leída, actualizar resumen
        if (response.notification.read) {
          loadSummary()
        }
      }
      
      return response
    } catch (error) {
      console.error('Error obteniendo notificación:', error)
      return { success: false, message: 'Error de conexión' }
    }
  }

  // Función para mostrar notificaciones toast (se puede integrar con una librería de toast)
  const showToast = (notification) => {
    // Aquí se puede integrar con react-hot-toast o similar
    console.log('Nueva notificación:', notification)
  }

  // Función para agregar una nueva notificación (para uso en tiempo real)
  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev])
    setSummary(prev => ({
      ...prev,
      unread_count: prev.unread_count + 1,
      priority_counts: {
        ...prev.priority_counts,
        [notification.priority]: prev.priority_counts[notification.priority] + 1
      },
      has_urgent: prev.has_urgent || notification.priority === 'urgent',
      has_high: prev.has_high || notification.priority === 'high'
    }))
    
    // Mostrar toast para notificaciones importantes
    if (notification.priority === 'urgent' || notification.priority === 'high') {
      showToast(notification)
    }
  }

  // Función para obtener el color del badge según la prioridad
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-500'
      case 'high':
        return 'bg-orange-500'
      case 'medium':
        return 'bg-blue-500'
      case 'low':
        return 'bg-gray-500'
      default:
        return 'bg-gray-500'
    }
  }

  // Función para obtener el texto de la prioridad
  const getPriorityText = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'Urgente'
      case 'high':
        return 'Alta'
      case 'medium':
        return 'Media'
      case 'low':
        return 'Baja'
      default:
        return 'Media'
    }
  }

  // Función para formatear fecha relativa
  const getRelativeTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    if (diffInSeconds < 60) {
      return 'Hace un momento'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `Hace ${hours} hora${hours > 1 ? 's' : ''}`
    } else {
      const days = Math.floor(diffInSeconds / 86400)
      return `Hace ${days} día${days > 1 ? 's' : ''}`
    }
  }

  const value = {
    // Estado
    notifications,
    summary,
    loading,
    
    // Acciones
    loadNotifications,
    loadSummary,
    markAsRead,
    markAllAsRead,
    getNotificationById,
    addNotification,
    
    // Utilidades
    getPriorityColor,
    getPriorityText,
    getRelativeTime,
    
    // Computed values
    hasUnread: summary.unread_count > 0,
    hasUrgent: summary.has_urgent,
    hasHigh: summary.has_high,
    unreadCount: summary.unread_count
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}
