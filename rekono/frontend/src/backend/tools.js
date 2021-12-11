import RekonoApi from './api'

class Tool extends RekonoApi {
  getTools () {
    return super.get('/api/tools/?o=stage')
      .then(response => {
        return response.data.results
      })
  }
}

export default new Tool()
