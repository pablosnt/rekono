import { rekonoApiGet } from './api'

const getTools = () => {
  return rekonoApiGet('/api/tools/?o=stage')
    .then(response => {
      return response.data.results
    })
}

export { getTools }
