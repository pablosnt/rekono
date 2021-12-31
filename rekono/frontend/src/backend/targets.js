import RekonoApi from './api'

class TargetsApi extends RekonoApi {
  getAllTargets (page = null, limit = null, filter = null) {
    return super.get('/api/targets/?o=target', page, limit, filter)
      .then(response => {
        return response.data
      })
  }

  createTarget (projectId, target) {
    return super.post('/api/targets/', { project: projectId, target: target })
      .then(response => {
        return response.data
      })
  }

  deleteTarget (targetId) {
    return super.delete(`/api/targets/${targetId}/`)
      .then(response => {
        return response.data
      })
  }
}

class TargetPortsApi extends RekonoApi {
  createTargetPort (targetId, port) {
    return super.post('/api/target-ports/', { target: targetId, port: port })
      .then(response => {
        return response.data
      })
  }

  deleteTargetPort (targetPortId) {
    return super.delete(`/api/target-ports/${targetPortId}/`)
      .then(response => {
        return response.data
      })
  }
}

class TargetEndpointsApi extends RekonoApi {
  createTargetEndpoint (targetPortId, endpoint) {
    return super.post('/api/target-endpoints/', { target_port: targetPortId, endpoint: endpoint })
      .then(response => {
        return response.data
      })
  }

  deleteTargetEndpoint (targetEndpointId) {
    return super.delete(`/api/target-endpoints/${targetEndpointId}/`)
      .then(response => {
        return response.data
      })
  }
}

export default {
  TargetsApi: new TargetsApi(),
  TargetPortsApi: new TargetPortsApi(),
  TargetEndpointsApi: new TargetEndpointsApi()
}
