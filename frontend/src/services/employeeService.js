import { apiClient } from './apiClient'

/**
 * Servicio para gestionar empleados
 */
class EmployeeService {
  /**
   * Crear un nuevo empleado (registro)
   * @param {Object} employeeData - Datos del empleado
   * @returns {Promise<Object>} Respuesta del servidor
   */
  async createEmployee(employeeData) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/a491d860-bd0b-4baf-92b3-3f62268aaf57',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'employeeService.js:12',message:'createEmployee llamado',data:{employeeData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    try {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/a491d860-bd0b-4baf-92b3-3f62268aaf57',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'employeeService.js:15',message:'Antes de llamar API',data:{url:'/employees/register',payload:employeeData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      const response = await apiClient.post('/employees/register', employeeData)
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/a491d860-bd0b-4baf-92b3-3f62268aaf57',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'employeeService.js:17',message:'Respuesta exitosa recibida',data:{status:response.status,data:response.data},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      return response.data
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/a491d860-bd0b-4baf-92b3-3f62268aaf57',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'employeeService.js:20',message:'Error capturado',data:{error:error.message,response:error.response?.data,status:error.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
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

