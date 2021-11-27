import { rekonoApiGet } from './api'

const getTools = () => {
  return rekonoApiGet('/api/tools/?o=stage')
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export {
  getTools
}
