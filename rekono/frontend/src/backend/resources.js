import { rekonoApiGet } from './api'

const getAllWordlists = () => {
  return rekonoApiGet('/api/resources/wordlists/')
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getAllWordlists }
