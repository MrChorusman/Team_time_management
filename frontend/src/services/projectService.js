import { apiClient } from './apiClient'

class ProjectService {
  async list(params = {}) {
    const response = await apiClient.get('/projects', { params })
    return response.data
  }

  async create(projectData) {
    const response = await apiClient.post('/projects', projectData)
    return response.data
  }

  async update(projectId, projectData) {
    const response = await apiClient.put(`/projects/${projectId}`, projectData)
    return response.data
  }

  async remove(projectId) {
    const response = await apiClient.delete(`/projects/${projectId}`)
    return response.data
  }

  async addAssignment(projectId, assignmentData) {
    const response = await apiClient.post(`/projects/${projectId}/assignments`, assignmentData)
    return response.data
  }

  async updateAssignment(projectId, assignmentId, payload) {
    const response = await apiClient.put(`/projects/${projectId}/assignments/${assignmentId}`, payload)
    return response.data
  }

  async deleteAssignment(projectId, assignmentId) {
    const response = await apiClient.delete(`/projects/${projectId}/assignments/${assignmentId}`)
    return response.data
  }
}

const projectService = new ProjectService()
export default projectService

