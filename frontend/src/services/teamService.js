import { apiClient } from './apiClient'

/**
 * Servicio para gestionar equipos
 */
class TeamService {
  /**
   * Obtener todos los equipos
   * @returns {Promise<Object>} Lista de equipos
   */
  async getAllTeams() {
    try {
      const response = await apiClient.get('/teams')
      return response.data
    } catch (error) {
      console.error('Error obteniendo equipos:', error)
      throw error
    }
  }

  /**
   * Obtener un equipo por ID
   * @param {number} teamId - ID del equipo
   * @returns {Promise<Object>} Datos del equipo
   */
  async getTeamById(teamId) {
    try {
      const response = await apiClient.get(`/teams/${teamId}`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo equipo:', error)
      throw error
    }
  }

  /**
   * Crear un nuevo equipo
   * @param {Object} teamData - Datos del equipo
   * @returns {Promise<Object>} Equipo creado
   */
  async createTeam(teamData) {
    try {
      const response = await apiClient.post('/teams', teamData)
      return response.data
    } catch (error) {
      console.error('Error creando equipo:', error)
      throw error
    }
  }

  /**
   * Obtener resumen de un equipo (con empleados y métricas)
   * @param {number} teamId - ID del equipo
   * @returns {Promise<Object>} Resumen del equipo
   */
  async getTeamSummary(teamId) {
    try {
      const response = await apiClient.get(`/teams/${teamId}/summary`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo resumen de equipo:', error)
      throw error
    }
  }

  /**
   * Obtener empleados de un equipo
   * @param {number} teamId - ID del equipo
   * @returns {Promise<Object>} Lista de empleados del equipo
   */
  async getTeamEmployees(teamId) {
    try {
      const response = await apiClient.get(`/teams/${teamId}/employees`)
      return response.data
    } catch (error) {
      console.error('Error obteniendo empleados del equipo:', error)
      throw error
    }
  }
}

const teamService = new TeamService()
export default teamService

