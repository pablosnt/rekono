import RekonoApi from './api'

class Users extends RekonoApi {
  getAllUsers (page = null, limit = null, filter = null) {
    return super.paginatedGet('/api/users/?o=username', page, limit, filter)
      .then(response => {
        return response.data.results
      })
  }

  updateRole (userId, role) {
    return super.put(`/api/users/${userId}/role/`, { role: role })
      .then(response => {
        return response.data
      })
  }

  disableUser (userId) {
    return super.delete(`/api/users/${userId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  enableUser (userId, role) {
    return super.post(`/api/users/${userId}/enable/`, { role: role })
      .then(response => {
        return response.data
      })
  }

  inviteUser (email, role) {
    return super.post('/api/users/invite/', { email: email, role: role })
      .then(response => {
        return response.data
      })
  }
}

export default new Users()
