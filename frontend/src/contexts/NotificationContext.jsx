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
  const { user, loading: authLoading } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [summary, setSummary] = useState({
    unread_count: 0,
    priority_counts: { urgent: 0, high: 0, medium: 0, low: 0 },
    recent_notifications: [],
    has_urgent: false,
    has_high: false
  })
  const [loading, setLoading] = useState(false)

  // Cargar notificaciones cuando el usuario esté autenticado Y AuthContext haya terminado de cargar
  useEffect(() => {
    console.log('[NotificationContext] useEffect triggered:', { user: !!user, authLoading })
    
    // NO hacer nada si AuthContext todavía está cargando
    if (authLoading) {
      console.log('[NotificationContext] Auth still loading, skipping')
      return
    }
    
    if (user) {
      console.log('[NotificationContext] User authenticated, loading notifications')
      loadNotifications()
      loadSummary()
      
      // OPTIMIZACIÓN: Configurar polling solo cuando la página está visible
      let interval = null
      
      const startPolling = () => {
        // Limpiar intervalo anterior si existe
        if (interval) {
          clearInterval(interval)
        }
        
        // Configurar polling para actualizaciones en tiempo real
        interval = setInterval(() => {
          // Solo hacer polling si la página está visible y hay usuario
          if (user && !document.hidden) {
            loadSummary()
          }
        }, 30000) // Cada 30 segundos
      }
      
      const stopPolling = () => {
        if (interval) {
          clearInterval(interval)
          interval = null
        }
      }
      
      // Iniciar polling solo si la página está visible
      if (!document.hidden) {
        startPolling()
      }
      
      // Manejar cambios de visibilidad de la página
      const handleVisibilityChange = () => {
        if (document.hidden) {
          stopPolling()
        } else {
          startPolling()
          // Cargar resumen inmediatamente cuando la página vuelve a ser visible
          loadSummary()
        }
      }
      
      document.addEventListener('visibilitychange', handleVisibilityChange)
      
      return () => {
        console.log('[NotificationContext] Cleaning up interval and listeners')
        stopPolling()
        document.removeEventListener('visibilitychange', handleVisibilityChange)
      }
    } else {
      console.log('[NotificationContext] No user, clearing state')
      // Si no hay usuario, limpiar el estado
      setNotifications([])
      setSummary({
        unread_count: 0,
        priority_counts: { urgent: 0, high: 0, medium: 0, low: 0 },
        recent_notifications: [],
        has_urgent: false,
        has_high: false
      })
    }
  }, [user, authLoading])

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
      // Silenciar errores 401 (no autenticado) para evitar spam en consola
      if (error.response?.status !== 401) {
        console.error('Error cargando notificaciones:', error)
      }
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
      // Silenciar errores 401 (no autenticado) para evitar spam en consola
      if (error.response?.status !== 401) {
        console.error('Error cargando resumen de notificaciones:', error)
      }
    }
  }

  const markAsRead = async (notificationIds) => {
    try {
      // Asegurar que notificationIds sea siempre un array
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds]
      
      const response = await notificationService.markAsRead(idsArray)
      
      if (response.success) {
        // Actualizar estado local
        setNotifications(prev => 
          prev.map(notif => 
            idsArray.includes(notif.id) 
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

  // Función para obtener el contador de no leídas (para compatibilidad)
  const getUnreadCount = () => summary.unread_count
  
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
    getUnreadCount,
    
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
