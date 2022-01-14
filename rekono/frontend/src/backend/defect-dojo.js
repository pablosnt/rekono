import RekonoApi from './api'

class DefectDojo extends RekonoApi {
  getData (engagementId, engagementName, engagementDescription) {
    if (engagementId !== null) {
      return {
        id: engagementId
      }
    } else if (engagementName !== null && engagementDescription !== null) {
      return {
        name: engagementName,
        description: engagementDescription
      }
    }
  }

  importFinding (path, itemId, engagementId, engagementName, engagementDescription) {
    return super.post(`/api/${path}/${itemId}/defect-dojo/`, this.getData(engagementId, engagementName, engagementDescription))
      .then(response => {
        return response.data
      })
  }

  importFindings (path, itemId, engagementId, engagementName, engagementDescription) {
    return super.post(`/api/${path}/${itemId}/defect-dojo-findings/`, this.getData(engagementId, engagementName, engagementDescription))
      .then(response => {
        return response.data
      })
  }

  importScans (path, itemId, engagementId, engagementName, engagementDescription) {
    return super.post(`/api/${path}/${itemId}/defect-dojo-scans/`, this.getData(engagementId, engagementName, engagementDescription))
      .then(response => {
        return response.data
      })
  }
}

export default new DefectDojo()