import RekonoApi from './api'

class Project extends RekonoApi {
  getProjectsByUser (userId) {
    return super.get('/api/projects/?members=' + userId + '&o=name')
      .then(response => {
        return response.data.results
      })
  }
}

export default new Project()
