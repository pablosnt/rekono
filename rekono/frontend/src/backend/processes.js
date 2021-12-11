import RekonoApi from './api'

class Process extends RekonoApi {
  getAllProcesses () {
    return super.get('/api/processes/?o=name')
      .then(response => {
        return response.data.results
      })
  }

  getProcessesByUser (userId) {
    return super.get('/api/processes/?o=name&creator=' + userId.toString())
      .then(response => {
        return response.data.results
      })
  }

  createProcess = (name, description) => {
    var data = {
      name: name,
      description: description
    }
    return super.post('/api/processes/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateProcess (processId, name, description) {
    var data = {
      name: name,
      description: description
    }
    return super.put('/api/processes/' + processId + '/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteProcess (processId) {
    return super.delete('/api/processes/' + processId + '/')
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

class Step extends RekonoApi {
  createStep (processId, toolId, configurationId, priority) {
    var data = {
      process: processId,
      tool_id: toolId,
      configuration_id: configurationId,
      priority: priority
    }
    return super.post('/api/steps/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateStep (stepId, priority) {
    var data = {
      priority: priority
    }
    return super.put('/api/steps/' + stepId + '/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteStep (stepId) {
    return super.delete('/api/steps/' + stepId + '/')
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

export { Process, Step }
