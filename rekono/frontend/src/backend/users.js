import RekonoApi from './api'

class Users extends RekonoApi {
  getAllUsers (filter = null) {
    return super.getAllPages('/api/users/?o=username', filter)
  }

  getPaginatedUsers (page = null, limit = null, filter = null) {
    return super.get('/api/users/?o=username', page, limit, filter)
      .then(response => {
        return response.data
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
        return response.data
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

  createUser (username, firstName, lastName, password, otp) {
    let data = {
      username: username,
      first_name: firstName,
      last_name: lastName,
      password: password,
      otp: otp
    }
    return super.post('/api/users/create/', data)
      .then(response => {
        return response.data
      })
  }

  requestResetPassword (email) {
    return super.post('/api/reset-password/', { email: email })
      .then(response => {
        return response.data
      })
  }

  resetPassword (password, otp) {
    return super.put('/api/reset-password/', { password: password, otp: otp })
      .then(response => {
        return response.data
      })
  }
}

export default new Users()
