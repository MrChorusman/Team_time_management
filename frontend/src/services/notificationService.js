import { apiClient } from './apiClient'

export const notificationService = {
  // Obtener notificaciones del usuario
  async getNotifications(page = 1, perPage = 20, unreadOnly = false) {
    const response = await apiClient.get('/notifications', {
      params: {
        page,
        per_page: perPage,
        unread_only: unreadOnly
      }
    })
    return response.data
  },

  // Obtener resumen de notificaciones
  async getSummary() {
    const response = await apiClient.get('/notifications/summary')
    return response.data
  },

  // Marcar notificaciones como leídas
  async markAsRead(notificationIds) {
    const response = await apiClient.post('/notifications/mark-read', {
      notification_ids: Array.isArray(notificationIds) ? notificationIds : [notificationIds]
    })
    return response.data
  },

  // Marcar todas las notificaciones como leídas
  async markAllAsRead() {
    const response = await apiClient.post('/notifications/mark-all-read')
    return response.data
  },

  // Obtener una notificación específica
  async getNotification(notificationId) {
    const response = await apiClient.get(`/notifications/${notificationId}`)
    return response.data
  },

  // Marcar una notificación específica como leída
  async markSingleAsRead(notificationId) {
    const response = await apiClient.post(`/notifications/${notificationId}/mark-read`)
    return response.data
  },

  // Crear notificación personalizada (solo admins)
  async createNotification(notificationData) {
    const response = await apiClient.post('/notifications/create', notificationData)
    return response.data
  },

  // Enviar notificación masiva (solo admins)
  async broadcastNotification(broadcastData) {
    const response = await apiClient.post('/notifications/broadcast', broadcastData)
    return response.data
  },

  // Obtener tipos de notificación disponibles
  async getNotificationTypes() {
    const response = await apiClient.get('/notifications/types')
    return response.data
  },

  // Limpiar notificaciones antiguas (solo admins)
  async cleanupOldNotifications(daysOld = 30) {
    const response = await apiClient.post('/notifications/cleanup', {
      days_old: daysOld
    })
    return response.data
  },

  // Procesar cola de notificaciones (solo admins)
  async processNotificationQueue() {
    const response = await apiClient.post('/notifications/process-queue')
    return response.data
  }
}
