import RekonoApi from './api'

class Wordlist extends RekonoApi {
  getAllWordlists (page = null, limit = null, filter = null) {
    return super.paginatedGet('/api/resources/wordlists/?o=type,name', page, limit, filter)
      .then(response => {
        return response.data.results
      })
  }

  createWordlist (name, type, file) {
    const data = new FormData()
    data.append('name', name)
    data.append('type', type)
    data.append('file', file)
    return super.post('/api/resources/wordlists/', data, true, { 'Content-Type': 'multipart/form-data' })
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateWordlist (wordlistId, name, type, file) {
    const data = new FormData()
    data.append('name', name)
    data.append('type', type)
    data.append('file', file)
    return super.put(`/api/resources/wordlists/${wordlistId}/`, data, false, { 'Content-Type': 'multipart/form-data' })
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteWordlist (wordlistId) {
    return super.delete(`/api/resources/wordlists/${wordlistId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

export default new Wordlist()
