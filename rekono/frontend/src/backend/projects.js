import RekonoApi from './api'

class Project extends RekonoApi {
  getProject (projectId) {
    return super.get(`/api/projects/${projectId}/`)
      .then(response => {
        return response.data
      })
  }

  getAllProjects () {
    return super.get('/api/projects/?o=name')
      .then(response => {
        return response.data
      })
  }

  getPaginatedProjects (page = null, limit = null, filter = null) {
    return super.get('/api/projects/?o=name', page, limit, filter)
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

  addMember (projectId, userId) {
    return super.post(`/api/projects/${projectId}/members/`, { user: userId })
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteMember (projectId, userId) {
    return super.delete(`/api/projects/${projectId}/members/${userId}`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  countProjects (filter = null) {
    return super.get('/api/projects/', 1, 1, filter)
      .then(response => {
        return response.data.count
      })
  }
}

export default new Project()
