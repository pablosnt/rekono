import { rekonoApiGet } from './api'

const getCurrentUserProjects = (userId) => {
  return rekonoApiGet('/api/projects/?members=' + userId + '&o=name')
    .then(response => {
      return response.data.results
    })
}

export { getCurrentUserProjects }
