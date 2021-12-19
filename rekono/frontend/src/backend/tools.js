import RekonoApi from './api'

class Tool extends RekonoApi {
  getTools (page = null, size = null, filter = null) {
    return super.paginatedGet('/api/tools/?o=stage', page, size, filter)
      .then(response => {
        return response.data
      })
  }
}

export default new Tool()
