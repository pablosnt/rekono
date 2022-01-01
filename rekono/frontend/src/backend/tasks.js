import RekonoApi from './api'

class Task extends RekonoApi {
  getAllTasks (page = null, limit = null, filter = null) {
    return super.get('/api/tasks/', page, limit, filter)
      .then(response => {
        return response.data
      })
  }

  createTask (target, process, tool, configuration, intensity, scheduledAtDate, scheduledAtTime, scheduledIn, scheduledTimeUnit, repeatIn, repeatTimeUnit, wordlists) {
    const data = {
      target: target,
      process: process,
      tool: tool,
      configuration: configuration,
      intensity_rank: intensity,
      scheduled_at: scheduledAtDate !== null && scheduledAtTime !== null ? `${scheduledAtDate}T${scheduledAtTime}Z` : null,
      scheduled_in: scheduledIn,
      schduled_time_unit: scheduledTimeUnit,
      repeat_in: repeatIn,
      repeat_time_unit: repeatTimeUnit,
      wordlists: wordlists
    }
    return super.post('/api/tasks/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  cancelTask (taskId) {
    return super.delete(`/api/tasks/${taskId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

export default new Task()
