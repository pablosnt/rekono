import { rekonoApiGet, rekonoApiDelete, rekonoApiPost, rekonoApiPut } from './api'

const getAllWordlists = () => {
  return rekonoApiGet('/api/resources/wordlists/?o=type,name')
    .then(response => {
      return response.data.results
    })
}

const createWordlist = (name, type, file) => {
  var data = new FormData()
  data.append('name', name)
  data.append('type', type)
  data.append('file', file)
  return rekonoApiPost('/api/resources/wordlists/', data, false, { 'Content-Type': 'multipart/form-data' })
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const updateWordlist = (wordlistId, name, type, file) => {
  var data = new FormData()
  data.append('name', name)
  data.append('type', type)
  data.append('file', file)
  return rekonoApiPut('/api/resources/wordlists/' + wordlistId + '/', data, false, { 'Content-Type': 'multipart/form-data' })
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const deleteWordlist = (wordlistId) => {
  return rekonoApiDelete('/api/resources/wordlists/' + wordlistId + '/')
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getAllWordlists, createWordlist, updateWordlist, deleteWordlist }
