import apiClient from './apiClient'

/**
 * Servicio para gestionar ubicaciones geográficas
 * Consume los endpoints de /api/locations
 */
const locationService = {
  /**
   * Obtiene todos los países activos
   * @returns {Promise<Object>} { success, countries, total_count }
   */
  getAllCountries: async () => {
    try {
      const response = await apiClient.get('/locations/countries')
      return response.data
    } catch (error) {
      console.error('Error obteniendo países:', error)
      throw error
    }
  },

  /**
   * Obtiene comunidades autónomas de un país
   * @param {string} countryCode - Código ISO del país (ej: 'ES', 'MX')
   * @returns {Promise<Object>} { success, autonomous_communities, total_count }
   */
  getAutonomousCommunities: async (countryCode) => {
    try {
      const response = await apiClient.get('/locations/autonomous-communities', {
        params: { country_code: countryCode }
      })
      return response.data
    } catch (error) {
      console.error('Error obteniendo comunidades autónomas:', error)
      throw error
    }
  },

  /**
   * Obtiene comunidades autónomas por ID de país
   * @param {number} countryId - ID del país
   * @returns {Promise<Object>} { success, autonomous_communities, total_count }
   */
  getAutonomousCommunitiesByCountryId: async (countryId) => {
    try {
      const response = await apiClient.get('/locations/autonomous-communities', {
        params: { country_id: countryId }
      })
      return response.data
    } catch (error) {
      console.error('Error obteniendo comunidades autónomas:', error)
      throw error
    }
  },

  /**
   * Obtiene provincias de una comunidad autónoma
   * @param {number} autonomousCommunityId - ID de la comunidad autónoma
   * @returns {Promise<Object>} { success, provinces, total_count }
   */
  getProvinces: async (autonomousCommunityId) => {
    try {
      const response = await apiClient.get('/locations/provinces', {
        params: { autonomous_community_id: autonomousCommunityId }
      })
      return response.data
    } catch (error) {
      console.error('Error obteniendo provincias:', error)
      throw error
    }
  },

  /**
   * Obtiene ciudades de una comunidad autónoma
   * @param {number} autonomousCommunityId - ID de la comunidad autónoma
   * @param {number} limit - Número máximo de resultados (default: 100)
   * @returns {Promise<Object>} { success, cities, total_count }
   */
  getCities: async (autonomousCommunityId, limit = 100) => {
    try {
      const response = await apiClient.get('/locations/cities', {
        params: { 
          autonomous_community_id: autonomousCommunityId,
          limit 
        }
      })
      return response.data
    } catch (error) {
      console.error('Error obteniendo ciudades:', error)
      throw error
    }
  },

  /**
   * Busca ciudades por nombre
   * @param {string} searchTerm - Término de búsqueda
   * @param {number} limit - Número máximo de resultados (default: 100)
   * @returns {Promise<Object>} { success, cities, total_count }
   */
  searchCities: async (searchTerm, limit = 100) => {
    try {
      const response = await apiClient.get('/locations/cities', {
        params: { 
          search: searchTerm,
          limit 
        }
      })
      return response.data
    } catch (error) {
      console.error('Error buscando ciudades:', error)
      throw error
    }
  },

  /**
   * Búsqueda unificada de ubicaciones
   * @param {string} searchTerm - Término de búsqueda
   * @param {string} type - Tipo de ubicación: 'all', 'country', 'community', 'city'
   * @returns {Promise<Object>} { success, results: { countries, autonomous_communities, cities } }
   */
  searchLocations: async (searchTerm, type = 'all') => {
    try {
      const response = await apiClient.get('/locations/search', {
        params: { 
          q: searchTerm,
          type 
        }
      })
      return response.data
    } catch (error) {
      console.error('Error buscando ubicaciones:', error)
      throw error
    }
  }
}

export default locationService

