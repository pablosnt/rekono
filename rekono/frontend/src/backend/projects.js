import { rekonoApiGet } from './api'

const getCurrentUserProjects = (userId) => {
  return rekonoApiGet('/api/projects/?members=' + userId + '&o=name')
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getCurrentUserProjects }
