import RekonoApi from './api'

class Project extends RekonoApi {
  getAllProjects () {
    return super.get('/api/projects/?o=name')
      .then(response => {
        return response.data
      })
  }

  getPaginatedProjects (page = null, limit = null, filter = null) {
    return super.paginatedGet('/api/projects/?o=name', page, limit, filter)
      .then(response => {
        return response.data
      })
  }

  createProject (name, description, defectDojoId = null) {
    const data = {
      name: name,
      description: description,
      defectdojo_product_id: defectDojoId
    }
    return super.post('/api/projects/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateProject (projectId, name, description, defectDojoId = null) {
    const data = {
      name: name,
      description: description,
      defectdojo_product_id: defectDojoId
    }
    return super.put(`/api/projects/${projectId}/`, data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteProject (projectId) {
    return super.delete(`/api/projects/${projectId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

export default new Project()
