import RekonoApi from './api'

class Tool extends RekonoApi {
  getTools (page = null, size = null) {
    return super.paginatedGet('/api/tools/?o=stage', page, size)
      .then(response => {
        return response.data
      })
  }
}

export default new Tool()
