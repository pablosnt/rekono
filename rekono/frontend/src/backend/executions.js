import RekonoApi from './api'

class Execution extends RekonoApi {
  getAllExecutionsByTask (taskId, page = 1, limit = 1000) {
    return super.get('/api/executions/', page, limit, { task: taskId })
      .then(response => {
        return response.data
      })
  }
}

export default new Execution()
