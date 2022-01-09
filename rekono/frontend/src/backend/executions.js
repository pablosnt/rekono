import RekonoApi from './api'

class Execution extends RekonoApi {
  getAllExecutionsByTask (taskId) {
    return super.getAllPages('/api/executions/', { task: taskId })
  }

  countExecutions (filter = null) {
    return super.get('/api/executions/', 1, 1, filter)
      .then(response => {
        return response.data.count
      })
  }
}

export default new Execution()
