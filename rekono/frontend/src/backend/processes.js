import { rekonoApiGet, rekonoApiPost } from './api'

const getAllProcesses = () => {
  return rekonoApiGet('/api/processes/?o=name')
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const getCurrentUserProcesses = (userId) => {
  return rekonoApiGet('/api/processes/?o=name&creator=' + userId.toString())
    .then(response => {
      return Promise.resolve(response.data.results)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const createNewProcess = (name, description) => {
  var data = {
    name: name,
    description: description
  }
  return rekonoApiPost('/api/processes/', data)
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const createNewStep = (processId, toolId, configurationId, priority) => {
  var data = {
    process: processId,
    tool_id: toolId,
    configuration_id: configurationId,
    priority: priority
  }
  return rekonoApiPost('/api/steps/', data)
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getAllProcesses, getCurrentUserProcesses, createNewProcess, createNewStep }
