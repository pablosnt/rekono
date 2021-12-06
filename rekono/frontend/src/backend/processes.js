import { rekonoApiGet, rekonoApiPost, rekonoApiPut } from './api'

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

const createProcess = (name, description) => {
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

const updateProcess = (processId, name, description) => {
  var data = {
    name: name,
    description: description
  }
  return rekonoApiPut('/api/processes/' + processId + '/', data)
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

const createStep = (processId, toolId, configurationId, priority) => {
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

const updateStep = (stepId, priority) => {
  var data = {
    priority: priority
  }
  return rekonoApiPut('/api/steps/' + stepId + '/', data)
    .then(response => {
      return Promise.resolve(response.data)
    })
    .catch(error => {
      return Promise.reject(error)
    })
}

export { getAllProcesses, getCurrentUserProcesses, createProcess, updateProcess, createStep, updateStep }
