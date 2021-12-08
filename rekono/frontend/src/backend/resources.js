import { rekonoApiGet } from './api'

const getAllWordlists = () => {
  return rekonoApiGet('/api/resources/wordlists/')
    .then(response => {
      return response.data.results
    })
}

export { getAllWordlists }
