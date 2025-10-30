import { apiClient } from './apiClient'

/**
 * Servicio para gestionar empleados
 */
class EmployeeService {
  /**
   * Crear un nuevo empleado
   * @param {Object} employeeData - Datos del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async createEmployee(employeeData) {
    try {
      const response = await apiClient.post('/employees', employeeData)
      return response.data
    } catch (error) {
      console.error('Error creando empleado:', error)
      throw error
    }
  }

  /**
   * Actualizar un empleado existente
   * @param {number} employeeId - ID del empleado
   * @param {Object} employeeData - Datos actualizados del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async updateEmployee(employeeId, employeeData) {
    try {
      const response = await apiClient.put(`/employees/${employeeId}`, employeeData)
      return response.data
    } catch (error) {
      console.error('Error actualizando empleado:', error)
      throw error
    }
  }

  /**
   * Obtener empleado por user_id
   * @param {number} userId - ID del usuario
   * @returns {Promise<Object>} Datos del empleado
   */
  async getEmployeeByUserId(userId) {
    try {
      const response = await apiClient.get(`/employees/user/${userId}`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo empleado por user_id:', error)
      throw error
    }
  }

  /**
   * Obtener un empleado por ID
   * @param {number} employeeId - ID del empleado
   * @returns {Promise<Object>} Datos del empleado
   */
  async getEmployee(employeeId) {
    try {
      const response = await apiClient.get(`/employees/${employeeId}`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo empleado:', error)
      throw error
    }
  }

  /**
   * Obtener todos los empleados
   * @param {Object} params - Parámetros de consulta (page, per_page, etc.)
   * @returns {Promise<Object>} Lista de empleados
   */
  async getAllEmployees(params = {}) {
    try {
      const response = await apiClient.get('/employees', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo empleados:', error)
      throw error
    }
  }

  /**
   * Eliminar un empleado
   * @param {number} employeeId - ID del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async deleteEmployee(employeeId) {
    try {
      const response = await apiClient.delete(`/employees/${employeeId}`)
      return response.data
    } catch (error) {
      console.error('Error eliminando empleado:', error)
      throw error
    }
  }

  /**
   * Aprobar un empleado
   * @param {number} employeeId - ID del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async approveEmployee(employeeId) {
    try {
      const response = await apiClient.post(`/employees/${employeeId}/approve`)
      return response.data
    } catch (error) {
      console.error('Error aprobando empleado:', error)
      throw error
    }
  }

  /**
   * Desactivar un empleado
   * @param {number} employeeId - ID del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async deactivateEmployee(employeeId) {
    try {
      const response = await apiClient.post(`/employees/${employeeId}/deactivate`)
      return response.data
    } catch (error) {
      console.error('Error desactivando empleado:', error)
      throw error
    }
  }
}

export default new EmployeeService()

