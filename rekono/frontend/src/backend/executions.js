import RekonoApi from './api'

class Execution extends RekonoApi {
  getAllExecutionsByTask (taskId) {
    return super.getAllPages('/api/executions/', { task: taskId })
  }
}

export default new Execution()
