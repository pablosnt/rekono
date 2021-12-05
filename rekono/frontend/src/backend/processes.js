import { rekonoApiGet } from './api'

const getProcesses = () => {
  return rekonoApiGet('/api/processes/?o=name')
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getProcesses }
