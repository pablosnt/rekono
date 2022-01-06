import RekonoApi from './api'

class Tool extends RekonoApi {
  getAllTools (filter = null) {
    return super.getAllPages('/api/tools/?o=stage', filter)
      .then(response => {
        return response.data
      })
  }

  getPaginatedTools (page = null, limit = null, filter = null) {
    return super.get('/api/tools/?o=stage', page, limit, filter)
      .then(response => {
        return response.data
      })
  }
}

export default new Tool()
