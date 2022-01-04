import RekonoApi from './api'

class Finding extends RekonoApi {
  getAllFindings (path, filter = null) {
    return super.getAllPages(`/api/${path}/?o=-creation`, filter)
  }

  enableFinding (path, findingId) {
    return super.post(`/api/${path}/${findingId}/enable/`, { })
      .then(response => {
        response.data
      })
  }

  disableFinding (path, findingId) {
    return super.delete(`/api/${path}/${findingId}/`)
      .then(response => {
        response.data
      })
  }

  createTargetFromOSINT (findingId) {
    return super.post(`/api/osint/${findingId}/target/`, { })
      .then(response => {
        response.data
      })
  }
}

export default new Finding()
